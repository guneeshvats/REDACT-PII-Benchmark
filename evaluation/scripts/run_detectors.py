"""
Detector evaluation harness.

Runs PII detectors on a corpus and produces per-record predictions in a
normalized format suitable for downstream scoring (F1, stratified F1,
Kendall's τ).

Supported detectors:
    presidio         Microsoft Presidio (regex + spaCy NER ensemble)
    gliner           GLiNER-multi zero-shot span detector
    gpt-4o-mini      OpenAI GPT-4o-mini as zero-shot extractor
    claude-haiku     Anthropic Claude Haiku as zero-shot extractor

Output is a JSON file:
    {
      "detector": "presidio",
      "n_records": 5500,
      "predictions": [
        {
          "record_id": 5,
          "text": "...",
          "gold_entities": [...],
          "predicted_entities": [
            {"entity_type": "...", "entity_string": "...",
             "start": 12, "end": 25, "score": 0.95}
          ]
        },
        ...
      ]
    }

This file is consumed by:
    compute_stratified_f1.py
    compute_kendall_tau.py

Dependencies (per detector):
    Presidio:   pip install presidio-analyzer presidio-anonymizer
                python -m spacy download en_core_web_lg
    GLiNER:     pip install gliner
    OpenAI:     pip install openai  + OPENAI_API_KEY
    Anthropic:  pip install anthropic + ANTHROPIC_API_KEY

Usage:
    python run_detectors.py corpus.json --detector presidio --out preds_presidio.json
    python run_detectors.py corpus.json --detector gliner --out preds_gliner.json
    python run_detectors.py corpus.json --detector gpt-4o-mini --out preds_gpt.json
    python run_detectors.py corpus.json --detector claude-haiku --out preds_claude.json

For LLM detectors, --sample 300 is recommended for the Family K subset to
control cost.
"""

import json
import argparse
import os
import re
import time
import random
from pathlib import Path
from typing import Optional


# Subset of our 51-type taxonomy mapped to types each detector knows about.
# Detectors that emit other type names get normalized via these maps.

PRESIDIO_TO_OURS = {
    "PERSON": "Full_Name",
    "EMAIL_ADDRESS": "Work_Email_Address",
    "PHONE_NUMBER": "Telephone_Numbers_Personal",
    "CREDIT_CARD": "Credit_Card_Numbers",
    "IBAN_CODE": "Customer_Reference_Number",
    "IP_ADDRESS": "Static_IP_Address",
    "DATE_TIME": "Date_Time",
    "US_SSN": "National_Identification_Number",
    "US_DRIVER_LICENSE": "Driving_License_Number",
    "US_PASSPORT": "Passport_Number",
    "LOCATION": "Location",
    "ORGANIZATION": "Org_Name",
    "MEDICAL_LICENSE": "Medical_Information",
    "URL": "Social_Media_Identifiers",
    "NRP": "Nationality",  # Nationality, religious, political (Presidio code)
}

GLINER_LABELS = [
    "person name", "first name", "last name",
    "email address", "phone number", "date of birth",
    "credit card number", "national id number", "passport number",
    "address", "city", "state", "country", "organization",
    "medical condition", "religion", "political party",
    "employee id", "ip address", "social media handle",
    "marital status", "gender", "nationality",
]

GLINER_TO_OURS = {
    "person name": "Full_Name",
    "first name": "First_Given_Name",
    "last name": "Last_Family_Name",
    "email address": "Work_Email_Address",
    "phone number": "Telephone_Numbers_Personal",
    "date of birth": "Date_of_Birth",
    "credit card number": "Credit_Card_Numbers",
    "national id number": "National_Identification_Number",
    "passport number": "Passport_Number",
    "address": "Address_Personal",
    "city": "City",
    "state": "State",
    "country": "Country_of_Residence",
    "organization": "Org_Name",
    "medical condition": "Medical_Information",
    "religion": "Religion",
    "political party": "Political_Party",
    "employee id": "Employee_ID_Number",
    "ip address": "Static_IP_Address",
    "social media handle": "Social_Media_Identifiers",
    "marital status": "Marital_Status",
    "gender": "Gender",
    "nationality": "Nationality",
}


# --------------------------------------------------------------------------
# Presidio
# --------------------------------------------------------------------------

def run_presidio(text: str, analyzer=None) -> list[dict]:
    """Run Presidio analyzer; return normalized predictions."""
    if analyzer is None:
        return []
    try:
        results = analyzer.analyze(text=text, language="en")
    except Exception:
        return []
    preds = []
    for r in results:
        our_type = PRESIDIO_TO_OURS.get(r.entity_type)
        if our_type:
            preds.append({
                "entity_type": our_type,
                "entity_string": text[r.start:r.end],
                "start": r.start,
                "end": r.end,
                "score": float(r.score),
                "_raw_type": r.entity_type,
            })
    return preds


def setup_presidio():
    try:
        from presidio_analyzer import AnalyzerEngine
    except ImportError:
        raise RuntimeError("Install: pip install presidio-analyzer presidio-anonymizer")
    return AnalyzerEngine()


# --------------------------------------------------------------------------
# GLiNER
# --------------------------------------------------------------------------

# def run_gliner(text: str, model=None) -> list[dict]:
#     if model is None:
#         return []
#     try:
#         results = model.predict_entities(text, GLINER_LABELS, threshold=0.5)
#     except Exception:
#         return []
#     preds = []
#     for r in results:
#         our_type = GLINER_TO_OURS.get(r["label"].lower())
#         if our_type:
#             preds.append({
#                 "entity_type": our_type,
#                 "entity_string": r["text"],
#                 "start": r["start"],
#                 "end": r["end"],
#                 "score": float(r.get("score", 0.5)),
#                 "_raw_type": r["label"],
#             })
#     return preds


def run_gliner(text: str, model=None) -> list[dict]:
    """
    GLiNER inference with sliding-window for long inputs.

    GLiNER-multi-PII has a 384-token context limit. We split long texts into
    overlapping character windows (~1200 chars ≈ 300 tokens, 200-char stride
    overlap to catch entities that span window boundaries), run inference on
    each window, adjust offsets back to absolute positions, and deduplicate
    spans that appear in overlap zones (keeping the higher-confidence one).
    """
    if model is None:
        return []

    WINDOW_CHARS = 1200   # ~300 tokens for most scripts
    STRIDE = 1000          # 200-char overlap between consecutive windows

    # Build window offsets
    text_len = len(text)
    if text_len <= WINDOW_CHARS:
        windows = [(0, text_len)]
    else:
        windows = []
        start = 0
        while start < text_len:
            end = min(start + WINDOW_CHARS, text_len)
            windows.append((start, end))
            if end >= text_len:
                break
            start += STRIDE

    # Run GLiNER on each window
    all_preds = []
    for win_start, win_end in windows:
        chunk = text[win_start:win_end]
        try:
            results = model.predict_entities(chunk, GLINER_LABELS, threshold=0.5)
        except Exception:
            continue
        for r in results:
            our_type = GLINER_TO_OURS.get(r["label"].lower())
            if not our_type:
                continue
            # Adjust offsets back to absolute position in original text
            abs_start = win_start + r["start"]
            abs_end = win_start + r["end"]
            all_preds.append({
                "entity_type": our_type,
                "entity_string": r["text"],
                "start": abs_start,
                "end": abs_end,
                "score": float(r.get("score", 0.5)),
                "_raw_type": r["label"],
            })

    # Deduplicate spans appearing in overlap zones.
    # Two preds are duplicates if same type and spans overlap >=70%.
    # Keep the one with higher score.
    if len(all_preds) <= 1:
        return all_preds

    all_preds.sort(key=lambda p: (p["start"], -p["score"]))
    deduped = []
    for p in all_preds:
        is_dup = False
        for q in deduped:
            if p["entity_type"] != q["entity_type"]:
                continue
            overlap = max(0, min(p["end"], q["end"]) - max(p["start"], q["start"]))
            span_p = p["end"] - p["start"]
            span_q = q["end"] - q["start"]
            if span_p == 0 or span_q == 0:
                continue
            iou = overlap / (span_p + span_q - overlap)
            if iou >= 0.7:
                is_dup = True
                # If new pred has higher score, replace
                if p["score"] > q["score"]:
                    deduped.remove(q)
                    deduped.append(p)
                break
        if not is_dup:
            deduped.append(p)

    deduped.sort(key=lambda p: p["start"])
    return deduped

def setup_gliner():
    try:
        from gliner import GLiNER
    except ImportError:
        raise RuntimeError("Install: pip install gliner")
    return GLiNER.from_pretrained("urchade/gliner_multi_pii-v1")


# --------------------------------------------------------------------------
# LLM as detector — shared prompt
# --------------------------------------------------------------------------

LLM_DETECTOR_PROMPT = """You are a PII detector. Given a text passage, extract all PII (Personally Identifiable Information) entities and return them as JSON.

Entity types to extract (use these labels exactly):
Full_Name, First_Given_Name, Last_Family_Name, Work_Email_Address, Personal_Email_Address, Telephone_Numbers_Work, Telephone_Numbers_Personal, Address_Work, Address_Personal, Date_of_Birth, Age, Gender, Marital_Status, Nationality, Religion, Sex_Orientation, Political_Party, Place_of_Birth, Country_of_Residence, State, City, Location, Geolocation_Data, National_Identification_Number, Passport_Number, Driving_License_Number, Tax_Reference_Number, Compensation_and_Salary, Credit_Card_Numbers, Customer_Reference_Number, Account_Statements, Business_Title, Org_Name, Employee_ID_Number, Building_Badge_Card_Number, Performance_Assessment, Disciplinary_Action, Sickness_Day_Records, Professional_Background, Crime, PEP_Status, Trade_Union_Membership, Allergy_Information, Medical_Information, Social_Media_Identifiers, Static_IP_Address, Password, Date_Time, Emergency_Contact_Details, Citizenship_Status, Preferred_Name

For each entity found, output the exact entity_string as it appears in the text.

Output ONLY a JSON object in this format (no other text):
{{
  "entities": [
    {{"entity_type": "<label>", "entity_string": "<verbatim text>"}}
  ]
}}

TEXT:
{text}"""


def parse_llm_predictions(response_text: str, source_text: str) -> list[dict]:
    """Extract entities from LLM JSON output and compute offsets via text.find()."""
    # Find JSON object in response
    m = re.search(r"\{[\s\S]*\}", response_text)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []

    preds = []
    seen_offsets = set()
    for e in data.get("entities", []):
        et = e.get("entity_type", "")
        es = e.get("entity_string", "")
        if not et or not es:
            continue
        # Find each occurrence in source_text
        start = 0
        while True:
            idx = source_text.find(es, start)
            if idx == -1:
                break
            offset_key = (idx, idx + len(es), et)
            if offset_key not in seen_offsets:
                preds.append({
                    "entity_type": et,
                    "entity_string": es,
                    "start": idx,
                    "end": idx + len(es),
                    "score": 1.0,
                })
                seen_offsets.add(offset_key)
            start = idx + 1
    return preds


def run_openai(text: str, client=None, model="gpt-4o-mini") -> list[dict]:
    if client is None:
        return []
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": LLM_DETECTOR_PROMPT.format(text=text[:4000])}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return parse_llm_predictions(resp.choices[0].message.content, text)
    except Exception as e:
        return []


def setup_openai():
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Install: pip install openai")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY env var")
    return OpenAI()


def run_anthropic(text: str, client=None, model="claude-haiku-4-5") -> list[dict]:
    if client is None:
        return []
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": LLM_DETECTOR_PROMPT.format(text=text[:4000])}],
        )
        return parse_llm_predictions(resp.content[0].text, text)
    except Exception:
        return []


def setup_anthropic():
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("Install: pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("Set ANTHROPIC_API_KEY env var")
    return anthropic.Anthropic()


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--detector", required=True,
                   choices=["presidio", "gliner", "gpt-4o-mini", "claude-haiku"])
    p.add_argument("--out", required=True)
    p.add_argument("--sample", type=int, default=None,
                   help="If set, evaluate only this many records (random sample with seed=42)")
    p.add_argument("--delay", type=float, default=0.05,
                   help="Delay between calls (for API detectors)")
    args = p.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)

    if args.sample and args.sample < len(records):
        rng = random.Random(42)
        records = rng.sample(records, args.sample)

    print(f"Running {args.detector} on {len(records):,} records...")

    # Setup detector
    if args.detector == "presidio":
        analyzer = setup_presidio()
        runner = lambda t: run_presidio(t, analyzer)
    elif args.detector == "gliner":
        model = setup_gliner()
        runner = lambda t: run_gliner(t, model)
    elif args.detector == "gpt-4o-mini":
        client = setup_openai()
        runner = lambda t: run_openai(t, client)
    elif args.detector == "claude-haiku":
        client = setup_anthropic()
        runner = lambda t: run_anthropic(t, client)

    predictions = []
    for i, r in enumerate(records):
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(records)}")
        text = r.get("text", "")
        preds = runner(text)
        predictions.append({
            "record_id": r.get("record_id"),
            "language": r.get("axes", {}).get("language"),
            "text": text,
            "gold_entities": r.get("entities", []),
            "predicted_entities": preds,
        })
        if args.detector in ("gpt-4o-mini", "claude-haiku"):
            time.sleep(args.delay)

    output = {
        "detector": args.detector,
        "n_records": len(records),
        "predictions": predictions,
    }
    with open(args.out, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    n_preds = sum(len(p["predicted_entities"]) for p in predictions)
    n_gold = sum(len(p["gold_entities"]) for p in predictions)
    print(f"Done. Gold entities: {n_gold:,}  Predictions: {n_preds:,}")
    print(f"Output: {args.out}")


if __name__ == "__main__":
    main()
