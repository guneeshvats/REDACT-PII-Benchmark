# REDACT : A Systematically Controlled Multilingual Benchmark for Personal Information Detection

<p align="center">
  <strong>13,427 records &nbsp;·&nbsp; 324,078 entity annotations &nbsp;·&nbsp; 51 PII types &nbsp;·&nbsp; 25 languages &nbsp;·&nbsp; 9 scripts &nbsp;·&nbsp; 4,127 surface-form patterns</strong>
</p>

<p align="center">
  <a href="#data">Data</a> •
  <a href="#taxonomy">Taxonomy</a> •
  <a href="#generation-pipeline">Generation</a> •
  <a href="#evaluation-harness">Evaluation</a> •
  <a href="#detector-baselines">Baselines</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#citation">Citation</a>
</p>

---

## Overview

**PII-Benchmark** is a systematically controlled, multilingual benchmark for evaluating Personally Identifiable Information (PII) detection systems. It addresses three gaps in current PII evaluation resources:

1. **Narrow taxonomies** — existing benchmarks cover 5–18 entity types; we define **51 types** with explicit GDPR Article 9 alignment.
2. **Limited multilingual coverage** — most benchmarks are English-only; we span **25 languages across 9 scripts**.
3. **No disclosure-aware evaluation** — no prior benchmark records whether a mention is *actually disclosed* vs. hypothetical, *complete* vs. obfuscated, or belongs to the *highest-sensitivity* regulatory tier.

A strength-2 covering-array sampler controls nine generation axes (domain, format, difficulty, length, density, code-switching, language, adjacency, co-occurrence pattern), guaranteeing that every pair of axis values co-occurs in at least one record. Three entity-level metadata fields (`disclosed`, `disclosure_form`, `sensitivity_tier`) power a **stratified evaluation framework** (F5/F6 metrics) that reveals architecture-dependent failure structures hidden by aggregate F1.

We evaluate five detectors — Presidio, GLiNER, the OpenAI Privacy Filter, GPT-4.1, and Claude Sonnet 4.6 — and release the benchmark, schema, generation prompts, evaluation harness, and detector baselines.

---

## Key Results

| Detector | Partial micro-F1 | Macro F1 | Exact micro-F1 |
|---|:---:|:---:|:---:|
| Presidio (Microsoft, 2024) | 0.195 | 0.063 | 0.145 |
| GLiNER-multi (Zaratiana et al., 2024) | 0.320 | 0.224 | 0.293 |
| OpenAI Privacy Filter (OpenAI, 2026) | 0.512 | 0.254 | 0.171 |
| GPT-4.1 | 0.597 | 0.565 | 0.558 |
| **Claude Sonnet 4.6** | **0.636** | **0.619** | **0.602** |

> Evaluated on the locked 1,000-record language-stratified sample under partial-overlap span matching.

**Stratified findings:**
- Presidio's recall drops from 0.23 (LOW tier) to 0.07 (HIGH / Article 9), revealing a +0.16 Article-9 gap.
- LLM detectors show the opposite pattern — highest recall on HIGH-tier entities.
- Obfuscated disclosure forms (redacted, masked) degrade all detectors; aggregate F1 hides this gap.

---

## Repository Structure

```
PII-Benchmark/
│
├── README.md                              # This file
├── LICENSE
├── .gitignore
│
├── data/
│   ├── pii_benchmark_full.json            # Full corpus: 13,427 records, 324K entities
│   ├── pii_benchmark_sample1000.json      # Locked 1,000-record stratified eval sample
│   └── schema.md                          # Record and entity schema documentation
│
├── catalog/
│   ├── PII_Pattern_Catalog_v4_MASTER.md   # 4,127 surface-form patterns across 51 types
│   ├── pattern_seed_data_v4.json          # Machine-readable pattern catalog (JSON)
│   └── co_to_v4_mapping.json              # Co-occurrence pattern → catalog mapping
│
├── generation/
│   ├── README.md                          # Generation pipeline documentation
│   ├── prompts/
│   │   ├── generation_prompt_v3.yaml      # Canonical generation prompt (15 hard rules)
│   │   └── generation_prompt_v3.md        # Human-readable prompt documentation
│   ├── samplers/
│   │   ├── build_generation_plan.py       # Strength-2 covering-array plan builder
│   │   ├── build_paired_sweep_plan.py     # Factorial paired-sweep plan builder
│   │   └── build_pattern_seed_v4.py       # Pattern seed JSON constructor
│   ├── sygra_graph/
│   │   ├── graph_config.yaml              # SyGra task graph configuration
│   │   └── task_executor.py               # SyGra task executor (generation + alignment)
│   ├── builders/
│   │   ├── build_prompt_doc.py            # Prompt → DOCX renderer
│   │   └── build_prompt_md.py             # Prompt → Markdown renderer
│   ├── postprocess.py                     # Post-generation cleanup (R13/R14/R4 fixes)
│   ├── run_full.sh                        # One-command full generation run script
│   └── seed/
│       ├── generation_plan.jsonl           # Coverage plan: 5,510 records
│       ├── paired_sweep_plan.jsonl         # Paired-sweep plan: 890 records
│       ├── paired_sweep_anchors.json       # Anchor records for paired sweep
│       ├── generation_plan_report.json     # Plan coverage statistics
│       └── paired_sweep_plan_report.json   # Sweep coverage statistics
│
├── evaluation/
│   ├── README.md                          # Evaluation pipeline documentation
│   ├── scripts/
│   │   ├── schema_validator.py            # Step 1: Record-level schema validation
│   │   ├── compute_critical_gates.py      # Step 2: Family B + A2 release gates
│   │   ├── filter_corpus.py               # Step 3: Structural filter + auto-repair
│   │   ├── compute_similarity_filter.py   # Step 4: Near-duplicate removal (SBERT + ROUGE-L)
│   │   ├── compute_corpus_stats.py        # Step 5: Corpus statistics (Table 1)
│   │   ├── compute_coverage.py            # Step 6: Family A coverage metrics
│   │   ├── compute_diversity.py           # Step 7: Family C diversity (Vendi, Self-BLEU, SBERT)
│   │   ├── compute_format_checksum.py     # Step 8: Family E format compliance (Luhn, IBAN, etc.)
│   │   ├── compute_g_eval.py              # Step 9: Family G LLM-as-judge (G-Eval)
│   │   ├── run_detectors.py               # Step 10: Detector evaluation harness
│   │   ├── run_privacy_filter.py          # Step 10e: OpenAI Privacy Filter runner
│   │   ├── compute_stratified_f1.py       # Step 11: Family F5/F6 stratified F1 (NOVEL)
│   │   ├── compute_kendall_tau.py         # Step 12: Family K synthetic-real correlation
│   │   └── tab_label_map.json             # TAB → 51-type taxonomy mapping
│   ├── judge/
│   │   ├── aide_geval.py                  # Three-judge G-Eval (GPT-5.2, Claude, Gemini)
│   │   ├── aide_llm_detectors.py          # LLM-as-detector (GPT-4.1, Claude Sonnet 4.6)
│   │   └── aide_test_models.py            # Model access sanity check
│   ├── deterministic_span_analysis/
│   │   ├── postprocess_spans.py           # GT annotation span post-processor
│   │   ├── span_reconciliation.py         # Multi-model span reconciliation
│   │   └── span_utils.py                  # Span utility functions
│   └── manual_validation/
│       ├── create_manual_validation_records.py  # Annotation sheet generator
│       └── PII_Manual_Validation_Instructions.docx
│
├── docs/
│   ├── methodology.md                     # Full generation methodology (v3.2)
│   ├── how_a_record_is_created.md         # Step-by-step record creation walkthrough
│   ├── metrics_reference.md               # All metric families with citations
│   ├── generation_guide.md                # Operational generation runbook
│   ├── runbook.md                         # Evaluation pipeline runbook
│   └── corpus_quality_comparison.md       # Before/after quality comparison
│
└── reports/                               # Pre-computed quality & evaluation reports
    ├── 01_schema.json                     # Schema validation results
    ├── 02_gates_raw.json                  # Critical gates on raw corpus
    ├── 03_filter.json                     # Filter + repair report
    ├── 04_similarity.json                 # Deduplication statistics
    ├── 05_gates_clean.json                # Critical gates on clean corpus
    ├── 06_stats.json                      # Corpus statistics (Table 1 data)
    ├── 07_coverage.json                   # Coverage metrics (Family A)
    ├── 08_diversity.json                  # Diversity metrics (Family C)
    ├── 09_format.json                     # Format compliance (Family E)
    └── 11_stratified_f1.json              # Stratified F1 results (Family F5/F6)
```

---

## Data

### Corpus Statistics

| Statistic | Value |
|---|---|
| Total records | 13,427 |
| Total entity annotations | 324,078 |
| Mean entities per record | 24.1 |
| Canonical entity types | 51 |
| Languages | 25 (across 9 scripts) |
| Surface-form patterns | 4,127 |
| Records per language | 453–621 (balanced) |
| Min entities per type | 282 (`Disciplinary_Action`) |
| Article 9 records | 3,829 (28.5%) |
| Pairwise axis coverage | 98.2% |
| Mean ROUGE-L (near-dup) | 0.03 |

### Downloads

| File | Records | Description |
|---|---|---|
| `data/pii_benchmark_full.json` | 13,427 | Full benchmark corpus |
| `data/pii_benchmark_sample1000.json` | 1,000 | Locked language-stratified evaluation sample (40 per language) |

### Record Schema

Each record is a JSON object with the following structure:

```json
{
  "record_id": 42,
  "text": "Patient record for María García, DOB 15/03/1985...",
  "mode": "coverage",
  "axes": {
    "domain": "healthcare",
    "format": "plain_text",
    "difficulty": "medium",
    "length": "large",
    "density": "high",
    "code_switching": "light",
    "language": "ES",
    "adjacency": "tight",
    "co_occurrence_pattern": "CO-007"
  },
  "behavioral_frame": "co_occurrence",
  "target_entity_type": "Medical_Information",
  "target_pattern_id": "MI-015",
  "entities": [
    {
      "entity_type": "Full_Name",
      "entity_string": "María García",
      "start": 19,
      "end": 31,
      "mention_index": 0,
      "disclosed": true,
      "disclosure_form": "complete",
      "sensitivity_tier": "MEDIUM"
    }
  ],
  "entity_count": 18,
  "generation_status": "ok"
}
```

### Entity-Level Metadata Fields

| Field | Values | Description |
|---|---|---|
| `disclosed` | `true` / `false` | Whether the entity is actually disclosed in context (vs. hypothetical, negated, or counterfactual) |
| `disclosure_form` | `complete` / `partial` / `obfuscated` | Surface form: full string, truncated/initialed, or masked/redacted |
| `sensitivity_tier` | `HIGH` / `MEDIUM` / `LOW` | GDPR Article 9 alignment: HIGH = special-category data (religion, health, sexual orientation, etc.), MEDIUM = direct identifiers, LOW = quasi-identifiers |

---

## Taxonomy

51 entity types organized into 7 families, aligned with GDPR Article 9 sensitivity tiers:

| Family | Entity Types | Sensitivity |
|---|---|---|
| **Identification** | `Full_Name`, `First_Given_Name`, `Last_Family_Name`, `Preferred_Name`, `National_Identification_Number`, `Passport_Number`, `Driving_License_Number`, `Tax_Reference_Number`, `Employee_ID_Number`, `Building_Badge_Card_Number`, `Customer_Reference_Number` | MEDIUM |
| **Contact** | `Address_Work`, `Address_Personal`, `Telephone_Numbers_Work`, `Telephone_Numbers_Personal`, `Work_Email_Address`, `Personal_Email_Address`, `Emergency_Contact_Details` | MEDIUM |
| **Demographic** | `Date_of_Birth`, `Age`, `Place_of_Birth`, `Gender`, `Marital_Status`, `Nationality`, `Citizenship_Status` | MEDIUM / LOW |
| **Sensitive (Article 9)** | `Sex_Orientation`, `Religion`, `Political_Party`, `Trade_Union_Membership`, `Medical_Information`, `Allergy_Information`, `Sickness_Day_Records`, `Crime`, `PEP_Status` | **HIGH** |
| **Geographic** | `Country_of_Residence`, `State`, `City`, `Location`, `Geolocation_Data` | LOW |
| **Financial** | `Compensation_and_Salary`, `Credit_Card_Numbers`, `Account_Statements` | MEDIUM |
| **Professional & Digital** | `Business_Title`, `Org_Name`, `Professional_Background`, `Performance_Assessment`, `Disciplinary_Action`, `Social_Media_Identifiers`, `Static_IP_Address`, `Password`, `Date_Time` | MEDIUM / LOW |

The full pattern catalog (`catalog/PII_Pattern_Catalog_v4_MASTER.md`) enumerates all 4,127 surface forms with per-pattern IDs, locale-specific formats, and example strings.

---

## Generation Pipeline

The benchmark is constructed through a **seven-stage deterministic pipeline**:

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Stage 1    │   │   Stage 2    │   │   Stage 3    │   │   Stage 4    │
│   Sampler    │──▶│  Generator   │──▶│   Aligner    │──▶│  Verifier    │
│              │   │              │   │              │   │              │
│ strength-2   │   │ Claude Opus  │   │ determ.      │   │ GPT-4o-mini  │
│ covering     │   │ 1 call ·     │   │ str.find     │   │ conditional  │
│ array, 9     │   │ 15 rules     │   │ exact        │   │              │
│ axes         │   │              │   │ offsets      │   │              │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
                                                              │
┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   Stage 7    │   │   Stage 6    │   │   Stage 5    │◀─────────┘
│   Auditor    │◀──│   Dedup      │◀──│   Repair     │
│              │   │              │   │              │
│ 6 quality    │   │ SBERT 0.85   │   │ rule fix     │
│ checks      │   │ ROUGE-L 0.70 │   │ multi-       │
│ release      │   │              │   │ mention +    │
│ gates       │   │              │   │ spans        │
└─────────────┘   └─────────────┘   └─────────────┘

Yield: 14,285 raw → structural & disclosure filters → multi-mention/span repair
       → dedup (−44) → 13,427 released (94.0%)
```

### Nine Sampling Axes

| Axis | Values | Count |
|---|---|---|
| Domain | healthcare, legal, finance, education, government, technology, HR, insurance, customer_service, law_enforcement, social_media, e_commerce | 12 |
| Format | plain_text, email, chat_transcript, log_entry, json_record, key_value_pairs, ticket_worknotes | 7 |
| Difficulty | easy, medium, hard | 3 |
| Length | small, medium, large, very_large | 4 |
| Density | low, medium, high | 3 |
| Code-switching | none, light, heavy | 3 |
| Language | EN, DE, FR, ES, IT, PT_BR, PT_EU, NL, DA, NO, SV, FI, HU, CS, TR, RU, AR, HE, HI, TH, ZH_CN, ZH_TW, JA, KO, FR_CA | 25 |
| Adjacency | none, loose, tight | 3 |
| Co-occurrence pattern | none + 15 named patterns (CO-001 through CO-015) | 16 |

### How to Run Generation

```bash
# 1. Install dependencies
pip install pyyaml requests allpairspy python-docx

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Full generation run (5,510 coverage + 890 paired sweep = 6,400 records)
bash generation/run_full.sh 2>&1 | tee outputs/generation.log
```

See `docs/generation_guide.md` for the detailed operational runbook.

---

## Evaluation Harness

The evaluation pipeline consists of 12 scripts executed in two phases:

### Phase 1: Corpus Quality (Steps 1–9)

```bash
cd evaluation/scripts

INPUT=../../data/pii_benchmark_full.json

# Step 1: Schema validation
python schema_validator.py $INPUT --out ../../reports/01_schema.json

# Step 2: Critical release gates (Family B)
python compute_critical_gates.py $INPUT --out ../../reports/02_gates.json

# Step 3: Structural filter + auto-repair
python filter_corpus.py $INPUT --out ../../data/clean.json --report ../../reports/03_filter.json

# Step 4: Near-duplicate removal (SBERT + ROUGE-L)
python compute_similarity_filter.py ../../data/clean.json \
    --out ../../data/clean_deduped.json --report ../../reports/04_similarity.json

# Step 5: Post-filter gates
python compute_critical_gates.py ../../data/clean_deduped.json --out ../../reports/05_gates_clean.json

# Step 6: Corpus statistics
python compute_corpus_stats.py ../../data/clean_deduped.json --out ../../reports/06_stats.json

# Step 7: Coverage metrics (Family A)
python compute_coverage.py ../../data/clean_deduped.json --out ../../reports/07_coverage.json

# Step 8: Diversity metrics (Family C)
python compute_diversity.py ../../data/clean_deduped.json --out ../../reports/08_diversity.json --sample 500

# Step 9: Format compliance (Family E)
python compute_format_checksum.py ../../data/clean_deduped.json --out ../../reports/09_format.json
```

### Phase 2: Detector Evaluation (Steps 10–12)

```bash
CORPUS=../../data/pii_benchmark_sample1000.json

# Step 10: Run detectors
python run_detectors.py $CORPUS --detector presidio    --out ../../predictions/preds_presidio.json
python run_detectors.py $CORPUS --detector gliner      --out ../../predictions/preds_gliner.json
python run_detectors.py $CORPUS --detector gpt-4.1     --out ../../predictions/preds_gpt.json
python run_detectors.py $CORPUS --detector claude-haiku --out ../../predictions/preds_claude.json
python run_privacy_filter.py  # OpenAI Privacy Filter

# Step 11: Stratified F1 (NOVEL F5/F6 contribution)
for det in presidio gliner gpt claude; do
  python compute_stratified_f1.py ../../predictions/preds_${det}.json \
      --out ../../reports/11_strat_f1_${det}.json --mode partial
done

# Step 12: Kendall's τ vs TAB (synthetic-real ranking correlation)
python compute_kendall_tau.py \
    --synthetic ../../reports/11_strat_f1_*.json \
    --real ../../reports/12_tab_f1_*.json \
    --out ../../reports/12_kendall_tau.json
```

### Metric Families

| Family | ID | What it measures | Scripts |
|---|---|---|---|
| **A — Coverage** | A1–A5 | Pattern, entity-type, language, pairwise axis, behavioral coverage | `compute_coverage.py` |
| **B — Annotation Integrity** | B1–B6 | Offset accuracy, zero-entity rate, type compliance, multi-mention | `compute_critical_gates.py` |
| **C — Diversity** | C1–C8 | Shannon entropy, Distinct-n, Self-BLEU, ROUGE-L, Vendi, SBERT | `compute_diversity.py` |
| **E — Format Compliance** | E1–E5 | Email RFC 5322, Luhn, IBAN mod-97, SSN, IPv4/v6 | `compute_format_checksum.py` |
| **F — Behavioral Soundness** | F1–F6 | Behavioral frame coverage, **per-form F1 (F5)**, **per-tier F1 (F6)** | `compute_stratified_f1.py` |
| **G — LLM-as-Judge** | G1–G2 | G-Eval coherence/realism, inter-judge agreement | `compute_g_eval.py` |
| **K — Ranking Correlation** | K1–K4 | Kendall's τ, Spearman's ρ vs. real corpora (TAB) | `compute_kendall_tau.py` |

---

## Detector Baselines

Five detectors spanning three architecture families:

| Detector | Architecture | Source |
|---|---|---|
| **Presidio** | Regex + spaCy NER ensemble | [Microsoft Presidio](https://github.com/microsoft/presidio) |
| **GLiNER-multi** | Zero-shot multilingual span detector | [GLiNER](https://github.com/urchade/GLiNER) |
| **OpenAI Privacy Filter** | Fine-tuned token classifier (8 categories) | [openai/privacy-filter](https://huggingface.co/openai/privacy-filter) |
| **GPT-4.1** | Frontier LLM, zero-shot extraction | OpenAI API |
| **Claude Sonnet 4.6** | Frontier LLM, zero-shot extraction | Anthropic API |

All five are evaluated on the locked 1,000-record sample with identical extraction prompts, under three span-matching modes:
- **Exact**: coincident span boundaries
- **Partial**: any same-type overlap (primary metric)
- **Fuzzy**: ≥50% overlap of the shorter span

---

## Stratified Evaluation (Novel Contribution)

### F5: Per-Disclosure-Form Recall

For each detector, recall is computed over gold entities tagged `complete`, `partial`, and `obfuscated`. The **obfuscation gap** Δ_F5 = R_complete − R_obfuscated quantifies how much aggregate F1 hides.

### F6: Per-Sensitivity-Tier Recall

Recall stratified by `HIGH` (Article 9), `MEDIUM`, and `LOW`. The **Article-9 gap** Δ_F6 = R_LOW − R_HIGH isolates regulatory-sensitive performance.

These metrics reveal that:
- Rule-based detectors (Presidio) perform poorly on HIGH-tier and obfuscated entities
- LLM detectors show robust HIGH-tier recall but still struggle with obfuscated forms
- A single aggregate F1 score masks these architecture-dependent failure structures

---

## Quality Assurance

The corpus passes a six-metric release-gate protocol:

| Gate | Metric | Result | Threshold |
|---|---|---|---|
| B1 | Offset accuracy | 99.65% (100% after repair) | 100% |
| B2 | Zero-entity rate | 0.00% | ≤ 0.5% |
| B4 | Triple-name decomposition | 61.7%* | ≥ 95% |
| B5 | Canonical type compliance | 100% | 100% |
| B6 | Multi-mention completeness | 99.49% (100% after R1) | ≥ 95% |
| A2 | Min entities per type | 282 | ≥ 50 |

\* B4 is a known limitation confined to non-Western naming patterns; discussed in the paper's Limitations section.

---

## Quick Start

### Requirements

```bash
# Create environment
conda create -n pii_bench python=3.11 -y
conda activate pii_bench

# Core dependencies (corpus quality)
pip install nltk sentence-transformers numpy scikit-learn
python -c "import nltk; nltk.download('punkt_tab')"

# Detector dependencies
pip install presidio-analyzer presidio-anonymizer gliner
python -m spacy download en_core_web_lg

# LLM detector / G-Eval dependencies
pip install openai anthropic

# Set API keys (for LLM detectors and G-Eval)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Run Evaluation on the Released Data

```bash
cd evaluation/scripts

# Compute corpus statistics
python compute_corpus_stats.py ../../data/pii_benchmark_full.json --out ../../reports/stats.json

# Run Presidio on the 1,000-record sample
python run_detectors.py ../../data/pii_benchmark_sample1000.json \
    --detector presidio --out ../../predictions/preds_presidio.json

# Compute stratified F1
python compute_stratified_f1.py ../../predictions/preds_presidio.json \
    --out ../../reports/strat_f1_presidio.json --mode partial
```

### Load the Data in Python

```python
import json

# Load the full corpus
with open("data/pii_benchmark_full.json") as f:
    corpus = json.load(f)

print(f"Records: {len(corpus)}")
print(f"Total entities: {sum(r['entity_count'] for r in corpus)}")

# Inspect one record
record = corpus[0]
print(f"Language: {record['axes']['language']}")
print(f"Domain: {record['axes']['domain']}")
print(f"Entities: {len(record['entities'])}")

for ent in record["entities"][:5]:
    print(f"  [{ent['sensitivity_tier']}] {ent['entity_type']}: "
          f"'{ent['entity_string']}' @ [{ent['start']}:{ent['end']}] "
          f"({ent['disclosure_form']}, disclosed={ent['disclosed']})")
```

---

## Languages

25 languages across 9 scripts, organized in three resource tiers:

| Tier | Languages | Script |
|---|---|---|
| **High-resource** (6) | English (EN), German (DE), French (FR), Spanish (ES), Portuguese-Brazil (PT_BR), Italian (IT) | Latin |
| **Mid-resource** (3) | Japanese (JA), Korean (KO), Chinese-Simplified (ZH_CN) | CJK |
| **Lower-resource** (16) | Dutch (NL), Danish (DA), Norwegian (NO), Swedish (SV), Finnish (FI), Hungarian (HU), Czech (CS), Turkish (TR), Russian (RU), Arabic (AR), Hebrew (HE), Hindi (HI), Thai (TH), Chinese-Traditional (ZH_TW), Portuguese-EU (PT_EU), French-Canada (FR_CA) | Latin, Cyrillic, Arabic, Hebrew, Devanagari, Thai, CJK |

Each language contributes 453–621 records (balanced by design).

---

## Manual Validation

Human annotators independently verified a stratified sample:
- **Task 1 — Entity validation**: 510 entities (10 per type), two annotators, checking type, span, disclosed flag, disclosure form, and sensitivity tier
- **Task 2 — Record-level audit**: 25 records (1 per language), checking for missing PII mentions

Annotation sheets and instructions are in `evaluation/manual_validation/`.

---

## Documentation

| Document | Description |
|---|---|
| `docs/methodology.md` | Full construction methodology (v3.2): taxonomy, sampling, generation, QA |
| `docs/how_a_record_is_created.md` | Step-by-step walkthrough of record creation |
| `docs/metrics_reference.md` | All metric families (A–K) with citations and thresholds |
| `docs/generation_guide.md` | Operational runbook for running the generation pipeline |
| `docs/runbook.md` | Evaluation pipeline runbook with timing and cost estimates |
| `docs/corpus_quality_comparison.md` | Before/after quality comparison across pipeline stages |
| `catalog/PII_Pattern_Catalog_v4_MASTER.md` | Full 4,127-pattern surface-form catalog |

---

## Reproducing the Paper Results

### Minimum scripts for core results

| Paper Section | Script | Output |
|---|---|---|
| Table 1 (Corpus Statistics) | `compute_corpus_stats.py` | `06_stats.json` |
| §3.6 (Quality Assurance) | `compute_critical_gates.py` | `05_gates_clean.json` |
| §5.1 (Coverage) | `compute_coverage.py` | `07_coverage.json` |
| §5.1 (Diversity) | `compute_diversity.py` | `08_diversity.json` |
| Table 1 (Detector Results) | `run_detectors.py` + `compute_stratified_f1.py` | `11_strat_f1_*.json` |
| §4.4 (G-Eval) | `compute_g_eval.py` / `aide_geval.py` | `geval_report.json` |

### Estimated time and cost

| Phase | Time | API Cost |
|---|---|---|
| Corpus quality (Steps 1–9) | ~1.5 hours | ~$2–4 (G-Eval only) |
| Detector evaluation (Steps 10–12) | ~2–3 hours | ~$10–20 |
| **Total** | **~4–5 hours** | **~$15–25** |

---

## Citation

```bibtex
@inproceedings{anonymous2026piibenchmark,
    title     = {A Systematically Controlled Multilingual Benchmark
                 for Personal Information Detection},
    author    = {Anonymous Authors},
    booktitle = {Proceedings of the 2026 Conference on Empirical Methods
                 in Natural Language Processing: Industry Track},
    year      = {2026},
    note      = {Under review}
}
```

---

## License

This benchmark is released for research purposes. See `LICENSE` for details.

---

## Acknowledgments

This work was conducted at Anonymous Institution. The generation pipeline is built on top of the [SyGra](https://anonymous.4open.science/r/SyGra) synthetic data generation framework.
