# PII Benchmark — Validation & Analysis Workspace

Downstream validation, filtering, evaluation, and analysis pipeline for the
Anonymous Institution PII Detection Benchmark. Targets EMNLP 2026 Industry Track
submission (deadline June 16, 2026).

This workspace is **separate** from the generation pipeline (`pii-bench-gen-main`)
which lives in the generation team's bundle. This folder only consumes the output of
that pipeline.

---

## Folder layout

```
PII_Benchmark_Analysis/
├── scripts/              # All 12 Python scripts + tab_label_map.json
├── docs/                 # RUNBOOK, METRICS_REFERENCE, etc.
├── input_corpora/        # Raw .json files from the generation team (you create this)
├── corpus/               # Filtered + deduplicated outputs (auto-created)
├── predictions/          # Detector outputs (auto-created)
├── reports/              # JSON metric reports (auto-created)
├── tab_corpus/           # TAB benchmark for Kendall's τ (later)
├── paper/                # LaTeX paper draft (later)
└── README.md             # This file
```

---

## Quick setup (one-time, ~15 min)

```bash
# 1. Create folder structure
mkdir -p ~/Desktop/PII_Benchmark_Analysis/{input_corpora,corpus,predictions,reports,tab_corpus,paper}
cd ~/Desktop/PII_Benchmark_Analysis

# 2. Move scripts/ and docs/ folders here (downloaded from the chat output)
# (Already done if you downloaded the bundle)

# 3. Create conda env
conda create -n pii_eval python=3.11 -y
conda activate pii_eval

# 4. Install dependencies
pip install nltk sentence-transformers numpy scikit-learn
pip install presidio-analyzer presidio-anonymizer gliner
pip install openai anthropic
python -m spacy download en_core_web_lg
python -c "import nltk; nltk.download('punkt_tab')"

# 5. (For detector eval later) Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 6. Copy the generation team's latest output into input_corpora/
cp ~/Desktop/run1_29may_clean_postprocessed.jsonl input_corpora/run1.jsonl
# Convert JSONL -> JSON (our scripts read JSON arrays):
python3 -c "
import json
records = [json.loads(l) for l in open('input_corpora/run1.jsonl') if l.strip()]
json.dump(records, open('input_corpora/run1.json', 'w'), ensure_ascii=False)
print(f'Converted {len(records)} records')
"
```

---

## Run the pilot (full pipeline on Run 1 alone)

See `docs/RUNBOOK.md` for the canonical command sequence. Quick version:

```bash
cd scripts

RUN1=../input_corpora/run1.json

# Phase 1: corpus quality (~30 min)
python schema_validator.py        $RUN1                            --out ../reports/01_schema.json
python compute_critical_gates.py  $RUN1                            --out ../reports/02_gates_raw.json
python filter_corpus.py           $RUN1                            --out ../corpus/clean.json         --report ../reports/03_filter.json
python compute_similarity_filter.py ../corpus/clean.json           --out ../corpus/clean_deduped.json --report ../reports/04_similarity.json
python compute_critical_gates.py  ../corpus/clean_deduped.json     --out ../reports/05_gates_clean.json
python compute_corpus_stats.py    ../corpus/clean_deduped.json     --out ../reports/06_stats.json
python compute_coverage.py        ../corpus/clean_deduped.json     --out ../reports/07_coverage.json
python compute_diversity.py       ../corpus/clean_deduped.json     --out ../reports/08_diversity.json --sample 300
python compute_format_checksum.py ../corpus/clean_deduped.json     --out ../reports/09_format.json

# Phase 2: detector evaluation (~2-3 hrs, ~$10)
python run_detectors.py ../corpus/clean_deduped.json --detector presidio    --out ../predictions/preds_presidio.json
python run_detectors.py ../corpus/clean_deduped.json --detector gliner      --out ../predictions/preds_gliner.json
python run_detectors.py ../corpus/clean_deduped.json --detector gpt-4o-mini --out ../predictions/preds_gpt.json --sample 300
python run_detectors.py ../corpus/clean_deduped.json --detector claude-haiku --out ../predictions/preds_claude.json --sample 300

# Stratified F1 (the novel paper contribution)
for det in presidio gliner gpt claude; do
  python compute_stratified_f1.py ../predictions/preds_${det}.json --out ../reports/11_strat_f1_${det}.json
done

# Optional G-Eval (~$2-4)
python compute_g_eval.py ../corpus/clean_deduped.json --out ../reports/10_g_eval.json --sample 300
```

---

## What each script does (one-liner)

| Script | Purpose |
|---|---|
| `schema_validator.py` | Catches malformed records before downstream stages |
| `compute_critical_gates.py` | Family B + A2 — the methodology's release gates |
| `filter_corpus.py` | Drops structurally-broken records, auto-repairs offsets and multi-mentions |
| `compute_similarity_filter.py` | Self-Instruct-style near-duplicate removal (ROUGE-L + SBERT) |
| `compute_corpus_stats.py` | Generates Table 1 data — counts per entity/language/axis/tier |
| `compute_coverage.py` | Family A — pattern, language, pairwise axis, behavioral coverage |
| `compute_diversity.py` | Family C — Distinct-n, Self-BLEU, ROUGE-L, Vendi, SBERT, pattern density |
| `compute_format_checksum.py` | Family E — Luhn, IBAN, RFC 5322, IPv4/v6, SSN format checks |
| `compute_g_eval.py` | Family G — GPT-4o-mini + Claude Haiku LLM-as-judge with bias mitigations |
| `run_detectors.py` | Runs Presidio / GLiNER / GPT-4o-mini / Claude Haiku on the corpus |
| `compute_stratified_f1.py` | Family F5/F6 — stratified F1 by disclosure_form and sensitivity_tier (NOVEL) |
| `compute_kendall_tau.py` | Family K — synthetic-real ranking correlation with bootstrap CI |
| `tab_label_map.json` | Reference — TAB → 51-type taxonomy mapping for Kendall's τ |

---

## Quality of current input

the generation team's latest file (`run1_29may_clean_postprocessed.jsonl`, 3,600 records)
shows substantial improvement over the earlier 4,400-record version. See
`docs/CORPUS_QUALITY_COMPARISON.md` for the before/after numbers.

After applying our filter + repair, **5 of 6 critical gates pass**:
- B1 offset accuracy: 99.65% (target 100%)
- B2 zero-entity: 0.00% ✓
- B5 canonical types: 100.00% ✓
- B6 multi-mention: 99.49% ✓
- A2 per-entity floor: min 58 ✓
- B4 triple-name: 61.70% (script limitation, not a data bug — see methodology)

This is paper-quality data.

---

## When Run 2 arrives

Run the same pipeline but pass both files to `filter_corpus.py`:

```bash
python filter_corpus.py ../input_corpora/run1.json ../input_corpora/run2.json \
    --out ../corpus/clean.json --report ../reports/03_filter.json
```

The script handles the merge + dedup automatically.

---

## Paper writing

When the pilot run completes, paste the 9 JSON reports from `reports/` into a
new chat and ask for the paper draft. Sections §1, §2, §3 can be drafted
in parallel with detector evaluation.

---

## Generation pipeline (not in this workspace)

the generation team's generation code lives in `~/Desktop/PII\ Benchmark/pii-bench-gen-main`.
This workspace doesn't touch that folder — it only consumes its outputs.
Don't mix the two.
