# pii_bench_gen

Clean, curated bundle for PII benchmark generation (v3.2) using the true SyGra framework.

---

## Bundle layout

- `prompts/`: canonical prompt YAML and reviewer-friendly docs
- `catalog/`: pattern catalog, seed JSON, and CO mapping
- `samplers/`: deterministic seed and plan builders
- `seed/`: frozen plans, reports, and anchors
- `sygra_graph/`: SyGra graph config and `task_executor.py`
- `builders/`: prompt renderer helpers
- `runbook/`: generation guide
- `docs/`: flowchart, delta notes, and review snapshots

---

## Quick start (if you received only the zip)

```bash
unzip ~/Documents/pii_bench_gen.zip -d ~/Documents
export BUNDLE=~/Documents/pii_bench_gen
export SYGRA_ROOT=~/Documents/qw_ansygra4/SyGra
```

Copy required files into the active SyGra repo:

```bash
cp "$BUNDLE/sygra_graph/task_executor.py" "$SYGRA_ROOT/tasks/pii_generation_v3/task_executor.py"
cp "$BUNDLE/sygra_graph/graph_config.yaml" "$SYGRA_ROOT/tasks/pii_generation_v3/graph_config.yaml"

cp "$BUNDLE/prompts/generation_prompt_v3.yaml" "$SYGRA_ROOT/tasks/pii_generation/generation_prompt_v3.yaml"
cp "$BUNDLE/catalog/pattern_seed_data_v4.json" "$SYGRA_ROOT/tasks/pii_generation/pattern_seed_data_v4.json"
cp "$BUNDLE/seed/generation_plan.jsonl" "$SYGRA_ROOT/tasks/pii_generation/generation_plan.jsonl"
cp "$BUNDLE/seed/paired_sweep_plan.jsonl" "$SYGRA_ROOT/tasks/pii_generation/paired_sweep_plan.jsonl"
cp "$BUNDLE/seed/paired_sweep_anchors.json" "$SYGRA_ROOT/tasks/pii_generation/paired_sweep_anchors.json"

mkdir -p "$SYGRA_ROOT/tasks/pii_generation/outputs"
```

---

## Environment setup (`$SYGRA_ROOT/.env`)

For true SyGra framework runs, ensure:

```bash
SYGRA_CLAUDE_OPUS4-6_URL=https://<claude-opus-proxy-endpoint>
SYGRA_CLAUDE_OPUS_URL=https://<claude-opus-proxy-endpoint>
SYGRA_GPT-4O-MINI_URL=https://<gpt4o-mini-endpoint>
SYGRA_GPT-4O-MINI_TOKEN=<token>
```

`run1_full6400.sh` reads `SYGRA_CLAUDE_OPUS4-6_URL` and exports it to `SYGRA_CLAUDE_OPUS_URL` at runtime.

---

## One-command full run (recommended)

```bash
mkdir -p ~/Documents/pii_bench_gen/outputs
bash ~/Documents/pii_bench_gen/run1_full6400.sh 2>&1 | tee ~/Documents/pii_bench_gen/outputs/run1_29may_console.log
```

`run1_full6400.sh` supports these runtime knobs:

- `SANITY_BATCH_SIZE` (default `1`)
- `RUN_BATCH_SIZE` (default `5`)
- `CHECKPOINT_INTERVAL` (default `100`)
- `QUIET_TERMINAL` (default `1`, suppresses SyGra INFO spam in terminal)

Constraint: `CHECKPOINT_INTERVAL` must be a multiple of `RUN_BATCH_SIZE`.

Examples:

```bash
# default tuned run
RUN_BATCH_SIZE=5 CHECKPOINT_INTERVAL=100 \
bash ~/Documents/pii_bench_gen/run1_full6400.sh 2>&1 | tee ~/Documents/pii_bench_gen/outputs/run1_29may_console.log

# more aggressive concurrency
RUN_BATCH_SIZE=8 CHECKPOINT_INTERVAL=160 \
bash ~/Documents/pii_bench_gen/run1_full6400.sh 2>&1 | tee ~/Documents/pii_bench_gen/outputs/run1_29may_console.log

# verbose terminal (show full SyGra logs in console)
QUIET_TERMINAL=0 RUN_BATCH_SIZE=5 CHECKPOINT_INTERVAL=100 \
bash ~/Documents/pii_bench_gen/run1_full6400.sh
```

---

## Logging and interruption handling

- Main SyGra log file: `~/Documents/pii_bench_gen/SyGra/logs/out.log`
- Follow live logs in parallel terminal:

```bash
tail -f ~/Documents/pii_bench_gen/SyGra/logs/out.log
```

- Script console log (when using `tee`): `~/Documents/pii_bench_gen/outputs/run1_29may_console.log`
- Per-phase SyGra logs (always captured): `~/Documents/pii_bench_gen/outputs/logs/`
- If connection drops mid-run, `run1_full6400.sh` exits and restores `graph_config.yaml` via trap.
- Fast recovery for current script flow: re-run the same one-command run above.

### Optional SyGra CLI resume mode (advanced)

SyGra supports resumable execution for interrupted single-phase runs.

- Use `--resume true` and keep both:
  - `tasks/pii_generation_v3/metadata.json`
  - the output file used by that phase
- Do not delete those files before retrying.

Example resume command:

```bash
cd "$SYGRA_ROOT"
SYGRA_CLAUDE_OPUS_URL="$SYGRA_CLAUDE_OPUS4-6_URL" uv run python main.py \
  --task tasks.pii_generation_v3 \
  --num_records 5510 \
  --batch_size 1 \
  --checkpoint_interval 100 \
  --resume true \
  --run_name run1_29may_coverage
```

---

## True SyGra CLI commands

### 1) Coverage-only run (5510 records)

```bash
cd "$SYGRA_ROOT"

uv run python main.py \
  --task tasks.pii_generation_v3 \
  --num_records 5510 \
  --batch_size 1 \
  --run_name run1_29may_coverage

mv tasks/pii_generation/outputs/v3_2_corpus.jsonl \
   tasks/pii_generation/outputs/run1_29may_coverage.jsonl
```

### 2) Full corpus run (6400 records = 5510 + 890)

```bash
cd "$SYGRA_ROOT"

# Backup current graph config
cp tasks/pii_generation_v3/graph_config.yaml tasks/pii_generation_v3/graph_config.yaml.bak_run1_29may

# Coverage slice (5510)
uv run python main.py \
  --task tasks.pii_generation_v3 \
  --num_records 5510 \
  --batch_size 1 \
  --run_name run1_29may_coverage

mv tasks/pii_generation/outputs/v3_2_corpus.jsonl \
   tasks/pii_generation/outputs/run1_29may_coverage.jsonl

# Switch source plan to paired sweep
sed -i '' 's#tasks/pii_generation/generation_plan.jsonl#tasks/pii_generation/paired_sweep_plan.jsonl#' \
  tasks/pii_generation_v3/graph_config.yaml

# Paired slice (890)
uv run python main.py \
  --task tasks.pii_generation_v3 \
  --num_records 890 \
  --batch_size 1 \
  --run_name run1_29may_paired

mv tasks/pii_generation/outputs/v3_2_corpus.jsonl \
   tasks/pii_generation/outputs/run1_29may_paired.jsonl

# Merge final file
cat tasks/pii_generation/outputs/run1_29may_coverage.jsonl \
    tasks/pii_generation/outputs/run1_29may_paired.jsonl \
  > tasks/pii_generation/outputs/run1_29may_full6400.jsonl

# Validate counts
wc -l tasks/pii_generation/outputs/run1_29may_coverage.jsonl \
      tasks/pii_generation/outputs/run1_29may_paired.jsonl \
      tasks/pii_generation/outputs/run1_29may_full6400.jsonl

# Restore original graph config
mv tasks/pii_generation_v3/graph_config.yaml.bak_run1_29may tasks/pii_generation_v3/graph_config.yaml
```

Expected counts:
- `run1_29may_coverage.jsonl`: 5510
- `run1_29may_paired.jsonl`: 890
- `run1_29may_full6400.jsonl`: 6400

---

## 3 full runs policy (intentional config repeats, no text repeats)

If you run the full corpus 3 times for paper-quality sampling:

- same `config` repeated across runs is expected
- same normalized `text` repeated for the same config is a duplicate and must be regenerated

Use this rule:

- add `run_id` (`1/2/3`) and keep `record_id`
- define `config_id = sha256(plan_row_without_record_id)`
- after merging 3 runs, every `config_id` must appear exactly `3` times
- define `text_hash = sha256(normalize(text))` where normalize = lowercase + collapse whitespace
- if `(config_id, text_hash)` repeats, mark as duplicate and regenerate that sample
- optional: flag near-duplicates for same `config_id` when text similarity is very high

### Validator for 3 full runs

Run this after creating:

- `tasks/pii_generation/outputs/run1_29may_full6400.jsonl`
- `tasks/pii_generation/outputs/run2_29may_full6400.jsonl`
- `tasks/pii_generation/outputs/run3_29may_full6400.jsonl`

```bash
cd "$SYGRA_ROOT"

python3 - <<'PY'
import json, hashlib, re, itertools
from collections import defaultdict, Counter
from pathlib import Path

plans = [
    "tasks/pii_generation/generation_plan.jsonl",
    "tasks/pii_generation/paired_sweep_plan.jsonl",
]
runs = [
    ("1", "tasks/pii_generation/outputs/run1_29may_full6400.jsonl"),
    ("2", "tasks/pii_generation/outputs/run2_29may_full6400.jsonl"),
    ("3", "tasks/pii_generation/outputs/run3_29may_full6400.jsonl"),
]

def h(x: str) -> str:
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def normalize_text(t: str) -> str:
    return re.sub(r"\\s+", " ", (t or "").lower()).strip()

def config_id_from_plan_row(row: dict) -> str:
    base = {k: v for k, v in row.items() if k != "record_id"}
    s = json.dumps(base, sort_keys=True, separators=(",", ":"))
    return h(s)

def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.split()), set(b.split())
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / max(1, len(sa | sb))

rid_to_cfg = {}
for p in plans:
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            rid = str(row["record_id"])
            rid_to_cfg[rid] = config_id_from_plan_row(row)

all_rows = []
for run_id, fp in runs:
    with open(fp, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            rid = str(r.get("record_id", ""))
            cfg = rid_to_cfg.get(rid)
            text = r.get("text") or r.get("generated_text") or r.get("response_text") or ""
            norm = normalize_text(text)
            th = h(norm)
            all_rows.append({
                "run_id": run_id,
                "record_id": rid,
                "config_id": cfg,
                "text": text,
                "norm_text": norm,
                "text_hash": th,
            })

cfg_counts = Counter(r["config_id"] for r in all_rows if r["config_id"] is not None)
bad_cfg = {k: v for k, v in cfg_counts.items() if v != 3}

pair_groups = defaultdict(list)
for r in all_rows:
    pair_groups[(r["config_id"], r["text_hash"])].append(r)

exact_dups = []
for _, rows in pair_groups.items():
    if len(rows) > 1:
        exact_dups.extend(rows[1:])

by_cfg = defaultdict(list)
for r in all_rows:
    by_cfg[r["config_id"]].append(r)

near_dups = []
for cfg, rows in by_cfg.items():
    for a, b in itertools.combinations(rows, 2):
        sim = jaccard(a["norm_text"], b["norm_text"])
        if sim > 0.9 and a["text_hash"] != b["text_hash"]:
            near_dups.append({
                "config_id": cfg,
                "a_run": a["run_id"], "a_record_id": a["record_id"],
                "b_run": b["run_id"], "b_record_id": b["record_id"],
                "similarity": round(sim, 4),
            })

Path("tasks/pii_generation/outputs").mkdir(parents=True, exist_ok=True)
with open("tasks/pii_generation/outputs/regen_exact_duplicates.jsonl", "w", encoding="utf-8") as f:
    for r in exact_dups:
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")

with open("tasks/pii_generation/outputs/near_duplicates.jsonl", "w", encoding="utf-8") as f:
    for r in near_dups:
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")

print("Total rows:", len(all_rows))
print("Unique config_ids:", len(cfg_counts))
print("Config IDs with count != 3:", len(bad_cfg))
print("Exact duplicates to regenerate:", len(exact_dups))
print("Near-duplicate flags (>0.9):", len(near_dups))

if bad_cfg:
    print("ERROR: Some config_id counts are not exactly 3.")
if exact_dups:
    print("ERROR: Exact duplicates found. See regen_exact_duplicates.jsonl")
PY
```

### Regeneration workflow

1. Run validator and inspect `tasks/pii_generation/outputs/regen_exact_duplicates.jsonl`.
2. Regenerate only flagged samples for their `run_id` using same `record_id`/config.
3. Replace those rows in that run output file.
4. Re-run validator until:
   - each `config_id` count is `3`
   - `Exact duplicates to regenerate` is `0`
