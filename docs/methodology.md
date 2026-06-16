# A Multilingual, Multi-Axis Synthetic PII Detection Benchmark
## Generation Methodology, Annotation Protocol, and Evaluation Framework

**Authors:** Anonymous Authors
**Affiliation:** Anonymous Institution
**Version:** 3.2 — Final Methodology (with Paired-Sweep Subset and Synthetic–Real Validation)
**Date:** May 2026

---

## Abstract

Existing PII detection benchmarks suffer from three systematic deficiencies: (i) narrow entity taxonomies — typically 5–18 types — that omit credentials, sensitive attributes, and enterprise-specific identifiers; (ii) English-dominant coverage with limited cross-script generalization; and (iii) random axis sampling that leaves rare combinations under-represented and cannot support causal claims about axis effects. We present a synthetic benchmark pipeline that addresses all three deficiencies through (a) a 51-entity taxonomy spanning 10 categories with ~820 surface-form patterns across 25 languages, (b) a nine-axis stratified generation protocol with a deterministically computed covering array supplemented by a paired-sweep subset for controlled comparisons, and (c) a single-call generation prompt that produces text and entity strings under fifteen formally-stated hard rules, with character offsets computed downstream by deterministic string alignment. Each entity span carries three novel metadata fields — `disclosed`, `disclosure_form`, and `sensitivity_tier` — that enable evaluation slicing for negation, hypothetical, partial, obfuscated, and GDPR Article 9 special-category cases without re-annotation. We further validate the benchmark as a proxy for real-world model performance through a synthetic–real ranking correlation study against publicly available real PII corpora (TAB, i2b2/n2c2). We define a 52-metric quality framework spanning coverage, annotation integrity, diversity, linguistic quality, format compliance, behavioral soundness (including per-disclosure-form and per-sensitivity-tier stratified F1), LLM-as-judge agreement, inter-run reproducibility, distributional match against real corpora, and synthetic–real ranking correlation. We target a final corpus of ≈6,400 records (5,510 main corpus + 890 paired-sweep subset) meeting per-entity minimum floors of N≥50 instances, zero-entity rate ≤0.5%, 100% offset accuracy by construction, Shannon entropy ≥4.0 bits over the entity-type distribution, MAUVE score ≥0.85 against domain-matched real text, and Kendall's τ ≥ 0.70 between model rankings on synthetic and real subsets. This work delivers Track 1 (PII entity detection); the per-entity metadata schema (`disclosed`, `disclosure_form`, `sensitivity_tier`) is designed to scaffold subsequent releases targeting query-aware masking, re-identification risk scoring, and model leakage, which are out of scope here.

**Keywords:** PII detection, synthetic data generation, multilingual NER, evaluation benchmark, GDPR, code-switching, LLM-as-annotator, paired-sweep design, synthetic–real validity.

---

## 1. Introduction

### 1.1 Motivation

Privacy-preserving NLP requires evaluation data with three properties that real documents cannot simultaneously provide: (a) character-level ground-truth entity spans, (b) coverage of statutorily sensitive categories (GDPR Article 9 — religion, trade-union membership, health, sexual orientation, political opinion), and (c) reproducibility for cross-institution benchmarking. Real corpora are inaccessible under regulatory constraint or insufficiently annotated when accessible.

Published PII benchmarks address subsets of these requirements but none addresses all three. CoNLL-2003 covers four entity types in English. The i2b2/n2c2 challenges cover clinical PHI in English with high-quality annotation but narrow domain. AI4Privacy provides multilingual coverage but with a small entity taxonomy. PIIBench (2025) empirically demonstrated that credentials, religion, sexual orientation, and criminal-record entities receive F1=0 from every evaluated NER system, precisely because they are absent from training and evaluation corpora.

A further methodological gap is shared by all of the above: none publishes a *controlled-comparison subset* in which the same content is rendered into different formats or domains, and none reports a *ranking-correlation validation* against real text. The first absence prevents causal claims about axis effects; the second leaves the benchmark's validity as a proxy for real-world performance unsubstantiated.

This work describes a pipeline that generates a synthetic PII benchmark addressing all five deficiencies simultaneously, with the design principle that **every annotation is guaranteed correct by construction**: entity spans are validated at the character level before any record enters the corpus, eliminating the annotation noise inherent in human labeling of real text.

### 1.2 Contributions

1. **A 51-entity taxonomy** organized in 10 categories, cross-referenced against an enterprise PII field registry (55 fields) for real-world coverage validation.
2. **A nine-axis diversity sampler** including a novel *Entity Adjacency* axis (none / loose / tight with 15 explicit co-occurrence patterns) that no prior PII benchmark systematically evaluates.
3. **A single-call generation prompt** with fifteen hard rules, ten few-shot anchors, and a strict output schema; the prompt explicitly excludes LLM-produced character offsets, which are computed deterministically downstream.
4. **Three novel per-entity metadata fields** — `disclosed` (real vs mentioned-only), `disclosure_form` (complete / partial / obfuscated), and `sensitivity_tier` (HIGH / MEDIUM / LOW with explicit GDPR Article 9 mapping) — that unlock Track 1 stratified evaluation across behavioral frames, disclosure forms, and Article 9 sensitivity tiers (Family F metrics F1, F5, F6), surfacing failure modes that aggregate F1 hides. The same metadata also scaffolds downstream tracks (masking, risk scoring, leakage), which are out of scope for this release.
5. **A dual-mode sampler** that combines a strength-2 covering array (coverage mode) with a factorial paired-sweep subset (controlled-comparison mode), enabling both broad axis coverage and causal claims about axis-specific effects.
6. **A synthetic–real ranking correlation study** validating the benchmark as a proxy for real-world model performance via Kendall's τ and Spearman's ρ against publicly available real PII corpora.
7. **A 50-metric quality framework** covering coverage, annotation integrity, diversity, linguistic quality, format compliance, behavioral soundness, LLM-as-judge agreement, inter-run reproducibility, distributional match against real corpora, and synthetic–real ranking correlation.
8. **A release-gate protocol** with formal thresholds across all metric families, enforced automatically before corpus publication.

### 1.3 Pipeline Overview

```
Pattern Catalog (820 patterns)  ──┐
Diversity Axes (9 axes)        ──┼──► Dual-Mode Sampler ──┬──► Coverage Subset
Behavioral Frames (7 frames)   ──┘                        │      (~5,510 records via covering array)
                                                          └──► Paired-Sweep Subset
                                                                 (~890 records via factorial sweep)
                                          │
                                          ▼
                                  Generator (single LLM call, v3.1 prompt)
                                          │
                                          ▼
                              Deterministic Offset Aligner
                                          │
                                          ▼
                              Conditional Verifier (only on self-check failures)
                                          │
                                          ▼
                                    Repair Stage (zero-entity recovery)
                                          │
                                          ▼
                                    Deduplicator (ROUGE-L + embedding)
                                          │
                                          ▼
                                    Auditor (50-metric evaluation)
                                          │
                                          ▼
                          ┌────────────────┴────────────────┐
                          ▼                                 ▼
              Released Corpus                Synthetic–Real Validation Study
              (release-gated)                (Kendall's τ vs TAB / i2b2)
```

---

## 2. Related Work

### 2.1 PII Benchmarks

| Benchmark | Entity Types | Languages | Offset Annotation | Code-Switching | Adjacency | Paired Sweep | Real-Validation |
|---|---|---|---|---|---|---|---|
| CoNLL-2003 | 4 | EN, DE, NL, ES | token-level | none | not modeled | no | n/a (real data) |
| OntoNotes 5.0 | 18 | EN, ZH, AR | token-level | none | not modeled | no | n/a (real data) |
| i2b2 2014 PHI | 25 | EN | token-level | none | not modeled | no | n/a (real data) |
| MultiCoNER I/II | 6 | 11–13 | token-level | none | character noise | no | partial |
| TAB | ~10 | EN | character | none | not modeled | no | n/a (real data) |
| AI4Privacy | 17 | 4 | character | none | not modeled | no | no |
| PIIBench (2025) | 13 | EN | character | none | not modeled | no | no |
| **This work** | **51** | **25** | **character** | **3 levels** | **3 levels × 15 CO patterns** | **yes (~890 records)** | **yes (Kendall's τ vs TAB+i2b2)** |

### 2.2 Synthetic Data Generation Methodologies

The Self-Instruct methodology (Wang et al., 2023) introduced LLM-based instruction generation with a ROUGE-L>0.7 deduplication filter, demonstrating that ~15–20% of unfiltered LLM outputs are near-duplicates. Evol-Instruct (Xu et al., 2023) systematized prompt-driven complexity expansion. DataDreamer (Patel et al., 2024) formalized reproducibility requirements for synthetic-data papers. Magpie (Xu et al., 2024) demonstrated that the generation prompt is itself the central research artifact. Our pipeline incorporates ROUGE-L and embedding-cosine deduplication, prompt versioning, and treats the generation prompt as a primary research contribution.

### 2.3 Diversity Sampling, Controlled Comparisons, and Benchmark Validity

Covering arrays for combinatorial test generation (NIST SP 800-142) guarantee that every pairwise combination of axis values appears at least once with a small mandatory record count. CheckList (Ribeiro et al., 2020) demonstrated that behavioral test matrices reveal systematic failures invisible to held-out evaluation. Our nine-axis design adopts both insights.

A complementary literature on *controlled comparison* in NLP evaluation (counterfactual augmentation; Kaushik et al., ICLR 2020; Gardner et al., EMNLP 2020) demonstrates that holding content fixed while varying one surface dimension at a time yields stronger causal claims than observational sampling alone. We adopt this via the paired-sweep subset (§4.6).

For benchmark validity, prior synthetic-data work in adjacent NLP areas (DynaBench; Kiela et al., 2021) has emphasized that ranking correlation between synthetic and real evaluation sets — not just distributional match — is the operationally meaningful measure of benchmark validity. We adopt Kendall's τ and Spearman's ρ as primary validity measures.

### 2.4 Evaluation Metrics

The diversity-metric literature converges on a layered framework: deterministic surface metrics (type-token ratio, Distinct-n), distributional metrics (perplexity, Self-BLEU), and semantic metrics (Vendi Score; Friedman & Dieng, 2023). For distribution match against real text, MAUVE (Pillutla et al., NeurIPS 2021) is the standard. LLM-as-judge approaches (G-Eval, Liu et al., 2023; Prometheus-2, Kim et al., 2024) provide rubric-based quality scoring. Our 50-metric framework incorporates all these families plus the synthetic–real ranking correlation introduced in §6.11.

---

## 3. Entity Taxonomy and Pattern Catalog

### 3.1 Taxonomy Design

The taxonomy derives from two sources: (i) a functional analysis of NLP privacy tasks (entity detection, masking, re-identification risk, model leakage) motivating fine-grained surface-form distinctions, and (ii) cross-reference against an enterprise PII field registry (BlackRock internal PI registry, 55 fields) grounding the taxonomy in real-world data governance.

**51 text-extractable entity types in 10 categories:**

| Category | Count | Examples |
|---|---|---|
| Name Family | 4 | Full_Name, First_Given_Name, Last_Family_Name, Preferred_Name |
| Contact Information | 6 | Work/Personal Email, Work/Personal Phone, Work/Personal Address |
| Demographic & Identity | 10 | Date_of_Birth, Age, Gender, Marital_Status, Nationality, Religion, Sex_Orientation, Political_Party, Place_of_Birth, Citizenship_Status |
| Geographic | 5 | Country_of_Residence, State, City, Location, Geolocation_Data |
| Government IDs | 4 | National_Identification_Number, Passport_Number, Driving_License_Number, Tax_Reference_Number |
| Financial | 4 | Compensation_And_Salary, Credit_Card_Numbers, Customer_Reference_Number, Account_Statements |
| Employment & Organization | 8 | Business_Title, Org_Name, Employee_ID_Number, Badge, Performance, Disciplinary, Sickness, Professional_Background |
| Sensitive Compliance | 3 | Crime, PEP_Status, Trade_Union_Membership |
| Health | 2 | Allergy_Information, Medical_Information |
| Digital & Other | 5 | Social_Media_Identifiers, Static_IP_Address, Password, Date_Time, Emergency_Contact_Details |

12 non-text entity types (audio recordings, CCTV, fingerprints, biometric data, signatures, system access logs, call-log data, etc.) are out of scope as they are not extractable from text.

### 3.2 Pattern Catalog

The catalog contains **4,127 surface-form patterns** distributed across the 51 types (Vats et al., 2026; *PII Pattern Catalog v4*), constructed through an 11-batch authored process combining entity-natural enumeration with a 20-dimensional cross-cutting consistency sweep. The catalog supersedes the v3 spec (~820 patterns); see Appendix G for the v3 CO-### co-occurrence pattern → v4 pattern mapping that preserves the adjacency-cluster contribution under the v4 reframing. Each pattern entry contains: `id`, `pattern_id` (category-scoped code e.g. FUN-001 for Full_Name, NID-001 for National_Identification_Number), `entity_type`, `pattern_desc`, `examples`. Mean depth is 80.9 patterns per entity (median 75, min 40 for Preferred_Name, max 152 for Marital_Status). Patterns include:

- 22 Full_Name name-order/script variants per entity (Western, CJK, Russian patronymic, Arabic ibn/bint, Hungarian order, Spanish/Portuguese double surnames, Hebrew, Thai, Devanagari, Cyrillic, Greek, Hangul) plus 79 surface variations (OCR distortion, masking, anonymization, script mixing, document-embedding)
- 105 work-address formats and 82 residential variants across 40+ countries
- 105 telephone formats covering E.164, national conventions, mobile prefixes, and structured representations
- 100 national-ID formats with country-specific checksum rules
- 103 date-of-birth formats including ISO 8601, locale-specific written forms, Buddhist era (Thai), Hebrew civil/religious dual calendar, Japanese Reiwa/Heisei/Showa eras, Hijri Arabic, Persian Jalali, Korean Dangi, and Chinese Lunar calendars

Pattern construction follows the v4 protocol's two-step structure: (Step 2a) unbounded entity-natural enumeration of format, locale, script, and embedding-context variants; (Step 2b) verification against a fixed 20-dimension cross-cutting sweep (OCR-distorted, masked/redacted, anonymized placeholder, multilingual context label, native script, country/locale variant, format variant, structured-data embedding, adjacency-tight, sentence-boundary tricky, domain-embedded, coding-system, verbal/spoken, lifecycle stage, partial/range/approximate, compound/multi-value, URL/scheme-embedded, status/state metadata, cross-purpose overlap, adversarial/homoglyph). Step 2b ensures cross-cutting minimum coverage that the entity-natural pass alone cannot guarantee.

### 3.3 Language Coverage

Languages are organized into three priority tiers:

| Tier | Count | Languages | Rationale |
|---|---|---|---|
| P1 | 6 | English, French, German, Italian, Spanish, Brazilian Portuguese | Highest enterprise demand; full P1 coverage required for any release |
| P2 | 3 | Canadian French, Japanese, Dutch | Required for enterprise multilingual claim |
| P3 | 16 | Swedish, Finnish, Czech, Hebrew, Hungarian, Korean, Norwegian, Portuguese (EU), Russian, Simplified Chinese, Traditional Chinese, Thai, Turkish, Arabic, Danish, (Hindi added v3.1) | Script-diversity coverage: Latin, CJK, Arabic, Devanagari, Cyrillic, Hebrew, Thai |

### 3.4 GDPR Article 9 Mapping

Eleven entity types are GDPR Article 9 special-category data: `Religion`, `Sex_Orientation`, `Political_Party`, `Trade_Union_Membership`, `Medical_Information`, `Allergy_Information`, `Crime` (where convictions are disclosed), plus four direct-identifier types treated as Article 9-equivalent for risk scoring: `National_Identification_Number`, `Passport_Number`, `Credit_Card_Numbers`, `Account_Statements`. All eleven receive `sensitivity_tier: HIGH` in the output schema, enabling stratified per-tier Track 1 reporting (Family F metric F6) and scaffolding downstream sensitivity-aware tasks beyond this release.

---

## 4. Generation Methodology

### 4.1 The Nine Diversity Axes

Each generated record is fully specified by a nine-axis configuration:

| # | Axis | Domain | Values |
|---|---|---|---|
| 1 | Text Domain | Application context | healthcare, legal, finance, education, government, technology, HR, insurance, customer_service, law_enforcement, social_media, e-commerce (12) |
| 2 | Text Format | Surface structure | plain_text, email, chat_transcript, ticket_worknotes, json_record, key_value_pairs, log_entry (7) |
| 3 | Difficulty | Extraction hardness | easy, medium, hard (3) |
| 4 | Context Length | Token budget (cl100k_base) | small (50–200), medium (200–600), large (600–2,000), very_large (2,000–4,000) (4) |
| 5 | Entity Density | PII intensity (entities per 1,000 tokens) | low (1–4/1K), medium (5–15/1K), high (≥16/1K) (3) |
| 6 | Code-Switching | Language mixing | none, light, heavy (3) |
| 7 | Language | Matrix language | 25 values across P1/P2/P3 |
| 8 | Entity Adjacency | Spatial clustering | none, loose, tight (3) |
| 9 | Co-occurrence Pattern | Tight-cluster shape | CO-001..CO-015, or `none` if adjacency≠tight |

Axis 9 (Entity Adjacency with CO-### patterns) is novel: no prior PII benchmark systematically evaluates entity boundary detection under co-occurrence clustering. The 15 CO-### patterns include: angle-bracket email metadata (CO-008), patient header (CO-009), authentication cluster (CO-010), compliance cluster (CO-011), HR record (CO-012), contact card (CO-013), legal citation (CO-014), form key-value adjacency (CO-015), and others detailed in the Pattern Catalog.

### 4.2 The Generation Prompt (v3.1)

The prompt consists of three blocks: a system prompt with fifteen hard rules and the output schema, a user prompt template with axis-value slots, a behavioral-frame slot, and a `scenario_seed` slot used both for scenario specification and (in paired-sweep mode) for entity-value pinning; and ten few-shot exemplars covering the hardest cases.

**Fifteen hard rules (summary):**

- **R1** No LLM-produced offsets; alignment is downstream.
- **R2** Entity strings must be verbatim substrings of the passage.
- **R3** PII must be entirely fictional.
- **R4** All occurrences emit list entries with distinct `mention_index`.
- **R5** All nine axes satisfied simultaneously; conflicts resolved by matrix-language precedence.
- **R6** Adjacency thresholds: none (≥10 words), loose (3–10), tight (CO-### pattern).
- **R7** Per-entity metadata: `disclosed`, `disclosure_form`, `mention_index`.
- **R8** OCR distortion uses explicit substitution rules (l↔1↔I, O↔0, S↔5, B↔8, rn↔m, cl↔d, diacritic dropping, spacing failures, ligature failures); not random noise.
- **R9** Code-switching is grammatical mixing, not translation.
- **R10** Nine-point pre-emit self-check.
- **R11** Triple-name rule: every Full_Name produces nested First/Last spans with eight decomposition cases.
- **R12** Format-validity contract: machine-parseable per format axis; PII formats must satisfy real-world checksums (Luhn, IBAN mod-97, country-specific NID).
- **R13** Canonical 51 entity types only; no invented variants.
- **R14** `sensitivity_tier` with explicit Article 9 mapping (enables Family F metric F6, per-sensitivity-tier stratified F1).
- **R15** Script-aware adjacency: ×3 character threshold for non-space-delimited scripts (CJK, Thai).

**Few-shot exemplars** (10 total): tight CO-008 email metadata, tight CO-009 patient header, hypothetical SSN (disclosed=false), partial PII (disclosure_form=partial), hard OCR across 8 entity types, heavy Hindi-English code-switching, cross-sentence coreference, Japanese JSON HR record (tight CO-012), Arabic RTL high-density key_value_pairs with IBAN and Article 9 Religion, and negation-frame ticket_worknotes with Religion+Crime under negation.

### 4.3 Behavioral Frames

The pipeline supports seven behavioral frames per the CheckList methodology (Ribeiro et al., 2020):

| Frame | Definition | Effect on annotation |
|---|---|---|
| `isolation` | Standard disclosure | `disclosed=true` |
| `co_occurrence` | Multiple PII clustered | follows CO-### pattern |
| `negation` | "He was NEVER convicted of fraud" | inner spans get `disclosed=false` |
| `hypothetical` | "If your SSN were 123-45-6789" | inner spans get `disclosed=false` |
| `instructional` | "For example, an email like j@x.com" | inner spans get `disclosed=false` |
| `partial` | "ending in 4291", "j***@acme.com" | `disclosure_form=partial` |
| `cross_sentence` | Pronouns refer to PII | pronouns NOT tagged; original span tagged once |

### 4.4 Pipeline Stages

#### Stage 1 — Dual-Mode Sampler

The sampler operates in two modes that produce disjoint record subsets, both of which feed the same downstream stages.

**Mode 1 — Coverage (covering-array sampling).** Replaces random axis sampling with a strength-2 covering array (NIST SP 800-142). The array guarantees that every pairwise (axis_i × axis_j) value combination appears at least once. A strength-2 covering array over our 9-axis × ~3,200-value space generates approximately 1,200 mandatory records. Random sampling supplements the covering array to reach (a) the target corpus size and (b) per-entity minimum floors of N≥50 instances. Total Mode 1 output: ~5,510 records.

**Algorithm 1 — Coverage sampling.**

```
INPUT:  axis_values = {axis: [values]}, target_corpus_size N, min_floor M
OUTPUT: generation_plan = list of axis-configurations

1.  mandatory = covering_array(axis_values, strength=2)  // ≈1,200 configs
2.  floor_supplement = []
3.  for each entity_type t with current_count(t) < M:
4.      add (M - current_count(t)) random configs targeting t
5.      append to floor_supplement
6.  diversity_supplement = random configs to fill (N - |mandatory| - |floor_supplement|)
7.  return shuffle(mandatory ∪ floor_supplement ∪ diversity_supplement)
```

**Mode 2 — Paired-Sweep (factorial sampling).** Generates matched record sets where the same scenario, entity values, and persona are rendered under varying values of a single chosen axis. See §4.6 for the design rationale and full specification. Total Mode 2 output: ~890 records.

#### Stage 2 — Generator

A single LLM call (Claude Opus or GPT-4o, model versions pinned in `corpus_registry.json`) consumes the v3.1 prompt with axis values interpolated and emits a JSON object containing `text`, `entities`, and `self_check`. Temperature is 0.0 for extraction-style fields and 0.9 for the text body, achieved via a two-stage internal completion. Output `maxTokens` is dynamically set based on density and length: `min(8192, est_entities × 150 + length_chars × 0.3)`.

In Mode 2 (paired sweep), the `scenario_seed` slot in the user prompt is populated with an explicit *scenario card* listing the frozen anchor: pattern_id, entity values to be used verbatim, persona, narrative scenario. The temperature for the text body is reduced to 0.5 in Mode 2 to suppress lexical drift across format variants while preserving format-specific surface adaptation.

#### Stage 3 — Deterministic Offset Aligner

For each entity in the emitted list:

```
For entity e with entity_string s, mention_index k:
    occurrences = [i for i in range(len(text)) if text[i:i+len(s)] == s]
    if k < len(occurrences):
        e.start = occurrences[k]
        e.end   = occurrences[k] + len(s)
    else:
        DROP entity, log self-consistency failure
```

This stage achieves 100% offset accuracy by construction. The aligner is deterministic Python code and contains no LLM call.

#### Stage 4 — Conditional Verifier

Records whose `self_check` block reports all true skip verification (≈85% of records, per pilot data). Records that fail any self-check predicate are sent to a verification LLM call (GPT-4o-mini) with the diagnostic flag set; the verifier returns a corrected entity list. The conditional gate reduces API cost by ≈30% vs unconditional verification while retaining the safety net for the ≈15% of records that need it. The verifier itself is audited via a targeted ablation study (§9, Threat 8).

#### Stage 5 — Repair

Records with zero entities after Stage 3 (target ≤0.5%) are sent to a repair pass using assistant prefilling (`{"entities": [`) with normalized key-name handling. Repair-only records receive `confidence=low` provenance. The repair script first attempts re-extraction with the primary model; on failure, it retries with GPT-4o-mini as a script-language fallback (relevant for Japanese, Arabic, Thai).

#### Stage 6 — Deduplicator

Pairwise comparison within each (domain, target_entity_type) stratum for Mode 1 records:

- **ROUGE-L filter:** discard the second record if max ROUGE-L > 0.70 against any prior record in the stratum.
- **Embedding filter:** embed with `sentence-transformers/all-mpnet-base-v2`; discard if cosine similarity > 0.85.

For multilingual records, embeddings use `paraphrase-multilingual-mpnet-base-v2`. Mode 2 (paired-sweep) records are **exempt** from deduplication: by construction they share content across format/domain variants and any "duplicate" flag would defeat the purpose of the controlled comparison.

#### Stage 7 — Auditor

The auditor computes all 50 metrics (Section 6), writes a per-record provenance log, and emits a release-gate decision per Section 7.4.

### 4.5 Reproducibility Guarantees

Per Issues doc §F.16, every released corpus is accompanied by `corpus_registry.json` recording: run name, git commit hash of `graph_config.yaml` and prompt v3.1, model versions and API endpoints, random seeds, output file path, audit report path, generation date. The git commit is tagged at the moment of corpus validation.

### 4.6 Paired-Sweep Subset (Contribution 5)

The covering array generates broad axis coverage but, by design, contains no two records with identical content. This precludes causal claims about axis effects: a benchmark consumer who observes that Model X scores worse on `format=json_record` than on `format=plain_text` cannot distinguish (a) a true effect of format from (b) confounding variation in domain, language, or content. The paired-sweep subset closes this gap by generating *matched record sets* in which all axes except one are held constant.

#### 4.6.1 Design

The paired-sweep subset contains three sub-sweeps:

| Sub-sweep | Anchors | Sweep axis | Variants per anchor | Records |
|---|---|---|---|---|
| Format sweep | 50 | text_format | 7 (plain_text, email, chat, ticket, json, kv, log) | 350 |
| Domain sweep | 30 | text_domain | 12 (healthcare, legal, finance, …) | 360 |
| Difficulty × Density sweep | 20 | (difficulty × density) | 9 (3 × 3) | 180 |
| **Total** | **100 anchors** | | | **890** |

Each *anchor* is a fully-specified scenario card containing: target pattern_id, frozen entity values (e.g., name "Mlchael Johsnon", DOB "03/15/1985", address "742 Evergreen Terrace"), persona description, and a one-sentence narrative scenario. The remaining eight axes are also frozen at the anchor configuration; only the sweep axis varies across variants.

#### 4.6.2 Anchor Selection

Anchors are stratified to span the high-value (axis_i × axis_j) regions of the corpus:

- 30 anchors target high-density × very_large × hard combinations (the stress-test region — Gaps doc §E.4)
- 30 anchors target Article 9 special-category content (Religion, Crime, Medical_Information, PEP_Status) to support sensitivity-aware evaluation
- 25 anchors target non-Latin scripts (CJK, Arabic, Devanagari, Hebrew, Thai)
- 15 anchors target adjacency=tight with each of the 15 CO-### patterns at least once

#### 4.6.3 Generation Algorithm

**Algorithm 2 — Paired-sweep generation.**

```
INPUT:  anchor_set A, sweep_axis_spec S (axis_name, values)
OUTPUT: paired_records (matched record sets)

1.  for each anchor a in A:
2.      scenario_card = build_scenario_card(a)
3.          # contains pattern_id, frozen entity values, persona, narrative
4.      for each value v in S.values:
5.          config = a.config
6.          config[S.axis_name] = v
7.          record = generate(prompt_with_scenario_card(scenario_card, config),
8.                            temperature_body=0.5)
9.          record.anchor_id = a.id
10.         record.sweep_axis = S.axis_name
11.         record.sweep_value = v
12.         emit record
```

#### 4.6.4 Prompt Implementation

The existing v3.1 user prompt's `scenario_seed` slot is repurposed to carry the scenario card. No new prompt rule is required; R3 (fictional only) is still satisfied — frozen entities are still fictional, merely consistent across the sweep. The generator's instructions are augmented at the user-prompt level with a single sentence: "Use the entity values provided in the scenario card *verbatim*; do not invent alternative names, dates, or identifiers." This is a soft constraint at the user level; R2 (verbatim substrings) is the corresponding hard constraint at the system level.

#### 4.6.5 Downstream Evaluation Use

The paired-sweep subset supports a class of causal claims that the main corpus cannot:

1. **Format effect:** *Holding content constant, Model X's F1 drops from 0.82 (plain_text) to 0.64 (json_record) — an 18-point format effect.* This is the strongest single sentence we can publish from this benchmark.
2. **Domain effect:** *Holding content constant, Model X's recall on Religion entities drops from 0.91 (healthcare) to 0.73 (finance), suggesting domain-specific masking.*
3. **Difficulty × Density interaction:** *The marginal F1 cost of switching from medium to high density is +2 F1 points at easy difficulty but +14 F1 points at hard difficulty.*

These claims, expressed as fixed-effects regressions over the paired-sweep subset with anchor identity as a random effect, are the principal value-add of Mode 2.

#### 4.6.6 Storage and Provenance

Paired-sweep records are stored in a separate `paired_sweep/` subdirectory and carry the additional metadata fields `anchor_id`, `sweep_axis`, and `sweep_value`. They are aggregated with the main corpus for metric families A–J but disaggregated for Family K and for any causal-effect analysis.

---

## 5. Pipeline Architecture

### 5.1 Implementation Substrate

The pipeline is implemented as a directed acyclic graph on the open-source SyGra framework (Anonymous Institution, 2025), which provides graph execution, YAML-based DAG configuration, model abstraction, and batching/checkpointing. All domain logic — entity taxonomy, pattern catalog, generation prompt, post-processors, validation, alignment, paired-sweep sampler, correlation-study harness, and quality tooling — is original work.

### 5.2 Node Specification

| Node | Type | Inputs | Outputs | Substrate |
|---|---|---|---|---|
| `sample_axes` (Mode 1) | Python | axis catalog, target N | coverage axis-configs | NIST ACTS bindings + numpy |
| `paired_sweep` (Mode 2) | Python | anchor set, sweep axis | paired axis-configs | numpy + scenario-card library |
| `generate_record` | LLM | axis config (+ scenario card in Mode 2), prompt v3.1 | JSON object (text + entities + self_check) | Claude Opus 4.x / GPT-4o |
| `align_offsets` | Python | record JSON | record + offsets | deterministic |
| `verify` (conditional) | LLM | record + flag | corrected record | GPT-4o-mini |
| `repair` (conditional) | LLM | zero-entity record | repaired entities | Claude (assistant prefill) → GPT-4o-mini fallback |
| `deduplicate` | Python | record batch (Mode 1 only) | filtered batch | rouge-score + sentence-transformers |
| `audit` | Python | full corpus | metric report + gate decision | numpy + scipy + custom |
| `correlation_study` | Python + LLM | synthetic subset + real subset, 5+ models | Kendall's τ, Spearman ρ, F1 deltas | external model APIs + scipy.stats |

### 5.3 Cost and Throughput

Empirical pilot data (April 2026, 200 records) extrapolated to the full v3.2 corpus:

| Metric | Value |
|---|---|
| Average tokens per call (system + few-shots + user) | 11,200 input |
| Average tokens per output | 2,800 |
| With prompt caching (5-min TTL) | 91% input cache hit rate |
| Effective cost per record (Claude Opus) | $0.018 |
| Effective cost per record (GPT-4o) | $0.012 |
| Wall-clock per record (sequential) | 8–14 s |
| Wall-clock with batch_size=10 | 1.2–2.0 s/record amortized |
| Mode 1 cost (5,510 records) | $66–$99 |
| Mode 2 cost (890 records) | $11–$16 |
| Correlation-study inference cost (5 models × 600 records) | $30–$60 |
| **Projected total cost** | **$107–$175** |
| Projected wall-clock (generation only) | ≈3 hours |
| Projected wall-clock (incl. correlation study) | ≈4 hours + DUA processing |

---

## 6. Evaluation Framework

The 50-metric framework is organized into eleven metric families. Every metric has a formal definition, a target threshold, and a release-gate boolean.

### 6.1 Family A — Coverage Metrics

| ID | Metric | Formula / Definition | Target |
|---|---|---|---|
| A1 | Pattern coverage rate | count(patterns observed ≥3 times) / 4127 | ≥95% |
| A2 | Per-entity-type floor | min over types of count(type) | ≥50 |
| A3 | Language tier coverage | records per (P1/P2/P3) language | P1≥250, P2≥150, P3≥100 |
| A4 | Pairwise axis coverage | count((axis_i, axis_j) tuples observed) / total | ≥98% (strength-2 array) |
| A5 | Behavioral matrix coverage | non-zero cells in (51 × 7) matrix | ≥85% of 204 expected |
| A6 | Adjacency × CO-### coverage | records per (adjacency, CO-###) | ≥1 record per CO-### |
| A7 | Domain × language coverage | non-zero cells in (12 × 25) | ≥80% |

### 6.2 Family B — Annotation Integrity Metrics

| ID | Metric | Definition | Target |
|---|---|---|---|
| B1 | Offset accuracy | fraction of entities with text[start:end] == entity_string | 100.0% |
| B2 | Zero-entity rate | records with 0 entities / total records | ≤0.5% |
| B3 | Validation-dropped rate | mean over records of dropped/extracted ratio | ≤2% |
| B4 | Triple-name rule compliance | Full_Name spans with matching First+Last entries | 100% |
| B5 | Canonical-type compliance | entities with `entity_type` in 51-type set | 100% |
| B6 | Multi-mention completeness | records where all string occurrences are tagged | ≥95% |
| B7 | Nesting consistency | nested entries where `nesting_parent` is a top-level span | 100% |

### 6.3 Family C — Diversity Metrics

| ID | Metric | Formula | Target |
|---|---|---|---|
| C1 | Entity-type entropy | H = -Σ p_t log₂ p_t over 51 types | ≥4.0 bits |
| C2 | Distinct-1 | unique unigrams / total unigrams | ≥0.06 |
| C3 | Distinct-2 | unique bigrams / total bigrams | ≥0.55 |
| C4 | Self-BLEU-3 | mean BLEU-3 of each record vs the rest | ≤0.35 |
| C5 | ROUGE-L intra-stratum max | max pairwise ROUGE-L within (domain, type) | ≤0.70 |
| C6 | Embedding-cosine dedup rate | discarded / proposed records | ≤15% |
| C7 | Vendi Score | exp(−Σ λ_i log λ_i) over sentence-BERT eigenvalues | ≥10.0 (large-corpus regime) |
| C8 | Compression ratio | gzip-compressed-size / raw-size | ≤0.42 |

Note: C2–C8 are computed on the Mode 1 (coverage) subset only. The paired-sweep subset is, by construction, internally less diverse and is excluded from these metrics to prevent biasing them downward.

### 6.4 Family D — Linguistic Quality Metrics

| ID | Metric | Reference | Target |
|---|---|---|---|
| D1 | Perplexity (per-language) | mGPT reference LM | within 1.5σ of real-corpus baseline per language |
| D2 | Type-token ratio (TTR) | unique tokens / total tokens | ≥0.40 per record |
| D3 | Yule's K | vocabulary richness | within published norms per domain |
| D4 | Language-ID confidence | fastText langid | ≥0.90 for non-code-switched; CS records validated separately |
| D5 | BERTScore-F1 vs real exemplars | multilingual BERTScore | ≥0.80 per domain |
| D6 | MAUVE (per domain) | Pillutla et al., 2021 | ≥0.85 per domain |

### 6.5 Family E — Format & Checksum Compliance (R12 validation)

| ID | Metric | Definition | Target |
|---|---|---|---|
| E1 | JSON parse rate | for format=json_record, fraction parsing with json.loads | 100% |
| E2 | RFC 5322 header completeness | for format=email, From/To/Subject/Date present | 100% |
| E3 | Luhn pass rate | Credit_Card_Numbers passing Luhn | ≥95% (5% intentionally invalid for difficulty=hard) |
| E4 | IBAN mod-97 pass rate | IBAN-tagged Customer_Reference_Number | ≥98% |
| E5 | NID checksum pass rate | country-specific NID (CPF, RRN, personnummer, ...) | ≥95% per country |
| E6 | Locale date/number compliance | matches Catalog Appendix A per language | ≥95% |
| E7 | Length-tier compliance | record length within declared tier band | ≥90% |

### 6.6 Family F — Behavioral Soundness Metrics

| ID | Metric | Definition | Target |
|---|---|---|---|
| F1 | Disclosure-classification accuracy | LLM-judge agreement on disclosed=true/false | ≥0.90 (Cohen's κ) |
| F2 | Coreference soundness | records with pronouns incorrectly tagged | ≤2% |
| F3 | OCR realism score | KL divergence between our OCR error distribution and a real OCR baseline (Tesseract on a noisy scan corpus) | ≤0.5 |
| F4 | Code-switching naturalness | matrix-language ratio + switch-point grammaticality (LLM judge) | switch density 0.15–0.40 for heavy, 0.03–0.10 for light |
| **F5** | **Per-disclosure-form F1 stratification** | **F1 stratified across `complete` / `partial` / `obfuscated` entity spans on a held-out PII detector. Reports all three per-stratum F1 scores; flags a *safety gap* if obfuscated-F1 is more than 20 points below complete-F1.** | **Report all three; gap ≤ 20 points** |
| **F6** | **Per-sensitivity-tier F1 stratification** | **F1 stratified across `HIGH` / `MEDIUM` / `LOW` sensitivity tiers (per R14 mapping; Article 9 categories are HIGH). Reports all three per-stratum F1 scores; flags an *Article 9 gap* if HIGH-tier F1 is more than 10 points below LOW-tier F1.** | **Report all three; gap ≤ 10 points** |

### 6.7 Family G — LLM-as-Judge Metrics

| ID | Metric | Definition | Target |
|---|---|---|---|
| G1 | G-Eval overall quality | rubric: coherence, relevance, format compliance, factuality | ≥4.0 / 5.0 mean |
| G2 | GPTScore per-dimension | conditional log-likelihood under judge model | ≥−1.5 mean |
| G3 | Prometheus-2 rubric score | structured rubric, per-dimension 1–5 | ≥4.0 mean per dimension |
| G4 | Inter-judge agreement | Krippendorff's α between Claude / GPT-4o / Gemini judges | ≥0.70 |

### 6.8 Family H — Inter-Run Reproducibility (LLM-IAA)

| ID | Metric | Definition | Target |
|---|---|---|---|
| H1 | Two-run extraction F1 | rerun generation with same axes, different seed; compute span F1 | ≥0.85 |
| H2 | Span-level precision/recall | between independent runs | P ≥0.88, R ≥0.85 |
| H3 | Entity-type-level agreement | Cohen's κ on type assignment | ≥0.85 |
| H4 | Offset exact-match rate | character-level offset agreement | ≥0.95 (post-alignment) |

### 6.9 Family I — Human Validation Metrics

Conducted on a stratified 10% sample (≈640 records across the 6,400-record corpus).

| ID | Metric | Definition | Target |
|---|---|---|---|
| I1 | Spot-check error rate | records with at least one annotation error | ≤3% |
| I2 | Reviewer agreement | Cohen's κ between two human reviewers on a 100-record overlap | ≥0.80 |
| I3 | Error-category distribution | missed entity / wrong type / wrong span / hallucinated entity | report all four |

### 6.10 Family J — Distributional Match Against Real Corpora

| ID | Metric | Reference Corpus | Target |
|---|---|---|---|
| J1 | MAUVE — medical | MIMIC-III de-identified subset (publicly available portions) | ≥0.85 |
| J2 | MAUVE — legal | EUR-Lex documents | ≥0.85 |
| J3 | MAUVE — social media | a 2024 Twitter / Reddit sample | ≥0.80 (typo-heavy register) |
| J4 | MAUVE — corporate | Enron emails (publicly released) | ≥0.85 |
| J5 | Vocabulary overlap (Jaccard) | per domain | ≥0.45 |

### 6.11 Family K — Synthetic–Real Ranking Correlation (Contribution 6)

Family K answers the question that distributional metrics (Family J) cannot: *if a benchmark consumer ranks PII detection models on this synthetic corpus, will they obtain the same ranking as on real PII text?* This is the operational definition of benchmark validity per Kiela et al. (2021) and is required evidence for any synthetic-benchmark paper at EMNLP / NeurIPS / ACL Datasets & Benchmarks track.

**Protocol.** Select a synthetic evaluation subset (n=300, stratified across Mode 1 P1+P2 languages) and a real evaluation subset (n=300 from the union of TAB and i2b2/n2c2 PHI corpora, normalized to the canonical 51-type taxonomy via a published label-mapping table). Evaluate the same five models on both subsets: (a) Microsoft Presidio, (b) GLiNER-multi, (c) a Llama-3-based extractor, (d) GPT-4o-mini, (e) Claude-Haiku. Report Track 1 F1 per model per subset. Compute rank-correlation statistics:

| ID | Metric | Definition | Target |
|---|---|---|---|
| K1 | Kendall's τ | rank correlation of model F1 between synthetic and real subsets, across 5 models (10 pairs) | ≥0.70 |
| K2 | Spearman's ρ | rank correlation (alternative measure) | ≥0.70 |
| K3 | Mean absolute F1 delta | mean over models of abs(F1_synth − F1_real) | ≤0.10 |
| K4 | τ confidence interval | 95% bootstrap CI on Kendall's τ does not include 0.5 | yes (lower bound ≥ 0.5) |

**Sample-size rationale.** With n=300 evaluation records per subset and 5 models, the standard error on Kendall's τ is ≈0.13, giving a 95% CI of approximately ±0.25 on a point estimate of 0.75. This is sufficient to distinguish τ ≥ 0.70 from chance (τ near 0) with high confidence but not from a weaker correlation (τ ≈ 0.50). We report the full CI rather than a point estimate alone.

**Real-data sourcing.**

- **TAB** (Pilán et al., 2022) — openly available, ~1,200 court documents with character-level annotation. Used as primary real-data source.
- **i2b2/n2c2 2014 PHI** (Stubbs & Uzuner, 2015) — clinical PHI, ~1,300 notes. Requires Data Use Agreement; access requested in parallel with Phase 1.
- **AI4Privacy validation set** (subset) — used as a secondary check if the primary sources prove insufficient.

**Label normalization.** Real-data PII labels (TAB uses ~10 types, i2b2 uses ~25) are mapped to our canonical 51-type taxonomy via a published `label_map.json` table. Entities in real data that lack a canonical mapping (e.g., i2b2 "PROFESSION" mapping to our `Business_Title`) are noted in the audit report and excluded from the correlation if mapping confidence is low.

**Failure-mode protocol.** If K1 < 0.70 in the v1 release, the synthetic-real gap is investigated by domain and by entity type. Domain-specific recalibration (re-running MAUVE per domain) may identify which subdomains produce the misranking, motivating targeted regeneration in v3.3.

### 6.12 Summary Table — Metric Families and Counts

| Family | Metrics | Purpose |
|---|---|---|
| A. Coverage | 7 | Stratified representation across axes |
| B. Annotation Integrity | 7 | Correctness by construction |
| C. Diversity | 8 | Intra-corpus variation |
| D. Linguistic Quality | 6 | Naturalness and language conformity |
| E. Format & Checksum | 7 | Surface validity |
| F. Behavioral Soundness | 6 | Disclosure / coreference / OCR / CS + **per-disclosure-form** (F5) + **per-sensitivity-tier** (F6) stratified F1 |
| G. LLM-as-Judge | 4 | Rubric-based external scoring |
| H. Reproducibility | 4 | Inter-run agreement |
| I. Human Validation | 3 | Spot-check error rate |
| J. Distribution Match | 5 | Real-text proximity |
| **K. Ranking Correlation** | **4** | **Validity as proxy for real-world performance** |
| **Total** | **52** | |

---

## 7. Release Gate Protocol

A corpus version may be released only when all of the following blocking thresholds are met:

### 7.1 Critical Gates (must all pass)

- B1 offset accuracy = 100.0%
- B2 zero-entity rate ≤ 0.5%
- B4 triple-name rule compliance = 100%
- B5 canonical-type compliance = 100%
- A2 per-entity-type floor ≥ 50 instances (every type)
- A4 pairwise axis coverage ≥ 98%

### 7.2 High-Severity Gates (must pass for full release; minor release allowed with documented waiver)

- A1 pattern coverage ≥ 95%
- A5 behavioral matrix coverage ≥ 85%
- C1 entity-type entropy ≥ 4.0 bits
- C5 ROUGE-L intra-stratum max ≤ 0.70
- E1, E2 format compliance = 100%
- E3 Luhn pass rate ≥ 95%
- H1 two-run F1 ≥ 0.85
- I1 spot-check error rate ≤ 3%
- **K1 Kendall's τ ≥ 0.70 between synthetic and real model rankings**
- **K4 τ 95% CI lower bound ≥ 0.50**

### 7.3 Medium-Severity Gates (report, do not block)

- C7 Vendi Score
- D5, D6 BERTScore, MAUVE per domain
- F1 disclosure-classification κ ≥ 0.90
- G1–G4 LLM-judge scores
- K2 Spearman's ρ
- K3 mean absolute F1 delta

### 7.4 Audit Workflow

```
1. Compute all 50 metrics on the full corpus.
2. Check each Critical Gate. Any failure → BLOCK release; trigger targeted regeneration.
3. Check High-Severity Gates. Failures → BLOCK; permit waiver only with explicit lead-author sign-off.
4. Check Medium-Severity Gates. Report in `audit_report.json`; do not block.
5. Generate `release_certificate.json` and tag the git commit.
```

---

## 8. Implementation Plan

The pipeline will be executed in seven phases over approximately six weeks.

### 8.1 Phase 1 — Smoke Test (Week 1, Days 1–2)

10 records generated under the most demanding configuration: `context_length=very_large`, `entity_density=high`, `difficulty=hard`. Purpose: validate that the prompt and pipeline handle the worst-case combination without truncation, offset misalignment, or self-check failure. Pass criterion: ≥8/10 records pass all Critical Gates individually.

### 8.2 Phase 2 — English Pilot (Week 1, Days 3–7)

500 records in English only, covering all 7 behavioral frames and all 51 entity types. Purpose: validate (a) the behavioral matrix produces semantically correct `disclosed=true/false` annotations, (b) the triple-name rule fires on all surface forms, (c) the deduplication thresholds are calibrated. Pass criterion: full Critical and High-Severity Gate pass (excluding K1, which is computed at Phase 7).

### 8.3 Phase 3 — P1 Language Release (Week 2)

1,500 records covering 6 P1 languages × all 9 axes via the covering array + per-language floor supplements. Pass criterion: full release-gate pass (excluding K1); tag as `corpus-v3.2-p1`.

### 8.4 Phase 3.5 — Paired-Sweep Generation (Week 2, in parallel with Phase 3)

890 paired-sweep records across 100 anchors and three sub-sweeps (format × 7 = 350, domain × 12 = 360, difficulty × density × 9 = 180). Anchors are selected per §4.6.2. Generation uses temperature=0.5 in Mode 2 (versus 0.9 in Mode 1) to suppress lexical drift across variants. Pass criterion: ≥95% of anchors emit all variants successfully; manual spot-check confirms entity-value consistency across variants per anchor.

### 8.5 Phase 4 — P2 Language Release (Week 3)

1,000 additional records covering Canadian French, Japanese, Dutch. Pass criterion: full release-gate pass (excluding K1) on the P1+P2 union; tag as `corpus-v3.2-p1p2`.

### 8.6 Phase 5 — P3 Language Release (Week 4)

3,000 additional records covering the 16 P3 languages with emphasis on script diversity (Latin, CJK, Arabic, Devanagari, Cyrillic, Hebrew, Thai). Pass criterion: full release-gate pass (excluding K1) on the full P1+P2+P3 corpus; tag as `corpus-v3.2-final-pending-validation`.

### 8.7 Phase 6 — Human Validation Sweep (Week 5)

10% stratified sample (≈640 records) reviewed by two annotators per record using `generate_review_sheet.py`. Disagreements adjudicated by the third author. Pass criterion: I1 ≤ 3%, I2 κ ≥ 0.80. In parallel, the verifier ablation study (§9, Threat 8) is conducted: 100 verifier-triggered records (50 EN + 50 non-Latin) compared four ways (Stage 2 raw, Stage 4 verified, Stage 2 + alignment only, human gold standard). Decision rule for Stage 4 is locked in advance.

### 8.8 Phase 7 — Synthetic–Real Correlation Study (Week 5–6)

The Family K validation study (§6.11). Subtasks:

1. **Data preparation (Week 5):** download TAB; submit i2b2/n2c2 DUA; build `label_map.json`; assemble 300-record real-data subset normalized to the 51-type taxonomy.
2. **Model evaluation (Week 6, Days 1–3):** run Presidio, GLiNER-multi, Llama-3-based extractor, GPT-4o-mini, Claude-Haiku on the synthetic subset (300 records from Mode 1 P1+P2 stratum) and the real subset.
3. **Statistical analysis (Week 6, Days 4–5):** compute K1–K4; produce bootstrap CIs; report per-domain and per-entity-type breakdowns; investigate failure modes if K1 < 0.70.
4. **Release decision (Week 6, Day 5):** if K1 ≥ 0.70 and K4 lower bound ≥ 0.50, tag `corpus-v3.2-final`. Otherwise document the gap, scope a v3.3 regeneration, and release as `corpus-v3.2-rc` (release candidate).

### 8.9 Total Targets

- **6,400 records** minimum (5,510 main + 890 paired sweep) across 25 languages
- **≥76,000 annotated entity instances** (mean ≥12 per record)
- **100% character-level offset accuracy** by construction
- **Kendall's τ ≥ 0.70** between synthetic and real-data model rankings
- **Four downstream evaluation tracks** supported by the metadata schema
- **Causal-comparison capability** via the paired-sweep subset

---

## 9. Threats to Validity and Limitations

1. **Synthetic-vs-real distribution gap.** MAUVE (Family J) measures this and the ranking-correlation study (Family K) tests whether it is operationally meaningful. We target MAUVE ≥ 0.85 per domain and Kendall's τ ≥ 0.70 between synthetic and real model rankings, but acknowledge that LLM-generated text retains stylistic regularities absent from human-written documents. Mitigation: report Family J and Family K per-domain in published metrics; recommend benchmark consumers calibrate against domain-matched real text where possible.

2. **LLM annotation bias.** Even with deterministic alignment, the *choice* of what to tag is the LLM's. We mitigate via: (a) two-model verification on flagged records, (b) inter-run reproducibility (H1–H4), (c) 10% human spot-check (Family I), and (d) the verifier ablation study (Threat 8 below).

3. **Low-resource-language gap.** P3 tier languages (Thai, Hungarian, Czech, etc.) may receive lower-quality generation than P1. We report per-language metrics (D1, D4, J*) and apply per-language release gates separately. Family K is computed on the P1+P2 stratum only; P3 ranking-correlation is left as future work pending availability of real P3-language PII corpora.

4. **Pattern catalog completeness.** The 820 patterns are large but not exhaustive. We expect a v4 expansion targeting (a) partial/obfuscated patterns for digital identifiers, (b) Hindi/Tamil/Indonesian for resource-level diversity, (c) more cross-script code-switching pairs.

5. **No coverage of audio, image, video PII.** This benchmark targets text-extractable PII only. Twelve excluded non-text types (audio recordings, CCTV, photos, fingerprints, biometric data, signatures, system access logs, etc.) are out of scope.

6. **Article 9 sensitive content generation.** The benchmark deliberately generates fictional Religion, Sex_Orientation, Political_Party, Trade_Union_Membership, Crime, and Medical_Information spans. All such content is fabricated; the `sensitivity_tier` field enables compliant downstream usage.

7. **Cost of LLM-as-judge metrics.** G1–G4 metrics require additional API calls. We compute these on a stratified 20% sample rather than the full corpus.

8. **Conditional verifier auditability.** Stage 4 silently rewrites entity lists for ~15% of records. We mitigate via a targeted ablation (Phase 6): 100 verifier-triggered records compared four ways (Stage 2 raw, Stage 4 verified, Stage 2 + alignment only, human gold). Decision rule locked in advance: if Stage 4 introduces errors at ≥ the rate it fixes them, Stage 4 is removed entirely.

9. **Correlation-study sample size and model selection.** Family K is computed on n=300 records per subset and 5 models. The resulting bootstrap CI on Kendall's τ is wide (±0.20–0.25 at point estimate 0.75). Reviewers may interpret this as preliminary evidence rather than conclusive validation. We report the CI honestly and frame K1 as a *necessary, not sufficient* condition for benchmark validity. Model selection (Presidio, GLiNER, Llama-3, GPT-4o-mini, Claude-Haiku) is biased toward currently popular systems; a longer-term validity study would include emerging models as they appear.

10. **Paired-sweep generalization.** Causal claims from Mode 2 generalize to the *anchor set* but not necessarily to the full corpus. The 100 anchors span Article 9 content, non-Latin scripts, high-density/very_large/hard combinations, and all 15 CO-### patterns, but readers should not over-generalize a paired-sweep effect (e.g., format effect on Mode 2 anchors) to records very different from the anchor set. We report paired-sweep effect sizes with bootstrap CIs over anchor identity to make this dependency explicit.

11. **Track 2–4 scoping.** This release operationalizes Track 1 (entity detection) only. Although the per-entity metadata schema (`disclosed`, `disclosure_form`, `sensitivity_tier`) is designed to scaffold Tracks 2 (query-aware masking), 3 (re-identification risk scoring), and 4 (model leakage), no evaluation scripts, sample stratification, or release gates are defined for them in this release. The metadata fields earn their place in v3.2 on Track 1 grounds alone — they power the F1/F5/F6 stratified-F1 evaluations of Family F. Reviewers and consumers should treat the metadata schema as both delivering Track 1 stratified evaluation and *additionally* enabling infrastructure for follow-up work, not as evidence of evaluated downstream task support.

---

## 10. Catalog v4 Integration

The v3.2 methodology described in §1–§9 was originally designed against the v3 pattern catalog (51 entities, ~820 patterns). The v4 pattern catalog (Vats et al., 2026 — *PII Pattern Catalog v4 Master*; companion document to this methodology) supersedes v3 with 4,127 patterns generated through an explicit two-step protocol (entity-natural enumeration + 20-dimensional cross-cutting consistency sweep) and a five-experiment validation plan. This section documents how the v3.2 methodology integrates with the v4 catalog.

**Authoritative pattern source.** The v4 catalog is the authoritative source for `pattern_id` references. The covering-array sampler (§4.4 Stage 1, Mode 1) operates over the v4 51-entity × 4,127-pattern space; paired-sweep anchors (§4.6) reference v4 pattern IDs in their frozen entity blocks; release-gate metric A1 (Family A) is computed against the 4,127 denominator.

**Cross-cutting dimension alignment.** v4's 20-dimension consistency sweep operationalizes several constructs that were previously implicit in v3.2: dimension #1 (OCR-distorted) aligns with R8; dimension #2 (masked/redacted) aligns with `disclosure_form: partial|obfuscated` (R7); dimension #4 (multilingual context label) aligns with the language axis; dimension #8 (structured-data embedding) aligns with the `text_format` axis; dimension #9 (adjacency-tight) aligns with `entity_adjacency: tight` and subsumes the v3 CO-### co-occurrence patterns (mapping in Appendix G); dimension #11 (domain-embedded) aligns with the `text_domain` axis. Where v3.2 specifies an axis value or hard-rule constraint, v4 patterns satisfying the corresponding dimension are eligible candidates.

**Backwards compatibility.** The v3.2 prompt and generation pipeline reference v3 pattern prefixes in their R13 canonical-type list and in 11 few-shot exemplars. A v3 → v4 pattern-prefix migration table is provided in Appendix H. Two prefix collisions and three entity name renames require explicit handling before generation begins (see Appendix H Section H.3).

**Catalog validation.** Family L (defined in this revision; see §6.13) integrates the four publication-grade validation experiments from the v4 catalog (external-benchmark coverage, inter-annotator agreement, industry-taxonomy gap analysis, saturation analysis) as additional release-gate evidence complementing the synthetic-real ranking correlation already specified as Family K.

---

## 11. Conclusion

This document specifies the final methodology, pipeline architecture, and evaluation framework for a 51-entity, 25-language synthetic PII benchmark for Track 1 (entity detection). The pipeline addresses the most consequential gaps in existing PII benchmarks: it provides character-level ground truth, multilingual cross-script coverage, stratified evaluation across behavioral frames and Article 9 sensitivity tiers via the `disclosed`, `disclosure_form`, and `sensitivity_tier` metadata fields, controlled-comparison capability via the paired-sweep subset, validity evidence via the synthetic–real ranking correlation study, and rigorous reproducibility via the corpus registry. The 52-metric evaluation framework supports release decisions, paper claims, and inter-corpus comparison. The implementation plan delivers a 6,400-record corpus (5,510 main + 890 paired-sweep) across seven phases with explicit per-phase pass criteria and a final ranking-correlation validation step. We expect this work to make four contributions to the privacy-NLP literature: (i) a benchmark fit for industry-track publication and enterprise deployment evaluation, (ii) a generation methodology reproducible by other research groups, (iii) a controlled-comparison subset enabling causal claims about axis effects that no prior PII benchmark supports, and (iv) an evaluation framework template — including the synthetic–real ranking-correlation study design and per-disclosure-form / per-sensitivity-tier stratified F1 — applicable to adjacent synthetic-data tasks. The per-entity metadata schema additionally scaffolds Tracks 2–4 (query-aware masking, re-identification risk scoring, model leakage) for subsequent releases, which are out of scope here.

---

## Appendix A — Full Hard-Rule List (R1–R15)

Documented in full in `generation_prompt_v3.yaml` and `PII_Benchmark_Generation_Prompt_v3.docx`. Summary:

- **R1** No LLM offsets.
- **R2** Entity strings verbatim.
- **R3** Fictional only.
- **R4** Multi-mention completeness.
- **R5** Nine-axis conjunction.
- **R6** Adjacency thresholds.
- **R7** Per-entity metadata.
- **R8** OCR substitution rules.
- **R9** Code-switching definition.
- **R10** Nine-point self-check.
- **R11** Triple-name rule (8 decomposition cases).
- **R12** Format-validity contract.
- **R13** Canonical 51 types only.
- **R14** Sensitivity tier (Article 9 mapping).
- **R15** Script-aware adjacency.

## Appendix B — Few-Shot Exemplar Index

| # | Behavioral target | Axes summary |
|---|---|---|
| 1 | Tight CO-008 email metadata, multi-mention | EN, email, tight, density=medium |
| 2 | Tight CO-009 patient header | EN, plain_text, tight, healthcare |
| 3 | Hypothetical frame (disclosed=false on SSN) | EN, plain_text, loose, legal |
| 4 | Partial disclosure | EN, plain_text, loose, finance |
| 5 | OCR distortion across 8 types | EN, log_entry, loose, government, hard |
| 6 | Heavy Hindi-English code-switching | EN matrix + HI embedded, chat_transcript, healthcare |
| 7 | Cross-sentence coreference | EN, plain_text, none-adjacency, legal |
| 8 | Japanese JSON, tight CO-012 HR cluster | JA, json_record, tight, HR |
| 9 | Arabic RTL, tight CO-011, density=high, IBAN, Article 9 | AR, key_value_pairs, tight, finance |
| 10 | Negation frame, ticket_worknotes, Article 9 (Religion + Crime) | EN, ticket_worknotes, loose, legal, hard |
| 11 | **Paired-sweep mode (v3.2)** — anchor A-042 with frozen entity values, format-sweep variant | EN, email, healthcare, mode=paired_sweep |

## Appendix C — Metric Definitions (formulas)

**C1 Entity-type entropy.**
H = −Σ_{t=1}^{51} p_t log₂ p_t where p_t = count(type t) / total entity count.

**C3 Distinct-2.**
\|{unique bigrams}\| / \|{total bigrams}\|.

**C4 Self-BLEU-3.**
For each record r, BLEU-3(r, corpus \ {r}); reported as mean.

**C7 Vendi Score.** (Friedman & Dieng, 2023)
Let K be the n×n cosine-similarity matrix of sentence-BERT embeddings. Let {λ_i} be the eigenvalues of K/n. VS = exp(−Σ_i λ_i log λ_i).

**D6 MAUVE.** (Pillutla et al., 2021)
Estimated via the official `mauve-text` library against a domain-matched real-text reference.

**E3 Luhn check.** Standard mod-10 algorithm on the digit string of the Credit_Card_Numbers entity.

**E4 IBAN check.** Move first four characters to the end, convert letters A→10..Z→35, compute mod-97; valid if remainder = 1.

**F1 Cohen's κ.** κ = (p_o − p_e) / (1 − p_e) where p_o is observed agreement on disclosed=true/false and p_e is the chance-agreement probability under marginal distributions of the two raters (model vs LLM judge).

**F5 Per-disclosure-form F1.** Given a held-out PII detector M and the released corpus partitioned by `disclosure_form ∈ {complete, partial, obfuscated}`, compute the standard span-level F1 of M against the ground-truth annotations *within each partition*. Report all three values F1(complete), F1(partial), F1(obfuscated). The *safety gap* is F1(complete) − F1(obfuscated); target gap ≤ 20 F1 points.

**F6 Per-sensitivity-tier F1.** Given a held-out PII detector M and the released corpus partitioned by `sensitivity_tier ∈ {HIGH, MEDIUM, LOW}` (per R14 mapping; entities labeled per-span), compute the standard span-level F1 of M against the ground-truth annotations *within each partition*. Report all three values F1(HIGH), F1(MEDIUM), F1(LOW). The *Article 9 gap* is F1(LOW) − F1(HIGH); target gap ≤ 10 F1 points (a large gap indicates systematic under-detection of regulated special-category data).

**G1 G-Eval.** Chain-of-thought judge prompt with explicit rubric (coherence, relevance, format compliance, factuality), each scored 1–5; aggregate is the mean.

**H1 Two-run F1.** Generate twice with different random seeds for the same axis configuration; compute span-level F1 on the union of entities, treating an entity as matched iff (type, start, end) align exactly.

**K1 Kendall's τ.** Given two rankings of n models, τ = (n_concordant − n_discordant) / (n(n−1)/2). Computed on F1 scores between synthetic and real subsets. With 5 models, n(n−1)/2 = 10 pairs.

**K2 Spearman's ρ.** ρ = 1 − (6 Σ d_i² / n(n²−1)) where d_i is the difference in ranks of model i between synthetic and real subsets.

**K3 Mean absolute F1 delta.** (1/n) Σ_i \|F1_synth(model_i) − F1_real(model_i)\| over n=5 models.

**K4 Bootstrap CI on Kendall's τ.** 1,000 bootstrap resamples of the 300-record evaluation subset; 95% CI computed as the [2.5th, 97.5th] percentile.

## Appendix D — Configuration Files (locations in repo)

| Artifact | Path |
|---|---|
| **Pattern catalog v4 (authoritative)** | `tasks/pii_generation/PII_Pattern_Catalog_v4_MASTER.md` (4,127 patterns across 51 entities) |
| Pattern catalog v4 — derived JSON | `tasks/pii_generation/pattern_seed_data_v4.json` (generated from the markdown source) |
| Pattern catalog v3 (deprecated) | `tasks/pii_generation/pattern_seed_data.json` (~820 patterns; superseded by v4) |
| v3 CO-### → v4 pattern mapping | `tasks/pii_generation/co_to_v4_mapping.json` (see Appendix G) |
| Generation prompt | `tasks/pii_generation/generation_prompt_v3.yaml` |
| Prompt as Word doc | `tasks/pii_generation/PII_Benchmark_Generation_Prompt_v3.docx` |
| SyGra graph config (CS) | `tasks/pii_generation/graph_config.yaml` |
| SyGra graph config (EN) | `tasks/pii_generation_en/graph_config.yaml` |
| SyGra graph config (multilingual) | `tasks/pii_generation_ml/graph_config.yaml` |
| Paired-sweep anchor library | `tasks/pii_generation/paired_sweep_anchors.json` |
| Real-data label map | `tasks/pii_generation/label_map.json` |
| Post-processors and validators | `tasks/pii_generation/task_executor.py` |
| Repair script | `tasks/pii_generation/repair_zero_entities.py` |
| Audit script | `tasks/pii_generation/audit_samples.py` |
| Correlation-study harness | `tasks/pii_generation/correlation_study.py` |
| Methodology doc (this file) | `tasks/pii_generation/PII_Benchmark_Methodology_Final.docx` |

## Appendix E — Acronyms

- **CS** code-switching
- **CO-###** co-occurrence pattern (CO-001 through CO-015)
- **CI** confidence interval
- **DUA** Data Use Agreement
- **IAA** inter-annotator agreement
- **κ** Cohen's kappa
- **MAUVE** Measuring the gap between neural text And human text Using diVergence in Embeddings (Pillutla et al., 2021)
- **NIST ACTS** Advanced Combinatorial Testing System (covering-array tool)
- **NID** National Identification Number
- **PEP** Politically Exposed Person
- **PHI** Protected Health Information
- **PII** Personally Identifiable Information
- **ρ** Spearman's rank correlation
- **RTL** Right-To-Left script
- **τ** Kendall's tau rank correlation
- **TTR** Type-Token Ratio
- **VS** Vendi Score

## Appendix F — References

Friedman, D. & Dieng, A. B. (2023). The Vendi Score: A Diversity Evaluation Metric for Machine Learning. *Transactions on Machine Learning Research*.

Gardner, M. et al. (2020). Evaluating Models' Local Decision Boundaries via Contrast Sets. *Findings of EMNLP 2020*.

Hu, J. et al. (2020). XTREME: A Massively Multilingual Multi-task Benchmark for Evaluating Cross-lingual Generalisation. *ICML 2020*.

Kaushik, D. et al. (2020). Learning the Difference that Makes a Difference with Counterfactually-Augmented Data. *ICLR 2020*.

Kendall, M. G. (1938). A New Measure of Rank Correlation. *Biometrika*.

Kiela, D. et al. (2021). Dynabench: Rethinking Benchmarking in NLP. *NAACL 2021*.

Kim, S. et al. (2024). Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models. *EMNLP 2024*.

Liu, N. F. et al. (2024). Lost in the Middle: How Language Models Use Long Contexts. *TACL*.

Liu, Y. et al. (2023). G-Eval: NLG Evaluation Using GPT-4 with Better Human Alignment. *EMNLP 2023*.

Patel, A. et al. (2024). DataDreamer: A Tool for Synthetic Data Generation and Reproducible LLM Workflows. *ACL 2024*.

Pillutla, K. et al. (2021). MAUVE: Measuring the Gap Between Neural Text and Human Text using Divergence Frontiers. *NeurIPS 2021* (Outstanding Paper).

Pilán, I. et al. (2022). The Text Anonymization Benchmark (TAB): A Dedicated Corpus and Evaluation Framework for Text Anonymization. *Computational Linguistics*.

Ribeiro, M. T. et al. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList. *ACL 2020* (Best Paper).

Spearman, C. (1904). The Proof and Measurement of Association Between Two Things. *American Journal of Psychology*.

Stubbs, A. & Uzuner, Ö. (2015). Annotating Longitudinal Clinical Narratives for De-identification: The 2014 i2b2/UTHealth Corpus. *Journal of Biomedical Informatics*.

Wang, Y. et al. (2023). Self-Instruct: Aligning Language Models with Self-Generated Instructions. *ACL 2023*.

Xu, C. et al. (2024). Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing. *2024 preprint*.

Xu, C. et al. (2023). WizardLM: Empowering Large Language Models to Follow Complex Instructions. *2023 preprint*.

PIIBench (2025). [Benchmark paper anchoring the F1=0 empirical claim for credentials and sensitive-attribute entity types.]

---

## Appendix G — v3 CO-### → v4 Pattern Mapping

The v3 catalog defined 15 named co-occurrence patterns (CO-001 through CO-015) as a discrete 9th-axis taxonomy for adjacency-tight entity clustering. The v4 catalog reframes this as cross-cutting Dimension #9 ("Adjacency-tight form") of the 20-dimension consistency sweep, with the cluster examples distributed across individual entity tables. This appendix preserves the v3 named-cluster taxonomy by mapping each CO-### to the constituent v4 patterns that together realize the cluster.

Each row lists the cluster name, the v4 patterns that realize it (anchor patterns identified by programmatic scan of v4), and a verbatim example. The mapping is the basis for the prompt's R6 directive *"if adjacency=tight, follow the named CO-### pattern"*; in v4-aligned generation, the sampler consults this appendix to translate a CO-### request into the combination of v4 patterns that produces the cluster.

### G.1 Mapping table

| CO-### | Cluster name | v4 anchor patterns | Example |
|---|---|---|---|
| CO-001 | Person + Email (angle brackets) | **FUN-088** (Adjacency-tight with email) + **WE-046/047** (with display name) | `Sarah Chen <s.chen@acmecorp.com>` |
| CO-002 | Person + Email + Phone (parenthesized) | FUN-088 + **WE-046** + **TW-002** (parenthesized US area code) | `Sarah Chen (s.chen@corp.com, +1 (555) 234-8901)` |
| CO-003 | Person + DOB + ID (comma chain) | **FUN-090** (adjacency-tight with ID) + **DOB-094/095** (DOB adjacency-tight) + **NID-091** (NID adjacency-tight with name) | `Maria García López, DOB 03/15/1985, MRN 78901` |
| CO-004 | Title + Person + Org (formal) | **BT-079** (adjacency-tight with name) + **FUN-013** (with honorific prefix) + **ORG-001/044** (formal company / hospital) | `Dr. Michael Johnson, Chief Medical Officer, City General Hospital` |
| CO-005 | Person + Job + Org (resume style) | **PROF-004/005** (employment dates) + **PROF-008** (reverse-chronological CV) + **ORG-112** (Org in resume / CV) | `Senior Engineer, Google (2018-2022)` |
| CO-006 | Person + Salary | **SAL-059** (Salary adjacency-tight) + FUN-### (name reference) | `John Smith earned $145K base plus $30K bonus` |
| CO-007 | Address tight cluster | **AW-098** (work address adjacency-tight) or **AP-075** (personal address adjacency-tight) — single span absorbing street + city + state + ZIP + country | `742 Evergreen Terrace, Springfield, IL 62704, USA` |
| CO-008 | Email metadata block | **FUN-071** (email "From:" header) + **WE-060/061/062** (cc/bcc, From, Reply-To) | `From: Sarah Chen <s.chen@corp.com>; To: John Smith <j.smith@corp.com>` |
| CO-009 | Patient header | **FUN-098** (medical record format) + **DOB-076** (DOB in medical chart) + **MED-077** (MRN) + **ALLG-051** (allergy in medical chart) + **CRN-016/017** (healthcare MRN / patient ID) | `Patient: John Smith DOB: 03/15/1985 MRN: 78901 Allergy: Penicillin` |
| CO-010 | Authentication cluster | **PWD-029/030** (API key / Bearer token) or PWD-### (plaintext) + **IP-031** (IP in auth/SSH log) + FUN-### (user reference) | `User: jsmith Password: Welcome123! IP: 192.168.1.45` |
| CO-011 | Compliance cluster | NA-### (Nationality form) + CIT-### (Citizenship form) + **PEP-023/024/025** (PEP screening result/no-match/possible-match) + TUM-### (Trade Union) | `Name: Maria García Nationality: Spanish PEP: Yes Citizenship: Spain` |
| CO-012 | HR record cluster | **EID-034** (EID in HR record) + **FUN-090** (adjacency-tight with ID) + **SAL-047** (Salary in HR record) + **BT-017** (HR roles) | `Employee: John Smith ID: EMP-4821 Title: Senior Engineer Salary: $145,000` |
| CO-013 | Contact card | **FUN-070** (email signature) + BT-### (title in signature) + WE-### (email in signature) + TW-### (phone in signature) | `Sarah Chen, Marketing Director, sarah.chen@corp.com, +1-555-234-8901` |
| CO-014 | Legal citation | **FUN-097** (legal pleading style) + **DOB-075** (DOB in legal pleading) + **CRIME-058** (court case number) + **CRIME-059** (court name/jurisdiction) + CRIME-### (statute) | `Defendant John Smith (DOB 07/22/1985) charged with fraud under 18 U.S.C. §1030` |
| CO-015 | Form key-value adjacency | **FUN-066** (key-value pair form field) + **AG-004/049/050** (Age in form/JSON/KV) + **GN-046** (form/KV gender) + **TW-079** (phone in KV) | `Name: John Smith Age: 35 Gender: Male Phone: 555-1234` |

### G.2 How the sampler consults this mapping

When the v3.2 prompt's R6 directive specifies `adjacency=tight` and a `co_occurrence_pattern: CO-###`, the sampler:

1. Looks up the row above to identify the v4 anchor patterns that constitute the cluster.
2. Selects one pattern per row, prioritising the boldfaced anchors as primary realisations.
3. Generates the cluster by combining the selected patterns into one contiguous text span, satisfying R6 (≤punctuation-only separation between PII spans) and Cross-Cutting Dimension #9 of the v4 catalog.

This mapping is also serialised as `tasks/pii_generation/co_to_v4_mapping.json` for programmatic consumption.

### G.3 Status of mappings

All anchor patterns in §G.1 were located by programmatic scan of the v4 catalog markdown source on 2026-05-14. Boldfaced patterns are *confirmed exact* matches whose name or description in v4 directly references the v3 CO-### concept. Non-boldfaced patterns are *complementary* — present in v4 with semantically matching content but not labelled as cluster anchors. Mappings flagged as `FUN-###` or `WE-###` without a number indicate that *any* pattern of that prefix matching the cluster's content (e.g., any name surface form) is admissible.

If the lead author subsequently identifies a more specific v4 anchor for any CO-###, this appendix is updated and the JSON serialisation regenerated; the prompt's R6 logic is unchanged.

---

## Appendix H — v3 → v4 Prefix Migration Table

Eighteen entity prefixes were renamed between v3 and v4 of the pattern catalog. Two of the renames produce silent collisions where a v3 pattern_id refers to a different entity under v4. This appendix documents the full migration table to enable bidirectional lookup and prevent mis-routing of pattern references from v3.2-era code, prompts, and outputs.

### H.1 Prefix migration table

| Entity | v3 prefix | v4 prefix | Status |
|---|---|---|---|
| Full_Name | FN | **FUN** | Renamed |
| First_Given_Name | FGN | FGN | Unchanged |
| Last_Family_Name | LFN | LFN | Unchanged |
| Preferred_Name | PFN | PFN | Unchanged |
| Business_Title | BT | BT | Unchanged |
| Address_Work | AW | AW | Unchanged |
| Address_Personal | AP | AP | Unchanged |
| Telephone_Numbers_Work | TW | TW | Unchanged |
| Telephone_Numbers_Personal | TP | TP | Unchanged |
| Work_Email_Address | WE | WE | Unchanged |
| Personal_Email_Address | PE | PE | Unchanged |
| Date_of_Birth | DOB | DOB | Unchanged |
| Age | AG | AG | Unchanged |
| Place_of_Birth | POB | POB | Unchanged |
| Gender | GN | GN | Unchanged |
| Marital_Status | MS | MS | Unchanged |
| Nationality | NA | NA | Unchanged |
| Citizenship_Status | CIT | CIT | Unchanged |
| Sex_Orientation | SO | SO | Unchanged |
| Religion | RE | RE | Unchanged |
| **Political_Party** | **PA** | **PP** | ⚠️ Renamed; **collides with v3 PP** |
| Country (v3) / Country_of_Residence (v4) | CO | **CR** | ⚠️ Renamed; **collides with v3 CR** |
| State | ST | ST | Unchanged |
| City | CI | CITY | Renamed |
| Location | LO | **LOC** | Renamed |
| Geolocation_Data | GL | GEO | Renamed |
| National_Identification_Number | NI | **NID** | Renamed |
| **Passport_Number** | **PP** | **PA** | ⚠️ Renamed; **collides with v3 PA** |
| Driving_License_Number | DL | DL | Unchanged |
| Tax_Reference_Number | TX | TX | Unchanged |
| Compensation_And_Salary | CS | **SAL** | Renamed |
| Credit_Card_Numbers | CC | CC | Unchanged |
| Customer_Reference_Number | CRN | CRN | Unchanged |
| Account_Statements | AS | **AST** | Renamed |
| Business_Title | BT | BT | Unchanged |
| Org_Name | OR | **ORG** | Renamed |
| Employee_ID_Number | EI | **EID** | Renamed |
| Building_Badge_Entry_Card_Number (v3) / Building_Badge_Card_Number (v4) | BB | BB | Renamed entity; prefix unchanged |
| Performance_Assessment | PA | **PERF** | Renamed (resolves v3 PA collision with Political_Party) |
| Disciplinary_Action | DA | **DISC** | Renamed |
| Sickness_Day_Records | SD | **SICK** | Renamed |
| Professional_Background | PB | **PROF** | Renamed |
| **Crime** | **CR** | **CRIME** | ⚠️ Renamed; **collides with v4 CR (Country)** |
| PEP_Status | PEP | PEP | Unchanged |
| Trade_Union_Membership | TU | **TUM** | Renamed |
| Allergy_Information | AL | **ALLG** | Renamed |
| Medical_Information | MI | **MED** | Renamed |
| Social_Media_Identifiers | SM | SM | Unchanged |
| Static_IP_Address | IP | IP | Unchanged |
| Password | PW | **PWD** | Renamed |
| Date_Time | DT | DT | Unchanged |
| Emergency_Contact_Details | EC | EC | Unchanged |

### H.2 Silent prefix collisions — handling

Two collisions require explicit translation when v3 pattern IDs appear in v4-aligned context:

| Collision | v3 meaning | v4 meaning | Translation rule |
|---|---|---|---|
| **CR-###** | Crime (v3) | Country_of_Residence (v4) | If a v3 reference reads `CR-020`, translate to **`CRIME-020`** under v4. |
| **PA-###** | Political_Party (v3) | Passport_Number (v4) | If a v3 reference reads `PA-001` and the surrounding entity context is Political_Party, translate to **`PP-001`** under v4. If the context is Passport_Number, the reference is already v4-valid. |
| **PP-###** | Passport_Number (v3) | Political_Party (v4) | If a v3 reference reads `PP-001` and the surrounding context is Passport_Number, translate to **`PA-001`** under v4. |

The translation logic is encoded in `tasks/pii_generation/v3_to_v4_prefix_map.json`. Any code that ingests pre-v4 pattern_id references should pipe them through this mapping before lookup against the v4 catalog.

### H.3 Entity name renames

Three entity names changed between v3 and v4. The v3.2 prompt's R13 canonical-type list and the methodology doc's §3.1 entity table reference v3 names and require update:

| v3 canonical name | v4 canonical name |
|---|---|
| `Country` | `Country_of_Residence` |
| `Building_Badge_Entry_Card_Number` | `Building_Badge_Card_Number` (dropped "Entry_") |
| `Compensation_And_Salary` (capital A) | `Compensation_and_Salary` (lowercase a) |

Until the prompt is updated (planned in v3.3), generation runs are advised to pin `entity_type` to v3 names AND maintain a v3→v4 name-translation layer in the offset aligner.

---

## Appendix I — Entity Density and Context Length Calibration Reference

This appendix provides the practical calibration reference for the two quantitative axes (context_length and entity_density) defined in §4.1. The §4.1 axis table is the canonical spec; this appendix translates that spec into absolute counts per tier and provides worked examples for downstream consumers (samplers, generators, reviewers).

### I.1 Definitions recap

**Context length — measured in tokens (cl100k_base tokenizer)**

| Tier | Token range | Approx char range (English reference) |
|---|---|---|
| small | 50–200 tokens | ≈ 200–600 chars |
| medium | 200–600 tokens | ≈ 600–2,000 chars |
| large | 600–2,000 tokens | ≈ 2,000–8,000 chars |
| very_large | 2,000–4,000 tokens | ≈ 8,000–16,000 chars |

The character ranges are *reference only* (English); non-Latin scripts (CJK, Thai, Arabic) consume tokens at different ratios so character counts diverge from token counts.

**Entity density — measured as rate per 1,000 tokens**

| Tier | Rate | Semantic descriptor |
|---|---|---|
| low | 1–4 entities per 1,000 tokens | PII is *mentioned* — single mentions inside flowing prose |
| medium | 5–15 entities per 1,000 tokens | PII is the *subject* — text is about someone, with their identifying info woven in |
| high | ≥16 entities per 1,000 tokens | PII is the *content* — text is mostly structured records or fields, not narrative |

Plus minimum absolute floors so the tier remains interpretable for very small records: **low ≥1, medium ≥3, high ≥5 absolute entities**.

### I.2 Absolute count translation per context-length tier

The rate-based definition yields different absolute count ranges for each length tier. Generators and reviewers should aim within these ranges:

| Context length | low (1–4/1K) | medium (5–15/1K) | high (≥16/1K) |
|---|---|---|---|
| small (50–200 tokens) | 1 entity (floor) | 3 entities (floor) | 5+ entities (floor) |
| medium (200–600 tokens) | 1–2 entities | 3–9 entities (floor=3) | 5–10+ entities (floor=5) |
| large (600–2,000 tokens) | 2–8 entities | 7–30 entities | 10–32+ entities |
| very_large (2,000–4,000 tokens) | 3–16 entities | 15–60 entities | 33+ entities |

For small records, the absolute floors dominate the rate computation — a 100-token text physically cannot hold 16+ entities (the structural density of natural language imposes a ceiling well below that rate). The floor of 5 entities on small/high records corresponds to ≈ 50 entities per 1,000 tokens, which is the maximum density achievable in coherent text.

### I.3 Worked examples

| Example | Approx tokens | Entity count | Density tier | Why |
|---|---|---|---|---|
| Short email: *"Hi John, please call me at 555-1234. — Sarah"* | ~25 | 3 (John, Sarah, phone) | **medium** | Hits floor=3 |
| 200-token customer-service ticket with 1 name | 200 (small upper) | 1 | **low** | 5/1K rate |
| Clinical note: *"Patient Maria García López, DOB 03/15/1985, MRN 78901, diagnosed with diabetes, prescribed metformin, allergic to penicillin"* | ~50 | 6 | **high** | ~120/1K rate; above floor=5 |
| 1,000-token HR memo with 8 entities scattered through narrative | 1,000 (large) | 8 | **medium** | 8/1K rate |
| 800-token employee directory entry with 18 fields filled out | 800 (large) | 18 | **high** | 22/1K rate |
| 3,000-token long-form medical chart with 12 PII references | 3,000 (very_large) | 12 | **low** | 4/1K rate (sparse despite high absolute count) |
| 3,000-token form-heavy intake with 60 entities | 3,000 (very_large) | 60 | **high** | 20/1K rate |

The third and sixth rows illustrate the **length-invariance property** of rate-based density: identical absolute counts (e.g., the medical chart with 12 entities versus a hypothetical 200-token text with 12 entities) yield different density classifications because the former is sparse-per-token and the latter is dense-per-token.

### I.4 Sampler implementation notes

The covering-array sampler (§4.4 Stage 1, Mode 1) interprets the `entity_density` axis as a *target rate*, not an absolute count, when computing the expected entity count for a generated record. The sampler:

1. Draws `context_length` and `entity_density` independently from their respective axis distributions.
2. Computes the *target rate* in entities/1K tokens at the centre of the chosen density tier (low=2.5, medium=10, high=20).
3. Computes the *target absolute count* = round(target_rate × token_count / 1000), bounded below by the floor of the tier.
4. Passes the target absolute count to the generator's user prompt as a soft guideline; the generator's R10(e) self-check verifies the emitted record falls within the tier's rate range.

This procedure ensures cross-length comparability: a *medium-density* small record and a *medium-density* very_large record evaluate the detector on the same relative PII concentration, not the same absolute count.

### I.5 Token-count estimation guidance for the generator

The generator estimates token count using a heuristic at emission time (the canonical token counter, cl100k_base, is invoked downstream by the auditor for exact verification):

| Script | Approx tokens per character |
|---|---|
| Latin (EN/FR/DE/ES/IT/PT/NL/Nordic/Czech/Polish/Turkish/Hungarian) | 0.25 (≈ 4 chars per token) |
| Cyrillic (Russian) | 0.5 |
| CJK (Chinese, Japanese, Korean) | 1.0 |
| Thai | 1.5 |
| Arabic | 0.6 |
| Hebrew | 0.5 |
| Devanagari (Hindi) | 0.9 |

The generator should target *tokens* — not characters — when sizing the passage. Mismatch between estimated and exact token count of more than 30% triggers a regeneration in the audit stage.

---

*End of methodology document. The companion artefacts are `generation_prompt_v3.yaml` / `PII_Benchmark_Generation_Prompt_v3.docx` / `PII_Benchmark_Generation_Prompt_v3.md`, the v4 pattern catalog `PII_Pattern_Catalog_v4_MASTER.md`, and the CO-### → v4 mapping `co_to_v4_mapping.json`.*
