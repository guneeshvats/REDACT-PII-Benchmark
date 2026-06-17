#!/usr/bin/env python3
"""
aide_llm_detectors.py — LLM-as-Detector for PII Benchmark (v3)

Runs GPT-4.1 + Claude Sonnet 4.6 as PII detectors on a stratified sample.

v3 improvements over v2:
  - Few-shot examples covering the failure modes documented in the
    annotation calibration guide:
      * Category mention vs personal disclosure (Article 9)
      * Partial-disclosure spans (last-4 digits, masked emails)
      * Multi-word name spans (full name as one entity)
      * Span boundary handling (exclude parentheticals, context words)
      * Multilingual offset calculation (CJK, Arabic RTL)
      * Illustrative example detection (developer docs, templates)
      * Multi-mention emission (every occurrence of same entity)
  - Explicit ordering and offset rules
  - Concrete YES/NO examples for each failure mode

Usage on AIDE:
  python aide_llm_detectors.py \
    --input clean_deduped.json \
    --out-dir detector_outputs/ \
    --report llm_detectors_report.json \
    --sample 1000
"""

import os
import sys
import json
import time
import argparse
import random
from collections import defaultdict
from typing import Dict, List, Optional, Any

try:
    from aide import AIDE
except ImportError:
    print("ERROR: 'aide' package not found. Run on AIDE.")
    sys.exit(1)

aide = AIDE()

DETECTORS = [
    {"model": "gpt-4.1",           "vendor": "openai",    "label": "gpt41"},
    {"model": "claude-sonnet-4-6", "vendor": "anthropic", "label": "claude_sonnet_4_6"},
]

CANONICAL_TYPES = [
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    "Personal_Email_Address", "Work_Email_Address",
    "Telephone_Numbers_Personal", "Telephone_Numbers_Work",
    "Address_Personal", "Address_Work",
    "Date_of_Birth", "Age", "Place_of_Birth", "Date_Time",
    "National_Identification_Number", "Passport_Number", "Driving_License_Number",
    "Tax_Reference_Number",
    "Credit_Card_Numbers", "Account_Statements",
    "Employee_ID_Number", "Customer_Reference_Number", "Building_Badge_Card_Number",
    "Static_IP_Address",
    "Social_Media_Identifiers", "Password",
    "Religion", "Sex_Orientation", "Political_Party",
    "Trade_Union_Membership", "Crime",
    "Medical_Information", "Allergy_Information", "Sickness_Day_Records",
    "Ethnicity", "Nationality", "Citizenship_Status", "Country_of_Residence",
    "Gender", "Marital_Status",
    "Compensation_and_Salary", "Performance_Assessment", "Disciplinary_Action",
    "Professional_Background", "Business_Title",
    "Geolocation_Data", "Org_Name", "PEP_Status",
    "Emergency_Contact_Details", "City", "State", "Location",
]


DETECTOR_PROMPT_TEMPLATE = """You are a multilingual PII (Personally Identifiable Information) detection system. You will receive a text and must identify all PII entities, returning them as JSON.

## TASK
For each PII entity in the text, output:
- entity_string: the exact text of the entity as it appears in the input
- entity_type: one of 51 canonical types (exact match required, see list below)
- start: character offset where the entity begins (0-indexed)
- end: character offset where the entity ends (exclusive — i.e., one past the last character)

## CANONICAL ENTITY TYPES (use ONLY these labels, exact match)
{canonical_types}

## CORE RULES

### Rule 1 — Character offsets
- Offsets are 0-indexed character positions in the original input text.
- For multibyte scripts (CJK, Arabic, Hebrew, Thai, Devanagari): count each character once, regardless of byte length. Python's `text[start:end]` should reproduce the entity_string exactly.
- Whitespace, punctuation, and emoji each count as one character.

### Rule 2 — Multiple mentions
- If the SAME entity appears multiple times in the text, emit ONE annotation per occurrence with the correct offsets for each.
- Example: if "Tomáš" appears at positions 45 and 312, emit two entities.

### Rule 3 — Span boundaries (NO context words, NO parenthetical translations)
- DO: span only the identifier characters
- DON'T: include surrounding context words like "last digits", "Mr.", "patient name:", etc.
- DON'T: include parenthetical translations like "(forgery)" after a non-English term

### Rule 4 — Multi-word names = ONE entity
- "John Smith" → one entity with entity_type=Full_Name, NOT two entities First_Given_Name + Last_Family_Name
- "Mohd. Irfan Ali Khan" → one entity Full_Name spanning the entire name
- Single-name entities only when only one name is present (e.g., a salutation "Hello Sarah,")

### Rule 5 — Category mentions ≠ personal disclosure
- Article 9 categories (Religion, Sex_Orientation, Political_Party, Trade_Union_Membership, Crime, Medical_Information, Allergy_Information, Ethnicity) should be tagged ONLY when they disclose a specific person's attribute.
- DO NOT tag the literal word "religion" or "sexual orientation" or "political party" when it appears as a category mention in a moderation note, government registry listing, compliance manual, or hate-speech discussion that doesn't disclose any individual's actual attribute.

### Rule 6 — Illustrative examples ≠ real disclosures
- If a phone number / VAT number / credit card / email appears in developer documentation or a template with text indicating it's an EXAMPLE ("for example...", "e.g....", "to illustrate this..."), still detect it — downstream evaluation will compare against the ground truth disclosed flag.

### Rule 7 — Partial disclosures
- "credit card last 4 digits 8473" → entity_string="8473" (digits only), NOT "끝자리 8473" or "last 4 digits 8473"
- "j***@gmail.com" → entity_string="j***@gmail.com" (the full obfuscated form is the entity)
- "EMP-TR-2201" → entity_string="EMP-TR-2201" (full structured ID)

### Rule 8 — Multilingual sensitivity
- Process Arabic, Hebrew (RTL scripts), CJK, Devanagari, Thai with proper character handling.
- Do NOT include parenthetical English translations in the span (e.g., for "जालसाजी (forgery)" the entity_string is "जालसाजी" only).

## FEW-SHOT EXAMPLES

### EXAMPLE 1 — Multi-word name, structured ID, partial credit card
INPUT TEXT:
[2024-03-15 14:23] Customer: Mehmet Kara (EMP-TR-2201) called about order. Charged credit card last 4 digits 8473.

CORRECT OUTPUT:
{{
  "entities": [
    {{"entity_string": "Mehmet Kara", "entity_type": "Full_Name", "start": 28, "end": 39}},
    {{"entity_string": "EMP-TR-2201", "entity_type": "Employee_ID_Number", "start": 41, "end": 52}},
    {{"entity_string": "8473", "entity_type": "Credit_Card_Numbers", "start": 100, "end": 104}}
  ]
}}

NOTES: "Mehmet Kara" is ONE Full_Name (not two). Credit card span is just "8473" (digits only), NOT "last 4 digits 8473".

### EXAMPLE 2 — Category mention NOT to tag (negative example)
INPUT TEXT:
Worknote: The flagged post contains slurs targeting individuals based on their sexual orientation and religion.

CORRECT OUTPUT:
{{"entities": []}}

NOTES: "sexual orientation" and "religion" are category terms in a moderation note, NOT disclosures about a specific person. Do not tag.

### EXAMPLE 3 — Genuine Article 9 disclosure
INPUT TEXT:
Patient record for Klaus Weber: Religion: Catholic. Allergies: Penicillin. Diagnosis: Type 2 diabetes.

CORRECT OUTPUT:
{{
  "entities": [
    {{"entity_string": "Klaus Weber", "entity_type": "Full_Name", "start": 19, "end": 30}},
    {{"entity_string": "Catholic", "entity_type": "Religion", "start": 42, "end": 50}},
    {{"entity_string": "Penicillin", "entity_type": "Allergy_Information", "start": 63, "end": 73}},
    {{"entity_string": "Type 2 diabetes", "entity_type": "Medical_Information", "start": 86, "end": 101}}
  ]
}}

NOTES: All three Article 9 attributes are genuine personal disclosures about Klaus Weber.

### EXAMPLE 4 — Multilingual without parenthetical translation
INPUT TEXT:
Charges against Mohd. Irfan Ali Khan include Section 467 IPC — जालसाजी (forgery) and Section 420 IPC — धोखाधड़ी (fraud).

CORRECT OUTPUT:
{{
  "entities": [
    {{"entity_string": "Mohd. Irfan Ali Khan", "entity_type": "Full_Name", "start": 16, "end": 36}},
    {{"entity_string": "जालसाजी", "entity_type": "Crime", "start": 67, "end": 74}},
    {{"entity_string": "धोखाधड़ी", "entity_type": "Crime", "start": 109, "end": 117}}
  ]
}}

NOTES: Crime spans are the Hindi terms only, NOT "जालसाजी (forgery)" with the parenthetical English translation.

### EXAMPLE 5 — Multiple mentions of same name
INPUT TEXT:
Hello Sarah, this is to confirm Sarah Johnson's appointment on March 15.

CORRECT OUTPUT:
{{
  "entities": [
    {{"entity_string": "Sarah", "entity_type": "First_Given_Name", "start": 6, "end": 11}},
    {{"entity_string": "Sarah Johnson", "entity_type": "Full_Name", "start": 32, "end": 45}},
    {{"entity_string": "March 15", "entity_type": "Date_Time", "start": 63, "end": 71}}
  ]
}}

NOTES: First mention is a single name (First_Given_Name); second mention has both names (Full_Name). Both occurrences are emitted.

### EXAMPLE 6 — JSON record with implicit boundaries
INPUT TEXT:
{{"name": "Tereza Nováková", "dob": "12.05.1998", "email": "t.novakova@centrum.cz"}}

CORRECT OUTPUT:
{{
  "entities": [
    {{"entity_string": "Tereza Nováková", "entity_type": "Full_Name", "start": 10, "end": 25}},
    {{"entity_string": "12.05.1998", "entity_type": "Date_of_Birth", "start": 35, "end": 45}},
    {{"entity_string": "t.novakova@centrum.cz", "entity_type": "Personal_Email_Address", "start": 56, "end": 77}}
  ]
}}

NOTES: Inside JSON, the entity is just the value (not quotes, not the key, not the colon).

## OUTPUT FORMAT

Return JSON in this exact format and nothing else (no preamble, no markdown fence):

{{"entities": [{{"entity_string": "...", "entity_type": "...", "start": N, "end": N}}, ...]}}

If no PII is present, return: {{"entities": []}}"""


def extract_content_from_response(response: Any, vendor: str) -> Optional[str]:
    """Vendor-aware content extraction including AIDE-wrapped Anthropic shape."""
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return response

    if not isinstance(response, dict):
        return None

    # AIDE-wrapped Anthropic shape
    if "output" in response and isinstance(response["output"], dict):
        output = response["output"]
        msg = output.get("message", {})
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        return block["text"]
            elif isinstance(content, str):
                return content

    # OpenAI shape
    if "choices" in response:
        choices = response.get("choices", [])
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message")
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                return block.get("text", "")
                if first.get("text"):
                    return first["text"]

    # Direct Anthropic shape
    if "content" in response:
        content = response["content"]
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        return block.get("text", "")
                    if "text" in block:
                        return block["text"]

    if "text" in response:
        return response["text"]
    return None


def make_payload(model: str, vendor: str, system_prompt: str, user_msg: str):
    if vendor == "google":
        return {
            "contents": {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n---\n\n{user_msg}"}]
            },
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 4000,
            }
        }
    if model == "gpt-5.2":
        return {
            "messages": [
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                {"role": "user",   "content": [{"type": "text", "text": user_msg}]}
            ],
            "max_completion_tokens": 4000,
        }
    return {
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user",   "content": [{"type": "text", "text": user_msg}]}
        ],
        "temperature": 0.0,
        "max_tokens": 4000,
    }


def call_detector(detector: Dict, text: str, max_retries: int = 3) -> Optional[List[Dict]]:
    model = detector["model"]
    vendor = detector["vendor"]
    system_prompt = DETECTOR_PROMPT_TEMPLATE.format(
        canonical_types=", ".join(CANONICAL_TYPES)
    )
    user_msg = f"TEXT:\n{text}"

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(2 ** attempt)
            payload = make_payload(model, vendor, system_prompt, user_msg)
            response = aide.call_llm(model=model, payload=payload)
            content = extract_content_from_response(response, vendor)
            if not content:
                continue

            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:])
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

            if not content.startswith("{"):
                start = content.find("{")
                end = content.rfind("}")
                if start >= 0 and end > start:
                    content = content[start:end+1]

            parsed = json.loads(content)
            if isinstance(parsed, dict) and "entities" in parsed:
                return parsed["entities"]
        except (json.JSONDecodeError, Exception) as e:
            if attempt == max_retries - 1:
                print(f"    {model} failed: {str(e)[:120]}")

    return None


def stratified_sample(records: List[Dict], n: int, seed: int = 42) -> List[int]:
    random.seed(seed)
    by_lang = defaultdict(list)
    for i, r in enumerate(records):
        lang = r.get("axes", {}).get("language", "UNK")
        by_lang[lang].append(i)

    n_langs = len(by_lang)
    per_lang = max(1, n // n_langs)
    chosen = []
    for lang, indices in by_lang.items():
        random.shuffle(indices)
        chosen.extend(indices[:per_lang])
    random.shuffle(chosen)
    return chosen[:n]


def run(input_path: str, out_dir: str, report_path: str, sample_size: int):
    print("=" * 70)
    print("AIDE LLM-AS-DETECTOR v3 — Few-Shot Prompted")
    print("=" * 70)
    print(f"Detectors: {[d['model'] for d in DETECTORS]}")
    print(f"Input:  {input_path}")
    print(f"Output dir: {out_dir}")
    print(f"Sample size: {sample_size}")
    print()

    os.makedirs(out_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else data.get("records", [])
    print(f"Loaded {len(records)} records")

    sample_indices = stratified_sample(records, sample_size)
    print(f"Stratified sample of {len(sample_indices)} records")
    print()

    pred_files = {
        d["label"]: open(os.path.join(out_dir, f"{d['label']}_predictions.jsonl"), "w", encoding="utf-8")
        for d in DETECTORS
    }

    stats = {d["label"]: {"records": 0, "entities": 0, "failures": 0} for d in DETECTORS}

    try:
        for i, rec_idx in enumerate(sample_indices):
            rec = records[rec_idx]
            rec_id = rec.get("record_id", f"idx_{rec_idx}")
            text = rec.get("text", "")
            lang = rec.get("axes", {}).get("language", "?")
            print(f"[{i+1}/{len(sample_indices)}] record_id={rec_id} (lang={lang}, len={len(text)})")

            for det in DETECTORS:
                entities = call_detector(det, text)
                if entities is None:
                    stats[det["label"]]["failures"] += 1
                    print(f"    {det['model']}: FAILED")
                    pred = {"record_id": rec_id, "record_index": rec_idx, "language": lang, "entities": []}
                    pred_files[det["label"]].write(json.dumps(pred, ensure_ascii=False) + "\n")
                    pred_files[det["label"]].flush()
                    continue

                filtered = []
                for e in entities:
                    if not isinstance(e, dict):
                        continue
                    et = e.get("entity_type", "")
                    if et not in CANONICAL_TYPES:
                        continue
                    s = e.get("start")
                    en = e.get("end")
                    if not isinstance(s, int) or not isinstance(en, int):
                        continue
                    if s < 0 or en > len(text) or s >= en:
                        continue
                    filtered.append({
                        "entity_string": e.get("entity_string", ""),
                        "entity_type": et,
                        "start": s,
                        "end": en,
                    })

                stats[det["label"]]["records"] += 1
                stats[det["label"]]["entities"] += len(filtered)

                pred = {
                    "record_id": rec_id,
                    "record_index": rec_idx,
                    "language": lang,
                    "entities": filtered,
                }
                pred_files[det["label"]].write(json.dumps(pred, ensure_ascii=False) + "\n")
                pred_files[det["label"]].flush()
                print(f"    {det['model']}: {len(filtered)} entities")

                time.sleep(0.3)
    finally:
        for f in pred_files.values():
            f.close()

    report = {
        "detectors": [d["model"] for d in DETECTORS],
        "n_records": len(sample_indices),
        "stats": stats,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("DETECTOR SUMMARY")
    print("=" * 70)
    for d in DETECTORS:
        s = stats[d["label"]]
        avg = s["entities"] / s["records"] if s["records"] else 0
        print(f"  {d['model']}: {s['records']} records, {s['entities']} entities "
              f"(avg {avg:.1f}/rec), {s['failures']} failures")
    print()
    print(f"Predictions: {out_dir}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--report", required=True)
    p.add_argument("--sample", type=int, default=1000)
    args = p.parse_args()
    run(args.input, args.out_dir, args.report, args.sample)
