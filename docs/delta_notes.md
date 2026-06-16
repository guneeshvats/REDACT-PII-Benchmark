# PII Data Generation v3 — Delta from Raw SyGra

## 1) Purpose

This document is the implementation-level reference for what was added/customized for PII data generation compared to base (raw) SyGra framework behavior.

It covers:
- Components and files
- Function/class inventory
- Current runnable paths (standalone + SyGra graph)
- Final SyGra wiring changes and validation status

---

## 2) Raw SyGra Baseline (Framework Layer)

These are framework capabilities we are building on (not PII-specific):

- `main.py`
  - CLI entrypoint for `--task`, `--num_records`, batching, logging, and execution dispatch.
- `sygra/core/base_task_executor.py`
  - Loads task `graph_config.yaml`, source data, sink config (`data_config.sink`), compiles graph, executes records.
- `sygra/core/graph/graph_config.py`
  - Parses node/edge config and state variables.
- `sygra/core/graph/langgraph/graph_builder.py`
  - Adds nodes/edges and conditional routing (expects condition function + `path_map` for conditional edges).
- `sygra/core/graph/nodes/llm_node.py`
  - LLM node wrapper, pre-process, prompt render, post-process, metadata/tokens.
- `sygra/core/graph/nodes/lambda_node.py`
  - Lambda node execution. Requires config key `lambda:`.
- `sygra/core/dataset/file_handler.py`
  - JSON/JSONL/CSV/parquet I/O abstraction.
- `sygra/config/models.yaml`
  - Central model registry and model runtime settings.

---

## 3) PII Add-ons (Task Layer)

## 3.1 Methodology + Prompt + Seed Inputs

- `pii_generation/methodology_final.md`
  - Design specification for v3.2 methodology (coverage axes, behavioral frames, quality rules).
- `pii_generation/generation_prompt_v3.yaml`
  - Generation contract (system/user prompt, few-shots, schema/rules).
- `pii_generation/PII_Pattern_Catalog_v4_MASTER 1.md`
  - Authored source catalog of PII patterns.
- `pii_generation/pattern_seed_data_v4.json`
  - Structured pattern seed produced from catalog markdown.

## 3.2 Seed and Plan Builders

### A) `pii_generation/build_pattern_seed_v4.py`
Builds seed JSON from markdown catalog.

Function inventory:
- `split_examples_cell`
- `infer_language_hint`
- `parse_pattern_table_row`
- `parse_sweep_table_row`
- `parse_entity_section`
- `main`

### B) `pii_generation/build_generation_plan.py`
Builds `generation_plan.jsonl` using covering-array style sampling + constraints.

Function inventory:
- `make_scenario_seed`
- `pick_target_pattern`
- `pick_behavioral_frame`
- `pick_co_pattern`
- `enrich_row`
- `main`

### C) `pii_generation/build_paired_sweep_plan.py`
Builds `paired_sweep_plan.jsonl` for matched-anchor sweeps.

Function inventory (major):
- Fictional value generators:
  - `fictional_email`, `fictional_dob`, `fictional_nid`, `fictional_mrn`, `fictional_employee_id`, `fictional_business_title`, `fictional_org`
- Anchor builders:
  - `build_base_anchor`, `build_stress_test_anchor`, `build_article_9_anchor`, `build_non_latin_anchor`, `build_co_pattern_anchor`
- Sweep executors:
  - `sweep_format`, `sweep_domain`, `sweep_difficulty_density`
- Target enrichment:
  - `enrich_variant_with_target`
- Entrypoint:
  - `main`

Generated artifacts:
- `pii_generation/generation_plan.jsonl`
- `pii_generation/generation_plan_report.json`
- `pii_generation/paired_sweep_plan.jsonl`
- `pii_generation/paired_sweep_plan_report.json`
- `pii_generation/paired_sweep_anchors.json`

## 3.3 Standalone v3 Runtime (Current Runnable Path)

- `pii_generation/run_phase1_pipeline.py`
  - Executes v3 flow without SyGra graph runtime.
  - Flow: `plan row -> prompt render -> LLM call -> JSON parse -> multi-mention expansion -> self-check -> write output`.

Function inventory:
- `select_checks_for_record`
- `build_plan_row_as_test_config`
- `generate_one_record`
- `main`

- `pii_generation/expand_multi_mentions.py`
  - Deterministic Stage-3 style occurrence expansion.

Function inventory:
- `expand_multi_mentions`
- `_count_occurrences`
- `expand_corpus_jsonl`
- `_entity_count`

- `pii_generation/smoke_test/run_smoke_test.py`
  - Prompt/API smoke harness.

Function inventory:
- `load_dotenv`
- `render_user_prompt`
- `build_few_shot_messages`
- `call_anthropic`
- `call_sygra_claude_opus`
- `call_sygra_gpt4o_mini`
- `run_auto`
- `run_manual`
- `run_check`
- `main`

## 3.4 SyGra-Orchestrated PII Task Customization (Existing Reservoir Path)

- `pii_generation/graph_config.yaml`
  - Task DAG configuration for PII pipeline nodes/output map.
- `pii_generation/task_executor.py`
  - Custom post-processors + lambda transforms + output generator.

Class/function inventory:
- `_parse_entity_json`
- `_validate_entity_format`
- `PiiTextPostProcessor`
- `PiiEntityPostProcessor`
- `PiiVerifyPostProcessor`
- `_find_all_occurrences`
- `validate_and_fix_entities`
- `enrich_latent_schema`
- `PiiOutputGenerator`

---

## 4) Raw SyGra vs PII Add-on Delta (At-a-Glance)

| Area | Raw SyGra | PII Add-on |
|---|---|---|
| Input data | Generic task input | Pattern catalog -> seed JSON -> generation plans |
| Diversity control | Generic sampling | 9-axis coverage + CO patterns + behavioral frames |
| Prompting | Task-dependent | Large v3 YAML prompt with strict schema/rules/few-shots |
| Runtime path | Graph via task config | Standalone script path added for rapid v3 iteration |
| Entity handling | Generic post-process | PII-specific parsing, validation, canonicalization, enrichment |
| Output schema | Framework map | PII latent schema and per-record validation metadata |
| Modes | Generic | Coverage mode + paired-sweep mode |
| Verification | Optional generic | Rule-driven self-check and conditional verify logic |

---

## 5) Current Status

## 5.1 What is runnable now

- Standalone v3 generation is runnable from:
  - `pii_generation/run_phase1_pipeline.py`
- It does not require SyGra graph compilation/runtime to execute.

## 5.2 SyGra CLI wiring status (`--task pii_generation_v3`)

Task config exists at:
- `pii_generation_v3/graph_config.yaml`

Implemented wiring changes:
1. Added missing module: `tasks/pii_generation_v3/task_executor.py`.
2. Updated lambda nodes to use `lambda:` key.
3. Replaced inline edge expressions with SyGra conditional routing (`condition` + `path_map`) via:
   - `SelfCheckRoute`
   - `VerifyRoute`
4. Added explicit `START` and `END` edges.
5. Migrated output config from `data_config.output` to `data_config.sink`.
6. Corrected sink type to SyGra output enum (`type: jsonl`), with output path retained.
7. Added required `prompt` blocks on LLM nodes for graph validation.
8. Added explicit `output_config.output_map` for stable sink serialization.
9. Removed duplicate list-style `output_keys` across nodes to satisfy SyGra GraphConfig uniqueness rules.
10. Updated verifier model override key from `maxTokens` to `max_tokens` for `gpt-4o-mini` compatibility.

Validation evidence:
- YAML parse: `tasks/pii_generation_v3/graph_config.yaml` loads successfully.
- Python compile/import: `tasks/pii_generation_v3/task_executor.py` compiles/imports in `.venv`.
- Graph build/compile: `GraphConfig + LangGraphBuilder` succeeds for `pii_generation_v3`.
- CLI smoke invocation reaches runtime model checks, but can fail if model endpoint/DNS/auth is unavailable.

---

## 6) Portable Bundle Notes

This document accompanies portable bundle:
- `portable/pii_generation_v3_portable`

Primary runnable assets in bundle:
- `pii_generation/generation_prompt_v3.yaml`
- `pii_generation/pattern_seed_data_v4.json`
- `pii_generation/generation_plan.jsonl`
- `pii_generation/paired_sweep_plan.jsonl`
- `pii_generation/run_phase1_pipeline.py`
- `pii_generation/smoke_test/*`
- `pii_generation_v3/graph_config.yaml` (draft for orchestration wiring)

---

## 7) Change Control Recommendation

For each new PII-generation change, update this document with:
- File path
- Added/modified component
- Function/class names
- Reason for change
- Runtime impact (standalone, graph, or both)
- Validation evidence (smoke run, sample size, summary path)
