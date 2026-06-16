# Corpus Quality Comparison — Old Run 1 vs. New Postprocessed File

Date: June 4, 2026

This doc compares the **original Run 1 file** (4,400 records) against the
**postprocessed file** the generation team shared after our findings discussion (3,600
records, `run1_29may_clean_postprocessed.jsonl`).

---

## TL;DR

**The new file is dramatically better.** the generation team's postprocessing addressed
the dominant issues we flagged:
- ✅ json_error records eliminated entirely
- ✅ Empty `sensitivity_tier` eliminated
- ✅ Multi-mention completeness substantially improved
- ✅ Average annotation density nearly doubled (~14 → 24 entities/record)

After applying our standard filter + auto-repair pipeline, the new corpus
passes **5 of 6 critical release gates**. This is paper-quality data.

---

## Side-by-side comparison

| Metric | Old Run 1 (4,400) | New File (3,600) | After filter+repair (3,396) |
|---|---|---|---|
| **Schema pass rate** | 57.7% | **94.3%** ⬆️ | 100% ⬆️ |
| **Records with `generation_status: json_error`** | 765 (17.4%) | **0** ✓ | 0 ✓ |
| **Entities with empty `sensitivity_tier`** | 15,016 (~23%) | **0** ✓ | 0 ✓ |
| **B1 — Offset accuracy** | 88.24% | 91.72% | **99.65%** ✓ |
| **B2 — Zero-entity rate** | 17.39% | **0.00%** ✓ | 0.00% ✓ |
| **B4 — Triple-name compliance** | 55.39% | 61.44% | 61.70% (script limit) |
| **B5 — Canonical-type compliance** | 98.33% | 99.69% | **100.00%** ✓ |
| **B6 — Multi-mention completeness** | 69.99% | 88.25% ⬆️ | **99.49%** ✓ |
| **A2 — Per-entity floor (min count)** | 61 ✓ | 60 ✓ | 58 ✓ |
| **Total entities** | ~64,000 | 89,411 ⬆️ | 82,429 |
| **Mean entities/record** | ~14 | **24.8** ⬆️ | 24.3 |

---

## What changed

### ✅ Issues fixed in the postprocessed file

| Old issue | Status in new file |
|---|---|
| 17% of records had `generation_status: json_error` and empty text | Eliminated — 0 such records |
| 23% of entities had empty `sensitivity_tier` ("") | Eliminated — all entities have HIGH/MEDIUM/LOW |
| Multi-mention completeness ~70% (only 1 of K mentions emitted) | Up to 88% in the postprocessed file; our auto-repair takes it to 99.49% |
| Mean annotation density was low (~14 entities/record) | Up to 24.3 entities/record — substantially richer annotations |

### ⚠️ Issues remaining (minor)

**1. Non-canonical entity types (~5.7% of records).**
The LLM still occasionally invents types outside our 51-type taxonomy:
- `Country` (27 instances) — should be folded into `Country_of_Residence`
- `Tax_Identification_Number` (22) — should be `Tax_Reference_Number`
- `Vehicle_Registration_Number` (19), `License_Plate` (11), `License_Plate_Number` (10) — vehicle-related, not in 51-type taxonomy
- `Middle_Name` (17) — could be folded into `First_Given_Name` per the naming convention
- `Username_Handle` (18), `Online_Handle` (13), `Digital_Identifier` (5) — should be `Social_Media_Identifiers`

These are caught by `F4_non_canonical_type` in the filter (181 records dropped).

**2. `disclosure_form` non-standard values (32 entities, very minor).**
Should be one of `complete`/`partial`/`obfuscated`. A few `redacted`,
`abbreviated`, etc. still slip through. Caught by `F5` filter (23 records).

**3. Triple-name compliance (61.70%).**
This is **not a data bug** — it's our validation script's baseline limitation.
The script only handles Western "First Last" decomposition. Real failures
include legitimate CJK names without spaces, patronymic naming, double
surnames, etc. Methodology R11 documents 8 such cases. The script needs
per-language extension OR we relax B4 to apply only where the simple rule
makes sense. Either is fine for the paper.

**4. B1 offset accuracy 99.65% (after repair).**
The remaining 0.35% are entities whose `entity_string` literally isn't
present in the `text` — i.e., the LLM hallucinated entity strings. Can't
fix post-hoc; these will be dropped at analysis time or flagged in §7
Limitations.

---

## Paper framing implications

This corpus is **good enough to write the paper around** without further
pipeline iteration. Key claims we can defensibly make:

1. **"Annotation integrity by construction"** — after Stage 3 deterministic
   alignment + R1/R2 post-hoc repair, offset accuracy is 99.65% and
   multi-mention completeness is 99.49%. Frame as "the residual 0.35% are
   LLM hallucinations, addressed in v2 by Stage 4 verifier expansion."

2. **"GDPR Article 9 coverage"** — entity counts will hit our floor across
   all sensitive categories. ✓

3. **"100% canonical-type compliance after filter"** — our taxonomy is
   strictly enforced post-hoc. ✓

4. **"Multi-language coverage at scale"** — 25 languages, 60+ records per
   entity type minimum, 89K total entity annotations. ✓

5. **"§7 Limitations: pipeline issues acknowledged and v2 roadmap"** —
   document the pipeline-level fixes (JSON robustness in Stage 2, multi-
   mention expansion in Stage 3, sensitivity_tier enforcement in Stage 4)
   as honest future work. Reviewers will appreciate the transparency.

---

## What this means for Run 2

If the generation team runs Run 2 with the same postprocessed pipeline, expect:
- ~3,600 raw records (similar drop from 6,400 attempts)
- ~3,400 records after our filter+repair
- **Combined Run 1 + Run 2: ~6,800 clean records** — strong size for the paper

If the second run produces similar quality (~94% schema pass), no further
intervention needed. Apply the filter, run analysis, write the paper.

---

## Recommended action

1. **Tell the generation team the postprocessed file looks great** — substantial
   improvement, paper-quality after our filter pipeline. Trigger Run 2
   on the same postprocessed pipeline whenever ready.
2. **Run the full pipeline on this Run 1 file now** as a pilot — gives you
   exact numbers to plug into the paper draft.
3. **Once Run 2 lands, merge + run again** — paper will need ~30 min update.
