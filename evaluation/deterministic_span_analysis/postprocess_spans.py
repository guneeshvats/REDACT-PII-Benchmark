"""
Post-processing script for GT annotation output.

Reads an existing GT annotation JSONL that has model_responses but empty spans,
re-parses the responses correctly, and recomputes per_model_spans and gt_entities.

Usage:
    python postprocess_spans.py \
        --input  /srv/.../prod032_task_gt.jsonl \
        --output /srv/.../prod032_task_gt_fixed.jsonl
"""

import argparse
import json
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ── Inline parsing logic (no dependency on broken server src/) ─────────────

def _try_parse_json(text):
    try:
        return json.loads(text, strict=False)
    except Exception:
        return None


def _try_parse_to_dict(text):
    """
    Handles the encoding chain seen in saved DART output files:
      RAW string in JSONL  : '"{\\n \\"PERSON\\"...'
      After json.loads     : '{\n "PERSON"...'   (still has \\")
      After replace+loads  : {"PERSON": [...]}   ← dict we want
    """
    # Step 1: parse the outer layer
    result = _try_parse_json(text)

    # Already a dict — done
    if isinstance(result, dict):
        return result

    # Got a string — try re-parsing directly first (preserves valid inner \" escaping),
    # then fall back to replacing \" if direct re-parse fails.
    if isinstance(result, str):
        r2 = _try_parse_json(result)
        if isinstance(r2, dict):
            return r2
        r2b = _try_parse_json(result.replace('\\"', '"'))
        if isinstance(r2b, dict):
            return r2b
        # Another level deep
        if isinstance(r2b, str):
            r3 = _try_parse_json(r2b.replace('\\"', '"'))
            if isinstance(r3, dict):
                return r3

    # Try unescaping the original first, then parse
    unescaped = text.replace('\\"', '"')
    r4 = _try_parse_json(unescaped)
    if isinstance(r4, dict):
        return r4
    if isinstance(r4, str):
        r5 = _try_parse_json(r4.replace('\\"', '"'))
        if isinstance(r5, dict):
            return r5

    return None


def parse_response(content):
    import re
    if not content:
        return {}
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    parsed = _try_parse_to_dict(cleaned)
    if parsed is None:
        m = re.search(r"\{[\s\S]+\}", content)
        if m:
            parsed = _try_parse_to_dict(m.group())
    if parsed is None:
        return {}

    known_types = {
        "PERSON", "ORGANIZATION", "LOCATION", "CITY", "STATE", "COUNTRY",
        "ADDRESS", "DATE_TIME", "DOB", "AGE", "JOB_POSITION", "SALARY",
        "PASSWORD", "RELIGION", "NATIONALITY", "POLITICAL_PARTY", "CRIME",
        "SEX_ORIENTATION", "EMAIL", "PHONE", "SSN",
    }

    if "entities_extracted" in parsed:
        return parsed["entities_extracted"]

    entities = {}
    for key, val in parsed.items():
        if key.upper() in known_types:
            if isinstance(val, list):
                entities[key.upper()] = val
            elif isinstance(val, str):
                entities[key.upper()] = [val]
    return entities


def normalize_entities(entities):
    normalized = {}
    for etype, elist in entities.items():
        norm_list = []
        for e in elist:
            if isinstance(e, str):
                norm_list.append({"text": e, "context": ""})
            elif isinstance(e, dict):
                norm_list.append({"text": e.get("text", ""), "context": e.get("context", "")})
        if norm_list:
            normalized[etype] = norm_list
    return normalized


# ── Span computation (inline, no import needed) ───────────────────────────

import re
import unicodedata


def _is_cjk(ch):
    try:
        name = unicodedata.name(ch, "")
        return any(s in name for s in ("CJK", "HANGUL", "HIRAGANA", "KATAKANA"))
    except ValueError:
        return False


def _boundary_ok(text, s, e):
    if s > 0:
        ch = text[s - 1]
        if ch.isalnum() or ch == '@':
            if not _is_cjk(text[s - 1]):
                return False
        if ch == '.' and s >= 2 and text[s - 2].isalnum():
            if not _is_cjk(text[s - 1]):
                return False
    if e < len(text):
        ch = text[e]
        if ch.isalnum() or ch == '@':
            if not _is_cjk(text[e]):
                return False
        if ch == '.' and e + 1 < len(text) and text[e + 1].isalnum():
            if not _is_cjk(text[e]):
                return False
    return True


def find_spans(text, entities):
    if not text or not entities:
        return []
    norm = unicodedata.normalize("NFC", text)
    spans = []
    covered = set()
    all_ents = []
    for etype, elist in entities.items():
        for e in elist:
            val = e.get("text", "") if isinstance(e, dict) else str(e)
            val_norm = unicodedata.normalize("NFC", val.strip())
            if val_norm:
                all_ents.append((etype, val_norm))
    all_ents.sort(key=lambda x: len(x[1]), reverse=True)

    for etype, val_norm in all_ents:
        pattern = re.escape(val_norm)
        positions = [(m.start(), m.end()) for m in re.finditer(pattern, norm)]
        if not positions:
            positions = [(m.start(), m.end()) for m in re.finditer(pattern, norm, re.IGNORECASE)]
        for s, e in positions:
            if not _boundary_ok(norm, s, e):
                continue
            if any(i in covered for i in range(s, e)):
                continue
            spans.append({"start": s, "end": e, "type": etype, "text": norm[s:e]})
            for i in range(s, e):
                covered.add(i)
            break
    spans.sort(key=lambda x: x["start"])
    return spans


def merge_spans(span_lists, min_agreement=2):
    all_spans = []
    for model_idx, spans in enumerate(span_lists):
        for sp in spans:
            all_spans.append({**sp, "model": model_idx})

    merged = []
    used = set()
    for i, sp in enumerate(all_spans):
        if i in used:
            continue
        group = [sp]
        for j, sp2 in enumerate(all_spans):
            if j <= i or j in used:
                continue
            if sp2["type"] == sp["type"] and sp2["model"] != sp["model"]:
                if sp["start"] < sp2["end"] and sp2["start"] < sp["end"]:
                    group.append(sp2)
                    used.add(j)
        models_in_group = {s["model"] for s in group}
        if len(models_in_group) >= min_agreement:
            best = max(group, key=lambda x: x["end"] - x["start"])
            merged.append({"start": best["start"], "end": best["end"],
                           "type": best["type"], "text": best["text"]})
        used.add(i)
    merged.sort(key=lambda x: x["start"])
    return merged


# ── Main ──────────────────────────────────────────────────────────────────

def process_record(record):
    text = record.get("input_text", "")
    model_responses = record.get("model_responses", {})

    model_spans = {}
    for model_name, raw in model_responses.items():
        entities = parse_response(raw)
        entities = normalize_entities(entities)
        spans = find_spans(text, entities)
        model_spans[model_name] = spans
        logger.debug(f"  {model_name}: {len(spans)} spans, keys={list(entities.keys())}")

    gt_entities = merge_spans(list(model_spans.values()), min_agreement=2)

    consensus_entities = {}
    for sp in gt_entities:
        etype = sp["type"]
        if etype not in consensus_entities:
            consensus_entities[etype] = []
        consensus_entities[etype].append(sp["text"])

    record["per_model_spans"] = model_spans
    record["gt_entities"] = gt_entities
    record["consensus_entities"] = consensus_entities
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = []
    with open(args.input) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    logger.info(f"Loaded {len(records)} records from {args.input}")

    fixed = 0
    with open(args.output, "w") as f:
        for i, rec in enumerate(records):
            rec = process_record(rec)
            f.write(json.dumps(rec) + "\n")
            n = len(rec["gt_entities"])
            if n > 0:
                fixed += 1
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i+1}/{len(records)}, records with gt_entities: {fixed}")

    logger.info(f"Done. {fixed}/{len(records)} records have gt_entities.")
    logger.info(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()
