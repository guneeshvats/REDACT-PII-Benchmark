# PII Benchmark — Metrics & Methods Reference

Quick reference for what each metric measures, the paper that introduced it,
and how it's framed in our submission. Use this when writing §4 (Evaluation
Framework) and §5 (Results).

---

## Family A — Coverage

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| A1 | Pattern coverage rate | (catalog framing, novel) | ≥50% (v1) |
| A2 | Per-entity-type floor | (operational, novel) | ≥50 records |
| A3 | Language tier coverage (P1/P2/P3) | (operational, novel) | 100% per tier |
| A4 | Pairwise axis coverage | NIST SP 800-142 (Kuhn et al., covering arrays) | ≥98% mean |
| A5 | Behavioral matrix coverage | CheckList (Ribeiro et al., ACL 2020) | descriptive |

**Paper framing:** "Coverage is enforced through a strength-2 covering array
sampler that guarantees every pair of axis values is exercised."

---

## Family B — Annotation Integrity (Critical Gates)

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| B1 | Offset accuracy | (deterministic-alignment framing) | 100% (after R2 repair) |
| B2 | Zero-entity rate | (operational) | ≤0.5% |
| B4 | Triple-name rule | (decomposition framing, novel) | ≥95% |
| B5 | Canonical-type compliance | (taxonomy enforcement) | 100% |
| B6 | Multi-mention completeness | (operational R4) | ≥95% (100% after R1) |

**Paper framing:** "Annotation integrity is enforced *by construction*: offsets
and multi-mentions are recomputed deterministically post-LLM via `text.find()`
iteration, eliminating LLM-compliance dependence."

---

## Family C — Diversity

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| C1 | Shannon entropy (entity-type) | Shannon 1948 | ≥4.0 bits |
| C2 | Distinct-1, Distinct-2, Distinct-3 | Li et al., NAACL 2016 | descriptive |
| C3 | Self-BLEU-3, Self-BLEU-4 | Zhu et al., SIGIR 2018 | Self-BLEU-3 ≤0.35 |
| C4 | ROUGE-L intra-stratum mean | Lin, ACL 2004; Wang et al. (Self-Instruct), ACL 2023 | ≤0.70 |
| C5 | Type-Token Ratio | Tweedie & Baayen, J. Quant. Ling. 1998 | descriptive |
| **C6** | **Vendi Score** | **Friedman & Dieng, 2023** | descriptive |
| **C7** | **SBERT semantic diversity** | **Reimers & Gurevych, EMNLP 2019; Gao et al., EMNLP 2021** | descriptive |
| **C8** | **Pattern density per record-bucket** | (novel) | descriptive |

**Paper framing:** "Diversity is evaluated along eight dimensions covering
lexical (Distinct-n, Self-BLEU), structural (ROUGE-L, TTR), semantic (Vendi,
SBERT), and pattern-level (C8) axes. No prior PII benchmark reports
multi-dimensional diversity at this granularity."

The **bolded** ones are the strongest differentiation in our submission since
they go beyond what PIIBench / AI4Privacy / TAB report.

---

## Family E — Format Compliance

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| E1 | Email RFC 5322 | RFC 5322 | ≥95% |
| E2 | Credit card Luhn | ISO/IEC 7812-1 | ≥95% |
| E3 | IBAN mod-97 | ISO 13616 | ≥95% |
| E4 | US SSN format | SSA published format rules | ≥95% |
| E5 | IPv4 / IPv6 valid | RFC 5952 | ≥95% |

**Paper framing:** "Format-bound entities are checksum-validated post-
generation to ensure structural plausibility."

---

## Family F — Behavioral Soundness

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| F1-F4 | Behavioral frame coverage | CheckList (Ribeiro et al., ACL 2020) | descriptive |
| **F5** | **Per-disclosure-form stratified F1** | **(novel — Track 1 contribution)** | descriptive |
| **F6** | **Per-sensitivity-tier stratified F1** | **(novel — Track 1 contribution)** | descriptive |

**F5 and F6 are the novel contribution** — no prior PII benchmark reports
stratified detector F1 by disclosure form or sensitivity tier. These metrics
operationalize the metadata fields and show detectors degrade on partial /
obfuscated / Article 9 categories.

**Paper framing:** "We evaluate the three metadata fields (`disclosed`,
`disclosure_form`, `sensitivity_tier`) by computing stratified F1 across each
metadata axis; substantial gaps demonstrate that aggregate F1 hides clinically
important failure modes."

---

## Family G — LLM-as-Judge (with Bias Mitigations)

| ID | Metric | Citation |
|---|---|---|
| G1 | G-Eval coherence/realism/authenticity/quality | Liu et al., 2023 |
| G2 | Cross-judge agreement (Krippendorff's α) | Krippendorff 2004 |

**Bias mitigations** applied (defensible against reviewer skepticism):

1. **Different judge model from generator** — Generator is Claude Opus; judge
   is GPT-4o-mini + Claude Haiku. Mitigates self-preference bias
   (Panickssery et al., NeurIPS 2024).
2. **Two-judge cross-validation** — Both judges score independently. Report
   Krippendorff's α; drop the metric if α < 0.5. Mitigates single-judge bias
   (Zheng et al., NeurIPS 2023).
3. **Chain-of-thought rubric** — Force explicit reasoning per dimension
   before scoring. Mitigates shortcut bias (Liu et al., 2023).
4. **Probability-weighted scoring** (G-Eval's signature trick) — expected
   value over full token-probability distribution, not just argmax. Reduces
   variance.
5. **Stratified sampling** — Sample evaluated records uniformly across
   languages to avoid majority-language dominance.

**Paper framing:** "We compute G-Eval (Liu et al., 2023) using two
independent judges and apply standard bias mitigations from the LLM-as-judge
literature (Panickssery 2024, Zheng 2023). Inter-judge Krippendorff's α is
reported as a reliability gate."

---

## Family J — Distributional Match (against real PII corpora)

| ID | Metric | Citation | Reference |
|---|---|---|---|
| J1 | MAUVE vs. TAB | Pillutla et al., NeurIPS 2021 | Pilán et al., TAB, CL 2022 |

**For the submission:** MAUVE against TAB only (publicly downloadable).
i2b2/n2c2 dropped due to DUA timeline. Frame as: "We compute distributional
similarity against the publicly-available TAB legal-domain corpus. Extension
to clinical PHI corpora is named as future work."

---

## Family K — Synthetic-Real Ranking Correlation (the Validity Test)

| ID | Metric | Citation | Threshold |
|---|---|---|---|
| K1 | Kendall's τ | Kendall 1938 | ≥0.70 (point) |
| K2 | Spearman's ρ | Spearman 1904 | ≥0.70 (point) |
| K3 | Mean abs F1 delta | (operational) | ≤0.10 |
| K4 | Bootstrap 95% CI | Efron 1979 | report CI |

**Why this matters:** This is the **operational validity test for the
benchmark** (Kiela et al., NeurIPS 2021 — DynaBench framework). If detectors
ranked by performance on our synthetic corpus rank the same way on real
TAB data, our benchmark is a valid proxy. If not, the benchmark has limited
external validity.

**Honest framing for n=300:** The bootstrap CI on Kendall's τ at n=300 and
5 detectors is approximately ±0.20. We report the point estimate and full CI
and frame as "necessary but not sufficient" evidence per Kiela 2021.

**Paper framing:** "We evaluate benchmark validity via Family K: do detectors
ranked by F1 on our synthetic corpus rank consistently on real-data corpora?
We compute Kendall's τ and Spearman's ρ between detector rankings on a
300-record synthetic subset and the same detectors on TAB, with bootstrap
confidence intervals."

---

## Sections of the paper where each family appears

| Family | Section |
|---|---|
| A — Coverage | §3 Construction; §5.1 Results |
| B — Annotation Integrity | §3 Construction; §5.1 Critical gates table |
| C — Diversity | §5.1 Diversity table |
| D — Linguistic Quality | DEFERRED to camera-ready |
| E — Format/Checksum | §5.1 Format compliance row |
| F — Behavioral Soundness | §5.3 Stratified F1 (the novel contribution) |
| G — LLM-as-Judge | §5.6 G-Eval results table |
| H — Inter-Run Reproducibility | DEFERRED |
| I — Human Validation | DEFERRED to camera-ready |
| J — Distributional Match | §5.4 MAUVE row |
| K — Ranking Correlation | §5.5 Kendall's τ (the validity proof) |

---

## What's truly novel vs. inherited

If a reviewer asks "what's new?" — point at these:

1. **The metadata field design** (`disclosed`, `disclosure_form`,
   `sensitivity_tier`) + the F5/F6 stratified F1 analysis that operationalizes
   them. This is the cleanest novel contribution.
2. **The 9-axis covering-array sampler** applied to PII benchmarks for the
   first time. Borrows NIST SP 800-142 from software testing.
3. **The pattern-density metric C8** as a corpus quality measure.
4. **The paired-sweep subset** for causal axis-effect claims. Counterfactual
   augmentation (Kaushik 2020) applied to PII for the first time.
5. **51-type taxonomy with GDPR Article 9 alignment** for sensitivity tier —
   no prior PII benchmark does this explicitly.

Everything else (Self-BLEU, ROUGE-L, Vendi, MAUVE, G-Eval, Kendall's τ) is
inherited from the broader benchmarking literature applied properly to PII.
