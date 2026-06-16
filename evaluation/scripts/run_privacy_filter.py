# #!/usr/bin/env python3
# """
# Run OpenAI Privacy Filter (openai/privacy-filter) over the locked 1,000-record
# PII eval subset and write predictions in the SAME schema as the GPT/Claude files.

# Outputs RAW Privacy Filter labels (the 8 categories) + char offsets.
# Do NOT map to the 51-type taxonomy here — the scorer does that mapping.

# Setup:  pip install "transformers>=4.44" torch --upgrade
# Run:    python run_privacy_filter.py   (works from scripts/ or anywhere in the project)
# """
# import os, json, time, torch
# from collections import Counter
# from transformers import AutoTokenizer, AutoModelForTokenClassification

# # --- Paths: resolved relative to THIS script's location, not your cwd.
# # Assumes layout:  PII_Benchmark_Analysis/{scripts/this_file, corpus/, predictions/}
# HERE = os.path.dirname(os.path.abspath(__file__))
# ROOT = os.path.dirname(HERE)                      # project root (parent of scripts/)
# GOLD = os.path.join(ROOT, "corpus", "clean_deduped_sample1000.json")
# OUT  = os.path.join(ROOT, "predictions", "privacy_filter_predictions.jsonl")
# os.makedirs(os.path.dirname(OUT), exist_ok=True)

# MODEL  = "openai/privacy-filter"
# MAXLEN = 4096          # most records are short; raise if you hit truncation
# LIMIT  = None           # <-- TIMING/SANITY: set to None for the full 1,000 run

# device = "mps" if torch.backends.mps.is_available() else "cpu"
# print(f"Device: {device}\nGOLD: {GOLD}\nOUT:  {OUT}")

# tok = AutoTokenizer.from_pretrained(MODEL)
# model = AutoModelForTokenClassification.from_pretrained(
#     MODEL, dtype=torch.float32).to(device).eval()
# id2label = model.config.id2label
# assert tok.is_fast, "Need a fast tokenizer for offset_mapping"

# def decode_spans(text, offsets, labels):
#     """BIOES token labels -> character spans."""
#     spans, cur = [], None
#     for (s, e), lab in zip(offsets, labels):
#         if s == e:                     # special token
#             continue
#         if lab in (None, "O"):
#             if cur: spans.append(cur); cur = None
#             continue
#         pref, _, base = lab.partition("-")
#         if base == "":
#             base, pref = pref, "I"
#         if pref in ("B", "S"):
#             if cur: spans.append(cur)
#             cur = [base, s, e]
#         elif pref in ("I", "E"):
#             if cur and cur[0] == base:
#                 cur[2] = e
#             else:
#                 cur = [base, s, e]
#         if pref in ("S", "E"):
#             if cur: spans.append(cur); cur = None
#     if cur: spans.append(cur)
#     return spans

# def lang_of(r):
#     a = r.get("axes")
#     return (a or {}).get("language") if isinstance(a, dict) else r.get("language")

# recs = json.load(open(GOLD, encoding="utf-8"))
# if LIMIT:
#     recs = recs[:LIMIT]
#     print(f"*** TIMING MODE: first {LIMIT} records. Set LIMIT=None for the full run. ***")

# t0 = time.time(); n_ent = 0
# with open(OUT, "w", encoding="utf-8") as f:
#     for i, r in enumerate(recs):
#         text = r["text"]
#         enc = tok(text, return_offsets_mapping=True, return_tensors="pt",
#                   truncation=True, max_length=MAXLEN)
#         offsets = enc.pop("offset_mapping")[0].tolist()
#         enc = {k: v.to(device) for k, v in enc.items()}
#         with torch.no_grad():
#             logits = model(**enc).logits[0]
#         labels = [id2label[p] for p in logits.argmax(-1).tolist()]
#         spans = decode_spans(text, offsets, labels)
#         ents = [{"entity_type": base, "start": s, "end": e,
#                  "entity_string": text[s:e]} for base, s, e in spans]
#         n_ent += len(ents)
#         f.write(json.dumps({
#             "record_id": r.get("record_id"),
#             "record_index": i,
#             "language": lang_of(r),
#             "entities": ents,
#         }, ensure_ascii=False) + "\n")
#         if i % 50 == 0:
#             print(f"  {i}/{len(recs)} records")

# dt = time.time() - t0
# print(f"\nDONE -> {OUT} | {len(recs)} records, {n_ent} entities | {dt:.1f}s "
#       f"({dt/max(1,len(recs)):.2f}s/record)")
# if LIMIT:
#     print(f"Projected full 1,000-record run: ~{dt/len(recs)*1000/60:.1f} min")
# c = Counter()
# for line in open(OUT, encoding="utf-8"):
#     for e in json.loads(line)["entities"]:
#         c[e["entity_type"]] += 1
# print("Predicted-label histogram:", dict(c))


#!/usr/bin/env python3
"""
RESUME the Privacy Filter run: keeps records already in the output file,
processes only the missing ones, and frees MPS memory each record to avoid
the swap-induced slowdown. Ctrl-C the original run BEFORE starting this.

Run:  python resume_privacy_filter.py
"""
import os, json, time, torch
from collections import Counter
from transformers import AutoTokenizer, AutoModelForTokenClassification

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GOLD = os.path.join(ROOT, "corpus", "clean_deduped_sample1000.json")
OUT  = os.path.join(ROOT, "predictions", "privacy_filter_predictions.jsonl")
MODEL  = "openai/privacy-filter"
MAXLEN = 4096

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Device: {device}")

# --- which record_index values are already done (robust to a truncated last line)
done = set()
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        try: done.add(json.loads(line)["record_index"])
        except Exception: pass  # skip a partial/corrupt trailing line
print(f"Already done: {len(done)} records")

tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForTokenClassification.from_pretrained(MODEL, dtype=torch.float32).to(device).eval()
id2label = model.config.id2label

def decode_spans(text, offsets, labels):
    spans, cur = [], None
    for (s, e), lab in zip(offsets, labels):
        if s == e: continue
        if lab in (None, "O"):
            if cur: spans.append(cur); cur = None
            continue
        pref, _, base = lab.partition("-")
        if base == "": base, pref = pref, "I"
        if pref in ("B", "S"):
            if cur: spans.append(cur)
            cur = [base, s, e]
        elif pref in ("I", "E"):
            if cur and cur[0] == base: cur[2] = e
            else: cur = [base, s, e]
        if pref in ("S", "E"):
            if cur: spans.append(cur); cur = None
    if cur: spans.append(cur)
    return spans

def lang_of(r):
    a = r.get("axes")
    return (a or {}).get("language") if isinstance(a, dict) else r.get("language")

recs = json.load(open(GOLD, encoding="utf-8"))
todo = [(i, r) for i, r in enumerate(recs) if i not in done]
print(f"Remaining: {len(todo)} records")

t0 = time.time()
with open(OUT, "a", encoding="utf-8") as f:          # APPEND, don't overwrite
    for k, (i, r) in enumerate(todo):
        text = r["text"]
        enc = tok(text, return_offsets_mapping=True, return_tensors="pt",
                  truncation=True, max_length=MAXLEN)
        ntok = enc["input_ids"].shape[1]
        offsets = enc.pop("offset_mapping")[0].tolist()
        enc = {kk: v.to(device) for kk, v in enc.items()}
        with torch.no_grad():
            logits = model(**enc).logits[0]
        labels = [id2label[p] for p in logits.argmax(-1).tolist()]
        spans = decode_spans(text, offsets, labels)
        ents = [{"entity_type": b, "start": s, "end": e, "entity_string": text[s:e]}
                for b, s, e in spans]
        f.write(json.dumps({"record_id": r.get("record_id"), "record_index": i,
                            "language": lang_of(r), "entities": ents},
                           ensure_ascii=False) + "\n")
        f.flush()                                     # save every line immediately
        if device == "mps":
            torch.mps.empty_cache()                   # <-- frees memory, stops the swap slowdown
        el = time.time() - t0
        print(f"  {k+1}/{len(todo)} (idx {i}, {ntok} tok) | {el:.0f}s elapsed, "
              f"{el/(k+1):.1f}s/rec, ETA {(len(todo)-k-1)*el/(k+1)/60:.1f} min")
print("DONE.")

# final tally
n = Counter()
for line in open(OUT, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    try:
        for e in json.loads(line)["entities"]: n[e["entity_type"]] += 1
    except Exception: pass
total = sum(1 for line in open(OUT) if line.strip())
print(f"Total records in file: {total}")
print("Predicted-label histogram:", dict(n))
