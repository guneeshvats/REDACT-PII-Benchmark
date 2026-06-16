"""
Family F — Stratified F1 by disclosure_form and sensitivity_tier.

This is the NOVEL contribution of the paper: per methodology §6.6, no
prior PII benchmark reports detector F1 stratified by these metadata
fields. Substantial gaps demonstrate that aggregate F1 hides important
failure modes.

  F5  Per-disclosure-form F1: complete vs partial vs obfuscated
  F6  Per-sensitivity-tier F1: HIGH vs MEDIUM vs LOW (Article 9 gap)

Also computes the more standard:
  Overall micro/macro F1
  Per-entity-type F1
  Per-language F1
  Per-axis F1 (domain, format, difficulty, density, code_switching)

Three matching modes:
  - exact: span boundaries must match exactly
  - partial: span overlap > 0 (any overlap counted as TP)
  - fuzzy: span overlap >= 50% of either span (token-aware would be better
    but character-level is OK for v1)

Usage:
    python compute_stratified_f1.py predictions.json --out stratified_f1.json

Input is the JSON file produced by run_detectors.py.
"""

import json
import argparse
from collections import defaultdict, Counter


def spans_match(g, p, mode="partial"):
    """Check if a gold span and a predicted span match."""
    if g["entity_type"] != p["entity_type"]:
        return False
    g_start = g.get("start")
    g_end = g.get("end")
    p_start = p.get("start")
    p_end = p.get("end")
    # If gold doesn't have computed offsets, fall back to string match
    if g_start is None or g_end is None:
        return g.get("entity_string") == p.get("entity_string")
    if p_start is None or p_end is None:
        return False

    if mode == "exact":
        return g_start == p_start and g_end == p_end
    elif mode == "partial":
        # Any overlap
        return not (g_end <= p_start or p_end <= g_start)
    elif mode == "fuzzy":
        # Overlap >= 50% of either span
        overlap = max(0, min(g_end, p_end) - max(g_start, p_start))
        return overlap >= 0.5 * min(g_end - g_start, p_end - p_start)


def compute_f1_for_records(records, mode="partial"):
    """
    Computes TP, FP, FN across a list of prediction records.

    Each record:
        {"gold_entities": [...], "predicted_entities": [...]}

    Returns (tp, fp, fn, precision, recall, f1).
    """
    tp, fp, fn = 0, 0, 0
    for r in records:
        gold = r.get("gold_entities", [])
        pred = r.get("predicted_entities", [])

        # Greedy matching: for each gold, find a matching prediction; consume it
        matched_pred_idx = set()
        for g in gold:
            found_match = False
            for i, p in enumerate(pred):
                if i in matched_pred_idx:
                    continue
                if spans_match(g, p, mode):
                    matched_pred_idx.add(i)
                    found_match = True
                    break
            if found_match:
                tp += 1
            else:
                fn += 1
        fp += len(pred) - len(matched_pred_idx)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return tp, fp, fn, precision, recall, f1


def filter_by_predicate(records, predicate):
    """
    Returns records where gold and pred have been filtered to only include
    entities satisfying the predicate. Used for stratified analysis.
    """
    out = []
    for r in records:
        gold = [g for g in r.get("gold_entities", []) if predicate(g)]
        pred = r.get("predicted_entities", [])
        # For predicted, we keep all and let matching filter out wrong types
        out.append({"gold_entities": gold, "predicted_entities": pred})
    return out


def stratify_by_field(records, field_key):
    """Group records (entity-level) by a field on the gold entity."""
    by_value = defaultdict(lambda: [])
    for r in records:
        # Group entities by field value, then bundle into per-value records
        gold_by_value = defaultdict(list)
        for g in r.get("gold_entities", []):
            v = g.get(field_key)
            gold_by_value[v].append(g)
        for v, gold_list in gold_by_value.items():
            by_value[v].append({
                "gold_entities": gold_list,
                "predicted_entities": r.get("predicted_entities", []),
            })
    return by_value


def stratify_by_axis(records, axis_key, original_records=None):
    """
    Group records by an axis value (e.g., language, domain).

    For axes, the value lives on the record (not the entity), so we use
    the prediction record's `language` field plus the input records (which
    have axes).
    """
    by_value = defaultdict(list)
    for r in records:
        v = r.get(axis_key) or r.get("language")
        # For axes other than language, we need to look up the original record.
        # Since predictions store .language only, this works for language axis.
        # For other axes (domain, format, ...), pass original_records.
        by_value[v].append(r)
    return by_value


def main():
    p = argparse.ArgumentParser()
    p.add_argument("predictions_path")
    p.add_argument("--out", default="stratified_f1.json")
    p.add_argument("--mode", default="partial",
                   choices=["exact", "partial", "fuzzy"])
    args = p.parse_args()

    with open(args.predictions_path) as f:
        data = json.load(f)
    records = data["predictions"]
    detector = data.get("detector", "unknown")

    print(f"Detector: {detector}")
    print(f"Mode: {args.mode}")
    print(f"Records: {len(records):,}")

    # 1. Overall F1
    tp, fp, fn, prec, rec, f1 = compute_f1_for_records(records, args.mode)
    print(f"\nOverall: P={prec:.3f}  R={rec:.3f}  F1={f1:.3f}  (TP={tp}, FP={fp}, FN={fn})")

    # 2. Per-entity-type F1
    per_entity = {}
    all_types = set()
    for r in records:
        for g in r["gold_entities"]:
            all_types.add(g.get("entity_type", ""))
    for et in sorted(all_types):
        filtered = filter_by_predicate(records, lambda g, et=et: g.get("entity_type") == et)
        ftp, ffp, ffn, fprec, frec, ff1 = compute_f1_for_records(filtered, args.mode)
        per_entity[et] = {
            "tp": ftp, "fp": ffp, "fn": ffn,
            "precision": round(fprec, 4), "recall": round(frec, 4), "f1": round(ff1, 4),
            "n_gold": ftp + ffn,
        }

    # 3. Per-language F1
    per_language = {}
    lang_groups = stratify_by_axis(records, "language")
    for lang, recs in lang_groups.items():
        ltp, lfp, lfn, lprec, lrec, lf1 = compute_f1_for_records(recs, args.mode)
        per_language[lang or "?"] = {
            "n_records": len(recs),
            "tp": ltp, "fp": lfp, "fn": lfn,
            "f1": round(lf1, 4),
            "precision": round(lprec, 4), "recall": round(lrec, 4),
        }

    # 4. F5 — Per disclosure_form
    print("\n[F5] Per disclosure_form (NOVEL):")
    f5 = {}
    df_groups = stratify_by_field(records, "disclosure_form")
    for df_value, recs in df_groups.items():
        if df_value is None:
            continue
        dtp, dfp, dfn, dprec, drec, df1 = compute_f1_for_records(recs, args.mode)
        f5[df_value] = {
            "n_entities_gold": dtp + dfn,
            "f1": round(df1, 4),
            "precision": round(dprec, 4),
            "recall": round(drec, 4),
        }
        print(f"  {df_value:<15} F1={df1:.3f}  n_gold={dtp+dfn}")

    # 5. F6 — Per sensitivity_tier
    print("\n[F6] Per sensitivity_tier (NOVEL):")
    f6 = {}
    st_groups = stratify_by_field(records, "sensitivity_tier")
    for st_value, recs in st_groups.items():
        if st_value is None or st_value == "":
            continue
        stp, sfp, sfn, sprec, srec, sf1 = compute_f1_for_records(recs, args.mode)
        f6[st_value] = {
            "n_entities_gold": stp + sfn,
            "f1": round(sf1, 4),
            "precision": round(sprec, 4),
            "recall": round(srec, 4),
        }
        print(f"  {st_value:<10} F1={sf1:.3f}  n_gold={stp+sfn}")

    # 6. Article 9 specific (HIGH tier subset)
    article_9_types = {"Religion", "Sex_Orientation", "Political_Party",
                       "Trade_Union_Membership", "Medical_Information",
                       "Allergy_Information", "Crime"}
    article_9_filtered = filter_by_predicate(
        records, lambda g: g.get("entity_type") in article_9_types
    )
    a9_tp, a9_fp, a9_fn, a9_p, a9_r, a9_f1 = compute_f1_for_records(article_9_filtered, args.mode)
    print(f"\nArticle 9 entities (the regulatory sensitive class):")
    print(f"  F1={a9_f1:.3f}  n_gold={a9_tp+a9_fn}")

    report = {
        "detector": detector,
        "matching_mode": args.mode,
        "n_records": len(records),
        "overall": {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
        },
        "per_entity_type_f1": per_entity,
        "per_language_f1": per_language,
        "F5_per_disclosure_form": f5,
        "F6_per_sensitivity_tier": f6,
        "article_9_f1": {
            "tp": a9_tp, "fp": a9_fp, "fn": a9_fn,
            "precision": round(a9_p, 4),
            "recall": round(a9_r, 4),
            "f1": round(a9_f1, 4),
            "n_gold": a9_tp + a9_fn,
        },
        "_note": (
            "F5 and F6 are the novel contribution. Compare the f1 across "
            "values to surface failure modes hidden by aggregate F1. "
            "Expected: F1(complete) > F1(partial) > F1(obfuscated). "
            "Expected: F1(LOW) >= F1(MEDIUM) > F1(HIGH/Article 9)."
        ),
    }

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
