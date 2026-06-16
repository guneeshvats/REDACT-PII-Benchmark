# Generation Guide

Operational runbook for generating the PII benchmark corpus (5,510 Mode 1 + 890 Mode 2 = **6,400 records**) using `pipeline/run_phase1_pipeline.py`.

This guide assumes the work is split across two parallel runs by language. Solo runs follow the same protocol — skip the coordination section.

---

## Before you start — checklist

| ☐ | Item |
|---|---|
| ☐ | VPN connected (required for `sygra_claude` and `sygra` providers — both proxies are internal hosts) |
| ☐ | Both runners have agreed on the language split (see §3) |
| ☐ | Both runners have agreed on a **single git commit hash to pin to** — prevents prompt drift mid-run |
| ☐ | `.env` file exists with the right credentials (see §2) |
| ☐ | Budget approval — ~$128 total for full 6,400 on Claude Opus 4-6 |
| ☐ | Time blocked — ~25–30 hours wall-clock per person (sequential), kickoff during work hours so you can monitor the first hour |

---

## 1. One-time setup (per person)

```bash
# 1.1 Clone the repo
git clone https://anonymous.4open.science/r/PII-Benchmark
cd pii-bench

# 1.2 Pin to the agreed commit (see §3)
git checkout 570a593     # ← replace with the hash you agreed on

# 1.3 Create venv and install deps
python3.11 -m venv .venv
source .venv/bin/activate
pip install pyyaml requests allpairspy python-docx

# 1.4 Create .env at repo root (gitignored — never commit this)
cat > .env <<'EOF'
SYGRA_API_URL=https://<sygra-gpt4o-mini-endpoint>
SYGRA_API_TOKEN=<your-token>
SYGRA_CLAUDE_OPUS4_6_URL=https://<sygra-claude-endpoint>
ANTHROPIC_API_KEY=<optional, only if using --provider anthropic>
EOF

# 1.5 Sanity: list-options should work without API calls
python pipeline/run_phase1_pipeline.py --list-options
# Should print 25 languages, 12 domains, 51 entity types.

# 1.6 Smoke test: 3 records to confirm credentials work
python pipeline/run_phase1_pipeline.py \
    --provider sygra_claude --limit 3 --output-tag smoketest
# Should produce pipeline/outputs/v3_2_phase1_records_smoketest.jsonl
# with 3 records. If this fails, fix .env / VPN before proceeding.
```

---

## 2. Required environment variables

| Variable | Required for | Where to get it |
|---|---|---|
| `SYGRA_API_URL` | `--provider sygra` (GPT-4o-mini) | SyGra team |
| `SYGRA_API_TOKEN` | both SyGra providers | SyGra team |
| `SYGRA_CLAUDE_OPUS4_6_URL` | `--provider sygra_claude` | SyGra team (this is the `dvb402` URL) |
| `ANTHROPIC_API_KEY` | `--provider anthropic` (direct, optional) | Anthropic console |

Source the .env automatically — the runner calls `load_dotenv()` internally; just keep `.env` at repo root.

---

## 3. Coordination protocol

**Lock the prompt.** Both runners `git checkout <hash>` to the same commit. Pick the latest commit on `main` at the moment the split is agreed. Do NOT edit the prompt YAML during the run — that would make `language_set1` records inconsistent with `language_set2` records.

**Agree on language split.** Suggested difficulty-balanced split:

| `language_set1` (13 languages) | `language_set2` (12 languages) |
|---|---|
| EN, ES, FR, DE, IT, PT_BR, PT_EU, NL, SV, DA, NO, FI, CS | HU, TR, RU, AR, HE, JA, ZH_CN, ZH_TW, KO, TH, HI, FR_CA |
| **2,837 records** (verified by `--list-options` filter) | **2,673 records** (verified by `--list-options` filter) |
| ~24h sequential on Opus, ~$57 | ~22h sequential on Opus, ~$53 |

Each set has roughly balanced "hard" (RTL / CJK / Devanagari) and "easy" (Latin) languages.

**Agree on output-tag conventions.** Use neutral language-set tags so the corpus stays portable:
- Set 1 → `--output-tag language_set1` → `pipeline/outputs/v3_2_phase1_records_language_set1.jsonl`
- Set 2 → `--output-tag language_set2` → `pipeline/outputs/v3_2_phase1_records_language_set2.jsonl`
- Mode 2 → `--output-tag paired` → `pipeline/outputs/v3_2_phase1_records_paired.jsonl`

This is the single most important step to prevent file-collision data loss.

**Decide who runs Mode 2 (paired-sweep, 890 records).** One of the two runners handles all of Mode 2 separately — it's only ~7h on Opus and uses different anchors, so it doesn't split cleanly by language.

---

## 4. The generation commands

### Mode 1 — covering-array corpus

```bash
# language_set1 — European-language half, 13 languages
python pipeline/run_phase1_pipeline.py \
    --language EN,ES,FR,DE,IT,PT_BR,PT_EU,NL,SV,DA,NO,FI,CS \
    --provider sygra_claude \
    --output-tag language_set1 \
    2>&1 | tee pipeline/outputs/run_language_set1.log

# language_set2 — non-Latin + variants half, 12 languages
python pipeline/run_phase1_pipeline.py \
    --language HU,TR,RU,AR,HE,JA,ZH_CN,ZH_TW,KO,TH,HI,FR_CA \
    --provider sygra_claude \
    --output-tag language_set2 \
    2>&1 | tee pipeline/outputs/run_language_set2.log
```

**Note:** there's no `--limit`, so the runner processes **all matching rows** (2,837 for `language_set1`, 2,673 for `language_set2`). Sum is exactly 5,510 = full Mode 1 corpus. The `tee` captures stdout to a log file so you can review later.

### Mode 2 — paired-sweep (one person, all of it)

```bash
python pipeline/run_phase1_pipeline.py \
    --plan paired_sweep \
    --provider sygra_claude \
    --output-tag paired \
    2>&1 | tee pipeline/outputs/run_paired.log
```

≈890 records, ≈7.5h sequential, ≈$18 on Claude Opus 4-6.

---

## 5. What to monitor during the run

The runner prints one line per record:

```
[ 12/2673] HI     healthcare     log_entry      tight  → Religion              ✓ 8/8  ent= 14  chars=  897  31.2s
            ↑ index   ↑ axes summary                          ↑ pass/fail  ↑ entity count  ↑ wall-clock
```

**Watch the first 5–10 lines:**

| Indicator | Healthy | Action if abnormal |
|---|---|---|
| Wall-clock per record | 25–40 s on Opus | >60s consistently → check VPN / proxy latency |
| `✓` vs `✗` | mostly `✓` | >50% `✗` → kill, inspect a failing record, fix prompt or expander |
| Entity count | 10–25 per record | 0 entities → JSON parse failure; check `status` field in jsonl |
| Wall-clock | smooth | Sudden jump to 120s+ → rate limit; check sygra status |

**If first 10 look good, walk away.** The run is self-monitoring — it writes to JSONL after every record, so a mid-run crash loses at most one record.

---

## 6. After it finishes — validate and merge

```bash
cd pipeline/outputs/

# 6.1 Confirm record counts match what was filtered
wc -l v3_2_phase1_records_language_set1.jsonl
wc -l v3_2_phase1_records_language_set2.jsonl
wc -l v3_2_phase1_records_paired.jsonl

# Expected: 2837 + 2673 + 890 = 6400 exactly (full corpus).
# If numbers don't match, re-verify with --list-options and the per-set
# row counts in §3.

# 6.2 Verify no record_id appears twice across files (zero output = clean)
cat v3_2_phase1_records_*.jsonl \
    | jq -r '.record_id' | sort | uniq -d

# 6.3 Merge into one corpus file
cat v3_2_phase1_records_language_set1.jsonl \
    v3_2_phase1_records_language_set2.jsonl \
    v3_2_phase1_records_paired.jsonl \
    > v3_2_phase1_records_combined.jsonl

wc -l v3_2_phase1_records_combined.jsonl

# 6.4 Re-run the R-rule analyzer over the combined corpus
cd ../..
python pipeline/smoke_test/analyze.py pipeline/outputs/v3_2_phase1_records_combined.jsonl

# 6.5 Read the per-tag summaries for high-level pass rates
cat pipeline/outputs/v3_2_phase1_summary_*.json
```

---

## 7. If things go wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| `NXDOMAIN` / `name resolution failure` | Wrong SyGra URL or VPN off | Verify VPN; use `dvb402` not `dva402` in URL |
| `SSL: CERTIFICATE_VERIFY_FAILED` | SyGra proxy uses non-public cert | Already handled in `run_smoke_test.py` (`verify=False`) — if it still fails, check VPN |
| `429 rate limit` for many records in a row | Concurrent run on same token | Coordinate the timing across the two runs; pause one for 15 min |
| `json_error` in record status | LLM returned malformed JSON | Already handled by fence-strip + regex fallback. If still failing, the record is logged with status `json_error: ...` — inspect it manually. |
| `api_error: ConnectionError` mid-run | Transient network blip | Re-run with `--limit` set to remaining count; the new records append to a new file with a different tag (or rename old file first) |
| `self_check_pass_rate` < 0.5 | Prompt regression | Compare your prompt YAML to the pinned hash with `git diff <hash> prompts/generation_prompt_v3.yaml` |

**Resumption after crash:** the runner does not natively support `--offset` (yet). Today, if it crashes at record 1500/2837 you would need to either: (a) accept the 1500 records you have and run the remaining with a new tag, then concatenate; or (b) re-run from scratch. For long runs consider chunking with `--limit` and incrementing tags (`_part1`, `_part2`).

---

## 8. What NOT to do

- ❌ **Don't edit the prompt YAML during the run.** Pin the commit hash; if a bug needs fixing, kill the run, fix on a branch, re-pin, re-start.
- ❌ **Don't share `.env` files.** Each person sets up their own (credentials may be scoped to user).
- ❌ **Don't commit outputs to git.** `outputs/` is already in `.gitignore`. The corpus will be shared via another channel (TBD: shared drive / object storage).
- ❌ **Don't run with the same `--output-tag` as the other run.** Files will be overwritten.
- ❌ **Don't skip the `--list-options` sanity check** before a long run. Catches typos in language codes (which silently filter to zero rows).
- ❌ **Don't run more than one Opus-provider job concurrently on the same token.** Shared rate limits cause cascading 429s. Coordinate the timing.
- ❌ **Don't push samples generated from a different commit hash than the rest of the corpus.** Mixing prompt versions invalidates the benchmark.

---

## 9. Cost & time budget summary

| Task | Records | Wall-clock (sequential, Opus 4-6) | Cost (Opus 4-6) |
|---|---|---|---|
| One-time smoke test (per person) | 3 | ~1.5 min | ~$0.06 |
| language_set1 (European half) | **2,837** | ~24 h | ~$57 |
| language_set2 (non-Latin half) | **2,673** | ~22 h | ~$53 |
| Paired-sweep (one person) | 890 | ~7.5 h | ~$18 |
| **Total** | **~6,400** | **~30 h (split between 2 people)** | **~$128** |

Add 15–20% buffer for retries / hiccups.

---

## 10. Final handoff

When all three jsonl files are merged and validated, the deliverable is:

| File | Lines | Purpose |
|---|---|---|
| `outputs/v3_2_phase1_records_combined.jsonl` | ~6,400 | The full Phase 1 corpus |
| `outputs/v3_2_phase1_summary_*.json` | (small) | Per-run R-rule pass rates and timing |
| `outputs/run_*.log` | (text) | Wall-clock logs for reproducibility |

Pin the corpus to the commit hash that produced it:
```bash
echo "Corpus generated from commit $(git rev-parse HEAD) on $(date -u +%Y-%m-%dT%H:%MZ)" \
    > outputs/CORPUS_PROVENANCE.txt
```

Share these via the team's agreed storage location (shared drive / object storage) — **not via git** (files are too large and `outputs/` is gitignored).

---

## Appendix — quick command reference

```bash
# Sanity
python pipeline/run_phase1_pipeline.py --help
python pipeline/run_phase1_pipeline.py --list-options

# Test (3 records, free-tier)
python pipeline/run_phase1_pipeline.py --provider sygra --limit 3 --output-tag test

# Production — language_set1 (European half, 13 langs)
python pipeline/run_phase1_pipeline.py \
    --language EN,ES,FR,DE,IT,PT_BR,PT_EU,NL,SV,DA,NO,FI,CS \
    --provider sygra_claude --output-tag language_set1

# Production — language_set2 (non-Latin + variants half, 12 langs)
python pipeline/run_phase1_pipeline.py \
    --language HU,TR,RU,AR,HE,JA,ZH_CN,ZH_TW,KO,TH,HI,FR_CA \
    --provider sygra_claude --output-tag language_set2

# Dry-run preview — verify filter math without API calls
python pipeline/run_phase1_pipeline.py \
    --language HU,TR,RU,AR,HE,JA,ZH_CN,ZH_TW,KO,TH,HI,FR_CA --limit 0

# Pilot — 50 records on language_set2 before committing to full ~22h run
python pipeline/run_phase1_pipeline.py \
    --language HU,TR,RU,AR,HE,JA,ZH_CN,ZH_TW,KO,TH,HI,FR_CA \
    --provider sygra_claude --limit 50 --output-tag language_set2_pilot

# Cheap pilot — same 50 on GPT-4o-mini (~5 min, ~$0.25) to catch bugs fast
python pipeline/run_phase1_pipeline.py \
    --language HU,TR,RU,AR,HE,JA,ZH_CN,ZH_TW,KO,TH,HI,FR_CA \
    --provider sygra --limit 50 --output-tag language_set2_pilot_4omini

# Single language drilldown
python pipeline/run_phase1_pipeline.py --language HI --limit 50 \
    --provider sygra_claude --output-tag hi_only

# Single entity drilldown
python pipeline/run_phase1_pipeline.py --entity Religion --limit 30 \
    --provider sygra_claude --output-tag religion_only

# Paired-sweep mode
python pipeline/run_phase1_pipeline.py --plan paired_sweep \
    --provider sygra_claude --output-tag paired
```
