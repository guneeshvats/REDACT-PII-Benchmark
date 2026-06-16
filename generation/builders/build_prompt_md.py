"""Render generation_prompt_v3.yaml as a clean Markdown document.

Produces PII_Benchmark_Generation_Prompt_v3.md alongside the existing
.yaml (source of truth) and .docx (styled view). The markdown rendering
is intended for reading, code review, and sharing with collaborators
who prefer markdown over docx.
"""

import json
import yaml
from pathlib import Path

HERE = Path(__file__).parent
SRC  = HERE / "generation_prompt_v3.yaml"
DST  = HERE / "PII_Benchmark_Generation_Prompt_v3.md"


# ── Few-shot titles (matches the docx builder for consistency) ───────────────
FS_TITLES = {
    0:  "Few-shot #1 — Adjacency=tight / CO-008 email metadata block (multi-mention test, full v3.1 schema)",
    1:  "Few-shot #2 — Adjacency=tight / CO-009 patient header (healthcare)",
    2:  "Few-shot #3 — Hypothetical SSN (disclosed=false)",
    3:  "Few-shot #4 — Partial PII (disclosure_form=partial)",
    4:  "Few-shot #5 — Hard OCR distortion across 8 entity types",
    5:  "Few-shot #6 — Heavy Hindi-English code-switching",
    6:  "Few-shot #7 — Cross-sentence coreference (pronouns NOT tagged)",
    7:  "Few-shot #8 — Japanese JSON record / CO-012 HR cluster (non-Latin)",
    8:  "Few-shot #9 — Arabic RTL / key_value_pairs / density=high (Article 9 + IBAN)",
    9:  "Few-shot #10 — Negation frame / ticket_worknotes (Article 9: Religion + Crime)",
    10: "Few-shot #11 — Paired-sweep mode (v3.2) / anchor A-042 / frozen entity values (R16)",
}


def render_axis_table(axes_dict):
    """Render an axes dict as a 2-column markdown table."""
    lines = ["| Axis | Value |", "|---|---|"]
    for k, v in axes_dict.items():
        # Represent lists (e.g., frozen_entity_values) as multi-line block in cell
        if isinstance(v, list):
            v_repr = "<br>".join(f"`{item}`" for item in v)
        else:
            v_repr = f"`{v}`" if not isinstance(v, str) or (" " not in v and "\"" not in v) else v
        lines.append(f"| `{k}` | {v_repr} |")
    return "\n".join(lines)


def pretty_json(json_str):
    """Re-format embedded JSON for readability."""
    s = json_str.strip()
    try:
        obj = json.loads(s)
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return s


def main():
    data = yaml.safe_load(SRC.read_text(encoding="utf-8"))

    out = []

    # ── Header ───────────────────────────────────────────────────────────────
    out.append("# PII Benchmark — Generation Prompt v3.2")
    out.append("")
    out.append("**Specialized prompt for synthetic eval-data generation**  ")
    out.append("**51 entities × 9 axes × 25 languages | 16 hard rules | 11 few-shots | Paired-Sweep Mode + Track 1 Scoping**")
    out.append("")
    out.append("**Authors:** Anonymous Authors  ")
    out.append("**Affiliation:** Anonymous Institution  ")
    out.append("**Version:** 3.2 — Paired-Sweep + Synthetic–Real Validation + Track 1 scoping  ")
    out.append("**Date:** May 2026")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## About this prompt")
    out.append("")
    out.append("This document is the generation prompt used to produce ground-truth records "
               "for the PII Detection Benchmark (Track 1). It is consumed by a single LLM call: "
               "the model emits the passage and the entity list; character offsets are computed "
               "downstream by deterministic string alignment (LLMs do not produce offsets — "
               "Issues doc §D.12).")
    out.append("")
    out.append("It addresses every prompt-addressable gap from the v3 Gap Analysis (A5 behavioral "
               "matrix, B3 negation/hypothetical, B4 partial/obfuscated, B5 cross-sentence "
               "coreference, C3 nested spans, D3/Article-9 sensitivity, F2 format & checksum "
               "validity). Pipeline-, sampler-, and audit-level gaps are out of scope.")
    out.append("")
    out.append("Companion artefacts:")
    out.append("- `generation_prompt_v3.yaml` — canonical source (this is rendered from it)")
    out.append("- `PII_Benchmark_Generation_Prompt_v3.docx` — Word version for non-technical reviewers")
    out.append("- `PII_Benchmark_Methodology_Final.docx` — full methodology, evaluation framework, and integration spec")
    out.append("- `PII_Pattern_Catalog_v4_MASTER.md` — pattern source (4,127 patterns across 51 entities)")
    out.append("- `co_to_v4_mapping.json` — v3 CO-### → v4 anchor patterns")
    out.append("")
    out.append("---")
    out.append("")

    # ── System Prompt ────────────────────────────────────────────────────────
    out.append("## 1. System Prompt")
    out.append("")
    out.append("Sent as the system message on every generation call. R1–R16 are enforced; "
               "the output schema is authoritative (overrides any older few-shot pattern).")
    out.append("")
    out.append("```")
    out.append(data["system_prompt"].rstrip())
    out.append("```")
    out.append("")
    out.append("---")
    out.append("")

    # ── User Prompt Template ─────────────────────────────────────────────────
    out.append("## 2. User Prompt Template")
    out.append("")
    out.append("Axis values in `{{ }}` are interpolated by the sampler (covering array, "
               "not random). Every record gets a fully-resolved 9-axis configuration plus "
               "a behavioral_frame, a generation mode (coverage | paired_sweep), and either "
               "a `prior_passages_summary` (coverage mode) or a paired-sweep anchor block "
               "(paired_sweep mode).")
    out.append("")
    out.append("```")
    out.append(data["user_prompt"].rstrip())
    out.append("```")
    out.append("")
    out.append("---")
    out.append("")

    # ── Few-shots ────────────────────────────────────────────────────────────
    out.append("## 3. Few-Shots")
    out.append("")
    out.append("Eleven examples chosen to anchor the cases v2 prompts got wrong. Each example "
               "shows the axis configuration that produced it (top) and the exact JSON the model "
               "must emit (bottom). Few-shot #1 demonstrates the FULL v3.1 schema (with "
               "`sensitivity_tier` and `nesting_parent` per R14/R11); few-shot #11 demonstrates "
               "v3.2 paired-sweep mode with frozen entity pinning (R16). Both are canonical "
               "patterns.")
    out.append("")

    for i, fs in enumerate(data["few_shots"]):
        out.append(f"### {FS_TITLES.get(i, f'Few-shot #{i+1}')}")
        out.append("")
        out.append("**Axis configuration:**")
        out.append("")
        out.append(render_axis_table(fs["axes"]))
        out.append("")
        out.append("**Expected output (verbatim):**")
        out.append("")
        out.append("```json")
        out.append(pretty_json(fs["output"]))
        out.append("```")
        out.append("")

    out.append("---")
    out.append("")

    # ── Integration Notes ────────────────────────────────────────────────────
    out.append("## 4. Integration Notes")
    out.append("")
    out.append("Operational notes for wiring this prompt into the SyGra `graph_config.yaml`. "
               "These are decisions for the pipeline, not the prompt itself.")
    out.append("")
    integ = data.get("integration", {})
    for key, val in integ.items():
        out.append(f"### {key.replace('_', ' ').title()}")
        out.append("")
        if isinstance(val, str):
            out.append(val.rstrip())
        else:
            out.append(str(val))
        out.append("")

    out.append("---")
    out.append("")

    # ── A→G coverage map summary ──────────────────────────────────────────────
    out.append("## 5. A→G Gap Coverage Map (summary)")
    out.append("")
    out.append("Full table in `PII_Benchmark_Methodology_Final.docx` §5. Summary:")
    out.append("")
    out.append("| Section | Gap | Status | Where in prompt |")
    out.append("|---|---|---|---|")
    rows = [
        ("A5", "No CheckList behavioral matrix", "✅", "`behavioral_frame` slot + few-shots #3, #4, #5, #7, #10"),
        ("B3", "Negation/hypothetical missing", "✅", "R7 `disclosed` field + few-shots #3, #10"),
        ("B4", "Partial/obfuscated missing", "✅", "R7 `disclosure_form` + R8 OCR rules + few-shots #4, #5"),
        ("B5", "Cross-sentence coreference", "✅", "`behavioral_frame=cross_sentence` + few-shot #7"),
        ("C3", "Nested span policy", "✅", "R11 triple-name rule + `nesting_parent` field"),
        ("D3", "GDPR Article 9 / sensitivity", "✅", "R14 `sensitivity_tier` + few-shots #9, #10"),
        ("F2", "Format/checksum compliance", "✅", "R12 format-validity contract"),
    ]
    for sec, gap, status, where in rows:
        out.append(f"| {sec} | {gap} | {status} | {where} |")

    out.append("")
    out.append("**Score:** 7/7 prompt-addressable gaps covered. Catalog-level gaps (A4, D1, D2) "
               "resolved by Catalog v3/v4. The other 17 items in the Gap Analysis are correctly "
               "out of scope for the prompt (they belong to the sampler, pipeline, audit, or "
               "process layer).")
    out.append("")

    out.append("---")
    out.append("")
    out.append(f"*Generated from `generation_prompt_v3.yaml` by `build_prompt_md.py` on {__import__('datetime').date.today().isoformat()}.*")
    out.append("")

    DST.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {DST}")
    print(f"Size: {DST.stat().st_size / 1024:.1f} KB")
    print(f"Lines: {len(out)}")


if __name__ == "__main__":
    main()
