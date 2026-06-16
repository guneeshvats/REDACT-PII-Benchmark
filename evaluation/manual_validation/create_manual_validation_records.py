#!/usr/bin/env python3
"""Sample the manual-validation sets and build annotation sheets. Run once."""
import json, csv, random, os

# ----------------------------- CONFIG -----------------------------
CORPUS_PATH = "corpus/clean_deduped.json"   # full 13,427-record corpus
OUT_DIR     = "manual_validation"
SEED        = 99
ENTITIES_PER_TYPE      = 10   # Task 1: entities sampled per canonical type
AUDIT_RECORDS_PER_LANG = 1    # Task 2: records per language (25 langs -> 25 records)
ANNOTATORS  = ["A1", "A2"]

# field names in your records — change these if your schema differs
F_ENTITIES, F_TEXT, F_LANG, F_ID = "entities", "text", "language", "id"
F_TYPE, F_STR, F_START, F_END    = "type", "entity_string", "start", "end"
F_DISCLOSED, F_FORM, F_TIER      = "disclosed", "disclosure_form", "sensitivity_tier"
# ------------------------------------------------------------------

def g(d, k, default=""):
    v = d.get(k, default)
    return default if v is None else v

def main():
    random.seed(SEED)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(CORPUS_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"Loaded {len(records)} records from {CORPUS_PATH}")

    # ---- TASK 1: entity-level, stratified by canonical type ----
    by_type = {}
    for ri, rec in enumerate(records):
        for ei, ent in enumerate(rec.get(F_ENTITIES, [])):
            by_type.setdefault(ent.get(F_TYPE, "UNKNOWN"), []).append((ri, ei))

    task1, short_types = [], []
    for etype in sorted(by_type):
        items = by_type[etype]
        if len(items) < ENTITIES_PER_TYPE:
            short_types.append((etype, len(items)))
        for ri, ei in random.sample(items, min(ENTITIES_PER_TYPE, len(items))):
            rec, ent = records[ri], records[ri][F_ENTITIES][ei]
            task1.append({
                "sample_id": f"{etype}__{ri}__{ei}",
                "language": g(rec, F_LANG),
                "text": g(rec, F_TEXT),
                "entity_string": g(ent, F_STR),
                "char_start": g(ent, F_START),
                "char_end": g(ent, F_END),
                "gold_type": g(ent, F_TYPE),
                "gold_disclosed": g(ent, F_DISCLOSED),
                "gold_disclosure_form": g(ent, F_FORM),
                "gold_sensitivity_tier": g(ent, F_TIER),
            })
    random.shuffle(task1)   # break type-clustering to reduce annotator bias

    # ---- TASK 2: full-record audit, stratified by language ----
    by_lang = {}
    for rec in records:
        by_lang.setdefault(g(rec, F_LANG, "unknown"), []).append(rec)
    audit = []
    for lang in sorted(by_lang):
        for rec in random.sample(by_lang[lang], min(AUDIT_RECORDS_PER_LANG, len(by_lang[lang]))):
            audit.append({
                "record_id": g(rec, F_ID, "n/a"),
                "language": lang,
                "text": g(rec, F_TEXT),
                "gold_entity_count": len(rec.get(F_ENTITIES, [])),
            })

    # ---- write identical sheets, one per annotator ----
    t1_cols = ["sample_id","language","text","entity_string","char_start","char_end",
               "gold_type","gold_disclosed","gold_disclosure_form","gold_sensitivity_tier",
               "type","span","disclosed","form","tier","comment"]
    t2_cols = ["record_id","language","text","gold_entity_count",
               "missed_count","missed_list","spurious_list","comment"]
    blank1 = {c:"" for c in ("type","span","disclosed","form","tier","comment")}
    blank2 = {c:"" for c in ("missed_count","missed_list","spurious_list","comment")}

    for ann in ANNOTATORS:
        with open(os.path.join(OUT_DIR, f"task1_entities_{ann}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=t1_cols); w.writeheader()
            for r in task1: w.writerow({**r, **blank1})
        with open(os.path.join(OUT_DIR, f"task2_audit_{ann}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=t2_cols); w.writeheader()
            for r in audit: w.writerow({**r, **blank2})

    # ---- gold keys (for scoring) + summary ----
    json.dump(task1, open(os.path.join(OUT_DIR,"task1_gold_key.json"),"w"), ensure_ascii=False, indent=2)
    json.dump(audit, open(os.path.join(OUT_DIR,"task2_gold_key.json"),"w"), ensure_ascii=False, indent=2)

    print(f"Task 1: {len(task1)} entities across {len(by_type)} types")
    print(f"Task 2: {len(audit)} records across {len(by_lang)} languages")
    if short_types:
        print(f"Types with < {ENTITIES_PER_TYPE} entities (took all available):")
        for t, n in short_types: print(f"   {t}: {n}")
    print(f"Wrote sheets for {ANNOTATORS} into ./{OUT_DIR}/")

if __name__ == "__main__":
    main()