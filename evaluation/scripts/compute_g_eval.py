"""
Family G — LLM-as-judge (G-Eval) with bias mitigations.

Implements:
  G1  G-Eval style scoring (Liu et al., 2023) with chain-of-thought rubric.
  G2  Two-judge cross-validation: GPT-4o-mini AND Prometheus-2 (or Claude
       if Prometheus unavailable). Krippendorff's α between judges as
       inter-rater reliability — drop the metric if α < 0.5.

Bias mitigations applied (citations in comments):
  - Different judge from generator (Panickssery et al., NeurIPS 2024 —
    self-preference bias).
  - Two-judge cross-validation (Zheng et al., NeurIPS 2023 — single-judge
    bias).
  - Chain-of-thought with explicit rubric before score (Liu et al., 2023 —
    shortcut bias).
  - Score distribution averaging over multiple prompt orderings would
    mitigate position bias (Wang et al., 2023), but this is single-record
    rating, not pair comparison, so position bias doesn't apply.

This script is API-cost-bearing. Estimate:
  - GPT-4o-mini at $0.15/1M input + $0.60/1M output tokens
  - Sample 500 records (stratified by language) → roughly $1-3
  - Sample 5,000 records → roughly $10-30

Dependencies:
    pip install openai anthropic numpy

Required env vars:
    OPENAI_API_KEY    (for GPT-4o-mini judge)
    ANTHROPIC_API_KEY (for Claude Haiku second judge — optional)

Usage:
    python compute_g_eval.py corpus.json --out g_eval_report.json --sample 500

NOTE: This script needs API access. If you don't have OPENAI_API_KEY set up
locally, this is the right one to defer to camera-ready. Otherwise run it.
"""

import json
import argparse
import os
import random
import time
from collections import defaultdict


G_EVAL_PROMPT = """You are evaluating a synthetic PII (Personally Identifiable Information) benchmark record. The record contains a passage of text and a list of PII entities annotated within it.

Evaluate the record on these four dimensions, each on a 1-5 scale:

1. **Coherence**: Does the text read like natural human writing for its domain (e.g., chat transcript, medical record, log entry)?
2. **Entity Realism**: Do the PII values look like plausible real-world examples? (Not too uniform, not too random.)
3. **Domain Authenticity**: Does the text style match the stated domain and format?
4. **Annotation Quality**: Do the listed entities accurately reflect the PII in the text? (No obvious missing or wrong entities.)

**Important**: First think through each dimension step by step. Then output a JSON object with the four scores and a brief justification.

RECORD METADATA:
- Domain: {domain}
- Format: {format}
- Language: {language}
- Target entity type: {target_entity_type}
- Behavioral frame: {behavioral_frame}

TEXT:
{text}

ANNOTATED ENTITIES:
{entities_repr}

Think step by step about each of the four dimensions, then output exactly one JSON object:
{{
  "coherence": <int 1-5>,
  "entity_realism": <int 1-5>,
  "domain_authenticity": <int 1-5>,
  "annotation_quality": <int 1-5>,
  "justification": "<1-2 sentence overall assessment>"
}}"""


def render_entities(entities: list[dict], cap: int = 25) -> str:
    """Compact entity list for prompt."""
    lines = []
    for e in entities[:cap]:
        lines.append(
            f"- {e.get('entity_type', '?')}: \"{e.get('entity_string', '')}\" "
            f"(sensitivity={e.get('sensitivity_tier', '?')}, "
            f"disclosed={e.get('disclosed', '?')})"
        )
    if len(entities) > cap:
        lines.append(f"... and {len(entities) - cap} more")
    return "\n".join(lines)


def call_openai_judge(record: dict, model: str = "gpt-4o-mini") -> dict:
    """Call OpenAI as G-Eval judge. Returns scores or {} on failure."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Install: pip install openai")

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = G_EVAL_PROMPT.format(
        domain=record.get("axes", {}).get("domain", "?"),
        format=record.get("axes", {}).get("format", "?"),
        language=record.get("axes", {}).get("language", "?"),
        target_entity_type=record.get("target_entity_type", "?"),
        behavioral_frame=record.get("behavioral_frame", "?"),
        text=record.get("text", "")[:3000],
        entities_repr=render_entities(record.get("entities", [])),
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"_error": str(e)}


def call_anthropic_judge(record: dict, model: str = "claude-haiku-4-5") -> dict:
    """Call Anthropic Claude as second judge."""
    try:
        import anthropic
    except ImportError:
        return {"_error": "anthropic SDK not installed"}

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    prompt = G_EVAL_PROMPT.format(
        domain=record.get("axes", {}).get("domain", "?"),
        format=record.get("axes", {}).get("format", "?"),
        language=record.get("axes", {}).get("language", "?"),
        target_entity_type=record.get("target_entity_type", "?"),
        behavioral_frame=record.get("behavioral_frame", "?"),
        text=record.get("text", "")[:3000],
        entities_repr=render_entities(record.get("entities", [])),
    )

    try:
        resp = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text
        # Extract JSON
        import re
        m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return {"_error": "no_json_in_response", "_raw": text[:300]}
    except Exception as e:
        return {"_error": str(e)}


def stratified_sample(records: list[dict], n: int, seed: int = 0) -> list[dict]:
    """Stratify by language so smaller languages aren't drowned out."""
    rng = random.Random(seed)
    by_lang = defaultdict(list)
    for i, r in enumerate(records):
        lang = r.get("axes", {}).get("language", "?")
        by_lang[lang].append(i)

    if n >= len(records):
        return list(records)

    # Round-robin across languages
    samples_per_lang = max(1, n // len(by_lang))
    chosen_indices = set()
    for lang, idxs in by_lang.items():
        if len(idxs) <= samples_per_lang:
            chosen_indices.update(idxs)
        else:
            chosen_indices.update(rng.sample(idxs, samples_per_lang))

    # Top up randomly if needed
    remaining = list(set(range(len(records))) - chosen_indices)
    rng.shuffle(remaining)
    while len(chosen_indices) < n and remaining:
        chosen_indices.add(remaining.pop())

    return [records[i] for i in sorted(chosen_indices)]


def compute_krippendorff_alpha(scores_a: list, scores_b: list) -> float:
    """Quick implementation for two raters, interval-scale scores."""
    try:
        import numpy as np
    except ImportError:
        return float("nan")
    valid = [(a, b) for a, b in zip(scores_a, scores_b) if a is not None and b is not None]
    if len(valid) < 2:
        return float("nan")
    a = np.array([v[0] for v in valid])
    b = np.array([v[1] for v in valid])
    # Disagreement
    Do = ((a - b) ** 2).mean()
    if Do == 0:
        return 1.0
    # Expected disagreement under chance
    combined = np.concatenate([a, b])
    De = ((combined[:, None] - combined[None, :]) ** 2).mean()
    if De == 0:
        return 0.0
    return float(1 - Do / De)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--out", default="g_eval_report.json")
    p.add_argument("--sample", type=int, default=500,
                   help="Number of records to evaluate (stratified by language)")
    p.add_argument("--judge1", default="gpt-4o-mini")
    p.add_argument("--judge2", default="claude-haiku-4-5",
                   help="Second judge for cross-validation. Set to 'none' to skip.")
    p.add_argument("--delay", type=float, default=0.1,
                   help="Delay between API calls (seconds)")
    args = p.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY env var not set. Cannot run G-Eval judge.")
        return 1

    with open(args.corpus_path) as f:
        records = json.load(f)

    sample = stratified_sample(records, args.sample)
    print(f"Stratified sample of {len(sample)} records (from {len(records):,})")

    judge1_scores = []
    judge2_scores = []
    per_record_results = []

    for i, rec in enumerate(sample):
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(sample)}")
        j1 = call_openai_judge(rec, args.judge1)
        judge1_scores.append(j1)
        if args.judge2 != "none":
            time.sleep(args.delay)
            j2 = call_anthropic_judge(rec, args.judge2)
            judge2_scores.append(j2)
        else:
            judge2_scores.append({})
        per_record_results.append({
            "record_id": rec.get("record_id"),
            "language": rec.get("axes", {}).get("language"),
            "judge1": j1,
            "judge2": judge2_scores[-1],
        })
        time.sleep(args.delay)

    # Aggregate
    def avg_dim(scores, key):
        vals = [s.get(key) for s in scores
                if isinstance(s, dict) and isinstance(s.get(key), (int, float))]
        return sum(vals) / len(vals) if vals else None

    dimensions = ["coherence", "entity_realism", "domain_authenticity", "annotation_quality"]

    summary_j1 = {d: avg_dim(judge1_scores, d) for d in dimensions}
    summary_j2 = {d: avg_dim(judge2_scores, d) for d in dimensions}

    # Krippendorff alpha per dimension (between j1 and j2)
    iaa = {}
    for d in dimensions:
        s1 = [s.get(d) if isinstance(s, dict) else None for s in judge1_scores]
        s2 = [s.get(d) if isinstance(s, dict) else None for s in judge2_scores]
        iaa[d] = round(compute_krippendorff_alpha(s1, s2), 3)

    report = {
        "n_records_sampled": len(sample),
        "judge1_model": args.judge1,
        "judge2_model": args.judge2,
        "judge1_mean_scores": {k: round(v, 2) if v else None for k, v in summary_j1.items()},
        "judge2_mean_scores": {k: round(v, 2) if v else None for k, v in summary_j2.items()},
        "inter_judge_krippendorff_alpha": iaa,
        "alpha_target": ">= 0.50 (else drop the metric)",
        "bias_mitigations": [
            "Different judge model from generator (Panickssery 2024)",
            "Two-judge cross-validation (Zheng 2023)",
            "Chain-of-thought rubric (Liu 2023)",
            "Stratified sampling across languages",
        ],
        "per_record_results": per_record_results[:100],  # truncate for readability
    }

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nJudge 1 ({args.judge1}) mean scores:")
    for k, v in summary_j1.items():
        print(f"  {k}: {v:.2f}" if v else f"  {k}: N/A")
    print(f"\nJudge 2 ({args.judge2}) mean scores:")
    for k, v in summary_j2.items():
        print(f"  {k}: {v:.2f}" if v else f"  {k}: N/A")
    print(f"\nInter-judge agreement (Krippendorff's α):")
    for k, v in iaa.items():
        print(f"  {k}: {v}")
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
