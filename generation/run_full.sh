#!/usr/bin/env bash
set -euo pipefail

BUNDLE="${BUNDLE:-$HOME/Documents/pii_bench_gen}"
LOCAL_SYGRA="${LOCAL_SYGRA:-$BUNDLE/SyGra}"
RUN_TAG="${RUN_TAG:-run1_29may}"
SANITY_BATCH_SIZE="${SANITY_BATCH_SIZE:-1}"
RUN_BATCH_SIZE="${RUN_BATCH_SIZE:-5}"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-100}"
QUIET_TERMINAL="${QUIET_TERMINAL:-1}"

require_file() {
  local p="$1"
  if [[ ! -f "$p" ]]; then
    echo "Missing required file: $p" >&2
    exit 1
  fi
}

require_cmd() {
  local c="$1"
  if ! command -v "$c" >/dev/null 2>&1; then
    echo "Missing required command: $c" >&2
    exit 1
  fi
}

require_cmd uv
require_cmd sed
require_cmd wc
require_cmd grep

if (( RUN_BATCH_SIZE < 1 )); then
  echo "RUN_BATCH_SIZE must be >= 1" >&2
  exit 1
fi

if (( CHECKPOINT_INTERVAL < 1 )); then
  echo "CHECKPOINT_INTERVAL must be >= 1" >&2
  exit 1
fi

if (( CHECKPOINT_INTERVAL % RUN_BATCH_SIZE != 0 )); then
  echo "CHECKPOINT_INTERVAL ($CHECKPOINT_INTERVAL) must be a multiple of RUN_BATCH_SIZE ($RUN_BATCH_SIZE)" >&2
  exit 1
fi

require_file "$LOCAL_SYGRA/main.py"
require_file "$LOCAL_SYGRA/.env"
require_file "$BUNDLE/sygra_graph/task_executor.py"
require_file "$BUNDLE/sygra_graph/graph_config.yaml"
require_file "$BUNDLE/prompts/generation_prompt_v3.yaml"
require_file "$BUNDLE/catalog/pattern_seed_data_v4.json"
require_file "$BUNDLE/seed/generation_plan.jsonl"
require_file "$BUNDLE/seed/paired_sweep_plan.jsonl"
require_file "$BUNDLE/seed/paired_sweep_anchors.json"

mkdir -p "$LOCAL_SYGRA/tasks/pii_generation/outputs"
mkdir -p "$BUNDLE/outputs"
mkdir -p "$BUNDLE/outputs/logs"

cp "$BUNDLE/sygra_graph/task_executor.py" "$LOCAL_SYGRA/tasks/pii_generation_v3/task_executor.py"
cp "$BUNDLE/sygra_graph/graph_config.yaml" "$LOCAL_SYGRA/tasks/pii_generation_v3/graph_config.yaml"
cp "$BUNDLE/prompts/generation_prompt_v3.yaml" "$LOCAL_SYGRA/tasks/pii_generation/generation_prompt_v3.yaml"
cp "$BUNDLE/catalog/pattern_seed_data_v4.json" "$LOCAL_SYGRA/tasks/pii_generation/pattern_seed_data_v4.json"
cp "$BUNDLE/seed/generation_plan.jsonl" "$LOCAL_SYGRA/tasks/pii_generation/generation_plan.jsonl"
cp "$BUNDLE/seed/paired_sweep_plan.jsonl" "$LOCAL_SYGRA/tasks/pii_generation/paired_sweep_plan.jsonl"
cp "$BUNDLE/seed/paired_sweep_anchors.json" "$LOCAL_SYGRA/tasks/pii_generation/paired_sweep_anchors.json"

GRAPH_CFG="$LOCAL_SYGRA/tasks/pii_generation_v3/graph_config.yaml"
BACKUP_CFG="$LOCAL_SYGRA/tasks/pii_generation_v3/graph_config.yaml.bak_${RUN_TAG}_$(date +%Y%m%d_%H%M%S)"
cp "$GRAPH_CFG" "$BACKUP_CFG"

restore_graph_config() {
  if [[ -f "$BACKUP_CFG" ]]; then
    cp "$BACKUP_CFG" "$GRAPH_CFG"
  fi
}
trap restore_graph_config EXIT

RAW_OUT="$LOCAL_SYGRA/tasks/pii_generation/outputs/v3_2_corpus.jsonl"
COVERAGE_OUT="$LOCAL_SYGRA/tasks/pii_generation/outputs/${RUN_TAG}_coverage.jsonl"
PAIRED_OUT="$LOCAL_SYGRA/tasks/pii_generation/outputs/${RUN_TAG}_paired.jsonl"
FULL_OUT="$LOCAL_SYGRA/tasks/pii_generation/outputs/${RUN_TAG}_full6400.jsonl"
SANITY_OUT="$LOCAL_SYGRA/tasks/pii_generation/outputs/${RUN_TAG}_opus_sanity.jsonl"

OPUS_URL="$(grep '^SYGRA_CLAUDE_OPUS4-6_URL=' "$LOCAL_SYGRA/.env" | sed 's/^SYGRA_CLAUDE_OPUS4-6_URL=//')"
if [[ -z "$OPUS_URL" ]]; then
  echo "Missing SYGRA_CLAUDE_OPUS4-6_URL in $LOCAL_SYGRA/.env" >&2
  exit 1
fi

run_sygra_phase() {
  local phase="$1"
  local phase_total="$2"
  shift 2
  local phase_log="$BUNDLE/outputs/logs/${RUN_TAG}_${phase}.log"
  : > "$phase_log"

  if [[ "$QUIET_TERMINAL" == "1" ]]; then
    local run_pid
    local last_progress=""
    SYGRA_CLAUDE_OPUS_URL="$OPUS_URL" uv run python main.py "$@" >> "$phase_log" 2>&1 &
    run_pid=$!

    while kill -0 "$run_pid" 2>/dev/null; do
      local progress=""

      progress="$(tail -n 200 "$phase_log" | tr '\r' '\n' | grep -Eo '[0-9]+/[0-9]+' | tail -1 || true)"

      if [[ -z "$progress" ]]; then
        progress="$(tail -n 200 "$phase_log" | sed -nE 's/.*Processed ([0-9]+) out of ([0-9]+) records.*/\1\/\2/p' | tail -1 || true)"
      fi

      if [[ -z "$progress" && -n "$phase_total" ]]; then
        progress="0/$phase_total"
      fi

      if [[ -n "$progress" && "$progress" != "$last_progress" ]]; then
        printf "\r[%s] %s" "$phase" "$progress"
        last_progress="$progress"
      fi

      sleep 2
    done

    if ! wait "$run_pid"; then
      printf "\n" >&2
      echo "Phase '$phase' failed. See: $phase_log" >&2
      tail -n 40 "$phase_log" >&2 || true
      exit 1
    fi

    if [[ -n "$phase_total" ]]; then
      printf "\r[%s] %s/%s\n" "$phase" "$phase_total" "$phase_total"
    elif [[ -n "$last_progress" ]]; then
      printf "\r[%s] %s\n" "$phase" "$last_progress"
    else
      printf "\n"
    fi
  else
    SYGRA_CLAUDE_OPUS_URL="$OPUS_URL" uv run python main.py "$@" 2>&1 | tee -a "$phase_log"
  fi
}

cd "$LOCAL_SYGRA"

echo "Run settings: sanity_batch=$SANITY_BATCH_SIZE, run_batch=$RUN_BATCH_SIZE, checkpoint_interval=$CHECKPOINT_INTERVAL"
echo "Terminal logs: $( [[ "$QUIET_TERMINAL" == "1" ]] && echo "quiet (file logs only)" || echo "verbose" )"

echo "[1/7] Opus sanity run (1 record)"
rm -f "$RAW_OUT"
run_sygra_phase "sanity" \
  "1" \
  --task tasks.pii_generation_v3 \
  --num_records 1 \
  --batch_size "$SANITY_BATCH_SIZE" \
  --checkpoint_interval "$CHECKPOINT_INTERVAL" \
  --run_name "${RUN_TAG}_opus_sanity"

if [[ ! -f "$RAW_OUT" ]]; then
  echo "Sanity run failed: expected output not found: $RAW_OUT" >&2
  exit 1
fi

SANITY_COUNT="$(wc -l < "$RAW_OUT" | tr -d ' ')"
echo "Sanity output line count: $SANITY_COUNT"
if [[ "$SANITY_COUNT" != "1" ]]; then
  echo "Sanity check failed: expected exactly 1 line, got $SANITY_COUNT. Stopping." >&2
  mv "$RAW_OUT" "$SANITY_OUT.failed"
  exit 1
fi
mv "$RAW_OUT" "$SANITY_OUT"
echo "Sanity check passed. Continuing full run."

echo "[2/7] Coverage run (5510)"
rm -f "$RAW_OUT"
run_sygra_phase "coverage" \
  "5510" \
  --task tasks.pii_generation_v3 \
  --num_records 5510 \
  --batch_size "$RUN_BATCH_SIZE" \
  --checkpoint_interval "$CHECKPOINT_INTERVAL" \
  --run_name "${RUN_TAG}_coverage"

if [[ ! -f "$RAW_OUT" ]]; then
  echo "Expected output not found: $RAW_OUT" >&2
  exit 1
fi
mv "$RAW_OUT" "$COVERAGE_OUT"

echo "[3/7] Switch graph source to paired_sweep_plan.jsonl"
sed -i '' 's#tasks/pii_generation/generation_plan.jsonl#tasks/pii_generation/paired_sweep_plan.jsonl#' "$GRAPH_CFG"

echo "[4/7] Paired run (890)"
rm -f "$RAW_OUT"
run_sygra_phase "paired" \
  "890" \
  --task tasks.pii_generation_v3 \
  --num_records 890 \
  --batch_size "$RUN_BATCH_SIZE" \
  --checkpoint_interval "$CHECKPOINT_INTERVAL" \
  --run_name "${RUN_TAG}_paired"

if [[ ! -f "$RAW_OUT" ]]; then
  echo "Expected output not found: $RAW_OUT" >&2
  exit 1
fi
mv "$RAW_OUT" "$PAIRED_OUT"

echo "[5/7] Merge full 6400"
cat "$COVERAGE_OUT" "$PAIRED_OUT" > "$FULL_OUT"

echo "[6/7] Verify line counts"
wc -l "$COVERAGE_OUT" "$PAIRED_OUT" "$FULL_OUT"

echo "[7/7] Copy outputs to $BUNDLE/outputs"
cp "$SANITY_OUT" "$BUNDLE/outputs/"
cp "$COVERAGE_OUT" "$BUNDLE/outputs/"
cp "$PAIRED_OUT" "$BUNDLE/outputs/"
cp "$FULL_OUT" "$BUNDLE/outputs/"

echo "Done."
echo "Sanity:   $SANITY_OUT"
echo "Coverage: $COVERAGE_OUT"
echo "Paired:   $PAIRED_OUT"
echo "Full:     $FULL_OUT"
echo "Copied to: $BUNDLE/outputs"
echo "Phase logs: $BUNDLE/outputs/logs"
