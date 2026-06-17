#!/usr/bin/env python3
"""
aide_geval.py — Three-judge LLM-as-Judge G-Eval for PII Benchmark (v3)

Three frontier LLM judges (GPT-5.2, Claude Sonnet 4.6, Gemini 2.5 Pro)
score each record on 6 dimensions with explicit 4-level anchors per
dimension and explicit bias controls. Reports per-judge scores and
inter-judge Cohen's kappa.

v3 improvements over v2:
  - Each dimension has explicit 4-level (1-2 / 3-4 / 5-7 / 8-10) anchors
  - Explicit bias controls: do not penalize for synthetic-ness alone,
    do not reward verbose annotations, score independently per dimension
  - Calibration examples at the prompt level (one short positive, one
    short negative) per the G-Eval methodology (Liu et al., 2023)
  - Step-by-step instruction asking the judge to reason about each
    dimension before assigning a score (chain-of-thought scoring)
  - Explicit "do not anchor on prior dimensions" instruction
  - Output schema includes brief justification per dimension
    (improves consistency, supports inter-judge analysis)

Usage on AIDE:
  python aide_geval.py --input clean_deduped.json --out geval_report.json --sample 500
"""

import os
import sys
import json
import time
import argparse
import random
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Any

try:
    from aide import AIDE
except ImportError:
    print("ERROR: 'aide' package not found. Run this on the AIDE environment.")
    sys.exit(1)

aide = AIDE()

JUDGES = [
    {"model": "gpt-5.2",            "vendor": "openai",    "label": "gpt5_2"},
    {"model": "claude-sonnet-4-6",  "vendor": "anthropic", "label": "claude_sonnet_4_6"},
    {"model": "gemini-2.5-pro",     "vendor": "google",    "label": "gemini_2_5_pro"},
]

DIMENSION_WEIGHTS = {
    "realism":          2.0,
    "entity_validity":  2.0,
    "type_correctness": 1.5,
    "disclosed_flag":   1.5,
    "tier_correctness": 1.0,
    "span_quality":     1.0,
}

JUDGE_PROMPT = """You are an expert quality judge evaluating a multilingual synthetic PII (Personally Identifiable Information) detection benchmark.

## TASK
You will receive ONE synthetic record containing:
- text: a generated document (chat, log, email, form, etc.)
- annotated_entities: PII entities identified within the text, each with:
  - entity_string: the surface form
  - entity_type: one of 51 canonical types
  - disclosed: boolean (true if a real person's attribute is being shared; false if the entity appears as a category mention, template example, registry entry, or hypothetical)
  - disclosure_form: complete | partial | obfuscated
  - sensitivity_tier: HIGH | MEDIUM | LOW

You must evaluate this record on 6 dimensions, scoring each 1-10 INDEPENDENTLY.

## CRITICAL EVALUATION RULES (READ BEFORE SCORING)

1. **Score each dimension independently.** Do not let a low score on one dimension drag down another. A record can have unrealistic text (low REALISM) but still have perfectly correct entity types (high TYPE_CORRECTNESS).

2. **Do not penalize synthetic-ness alone.** The text is intentionally synthetic. Penalize only if it reads as IMPLAUSIBLE (e.g., a bcrypt hash labeled as a plaintext password sent in email, geo coordinates pointing to the wrong city). A clean, realistic-sounding synthetic record should score 8-10 on REALISM.

3. **Do not anchor on annotation quantity.** A record with 30 well-labeled entities is not better than one with 5 well-labeled entities. Score quality, not volume.

4. **Article 9 sensitivity tier mapping (memorize this for TIER_CORRECTNESS):**
   - HIGH only if the entity_type is Religion, Sex_Orientation, Political_Party, Trade_Union_Membership, Crime, Medical_Information, Allergy_Information, or Ethnicity
   - MEDIUM for direct identifiers: names, emails, phone, address, all account/ID numbers, passport, driving license, tax ref, credit card, IP address, social handles
   - LOW for quasi-identifiers: city, state, country, business title, gender, marital status (when not implicitly Article 9), nationality
   - Date_of_Birth: HIGH (special category)

5. **Category mention vs personal disclosure (critical for DISCLOSED_FLAG):**
   - If "Religion: Catholic" appears in a person's HR record → disclosed=true is correct
   - If "Religion" appears in a moderation note about hate speech targeting religious groups → disclosed=false is correct (no individual's religion is being disclosed)
   - If a VAT number appears in developer documentation as an EXAMPLE → disclosed=false is correct
   - This is the most error-prone field. Score it carefully.

6. **Calibration examples:**
   - GOOD example: a Czech school registration form with DOB "12.05.1998" labeled Date_of_Birth/HIGH/complete/disclosed=true. All 5 fields correct → score 9-10 on all dimensions.
   - BAD example: an Arabic moderation worknote where the literal phrase "sexual orientation" is annotated as Sex_Orientation/HIGH/disclosed=true. The phrase is a category mention, not a personal disclosure → should be disclosed=false. ENTITY_VALIDITY=1-3, DISCLOSED_FLAG=1-3.

## 6 SCORING DIMENSIONS

### 1. REALISM (1-10)
Does the text read like an authentic real-world document?
- 8-10: Indistinguishable from real text in this format/domain. Natural phrasing, plausible details, internally consistent context.
- 5-7: Mostly plausible but with minor synthetic tells (slightly stilted phrasing, generic content, mild inconsistencies).
- 3-4: Clearly AI-generated. Template-like, repetitive, or contains anachronisms.
- 1-2: Nonsensical, internally contradictory, or obviously fake (e.g., a bcrypt hash as a typed password, coordinates pointing to wrong city).

### 2. ENTITY_VALIDITY (1-10)
Are the annotated entities actual PII for a SPECIFIC PERSON (not categories, templates, or hypotheticals)?
- 8-10: All annotated spans are genuine personal disclosures about identifiable individuals.
- 5-7: Most are genuine, but 1-2 entities are category mentions or template content.
- 3-4: Many entities are abstract category references rather than personal disclosures.
- 1-2: The majority of annotations are not actual PII about specific people.

### 3. TYPE_CORRECTNESS (1-10)
Is each entity_type label the correct category from the 51-type taxonomy?
- 8-10: All entity_type labels match what the entity actually is.
- 5-7: Most types correct; 1-2 errors at semantic boundaries (e.g., Tax_Reference vs National_ID, Personal_Email vs Work_Email).
- 3-4: Multiple type misclassifications, including some that should be obvious.
- 1-2: Most entity_type labels are wrong.

### 4. DISCLOSED_FLAG (1-10)
Is the `disclosed` boolean correctly set on each entity?
- 8-10: Boolean correctly distinguishes actual disclosures (true) from category mentions, examples, templates, and hypotheticals (false).
- 5-7: Mostly correct, but 1-2 clear category mentions are incorrectly marked disclosed=true.
- 3-4: Multiple category mentions incorrectly marked disclosed=true, OR multiple genuine disclosures incorrectly marked disclosed=false.
- 1-2: The disclosed field is essentially arbitrary; does not match the text's actual disclosure semantics.

### 5. TIER_CORRECTNESS (1-10)
Is sensitivity_tier (HIGH/MEDIUM/LOW) correctly assigned per the mapping in rule 4 above?
- 8-10: All tiers match the entity_type per the Article 9 / direct / quasi mapping.
- 5-7: Most correct; some contact-info entities (phone, email, address) over-tiered as HIGH when they should be MEDIUM.
- 3-4: Systematic tier errors; Article 9 categories at MEDIUM or direct IDs at HIGH.
- 1-2: Tier assignments appear arbitrary.

### 6. SPAN_QUALITY (1-10)
Are entity spans correctly bounded (no extra context words, no merged multi-entity spans)?
- 8-10: Clean spans. entity_string contains exactly the identifier, no surrounding context.
- 5-7: Some spans include parenthetical translations or context words (e.g., "끝자리 8473" instead of "8473"), but the entity is still identifiable.
- 3-4: Multiple spans include significant extra context, OR multiple entities merged into a single span.
- 1-2: Spans are systematically malformed.

## OUTPUT FORMAT

Think through each dimension BEFORE assigning a score. Then output ONLY a JSON object (no preamble, no markdown fence) in this exact format:

{
  "scores": {
    "realism": <1-10>,
    "entity_validity": <1-10>,
    "type_correctness": <1-10>,
    "disclosed_flag": <1-10>,
    "tier_correctness": <1-10>,
    "span_quality": <1-10>
  },
  "justifications": {
    "realism": "<one short sentence>",
    "entity_validity": "<one short sentence>",
    "type_correctness": "<one short sentence>",
    "disclosed_flag": "<one short sentence>",
    "tier_correctness": "<one short sentence>",
    "span_quality": "<one short sentence>"
  },
  "top_issue": "<single biggest issue with this record, or 'None' if 8+ on all dimensions>",
  "verdict": "<EXCELLENT | GOOD | ACCEPTABLE | POOR | FAIL>"
}

Verdict mapping (compute from weighted average):
- EXCELLENT: weighted average >= 8.5
- GOOD: 7.0 - 8.4
- ACCEPTABLE: 5.5 - 6.9
- POOR: 3.5 - 5.4
- FAIL: < 3.5"""


def extract_content_from_response(response: Any, vendor: str) -> Optional[str]:
    """Vendor-aware content extraction including AIDE-wrapped Anthropic shape."""
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return response

    if not isinstance(response, dict):
        return None

    # AIDE-wrapped Anthropic shape: output.message.content[0].text
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

    # Gemini shape
    if "candidates" in response:
        cands = response.get("candidates", [])
        if isinstance(cands, list) and cands:
            first = cands[0]
            if isinstance(first, dict):
                gcontent = first.get("content", {})
                if isinstance(gcontent, dict):
                    parts = gcontent.get("parts", [])
                    if isinstance(parts, list) and parts:
                        text = parts[0].get("text", "")
                        if text:
                            return text

    if "text" in response:
        return response["text"]
    return None


def make_payload(model: str, vendor: str, system_prompt: str, user_msg: str):
    """Vendor-specific payload construction."""
    if vendor == "google":
        return {
            "contents": {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n---\n\nRECORD TO EVALUATE:\n\n{user_msg}"}]
            },
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 3000,
            }
        }
    if model == "gpt-5.2":
        return {
            "messages": [
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                {"role": "user",   "content": [{"type": "text", "text": user_msg}]}
            ],
            "max_completion_tokens": 3000,
        }
    return {
        "messages": [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user",   "content": [{"type": "text", "text": user_msg}]}
        ],
        "temperature": 0.1,
        "max_tokens": 1500,
    }


def call_judge(judge: Dict, user_msg: str, max_retries: int = 3) -> Optional[Dict]:
    model = judge["model"]
    vendor = judge["vendor"]

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(2 ** attempt)
            payload = make_payload(model, vendor, JUDGE_PROMPT, user_msg)
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
            if isinstance(parsed, dict) and "scores" in parsed:
                return parsed
        except (json.JSONDecodeError, Exception) as e:
            if attempt == max_retries - 1:
                print(f"    {model} failed: {str(e)[:120]}")

    return None


def build_record_summary(record: Dict, max_entities: int = 12) -> str:
    text = record.get("text", "")
    if len(text) > 2200:
        text = text[:2200] + " ... [truncated]"

    axes = record.get("axes", {})
    entities = record.get("entities", [])[:max_entities]

    summary = {
        "record_id": record.get("record_id", ""),
        "language": axes.get("language", ""),
        "domain": axes.get("domain", ""),
        "format": axes.get("format", ""),
        "text": text,
        "annotated_entities": [
            {
                "entity_string": e.get("entity_string", ""),
                "entity_type": e.get("entity_type", ""),
                "disclosed": e.get("disclosed", None),
                "disclosure_form": e.get("disclosure_form", ""),
                "sensitivity_tier": e.get("sensitivity_tier", ""),
            }
            for e in entities
        ],
    }
    return json.dumps(summary, indent=2, ensure_ascii=False)


def cohens_kappa(a: List[int], b: List[int]) -> float:
    if not a or len(a) != len(b):
        return 0.0
    n = len(a)
    def bin_score(s):
        if s <= 4: return 0
        if s <= 7: return 1
        return 2
    ba = [bin_score(s) for s in a]
    bb = [bin_score(s) for s in b]
    agree = sum(1 for x, y in zip(ba, bb) if x == y)
    p_o = agree / n
    ca = Counter(ba)
    cb = Counter(bb)
    p_e = sum((ca[k] / n) * (cb[k] / n) for k in set(list(ca.keys()) + list(cb.keys())))
    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


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


def run(input_path: str, out_path: str, sample_size: int):
    print("=" * 70)
    print("AIDE G-EVAL v3 — Three-Judge LLM-as-Judge with Bias Controls")
    print("=" * 70)
    print(f"Judges: {[j['model'] for j in JUDGES]}")
    print(f"Input:  {input_path}")
    print(f"Output: {out_path}")
    print(f"Sample size: {sample_size}")
    print()

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else data.get("records", [])
    print(f"Loaded {len(records)} records")

    sample_indices = stratified_sample(records, sample_size)
    print(f"Stratified sample of {len(sample_indices)} records selected (by language)")
    print()

    all_results = []
    judge_scores = {j["label"]: defaultdict(list) for j in JUDGES}

    for i, rec_idx in enumerate(sample_indices):
        rec = records[rec_idx]
        rec_id = rec.get("record_id", f"idx_{rec_idx}")
        lang = rec.get("axes", {}).get("language", "?")
        print(f"[{i+1}/{len(sample_indices)}] record_id={rec_id} (lang={lang})")

        user_msg = build_record_summary(rec)
        record_result = {
            "record_index": rec_idx,
            "record_id": rec_id,
            "language": lang,
            "judges": {},
        }

        for judge in JUDGES:
            judgment = call_judge(judge, user_msg)
            if judgment:
                record_result["judges"][judge["label"]] = judgment
                for dim, score in judgment.get("scores", {}).items():
                    judge_scores[judge["label"]][dim].append(score)
                print(f"    {judge['model']}: {judgment.get('verdict', '?')}")
            else:
                record_result["judges"][judge["label"]] = None
                print(f"    {judge['model']}: FAILED")
            time.sleep(0.3)

        cross_judge = {}
        for dim in DIMENSION_WEIGHTS:
            dim_vals = []
            for jl in [j["label"] for j in JUDGES]:
                j_result = record_result["judges"].get(jl)
                if j_result and "scores" in j_result:
                    dim_vals.append(j_result["scores"].get(dim, None))
            dim_vals = [v for v in dim_vals if v is not None]
            cross_judge[dim] = sum(dim_vals) / len(dim_vals) if dim_vals else None

        weighted_sum = 0
        total_w = 0
        for dim, w in DIMENSION_WEIGHTS.items():
            if cross_judge[dim] is not None:
                weighted_sum += cross_judge[dim] * w
                total_w += w
        record_result["cross_judge_mean"] = cross_judge
        record_result["weighted_average"] = round(weighted_sum / total_w, 2) if total_w else None
        all_results.append(record_result)

        if (i + 1) % 25 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"in_progress": True, "completed": i + 1, "results": all_results}, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("AGGREGATE STATISTICS")
    print("=" * 70)

    per_judge_stats = {}
    for j in JUDGES:
        jl = j["label"]
        ds = judge_scores[jl]
        per_judge_stats[jl] = {
            dim: {
                "mean": round(sum(vs) / len(vs), 2) if vs else None,
                "n": len(vs),
            }
            for dim, vs in ds.items()
        }
        print(f"\n{j['model']}:")
        for dim, stats in per_judge_stats[jl].items():
            print(f"  {dim}: mean={stats['mean']} (n={stats['n']})")

    print()
    print("Inter-judge Cohen's kappa (per dimension):")
    judge_labels = [j["label"] for j in JUDGES]
    interjudge_kappa = {}
    for ji in range(len(judge_labels)):
        for jj in range(ji + 1, len(judge_labels)):
            ja, jb = judge_labels[ji], judge_labels[jj]
            pair_key = f"{ja}_vs_{jb}"
            interjudge_kappa[pair_key] = {}
            for dim in DIMENSION_WEIGHTS:
                a, b = [], []
                for r in all_results:
                    sa = r["judges"].get(ja, {}) and r["judges"][ja].get("scores", {}).get(dim)
                    sb = r["judges"].get(jb, {}) and r["judges"][jb].get("scores", {}).get(dim)
                    if sa is not None and sb is not None:
                        a.append(sa)
                        b.append(sb)
                k = cohens_kappa(a, b)
                interjudge_kappa[pair_key][dim] = round(k, 3)
            print(f"  {pair_key}: {interjudge_kappa[pair_key]}")

    overall_weighted = [r["weighted_average"] for r in all_results if r.get("weighted_average")]
    overall_mean = round(sum(overall_weighted) / len(overall_weighted), 2) if overall_weighted else None
    print()
    print(f"Cross-judge overall weighted mean (1-10): {overall_mean}")

    final_report = {
        "judges": [j["model"] for j in JUDGES],
        "dimension_weights": DIMENSION_WEIGHTS,
        "n_records_judged": len(all_results),
        "overall_cross_judge_weighted_mean": overall_mean,
        "per_judge_stats": per_judge_stats,
        "interjudge_cohens_kappa": interjudge_kappa,
        "results": all_results,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--sample", type=int, default=500)
    args = p.parse_args()
    run(args.input, args.out, args.sample)
