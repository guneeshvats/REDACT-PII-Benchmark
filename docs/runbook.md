# PII Benchmark — Validation & Analysis Pipeline

Single-page guide for running the corpus quality + detector evaluation
pipeline end-to-end.

---

## What's in this folder

```
pii_validation/scripts/
├── schema_validator.py            # Step 1 — record-level schema check
├── compute_critical_gates.py      # Step 2 — Family B + A2 integrity gates
├── filter_corpus.py               # Step 3 — F1-F5 filter + R1-R2 repair
├── compute_similarity_filter.py   # Step 4 — Self-Instruct near-dup removal
├── compute_corpus_stats.py        # Step 5 — Table 1 data
├── compute_coverage.py            # Step 6 — Family A coverage metrics
├── compute_diversity.py           # Step 7 — Family C diversity (Vendi, SBERT)
├── compute_format_checksum.py     # Step 8 — Family E format compliance
├── compute_g_eval.py              # Step 9 — Family G LLM-as-judge (API cost)
├── run_detectors.py               # Step 10 — Run Presidio/GLiNER/LLM detectors
├── compute_stratified_f1.py       # Step 11 — Family F5/F6 (NOVEL contribution)
├── compute_kendall_tau.py         # Step 12 — Family K synthetic-real correlation
└── tab_label_map.json             # Reference — TAB → 51-type mapping for K1
```

---

## One-time setup (~10–20 min)

```bash
# Fresh conda env recommended
conda create -n pii_eval python=3.11 -y
conda activate pii_eval

# Core deps — always needed
pip install nltk sentence-transformers numpy scikit-learn
python -c "import nltk; nltk.download('punkt_tab')"

# For LLM-as-judge (Step 9) AND LLM detectors (Step 10)
pip install openai anthropic

# For Presidio detector (Step 10)
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg

# For GLiNER detector (Step 10)
pip install gliner

# Set API keys (for Steps 9, 10 with LLM detectors)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Download TAB for Step 12 (Kendall's τ)
git clone https://github.com/NorskRegnesentral/text-anonymization-benchmark.git
```


## ⚠️ If the generation team's file is JSONL (one record per line)

Our scripts read JSON arrays. Convert JSONL → JSON once:

```bash
python3 -c "
import json
records = [json.loads(l) for l in open('input_corpora/run1.jsonl') if l.strip()]
json.dump(records, open('input_corpora/run1.json', 'w'), ensure_ascii=False)
print(f'Converted {len(records)} records')
"
```

---

## End-to-end run (canonical order)

**Phase 1: Corpus quality (Steps 1–9)** — runs first
**Phase 2: Detector evaluation (Steps 10–12)** — runs after corpus is locked

```bash
cd /path/to/pii_validation/scripts
mkdir -p ../corpus ../reports ../predictions

# =========================
# Phase 1: Corpus quality
# =========================

# Step 1 — Schema validation on raw runs
python schema_validator.py ~/Desktop/run1.json --out ../reports/01_schema_run1.json
python schema_validator.py ~/Desktop/run2.json --out ../reports/01_schema_run2.json

# Step 2 — Critical gates on raw runs (for §7 Limitations honesty)
python compute_critical_gates.py ~/Desktop/run1.json --out ../reports/02_gates_run1_raw.json
python compute_critical_gates.py ~/Desktop/run2.json --out ../reports/02_gates_run2_raw.json

# Step 3 — Structural filter + auto-repair (combines runs)
python filter_corpus.py \
  ~/Desktop/run1.json ~/Desktop/run2.json \
  --out ../corpus/clean.json --report ../reports/03_filter.json

# Step 4 — Similarity-based dedup
python compute_similarity_filter.py ../corpus/clean.json \
  --out ../corpus/clean_deduped.json --report ../reports/04_similarity.json

# Step 5 — Critical gates on cleaned corpus
python compute_critical_gates.py ../corpus/clean_deduped.json --out ../reports/05_gates_clean.json

# Step 6 — Corpus stats (Table 1)
python compute_corpus_stats.py ../corpus/clean_deduped.json --out ../reports/06_stats.json

# Step 7 — Coverage (Family A)
python compute_coverage.py ../corpus/clean_deduped.json --out ../reports/07_coverage.json

# Step 8 — Diversity (Family C — slow, ~5-10 min)
python compute_diversity.py ../corpus/clean_deduped.json --out ../reports/08_diversity.json --sample 500

# Step 9 — Format compliance (Family E)
python compute_format_checksum.py ../corpus/clean_deduped.json --out ../reports/09_format.json

# Step 9.5 — G-Eval (optional, API cost ~$2-4)
python compute_g_eval.py ../corpus/clean_deduped.json --out ../reports/09_g_eval.json --sample 500

# ===================================
# Phase 2: Detector evaluation
# ===================================

# Step 10a — Presidio (free, ~20 min)
python run_detectors.py ../corpus/clean_deduped.json --detector presidio --out ../predictions/preds_presidio.json

# Step 10b — GLiNER (free, ~30-60 min on CPU)
python run_detectors.py ../corpus/clean_deduped.json --detector gliner --out ../predictions/preds_gliner.json

# Step 10c — GPT-4o-mini (~$5-15 for 500 records)
python run_detectors.py ../corpus/clean_deduped.json --detector gpt-4o-mini --out ../predictions/preds_gpt.json --sample 500

# Step 10d — Claude Haiku (~$3-10)
python run_detectors.py ../corpus/clean_deduped.json --detector claude-haiku --out ../predictions/preds_claude.json --sample 500

# Step 11 — Stratified F1 (the NOVEL F5/F6 contribution)
for det in presidio gliner gpt claude; do
  python compute_stratified_f1.py ../predictions/preds_${det}.json \
    --out ../reports/11_strat_f1_${det}.json --mode partial
done

# Step 12 — Kendall's τ vs TAB
# (Requires: TAB normalized + detectors run on TAB; see "TAB preparation" below)
python compute_kendall_tau.py \
  --synthetic ../reports/11_strat_f1_*.json \
  --real      ../reports/12_tab_f1_*.json \
  --out ../reports/12_kendall_tau.json
```

---

## What each script produces (paper mapping)

| # | Script | Paper section / table |
|---|---|---|
| 1 | `schema_validator.py` | §7 Limitations |
| 2 | `compute_critical_gates.py` (raw) | §3.5 pipeline issues |
| 3 | `filter_corpus.py` | §3 Pipeline + §7 |
| 4 | `compute_similarity_filter.py` | §3.5 dedup |
| 5 | `compute_critical_gates.py` (clean) | §4 Evaluation framework |
| 6 | `compute_corpus_stats.py` | **Table 1** |
| 7 | `compute_coverage.py` | **§5.1** coverage |
| 8 | `compute_diversity.py` | **§5.1** diversity |
| 9 | `compute_format_checksum.py` | §5.1 format validity |
| 9.5 | `compute_g_eval.py` | **§5.6** LLM-as-judge |
| 10 | `run_detectors.py` | (input to 11, 12) |
| 11 | `compute_stratified_f1.py` | **§5.3** stratified F1 (NOVEL) |
| 12 | `compute_kendall_tau.py` | **§5.5** Kendall's τ (validity) |

---

## Timing & cost summary (for ~5,500 records)

| Phase | Time | API cost |
|---|---|---|
| Phase 1 (Steps 1–9.5) | ~1.5 hours | ~$2–4 (G-Eval only) |
| Phase 2 (Steps 10–12) | ~2–3 hours | ~$10–20 |
| **Total** | **~4–5 hours** | **~$15–25** |

---

## TAB preparation (Step 12 prerequisite)

```bash
# 1. Clone TAB
git clone https://github.com/NorskRegnesentral/text-anonymization-benchmark.git

# 2. Normalize TAB to our schema using tab_label_map.json
# (~50-line adapter script; uses the high-confidence mappings:
#  PERSON, LOC, ORG, DATETIME only — see tab_label_map.json for rationale)

# 3. Run detectors on TAB
python run_detectors.py tab_normalized.json --detector presidio --out tab_preds_presidio.json
# ... repeat for each detector

# 4. Compute F1 on TAB
for det in presidio gliner gpt claude; do
  python compute_stratified_f1.py tab_preds_${det}.json --out tab_f1_${det}.json
done

# 5. Run Kendall's τ
python compute_kendall_tau.py --synthetic synth_f1_*.json --real tab_f1_*.json --out kendall.json
```

---

## Common issues

- **nltk.download** fails on `punkt_tab` — try `punkt` for older nltk versions
- **SBERT first run** is slow (downloads ~80MB model, then cached)
- **GLiNER first run** downloads 500MB+ model
- **Presidio scores low on non-English** — that's the expected baseline gap, mention in paper
- **LLM detectors hit rate limits** — use `--delay 0.5` or `--sample 200`
- **Kendall's τ CI is wide** at n=4 detectors — expected, frame per Kiela 2021

---

## Minimum to run for paper

If only 6 scripts can be run:

1. `filter_corpus.py` → clean corpus
2. `compute_critical_gates.py` → §4
3. `compute_corpus_stats.py` → Table 1
4. `compute_coverage.py` → §5.1
5. `compute_diversity.py` → §5.1
6. `run_detectors.py` + `compute_stratified_f1.py` (Presidio + 1 LLM) → §5.2 + §5.3

Add G-Eval and Kendall's τ for the stronger version.
