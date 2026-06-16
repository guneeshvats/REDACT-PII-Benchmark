# PII Pattern Catalog v4 — Consolidated Master Document

**Authors:** Anonymous Authors  
**Affiliation:** Anonymous Institution  
**Version:** 4.0 (Final)  
**Date:** May 2026  
**Status:** Draft for review — to support EMNLP 2026 submission

---

## Abstract

This document presents the v4 Pattern Catalog supporting the *Multilingual PII Detection Benchmark* project at Anonymous Institution. The catalog defines a structured, exhaustive enumeration of surface-form patterns under which 51 distinct Personally Identifiable Information (PII) entity types appear in real-world text. It contains **4,127 patterns** across **51 entities**, generated through an 11-batch authored process combining entity-natural enumeration with a 20-dimensional cross-cutting consistency sweep. The catalog serves three roles in the benchmark project: (a) as the *generation specification* fed to the SyGra-based synthetic data pipeline, (b) as the *evaluation taxonomy* used by the Python evaluation framework, and (c) as the *coverage claim* defended in the accompanying research paper.

This document is structured in three parts:
1. **Methodology and Foundations** (§1–§4) — describing the research-grade construction process suitable for publication
2. **Validation Plan** (§5) — five quantitative validation experiments that defend the "exhaustive" claim for peer review
3. **Pattern Catalog** (§6 onward) — all 4,127 patterns organized by entity in sequence

---

## §1. Motivation and Research Foundations

### 1.1 Why an explicit pattern catalog is needed

Existing PII detection benchmarks — i2b2/n2c2 clinical de-identification corpora (Stubbs & Uzuner, 2015; 2017), WikiPII, ai4Privacy, CoNLL-2003 PER/LOC/ORG subset — provide *labeled corpora* but do not publish the *surface-form taxonomy* underlying the labels. This creates three problems for benchmark design:

1. **Opaque coverage.** When a detector achieves 95% F1 on a benchmark, it is unclear whether the missed 5% is uniform noise or a systematic gap (e.g., the benchmark contained no non-Latin scripts, no OCR-distorted samples, no privacy-redacted samples).
2. **No basis for extension.** Without an enumerated pattern space, augmenting an existing benchmark with new patterns risks introducing distribution shift rather than legitimately expanding coverage.
3. **Cross-benchmark comparison is impossible.** Two benchmarks both labeled "SSN" may sample radically different sub-pattern distributions (one all dash-separated XXX-XX-XXXX, another all compact 9-digit), but downstream consumers cannot see this.

The Pattern Catalog directly addresses these gaps. Each entity is decomposed into named, ID-tagged sub-patterns (e.g., `NID-001` = US SSN dash-separated; `NID-002` = US SSN compact; `NID-095` = masked SSN with last-4 only). The catalog can be cited as a controlled vocabulary, queried for coverage gaps, and extended without ambiguity.

### 1.2 Position relative to existing taxonomies

The catalog is designed as a strict superset of four existing industry / regulatory taxonomies, with explicit additive entities and sub-patterns:

| Taxonomy | Entity count | Multilingual coverage | Pattern-level decomposition |
|---|---|---|---|
| Microsoft Presidio | ~25 | Partial (12 languages) | No |
| Google Cloud DLP | ~150 (mostly US-centric) | Partial | No |
| AWS Comprehend Medical PII | ~14 (clinical only) | English-only | No |
| NIST SP 800-122 | Conceptual taxonomy, no enumeration | N/A | No |
| **PII Catalog v4 (this work)** | **51** | **21+ languages, 7+ scripts** | **Yes — 4,127 sub-patterns** |

The catalog adds entities absent from all four comparators (Place_of_Birth, Sickness_Day_Records, Performance_Assessment, Disciplinary_Action, Trade_Union_Membership, PEP_Status, etc.) and decomposes each entity into named sub-patterns covering format, locale, script, embedding context, and adversarial cases (OCR distortion, partial masking, adjacency-tight cases).

---

## §2. Methodology — Three-Phase Construction

### Phase 1 — Entity Taxonomy Definition

The starting taxonomy was the team's internal PII Benchmark Methodology document (v3, 52 entities). Through iterative refinement and a v3→v4 merge of `Dietary_Preferences` into Religion (entries RE-021/RE-022) — based on the observation that all dietary patterns in v3 were religiously-motivated — the final v4 taxonomy contains 51 entities organized into 11 thematic batches:

| Batch | Theme | Entities |
|---|---|---|
| 1 | Personal names and titles | Full_Name, First_Given_Name, Last_Family_Name, Preferred_Name, Business_Title |
| 2 | Contact infrastructure | Address (Work, Personal), Telephone (Work, Personal), Work_Email |
| 3 | Personal demographics | Personal_Email, DOB, Age, Place_of_Birth, Gender |
| 4 | Identity & belief (GDPR Art. 9) | Marital, Nationality, Citizenship, Sex_Orientation, Religion |
| 5 | Geography & affiliation | Political_Party, Country_of_Residence, Location, City, State |
| 6 | Government-issued IDs | Geolocation, National_ID, Passport, Driving_License, Tax_Ref |
| 7 | Financial & employment IDs | Credit_Card, Customer_Ref, Account_Statements, Compensation, Employee_ID |
| 8 | HR / workplace data | Building_Badge, Performance_Assessment, Disciplinary_Action, Sickness_Records, Professional_Background |
| 9 | Special-category sensitive (Art. 9/10) | Crime, PEP_Status, Trade_Union, Allergy, Medical |
| 10 | Technical & temporal | Social_Media, Static_IP, Password, Date_Time, Emergency_Contact |
| 11 | Organizational | Org_Name |

Batching enables systematic processing, parallelization of authoring labor, and natural quality gates between batches.

### Phase 2 — Per-Entity Pattern Generation (Two-Step Protocol)

For each entity in each batch, authors applied the following protocol:

**Step 2a — Natural enumeration (unbounded).** Generate patterns naturally driven by the entity's intrinsic structure. The author considered, without an a priori cap on count:

- **Format variants** (e.g., for SSN: dash-separated, compact, with label, last-4 only, etc.)
- **Locale / country-specific variants** (e.g., for National_ID: 40+ country systems including US SSN/ITIN, UK NINO, German Steuer-ID, French NIR, Italian Codice Fiscale, Indian Aadhaar/PAN, etc.)
- **Script variants** for entities where non-Latin scripts produce structurally distinct patterns (e.g., Japanese 田中太郎 vs. romanized "Tanaka Taro")
- **Embedding contexts** — how the entity surfaces in the wild: clinical notes, HR records, legal pleadings, passport stamps, social-media bios, etc.

The objective is *recall* — capture every commonly-occurring pattern, without filtering for redundancy at this stage.

**Step 2b — Cross-cutting consistency sweep.** Apply a fixed 20-dimension consistency checklist to the patterns generated in Step 2a. For each dimension, verify at least one pattern is present; if absent, generate the missing pattern(s) before closing out the entity. The 20 dimensions are:

| # | Dimension | What it checks |
|---|---|---|
| 1 | OCR-distorted form | Common OCR errors (l↔1, O↔0, rn↔m, etc.) |
| 2 | Masked / redacted form | Privacy redaction patterns (X***X, ****, [REDACTED]) |
| 3 | Anonymized placeholder | Generic test values (000-00-0000, Jane Doe, example.com) |
| 4 | Multilingual context label | "DOB:" / "Date of Birth:" / "Fecha de nacimiento:" etc. |
| 5 | Native script representation | Where applicable (Japanese, Korean, Chinese, Russian, Arabic, Hebrew, etc.) |
| 6 | Country / locale variant | At minimum, 5+ countries where applicable |
| 7 | Format variant | Multiple format conventions (slash/dash/dot separators, etc.) |
| 8 | Structured-data embedding | JSON, KV, XML, CSV representations |
| 9 | Adjacency-tight form | No whitespace separator from adjacent text |
| 10 | Sentence-boundary tricky form | Trailing punctuation that could be confused with the value |
| 11 | Domain-embedded form | Clinical, legal, HR, financial domain contexts |
| 12 | Coding-system representation | ICD, CPT, ISO codes where applicable |
| 13 | Verbal / spoken-form transcription | "one-two-three-four-five" style |
| 14 | Date-anchored / lifecycle stage | Issued/expired/revoked status where applicable |
| 15 | Partial / range / approximate | "ending in X", "around 35", "in the 80s" |
| 16 | Compound / multi-value combination | E.g., card + CVV + expiry as bundle |
| 17 | URL / scheme-embedded form | Embedded in protocol/URL contexts |
| 18 | Status / state metadata | Active/inactive/pending/historical |
| 19 | Cross-purpose identifier overlap | Same ID used in multiple contexts (SSN as TIN, etc.) |
| 20 | Adversarial / homoglyph form | Cyrillic look-alikes, zero-width chars, etc., where applicable |

This dual-step protocol is critical to the methodology's defensibility: Step 2a guarantees *entity-natural depth*, while Step 2b guarantees *cross-cutting minimum coverage*. Together, they prevent two common failure modes: (a) a catalog deep on US-specific patterns but missing international variants, and (b) a catalog broad on countries but missing real-world distortion modes like OCR errors.

### Phase 3 — Authorship and Versioning

The catalog was authored by 5 contributors with overlapping review:

| Contributor | Primary contribution |
|---|---|
| Anonymous Author 1 | Lead author, taxonomy design, methodology, batches 1-11 |
| Anonymous Author 2 | Methodology validation, validation framework design |
| Anonymous Author 3 | Strategic review, taxonomy oversight |
| Anonymous Author 4 | Domain review |
| Anonymous Author 5 | Pipeline integration review |

The catalog evolved through four versions:

- **v1** — the generation team's initial seed document (18 base entities, exploratory patterns)
- **v2** — Expanded to 43 entities after excluding 12 non-text entities (image-only, audio-only); patterns reorganized
- **v3** — Expanded to 52 entities, ~750 patterns, formalized cross-cutting dimensions
- **v4** (this document) — 51 entities (Dietary merged into Religion), 4,127 patterns, formal 20-dimension sweep applied uniformly

---

## §3. Cross-Cutting Consistency Sweep — Full Definition

The 20-dimension sweep defined in §2 Step 2b is the methodological centerpiece of the catalog. Below, each dimension is defined with its purpose and example:

### Dimension 1 — OCR-distorted form
**Purpose:** Real-world PII data passes through document scanners (passports, IDs, medical records, signed contracts). OCR introduces characteristic substitutions.  
**Examples:** `l23-45-6789` (l for 1 in SSN), `j0hnsm1th@gmail.com` (zero for o), `RossSmlth` (l for i).

### Dimension 2 — Masked / redacted form
**Purpose:** PII in production systems frequently appears partially-redacted for safety. Detectors must recognize *both* full forms and masked forms.  
**Examples:** `***-**-6789`, `XXX-XX-1234`, `Smith, J***`, `[REDACTED]`.

### Dimension 3 — Anonymized placeholder
**Purpose:** Synthetic and test data uses canonical placeholders that should be detectable to avoid false-positive PII flags.  
**Examples:** `000-00-0000`, `Jane Doe`, `4111-1111-1111-1111` (Visa test card), `example.com`.

### Dimension 4 — Multilingual context label
**Purpose:** PII appears with localized field labels in forms and documents. Detection should be label-aware across languages.  
**Examples:** "DOB:" (EN), "Date de naissance:" (FR), "Geburtsdatum:" (DE), "出生日期:" (ZH), "תאריך לידה:" (HE).

### Dimension 5 — Native script representation
**Purpose:** Names, addresses, and labels in non-Latin scripts have distinct surface forms not derivable by transliteration alone.  
**Examples:** 田中太郎 (Japanese), 김민수 (Korean), Иван Петров (Russian), محمد أحمد (Arabic).

### Dimension 6 — Country / locale variant
**Purpose:** Many entities (national IDs, phone numbers, addresses, dates) have country-specific formats with no canonical superset.  
**Examples:** SSN (US 123-45-6789) vs. NINO (UK AB123456C) vs. Aadhaar (IN 1234 5678 9012).

### Dimension 7 — Format variant
**Purpose:** Within a single locale, an entity often has multiple acceptable format conventions.  
**Examples:** US SSN: dash-separated `123-45-6789`, compact `123456789`, with label `SSN: 123-45-6789`.

### Dimension 8 — Structured-data embedding
**Purpose:** PII flows through APIs and databases as structured data, not free text.  
**Examples:** JSON `{"ssn": "123-45-6789"}`, XML `<ssn>123-45-6789</ssn>`, CSV `"123-45-6789"`, KV `ssn=123-45-6789`.

### Dimension 9 — Adjacency-tight form
**Purpose:** OCR concatenation, malformed export pipelines, and poorly-tokenized strings produce no-whitespace boundaries between PII and adjacent content. Detectors built on whitespace tokenization fail here.  
**Examples:** `JohnSmith123-45-6789Customer`, `MariaGarcía@gmail.comPhone+1-917-555-0123`.

### Dimension 10 — Sentence-boundary tricky form
**Purpose:** Punctuation adjacent to PII (trailing period, question mark, exclamation) is a common source of detection error.  
**Examples:** "His SSN is 123-45-6789.", "Was the number A12345678?", "Email: john@example.com!".

### Dimension 11 — Domain-embedded form
**Purpose:** PII appears in domain-specific document templates that are themselves identifying.  
**Examples:** Clinical chart format (`Pt: Smith, John; DOB 03/15/1985; MRN 12345`), legal pleading, HR record.

### Dimension 12 — Coding-system representation
**Purpose:** Medical, financial, and government data have standardized coding systems alongside natural language.  
**Examples:** ICD-10 `E11.9`, CPT `99213`, SNOMED CT `73211009`, ISO 3166 `USA`.

### Dimension 13 — Verbal / spoken-form transcription
**Purpose:** Call-center recordings, voice notes, dictation produce non-numeric forms of numeric PII.  
**Examples:** "one-two-three dash four-five dash six-seven-eight-nine" (SSN), "March fifteenth, nineteen eighty-five" (DOB).

### Dimension 14 — Date-anchored / lifecycle stage
**Purpose:** Identifiers have lifecycle states (issued, expired, revoked, replaced) that change their context.  
**Examples:** "Passport issued 2020-03-15, expires 2030-03-15", "DL suspended", "Visa H-1B status".

### Dimension 15 — Partial / range / approximate
**Purpose:** Privacy practices often surface only partial identifying information.  
**Examples:** "ending in 6789", "age 30-35", "born in the 1980s", "first letter starts with J".

### Dimension 16 — Compound / multi-value combination
**Purpose:** PII frequently appears in bundles that increase joint identifying power (and risk).  
**Examples:** "Visa 4111-1111-1111-1111, exp 12/30, CVV 123", "John Smith, EID 12345, SSN 123-45-6789, DOB 03/15/1985".

### Dimension 17 — URL / scheme-embedded form
**Purpose:** PII leaks through URL parameters, deep links, and protocol schemes.  
**Examples:** `mailto:john@example.com`, `tel:+1-917-555-0123`, `https://app.example.com/user/12345?token=xyz`.

### Dimension 18 — Status / state metadata
**Purpose:** Production systems track active/inactive/pending/historical states alongside identifiers.  
**Examples:** "Customer active since 2010", "PIP in progress", "FMLA approved", "PEP status confirmed".

### Dimension 19 — Cross-purpose identifier overlap
**Purpose:** A single identifier often serves multiple purposes; detectors must recognize the same number under different labels.  
**Examples:** US SSN used as Tax ID (TIN), Italian Codice Fiscale used as both national ID and tax ID, Aadhaar linked to PAN.

### Dimension 20 — Adversarial / homoglyph form
**Purpose:** Adversarial attackers (and accidentally, internationalized text) introduce Unicode look-alikes that bypass naive pattern matching.  
**Examples:** `john.smіth@gmail.com` (Cyrillic і for Latin i), zero-width spaces, RTL override characters.

---

## §4. Statistical Summary

### 4.1 Overall counts

- **Total entities:** 51
- **Total patterns:** 4,127
- **Mean patterns per entity:** 80.9
- **Median patterns per entity:** 75
- **Min patterns per entity:** 40 (Preferred_Name)
- **Max patterns per entity:** 152 (Marital_Status)
- **Std deviation:** ~24 patterns per entity

### 4.2 Patterns per batch

| Batch | Theme | Entities | Patterns |
|---|---|---|---|
| 1 | Names + Title | 5 | 376 |
| 2 | Address + Phone + Work Email | 5 | 435 |
| 3 | Personal Email + DOB + Age + POB + Gender | 5 | 426 |
| 4 | Marital + Nationality + Citizenship + Orientation + Religion | 5 | 527 |
| 5 | Political + Country + Location + City + State | 5 | 400 |
| 6 | Geolocation + National ID + Passport + DL + Tax | 5 | 413 |
| 7 | Credit Card + Customer Ref + Statements + Salary + Employee ID | 5 | 327 |
| 8 | Badge + Performance + Discipline + Sickness + Professional | 5 | 301 |
| 9 | Crime + PEP + Union + Allergy + Medical | 5 | 433 |
| 10 | Social + IP + Password + Date/Time + Emergency Contact | 5 | 374 |
| 11 | Organization | 1 | 115 |
| **Total** | **11 batches** | **51 entities** | **4,127 patterns** |

### 4.3 Patterns per entity (full table)

| # | Entity | Prefix | Patterns |
|---|---|---|---|
| 1 | Full_Name | FUN | 101 |
| 2 | First_Given_Name | FGN | 71 |
| 3 | Last_Family_Name | LFN | 76 |
| 4 | Preferred_Name | PFN | 40 |
| 5 | Business_Title | BT | 88 |
| 6 | Address_Work | AW | 105 |
| 7 | Address_Personal | AP | 82 |
| 8 | Telephone_Numbers_Work | TW | 105 |
| 9 | Telephone_Numbers_Personal | TP | 57 |
| 10 | Work_Email_Address | WE | 86 |
| 11 | Personal_Email_Address | PE | 125 |
| 12 | Date_of_Birth | DOB | 103 |
| 13 | Age | AG | 80 |
| 14 | Place_of_Birth | POB | 53 |
| 15 | Gender | GN | 65 |
| 16 | Marital_Status | MS | 152 |
| 17 | Nationality | NA | 74 |
| 18 | Citizenship_Status | CIT | 86 |
| 19 | Sex_Orientation | SO | 95 |
| 20 | Religion | RE | 120 |
| 21 | Political_Party | PP | 136 |
| 22 | Country_of_Residence | CR | 50 |
| 23 | Location | LOC | 67 |
| 24 | City | CITY | 69 |
| 25 | State | ST | 78 |
| 26 | Geolocation_Data | GEO | 60 |
| 27 | National_Identification_Number | NID | 100 |
| 28 | Passport_Number | PA | 78 |
| 29 | Driving_License_Number | DL | 75 |
| 30 | Tax_Reference_Number | TX | 100 |
| 31 | Credit_Card_Numbers | CC | 73 |
| 32 | Customer_Reference_Number | CRN | 60 |
| 33 | Account_Statements | AST | 61 |
| 34 | Compensation_and_Salary | SAL | 73 |
| 35 | Employee_ID_Number | EID | 60 |
| 36 | Building_Badge_Card_Number | BB | 57 |
| 37 | Performance_Assessment | PERF | 55 |
| 38 | Disciplinary_Action | DISC | 57 |
| 39 | Sickness_Day_Records | SICK | 57 |
| 40 | Professional_Background | PROF | 75 |
| 41 | Crime | CRIME | 100 |
| 42 | PEP_Status | PEP | 62 |
| 43 | Trade_Union_Membership | TUM | 86 |
| 44 | Allergy_Information | ALLG | 75 |
| 45 | Medical_Information | MED | 110 |
| 46 | Social_Media_Identifiers | SM | 90 |
| 47 | Static_IP_Address | IP | 69 |
| 48 | Password | PWD | 70 |
| 49 | Date_Time | DT | 90 |
| 50 | Emergency_Contact_Details | EC | 55 |
| 51 | Org_Name | ORG | 115 |
| **Total** | | | **4,127** |

### 4.4 Coverage breadth

- **Languages with explicit pattern coverage:** 21+ (English, French, German, Spanish, Italian, Portuguese, Dutch, Russian, Japanese, Korean, Chinese (Simplified + Traditional), Arabic, Hebrew, Thai, Turkish, Polish, Czech, Hungarian, Hindi, Swedish, Norwegian, Danish, Finnish)
- **Writing systems / scripts:** Latin, Cyrillic, Arabic, Hebrew, Han (Hanzi/Kanji), Hangul, Devanagari, Thai, Hiragana, Katakana
- **Countries with locale-specific patterns:** 40+ for national IDs, 30+ for addresses and phone numbers
- **Calendar systems beyond Gregorian:** 7 (Japanese Reiwa/Heisei/Showa, Thai Buddhist, Hebrew, Hijri Arabic, Persian Jalali, Korean Dangi, Chinese Lunar)

---

## §5. Validation Plan

This section defines the five validation experiments that will accompany the pattern catalog in the EMNLP paper submission. Each experiment is described with its methodology, success criterion, and expected output.

### 5.1 Validation Experiment 1 — Coverage Against External Public Benchmarks

**Goal:** Quantify the fraction of real-world PII instances in established benchmark corpora that are captured by at least one pattern in our catalog. This is the *strongest single defense* against the "is it really exhaustive?" critique.

**Datasets:**
- **i2b2 / n2c2 2014 De-identification Challenge** — 1,304 longitudinal medical records, 28,872 PII instances across 25 PHI categories
- **i2b2 / n2c2 2016 De-identification Track** — 1,000 records, expanded PHI definitions
- **ai4Privacy multilingual PII dataset** (HuggingFace) — synthetic + scraped PII in 30+ languages
- **WikiPII** — synthetic PII inserted into Wikipedia article excerpts
- *(Optional)* CoNLL-2003 NER subset (PER, LOC, ORG only)

**Methodology:**
1. For each external PII instance in the benchmark, manually (or with pre-defined rules) determine which catalog pattern ID — if any — matches it.
2. Compute coverage: `% instances matched / total instances`, reported overall and broken down by entity.
3. For unmatched instances, classify into one of: (a) genuine gap in our catalog → add pattern; (b) entity outside our taxonomy → note as out-of-scope; (c) ambiguous → adjudicate.
4. Repeat after gap closure to compute final coverage.

**Success criterion:** ≥ 95% coverage on i2b2/n2c2; ≥ 90% on ai4Privacy/WikiPII (multilingual is harder).

**Expected output for paper:** Coverage table:

| Benchmark | Total PII instances | Matched by catalog | Coverage | Top 3 unmatched categories |
|---|---|---|---|---|
| i2b2 2014 | 28,872 | TBD | TBD | TBD |
| n2c2 2016 | TBD | TBD | TBD | TBD |
| ai4Privacy (en+fr+de+es) | TBD | TBD | TBD | TBD |
| WikiPII | TBD | TBD | TBD | TBD |

### 5.2 Validation Experiment 2 — Inter-Annotator Agreement (IAA)

**Goal:** Quantify reproducibility of the pattern-generation process. If two independent annotators following the same methodology produce highly-overlapping pattern sets, the methodology is reproducible and the catalog is not idiosyncratic to its author.

**Methodology:**
1. Select 5 entities from the v4 catalog at random, stratified across batches (one entity from each of 5 different batches to avoid topical clustering).
2. Recruit 2-3 independent annotators (Vidhan, the generation team, plus one additional team member) who have *not seen* the existing patterns for these entities.
3. Provide each annotator with:
   - The entity definition
   - The 20-dimension cross-cutting consistency sweep
   - 2-3 example patterns from a *different* entity as format reference
4. Each annotator independently generates patterns for the 5 entities, following the two-step protocol (§2.2).
5. Compute pairwise pattern-set overlap (Jaccard similarity) and Cohen's kappa on a per-pattern semantic-equivalence classification.

**Success criterion:** Cohen's κ ≥ 0.70 (substantial agreement, Landis & Koch 1977); Jaccard ≥ 0.65.

**Expected output for paper:** Table of per-entity κ values + qualitative discussion of disagreements (typically: granularity choices — "do MM/DD/YY and DD/MM/YY count as one pattern or two?").

### 5.3 Validation Experiment 3 — Industry / Regulatory Taxonomy Comparison

**Goal:** Demonstrate that the v4 catalog is a strict superset of existing industry and regulatory PII taxonomies, with explicit additive contributions.

**Comparators:**
- **Microsoft Presidio** — Open-source PII anonymization (entity types in `presidio_analyzer`)
- **Google Cloud DLP** — InfoType list (currently ~150 types)
- **AWS Comprehend Medical PII** — Clinical PII entities
- **NIST SP 800-122** — US federal taxonomy of PII categories
- **GDPR Article 4(1) + Article 9 + Article 10** — Regulatory categories

**Methodology:**
1. Enumerate each comparator's published entity types.
2. For each comparator entity, identify the corresponding catalog entity (or note: "not in v4 → consider adding" / "v4 covers but split across multiple entities").
3. For each catalog entity, count comparator coverage (0/4, 1/4, ..., 4/4 of comparators that include it).
4. Identify catalog entities present in **0/4** comparators — these are the v4 contributions absent from all existing industry taxonomies.

**Success criterion:** v4 includes 100% of comparators' entities (with documented mapping); v4 contributes ≥ 10 entities present in 0/4 comparators.

**Expected output for paper:** Comparison matrix (51 rows × 5 columns), plus a list of the v4-novel entities.

### 5.4 Validation Experiment 4 — Saturation Analysis

**Goal:** Defend the claim that the catalog is "exhaustive within its taxonomy" by showing that additional iteration produces diminishing returns.

**Methodology:**
1. After v4 freezes, select 5 entities randomly (different from the IAA entities).
2. The lead author generates an *additional* round of patterns for these 5 entities, with the explicit goal of finding patterns that were missed.
3. Classify newly-generated patterns into: (a) genuinely novel patterns absent from v4; (b) variants of patterns already in v4; (c) duplicates.
4. Report the saturation ratio = `genuinely novel / total newly-generated`.

**Success criterion:** Saturation ratio < 10% (i.e., < 10% of additional generation produces truly novel patterns).

**Expected output for paper:** Per-entity saturation table + the genuinely-novel patterns (incorporated into v4.1 minor revision if any are found).

### 5.5 Validation Experiment 5 — Quantitative Descriptive Statistics

**Goal:** Provide a "reading guide" set of statistics that lets reviewers and downstream users quickly assess catalog scope and density.

**Reported metrics:**
1. Patterns per entity: mean, median, min/max, std dev (already computed in §4.1)
2. **Cross-cutting dimension coverage matrix:** for each entity × each of the 20 dimensions, indicate ✓ / ✗. Target: all 51 × 20 = 1,020 cells filled. Report % filled overall + by dimension.
3. **Language coverage:** for each language, list which entities have explicit pattern coverage. Target: 21 languages × ≥ 10 entities each.
4. **Format-variant density:** average number of format variants per entity for entities that have multiple format conventions (e.g., dates, IDs, phones).
5. **Domain-embedding density:** how many real-world domains (clinical / legal / HR / financial / etc.) have at least one pattern per entity.

**Success criterion:** All metrics reported transparently; cross-cutting coverage ≥ 80% of cells filled.

**Expected output for paper:** Compact statistics tables + one heatmap visualization of cross-cutting dimension coverage.

---

## §6. Validation Schedule and Resource Plan

| Experiment | Effort estimate | Lead | Status |
|---|---|---|---|
| 5.1 External benchmark coverage | 3-4 weeks (annotator labor on i2b2 + ai4Privacy) | the lead author + Vidhan | Not started |
| 5.2 Inter-annotator agreement | 1 week (5 entities × 3 annotators) | the generation team + 2 annotators | Not started |
| 5.3 Industry taxonomy comparison | 1 week (desk research + mapping) | the lead author | Not started |
| 5.4 Saturation analysis | 3 days | the lead author | Not started |
| 5.5 Descriptive statistics | 1 day (script + visualization) | the lead author | §4 partial — needs cross-cutting matrix |

Total estimated effort: **5-6 weeks to complete all five experiments** post-v4 freeze.

---

## §7. Open Issues and Known Limitations

For transparency, the following are limitations to be acknowledged in the paper:

1. **No empirical labor-validated patterns yet.** The catalog is author-generated; the validation experiments above (especially 5.1) are designed to retrospectively test author-generated patterns against real corpora, but no patterns were *derived from* real corpora during construction. This is the most important gap.
2. **English / Western-bias residual.** Despite 21+ language coverage, the entity-natural step relies on author familiarity with US/EU contexts. Languages like Tagalog, Vietnamese, Swahili, Bengali, etc. have lighter coverage.
3. **Coding-system coverage is point-in-time.** ICD-11 transitions, EU AML 6 directive updates, US REAL ID compliance changes — the catalog will need periodic refresh.
4. **No formal sub-pattern hierarchy.** Patterns are flat-listed within each entity; a future v5 may introduce hierarchical sub-pattern groupings (e.g., NID → US → SSN → {dash, compact, label, masked}).

---

## §8. Pattern Catalog — Entity-by-Entity (4,127 patterns across 51 entities)

The remainder of this document presents the complete pattern catalog, organized in 51 entity sections (entities #1 through #51), following the same numbering and prefix scheme as the per-batch source files. Each entity section contains:

1. A brief definition of the entity
2. A **Natural Patterns** table with all numbered patterns, descriptions, and examples
3. A **Cross-Cutting Consistency Sweep** table verifying that all 20 dimensions are covered (with cross-references to the pattern IDs that cover each dimension)
4. A pattern count summary

The 11 thematic batches (§2.1) are preserved as logical grouping but the document reads as one continuous catalog from Entity 1 (Full_Name) to Entity 51 (Org_Name).

---

<!-- BEGIN CONSOLIDATED PATTERN CATALOG -->
## Entity 1: Full_Name

The complete personal name as a single span. Most names appear concatenated in real text. Highly culturally variable — name order, particles, double surnames, and script differ widely.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| FUN-001 | First Last (Western canonical) | Standard given + family order | John Smith, Sarah Chen, Maria Garcia, David Wilson |
| FUN-002 | First Middle Last | With middle name | John David Smith, Sarah Elizabeth Chen, Robert James Wilson |
| FUN-003 | First M. Last | Middle as initial | John D. Smith, Sarah M. Chen, Robert J. Williams, P. D. Q. Bach |
| FUN-004 | First Middle1 Middle2 Last | Multiple middle names | Mary Anne Elizabeth Smith, José Carlos Antonio García |
| FUN-005 | Inverted (Last, First) | Database / formal order | Smith, John; Chen, Sarah; García López, María |
| FUN-006 | Inverted with middle | Last, First Middle | Smith, John David; Chen, Sarah Elizabeth |
| FUN-007 | With nobiliary particle | Aristocratic / geographic | Ludwig van Beethoven, Catherine de Medici, Friedrich von Braun, Anne d'Arc |
| FUN-008 | With patronymic particle | Father-of indicator | Ahmed bin Salman, Fatima bint Mohammed, Björn Jónsson, Sigrid Jónsdóttir |
| FUN-009 | Hyphenated full name | Compound surname | Anne-Marie Müller-Schmidt, Jean-Paul Lefèvre, Mary-Jane Watson-Smith |
| FUN-010 | Spanish double surname | Paternal + maternal | María García López, Juan Rodríguez Fernández, Carlos Martínez Ruiz |
| FUN-011 | Portuguese double surname | Maternal + paternal | João Santos Silva, Ana Oliveira Costa, Pedro Souza Almeida |
| FUN-012 | With "y" / "i" conjunction | Spanish-Catalan compound | José y María García, Joan i Pere Mas-Colell |
| FUN-013 | With honorific prefix | Title + name | Dr. Sarah Chen, Mrs. Maria García, Prof. Wolfgang Müller, Rev. James O'Brien |
| FUN-014 | Religious honorific | Religious title | Father Patrick O'Brien, Rabbi David Cohen, Imam Ahmed Hassan, Sister Mary |
| FUN-015 | Military rank prefix | Rank + name | Col. James Mitchell, Capt. Sarah Brown, Sgt. Michael Davis, Lt. Cmdr. Williams |
| FUN-016 | Royal / aristocratic prefix | Title of nobility | Sir John Smith, Lady Margaret Thatcher, Lord Byron, Baroness Ashton |
| FUN-017 | With professional suffix | Credential after name | John Smith, MD; Sarah Chen, PhD; Wolfgang Müller, Esq.; Mary Jones, RN |
| FUN-018 | With generational suffix | Family suffix | John Smith Jr., Robert Wilson III, Henry James IV, Sr. |
| FUN-019 | Combined honorific + suffix | Both prefix and suffix | Dr. John Smith Jr., MD; Prof. Maria García-López, PhD |
| FUN-020 | Japanese (Last First, kanji) | Surname-first | 山田太郎, 鈴木花子, 田中健一, 佐藤美咲, 高橋翔 |
| FUN-021 | Japanese with romanization | Kanji + romaji | 山田太郎 (Yamada Tarō), 鈴木花子 (Suzuki Hanako) |
| FUN-022 | Japanese kana | Hiragana / katakana | やまだ たろう, ヤマダ タロウ |
| FUN-023 | Chinese (Last First, Hanzi) | Surname-first | 王伟, 李芳, 张明, 刘洋, 陈静 |
| FUN-024 | Chinese with pinyin | Hanzi + pinyin | 王伟 (Wáng Wěi), 李芳 (Lǐ Fāng), 张明 (Zhāng Míng) |
| FUN-025 | Traditional Chinese | Traditional Hanzi | 王偉, 李芳, 張明, 劉洋 |
| FUN-026 | Korean (Last First, Hangul) | Surname-first | 김민수, 이지영, 박현우, 정수진, 최서연 |
| FUN-027 | Korean with romanization | Hangul + romanized | 김민수 (Kim Min-su), 이지영 (Lee Ji-yeong) |
| FUN-028 | Hungarian order | Surname-first Latin | Nagy László, Kovács Katalin, Szabó Gábor, Tóth Erzsébet |
| FUN-029 | Vietnamese order | Last + Middle + First | Nguyễn Văn An, Trần Thị Mai, Lê Hoàng Long |
| FUN-030 | Russian patronymic | First + Patronymic + Last | Иван Петрович Сидоров, Мария Александровна Петрова |
| FUN-031 | Russian gender suffix | Surname agrees with gender | Иванов (m) / Иванова (f), Петров (m) / Петрова (f) |
| FUN-032 | Arabic with kunya/nasab | Multi-component traditional | Ahmed ibn Ali al-Rashid, Abu Bakr ibn Muhammad |
| FUN-033 | Arabic modern | Westernized shortened | محمد العبدالله, فاطمة الرشيد, أحمد بن سعيد |
| FUN-034 | Indian with initials | Initials + surname | A.P.J. Abdul Kalam, K.R. Narayanan, S. Radhakrishnan |
| FUN-035 | Indian community / caste indicator | Cultural marker | Sharma, Patel, Khan, Singh (Sikh), Iyer (Tamil Brahmin), Reddy |
| FUN-036 | Indonesian / mononym | Single name only | Sukarno, Suharto, Joko Widodo |
| FUN-037 | Icelandic patronymic | Father + son/dóttir | Björn Jónsson, Sigrid Jónsdóttir, Eiríkur Magnússon |
| FUN-038 | Spanish "de" particle | Aristocratic / geographic | Antonio Banderas de la Calle, María de los Ángeles |
| FUN-039 | Dutch "van / van der" particle | Geographic | Jan van der Berg, Marieke van Beek, Pieter van den Hoek |
| FUN-040 | French "de / du" particle | Aristocratic | Charles de Gaulle, Alexis de Tocqueville, Olivier du Pont |
| FUN-041 | Scottish / Irish Mc / Mac / O' | Patronymic prefix | John McGregor, Sarah O'Brien, Patrick MacDonald, Liam O'Sullivan |
| FUN-042 | With apostrophe | Celtic / Italian | O'Brien, O'Connor, D'Angelo, Dell'Acqua, D'Souza |
| FUN-043 | All-caps form | Official documents | JOHN SMITH, MARÍA GARCÍA, 山田太郎, WOLFGANG MÜLLER |
| FUN-044 | All-lowercase | Informal / digital | john smith, sarah chen, maria garcia |
| FUN-045 | Title-case mixed (typo) | Inconsistent casing | John smith, john Smith, MARIA garcía |
| FUN-046 | CamelCase (no spaces) | Compressed | JohnSmith, MariaGarcia, WolfgangMüller |
| FUN-047 | snake_case form | Database / programming | john_smith, maria_garcia, wolfgang_müller |
| FUN-048 | kebab-case form | URL slug | john-smith, maria-garcia-lopez, wolfgang-mueller |
| FUN-049 | OCR-distorted (l↔1↔I) | Character substitution | Mlchael Johsnon, Wllliam Srnith, Saral1 Clen |
| FUN-050 | OCR-distorted (O↔0) | Digit / letter confusion | J0hn Sm1th, Pe0rge Wash1ngt0n, R0bert Br0wn |
| FUN-051 | OCR-distorted (rn↔m, cl↔d) | Ligature failures | Wllllarn (Williams), Rlchard, Hlllary |
| FUN-052 | OCR-distorted (S↔5, B↔8) | Visual confusion | 5arah Chen, 8rian Wilson, Janne5 Thompson |
| FUN-053 | OCR-distorted whitespace | Spacing errors | JohnSmith (lost space), Sarah  Chen (double space) |
| FUN-054 | OCR diacritic stripping | Lost accents | Francois Muller (was François Müller), Soren Andersen |
| FUN-055 | With Latin diacritics | Accented chars | François Müller, Søren Andersen, Łukasz Kowalczyk, Ángel García-Pérez |
| FUN-056 | Mixed-script transliteration | Native + Latin parenthetical | 田中太郎 (Tanaka Tarō), 김민수 (Kim Min-su), محمد (Muhammad) |
| FUN-057 | Cyrillic name | Russian / Bulgarian / Serbian | Иван Иванов, Мария Петрова, Александр Соколов |
| FUN-058 | Hebrew name | Hebrew script | דוד כהן, שרה לוי, משה רוזנברג |
| FUN-059 | Thai name | Thai script | สมชาย สุขสวัสดิ์, สุภาพ พิทักษ์กุล |
| FUN-060 | Greek name | Greek script | Γιώργος Παπαδόπουλος, Μαρία Νικολαΐδης |
| FUN-061 | Embedded in email local-part | First/last inside email | sarah.chen@corp.com, john_smith@email.com, mariagarcia@gmail.com |
| FUN-062 | Embedded in URL path | Inside URL | linkedin.com/in/john-smith, /users/maria-garcia, github.com/wolfgang-mueller |
| FUN-063 | Embedded in social handle | Inside @ handle | @johnsmith, @maria.garcia, @wolfgang_mueller |
| FUN-064 | Embedded in file path | Filesystem path | /home/john.smith/, C:\Users\Sarah.Chen\, /var/log/maria_garcia.log |
| FUN-065 | JSON structured | Key + value | "full_name": "John Smith", "name":"Maria Garcia" |
| FUN-066 | Key-value pair | Form field | full_name=John Smith, Name: Maria Garcia, NAME: WOLFGANG MUELLER |
| FUN-067 | CSV row cell | Comma-separated | "Smith,John,35,Engineer", "Garcia,Maria,42,Manager" |
| FUN-068 | XML element | Markup tag | <name>John Smith</name>, <full_name>María García</full_name> |
| FUN-069 | Log line embedded | System log format | User John Smith logged in at..., [INFO] auth_user=sarah.chen |
| FUN-070 | Email signature | At end of email | Best regards, John Smith, Senior Engineer |
| FUN-071 | Email "From:" header | Email metadata | From: John Smith <jsmith@corp.com>, From: "Maria García" <maria@corp.com> |
| FUN-072 | Email greeting | "Dear" / "Hi" format | Dear John Smith, Hi Sarah, Hello Wolfgang Müller |
| FUN-073 | Email closing | "Sincerely" sign-off | Sincerely, John Smith; Best, Maria; Regards, Wolfgang |
| FUN-074 | Truncated / initials only | Heavy abbreviation | J. Smith, J.D.S., M.G.L., Dr. C., Sgt. M., J.S. |
| FUN-075 | With "née" / "born" | Maiden name marker | Sarah Chen (née Rodriguez), Mary Smith, born Mary Johnson |
| FUN-076 | Quoted nickname embedded | Formal + preferred | Robert "Bob" Smith, William "Bill" Jones, José "Pepe" Hernández |
| FUN-077 | With parenthesized translation | International doc | John Smith (ジョン・スミス), María García (玛丽亚·加西亚) |
| FUN-078 | Name list / multiple | Several names together | Smith, Chen, and Williams; the Garcia-Lopez family; Mike, Lisa, Tom, and Sarah |
| FUN-079 | Comma-separated multi-name | Database list | "Smith, John; Chen, Sarah; García, María" |
| FUN-080 | Masked / partial (initials) | Privacy-redacted | J. Smith, John S., S. Chen, J*** S***, M.G. (initials only) |
| FUN-081 | Masked with stars | Asterisk redaction | J*** Smith, John *****, **** García López, [Name Redacted] |
| FUN-082 | Anonymized placeholder | Standard generic | John Doe, Jane Doe, Pseudonym A, Subject 042, [PATIENT_NAME] |
| FUN-083 | Sentence-boundary tricky | Trailing punctuation | "Please contact John Smith.", "Was Sarah Chen there?", "María, please respond." |
| FUN-084 | Mid-sentence apposition | Comma-bounded inline | John Smith, the new hire, joined yesterday; Maria, our CMO, will speak |
| FUN-085 | Possessive form | With 's | John's email, Smith's office, García's report, Müller's analysis |
| FUN-086 | Plural / family form | "The X family" | the Smiths, the Garcías, the von Brauns, the O'Briens |
| FUN-087 | At line-start (greeting) | Salutation position | John Smith, Thank you for...; Maria García, Please... |
| FUN-088 | Adjacency-tight with email | Mashed with email | Sarah Chen<s.chen@corp.com>, <John Smith>jsmith@x.com |
| FUN-089 | Adjacency-tight with title | Mashed with title | Dr.Sarah Chen, Sr.John Smith Jr., MariaGarcíaPhD |
| FUN-090 | Adjacency-tight with ID | Mashed with ID | John Smith (EMP-4521), MariaGarcía/12345 |
| FUN-091 | Stage name / mononym | Single-name famous | Madonna, Beyoncé, Sting, Bono, Pelé, Adele, Banksy |
| FUN-092 | Religious / adopted name | Cultural conversion | Muhammad Ali (was Cassius Clay), Yusuf Islam (was Cat Stevens) |
| FUN-093 | With "aka" / "alias" | Multiple identity | John Smith, aka "Slim"; Maria García, alias "M. Lopez" |
| FUN-094 | Romanization variant | Spelling variants | José vs Jose, Müller vs Mueller, Smith vs Smyth |
| FUN-095 | Obfuscated / homoglyph | Look-alike chars | Jоhn Smіth (Cyrillic о, і), Magia Garcia (Latin M vs Cyrillic М) |
| FUN-096 | Anti-doxxing redaction | Privacy markers | J. D. (heavy redaction), [PATIENT 042], **REDACTED**, ANON_USER_4521 |
| FUN-097 | Legal pleading style | Court document format | Plaintiff John Smith, v. Defendant Maria García; Re: Smith, John (Petitioner) |
| FUN-098 | Medical record format | Clinical convention | Patient: Chen, Sarah; MRN: 47291; Pt. J. Smith, DOB 01/15/1985 |
| FUN-099 | Financial / KYC format | Bank format | Account holder: SMITH, JOHN A.; Beneficiary: María García-López |
| FUN-100 | "Mr./Mrs. + lastname only" | Surname-only address | Mr. Smith called; Ms. García sent; Dr. Müller approved |
| FUN-101 | Multilingual context label | "Name:" various languages | Name: John (EN), Nom: Marie (FR), 名前: 山田 (JP), Nombre: Juan (ES), Имя: Иван (RU) |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | FUN-049 to FUN-054 (l/1/I, O/0, rn/m, S/5/B/8, whitespace, diacritic-stripping) |
| Masked / partial / redacted | ✓ | FUN-080, FUN-081, FUN-082, FUN-096 |
| Multilingual context labels | ✓ | FUN-101 |
| Latin diacritics | ✓ | FUN-055 |
| Script variations | ✓ | FUN-020 to FUN-027, FUN-057 to FUN-060 (JP, ZH, KR, RU, HE, TH, GR) |
| Embedded in URL/email/path | ✓ | FUN-061, FUN-062, FUN-063, FUN-064 |
| In structured data | ✓ | FUN-065 to FUN-069 (JSON, KV, CSV, XML, log) |
| Adjacency-tight | ✓ | FUN-088, FUN-089, FUN-090 |
| Sentence-boundary tricky | ✓ | FUN-083, FUN-084 |
| Possessive form | ✓ | FUN-085 |
| Domain-embedded (medical/legal/financial) | ✓ | FUN-097, FUN-098, FUN-099 |
| Homoglyph / obfuscation | ✓ | FUN-095 |
| Case variations | ✓ | FUN-043, FUN-044, FUN-045, FUN-046, FUN-047, FUN-048 |

**Total patterns for Full_Name: 101**

---

## Entity 2: First_Given_Name

The given/first name component extracted independently. Triple-name rule: every Full_Name produces a corresponding First_Given_Name extraction.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| FGN-001 | Standard Western first | Common given name | John, Sarah, Michael, Emily, William, Jennifer |
| FGN-002 | Hyphenated first | Compound given | Jean-Pierre, Anne-Marie, María-José, Hans-Peter, Mary-Beth |
| FGN-003 | Multi-word first | Space, no hyphen | Mary Jane, Ana María, Jan Willem, Sarah Ellen |
| FGN-004 | Initial only | Single letter | J., M., S., W., R. |
| FGN-005 | Two-letter abbreviation | Doubled initial | J.D., M.A., W.E.B. (DuBois), A.P.J. (Kalam) |
| FGN-006 | Diminutive (English) | Standard short | Bob (Robert), Liz (Elizabeth), Jim (James), Pat (Patrick), Tony (Anthony) |
| FGN-007 | Diminutive (Slavic) | -sha/-enka style | Sasha (Alexander), Misha (Mikhail), Katya (Ekaterina), Volodya (Vladimir) |
| FGN-008 | Diminutive (Spanish) | -ito/-illo style | Paco (Francisco), Pepe (José), Lupe (Guadalupe), Beto (Roberto) |
| FGN-009 | Diminutive (Brazilian) | -inho/-zinho | Joãozinho, Mariazinha, Pedrinho, Aninha |
| FGN-010 | Religious compound (Maria + X) | Spanish religious | María del Carmen, María José, María Teresa, Anne-Marie |
| FGN-011 | Transliterated (CJK origin) | Romanized | Hiroshi, Yuki, Akira, Wei, Ming, Min-su, Ji-yeong |
| FGN-012 | Transliterated (Arabic origin) | Romanized | Mohammed, Fatima, Aisha, Khalid, Layla, Yusuf |
| FGN-013 | Transliterated (Slavic origin) | Romanized | Anastasia, Dmitri, Yelena, Olga, Pyotr, Yulia |
| FGN-014 | Transliterated (Indian origin) | Romanized | Priya, Rajesh, Anjali, Vikram, Lakshmi, Arjun |
| FGN-015 | Chinese given (Hanzi) | Chinese characters | 太郎, 明, 伟, 丽华, 建国, 静 |
| FGN-016 | Chinese given (pinyin with tones) | Tonal romanization | Tài Láng, Wěi, Lìhuá, Jìng |
| FGN-017 | Japanese given (Kanji) | Kanji | 太郎, 花子, 翔, 美咲, 健太 |
| FGN-018 | Japanese given (Hiragana) | Hiragana | たろう, はなこ, しょう, みさき |
| FGN-019 | Japanese given (Katakana) | Foreign-origin katakana | マイケル (Michael), ジョン (John), サラ (Sarah) |
| FGN-020 | Korean given (Hangul) | Hangul | 민수, 지영, 현우, 수진, 서연 |
| FGN-021 | Korean with romanization | Hangul + romanized | 민수 (Min-su), 지영 (Ji-yeong), 현우 (Hyeon-u) |
| FGN-022 | Arabic given | Arabic script | محمد, فاطمة, أحمد, نور, عائشة, خالد |
| FGN-023 | Hebrew given | Hebrew script | דוד, שרה, משה, רחל, יעקב, נועה |
| FGN-024 | Thai given | Thai script | สมชาย, สุภาพ, นิรันดร์, อัจฉรา, ปราณี |
| FGN-025 | Cyrillic given | Russian/Bulgarian/Serbian | Иван, Мария, Дмитрий, Анна, Сергей, Татьяна |
| FGN-026 | Greek given | Greek script | Γιώργος, Μαρία, Νικόλαος, Ελένη, Αλέξανδρος |
| FGN-027 | Devanagari given | Hindi script | राज, सीता, अमित, प्रिया, अर्जुन |
| FGN-028 | With Latin diacritics | Accented chars | René, François, José, Ángela, Łukasz, Søren, Žofie, Naïm |
| FGN-029 | OCR-distorted (l↔1↔I) | Character substitution | Mlchael, Wllliam, Marla, Phlllp |
| FGN-030 | OCR-distorted (O↔0) | Digit / letter confusion | J0hn, R0bert, M0nica, T0m |
| FGN-031 | OCR-distorted (rn↔m, cl↔d) | Ligature failures | Sarali (Sarah confused), Janne5 (James), Rlchard |
| FGN-032 | OCR-distorted (S↔5, B↔8) | Visual confusion | 5arah, 8rian, Ja5on, 5usan |
| FGN-033 | OCR-distorted (diacritic stripping) | Lost accents | Francois (was François), Soren (was Søren), Jose (was José) |
| FGN-034 | All-caps | Forms / official docs | JOHN, SARAH, MICHAEL, MARÍA |
| FGN-035 | All-lowercase | Informal / chat | john, sarah, michael, maria |
| FGN-036 | First-cap, rest lower | Standard prose | John, Sarah, María, Wolfgang |
| FGN-037 | First-letter lower (typo) | Lowercased name | john Smith, sarah chen, maria garcia |
| FGN-038 | Patronymic-derived given | From father's name | Ivanovich (Russian patronymic), Mikhailovich, Petrovich |
| FGN-039 | Gender-neutral | Cross-gender | Alex, Jordan, Taylor, Sam, Robin, Casey, Morgan, Devon |
| FGN-040 | Rare / unusual | Uncommon | Xylophone, Bluebell, Nirvana, Bear, Apple, North |
| FGN-041 | Biblical / classical | Religious / mythological | Solomon, Jezebel, Achilles, Athena, Magdalena, Gabriel |
| FGN-042 | Saint-derived | Religious name | Maria (Mary), Pedro (Peter), Pavel (Paul), Yusuf (Joseph) |
| FGN-043 | Geographical | Place-origin | Brittany, Florence, Jordan, Asia, Paris |
| FGN-044 | Day-of-week given | Named after day | Wednesday, Friday, Tuesday |
| FGN-045 | Virtue / quality | Concept name | Hope, Grace, Honor, Patience, Constance |
| FGN-046 | Embedded in email local-part | Inside email | john@corp.com → "john", sarah_chen@gmail.com → "sarah" |
| FGN-047 | Embedded in URL path | Inside URL | /users/sarah/, github.com/maria-dev, linkedin.com/in/john- |
| FGN-048 | Embedded in social handle | Inside @ handle | @sarah, @johndoe, @mariag |
| FGN-049 | Embedded in file path | Filesystem | /home/sarah/, C:\Users\John\, /tmp/maria_garcia |
| FGN-050 | JSON structured | Key + value | "first_name": "Sarah", "given_name": "John", "first": "Maria" |
| FGN-051 | Key-value pair | Form field | first_name=Sarah, Given Name: John, FIRST NAME: MARIA |
| FGN-052 | XML element | Markup tag | <first_name>Sarah</first_name>, <givenName>John</givenName> |
| FGN-053 | CSV column | In tabular data | "Smith","John","35"; "Chen","Sarah","Engineer" |
| FGN-054 | Adjacency-tight with surname | Mashed | JohnSmith, SarahChen, MariaGarcia |
| FGN-055 | Adjacency-tight with email | Inside email | sarahsmith@corp.com (first+last fused), john.smith → john |
| FGN-056 | Adjacency-tight with comma | No space after comma | "Smith,John", "García,María" |
| FGN-057 | Sentence-boundary tricky | Trailing punctuation | "Please call John.", "Was Sarah here?", "María, please respond." |
| FGN-058 | At start of greeting | Salutation | Sarah, Thank you...; Dear John, |
| FGN-059 | Possessive | First name with 's | John's email, Sarah's office, María's report |
| FGN-060 | Plural / family | "The X family" | the Sarahs in our class, the Johns of the world |
| FGN-061 | Name list / multiple | Several first names | John, Sarah, and María attended; Mike, Lisa, Tom, and Anna |
| FGN-062 | Masked / partial (initial only) | Single letter | J., S., M., W. |
| FGN-063 | Masked / partial (with stars) | Asterisk redaction | J***, Sa***, M****, [REDACTED] |
| FGN-064 | Anonymized placeholder | Standard placeholder | John, Jane, Pseudonym A, [FIRST_NAME], Subject 042 |
| FGN-065 | Multilingual context label | "First Name:" various | First Name (EN), Prénom (FR), Vorname (DE), Nombre (ES), 名 (JP), 이름 (KR), Имя (RU), 名 (ZH) |
| FGN-066 | Homoglyph attack | Look-alike chars | Jоhn (Cyrillic о), Sаrah (Cyrillic а), Marіа (mixed scripts) |
| FGN-067 | Compressed with honorific | No space after honorific | Dr.John, Mr.Sarah, Ms.María (no space) |
| FGN-068 | Voicemail / phone context | Transcribed speech | "Hi, this is John...", "Hello, Sarah here..." |
| FGN-069 | Chat message attribution | Speaker label | [14:32] Sarah: hey there; John > can you help? |
| FGN-070 | Medical chart attribution | Clinical context | "Pt: J. Smith", "Patient first name: Sarah" |
| FGN-071 | Legal pleading | Court format | I, John Smith, hereby declare...; Plaintiff: Sarah Chen |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | FGN-029 to FGN-033 |
| Masked / partial / redacted | ✓ | FGN-062, FGN-063, FGN-064 |
| Multilingual context labels | ✓ | FGN-065 |
| Script variations | ✓ | FGN-015 to FGN-027 (JP, ZH, KR, AR, HE, TH, RU, GR, Hindi) |
| Embedded in URL/email/path | ✓ | FGN-046 to FGN-049 |
| In structured data | ✓ | FGN-050 to FGN-053 |
| Adjacency-tight | ✓ | FGN-054, FGN-055, FGN-056, FGN-067 |
| Sentence-boundary tricky | ✓ | FGN-057 |
| Case variations | ✓ | FGN-034 to FGN-037 |
| Diacritics | ✓ | FGN-028 |
| Domain-embedded (medical/legal/chat) | ✓ | FGN-068, FGN-069, FGN-070, FGN-071 |
| Possessive | ✓ | FGN-059 |
| Homoglyph / obfuscation | ✓ | FGN-066 |

**Total patterns for First_Given_Name: 71**

---

## Entity 3: Last_Family_Name

Family / surname extracted independently. Highly culturally variable.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| LFN-001 | Standard Western | Single-word | Smith, Johnson, Williams, Brown, Davis, Wilson |
| LFN-002 | Hyphenated | Compound | Chen-Williams, Rodriguez-Garcia, Müller-Schmidt, Lloyd-Webber |
| LFN-003 | With Mc / Mac prefix | Scottish/Irish | McGregor, MacDonald, McCarthy, MacKenzie, Mc'Bride |
| LFN-004 | With O' prefix | Irish | O'Brien, O'Connor, O'Sullivan, O'Reilly, O'Hara |
| LFN-005 | With van / van der / van den | Dutch | van der Berg, van Beek, van den Hoek, van Zee |
| LFN-006 | With von / zu / von der | German | von Braun, von Bismarck, zu Guttenberg, von der Leyen |
| LFN-007 | With de / du / des | French | de Gaulle, du Pont, des Moulins, de la Cour |
| LFN-008 | With de la / de los / de las | Spanish | de la Cruz, de los Santos, de las Casas |
| LFN-009 | With al- / el- / ibn / bin | Arabic | al-Rashid, el-Sadat, ibn Saud, bin Laden, al-Husseini |
| LFN-010 | With bar / ben | Hebrew | bar-Kochba, ben-Gurion, ben-David |
| LFN-011 | With fitz | Norman-derived | Fitzgerald, Fitzpatrick, Fitzsimmons |
| LFN-012 | Patronymic -son endings | Scandinavian / English | Johansson, Andersson, Petersen, Hansen, Olsen, Robinson |
| LFN-013 | Patronymic -sen endings | Danish / Norwegian | Christiansen, Nielsen, Larsen, Petersen |
| LFN-014 | Patronymic -dóttir endings | Icelandic matronymic | Jónsdóttir, Eiríksdóttir, Þorvaldsdóttir |
| LFN-015 | Patronymic -ovich endings | Russian male | Ivanovich, Petrovich, Sidorovich |
| LFN-016 | Russian surname (Cyrillic, male) | Cyrillic | Иванов, Петров, Соколов, Кузнецов, Смирнов |
| LFN-017 | Russian surname (Cyrillic, female) | Gender suffix | Иванова, Петрова, Соколова, Кузнецова, Смирнова |
| LFN-018 | Russian surname (transliterated) | Romanized | Ivanov / Ivanova, Petrov / Petrova, Sokolov / Sokolova |
| LFN-019 | Polish surname (male) | -ski / -cki endings | Kowalski, Wiśniewski, Lewandowski, Kamiński |
| LFN-020 | Polish surname (female) | -ska / -cka variant | Kowalska, Wiśniewska, Lewandowska, Kamińska |
| LFN-021 | Czech / Slovak surname (male) | Standard form | Novák, Svoboda, Dvořák, Procházka |
| LFN-022 | Czech / Slovak surname (female) | -ová suffix | Nováková, Svobodová, Dvořáková, Procházková |
| LFN-023 | Japanese surname | Kanji | 山田, 田中, 佐藤, 鈴木, 高橋, 渡辺 |
| LFN-024 | Japanese with romanization | Kanji + romaji | 山田 (Yamada), 田中 (Tanaka), 佐藤 (Satō) |
| LFN-025 | Chinese surname (Hanzi) | Hanzi, precedes given | 王, 李, 张, 刘, 陈, 杨 |
| LFN-026 | Chinese surname (Traditional) | Traditional Hanzi | 王, 李, 張, 劉, 陳, 楊 |
| LFN-027 | Chinese surname (pinyin) | Romanized | Wang, Li, Zhang, Liu, Chen, Yang |
| LFN-028 | Korean surname | Hangul | 김, 이, 박, 정, 최, 강 |
| LFN-029 | Korean surname romanization | Romanized | Kim, Lee, Park, Jung, Choi, Kang |
| LFN-030 | Vietnamese surname | Vietnamese | Nguyễn, Trần, Lê, Phạm, Hoàng, Vũ |
| LFN-031 | Arabic surname | Arabic script | الرشيد, محمد, العبدالله, الحسن, الجابري |
| LFN-032 | Hebrew surname | Hebrew script | כהן, לוי, גולדברג, רוזנברג, פרץ |
| LFN-033 | Thai surname | Thai script | สุขสวัสดิ์, พิทักษ์กุล, ศรีสุข, รัตนวงศ์ |
| LFN-034 | Indian / South Asian surname | Caste / community markers | Sharma, Patel, Singh, Khan, Iyer, Reddy, Kapoor |
| LFN-035 | Spanish double surname | Paternal + maternal | García López, Rodríguez Fernández, Martínez Ruiz |
| LFN-036 | Portuguese double surname | Maternal + paternal | Santos Silva, Oliveira Costa, Almeida Pereira |
| LFN-037 | Brazilian double surname | Mom + Dad | Silva Santos, Costa Oliveira, Ferreira Almeida |
| LFN-038 | With apostrophe | Celtic / Italian | O'Brien, D'Angelo, Dell'Acqua, D'Souza, O'Connell |
| LFN-039 | With diacritics | Accented | Müller, Søren, Łukaszewski, Dvořák, Hämäläinen, Núñez, Cañón |
| LFN-040 | OCR-distorted (l↔1↔I) | Char substitution | Wll1iams, JohnsonI, Brown1ng, Sm1th |
| LFN-041 | OCR-distorted (O↔0) | Digit / letter confusion | Th0mpson, J0hnson, R0driguez, M00re |
| LFN-042 | OCR-distorted (rn↔m, cl↔d) | Ligature failures | Sirnpson (was Simpson), Wlllarns (was Williams) |
| LFN-043 | OCR-distorted (S↔5, B↔8) | Visual confusion | 5mith, 8rown, John5on, William5 |
| LFN-044 | OCR-distorted (whitespace) | Spacing errors | Mac Donald (split), VanDerBerg (lost spaces) |
| LFN-045 | OCR-distorted (diacritic stripping) | Lost accents | Muller (was Müller), Soren (was Søren), Garcia (was García) |
| LFN-046 | All-caps | Forms | SMITH, JOHNSON, GARCÍA, MÜLLER, NAGY |
| LFN-047 | All-lowercase | Informal | smith, johnson, müller, garcía |
| LFN-048 | First-cap only | Standard prose | Smith, García, Müller |
| LFN-049 | Inverted (Last, First) | Database format | Smith, John; García, María; Müller, Wolfgang |
| LFN-050 | Inverted with initials | Last, First M. | Smith, J. D.; García, M. C.; Müller, W. F. |
| LFN-051 | With generational suffix | Family suffix | Smith Jr., Rodriguez III, von Braun Sr., Johnson IV, González II |
| LFN-052 | Lowercase patronymic prefix | "van", "de", "von" lowercased | john van der berg, maria de la cruz |
| LFN-053 | Embedded in email local-part | Inside email | smith@corp.com, mgarcia@gmail.com, johnson_w@email.com |
| LFN-054 | Embedded in URL path | Inside URL | /users/smith/, github.com/garcia-dev, linkedin.com/in/john-smith |
| LFN-055 | Embedded in social handle | Inside @ | @smithj, @garcia_m, @müller |
| LFN-056 | Embedded in file path | Filesystem | /home/smith/, C:\Users\Garcia\, /var/log/wilson.log |
| LFN-057 | JSON structured | Key + value | "last_name": "Smith", "family_name": "García", "surname": "Müller" |
| LFN-058 | Key-value pair | Form field | last_name=Smith, Family Name: García, SURNAME: MÜLLER |
| LFN-059 | XML element | Markup tag | <last_name>Smith</last_name>, <familyName>García</familyName> |
| LFN-060 | CSV column | Tabular data | "Smith","John"; "García","María" |
| LFN-061 | Adjacency-tight with first | No space | JohnSmith, SarahChen, MaríaGarcía |
| LFN-062 | Adjacency-tight with email | Mashed | sarahjohnson@corp.com (no separator) |
| LFN-063 | Adjacency-tight with ID | Mashed | Smith/EMP-4521, García_12345 |
| LFN-064 | Sentence-boundary tricky | Trailing punctuation | "Please contact Smith.", "Was García there?" |
| LFN-065 | Possessive form | With 's | Smith's office, García's report, Müller's analysis, Jones's case |
| LFN-066 | Plural / family | "The Xs" | the Smiths, the Garcías, the von Brauns, the O'Briens |
| LFN-067 | Masked / partial (initial) | Single letter | S. (for Smith), G. (for García), M. (for Müller) |
| LFN-068 | Masked / partial (stars) | Asterisk redaction | S**** (Smith), J***, [LAST_NAME], **** García |
| LFN-069 | Anonymized placeholder | Standard placeholder | Doe (Jane/John Doe), Smith (generic), Pseudonym B |
| LFN-070 | Multilingual context label | Various languages | Last Name (EN), Nom de famille (FR), Familienname (DE), Apellido (ES), 姓 (JP), 성 (KR), Фамилия (RU) |
| LFN-071 | Homoglyph attack | Look-alike chars | Smіth (Cyrillic і), Mаrtinez (Cyrillic а) |
| LFN-072 | Medical record format | Clinical convention | Pt: Chen, Sarah; Smith, J. (DOB 01/15/1985) |
| LFN-073 | Legal pleading | Court format | v. Smith, et al.; Smith, plaintiff; García, defendant |
| LFN-074 | Financial / KYC format | Bank format | Account holder: SMITH, JOHN A.; Beneficiary: MARÍA GARCÍA-LÓPEZ |
| LFN-075 | Single-mononym usage | Famous one-name | Pelé, Madonna, Beyoncé (no family name used) |
| LFN-076 | Compound place-based | "Of X" / "from X" | of York (royalty), from Nazareth (historical) |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | LFN-040 to LFN-045 |
| Masked / partial / redacted | ✓ | LFN-067, LFN-068, LFN-069 |
| Multilingual context labels | ✓ | LFN-070 |
| Script variations | ✓ | LFN-023 to LFN-033 (JP, ZH, KR, VI, AR, HE, TH, Hindi-related) |
| Embedded in URL/email/path | ✓ | LFN-053 to LFN-056 |
| In structured data | ✓ | LFN-057 to LFN-060 |
| Adjacency-tight | ✓ | LFN-061, LFN-062, LFN-063 |
| Sentence-boundary tricky | ✓ | LFN-064 |
| Case variations | ✓ | LFN-046, LFN-047, LFN-048 |
| Diacritics | ✓ | LFN-039 |
| Domain-embedded (medical/legal/financial) | ✓ | LFN-072, LFN-073, LFN-074 |
| Possessive | ✓ | LFN-065 |
| Homoglyph / obfuscation | ✓ | LFN-071 |

**Total patterns for Last_Family_Name: 76**

---

## Entity 4: Preferred_Name

Nicknames, aliases, pen names, stage names, gamer tags, chosen names, gender-affirming names.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PFN-001 | Common nickname (English) | Shortened legal | Bob (Robert), Bill (William), Liz (Elizabeth), Dick (Richard), Mike (Michael) |
| PFN-002 | Slavic diminutive | Endearing form | Sasha (Alexander), Misha (Mikhail), Katya (Ekaterina), Volodya (Vladimir) |
| PFN-003 | Spanish diminutive | -ito / -illo / -cito | Paco (Francisco), Pepe (José), Lupe (Guadalupe), Beto (Roberto) |
| PFN-004 | Brazilian diminutive | -inho / -zinho | Joãozinho, Mariazinha, Aninha, Pedrinho |
| PFN-005 | Italian diminutive | -ino / -etto / -uccio | Toto (Salvatore), Tonino (Antonio), Beppe (Giuseppe) |
| PFN-006 | French diminutive | -et / -ot / -ou | Tonton (uncle/Antoine), Jojo (Joseph) |
| PFN-007 | Unrelated nickname | Not derived from legal | Buddy, Slim, Red, Tiger, Cookie, Ace, Doc, Lucky |
| PFN-008 | Stage / pen name | Pseudonym | Mark Twain, Lady Gaga, Banksy, Sting, Bono, Pelé, George Eliot |
| PFN-009 | Quoted preferred | Marked typographically | Robert "Bob" Smith, William "Bill" Jones, José "Pepe" Hernández |
| PFN-010 | "Aka" / "Also known as" | Explicit indicator | aka Bob, also known as "The Professor", goes by Liz, a/k/a Sarah |
| PFN-011 | Religious / spiritual name | Cultural conversion | Muhammad Ali (was Cassius Clay), Yusuf Islam (was Cat Stevens), Brother Aaron |
| PFN-012 | Maiden name marker | Née | Sarah Chen (née Rodriguez), Mary Smith (née Johnson), Hillary Clinton (née Rodham) |
| PFN-013 | Married name marker | Born + married | born Mary Williams (now Smith), formerly Smith |
| PFN-014 | Gender-affirming chosen name | Chosen vs birth | preferred name: Alex, chosen name: Maya (legal name redacted) |
| PFN-015 | Online handle / gamertag | Internet pseudonym | @darknight99, xXProGamerXx, PixelQueen, u/throwaway42 |
| PFN-016 | Discord-style #1234 | Username + numeric tag | johndoe#1234, sarah_x#5678, gamer42#9012 |
| PFN-017 | Reddit u/ handle | u/username | u/sarah_chen, u/throwaway42, u/anon_user_99 |
| PFN-018 | Forum / BBS handle | Internet-era nickname | DarkLord42, xX_Sniper_Xx, MoonlightSonata |
| PFN-019 | Twitter/X @ handle | Social handle | @JohnDoe, @SarahChen, @maria_dev, @TheRealJohnSmith |
| PFN-020 | Instagram @ handle | Social handle | @john.doe, @sarah_chen_official, @maria.dev |
| PFN-021 | TikTok @ handle | Social handle | @johndoe_tt, @sarah.tiktok, @therealmaria |
| PFN-022 | Twitch handle | Streaming name | TheRealJohn, SarahPlaysGames, mariastreams |
| PFN-023 | Anonymous placeholder | Standard generic | Anonymous, Anon, John Doe, Jane Doe |
| PFN-024 | Pen name (single mononym) | One-word | Madonna, Sting, Cher, Beyoncé, Pink, Bono |
| PFN-025 | Cultural mononym | Single name | Sukarno, Suharto, Pelé, Ronaldinho |
| PFN-026 | Non-Latin script nickname | In native script | あだ名: たろちゃん (JP), 别名: 小明 (ZH), 별명: 미니 (KR) |
| PFN-027 | Roman transliteration of native | Romanized preferred | Yuki (preferred over 雪), Wei (over 伟), Min (over 민수) |
| PFN-028 | Diminutive with diacritics | Accented short form | Café (nickname), Søsø (Søren), François as "Fanfan" |
| PFN-029 | Childhood / family-only | Family-only name | what mom called him: Bubba; always Sissy at home |
| PFN-030 | Work-only nickname | Professional informal | Goes by Doc in the office; Everyone calls her Coach |
| PFN-031 | Sports nickname | Athletic / team | Magic Johnson, The Rock, Iron Mike, Air Jordan |
| PFN-032 | Military callsign | Aviation / radio | Maverick, Goose, Iceman, Mongoose |
| PFN-033 | Mafia / criminal alias | Underworld | "Lucky" Luciano, "Bugsy" Siegel, "Scarface" |
| PFN-034 | Compound preferred | Multi-word | Big John, Little Sarah, The Boss, Mr. T, Crazy Eddie |
| PFN-035 | In structured data | JSON, KV | "preferred_name": "Bob", nickname=Liz, "preferred":"Alex" |
| PFN-036 | Key-value pair (forms) | Form field | Nickname: Bob, Preferred Name: Alex, Goes by: Liz |
| PFN-037 | Multilingual labels | Various languages | Preferred Name (EN), Nom préféré (FR), Spitzname (DE), Apodo (ES), Soprannome (IT), あだ名 (JP), 별명 (KR), Прозвище (RU) |
| PFN-038 | Embedded in profile URL | Inside URL | linkedin.com/in/the-real-john, github.com/awesomesarah, twitch.tv/proGamer42 |
| PFN-039 | Masked / partial | Privacy-redacted | preferred: B*** (Bob), known as [REDACTED], preferred name omitted |
| PFN-040 | Pronoun-only reference | Indirect | the one we call Tiger, his Discord handle, her stage name |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | N/A | Preferred names rarely scanned; chosen / digital-native |
| Masked / partial / redacted | ✓ | PFN-039 |
| Multilingual context labels | ✓ | PFN-037 |
| Script variations | ✓ | PFN-026, PFN-027 |
| Embedded in URL/email/path | ✓ | PFN-019 to PFN-022, PFN-038 |
| In structured data | ✓ | PFN-035, PFN-036 |
| Adjacency-tight | N/A | Preferred names typically introduced explicitly with quotes or "aka" |
| Sentence-boundary tricky | N/A | Covered under Full_Name patterns |
| Case variations | N/A | Preferred names don't have meaningful case variants |
| Diacritics | ✓ | PFN-028 |

**Total patterns for Preferred_Name: 40**

---

## Entity 5: Business_Title

Job title, professional role, organizational rank, academic position, military rank.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| BT-001 | C-suite executive | Top leadership | CEO, CFO, CTO, COO, CISO, CMO, CHRO, CDO, CRO |
| BT-002 | C-suite full form | Spelled out | Chief Executive Officer, Chief Financial Officer, Chief Technology Officer |
| BT-003 | President / Founder | Top leadership variants | President, Co-Founder, Founder, Founding Partner, Managing Partner |
| BT-004 | VP / SVP / EVP / AVP | Vice president levels | VP, SVP, EVP, AVP, Senior Vice President, Executive Vice President |
| BT-005 | Director levels | Standard director hierarchy | Director, Senior Director, Managing Director, Executive Director |
| BT-006 | Manager levels | Manager hierarchy | Manager, Senior Manager, Group Manager, Program Manager, Project Manager |
| BT-007 | Engineer levels | Tech career ladder | Engineer, Senior Engineer, Staff Engineer, Principal Engineer, Distinguished Engineer |
| BT-008 | Engineer with level / band | Tech ladder + level | Software Engineer L4, Senior Engineer L5, Staff Engineer L6, Principal L7 |
| BT-009 | Architect levels | Tech architect | Solutions Architect, Senior Architect, Principal Architect, Chief Architect |
| BT-010 | Analyst levels | Business analyst | Analyst, Senior Analyst, Lead Analyst, Principal Analyst |
| BT-011 | Lead / Team Lead | Technical leadership | Team Lead, Tech Lead, Engineering Lead, Lead Developer |
| BT-012 | Specialist roles | Specialist hierarchy | Specialist, Senior Specialist, Subject Matter Expert (SME) |
| BT-013 | Consultant roles | Advisory roles | Consultant, Senior Consultant, Principal Consultant, Partner |
| BT-014 | Coordinator / Administrator | Support roles | Coordinator, Administrator, Office Manager, Executive Assistant |
| BT-015 | Sales roles | Sales hierarchy | Sales Representative, Account Executive, Account Manager, Regional Sales Director |
| BT-016 | Marketing roles | Marketing | Marketing Coordinator, Brand Manager, Product Marketing Manager |
| BT-017 | HR roles | Human resources | HR Generalist, HR Business Partner, Talent Acquisition Manager, CHRO |
| BT-018 | Finance roles | Accounting / finance | Accountant, Controller, Treasurer, FP&A Manager, CFO |
| BT-019 | Academic professor levels | Tenure track | Assistant Professor, Associate Professor, Full Professor, Distinguished Professor, Professor Emeritus |
| BT-020 | Academic non-faculty | Research / teaching | Postdoc, Research Fellow, Lecturer, Adjunct Professor, Visiting Scholar |
| BT-021 | Academic leadership | Administration | Dean, Provost, Chancellor, Department Chair, President of the University |
| BT-022 | Medical attending levels | Hospital hierarchy | Attending Physician, Chief Resident, Resident, Fellow, Intern |
| BT-023 | Medical specialists | Specialty titles | Surgeon, Anesthesiologist, Pediatrician, Cardiologist, Neurologist |
| BT-024 | Nursing roles | Nursing hierarchy | RN (Registered Nurse), LPN, Nurse Practitioner, Chief Nursing Officer |
| BT-025 | Allied health | Other clinical | Physical Therapist, Occupational Therapist, Pharmacist, Lab Technician |
| BT-026 | Legal — law firm | Partner track | Partner, Senior Associate, Associate, Of Counsel, Counsel |
| BT-027 | Legal — courts | Judiciary | Judge, Chief Justice, Magistrate, Justice of the Peace |
| BT-028 | Legal — practice areas | Specialization | Criminal Defense Attorney, Corporate Counsel, Intellectual Property Lawyer |
| BT-029 | Military rank — officer | Commissioned | Lieutenant, Captain, Major, Colonel, General, Admiral, Brigadier |
| BT-030 | Military rank — enlisted | NCO / enlisted | Sergeant, Corporal, Sergeant Major, Master Sergeant, Petty Officer |
| BT-031 | Military rank — abbreviated | Short form | Sgt., Cpl., Lt., Col., Cpt., Maj., MSgt., 2Lt. |
| BT-032 | Government — executive branch | Federal / state | Secretary of State, Attorney General, Director of FBI, Cabinet Secretary |
| BT-033 | Government — legislative | Elected | Senator, Representative, Congressman, Speaker, Whip, Minority Leader |
| BT-034 | Government — local | Municipal | Mayor, City Council Member, Alderman, Commissioner, County Clerk |
| BT-035 | Government — diplomatic | Foreign service | Ambassador, Consul, Attaché, Deputy Chief of Mission |
| BT-036 | Religious clergy | Religious roles | Pastor, Priest, Rabbi, Imam, Minister, Bishop, Cardinal, Pope, Reverend |
| BT-037 | Religious — monastic | Monastic life | Monk, Nun, Brother, Sister, Abbot, Mother Superior |
| BT-038 | Freelance / contract | Non-employee | Freelancer, Independent Contractor, Consultant, Advisor, 1099 |
| BT-039 | Entry-level / trainee | Beginning roles | Intern, Summer Intern, Apprentice, Graduate Trainee, Trainee, Junior Analyst |
| BT-040 | Founder / entrepreneur | Self-employed | Founder, Co-Founder, Entrepreneur, Owner, Solo Practitioner |
| BT-041 | Board roles | Governance | Board Member, Chairman, Chairwoman, Chair of the Board, Director (board) |
| BT-042 | Title with department | Role + dept | Head of Engineering, Director of Sales EMEA, VP of Marketing |
| BT-043 | Title with region | Role + geography | EMEA Sales Director, APAC Marketing Lead, US Regional Manager |
| BT-044 | Title with function | Role + function | Software Engineer, Backend Developer, Mobile Developer, Frontend Developer |
| BT-045 | Title with vendor / tech | Tech-specific | Salesforce Administrator, AWS Solutions Architect, Anonymous Institution Developer |
| BT-046 | Hyphenated title | Combined roles | Player-Coach, Developer-Designer, Owner-Operator, CEO-Founder, Author-Editor |
| BT-047 | Title with honorific | Combined | Dr. Sarah Chen, Chief Medical Officer; Prof. Mueller, Dean |
| BT-048 | Title with credentials suffix | Title + cert | John Smith, PMP-certified Project Manager; Sarah Chen, CISSP, CISO |
| BT-049 | Acting / Interim title | Temporary role | Acting CEO, Interim CFO, Acting Director, Temporary VP |
| BT-050 | Former / past title | Historical reference | former CEO, ex-CFO, retired General, past President |
| BT-051 | German title | German | Geschäftsführer, Abteilungsleiter, Vorstand, Personalleiter, Sachbearbeiter |
| BT-052 | French title | French | Directeur Général, Chef de Projet, Ingénieur Principal, Responsable RH, Cadre |
| BT-053 | Italian title | Italian | Amministratore Delegato, Direttore Tecnico, Responsabile, Capo Reparto |
| BT-054 | Spanish title | Spanish | Director General, Gerente, Jefe de Ventas, Coordinador, Subgerente |
| BT-055 | Brazilian Portuguese title | Portuguese (BR) | Diretor Executivo, Gerente de Projetos, Engenheiro Sênior, Coordenador |
| BT-056 | Japanese title (Kanji) | Japanese | 社長 (President), 部長 (Department Head), 課長 (Section Chief), 取締役 (Director) |
| BT-057 | Korean title (Hangul) | Korean | 대표이사 (CEO), 부장 (Department Head), 과장 (Section Chief), 팀장 (Team Lead) |
| BT-058 | Chinese title (Hanzi) | Chinese | 总经理 (General Manager), 董事长 (Chairman), 工程师 (Engineer), 主任 (Director) |
| BT-059 | Russian title (Cyrillic) | Russian | Генеральный директор, Руководитель проекта, Старший инженер, Менеджер |
| BT-060 | Arabic title | Arabic | مدير عام (General Manager), رئيس مجلس الإدارة (Chairman), مدير المشروع |
| BT-061 | Hebrew title | Hebrew | מנכ"ל (CEO), סמנכ"ל (VP), מנהל אגף, ראש צוות |
| BT-062 | Nordic titles | Scandinavian | VD (CEO Swedish), Adm. dir. (NO/DK), Toimitusjohtaja (Finnish) |
| BT-063 | Dutch title | Dutch | Directeur, Afdelingshoofd, Projectleider, Hoofdingenieur |
| BT-064 | Polish title | Polish | Dyrektor, Kierownik, Inżynier, Specjalista, Prezes |
| BT-065 | Turkish title | Turkish | Genel Müdür, Departman Müdürü, Kıdemli Mühendis, Yönetici |
| BT-066 | Thai title | Thai | ผู้จัดการทั่วไป, ผู้อำนวยการ, วิศวกรอาวุโส |
| BT-067 | All-caps | ALL CAPS form | CEO, CFO, MANAGER, SENIOR ENGINEER, DIRECTOR OF SALES |
| BT-068 | All-lowercase | Casual / informal | ceo, senior engineer, director, manager |
| BT-069 | OCR-distorted (l↔1↔I) | Character errors | Manaqer (Manager), Dlrector (Director), V1ce President |
| BT-070 | OCR-distorted (O↔0) | Digit / letter | CE0, CT0, C00, Dlrect0r |
| BT-071 | OCR-distorted (general) | Mixed errors | Pr0ject Lead, Senlor Engineer, MaIIager, V1ce-Presideilt |
| BT-072 | With diacritics | Accented | Président, Directeur Général, Geschäftsführer, Régisseur |
| BT-073 | Embedded in email signature | Signature block | Sarah Chen, CMO | Acme Corp; Best, John Smith, Senior Engineer |
| BT-074 | Embedded in URL | Inside URL | linkedin.com/in/john-smith-cmo, jobs.acme.com/senior-engineer |
| BT-075 | JSON structured | Key + value | "title": "Senior Engineer", "job_title": "Director", "position": "Manager" |
| BT-076 | Key-value pair | Form field | Title: Director, Job Title: Senior Engineer, POSITION: VP SALES |
| BT-077 | XML element | Markup tag | <title>CEO</title>, <jobTitle>Senior Engineer</jobTitle> |
| BT-078 | CSV column | Tabular data | "Smith,John,35,CEO"; "García,María,42,VP Sales" |
| BT-079 | Adjacency-tight with name | Mashed | Sarah Chen,CMO; Dr.JohnSmith,MD; MariaGarcíaVP |
| BT-080 | Adjacency-tight with ID | Mashed | EMP4521/Director; EmpID:123,Mgr |
| BT-081 | Email signature with phone | Multi-line | Sarah Chen, CMO | Acme Corp, +1-555-1234 |
| BT-082 | Sentence-boundary tricky | Trailing punctuation | "She's the new CEO.", "Was he the Director?" |
| BT-083 | Multiple titles list | Several roles | CEO and Founder, CMO/CFO, President & CEO, Director, Engineering and Operations |
| BT-084 | Masked / partial | Redacted | Senior [REDACTED], Director of ***, [TITLE], position omitted |
| BT-085 | Multilingual context label | Various languages | Title (EN), Titre (FR), Berufsbezeichnung (DE), Cargo (ES/PT), Titolo (IT), 役職 (JP), 직책 (KR), Должность (RU) |
| BT-086 | Contract / legal doc | Formal binding | John Smith, in his capacity as Chief Executive Officer; Sarah Chen, herein the "Director" |
| BT-087 | Possessive | With 's | the CEO's office, the Director's report, the Manager's review |
| BT-088 | Homoglyph attack | Look-alike chars | CΕO (Greek Ε), Dіrector (Cyrillic і), Maпager (Cyrillic п) |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | BT-069, BT-070, BT-071 |
| Masked / partial / redacted | ✓ | BT-084 |
| Multilingual context labels | ✓ | BT-085 |
| Script variations | ✓ | BT-056 to BT-061, BT-066 (JP, KR, ZH, RU, AR, HE, Thai) |
| Embedded in URL/email/path | ✓ | BT-073, BT-074, BT-081 |
| In structured data | ✓ | BT-075, BT-076, BT-077, BT-078 |
| Adjacency-tight | ✓ | BT-079, BT-080 |
| Sentence-boundary tricky | ✓ | BT-082 |
| Case variations | ✓ | BT-067, BT-068 |
| Diacritics | ✓ | BT-072 |
| Domain-embedded (contract/email) | ✓ | BT-086 |
| Possessive | ✓ | BT-087 |
| Homoglyph / obfuscation | ✓ | BT-088 |

**Total patterns for Business_Title: 88**

---

## Entity 6: Address_Work

Business / office addresses. Country-specific formatting conventions vary dramatically. Often appears in email signatures, contact cards, official correspondence, and business filings.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| AW-001 | US standard single-line | Street, Suite, City, State ZIP | 100 Park Avenue, Suite 1200, New York, NY 10017 |
| AW-002 | US standard multi-line | Multi-line format | 100 Park Avenue\nSuite 1200\nNew York, NY 10017 |
| AW-003 | US with ZIP+4 | Extended ZIP | 100 Park Avenue, New York, NY 10017-1234 |
| AW-004 | US PO Box | Post Office Box | P.O. Box 7890, Wilmington, DE 19899 |
| AW-005 | US PMB (Private Mailbox) | Mail-forwarding service | 123 Main St #PMB 456, Anytown, CA 90210 |
| AW-006 | US APO/FPO/DPO military | Military address | Unit 2050 Box 4190, APO AP 96278-2050; PSC 1234 Box 5678, FPO AE 09498 |
| AW-007 | US with attention line | ATTN: addressee | ATTN: Sarah Chen, 100 Park Avenue, Suite 1200, New York, NY 10017 |
| AW-008 | US with c/o | Care of | c/o Acme Corp, 100 Park Avenue, New York, NY 10017 |
| AW-009 | UK standard | Building, Street, City, Postcode | 25 Bank Street, Canary Wharf, London E14 5JP |
| AW-010 | UK with county | With county name | 1 The Crescent, Sheffield, South Yorkshire, S2 4XF |
| AW-011 | UK without comma after street | Compact UK | 25 Bank Street Canary Wharf London E14 5JP |
| AW-012 | German standard | Straße Nr, PLZ Stadt | Friedrichstraße 43-45, 10117 Berlin |
| AW-013 | German with district | Plus Bezirk/Stadtteil | Friedrichstraße 43, 10117 Berlin-Mitte |
| AW-014 | German with country | DE prefix | Friedrichstraße 43, D-10117 Berlin |
| AW-015 | French standard | N° Rue, CP Ville | 12 Rue de Rivoli, 75001 Paris |
| AW-016 | French with arrondissement | Numbered district | 12 Rue de Rivoli, 75001 Paris, 1er arrondissement |
| AW-017 | French CEDEX | Business postal routing | 35 Rue du Commerce, 75015 PARIS CEDEX 15 |
| AW-018 | Italian standard | Via/Piazza Nr, CAP Città | Via Roma 42, 00184 Roma (RM) |
| AW-019 | Italian with province code | Two-letter province | Via Garibaldi 10, 20121 Milano (MI) |
| AW-020 | Spanish standard | Calle/Avenida Nr, CP Ciudad | Calle Gran Vía 28, Planta 5, 28013 Madrid |
| AW-021 | Spanish with province | Plus province | Calle Mayor 5, 41001 Sevilla (Sevilla) |
| AW-022 | Brazilian standard | Rua Nr, Bairro, CEP Cidade-UF | Av. Paulista 1578, Bela Vista, 01310-200 São Paulo-SP |
| AW-023 | Brazilian with complemento | Plus apt/floor | Av. Paulista 1578, conj. 1502, Bela Vista, 01310-200 São Paulo-SP |
| AW-024 | Brazilian CEP format | With dash in CEP | Rua das Flores 123, 04567-001 São Paulo, SP |
| AW-025 | Japanese standard | 〒Postal, Pref, City, District | 〒100-8111 東京都千代田区千代田1-1 |
| AW-026 | Japanese romaji | Romanized | 1-1 Chiyoda, Chiyoda-ku, Tokyo 100-8111 |
| AW-027 | Japanese with building | Building name appended | 〒100-0005 東京都千代田区丸の内2-7-2 JPタワー |
| AW-028 | Dutch standard | Straat Nr, Postcode Stad | Herengracht 420, 1017 BZ Amsterdam |
| AW-029 | Dutch with house letter | Number + letter | Herengracht 420A, 1017 BZ Amsterdam |
| AW-030 | Swedish standard | Gata Nr, Postnummer Stad | Storgatan 15, 111 51 Stockholm |
| AW-031 | Swedish with c/o | "Att:" addressee | Storgatan 15, 4 tr, 111 51 Stockholm; Att: Sarah Chen |
| AW-032 | Finnish standard | Katu Nr, Postinumero Kaupunki | Mannerheimintie 5, 00100 Helsinki |
| AW-033 | Czech standard | Ulice číslo, PSČ Město | Václavské náměstí 1, 110 00 Praha 1 |
| AW-034 | Czech with district number | District suffix | Wenceslas Square 1, 110 00 Prague 1 |
| AW-035 | Polish standard | ul. Ulica Nr, Kod Miasto | ul. Marszałkowska 42, 00-024 Warszawa |
| AW-036 | Polish abbreviations | "ul.", "al.", "pl." | al. Jerozolimskie 65, 00-697 Warszawa; pl. Wolności 1, 50-071 Wrocław |
| AW-037 | Hungarian standard | Város, Utca szám, Irányítószám | Budapest, Andrássy út 60, 1062 |
| AW-038 | Hungarian (postcode first) | Postcode-first variant | 1062 Budapest, Andrássy út 60 |
| AW-039 | Russian standard | Город, Улица, дом Nr, Индекс | г. Москва, ул. Тверская, д. 13, 125009 |
| AW-040 | Russian abbreviated | ул., д., кв. | ул. Ленина, д. 15, оф. 401, 191025 СПб |
| AW-041 | Russian transliterated | Romanized | g. Moscow, ul. Tverskaya, d. 13, 125009 |
| AW-042 | Korean standard | 시/도 구/시 동 번지 우편번호 | 서울특별시 강남구 테헤란로 152, 06236 |
| AW-043 | Korean new road-based | Doromyeong system | 서울특별시 종로구 종로 1, 03154 |
| AW-044 | Chinese standard (Mainland) | 省市区街道号 邮编 | 北京市朝阳区建国路93号, 100022 |
| AW-045 | Chinese with building | Plus 大厦/楼 | 上海市浦东新区世纪大道100号 上海环球金融中心, 200120 |
| AW-046 | Taiwan address | Same components, Traditional | 台北市信義區市府路45號, 11008 |
| AW-047 | Hong Kong address | English-Chinese mix | 8 Connaught Place, Central, Hong Kong |
| AW-048 | Arabic UAE (RTL) | Right-to-left format | شارع الشيخ زايد، صندوق بريد 12345، دبي، الإمارات العربية المتحدة |
| AW-049 | Arabic Saudi Arabia | Saudi format | شارع الملك فهد، الرياض 11564، المملكة العربية السعودية |
| AW-050 | Turkish standard | Cadde/Sokak No, PK İlçe/İl | Bağdat Caddesi No:42, 34710 Kadıköy/İstanbul |
| AW-051 | Turkish with mahalle | With neighborhood | Atatürk Mah., Cumhuriyet Cad. No:15, 06100 Çankaya/Ankara |
| AW-052 | Norwegian standard | Gate Nr, Postnummer Sted | Karl Johans gate 22, 0159 Oslo |
| AW-053 | Danish standard | Vej Nr, Postnr By | Strøget 12, 1160 København K |
| AW-054 | Hebrew (RTL) | Right-to-left | רחוב רוטשילד 1, תל אביב 6688101 |
| AW-055 | Hebrew with floor | Plus floor | רחוב הרצל 50, קומה 12, תל אביב 6423906 |
| AW-056 | Thai standard | Thai address | 123 ถนนสุขุมวิท แขวงคลองตัน เขตคลองเตย กรุงเทพฯ 10110 |
| AW-057 | Indian standard | Building/Plot, Area, City, State, PIN | 5th Floor, Tower B, DLF Cyber City, Gurugram, Haryana 122002 |
| AW-058 | Indian with PIN code | 6-digit PIN | 42 MG Road, Bengaluru, Karnataka 560001 |
| AW-059 | Canadian standard | Street, City, Province + Postal | 100 King Street West, Suite 4400, Toronto, ON M5X 1B1 |
| AW-060 | Mexican standard | Calle, Col., CP Ciudad, Estado | Av. Reforma 250, Col. Juárez, 06600 CDMX |
| AW-061 | Australian standard | Street, Suburb, State Postcode | 1 Macquarie Place, Sydney, NSW 2000 |
| AW-062 | Singapore standard | Block-Unit, Street, Singapore Postal | 1 Marina Bay Sands, Singapore 018971 |
| AW-063 | Floor / Suite indicator (Eng) | Suite/Floor markers | Suite 400, Floor 12, Ste. 200, 5F |
| AW-064 | Floor / Suite indicator (multilingual) | Various languages | Etage 3 (FR), 3. OG (DE), 5階 (JP), 3piso (PT/BR), 3층 (KR) |
| AW-065 | Business park / campus | Named complex | Building C, TechPark Dublin; Block 3, Hong Kong Science Park |
| AW-066 | Business park with suite | Plus internal address | Park Avenue Tower, Building 4, Suite 1200 |
| AW-067 | Diplomatic mission | Embassy / consulate | Embassy of the United States, 24 Grosvenor Square, London W1A 1AE |
| AW-068 | Government agency | Federal/state office | 1600 Pennsylvania Avenue NW, Washington, DC 20500 |
| AW-069 | Coworking space | WeWork / Regus style | WeWork 100 Park Ave, 4th Floor, New York, NY 10017 |
| AW-070 | Virtual office / mail forwarding | No physical presence | Mailing address only: 100 Park Avenue, Suite 1200, New York, NY 10017 |
| AW-071 | Address with phone | Full contact line | Acme Corp, 100 Park Ave, NY 10017 | +1-555-1234 |
| AW-072 | Address in email signature | Multi-line signature | Sarah Chen\nAcme Corp\n100 Park Ave, Suite 1200\nNew York, NY 10017 |
| AW-073 | Address with website | Plus URL | 100 Park Avenue, New York, NY 10017 | www.acme.com |
| AW-074 | Address in JSON | Structured | {"street": "100 Park Ave", "city": "New York", "state": "NY", "zip": "10017"} |
| AW-075 | Address in key-value | Form fields | street=100 Park Ave\ncity=New York\nstate=NY\nzip=10017 |
| AW-076 | Address as XML | Markup | <address><street>100 Park Ave</street><city>New York</city></address> |
| AW-077 | Single-string CSV | Comma-separated | "100 Park Ave, Suite 1200, New York, NY, 10017" |
| AW-078 | OCR-distorted (digits/letters) | Char substitution | 1OO Park Avenue (O for 0), Sulte 12OO, New Y0rk, NY 1OO17 |
| AW-079 | OCR-distorted (street name) | Mangled street | Frledrichstraße 43, 1O117 BerIln (Friedrichstraße, 10117 Berlin) |
| AW-080 | OCR-distorted whitespace | Lost / extra spaces | 100ParkAvenue,Suite1200,NewYork; 100  Park  Avenue (doubled spaces) |
| AW-081 | OCR-distorted (diacritic stripping) | Lost accents | Rue de l'Hopital (was Hôpital), Calle Bilbao (lost accent), Munchen (was München) |
| AW-082 | Abbreviated (Eng street types) | Common abbreviations | 100 Park Ave, 25 Bank St, 200 Main Blvd, 50 Oak Rd, 75 Pine Ln |
| AW-083 | Abbreviated state name | 2-letter state | Springfield, IL; Portland, OR; Cambridge, MA |
| AW-084 | Full state name spelled | No abbreviation | Springfield, Illinois 62704 |
| AW-085 | All-caps address | Forms / labels | 100 PARK AVENUE, SUITE 1200, NEW YORK, NY 10017 |
| AW-086 | All-lowercase address | Informal | 100 park avenue, suite 1200, new york, ny 10017 |
| AW-087 | Mixed case (typo) | Inconsistent | 100 park Avenue, suite 1200, NEW york, ny 10017 |
| AW-088 | Numeric-only address | Address as numbers only | 12345 (ZIP only), or "Address: 100" (street # alone) |
| AW-089 | Address with parenthetical landmark | Plus reference | 100 Park Ave (near Grand Central), New York, NY 10017 |
| AW-090 | Building name alone | Named building no street | The Empire State Building, New York, NY 10118 |
| AW-091 | Embassy address | Plus country | 24 Grosvenor Square, London W1A 1AE, United Kingdom |
| AW-092 | Hospital address | Plus department | City General Hospital, 100 Hospital Way, Boston, MA 02115, Cardiology Department |
| AW-093 | University address | Plus department | MIT, 77 Massachusetts Avenue, Cambridge, MA 02139, Department of Computer Science |
| AW-094 | Address with cross-street | "Corner of X & Y" | 100 Park Ave at 41st Street, New York, NY 10017 |
| AW-095 | GPS-augmented address | Lat/long alternative | 100 Park Ave, NYC (40.7536° N, 73.9806° W) |
| AW-096 | Masked / partial address | Privacy-redacted | 100 *** Avenue, ****** , NY 10017; XXX Park Ave, [REDACTED] |
| AW-097 | Anonymized placeholder | Standard generic | 123 Main Street, Anytown, USA; [BUSINESS ADDRESS] |
| AW-098 | Address adjacency-tight | No separators | 100ParkAve,NewYorkNY10017; FriedrichStr43,10117Berlin |
| AW-099 | Multilingual context label | "Address:" various langs | Address (EN), Adresse (FR/DE), Indirizzo (IT), Dirección (ES), Endereço (PT), 住所 (JP), 주소 (KR), Адрес (RU), Adres (TR), כתובת (HE), العنوان (AR) |
| AW-100 | Address with delivery instructions | Plus routing | 100 Park Ave, Suite 1200, New York, NY 10017 (Loading dock entrance, north side) |
| AW-101 | Country code on its own line | Multi-line international | 100 Park Avenue\nNew York, NY 10017\nUSA |
| AW-102 | Address sentence-boundary | Trailing punctuation | "Mail to 100 Park Avenue, New York, NY 10017.", "Was it 100 Park Ave?" |
| AW-103 | Embedded in URL | Inside URL | google.com/maps?q=100+Park+Ave+New+York+NY+10017 |
| AW-104 | Sub-building / unit notation | Various conventions | Office 302, Room 4B, Apt #5, Suite #1200, Unit-7C |
| AW-105 | Coworking address (full) | Full convention | "WeWork @ 100 Park Ave, Suite 1200, NYC" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | AW-078, AW-079, AW-080, AW-081 |
| Masked / partial / redacted | ✓ | AW-096, AW-097 |
| Multilingual context labels | ✓ | AW-099 |
| Latin diacritics | ✓ | AW-015, AW-022, AW-052, AW-053 |
| Script variations | ✓ | AW-025, AW-042, AW-044, AW-046, AW-048, AW-054, AW-056 (JP, KR, ZH, AR, HE, TH) |
| Embedded in URL/email/path | ✓ | AW-103 |
| In structured data | ✓ | AW-074, AW-075, AW-076, AW-077 |
| Adjacency-tight | ✓ | AW-098, AW-105 |
| Sentence-boundary tricky | ✓ | AW-102 |
| Case variations | ✓ | AW-085, AW-086, AW-087 |
| Country-specific format coverage | ✓ | AW-001 through AW-062 (US, UK, DE, FR, IT, ES, BR, JP, NL, SE, FI, CZ, PL, HU, RU, KR, ZH-CN, ZH-TW, HK, AR-UAE, AR-KSA, TR, NO, DK, HE, TH, IN, CA, MX, AU, SG) |
| Domain-embedded (hospital/embassy/university) | ✓ | AW-067, AW-068, AW-091, AW-092, AW-093 |
| Special formats (PO Box, military, c/o) | ✓ | AW-004, AW-005, AW-006, AW-007, AW-008 |

**Total patterns for Address_Work: 105**

---

## Entity 7: Address_Personal

Residential / home addresses. Same country formats as Work but with residential indicators (apartment/flat numbers, c/o, rural routes).

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| AP-001 | US residential standard | Standard home | 742 Evergreen Terrace, Springfield, IL 62704 |
| AP-002 | US residential with apartment | Apt/Unit included | 742 Evergreen Terrace, Apt 4B, Springfield, IL 62704 |
| AP-003 | US with #unit | Hash-marked unit | 742 Evergreen Terrace #4B, Springfield, IL 62704 |
| AP-004 | US rural route | RR/HC numbering | RR 2, Box 145, Smithville, IL 62000 |
| AP-005 | US Highway Contract route | HC + box | HC 1 Box 28, Pine Grove, KY 40000 |
| AP-006 | US star route | Star Rt | Star Rt Box 250, Mountainside, CO 80000 |
| AP-007 | US trailer park / mobile home | MHC / Lot | Lot 42, Sunset Mobile Home Park, Phoenix, AZ 85000 |
| AP-008 | US dormitory / college | Campus + room | 100 College Ave, Smith Hall Room 304, Cambridge, MA 02139 |
| AP-009 | UK residential | UK home + postcode | 4 Privet Drive, Little Whinging, Surrey GU1 1AA |
| AP-010 | UK flat | Flat + house number | Flat 12, 221B Baker Street, London NW1 6XE |
| AP-011 | UK with floor | Plus floor number | Flat 3, 1st Floor, 25 Bank Street, London E14 5JP |
| AP-012 | UK terraced house number | Just number + street | 10 Downing Street, London SW1A 2AA |
| AP-013 | German residential | Plus Wohnung/Stockwerk | Berliner Straße 42, 3. OG links, 10715 Berlin |
| AP-014 | German with hinten/vorne | Front/back unit | Schillerstr. 5 HH (Hinterhaus), 60313 Frankfurt |
| AP-015 | French residential | Appartement/Étage | 15 Rue des Fleurs, Appt. 3B, 75015 Paris |
| AP-016 | French with bâtiment | Building reference | 15 Rue des Fleurs, Bâtiment A, Appt. 5, 75015 Paris |
| AP-017 | French rural / lieu-dit | Place-name only | Lieu-dit "Les Chênes", 24530 Saint-Jean-de-Côle |
| AP-018 | Italian residential | Interno/Scala | Via Garibaldi 10, Interno 5, Scala B, 00153 Roma (RM) |
| AP-019 | Italian with palazzina | Building block | Via Roma 42, Palazzina C, Int. 12, 00184 Roma |
| AP-020 | Spanish residential | Piso/Puerta | Calle Mayor 12, 3º Izq, 28013 Madrid |
| AP-021 | Spanish with bloque | Multi-block | Calle Castellana 100, Bloque A, 3º D, 28046 Madrid |
| AP-022 | Brazilian residential | Apto/Bloco | Rua das Flores 123, Apto 501, Bloco B, 04567-001 São Paulo-SP |
| AP-023 | Brazilian with condomínio | Gated community | Rua das Acácias 50, Condomínio Vila Verde, Casa 12, Granja Viana, 06710-000 |
| AP-024 | Brazilian fundos | Back unit | Rua Augusta 100, Fundos, 01304-000 São Paulo-SP |
| AP-025 | Japanese residential | Apt unit | 東京都新宿区西新宿2-8-1 マンション301号室 |
| AP-026 | Japanese with apartment name | Apt building + room | 東京都渋谷区代々木1-2-3 サンシャイン代々木 502号室 |
| AP-027 | Japanese rural | 番地 + village | 〒999-1234 山形県西村山郡朝日町大字○○123番地 |
| AP-028 | Dutch residential | Verdieping | Keizersgracht 174-II, 1015 DG Amsterdam |
| AP-029 | Dutch with house letter | Number + letter | Prinsengracht 263A, 1016 GV Amsterdam |
| AP-030 | Swedish residential | Lägenhet | Storgatan 5, lgh 1201, 111 51 Stockholm |
| AP-031 | Swedish c/o | "Att:" addressee | Att: Erik Andersson, Storgatan 5 lgh 1201, 111 51 Stockholm |
| AP-032 | Finnish residential | As Oy + huoneisto | As Oy Päivänkukka, Kukkakatu 5 A 12, 00100 Helsinki |
| AP-033 | Czech residential | Block + unit | Šlikova 12/345, byt č. 5, 169 00 Praha 6 |
| AP-034 | Polish residential | ul. + mieszkanie | ul. Marszałkowska 42 m. 5, 00-024 Warszawa |
| AP-035 | Hungarian residential | Plus emelet/ajtó | Budapest, Andrássy út 60, 3. emelet 5. ajtó, 1062 |
| AP-036 | Russian residential | кв. (apartment) | ул. Ленина, д. 15, кв. 42, г. Санкт-Петербург, 191025 |
| AP-037 | Russian with корпус | Building number | ул. Тверская, д. 8, корп. 2, кв. 53, Москва 125009 |
| AP-038 | Korean residential | 아파트 단지 | 서울특별시 서초구 반포대로 201 아크로리버파크 103동 1501호 |
| AP-039 | Korean villa / townhouse | Lower density | 서울특별시 마포구 합정동 123-45 빌라 2층 |
| AP-040 | Chinese residential | Community/Bldg/Room | 上海市浦东新区陆家嘴环路1000号 恒生大厦 2301室 |
| AP-041 | Chinese xiaoqu | Residential compound | 北京市朝阳区望京西路11号 望京小区3号楼2单元501室 |
| AP-042 | Arabic residential | شقة (apartment) | شقة 5، عمارة 12، شارع النيل، القاهرة |
| AP-043 | Arabic with floor | Plus floor | الطابق الثالث، شقة 5، عمارة 12، شارع النيل، القاهرة |
| AP-044 | Hebrew residential | RTL with apt | רחוב הרצל 50, דירה 5, קומה 3, תל אביב 6423906 |
| AP-045 | Thai residential | Plus unit | 123 หมู่ 5 ถนนพระราม 9 แขวงห้วยขวาง เขตห้วยขวาง กรุงเทพฯ 10310 |
| AP-046 | Thai with moo/village | Plus หมู่ | 45 หมู่ 3 ตำบลบ้านดอน อำเภอเมือง จังหวัดสุพรรณบุรี 72000 |
| AP-047 | Indian residential | Multi-component | Flat 3B, Tower 2, DLF Cyber City Apartments, Gurugram, Haryana 122002 |
| AP-048 | Indian colony/society | Society name | A-12 Vasant Vihar, New Delhi 110057 |
| AP-049 | Turkish residential | Mahalle + daire | Atatürk Mah., Cumhuriyet Cad. No:15 D:3, 06100 Çankaya/Ankara |
| AP-050 | Norwegian residential | Standard format | Karl Johans gate 22, 4. etg, 0159 Oslo |
| AP-051 | Danish residential | st./th./mf. | Strøget 12, 3. th., 1160 København K |
| AP-052 | Canadian residential | Unit + street | 4400-100 King Street West, Toronto, ON M5X 1B1 |
| AP-053 | Mexican residential | Plus interior | Av. Reforma 250, Int. 5, Col. Juárez, 06600 CDMX |
| AP-054 | Australian residential | Unit number prefix | 4/100 George Street, Sydney NSW 2000 |
| AP-055 | c/o personal address | Care of | c/o John Smith, 742 Evergreen Terrace, Apt 4B, Springfield, IL 62704 |
| AP-056 | PO Box (residential) | Personal P.O. Box | P.O. Box 1234, Springfield, IL 62701 |
| AP-057 | General Delivery | US Post Office hold | General Delivery, Smithville, KS 67000 |
| AP-058 | Diplomatic / embassy residence | Plus country code | 24 Embassy Row, Washington DC 20008 (Embassy of Japan staff residence) |
| AP-059 | Shelter / transitional housing | Special address | Salvation Army Shelter, 100 Hope Lane, City, State ZIP |
| AP-060 | Address with house name (UK) | Named house | "The Old Vicarage", Vicarage Lane, Lower Tilling, Sussex BN26 6AA |
| AP-061 | Address with floor + building | Multi-component | Tower 2, 5th Floor, Apt 502, Marina Heights, Dubai Marina |
| AP-062 | Address with parenthetical | Inline reference | 742 Evergreen Terrace (the yellow house), Springfield, IL 62704 |
| AP-063 | Address with directions | Plus orientation | 742 Evergreen Terrace (3rd house on left from the corner), Springfield, IL |
| AP-064 | Address in JSON (personal) | Structured | {"home_address": "742 Evergreen Terrace, Apt 4B", "city": "Springfield"} |
| AP-065 | Address in KV (personal) | Form fields | home_street=742 Evergreen Terrace\nhome_apt=4B\nhome_city=Springfield |
| AP-066 | Address XML (personal) | Markup | <home><street>742 Evergreen Terrace</street><apt>4B</apt></home> |
| AP-067 | OCR-distorted personal | Char substitution | 742 EvergreenTerrace,Apt48 (was 4B), Sprlngfield, lL 62704 |
| AP-068 | OCR diacritic stripping (personal) | Lost accents | Sao Paulo (was São Paulo), Munchen (was München) |
| AP-069 | Abbreviated street type (personal) | Common abbreviations | 742 Evergreen Ter, 4 Privet Dr, 50 Oak Rd, 25 Pine Ln |
| AP-070 | All-caps (personal) | Forms / labels | 742 EVERGREEN TERRACE, APT 4B, SPRINGFIELD, IL 62704 |
| AP-071 | All-lowercase (personal) | Informal | 742 evergreen terrace, apt 4b, springfield, il 62704 |
| AP-072 | Masked / partial (personal) | Privacy-redacted | 742 *** Terrace, Apt 4B, ****field, IL 627**; XXX Evergreen Ter |
| AP-073 | Anonymized placeholder (personal) | Standard generic | 123 Main Street, Anytown, USA; [HOME ADDRESS REDACTED]; Sample Address |
| AP-074 | Sentence-boundary tricky | Trailing punctuation | "Sent to 742 Evergreen Terrace, Apt 4B.", "Is it 742 Evergreen?" |
| AP-075 | Personal address adjacency-tight | No separators | 742EvergreenTerrace,Apt4B,Springfield,IL62704 |
| AP-076 | Multilingual context label | "Home Address:" various | Home Address (EN), Adresse personnelle (FR), Wohnanschrift (DE), Endereço residencial (PT-BR), 自宅住所 (JP), 자택 주소 (KR), Домашний адрес (RU) |
| AP-077 | Address change notice | "Previous:"/"New:" | Previous Address: 100 Old St, New York, NY; New Address: 742 Evergreen Terrace |
| AP-078 | Forwarding address | Mail-forward | Forwarding to: 742 Evergreen Terrace, Apt 4B, Springfield, IL 62704 |
| AP-079 | Hospital / care facility (personal) | Patient residence | Patient address: City General Hospital, Room 502, 100 Hospital Way |
| AP-080 | Multi-residence (multiple homes) | Primary + secondary | Primary: 742 Evergreen Terrace, Springfield; Secondary: Beach House, 50 Ocean Dr |
| AP-081 | Mailing vs physical | Distinct addresses | Mailing: P.O. Box 1234; Physical: 742 Evergreen Terrace |
| AP-082 | Adjacency with name (form line) | Name + address mashed | "John Smith,742 Evergreen,Apt 4B,Springfield IL 62704" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | AP-067, AP-068 |
| Masked / partial / redacted | ✓ | AP-072, AP-073 |
| Multilingual context labels | ✓ | AP-076 |
| Latin diacritics | ✓ | AP-015, AP-022, AP-068 |
| Script variations | ✓ | AP-025–AP-027, AP-038–AP-041, AP-042–AP-046 (JP, KR, ZH, AR, HE, TH) |
| Embedded in URL/email/path | N/A | Residential addresses rarely embedded in URLs (less common than Work) |
| In structured data | ✓ | AP-064, AP-065, AP-066 |
| Adjacency-tight | ✓ | AP-075, AP-082 |
| Sentence-boundary tricky | ✓ | AP-074 |
| Case variations | ✓ | AP-070, AP-071 |
| Country-specific format coverage | ✓ | AP-001 through AP-054 (US, UK, DE, FR, IT, ES, BR, JP, NL, SE, FI, CZ, PL, HU, RU, KR, ZH, AR, HE, TH, IN, TR, NO, DK, CA, MX, AU) |
| Special formats (rural, dorm, shelter, c/o, PO Box) | ✓ | AP-004 to AP-008, AP-055, AP-056, AP-057, AP-059 |
| Multi-residence / change notice | ✓ | AP-077, AP-078, AP-080, AP-081 |

**Total patterns for Address_Personal: 82**

---

## Entity 8: Telephone_Numbers_Work

Business / office phone numbers. Country-specific formats. Often appears in email signatures, contact cards, business filings. Includes fax numbers.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| TW-001 | US E.164 | + country format | +1 (212) 555-0100, +1 212 555 0100 |
| TW-002 | US (XXX) XXX-XXXX | Parenthesized area code | (212) 555-0100 |
| TW-003 | US XXX-XXX-XXXX | Dash-separated | 212-555-0100 |
| TW-004 | US XXX.XXX.XXXX | Dot-separated | 212.555.0100 |
| TW-005 | US XXX XXX XXXX | Space-separated | 212 555 0100 |
| TW-006 | US 1-XXX-XXX-XXXX | With leading 1 | 1-212-555-0100, 1-800-555-0199 |
| TW-007 | US no separators | Digits only | 2125550100 |
| TW-008 | US toll-free | 800/888/877/866/855/844/833 | 1-800-555-0199, 1-888-555-0123, +1-877-COMCAST |
| TW-009 | US vanity number | Letters in number | 1-800-FLOWERS, 1-888-NEW-CARS, 1-866-MY-APPLE |
| TW-010 | US with extension | Number + ext | +1 (212) 555-0100 ext. 4321, 212-555-0100 x4321, 212.555.0100 Ext 432 |
| TW-011 | UK E.164 | International | +44 20 7946 0958 |
| TW-012 | UK local format | National | 020 7946 0958, 020-7946-0958 |
| TW-013 | UK with prefix abbreviation | "Tel:" / "T:" | Tel: 020 7946 0958, T: +44 20 7946 0958 |
| TW-014 | German E.164 | International | +49 30 12345678 |
| TW-015 | German local | National | 030 12345678, 030/12345-678, (030) 12345 678 |
| TW-016 | German with slash | DE separator | 030/12345-678 (slash + dash combo) |
| TW-017 | French E.164 | International | +33 1 42 68 53 00 |
| TW-018 | French local | National | 01 42 68 53 00, 01.42.68.53.00 |
| TW-019 | Italian E.164 | International | +39 06 6982 1000, +39 02 8901 2345 |
| TW-020 | Italian local | National | 06 6982 1000, 02 89012345 |
| TW-021 | Spanish E.164 | International | +34 915 555 000 |
| TW-022 | Spanish local | National | 915 555 000, 91 555 50 00 |
| TW-023 | Brazilian E.164 | International | +55 11 3456-7890 |
| TW-024 | Brazilian local | National | (11) 3456-7890, 011 3456 7890 |
| TW-025 | Japanese E.164 | International | +81 3-5555-0192 |
| TW-026 | Japanese local | National | 03-5555-0192, 03-5555-0192 |
| TW-027 | Japanese with brackets | With (0) for national | +81(0)3-5555-0192 |
| TW-028 | Dutch E.164 | International | +31 20 123 4567 |
| TW-029 | Dutch local | National | 020 123 4567, 020-1234567 |
| TW-030 | Swedish E.164 | International | +46 8 555 123 45 |
| TW-031 | Swedish local | National | 08-555 123 45, 08 555 12 345 |
| TW-032 | Finnish E.164 | International | +358 9 123 4567 |
| TW-033 | Finnish local | National | (09) 123 4567, 09-1234567 |
| TW-034 | Czech E.164 | International | +420 221 234 567 |
| TW-035 | Czech local | National | 221 234 567, 221-234-567 |
| TW-036 | Israeli E.164 | International | +972 3-555-0100 |
| TW-037 | Israeli local | National | 03-5550100, 03-555-0100 |
| TW-038 | Hungarian E.164 | International | +36 1 234 5678 |
| TW-039 | Hungarian local | National | 06 1 234 5678, (1) 234 5678 |
| TW-040 | Korean E.164 | International | +82 2-1234-5678 |
| TW-041 | Korean local | National | 02-1234-5678, 02-1234-5678 |
| TW-042 | Norwegian E.164 | International | +47 22 12 34 56 |
| TW-043 | Norwegian local | National | 22 12 34 56, 22-12-34-56 |
| TW-044 | Polish E.164 | International | +48 22 123 45 67 |
| TW-045 | Polish local | National | 22 123 45 67, (22) 123-45-67 |
| TW-046 | Russian E.164 | International | +7 495 123-45-67 |
| TW-047 | Russian local | National | 8 (495) 123-45-67, (495) 123-45-67 |
| TW-048 | Chinese E.164 | International | +86 10-6555-1234 |
| TW-049 | Chinese local | National | 010-6555-1234, 010 6555 1234 |
| TW-050 | UAE E.164 | International | +971 4 555 1234 |
| TW-051 | Saudi Arabia E.164 | International | +966 11 234 5678 |
| TW-052 | Turkish E.164 | International | +90 212 555 12 34 |
| TW-053 | Turkish local | National | 0212 555 12 34, (212) 555-1234 |
| TW-054 | Thai E.164 | International | +66 2 1234 5678 |
| TW-055 | Thai local | National | 02 1234 5678, 02-123-4567 |
| TW-056 | Danish E.164 | International | +45 33 12 34 56 |
| TW-057 | Danish local | National | 33 12 34 56, 33-12-34-56 |
| TW-058 | Portuguese (EU) E.164 | International | +351 21 123 4567 |
| TW-059 | Portuguese (EU) local | National | 21 123 4567 |
| TW-060 | Canadian E.164 | Same as US format | +1 (416) 555-1234, 416-555-1234 |
| TW-061 | Australian E.164 | International | +61 2 9374 4000 |
| TW-062 | Indian E.164 | International | +91 22 1234 5678 |
| TW-063 | Indian local with STD | National | 022 1234 5678, 022-1234-5678 |
| TW-064 | Mexican E.164 | International | +52 55 1234 5678 |
| TW-065 | Singapore E.164 | International | +65 6123 4567 |
| TW-066 | UK toll-free 0800 | National toll-free | 0800 123 4567 |
| TW-067 | German toll-free 0800 | National toll-free | 0800 123 4567 |
| TW-068 | French toll-free 0800 | National toll-free | 0800 12 34 56 |
| TW-069 | Premium-rate (US 900) | Pay-per-call | 1-900-555-1234 |
| TW-070 | Premium-rate (UK 0871) | Higher charge | 0871 234 5678 |
| TW-071 | Internal corporate short dial | 4–5 digit | Dial 5-4321, x2345, #1234, ext 432 |
| TW-072 | Direct inward dial (DID) | Direct number | DID: +1-212-555-0142, Direct: 212-555-0142 |
| TW-073 | Operator-assisted | Switchboard | Main: +1-212-555-0100; Switchboard, then ext 4321 |
| TW-074 | Fax number | Explicitly labeled fax | Fax: +1 (212) 555-0101, Fax: +49 30 12345679, télécopieur: 01 42 68 53 01 |
| TW-075 | Multiple numbers in line | Phone + fax | Tel: 212-555-0100 | Fax: 212-555-0101 |
| TW-076 | Voicemail context | Plus voicemail | +1-212-555-0100 (voicemail) |
| TW-077 | Number with country label | Plus country abbrev | 212-555-0100 (USA), +49 30 12345 (DE) |
| TW-078 | Phone in JSON | Structured | "phone": "+1-212-555-0100", "work_phone": "212-555-0100" |
| TW-079 | Phone in key-value | Form fields | phone=212-555-0100, Work Phone: +1 212 555 0100 |
| TW-080 | Phone in XML | Markup | <phone>+1 (212) 555-0100</phone>, <workPhone type="office">212-555-0100</workPhone> |
| TW-081 | Phone in CSV | Tabular | "Sarah Chen","CMO","+1-212-555-0100" |
| TW-082 | Phone in email signature | Multi-line | Sarah Chen, CMO\nAcme Corp\n+1 (212) 555-0100 | sarah@acme.com |
| TW-083 | OCR-distorted phone | Digit confusion | +1 (Z12) 555-O1OO (Z for 2, O for 0); (Z1Z) 555-OlOO |
| TW-084 | OCR-distorted separators | Lost / wrong separators | (212)5550100 (lost spaces), 212.555-0100 (mixed), 212 555 -0100 |
| TW-085 | OCR-distorted whitespace | Spacing errors | +1212 555 0100 (lost space after +1), +1  (212)  555-0100 (doubled) |
| TW-086 | Phone written out | Verbalized | "two-one-two five-five-five oh-one-hundred" |
| TW-087 | Masked / partial phone | Privacy-redacted | (212) ***-****, +1-XXX-XXX-0100, +1-212-555-**** |
| TW-088 | Phone ending in X | Reference to number | "the line ending in 0100", "your number ending in 1234" |
| TW-089 | Anonymized phone placeholder | Standard generic | (555) 123-4567 (TV placeholder), +1-555-0100 |
| TW-090 | Sentence-boundary tricky | Trailing punctuation | "Call me at +1 (212) 555-0100.", "Was the number 212-555-0100?" |
| TW-091 | Adjacency-tight with name | No separator | Sarah Chen+1-212-555-0100, John Smith212-555-0100 |
| TW-092 | Adjacency-tight with email | No separator | sarah@acme.com+1-212-555-0100 |
| TW-093 | Multilingual context label | "Phone:" various | Phone (EN), Téléphone / Tél. (FR), Telefon (DE), Teléfono (ES/IT), 電話 (JP), 전화 (KR), Телефон (RU), Telefon (TR), טלפון (HE), هاتف (AR) |
| TW-094 | "Mobile" vs "Office" labels | Type indicators | Office: +1 (212) 555-0100, Mobile: +1 (917) 555-0123, Tel: +44 20 7946 0958 |
| TW-095 | "Direct" vs "Main" labels | Reach type | Direct: +1-212-555-0142; Main: +1-212-555-0100 |
| TW-096 | Phone with operating hours | Business hours appended | +1 (212) 555-0100 (Mon-Fri 9am-5pm ET) |
| TW-097 | International with country name | Plus full country | +1 (212) 555-0100, United States; +49 30 12345, Germany |
| TW-098 | E.164 strict | No separators ever | +12125550100, +442079460958 |
| TW-099 | tel: URI scheme | Click-to-call link | tel:+12125550100, <a href="tel:+1-212-555-0100">Call us</a> |
| TW-100 | callto: URI scheme | Skype-style | callto:+12125550100 |
| TW-101 | Conference call format | Plus access code | +1-212-555-0100, access code: 123 456 789# |
| TW-102 | Multiple separated phones | List with semicolons | +1-212-555-0100; +1-917-555-0123; +44 20 7946 0958 |
| TW-103 | Phone in domain (geo TLD) | Country TLD context | +1-212-555-0100 (.com), +49-30-12345-678 (.de) |
| TW-104 | Phone with TTY/TDD | Disability service | TTY: +1 (212) 555-0500, TDD: 1-800-555-0500 |
| TW-105 | Phone with extension hyphenated | x42, ext-42 | +1-212-555-0100x42, 212-555-0100-ext-42 |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | TW-083, TW-084, TW-085 |
| Masked / partial / redacted | ✓ | TW-087, TW-088, TW-089 |
| Multilingual context labels | ✓ | TW-093 |
| Country-specific format coverage | ✓ | TW-001 through TW-065 (US, UK, DE, FR, IT, ES, BR, JP, NL, SE, FI, CZ, HE, HU, KR, NO, PL, RU, ZH, AR-UAE, AR-KSA, TR, TH, DK, PT, CA, AU, IN, MX, SG) |
| Embedded in URL/path | ✓ | TW-099, TW-100 (tel:, callto:) |
| In structured data | ✓ | TW-078, TW-079, TW-080, TW-081 |
| Adjacency-tight | ✓ | TW-091, TW-092 |
| Sentence-boundary tricky | ✓ | TW-090 |
| Domain-embedded (email signature) | ✓ | TW-082 |
| Special formats (vanity, toll-free, premium, TTY) | ✓ | TW-008, TW-009, TW-066, TW-067, TW-068, TW-069, TW-070, TW-104 |
| Fax number | ✓ | TW-074, TW-075 |
| Extension formats | ✓ | TW-010, TW-105 |
| Verbalized / written out | ✓ | TW-086 |

**Total patterns for Telephone_Numbers_Work: 105**

---

## Entity 9: Telephone_Numbers_Personal

Personal / mobile phone numbers. All work phone country formats apply; this entity emphasizes mobile prefixes and messaging-app contexts.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| TP-001 | US/Canada mobile (no distinction) | All 10-digit | +1 (917) 555-0123, +1 415 555 0142, (646) 555-0199 |
| TP-002 | UK mobile prefix 07XXX | UK mobile | +44 7700 900123, 07700 900123, 07-7000-9001-23 |
| TP-003 | German mobile 01XX | DE mobile prefix | +49 151 12345678, 0151 12345678, 0177 1234567 |
| TP-004 | French mobile 06/07 | FR mobile | +33 6 12 34 56 78, 06 12 34 56 78, +33 7 89 12 34 56 |
| TP-005 | Italian mobile 3XX | IT mobile | +39 320 1234567, 320 1234567, +39 347 9876543 |
| TP-006 | Spanish mobile 6XX/7XX | ES mobile | +34 612 345 678, 612 345 678, +34 700 123 456 |
| TP-007 | Brazilian mobile 9 prefix | BR mobile (9-digit local) | +55 11 98765-4321, (11) 98765-4321 |
| TP-008 | Japanese mobile 090/080/070 | JP mobile | +81 90-1234-5678, 090-1234-5678, 080-9876-5432, 070-1111-2222 |
| TP-009 | Dutch mobile 06 | NL mobile | +31 6 12345678, 06-12345678 |
| TP-010 | Swedish mobile 07X | SE mobile | +46 70 123 45 67, 070-123 45 67, 073 555 12 34 |
| TP-011 | Finnish mobile 04/05 | FI mobile | +358 40 123 4567, 040 1234567, 050 123 4567 |
| TP-012 | Czech mobile 6XX/7XX | CZ mobile | +420 602 123 456, 602 123 456 |
| TP-013 | Israeli mobile 05X | IL mobile | +972 50-123-4567, 050-123-4567, 052-987-6543 |
| TP-014 | Hungarian mobile 06 20/30/70 | HU mobile | +36 20 123 4567, 06-20-123-4567 |
| TP-015 | Korean mobile 010 | KR mobile | +82 10-1234-5678, 010-1234-5678 |
| TP-016 | Norwegian mobile 4XX/9XX | NO mobile | +47 412 34 567, 412 34 567 |
| TP-017 | Polish mobile 5XX/6XX/7XX/8XX | PL mobile | +48 600 123 456, 600 123 456 |
| TP-018 | Russian mobile 9XX | RU mobile | +7 916 123-45-67, 8 916 1234567 |
| TP-019 | Chinese mobile 1XX | CN mobile | +86 138 0013 8000, 138-0013-8000 |
| TP-020 | UAE mobile 50/54/55/56 | UAE mobile | +971 50 123 4567, 050 123 4567 |
| TP-021 | Saudi mobile 5XX | KSA mobile | +966 50 123 4567, 050 123 4567 |
| TP-022 | Turkish mobile 5XX | TR mobile | +90 532 123 45 67, 0532-123-4567 |
| TP-023 | Thai mobile 06/08/09 | TH mobile | +66 81 234 5678, 081-234-5678, 089 876 5432 |
| TP-024 | Danish mobile (no prefix) | DK 8-digit | +45 20 12 34 56, 20-12-34-56 |
| TP-025 | Portuguese mobile 9X | PT mobile | +351 91 234 5678, 91 234 5678, 93 555 1234 |
| TP-026 | Australian mobile 04XX | AU mobile | +61 4 1234 5678, 0411 234 567 |
| TP-027 | Indian mobile 9XXX/8XXX/7XXX/6XXX | IN mobile | +91 98765 43210, 98765 43210, 9876543210 |
| TP-028 | Singapore mobile 8XXX/9XXX | SG mobile | +65 9123 4567, 9123 4567 |
| TP-029 | Mexican mobile (no special prefix) | MX 10-digit | +52 1 55 1234 5678, 55-1234-5678 |
| TP-030 | WhatsApp context | App-specific | WhatsApp: +55 11 98765-4321; chat me on WhatsApp at +44 7700 900123 |
| TP-031 | Telegram context | App-specific | Telegram: +1-415-555-0123; @username on Telegram |
| TP-032 | Signal context | App-specific | Signal: +1-555-123-4567 |
| TP-033 | iMessage / FaceTime | Apple context | iMessage: +1-415-555-0123, FaceTime: +44 7700 900123 |
| TP-034 | SMS shortcode | Messaging short | Text HELP to 741741 (crisis hotline), SMS 12345, Text "JOIN" to 80008 |
| TP-035 | "Mobile:" / "Cell:" label | Type indicator | Mobile: +1 (917) 555-0123, Cell: +1-415-555-0142, Cellphone: 09-8765-4321 |
| TP-036 | "Home:" label (landline) | Landline indicator | Home: +1 (212) 555-0177 (personal landline) |
| TP-037 | Mobile with "(M)" / "(c)" | Inline marker | +1-917-555-0123 (M), 020-7946-0958 (c) |
| TP-038 | Voicemail-specific | Voicemail context | Mobile voicemail: +1 (917) 555-0123, leave message |
| TP-039 | All work phone formats | Same separators | (See TW-001 through TW-065 — all country formats apply) |
| TP-040 | Personal phone in email signature | Multi-line | Sarah Chen | Mobile: +1 (917) 555-0123 | sarah.chen@email.com |
| TP-041 | Personal phone in JSON | Structured | "mobile": "+1-917-555-0123", "personal_phone": "+1-917-555-0123" |
| TP-042 | Personal phone in KV | Form field | mobile=+1-917-555-0123, Personal Phone: +1 (917) 555-0123 |
| TP-043 | Personal phone XML | Markup | <mobile>+1-917-555-0123</mobile>, <phone type="personal">+1-917-555-0123</phone> |
| TP-044 | OCR-distorted personal | Digit confusion | +l (Z17) 555-O1Z3 (l for 1, Z for 2, O for 0), (917)555.O123 |
| TP-045 | OCR-distorted separators | Lost / wrong separators | (917)9175550123 (collapsed), +1 917-555 0123 (mixed) |
| TP-046 | Masked / partial mobile | Privacy-redacted | (917) ***-0123, +1-XXX-XXX-0123, +1-917-555-**** |
| TP-047 | Phone in chat/SMS context | Conversational | "Hey, my new number is +1-917-555-0123, save it!", "Lost my phone, text me at..." |
| TP-048 | Adjacency-tight (name + mobile) | No separators | SarahChen+19175550123, JohnSmith917-555-0123 |
| TP-049 | tel: URI for mobile | Click-to-call | tel:+19175550123, <a href="tel:+1-917-555-0123">Call me</a> |
| TP-050 | Sentence-boundary tricky (personal) | Trailing punctuation | "Call me at +1 (917) 555-0123.", "Was it 917-555-0123?" |
| TP-051 | International with country emoji | With flag | 🇺🇸 +1-917-555-0123, 🇬🇧 +44 7700 900123 |
| TP-052 | Mobile with operator hint | Carrier reference | +1-917-555-0123 (Verizon), +44 7700 900123 (Vodafone) |
| TP-053 | Multilingual context label | Various languages | Mobile (EN), Portable (FR), Handy / Mobil (DE), Móvil (ES/PT), Cellulare (IT), 携帯 (JP), 휴대전화 (KR), Мобильный (RU) |
| TP-054 | Multiple phones (mobile + home) | Listed together | Mobile: +1-917-555-0123 \| Home: +1-212-555-0177 |
| TP-055 | Phone in voicemail transcript | Conversational | "Hi, this is Sarah, please call me back at nine one seven five five five zero one two three" |
| TP-056 | Anonymized placeholder mobile | Standard generic | (555) 123-4567 (placeholder), +1-555-0123 |
| TP-057 | Embedded in messaging URL | App share link | wa.me/19175550123 (WhatsApp), t.me/+19175550123 (Telegram) |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | TP-044, TP-045 |
| Masked / partial / redacted | ✓ | TP-046, TP-056 |
| Multilingual context labels | ✓ | TP-053 |
| Country-specific mobile coverage | ✓ | TP-001 through TP-029 (29 countries with mobile prefix patterns) |
| Embedded in URL/path | ✓ | TP-049, TP-057 |
| In structured data | ✓ | TP-041, TP-042, TP-043 |
| Adjacency-tight | ✓ | TP-048 |
| Sentence-boundary tricky | ✓ | TP-050 |
| Domain-embedded (email signature, chat, voicemail) | ✓ | TP-040, TP-047, TP-055 |
| Messaging app contexts | ✓ | TP-030, TP-031, TP-032, TP-033, TP-034 |
| Verbalized / spelled-out | ✓ | TP-055 |
| All work phone formats apply | ✓ | TP-039 (cross-reference to TW-001 to TW-065) |

**Total patterns for Telephone_Numbers_Personal: 57**

---

## Entity 10: Work_Email_Address

Professional / business email address. Domain typically indicates corporate, government, or educational affiliation.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| WE-001 | firstname.lastname@company | Most common corporate | john.smith@acmecorp.com, maria.garcia@servicenow.com, wolfgang.mueller@example.de |
| WE-002 | firstname_lastname@company | Underscore separator | john_smith@acmecorp.com, maria_garcia@corp.com |
| WE-003 | first initial + lastname | Abbreviated | jsmith@company.com, mgarcia@corp.com, wmueller@example.com |
| WE-004 | firstname + last initial | Reverse abbreviation | johns@company.com, mariag@corp.com |
| WE-005 | firstname@company | First name only | john@startup.io, sarah@design.co, wolfgang@example.de |
| WE-006 | lastname@company | Surname only | smith@company.com, garcia@corp.com, mueller@example.de |
| WE-007 | first-lastname@company | Hyphen separator | john-smith@acmecorp.com, maria-garcia@corp.com |
| WE-008 | firstnamelastname (no separator) | Concatenated | johnsmith@acmecorp.com, mariagarcia@corp.com |
| WE-009 | numeric employee ID | ID-based | emp12345@corp.com, e78901@company.com, id4521@example.com |
| WE-010 | Role-based — HR | Department/role | hr@company.com, careers@corp.com, jobs@example.com |
| WE-011 | Role-based — support | Customer service | support@company.com, help@corp.com, customerservice@example.com |
| WE-012 | Role-based — sales | Sales / contact | sales@company.com, contact@corp.com, info@example.com |
| WE-013 | Role-based — admin | Admin / IT | admin@company.com, it@corp.com, sysadmin@example.com |
| WE-014 | Role-based — security | Security / abuse | security@company.com, abuse@corp.com, soc@example.com |
| WE-015 | Role-based — finance | Finance / billing | finance@company.com, billing@corp.com, accounts@example.com |
| WE-016 | No-reply / system | Automated email | noreply@company.com, no-reply@corp.com, donotreply@example.com |
| WE-017 | .com TLD | Standard generic | john.smith@acmecorp.com |
| WE-018 | Country-code TLD (.de) | German company | wolfgang.mueller@firma.de |
| WE-019 | Country-code TLD (.fr) | French company | marie.dubois@société.fr, marie.dubois@societe.fr |
| WE-020 | Country-code TLD (.it) | Italian company | giovanni.rossi@azienda.it |
| WE-021 | Country-code TLD (.es) | Spanish company | maria.garcia@empresa.es |
| WE-022 | Country-code TLD (.br) | Brazilian company | joao.silva@empresa.com.br |
| WE-023 | Country-code TLD (.jp) | Japanese company | tanaka@kaisha.co.jp, suzuki@example.jp |
| WE-024 | Country-code TLD (.uk) | UK company | sarah.chen@example.co.uk, john.smith@firm.org.uk |
| WE-025 | Country-code TLD (.in) | Indian company | priya.sharma@company.in, rajesh@firm.co.in |
| WE-026 | Country-code TLD (.cn) | Chinese company | wang.wei@company.cn |
| WE-027 | Government TLD (.gov) | US government | john.smith@agency.gov, sarah.chen@whitehouse.gov |
| WE-028 | Government TLD (.gov.uk) | UK government | john.smith@nhs.gov.uk |
| WE-029 | Educational TLD (.edu) | US university | sarah.chen@mit.edu, professor@stanford.edu |
| WE-030 | Educational TLD (.ac.uk / .ac.jp) | UK / Japan academic | researcher@cam.ac.uk, professor@u-tokyo.ac.jp |
| WE-031 | Military TLD (.mil) | US military | sgt.smith@army.mil, capt.brown@navy.mil |
| WE-032 | Health TLD (.nhs.uk) | NHS | doctor@nhs.uk, sarah.chen@nhs.net |
| WE-033 | New gTLD | Generic TLD | hello@design.studio, info@brand.agency, support@app.io |
| WE-034 | Subdomained — department | Department subdomain | john@eng.company.com, sarah@emea.corp.com, wolfgang@de.example.com |
| WE-035 | Subdomained — region | Geographic subdomain | sarah@emea.acme.com, john@apac.corp.com, maria@latam.example.com |
| WE-036 | Subdomained — function | Functional subdomain | sales@us.company.com, support@asia.corp.com |
| WE-037 | Multi-level subdomain | Deep subdomain | john@hr.us.corp.com, sarah@dev.emea.company.com |
| WE-038 | Plus-addressed (Gmail-style tagging) | Sub-tag | john.smith+work@gmail.com, sarah+project@corp.com, info+sales@example.com |
| WE-039 | Plus-addressed for forwarding | Forwarding tag | john.smith+forward@corp.com, sarah+spam@company.com |
| WE-040 | Hyphenated tag | Alternative tag separator | john.smith-work@corp.com (some servers) |
| WE-041 | Non-Latin local part (Unicode) | Unicode email | 田中@企業.jp, müller@firma.de, García@empresa.es |
| WE-042 | Internationalized domain (IDN) | Unicode TLD | sarah@société.fr, john@日本企業.jp |
| WE-043 | All-caps email | Uppercase | JOHN.SMITH@COMPANY.COM, MARIA.GARCIA@CORP.COM |
| WE-044 | All-lowercase email | Lowercase | john.smith@company.com (standard normalized form) |
| WE-045 | Mixed-case (typo) | Inconsistent | John.Smith@Company.com, MARIA.garcia@CORP.com |
| WE-046 | With display name | Friendly format | "John Smith" <john.smith@corp.com>, John Smith <jsmith@co.com> |
| WE-047 | With display name (no quotes) | Bare format | John Smith <john.smith@corp.com> |
| WE-048 | RFC 5322 with comment | Parenthesized comment | john.smith@corp.com (CMO) |
| WE-049 | Obfuscated [at] / [dot] | Anti-spam | john [dot] smith [at] company [dot] com, john(at)company.com |
| WE-050 | Obfuscated AT / DOT | Caps obfuscation | john DOT smith AT company DOT com |
| WE-051 | Obfuscated with @+? | Visual obscure | john.smith{at}company.com, john.smith [REMOVE] @company.com |
| WE-052 | Image-based / invisible chars | Anti-bot | john.smith​@company.com (zero-width space inserted) |
| WE-053 | Homoglyph attack | Look-alike chars | john.smіth@company.com (Cyrillic і), maria.garcіa@corp.com |
| WE-054 | Email at sentence end | Trailing punctuation | "Email me at john.smith@corp.com." (period inside or outside) |
| WE-055 | Email with comma after | Inline | "John (john.smith@corp.com), the CMO, will lead..." |
| WE-056 | Email inside parentheses | Parenthetical | "Contact Sarah (sarah.chen@acme.com) for details" |
| WE-057 | Email with closing brace | At end of structure | "Sarah <sarah@corp.com>}" (after JSON-like structure) |
| WE-058 | Email in mailto: link | URL scheme | mailto:john.smith@corp.com, <a href="mailto:sarah@acme.com">Email Sarah</a> |
| WE-059 | Email with subject in mailto: | URL parameters | mailto:support@corp.com?subject=Help&body=Hello |
| WE-060 | Email with cc/bcc context | Header context | "To: john.smith@corp.com, cc: sarah.chen@corp.com, bcc: wolfgang@corp.com" |
| WE-061 | Email in From: header | RFC 5322 | "From: John Smith <john.smith@corp.com>" |
| WE-062 | Email in Reply-To: | Header field | "Reply-To: noreply@company.com" |
| WE-063 | Email in JSON | Structured | "email": "john.smith@corp.com", "work_email": "sarah@acme.com" |
| WE-064 | Email in KV | Form field | email=john.smith@corp.com, Work Email: sarah.chen@acme.com |
| WE-065 | Email in XML | Markup tag | <email>john.smith@corp.com</email>, <workEmail>sarah@acme.com</workEmail> |
| WE-066 | Email in CSV | Tabular data | "Smith","John","john.smith@corp.com" |
| WE-067 | Email in email signature | Multi-line block | Sarah Chen \| CMO \| sarah.chen@acme.com \| +1-212-555-0100 |
| WE-068 | OCR-distorted (l↔1↔I) | Char substitution | john.sm1th@corp.com, marlia.garcla@example.com, l1z.smith@company.com |
| WE-069 | OCR-distorted (O↔0) | Digit/letter | jOhn.smith@cOrp.cOm, john.smith@c0mpany.c0m |
| WE-070 | OCR-distorted (whitespace) | Lost / extra spaces | "john.smith @corp.com" (space before @), "john .smith@corp.com" |
| WE-071 | Masked / partial email | Privacy-redacted | j***@corp.com, john.s***@corp.com, ****@acme.com, [email redacted] |
| WE-072 | Last 4 chars only | Reference | "ending in @corp.com", "email starts with j.s..." |
| WE-073 | Anonymized placeholder | Standard generic | user@example.com, name@domain.com, john.doe@email.com |
| WE-074 | Email in URL path | Inside URL | linkedin.com/in/john-smith?email=john.smith@corp.com |
| WE-075 | Long local-part | Up to 64 chars | really.long.firstname.really.long.lastname.with.middle@company.com |
| WE-076 | Period-rich local | Multiple dots | j.o.h.n.s.m.i.t.h@corp.com (each char dotted) |
| WE-077 | Trailing dot before @ | Edge case | john.smith.@corp.com (RFC-allowed in quoted-local, rare) |
| WE-078 | Quoted local part | RFC quoted | "john..smith"@corp.com, "j.smith"@corp.com |
| WE-079 | Adjacency-tight with name | No separator | John Smith<jsmith@corp.com>, MariaGarcia<m.garcia@corp.com> |
| WE-080 | Adjacency-tight with phone | No separator | john.smith@corp.com+1-212-555-0100 |
| WE-081 | Multilingual context label | "Email:" various | Email (EN), Courriel (FR-CA) / E-mail (FR), E-Mail (DE), Correo electrónico (ES), Posta elettronica (IT), メール (JP), 이메일 (KR), Электронная почта (RU), البريد الإلكتروني (AR) |
| WE-082 | Email with title context | Plus title | john.smith@corp.com (CMO), sarah.chen@acme.com (Director of Sales) |
| WE-083 | Internal vs external email | Domain comparison | john.smith@acmecorp.com (internal); sarah.chen@vendor.com (external) |
| WE-084 | Email with PGP fingerprint | Plus crypto | sarah.chen@corp.com (PGP: 0x12345678) |
| WE-085 | Alias / forwarding email | Aliased | john.smith@corp.com (alias of j.smith.eng@corp.com) |
| WE-086 | Distribution list / group | Group email | engineering-team@corp.com, all-staff@acme.com, finance-dl@example.com |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | WE-068, WE-069, WE-070 |
| Masked / partial / redacted | ✓ | WE-071, WE-072, WE-073 |
| Multilingual context labels | ✓ | WE-081 |
| TLD coverage (gTLD, ccTLD, .gov, .edu, .mil) | ✓ | WE-017 to WE-033 |
| Unicode / non-Latin | ✓ | WE-041, WE-042 |
| Embedded in URL/path | ✓ | WE-058, WE-059, WE-074 |
| In structured data | ✓ | WE-063, WE-064, WE-065, WE-066 |
| Adjacency-tight | ✓ | WE-079, WE-080 |
| Sentence-boundary tricky | ✓ | WE-054, WE-055, WE-056, WE-057 |
| Case variations | ✓ | WE-043, WE-044, WE-045 |
| Obfuscation (anti-spam, homoglyph) | ✓ | WE-049, WE-050, WE-051, WE-052, WE-053 |
| Domain-embedded (header, signature, KV) | ✓ | WE-060, WE-061, WE-062, WE-067 |
| Role-based / functional | ✓ | WE-010 to WE-016 |
| Display name format | ✓ | WE-046, WE-047, WE-048 |

**Total patterns for Work_Email_Address: 86**

---

## Entity 11: Personal_Email_Address

Personal / consumer email address. Domain typically indicates freemail provider, ISP, or custom personal domain. All structural patterns from Work_Email also apply here.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PE-001 | Gmail | Google freemail | john.smith@gmail.com, maria.garcia99@gmail.com, sarah.chen.dev@gmail.com |
| PE-002 | Yahoo Mail | Yahoo freemail | john_smith@yahoo.com, maria.garcia@yahoo.com, jsmith88@yahoo.com |
| PE-003 | Outlook / Hotmail / Live | Microsoft freemail | jsmith@outlook.com, sarah.chen@hotmail.com, maria@live.com |
| PE-004 | iCloud / Apple ID | Apple freemail | john.smith@icloud.com, maria.garcia@me.com, sarah@mac.com |
| PE-005 | AOL Mail | Vintage US freemail | jsmith@aol.com, sarah_chen42@aol.com |
| PE-006 | ProtonMail | Privacy-focused | john.smith@proton.me, sarah.chen@protonmail.com |
| PE-007 | Tutanota | Encrypted email | john@tutanota.com, sarah@tutamail.com |
| PE-008 | German freemail (web.de) | DE local provider | wolfgang.mueller@web.de, hans-peter@web.de |
| PE-009 | German freemail (gmx.de / gmx.net) | DE GMX | sarah.schmidt@gmx.de, wolfgang.mueller@gmx.net |
| PE-010 | German freemail (t-online.de) | DE Telekom | hans.mueller@t-online.de |
| PE-011 | German freemail (freenet.de) | DE freenet | hans.weber@freenet.de |
| PE-012 | French freemail (orange.fr) | FR Orange | pierre.dubois@orange.fr, marie.lefevre@orange.fr |
| PE-013 | French freemail (wanadoo.fr) | FR Wanadoo (legacy) | pierre.dubois@wanadoo.fr |
| PE-014 | French freemail (free.fr) | FR Free | pierre.dubois@free.fr, marie.lefevre@free.fr |
| PE-015 | French freemail (laposte.net) | FR La Poste | pierre.dubois@laposte.net |
| PE-016 | French freemail (sfr.fr) | FR SFR | pierre.dubois@sfr.fr |
| PE-017 | Italian freemail (libero.it) | IT Libero | giovanni.rossi@libero.it, francesca.bianchi@libero.it |
| PE-018 | Italian freemail (alice.it / tin.it) | IT Telecom | giovanni.rossi@alice.it, marco.ferrari@tin.it |
| PE-019 | Italian freemail (virgilio.it) | IT Virgilio | giovanni.rossi@virgilio.it |
| PE-020 | Spanish freemail (terra.es / movistar.es) | ES local | juan.garcia@terra.es, maria.rodriguez@movistar.es |
| PE-021 | Brazilian freemail (uol.com.br) | BR UOL | joao.silva@uol.com.br, maria.santos@uol.com.br |
| PE-022 | Brazilian freemail (bol.com.br / terra.com.br) | BR local | pedro.souza@bol.com.br, ana.oliveira@terra.com.br |
| PE-023 | Brazilian freemail (ig.com.br) | BR iG | pedro.souza@ig.com.br |
| PE-024 | Japanese freemail (yahoo.co.jp) | JP Yahoo | tanaka@yahoo.co.jp, suzuki.hanako@yahoo.co.jp |
| PE-025 | Japanese freemail (docomo.ne.jp / softbank.ne.jp / au.com) | JP carrier | tanaka@docomo.ne.jp, suzuki@softbank.ne.jp |
| PE-026 | Japanese freemail (nifty.com) | JP nifty | tanaka.taro@nifty.com |
| PE-027 | Korean freemail (naver.com) | KR Naver | minsu.kim@naver.com, jiyeong.lee@naver.com |
| PE-028 | Korean freemail (daum.net / hanmail.net) | KR Daum | minsu.kim@daum.net, sujin.park@hanmail.net |
| PE-029 | Korean freemail (nate.com / kakao.com) | KR Nate / Kakao | minsu.kim@nate.com, jiyeong@kakao.com |
| PE-030 | Chinese freemail (qq.com) | CN Tencent QQ | 12345678@qq.com, wang.wei@qq.com |
| PE-031 | Chinese freemail (163.com / 126.com) | CN NetEase | wang.wei@163.com, li.fang@126.com |
| PE-032 | Chinese freemail (sina.com / sohu.com) | CN other | zhang.ming@sina.com, liu.yang@sohu.com |
| PE-033 | Russian freemail (mail.ru) | RU Mail.ru | ivan.petrov@mail.ru, maria.sokolova@mail.ru |
| PE-034 | Russian freemail (yandex.ru / yandex.com) | RU Yandex | ivan@yandex.ru, maria@yandex.com |
| PE-035 | Russian freemail (rambler.ru) | RU Rambler | ivan.petrov@rambler.ru |
| PE-036 | UK freemail (btinternet.com / sky.com) | UK ISP | john.smith@btinternet.com, sarah.chen@sky.com |
| PE-037 | Dutch freemail (kpn.nl / xs4all.nl) | NL local | jan.devries@kpn.nl, marieke@xs4all.nl |
| PE-038 | Polish freemail (wp.pl / o2.pl / interia.pl) | PL local | krzysztof@wp.pl, agnieszka@o2.pl, tomasz@interia.pl |
| PE-039 | Czech freemail (seznam.cz / centrum.cz) | CZ local | jan.novak@seznam.cz, petra@centrum.cz |
| PE-040 | Hungarian freemail (freemail.hu / citromail.hu) | HU local | nagy.laszlo@freemail.hu, kovacs@citromail.hu |
| PE-041 | Turkish freemail (mynet.com) | TR local | mehmet@mynet.com, ayse.ozturk@mynet.com |
| PE-042 | Israeli freemail (walla.co.il) | IL local | david.cohen@walla.co.il |
| PE-043 | Indian freemail (rediffmail.com) | IN local | rajesh@rediffmail.com, priya.sharma@rediffmail.com |
| PE-044 | US ISP-assigned (comcast.net) | Comcast / Xfinity | john.smith@comcast.net |
| PE-045 | US ISP-assigned (verizon.net) | Verizon | sarah.chen@verizon.net |
| PE-046 | US ISP-assigned (att.net / sbcglobal.net) | AT&T | wolfgang.mueller@att.net, j.smith@sbcglobal.net |
| PE-047 | US ISP-assigned (cox.net / charter.net) | Cox / Charter | maria@cox.net, john@charter.net |
| PE-048 | UK ISP-assigned (bt.com / virginmedia.com) | UK ISP | sarah.chen@bt.com, john@virginmedia.com |
| PE-049 | DE ISP-assigned (vodafone.de) | DE Vodafone | hans@vodafone.de |
| PE-050 | Country-specific Yahoo (.co.uk, .fr, .de, etc.) | Localized Yahoo | sarah@yahoo.co.uk, pierre@yahoo.fr, hans@yahoo.de |
| PE-051 | Country-specific Gmail-style (.co.jp, etc.) | International | tanaka@gmail.com (no co.jp variant, but uses gmail) |
| PE-052 | Custom personal domain | Self-hosted | me@johnsmith.com, hello@mariadesign.com, contact@sarahchen.io |
| PE-053 | Vanity domain (firstname.com / firstnamelastname.com) | Personal brand | hi@john.com, hello@sarahchen.com |
| PE-054 | Tech-leaning custom (.io, .dev, .me) | Developer-style | john@dev.io, sarah@coder.dev, maria@me.com |
| PE-055 | Disposable (10minutemail) | Throwaway 10min | user12345@10minutemail.com, anon@10minemail.net |
| PE-056 | Disposable (mailinator) | Throwaway long-term | test@mailinator.com, throwaway@mailinator.com |
| PE-057 | Disposable (guerrillamail) | Throwaway | anon@guerrillamail.com, temp@sharklasers.com |
| PE-058 | Disposable (tempmail / temp-mail) | Generic throwaway | tempuser@tempmail.com, anon@temp-mail.org |
| PE-059 | Disposable (yopmail) | Throwaway with subaddressing | anything@yopmail.com, test123@yopmail.fr |
| PE-060 | Privacy relay (Apple Hide My Email) | Hash + privaterelay.appleid.com | john.smith_aw3qb9@privaterelay.appleid.com |
| PE-061 | Privacy relay (Firefox Relay) | Random + mozmail.com | tj9k2vqz@mozmail.com, m4st3rx@mozmail.com |
| PE-062 | Privacy relay (SimpleLogin) | Random + simplelogin.com | random123@aleeas.com, anon456@simplelogin.com |
| PE-063 | Privacy relay (DuckDuckGo) | DuckDuckGo Email Protection | random@duck.com |
| PE-064 | Numeric / random local part | Non-name based | user12345@gmail.com, xkcd_fan_99@hotmail.com, 8675309@yahoo.com |
| PE-065 | Name + birth year combo | Common personal pattern | jsmith1985@gmail.com, maria.garcia92@yahoo.com, john88@outlook.com |
| PE-066 | Name + numbers (no clear pattern) | Disambiguation | sarah_chen42@gmail.com, john.smith27@yahoo.com |
| PE-067 | Plus-addressed (subaddressing) | Tagging | john.smith+shopping@gmail.com, sarah+newsletters@gmail.com |
| PE-068 | Plus-addressed for filtering | Sender tracking | john+amazon@gmail.com, john+facebook@gmail.com |
| PE-069 | Plus-addressed for forwarding | Forwarding tag | john+forward@gmail.com, sarah+main@gmail.com |
| PE-070 | Dot-variations (Gmail) | Equivalent dots | j.o.h.n.s.m.i.t.h@gmail.com, jo.hn.sm.it.h@gmail.com (Gmail ignores dots) |
| PE-071 | First name + last initial | Short personal | sarah.c@gmail.com, j.smith@yahoo.com |
| PE-072 | Email with hobby / interest | Personal expression | metalhead42@gmail.com, gardener_sarah@yahoo.com, coffeelover@outlook.com |
| PE-073 | Email with pet name | Personal | tigerlover@gmail.com, sparkysmom@yahoo.com |
| PE-074 | Email with sports team | Personal expression | lakersfan@gmail.com, mufc4life@yahoo.com |
| PE-075 | Old-style abbreviated | Vintage AOL-era | jsmth@aol.com, srhchn@hotmail.com (vowels dropped) |
| PE-076 | All-caps personal email | Uppercase | JOHN.SMITH@GMAIL.COM, MARIA.GARCIA@YAHOO.COM |
| PE-077 | All-lowercase | Standard normalized | john.smith@gmail.com, maria.garcia@yahoo.com |
| PE-078 | Mixed-case (typo) | Inconsistent | John.Smith@gmail.com, MARIA.garcia@Yahoo.com |
| PE-079 | Hyphenated local | Hyphen separator | john-smith@gmail.com, maria-garcia@yahoo.com |
| PE-080 | Concatenated (no separator) | All together | johnsmith@gmail.com, mariagarcia@yahoo.com |
| PE-081 | Personal email with display name | Friendly format | "John Smith" <john.smith@gmail.com>, John Smith <jsmith@yahoo.com> |
| PE-082 | Display name only (no quotes) | Bare format | John Smith <john.smith@gmail.com> |
| PE-083 | Display name nickname | Friendly format | "Johnny" <john.smith@gmail.com>, "Sarah from Acme" <sarah@gmail.com> |
| PE-084 | Non-Latin local part (Unicode) | IDN email | 田中@gmail.com, müller@web.de, García@gmail.com |
| PE-085 | Internationalized domain (IDN) | Unicode TLD | sarah@société.fr, john@日本.jp, anna@münchen.de |
| PE-086 | Cyrillic local part | Russian email | иван@yandex.ru, мария@mail.ru |
| PE-087 | Hebrew local part | Hebrew email | דוד@gmail.com (rare, but RFC-allowed) |
| PE-088 | Arabic local part | Arabic email | محمد@gmail.com (rare, RFC-allowed) |
| PE-089 | Obfuscated [at] / [dot] | Anti-spam | john [dot] smith [at] gmail [dot] com, john(at)gmail.com |
| PE-090 | Obfuscated AT / DOT capitalized | Caps obfuscation | john DOT smith AT gmail DOT com |
| PE-091 | Obfuscated with [REMOVE] | Bot-blocking | john.smith [REMOVE THIS] @gmail.com |
| PE-092 | Image-based / invisible chars | Anti-bot | john.smith​@gmail.com (zero-width space) |
| PE-093 | Homoglyph attack | Look-alike chars | john.smіth@gmail.com (Cyrillic і), maria.garcіa@yahoo.com |
| PE-094 | mailto: link | URL scheme | mailto:john.smith@gmail.com, <a href="mailto:sarah@yahoo.com">Email Sarah</a> |
| PE-095 | mailto: with subject | URL with parameters | mailto:john@gmail.com?subject=Hello&body=Hi |
| PE-096 | Email at sentence boundary | Trailing punctuation | "Email me at john.smith@gmail.com.", "Was it sarah@yahoo.com?" |
| PE-097 | Email inside parentheses | Inline parenthetical | "Contact John (john.smith@gmail.com) for details" |
| PE-098 | Email with comma after | Inline | "John (john.smith@gmail.com), my friend, will help" |
| PE-099 | Email in chat / SMS | Casual mention | "yo my email is sarah.chen@gmail.com", "drop me a line at john@yahoo.com" |
| PE-100 | Email in forum / Reddit / Discord | Online platform | "DM me at sarah.chen@gmail.com", "Reach me on Discord: john_doe#1234, or email john@gmail.com" |
| PE-101 | Email in social profile | Profile bio | "📧 sarah.chen@gmail.com" (in Instagram/Twitter bio) |
| PE-102 | Email with cc/bcc context | Header context | "To: friend1@gmail.com, cc: friend2@yahoo.com" |
| PE-103 | Email in From: header | RFC 5322 | "From: John Smith <john.smith@gmail.com>" |
| PE-104 | Email in Reply-To: | Header field | "Reply-To: john.smith@gmail.com" |
| PE-105 | Email in JSON | Structured | "email": "john.smith@gmail.com", "personal_email": "sarah@yahoo.com" |
| PE-106 | Email in KV | Form field | email=john.smith@gmail.com, Personal Email: sarah@yahoo.com |
| PE-107 | Email in XML | Markup tag | <email>john.smith@gmail.com</email>, <personalEmail>sarah@yahoo.com</personalEmail> |
| PE-108 | Email in CSV | Tabular data | "Smith","John","john.smith@gmail.com","Personal" |
| PE-109 | OCR-distorted (l↔1↔I) | Char substitution | john.sm1th@gmail.com, mar1a.garcla@yahoo.com, l1z.smith@hotmail.com |
| PE-110 | OCR-distorted (O↔0) | Digit / letter | jOhn.smith@gmail.cOm, john.smith@g0mail.c0m, jOhn.smIth@yahoo.cOm |
| PE-111 | OCR-distorted whitespace | Lost / extra spaces | "john.smith @gmail.com" (space before @), "john .smith@gmail.com" |
| PE-112 | OCR diacritic stripping | Lost accents | francois.muller@gmail.com (was Müller), jose@gmail.com (was José) |
| PE-113 | Masked / partial email | Privacy-redacted | j***@gmail.com, john.s***@gmail.com, ****@yahoo.com, [email redacted] |
| PE-114 | Last 4 chars only / domain only | Reference | "ending in @gmail.com", "email starts with j.s..." |
| PE-115 | Anonymized placeholder | Standard generic | user@example.com, anonymous@email.com, jane.doe@gmail.com |
| PE-116 | Adjacency-tight with name | No separator | John Smith<jsmith@gmail.com>, MariaGarcia<m.garcia@yahoo.com> |
| PE-117 | Adjacency-tight with phone | No separator | john.smith@gmail.com+1-917-555-0123 |
| PE-118 | Multilingual context label | "Personal email:" various | Personal Email (EN), Courriel personnel (FR-CA), Privat E-Mail (DE), Correo personal (ES), Email personale (IT), 個人メール (JP), 개인 이메일 (KR), Личная почта (RU) |
| PE-119 | "Backup email" / "Recovery email" label | Security context | Backup email: sarah.chen@gmail.com, Recovery email: maria@yahoo.com |
| PE-120 | Personal vs work distinction | Form field | Work: john.smith@acme.com; Personal: jsmith1985@gmail.com |
| PE-121 | Email with PGP fingerprint | Plus crypto | sarah.chen@gmail.com (PGP key: 0xABCDEF12) |
| PE-122 | Long local-part personal | Up to 64 chars | really.long.firstname.really.long.lastname@gmail.com |
| PE-123 | Period-rich local | Multiple dots (Gmail-equivalent) | j.o.h.n.s.m.i.t.h@gmail.com (Gmail treats as same as johnsmith) |
| PE-124 | Quoted local part | RFC quoted | "john..smith"@gmail.com (technically valid but rare) |
| PE-125 | All structural patterns WE-001 to WE-086 | Apply structurally | (Same structural patterns as Work_Email apply — first.last, first_last, hyphen, no-sep, role-based, etc.) |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | PE-109, PE-110, PE-111, PE-112 |
| Masked / partial / redacted | ✓ | PE-113, PE-114, PE-115 |
| Multilingual context labels | ✓ | PE-118, PE-119 |
| Country freemail coverage | ✓ | PE-008 to PE-051 (15+ countries: DE, FR, IT, ES, BR, JP, KR, CN, RU, UK, NL, PL, CZ, HU, TR, IL, IN) |
| Unicode / non-Latin local part | ✓ | PE-084, PE-085, PE-086, PE-087, PE-088 |
| Embedded in URL/path | ✓ | PE-094, PE-095 |
| In structured data | ✓ | PE-105, PE-106, PE-107, PE-108 |
| Adjacency-tight | ✓ | PE-116, PE-117 |
| Sentence-boundary tricky | ✓ | PE-096, PE-097, PE-098 |
| Case variations | ✓ | PE-076, PE-077, PE-078 |
| Obfuscation (anti-spam, homoglyph) | ✓ | PE-089 to PE-093 |
| Domain-embedded (chat, social, header) | ✓ | PE-099, PE-100, PE-101, PE-103, PE-104 |
| Privacy-relay / disposable | ✓ | PE-055 to PE-063 |
| Display name format | ✓ | PE-081, PE-082, PE-083 |
| All structural patterns from Work_Email | ✓ | PE-125 (cross-reference) |

**Total patterns for Personal_Email_Address: 125**

---

## Entity 12: Date_of_Birth

Date of birth in all date formats, plus birth-specific contextual patterns. Includes era-based dates, partial dates, age-derived DOB, and DOB embedded in national IDs.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| DOB-001 | US format MM/DD/YYYY | Slash-separated | 03/15/1985, 07/22/1990, 12/31/1972 |
| DOB-002 | US with dashes | MM-DD-YYYY | 03-15-1985, 07-22-1990 |
| DOB-003 | European DD/MM/YYYY | Day-first | 15/03/1985, 22/07/1990, 31/12/1972 |
| DOB-004 | European DD.MM.YYYY | Period separator | 15.03.1985, 22.07.1990, 31.12.1972 |
| DOB-005 | European DD-MM-YYYY | Dash separator | 15-03-1985, 22-07-1990 |
| DOB-006 | ISO 8601 YYYY-MM-DD | International standard | 1985-03-15, 1990-07-22, 1972-12-31 |
| DOB-007 | YYYY/MM/DD (Japanese / Korean) | Year-first slash | 1985/03/15, 1990/07/22 |
| DOB-008 | YYYY.MM.DD (Hungarian / Korean) | Year-first dot | 1985.03.15, 1990.07.22 |
| DOB-009 | YYYY年MM月DD日 (Japanese) | Japanese kanji format | 1985年3月15日, 1990年7月22日 |
| DOB-010 | YYYY년 MM월 DD일 (Korean) | Korean hangul format | 1985년 3월 15일, 1990년 7월 22일 |
| DOB-011 | YYYY年MM月DD日 (Chinese) | Chinese | 1985年3月15日, 1990年7月22日 |
| DOB-012 | Written English (full) | Word form | March 15, 1985; 15th March 1985; March fifteenth, 1985 |
| DOB-013 | Written English (abbreviated month) | Short month | Mar 15, 1985; 15 Mar 1985; 15-Mar-1985 |
| DOB-014 | Written English (ordinal) | With "th"/"st"/"nd"/"rd" | March 15th, 1985; the 22nd of July, 1990; July 4th, 1976 |
| DOB-015 | Written French | French format | 15 mars 1985, le 15 mars 1985, né(e) le 15 mars 1985 |
| DOB-016 | Written French (abbreviated) | French short month | 15 mars 1985, 22 juil. 1990 |
| DOB-017 | Written German | German format | 15. März 1985, geboren am 15. März 1985, 15.3.1985 |
| DOB-018 | Written German (abbreviated) | DE short month | 15. Mrz. 1985, 22. Jul. 1990 |
| DOB-019 | Written Spanish | Spanish format | 15 de marzo de 1985, nacido el 15 de marzo de 1985 |
| DOB-020 | Written Spanish (abbreviated) | ES short month | 15 mar 1985, 22-jul-1990 |
| DOB-021 | Written Italian | Italian format | 15 marzo 1985, nato il 15 marzo 1985 |
| DOB-022 | Written Italian (abbreviated) | IT short month | 15 mar 1985, 22 lug. 1990 |
| DOB-023 | Written Portuguese | Portuguese format | 15 de março de 1985, 15 de março/1985, nascido em 15 de março |
| DOB-024 | Written Portuguese (abbreviated) | PT short month | 15 mar 1985, 22 jul./1990 |
| DOB-025 | Written Dutch | Dutch format | 15 maart 1985, geboren op 15 maart 1985 |
| DOB-026 | Written Swedish | Swedish format | 15 mars 1985, den 15 mars 1985 |
| DOB-027 | Written Finnish | Finnish format | 15.3.1985, 15. maaliskuuta 1985 |
| DOB-028 | Written Polish | Polish format | 15 marca 1985, 15.03.1985 r., ur. 15.03.1985 |
| DOB-029 | Written Czech | Czech format | 15. března 1985, 15. 3. 1985, nar. 15. 3. 1985 |
| DOB-030 | Written Hungarian | YYYY. MM. DD. format | 1985. március 15., 1985.03.15., szül.: 1985. 03. 15. |
| DOB-031 | Written Turkish | Turkish format | 15 Mart 1985, doğum tarihi: 15.03.1985 |
| DOB-032 | Written Norwegian | Norwegian format | 15. mars 1985, født 15. mars 1985 |
| DOB-033 | Written Danish | Danish format | 15. marts 1985, født den 15. marts 1985 |
| DOB-034 | Written Russian | Russian format | 15 марта 1985 г., 15.03.1985 |
| DOB-035 | Russian dot format | RU numeric | 15.03.1985, 15.03.85 |
| DOB-036 | Japanese era — Reiwa | Heisei/Showa/Reiwa | 昭和60年3月15日 (Showa 60 = 1985), 平成2年7月22日 (Heisei 2 = 1990) |
| DOB-037 | Japanese era — abbreviated | S/H/R prefix | S60.3.15 (Showa 60 = 1985), H2.7.22 (Heisei 2 = 1990), R5.5.1 (Reiwa 5 = 2023) |
| DOB-038 | Korean era / Dangi | Traditional Korean | 단기 4318년 3월 15일 (Dangi 4318 = 1985) |
| DOB-039 | Thai Buddhist era | +543 years | 15 มีนาคม 2528 (BE 2528 = 1985), 22 กรกฎาคม 2533 (BE 2533 = 1990) |
| DOB-040 | Thai Buddhist era (numeric) | DD/MM/YYYY+543 | 15/03/2528, 15-03-2528 |
| DOB-041 | Hebrew calendar | Hebrew civil/religious | כ"ב אדר ב' תשמ"ה (22 Adar II 5745 = 1985), ט"ז תמוז תש"נ (16 Tammuz 5750 = 1990) |
| DOB-042 | Hebrew civil with Hebrew script | Civil format Hebrew | 15 במרץ 1985, נולד ב-15 במרץ 1985 |
| DOB-043 | Arabic Hijri calendar | Islamic lunar | 23 جمادى الثانية 1405 هـ (= 1985 CE), 5 ذو الحجة 1410 هـ (= 1990 CE) |
| DOB-044 | Arabic civil with Arabic-Indic digits | Arabic numerals | ١٥/٣/١٩٨٥, ٢٢ يوليو ١٩٩٠ |
| DOB-045 | Arabic civil with Latin digits | Latin numerals + Arabic month | 15 مارس 1985, 22 يوليو 1990 |
| DOB-046 | Persian / Jalali calendar | Iranian solar | 24 اسفند 1363 (= 15 March 1985) |
| DOB-047 | Chinese lunar calendar | Traditional lunar | 农历1985年正月二十四 (lunar new year date) |
| DOB-048 | DOB with "born" English label | Explicit | born on March 15, 1985; born 03/15/1985; DOB: March 15, 1985 |
| DOB-049 | DOB with "DOB:" label | Common form prefix | DOB: 03/15/1985, D.O.B.: 15/03/1985, D-O-B: 1985-03-15 |
| DOB-050 | DOB with "Date of Birth:" label | Full label | Date of Birth: March 15, 1985; Date of Birth: 15.03.1985 |
| DOB-051 | DOB multilingual context | "Born" various langs | né(e) le (FR), geboren am (DE), nacido el (ES), nato il (IT), 生年月日 (JP), 출생일 (KR), Дата рождения (RU), 出生日期 (ZH), Doğum tarihi (TR), תאריך לידה (HE), تاريخ الميلاد (AR) |
| DOB-052 | DOB with day of week | Full timestamp | Friday, March 15, 1985; Vendredi 15 mars 1985 |
| DOB-053 | DOB with time | Birth time | Born March 15, 1985 at 3:42 AM; DOB: 03/15/1985 03:42 |
| DOB-054 | DOB with hospital context | Plus location | Born March 15, 1985 at St. Mary's Hospital, Boston |
| DOB-055 | DOB numeric only — 8 digits | YYYYMMDD compact | 19850315, 19900722, 19721231 |
| DOB-056 | DOB numeric only — 6 digits | YYMMDD compact | 850315, 900722, 721231 |
| DOB-057 | Two-digit year (ambiguous) | Year truncated | 03/15/85, 15.03.85, 15-03-85 |
| DOB-058 | Two-digit year with apostrophe | '85 style | 03/15/'85, March 15, '85 |
| DOB-059 | Partial DOB — month/year only | Year + month | March 1985, 03/1985, 1985-03, mars 1985 |
| DOB-060 | Partial DOB — year only | Year alone | Born 1985, b. 1985, * 1985 (genealogy) |
| DOB-061 | Partial DOB — month/day only | No year | March 15 (year withheld), 03/15 |
| DOB-062 | DOB redacted year | Privacy partial | born 03/15/****, DOB: **/**/1985 |
| DOB-063 | DOB embedded in Swedish personnummer | YYMMDD-XXXX | 850315-1234, 19850315-1234 |
| DOB-064 | DOB embedded in Finnish henkilötunnus | DDMMYY-XXXX | 150385-123A, 150385+123A (1800s) |
| DOB-065 | DOB embedded in Norwegian fødselsnummer | DDMMYY + 5 digits | 15038512345 |
| DOB-066 | DOB embedded in Danish CPR | DDMMYY-XXXX | 150385-1234 |
| DOB-067 | DOB embedded in Polish PESEL | YYMMDDXXXXX | 85031512345 |
| DOB-068 | DOB embedded in Korean RRN | YYMMDD-XXXXXXX | 850315-1234567 |
| DOB-069 | DOB embedded in Chinese ID | 18-digit with DOB | 110101198503151234 (DOB = 19850315 in positions 7-14) |
| DOB-070 | DOB embedded in Italian Codice Fiscale | Encoded month + day | RSSMRA85M01H501Z (M = March, 01 = day-related) |
| DOB-071 | Age-derived DOB | Computed from age | "35 years old (as of March 2020) → ~1985" |
| DOB-072 | Age range derived | Approx birth year | "in his 40s → born ~1980-1985" |
| DOB-073 | DOB with century prefix | Y2K-aware | DOB: 19850315; 21st-century birth: 20050722 |
| DOB-074 | DOB in passport context | Travel document | "Date of birth (passport): 15 MAR 1985"; DOB stamp: 15-MAR-1985 |
| DOB-075 | DOB in legal pleading | Court context | "Plaintiff John Smith, born March 15, 1985, hereby..." |
| DOB-076 | DOB in medical chart | Clinical convention | "Patient: Chen, Sarah; DOB: 07/22/1990; Age: 34" |
| DOB-077 | DOB in financial KYC | Bank/KYC | "DOB: 15-Mar-1985, age 39, Customer since 2010" |
| DOB-078 | DOB in HR record | Employment | "Employee DOB: 1985-03-15, Hire date: 2010-06-01" |
| DOB-079 | DOB with leading zero stripped | Inconsistent zeroing | 3/15/85, 15/3/1985, 7/22/1990 |
| DOB-080 | DOB with leading zero | Padded zero | 03/15/1985, 07/22/1990, 09/01/1995 |
| DOB-081 | DOB in JSON | Structured | "date_of_birth": "1985-03-15", "dob": "03/15/1985", "birth_date": "March 15, 1985" |
| DOB-082 | DOB in KV | Form field | dob=03/15/1985, Date of Birth: March 15, 1985, BIRTHDATE: 1985-03-15 |
| DOB-083 | DOB in XML | Markup tag | <dob>1985-03-15</dob>, <birthDate>1985-03-15T00:00:00</birthDate> |
| DOB-084 | DOB in CSV | Tabular data | "Smith","John","1985-03-15","Male" |
| DOB-085 | DOB in log timestamp | Embedded in log | "[2024-03-15 14:30:22] user_dob=1985-03-15" |
| DOB-086 | DOB with timezone | Birth + TZ | "Born 1985-03-15T03:42:00-05:00" |
| DOB-087 | OCR-distorted DOB (digits) | Char substitution | O3/l5/l985 (O for 0, l for 1), 1S/O3/198S (S for 5) |
| DOB-088 | OCR-distorted DOB (separators) | Lost / wrong separators | 03 15 1985 (lost slashes), 03/15.1985 (mixed) |
| DOB-089 | OCR-distorted month name | Mangled month | Marcli 15, 1985 (cli for h); Janury (lost 'a'); Decemher |
| DOB-090 | Masked / partial DOB | Privacy-redacted | XX/XX/1985, **/03/1985, born ****; DOB: **/**/**** |
| DOB-091 | Masked DOB — year-only | Just year shown | DOB: ****/1985, born 19XX, year of birth: 1985 |
| DOB-092 | DOB anonymized placeholder | Standard generic | 01/01/1970 (Unix epoch placeholder), 1980-01-01 (anonymized) |
| DOB-093 | DOB sentence-boundary tricky | Trailing punctuation | "She was born on March 15, 1985.", "DOB 1985-03-15?", "born 15.03.1985!" |
| DOB-094 | DOB adjacency-tight with name | No separator | "Smith,John,1985-03-15"; "JohnSmith1985-03-15"; "Maria García-03/15/1985" |
| DOB-095 | DOB adjacency-tight with SSN | Mashed | "1985-03-15/123-45-6789"; DOB+SSN concat |
| DOB-096 | Decade reference | Birth decade | "born in the 80s", "a child of the 90s", "70s baby" |
| DOB-097 | "Birthday" context | Celebration | "happy birthday on March 15!", "her birthday is 03/15" |
| DOB-098 | Birth season reference | Vague | "born in spring 1985", "summer baby" |
| DOB-099 | Astrological context | Zodiac | "born March 15, 1985 (Pisces)", "DOB: Aries, April 5, 1990" |
| DOB-100 | DOB in voicemail / spoken | Verbalized | "I was born nineteen eighty-five", "March fifteenth, eighty-five" |
| DOB-101 | DOB ISO compact (YYYYMMDD) | No separators | 19850315 (8-digit no-sep) |
| DOB-102 | DOB with timezone-stripped time | ISO + time | 1985-03-15T03:42:00, 1985-03-15 03:42:00 UTC |
| DOB-103 | DOB at signature line | After name | "Signed: John Smith (DOB: 03/15/1985)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | DOB-087, DOB-088, DOB-089 |
| Masked / partial / redacted | ✓ | DOB-062, DOB-090, DOB-091, DOB-092 |
| Multilingual context labels | ✓ | DOB-051 |
| Country / locale-specific formats | ✓ | DOB-001 to DOB-035 (US, EU, ISO, JP, KR, ZH, multiple European langs) |
| Era-based / non-Gregorian | ✓ | DOB-036, DOB-037, DOB-038, DOB-039, DOB-040, DOB-041, DOB-043, DOB-046, DOB-047 (Reiwa/Heisei/Showa, Buddhist, Hebrew, Hijri, Persian, Lunar) |
| Script variations | ✓ | DOB-009, DOB-010, DOB-011, DOB-039 to DOB-047 (JP, KR, ZH, AR, HE, TH, RU, FA) |
| Embedded in national ID | ✓ | DOB-063 to DOB-070 (SE, FI, NO, DK, PL, KR, ZH, IT) |
| In structured data | ✓ | DOB-081, DOB-082, DOB-083, DOB-084, DOB-085 |
| Adjacency-tight | ✓ | DOB-094, DOB-095 |
| Sentence-boundary tricky | ✓ | DOB-093 |
| Verbalized / written out | ✓ | DOB-012 to DOB-033, DOB-100 |
| Two-digit year ambiguity | ✓ | DOB-057, DOB-058 |
| Partial / range / decade | ✓ | DOB-059, DOB-060, DOB-061, DOB-071, DOB-072, DOB-096 |
| Domain-embedded (medical/legal/financial/HR/passport) | ✓ | DOB-074, DOB-075, DOB-076, DOB-077, DOB-078 |

**Total patterns for Date_of_Birth: 103**

---

## Entity 13: Age

Numeric or descriptive age of a person.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| AG-001 | Numeric + "years old" | English standard | 35 years old, 67 years of age, age 42 |
| AG-002 | Numeric + "yr/yrs" abbreviated | English short | 35 yrs, 67 yr, 22 yr old |
| AG-003 | Numeric + "y/o" | Casual abbreviation | 35 y/o, 35yo, 67y/o |
| AG-004 | "Age:" + numeric | Form / KV style | Age: 35, AGE: 67, age=42 |
| AG-005 | "aged X" prefix | Inline reference | "aged 35", "a 35-year-old", "aged about 30" |
| AG-006 | Numeric + multilingual unit (FR) | French | 35 ans, âgé(e) de 35 ans, à l'âge de 35 ans |
| AG-007 | Numeric + multilingual unit (DE) | German | 35 Jahre alt, im Alter von 35 Jahren, 35-jährig |
| AG-008 | Numeric + multilingual unit (ES) | Spanish | 35 años, tiene 35 años, a la edad de 35 |
| AG-009 | Numeric + multilingual unit (IT) | Italian | 35 anni, all'età di 35 anni, di 35 anni |
| AG-010 | Numeric + multilingual unit (PT) | Portuguese | 35 anos, com 35 anos, à idade de 35 |
| AG-011 | Numeric + multilingual unit (JP) | Japanese | 35歳, 35才 (variant), 35歳の |
| AG-012 | Numeric + multilingual unit (KR) | Korean | 35세, 만 35세, 35살 (informal) |
| AG-013 | Numeric + multilingual unit (ZH) | Chinese | 35岁, 35歲 (traditional) |
| AG-014 | Numeric + multilingual unit (RU) | Russian | 35 лет, в возрасте 35 лет |
| AG-015 | Numeric + multilingual unit (AR) | Arabic | عمره 35 سنة, ٣٥ سنة |
| AG-016 | Numeric + multilingual unit (HE) | Hebrew | בן 35, בת 35, גיל 35 |
| AG-017 | Numeric + multilingual unit (TH) | Thai | อายุ 35 ปี, 35 ปี |
| AG-018 | Numeric + multilingual unit (TR) | Turkish | 35 yaşında, 35 yaş |
| AG-019 | Age range (inclusive) | X-Y span | 30-35, ages 25 to 30, between 25 and 30 |
| AG-020 | Age range (with units) | With "years" | 30-35 years old, ages 25 to 30 years |
| AG-021 | Age range (approximate) | Mid-X-Y style | mid-thirties, early forties, late twenties |
| AG-022 | Numeric written out (English) | Word form | thirty-five, sixty-seven, twenty-two, a hundred and one |
| AG-023 | Numeric written out (French) | Word form | trente-cinq, soixante-sept, vingt-deux |
| AG-024 | Numeric written out (German) | Word form | fünfunddreißig, siebenundsechzig, zweiundzwanzig |
| AG-025 | Numeric written out (Spanish) | Word form | treinta y cinco, sesenta y siete, veintidós |
| AG-026 | Numeric written out (other langs) | Word form | trentacinque (IT), 三十五歳 (JP), 서른다섯 (KR) |
| AG-027 | Life stage — child | Pre-teen | infant, toddler, preschooler, elementary-aged, tween |
| AG-028 | Life stage — adolescent | Teen years | teenager, teen, adolescent, high schooler, young person |
| AG-029 | Life stage — young adult | 18-30 | young adult, twentysomething, in his 20s, millennial |
| AG-030 | Life stage — adult | 30-60 | adult, middle-aged, in her prime, prime working age |
| AG-031 | Life stage — senior | 60+ | senior, elderly, geriatric, retiree, OAP (UK), pensioner |
| AG-032 | Life stage — centenarian | 100+ | centenarian, supercentenarian (110+) |
| AG-033 | Decade reference (English) | "in his/her 30s" | in her thirties, in his 40s, in their twenties |
| AG-034 | Decade reference (multilingual) | Various | dans la cinquantaine (FR), in den Fünfzigern (DE), en los treinta (ES), trentenne (IT) |
| AG-035 | Age at event | Specific moment | aged 35 at the time, was 22 when hired, died at age 89 |
| AG-036 | "Years young" (euphemism) | Polite form for elders | 80 years young, 95 years young |
| AG-037 | Minor indicator | Under 18 | minor, juvenile, underage, 16-year-old (minor), mineur(e) (FR), minderjährig (DE) |
| AG-038 | Specific minor ages | Single ages | 16-year-old, 15-year-old, a 14-year-old girl |
| AG-039 | Adult-of-majority indicator | Just-of-age | of legal age, 18+ verified, 21+ (US drinking age) |
| AG-040 | DOB-derived age | Computed from DOB | "born 1985 (currently ~39)", "DOB implies age 42" |
| AG-041 | Comparative age (older than) | Threshold | older than 65, over 21, above 18 |
| AG-042 | Comparative age (younger than) | Threshold | younger than 18, under 30, below 21 |
| AG-043 | Approximate / about | Hedged | about 35, approximately 30, around 25, ~40 |
| AG-044 | Plus/minus age | With error margin | 35 ±2, 30 to 35, late 30s |
| AG-045 | Age in months (infants) | Sub-year | 6 months old, 18 months old, 24 months |
| AG-046 | Age in weeks (newborns) | Very young | 2 weeks old, 6 weeks postnatal |
| AG-047 | Age in days (neonatal) | Days-old | 3 days old, 5-day-old |
| AG-048 | Age in years + months | Combined | 5 years 3 months old, 35.5 years old |
| AG-049 | Age in JSON | Structured | "age": 35, "patient_age": 67, "age_years": 35 |
| AG-050 | Age in KV | Form field | age=35, AGE: 67, patient_age: 42 |
| AG-051 | Age in XML | Markup | <age>35</age>, <patient_age unit="years">67</patient_age> |
| AG-052 | Age in CSV | Tabular | "Smith","John","35","Male" |
| AG-053 | Age in log timestamp | Embedded | "user_age=35", "age:42" |
| AG-054 | Multi-language label "Age:" | Various | Age (EN), Âge (FR), Alter (DE), Edad (ES), Età (IT), Idade (PT), 年齢 (JP), 나이 (KR), 年龄 (ZH), Возраст (RU), Yaş (TR), سن (AR), גיל (HE), อายุ (TH) |
| AG-055 | Age implied from school grade | Educational context | "in 3rd grade (~8-9 yo)", "freshman year (~18)", "Year 7 (~11 yo)" |
| AG-056 | Age implied from role | Professional context | "first-year resident (~25-26)", "tenured professor (typically 40+)" |
| AG-057 | Age implied from years experience | Career context | "30+ years experience (~55+)", "5 years out of college (~27)" |
| AG-058 | Age implied from grandparent status | Relational | "grandmother (typically 50+)", "great-grandparent (typically 70+)" |
| AG-059 | Age range for cohort | Demographic | "Boomers (60-78)", "Gen X (45-60)", "Millennials (30-45)", "Gen Z (15-28)" |
| AG-060 | Age in medical context | Clinical | "Pt age: 35y", "neonate (0-28 days)", "geriatric (65+)", "pediatric (0-17)" |
| AG-061 | Age in legal pleading | Court | "the defendant, age 35, hereby..."; "the minor child, aged 8" |
| AG-062 | Age in HR record | Employment | "Employee age (computed from DOB): 35"; "Age range: 30-39" |
| AG-063 | Age in immigration form | Government | "Age at entry: 28", "Currently aged 35" |
| AG-064 | Age with sibling comparison | Family | "John (35) and his sister Sarah (32)" |
| AG-065 | Age in obituary | Death notice | "passed away at age 89", "died Tuesday, age 67" |
| AG-066 | Age in birthday post | Social media | "Happy 35th birthday!", "She just turned 50!" |
| AG-067 | Age with title | Combined | "35-year-old engineer", "a 67-year-old retiree" |
| AG-068 | "Centenarian"/"Septuagenarian" etc. | Latin-based | septuagenarian (70s), octogenarian (80s), nonagenarian (90s) |
| AG-069 | OCR-distorted age (digits) | Char substitution | 3S years old (S for 5), Z2 yo (Z for 2), l0O years old (l for 1, O for 0) |
| AG-070 | OCR-distorted age unit | Mangled | "35 yeors old" (e for a), "35 yro" (missing letter) |
| AG-071 | Masked / partial age | Privacy-redacted | age: **, ~35 (approximate), age 30+ (over 30) |
| AG-072 | Age anonymized placeholder | Standard generic | age: 35 (placeholder), Sample age 30 |
| AG-073 | Age sentence-boundary | Trailing punctuation | "He is 35 years old.", "Was she 22?", "Aged 35!" |
| AG-074 | Age adjacency-tight | No separator | "John35", "Sarah-22-Engineer", "Smith,John,35,Male" |
| AG-075 | Multiple ages in list | Series | "ages 35, 42, and 67"; "John (35), Sarah (32), Pat (28)" |
| AG-076 | Pregnancy week (gestational age) | Prenatal | "32 weeks pregnant", "gestational age: 28 weeks" |
| AG-077 | Age in dog years / pet age | Pet context | "dog age: 7 (human 49)", "cat age: 12 years" |
| AG-078 | Age with retirement indicator | Life-stage | "retired at 65", "retiring soon (turning 67)" |
| AG-079 | Birthday milestone | Round numbers | "celebrating 50!", "the big 5-0", "turning 40 next month" |
| AG-080 | Age implied from photo / context | Indirect | "the elderly man (likely 70+)", "the child (about 6)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | AG-069, AG-070 |
| Masked / partial / redacted | ✓ | AG-071, AG-072 |
| Multilingual context labels | ✓ | AG-054 |
| Multilingual unit terms | ✓ | AG-006 to AG-018 (13 languages) |
| Verbalized / written out | ✓ | AG-022 to AG-026 |
| In structured data | ✓ | AG-049, AG-050, AG-051, AG-052, AG-053 |
| Adjacency-tight | ✓ | AG-074 |
| Sentence-boundary tricky | ✓ | AG-073 |
| Range / approximate | ✓ | AG-019, AG-020, AG-021, AG-043, AG-044 |
| Sub-year (months/weeks/days) | ✓ | AG-045, AG-046, AG-047, AG-048 |
| Implied / contextual age | ✓ | AG-055, AG-056, AG-057, AG-058, AG-080 |
| Life stage labels | ✓ | AG-027 to AG-032, AG-068 |
| Domain-embedded (medical/legal/HR/obituary) | ✓ | AG-060, AG-061, AG-062, AG-065 |
| Decade / cohort reference | ✓ | AG-033, AG-034, AG-059 |

**Total patterns for Age: 80**

---

## Entity 14: Place_of_Birth

Birthplace — city, region, country, hospital, or facility where a person was born.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| POB-001 | City + Country | Standard birthplace | born in London, England; birthplace: Tokyo, Japan; born in São Paulo, Brazil |
| POB-002 | City only | City alone | born in Paris, native of Berlin, hometown: Boston |
| POB-003 | City + State (US) | US convention | born in Springfield, IL; born in Cambridge, MA; born in Portland, OR |
| POB-004 | Country only | Just country | born in France, hails from Japan, native of Mexico |
| POB-005 | Region / state / prefecture | Sub-national | born in Bavaria, Germany; birthplace: Osaka Prefecture; born in Catalonia |
| POB-006 | Hospital / facility | Specific birth location | born at St. Mary's Hospital, delivered at General Hospital, born at Mount Sinai |
| POB-007 | Hospital with city | Combined | born at St. Mary's Hospital, London; delivered at Massachusetts General, Boston |
| POB-008 | Multilingual "born in" (French) | French | né(e) à Paris, lieu de naissance: Lyon, originaire de Marseille |
| POB-009 | Multilingual "born in" (German) | German | geboren in Berlin, Geburtsort: München, aus Hamburg stammend |
| POB-010 | Multilingual "born in" (Spanish) | Spanish | nacido en Madrid, lugar de nacimiento: Barcelona, natural de Sevilla |
| POB-011 | Multilingual "born in" (Italian) | Italian | nato a Roma, luogo di nascita: Milano, originario di Firenze |
| POB-012 | Multilingual "born in" (Portuguese) | Portuguese | nascido em São Paulo, naturalidade: Lisboa, oriundo de Salvador |
| POB-013 | Multilingual "born in" (Japanese) | Japanese | 東京生まれ, 出生地: 大阪, 出身: 京都 |
| POB-014 | Multilingual "born in" (Korean) | Korean | 출생지: 서울, 서울 출신, 부산에서 태어남 |
| POB-015 | Multilingual "born in" (Chinese) | Chinese | 出生于北京, 籍贯: 上海, 出生地: 广州 |
| POB-016 | Multilingual "born in" (Russian) | Russian | родился в Москве, место рождения: Санкт-Петербург, уроженец Казани |
| POB-017 | Multilingual "born in" (Arabic) | Arabic | ولد في القاهرة, مكان الميلاد: الرياض |
| POB-018 | Multilingual "born in" (Hebrew) | Hebrew | נולד בתל אביב, מקום לידה: ירושלים |
| POB-019 | Multilingual "born in" (Thai) | Thai | เกิดที่กรุงเทพฯ, สถานที่เกิด: เชียงใหม่ |
| POB-020 | Multilingual "born in" (Turkish) | Turkish | İstanbul doğumlu, doğum yeri: Ankara |
| POB-021 | Multilingual "born in" (Polish) | Polish | urodzony w Warszawie, miejsce urodzenia: Kraków |
| POB-022 | Multilingual "born in" (Dutch) | Dutch | geboren in Amsterdam, geboorteplaats: Rotterdam |
| POB-023 | Historical / changed city name | Former name | born in Leningrad (now St. Petersburg), Bombay (now Mumbai), Constantinople (now Istanbul) |
| POB-024 | Historical / changed country | Former country | born in East Germany, born in USSR, born in Yugoslavia, born in Czechoslovakia |
| POB-025 | Born on ship / "at sea" | Unusual location | born at sea aboard the SS Maritime; born aboard Air France flight 123 |
| POB-026 | Born "in transit" / refugee | Special case | born in refugee camp Zaatari, Jordan; born in transit, Greece |
| POB-027 | Birth on military base / overseas | Military family | born at Ramstein Air Base, Germany; born at Yokota AB, Japan |
| POB-028 | Birth in colonial-era name | Colonial-era | born in British India, born in Indo-China, born in the Dutch East Indies |
| POB-029 | Indigenous / tribal context | Cultural | born on Pine Ridge Reservation, born in Navajo Nation |
| POB-030 | Latitude/longitude (rare) | Exact location | "POB: 51.5074° N, 0.1278° W (London)"; born at coordinates 40.7128, -74.0060 |
| POB-031 | POB in passport context | Travel document | "Place of Birth: LONDON / ROYAUME-UNI (passport stamp)", "POB: TOKYO, JPN" |
| POB-032 | POB in immigration form | Government | "Country of Birth: Mexico", "City of Birth: Mexico City" |
| POB-033 | POB in medical record | Clinical | "Patient: Chen, Sarah; POB: Shanghai, China; DOB: 07/22/1990" |
| POB-034 | POB in legal pleading | Court | "Plaintiff John Smith, born March 15, 1985 in Springfield, IL, hereby..." |
| POB-035 | POB in HR / immigration record | Employment | "Employee POB: Mumbai, India; Hire date: 2020-01-15" |
| POB-036 | POB in CV / resume | Personal info section | "Personal: Born in São Paulo, Brazil (1985)" |
| POB-037 | POB in genealogy notation | Family records | "* New York, NY, USA (1985)", "born: Berlin, Germany" |
| POB-038 | POB in JSON | Structured | "place_of_birth": "London, UK", "pob": "Tokyo, Japan", "birthplace": "Springfield, IL" |
| POB-039 | POB in KV | Form field | place_of_birth=London, UK; POB: Tokyo, Japan; birthplace=Springfield |
| POB-040 | POB in XML | Markup | <place_of_birth>London, UK</place_of_birth>, <pob country="JP">Tokyo</pob> |
| POB-041 | POB in CSV | Tabular | "Smith","John","Springfield, IL","Male" |
| POB-042 | POB anonymized placeholder | Standard generic | "POB: [REDACTED]", "born in <City>, <Country>", "place of birth: ******" |
| POB-043 | Masked / partial POB | Privacy-redacted | "born in *** city, France"; "POB: London, **"; "born in Springfield, **" |
| POB-044 | OCR-distorted POB | Char substitution | "born in Lond0n" (O for 0), "POB: Tokyo Japan" (lost comma), "Sprinqfield" (q for g) |
| POB-045 | POB diacritic stripping (OCR) | Lost accents | "born in Sao Paulo" (was São Paulo), "Munchen" (was München), "Zurich" (was Zürich) |
| POB-046 | POB at sentence-boundary | Trailing punctuation | "He was born in Tokyo.", "Was she born in London?", "POB: Springfield, IL." |
| POB-047 | POB adjacency-tight with DOB | No separator | "1985-03-15,Springfield IL"; "John Smith POB:Tokyo,Japan DOB:1985-07-22" |
| POB-048 | Multilingual context label | Various languages | Place of Birth (EN), Lieu de naissance (FR), Geburtsort (DE), Lugar de nacimiento (ES), Luogo di nascita (IT), Local de nascimento (PT), 出生地 (JP), 출생지 (KR), 出生地 (ZH), Место рождения (RU), Doğum yeri (TR), مكان الميلاد (AR), מקום לידה (HE), สถานที่เกิด (TH) |
| POB-049 | POB on birth certificate | Official document | "Place of Birth: Springfield, IL, USA; Hospital: Mercy Hospital" |
| POB-050 | Birth in major historical event | Context | "born during the Berlin Wall's fall, in Berlin"; "born during partition of India" |
| POB-051 | POB with mother's residence | Maternal context | "born to mother residing in Boston, hospital: Boston General" |
| POB-052 | POB with multiple cultural names | Bilingual | "born in Kyiv (Ukraine) / Kiev (Russian)"; "Mumbai / Bombay" |
| POB-053 | Born in territory/protectorate | Special status | "born in Puerto Rico (US territory)", "born in Hong Kong (Special Administrative Region)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | POB-044, POB-045 |
| Masked / partial / redacted | ✓ | POB-042, POB-043 |
| Multilingual context labels | ✓ | POB-048 |
| Multilingual "born in" verbs | ✓ | POB-008 to POB-022 (15 languages) |
| Script variations | ✓ | POB-013 to POB-019 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | POB-038, POB-039, POB-040, POB-041 |
| Adjacency-tight | ✓ | POB-047 |
| Sentence-boundary tricky | ✓ | POB-046 |
| Domain-embedded (passport/medical/HR/legal/CV) | ✓ | POB-031 to POB-037 |
| Historical / former-name variants | ✓ | POB-023, POB-024, POB-028, POB-052 |
| Special locations (sea, base, refugee, indigenous) | ✓ | POB-025, POB-026, POB-027, POB-029 |
| Coordinates | ✓ | POB-030 |

**Total patterns for Place_of_Birth: 53**

---

## Entity 15: Gender

Gender or sex as recorded on forms, documents, or records. Includes binary, non-binary, legal-vs-identity distinctions.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| GN-001 | Binary M / F | Single letter | M, F, m, f |
| GN-002 | Binary written out (English) | Full word | Male, Female |
| GN-003 | Binary lowercase | Lowercase | male, female |
| GN-004 | Binary all-caps | Uppercase | MALE, FEMALE |
| GN-005 | Binary mixed case (typo) | Inconsistent | male, Female, MaLe (typos) |
| GN-006 | Non-binary "X" | Third option | X (passport), Sex: X |
| GN-007 | Non-binary written out | Categorical | Non-binary, NB, non-binary, Genderqueer, Gender-fluid |
| GN-008 | "Other" / "Prefer not to say" | Form options | Other, Prefer not to say, Decline to state, Unspecified |
| GN-009 | Diverse (German legal) | German non-binary | divers, Divers, "d" (Germany legal third gender since 2018) |
| GN-010 | "Inter*" / Intersex | Intersex category | Intersex, Inter*, Variations in sex characteristics |
| GN-011 | Multilingual binary (FR) | French | masculin / féminin, M / F, Homme / Femme |
| GN-012 | Multilingual binary (DE) | German | männlich / weiblich, m / w, Herr / Frau |
| GN-013 | Multilingual binary (ES) | Spanish | masculino / femenino, hombre / mujer, M / F |
| GN-014 | Multilingual binary (IT) | Italian | maschio / femmina, M / F, uomo / donna |
| GN-015 | Multilingual binary (PT) | Portuguese | masculino / feminino, M / F, homem / mulher |
| GN-016 | Multilingual binary (JP) | Japanese | 男性 / 女性, 男 / 女, M/F |
| GN-017 | Multilingual binary (KR) | Korean | 남성 / 여성, 남 / 여, 남자 / 여자 |
| GN-018 | Multilingual binary (ZH) | Chinese | 男 / 女, 男性 / 女性 |
| GN-019 | Multilingual binary (RU) | Russian | мужской / женский, муж / жен, м / ж |
| GN-020 | Multilingual binary (AR) | Arabic | ذكر / أنثى, ذ / أ |
| GN-021 | Multilingual binary (HE) | Hebrew | זכר / נקבה, ז / נ |
| GN-022 | Multilingual binary (TH) | Thai | ชาย / หญิง, ช / ญ |
| GN-023 | Multilingual binary (TR) | Turkish | Erkek / Kadın, E / K |
| GN-024 | Multilingual binary (PL) | Polish | mężczyzna / kobieta, M / K |
| GN-025 | Multilingual binary (CZ) | Czech | muž / žena, M / Ž |
| GN-026 | Multilingual binary (NL) | Dutch | man / vrouw, M / V |
| GN-027 | Multilingual binary (SE) | Swedish | man / kvinna, M / K |
| GN-028 | Multilingual binary (FI) | Finnish | mies / nainen, M / N |
| GN-029 | Multilingual binary (NO) | Norwegian | mann / kvinne, M / K |
| GN-030 | Multilingual binary (DK) | Danish | mand / kvinde, M / K |
| GN-031 | Multilingual binary (HU) | Hungarian | férfi / nő, F / N |
| GN-032 | Title-inferred (English) | From honorific | Mr. = M, Mrs./Ms. = F, Mx. = NB, Dr. = neutral |
| GN-033 | Title-inferred (multilingual) | Various | Herr/Frau (DE), M./Mme (FR), Don/Doña (ES), Signor/Signora (IT) |
| GN-034 | Pronoun-inferred (he/him) | Pronoun marker | uses he/him pronouns, he/him, preferred pronouns: he/him |
| GN-035 | Pronoun-inferred (she/her) | Pronoun marker | uses she/her pronouns, she/her, preferred pronouns: she/her |
| GN-036 | Pronoun-inferred (they/them) | NB pronouns | uses they/them pronouns, they/them, preferred pronouns: they/them |
| GN-037 | Pronoun-inferred (neopronouns) | Modern variants | xe/xem, ze/zir, ey/em |
| GN-038 | Pronoun with multiple options | Combined | he/they, she/they, any pronouns |
| GN-039 | Sex assigned at birth (AMAB/AFAB) | Trans context | AFAB (assigned female at birth), AMAB, assigned male at birth |
| GN-040 | Legal vs identity gender (form) | Distinct fields | Legal Sex: M; Gender Identity: Non-binary |
| GN-041 | Trans identifier | Trans status | trans woman, trans man, transgender, transfeminine, transmasculine |
| GN-042 | Cis identifier | Cis status | cisgender, cis woman, cis man |
| GN-043 | ISO 5218 numeric coding | International standard | 0 = unknown, 1 = male, 2 = female, 9 = not applicable |
| GN-044 | HL7 / FHIR coding | Medical standard | male, female, other, unknown (FHIR AdministrativeGender) |
| GN-045 | Single-letter abbreviations (intl) | One-char codes | M/F (EN), H/F (FR), M/W (DE), 男/女 (JP/ZH/KR) |
| GN-046 | Form / KV gender | Field format | Gender: M, Sex: Female, gender="male", SEX: F |
| GN-047 | Gender in JSON | Structured | "gender": "Male", "sex": "F", "gender_identity": "non-binary" |
| GN-048 | Gender in XML | Markup | <gender>Female</gender>, <sex>M</sex> |
| GN-049 | Gender in CSV | Tabular | "Smith","John","M","35" |
| GN-050 | Gender in log / audit | Embedded | user_gender=female, gender:M, AUDIT: gender=NonBinary |
| GN-051 | Gender symbols | Mars/Venus symbols | ♂ (male), ♀ (female), ⚥ (intersex), ⚧ (transgender), ⚪ (neuter) |
| GN-052 | OCR-distorted gender (single letter) | Char substitution | M as "lvl" or "lV1", F as "P" or "E" (poor OCR), 0 (zero for "M"/"F" misread) |
| GN-053 | OCR-distorted gender (word) | Mangled | "Maie" (was Male), "Femaie", "MaIe" (capital I for l) |
| GN-054 | Masked / partial gender | Privacy-redacted | Gender: *, Sex: [REDACTED], gender: ** |
| GN-055 | Gender anonymized placeholder | Standard generic | Gender: X (placeholder), Sex: --, Gender: NA |
| GN-056 | "Sex" vs "Gender" labels | Distinguished | Sex: F (biological); Gender: Female (identity); Legal Sex: M |
| GN-057 | Gender on driver's license | Document context | "Sex: F" (US DL), "Sex: M" (US passport) |
| GN-058 | Gender on medical chart | Clinical | "Pt: Chen, Sarah; Sex: F; DOB: 1990-07-22" |
| GN-059 | Gender in HR record | Employment | "Employee gender: Male"; "Self-ID gender: Non-binary" |
| GN-060 | Gender in diversity report | DEI context | "Workforce gender breakdown: 45% F, 50% M, 5% Non-binary" |
| GN-061 | Multilingual "Gender:" label | Various languages | Gender (EN), Genre / Sexe (FR), Geschlecht (DE), Género / Sexo (ES), Genere / Sesso (IT), Gênero (PT), 性別 (JP), 성별 (KR), 性别 (ZH), Пол (RU), Cinsiyet (TR), جنس (AR), מין (HE), เพศ (TH) |
| GN-062 | Gender as code in transmission | EDI / X12 | "GEN:M", "SX:F", "Gender_Code: 2" |
| GN-063 | Gender on passport (X option) | New gender markers | "Sex: X" (US passport since 2022), "Sex: F", "Sex: M" |
| GN-064 | Adjacency-tight | No separator | "John Smith,35,M,Engineer"; "Sarah Chen,F,32" |
| GN-065 | Gender sentence-boundary | Trailing punctuation | "Gender: M.", "Was the patient female?", "She identifies as non-binary." |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | GN-052, GN-053 |
| Masked / partial / redacted | ✓ | GN-054, GN-055 |
| Multilingual context labels | ✓ | GN-061 |
| Multilingual binary terms | ✓ | GN-011 to GN-031 (21 languages) |
| Script variations | ✓ | GN-016 to GN-022 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | GN-046, GN-047, GN-048, GN-049, GN-050 |
| Adjacency-tight | ✓ | GN-064 |
| Sentence-boundary tricky | ✓ | GN-065 |
| Domain-embedded (medical/HR/passport/DEI) | ✓ | GN-057, GN-058, GN-059, GN-060 |
| Non-binary / modern identifiers | ✓ | GN-006, GN-007, GN-009, GN-010, GN-037 to GN-042 |
| Coding systems (ISO, HL7, X12) | ✓ | GN-043, GN-044, GN-062 |
| Title-inferred / pronoun-inferred | ✓ | GN-032, GN-033, GN-034 to GN-038 |
| Sex-vs-Gender distinction | ✓ | GN-040, GN-056 |
| Symbol representations | ✓ | GN-051 |
| Case variations | ✓ | GN-001, GN-002, GN-003, GN-004, GN-005 |

**Total patterns for Gender: 65**

---

## Entity 16: Marital_Status

Marriage / civil partnership / relationship status. Includes binary categories, civil partnerships, religious marriages, polyamorous status, and culturally specific arrangements.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| MS-001 | Single (English) | Never-married standard | Single, single, SINGLE |
| MS-002 | Married (English) | Currently married | Married, married, MARRIED |
| MS-003 | Divorced (English) | Marriage dissolved | Divorced, divorced, DIVORCED |
| MS-004 | Widowed (English) | Surviving spouse | Widowed, Widow, Widower, surviving spouse |
| MS-005 | Separated (English) | Legally / informally separated | Separated, legally separated, in separation |
| MS-006 | Engaged (English) | Pre-marriage commitment | Engaged, betrothed, affianced |
| MS-007 | Civil partnership | Legal partnership (non-marriage) | Civil Partner, Civil Union, Registered Partnership |
| MS-008 | Domestic partnership | US/Canadian variant | Domestic Partner, Domestic Partnership (registered) |
| MS-009 | PACS (France) | French civil pact | PACS (Pacte civil de solidarité), pacsé(e) |
| MS-010 | Cohabitation | Living together unmarried | Cohabiting, Living with partner, Common-law, in a relationship |
| MS-011 | Common-law marriage | Legal recognition w/o ceremony | Common-law spouse, Common-law wife/husband, "common-law" |
| MS-012 | Annulled | Marriage voided | Annulled, marriage annulled, annulment granted |
| MS-013 | Remarried | Subsequent marriage | Remarried, on my second marriage, third marriage |
| MS-014 | "It's complicated" | Informal Facebook-era | It's complicated, "complicated relationship status" |
| MS-015 | Polygamous (where legal) | Multiple spouses | Polygamous, in a polygamous marriage, plural marriage |
| MS-016 | Polyamorous | Multiple consenting partners | Polyamorous, poly, in a polyamorous relationship |
| MS-017 | Religious marriage only | No civil registration | Religiously married, married in church only, nikah-only, kosher-only marriage |
| MS-018 | Civil marriage only | No religious ceremony | Civilly married, civil-only marriage, marié à la mairie |
| MS-019 | In a relationship | Boyfriend / girlfriend | In a relationship, dating, has a boyfriend/girlfriend, partnered |
| MS-020 | Estranged | Married but apart | Estranged spouse, estranged from spouse, married but estranged |
| MS-021 | Engaged-to-be-married | Date set | Engaged (wedding date set), about to be married, fiancé(e) since 2024 |
| MS-022 | French — célibataire | French | célibataire, jamais marié(e) |
| MS-023 | French — marié(e) | French | marié, mariée, marié(e) |
| MS-024 | French — divorcé(e) | French | divorcé, divorcée, divorcé(e) |
| MS-025 | French — veuf / veuve | French widowed | veuf (m), veuve (f), veuf/veuve |
| MS-026 | French — séparé(e) | French separated | séparé, séparée, en instance de divorce |
| MS-027 | French — pacsé(e) | French civil union | pacsé, pacsée, en PACS, pacsé(e) |
| MS-028 | German — ledig | German single | ledig, unverheiratet |
| MS-029 | German — verheiratet | German married | verheiratet, frisch verheiratet |
| MS-030 | German — geschieden | German divorced | geschieden, frisch geschieden |
| MS-031 | German — verwitwet | German widowed | verwitwet, Witwer (m), Witwe (f) |
| MS-032 | German — getrennt lebend | German separated | getrennt lebend, in Trennung |
| MS-033 | German — eingetragene Partnerschaft | German civil partnership | eingetragene Lebenspartnerschaft |
| MS-034 | Spanish — soltero/a | Spanish single | soltero, soltera, soltero/a |
| MS-035 | Spanish — casado/a | Spanish married | casado, casada, casado/a |
| MS-036 | Spanish — divorciado/a | Spanish divorced | divorciado, divorciada, divorciado/a |
| MS-037 | Spanish — viudo/a | Spanish widowed | viudo, viuda, viudo/a |
| MS-038 | Spanish — separado/a | Spanish separated | separado, separada, en proceso de divorcio |
| MS-039 | Spanish — pareja de hecho | Spanish civil partnership | pareja de hecho, unión de hecho, pareja registrada |
| MS-040 | Italian — celibe / nubile | Italian single (gendered) | celibe (m), nubile (f), single |
| MS-041 | Italian — coniugato / coniugata | Italian married | coniugato, coniugata, sposato/a |
| MS-042 | Italian — divorziato/a | Italian divorced | divorziato, divorziata |
| MS-043 | Italian — vedovo / vedova | Italian widowed | vedovo, vedova |
| MS-044 | Italian — separato/a | Italian separated | separato, separata, separato/a |
| MS-045 | Italian — unito/a civilmente | Italian civil union | unito civilmente, unita civilmente, unione civile |
| MS-046 | Portuguese (PT/BR) — solteiro/a | Portuguese single | solteiro, solteira, solteiro/a |
| MS-047 | Portuguese (PT/BR) — casado/a | Portuguese married | casado, casada, casado/a |
| MS-048 | Portuguese (PT/BR) — divorciado/a | Portuguese divorced | divorciado, divorciada |
| MS-049 | Portuguese (PT/BR) — viúvo/a | Portuguese widowed | viúvo, viúva |
| MS-050 | Portuguese (PT/BR) — união estável | BR civil union | união estável, em união estável |
| MS-051 | Dutch — ongehuwd | Dutch single | ongehuwd, alleenstaand |
| MS-052 | Dutch — gehuwd | Dutch married | gehuwd, getrouwd |
| MS-053 | Dutch — gescheiden | Dutch divorced | gescheiden |
| MS-054 | Dutch — weduwe / weduwnaar | Dutch widowed | weduwe, weduwnaar |
| MS-055 | Dutch — geregistreerd partnerschap | Dutch civil partnership | geregistreerd partnerschap, partner |
| MS-056 | Swedish — ogift | Swedish single | ogift, singel |
| MS-057 | Swedish — gift | Swedish married | gift, gift man, gift kvinna |
| MS-058 | Swedish — skild | Swedish divorced | skild, frånskild |
| MS-059 | Swedish — änka / änkling | Swedish widowed | änka, änkling |
| MS-060 | Swedish — sambo | Swedish cohabiting | sambo (legal cohabitation status) |
| MS-061 | Finnish — naimaton | Finnish single | naimaton, naimaton henkilö |
| MS-062 | Finnish — naimisissa | Finnish married | naimisissa, avioliitossa |
| MS-063 | Finnish — eronnut | Finnish divorced | eronnut |
| MS-064 | Finnish — leski | Finnish widowed | leski |
| MS-065 | Finnish — avoliitto | Finnish common-law | avoliitto, avopari |
| MS-066 | Russian — холост / холостой | Russian single (male) | холост, холостой, не женат |
| MS-067 | Russian — незамужем | Russian single (female) | незамужем, не замужем |
| MS-068 | Russian — женат / замужем | Russian married | женат (m), замужем (f) |
| MS-069 | Russian — разведён / разведена | Russian divorced | разведён, разведена, в разводе |
| MS-070 | Russian — вдовец / вдова | Russian widowed | вдовец, вдова |
| MS-071 | Polish — kawaler / panna | Polish single (gendered) | kawaler (m), panna (f), wolny stan |
| MS-072 | Polish — żonaty / mężatka | Polish married | żonaty (m), mężatka (f) |
| MS-073 | Polish — rozwiedziony/a | Polish divorced | rozwiedziony, rozwiedziona |
| MS-074 | Polish — wdowiec / wdowa | Polish widowed | wdowiec, wdowa |
| MS-075 | Czech — svobodný/á | Czech single | svobodný, svobodná |
| MS-076 | Czech — ženatý / vdaná | Czech married | ženatý (m), vdaná (f) |
| MS-077 | Czech — rozvedený/á | Czech divorced | rozvedený, rozvedená |
| MS-078 | Czech — vdovec / vdova | Czech widowed | vdovec, vdova |
| MS-079 | Hungarian — egyedülálló | Hungarian single | egyedülálló, hajadon (f), nőtlen (m) |
| MS-080 | Hungarian — házas | Hungarian married | házas, nős (m), férjezett (f) |
| MS-081 | Hungarian — elvált | Hungarian divorced | elvált |
| MS-082 | Hungarian — özvegy | Hungarian widowed | özvegy, özvegyasszony |
| MS-083 | Turkish — bekâr | Turkish single | bekâr, bekar |
| MS-084 | Turkish — evli | Turkish married | evli |
| MS-085 | Turkish — boşanmış | Turkish divorced | boşanmış |
| MS-086 | Turkish — dul | Turkish widowed | dul |
| MS-087 | Japanese — 独身 / 未婚 | Japanese single | 独身 (single), 未婚 (unmarried) |
| MS-088 | Japanese — 既婚 / 結婚 | Japanese married | 既婚, 結婚, 結婚しています |
| MS-089 | Japanese — 離婚 | Japanese divorced | 離婚, バツイチ (informal) |
| MS-090 | Japanese — 死別 / 寡婦 / 寡夫 | Japanese widowed | 死別, 寡婦 (f), 寡夫 (m) |
| MS-091 | Korean — 미혼 | Korean single | 미혼, 결혼 안 함 |
| MS-092 | Korean — 기혼 | Korean married | 기혼, 결혼함 |
| MS-093 | Korean — 이혼 | Korean divorced | 이혼, 이혼함 |
| MS-094 | Korean — 사별 | Korean widowed | 사별, 사별함 |
| MS-095 | Chinese — 未婚 / 单身 | Chinese single | 未婚 (unmarried), 单身 (single) |
| MS-096 | Chinese — 已婚 | Chinese married | 已婚, 结婚 |
| MS-097 | Chinese — 离婚 / 离异 | Chinese divorced | 离婚, 离异 |
| MS-098 | Chinese — 丧偶 | Chinese widowed | 丧偶 |
| MS-099 | Arabic — أعزب / عزباء | Arabic single | أعزب (m), عزباء (f) |
| MS-100 | Arabic — متزوج / متزوجة | Arabic married | متزوج (m), متزوجة (f) |
| MS-101 | Arabic — مطلق / مطلقة | Arabic divorced | مطلق (m), مطلقة (f) |
| MS-102 | Arabic — أرمل / أرملة | Arabic widowed | أرمل (m), أرملة (f) |
| MS-103 | Hebrew — רווק / רווקה | Hebrew single | רווק (m), רווקה (f) |
| MS-104 | Hebrew — נשוי / נשואה | Hebrew married | נשוי (m), נשואה (f) |
| MS-105 | Hebrew — גרוש / גרושה | Hebrew divorced | גרוש (m), גרושה (f) |
| MS-106 | Hebrew — אלמן / אלמנה | Hebrew widowed | אלמן (m), אלמנה (f) |
| MS-107 | Thai — โสด | Thai single | โสด |
| MS-108 | Thai — สมรส | Thai married | สมรส, แต่งงานแล้ว |
| MS-109 | Thai — หย่า | Thai divorced | หย่า, หย่าร้าง |
| MS-110 | Thai — หม้าย | Thai widowed | หม้าย |
| MS-111 | Danish — ugift | Danish single | ugift, single |
| MS-112 | Danish — gift | Danish married | gift |
| MS-113 | Norwegian — ugift | Norwegian single | ugift, enslig |
| MS-114 | Norwegian — gift | Norwegian married | gift |
| MS-115 | Form / KV format | Form field | Marital Status: Married, Status: Single, RELATIONSHIP: Divorced |
| MS-116 | Form / KV (multilingual) | Multi-lang form field | État civil: marié (FR), Familienstand: verheiratet (DE), Estado civil: casado (ES) |
| MS-117 | Title-inferred (Mrs.) | From honorific (married) | Mrs. (married), Mme (FR married), Frau (DE adult woman), Sra. (ES married) |
| MS-118 | Title-inferred (Miss) | From honorific (single F) | Miss (unmarried F), Mlle (FR unmarried), Fräulein (DE archaic), Srta. (ES single F) |
| MS-119 | Title-inferred (Ms.) | Unspecified | Ms. (marital status not indicated) |
| MS-120 | Title-inferred (Mx.) | Gender-neutral | Mx. (gender-neutral, marital status undetermined) |
| MS-121 | Spouse reference (direct) | Indirect indicator | "married to John Smith", "wife of Maria", "husband of Sarah Chen" |
| MS-122 | Spouse reference (multilingual) | Various languages | époux/épouse (FR), Ehemann/Ehefrau (DE), marido/esposa (ES/PT), 夫/妻 (JP) |
| MS-123 | Ex-spouse reference | Past relationship | "ex-wife", "ex-husband", "former spouse", "his ex" |
| MS-124 | Marriage date / anniversary | Date context | "Married since 2010", "married on June 15, 2010", "10th wedding anniversary" |
| MS-125 | Children indicator | Family context | "married with 2 children", "Single father", "Single mother of 3" |
| MS-126 | "Mrs." vs "Ms." preference | Self-identification | "she prefers Ms.", "uses Mrs. Chen", "prefers to be called Ms." |
| MS-127 | Cultural marriage forms (Hindu) | Cultural | "Hindu marriage performed", "Arya Samaj marriage", "registered Hindu marriage" |
| MS-128 | Cultural marriage forms (Islamic) | Cultural | "Nikah completed", "Islamic marriage contract signed" |
| MS-129 | Cultural marriage forms (Jewish) | Cultural | "Ketubah signed", "Jewish wedding under chuppah" |
| MS-130 | Cultural marriage forms (Sikh) | Cultural | "Anand Karaj performed", "Sikh marriage" |
| MS-131 | Arranged marriage | Cultural | "arranged marriage", "love marriage" (contrast) |
| MS-132 | Civil partnership multilingual | Various languages | PACS (FR), unione civile (IT), Lebenspartnerschaft (DE), unión de hecho (ES) |
| MS-133 | Trial separation | Pre-divorce | "in trial separation", "temporary separation", "trying separation" |
| MS-134 | Open relationship / marriage | Modern arrangement | "in an open marriage", "open relationship", "non-monogamous" |
| MS-135 | Marital status in JSON | Structured | "marital_status": "Married", "civil_status": "Single" |
| MS-136 | Marital status in KV | Form field | marital_status=Married, civil_status=Divorced, relationship_status=Engaged |
| MS-137 | Marital status in XML | Markup | <marital_status>Married</marital_status>, <civilStatus>Single</civilStatus> |
| MS-138 | Marital status in CSV | Tabular | "Smith","John","M","35","Married" |
| MS-139 | Marital status in log | Audit context | marital_status:Married, user.marital_status=Single |
| MS-140 | Multilingual context label | "Marital Status:" various | Marital Status (EN), État civil (FR), Familienstand (DE), Estado civil (ES/PT), Stato civile (IT), 婚姻状況 (JP), 결혼 상태 (KR), 婚姻状况 (ZH), Семейное положение (RU), Medeni Durum (TR), الحالة الاجتماعية (AR), מצב משפחתי (HE) |
| MS-141 | OCR-distorted (letter-confusion) | Char substitution | Marrled (was Married), Sinqle (q for g), Dlvorced (l for i), Wid0wed (0 for o) |
| MS-142 | OCR-distorted (diacritic stripping) | Lost accents | celibataire (was célibataire), separe (was séparé), divorcie (was divorcée) |
| MS-143 | Masked / partial marital status | Privacy-redacted | Marital Status: ***, Status: [REDACTED], civil_status=**** |
| MS-144 | Marital status anonymized placeholder | Standard generic | Status: Married (sample), [MARITAL_STATUS] |
| MS-145 | Marital status sentence-boundary | Trailing punctuation | "He is married.", "Is she single?", "Status: Divorced." |
| MS-146 | Marital status adjacency-tight | No separator | "John,35,M,Married,Engineer", "Sarah-Single-32" |
| MS-147 | Multiple statuses in life history | Timeline | "Single (1990-2010), Married (2010-2018), Divorced (2018-present)" |
| MS-148 | Domain-embedded (medical / patient) | Clinical | "Patient: Chen, Sarah; Marital Status: Married; Spouse: David Williams" |
| MS-149 | Domain-embedded (immigration form) | Government | "I-485 Marital Status: Married; Date of marriage: 2015-06-15" |
| MS-150 | Domain-embedded (HR record) | Employment | "Employee marital status: Married; Beneficiary: Sarah Chen (spouse)" |
| MS-151 | Domain-embedded (tax filing) | Tax | "Filing Status: Married Filing Jointly", "Single", "Head of Household" |
| MS-152 | Inferred from joint accounts | Indirect | "joint bank account with spouse John Smith"; "joint tax return" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | MS-141, MS-142 |
| Masked / partial / redacted | ✓ | MS-143, MS-144 |
| Multilingual context labels | ✓ | MS-116, MS-140 |
| Multilingual binary categories | ✓ | MS-022 to MS-114 (covers 21+ languages with gendered variants) |
| Script variations | ✓ | MS-087 to MS-110 (JP, KR, ZH, AR, HE, TH) |
| In structured data | ✓ | MS-135, MS-136, MS-137, MS-138, MS-139 |
| Adjacency-tight | ✓ | MS-146 |
| Sentence-boundary tricky | ✓ | MS-145 |
| Domain-embedded (medical/HR/immigration/tax) | ✓ | MS-148, MS-149, MS-150, MS-151 |
| Cultural / religious variants | ✓ | MS-127, MS-128, MS-129, MS-130, MS-131 |
| Modern non-binary statuses | ✓ | MS-014, MS-016, MS-134 |
| Title-inferred | ✓ | MS-117, MS-118, MS-119, MS-120 |
| Spouse-reference inferred | ✓ | MS-121, MS-122, MS-123 |
| Gendered linguistic variants | ✓ | MS-022 to MS-114 (most languages have gendered forms) |

**Total patterns for Marital_Status: 152**

---

## Entity 17: Nationality

A person's nationality, ethnic origin, national identity. Distinct from Citizenship_Status (legal) — Nationality is about identity / origin / passport-issuing country.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| NA-001 | Adjectival demonym (English) | Standard | American, British, French, German, Japanese, Italian, Spanish, Mexican, Brazilian, Canadian, Australian, Indian, Chinese, Korean, Russian |
| NA-002 | Adjectival demonym (less common) | Other countries | Algerian, Argentine, Egyptian, Ethiopian, Greek, Indonesian, Kenyan, Lebanese, Moroccan, Nigerian, Pakistani, Peruvian, Portuguese, Swedish, Thai, Turkish, Ukrainian, Vietnamese |
| NA-003 | Noun form ("a/an + nationality") | Indefinite article | an American, a Japanese citizen, a Frenchman, a Frenchwoman, an Australian |
| NA-004 | Plural / collective form | Group reference | the French, Americans, Japanese (uncountable), the Spanish, Italians |
| NA-005 | Demonym in local language (FR) | French | français (m), française (f), de nationalité française |
| NA-006 | Demonym in local language (DE) | German | deutsch, Deutscher (m), Deutsche (f), deutscher Staatsbürger |
| NA-007 | Demonym in local language (ES) | Spanish | español, española, mexicano/a, argentino/a, colombiano/a |
| NA-008 | Demonym in local language (IT) | Italian | italiano, italiana, di nazionalità italiana |
| NA-009 | Demonym in local language (PT) | Portuguese | português, portuguesa, brasileiro/a, lusitano/a |
| NA-010 | Demonym in local language (JP) | Japanese | 日本人, 日本国民, アメリカ人 |
| NA-011 | Demonym in local language (KR) | Korean | 한국인, 미국인, 일본인, 중국인 |
| NA-012 | Demonym in local language (ZH) | Chinese | 中国人, 美国人, 日本人, 韩国人 |
| NA-013 | Demonym in local language (RU) | Russian | россиянин (m), россиянка (f), русский (ethnic), американец, англичанин |
| NA-014 | Demonym in local language (AR) | Arabic | عربي (Arab), سعودي (Saudi), مصري (Egyptian), أمريكي (American), بريطاني (British) |
| NA-015 | Demonym in local language (HE) | Hebrew | ישראלי (m), ישראלית (f), אמריקאי, צרפתי |
| NA-016 | Demonym in local language (TH) | Thai | ไทย (Thai), อเมริกัน (American), ญี่ปุ่น (Japanese) |
| NA-017 | Demonym in local language (TR) | Turkish | Türk, Türk vatandaşı, Amerikalı, Alman, Fransız |
| NA-018 | Demonym in local language (NL) | Dutch | Nederlands, Nederlandse, Belg, Engelse, Duitser |
| NA-019 | Demonym in local language (PL) | Polish | Polak (m), Polka (f), Niemiec, Francuz, Amerykanin |
| NA-020 | Demonym in local language (CZ) | Czech | Čech (m), Češka (f), Němec, Američan, Francouz |
| NA-021 | Demonym in local language (HU) | Hungarian | magyar, magyar állampolgár, amerikai, német |
| NA-022 | Demonym in local language (SE/NO/DK/FI) | Nordic | svensk, norsk, dansk, suomalainen, finne |
| NA-023 | Dual / multiple nationality (English) | Multiple | Japanese-American, Franco-German, dual British-Australian, dual citizen UK-Italy |
| NA-024 | Dual / multiple (hyphenated identity) | Identity form | Mexican-American, Korean-Canadian, Iranian-American, Indo-American |
| NA-025 | Triple nationality | Multiple | "triple citizen US/UK/Italy", "tri-national" |
| NA-026 | Ethnic / cultural identity (Hispanic/Latino) | Pan-ethnic | Hispanic, Latino/a, Latinx, Latine, Chicano/a |
| NA-027 | Ethnic / cultural identity (Asian) | Pan-ethnic | Asian, Asian-American, South Asian, East Asian, Southeast Asian |
| NA-028 | Ethnic / cultural identity (Black/African) | Pan-ethnic | Black, African-American, Afro-Caribbean, Afro-Latino, Afro-European |
| NA-029 | Ethnic / cultural identity (Indigenous) | Indigenous peoples | Indigenous Australian, Aboriginal, First Nations, Native American, Indigenous, Métis, Inuit |
| NA-030 | Specific tribal affiliation (US) | Tribal | Navajo, Cherokee, Lakota, Hopi, Apache, Choctaw, Iroquois, Pueblo |
| NA-031 | Specific indigenous (other countries) | Various | Maori (NZ), Sami (NO/SE/FI), Romani/Roma, Quechua (Peru), Mapuche (Chile) |
| NA-032 | Stateless | No nationality | stateless person, no nationality, apatride (FR), Staatenloser (DE), apolide (IT) |
| NA-033 | Refugee (origin context) | Forced migration | Syrian refugee, Afghan refugee, Ukrainian refugee, displaced person |
| NA-034 | "Nationality:" form field | Form context | Nationality: Japanese, Nationality: British, NATIONALITY: GERMAN |
| NA-035 | Multilingual "Nationality:" label | Various languages | Nationalité (FR), Staatsangehörigkeit (DE), Nacionalidad (ES), Nazionalità (IT), Nacionalidade (PT), 国籍 (JP), 국적 (KR), 国籍 (ZH), Гражданство (RU), Uyruğu (TR), الجنسية (AR), אזרחות (HE), สัญชาติ (TH), Obywatelstwo (PL), Állampolgárság (HU) |
| NA-036 | Passport-derived nationality | Travel doc | "holder of a Japanese passport", "passport nationality: German", "carries US passport" |
| NA-037 | Diaspora / heritage | Ancestral reference | of Italian descent, Korean heritage, third-generation Mexican-American, partially Irish |
| NA-038 | Informal / colloquial demonyms | Casual | Aussie, Brit, Yank, Kiwi, Canuck, Brazucas, Tico (Costa Rican) |
| NA-039 | Country-of-origin reference | Indirect | originally from Japan, comes from Brazil, hails from Egypt |
| NA-040 | Born in but lives elsewhere | Origin + residence | born in India, raised in US; Japanese-born, Australian resident |
| NA-041 | Hyphenated identity (X-American) | Identity hyphenation | African-American, Italian-American, Chinese-American, Cuban-American |
| NA-042 | British subjects (historical) | Pre-1983 UK status | British subject, British overseas territories citizen, British national (overseas) |
| NA-043 | EU citizenship + national | EU dual concept | EU citizen (national of France), Italian and EU citizen |
| NA-044 | Soviet-era nationality | Historical | former Soviet citizen, USSR-born, Soviet émigré |
| NA-045 | Yugoslav-era nationality | Historical | Yugoslav, former Yugoslav, ex-Yugoslav |
| NA-046 | Czechoslovak (pre-1993) | Historical | Czechoslovak, former Czechoslovak |
| NA-047 | "Of [country] origin" | Origin phrasing | of Mexican origin, of Egyptian origin, of Korean origin |
| NA-048 | Nationality in passport stamp | Travel doc | "Nationality: GBR (passport)", "DEU passport stamp" |
| NA-049 | ISO 3166-1 country code | 2- or 3-letter | nationality: US, citizenship: GB, nation: DE, country: JP |
| NA-050 | Three-letter ISO | Alpha-3 | USA, GBR, DEU, JPN, BRA, FRA |
| NA-051 | Pre-Brexit "European" | EU vs UK | "European" (pre-Brexit UK context), "Continental European" |
| NA-052 | Linguistic / cultural nation | Sub-national | Welsh, Scottish, Catalan, Basque, Kurdish, Tibetan, Quebecois |
| NA-053 | Non-state / unrecognized | Special | Palestinian, Kurdish, Tibetan, Taiwanese (politically contested), Catalan |
| NA-054 | Indigenous nation (Canada) | First Nations | Cree, Ojibwe, Mohawk, Haida, Métis (recognized in Canada) |
| NA-055 | Maori / Pasifika | NZ context | Maori, Pasifika, Pacific Islander, Polynesian, Melanesian, Micronesian |
| NA-056 | Romani / Sinti | Pan-European | Romani, Roma, Sinti, Travelers |
| NA-057 | Jewish (ethnic vs religious) | Ambiguous identity | Jewish (ethnic), Jewish heritage, of Jewish descent |
| NA-058 | Nationality with hyphen-multi-cultural | Multi-hyphen | Chinese-American-Canadian, Trinidadian-British, etc. |
| NA-059 | Nationality in JSON | Structured | "nationality": "American", "nationality": "Japanese", "country_of_nationality": "DE" |
| NA-060 | Nationality in KV | Form field | nationality=American, country_of_nationality=DE, NATIONALITY: BR |
| NA-061 | Nationality in XML | Markup | <nationality>American</nationality>, <nationality_code>US</nationality_code> |
| NA-062 | Nationality in CSV | Tabular | "Smith","John","M","35","American","US" |
| NA-063 | Nationality in passport JSON | Structured travel | "passport_nationality": "USA", "passport_country": "United States" |
| NA-064 | Embedded in immigration form | Visa application | "Country of Nationality: India"; "I-94 Nationality: IND" |
| NA-065 | Embedded in HR record | Employment | "Employee Nationality: Brazilian; Work auth: Permanent Resident" |
| NA-066 | Embedded in legal pleading | Court | "the defendant, a citizen of Mexico, hereby...", "Plaintiff (Australian national)" |
| NA-067 | Embedded in medical record | Clinical | "Patient nationality: Japanese; Language: Japanese; Translator needed" |
| NA-068 | OCR-distorted nationality | Char substitution | Amerlcan (l for i), Britlsh, J@panese (@ for a), Sp@nish |
| NA-069 | OCR diacritic stripping | Lost accents | francais (was français), espanol (was español), portugues (was português) |
| NA-070 | Masked / partial nationality | Privacy-redacted | Nationality: ***, country: [REDACTED], national of **** |
| NA-071 | Anonymized placeholder | Standard generic | Nationality: [Country] (placeholder), Sample nationality: American |
| NA-072 | Nationality sentence-boundary | Trailing punctuation | "He is American.", "Was she German?", "Nationality: Italian." |
| NA-073 | Nationality adjacency-tight | No separator | "John Smith,American,35,M"; "JohnAmerican35"; "Sarah,Japanese-American" |
| NA-074 | Nationality with country flag emoji | Modern visual | 🇺🇸 American, 🇯🇵 Japanese, 🇩🇪 German, 🇧🇷 Brazilian |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | NA-068, NA-069 |
| Masked / partial / redacted | ✓ | NA-070, NA-071 |
| Multilingual context labels | ✓ | NA-035 |
| Multilingual demonyms | ✓ | NA-005 to NA-022 (18+ languages) |
| Script variations | ✓ | NA-010 to NA-016 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | NA-059 to NA-063 |
| Adjacency-tight | ✓ | NA-073 |
| Sentence-boundary tricky | ✓ | NA-072 |
| Domain-embedded (immigration/HR/legal/medical) | ✓ | NA-064 to NA-067 |
| Country code coverage (ISO 3166 alpha-2/3) | ✓ | NA-049, NA-050 |
| Ethnic / cultural / indigenous categories | ✓ | NA-026 to NA-031, NA-052 to NA-057 |
| Hyphenated / dual identities | ✓ | NA-023, NA-024, NA-025, NA-041, NA-058 |
| Historical nationalities | ✓ | NA-042, NA-044, NA-045, NA-046 |
| Stateless / refugee | ✓ | NA-032, NA-033 |

**Total patterns for Nationality: 74**

---

## Entity 18: Citizenship_Status

Immigration / citizenship / residency / legal status. Distinct from Nationality — Citizenship_Status is about legal authorization (visa, PR, naturalized, refugee, etc.).

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CIT-001 | US citizen by birth | Birthright | US citizen, U.S. citizen by birth, born American, natural-born citizen |
| CIT-002 | Naturalized citizen | Acquired citizenship | naturalized US citizen, became a citizen in 2015, naturalized in 2020 |
| CIT-003 | Citizenship by descent | Jus sanguinis | citizenship by descent, Italian citizenship through grandparent, Irish citizenship through ancestry |
| CIT-004 | Citizenship by marriage | Spousal | obtained citizenship through marriage, citizenship by marriage to a French national |
| CIT-005 | Citizenship by investment | Golden visa pathway | citizenship by investment, "golden passport", Caribbean CBI |
| CIT-006 | Dual citizen | Two citizenships | dual citizen (US/UK), dual US-Canadian citizen, dual national |
| CIT-007 | Triple / multiple citizen | More than two | triple citizen, multiple-citizenship, "holds 3 passports" |
| CIT-008 | Permanent resident (US) | Green Card | permanent resident, Green Card holder, LPR (Lawful Permanent Resident), PR card |
| CIT-009 | Permanent resident (Canada) | PR (Canada) | Canadian permanent resident, PR Canada, IMM 5292 (CoPR) |
| CIT-010 | Permanent resident (other countries) | International PR | permanent resident of Germany, UK Indefinite Leave to Remain (ILR), Australian PR |
| CIT-011 | EU permanent residence | EU context | EU long-term resident, EU permanent residence permit |
| CIT-012 | Conditional resident | 2-year US | 2-year conditional resident (marriage-based), I-751 pending |
| CIT-013 | UK Settled Status | Post-Brexit | UK Settled Status, pre-settled status, EU Settlement Scheme |
| CIT-014 | Work visa — H-1B | US specialty occupation | H-1B visa, H-1B holder, H-1B specialty occupation |
| CIT-015 | Work visa — L-1 | US intracompany | L-1A (executive), L-1B (specialized knowledge) |
| CIT-016 | Work visa — O-1 | US extraordinary ability | O-1 visa, extraordinary ability visa |
| CIT-017 | Work visa — TN | NAFTA / USMCA | TN visa (Canadian/Mexican professional) |
| CIT-018 | Work visa — E-2 / EB-5 | US investor | E-2 treaty investor, EB-5 immigrant investor |
| CIT-019 | Student visa — F-1 (US) | US student | F-1 student visa, F-1 visa holder |
| CIT-020 | Student visa — J-1 (US) | US exchange | J-1 exchange visitor, J-1 visa holder |
| CIT-021 | Student visa — M-1 (US) | US vocational | M-1 vocational student |
| CIT-022 | Student visa — international | Other countries | Tier 4 student visa (UK), Studienvisum (DE), 留学ビザ (JP) |
| CIT-023 | Tourist / visitor visa | Travel | B-1/B-2 (US), Schengen visa, ESTA, Tourist visa, Visitor visa |
| CIT-024 | Work permit (international) | Various countries | German Aufenthaltserlaubnis with Erlaubnis zur Erwerbstätigkeit; UK Tier 2 |
| CIT-025 | Working Holiday Visa | International | Working Holiday Visa (Australia, NZ, Canada, Japan) |
| CIT-026 | Digital nomad visa | Modern | Estonia Digital Nomad Visa, Portugal D7, Spain Digital Nomad |
| CIT-027 | Refugee status | Protected | refugee status, granted refugee status, UNHCR recognized refugee |
| CIT-028 | Asylum seeker | Application pending | asylum seeker, asylum applicant, pending asylum |
| CIT-029 | Granted asylum | Approved | granted asylum, asylee, asylee status |
| CIT-030 | Subsidiary protection | EU | subsidiary protection, complementary protection |
| CIT-031 | Temporary Protected Status (US) | US TPS | TPS, Temporary Protected Status, TPS Salvadoran |
| CIT-032 | DACA recipient | US deferred action | DACA recipient, Dreamer, Deferred Action for Childhood Arrivals |
| CIT-033 | Humanitarian parole | US | humanitarian parolee, parole status |
| CIT-034 | Undocumented (modern term) | Status | undocumented immigrant, undocumented, without papers |
| CIT-035 | Irregular migrant (EU term) | EU | irregular migrant, irregular status |
| CIT-036 | Sans-papiers (French) | French context | sans-papiers, "without papers", undocumented FR |
| CIT-037 | Visa overstay | Out of status | visa overstay, overstayed visa, out of status |
| CIT-038 | Illegal alien (US legal/derogatory) | US official | illegal alien (now usually replaced by "undocumented") |
| CIT-039 | Removal / deportation pending | Status | deportation pending, in removal proceedings, ordered removed |
| CIT-040 | Stateless person | No citizenship | stateless, apatride (FR), Staatenloser (DE), apolide (IT), stateless person status |
| CIT-041 | Naturalization pending | Application phase | application for naturalization pending, N-400 pending |
| CIT-042 | Green Card pending | Adjustment | adjustment of status pending, I-485 pending, Green Card processing |
| CIT-043 | Renounced citizenship | Voluntary loss | renounced US citizenship, expatriated, renunciation completed |
| CIT-044 | Citizenship revoked | Involuntary loss | citizenship revoked, denaturalized, citizenship stripped |
| CIT-045 | Citizenship of convenience | Modern term | "passport of convenience", flag-of-convenience citizenship |
| CIT-046 | Aufenthaltserlaubnis (DE) | German residence permit | Aufenthaltserlaubnis, Niederlassungserlaubnis (settlement), Daueraufenthaltsrecht |
| CIT-047 | Permesso di soggiorno (IT) | Italian permit | permesso di soggiorno, carta di soggiorno (long-term) |
| CIT-048 | Carte de séjour (FR) | French permit | carte de séjour, titre de séjour, carte de résident permanent |
| CIT-049 | Residencia (ES) | Spanish | residencia, NIE (resident foreigner), tarjeta de residencia |
| CIT-050 | 在留カード (JP) | Japanese residence | 在留カード, 永住権 (permanent residency), 特別永住者 (Special Permanent Resident) |
| CIT-051 | 외국인등록증 (KR) | Korean alien reg | 외국인등록증 (Alien Registration Card), F-5 (PR), D-8 (Investor) |
| CIT-052 | 居留许可 (ZH) | Chinese residence | 居留许可, 永久居留权, Z visa (work) |
| CIT-053 | UK BRP | Biometric residence permit | BRP (Biometric Residence Permit), UK BRP card |
| CIT-054 | Schengen visa types | EU short-stay | Schengen visa Type A (airport transit), Type C (short stay), Type D (long stay) |
| CIT-055 | Naturalization year | Date context | "naturalized in 2015", "became a citizen in March 2020" |
| CIT-056 | "Country of citizenship" form | Form field | Country of Citizenship: United States, Country of Citizenship: India |
| CIT-057 | "Citizenship status" form | Form field | Citizenship Status: US Citizen, Citizenship Status: Permanent Resident |
| CIT-058 | "Immigration status" form | Form field | Immigration Status: F-1, Immigration Status: Permanent Resident |
| CIT-059 | "Work authorization" form | Employment context | Work Authorization: H-1B, Work Auth: PR Card, Authorized to work in US: Yes |
| CIT-060 | I-9 Form (US) | US work eligibility | I-9 Section 1: U.S. Citizen / Non-Citizen National / LPR / Authorized Alien |
| CIT-061 | A-Number (US) | Alien Registration | A# 123-456-789, A-Number: 012345678, USCIS#: 098765432 |
| CIT-062 | USCIS#: | US immigration ID | USCIS#: 12345678, A-Number 087654321 |
| CIT-063 | I-94 Number (US) | US entry record | I-94 Number: 12345678-1, Form I-94 |
| CIT-064 | EAD (US) | Work authorization card | EAD (Employment Authorization Document), EAD card, Form I-765 |
| CIT-065 | Multilingual "citizenship" labels | Various languages | Citizenship (EN), Citoyenneté (FR), Staatsbürgerschaft (DE), Ciudadanía (ES), Cittadinanza (IT), Cidadania (PT), 国籍 (JP — often used for citizenship), 시민권 (KR), 公民身份 (ZH), Гражданство (RU), Vatandaşlık (TR), المواطنة (AR), אזרחות (HE), สัญชาติ (TH) |
| CIT-066 | "Citizen of [country]" English | Predicate form | "citizen of France", "US citizen", "citizen of the United Kingdom" |
| CIT-067 | "National of [country]" English | Formal | "national of Japan", "Mexican national", "national of Germany" |
| CIT-068 | Pre-Brexit EU citizenship reference | UK historical | "UK national (pre-Brexit EU citizen)", "EU national (no longer)" |
| CIT-069 | Citizenship in JSON | Structured | "citizenship": "US Citizen", "immigration_status": "H-1B", "work_auth": "EAD" |
| CIT-070 | Citizenship in KV | Form field | citizenship=US Citizen, immigration_status=PR, work_auth=H-1B |
| CIT-071 | Citizenship in XML | Markup | <citizenship>US Citizen</citizenship>, <immigration_status>H-1B</immigration_status> |
| CIT-072 | Citizenship in CSV | Tabular | "Smith","John","M","35","US Citizen","Yes" |
| CIT-073 | Embedded in HR record | Employment | "Work auth: H-1B, sponsored by employer until 2026; Green Card in process" |
| CIT-074 | Embedded in I-9 form | US legal | "I-9: Section 1: A. Citizen of the United States" |
| CIT-075 | Embedded in legal pleading | Court | "The petitioner, a Mexican national legally present on H-1B, hereby..." |
| CIT-076 | Embedded in medical record | Clinical | "Patient: Chen, Sarah; Citizenship: China; Immigration: H-4 dependent visa" |
| CIT-077 | Visa stamp on passport | Travel doc | "F-1 visa stamp valid until 2025", "H-1B visa stamp, valid through 2027" |
| CIT-078 | OCR-distorted (visa codes) | Char substitution | H-l8 (was H-1B), F-l (was F-1), Greell Card (was Green) |
| CIT-079 | OCR-distorted (status words) | Mangled | naturaIized (capital I for l), citlzen, permanetn resident |
| CIT-080 | Masked / partial citizenship status | Privacy-redacted | Citizenship: ***, Status: [REDACTED], Visa: **** |
| CIT-081 | Anonymized placeholder | Standard generic | Citizenship: [STATUS], Sample status: PR |
| CIT-082 | Citizenship sentence-boundary | Trailing punctuation | "She is a US citizen.", "Is he on H-1B?", "Status: Permanent Resident." |
| CIT-083 | Citizenship adjacency-tight | No separator | "John Smith,US Citizen,35,M"; "Sarah-H1B-Engineer-32" |
| CIT-084 | Refugee from specific country | Origin context | "Syrian refugee", "Ukrainian refugee", "Afghan asylum seeker" |
| CIT-085 | Visa transition (status change) | Multi-status | "OPT → H-1B (Oct 2024)", "F-1 → H-1B transition" |
| CIT-086 | Spouse of citizen / resident | Dependent status | "spouse of US citizen", "H-4 dependent of H-1B holder", "L-2 dependent" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | CIT-078, CIT-079 |
| Masked / partial / redacted | ✓ | CIT-080, CIT-081 |
| Multilingual context labels | ✓ | CIT-065 |
| Country-specific residence permits | ✓ | CIT-046 to CIT-053 (DE, IT, FR, ES, JP, KR, ZH, UK) |
| Script variations | ✓ | CIT-050, CIT-051, CIT-052 (JP, KR, ZH) |
| In structured data | ✓ | CIT-069, CIT-070, CIT-071, CIT-072 |
| Adjacency-tight | ✓ | CIT-083 |
| Sentence-boundary tricky | ✓ | CIT-082 |
| Domain-embedded (HR/legal/medical/I-9) | ✓ | CIT-073 to CIT-077 |
| Visa-specific (US) | ✓ | CIT-014 to CIT-022, CIT-060 to CIT-064 |
| Refugee / asylum / protection | ✓ | CIT-027 to CIT-033 |
| Stateless / undocumented | ✓ | CIT-034 to CIT-040 |
| Multiple-citizenship variants | ✓ | CIT-006, CIT-007, CIT-068 |

**Total patterns for Citizenship_Status: 86**

---

## Entity 19: Sex_Orientation

Sexual orientation or romantic identity. Highly sensitive (GDPR Article 9). Includes LGBTQ+ identifications, asexual/aromantic spectrum, indigenous Two-Spirit, and self-identification phrasing.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| SO-001 | Heterosexual (English) | Standard | heterosexual, straight, hetero |
| SO-002 | Homosexual (English) | Standard | homosexual, gay (m or general), lesbian (f) |
| SO-003 | Bisexual (English) | Attracted to multiple | bisexual, bi |
| SO-004 | Gay (specific male) | Modern usage | gay man, openly gay, out gay |
| SO-005 | Lesbian | Female homosexual | lesbian, lesbian woman, openly lesbian |
| SO-006 | Pansexual | All gender attraction | pansexual, pan, gender-blind attraction |
| SO-007 | Asexual | No sexual attraction | asexual, ace, on the ace spectrum |
| SO-008 | Aromantic | No romantic attraction | aromantic, aro, on the aromantic spectrum |
| SO-009 | Demisexual | Connection-dependent | demisexual, demi |
| SO-010 | Demiromantic | Connection-dependent romantic | demiromantic |
| SO-011 | Queer (umbrella) | LGBTQ+ general | queer, identifies as queer |
| SO-012 | Questioning | Exploring identity | questioning, exploring my sexuality, Q (in LGBTQ+) |
| SO-013 | Two-Spirit (Indigenous) | Indigenous N. American | Two-Spirit, 2S, two-spirit identity |
| SO-014 | Bicurious | Exploration | bicurious |
| SO-015 | Skoliosexual / Gynesexual / Androsexual | Modern specific | skoliosexual, gynesexual, androsexual, abrosexual |
| SO-016 | Sapiosexual | Attraction to intellect | sapiosexual, attracted to intelligence |
| SO-017 | Polysexual | Many but not all genders | polysexual |
| SO-018 | Greysexual / Greyromantic | On ace/aro spectrum | greysexual, greyromantic, gray-ace |
| SO-019 | Fluid | Identity not fixed | fluid, sexually fluid, identity is fluid |
| SO-020 | Out / openly | Self-disclosure | openly gay, out as bisexual, out and proud |
| SO-021 | Closeted | Not out | in the closet, closeted, not out yet |
| SO-022 | Came out | Disclosed | came out as gay, came out as bisexual, came out in 2015 |
| SO-023 | Self-identification phrasing | "Identifies as" | identifies as gay, self-identifies as bisexual, identifies as queer |
| SO-024 | Community / Pride membership | Group affiliation | LGBTQ+ community member, Pride participant, ally, queer community |
| SO-025 | Acronym variants | Umbrella terms | LGBT, LGBTQ, LGBTQIA+, LGBTQIA2S+ (incl Two-Spirit), 2SLGBTQ+ |
| SO-026 | Relationship-inferred (same-sex partner) | Indirect | "married to his husband", "her wife", "same-sex partner", "her girlfriend" |
| SO-027 | Relationship-inferred (multi-gender history) | Pattern | "previously married to a man, now dating a woman" |
| SO-028 | Spouse-pronoun mismatch | Inference | "John and his husband", "Maria and her wife" (suggests gay/lesbian identity) |
| SO-029 | French — homosexuel/le | French | homosexuel, homosexuelle, gay, lesbienne |
| SO-030 | French — bisexuel/le | French | bisexuel, bisexuelle, bi |
| SO-031 | French — hétérosexuel/le | French | hétérosexuel, hétérosexuelle |
| SO-032 | French — pansexuel/le | French | pansexuel, pansexuelle |
| SO-033 | French — asexuel/le | French | asexuel, asexuelle |
| SO-034 | German — homosexuell | German | homosexuell, schwul (m), lesbisch (f) |
| SO-035 | German — bisexuell | German | bisexuell, bi |
| SO-036 | German — heterosexuell | German | heterosexuell, hetero |
| SO-037 | German — pansexuell | German | pansexuell |
| SO-038 | German — asexuell | German | asexuell |
| SO-039 | Spanish — homosexual | Spanish | homosexual, gay, lesbiana |
| SO-040 | Spanish — bisexual | Spanish | bisexual, bi |
| SO-041 | Spanish — heterosexual | Spanish | heterosexual, hetero |
| SO-042 | Spanish — pansexual | Spanish | pansexual |
| SO-043 | Italian — omosessuale | Italian | omosessuale, gay, lesbica |
| SO-044 | Italian — bisessuale | Italian | bisessuale, bi |
| SO-045 | Italian — eterosessuale | Italian | eterosessuale, etero |
| SO-046 | Portuguese — homossexual | Portuguese | homossexual, gay, lésbica |
| SO-047 | Portuguese — bissexual | Portuguese | bissexual, bi |
| SO-048 | Portuguese — heterossexual | Portuguese | heterossexual, hetero |
| SO-049 | Dutch — homoseksueel | Dutch | homoseksueel, homo, lesbisch |
| SO-050 | Dutch — biseksueel | Dutch | biseksueel, bi |
| SO-051 | Dutch — heteroseksueel | Dutch | heteroseksueel, hetero |
| SO-052 | Japanese — 同性愛者 | Japanese | 同性愛者, ゲイ, レズビアン, レズ |
| SO-053 | Japanese — 両性愛者 | Japanese | 両性愛者, バイセクシュアル |
| SO-054 | Japanese — 異性愛者 | Japanese | 異性愛者, ヘテロセクシュアル |
| SO-055 | Japanese — パンセクシャル / 全性愛 | Japanese pansexual | パンセクシャル, 全性愛 |
| SO-056 | Japanese — 無性愛 / アセクシュアル | Japanese asexual | 無性愛, アセクシュアル |
| SO-057 | Korean — 동성애자 | Korean | 동성애자, 게이, 레즈비언 |
| SO-058 | Korean — 양성애자 | Korean | 양성애자, 바이섹슈얼 |
| SO-059 | Korean — 이성애자 | Korean | 이성애자, 헤테로 |
| SO-060 | Chinese — 同性恋 | Chinese | 同性恋, 同志 (slang), 拉拉 (lesbian) |
| SO-061 | Chinese — 双性恋 | Chinese | 双性恋 |
| SO-062 | Chinese — 异性恋 | Chinese | 异性恋 |
| SO-063 | Russian — гомосексуал | Russian | гомосексуал, гей, лесбиянка |
| SO-064 | Russian — бисексуал | Russian | бисексуал |
| SO-065 | Russian — гетеросексуал | Russian | гетеросексуал |
| SO-066 | Arabic — مثلي الجنس | Arabic | مثلي الجنس (homosexual), مثلية (lesbian) |
| SO-067 | Arabic — ثنائي الجنس | Arabic bi | ثنائي الجنس, ثنائي الميول |
| SO-068 | Hebrew — הומוסקסואל | Hebrew | הומוסקסואל, גיי, לסבית |
| SO-069 | Hebrew — ביסקסואל | Hebrew bi | ביסקסואל |
| SO-070 | Thai — รักร่วมเพศ / เกย์ | Thai | รักร่วมเพศ, เกย์, เลสเบี้ยน |
| SO-071 | Turkish — eşcinsel | Turkish | eşcinsel, gay, lezbiyen |
| SO-072 | Polish — homoseksualny | Polish | homoseksualny, gej, lesbijka |
| SO-073 | Form / KV (structured) | Form field | Sexual Orientation: Gay, Orientation: Bisexual, sexual_orientation=heterosexual |
| SO-074 | Self-ID survey | DEI / census | "How do you identify your sexual orientation? [Straight/Gay/Bisexual/Other]" |
| SO-075 | Pronoun-inferred (community context) | Implicit | "lives in a queer community", "active in Pride parade" |
| SO-076 | "Out" professional context | Workplace | "openly gay in the workplace", "out at work", "an out executive" |
| SO-077 | Euphemism / coded language (historical) | Old terms | "confirmed bachelor" (historical for gay man), "friend of Dorothy", "Boston marriage" |
| SO-078 | Slur / derogatory (do NOT detect) | Hate speech | (intentionally NOT enumerating slurs; benchmark should detect identity, not slurs) |
| SO-079 | Sex orientation in JSON | Structured | "sexual_orientation": "Bisexual", "orientation": "Gay" |
| SO-080 | Sex orientation in KV | Form field | sexual_orientation=Lesbian, orientation=Queer |
| SO-081 | Sex orientation in XML | Markup | <sexual_orientation>Gay</sexual_orientation>, <orientation>Bi</orientation> |
| SO-082 | Sex orientation in CSV | Tabular | "Smith","John","M","35","Gay","Single" |
| SO-083 | Multilingual context label | Various languages | Sexual Orientation (EN), Orientation sexuelle (FR), Sexuelle Orientierung (DE), Orientación sexual (ES), Orientamento sessuale (IT), Orientação sexual (PT), 性的指向 (JP), 성적 지향 (KR), 性取向 (ZH), Сексуальная ориентация (RU), Cinsel yönelim (TR), التوجه الجنسي (AR), נטייה מינית (HE) |
| SO-084 | Embedded in dating app context | Casual | "I'm bisexual on my dating profile", "matched on a gay dating app" |
| SO-085 | Embedded in medical record | Clinical | "Patient reports being gay; relationship: married to same-sex spouse" |
| SO-086 | Embedded in HR diversity record | DEI | "Self-identified as LGBTQ+ for DEI tracking", "Sexual orientation (self-reported): Bisexual" |
| SO-087 | Embedded in legal pleading | Court | "the plaintiff, a lesbian woman, alleges discrimination based on sexual orientation" |
| SO-088 | OCR-distorted | Char substitution | b1sexual (1 for i), q@y (@ for a), 1esbian (1 for L) |
| SO-089 | Masked / partial | Privacy-redacted | Sexual Orientation: ***, Orientation: [REDACTED], LGBTQ+ status: **** |
| SO-090 | Sex orientation anonymized placeholder | Standard generic | Orientation: [LGBTQ+] (placeholder) |
| SO-091 | Sex orientation sentence-boundary | Trailing punctuation | "He is gay.", "Is she bisexual?", "Orientation: Lesbian." |
| SO-092 | Sex orientation adjacency-tight | No separator | "John Smith,Gay,35,M"; "Sarah,Bisexual,32" |
| SO-093 | Pronoun + identity combo | Profile bio | "she/her | pansexual | LGBTQ+ activist" |
| SO-094 | LGBTQ+ status in pride | Public identity | "Pride 2024 marcher", "LGBTQ+ youth advocate", "queer artist" |
| SO-095 | "Heteronormative" / "queer" academic | Scholarly | "rejecting heteronormative assumptions", "queer studies professor" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | SO-088 |
| Masked / partial / redacted | ✓ | SO-089, SO-090 |
| Multilingual context labels | ✓ | SO-083 |
| Multilingual identity terms | ✓ | SO-029 to SO-072 (~20 languages) |
| Script variations | ✓ | SO-052 to SO-070 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | SO-079, SO-080, SO-081, SO-082 |
| Adjacency-tight | ✓ | SO-092 |
| Sentence-boundary tricky | ✓ | SO-091 |
| Domain-embedded (HR/medical/legal/dating) | ✓ | SO-084, SO-085, SO-086, SO-087 |
| Indigenous identity | ✓ | SO-013 |
| Asexual / aromantic spectrum | ✓ | SO-007, SO-008, SO-009, SO-010, SO-018 |
| Modern specific identities | ✓ | SO-015, SO-016, SO-017 |
| Self-identification phrasing | ✓ | SO-023 |
| Out / closeted context | ✓ | SO-020, SO-021, SO-022 |
| Relationship-inferred | ✓ | SO-026, SO-027, SO-028 |
| Acronyms (LGBT, LGBTQIA+, 2SLGBTQ+) | ✓ | SO-025 |

**Total patterns for Sex_Orientation: 95**

---

## Entity 20: Religion

Religious affiliation, denomination, sect, spiritual practice, and dietary indicators of religious belief. Highly sensitive (GDPR Article 9).

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| RE-001 | Christian (broad) | Major religion | Christian, follower of Christianity |
| RE-002 | Catholic / Roman Catholic | Christian denomination | Catholic, Roman Catholic, RC, devout Catholic, practicing Catholic |
| RE-003 | Orthodox Christian | Eastern Orthodox | Orthodox Christian, Greek Orthodox, Russian Orthodox, Serbian Orthodox, Eastern Orthodox |
| RE-004 | Protestant (umbrella) | Christian | Protestant, Reformed |
| RE-005 | Baptist | Christian denomination | Baptist, Southern Baptist, American Baptist |
| RE-006 | Methodist | Christian denomination | Methodist, United Methodist, AME (African Methodist Episcopal) |
| RE-007 | Lutheran | Christian denomination | Lutheran, ELCA, Missouri Synod |
| RE-008 | Anglican / Episcopalian | Christian denomination | Anglican, Church of England, Episcopalian (US) |
| RE-009 | Evangelical | Christian movement | Evangelical, evangelical Christian, born-again Christian |
| RE-010 | Pentecostal | Christian denomination | Pentecostal, Assemblies of God, Church of God |
| RE-011 | Mormon / LDS | Christian-related | Mormon, LDS (Latter-day Saints), Church of Jesus Christ of Latter-day Saints |
| RE-012 | Presbyterian | Christian denomination | Presbyterian, PCUSA, Reformed Presbyterian |
| RE-013 | Quaker | Christian denomination | Quaker, Religious Society of Friends, Friend |
| RE-014 | Adventist | Christian denomination | Seventh-day Adventist, SDA, Adventist |
| RE-015 | Jehovah's Witness | Christian-related | Jehovah's Witness, JW |
| RE-016 | Coptic Orthodox | Egyptian Christian | Coptic, Coptic Orthodox, Egyptian Copt |
| RE-017 | Maronite | Lebanese Christian | Maronite, Maronite Catholic |
| RE-018 | Mennonite / Amish | Anabaptist | Mennonite, Amish, Hutterite |
| RE-019 | Muslim (broad) | Major religion | Muslim, Islamic, follower of Islam |
| RE-020 | Sunni Muslim | Islamic denomination | Sunni, Sunni Muslim |
| RE-021 | Shia / Shiite Muslim | Islamic denomination | Shia, Shiite, Shi'a Muslim |
| RE-022 | Sufi | Islamic mystical | Sufi, follower of Sufism, Sufi order (Naqshbandi, etc.) |
| RE-023 | Ahmadiyya | Islamic minority | Ahmadiyya, Ahmadi |
| RE-024 | Ibadi | Omani Islamic | Ibadi Muslim |
| RE-025 | Druze | Distinct from Islam | Druze, Druze faith |
| RE-026 | Alawite | Syrian Islamic offshoot | Alawite, Alawi |
| RE-027 | Jewish (broad) | Major religion | Jewish, Jew, follower of Judaism, of the Jewish faith |
| RE-028 | Orthodox Jewish | Jewish denomination | Orthodox Jewish, Modern Orthodox, Haredi, Hasidic, ultra-Orthodox |
| RE-029 | Reform Jewish | Jewish denomination | Reform Jewish, Liberal Judaism |
| RE-030 | Conservative / Masorti | Jewish denomination | Conservative Jewish, Masorti |
| RE-031 | Reconstructionist | Jewish denomination | Reconstructionist Jewish |
| RE-032 | Karaite | Jewish minority | Karaite Jew |
| RE-033 | Sephardic / Ashkenazic | Jewish ethnic-religious | Sephardic Jew, Ashkenazi Jew, Mizrahi Jew |
| RE-034 | Hindu (broad) | Major religion | Hindu, follower of Hinduism |
| RE-035 | Shaivite | Hindu tradition | Shaivite, follower of Shiva |
| RE-036 | Vaishnavite | Hindu tradition | Vaishnavite, follower of Vishnu, ISKCON / Hare Krishna |
| RE-037 | Shakta | Hindu tradition | Shakta, follower of Shakti |
| RE-038 | Smarta | Hindu tradition | Smarta |
| RE-039 | Buddhist (broad) | Major religion | Buddhist, follower of Buddhism |
| RE-040 | Theravada | Buddhist tradition | Theravada Buddhist (Southeast Asian) |
| RE-041 | Mahayana | Buddhist tradition | Mahayana Buddhist |
| RE-042 | Zen | Buddhist tradition | Zen Buddhist, Soto Zen, Rinzai Zen |
| RE-043 | Tibetan / Vajrayana | Buddhist tradition | Tibetan Buddhist, Vajrayana, Nyingma, Gelug |
| RE-044 | Pure Land | Buddhist tradition | Pure Land Buddhist, Jodo Shinshu, 浄土真宗 |
| RE-045 | Nichiren | Buddhist tradition | Nichiren Buddhist, Soka Gakkai |
| RE-046 | Sikh | Major religion | Sikh, follower of Sikhism, Khalsa Sikh |
| RE-047 | Jain | Major religion | Jain, follower of Jainism, Digambara, Svetambara |
| RE-048 | Bahá'í | World religion | Bahá'í, follower of the Bahá'í Faith |
| RE-049 | Zoroastrian / Parsi | Ancient world religion | Zoroastrian, Parsi (Indian), Zarathushti |
| RE-050 | Shinto (Japan) | Indigenous Japanese | Shinto, follower of Shinto, 神道 |
| RE-051 | Taoist / Daoist | Chinese tradition | Taoist, Daoist, 道教 |
| RE-052 | Confucian | Chinese tradition | Confucian, 儒家 |
| RE-053 | Rastafarian | Caribbean-rooted | Rastafarian, Rasta |
| RE-054 | Wiccan / Neo-pagan | Modern pagan | Wiccan, Neo-pagan, Pagan, Witch (religious), Druid, Heathen |
| RE-055 | Indigenous / traditional / animist | Various peoples | Indigenous religion, traditional African religion, Yoruba religion, Native American spirituality, Inuit traditional |
| RE-056 | Scientologist | New religious movement | Scientologist, member of Church of Scientology |
| RE-057 | Falun Gong / Falun Dafa | Chinese new religion | Falun Gong practitioner, 法轮功 |
| RE-058 | Cao Dai / Hoa Hao | Vietnamese | Cao Dai, Hoa Hao |
| RE-059 | Shinto-Buddhist syncretic (JP) | Japanese practice | Shinto-Buddhist, 仏教徒であり神道信者 |
| RE-060 | Atheist | Non-religious | atheist, "I'm an atheist", non-believer |
| RE-061 | Agnostic | Non-religious | agnostic, agnostic atheist, agnostic theist |
| RE-062 | Secular humanist | Non-religious | secular humanist, secular |
| RE-063 | Spiritual but not religious | Modern category | spiritual but not religious, SBNR, "I'm spiritual" |
| RE-064 | "None" / no religion | Census category | None, no religion, religiously unaffiliated, "nones" |
| RE-065 | Deist | Philosophical | Deist, Deism |
| RE-066 | Membership language (English) | Affiliation phrasing | member of [church/temple], practices [religion], observes [religion], follower of [religion], devout, devoted, practicing |
| RE-067 | Specific religious institution | Place / org | "attends St. Mary's Catholic Church", "member of Temple Beth El", "goes to the local mosque", "regular at Sangat Sahib Gurdwara" |
| RE-068 | Religious leadership role | Title + role | "Father Patrick (Catholic priest)", "Rabbi David Cohen", "Imam Ahmed Hassan", "Pastor Sarah Williams", "Bhante (Buddhist monk)" |
| RE-069 | Religious practice observable | Behavior | "wears hijab", "keeps kosher", "vegetarian (Buddhist)", "observes Sabbath", "fasts during Ramadan", "wears a kippah", "marks ash on forehead (Hindu)" |
| RE-070 | Religious clothing indicators | Visual identifiers | wears hijab, niqab, burqa, kippah, yarmulke, kasaya (Buddhist robe), kesh (Sikh uncut hair) |
| RE-071 | Religious dietary — Halal | Islamic | "halal meal required", "halal-certified only", "no pork (halal)" |
| RE-072 | Religious dietary — Kosher | Jewish | "kosher meals", "keeps kosher", "kosher-certified", "shomer kashrut" |
| RE-073 | Religious dietary — Hindu vegetarian | Hindu / Jain | "vegetarian (Hindu)", "Jain vegetarian (no onion/garlic)", "lacto-vegetarian", "no beef" |
| RE-074 | Religious dietary — Buddhist | Buddhist | "vegetarian (Buddhist)", "no killing of animals", "Theravada-vegetarian" |
| RE-075 | Religious fasting — Ramadan | Islamic | "fasting for Ramadan", "Ramadan fasting", "iftar" |
| RE-076 | Religious fasting — Lent | Christian | "Lenten fast", "giving up chocolate for Lent", "Ash Wednesday" |
| RE-077 | Religious fasting — Yom Kippur | Jewish | "Yom Kippur fast", "fasting on the High Holidays" |
| RE-078 | Religious fasting — Navratri | Hindu | "Navratri fast", "fasting during Navratri", "vrat" |
| RE-079 | Religious holidays as indicators | Holiday observance | "celebrates Eid al-Fitr / Eid al-Adha (Muslim)", "celebrates Passover (Jewish)", "celebrates Diwali (Hindu)", "celebrates Vesak (Buddhist)" |
| RE-080 | Religion French | French | catholique, musulman(e), juif/juive, pratiquant(e), hindouiste, bouddhiste, athée, agnostique |
| RE-081 | Religion German | German | evangelisch, katholisch, muslimisch, jüdisch, Buddhist, Hindu, Atheist |
| RE-082 | Religion Spanish | Spanish | católico/a, musulmán/a, judío/a, cristiano/a, hindú, budista, ateo/a |
| RE-083 | Religion Italian | Italian | cattolico/a, musulmano/a, ebreo/a, cristiano/a, induista, buddhista, ateo/a |
| RE-084 | Religion Portuguese | Portuguese | católico/a, muçulmano/a, judeu/judia, cristão/cristã, hindu, budista, ateu/ateia |
| RE-085 | Religion Dutch | Dutch | katholiek, moslim, joods, christelijk, hindoe, boeddhist, atheïst |
| RE-086 | Religion Japanese | Japanese | キリスト教, イスラム教, 仏教, 神道, ユダヤ教, ヒンドゥー教, 無神論者 |
| RE-087 | Religion Korean | Korean | 기독교 (Christian), 천주교 (Catholic), 불교 (Buddhism), 이슬람 (Islam), 무신론자 (atheist) |
| RE-088 | Religion Chinese | Chinese | 基督教 (Christian), 天主教 (Catholic), 佛教 (Buddhist), 伊斯兰教 (Islamic), 无神论者 (atheist) |
| RE-089 | Religion Russian | Russian | православный (Orthodox), католик (Catholic), мусульманин (Muslim), иудей (Jewish), буддист, атеист |
| RE-090 | Religion Arabic | Arabic | مسلم (Muslim), مسيحي (Christian), يهودي (Jewish), بوذي (Buddhist), هندوسي (Hindu), ملحد (atheist) |
| RE-091 | Religion Hebrew | Hebrew | יהודי (Jewish), נוצרי (Christian), מוסלמי (Muslim), אתאיסט (atheist) |
| RE-092 | Religion Thai | Thai | พุทธ (Buddhist), คริสต์ (Christian), อิสลาม (Muslim), ฮินดู (Hindu) |
| RE-093 | Religion Turkish | Turkish | Müslüman, Hristiyan, Yahudi, Budist, Ateist |
| RE-094 | Religion Polish | Polish | katolik, protestant, muzułmanin, żyd, ateista |
| RE-095 | Religion Czech | Czech | katolík, protestant, muslim, žid, ateista |
| RE-096 | Religion Hungarian | Hungarian | katolikus, protestáns, muszlim, zsidó, ateista |
| RE-097 | Adjectival religious form | "X morality / heritage" | "Christian morality", "Jewish heritage", "Islamic finance", "Buddhist meditation" |
| RE-098 | Religious conversion | Change of religion | "converted to Islam", "became Buddhist", "convert to Judaism", "left the Church" |
| RE-099 | Religious nation reference | Country context | "the Jewish state (Israel)", "Islamic Republic (of Iran)", "Hindu-majority nation (India)" |
| RE-100 | Sacred text reference | Indirect identity | "reads the Bible daily", "studies the Quran", "Torah scholar", "Vedanta student" |
| RE-101 | Religious symbol on person | Identity marker | "wears a cross necklace", "Star of David pendant", "Buddha pendant", "Om symbol jewelry" |
| RE-102 | "Religious" vs "Spiritual" labels | Self-identification | "religious but not spiritual", "spiritual but not religious", "culturally Jewish but not religious" |
| RE-103 | Religion in JSON | Structured | "religion": "Catholic", "faith": "Muslim", "religious_affiliation": "Buddhist" |
| RE-104 | Religion in KV | Form field | religion=Catholic, faith=Muslim, religious_affiliation=Buddhist |
| RE-105 | Religion in XML | Markup | <religion>Catholic</religion>, <faith>Muslim</faith> |
| RE-106 | Religion in CSV | Tabular | "Smith","John","M","35","Christian","Catholic" |
| RE-107 | Multilingual context label | Various languages | Religion (EN), Religion (FR), Religion / Konfession (DE), Religión (ES), Religione (IT), Religião (PT), 宗教 (JP), 종교 (KR), 宗教 (ZH), Религия (RU), Din (TR), دين (AR), דת (HE), ศาสนา (TH) |
| RE-108 | Embedded in HR / DEI form | Workplace | "Religious accommodation request: prayer break for Friday Jumu'ah", "Religious dietary requirement: kosher" |
| RE-109 | Embedded in dietary preference form | Travel / event | "Special meal: HMEAL (halal)", "Special meal: KSML (kosher)", "Special meal: VGML (vegetarian, Hindu)" |
| RE-110 | Embedded in marriage record | Civil registry | "Religious ceremony: Catholic, Officiant: Father Patrick" |
| RE-111 | Embedded in medical record | Clinical | "Patient religion: Jehovah's Witness (no blood transfusion); record: noted in chart" |
| RE-112 | Embedded in immigration / census | Government | "Religion: Christian (Census 2020)"; "Religion (optional): Buddhist" |
| RE-113 | Embedded in legal pleading | Court | "the plaintiff, a devout Catholic, alleges religious discrimination" |
| RE-114 | OCR-distorted | Char substitution | Cathol1c (1 for i), Mus11m (1 for l), Bud_dh1st, Jew1sh |
| RE-115 | OCR diacritic stripping | Lost accents | Bahai (was Bahá'í), Bouddhiste (was bouddhiste), atheist (lost é → atheiste) |
| RE-116 | Masked / partial religion | Privacy-redacted | Religion: ***, Faith: [REDACTED], religious_affiliation=**** |
| RE-117 | Religion anonymized placeholder | Standard generic | Religion: [Religion], Sample religion: Christian |
| RE-118 | Religion sentence-boundary | Trailing punctuation | "He is Catholic.", "Is she Muslim?", "Religion: Hindu." |
| RE-119 | Religion adjacency-tight | No separator | "John Smith,Catholic,35,M"; "Sarah-Muslim-32" |
| RE-120 | Mixed / interfaith | Multi-religion | "raised Catholic, now Buddhist", "interfaith household: Jewish-Hindu" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | RE-114, RE-115 |
| Masked / partial / redacted | ✓ | RE-116, RE-117 |
| Multilingual context labels | ✓ | RE-107 |
| Multilingual religion terms | ✓ | RE-080 to RE-096 (~16 languages) |
| Script variations | ✓ | RE-086 to RE-092 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | RE-103, RE-104, RE-105, RE-106 |
| Adjacency-tight | ✓ | RE-119 |
| Sentence-boundary tricky | ✓ | RE-118 |
| Domain-embedded (HR/medical/legal/census/marriage) | ✓ | RE-108 to RE-113 |
| Religious dietary indicators | ✓ | RE-071, RE-072, RE-073, RE-074 |
| Religious fasting / observance | ✓ | RE-075, RE-076, RE-077, RE-078, RE-079 |
| Religious practice / clothing | ✓ | RE-069, RE-070 |
| Religious institution / leadership | ✓ | RE-067, RE-068 |
| Non-religious identifiers | ✓ | RE-060, RE-061, RE-062, RE-063, RE-064, RE-065 |
| Major world religions covered | ✓ | RE-001 to RE-059 (Christianity 18 subdivisions, Islam 8, Judaism 7, Hindu 5, Buddhist 7, plus Sikh, Jain, Bahá'í, Zoroastrian, Shinto, Taoist, Confucian, Rasta, Pagan, indigenous, NRMs) |
| Conversion / mixed / interfaith | ✓ | RE-098, RE-120 |

**Total patterns for Religion: 120**

---

## Entity 21: Political_Party

Political party affiliation or membership. Highly sensitive (GDPR Article 9). Includes major parties globally, ideological identifications, and membership phrasings.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PP-001 | US Democratic | US major | Democrat, Democratic Party, Dem, registered Democrat |
| PP-002 | US Republican | US major | Republican, Republican Party, GOP, Grand Old Party, registered Republican |
| PP-003 | US Independent | US unaffiliated | Independent, registered Independent, unaffiliated voter |
| PP-004 | US Libertarian | US minor | Libertarian, Libertarian Party, LP |
| PP-005 | US Green | US minor | Green Party (US), US Green Party |
| PP-006 | US Working Families | US minor | Working Families Party, WFP |
| PP-007 | US Constitution Party | US minor | Constitution Party |
| PP-008 | UK Labour | UK major | Labour, Labour Party, the party of Labour |
| PP-009 | UK Conservative | UK major | Conservative, Conservatives, Tory, Tories, Conservative Party, Tory Party |
| PP-010 | UK Liberal Democrat | UK | Liberal Democrat, Lib Dem, LD, Liberal Democrats |
| PP-011 | UK SNP | Scottish | SNP, Scottish National Party |
| PP-012 | UK Reform UK | UK | Reform, Reform UK, Reform Party |
| PP-013 | UK Green | UK | Green Party (UK), Green Party of England and Wales |
| PP-014 | UK DUP | NI Unionist | DUP, Democratic Unionist Party |
| PP-015 | UK Sinn Féin | NI Republican | Sinn Féin, Sinn Fein |
| PP-016 | UK Plaid Cymru | Welsh | Plaid Cymru, Plaid |
| PP-017 | German CDU | German major | CDU, Christian Democratic Union, Christlich Demokratische Union |
| PP-018 | German CSU | German Bavarian | CSU, Christian Social Union, Christlich-Soziale Union |
| PP-019 | German SPD | German major | SPD, Social Democratic Party, Sozialdemokratische Partei |
| PP-020 | German FDP | German liberal | FDP, Free Democratic Party, Freie Demokratische Partei |
| PP-021 | German Greens | German green | Grüne, Bündnis 90/Die Grünen, German Greens |
| PP-022 | German Linke | German left | Die Linke, The Left |
| PP-023 | German AfD | German right-wing | AfD, Alternative für Deutschland, Alternative for Germany |
| PP-024 | German BSW | German new | BSW, Bündnis Sahra Wagenknecht |
| PP-025 | French Renaissance / LREM | French ruling | Renaissance, La République En Marche, LREM, Macron's party |
| PP-026 | French RN / FN | French right | RN, Rassemblement National, Front National (former) |
| PP-027 | French LFI | French left | LFI, La France Insoumise, France Unbowed |
| PP-028 | French PS | French socialist | PS, Parti Socialiste, Socialist Party |
| PP-029 | French LR | French center-right | LR, Les Républicains, The Republicans |
| PP-030 | French EELV | French green | EELV, Europe Écologie Les Verts |
| PP-031 | French PCF | French communist | PCF, Parti Communiste Français |
| PP-032 | Italian FdI | Italian right | FdI, Fratelli d'Italia, Brothers of Italy |
| PP-033 | Italian Lega | Italian right | Lega, Lega Nord, Northern League |
| PP-034 | Italian PD | Italian left | PD, Partito Democratico, Democratic Party |
| PP-035 | Italian M5S | Italian populist | M5S, Movimento 5 Stelle, Five Star Movement |
| PP-036 | Italian Forza Italia | Italian center-right | Forza Italia, FI |
| PP-037 | Italian Azione | Italian centrist | Azione |
| PP-038 | Spanish PSOE | Spanish left | PSOE, Partido Socialista Obrero Español |
| PP-039 | Spanish PP | Spanish right | PP, Partido Popular |
| PP-040 | Spanish Vox | Spanish far-right | Vox |
| PP-041 | Spanish Sumar / Podemos | Spanish left | Sumar, Podemos |
| PP-042 | Spanish Ciudadanos | Spanish centrist | Ciudadanos, Cs |
| PP-043 | Catalan ERC | Catalan independence | ERC, Esquerra Republicana de Catalunya |
| PP-044 | Catalan Junts | Catalan independence | Junts, Junts per Catalunya |
| PP-045 | Basque PNV | Basque nationalist | PNV, Partido Nacionalista Vasco, EAJ |
| PP-046 | Portuguese PS | Portuguese socialist | PS, Partido Socialista (PT) |
| PP-047 | Portuguese PSD | Portuguese center-right | PSD, Partido Social Democrata |
| PP-048 | Portuguese Chega | Portuguese far-right | Chega |
| PP-049 | Dutch VVD | Dutch liberal | VVD, Volkspartij voor Vrijheid en Democratie |
| PP-050 | Dutch PVV | Dutch far-right | PVV, Partij voor de Vrijheid |
| PP-051 | Dutch GL-PvdA | Dutch left | GroenLinks-PvdA, GL-PvdA |
| PP-052 | Dutch D66 | Dutch progressive | D66, Democraten 66 |
| PP-053 | Dutch CDA | Dutch Christian Democrat | CDA, Christen-Democratisch Appèl |
| PP-054 | Swedish Social Democrats | Swedish left | Socialdemokraterna, S, Social Democrats |
| PP-055 | Swedish Moderaterna | Swedish center-right | Moderaterna, M, the Moderates |
| PP-056 | Swedish Sweden Democrats | Swedish far-right | Sverigedemokraterna, SD, Sweden Democrats |
| PP-057 | Norwegian Labour / Høyre | Norwegian | Arbeiderpartiet (Ap), Høyre (H) |
| PP-058 | Finnish parties | Finnish | Kokoomus, SDP, Keskusta, PS, Vihreät |
| PP-059 | Danish parties | Danish | Socialdemokraterne (S), Venstre (V), Liberal Alliance, DF |
| PP-060 | Polish PiS | Polish right | PiS, Prawo i Sprawiedliwość, Law and Justice |
| PP-061 | Polish PO / KO | Polish center | PO, Platforma Obywatelska, Civic Platform; KO |
| PP-062 | Polish Konfederacja | Polish right | Konfederacja |
| PP-063 | Czech ANO / ODS / Piráti | Czech parties | ANO, ODS (Civic Democrats), Piráti (Pirates) |
| PP-064 | Hungarian Fidesz | Hungarian ruling | Fidesz, Fidesz–KDNP |
| PP-065 | Hungarian DK / Jobbik / Tisza | Hungarian opposition | DK (Democratic Coalition), Jobbik, Tisza |
| PP-066 | Russian United Russia | Russian ruling | United Russia, Единая Россия, ER |
| PP-067 | Russian KPRF | Russian communist | KPRF, Communist Party of the Russian Federation, КПРФ |
| PP-068 | Russian LDPR | Russian nationalist | LDPR, Liberal Democratic Party, ЛДПР |
| PP-069 | Russian Just Russia | Russian | Just Russia, Справедливая Россия |
| PP-070 | Russian Yabloko | Russian liberal opposition | Yabloko, Яблоко |
| PP-071 | Turkish AKP | Turkish ruling | AKP, AK Parti, Adalet ve Kalkınma Partisi, Justice and Development |
| PP-072 | Turkish CHP | Turkish opposition | CHP, Cumhuriyet Halk Partisi, Republican People's Party |
| PP-073 | Turkish MHP | Turkish nationalist | MHP, Milliyetçi Hareket Partisi |
| PP-074 | Turkish HDP / DEM | Turkish Kurdish | HDP, DEM Party, Halkların Eşitlik ve Demokrasi Partisi |
| PP-075 | Brazilian PT | Brazilian left | PT, Partido dos Trabalhadores, Workers' Party |
| PP-076 | Brazilian PL / PSL | Brazilian right | PL (Liberal), PSL (former Bolsonaro party) |
| PP-077 | Brazilian PSDB | Brazilian centrist | PSDB, Partido da Social Democracia Brasileira |
| PP-078 | Brazilian MDB | Brazilian centrist | MDB, Movimento Democrático Brasileiro |
| PP-079 | Brazilian PSOL | Brazilian far-left | PSOL, Partido Socialismo e Liberdade |
| PP-080 | Mexican Morena | Mexican ruling | Morena, Movimiento Regeneración Nacional |
| PP-081 | Mexican PAN / PRI / PRD | Mexican opposition | PAN, PRI, PRD |
| PP-082 | Argentine peronist / radical | Argentine | Peronist (PJ), Radical Civic Union (UCR), La Libertad Avanza |
| PP-083 | Indian BJP | Indian ruling | BJP, Bharatiya Janata Party |
| PP-084 | Indian Congress / INC | Indian opposition | INC, Indian National Congress, Congress |
| PP-085 | Indian AAP | Indian | AAP, Aam Aadmi Party |
| PP-086 | Indian regional parties | Indian state | DMK (Tamil Nadu), Shiv Sena, TMC (Trinamool), Akali Dal, BJD (Odisha) |
| PP-087 | Japanese LDP | Japanese ruling | LDP, Liberal Democratic Party, 自由民主党, 自民党 |
| PP-088 | Japanese CDP | Japanese opposition | CDP, Constitutional Democratic Party, 立憲民主党 |
| PP-089 | Japanese Komeito | Japanese coalition | Komeito, 公明党 |
| PP-090 | Japanese DPP / JIP / JCP | Japanese minor | DPP (Democratic Party for the People), JIP (Japan Innovation), JCP (Communist Party) |
| PP-091 | Japanese Reiwa / Sansei | Japanese new | Reiwa Shinsengumi (令和新選組), Sanseito (参政党) |
| PP-092 | Korean People Power | Korean conservative | People Power Party, 국민의힘 |
| PP-093 | Korean Democratic | Korean progressive | Democratic Party, 더불어민주당 |
| PP-094 | Korean Justice / Progressive | Korean left | Justice Party, 정의당 |
| PP-095 | Chinese CCP | Chinese ruling | CCP, Chinese Communist Party, 中国共产党, 中共, member of the Party |
| PP-096 | Australian Labor / Liberal | Australian | Labor (Australian Labor Party, ALP), Liberal (Liberal Party of Australia), Nationals, Greens (AU) |
| PP-097 | NZ Labour / National | NZ | Labour (NZ), National (NZ), Greens (NZ), ACT, NZ First |
| PP-098 | Canadian Liberal / Conservative / NDP | Canadian | Liberal Party of Canada, Conservative Party, NDP (New Democratic), Bloc Québécois, Greens |
| PP-099 | Israeli Likud | Israeli right | Likud, ליכוד |
| PP-100 | Israeli Labor / Yesh Atid / Religious Zionism | Israeli | Labor, Yesh Atid (יש עתיד), Religious Zionism, Shas, UTJ |
| PP-101 | Egyptian / Saudi (one-party / limited) | Regional | National Democratic (historical Egypt), Saudi consultative (no parties) |
| PP-102 | South African ANC / EFF / DA | South African | ANC (African National Congress), EFF (Economic Freedom Fighters), DA (Democratic Alliance) |
| PP-103 | Membership phrasing — "registered" | Voter registration | "registered Democrat", "registered Republican", "registered Independent" |
| PP-104 | Membership phrasing — "card-carrying" | Party member | "card-carrying member of the Labour Party", "Communist Party card-carrying member" |
| PP-105 | Membership phrasing — "lifelong" | Loyalty | "lifelong Democrat", "lifelong Tory", "always voted Labour" |
| PP-106 | Membership — "member of" | Direct | "member of the SPD", "Conservative Party member since 2010" |
| PP-107 | Donor / contributor | Funding | "donor to the Democratic Party", "Republican mega-donor", "PAC contributor" |
| PP-108 | Voting history | Pattern | "votes Democrat", "always votes Labour", "Tory voter" |
| PP-109 | Ideology — Conservative | Right-leaning | Conservative, conservative, right-leaning, right-wing |
| PP-110 | Ideology — Liberal | US center-left | Liberal (US), progressive, left-leaning |
| PP-111 | Ideology — Progressive | Modern left | Progressive, progressive movement |
| PP-112 | Ideology — Socialist | Left | Socialist, Democratic Socialist, social democrat |
| PP-113 | Ideology — Communist | Far-left | Communist, Marxist, Maoist, Trotskyist |
| PP-114 | Ideology — Far-right / Nationalist | Far-right | Far-right, ultranationalist, nationalist, ethno-nationalist |
| PP-115 | Ideology — Centrist | Middle | Centrist, moderate, center, middle-of-the-road |
| PP-116 | Ideology — Libertarian | Right-libertarian | Libertarian, classical liberal, minarchist |
| PP-117 | Ideology — Green / Ecologist | Environmental | Green, ecologist, environmentalist (politically active) |
| PP-118 | Coalition / Bloc membership | Cross-party | "EPP member" (European Parliament), "PES affiliate", "EFA member" |
| PP-119 | Position within party | Leadership role | "party chairman", "Whip", "shadow minister", "spokesperson for the Greens" |
| PP-120 | Multilingual context label | Various languages | Political Party (EN), Parti politique (FR), Partei (DE), Partido (ES/PT), Partito (IT), Politieke partij (NL), 政党 (JP), 정당 (KR), 政党 (ZH), Партия (RU), Siyasi parti (TR), حزب سياسي (AR), מפלגה (HE), พรรคการเมือง (TH) |
| PP-121 | Political party in JSON | Structured | "political_party": "Democratic", "party_affiliation": "Conservative" |
| PP-122 | Political party in KV | Form field | political_party=Democratic, party_affiliation=Conservative |
| PP-123 | Political party in XML | Markup | <political_party>Democratic</political_party> |
| PP-124 | Political party in CSV | Tabular | "Smith","John","M","35","Democrat","NY" |
| PP-125 | Embedded in voter registration | Civic | "Voter ID: 12345; Party: Democratic; Precinct: 4B" |
| PP-126 | Embedded in HR/DEI (sensitive) | Workplace | "Self-disclosed political affiliation: Independent" (rarely collected, sensitive) |
| PP-127 | Embedded in donation record | Campaign finance | "Donor: John Smith; Contribution: $500 to Smith for Senate (Dem)" |
| PP-128 | Embedded in legal pleading | Court | "the plaintiff, a registered Democrat, alleges discrimination based on political affiliation" |
| PP-129 | OCR-distorted (party names) | Char substitution | Demoorat (was Democrat — 0 for c), Repuublican (doubled u), Lib Dern (rn for m) |
| PP-130 | OCR diacritic stripping | Lost accents | Sinn Fein (was Sinn Féin), Grune (was Grüne), Pirati (was Piráti) |
| PP-131 | Masked / partial party | Privacy-redacted | Party: ***, Political Party: [REDACTED], affiliation=**** |
| PP-132 | Anonymized placeholder | Standard generic | Party: [Party], Sample party: Democratic |
| PP-133 | Sentence-boundary tricky | Trailing punctuation | "He is a Democrat.", "Is she Republican?", "Party: Labour." |
| PP-134 | Adjacency-tight | No separator | "John Smith,Democrat,35,NY"; "Sarah-Labour-32" |
| PP-135 | Former / past affiliation | History | "former Republican", "ex-Democrat (now Independent)", "left the Conservative Party in 2020" |
| PP-136 | Suspended / expelled | Party action | "expelled from the Labour Party", "membership suspended", "stripped of party whip" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | PP-129, PP-130 |
| Masked / partial / redacted | ✓ | PP-131, PP-132 |
| Multilingual context labels | ✓ | PP-120 |
| Country-specific party coverage | ✓ | PP-001 to PP-102 (30+ countries — US, UK, DE, FR, IT, ES, PT, NL, SE, NO, FI, DK, PL, CZ, HU, RU, TR, BR, MX, AR, IN, JP, KR, ZH, AU, NZ, CA, IL, EG, ZA, plus EU and pan-European blocs) |
| Script variations | ✓ | PP-087, PP-088, PP-089, PP-092, PP-095, PP-099 (JP, KR, ZH, HE) |
| In structured data | ✓ | PP-121, PP-122, PP-123, PP-124 |
| Adjacency-tight | ✓ | PP-134 |
| Sentence-boundary tricky | ✓ | PP-133 |
| Domain-embedded (voter reg/donation/HR/legal) | ✓ | PP-125, PP-126, PP-127, PP-128 |
| Membership phrasings | ✓ | PP-103, PP-104, PP-105, PP-106 |
| Voting history / donor | ✓ | PP-107, PP-108 |
| Ideological labels | ✓ | PP-109 to PP-117 |
| Coalition / bloc | ✓ | PP-118 |
| Leadership position | ✓ | PP-119 |
| Former / suspended | ✓ | PP-135, PP-136 |

**Total patterns for Political_Party: 136**

---

## Entity 22: Country_of_Residence

The country where a person currently lives. Distinct from Nationality (passport identity) and Citizenship_Status (legal authorization). Includes tax residency, domicile, and special territories.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CR-001 | Country name (English) — major | Standard English | United States, United Kingdom, Germany, France, Italy, Spain, Japan, Brazil, India, China |
| CR-002 | Country name (English) — abbreviated | Common short | US, USA, UK, GB, DE, FR, IT, ES, JP, BR, IN, CN |
| CR-003 | Country name (English) — full / official | Official long form | the United States of America, the United Kingdom of Great Britain and Northern Ireland, the Federal Republic of Germany, the People's Republic of China |
| CR-004 | Country name (local language — major) | Native form | France (FR), Deutschland (DE), Italia (IT), España (ES), Brasil (BR), 日本 (JP), 中国 (CN), 한국 (KR) |
| CR-005 | Country name (multilingual) | Translated names | États-Unis (FR for US), Vereinigte Staaten (DE for US), Stati Uniti (IT), Estados Unidos (ES/PT), 米国 (JP for US), 미국 (KR for US), 美国 (ZH for US) |
| CR-006 | ISO 3166-1 alpha-2 | Two-letter code | US, GB, DE, FR, IT, ES, JP, BR, IN, CN, KR, RU |
| CR-007 | ISO 3166-1 alpha-3 | Three-letter code | USA, GBR, DEU, FRA, ITA, ESP, JPN, BRA, IND, CHN, KOR, RUS |
| CR-008 | ISO 3166-1 numeric | Three-digit code | 840 (US), 826 (GB), 276 (DE), 250 (FR), 380 (IT), 392 (JP) |
| CR-009 | With "residing in" prefix | Phrasing | residing in the United States, residing in Japan, living in Germany |
| CR-010 | With "living in" prefix | Phrasing | living in France, lives in Brazil, currently living in Australia |
| CR-011 | With "currently in" / "based in" | Temporary residence | currently in Spain, based in London (UK), based in Singapore |
| CR-012 | "From [country]" | Origin phrasing | originally from Mexico, came from India |
| CR-013 | "I live in" first-person | Self-reference | I live in Germany, my home is in Italy, I am a resident of Spain |
| CR-014 | Domicile | Legal residence | domiciled in the UK, legal domicile: United States |
| CR-015 | Tax residency | Tax-specific | tax resident of Singapore, US tax resident, tax-resident in Portugal |
| CR-016 | Non-domiciled (non-dom, UK) | UK tax status | non-dom resident, non-domiciled, non-dom status |
| CR-017 | Permanent residence | Long-term | permanently resident in France, permanent residence: Spain |
| CR-018 | Temporary residence | Short-term | temporarily residing in Norway, on temporary stay in the Netherlands |
| CR-019 | Multi-country resident | Dual/multi-residence | resident in both US and UK, splits time between Germany and Italy |
| CR-020 | Country of residence + city | Combined | resident in Berlin, Germany; resides in Tokyo, Japan |
| CR-021 | Country of residence on form | Form field | Country of Residence: United States, COR: Japan |
| CR-022 | Multilingual "country of residence" | Form label | Pays de résidence (FR), Wohnsitzland (DE), País de residencia (ES), Paese di residenza (IT), País de residência (PT), 居住国 (JP), 거주 국가 (KR), 居住国家 (ZH), Страна проживания (RU), İkamet ülkesi (TR), بلد الإقامة (AR), ארץ מגורים (HE), ประเทศที่อยู่ (TH), Land van verblijf (NL) |
| CR-023 | Special territories | Non-sovereign | Puerto Rico (US territory), Guam (US), Hong Kong (PRC SAR), Macau (PRC SAR), Greenland (DK) |
| CR-024 | Overseas territories | Dependent territories | Bermuda (UK), Cayman Islands (UK), French Polynesia, New Caledonia (FR) |
| CR-025 | Historical country names | Outdated | USSR (former), East Germany (former), Yugoslavia (former), Czechoslovakia (former) |
| CR-026 | Country name variants | Alternative names | Burma / Myanmar, Czech Republic / Czechia, Côte d'Ivoire / Ivory Coast, Cabo Verde / Cape Verde |
| CR-027 | Country with definite article | "The X" | the Netherlands, the Bahamas, the Philippines, the Czech Republic |
| CR-028 | Country in passport context | Travel doc | "Passport issued: USA; Country of Residence: Germany"; "Resident in: JPN" |
| CR-029 | Country in immigration form | Government | "Country of Residence (last 5 years): USA, France, Spain" |
| CR-030 | Country in tax form | IRS / HMRC | "1040: Country of Residence: USA"; "Form 8938: Foreign country: Switzerland" |
| CR-031 | Country in KYC / AML | Banking | "KYC: Country of Residence: UAE"; "AML check: Country: Singapore" |
| CR-032 | Country in medical record | Clinical | "Patient COR: Brazil; Insurance: Brazilian National Health" |
| CR-033 | Country in HR record | Employment | "Employee Country of Residence: Germany; Work location: Berlin office" |
| CR-034 | Country with FLAG emoji | Modern visual | 🇺🇸 USA, 🇯🇵 Japan, 🇩🇪 Germany, 🇧🇷 Brazil |
| CR-035 | Country code in phone format | Implicit | "+1 (USA/Canada)", "+44 (UK)", "+33 (France)" |
| CR-036 | Country in mailing address | End of address | "100 Park Ave, NY 10017, USA"; "Friedrichstr. 43, 10117 Berlin, Germany" |
| CR-037 | Country adjective form | Demonym implied | "the German resident", "an American resident" (implies country) |
| CR-038 | Country in JSON | Structured | "country_of_residence": "Germany", "country": "Japan", "residence_country": "BR" |
| CR-039 | Country in KV | Form field | country_of_residence=Germany, residence_country=JP, country=USA |
| CR-040 | Country in XML | Markup | <country_of_residence>Germany</country_of_residence>, <country code="JP">Japan</country> |
| CR-041 | Country in CSV | Tabular | "Smith","John","M","35","USA","NY" |
| CR-042 | OCR-distorted country | Char substitution | Unlted States (l for i), Gerrnany (rn for m), Brazll (l for i), J@pan (@ for a) |
| CR-043 | OCR diacritic stripping | Lost accents | Espana (was España), Cote d'Ivoire (was Côte), Brasil (BR vs Brazil EN variant) |
| CR-044 | Masked / partial country | Privacy-redacted | COR: ***, Country: [REDACTED], country_of_residence=**** |
| CR-045 | Country anonymized placeholder | Standard generic | Country: [Country], Sample country: USA |
| CR-046 | Country sentence-boundary | Trailing punctuation | "She lives in Spain.", "Are you in the UK?", "Country: France." |
| CR-047 | Country adjacency-tight | No separator | "John Smith,USA,35,M"; "Sarah-Japan-32"; "ResidenceJapan" |
| CR-048 | Country with city prefix | Combined | "Berlin, Germany"; "Tokyo, Japan"; "São Paulo, Brazil" |
| CR-049 | Embassy / consulate context | Diplomatic | "registered with US Embassy in Berlin, Germany"; "American expat in Japan" |
| CR-050 | Expat / repatriate context | Migration status | "American expat living in Portugal", "British repatriate to UK from Spain" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | CR-042, CR-043 |
| Masked / partial / redacted | ✓ | CR-044, CR-045 |
| Multilingual context labels | ✓ | CR-022 |
| Multilingual country names | ✓ | CR-004, CR-005 |
| Script variations | ✓ | CR-004 (JP, ZH, KR examples) |
| In structured data | ✓ | CR-038, CR-039, CR-040, CR-041 |
| Adjacency-tight | ✓ | CR-047 |
| Sentence-boundary tricky | ✓ | CR-046 |
| Domain-embedded (passport/immigration/tax/KYC/medical/HR) | ✓ | CR-028 to CR-033 |
| ISO 3166 codes (alpha-2, alpha-3, numeric) | ✓ | CR-006, CR-007, CR-008 |
| Special / historical / variant names | ✓ | CR-023, CR-024, CR-025, CR-026, CR-027 |
| Tax / domicile distinctions | ✓ | CR-014, CR-015, CR-016 |
| Multi-country residence | ✓ | CR-019, CR-050 |
| Country prefixes / phrasings | ✓ | CR-009 to CR-013 |

**Total patterns for Country_of_Residence: 50**

---

## Entity 23: Location

Generic geographic / spatial location. Distinct from City (just city), State (sub-national), Country (sovereign). Location is a generic span — could be a landmark, building, region, GPS coords, or "near X" reference.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| LOC-001 | City + Country | Geographic combination | Tokyo, Japan; New York, USA; Paris, France; Cairo, Egypt |
| LOC-002 | City + State + Country | Three-level | Springfield, IL, USA; Brisbane, QLD, Australia |
| LOC-003 | Landmark name | Famous landmark | the Eiffel Tower, Big Ben, the Statue of Liberty, the Great Wall, Mount Fuji |
| LOC-004 | Landmark + city | Combined | the Louvre in Paris, Times Square in NYC, the Vatican in Rome |
| LOC-005 | Geographic feature — mountain | Natural feature | Mount Kilimanjaro, the Himalayas, the Alps, the Rockies, Mount Everest, Mt. Fuji, Mt. Etna |
| LOC-006 | Geographic feature — river | Natural feature | the Nile, the Amazon, the Mississippi, the Thames, the Rhine, the Ganges, the Yangtze |
| LOC-007 | Geographic feature — lake | Natural feature | Lake Tahoe, Lake Geneva, Lake Victoria, the Great Lakes, Loch Ness |
| LOC-008 | Geographic feature — ocean / sea | Natural feature | the Atlantic, the Pacific, the Mediterranean, the Caribbean, the South China Sea, the Indian Ocean |
| LOC-009 | Geographic feature — desert | Natural feature | the Sahara, the Gobi, the Atacama, the Kalahari, Death Valley |
| LOC-010 | Geographic feature — forest / jungle | Natural feature | the Amazon Rainforest, the Black Forest, the Congo Basin, the Daintree Rainforest |
| LOC-011 | Geographic feature — island | Insular | Maui, Hokkaido, Sicily, Bali, Manhattan (technical island), Easter Island |
| LOC-012 | Region / area / metro | Sub-national | the Bay Area, Silicon Valley, the Ruhr, the Riviera, Greater London, Tri-State Area |
| LOC-013 | Neighborhood / district | Urban subdivision | Brooklyn (NYC), Shibuya (Tokyo), Le Marais (Paris), Soho (London), Eixample (Barcelona) |
| LOC-014 | Building / venue | Specific structure | the Empire State Building, the Sydney Opera House, Wembley Stadium, Madison Square Garden |
| LOC-015 | Tourist attraction / park | Public space | Central Park, Hyde Park, Yellowstone National Park, Disneyland, Disney World |
| LOC-016 | University / campus | Educational | MIT campus, Stanford campus, Cambridge University, Oxford (academic) |
| LOC-017 | Hospital / medical complex | Healthcare facility | Mayo Clinic, Cleveland Clinic, Massachusetts General Hospital, Mount Sinai Hospital |
| LOC-018 | Airport name / code | Travel hub | JFK (Airport), LAX, Heathrow, Charles de Gaulle (CDG), Tokyo Narita, Haneda |
| LOC-019 | Train station / transit hub | Transit point | Grand Central Terminal, King's Cross, Gare du Nord, Tokyo Station, Shinjuku Station |
| LOC-020 | Port / harbor | Maritime | the Port of Rotterdam, Singapore Port, the Port of Shanghai, the Port of LA/Long Beach |
| LOC-021 | Border crossing | Geographic boundary | the US-Mexico border, Checkpoint Charlie, the DMZ (Korean), Dover-Calais crossing |
| LOC-022 | Bridge / tunnel | Engineered crossing | the Golden Gate Bridge, the Channel Tunnel, the Brooklyn Bridge, the Bosphorus Bridge |
| LOC-023 | Embassy / consulate | Diplomatic | the US Embassy in Tokyo, the British High Commission in Delhi, the French Consulate in NYC |
| LOC-024 | Government building | Official | the White House, the Kremlin, 10 Downing Street, the Élysée Palace, the Diet Building |
| LOC-025 | Religious site | Sacred place | the Vatican, Mecca, Jerusalem (Old City), the Western Wall, Bodh Gaya, the Golden Temple |
| LOC-026 | Cemetery / memorial | Memorial | Arlington National Cemetery, Père Lachaise, the Vietnam Memorial, Ground Zero |
| LOC-027 | Military base | Defense | Pentagon, Fort Bragg, Camp Pendleton, Ramstein AFB, Yokota AB, Andrews AFB |
| LOC-028 | Refugee camp | Crisis site | Zaatari camp (Jordan), Cox's Bazar (Bangladesh), Kakuma camp (Kenya), Dadaab camp (Kenya) |
| LOC-029 | Coordinates — Decimal degrees | GPS | 40.7128, -74.0060; 35.6762, 139.6503; -33.8688, 151.2093 |
| LOC-030 | Coordinates — DMS | Degrees-minutes-seconds | 40°42'46" N, 74°00'21" W; 35°40'34" N, 139°39'01" E |
| LOC-031 | Coordinates — sexagesimal | Mixed | 40° 42' 46.0008'' N, 74° 0' 21.5184'' W |
| LOC-032 | Coordinates — UTM | Universal Transverse Mercator | 18T 583960 4507523 (NYC in UTM) |
| LOC-033 | Plus Code (Open Location Code) | Google Plus Code | 87G7PXM5+JR (NYC), 8Q7XRJX5+5G (Tokyo) |
| LOC-034 | What3Words | 3-word geocoding | ///filled.count.soap, ///table.book.chair |
| LOC-035 | "Near X" / "next to Y" | Relative location | "near the airport", "next to the post office", "across from City Hall", "by the river" |
| LOC-036 | "On the corner of X and Y" | Intersection | "on the corner of 5th Avenue and 42nd Street", "intersection of A Street and B Avenue" |
| LOC-037 | "X miles from Y" | Distance reference | "20 miles north of Boston", "5 km from city center", "200 m from the beach" |
| LOC-038 | Compass direction | Cardinal | northern Italy, southern France, the Pacific Northwest, the Southeast, the Midwest |
| LOC-039 | Time zone reference | Temporal-geo | "EST (US East)", "PST (US West)", "CET (Central Europe)", "JST (Japan)", "GMT/UTC" |
| LOC-040 | Continent | Highest level | North America, Europe, Asia, Africa, South America, Oceania, Antarctica |
| LOC-041 | Sub-continent / geo-region | Cultural-geo region | Southeast Asia, the Middle East, Sub-Saharan Africa, the Caribbean, Eastern Europe |
| LOC-042 | "Hometown" reference | Personal | "from my hometown of Springfield", "born and raised in Brooklyn", "raised in rural Kansas" |
| LOC-043 | "Workplace" / "office" | Personal work | "at the office", "in the lab", "at my workplace", "in the conference room" |
| LOC-044 | Café / coffeeshop | Common meeting place | "at Starbucks on 5th Avenue", "the café on the corner", "my local Costa Coffee" |
| LOC-045 | Restaurant / bar | Hospitality | "Le Bernardin", "Joe's Pizza", "the bar across the street" |
| LOC-046 | Mall / shopping center | Commercial | "Mall of America", "Westfield Stratford City", "Bullring (Birmingham)" |
| LOC-047 | Multilingual location name | Native script | 東京 (Tokyo), 北京 (Beijing), 서울 (Seoul), Москва (Moscow), القاهرة (Cairo), ירושלים (Jerusalem), กรุงเทพฯ (Bangkok) |
| LOC-048 | Spelled out coordinates | Verbalized | "forty point seven degrees north, seventy-four degrees west" |
| LOC-049 | Location in Maps URL | URL embedded | google.com/maps?q=40.7128,-74.0060, maps.apple.com/?ll=35.6762,139.6503 |
| LOC-050 | Location in JSON | Structured | "location": "Tokyo, Japan", "coordinates": [40.7128, -74.0060], "venue": "Madison Square Garden" |
| LOC-051 | Location in KV | Form field | location=Tokyo, venue=MSG, coordinates=40.7128,-74.0060 |
| LOC-052 | Location in XML | Markup | <location>Tokyo, Japan</location>, <coordinates lat="40.7128" lon="-74.0060"/> |
| LOC-053 | Location in CSV | Tabular | "Smith","John","Meeting","Conference Room 4B","2024-03-15" |
| LOC-054 | Location in geo-tagged photo | EXIF data | "Photo location: 40.7128° N, 74.0060° W", "GPS coords from EXIF: ..." |
| LOC-055 | Location in social media post | Geo-tag | "Posted from Times Square, NYC", "Checked in at Eiffel Tower" |
| LOC-056 | OCR-distorted location name | Char substitution | T1mes Square (1 for i), 5tarbucks (5 for S), Bro0klyn (0 for o) |
| LOC-057 | OCR diacritic stripping | Lost accents | Sao Paulo (was São Paulo), Cote d'Azur (was Côte), Wurzburg (was Würzburg) |
| LOC-058 | Masked / partial location | Privacy-redacted | location: ***, met at [REDACTED], near *** Park, somewhere in **** |
| LOC-059 | Location sentence-boundary | Trailing punctuation | "We met at Times Square.", "Are you in Tokyo?", "Location: NYC." |
| LOC-060 | Location adjacency-tight | No separator | "John Smith,Tokyo,2024-03-15"; "Sarah-Brooklyn-Meeting"; "MeetingPoint:NYC" |
| LOC-061 | Multilingual "Location:" label | Form label | Location (EN), Lieu (FR), Ort (DE), Ubicación / Lugar (ES), Luogo (IT), Local (PT), 場所 (JP), 위치 (KR), 位置 / 地点 (ZH), Местоположение (RU), Konum (TR), موقع (AR), מיקום (HE), ที่ตั้ง (TH) |
| LOC-062 | Region with administrative level | Administrative | "Greater Tokyo Area", "Metropolitan Statistical Area (MSA)", "Île-de-France region" |
| LOC-063 | Postal / ZIP code area | Mailing zone | "ZIP code 10017 (Midtown Manhattan)", "Postcode SW1A (Westminster)", "PLZ 10117 (Berlin-Mitte)" |
| LOC-064 | Conference / event venue | Specific gathering | "RSA Conference at Moscone Center", "K-Con at SVP Pavilion", "WWDC at Apple Park" |
| LOC-065 | Coworking space | Modern workplace | "WeWork at Chelsea Market", "Regus at Manhattan", "Industrious in SoHo" |
| LOC-066 | Hotel / resort | Hospitality stay | "Marriott in Times Square", "Four Seasons George V Paris", "Park Hyatt Tokyo" |
| LOC-067 | Anonymized placeholder location | Standard generic | Location: [Location], Sample location: NYC, "Place A" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | LOC-056, LOC-057 |
| Masked / partial / redacted | ✓ | LOC-058, LOC-067 |
| Multilingual context labels | ✓ | LOC-061 |
| Multilingual location names | ✓ | LOC-047 |
| Script variations | ✓ | LOC-047 (JP, ZH, KR, RU, AR, HE, TH) |
| In structured data | ✓ | LOC-050, LOC-051, LOC-052, LOC-053 |
| Adjacency-tight | ✓ | LOC-060 |
| Sentence-boundary tricky | ✓ | LOC-059 |
| Embedded in URL/path | ✓ | LOC-049, LOC-054, LOC-055 |
| Coordinate systems (decimal, DMS, UTM, Plus Code, What3Words) | ✓ | LOC-029 to LOC-034 |
| Geographic feature types (mountain, river, lake, ocean, desert, forest, island) | ✓ | LOC-005 to LOC-011 |
| Domain-embedded (geo-tagged photos / social) | ✓ | LOC-054, LOC-055 |
| Region / district / metro | ✓ | LOC-012, LOC-013, LOC-040, LOC-041, LOC-062 |
| Built environments (airport, station, port, embassy, base, etc.) | ✓ | LOC-018 to LOC-027, LOC-064 to LOC-066 |
| Relative location | ✓ | LOC-035, LOC-036, LOC-037, LOC-038 |
| Verbalized coordinates | ✓ | LOC-048 |

**Total patterns for Location: 67**

---

## Entity 24: City

City or town name. The most common geographic PII.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CITY-001 | Major world city — English | Standard | New York, London, Paris, Tokyo, Berlin, Sydney, Rio de Janeiro, Mumbai, Shanghai, Cairo |
| CITY-002 | Major US city | US | Los Angeles, Chicago, Houston, Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Austin, Boston |
| CITY-003 | Mid-tier US city | US smaller | Cambridge, Portland (OR), Portland (ME), Springfield (IL), Springfield (MA), Concord (NH) |
| CITY-004 | Common US city abbreviation | US shortform | NYC, LA, SF, DC, Philly, Vegas, ATL (Atlanta), NOLA (New Orleans) |
| CITY-005 | Major UK city | UK | London, Manchester, Birmingham, Glasgow, Edinburgh, Liverpool, Leeds, Cardiff, Belfast, Bristol |
| CITY-006 | UK city abbreviation | UK shortform | LDN (London), Brum (Birmingham), Mancs (Manchester), Edinburgh sometimes "Embra" |
| CITY-007 | Major German city | DE | Berlin, Hamburg, München (Munich), Köln (Cologne), Frankfurt am Main, Stuttgart, Düsseldorf, Leipzig, Dresden |
| CITY-008 | German city + suffix | DE typing | Frankfurt am Main, Frankfurt (Oder), Berlin-Mitte, München-Schwabing |
| CITY-009 | Major French city | FR | Paris, Marseille, Lyon, Toulouse, Nice, Nantes, Strasbourg, Montpellier, Bordeaux, Lille |
| CITY-010 | Major Italian city | IT | Roma (Rome), Milano (Milan), Napoli (Naples), Torino (Turin), Palermo, Genova, Bologna, Firenze (Florence), Bari, Catania |
| CITY-011 | Major Spanish city | ES | Madrid, Barcelona, Valencia, Sevilla (Seville), Zaragoza, Málaga, Murcia, Palma, Bilbao, Las Palmas |
| CITY-012 | Major Brazilian city | BR | São Paulo, Rio de Janeiro, Salvador, Brasília, Fortaleza, Belo Horizonte, Manaus, Curitiba, Recife, Porto Alegre |
| CITY-013 | Major Mexican city | MX | Ciudad de México (CDMX / Mexico City), Guadalajara, Monterrey, Puebla, Tijuana, León, Mérida, Cancún |
| CITY-014 | Major Canadian city | CA | Toronto, Montréal (Montreal), Vancouver, Calgary, Ottawa, Edmonton, Winnipeg, Québec City, Halifax |
| CITY-015 | Major Australian city | AU | Sydney, Melbourne, Brisbane, Perth, Adelaide, Gold Coast, Newcastle, Canberra, Hobart, Darwin |
| CITY-016 | Major Japanese city (English) | JP romanized | Tokyo, Osaka, Yokohama, Nagoya, Sapporo, Fukuoka, Kobe, Kyoto, Hiroshima |
| CITY-017 | Japanese city in kanji | JP native | 東京 (Tokyo), 大阪 (Osaka), 横浜 (Yokohama), 名古屋 (Nagoya), 札幌 (Sapporo), 福岡 (Fukuoka), 京都 (Kyoto), 神戸 (Kobe), 広島 (Hiroshima) |
| CITY-018 | Major Korean city (English) | KR romanized | Seoul, Busan, Incheon, Daegu, Daejeon, Gwangju, Suwon, Ulsan, Sejong |
| CITY-019 | Korean city in hangul | KR native | 서울 (Seoul), 부산 (Busan), 인천 (Incheon), 대구 (Daegu), 대전 (Daejeon), 광주 (Gwangju) |
| CITY-020 | Major Chinese city (English) | CN romanized | Beijing, Shanghai, Guangzhou, Shenzhen, Chengdu, Chongqing, Tianjin, Wuhan, Xi'an, Hangzhou |
| CITY-021 | Chinese city in hanzi | CN native | 北京 (Beijing), 上海 (Shanghai), 广州 (Guangzhou), 深圳 (Shenzhen), 成都 (Chengdu), 重庆 (Chongqing) |
| CITY-022 | Traditional Chinese / Taiwan city | TW | 台北 (Taipei), 高雄 (Kaohsiung), 台中 (Taichung), 台南 (Tainan) |
| CITY-023 | Hong Kong | HK | Hong Kong, 香港 (HK Chinese), Kowloon, Mong Kok, Central, Wan Chai |
| CITY-024 | Singapore | SG | Singapore, 新加坡 (ZH), シンガポール (JP) |
| CITY-025 | Major Indian city (English) | IN | Mumbai, Delhi, Bangalore (Bengaluru), Hyderabad, Chennai, Kolkata, Ahmedabad, Pune, Jaipur, Lucknow |
| CITY-026 | Major Russian city (English) | RU romanized | Moscow, Saint Petersburg, Novosibirsk, Yekaterinburg, Kazan, Nizhny Novgorod, Samara, Vladivostok |
| CITY-027 | Russian city in Cyrillic | RU native | Москва (Moscow), Санкт-Петербург (SPb), Новосибирск (Novosibirsk), Казань (Kazan) |
| CITY-028 | Major Arab city (English) | AR | Cairo, Dubai, Riyadh, Casablanca, Algiers, Tunis, Tripoli, Baghdad, Damascus, Beirut, Amman, Doha, Manama, Muscat |
| CITY-029 | Arabic city in native script | AR native | القاهرة (Cairo), الرياض (Riyadh), دبي (Dubai), بيروت (Beirut), دمشق (Damascus), بغداد (Baghdad) |
| CITY-030 | Major Israeli city | IL | Tel Aviv, Jerusalem, Haifa, Eilat, Beersheba, Netanya, Ashdod |
| CITY-031 | Hebrew city in native script | IL native | תל אביב (Tel Aviv), ירושלים (Jerusalem), חיפה (Haifa), אילת (Eilat) |
| CITY-032 | Major Thai city (English) | TH romanized | Bangkok, Chiang Mai, Phuket, Pattaya, Ayutthaya, Hua Hin |
| CITY-033 | Thai city in native script | TH native | กรุงเทพมหานคร (Bangkok), เชียงใหม่ (Chiang Mai), ภูเก็ต (Phuket), พัทยา (Pattaya) |
| CITY-034 | Major Turkish city | TR | Istanbul, Ankara, Izmir, Bursa, Antalya, Gaziantep, Adana, Konya |
| CITY-035 | Major Polish city | PL | Warszawa (Warsaw), Kraków (Krakow), Łódź, Wrocław, Poznań, Gdańsk, Lublin |
| CITY-036 | Major Czech / Slovak city | CZ / SK | Praha (Prague), Brno, Ostrava, Bratislava (Slovakia), Košice (Slovakia) |
| CITY-037 | Major Hungarian city | HU | Budapest, Debrecen, Szeged, Pécs, Győr |
| CITY-038 | Major Dutch / Belgian city | NL / BE | Amsterdam, Rotterdam, The Hague (Den Haag), Utrecht, Brussels (Bruxelles), Antwerp |
| CITY-039 | Major Nordic city | SE / NO / DK / FI | Stockholm, Göteborg (Gothenburg), Oslo, Bergen, Copenhagen (København), Helsinki, Reykjavík |
| CITY-040 | Major African city | AF | Lagos, Cairo, Johannesburg, Nairobi, Kinshasa, Casablanca, Cape Town, Addis Ababa, Khartoum, Dakar |
| CITY-041 | City + state/province (US) | Disambiguation | Portland, OR; Portland, ME; Springfield, IL; Springfield, MA; Kansas City, MO; Kansas City, KS |
| CITY-042 | City + country | International disambiguation | London, UK; London, Ontario; Cambridge, UK; Cambridge, MA, USA |
| CITY-043 | Historical / former city name | Outdated | Bombay (now Mumbai), Calcutta (Kolkata), Madras (Chennai), Peking (Beijing), Leningrad (St. Petersburg), Constantinople (Istanbul), Saigon (Ho Chi Minh City), Edo (Tokyo), Königsberg (Kaliningrad) |
| CITY-044 | City rebranding | Recent change | Kyiv (formerly Kiev, post-2022), Czechia (formerly Czech Republic) |
| CITY-045 | Sister-city pair | Paired | "sister cities Paris-Tokyo", "twin cities Berlin-Buenos Aires" |
| CITY-046 | Capital city indicator | Political | "the capital, Tokyo"; "Washington DC (capital of USA)"; "Brasília (capital)" |
| CITY-047 | City with definite article | "The city of" | the city of Paris, the city of New York, "in the city of Madrid" |
| CITY-048 | Metropolitan area / Greater X | Metro reference | Greater London, Greater Tokyo Area, Greater LA, the Bay Area (San Francisco metro) |
| CITY-049 | City with transit reference | Implicit | "took the metro from Times Square to Central Park" (NYC implied) |
| CITY-050 | City as hometown identifier | Personal | "Berlin-born", "London-based", "Tokyo native", "from Mumbai originally" |
| CITY-051 | City informal nickname | Slang | the Big Apple (NYC), the City of Light (Paris), the Eternal City (Rome), the Big Easy (New Orleans), Bay Area (SF), the Windy City (Chicago) |
| CITY-052 | City + airport code | Travel | "JFK NYC", "NRT Tokyo", "LHR London", "CDG Paris" |
| CITY-053 | Country capital | Implied national identity | "Washington" (US), "Beijing" (China), "Brasília" (Brazil), "Canberra" (Australia) |
| CITY-054 | Multilingual city name | Same city in many langs | Vienna (EN) / Wien (DE) / Vienne (FR) / Bécs (HU); Munich (EN) / München (DE); Florence (EN) / Firenze (IT) |
| CITY-055 | City in passport stamp | Travel doc | "Stamped in: Tokyo, JPN, 2024-03-15"; "Entry: London Heathrow" |
| CITY-056 | City in mailing address | Address component | "100 Park Ave, New York, NY 10017"; "Friedrichstr. 43, 10117 Berlin" |
| CITY-057 | City in JSON | Structured | "city": "New York", "city_of_residence": "Tokyo", "birthplace_city": "Mumbai" |
| CITY-058 | City in KV | Form field | city=New York, City of Birth: Tokyo, RESIDENCE_CITY: BERLIN |
| CITY-059 | City in XML | Markup | <city>New York</city>, <city_of_birth>Tokyo</city_of_birth> |
| CITY-060 | City in CSV | Tabular | "Smith","John","M","35","New York","NY" |
| CITY-061 | OCR-distorted city | Char substitution | Pa1ls (was Paris), N3w York (3 for e), LOndon (zero for O), T0ky0 (zero for o) |
| CITY-062 | OCR diacritic stripping | Lost accents | Sao Paulo (was São Paulo), Munchen (was München), Zurich (was Zürich), Cologne anglicized |
| CITY-063 | Masked / partial city | Privacy-redacted | City: ***, born in *** city, *** York (NY masked), [REDACTED] |
| CITY-064 | City anonymized placeholder | Standard generic | City: [City], Sample city: NYC, "City A" |
| CITY-065 | City sentence-boundary | Trailing punctuation | "She lives in Berlin.", "Are you in Tokyo?", "City: Paris." |
| CITY-066 | City adjacency-tight | No separator | "John Smith,NYC,35,M"; "Sarah-Berlin-32"; "TokyoResident" |
| CITY-067 | Multilingual "City:" label | Form label | City (EN), Ville (FR), Stadt (DE), Ciudad (ES), Città (IT), Cidade (PT), 市 (JP), 도시 (KR), 城市 (ZH), Город (RU), Şehir (TR), مدينة (AR), עיר (HE), เมือง (TH) |
| CITY-068 | Embedded in social media post | Geo-tag | "Posted from Times Square, NYC", "Checked in: Berlin Hauptbahnhof", "Eiffel Tower, Paris 🗼" |
| CITY-069 | Embedded in journalism / news | News context | "Reuters / Tokyo, March 15 — ...", "BERLIN (AFP) — ...", "Reporting from Cairo" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | CITY-061, CITY-062 |
| Masked / partial / redacted | ✓ | CITY-063, CITY-064 |
| Multilingual context labels | ✓ | CITY-067 |
| Multilingual city names | ✓ | CITY-054 |
| Script variations | ✓ | CITY-017, CITY-019, CITY-021, CITY-022, CITY-027, CITY-029, CITY-031, CITY-033 |
| In structured data | ✓ | CITY-057, CITY-058, CITY-059, CITY-060 |
| Adjacency-tight | ✓ | CITY-066 |
| Sentence-boundary tricky | ✓ | CITY-065 |
| Domain-embedded (passport/address/social/news) | ✓ | CITY-055, CITY-056, CITY-068, CITY-069 |
| Country coverage | ✓ | CITY-001 to CITY-040 (40+ countries with major cities) |
| Historical / former names | ✓ | CITY-043, CITY-044 |
| Disambiguation (city + state/country) | ✓ | CITY-041, CITY-042 |
| Informal / nickname | ✓ | CITY-051 |
| Metro / region | ✓ | CITY-048 |
| Hometown / personal identifier | ✓ | CITY-050 |

**Total patterns for City: 69**

---

## Entity 25: State

State / province / region — sub-national administrative division. Highly country-specific.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| ST-001 | US state name — full | Spelled out | California, New York, Texas, Florida, Illinois, Pennsylvania, Ohio, Georgia, North Carolina, Michigan |
| ST-002 | US state — 2-letter abbreviation | USPS code | CA, NY, TX, FL, IL, PA, OH, GA, NC, MI, MA, WA, OR, CO, AZ, MN, WI, VA, MD, NJ |
| ST-003 | US territory | Non-state | Puerto Rico (PR), Guam (GU), US Virgin Islands (VI), American Samoa (AS), Northern Mariana Islands (MP), Washington DC (DC) |
| ST-004 | US state with descriptor | Common phrasing | "the state of California", "in California", "California-based", "California resident" |
| ST-005 | Canadian province — full | Spelled out | Ontario, Quebec, British Columbia, Alberta, Manitoba, Saskatchewan, Nova Scotia, New Brunswick, Newfoundland and Labrador, Prince Edward Island |
| ST-006 | Canadian province — 2-letter abbreviation | Canada Post code | ON, QC, BC, AB, MB, SK, NS, NB, NL, PE |
| ST-007 | Canadian territory | Non-province | Northwest Territories (NT), Yukon (YT), Nunavut (NU) |
| ST-008 | Australian state — full | Spelled out | New South Wales, Victoria, Queensland, Western Australia, South Australia, Tasmania |
| ST-009 | Australian state — abbreviation | Common code | NSW, VIC, QLD, WA, SA, TAS, NT (Northern Territory), ACT (Australian Capital Territory) |
| ST-010 | German Bundesland — full | DE state | Bayern (Bavaria), Baden-Württemberg, Nordrhein-Westfalen (NRW), Hessen, Niedersachsen, Sachsen, Rheinland-Pfalz, Berlin, Hamburg, Bremen |
| ST-011 | German Bundesland — abbreviation | DE state code | BY (Bayern), BW (Baden-Württemberg), NRW, HE, NI, SN, RP, BE, HH, HB |
| ST-012 | Austrian Bundesland | AT state | Wien (Vienna), Niederösterreich, Oberösterreich, Steiermark, Tirol, Kärnten, Salzburg, Burgenland, Vorarlberg |
| ST-013 | Swiss canton | CH | Zürich, Bern, Vaud, Genf, Basel-Stadt, Tessin, Luzern, Aargau |
| ST-014 | French région | FR (post-2016 13 régions) | Île-de-France, Auvergne-Rhône-Alpes, Provence-Alpes-Côte d'Azur (PACA), Hauts-de-France, Nouvelle-Aquitaine, Occitanie, Grand Est, Bretagne, Normandie |
| ST-015 | French département | FR sub-region | Paris (75), Hauts-de-Seine (92), Bouches-du-Rhône (13), Nord (59), Rhône (69) |
| ST-016 | Italian region | IT | Lombardia, Lazio, Campania, Veneto, Piemonte, Sicilia, Toscana, Emilia-Romagna, Calabria, Puglia |
| ST-017 | Italian province (2-letter) | IT province code | MI (Milano), RM (Roma), NA (Napoli), TO (Torino), FI (Firenze), BO (Bologna), VE (Venezia) |
| ST-018 | Spanish autonomous community | ES | Andalucía, Cataluña, Comunidad de Madrid, Comunidad Valenciana, Galicia, Castilla y León, País Vasco, Castilla-La Mancha, Canarias, Aragón, Murcia, Asturias, Navarra, Cantabria, La Rioja, Extremadura |
| ST-019 | Spanish province | ES sub-region | Madrid, Barcelona, Sevilla, Valencia, Zaragoza, Málaga, Bilbao (Vizcaya), Alicante |
| ST-020 | Portuguese district | PT (mainland) | Lisboa, Porto, Setúbal, Faro, Coimbra, Aveiro, Braga, Leiria |
| ST-021 | Brazilian state — full | BR state | São Paulo, Rio de Janeiro, Minas Gerais, Bahia, Paraná, Rio Grande do Sul, Pernambuco, Ceará |
| ST-022 | Brazilian state — abbreviation | BR state code | SP, RJ, MG, BA, PR, RS, PE, CE, SC, GO, DF (Distrito Federal), AM, PA, MA |
| ST-023 | Mexican state — full | MX state | Jalisco, Nuevo León, Estado de México (Edomex), Veracruz, Puebla, Guanajuato, Chihuahua, Sonora, Baja California, Yucatán |
| ST-024 | Mexican state — abbreviation | MX state code | JAL, NL, MEX, VER, PUE, GTO, CHIH, SON, BC, YUC |
| ST-025 | Mexico City | MX special | Ciudad de México (CDMX, formerly Distrito Federal/DF) |
| ST-026 | Indian state — full | IN | Maharashtra, Tamil Nadu, Uttar Pradesh, Karnataka, Gujarat, West Bengal, Rajasthan, Madhya Pradesh, Bihar, Andhra Pradesh, Telangana, Kerala, Punjab, Haryana, Odisha |
| ST-027 | Indian Union Territory | IN | Delhi (NCT), Chandigarh, Jammu and Kashmir, Ladakh, Puducherry, Andaman and Nicobar Islands, Lakshadweep, Daman and Diu (now merged), Dadra and Nagar Haveli (merged) |
| ST-028 | Indian state abbreviation | IN code | MH (Maharashtra), TN (Tamil Nadu), UP (Uttar Pradesh), KA (Karnataka), GJ (Gujarat), WB (West Bengal), DL (Delhi), HR (Haryana) |
| ST-029 | Chinese province | CN | 北京 (Beijing — municipality), 上海 (Shanghai — municipality), 广东 (Guangdong), 江苏 (Jiangsu), 山东 (Shandong), 浙江 (Zhejiang), 四川 (Sichuan), 河南 (Henan), 河北 (Hebei), 湖北 (Hubei), 福建 (Fujian) |
| ST-030 | Chinese autonomous region | CN special | 新疆 (Xinjiang), 西藏 (Tibet), 内蒙古 (Inner Mongolia), 广西 (Guangxi), 宁夏 (Ningxia) |
| ST-031 | Chinese province (English / pinyin) | CN romanized | Guangdong, Jiangsu, Shandong, Zhejiang, Sichuan, Henan, Hebei, Hubei, Fujian, Anhui, Yunnan, Liaoning, Hunan, Shaanxi |
| ST-032 | Japanese prefecture | JP | 東京都 (Tokyo), 大阪府 (Osaka), 京都府 (Kyoto), 北海道 (Hokkaido), 神奈川県 (Kanagawa), 愛知県 (Aichi), 福岡県 (Fukuoka), 兵庫県 (Hyogo), 千葉県 (Chiba), 埼玉県 (Saitama) |
| ST-033 | Japanese prefecture (English) | JP romanized | Tokyo, Osaka, Kyoto, Hokkaido, Kanagawa, Aichi, Fukuoka, Hyogo, Chiba, Saitama, Hiroshima |
| ST-034 | Korean province / metropolitan city | KR | 서울특별시 (Seoul), 부산광역시 (Busan), 인천광역시 (Incheon), 경기도 (Gyeonggi), 강원도 (Gangwon), 충청북도 (Chungcheongbuk-do), 전라남도 (Jeollanam-do), 제주특별자치도 (Jeju) |
| ST-035 | Korean province (English) | KR romanized | Seoul, Busan, Incheon, Gyeonggi, Gangwon, North Chungcheong, South Jeolla, Jeju |
| ST-036 | UK constituent country | UK | England, Scotland, Wales, Northern Ireland |
| ST-037 | UK county | UK sub-national | Yorkshire, Lancashire, Kent, Sussex, Surrey, Hampshire, Cornwall, Devon, Cheshire |
| ST-038 | UK city-region / metropolitan area | UK metro | Greater London, Greater Manchester, West Midlands (Birmingham metro), Merseyside, West Yorkshire |
| ST-039 | Scotland — council area | Scotland sub | Highland, Edinburgh, Glasgow, Fife, Aberdeenshire, Renfrewshire |
| ST-040 | Russian federal subject | RU | Москва (Moscow), Санкт-Петербург (SPb), Московская область, Республика Татарстан, Краснодарский край |
| ST-041 | Russian federal subject — English | RU romanized | Moscow Oblast, Saint Petersburg, Tatarstan, Krasnodar Krai, Sverdlovsk Oblast |
| ST-042 | Turkish il (province) | TR | İstanbul, Ankara, İzmir, Bursa, Antalya, Konya, Gaziantep, Adana, Mersin, Şanlıurfa |
| ST-043 | Polish voivodeship | PL | Mazowieckie, Małopolskie, Wielkopolskie, Śląskie, Dolnośląskie, Łódzkie, Pomorskie, Lubelskie |
| ST-044 | Czech kraj (region) | CZ | Praha, Středočeský, Jihočeský, Plzeňský, Karlovarský, Ústecký, Liberecký, Královéhradecký |
| ST-045 | Hungarian county | HU | Pest megye, Bács-Kiskun, Hajdú-Bihar, Csongrád-Csanád, Borsod-Abaúj-Zemplén, Győr-Moson-Sopron |
| ST-046 | Dutch province | NL | Noord-Holland, Zuid-Holland, Utrecht, Gelderland, Noord-Brabant, Limburg, Friesland, Drenthe |
| ST-047 | Belgian region | BE | Vlaanderen (Flanders), Wallonie (Wallonia), Brussels (Bruxelles) |
| ST-048 | Swedish län | SE | Stockholms län, Västra Götalands län, Skåne län, Östergötlands län |
| ST-049 | Norwegian fylke | NO | Oslo, Viken, Innlandet, Vestland, Trøndelag, Rogaland, Nordland |
| ST-050 | Danish region | DK | Hovedstaden (Capital), Sjælland, Syddanmark, Midtjylland, Nordjylland |
| ST-051 | Finnish region (maakunta) | FI | Uusimaa, Pirkanmaa, Pohjois-Pohjanmaa, Varsinais-Suomi |
| ST-052 | South African province | ZA | Gauteng, Western Cape, KwaZulu-Natal, Eastern Cape, Free State, Limpopo, Mpumalanga, North West, Northern Cape |
| ST-053 | Argentine province | AR | Buenos Aires, Córdoba, Santa Fe, Mendoza, Salta, Tucumán, Entre Ríos |
| ST-054 | Israeli district | IL | Tel Aviv District, Central District, Jerusalem District, Northern District, Southern District, Haifa District |
| ST-055 | Saudi Arabian region | SA | Riyadh, Makkah, Medina, Eastern Province, Asir, Tabuk, Al Bahah, Hail |
| ST-056 | UAE emirate | AE | Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah |
| ST-057 | Iranian province | IR | Tehran, Isfahan, Razavi Khorasan, East Azerbaijan, Fars, Khuzestan |
| ST-058 | Pakistani province | PK | Punjab, Sindh, Khyber Pakhtunkhwa, Balochistan, Islamabad Capital Territory |
| ST-059 | Indonesian province | ID | Jakarta, West Java, East Java, Central Java, Bali, North Sumatra, South Sulawesi, Papua |
| ST-060 | Vietnamese province | VN | Hà Nội (Hanoi), Hồ Chí Minh (HCMC), Đà Nẵng, Hải Phòng, Cần Thơ, Huế |
| ST-061 | Thai province (changwat) | TH | กรุงเทพมหานคร (Bangkok), เชียงใหม่ (Chiang Mai), ภูเก็ต (Phuket), ขอนแก่น (Khon Kaen) |
| ST-062 | Philippine region | PH | National Capital Region (NCR/Metro Manila), Cebu, Davao, CALABARZON, Central Luzon |
| ST-063 | Multilingual "State:" label | Form label | State (EN), État (FR), Bundesland (DE), Estado (ES/PT), Stato (IT), Staat (NL), 都道府県 (JP — prefecture), 도 (KR), 省 (ZH), Область (RU), İl (TR), ولاية (AR), מחוז (HE), จังหวัด (TH), Vajdaság (HU), Voivodato (PL) |
| ST-064 | State in postal address | Address component | Springfield, IL 62704; Berlin BY; Lyon, Auvergne-Rhône-Alpes |
| ST-065 | State in DL / passport context | Identity doc | "DL issued by: CA"; "Driver's License: Texas"; "Passport issued in: NY" |
| ST-066 | State as voter registration | Civic | "Voter ID: registered in Florida"; "Voted in Pennsylvania" |
| ST-067 | State in JSON | Structured | "state": "California", "state_code": "CA", "province": "Ontario" |
| ST-068 | State in KV | Form field | state=California, state_code=CA, province=Ontario, region=Île-de-France |
| ST-069 | State in XML | Markup | <state>California</state>, <state_code>CA</state_code>, <province>Ontario</province> |
| ST-070 | State in CSV | Tabular | "Smith","John","Springfield","IL","USA" |
| ST-071 | OCR-distorted state | Char substitution | Cal1fornla (1 for i), TeXas (X for x), Onta r io (extra space), Florlda (l for i) |
| ST-072 | OCR diacritic stripping | Lost accents | Munchen (was München — when used as state context Bayern is fine but...), Salzburg (no accent needed), Cordoba (was Córdoba), Quebec (lost é → Québec) |
| ST-073 | Masked / partial state | Privacy-redacted | State: ***, in *** state, ** (just 2-letter masked), [STATE_REDACTED] |
| ST-074 | State anonymized placeholder | Standard generic | State: [State], Sample state: CA, "State A" |
| ST-075 | State sentence-boundary | Trailing punctuation | "She lives in California.", "Are you in Texas?", "State: NY." |
| ST-076 | State adjacency-tight | No separator | "John Smith,Springfield,IL,USA"; "Sarah-California-32"; "CAResident" |
| ST-077 | Embedded in driver's license | Identity doc | "California Driver License #C1234567"; "Texas DL: 12345678" |
| ST-078 | Embedded in zip / postcode | Postal context | "ZIP 62704 (Springfield, IL)"; "PLZ 10117 (Berlin, BY... no wait, BE)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted (broad) | ✓ | ST-071, ST-072 |
| Masked / partial / redacted | ✓ | ST-073, ST-074 |
| Multilingual context labels | ✓ | ST-063 |
| Country-specific coverage | ✓ | ST-001 to ST-062 (30+ countries: US, CA, AU, DE, AT, CH, FR, IT, ES, PT, BR, MX, IN, CN, JP, KR, UK, RU, TR, PL, CZ, HU, NL, BE, SE, NO, DK, FI, ZA, AR, IL, SA, AE, IR, PK, ID, VN, TH, PH) |
| Script variations | ✓ | ST-029, ST-030, ST-032, ST-034, ST-040, ST-061 (JP, KR, ZH, RU, AR, HE, TH) |
| In structured data | ✓ | ST-067, ST-068, ST-069, ST-070 |
| Adjacency-tight | ✓ | ST-076 |
| Sentence-boundary tricky | ✓ | ST-075 |
| Domain-embedded (DL/passport/voter/postal) | ✓ | ST-065, ST-066, ST-077, ST-078 |
| Abbreviations (2-letter codes) | ✓ | ST-002, ST-006, ST-011, ST-022, ST-024, ST-028 |
| Territories / non-state divisions | ✓ | ST-003, ST-007, ST-009, ST-027, ST-030 |
| State + city combination | ✓ | ST-004, ST-064 |

**Total patterns for State: 78**

---

## Entity 26: Geolocation_Data

GPS coordinates, location data, geographic positioning. Machine-readable or human-readable form.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| GEO-001 | Decimal degrees (DD) — signed | Standard GPS | 40.7128, -74.0060; 51.5074, -0.1278; -33.8688, 151.2093 |
| GEO-002 | Decimal degrees with N/S/E/W | Compass-suffix | 40.7128° N, 74.0060° W; 51.5074° N, 0.1278° W |
| GEO-003 | Decimal degrees comma-separated | Lat,Lon | 40.7128,-74.0060; 35.6762,139.6503; -33.8688,151.2093 |
| GEO-004 | Decimal degrees space-separated | Lat Lon | 40.7128 -74.0060; 35.6762 139.6503 |
| GEO-005 | Decimal degrees with labels | "lat:", "lon:" | lat: 40.7128, lon: -74.0060; latitude=51.5074, longitude=-0.1278 |
| GEO-006 | Degrees Minutes Seconds (DMS) | Sexagesimal | 40°42′46″N 74°00′21″W; 51°30′26″N 0°07′40″W |
| GEO-007 | Degrees Minutes Seconds with quotes | Quote variant | 40°42'46"N 74°00'21"W; 51°30'26"N 0°07'40"W |
| GEO-008 | Degrees Decimal Minutes (DDM) | Hybrid format | 40°42.7667′N 74°0.36′W; 51°30.4444′N 0°7.6667′W |
| GEO-009 | DMS with all spaces | Aviation style | 40 42 46 N 074 00 21 W; 51 30 26 N 000 07 40 W |
| GEO-010 | UTM coordinates | Universal Transverse Mercator | 18T 583960 4507523; 30U 699319 5710092 |
| GEO-011 | UTM with hemisphere | Full UTM | UTM 18N 583960 4507523; UTM Zone 30U 699319mE 5710092mN |
| GEO-012 | MGRS (Military Grid Reference) | NATO grid | 18TWL83960 07523; 30UYC9931910092 |
| GEO-013 | Plus Codes (Open Location Code) | Google plus codes | 87G7PXJW+RM (NYC); 9C3XGV4M+4F (London) |
| GEO-014 | Plus Codes short form | With reference area | PXJW+RM, New York; GV4M+4F, London |
| GEO-015 | What3Words | 3-word location | ///filled.count.soap (NYC); ///example.start.here |
| GEO-016 | Geohash | Base-32 encoded | dr5regw3pg6; gcpvj0duvb (London) |
| GEO-017 | Geo URI scheme | RFC 5870 | geo:40.7128,-74.0060; geo:51.5074,-0.1278;u=10 |
| GEO-018 | Google Maps URL | Map link | maps.google.com/?q=40.7128,-74.0060; google.com/maps/@40.7128,-74.0060,15z |
| GEO-019 | Apple Maps URL | Map link | maps.apple.com/?ll=40.7128,-74.0060; maps.apple.com/?ll=51.5074,-0.1278 |
| GEO-020 | OpenStreetMap URL | OSM link | openstreetmap.org/?mlat=40.7128&mlon=-74.0060; osm.org/go/0EEQjE-- |
| GEO-021 | Bing Maps URL | Bing link | bing.com/maps?cp=40.7128~-74.0060; bing.com/maps?q=51.5074%2C-0.1278 |
| GEO-022 | Waze share | Waze deep link | waze.com/ul?ll=40.7128,-74.0060&navigate=yes |
| GEO-023 | EXIF GPS metadata | Photo embedded | GPSLatitude: 40°42'46"N, GPSLongitude: 74°0'21"W, GPSAltitude: 10m |
| GEO-024 | EXIF as decimal | Photo decimal | GPS: 40.712800,-74.006000 (from JPEG metadata) |
| GEO-025 | KML / KMZ coordinates | Google Earth format | <coordinates>-74.0060,40.7128,0</coordinates> (lon,lat,alt) |
| GEO-026 | GPX waypoint | GPS Exchange Format | <wpt lat="40.7128" lon="-74.0060"><name>NYC</name></wpt> |
| GEO-027 | GeoJSON Point | Spec-compliant JSON | {"type": "Point", "coordinates": [-74.0060, 40.7128]} |
| GEO-028 | GeoJSON Feature | With properties | {"type":"Feature","geometry":{"type":"Point","coordinates":[-74.006,40.7128]},"properties":{"name":"NYC"}} |
| GEO-029 | NMEA 0183 sentence | GPS chip output | $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47 |
| GEO-030 | Cell tower / CGI | Mobile tower position | MCC: 310, MNC: 410, LAC: 5678, CID: 1234 (US AT&T tower) |
| GEO-031 | WiFi BSSID + RSSI | WiFi positioning | BSSID: 00:14:22:01:23:45, SSID: "CafeNet", RSSI: -65 dBm |
| GEO-032 | Bluetooth beacon (iBeacon) | Indoor positioning | UUID: B9407F30-F5F8-466E-AFF9-25556B57FE6D, Major: 1, Minor: 42 |
| GEO-033 | IP-based geolocation | Estimated from IP | IP 192.0.2.42 → New York, NY, USA (approx 40.71, -74.01) |
| GEO-034 | Inferred from check-in | Social media check-in | "Checked in at Times Square, NYC", "🗽 @ Statue of Liberty, NY" |
| GEO-035 | Inferred from photo caption | Image context | "Sunset at Brighton Beach (51.4844° N, 0.1431° W)" |
| GEO-036 | Geofencing event | Fence trigger | "User entered geofence: home (40.7128, -74.0060, radius 100m)" |
| GEO-037 | Last known location | Tracking log | "Last seen at 40.7128, -74.0060 at 2024-03-15 14:30 UTC" |
| GEO-038 | "Approximately X" | Vague reference | approximately at 40.71° N, 74.01° W (low precision) |
| GEO-039 | Coordinate at sentence boundary | Trailing punctuation | "Meet me at 40.7128, -74.0060.", "Was the photo at 51.5074, -0.1278?" |
| GEO-040 | Coordinates adjacency-tight | No separator | "Photo:40.7128,-74.0060Time:14:30", "LOC40.7128-74.0060" |
| GEO-041 | Coordinates in JSON | Structured | "location": {"lat": 40.7128, "lon": -74.0060}, "coordinates": [-74.006, 40.7128] |
| GEO-042 | Coordinates in KV | Form field | latitude=40.7128, longitude=-74.0060, gps=40.7128,-74.0060 |
| GEO-043 | Coordinates in XML | Markup | <location lat="40.7128" lon="-74.0060"/>, <gps><lat>40.7128</lat></gps> |
| GEO-044 | Coordinates in CSV | Tabular | "Smith","John","40.7128","-74.0060","2024-03-15" |
| GEO-045 | OCR-distorted coordinates | Digit confusion | 4O.71Z8 (O for 0, Z for 2), -7A.OO60 (A for 4, O for 0); 4o.7l28,-74.OO6O |
| GEO-046 | OCR-distorted separators | Lost / wrong | "40.7128 -74.0060" (lost comma), "40,7128, -74,0060" (European comma decimal) |
| GEO-047 | European decimal (comma) | Continental | 40,7128, -74,0060 (DE/FR/ES use comma instead of period) |
| GEO-048 | Masked / partial coordinates | Privacy-redacted | 40.7128, -74.****; 4*.****, -7*.****; [GPS REDACTED] |
| GEO-049 | Anonymized placeholder | Standard generic | 0.0, 0.0 (null island); 51.5074, -0.1278 (London-default placeholder) |
| GEO-050 | Multilingual context label | "Location:" various | Location (EN), Localisation (FR), Standort (DE), Ubicación (ES), Posizione (IT), 位置 (JP), 위치 (KR), 位置 (ZH), Местоположение (RU), Konum (TR), موقع (AR), מיקום (HE), ตำแหน่ง (TH) |
| GEO-051 | Coordinates with altitude | 3D position | 40.7128, -74.0060, 10m (alt); lat,lon,alt; 40.7128 -74.0060 33ft |
| GEO-052 | Coordinates with time | Spatio-temporal | "(40.7128, -74.0060) at 2024-03-15T14:30:00Z" |
| GEO-053 | Coordinates with accuracy | Precision marker | 40.7128, -74.0060 ±5m; 40.7128, -74.0060 (HDOP: 1.2) |
| GEO-054 | Coordinate in legal pleading | Court / investigation | "The suspect's phone was located at 40.7128° N, 74.0060° W at 03:42 AM" |
| GEO-055 | Coordinate in medical context | Field clinical | "Mobile clinic GPS: 40.7128, -74.0060; serving uninsured patients" |
| GEO-056 | Coordinate in HR / device tracking | Employee monitoring | "Last device check-in: 40.7128, -74.0060 at 09:15"; "Fleet vehicle GPS log" |
| GEO-057 | Coordinate in social media metadata | Twitter / Instagram | "Tweeted from 40.7128, -74.0060"; "IG geotag: Brooklyn Bridge" |
| GEO-058 | Distance / direction from landmark | Relative | "200m NE of Times Square"; "3 miles south of downtown"; "50km west of Berlin" |
| GEO-059 | Coordinates in negative form | Anti-tracking | "DO NOT geotag", "geotag disabled", "no location shared" |
| GEO-060 | "Lat/Long" pair colloquially | Casual | "Send me your lat-long", "Drop a pin", "Share your live location" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | GEO-045, GEO-046 |
| Masked / partial / redacted | ✓ | GEO-048, GEO-049 |
| Multilingual context labels | ✓ | GEO-050 |
| Coordinate system coverage | ✓ | GEO-001 to GEO-016 (DD, DMS, DDM, UTM, MGRS, Plus Code, What3Words, Geohash) |
| Embedded in URL / scheme | ✓ | GEO-017 to GEO-022 (geo:, Google/Apple/OSM/Bing/Waze) |
| In structured data | ✓ | GEO-025 to GEO-028, GEO-041 to GEO-044 |
| Adjacency-tight | ✓ | GEO-040 |
| Sentence-boundary tricky | ✓ | GEO-039 |
| Domain-embedded (legal/medical/HR/social) | ✓ | GEO-054, GEO-055, GEO-056, GEO-057 |
| Device / network derived | ✓ | GEO-030 (cell), GEO-031 (WiFi), GEO-032 (BLE), GEO-033 (IP) |
| Metadata sources | ✓ | GEO-023, GEO-024 (EXIF), GEO-025 (KML), GEO-026 (GPX), GEO-029 (NMEA) |
| European decimal | ✓ | GEO-047 |
| Altitude / accuracy / time | ✓ | GEO-051, GEO-052, GEO-053 |
| Relative / inferred location | ✓ | GEO-034, GEO-035, GEO-038, GEO-058 |
| Privacy / anti-tracking | ✓ | GEO-059 |

**Total patterns for Geolocation_Data: 60**

---

## Entity 27: National_Identification_Number

Government-issued national ID numbers. Most countries have one or more national ID systems. Highly sensitive.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| NID-001 | US SSN (XXX-XX-XXXX) | Social Security Number | 123-45-6789, 987-65-4321 |
| NID-002 | US SSN no separators | Compact | 123456789, 987654321 |
| NID-003 | US SSN with "SSN:" label | Form context | SSN: 123-45-6789, S.S.N. 123-45-6789, Social Security Number: 123-45-6789 |
| NID-004 | US SSN last 4 only | Partial reference | "ending in 6789", "last 4: 6789", "SSN xxxx-xx-6789" |
| NID-005 | US ITIN (Individual Taxpayer) | Non-citizen taxpayer | 9XX-7X-XXXX (starts with 9, 4th digit 7 or 8); ITIN: 912-71-2345 |
| NID-006 | UK National Insurance Number (NINO) | UK NIN | AB123456C, AB 12 34 56 C; QQ123456A, JZ 12 34 56 D |
| NID-007 | UK NINO with label | Form context | NI Number: AB 12 34 56 C, NIN: AB123456C, National Insurance: AB123456C |
| NID-008 | German Steueridentifikationsnummer | DE Tax ID (11 digits) | 12 345 678 901, 12345678901 |
| NID-009 | German Steueridentifikationsnummer label | DE form | Steuer-ID: 12345678901, Steueridentifikationsnummer: 12 345 678 901 |
| NID-010 | German Sozialversicherungsnummer | DE social insurance | 12 345678 R 901; 12345678R901 |
| NID-011 | French NIR / INSEE / Sécu | FR social security | 1 85 03 75 116 001 23, 185037511600123 (gender 1/2 + YY + MM + département + commune + birth order + key) |
| NID-012 | French NIR label | FR form | NIR: 1 85 03 75 116 001 23, Numéro de Sécurité Sociale: 185037511600123 |
| NID-013 | Italian Codice Fiscale | IT 16-char alphanumeric | RSSMRA85M01H501Z, GRCMRA90A22H501P |
| NID-014 | Italian Codice Fiscale label | IT form | CF: RSSMRA85M01H501Z, Codice Fiscale: RSSMRA85M01H501Z |
| NID-015 | Spanish DNI | ES national ID | 12345678Z, 12345678-Z, 12.345.678-Z |
| NID-016 | Spanish NIE | ES foreigner ID | X1234567L, Y-1234567-L, Z 1234567 L |
| NID-017 | Spanish DNI / NIE label | ES form | DNI: 12345678Z, NIE: X1234567L, Documento: 12345678Z |
| NID-018 | Brazilian CPF | BR taxpayer ID | 123.456.789-09, 12345678909, 123 456 789 09 |
| NID-019 | Brazilian CPF label | BR form | CPF: 123.456.789-09, Cadastro de Pessoas Físicas: 12345678909 |
| NID-020 | Brazilian RG | BR state ID | 12.345.678-9, 12345678-9 (varies by state, SP format shown) |
| NID-021 | Japanese My Number | JP national ID (12 digits) | 1234 5678 9012, 123456789012 |
| NID-022 | Japanese My Number label | JP form | マイナンバー: 1234 5678 9012, My Number: 123456789012, 個人番号: 123456789012 |
| NID-023 | Korean RRN (Resident Registration #) | KR (YYMMDD-XXXXXXX) | 850315-1234567 |
| NID-024 | Korean RRN label | KR form | 주민등록번호: 850315-1234567, RRN: 850315-1234567 |
| NID-025 | Chinese ID (居民身份证号) | CN 18-digit | 110101198503151234, 110101 19850315 123 X (X = check digit can be X) |
| NID-026 | Chinese ID label | CN form | 身份证号: 110101198503151234, ID: 110101198503151234 |
| NID-027 | Indian Aadhaar | IN 12-digit | 1234 5678 9012, 123456789012 |
| NID-028 | Indian Aadhaar label | IN form | Aadhaar: 1234 5678 9012, UID: 123456789012, आधार: 1234 5678 9012 |
| NID-029 | Indian PAN | IN tax ID (10-char) | ABCDE1234F, ABCDE 1234 F |
| NID-030 | Indian PAN label | IN form | PAN: ABCDE1234F, Permanent Account Number: ABCDE1234F |
| NID-031 | Mexican CURP | MX 18-char | RAGM850315HDFMRR09 (gender H/M + birth state code + 2 consonants) |
| NID-032 | Mexican CURP label | MX form | CURP: RAGM850315HDFMRR09, Clave Única: RAGM850315HDFMRR09 |
| NID-033 | Mexican RFC | MX tax ID (13-char) | RAGM850315H08, GARH900722MAB |
| NID-034 | Mexican RFC label | MX form | RFC: RAGM850315H08, Registro Federal de Contribuyentes |
| NID-035 | Canadian SIN | CA 9-digit | 123-456-789, 123 456 789, 123456789 |
| NID-036 | Canadian SIN label | CA form | SIN: 123-456-789, Numéro d'assurance sociale (FR): 123 456 789 |
| NID-037 | Canadian SIN temp resident | Starts with 9 | 9XX-XXX-XXX (temp worker SIN) |
| NID-038 | Australian TFN | AU tax file (8-9 digits) | 123 456 782, 12345678 |
| NID-039 | Australian Medicare | AU healthcare | 1234 56789 1, 12345678910 |
| NID-040 | Australian DL number | AU state-specific | NSW: 1234 5678; VIC: 123456789; QLD: 12345678 |
| NID-041 | South African ID | ZA 13-digit | 850315 1234 089; YYMMDD-XXXX-CCC (gender 0-4 F, 5-9 M; citizenship; checksum) |
| NID-042 | Polish PESEL | PL 11-digit (YYMMDD + 5) | 85031512345; 8503151234 5 |
| NID-043 | Polish PESEL label | PL form | PESEL: 85031512345, Numer PESEL: 85031512345 |
| NID-044 | Czech rodné číslo | CZ 9-10 digit | 850315/1234, 8503151234 |
| NID-045 | Swedish personnummer | SE 12-digit | 19850315-1234, 850315-1234 |
| NID-046 | Swedish personnummer label | SE form | Personnummer: 19850315-1234, P-nr: 850315-1234 |
| NID-047 | Swedish samordningsnummer | SE temp ID (+60 days) | 850375-1234 (DD+60), for non-residents |
| NID-048 | Finnish henkilötunnus | FI 11-char | 150385-1230, 150385+1230 (1800s sign), 150385A1230 (2000s sign A) |
| NID-049 | Finnish henkilötunnus label | FI form | Henkilötunnus: 150385-1230, HETU: 150385-1230 |
| NID-050 | Norwegian fødselsnummer | NO 11-digit | 15038512345 |
| NID-051 | Norwegian fødselsnummer label | NO form | Fødselsnummer: 15038512345, F.nr: 15038512345 |
| NID-052 | Norwegian D-nummer | NO temp ID | First digit +4 (e.g., 55038512345 instead of 15...) |
| NID-053 | Danish CPR | DK 10-digit | 150385-1234, 1503851234 |
| NID-054 | Danish CPR label | DK form | CPR-nummer: 150385-1234, CPR: 1503851234 |
| NID-055 | Belgian Rijksregister | BE 11-digit | 85.03.15-123.45 |
| NID-056 | Dutch BSN | NL 9-digit | 123 456 789, 123456789, BSN: 123456789 |
| NID-057 | Israeli Teudat Zehut | IL 9-digit | 123456782, 123-456-782, ת.ז.: 123456782 |
| NID-058 | Turkish TC Kimlik | TR 11-digit | 12345678901, T.C. Kimlik No: 12345678901 |
| NID-059 | Hungarian személyi szám | HU 11-digit | 1 850315 1234, 18503151234 |
| NID-060 | Singapore NRIC | SG (S/T/F/G/M letter + 7 digits + check) | S1234567A, T1234567B, F1234567C, NRIC: S1234567A |
| NID-061 | Singapore FIN | SG foreign ID | G1234567H, M1234567J (M added 2021), FIN: G1234567H |
| NID-062 | Hong Kong HKID | HK letter(s) + digits | A123456(7), AB123456(7) |
| NID-063 | Taiwan National ID | TW letter + 9 digits | A123456789 (A=Taipei; 1=male, 2=female) |
| NID-064 | Argentine DNI | AR 7-8 digit | 12.345.678, DNI: 12345678 |
| NID-065 | Chilean RUT/RUN | CL X.XXX.XXX-K | 12.345.678-9, 12345678-9, RUT: 12345678-9 |
| NID-066 | Peruvian DNI | PE 8-digit | 12345678, DNI: 12345678 |
| NID-067 | Colombian Cédula | CO 8-10 digit | 1.234.567.890, 1234567890, Cédula: 1234567890 |
| NID-068 | Venezuelan Cédula | VE V- prefix | V-12345678, E-12345678 (foreigner), V12.345.678 |
| NID-069 | Russian СНИЛС (SNILS) | RU social insurance | 123-456-789 00, 123-456-789-00 |
| NID-070 | Russian INN (Tax #) | RU 12-digit (individual) | 123456789012, ИНН: 123456789012 |
| NID-071 | Russian internal passport | RU "passport" used as ID | Серия: 1234, Номер: 567890; Passport: 1234 567890 |
| NID-072 | Iranian National ID | IR 10-digit | 0012345678, کد ملی: 0012345678 |
| NID-073 | Pakistani CNIC | PK 13-digit | 12345-1234567-1, CNIC: 12345-1234567-1 |
| NID-074 | Bangladesh National ID | BD 10/13/17-digit | 1234567890; 1985012345678; BD NID: 1234567890 |
| NID-075 | Saudi National ID | SA 10-digit | 1234567890, الرقم الوطني: 1234567890 |
| NID-076 | UAE Emirates ID | AE 15-digit | 784-1985-1234567-8, Emirates ID: 784198512345678 |
| NID-077 | Egyptian National ID | EG 14-digit | 28503151234567, الرقم القومي: 28503151234567 |
| NID-078 | Iraqi National ID | IQ varies | 199012345678 |
| NID-079 | Bulgarian EGN | BG 10-digit | 8503151234 (months +40 for Jul-Dec 2000+, +20 1800s) |
| NID-080 | Romanian CNP | RO 13-digit | 1850315123456 (1/2 = M/F 1900-1999, 5/6 = M/F 2000+) |
| NID-081 | Estonian Isikukood | EE 11-digit | 38503151234 (3 = M 1900-1999, 5 = M 2000+) |
| NID-082 | Latvian Personas kods | LV 11-digit | 150385-12345 |
| NID-083 | Lithuanian Asmens kodas | LT 11-digit | 38503151234 |
| NID-084 | Slovenian EMŠO | SI 13-digit | 1503985500001 |
| NID-085 | Croatian OIB | HR 11-digit | 12345678901 |
| NID-086 | Serbian JMBG | RS 13-digit | 1503985500001 |
| NID-087 | National ID in JSON | Structured | "ssn": "123-45-6789", "national_id": "RSSMRA85M01H501Z", "aadhaar": "1234 5678 9012" |
| NID-088 | National ID in KV | Form field | ssn=123-45-6789, SSN: 123-45-6789, CPF: 123.456.789-09 |
| NID-089 | National ID in XML | Markup | <ssn>123-45-6789</ssn>, <national_id country="IT">RSSMRA85M01H501Z</national_id> |
| NID-090 | National ID in CSV | Tabular | "Smith","John","123-45-6789","SSN","US" |
| NID-091 | Adjacency-tight with name | No separator | "John Smith123-45-6789", "Sarah Chen,A123456789,Engineer" |
| NID-092 | Sentence-boundary tricky | Trailing punctuation | "His SSN is 123-45-6789.", "Was the Aadhaar 1234 5678 9012?", "PAN: ABCDE1234F!" |
| NID-093 | OCR-distorted national ID | Char substitution | l23-45-6789 (l for 1), I23-45-6789 (I for 1); O00-12-3456 (O for 0); 5SN 123-45-6789 (5 for S) |
| NID-094 | OCR-distorted separators | Lost / wrong | 123 45 6789 (lost dashes), 123/45/6789 (wrong separator) |
| NID-095 | Masked / partial national ID | Privacy-redacted | XXX-XX-6789, ***-**-6789, SSN ending in 6789, [REDACTED]-**-XXXX |
| NID-096 | Anonymized placeholder | Standard generic | 000-00-0000 (US placeholder), 111-11-1111, [NATIONAL ID], <SSN> |
| NID-097 | Multilingual context label | Various languages | National ID (EN), Numéro national (FR), Personalausweisnummer (DE), DNI (ES), Codice (IT), 国民番号 (JP), 주민번호 (KR), 身份证号 (ZH), Идентификационный номер (RU), Kimlik No (TR), رقم الهوية (AR), מספר זהות (HE) |
| NID-098 | National ID with biometric reference | Linked | "Aadhaar 1234 5678 9012 (biometrically verified)"; "SSN linked to fingerprint on file" |
| NID-099 | National ID with status | Validity | "SSN active", "Aadhaar suspended", "CPF irregular", "PAN active" |
| NID-100 | Multiple IDs in one record | List | "SSN: 123-45-6789; ITIN: 912-71-2345"; "PAN: ABCDE1234F, Aadhaar: 1234 5678 9012" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | NID-093, NID-094 |
| Masked / partial / redacted | ✓ | NID-004, NID-095, NID-096 |
| Multilingual context labels | ✓ | NID-097 |
| Country-specific coverage | ✓ | NID-001 to NID-086 (40+ country systems) |
| Format variants per country | ✓ | NID-001 to NID-004 (US SSN: full, no sep, label, partial) |
| In structured data | ✓ | NID-087, NID-088, NID-089, NID-090 |
| Adjacency-tight | ✓ | NID-091 |
| Sentence-boundary tricky | ✓ | NID-092 |
| Script variations in labels | ✓ | NID-022, NID-024, NID-026, NID-028 (JP, KR, ZH, Devanagari), NID-072, NID-075, NID-077 (Persian, Arabic) |
| Cross-linked / multi-ID | ✓ | NID-098, NID-100 |
| Status / validity context | ✓ | NID-099 |

**Total patterns for National_Identification_Number: 100**

---

## Entity 28: Passport_Number

International travel document number. Country-specific formats.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PA-001 | US passport (9 digits) | Standard book | 123456789, 987654321 |
| PA-002 | US passport with letter | Newer issuance | A12345678, B12345678 |
| PA-003 | US passport card | Wallet card (US/CA/MX/Bermuda only) | C12345678 (card prefix; alphanumeric) |
| PA-004 | US passport label | Form context | Passport No.: 123456789, US Passport: 123456789 |
| PA-005 | UK passport (9 digits) | Standard | 123456789, 987654321 |
| PA-006 | UK passport label | Form context | Passport No.: 123456789, UK Passport: 123456789 |
| PA-007 | German passport | 1-2 letters + 7 digits + check | C1AB23456, CFRPK0X53; old: A12345678 |
| PA-008 | French passport | 2 digits + 2 letters + 5 digits | 12AB12345, 09FH67890 |
| PA-009 | Italian passport | 2 letters + 7 digits | YA1234567, AB1234567 |
| PA-010 | Spanish passport | 3 letters + 6 digits | AAA123456 |
| PA-011 | Brazilian passport | 2 letters + 6 digits | FA123456, AB987654 |
| PA-012 | Mexican passport | 8-9 digits | 12345678, G12345678 |
| PA-013 | Japanese passport | 2 letters + 7 digits | TK1234567, MA7654321 |
| PA-014 | Korean passport | 1 letter + 8 digits | M12345678, S87654321 |
| PA-015 | Chinese passport (P/G prefix) | E for biometric, G for old | E12345678, G12345678 (older), EH1234567 |
| PA-016 | Indian passport | 1 letter + 7 digits | A1234567, B2345678, M3456789 |
| PA-017 | Canadian passport | 2 letters + 6 digits | AB123456, GA987654 |
| PA-018 | Australian passport | 8 digits + letter; 1 letter + 7 digits | M1234567, A1234567 |
| PA-019 | Russian passport — international | 9 digits | 123456789 |
| PA-020 | Russian passport — internal | Series + number | Серия 12 34, Номер 567890 (series + 6-digit number) |
| PA-021 | Polish passport | 2 letters + 7 digits | AB1234567 |
| PA-022 | Dutch passport | 1 letter + 8 alphanumeric | NV9876543 |
| PA-023 | Swedish passport | 8 digits | 12345678, 87654321 |
| PA-024 | Finnish passport | 2 letters + 7 digits | XP1234567 |
| PA-025 | Norwegian passport | 8 digits | 12345678 |
| PA-026 | Danish passport | 9 digits | 200912345 |
| PA-027 | Belgian passport | 2 letters + 6 digits | EH123456 |
| PA-028 | Swiss passport | 1 letter + 7 digits | X1234567 |
| PA-029 | Austrian passport | 1 letter + 7 digits | U1234567 |
| PA-030 | Greek passport | 2 letters + 7 digits | AB1234567 |
| PA-031 | Portuguese passport | 1 letter + 6 digits | C123456 |
| PA-032 | Czech passport | 8 alphanumeric | 12345678, AB123456 |
| PA-033 | Hungarian passport | 2 letters + 6 digits | XY123456 |
| PA-034 | Turkish passport | 1 letter + 7 digits | U12345678 |
| PA-035 | Israeli passport | 8-9 digits | 12345678, 123456789 |
| PA-036 | Saudi Arabian passport | 1 letter + 8 digits or 9 digits | A12345678, 123456789 |
| PA-037 | UAE passport | 8-9 digits | 12345678 |
| PA-038 | Egyptian passport | 9 digits | 123456789 |
| PA-039 | Iranian passport | 1 letter + 7-8 digits | A12345678 |
| PA-040 | Pakistani passport | 2 letters + 7 digits | AB1234567 |
| PA-041 | Singapore passport | 1 letter + 7 digits + check | K1234567A, E7654321B |
| PA-042 | Malaysian passport | 1 letter + 8 digits | A12345678 |
| PA-043 | Thai passport | 1 letter + 7 digits | A1234567 |
| PA-044 | Vietnamese passport | 1 letter + 7 digits | B1234567 |
| PA-045 | Indonesian passport | 1 letter + 7 digits | A1234567 |
| PA-046 | Filipino passport | 9 alphanumeric | EC1234567, P0123456A |
| PA-047 | Argentine passport | 8 digits | 12345678, AA123456 (older) |
| PA-048 | South African passport | 8-9 alphanumeric | M12345678 |
| PA-049 | Diplomatic passport | Special category | Diplomatic Passport: D1234567 (DE), DI-12345 (FR) |
| PA-050 | Service / Official passport | Government work | Service Passport: S1234567, Official Passport: O12345678 |
| PA-051 | Emergency / Temporary passport | Provisional | Emergency Passport: T12345678 (US emergency), Temporary Travel Document |
| PA-052 | Refugee Travel Document | Travel doc | RTD No.: 12345678, Refugee Travel Document |
| PA-053 | Passport in MRZ format | Machine-readable zone | P<USAJSMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n123456789USA8503151M2503159<<<<<<<<<<<<<<04 |
| PA-054 | Passport expiry date | Plus expiration | Passport 123456789 (expires 2030-03-15); Exp: 03/15/2030 |
| PA-055 | Passport issuance date | Plus issue | Issued: 2020-03-15; Date of Issue: 03/15/2020 |
| PA-056 | Passport issuance place | Plus place | Issued at: New York Passport Agency; Place of Issue: Washington DC |
| PA-057 | Passport with full holder | Combined | "John Smith, US Passport 123456789, exp 2030-03-15" |
| PA-058 | E-passport indicator | Biometric chip | "e-Passport with chip", "E-Passport: 123456789", electronic passport |
| PA-059 | Passport in JSON | Structured | "passport_no": "123456789", "passport_country": "US", "passport_expiry": "2030-03-15" |
| PA-060 | Passport in KV | Form field | passport=123456789, PASSPORT NO: 123456789 |
| PA-061 | Passport in XML | Markup | <passport>123456789</passport>, <passportNo country="US">123456789</passportNo> |
| PA-062 | Passport in CSV | Tabular | "Smith","John","123456789","US","2030-03-15" |
| PA-063 | Multilingual context label | "Passport:" various | Passport (EN), Passeport (FR), Reisepass (DE), Pasaporte (ES), Passaporto (IT), Passaporte (PT), パスポート (JP), 여권 (KR), 护照 (ZH), Паспорт (RU), Pasaport (TR), جواز سفر (AR), דרכון (HE), หนังสือเดินทาง (TH) |
| PA-064 | OCR-distorted passport | Char substitution | l23456789 (l for 1), AB12345678 → A813245678; A1Z34567 (Z for 2) |
| PA-065 | OCR-distorted MRZ | MRZ confusion | "<<<<<<<<<<JOHNN<<<SMITH" (lost separators), "P<USA" → "P<U5A" |
| PA-066 | Masked / partial passport | Privacy-redacted | Passport ****6789 (last 4), 123*****89 (middle hidden), Passport: [REDACTED] |
| PA-067 | Anonymized placeholder | Standard generic | Passport: 000000000, <PASSPORT>, [PASSPORT] |
| PA-068 | Sentence-boundary tricky | Trailing punctuation | "Her passport is 123456789.", "Was the number A12345678?", "Passport expired!" |
| PA-069 | Adjacency-tight | No separator | "John Smith123456789Passport US", "MariaGarcíaPassportA12345678" |
| PA-070 | Passport in travel itinerary | Booking context | "PAX: SMITH/JOHN MR; Passport: 123456789; Nationality: USA" |
| PA-071 | Passport in visa application | Government form | "Passport No.: 123456789; Issuing country: USA; Expiry: 03/15/2030" |
| PA-072 | Passport in airline boarding | Flight context | "Passport: ****6789 (last 4)", "Travel doc: A12345678" |
| PA-073 | Passport in hotel check-in | Hospitality | "Photocopy of passport retained; passport no: 123456789" |
| PA-074 | Passport in border control log | Immigration | "Passport scan: 123456789, USA, entered 03/15/2024 at JFK" |
| PA-075 | Passport in customs declaration | Forms | "Customs Form, Passport: 123456789, declared $5,000" |
| PA-076 | Old passport book | Pre-biometric | "Old passport book (no chip): A12345678, expired 2010" |
| PA-077 | Renewed passport | Plus history | "Current passport: 123456789 (renewal of A12345678)" |
| PA-078 | Lost / Stolen passport report | Negative status | "Reported lost: passport 123456789 (USA) on 2024-03-15" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | PA-064, PA-065 |
| Masked / partial / redacted | ✓ | PA-066, PA-067 |
| Multilingual context labels | ✓ | PA-063 |
| Country-specific coverage | ✓ | PA-001 to PA-052 (47+ countries plus diplomatic/service/emergency/refugee) |
| In structured data | ✓ | PA-053 (MRZ), PA-059, PA-060, PA-061, PA-062 |
| Adjacency-tight | ✓ | PA-069 |
| Sentence-boundary tricky | ✓ | PA-068 |
| Domain-embedded (travel/visa/hotel/border) | ✓ | PA-070 to PA-075 |
| Special variants (diplomatic/service/emergency/RTD) | ✓ | PA-049, PA-050, PA-051, PA-052 |
| Metadata (expiry/issue/place) | ✓ | PA-054, PA-055, PA-056 |
| Status (e-passport/lost/renewed/old) | ✓ | PA-058, PA-076, PA-077, PA-078 |

**Total patterns for Passport_Number: 78**

---

## Entity 29: Driving_License_Number

Driver / driving license number. Country and state-specific formats.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| DL-001 | US — California DL | CA format: 1 letter + 7 digits | A1234567 |
| DL-002 | US — New York DL | NY: 9 digits | 123 456 789, 123456789 |
| DL-003 | US — Texas DL | TX: 8 digits | 12345678 |
| DL-004 | US — Florida DL | FL: 1 letter + 12 digits | A123-456-78-901-0 |
| DL-005 | US — Illinois DL | IL: 1 letter + 11 digits | A123-4567-8901 |
| DL-006 | US — Pennsylvania DL | PA: 8 digits | 12 345 678 |
| DL-007 | US — Ohio DL | OH: 2 letters + 6 digits | AB123456 |
| DL-008 | US — Georgia DL | GA: 9 digits | 123456789 |
| DL-009 | US — Massachusetts DL | MA: S + 8 digits or 9 digits | S12345678 |
| DL-010 | US — Michigan DL | MI: 1 letter + 12 digits | A123-456-789-012 |
| DL-011 | US — New Jersey DL | NJ: 1 letter + 14 alphanumeric | A1234-56789-01234 |
| DL-012 | US — Virginia DL | VA: 1 letter + 8 digits | A12345678 |
| DL-013 | US — Washington DL | WA: WDLABCD123XY | WDLSAMPL123A4 |
| DL-014 | US — Arizona DL | AZ: 1 letter + 8 digits or 9 digits | A12345678 |
| DL-015 | US — Generic state DL | "DL#" + ID | State of [X], DL: 12345678, Driver's License #: A1234567 |
| DL-016 | US — REAL ID indicator | Federal compliant | REAL ID compliant DL: A1234567 (star indicator) |
| DL-017 | US — CDL (Commercial DL) | Class A/B/C | CDL Class A: 12345678; CDL endorsement: H (Hazmat) |
| DL-018 | US — Learner's permit | Provisional | Learner's Permit: P1234567 (varies by state) |
| DL-019 | UK DVLA license | DVLA: 5 letters + 6 digits + 5 alphanumeric | SMITH912155SM9DC; PRESLEY902095J99FG |
| DL-020 | UK DVLA license label | UK form | Driver Number: SMITH912155SM9DC; DVLA Licence: SMITH912155SM9DC |
| DL-021 | German Führerschein | DE: alphanumeric varies | F1234567890, K1234567890 (Kartenführerschein) |
| DL-022 | German Führerschein label | DE form | Führerscheinnummer: F1234567890, FS-Nr.: F1234567890 |
| DL-023 | French Permis de conduire | FR: 12 digits | 123456789012 |
| DL-024 | French Permis label | FR form | Numéro de permis: 123456789012, Permis de conduire: 12 34 56 78 90 12 |
| DL-025 | Italian Patente | IT: alphanumeric | U1A123456V, AB123456C |
| DL-026 | Italian Patente label | IT form | Numero patente: U1A123456V, Patente: AB123456C |
| DL-027 | Spanish Permiso de Conducir | ES: same as DNI + class | DNI 12345678Z, Class B |
| DL-028 | Brazilian CNH | BR: 11 digits | 12345678901 |
| DL-029 | Brazilian CNH label | BR form | CNH: 12345678901, Carteira Nacional de Habilitação |
| DL-030 | Japanese 運転免許証 | JP: 12-digit | 1234 5678 9012, 公安委員会発行 |
| DL-031 | Japanese license label | JP form | 運転免許番号: 1234 5678 9012, Driver's License: 1234 5678 9012 |
| DL-032 | Korean DL | KR: 12 digits + region | 12-34-567890-12 |
| DL-033 | Chinese DL | CN: 18-digit (matches ID) | 110101198503151234 (same as national ID for newer licenses) |
| DL-034 | Indian DL (state-specific) | IN: 13-16 chars | MH-0120150012345 (Maharashtra format); DL-1320110012345 |
| DL-035 | Indian DL label | IN form | Driving Licence No.: MH-0120150012345 |
| DL-036 | Australian DL — NSW | NSW: 8-digit | 12345678 |
| DL-037 | Australian DL — VIC | VIC: 9-digit | 123456789 |
| DL-038 | Australian DL — QLD | QLD: 8-digit | 123-456-789 |
| DL-039 | Canadian DL — Ontario | ON: 5 chars + 10 digits | S1234-12345-12345 |
| DL-040 | Canadian DL — Quebec | QC: 13 digits | S123456789012 (S = SAAQ) |
| DL-041 | Canadian DL — BC | BC: 7 digits | 1234567 |
| DL-042 | International Driving Permit | IDP | IDP No.: 1234567 (US AAA-issued), valid 1 year |
| DL-043 | Mexican Licencia | MX: state varies | DF12345678901, CdMx: 12345678901 |
| DL-044 | Russian Водительское удостоверение | RU: 10 digits | 1234 567890 |
| DL-045 | Turkish Sürücü Belgesi | TR: alphanumeric | 12-34-56-78 |
| DL-046 | Polish Prawo jazdy | PL: 10 alphanumeric | 12345/67/8901 |
| DL-047 | Dutch Rijbewijs | NL: 10 digits | 1234567890 |
| DL-048 | Swedish Körkort | SE: 12 digits (matches personnummer) | 19850315-1234 |
| DL-049 | Norwegian Førerkort | NO: 14 chars | 12345678901234 |
| DL-050 | Danish Kørekort | DK: 8 digits | 12345678 |
| DL-051 | Finnish Ajokortti | FI: 11-char (matches HETU) | 150385-1230 |
| DL-052 | Israeli DL | IL: 9 digits | 12345678 |
| DL-053 | DL class / category | License class | Class B (cars), Class C (motorcycles), Class A (CDL), HGV (UK heavy goods) |
| DL-054 | DL endorsement | Special permissions | Endorsements: Motorcycle, Hazmat (H), School Bus (P), Passenger (P) |
| DL-055 | DL restriction code | Limits | Restrictions: corrective lenses (B), automatic transmission (78) |
| DL-056 | DL expiration | Plus expiry | DL: A1234567, exp: 2030-03-15 |
| DL-057 | DL issuance date | Plus issued | DL: A1234567, issued: 2020-03-15 |
| DL-058 | DL with full holder | Combined | "John Smith, CA DL A1234567, exp 03/15/2030" |
| DL-059 | DL in JSON | Structured | "drivers_license": "A1234567", "dl_state": "CA", "dl_expiry": "2030-03-15" |
| DL-060 | DL in KV | Form field | drivers_license=A1234567, DL: A1234567, DRIVER LIC: 12345678 |
| DL-061 | DL in XML | Markup | <drivers_license>A1234567</drivers_license>, <dl state="CA">A1234567</dl> |
| DL-062 | DL in CSV | Tabular | "Smith","John","A1234567","CA","2030-03-15" |
| DL-063 | DL on traffic ticket | Citation context | "Citation issued to: John Smith, DL: A1234567 (CA), violation: speeding" |
| DL-064 | DL on insurance form | Insurance application | "Policy holder DL: A1234567 (CA), years of driving: 15" |
| DL-065 | DL on rental car form | Rental context | "Renter DL: A1234567 (CA), exp 2030-03-15, additional driver: B7654321" |
| DL-066 | DL on accident report | Police report | "Driver 1: John Smith, DL A1234567 (CA); Driver 2: Maria García, DL 12345678 (TX)" |
| DL-067 | Suspended / Revoked DL | Status | "DL status: SUSPENDED until 2025-06-15"; "DL revoked due to DUI" |
| DL-068 | Provisional DL | Probation | "Provisional DL (under 18): P1234567" |
| DL-069 | Multilingual context label | "Driver's License:" | DL (EN), Permis de conduire (FR), Führerschein (DE), Permiso (ES), Patente (IT), CNH (PT-BR), 運転免許 (JP), 운전면허 (KR), 驾照 (ZH), Водительское удостоверение (RU), Ehliyet (TR), رخصة قيادة (AR), רישיון נהיגה (HE) |
| DL-070 | OCR-distorted DL | Char substitution | A1Z34567 (Z for 2), Al234567 (l for 1); B7B54321 (B for 8); 0OABC (O for 0) |
| DL-071 | Masked / partial DL | Privacy-redacted | DL: A***4567, License ending in 4567, DL: [REDACTED] |
| DL-072 | Anonymized placeholder | Standard generic | DL: 00000000, <DL>, [LICENSE], DLN: <REDACTED> |
| DL-073 | Sentence-boundary tricky | Trailing punctuation | "His DL is A1234567.", "Was the license A1234567?", "DL expired!" |
| DL-074 | Adjacency-tight | No separator | "John SmithA1234567CA", "MariaGarcía12345678TX" |
| DL-075 | DL in traffic stop dialog | Verbal context | "Officer: License please. Driver: Here's my DL, A1234567" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | DL-070 |
| Masked / partial / redacted | ✓ | DL-071, DL-072 |
| Multilingual context labels | ✓ | DL-069 |
| Country / state coverage | ✓ | DL-001 to DL-052 (US 14 states + UK + 25+ countries) |
| In structured data | ✓ | DL-059, DL-060, DL-061, DL-062 |
| Adjacency-tight | ✓ | DL-074 |
| Sentence-boundary tricky | ✓ | DL-073 |
| Domain-embedded (traffic/insurance/rental/accident) | ✓ | DL-063, DL-064, DL-065, DL-066 |
| License attributes (class/endorsement/restriction) | ✓ | DL-053, DL-054, DL-055 |
| Status (expired/suspended/provisional) | ✓ | DL-056, DL-067, DL-068 |
| CDL / special licenses | ✓ | DL-017, DL-042 |

**Total patterns for Driving_License_Number: 75**

---

## Entity 30: Tax_Reference_Number

Tax identification numbers for individuals and businesses. Country-specific.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| TX-001 | US SSN (used as TIN for individuals) | Tax via SSN | 123-45-6789 (used as TIN for US individuals) |
| TX-002 | US ITIN (Individual Taxpayer ID) | Non-citizen | 9XX-7X-XXXX, ITIN: 912-71-2345 |
| TX-003 | US EIN (Employer ID Number) | Business | 12-3456789, EIN: 12-3456789, Tax ID: 123456789 |
| TX-004 | US EIN with label | Business context | EIN: 12-3456789, Employer Identification Number, FEIN: 12-3456789 |
| TX-005 | US PTIN (Preparer Tax ID) | Tax preparer | PTIN: P12345678 |
| TX-006 | US ATIN (Adoption Taxpayer ID) | Adopted child | ATIN: 9XX-93-XXXX |
| TX-007 | UK UTR (Unique Taxpayer Reference) | UK personal | 1234567890 (10 digits), UTR: 1234567890 |
| TX-008 | UK UTR label | UK form | UTR: 1234567890, Unique Taxpayer Reference: 1234567890 |
| TX-009 | UK VAT number | UK business | GB 123 4567 89, GB123456789, VAT GB 123 4567 89 |
| TX-010 | UK Corporation Tax UTR | UK company | 1234567890 (10 digits, format like personal) |
| TX-011 | German Steuernummer | DE personal/business | 12/345/67890 (Bavaria format), 1234567890 |
| TX-012 | German USt-IdNr | DE VAT | DE 123456789, DE123456789, USt-IdNr: DE123456789 |
| TX-013 | German Wirtschafts-Identifikationsnummer | DE business | DE 1234567890 (W-IdNr) |
| TX-014 | French SIRET | FR business | 12345678901234 (14 digits, includes SIREN + NIC) |
| TX-015 | French SIREN | FR business legal | 123456789 (9 digits, identifies legal entity) |
| TX-016 | French TVA intracommunautaire | FR VAT | FR12345678901, FR 12 345 678 901 |
| TX-017 | French Numéro fiscal | FR personal | 13 chiffres: 1234567890123 |
| TX-018 | Italian Codice Fiscale (personal TIN) | IT personal | RSSMRA85M01H501Z (also serves as TIN) |
| TX-019 | Italian Partita IVA | IT VAT / business | 12345678901 (11 digits), P.IVA 12345678901 |
| TX-020 | Spanish NIF (Número Identificación Fiscal) | ES personal/business | DNI 12345678Z (used as NIF), NIE Y1234567-L |
| TX-021 | Spanish CIF (Código Identificación Fiscal) | ES company | A12345678 (letter + 8 digits; replaced by NIF in 2008 but still used) |
| TX-022 | Spanish IVA | ES VAT | ES A12345678, ES 12345678Z |
| TX-023 | Brazilian CPF (personal tax) | BR personal | 123.456.789-09 |
| TX-024 | Brazilian CNPJ (business tax) | BR business | 12.345.678/0001-90, 12345678000190 |
| TX-025 | Brazilian CNPJ label | BR form | CNPJ: 12.345.678/0001-90, Cadastro Nacional da Pessoa Jurídica |
| TX-026 | Indian PAN (Permanent Account Number) | IN personal/business | ABCDE1234F (5 letters + 4 digits + 1 letter) |
| TX-027 | Indian GSTIN | IN GST tax | 27AAACT0123A1Z5 (15-char alphanumeric: state code + PAN + entity + Z + check) |
| TX-028 | Indian TAN | IN tax deductor | DELT12345A (4 letters + 5 digits + 1 letter) |
| TX-029 | Indian TIN (state) | IN sales tax (legacy) | 27123456789 (11-digit, state code + ID) |
| TX-030 | Mexican RFC (personal) | MX personal | RAGM850315H08 (13-char with DOB and homonym) |
| TX-031 | Mexican RFC (business) | MX business | MEX012345AB1 (12-char for company) |
| TX-032 | Mexican CURP (personal ID, used as TIN context) | MX personal | RAGM850315HDFMRR09 |
| TX-033 | Canadian SIN (used as TIN for individuals) | CA personal | 123-456-789 (used as TIN for individuals) |
| TX-034 | Canadian BN (Business Number) | CA business | 123456789 RT0001 (9 digits + program account) |
| TX-035 | Canadian GST/HST | CA tax | 123456789 RT 0001 |
| TX-036 | Australian TFN (Tax File Number) | AU personal/business | 123 456 782, 12 345 678 |
| TX-037 | Australian ABN (Business Number) | AU business | 53 004 085 616, ABN 53 004 085 616 |
| TX-038 | Australian GST | AU | GST registration ABN-linked |
| TX-039 | Japanese 法人番号 (Corporate Number) | JP business | 1234567890123 (13 digits) |
| TX-040 | Japanese マイナンバー (used for tax) | JP personal | 1234 5678 9012 (used for tax purposes too) |
| TX-041 | Korean 사업자등록번호 (Business Registration) | KR business | 123-45-67890 (10 digits, 3-2-5 format) |
| TX-042 | Korean RRN (used for personal tax) | KR personal | 850315-1234567 |
| TX-043 | Chinese 纳税人识别号 | CN business/personal | 91110108MA01ABCD1X (18-char Unified Social Credit Identifier for business) |
| TX-044 | Chinese 个人所得税号 | CN personal tax | uses 18-digit national ID for individuals |
| TX-045 | Russian INN (personal) | RU personal | 123456789012 (12 digits) |
| TX-046 | Russian INN (business) | RU business | 1234567890 (10 digits for legal entities) |
| TX-047 | Russian OGRN | RU business registration | 1234567890123 (13 digits) |
| TX-048 | Russian OGRNIP | RU sole proprietor | 123456789012345 (15 digits) |
| TX-049 | Russian KPP | RU tax reason code | 123456789 (9 digits, paired with INN) |
| TX-050 | Dutch BSN (used for tax) | NL personal | 123456789 (used for tax) |
| TX-051 | Dutch BTW-nummer | NL VAT | NL123456789B01, NL 1234.56.789.B.01 |
| TX-052 | Dutch RSIN (Rechtspersonen) | NL legal entity | 123456789 |
| TX-053 | Polish NIP (Numer Identyfikacji Podatkowej) | PL business/individual | 1234567890, NIP: 1234567890 |
| TX-054 | Polish PESEL (used for personal tax) | PL personal | 85031512345 (used for tax for individuals not engaged in business) |
| TX-055 | Polish REGON | PL business registry | 123456789 (9 digits, or 14 for branches) |
| TX-056 | Czech DIČ (Daňové identifikační číslo) | CZ tax | CZ12345678, CZ 8503151234 |
| TX-057 | Slovak DIČ | SK tax | SK1020034567 |
| TX-058 | Hungarian Adóazonosító jel | HU personal | 8123456789 (10 digits starting with 8) |
| TX-059 | Hungarian Adószám | HU business | 12345678-1-12 (xxxxxxxx-y-zz format) |
| TX-060 | Belgian BTW / TVA | BE VAT | BE 0123.456.789, BE0123456789 |
| TX-061 | Belgian Ondernemingsnummer | BE business | 0123.456.789 |
| TX-062 | Swedish Personnummer (used for tax) | SE personal | 19850315-1234 |
| TX-063 | Swedish Organisationsnummer | SE business | 556677-8899 (6 digits + 4 digits) |
| TX-064 | Swedish VAT (Momsnummer) | SE VAT | SE556677889901, SE 556677889901 |
| TX-065 | Norwegian Organisasjonsnummer | NO business | 123456789 (9 digits) |
| TX-066 | Norwegian VAT | NO VAT | NO123456789MVA, NO 123 456 789 MVA |
| TX-067 | Finnish Y-tunnus (Business ID) | FI business | 1234567-8 |
| TX-068 | Finnish henkilötunnus (used for personal tax) | FI personal | 150385-1230 |
| TX-069 | Danish CVR (Business) | DK business | 12345678 (8 digits) |
| TX-070 | Danish CPR (Personal tax) | DK personal | 150385-1234 |
| TX-071 | Austrian UID-Nummer | AT VAT | ATU12345678, AT U12345678 |
| TX-072 | Swiss UID (Unternehmens-Identifikationsnummer) | CH business | CHE-123.456.789, CHE 123456789, CHE-123.456.789 MWST |
| TX-073 | Israeli Tax File Number | IL | 123456789 (often matches Teudat Zehut) |
| TX-074 | Turkish Vergi Kimlik Numarası | TR business | 1234567890 (10 digits) |
| TX-075 | Turkish TC Kimlik (personal tax) | TR personal | 12345678901 |
| TX-076 | South African Tax Number | ZA | 1234567890 (10 digits) |
| TX-077 | Singapore UEN | SG business | 201234567A (12-char) |
| TX-078 | Singapore Tax Reference (NRIC-linked) | SG personal | S1234567A |
| TX-079 | Hong Kong BR (Business Registration) | HK business | 12345678 (8 digits) |
| TX-080 | Hong Kong Tax File Number | HK personal | uses HKID + suffix |
| TX-081 | Generic VAT format (EU) | EU country code + digits | DE123456789, FR12345678901, IT12345678901, ES A12345678 |
| TX-082 | EORI number (EU customs) | EU customs | DE1234567890, GB123456789000 |
| TX-083 | TIN in JSON | Structured | "tin": "12-3456789", "tax_id": "123-45-6789", "ein": "123456789", "vat": "GB123456789" |
| TX-084 | TIN in KV | Form field | tin=123-45-6789, EIN: 12-3456789, VAT: GB123456789 |
| TX-085 | TIN in XML | Markup | <tin>12-3456789</tin>, <vat country="DE">DE123456789</vat> |
| TX-086 | TIN in CSV | Tabular | "Smith","John","123-45-6789","SSN/TIN","US" |
| TX-087 | Multilingual context label | "Tax ID:" various | Tax ID (EN), Numéro fiscal (FR), Steuernummer (DE), Número fiscal (ES), Codice fiscale (IT), Número de identificação fiscal (PT), 税番号 (JP), 세금 번호 (KR), 税号 (ZH), ИНН (RU), Vergi numarası (TR), رقم ضريبي (AR), מספר מס (HE) |
| TX-088 | OCR-distorted TIN | Char substitution | l2-3456789 (l for 1), 12-345678O (O for 0); A8COE1234F (O for 0, 8 for B); GBl23456789 (l for 1) |
| TX-089 | Masked / partial TIN | Privacy-redacted | EIN: **-***6789 (last 4), TIN: ***-**-6789, VAT: GB*****789 |
| TX-090 | Anonymized placeholder | Standard generic | EIN: 00-0000000, TIN: 000-00-0000, VAT: <REDACTED>, <TAX_ID> |
| TX-091 | Sentence-boundary tricky | Trailing punctuation | "Our EIN is 12-3456789.", "Was the VAT GB123456789?", "PAN: ABCDE1234F!" |
| TX-092 | Adjacency-tight | No separator | "Acme Corp12-3456789EIN", "John Smith123-45-6789Customer" |
| TX-093 | TIN in tax form | IRS / govt context | "Form 1040: SSN 123-45-6789"; "Schedule C: EIN 12-3456789" |
| TX-094 | TIN in invoice | Business doc | "Invoice from Acme Corp, VAT: GB123456789, EIN: 12-3456789" |
| TX-095 | TIN in contract | Legal context | "Contractor: Acme LLC, EIN: 12-3456789, registered in Delaware" |
| TX-096 | TIN in W-9 form | US specific | "W-9: TIN: 123-45-6789, Type: Individual/SSN" |
| TX-097 | TIN in W-8 form | US foreign | "W-8BEN: Foreign TIN: DE12345678901, Country: Germany" |
| TX-098 | TIN in payroll record | HR / accounting | "Employee TIN: 123-45-6789, withholding: $XXX/month" |
| TX-099 | Multiple TINs in one record | Combined | "EIN: 12-3456789; State Tax ID: 12345; VAT: GB123456789" |
| TX-100 | TIN with status | Active / inactive | "EIN: 12-3456789 (active)", "VAT: GB123456789 (suspended)", "TIN: 123-45-6789 (revoked)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | TX-088 |
| Masked / partial / redacted | ✓ | TX-089, TX-090 |
| Multilingual context labels | ✓ | TX-087 |
| Country / format coverage | ✓ | TX-001 to TX-082 (40+ tax systems across US, UK, EU, Asia, Latin America, Middle East, Africa) |
| Personal vs business distinction | ✓ | TX-001/TX-003 (US), TX-007/TX-009/TX-010 (UK), TX-011/TX-012 (DE), TX-014/TX-015 (FR), TX-018/TX-019 (IT), TX-023/TX-024 (BR), TX-026/TX-027/TX-028 (IN), TX-030/TX-031 (MX), TX-039/TX-040 (JP), TX-045/TX-046 (RU) |
| In structured data | ✓ | TX-083, TX-084, TX-085, TX-086 |
| Adjacency-tight | ✓ | TX-092 |
| Sentence-boundary tricky | ✓ | TX-091 |
| Domain-embedded (tax form/invoice/contract/W-9/payroll) | ✓ | TX-093, TX-094, TX-095, TX-096, TX-097, TX-098 |
| EU VAT generic format | ✓ | TX-081, TX-082 |
| Status / multi-TIN | ✓ | TX-099, TX-100 |
| Cross-purpose IDs (SSN as TIN, CPF, CF, etc.) | ✓ | TX-001, TX-018, TX-023, TX-033, TX-042, TX-050, TX-054, TX-062, TX-068, TX-070, TX-075, TX-078, TX-080 |

**Total patterns for Tax_Reference_Number: 100**

---

## Entity 31: Credit_Card_Numbers

Payment card numbers (PAN — Primary Account Number) and related card data. PCI-DSS scope.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CC-001 | Visa — 16-digit space-separated | Standard formatting | 4111 1111 1111 1111, 4242 4242 4242 4242 |
| CC-002 | Visa — 16-digit dash-separated | Dash format | 4111-1111-1111-1111, 4242-4242-4242-4242 |
| CC-003 | Visa — 16-digit no separator | Compact | 4111111111111111, 4242424242424242 |
| CC-004 | Visa — 13-digit (legacy) | Older Visa | 4111111111111, 4222222222222 |
| CC-005 | Visa — 19-digit | Extended Visa | 4111111111111111234 |
| CC-006 | Visa with label | Form context | Visa: 4111 1111 1111 1111, Card: 4242-4242-4242-4242 |
| CC-007 | Mastercard 51-55 prefix | Old MC range | 5555 5555 5555 4444, 5105 1051 0510 5100 |
| CC-008 | Mastercard 2221-2720 prefix | New MC range | 2223 0031 2200 3222, 2720 9999 9999 9999 |
| CC-009 | Mastercard label | Form context | MasterCard: 5555 5555 5555 4444, MC: 5105-1051-0510-5100 |
| CC-010 | American Express 34 / 37 prefix | 15-digit AmEx | 3782 822463 10005, 371449 635398431 |
| CC-011 | AmEx with 4-6-5 grouping | AmEx standard | 3782 822463 10005, 3714 496353 98431 |
| CC-012 | AmEx label | Form context | AmEx: 3782 822463 10005, American Express: 3714 496353 98431 |
| CC-013 | Discover (6011, 65, 644-649) | Discover | 6011 1111 1111 1117, 6500 0000 0000 0002 |
| CC-014 | Discover label | Form context | Discover: 6011 1111 1111 1117 |
| CC-015 | Diners Club (300-305, 36, 38) | 14-digit Diners | 3056 9309 0259 04, 3852 0000 0232 37 |
| CC-016 | JCB (3528-3589) | 16-19 digits | 3530 1113 3330 0000, 3566 0020 2036 0505 |
| CC-017 | UnionPay (62) prefix | 16-19 digits | 6212 3456 7890 1234, 6228 4801 5757 1234 |
| CC-018 | Maestro (50, 56-69) | 12-19 digits | 6759 6498 2643 8453, 5018 0000 0000 0009 |
| CC-019 | Maestro UK (6759, 5018, 5020) | Maestro variants | 5020 1234 5678 9012, 6759 6498 2643 8453 |
| CC-020 | Hipercard (Brazil 606282) | BR card | 6062 8211 1111 1144 |
| CC-021 | Elo (Brazil) | BR card | 4514 1612 3456 7890, 5067 1234 5678 9012 |
| CC-022 | Rupay (India) | IN card | 6076 0000 0000 0001 |
| CC-023 | Mir (Russia, 2200-2204) | RU card | 2200 1234 5678 9012 |
| CC-024 | Card number in JSON | Structured | "credit_card": "4111111111111111", "card_number": "4242 4242 4242 4242", "pan": "5555555555554444" |
| CC-025 | Card number in KV | Form field | credit_card=4111111111111111, CC: 5555-5555-5555-4444, CARD NO: 3782 822463 10005 |
| CC-026 | Card number in XML | Markup | <credit_card>4111111111111111</credit_card>, <card_number type="visa">4242 4242 4242 4242</card_number> |
| CC-027 | Card number in CSV | Tabular | "Smith","John","4111111111111111","Visa","12/30" |
| CC-028 | Last 4 digits only | Privacy reference | ending in 1111, ****-****-****-1111, card on file ending 4444, last 4: 1234 |
| CC-029 | First 6 + last 4 (BIN + last 4) | PCI-allowed | 411111******1111, 4242 42** **** 4444, 555555******4444 |
| CC-030 | Masked with asterisks | Privacy | ****-****-****-1111, **** **** **** 4444, ****1111 |
| CC-031 | Masked with X | Alternative mask | XXXX-XXXX-XXXX-1111, xxxx xxxx xxxx 4444 |
| CC-032 | Masked with bullet/dot | Mobile-style | ●●●● ●●●● ●●●● 1111, •••• •••• •••• 4444 |
| CC-033 | Masked with leading digits visible | Reverse mask | 4111 **** **** ****, 5555 XX XXXX XXXX |
| CC-034 | CVV / CVC — 3 digits | Card verification | CVV: 123, CVC: 456, Security code: 789 |
| CC-035 | CVV / CVC — 4 digits (AmEx) | AmEx 4-digit | CID: 1234, CVV2: 5678 (AmEx) |
| CC-036 | CVV with label variants | Form context | CVV2, CVC2, CID, CSC, Security Code, Card Verification Code, CV Code |
| CC-037 | Expiration MM/YY | Standard format | 12/30, 03/25, 11/27, Exp: 12/30 |
| CC-038 | Expiration MM/YYYY | Long year | 12/2030, 03/2025, Exp Date: 11/2027 |
| CC-039 | Expiration MM-YY | Dash format | 12-30, 03-25 |
| CC-040 | Expiration "Valid Thru" | Card text | VALID THRU 12/30, Valid From 03/25 to 12/30 |
| CC-041 | Expiration with month name | Long form | Expires December 2030, Exp: Dec 30 |
| CC-042 | Cardholder name | On card | JOHN SMITH (cardholder name), Maria García (printed on card) |
| CC-043 | BIN / IIN (first 6 digits) | Bank identifier | BIN: 411111 (Visa Bank of America), IIN: 555555 |
| CC-044 | Track 1 magstripe data | Magnetic stripe | %B4111111111111111^SMITH/JOHN^30121011000000000?* |
| CC-045 | Track 2 magstripe data | Magnetic stripe | ;4111111111111111=30121010000000000000? |
| CC-046 | EMV chip data reference | EMV context | EMV chip transaction, ARQC: ABCDEF1234567890, ATC: 0042 |
| CC-047 | Apple Pay token | DPAN | Apple Pay DPAN: 4111888888881111 (tokenized) |
| CC-048 | Google Pay token | Tokenized PAN | Google Pay token: 4111888888881111, GPay tokenized |
| CC-049 | Samsung Pay token | Tokenized PAN | Samsung Pay tokenized card |
| CC-050 | Virtual card number | Single-use | Virtual card: 4111 8888 7777 6666 (single-use), Capital One Virtual Card |
| CC-051 | Gift card number | Pre-paid | Gift card: 6010 1234 5678 9012, Amazon gift card 16-digit |
| CC-052 | Network in text | Brand mention | Visa ending in 1111, Amex ending 0005, Mastercard •••• 4444 |
| CC-053 | Card with billing zip | Plus zip verification | Card: 4111 1111 1111 1111, ZIP: 90210 |
| CC-054 | Cardholder + card combined | Full bundle | "John Smith, Visa 4111-1111-1111-1111, exp 12/30, CVV 123" |
| CC-055 | Charge / transaction context | Statement line | "Charged $42.99 to Visa ending 1111 on 03/15/2024" |
| CC-056 | Refund context | Reversed charge | "Refunded $42.99 to Visa ****1111 on 03/16/2024" |
| CC-057 | Card on file | Saved | Card on file: Visa ****1111, Saved payment: MC •••• 4444 |
| CC-058 | Card decline | Failed transaction | "Card 4111-1111-1111-1111 declined: insufficient funds" |
| CC-059 | Card auth code | Approval | Auth Code: 123456, Approval Code: ABC123 |
| CC-060 | OCR-distorted card | Char substitution | 4lll-llll-llll-llll (l for 1), 4111-1ll1-1111-1111 (lowercase l); O5555555555555O (O for zeros) |
| CC-061 | OCR-distorted separators | Lost / wrong | 4111 1111 1111 1111 → 41111111 11111111 (lost spaces), 4111.1111.1111.1111 (period) |
| CC-062 | Multilingual context label | "Credit Card:" | Credit Card (EN), Carte de crédit (FR), Kreditkarte (DE), Tarjeta de crédito (ES), Carta di credito (IT), Cartão de crédito (PT), クレジットカード (JP), 신용카드 (KR), 信用卡 (ZH), Кредитная карта (RU), Kredi kartı (TR), بطاقة ائتمان (AR), כרטיס אשראי (HE), บัตรเครดิต (TH) |
| CC-063 | Anonymized placeholder | Standard test cards | 4111 1111 1111 1111 (Visa test), 5555 5555 5555 4444 (MC test), 3782 822463 10005 (AmEx test) |
| CC-064 | Sentence-boundary tricky | Trailing punctuation | "Charge it to 4111-1111-1111-1111.", "Was the card 5555 5555 5555 4444?", "Visa: 4242 4242 4242 4242!" |
| CC-065 | Adjacency-tight with name | No separator | "JohnSmith4111111111111111Visa", "Maria García,4111-1111-1111-1111,12/30" |
| CC-066 | Card in receipt | Point-of-sale | "Receipt: $42.99 charged to Visa ending 1111 at 14:30"; "AMEX 0005, Auth: 123456, $99.00" |
| CC-067 | Card in chargeback | Dispute | "Chargeback filed for Visa ****1111, reason: 4837 (no cardholder authorization)" |
| CC-068 | Card in subscription | Recurring | "Subscription billed to Visa ****1111, $9.99/month, next bill 04/15/2024" |
| CC-069 | Card in fraud alert | Security context | "Suspicious activity on Visa ****1111: $500 at unknown merchant, blocked" |
| CC-070 | Card in spoken / voice | Phone order | "I'll give you my card: four-one-one-one, one-one-one-one, one-one-one-one, one-one-one-one"; "Visa ending in triple-one one" |
| CC-071 | Card in email confirmation | Email body | "Your order paid with Visa ending in 1111 has shipped" |
| CC-072 | Card in dispute letter | Formal | "I dispute the charge of $99.99 to my Mastercard ending 4444 dated 03/15/2024" |
| CC-073 | Card type — Debit/Prepaid distinction | Type marker | "Debit Visa: 4111 1111 1111 1111", "Prepaid card: 5555 5555 5555 4444" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | CC-060, CC-061 |
| Masked / partial / redacted | ✓ | CC-028, CC-029, CC-030, CC-031, CC-032, CC-033 |
| Multilingual context labels | ✓ | CC-062 |
| Card network coverage | ✓ | CC-001 to CC-023 (Visa, MC, AmEx, Discover, Diners, JCB, UnionPay, Maestro, Hipercard, Elo, Rupay, Mir) |
| In structured data | ✓ | CC-024, CC-025, CC-026, CC-027 |
| Adjacency-tight | ✓ | CC-065 |
| Sentence-boundary tricky | ✓ | CC-064 |
| Domain-embedded (receipt/chargeback/subscription/fraud/dispute) | ✓ | CC-066 to CC-072 |
| Associated data (CVV, expiry, cardholder, BIN) | ✓ | CC-034 to CC-043 |
| Magstripe / EMV / tokens | ✓ | CC-044, CC-045, CC-046, CC-047, CC-048, CC-049, CC-050 |
| Verbal / spoken | ✓ | CC-070 |
| Anonymized test cards | ✓ | CC-063 |

**Total patterns for Credit_Card_Numbers: 73**

---

## Entity 32: Customer_Reference_Number

Customer ID / reference / account number used by a service provider to identify a person. Highly variable per industry.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CRN-001 | Numeric customer ID (short) | Sequential | Customer ID: 12345, Cust #: 67890 |
| CRN-002 | Numeric customer ID (long) | Sequential / random | Customer ID: 1234567890, Cust #: 9876543210 |
| CRN-003 | Alphanumeric customer ID | Mixed | Customer ID: ABC123456, Account: AB-12345-XY |
| CRN-004 | UUID / GUID format | Opaque | a3bb189e-8bf9-3888-9912-ace4e6543002, 550e8400-e29b-41d4-a716-446655440000 |
| CRN-005 | Hashed customer ID | Opaque hash | Customer hash: 7a3b1c9d8e6f5a2b3c4d5e6f, MD5/SHA-derived ID |
| CRN-006 | Email as customer ID | Email-based | Customer: john.smith@gmail.com (treated as ID by some services) |
| CRN-007 | Phone as customer ID | Phone-based | Customer ID: +1-917-555-0123 (used as ID by some services) |
| CRN-008 | Bank customer number | Bank-issued | Customer Number: 1234567890 (Chase), Cust ID: 9876543210 |
| CRN-009 | Bank customer with prefix | Bank format | CHASE-CN-1234567890, BOFA Customer: 9876543210 |
| CRN-010 | Utility customer number | Power / water / gas | Account #: 1234567890-001, ConEd Account: 12345-6789 |
| CRN-011 | Phone provider customer | Telco | Verizon Account: 9876543210, AT&T Customer: 123456789-0001 |
| CRN-012 | Internet provider customer | ISP | Comcast Account: 8123 12 345 1234567, Xfinity: 1234567890 |
| CRN-013 | Insurance member ID | Health insurance | Member ID: XQR123456789, Aetna Member: W123456789, BCBS: 12345XYZ67 |
| CRN-014 | Medicare beneficiary ID (MBI) | US Medicare | 1A2B-3C4-D5E6 (11 chars), MBI: 1AB2-CD3-EF45 |
| CRN-015 | Medicaid ID | US Medicaid | State Medicaid #: AA12345678, varies by state |
| CRN-016 | Healthcare MRN (Medical Record Number) | Hospital | MRN: 12345678, Medical Record No.: 9876543210 (hospital-specific) |
| CRN-017 | Patient ID (hospital-specific) | Clinical | Patient ID: P-12345678, PID: 87654321 |
| CRN-018 | Loyalty program member ID | Rewards | Loyalty #: 12345678, Member ID: SBUX12345 (Starbucks), Member: 9876543210 |
| CRN-019 | Frequent flyer number | Airline | American AAdvantage #: ABC123, Delta SkyMiles: 1234567890, United MileagePlus: AB123CD |
| CRN-020 | Hotel rewards | Hospitality | Marriott Bonvoy: 123456789, Hilton Honors: 987654321 |
| CRN-021 | Subscription service ID | SaaS / streaming | Netflix Account: john.smith@gmail.com (email-based), Spotify ID: 12345678 |
| CRN-022 | Cloud platform user ID | Cloud | AWS Account ID: 123456789012 (12 digits), Azure tenant: a1b2c3d4-..., GCP project: my-project-123456 |
| CRN-023 | Government benefit number | Welfare / SS | SSI Number: 123456789, SNAP/EBT Account: 1234567890123456 |
| CRN-024 | Veterans Affairs number | US VA | VA File Number: 12345678, VA ID: 123-45-6789 (SSN-linked) |
| CRN-025 | Insurance policy holder ID | Insurance | Policy holder ID: PH123456789, Insured ID: 987654321 |
| CRN-026 | Insurance policy number | Coverage | Policy #: POL-12345678, Auto Policy: A1234567890 |
| CRN-027 | Insurance claim number | Claim | Claim #: CL-2024-001234, Claim Reference: 987654321 |
| CRN-028 | Subscription number (magazines, newspapers) | Print | Subscription #: SUB-12345, NY Times Sub: 1234567890 |
| CRN-029 | Pension / 401k participant ID | Retirement | Participant ID: 12345678, 401k Account: P-1234567 |
| CRN-030 | Brokerage account number | Investment | Brokerage Acct: 12345678 (Fidelity), Schwab Acct: 1234-5678 |
| CRN-031 | Crypto exchange user ID | Crypto | Coinbase User ID: 12345abc, Binance UID: 123456789 |
| CRN-032 | Government tax ID-linked customer | Tax filing | IRS Customer File Number: 1234567 (alternative to SSN) |
| CRN-033 | Library card number | Library | Library Card #: 21221012345678, Library Acct: 123456 |
| CRN-034 | Gym / club membership ID | Fitness | Gym Member ID: 12345, LA Fitness: 6789 |
| CRN-035 | Cable TV / satellite account | Cable | Cox Cable: 1234567890123, DirecTV Account: 12345678 |
| CRN-036 | Mobile carrier account | Mobile | T-Mobile Account: 123456789, Verizon Wireless: 9876543210-001 |
| CRN-037 | Email service customer | Email service | Customer: john.smith@gmail.com, Gmail user ID |
| CRN-038 | Social media user ID | Platform | Twitter User ID: 12345678 (internal numeric ID), Facebook User ID: 1234567890 |
| CRN-039 | E-commerce customer ID | Online retail | Amazon Customer ID: A1B2C3D4E5F6G7, eBay User ID: bidder1234 |
| CRN-040 | Government driver / passport-linked customer | Govt service | Customer ID linked to DL/passport for DMV systems |
| CRN-041 | "Customer" / "Account" prefix variations | Label variants | Customer ID, Customer Number, Account Number, Account ID, Member ID, Member Number, Reference Number, Reference ID, Client ID, Client Number |
| CRN-042 | "Reference number" generic | Generic | Reference: REF-2024-001234, Ref #: ABCDEF12 |
| CRN-043 | Order / transaction reference | E-commerce | Order #: ORD-12345678, Transaction ID: TXN-987654321 |
| CRN-044 | Booking / confirmation number | Travel | Confirmation #: XYZ123, Booking Ref: ABC123, PNR: ABC123 |
| CRN-045 | Case / ticket number | Support | Case #: CS-2024-001234, Ticket: T-987654321, Incident: INC0012345 |
| CRN-046 | Patient appointment ID | Healthcare | Appointment ID: APT-2024-001234 |
| CRN-047 | National healthcare number | UK / European | NHS Number (UK): 943 476 5919 (10 digits), Carte Vitale (FR) |
| CRN-048 | Numeric in JSON | Structured | "customer_id": 12345678, "customer_ref": "CUST-12345", "member_id": "ABC123" |
| CRN-049 | Numeric in KV | Form field | customer_id=12345678, CUST_ID: ABC123, REF: REF-2024-001 |
| CRN-050 | Numeric in XML | Markup | <customer_id>12345678</customer_id>, <member_id>ABC-12345</member_id> |
| CRN-051 | Numeric in CSV | Tabular | "Smith","John","12345678","Customer","Active" |
| CRN-052 | Multilingual context label | "Customer:" various | Customer ID (EN), N° client (FR), Kundennummer (DE), Nº cliente (ES), N° cliente (IT), Nº de cliente (PT), 顧客番号 (JP), 고객 번호 (KR), 客户号 (ZH), Номер клиента (RU), Müşteri No (TR), رقم العميل (AR), מספר לקוח (HE), หมายเลขลูกค้า (TH) |
| CRN-053 | OCR-distorted customer ID | Char substitution | l23456789 (l for 1), Customer lD: l2345 (l for I, l for 1); CUS-O0123 (O for 0) |
| CRN-054 | Masked / partial customer ID | Privacy-redacted | Customer ****-1234 (last 4), ID: ABC***123, Ref: [REDACTED] |
| CRN-055 | Anonymized placeholder | Standard generic | Customer ID: 0000000, Customer: <REDACTED>, <CUSTOMER_ID> |
| CRN-056 | Sentence-boundary tricky | Trailing punctuation | "His customer ID is 12345678.", "Was the reference CUST-001?", "Member: ABC123!" |
| CRN-057 | Adjacency-tight | No separator | "John Smith12345678Customer", "MariaGarcíaCUST-001Active" |
| CRN-058 | Multi-system customer mapping | Cross-ref | "Internal ID: 12345678, External ID: ABC-123, Bank Cust: 9876543210" |
| CRN-059 | Customer in support transcript | Voice | "Can I have your customer ID? — It's one-two-three-four-five-six-seven-eight" |
| CRN-060 | Customer with status | Tier / status | "Customer ID: 12345678, Tier: Platinum, Status: Active, Since: 2010" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | CRN-053 |
| Masked / partial / redacted | ✓ | CRN-054, CRN-055 |
| Multilingual context labels | ✓ | CRN-052 |
| Industry coverage | ✓ | CRN-008 to CRN-040 (banking, utility, telco, ISP, insurance, healthcare, loyalty, airline, hotel, subscription, cloud, government, brokerage, crypto, library, gym, cable, mobile, e-commerce, social) |
| Format variation | ✓ | CRN-001 (short numeric), CRN-002 (long numeric), CRN-003 (alphanumeric), CRN-004 (UUID), CRN-005 (hash) |
| In structured data | ✓ | CRN-048, CRN-049, CRN-050, CRN-051 |
| Adjacency-tight | ✓ | CRN-057 |
| Sentence-boundary tricky | ✓ | CRN-056 |
| Domain-embedded (support/transcript/multi-system) | ✓ | CRN-058, CRN-059 |
| Cross-purpose (email/phone as ID) | ✓ | CRN-006, CRN-007, CRN-037 |
| Government benefit / healthcare | ✓ | CRN-014, CRN-015, CRN-016, CRN-023, CRN-024, CRN-047 |
| Generic reference labels | ✓ | CRN-041, CRN-042 |
| With status metadata | ✓ | CRN-060 |

**Total patterns for Customer_Reference_Number: 60**

---

## Entity 33: Account_Statements

Financial / billing / activity statements containing account info, transactions, balances. Long-form documents.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| AST-001 | Bank statement header | Identification block | "Bank of America\nStatement Period: 03/01/2024 — 03/31/2024\nAccount: ****1234\nJohn Smith" |
| AST-002 | Bank statement balance | Opening / closing | "Opening Balance: $5,234.78\nClosing Balance: $6,891.42\nTotal Deposits: $3,500.00\nTotal Withdrawals: $1,843.36" |
| AST-003 | Bank statement transaction line | Single transaction | "03/15/2024 DEPOSIT — PAYROLL FROM ACME CORP $3,500.00" |
| AST-004 | Bank statement multi-transaction | Multiple lines | "03/01 BALANCE FORWARD $5,234.78\n03/05 ATM WITHDRAWAL -$100.00\n03/10 CHECK #1234 -$250.00\n03/15 PAYROLL DEPOSIT +$3,500.00" |
| AST-005 | Credit card statement | CC statement | "American Express\nStatement: 02/15/24 - 03/14/24\nCardholder: John Smith\nAccount: ****10005\nNew Balance: $2,341.67\nMinimum Payment: $65.00\nPayment Due: 04/10/2024" |
| AST-006 | Credit card transactions | Charges listed | "03/01 STARBUCKS NEW YORK NY $5.42\n03/03 AMAZON.COM SEATTLE WA $129.99\n03/05 SHELL OIL CHICAGO IL $45.00" |
| AST-007 | Investment / brokerage statement | Portfolio | "Fidelity Brokerage Statement\nAccount: ****-5678\nJohn Smith\nPortfolio Value: $125,432.89\nHoldings: AAPL 50 shares, GOOG 10 shares, VTSAX 200 shares" |
| AST-008 | Mutual fund statement | Fund detail | "Vanguard VTSAX\nAccount: 12345678\nShares: 1,234.567\nNAV: $98.45\nValue: $121,545.21" |
| AST-009 | Mortgage statement | Loan | "Wells Fargo Mortgage\nLoan #: 1234567890\nProperty: 123 Main St, Springfield IL\nPrincipal Balance: $245,678.90\nInterest Rate: 6.25%\nMonthly Payment: $1,512.34" |
| AST-010 | Auto loan statement | Vehicle loan | "Auto Loan Statement\nLoan #: AL-12345678\nVehicle: 2022 Honda Civic VIN: 1HGCV1F30NA123456\nPrincipal: $18,234.56\nNext Due: $456.78 on 04/01/2024" |
| AST-011 | Student loan statement | Education loan | "Sallie Mae Student Loan\nAccount: SLM-12345678\nOriginal Balance: $45,000.00\nCurrent Balance: $38,234.56\nInterest Rate: 4.5%" |
| AST-012 | Utility bill statement | Power / water / gas | "ConEd Electric Bill\nAccount: 1234567890-001\nService Address: 123 Main St, NYC\nUsage: 542 kWh\nAmount Due: $98.45\nDue Date: 04/15/2024" |
| AST-013 | Phone bill statement | Mobile / landline | "Verizon Wireless\nAccount: 1234567890\nBilling Period: 03/01-03/31\nLines: (917) 555-0123 — John Smith\nAmount Due: $112.45" |
| AST-014 | Cable / internet bill | ISP / cable | "Comcast Xfinity\nAccount: 8123 12 345 1234567\nServices: Internet (1 Gbps), Cable TV\nAmount Due: $189.95" |
| AST-015 | Insurance premium statement | Insurance | "State Farm Auto Insurance\nPolicy: A1234567890\nPolicyholder: John Smith\nPremium: $876.45 (6-month)\nCoverage: Liability, Collision, Comprehensive" |
| AST-016 | Insurance benefits / EOB | Health EOB | "Aetna Explanation of Benefits\nMember: John Smith, ID: W123456789\nClaim: 2024-001234\nProvider: Dr. Sarah Chen\nBilled: $450.00, Allowed: $325.00, Patient Owes: $125.00" |
| AST-017 | Tax statement (W-2) | US wage stmt | "Form W-2 (2024)\nEmployer: Acme Corp, EIN: 12-3456789\nEmployee: John Smith, SSN: ***-**-6789\nBox 1: $85,000.00 (Wages), Box 2: $12,500.00 (Federal Tax Withheld)" |
| AST-018 | Tax statement (1099-MISC) | US contractor | "Form 1099-NEC (2024)\nPayer: Acme Corp\nRecipient: John Smith\nBox 1: $25,000.00 (Nonemployee Compensation)" |
| AST-019 | Tax statement (1099-INT) | US interest | "Form 1099-INT\nPayer: Chase Bank\nBox 1: $156.78 (Interest Income)" |
| AST-020 | Tax statement (1099-DIV) | US dividends | "Form 1099-DIV\nPayer: Fidelity Brokerage\nBox 1a: $1,234.56 (Total Ordinary Dividends)" |
| AST-021 | UK P60 / P45 | UK tax stmt | "P60 End of Year Certificate 2023-24\nEmployee: John Smith, NI: AB123456C\nGross Pay: £45,000.00\nTax Deducted: £8,234.56" |
| AST-022 | UK Self-Assessment statement | UK tax filing | "HMRC Self-Assessment 2023-24\nUTR: 1234567890\nTotal Liability: £12,345.67\nDue: 31 January 2025" |
| AST-023 | German Lohnsteuerbescheinigung | DE tax cert | "Lohnsteuerbescheinigung 2024\nArbeitgeber: Acme GmbH\nArbeitnehmer: John Schmidt, Steuer-ID: 12345678901\nBruttoarbeitslohn: €65,000.00" |
| AST-024 | Italian CUD / 730 statement | IT tax cert | "Certificazione Unica 2024\nDatore: Acme S.r.l.\nDipendente: Mario Rossi, CF: RSSMRA85M01H501Z\nReddito: €45,000.00" |
| AST-025 | French bulletin de salaire | FR paystub | "Bulletin de Salaire — Mars 2024\nEmployeur: Acme SAS\nEmployé: Pierre Dubois, NIR: 185037511600123\nSalaire Brut: €4,250.00\nNet Imposable: €3,234.56" |
| AST-026 | Brazilian holerite / contracheque | BR paystub | "Holerite — Março 2024\nEmpresa: Acme Ltda, CNPJ: 12.345.678/0001-90\nFuncionário: João Silva, CPF: 123.456.789-09\nSalário Bruto: R$7,500.00" |
| AST-027 | Generic paystub | Pay statement | "Pay Stub — Pay Period: 03/01/24 - 03/15/24\nEmployee: John Smith, EID: E12345\nGross: $3,500.00, Net: $2,623.45\nDeductions: Federal Tax $487.50, State Tax $156.78, FICA $267.75, 401k $350.00" |
| AST-028 | Pension / retirement statement | 401k/IRA | "Fidelity 401(k) Quarterly Statement\nParticipant: John Smith\nAccount: 12345678\nBalance: $234,567.89\nYTD Contributions: $4,500.00\nEmployer Match: $2,250.00" |
| AST-029 | Social Security statement | US SSA | "Social Security Statement\nJohn Smith, SSN: ***-**-6789\nEstimated Monthly Benefit at 67: $3,234.00\nCurrent Earnings Record: $85,000 (2023)" |
| AST-030 | Cryptocurrency statement | Crypto exchange | "Coinbase Account Statement — Q1 2024\nUser: john.smith@gmail.com\nHoldings: BTC 0.5 ($30,234), ETH 5.0 ($16,890), USDC $5,000.00\nTotal: $52,124.00" |
| AST-031 | PayPal / Venmo statement | P2P payment | "PayPal Statement — March 2024\nAccount: john.smith@gmail.com\nBalance: $342.18\nTransactions: 15 sent, 8 received" |
| AST-032 | Loyalty / rewards statement | Points | "Marriott Bonvoy Statement\nMember: John Smith, #123456789\nPoint Balance: 87,234 points\nNights Stayed YTD: 25\nElite Status: Gold" |
| AST-033 | Airline miles statement | Frequent flyer | "American AAdvantage Statement\nMember: John Smith, #ABC123\nMile Balance: 124,567 miles\nElite Status: Platinum Pro\nQualifying Miles YTD: 65,432" |
| AST-034 | Statement embedded in PDF | Filename context | filename: "BoA_Statement_March_2024.pdf", "AMEX_Statement_2024-03.pdf", "Fidelity_Q1_2024.pdf" |
| AST-035 | Statement embedded in email | Email attachment | "Your March statement is attached. — Wells Fargo"; subject: "Your AMEX Statement for March 2024 is now available" |
| AST-036 | Statement summary line | One-liner | "March 2024 statement: closing balance $6,891.42, 23 transactions" |
| AST-037 | Transaction detail with merchant | Single charge | "03/15/2024 AMAZON.COM SEATTLE WA -$129.99 (Visa ****1111)" |
| AST-038 | Pending vs posted transactions | Status | "PENDING — 03/14/2024 STARBUCKS — $5.42"; "POSTED — 03/13/2024 PAYROLL +$3,500.00" |
| AST-039 | Statement transaction in JSON | Structured | "transaction": {"date": "2024-03-15", "amount": -129.99, "merchant": "AMAZON.COM", "card": "****1111"} |
| AST-040 | Statement in XML | Markup | <statement><account>****1234</account><balance>6891.42</balance></statement> |
| AST-041 | Statement in CSV (transactions) | Bank CSV export | "Date,Description,Amount,Balance\n03/15/2024,PAYROLL,3500.00,6891.42\n03/14/2024,STARBUCKS,-5.42,3391.42" |
| AST-042 | Statement period in label | Date range | Statement Period: 03/01/2024 — 03/31/2024, Billing Cycle: 02/15 - 03/14 |
| AST-043 | Statement with year-to-date | YTD figures | "YTD Deposits: $42,500.00, YTD Withdrawals: $18,234.56, YTD Interest: $156.78" |
| AST-044 | Account holder block | Identification | "Account Holder: John A. Smith\nAddress: 123 Main St, Springfield, IL 62701\nAccount Number: ****1234" |
| AST-045 | Joint account holder | Multiple names | "Account Holders: John Smith AND Sarah Smith\nJoint Account: ****1234" |
| AST-046 | Mortgage payment schedule | Amortization | "Payment #237 of 360\nPrincipal: $345.67, Interest: $1,166.67, Escrow: $250.00\nRemaining Balance: $185,432.18" |
| AST-047 | Statement with IBAN | European | "IBAN: GB29 NWBK 6016 1331 9268 19, Statement Period: 03/2024, Balance: €8,234.56" |
| AST-048 | Statement with SWIFT/BIC | International | "BIC: NWBKGB2L, SWIFT: NWBKGB2LXXX, Wire received: $5,000.00 on 03/15/2024" |
| AST-049 | Multilingual context label | "Statement:" various | Statement (EN), Relevé (FR), Kontoauszug (DE), Estado de cuenta (ES), Estratto conto (IT), Extrato (PT), 明細書 (JP), 명세서 (KR), 对账单 (ZH), Выписка (RU), Hesap özeti (TR), كشف حساب (AR), דף חשבון (HE), ใบแจ้งยอด (TH) |
| AST-050 | OCR-distorted statement | Char substitution | "Statenent of Account" (n for m), "Balance: $S,234.78" (S for 5), "Account: ****l234" (l for 1) |
| AST-051 | OCR-distorted numeric amounts | Number errors | "$5,Z34.78" (Z for 2), "$6,89l.42" (l for 1), "$1OO.OO" (O for 0) |
| AST-052 | Masked / partial statement | Privacy-redacted | "Account: ****1234, Balance: $[REDACTED]", "Customer: [REDACTED], Transactions hidden" |
| AST-053 | Anonymized placeholder | Standard generic | Account: 0000-0000-0000-0000, Balance: $0.00, John Doe, 123 Main St |
| AST-054 | Statement at sentence boundary | Trailing punctuation | "The statement shows $6,891.42.", "Was the balance $5,234.78?", "Total: $1,234.56!" |
| AST-055 | Statement adjacency-tight | No separator | "JohnSmith****1234$6891.42", "Statement03/2024Balance$5234.78" |
| AST-056 | Statement in audit trail | SOX / compliance | "Audit log: Statement accessed 2024-03-15 14:30 by user@acme.com, Account ****1234" |
| AST-057 | Reconciliation statement | Acct reconcile | "Reconciliation Report — Acct ****1234, Period 03/2024\nGL Balance: $6,891.42\nBank Statement: $6,891.42\nVariance: $0.00" |
| AST-058 | Statement in legal discovery | E-discovery | "Subpoena response: Statements for John Smith, Acct ****1234, periods 01/2020-12/2023" |
| AST-059 | Statement in divorce / financial disclosure | Legal | "Form 13 — Financial Statement, John Smith, Assets: Bank acct ****1234 ($6,891.42), Brokerage ****5678 ($125,432.89)" |
| AST-060 | Loan repayment schedule | Schedule | "Payment Date, Principal, Interest, Balance\n04/01/2024, $456.78, $98.22, $17,777.78" |
| AST-061 | Combined household statement | Multi-account | "Smith Family Account Summary\nChecking ****1234: $6,891.42\nSavings ****5678: $25,000.00\nMortgage ****9012: -$245,678.90\nNet Worth: $87,654.32" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | AST-050, AST-051 |
| Masked / partial / redacted | ✓ | AST-052, AST-053 |
| Multilingual context labels | ✓ | AST-049 |
| Statement type coverage | ✓ | AST-001 to AST-033 (bank, CC, brokerage, mutual fund, mortgage, auto, student, utility, phone, cable, insurance, EOB, W-2, 1099, P60, P45, German/Italian/French/BR paystub, generic paystub, 401k, SS, crypto, PayPal/Venmo, loyalty, miles) |
| In structured data | ✓ | AST-039, AST-040, AST-041 |
| Adjacency-tight | ✓ | AST-055 |
| Sentence-boundary tricky | ✓ | AST-054 |
| Domain-embedded (audit/legal/divorce) | ✓ | AST-056, AST-057, AST-058, AST-059 |
| Multi-account / household | ✓ | AST-045, AST-061 |
| Statement attributes (period, YTD, account holder) | ✓ | AST-042, AST-043, AST-044 |
| International banking identifiers | ✓ | AST-047, AST-048 |
| Filename / email context | ✓ | AST-034, AST-035 |
| Transactions with status (pending/posted) | ✓ | AST-038 |
| Schedules (mortgage/loan amortization) | ✓ | AST-046, AST-060 |

**Total patterns for Account_Statements: 61**

---

## Entity 34: Compensation_and_Salary

Salary, wage, bonus, equity, and total compensation data. HR-sensitive / pay-equity-sensitive.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| SAL-001 | Annual salary USD | US base | $85,000/year, $85,000 per annum, $85K/yr, $85,000.00 annual salary |
| SAL-002 | Annual salary with "annual" | Explicit | Annual salary: $120,000, Yearly: $85,000 |
| SAL-003 | Annual salary written out | Word form | eighty-five thousand dollars per year, one hundred twenty thousand annually |
| SAL-004 | Salary with K abbreviation | Common shorthand | $85K, $120K, $250K |
| SAL-005 | Salary range | Min-max | $85,000 — $110,000, $80K-$100K, range: $85K to $120K |
| SAL-006 | Hourly rate USD | Hourly | $42.50/hour, $42.50/hr, $25/hour, $25.00 per hour |
| SAL-007 | Hourly rate with "rate" | Explicit | Hourly rate: $42.50, Rate: $25/hr, Wage: $20/hour |
| SAL-008 | Monthly salary | Per month | $7,083.33/month, $7,083 per month, monthly: $7,083 |
| SAL-009 | Bi-weekly pay | Pay period | $3,269.23 bi-weekly, $3,269/biweekly, bi-weekly gross: $3,269 |
| SAL-010 | Weekly pay | Per week | $1,634.62/week, $1,634/weekly |
| SAL-011 | Salary in EUR | European | €65,000/year, €5,416.67/month, €65.000 (DE/AT comma decimal) |
| SAL-012 | Salary in GBP | UK | £55,000/year, £4,583.33/month, £55,000 per annum |
| SAL-013 | Salary in CAD | Canadian | CAD $95,000, $95,000 CAD, C$95,000 |
| SAL-014 | Salary in AUD | Australian | AUD $110,000, A$110,000, $110,000 AUD |
| SAL-015 | Salary in INR | Indian | ₹1,200,000 per annum, ₹12 lakh/year, ₹12L, 12 LPA, 12.5 LPA |
| SAL-016 | Salary in JPY | Japanese | ¥8,000,000/年, 800万円 (8M yen), 年収800万 |
| SAL-017 | Salary in KRW | Korean | ₩70,000,000/년, 7천만원 |
| SAL-018 | Salary in CNY | Chinese | ¥500,000/年, 50万元, 年薪50万 |
| SAL-019 | Salary in BRL | Brazilian | R$ 120.000,00/ano (BR format), R$ 10.000/mês |
| SAL-020 | Salary in MXN | Mexican | MXN $1,200,000/año, $1.2M MXN |
| SAL-021 | Salary in CHF | Swiss | CHF 150,000, 150'000 CHF (Swiss apostrophe), 12'500 CHF/month |
| SAL-022 | Salary in multiple currencies | Multi-currency | Base: $85,000 USD / €78,000 EUR / £67,000 GBP |
| SAL-023 | Salary with currency label | Explicit currency | Salary in USD: 85000, Compensation: 120000 EUR, Annual (USD): $85,000 |
| SAL-024 | Total compensation | TC breakdown | Total Compensation: $250,000 = $180K base + $40K bonus + $30K equity |
| SAL-025 | Base salary specifically | Excluding bonus | Base salary: $180,000, Base: $85K (excluding bonus/equity) |
| SAL-026 | Bonus / target bonus | Variable comp | Annual bonus: $25,000 (15% of base), Target bonus: 20% of base, Performance bonus: $40,000 |
| SAL-027 | Sign-on bonus | One-time | Sign-on bonus: $20,000 (paid 30 days post-hire), Signing bonus: $15K |
| SAL-028 | Retention bonus | Stay bonus | Retention bonus: $50,000 (vested 24 months) |
| SAL-029 | Spot / discretionary bonus | One-time | Spot award: $5,000, Discretionary bonus: $10K |
| SAL-030 | Commission | Sales | Commission: 5% of revenue, OTE: $300,000 (50/50 base/commission split), Sales quota: $2M |
| SAL-031 | Stock grant / RSU | Equity | RSU: 5,000 shares vesting 4 years, $50,000/year RSU grant, Stock Grant: 1,000 shares (cliff 1-year) |
| SAL-032 | Stock options ISO / NSO | Options | ISO: 10,000 shares @ $5 strike, NSO: 5,000 shares, Options vesting 4yr/1yr cliff |
| SAL-033 | Equity percentage | Founder / early | Equity: 2.5% of fully-diluted shares, 0.5% equity (post-funding), Founder equity: 25% |
| SAL-034 | Severance | Departure | Severance: 6 months base + 1 month vacation payout, Severance package: $75,000 |
| SAL-035 | 401(k) match | US retirement | 401k match: 6% (100% match up to 6%); Employer match: $5,100/year |
| SAL-036 | Pension contribution | Retirement | Pension contribution: 8% employer + 4% employee, Defined Benefit Pension: $X/month at 65 |
| SAL-037 | Healthcare valuation | Benefits | Healthcare benefits valued at $18,000/year, Employer healthcare contribution: $1,200/month |
| SAL-038 | Stipend / allowance | Reimbursement | Cell phone allowance: $100/month, Internet stipend: $50/month, Remote work allowance: $1,000 |
| SAL-039 | Cost-of-living adjustment (COLA) | Annual increase | COLA: 3.5% effective 01/01/2024, Cost-of-Living Adjustment: 3.0% |
| SAL-040 | Merit increase | Performance raise | Merit increase: 5% (new salary $89,250), Merit raise: 4.5%, Annual raise: $5,000 |
| SAL-041 | Promotion increase | Promo bump | Promotion to Senior Engineer: $85K → $115K (+35%), Promo raise: 25% |
| SAL-042 | Pay band / salary band | Range | Pay Band: L5 ($110K-$160K), Salary Band: Senior IC III, Grade: SG3 ($85K-$120K) |
| SAL-043 | Pay grade / level | Internal level | Level 5 (E5), L4 IC, Grade GS-13, Title: Staff Engineer (L6) |
| SAL-044 | Salary on offer letter | Offer doc | "We offer base salary of $185,000, sign-on bonus $25,000, equity grant 5,000 RSU vesting 4 years" |
| SAL-045 | Salary on paystub | Pay stmt | Gross Pay: $7,083.33, Net Pay: $5,234.78, YTD Gross: $42,500.00 |
| SAL-046 | W-2 Box 1 / Box 5 amount | US tax | W-2 Box 1 (Wages): $85,000.00, Box 3 (SS Wages): $85,000.00, Box 5 (Medicare Wages): $85,000.00 |
| SAL-047 | Salary in HR record | Internal | Employee salary: $85,000, Last review salary: $80,000, Salary effective 03/15/2024 |
| SAL-048 | Salary in CV / resume | Personal | Current salary: $85K, Salary expectation: $100K-$120K |
| SAL-049 | Salary in JSON | Structured | "salary": 85000, "compensation": {"base": 180000, "bonus": 40000, "equity": 30000}, "annual_salary": 85000 |
| SAL-050 | Salary in KV | Form field | salary=85000, BASE_SALARY: 180000, ANNUAL_COMP: $250K |
| SAL-051 | Salary in XML | Markup | <salary currency="USD">85000</salary>, <compensation><base>180000</base></compensation> |
| SAL-052 | Salary in CSV | Tabular | "Smith","John","E12345","$85,000","Engineer","2020-01-15" |
| SAL-053 | Multilingual context label | "Salary:" various | Salary (EN), Salaire (FR), Gehalt (DE), Salario (ES), Stipendio (IT), Salário (PT), 給料 (JP), 급여 (KR), 工资 (ZH), Зарплата (RU), Maaş (TR), راتب (AR), משכורת (HE), เงินเดือน (TH) |
| SAL-054 | OCR-distorted salary | Char substitution | $8S,OOO (S for 5, O for 0), $l20,000 (l for 1), $85,0OO/yr (O for 0) |
| SAL-055 | OCR-distorted currency | Lost symbol | "85000/year" (lost $), "85,000 USD" (text instead of symbol) |
| SAL-056 | Masked / partial salary | Privacy-redacted | Salary: $***K, Comp: [REDACTED], Salary range: $80K-$XXX |
| SAL-057 | Anonymized placeholder | Standard generic | Salary: $0.00, Compensation: <REDACTED>, [SALARY] |
| SAL-058 | Sentence-boundary tricky | Trailing punctuation | "She earns $85,000.", "Was the offer $120K?", "Salary: $85K!" |
| SAL-059 | Adjacency-tight | No separator | "John Smith,$85,000,Engineer", "MariaGarcía$120KSenior" |
| SAL-060 | Salary in pay equity audit | DEI / pay equity | "Pay equity audit: median female salary $78K vs male $82K, gap of 4.9%"; "EEO-1 Component 2: Pay bands by gender" |
| SAL-061 | Salary in promotion review | Performance | "Performance rating: Exceeds; Recommended salary: $95K (+12%)" |
| SAL-062 | Salary in offer negotiation | Recruitment | "Initial offer: $120K base; Counter: $135K base + $20K sign-on; Final: $130K + $25K sign-on" |
| SAL-063 | Net vs gross distinction | Pre/post-tax | Gross: $85,000 (pre-tax), Net: $62,500 (after taxes), Take-home: $5,208/month |
| SAL-064 | Salary on tax form / payslip | Government | "Bruttoarbeitslohn: €65,000.00 (DE Steuerbescheinigung)", "Salaire net imposable: €3,234 (FR fiche de paie)" |
| SAL-065 | Salary in spoken / negotiation | Verbal | "I'm looking for around eighty-five thousand", "what's the band for this role" |
| SAL-066 | Salary with FX conversion | International offer | "Offer: $85K USD (~€78K EUR / ~£67K GBP at 1 USD = 0.92 EUR = 0.79 GBP)" |
| SAL-067 | Salary with relocation | Relocation package | "Relocation: $15K lump sum, packing/moving covered, 90 days temp housing ($3K/month)" |
| SAL-068 | Equity refresh | Annual top-up | "Equity refresh: 2,000 RSU/year starting Year 4, refresh grants $30K/year" |
| SAL-069 | Carried interest (PE/VC) | Partner comp | "Carry: 20% of fund profits over 8% preferred return", "Carried interest: 1.5% of Fund III" |
| SAL-070 | Salary in collective bargaining | Union | "CBA Article 12: Step-1 RN salary $72,500, Step-10 RN salary $98,750"; "Union scale: $42.50/hr base + shift differentials" |
| SAL-071 | Salary in court / divorce | Legal | "Imputed income for child support: $85,000/year"; "W-2 evidence: $85,000 gross 2023" |
| SAL-072 | Salary in census / employment data | Statistical | "Median household income: $74,580 (US, 2024)"; "BLS occupational wage: SW Eng $124,200" |
| SAL-073 | Per diem / contractor rate | Daily / hourly contractor | "Per diem: $750/day"; "Contractor rate: $150/hr W-2, $175/hr 1099" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | SAL-054, SAL-055 |
| Masked / partial / redacted | ✓ | SAL-056, SAL-057 |
| Multilingual context labels | ✓ | SAL-053 |
| Currency coverage | ✓ | SAL-001 (USD), SAL-011 (EUR), SAL-012 (GBP), SAL-013 (CAD), SAL-014 (AUD), SAL-015 (INR), SAL-016 (JPY), SAL-017 (KRW), SAL-018 (CNY), SAL-019 (BRL), SAL-020 (MXN), SAL-021 (CHF) |
| Period variants | ✓ | SAL-001 (annual), SAL-006 (hourly), SAL-008 (monthly), SAL-009 (bi-weekly), SAL-010 (weekly), SAL-073 (per diem) |
| Compensation components | ✓ | SAL-024 (TC), SAL-025 (base), SAL-026 (bonus), SAL-027 (sign-on), SAL-028 (retention), SAL-030 (commission), SAL-031 (RSU), SAL-032 (options), SAL-033 (equity %), SAL-034 (severance), SAL-035 (401k), SAL-036 (pension), SAL-037 (healthcare), SAL-038 (stipend), SAL-068 (refresh), SAL-069 (carry), SAL-067 (relocation) |
| In structured data | ✓ | SAL-049, SAL-050, SAL-051, SAL-052 |
| Adjacency-tight | ✓ | SAL-059 |
| Sentence-boundary tricky | ✓ | SAL-058 |
| Domain-embedded (offer/paystub/W-2/HR/CV/audit/legal/union) | ✓ | SAL-044, SAL-045, SAL-046, SAL-047, SAL-048, SAL-060, SAL-061, SAL-062, SAL-064, SAL-070, SAL-071 |
| Verbal / spoken | ✓ | SAL-065 |
| Bands / grades / levels | ✓ | SAL-042, SAL-043 |
| Pay change / progression | ✓ | SAL-039, SAL-040, SAL-041 |
| Gross vs net | ✓ | SAL-063 |
| Foreign exchange conversion | ✓ | SAL-066 |

**Total patterns for Compensation_and_Salary: 73**

---

## Entity 35: Employee_ID_Number

Internal employee identifier assigned by an organization. Format varies wildly by company.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| EID-001 | Short numeric employee ID | 5-6 digits | Employee ID: 12345, EID: 67890, Emp #: 123456 |
| EID-002 | Long numeric employee ID | 7-10 digits | Employee ID: 1234567, EID: 9876543210 |
| EID-003 | Alphanumeric with prefix | Common corporate | EID: E12345, EMP-12345, ID: EMP000001234 |
| EID-004 | Letter + number combo | Department-prefixed | ENG12345, HR-001, SAL-9876, IT-1234567 |
| EID-005 | Hyphenated EID | Multi-segment | E-12345, EMP-0123-4567, EID-2024-12345 |
| EID-006 | Padded numeric | Leading zeros | Employee ID: 0000012345, EID: 000123 |
| EID-007 | Format with check digit | Validation | Employee #: 1234567-X, EID: 9876543210-K (check letter at end) |
| EID-008 | New-hire vs legacy ID | Migration context | Legacy ID: 98765 (pre-2020), New ID: NH-2024-12345 |
| EID-009 | LDAP / AD username | Username-as-ID | LDAP: jsmith001, AD username: jsmith, samAccountName: jsmith |
| EID-010 | Email-based ID | Work email = ID | Employee email: john.smith@acme.com (used as EID), Email ID: jsmith@acme.com |
| EID-011 | Workday Worker ID | Workday HRIS | Worker ID: 100123456 (Workday format), Workday EID: 23456 |
| EID-012 | SAP SuccessFactors / HCM ID | SAP HRIS | Personnel #: 12345678 (SAP PERNR), SAP HR ID: 00012345 |
| EID-013 | Oracle HCM Person Number | Oracle HRIS | Person Number: 1234567, Worker Number: PN-12345 |
| EID-014 | UltiPro / UKG ID | UKG HRIS | UltiPro EID: 12345, UKG Employee ID: A12345 |
| EID-015 | ADP Associate ID | ADP payroll | ADP Associate ID: 1234567, File #: 12345 |
| EID-016 | Badge / building access number | Physical security | Badge #: 98765, Building Access: B-12345 (note: full Building_Badge_Card_Number entity) |
| EID-017 | Cost center + ID | Combined | Cost Center 12345 / Employee 67890, CC-EID: 12345-67890 |
| EID-018 | Department + ID | Org structure | Eng-1234, Marketing-5678, HR-001 |
| EID-019 | Geographic + ID | Office-based | NYC-12345, LON-EID-67890, SF-EMP-001 |
| EID-020 | Contractor / temp ID prefix | Distinguishing | Contractor ID: C-12345, Temp ID: T-9876, Vendor: V-001 (vs full-time E-prefix) |
| EID-021 | Intern ID prefix | Distinct cohort | Intern ID: I-2024-12345, Summer-intern: SI-001 |
| EID-022 | Employee ID + location | Combined | Employee ID 12345 (Office: NYC), EID: 12345 / Office: SFO |
| EID-023 | Generic "Employee Number" label | Form context | Employee Number: 12345, Emp No.: 67890, Personnel #: 123456 |
| EID-024 | "EID" abbreviation | Short form | EID: 12345, Your EID is 67890 |
| EID-025 | Hire date appended | EID + tenure | EID: 12345 (hired 2010-06-01), 12345-20100601 |
| EID-026 | EID in JSON | Structured | "employee_id": 12345, "eid": "E12345", "worker_id": "100123456" |
| EID-027 | EID in KV | Form field | employee_id=12345, EID: E12345, EMP_NUMBER: 0123456 |
| EID-028 | EID in XML | Markup | <employee_id>E12345</employee_id>, <eid type="Workday">100123456</eid> |
| EID-029 | EID in CSV | Tabular | "Smith","John","E12345","Engineer","2020-01-15" |
| EID-030 | EID on ID badge | Physical card | "John Smith, Senior Engineer, EID: E12345, Acme Corp" |
| EID-031 | EID in email signature | Email signature | "John Smith | Senior Engineer | EID 12345 | Acme Corp" |
| EID-032 | EID in payroll record | Payroll | Paystub: Employee 12345, John Smith, Pay Period 03/01-03/15 |
| EID-033 | EID in offer letter | Offer doc | "Welcome John Smith — Your Employee ID is E12345" |
| EID-034 | EID in HR record | HRIS | "Personnel File: EID 12345 — John A. Smith — Hired 2020-01-15" |
| EID-035 | EID in timesheet | Time tracking | "Timesheet — Employee 12345 — Week of 03/11/2024 — 40 hours" |
| EID-036 | EID in performance review | Performance doc | "2024 Annual Review — Employee: John Smith (EID: 12345) — Rating: Exceeds" |
| EID-037 | EID in expense report | Expenses | "Expense Report — Employee 12345 — Trip to NYC — Total $1,234.56" |
| EID-038 | EID in incident / disciplinary | HR action | "HR Incident Report — EID 12345 — Verbal Warning issued 03/15/2024" |
| EID-039 | EID in org chart | Org structure | "Manager: Jane Doe (E11111) — Reports: John Smith (E12345), Maria García (E67890)" |
| EID-040 | EID in ticket / IT support | IT ticket | "Anonymous Institution Incident INC0012345 — Requestor: John Smith (EID 12345)" |
| EID-041 | EID with role / department | Profile | "John Smith — EID 12345 — Senior Engineer — Engineering Department" |
| EID-042 | EID with manager reference | Reporting | "EID 12345 reports to EID 11111 (Jane Doe, VP Engineering)" |
| EID-043 | Termination / off-boarding ID | Departure | "Terminated EID 12345 effective 2024-03-15, off-boarding ticket #12345" |
| EID-044 | Reinstated EID | Rehire | "Rehired employee, original EID 12345, new tenure starts 2024-06-01" |
| EID-045 | Multilingual context label | "Employee ID:" various | Employee ID (EN), Matricule (FR), Personalnummer (DE), Número de empleado (ES), Matricola (IT), Nº de funcionário (PT), 社員番号 (JP), 사원번호 (KR), 员工编号 (ZH), Табельный номер (RU), Sicil No (TR), رقم الموظف (AR), מספר עובד (HE), รหัสพนักงาน (TH) |
| EID-046 | OCR-distorted EID | Char substitution | El2345 (E + lowercase l), 0OO123 (O for 0); EIDO12345 (O for 0); E1Z345 (Z for 2) |
| EID-047 | OCR-distorted prefix | Lost letters | "E 12345" (lost dash), "EMP12345" → "EM12345" |
| EID-048 | Masked / partial EID | Privacy-redacted | EID: E***45, Employee ****45, [REDACTED EID] |
| EID-049 | Anonymized placeholder | Standard generic | Employee ID: 0, EID: <REDACTED>, EMP: [EID] |
| EID-050 | Sentence-boundary tricky | Trailing punctuation | "His EID is 12345.", "Was your EID E12345?", "Employee 12345!" |
| EID-051 | Adjacency-tight | No separator | "JohnSmithE12345Engineer", "MariaGarcía,67890,Senior" |
| EID-052 | EID in audit log | Security log | "Audit: User EID 12345 accessed payroll system at 2024-03-15 14:30 UTC" |
| EID-053 | EID with system-specific suffix | Hybrid | EID 12345 / Workday 100123456 / LDAP jsmith001 / Email jsmith@acme.com |
| EID-054 | EID in spoken / dictated | Verbal | "What's your EID? Mine is E-one-two-three-four-five", "EID twelve-thousand-three-forty-five" |
| EID-055 | Globalized employee ID | Multi-region | Global EID: G-2024-US-12345, APAC EID: AP-12345 |
| EID-056 | EID in equity grant doc | Stock paperwork | "Stock Grant Notice — Recipient: John Smith (EID 12345) — Grant: 1,000 RSU" |
| EID-057 | EID in benefits enrollment | Benefits HR | "Open Enrollment 2024 — EID 12345 — Medical: Aetna PPO, Dental: Delta, Vision: VSP" |
| EID-058 | EID in training / certification | Training records | "Training Completion — EID 12345 — Security Awareness 2024 — Passed 03/15/2024" |
| EID-059 | EID linked to social/payroll | Multi-ID lookup | "John Smith — EID 12345 — SSN ***-**-6789 — Payroll ID PR-7890" |
| EID-060 | EID range / cohort | Bulk reference | "EIDs 10000-19999 are pre-2020 hires"; "Onboarding wave: EIDs 12340-12350" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | EID-046, EID-047 |
| Masked / partial / redacted | ✓ | EID-048, EID-049 |
| Multilingual context labels | ✓ | EID-045 |
| Format variation | ✓ | EID-001 (short num), EID-002 (long num), EID-003 (alphanumeric), EID-004 (dept-prefix), EID-005 (hyphenated), EID-006 (zero-padded), EID-007 (check digit) |
| HRIS-specific formats | ✓ | EID-011 (Workday), EID-012 (SAP), EID-013 (Oracle), EID-014 (UKG), EID-015 (ADP) |
| In structured data | ✓ | EID-026, EID-027, EID-028, EID-029 |
| Adjacency-tight | ✓ | EID-051 |
| Sentence-boundary tricky | ✓ | EID-050 |
| Domain-embedded (paystub/timesheet/review/expense/training/IT) | ✓ | EID-032, EID-033, EID-034, EID-035, EID-036, EID-037, EID-040, EID-056, EID-057, EID-058 |
| Cross-purpose IDs (LDAP/email/multi-system) | ✓ | EID-009, EID-010, EID-053, EID-059 |
| Worker category prefixes | ✓ | EID-020 (contractor), EID-021 (intern), EID-022 (location) |
| Lifecycle (hire/term/rehire) | ✓ | EID-008, EID-025, EID-043, EID-044 |
| Verbal / spoken | ✓ | EID-054 |
| Audit / security | ✓ | EID-052 |
| Bulk / cohort | ✓ | EID-060 |

**Total patterns for Employee_ID_Number: 60**

---

## Entity 36: Building_Badge_Card_Number

Physical access credential — building entry, parking, visitor badges. Often paired with employee/visitor identity.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| BB-001 | Numeric badge — short | 4-6 digit | Badge #: 12345, Card #: 67890, ID: 4567 |
| BB-002 | Numeric badge — long | 7-10 digit | Badge: 1234567890, Card #: 987654321 |
| BB-003 | Facility code + card number | HID Wiegand 26-bit | FC: 123, Card: 45678 → "123-45678", FC123-CN45678 |
| BB-004 | HID Wiegand 26-bit | 8-bit facility + 16-bit card | FC 042 — Card 12345; Wiegand: 0421234500 |
| BB-005 | HID Wiegand 34-bit | Extended HID | 34-bit format: FC 8421-CN 123456 |
| BB-006 | HID Wiegand 35-bit | Corporate 1000 | Corp 1000: 35-bit format Card #: 1234567890 |
| BB-007 | HID Corporate 1000 | 48-bit format | HID CP1000: Card 12345678901 |
| BB-008 | Mifare card UID | 4 or 7-byte hex | UID: A1B2C3D4, 7-byte UID: A1:B2:C3:D4:E5:F6:07 |
| BB-009 | Mifare DESFire AID | Application ID | AID: F12345 (DESFire app), Mifare DESFire serial: 04A1B2C3D4E5F6 |
| BB-010 | iCLASS PIV / FIPS-201 | Federal | PIV CHUID: 1234567890ABCDEF, iCLASS Card: 1234567890 |
| BB-011 | ProxCard II / Prox | Legacy 125kHz | Prox card: 0008812345, ProxCard Format A: 12345 |
| BB-012 | LF (125 kHz) | Low-frequency | EM4100: 0F12345678 (hex), Indala: 32-bit prox |
| BB-013 | HF (13.56 MHz) | High-frequency | NFC card UID: 04 A1 B2 C3 D4 E5 06, NTAG215 UID |
| BB-014 | UHF (860-960 MHz) | RFID parking | UHF tag: 30143639F84191AD22900417 (EPC GTIN) |
| BB-015 | Mobile credential (HID Mobile Access) | Phone-based | HID Mobile Access #: M-1234567890, HID Origo credential |
| BB-016 | Mobile credential (Openpath / Avigilon) | Phone NFC/BLE | Openpath mobile: U-12345-credential |
| BB-017 | Apple Wallet / Google Wallet pass | Digital | Apple Wallet badge: ACME-12345, Google Wallet pass: 1234567890 |
| BB-018 | Badge printed number | Visible card text | Card #: 12345 (printed on card front); Employee 12345 |
| BB-019 | Internal card number (Wiegand) | System ID | Internal: 4276451245 (32-bit decimal Wiegand) |
| BB-020 | Badge with photo + ID | Card description | "Photo ID badge: John Smith, EID E12345, Card #45678, expires 2026-03-15" |
| BB-021 | Tenant / floor-specific card | Multi-tenant | Floor 23 access card: 12345-FL23, Tenant Acme: TN-ACME-12345 |
| BB-022 | Zone / area access | Restricted | Data center access: DC-12345 (higher clearance), Lab Access: LAB-67890 |
| BB-023 | Master / admin card | Privileged | Master Card #: MK-001, Admin Access: ADM-12345 |
| BB-024 | Visitor badge | Temporary | Visitor #: V-12345, Visitor Badge: VST-2024-001234, Day Pass: DP-001 |
| BB-025 | Contractor / vendor badge | External | Contractor Badge: C-12345, Vendor: VND-67890 |
| BB-026 | Guest WiFi voucher | Adjacent system | WiFi Voucher: G-12345-WIFI (separate from physical access) |
| BB-027 | Vehicle / parking pass | Auto access | Parking Permit: P-12345, Vehicle Tag: VT-67890, Lot Pass: L-001-12345 |
| BB-028 | Garage access card | Parking | Garage Card #: 12345-GAR, Lot A: A-001 |
| BB-029 | Time & Attendance integration | TA system | Clock-in Badge: 12345 (linked to ADP/UKG TA system) |
| BB-030 | Card issuance date | Plus issue | Badge 12345 issued 2024-03-15, replacement date logged |
| BB-031 | Card expiration | Plus expiry | Badge 12345 expires 2026-03-15, valid until 12/31/2025 |
| BB-032 | Lost / Stolen badge | Status | "Reported lost: Badge 12345 on 2024-03-15, deactivated"; "Stolen card 67890" |
| BB-033 | Replacement badge | Reissue | "Replacement badge 12345-R issued for lost 12345 on 2024-03-20" |
| BB-034 | Card replacement fee | Admin | "Replacement fee $25 for lost badge 12345"; "Charged to EID 12345" |
| BB-035 | Deactivated badge | Off-boarding | "Badge 12345 deactivated 2024-03-15 (employee terminated)" |
| BB-036 | Access log entry | Audit | "2024-03-15 09:15 — Badge 12345 — Granted — Main Entrance"; "2024-03-15 17:30 — Badge 12345 — Granted — Exit" |
| BB-037 | Access denial log | Audit failure | "2024-03-15 22:00 — Badge 12345 — DENIED — Data Center (insufficient privileges)" |
| BB-038 | Tailgating event | Security incident | "Tailgating alert: Badge 12345 entered after Badge 67890 within 2 seconds, Main Entrance" |
| BB-039 | Badge in JSON | Structured | "badge_number": "12345", "card_id": "FC123-CN45678", "wiegand": "0421234500" |
| BB-040 | Badge in KV | Form field | badge=12345, CARD_ID: FC123-CN45678, ACCESS_CARD: 0421234500 |
| BB-041 | Badge in XML | Markup | <badge_number>12345</badge_number>, <access_card facility="123">45678</access_card> |
| BB-042 | Badge in CSV | Tabular | "Smith","John","E12345","Badge45678","Main Office" |
| BB-043 | Multilingual context label | "Badge:" various | Badge (EN), Badge / Carte d'accès (FR), Ausweis / Karte (DE), Insignia / Tarjeta (ES), Tessera (IT), Cartão de acesso (PT), 入館証 (JP), 출입증 (KR), 门禁卡 (ZH), Пропуск (RU), Kart / Kimlik (TR), بطاقة دخول (AR), תג כניסה (HE), บัตรเข้า-ออก (TH) |
| BB-044 | OCR-distorted badge | Char substitution | l2345 (l for 1), 0OO12345 (O for 0), FCl23-CN45678 (l for 1) |
| BB-045 | Masked / partial badge | Privacy-redacted | Badge ****45 (last 4), Card: ABC***123, Badge: [REDACTED] |
| BB-046 | Anonymized placeholder | Standard generic | Badge: 00000, Card #: <REDACTED>, [BADGE_ID] |
| BB-047 | Sentence-boundary tricky | Trailing punctuation | "His badge is 12345.", "Was the card FC123-CN45678?", "Badge denied!" |
| BB-048 | Adjacency-tight | No separator | "JohnSmith12345Badge", "MariaGarcía45678Lobby" |
| BB-049 | Badge in security incident report | Incident doc | "Security Incident #SI-2024-001: Badge 12345 used 47 times in 1 hour — anomaly" |
| BB-050 | Badge with biometric | Multi-factor | "Badge 12345 + fingerprint scan required", "Card + PIN: 12345 / 1234" |
| BB-051 | Badge in evacuation roster | Emergency | "Building evacuation roster — Badge 12345 (John Smith) accounted for at assembly point" |
| BB-052 | Badge in physical security log | Manual log | "Visitor sign-in log: Name: John Smith, Badge V-12345, Time In: 09:00, Out: 17:00" |
| BB-053 | Mobile badge with credential ID | App-based | "HID Mobile App credential: M-12345-A1B2C3, paired with phone IMEI: 359 245 080 123 456" |
| BB-054 | Smart card chip serial | Chip ID | Chip serial: 1A2B3C4D5E6F (smart card on the badge); Java Card AID |
| BB-055 | Badge with QR code | Visual | Badge contains QR: encodes "BADGE-12345-ACME-2024" or signed JWT |
| BB-056 | Anti-passback violation | Security | "Anti-passback: Badge 12345 attempted re-entry without exit logged" |
| BB-057 | Cloned / duplicated badge alert | Fraud | "Card cloning detected: Badge 12345 used simultaneously at NYC and SF offices" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | BB-044 |
| Masked / partial / redacted | ✓ | BB-045, BB-046 |
| Multilingual context labels | ✓ | BB-043 |
| Technology stack coverage | ✓ | BB-004 to BB-014 (HID Wiegand 26/34/35-bit, Mifare, iCLASS PIV, ProxCard, EM4100, NFC/NTAG, UHF RFID) |
| Mobile / digital credentials | ✓ | BB-015, BB-016, BB-017, BB-053 |
| Badge attributes (issuance, expiry, status) | ✓ | BB-030, BB-031, BB-032, BB-033, BB-035 |
| In structured data | ✓ | BB-039, BB-040, BB-041, BB-042 |
| Adjacency-tight | ✓ | BB-048 |
| Sentence-boundary tricky | ✓ | BB-047 |
| Domain-embedded (access log/incident/evacuation/sign-in) | ✓ | BB-036, BB-037, BB-038, BB-049, BB-051, BB-052, BB-056, BB-057 |
| Worker category (visitor/contractor/vendor) | ✓ | BB-024, BB-025 |
| Combined with biometric / multi-factor | ✓ | BB-050 |
| Zone / privilege levels | ✓ | BB-021, BB-022, BB-023 |

**Total patterns for Building_Badge_Card_Number: 57**

---

## Entity 37: Performance_Assessment

Employee performance ratings, reviews, feedback. HR-confidential, often used in compensation and promotion decisions.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PERF-001 | 5-point rating scale | Standard scale | Rating: 4/5, Performance: 5 out of 5, Score: 3.5/5 |
| PERF-002 | 5-point label scale | Descriptive | Far Exceeds Expectations, Exceeds Expectations, Meets Expectations, Below Expectations, Unsatisfactory |
| PERF-003 | 3-point label scale | Simplified | Exceeds / Meets / Needs Improvement; A / B / C |
| PERF-004 | 4-point scale | Common variant | Outstanding, Strong, Building, Developing |
| PERF-005 | 9-box grid | Performance × Potential | "9-box: High Performer / High Potential (top right)", "Box 4: Solid Performer, Moderate Potential" |
| PERF-006 | Letter grade | School-style | Performance Grade: A, B+, C-, A-/A range |
| PERF-007 | Numeric score | Continuous | Performance score: 87/100, Composite Score: 92.5%, Index: 4.2 |
| PERF-008 | Percentage rating | Percent-based | Performance: 85th percentile, Top 10%, Top quartile |
| PERF-009 | Stack rank | Forced ranking | "Ranked 3 of 25 on team", "Top 5% globally", "Bottom 10% (PIP candidate)" |
| PERF-010 | Calibration outcome | Post-calibration | "Calibrated rating: Meets+ (was Exceeds in self-rating)"; "Calibration committee adjusted rating from 4 to 3" |
| PERF-011 | OKR achievement | Objective scoring | OKR Q1: 0.85 (good); KR1: 1.0, KR2: 0.7, KR3: 0.85; OKR target: 0.7-1.0 |
| PERF-012 | KPI scorecard | Metric tracking | "KPI: Sales quota 110% achieved (Quota: $2M, Actual: $2.2M)"; KPI Dashboard: Green/Yellow/Red |
| PERF-013 | 360-degree feedback summary | Multi-source | "360 feedback: Strengths — collaboration, technical; Growth — communication, prioritization"; "360 score: 4.2 avg from 8 reviewers" |
| PERF-014 | Self-assessment rating | Employee input | Self-rating: Exceeds Expectations, Self-score: 4/5, Self: "I exceeded my goals this quarter" |
| PERF-015 | Manager assessment | Manager input | Manager rating: 3 (Meets), Manager comments: "Solid performance, room to grow on leadership" |
| PERF-016 | Peer review score | Peers input | Peer review avg: 4.5/5, 7 peer reviewers; Anonymous peer comments included |
| PERF-017 | Skip-level review | 2-up input | Skip-level (VP) rating: 4, comments from director-level |
| PERF-018 | Annual review document | Form | "Annual Performance Review 2024: John Smith, Senior Engineer\nOverall Rating: Exceeds\nDevelopment Plan: pursue ML certification" |
| PERF-019 | Quarterly review | Q1/Q2/Q3/Q4 | "Q1 2024 Performance Check-in: On track, 90% of goals met to date" |
| PERF-020 | Mid-year review | Half-year | "Mid-Year 2024 Review: Tracking strong, recommend stretch goal for H2" |
| PERF-021 | Probation review | New hire | "30/60/90 Day Review — John Smith — Status: Passing probation, no concerns" |
| PERF-022 | Performance Improvement Plan (PIP) | Formal corrective | "PIP for John Smith, EID 12345, dated 2024-03-15\nDuration: 60 days\nGoals: improve code review turnaround, deliver Project X on time\nOutcome: TBD" |
| PERF-023 | PIP outcome — successful | Pass | "PIP closed 2024-05-15: Employee met all goals, returned to standard performance management" |
| PERF-024 | PIP outcome — failed | Termination | "PIP failed 2024-05-15: Termination recommended, separation date 2024-05-30" |
| PERF-025 | Bonus eligibility tied to rating | Comp impact | "Bonus calculation: Rating 4 = 100% target, Rating 5 = 130%, Rating 3 = 80%"; "Per rating, bonus multiplier 1.0x" |
| PERF-026 | Promotion recommendation | Comp/career | "Promotion recommended: John Smith from L4 to L5 effective Q3 2024"; "Promo case scored: Strong" |
| PERF-027 | High-Potential (HiPo) designation | Talent | "HiPo: Yes — identified for accelerated career path"; "Top Talent designation: Top 5%" |
| PERF-028 | At-risk / underperforming | Watch list | "At Risk: Performance trending down 2 consecutive quarters"; "Underperforming employee — manager intervention required" |
| PERF-029 | Performance comments — strengths | Narrative | "Strengths: Strong technical skills, excellent customer focus, builds trust quickly" |
| PERF-030 | Performance comments — improvement | Narrative | "Areas for improvement: Strategic thinking, executive communication, scope management" |
| PERF-031 | Performance score in JSON | Structured | "performance_rating": 4, "annual_review": {"overall": "Exceeds", "score": 4.2}, "pip_status": "active" |
| PERF-032 | Performance in KV | Form field | rating=4, PERFORMANCE: Exceeds, PIP: No, HIPO: Yes |
| PERF-033 | Performance in XML | Markup | <performance_rating>4</performance_rating>, <annual_review year="2024">Exceeds</annual_review> |
| PERF-034 | Performance in CSV | Tabular | "Smith","John","E12345","2024","Exceeds","4.2","HiPo" |
| PERF-035 | Calibration in spreadsheet | HR tracker | "Pre-calibration: Exceeds; Post-calibration: Meets+; Reason: distribution adjustment" |
| PERF-036 | Reviewer / Rater name | Linked | "Reviewed by: Jane Doe (Manager); Approved by: Mike Chen (Director)" |
| PERF-037 | Review cycle dates | Time window | "Review Period: 2024-01-01 to 2024-12-31; Review Date: 2025-02-15" |
| PERF-038 | Goals / objectives list | Doc structure | "Goal 1: Ship Project X by Q2 (Status: Complete); Goal 2: Mentor 2 junior engineers (Status: On track)" |
| PERF-039 | Competency framework | Skills matrix | "Technical Skills: Advanced (4); Leadership: Developing (2); Communication: Proficient (3)" |
| PERF-040 | Promotion packet content | Promo case | "Promotion Case: Sustained performance at next level for 12+ months, demonstrated by [X, Y, Z]" |
| PERF-041 | Performance multilingual label | Various | Performance (EN), Évaluation (FR), Leistungsbeurteilung (DE), Evaluación del desempeño (ES), Valutazione (IT), Avaliação (PT), 業績評価 (JP), 성과 평가 (KR), 绩效评估 (ZH), Оценка эффективности (RU), Performans (TR), تقييم الأداء (AR), הערכת ביצועים (HE) |
| PERF-042 | OCR-distorted rating | Char substitution | "Exceede" (lost d), "Ratlng: 4" (l for i), Rat1ng: 5 (1 for i); "PerfOrmance" (O for o) |
| PERF-043 | Masked / partial review | Privacy-redacted | "Rating: ***", Review: [REDACTED], Performance score: ** |
| PERF-044 | Anonymized placeholder | Standard generic | Rating: N/A, Review: [PENDING], Performance: <SCORE> |
| PERF-045 | Sentence-boundary tricky | Trailing punctuation | "She received an Exceeds rating.", "Was the score 4.5?", "Promotion approved!" |
| PERF-046 | Adjacency-tight | No separator | "JohnSmithExceedsExpectations", "EID12345Rating4Exceeds" |
| PERF-047 | Performance with manager context | Linked | "John Smith (EID 12345) rated Exceeds by manager Jane Doe (EID 11111)" |
| PERF-048 | Performance in EEOC complaint | Legal | "EEOC complaint: Plaintiff alleges performance ratings were biased on basis of race"; "Pattern of low ratings for protected class members" |
| PERF-049 | Performance in lawsuit | Court | "Defendant cites performance documentation in wrongful termination suit" |
| PERF-050 | Performance in compensation memo | Comp committee | "Comp Committee: John Smith — Exceeds — Recommend 5% merit + $15K bonus + 1,000 RSU refresh" |
| PERF-051 | Continuous performance check-in | Modern HR | "Weekly 1:1 — John Smith — Project X on track, no blockers, growth area: communication" |
| PERF-052 | Crowdsourced peer feedback | Modern HR | "Peer kudos: 12 received this quarter; specific examples: 'great cross-team collaboration on Q1 launch'" |
| PERF-053 | Performance trend over time | Multi-year | "Performance history: 2022 Meets, 2023 Exceeds, 2024 Exceeds (trending up)" |
| PERF-054 | Calibration session note | Meeting record | "Calibration Session Q2 2024: Engineering team — 30 reviewed, distribution: 5% FE, 15% E, 70% M, 8% BE, 2% U" |
| PERF-055 | Stretch goal completion | Above-and-beyond | "Stretch goal achieved: Led Project Y delivery 2 weeks early"; "Beyond scope: completed mentorship program" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | PERF-042 |
| Masked / partial / redacted | ✓ | PERF-043, PERF-044 |
| Multilingual context labels | ✓ | PERF-041 |
| Rating system coverage | ✓ | PERF-001 (5-pt num), PERF-002 (5-pt label), PERF-003 (3-pt), PERF-004 (4-pt), PERF-005 (9-box), PERF-006 (letter), PERF-007 (numeric), PERF-008 (%), PERF-009 (stack rank) |
| Review type coverage | ✓ | PERF-013 (360), PERF-014 (self), PERF-015 (manager), PERF-016 (peer), PERF-017 (skip-level), PERF-018 (annual), PERF-019 (quarterly), PERF-020 (mid-year), PERF-021 (probation) |
| In structured data | ✓ | PERF-031, PERF-032, PERF-033, PERF-034 |
| Adjacency-tight | ✓ | PERF-046 |
| Sentence-boundary tricky | ✓ | PERF-045 |
| Domain-embedded (PIP/promo/lawsuit/comp) | ✓ | PERF-022, PERF-023, PERF-024, PERF-026, PERF-040, PERF-048, PERF-049, PERF-050 |
| HR system / process | ✓ | PERF-010, PERF-035, PERF-054 |
| OKR / KPI / Competency | ✓ | PERF-011, PERF-012, PERF-039 |
| Talent designation | ✓ | PERF-027, PERF-028 |
| Time-trend / multi-period | ✓ | PERF-053 |
| Modern continuous feedback | ✓ | PERF-051, PERF-052, PERF-055 |

**Total patterns for Performance_Assessment: 55**

---

## Entity 38: Disciplinary_Action

Records of warnings, suspensions, terminations, and other corrective actions. Sensitive personnel data.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| DISC-001 | Verbal warning | First-step informal | "Verbal warning issued to John Smith on 2024-03-15 for tardiness"; "Documented verbal counseling" |
| DISC-002 | Written warning | First written step | "Written Warning — John Smith — 2024-03-15 — Reason: violation of attendance policy"; "First written warning" |
| DISC-003 | Final written warning | Last step | "Final Written Warning — failure to improve will result in termination" |
| DISC-004 | Performance Improvement Plan (PIP) | Formal | "PIP issued 2024-03-15, 60-day duration, failure may result in termination" |
| DISC-005 | Suspension — paid | Investigation pending | "Suspended with pay pending investigation, effective 2024-03-15" |
| DISC-006 | Suspension — unpaid | Disciplinary | "5-day unpaid suspension, 2024-03-15 to 2024-03-19, for code of conduct violation" |
| DISC-007 | Demotion | Rank reduction | "Demoted from Senior Engineer (L5) to Engineer (L4) effective 2024-04-01, salary reduction $25K" |
| DISC-008 | Reassignment | Lateral move | "Reassigned to different team effective 2024-03-15 due to interpersonal conflict" |
| DISC-009 | Termination — for cause | Cause termination | "Terminated for cause — gross misconduct (theft of company property) — effective immediately 2024-03-15" |
| DISC-010 | Termination — without cause | At-will | "Terminated without cause effective 2024-03-15, severance package per policy" |
| DISC-011 | Termination — performance | Performance-based | "Terminated for performance after PIP failure, effective 2024-05-30" |
| DISC-012 | Resignation in lieu | Negotiated | "Resignation accepted 2024-03-15 in lieu of termination, severance per agreement" |
| DISC-013 | Termination — attendance | Attendance-based | "Terminated for excessive absenteeism per attendance policy" |
| DISC-014 | Probationary status | New hire watch | "Placed on extended probation, 90 additional days" |
| DISC-015 | Code of conduct violation | Generic | "Code of Conduct violation: inappropriate language in workplace, written warning issued" |
| DISC-016 | Harassment finding | Title VII context | "Harassment investigation completed; substantiated; respondent issued written warning + mandatory training" |
| DISC-017 | Discrimination finding | Title VII / GDPR | "Discrimination complaint substantiated; respondent terminated, restitution to complainant" |
| DISC-018 | Workplace violence | Severe | "Workplace violence incident — physical altercation — immediate termination + restraining order" |
| DISC-019 | Theft / fraud | Property / financial | "Termination for theft — laptop and equipment valued at $4,500 — referred to law enforcement" |
| DISC-020 | Embezzlement | Financial fraud | "Termination for embezzlement — $250,000 — criminal charges filed" |
| DISC-021 | Sexual harassment | Specific category | "Sexual harassment violation, Title VII — termination + ongoing legal review" |
| DISC-022 | Drug / alcohol policy | Substance | "Termination after positive drug test (cocaine) per zero-tolerance policy" |
| DISC-023 | Confidentiality breach | NDA / data | "NDA violation — leaked Project X details to press — termination + legal action" |
| DISC-024 | Data breach (employee-caused) | Security | "Employee terminated for unauthorized disclosure of customer PII to external party" |
| DISC-025 | Insider trading | Securities | "Termination for insider trading violation, referred to SEC" |
| DISC-026 | Falsified records / timesheet fraud | Records | "Termination for falsified timesheets — claimed 60 hours worked, actually 30 hours" |
| DISC-027 | Workplace safety violation | OSHA | "Written warning for ignoring lockout/tagout procedure"; "Termination after 3rd safety violation" |
| DISC-028 | Insubordination | Authority | "Written warning for insubordination — refused direct orders from supervisor" |
| DISC-029 | Conflict of interest | Ethics | "Written warning for undisclosed conflict of interest — vendor relationship" |
| DISC-030 | Social media / public comments | External conduct | "Termination for public social media post violating company values" |
| DISC-031 | Union grievance — filed | Labor | "Grievance Step 1 filed by employee 12345, alleging unjust written warning" |
| DISC-032 | Union grievance — resolved | Labor | "Grievance resolved at Step 2 — written warning rescinded, employee made whole" |
| DISC-033 | Arbitration outcome | Labor | "Arbitration: termination upheld; or grievance sustained, employee reinstated with back pay" |
| DISC-034 | Just-cause analysis | Union context | "Just-cause analysis: progressive discipline followed, termination upheld" |
| DISC-035 | Wrongful termination claim | Legal | "Wrongful termination lawsuit filed 2024-04-15; alleges retaliation for whistleblower complaint" |
| DISC-036 | Discrimination claim filed | EEOC / agency | "EEOC charge filed 2024-03-15 — alleging termination based on age" |
| DISC-037 | Investigation memo | HR doc | "Investigation Memo: Allegation — harassment; Findings — substantiated; Recommended action — written warning + training" |
| DISC-038 | Witness statement | Investigation | "Witness statement — Jane Doe (EID 11111) — observed John Smith making inappropriate comment on 2024-03-10" |
| DISC-039 | Disciplinary in personnel file | HR file | "Personnel File — John Smith — 2024-03-15: First Written Warning, 2024-05-15: Final Written, 2024-08-15: Termination" |
| DISC-040 | Disciplinary in JSON | Structured | "discipline": {"type": "written_warning", "date": "2024-03-15", "reason": "tardiness"} |
| DISC-041 | Disciplinary in KV | Form field | discipline_type=written_warning, REASON: tardiness, DATE: 2024-03-15 |
| DISC-042 | Disciplinary in XML | Markup | <disciplinary_action type="written_warning"><reason>tardiness</reason><date>2024-03-15</date></disciplinary_action> |
| DISC-043 | Disciplinary in CSV | Tabular | "Smith","John","E12345","Written Warning","2024-03-15","Tardiness" |
| DISC-044 | Multilingual context label | Various | Disciplinary Action (EN), Mesure disciplinaire (FR), Disziplinarmaßnahme (DE), Acción disciplinaria (ES), Provvedimento disciplinare (IT), 懲戒処分 (JP), 징계 (KR), 纪律处分 (ZH), Дисциплинарное взыскание (RU), Disiplin cezası (TR), إجراء تأديبي (AR), פעולת משמעת (HE) |
| DISC-045 | OCR-distorted disciplinary | Char substitution | "Wrltten Warnlng" (l for i), "Suspenslon" (l for i); "TermlnatlOn" (l for i, O for o) |
| DISC-046 | Masked / partial discipline | Privacy-redacted | "Discipline: [REDACTED]", "Reason: ***", "Action type: ****" |
| DISC-047 | Anonymized placeholder | Standard generic | Action: <REDACTED>, Reason: [PRIVATE], Disciplinary: TBD |
| DISC-048 | Sentence-boundary tricky | Trailing punctuation | "He received a written warning.", "Was the termination justified?", "Suspended immediately!" |
| DISC-049 | Adjacency-tight | No separator | "JohnSmithE12345TerminatedTheft", "MariaGarcíaWrittenWarning2024-03-15" |
| DISC-050 | Reinstatement | Reversal | "Reinstated 2024-06-01 following arbitration ruling, back pay $X awarded" |
| DISC-051 | Discipline rescinded | Reversal | "Written warning rescinded 2024-04-15; no longer in personnel file" |
| DISC-052 | Last-chance agreement | Restoration with conditions | "Last Chance Agreement signed 2024-03-15 — return from suspension contingent on no further violations" |
| DISC-053 | Disciplinary appeal | Process | "Appeal filed by employee 12345 regarding written warning; review scheduled 2024-04-01" |
| DISC-054 | Open / Pending investigation | Status | "Pending investigation — pre-determination conference scheduled 2024-03-20" |
| DISC-055 | Closed investigation — unfounded | Cleared | "Investigation closed 2024-03-15: allegations unfounded, no discipline issued" |
| DISC-056 | Settlement / non-disclosure | Confidential resolution | "Settlement Agreement signed 2024-03-15: $XXX,XXX, mutual NDA, separation effective 2024-03-30" |
| DISC-057 | Severance with discipline | Mixed | "Termination with severance — 4 weeks pay + COBRA contribution — in exchange for release of claims" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | DISC-045 |
| Masked / partial / redacted | ✓ | DISC-046, DISC-047 |
| Multilingual context labels | ✓ | DISC-044 |
| Action type coverage | ✓ | DISC-001 (verbal), DISC-002 (written), DISC-003 (final), DISC-004 (PIP), DISC-005 (paid susp), DISC-006 (unpaid susp), DISC-007 (demotion), DISC-008 (reassign), DISC-009 (cause), DISC-010 (no-cause), DISC-011 (perf), DISC-012 (resign-in-lieu), DISC-013 (attendance) |
| Cause type coverage | ✓ | DISC-015 (CoC), DISC-016 (harassment), DISC-017 (discrim), DISC-018 (violence), DISC-019 (theft), DISC-020 (embezzlement), DISC-021 (sexual harass), DISC-022 (drug/alc), DISC-023 (NDA), DISC-024 (data breach), DISC-025 (insider trading), DISC-026 (timesheet fraud), DISC-027 (safety), DISC-028 (insubordination), DISC-029 (conflict), DISC-030 (social media) |
| Union / labor specific | ✓ | DISC-031, DISC-032, DISC-033, DISC-034 |
| Legal / litigation | ✓ | DISC-035, DISC-036, DISC-049 |
| Investigation lifecycle | ✓ | DISC-037, DISC-038, DISC-054, DISC-055 |
| In structured data | ✓ | DISC-040, DISC-041, DISC-042, DISC-043 |
| Adjacency-tight | ✓ | DISC-049 |
| Sentence-boundary tricky | ✓ | DISC-048 |
| Reversal / appeal | ✓ | DISC-050, DISC-051, DISC-053 |
| Settlement / agreement | ✓ | DISC-052, DISC-056, DISC-057 |
| Personnel file domain | ✓ | DISC-039 |

**Total patterns for Disciplinary_Action: 57**

---

## Entity 39: Sickness_Day_Records

Sick leave, medical leave, disability records. GDPR Article 9 health-adjacent data; FMLA/ADA in US; comparable laws elsewhere.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| SICK-001 | Sick days taken — count | Numeric | Sick days used: 3, Sick: 5 days in 2024, Out sick: 2 days |
| SICK-002 | Sick days balance | Remaining | Sick day balance: 7 days remaining, Sick PTO: 40 hours left |
| SICK-003 | Sick day accrual rate | Earning | Accrual rate: 1.5 sick days/month, 8 hours sick per month |
| SICK-004 | Sick call-in log | Daily record | "Called in sick 2024-03-15"; "Sick call: 2024-03-15, John Smith, flu symptoms" |
| SICK-005 | Sick day with date range | Multi-day | "Out sick 2024-03-15 to 2024-03-19 (5 days)"; "Sick leave from Monday to Wednesday" |
| SICK-006 | Reason / symptom note | Cause | "Reason: flu", "Symptoms: fever, cough"; "Sick reason: migraine" — note: many companies don't require this |
| SICK-007 | Specific medical condition | Sensitive | "Out for diabetes management, 1 day"; "Migraine — 3 days"; "Cancer treatment — extended leave" |
| SICK-008 | Doctor's note required | Documentation | "Doctor's note required after 3+ consecutive sick days"; "Doctor's note submitted 2024-03-20" |
| SICK-009 | Doctor's note attached | Doc reference | "Medical certificate from Dr. Sarah Chen dated 2024-03-15; diagnosis: bronchitis" |
| SICK-010 | FMLA (US Family Medical Leave) | 12 weeks | "FMLA leave approved: 12 weeks for serious health condition; 2024-04-01 to 2024-06-23"; "FMLA-protected absence" |
| SICK-011 | FMLA intermittent | Episodic | "Intermittent FMLA approved for chronic condition (migraines), up to 2 days/week" |
| SICK-012 | FMLA — bonding leave | New parent | "FMLA Bonding Leave for new child, 12 weeks starting 2024-04-15" |
| SICK-013 | FMLA — military caregiver | Service member family | "FMLA Military Caregiver Leave, 26 weeks for service member spouse" |
| SICK-014 | ADA accommodation | Disability | "ADA accommodation: ergonomic workstation, flexible schedule, remote work 2 days/week" |
| SICK-015 | ADA disability disclosure | Self-disclose | "Employee self-identifies with disability (chronic pain), accommodation requested" |
| SICK-016 | Short-Term Disability (STD) | Insurance | "STD claim approved: 60% income replacement, 2024-03-15 to 2024-06-15, 13 weeks" |
| SICK-017 | Long-Term Disability (LTD) | Long-term insurance | "LTD claim approved after 6-month elimination period; 50% income replacement until age 65 or recovery" |
| SICK-018 | Maternity leave | Childbirth | "Maternity leave: 12 weeks paid + 4 weeks unpaid, expected return 2024-09-01" |
| SICK-019 | Paternity leave | New father | "Paternity leave: 4 weeks paid, 2024-04-01 to 2024-04-28" |
| SICK-020 | Parental leave (non-gender-specific) | Modern | "Parental Leave: 16 weeks for new parent regardless of gender" |
| SICK-021 | Adoption leave | New child via adoption | "Adoption Leave: 8 weeks paid following placement" |
| SICK-022 | Worker's compensation | Work injury | "Worker's comp claim #WC-2024-001234: back injury at warehouse; off work 6 weeks; case manager: J. Davis" |
| SICK-023 | Mental health day | Modern | "Mental health day taken 2024-03-15"; "Wellness day"; "Personal day used for mental health" |
| SICK-024 | Personal day | Generic | "Personal day used 2024-03-15"; "Floating Holiday taken"; "Used 1 PTO day" |
| SICK-025 | PTO bank usage | Pooled time off | "Used 3 PTO days; PTO balance: 12 days remaining (60% of annual entitlement)" |
| SICK-026 | Bereavement leave | Family death | "Bereavement Leave: 5 days for parent/spouse/child death; 3 days for grandparent" |
| SICK-027 | Jury duty leave | Civic | "Jury duty: 2024-03-15 to 2024-03-19, paid by employer (no PTO deduction)" |
| SICK-028 | Military leave | Reservist | "Military Leave: 2 weeks annual training for National Guard, USERRA-protected" |
| SICK-029 | Sabbatical | Extended unpaid | "Sabbatical: 3 months unpaid, 2024-06-01 to 2024-09-01" |
| SICK-030 | Garden leave | Post-resignation | "Garden Leave: paid during 90-day notice period, no work performed" |
| SICK-031 | COVID-19 leave | Pandemic | "COVID Sick Leave: tested positive 2024-01-15, isolated 5 days per CDC"; "COVID quarantine 10 days" |
| SICK-032 | Cancer treatment leave | Specific severe | "Out for chemotherapy 2024-03-15; FMLA intermittent approved for treatment days" |
| SICK-033 | Surgery recovery | Surgical context | "Knee surgery 2024-03-15; expected 4-6 weeks recovery; STD claim filed" |
| SICK-034 | Pregnancy-related leave (pre-delivery) | Antepartum | "Pregnancy-related medical leave 2024-03-15 (bed rest ordered by OB)" |
| SICK-035 | Postpartum recovery | After delivery | "Postpartum recovery period: 6 weeks (8 if C-section); separate from bonding leave" |
| SICK-036 | Workers' comp + lost wages | WC claim | "WC claim approved: $X/week lost wages, medical bills covered by carrier" |
| SICK-037 | Return-to-work clearance | Doctor clearance | "Cleared to return to work effective 2024-04-15 with no restrictions"; "Return with light duty restrictions" |
| SICK-038 | Return-to-work with accommodation | Modified duty | "Cleared to return with accommodations: no lifting >10 lbs, hybrid schedule" |
| SICK-039 | Excessive absenteeism warning | Pattern | "Attendance review: 12 unplanned absences in 6 months exceeds policy threshold (8)" |
| SICK-040 | No-call/no-show | Job abandonment | "No-call/no-show 3 consecutive days 2024-03-15 to 2024-03-19; deemed voluntary resignation" |
| SICK-041 | Sick leave abuse investigation | Audit | "Sick leave audit: pattern of Friday/Monday absences flagged for review" |
| SICK-042 | Sick day in JSON | Structured | "sick_days_used": 3, "sick_balance": 7, "fmla_status": "approved" |
| SICK-043 | Sick day in KV | Form field | sick_days=3, FMLA: APPROVED, REASON: flu |
| SICK-044 | Sick day in XML | Markup | <sick_days_used>3</sick_days_used>, <fmla_status>approved</fmla_status> |
| SICK-045 | Sick day in CSV | Tabular | "Smith","John","E12345","2024-03-15","Sick","1","Flu" |
| SICK-046 | Multilingual context label | Various | Sick Leave (EN), Congé maladie (FR), Krankheitstage (DE), Baja por enfermedad (ES), Malattia (IT), Atestado médico (PT), 病気休暇 (JP), 병가 (KR), 病假 (ZH), Больничный (RU), Hastalık izni (TR), إجازة مرضية (AR), ימי מחלה (HE), ลาป่วย (TH) |
| SICK-047 | OCR-distorted sick record | Char substitution | "Slck Leave" (l for i), "FMlA" (l for L), "Mat3rnlty" (3 for e, l for i) |
| SICK-048 | Masked / partial sick record | Privacy-redacted | "Sick days: ***", Diagnosis: [REDACTED], Medical: [PRIVATE] |
| SICK-049 | Anonymized placeholder | Standard generic | Sick: 0 days, Leave Type: <REDACTED>, Reason: [SENSITIVE] |
| SICK-050 | Sentence-boundary tricky | Trailing punctuation | "She was out sick 3 days.", "Is FMLA approved?", "Maternity leave starts Monday!" |
| SICK-051 | Adjacency-tight | No separator | "JohnSmithE12345Sick3Days", "MariaGarcíaFMLAApprovedMaternity" |
| SICK-052 | Disability rating / percentage | VA-style | "VA disability rating: 70% service-connected (PTSD)"; "Permanent partial disability: 25%" |
| SICK-053 | Catastrophic illness leave | Severe | "Catastrophic leave: pooled donated PTO from coworkers for cancer treatment" |
| SICK-054 | EAP referral | Employee Assistance | "EAP referral for stress management; confidential counseling sessions" |
| SICK-055 | Health insurance claim linked | Medical claim | "Linked to medical claim #MC-2024-001 for back surgery, $XX,XXX billed" |
| SICK-056 | Sick leave conversion | Buy-out / cash | "Unused sick leave converted to cash: $X,XXX at retirement (per policy)" |
| SICK-057 | Sick leave audit / unused | Year-end | "Year-end unused sick leave: 5 days carried over to 2025 (max 10 days carryover)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | SICK-047 |
| Masked / partial / redacted | ✓ | SICK-048, SICK-049 |
| Multilingual context labels | ✓ | SICK-046 |
| Leave type coverage | ✓ | SICK-001 (sick), SICK-010 (FMLA), SICK-014 (ADA), SICK-016 (STD), SICK-017 (LTD), SICK-018 (maternity), SICK-019 (paternity), SICK-020 (parental), SICK-021 (adoption), SICK-022 (workers comp), SICK-023 (mental health), SICK-024 (personal), SICK-026 (bereavement), SICK-027 (jury), SICK-028 (military), SICK-029 (sabbatical), SICK-030 (garden), SICK-031 (COVID) |
| Medical specificity | ✓ | SICK-007, SICK-031, SICK-032, SICK-033, SICK-034, SICK-035, SICK-052 |
| Documentation / certification | ✓ | SICK-008, SICK-009, SICK-037, SICK-038 |
| In structured data | ✓ | SICK-042, SICK-043, SICK-044, SICK-045 |
| Adjacency-tight | ✓ | SICK-051 |
| Sentence-boundary tricky | ✓ | SICK-050 |
| Domain-embedded (workers comp/EAP/audit) | ✓ | SICK-022, SICK-036, SICK-054, SICK-055 |
| Pattern / abuse / abandonment | ✓ | SICK-039, SICK-040, SICK-041 |
| Conversion / carryover | ✓ | SICK-056, SICK-057 |
| Pre/postnatal / specific maternity | ✓ | SICK-034, SICK-035 |

**Total patterns for Sickness_Day_Records: 57**

---

## Entity 40: Professional_Background

Career history, education, skills, certifications. CV / resume / LinkedIn-style data.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PROF-001 | Job title — current | Active role | Current role: Senior Software Engineer, Position: VP of Engineering, Title: Manager, Customer Success |
| PROF-002 | Job title with seniority | Level + role | Senior Engineer II, Principal Architect, Staff Engineer, Distinguished Engineer, Fellow |
| PROF-003 | Job title with department | Functional | Director of Marketing, Head of Product, VP of Engineering, Chief Information Security Officer |
| PROF-004 | Employment dates — range | Tenure | "Senior Engineer at Acme Corp — June 2020 to Present"; "2018-2020"; "May 2018 — Aug 2022 (4 yr 4 mo)" |
| PROF-005 | Employment dates — single | Anchor | "Joined Acme 2020"; "Started June 2020"; "Hired Q2 2020" |
| PROF-006 | Tenure expressed in years | Duration | "5 years at Acme Corp"; "4.5 years tenure"; "1 year 7 months" |
| PROF-007 | Company history — chronological | Multi-employer | "Acme Corp (2020-present), Beta Inc (2018-2020), Gamma LLC (2015-2018)" |
| PROF-008 | Reverse chronological CV style | LinkedIn format | "EXPERIENCE\nSenior Engineer, Acme Corp (Jun 2020-Present)\n• Led team of 5\nSoftware Engineer, Beta Inc (Mar 2018-May 2020)" |
| PROF-009 | Job duties / responsibilities | Bullet description | "Led cross-functional team of 8 engineers, designed scalable microservices architecture, mentored 3 junior engineers" |
| PROF-010 | Career gap | Employment hiatus | "Career break: 2019-2020 (caregiving for family)"; "Sabbatical 2022 (6 months)"; "Gap 2018-2019" |
| PROF-011 | Reason for leaving | Departure cause | "Reason for leaving: career growth"; "Left due to layoffs"; "Restructuring"; "Better opportunity" |
| PROF-012 | Promotion within company | Internal progression | "Promoted from Senior Engineer to Staff Engineer (Jan 2023)"; "Internal move: IC to Manager 2022" |
| PROF-013 | Education — degree | Highest credential | MS in Computer Science, MBA, PhD in Physics, BSc Mathematics, BTech Electrical Engineering |
| PROF-014 | Education — institution | School | Stanford University, MIT, Carnegie Mellon, IIT Hyderabad, Oxford, INSEAD |
| PROF-015 | Education — graduation year | Year | Graduated 2015; Class of 2020; Completed May 2018 |
| PROF-016 | Education — GPA / honors | Academic | GPA: 3.92/4.0, Summa Cum Laude, First Class with Distinction, Magna Cum Laude |
| PROF-017 | Education — major / minor | Focus | Major: Computer Science, Minor: Mathematics; Concentration: AI/ML |
| PROF-018 | Education — thesis / dissertation | Research | Master's Thesis: "Change-Point Detection via Structured Projections", Advisor: Prof. Yardi |
| PROF-019 | Online course / MOOC | Modern training | Coursera Deep Learning Specialization (2023), edX MIT MicroMasters, fast.ai Practical Deep Learning |
| PROF-020 | Professional certifications | Industry | AWS Solutions Architect Professional (2023, expires 2026), CISSP, PMP, CFA Level III, Google Cloud Certified Engineer |
| PROF-021 | Professional license | State-issued | Licensed PE (Professional Engineer) — IL #62-12345, expires 12/31/2025; Bar Admission: NY State Bar #1234567 |
| PROF-022 | Medical license | Medical | MD License #MD-12345 (CA), board certification: Internal Medicine (ABIM #ABCD12345) |
| PROF-023 | CPA / Accounting license | Accounting | CPA Indiana #CP12345, active since 2010, AICPA member |
| PROF-024 | Notary public | Legal admin | Notary Public #NP-12345 (NY), commission expires 2028-03-15 |
| PROF-025 | Bar number / Attorney | Legal | NY State Bar #1234567 (admitted 2015), DC Bar #87654, AAA arbitrator |
| PROF-026 | Real estate license | Property | Real Estate Broker License #REB-12345 (TX), Salesperson License #RES-67890 (FL) |
| PROF-027 | Skills / competencies list | Skill block | "Skills: Python, SQL, PyTorch, TensorFlow, Kubernetes, AWS, machine learning, NLP, statistical analysis" |
| PROF-028 | Programming languages | Tech-specific | Python, Java, C++, JavaScript, Go, Rust, SQL, R, MATLAB, Scala |
| PROF-029 | Frameworks / tools | Tech-specific | React, Django, FastAPI, PyTorch, TensorFlow, Kubernetes, Docker, Terraform, Airflow |
| PROF-030 | Language proficiency | Spoken/written | "Languages: English (native), Spanish (fluent), French (conversational), Hindi (basic)" |
| PROF-031 | Years of experience — total | Career length | "15+ years of experience in software engineering"; "8 years of ML research"; "20 years of healthcare admin" |
| PROF-032 | Years in specific role | Role-specific | "5 years as engineering manager"; "10 years in product management" |
| PROF-033 | Industry experience | Domain | "Fintech: 8 years (Goldman, JPMC); Healthcare: 4 years (UnitedHealth)" |
| PROF-034 | Conference talks / presentations | Speaking | "Speaker at NeurIPS 2023, Strange Loop 2022, KubeCon 2024" |
| PROF-035 | Publications | Authored work | "Published in IEEE WCNC 2026: 'Change-Point Detection in Channel Codes'"; "Co-author on 12 papers" |
| PROF-036 | Patents | Inventions | "Patent #US 11,234,567: 'System for X'"; "3 patents granted, 5 pending"; "Inventor on USPTO patents" |
| PROF-037 | Open source contributions | Modern dev | "Top contributor to project X (500+ commits)"; "Maintainer of PyTorch module"; "GitHub: github.com/jsmith — 1,200 stars" |
| PROF-038 | LinkedIn profile URL | Modern | linkedin.com/in/john-smith-12345 |
| PROF-039 | Personal website | Portfolio | johnsmith.dev, sarahchen.io, mariagarcia.com |
| PROF-040 | GitHub profile | Dev portfolio | github.com/jsmith, github.com/sarahchen |
| PROF-041 | ORCID / academic ID | Researcher | ORCID: 0000-0002-1825-0097, ResearcherID: A-1234-5678 |
| PROF-042 | Google Scholar profile | Academic | Google Scholar: scholar.google.com/citations?user=ABCDEFGH, h-index: 15 |
| PROF-043 | Twitter / X handle for professional | Modern | @jsmith_dev on Twitter, follower count |
| PROF-044 | Awards / honors | Recognition | "MIT 35 Under 35 (2022)"; "Forbes 30 Under 30 (2020)"; "ACM Distinguished Engineer"; "Fortune Most Powerful Women" |
| PROF-045 | Professional society memberships | Affiliation | "IEEE Senior Member"; "ACM member since 2010"; "Member, American Bar Association" |
| PROF-046 | Volunteer / Board positions | Outside | "Board member, Code for America (2022-present)"; "Volunteer mentor, Girls Who Code" |
| PROF-047 | References — prior employer | Vouching | "Reference: Jane Doe, VP Eng at Acme, jane.doe@acme.com, 917-555-0100"; "References available upon request" |
| PROF-048 | Resume bullet — quantified impact | Standard CV | "Reduced infrastructure costs by 35% ($2M annual savings) by migrating to Kubernetes"; "Led team that shipped product to 10M users in 6 months" |
| PROF-049 | Quantified achievements (revenue) | Sales / business | "Closed $5M in new business in 2023"; "Grew customer base by 250% in 2 years" |
| PROF-050 | Promotion velocity | Career trajectory | "Promoted twice in 3 years"; "Fast-tracked to Senior Engineer in 18 months" |
| PROF-051 | Visa / work authorization | Eligibility | "Eligible to work in US (Green Card holder)"; "Requires H-1B sponsorship"; "Authorized in UK and EU" |
| PROF-052 | Background check status | Employment screening | "Background check: passed (2024-03-15)"; "Pending: education verification, criminal background" |
| PROF-053 | Reference check status | Employment | "References checked: 3 of 3 positive; Jane Doe (Acme), Mike Chen (Beta)" |
| PROF-054 | Drug screening | Pre-employment | "Drug screen: negative (2024-03-15)"; "DOT drug test (commercial driver): passed" |
| PROF-055 | Security clearance | Government / defense | "Active TS/SCI clearance (DOD)"; "Secret clearance until 2025"; "DoE Q clearance" |
| PROF-056 | Government / defense work history | Public sector | "DoD employee 2010-2015 (Pentagon)"; "Federal contractor at LLNL 2018-2022" |
| PROF-057 | Internship / co-op experience | Early career | "Internship: Google STEP 2018"; "Co-op: Boeing 2016-2017 (3 rotations)" |
| PROF-058 | Bootcamp / non-traditional education | Modern | "App Academy 2019 (16-week bootcamp)"; "Lambda School / BloomTech 2020"; "General Assembly UX 2018" |
| PROF-059 | Self-taught / non-degree | Path | "Self-taught Python and ML from online courses, GitHub portfolio"; "Career changer from teaching to software dev" |
| PROF-060 | Professional in JSON | Structured | "title": "Senior Engineer", "company": "Acme", "tenure_years": 5, "skills": ["Python", "ML"] |
| PROF-061 | Professional in KV | Form field | title=Senior Engineer, COMPANY: Acme, TENURE: 5 years |
| PROF-062 | Professional in XML | Markup | <employment><title>Senior Engineer</title><company>Acme</company><tenure>5y</tenure></employment> |
| PROF-063 | Professional in CSV | Tabular | "Smith","John","E12345","Senior Engineer","Acme","2020-06-01" |
| PROF-064 | Multilingual context label | Various | Experience (EN), Expérience professionnelle (FR), Berufserfahrung (DE), Experiencia profesional (ES), Esperienza (IT), Experiência (PT), 職歴 (JP), 경력 (KR), 工作经历 (ZH), Опыт работы (RU), İş Tecrübesi (TR), خبرة مهنية (AR), ניסיון תעסוקתי (HE), ประสบการณ์ทำงาน (TH) |
| PROF-065 | OCR-distorted background | Char substitution | "Senlor Englneer" (l for i), "Acmé Corp" (lost a), "Englneer" (l for i); "Stanf0rd" (0 for o) |
| PROF-066 | Masked / partial background | Privacy-redacted | "Senior Engineer at [REDACTED]"; "Worked at *** for 5 years"; "Education: ***" |
| PROF-067 | Anonymized placeholder | Standard generic | "Title: [TITLE]"; "Company: Example Corp"; "John Doe, Senior Manager (placeholder)" |
| PROF-068 | Sentence-boundary tricky | Trailing punctuation | "He's a Senior Engineer at Acme.", "Was she a VP at Beta?", "Joined Stanford in 2015!" |
| PROF-069 | Adjacency-tight | No separator | "JohnSmithSeniorEngineerAcme2020", "MariaGarcíaMBAHarvard2018" |
| PROF-070 | Sabbatical / extended leave noted | Career pause | "Sabbatical 2022 (6 months) — traveled internationally"; "Career break 2019-2020 for caregiving" |
| PROF-071 | Boomerang employee | Returning hire | "Rejoined Acme in 2023 after 2 years at Beta"; "Boomerang: returned to original role 2024" |
| PROF-072 | Internal transfer | Internal move | "Internal transfer from Acme NYC to Acme London (2022)"; "Lateral move from Eng to PM (2021)" |
| PROF-073 | Acquisition / merger work history | Corporate change | "Joined Beta Inc 2018, became Acme Corp employee via acquisition Q3 2020" |
| PROF-074 | Startup founding history | Founder | "Co-founder of Beta Inc 2015 (acquired by Acme 2020); served as CTO" |
| PROF-075 | Industry transition | Career pivot | "Pivoted from Finance to Tech in 2018 (took bootcamp + 1 year internship)" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | PROF-065 |
| Masked / partial / redacted | ✓ | PROF-066, PROF-067 |
| Multilingual context labels | ✓ | PROF-064 |
| Career data type coverage | ✓ | PROF-001 to PROF-012 (titles, dates, duties, gaps, transitions) |
| Education coverage | ✓ | PROF-013 to PROF-019 (degree, institution, year, GPA, major, thesis, MOOC) |
| Certifications / licenses | ✓ | PROF-020 to PROF-026 (industry certs, PE, bar, medical, CPA, notary, real estate) |
| Skills / language | ✓ | PROF-027 to PROF-030 |
| Achievements / quantified | ✓ | PROF-031 to PROF-036, PROF-044, PROF-048, PROF-049 |
| Online identity / portfolio | ✓ | PROF-038 to PROF-043 |
| Background / clearance screening | ✓ | PROF-051 to PROF-056 |
| In structured data | ✓ | PROF-060, PROF-061, PROF-062, PROF-063 |
| Adjacency-tight | ✓ | PROF-069 |
| Sentence-boundary tricky | ✓ | PROF-068 |
| Non-traditional career path | ✓ | PROF-057, PROF-058, PROF-059, PROF-074, PROF-075 |
| Career events (sabbatical/boomerang/acquisition) | ✓ | PROF-070, PROF-071, PROF-072, PROF-073 |
| References & social proof | ✓ | PROF-045, PROF-046, PROF-047 |

**Total patterns for Professional_Background: 75**

---

## Entity 41: Crime

Criminal history, arrests, convictions, charges. GDPR Article 10 data. Heavily regulated for background checks.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| CRIME-001 | Criminal conviction — general | Status | Convicted of theft (2018), Conviction: assault, Criminal record: yes |
| CRIME-002 | Felony — general | Severity | Felony conviction, Felon, Class A Felony, Class 1 Felony, Felony probation |
| CRIME-003 | Misdemeanor — general | Severity | Misdemeanor, Class B Misdemeanor, Petty offense, Summary offense (UK) |
| CRIME-004 | Infraction / violation | Minor | Infraction, Civil infraction, Citation, Ordinance violation |
| CRIME-005 | Theft — specific | Property crime | Theft, Petty theft (under $950 CA), Grand theft (over $950 CA), Grand larceny (NY) |
| CRIME-006 | Burglary | Property crime | Burglary, Breaking and entering, Home invasion, B&E |
| CRIME-007 | Robbery | Violent property | Robbery, Armed robbery, Strong-arm robbery, Carjacking |
| CRIME-008 | Assault | Violent | Assault, Aggravated assault, Simple assault, ABH (UK), GBH (UK) |
| CRIME-009 | Battery | Violent | Battery, Aggravated battery, Domestic battery |
| CRIME-010 | Homicide / Murder | Most serious | Murder (1st degree), Murder (2nd degree), Manslaughter (voluntary), Manslaughter (involuntary), Vehicular manslaughter, Capital murder |
| CRIME-011 | Sexual offense | Sex crime | Sexual assault, Rape, Statutory rape, Sexual battery, Lewd conduct |
| CRIME-012 | Sex offender registration | Registry | Registered sex offender, Tier I/II/III offender (US), SOR registrant, Megan's Law listing |
| CRIME-013 | DUI / DWI | Driving under influence | DUI (1st offense), DWI, OWI, OUI, BAC 0.18 at arrest, DUI with injury |
| CRIME-014 | DUI — aggravated | Severe DUI | Aggravated DUI, Felony DUI, DUI manslaughter, 3rd DUI in 10 years |
| CRIME-015 | Drug possession | Drug crime | Possession of marijuana (under 1oz), Possession of cocaine, Possession with intent to distribute |
| CRIME-016 | Drug distribution / trafficking | Drug crime | Drug trafficking, Drug distribution, Drug dealing, Conspiracy to distribute |
| CRIME-017 | Drug manufacturing | Drug crime | Manufacturing methamphetamine, Drug cultivation (marijuana), Operating a drug lab |
| CRIME-018 | Fraud — general | White-collar | Fraud, Wire fraud, Mail fraud, Bank fraud, Tax fraud, Securities fraud |
| CRIME-019 | Identity theft | White-collar | Identity theft, Aggravated identity theft, ID theft conviction |
| CRIME-020 | Embezzlement | White-collar | Embezzlement, Conversion, Larceny by employee |
| CRIME-021 | Money laundering | White-collar | Money laundering, Structuring, Bulk cash smuggling |
| CRIME-022 | Insider trading | White-collar | Insider trading, Securities violation (SEC), Tippee liability |
| CRIME-023 | Tax evasion | White-collar | Tax evasion, Failure to file, Tax fraud, IRS conviction |
| CRIME-024 | Cybercrime | Modern | Computer fraud, CFAA violation, Hacking, Unauthorized access, Cyberstalking |
| CRIME-025 | Domestic violence | Family | Domestic violence, DV, IPV (Intimate Partner Violence), Spousal abuse |
| CRIME-026 | Child abuse | Child welfare | Child abuse, Child endangerment, Child neglect, CPS-substantiated |
| CRIME-027 | Child pornography | Sex crime | Possession of child pornography, CSAM possession, Distribution of CSAM |
| CRIME-028 | Stalking | Harassment | Stalking, Aggravated stalking, Cyberstalking conviction |
| CRIME-029 | Harassment | Lesser | Harassment, Criminal harassment, Telephone harassment |
| CRIME-030 | Trespassing | Property | Trespassing, Criminal trespass, Defiant trespass |
| CRIME-031 | Vandalism | Property | Vandalism, Malicious mischief, Criminal mischief, Graffiti conviction |
| CRIME-032 | Arson | Property/violent | Arson, Arson (1st degree), Reckless burning, Insurance arson |
| CRIME-033 | Weapons offense | Weapons | Illegal possession of firearm, Felon in possession, Carrying concealed without permit, Brandishing |
| CRIME-034 | Gun violence | Firearms | Discharge of firearm, Aggravated assault with firearm, Drive-by shooting |
| CRIME-035 | Terrorism / extremism | National security | Terrorism conspiracy, Material support for terrorism, Domestic terrorism charges |
| CRIME-036 | Kidnapping | Violent | Kidnapping, Unlawful imprisonment, False imprisonment, Custodial interference |
| CRIME-037 | Human trafficking | Severe | Human trafficking, Sex trafficking, Labor trafficking, Smuggling |
| CRIME-038 | Hate crime | Bias-motivated | Hate crime enhancement, Racially motivated assault, Religious bias crime |
| CRIME-039 | Resisting arrest | Police-related | Resisting arrest, Obstruction of justice, Eluding police |
| CRIME-040 | Disorderly conduct | Public order | Disorderly conduct, Public intoxication, Drunk and disorderly |
| CRIME-041 | Prostitution / solicitation | Vice | Prostitution, Solicitation, Pimping, Pandering |
| CRIME-042 | Pending charges | Status | Pending charges, Awaiting trial, Charged but not convicted, Indicted (federal grand jury) |
| CRIME-043 | Arrest record (no conviction) | Police record | Arrested 2020-03-15, Arrest record (charges dropped), Booked but not charged |
| CRIME-044 | Acquittal | Outcome | Acquitted at trial, Not guilty verdict, Found not guilty |
| CRIME-045 | Dismissed charges | Outcome | Charges dismissed, Dismissed with prejudice, Nolle prosequi |
| CRIME-046 | Plea bargain | Outcome | Pled guilty to lesser charge, Plea deal: reduced to misdemeanor, No contest plea |
| CRIME-047 | Nolo contendere | Plea type | Nolo contendere (no contest), Plea of nolo |
| CRIME-048 | Conviction outcome — probation | Sentence | Sentenced to 3 years probation, Supervised probation, Unsupervised probation |
| CRIME-049 | Conviction outcome — fine | Sentence | Fined $5,000, Court costs $1,200, Restitution $25,000 |
| CRIME-050 | Conviction outcome — community service | Sentence | 200 hours community service, Community service in lieu of jail |
| CRIME-051 | Conviction outcome — jail / prison | Sentence | Sentenced to 18 months in county jail, 5 years state prison, 10 years federal prison |
| CRIME-052 | Conviction — concurrent sentences | Sentence | Concurrent sentences (3 years each, running together), Consecutive sentences |
| CRIME-053 | Conviction — suspended sentence | Sentence | Suspended sentence (5 years), Conditional discharge |
| CRIME-054 | Conviction — death penalty | Sentence | Sentenced to death, Death row, Capital punishment |
| CRIME-055 | Parole status | Post-conviction | On parole until 2026-03-15, Parole eligible 2024, Parolee, Parole officer: J. Davis |
| CRIME-056 | Probation status | Post-conviction | On probation, Probation officer assigned, Probation violation hearing |
| CRIME-057 | Probation violation | Status | Probation violation 2024-03-15, VOP, Revoked probation |
| CRIME-058 | Court case number | Case ID | Case No.: CR-2020-001234, Case #: 2020-CF-12345, Indictment #: 20-CR-12345 |
| CRIME-059 | Court name / jurisdiction | Court | US District Court Eastern District of Texas, Cook County Circuit Court, NY Supreme Court |
| CRIME-060 | Judge name | Court | Judge: Hon. Sarah Chen, Honorable John Smith, Magistrate Judge |
| CRIME-061 | Prosecutor / DA | Court | DA Maria García, US Attorney's Office for SDNY, Crown Prosecution Service (UK) |
| CRIME-062 | Defense attorney | Court | Defense: John Doe, Esq., Public defender assigned, Pro se (self-represented) |
| CRIME-063 | Bail / bond | Pre-trial | Bail set at $50,000, Released on $10,000 bond, ROR (Released on Recognizance), Bail denied |
| CRIME-064 | Bond conditions | Pre-trial | Conditions: no contact with victim, surrender passport, electronic monitoring (ankle bracelet) |
| CRIME-065 | Bench warrant | Failure to appear | Bench warrant issued for FTA, Outstanding warrant, Active warrant |
| CRIME-066 | Restraining order / protective order | Civil-criminal | Restraining order against [name], TRO (Temporary Restraining Order), Order of Protection, NCO (No Contact Order) |
| CRIME-067 | Civil protection order | Family law | DV protective order, Civil protection order, Stalking protection order |
| CRIME-068 | Juvenile record | Minor | Juvenile adjudication (not conviction), Juvenile court record sealed at 18, Youthful Offender (NY) |
| CRIME-069 | Expunged / sealed record | Cleared | Expunged 2020, Record sealed under 18 USC § XXX, Set-aside conviction, Pardon granted |
| CRIME-070 | Pardon | Executive clemency | Pardoned by governor 2022, Presidential pardon, Conditional pardon |
| CRIME-071 | Commutation | Sentence reduction | Sentence commuted from 20 years to 10, Commutation granted |
| CRIME-072 | Foreign criminal record | International | INTERPOL Red Notice, Foreign conviction (UK, theft, 2015), International background check result |
| CRIME-073 | Background check report | Pre-employment | Background check: 1 misdemeanor (2018), Pre-employment screening: clean, Criminal history report |
| CRIME-074 | Court date | Schedule | Hearing: 2024-04-15 9:00 AM, Trial date: 2024-06-01, Arraignment: 2024-03-22 |
| CRIME-075 | Sentencing date | Schedule | Sentencing: 2024-09-15, Pre-sentence report due 2024-08-15 |
| CRIME-076 | Booking number | Police | Booking #: B-2020-001234, Booking number: 87654321 |
| CRIME-077 | Mugshot reference | Police | Mugshot taken 2020-03-15, Police photo on file |
| CRIME-078 | NCIC / FBI ID | Federal | NCIC #: 1234567890 (National Crime Information Center), FBI Number: 123A45B6 |
| CRIME-079 | State ID — criminal | State CHRI | State ID: CA-12345678 (Criminal History Record Information) |
| CRIME-080 | DOC inmate number | Correctional | Inmate #: A12345 (CA DOC), Federal Inmate Reg #: 12345-678 (BOP) |
| CRIME-081 | Traffic violation | Lesser | Speeding ticket, Reckless driving (criminal in some states), Hit and run, Driving without license |
| CRIME-082 | Civil judgment | Civil not criminal | Civil judgment against, Default judgment, Settled out of court, Wage garnishment order |
| CRIME-083 | Bankruptcy filing | Civil financial | Chapter 7 bankruptcy filed 2020, Chapter 13 bankruptcy, Discharged in bankruptcy |
| CRIME-084 | Crime in JSON | Structured | "criminal_history": {"convictions": [{"crime": "theft", "year": 2018, "outcome": "probation"}]} |
| CRIME-085 | Crime in KV | Form field | conviction=theft, FELONY: yes, PROBATION: active |
| CRIME-086 | Crime in XML | Markup | <conviction><type>theft</type><year>2018</year></conviction>, <criminal_record>yes</criminal_record> |
| CRIME-087 | Crime in CSV | Tabular | "Smith","John","E12345","Theft","2018","Probation" |
| CRIME-088 | Multilingual context label | Various | Criminal Record (EN), Casier judiciaire (FR), Vorstrafen (DE), Antecedentes penales (ES), Casellario giudiziale (IT), Antecedentes criminais (PT), 犯罪歴 (JP), 전과 (KR), 犯罪记录 (ZH), Судимость (RU), Sabıka kaydı (TR), سجل جنائي (AR), עבר פלילי (HE), ประวัติอาชญากรรม (TH) |
| CRIME-089 | OCR-distorted crime | Char substitution | Convlcted (l for i), Feiony (i for l, l for o), TheFt (F for f), Asault (lost s) |
| CRIME-090 | Masked / partial criminal record | Privacy-redacted | Crime: [REDACTED], Conviction: ***, Charges: [PRIVATE] |
| CRIME-091 | Anonymized placeholder | Standard generic | Criminal record: [NONE/REDACTED], Conviction: <CHARGE>, [SEALED] |
| CRIME-092 | Sentence-boundary tricky | Trailing punctuation | "He was convicted of theft.", "Was the charge DUI?", "Felony record!" |
| CRIME-093 | Adjacency-tight | No separator | "JohnSmithCR-2020-001234Theft", "MariaGarcíaFelonyDUI2018" |
| CRIME-094 | International crime variations | Country-specific | "Indictable offence" (UK), "Summary conviction" (CA), "Délit/Crime" (FR), "Vergehen/Verbrechen" (DE), "Felonia" (ES) |
| CRIME-095 | Specific drug schedules | Controlled subs | Schedule I drug (heroin), Schedule II (cocaine, methamphetamine), Schedule III (anabolic steroids) |
| CRIME-096 | RICO charges | Federal | RICO Act violation, Racketeering charges, Conspiracy under RICO |
| CRIME-097 | Federal vs state distinction | Jurisdiction | Federal conviction (transported across state lines), State court conviction (CA Superior Court) |
| CRIME-098 | Recidivism / repeat offender | Career criminal | Repeat offender, Three strikes (CA), Habitual offender enhancement |
| CRIME-099 | Awaiting deportation | Immigration-criminal | Deportation hearing pending after conviction, ICE detainer issued |
| CRIME-100 | Asylum-bar crime | Immigration | Aggravated felony (immigration), Crime involving moral turpitude (CIMT), Particularly serious crime |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | CRIME-089 |
| Masked / partial / redacted | ✓ | CRIME-090, CRIME-091 |
| Multilingual context labels | ✓ | CRIME-088 |
| Crime category coverage | ✓ | CRIME-005 to CRIME-041 (theft, burglary, robbery, assault, homicide, sex crime, DUI, drug, fraud, identity theft, embezzlement, money laundering, insider trading, tax evasion, cybercrime, DV, child abuse, child porn, stalking, vandalism, arson, weapons, terrorism, kidnapping, trafficking, hate crime, resisting arrest, disorderly conduct, prostitution) |
| Severity tiers | ✓ | CRIME-002 (felony), CRIME-003 (misdemeanor), CRIME-004 (infraction) |
| Case lifecycle | ✓ | CRIME-042 (pending), CRIME-043 (arrest no conviction), CRIME-044 (acquittal), CRIME-045 (dismissed), CRIME-046 (plea), CRIME-047 (nolo) |
| Sentence types | ✓ | CRIME-048 to CRIME-054 (probation, fine, community service, jail, concurrent/consecutive, suspended, death) |
| Post-conviction status | ✓ | CRIME-055 (parole), CRIME-056 (probation), CRIME-057 (VOP), CRIME-065 (bench warrant) |
| In structured data | ✓ | CRIME-084, CRIME-085, CRIME-086, CRIME-087 |
| Adjacency-tight | ✓ | CRIME-093 |
| Sentence-boundary tricky | ✓ | CRIME-092 |
| Identifiers (case #, NCIC, DOC, booking) | ✓ | CRIME-058, CRIME-076, CRIME-078, CRIME-079, CRIME-080 |
| Privacy / sealed / expunged | ✓ | CRIME-068, CRIME-069, CRIME-070, CRIME-071 |
| Court actors (judge, DA, defense) | ✓ | CRIME-060, CRIME-061, CRIME-062 |
| Immigration-criminal | ✓ | CRIME-099, CRIME-100 |
| International / jurisdictional | ✓ | CRIME-072, CRIME-094, CRIME-097 |

**Total patterns for Crime: 100**

---

## Entity 42: PEP_Status

Politically Exposed Person status (AML/KYC sensitive data — FATF Recommendations). High risk for banks, broker-dealers, real estate, and other regulated entities.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PEP-001 | PEP flag — yes/no | Binary | PEP: Yes, PEP Status: No, Is PEP: True, PEP Flag: Y |
| PEP-002 | PEP flag — risk level | Tier | PEP Risk: High, PEP Risk: Medium, PEP Risk: Low, PEP-1 (highest risk) |
| PEP-003 | Domestic PEP (DPEP) | Same-country PEP | DPEP, Domestic PEP, PEP Type: Domestic, Resident PEP |
| PEP-004 | Foreign PEP (FPEP) | Foreign government | FPEP, Foreign PEP, Foreign Senior Political Figure (FSPF, US OCC term) |
| PEP-005 | International Organization PEP (IO PEP) | UN, World Bank, etc. | IO PEP, International Org PEP, UN PEP, WHO senior official |
| PEP-006 | Head of State / Government | Highest tier | President, Prime Minister, Chancellor, Head of Government, Head of State |
| PEP-007 | Cabinet Minister | Executive branch | Minister of Finance, Cabinet Secretary, Secretary of State, Foreign Minister |
| PEP-008 | Senior politician | Legislative | Senator, MP, Member of Parliament, Congressman, Congresswoman, Bundestagsabgeordneter |
| PEP-009 | Military senior officer | Defense | General, Lieutenant General, Admiral, Chief of Staff, Joint Chiefs |
| PEP-010 | Senior judiciary | Judicial | Supreme Court Justice, Chief Justice, High Court Judge, Federal Judge |
| PEP-011 | Senior law enforcement | Police | Chief of Police (major city), Commissioner of Police, FBI Director, Attorney General |
| PEP-012 | Central bank / regulatory | Financial regulators | Central Bank Governor, Fed Chair, SEC Chair, FCA CEO, BoE Governor |
| PEP-013 | Ambassador / diplomat | Foreign service | Ambassador, Consul General, Diplomatic Mission Chief, Chargé d'Affaires |
| PEP-014 | State-owned enterprise (SOE) senior | SOE leadership | CEO of state oil company, Chairman of national airline (state-owned), SOE board member |
| PEP-015 | Political party — senior | Party leadership | Party Chairman, Party Leader, General Secretary, National Committee Chair |
| PEP-016 | Royalty / royal family | Monarchy | Royal family member, Crown Prince, Princess, Member of [royal family name] |
| PEP-017 | Family member of PEP (immediate) | RCA spouse/child/parent | Spouse of PEP, Child of PEP, Parent of PEP, Sibling of PEP, Family member of PEP |
| PEP-018 | Close associate of PEP (RCA) | Business partner | Business partner of PEP, Close associate, RCA (Relative or Close Associate), known associate |
| PEP-019 | Specific spouse PEP | Named | "Spouse of Minister Smith"; "Wife of Senator Jones"; "Husband of Ambassador Chen" |
| PEP-020 | Specific child PEP | Named | "Son of President X"; "Daughter of PM Y"; "Adult child of PEP" |
| PEP-021 | PEP — former / Ex-PEP | No longer in role | Former PEP, Ex-PEP (5 years since leaving office), Lapsed PEP |
| PEP-022 | PEP — active | Currently in role | Currently active PEP, PEP in office, Sitting PEP |
| PEP-023 | PEP screening result | Match | PEP screening: Match Found, PEP Hit, PEP Match Confirmed, PEP Adverse Media Found |
| PEP-024 | PEP screening — no match | Clear | PEP Screen: No Match, Clear of PEP, Negative PEP Result |
| PEP-025 | PEP screening — possible match | Manual review | PEP Possible Match — Manual Review Required, Fuzzy Match Score: 0.85 |
| PEP-026 | OFAC / SDN screening | US sanctions | OFAC SDN List Match, SDN: Specially Designated National, OFAC Hit |
| PEP-027 | UN Sanctions List | UN | UN Sanctions List Match, UN 1267 (terror) list, UN Security Council Sanctions |
| PEP-028 | EU Sanctions List | EU | EU Consolidated List Match, EU Restrictive Measures, EU CFSP sanctions |
| PEP-029 | UK Sanctions List (OFSI) | UK | UK HM Treasury OFSI Match, UK Consolidated List, UK Asset Freeze |
| PEP-030 | HMT (UK Treasury) — discontinued | Legacy | HMT Match (legacy term, now OFSI) |
| PEP-031 | Interpol Notices | Law enforcement | INTERPOL Red Notice, Yellow Notice (missing), Blue Notice (info request) |
| PEP-032 | Watchlist match — generic | Multi-list | Watchlist Match: 3 lists (OFAC, UN, EU), Adverse Media Match |
| PEP-033 | Adverse media | News-based | Adverse media: 2 articles regarding corruption allegations 2022, Negative news search positive |
| PEP-034 | KYC — enhanced due diligence (EDD) | Process | EDD required (PEP status); Enhanced Due Diligence completed 2024-03-15 |
| PEP-035 | Source of wealth (SOW) | KYC inquiry | Source of Wealth: Inheritance (50%), Business income (35%), Investment (15%) — required for PEP |
| PEP-036 | Source of funds (SOF) | KYC inquiry | Source of Funds for this transaction: Salary, Sale of property, etc. |
| PEP-037 | PEP review frequency | Ongoing monitoring | Reviewed: Annual (PEP requires annual review), Last reviewed: 2024-03-15, Next review: 2025-03-15 |
| PEP-038 | PEP designation date | When flagged | Flagged as PEP: 2020-06-15 (assumed office); De-listed: TBD |
| PEP-039 | PEP-related transaction flag | Alert | Transaction Alert: PEP wire transfer $250,000, manual review required |
| PEP-040 | PEP exit / cooling-off period | Post-PEP | Cooling-off period: 12 months after leaving office (jurisdiction-specific); 5-year monitoring per some regulators |
| PEP-041 | PEP-by-country list | Geographic | High-Risk Jurisdiction: Russia, Belarus, Iran, North Korea, Sudan — FATF grey/black list |
| PEP-042 | Senior management of SOE — international | SOE specific | Senior Mgmt of SOE: CNPC (China), Gazprom (Russia), Saudi Aramco (Saudi Arabia), PetroBras (Brazil) |
| PEP-043 | Tribal nation leadership | Indigenous government | Tribal Chairman (Cherokee Nation), Tribal Council Member, Native American government leader (may be PEP per some standards) |
| PEP-044 | Subnational PEP (governor, mayor) | Sub-national | Governor of California, Mayor of London, Major-city mayor (may be PEP per jurisdiction) |
| PEP-045 | PEP — local politicians | Below national | Local council member (typically not PEP unless senior), Local PEP per some standards |
| PEP-046 | UNODC Sanctions / Watchlist | UN crime office | UN Office on Drugs and Crime watchlist match |
| PEP-047 | World Bank Debarment | Multilateral | World Bank Debarred Firms list, IFC Debarment List |
| PEP-048 | Multilingual context label | Various | PEP (universal abbreviation), Personne politiquement exposée (FR), Politisch exponierte Person (DE), Persona políticamente expuesta (ES), Persona politicamente esposta (IT), Pessoa Politicamente Exposta (PT), 政治的に重要な公的地位を有する者 (JP), 정치적 주요인물 (KR), 政治公众人物 (ZH), Публичное должностное лицо (RU), Siyasi Nüfuz Sahibi (TR), شخصية سياسية مكشوفة (AR) |
| PEP-049 | PEP in JSON | Structured | "pep_status": true, "pep_type": "Domestic", "pep_role": "Senator", "sanctions_hit": false |
| PEP-050 | PEP in KV | Form field | pep=YES, PEP_RISK: High, PEP_TYPE: FPEP |
| PEP-051 | PEP in XML | Markup | <pep_status>true</pep_status>, <pep_type>FPEP</pep_type>, <sanctions_list>OFAC SDN</sanctions_list> |
| PEP-052 | PEP in CSV | Tabular | "Smith","John","E12345","PEP","Domestic","High","2020-06-15" |
| PEP-053 | OCR-distorted PEP | Char substitution | PFP (lost E), P3P (3 for E), SD/N (slash inserted), 0FAC (0 for O) |
| PEP-054 | Masked / partial PEP | Privacy-redacted | PEP Status: [REDACTED], Sanctions: ***, PEP role: [PRIVATE] |
| PEP-055 | Anonymized placeholder | Standard generic | PEP: <STATUS>, Sanctions Hit: NO, PEP Role: [REDACTED] |
| PEP-056 | Sentence-boundary tricky | Trailing punctuation | "He is a PEP.", "Is she on the SDN list?", "PEP screening positive!" |
| PEP-057 | Adjacency-tight | No separator | "JohnSmithSenatorPEP", "MariaGarcíaSDNHitOFAC" |
| PEP-058 | Specific PEP role examples (international) | Comparable roles | "Minister-equivalent role: Bundesminister (DE), Ministro (ES/IT/PT), Министр (RU), 大臣 (JP), 장관 (KR)" |
| PEP-059 | PEP disclosure form (self-declaration) | KYC form | "PEP Self-Declaration Form: I, [name], do/do not have PEP status as of [date]" |
| PEP-060 | Friend or business associate flag | RCA expansion | "Known associate of PEP: business partner in joint venture 2018-2022" |
| PEP-061 | PEP escalation level | Bank-specific | "PEP Tier 1 (CEO approval required)", "PEP Tier 2 (Compliance Officer approval)", "PEP Tier 3 (relationship manager approval)" |
| PEP-062 | Senior Foreign Political Figure (SFPF) | US specific (USA PATRIOT Act § 312) | SFPF designation, Senior Foreign Political Figure under USA PATRIOT Act |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | PEP-053 |
| Masked / partial / redacted | ✓ | PEP-054, PEP-055 |
| Multilingual context labels | ✓ | PEP-048 |
| PEP type coverage | ✓ | PEP-003 (Domestic), PEP-004 (Foreign), PEP-005 (International Org) |
| Role coverage | ✓ | PEP-006 to PEP-016 (Head of State, Minister, Senator, Military, Judicial, Police, Central Bank, Ambassador, SOE, Party, Royal) |
| Family / associate (RCA) | ✓ | PEP-017, PEP-018, PEP-019, PEP-020 |
| Sanctions list coverage | ✓ | PEP-026 (OFAC SDN), PEP-027 (UN), PEP-028 (EU), PEP-029 (UK OFSI), PEP-030 (HMT legacy), PEP-031 (Interpol), PEP-046 (UNODC), PEP-047 (World Bank) |
| Screening lifecycle | ✓ | PEP-023 (match), PEP-024 (no match), PEP-025 (possible), PEP-032 (multi-list), PEP-033 (adverse media) |
| KYC / EDD process | ✓ | PEP-034, PEP-035, PEP-036, PEP-037 |
| Time lifecycle | ✓ | PEP-021 (former), PEP-022 (active), PEP-038 (designation date), PEP-040 (cooling-off) |
| In structured data | ✓ | PEP-049, PEP-050, PEP-051, PEP-052 |
| Adjacency-tight | ✓ | PEP-057 |
| Sentence-boundary tricky | ✓ | PEP-056 |
| US-specific (SFPF) | ✓ | PEP-062 |
| Risk-tiered escalation | ✓ | PEP-061 |
| Indigenous / tribal | ✓ | PEP-043 |

**Total patterns for PEP_Status: 62**

---

## Entity 43: Trade_Union_Membership

Union membership data. GDPR Article 9 (special category). Subject to anti-discrimination protections.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| TUM-001 | Union member — yes/no | Status | Union member: Yes, Trade Union: No, Union Status: Active member |
| TUM-002 | Union name — US AFL-CIO affiliates | US labor federations | AFL-CIO, AFL-CIO affiliated union, Member of AFL-CIO union |
| TUM-003 | UAW — United Auto Workers | US industry | UAW (United Auto Workers), UAW Local 235, UAW member |
| TUM-004 | Teamsters | US transport | International Brotherhood of Teamsters, IBT, Teamsters Local 75, Teamsters member |
| TUM-005 | SEIU — Service Employees | US service | SEIU (Service Employees International Union), SEIU Local 1199, SEIU healthcare workers |
| TUM-006 | IBEW — Electrical Workers | US trade | IBEW (International Brotherhood of Electrical Workers), IBEW Local 3, Journeyman electrician |
| TUM-007 | UFCW — Food and Commercial Workers | US retail | UFCW, United Food and Commercial Workers, UFCW Local 1500 (NY supermarkets) |
| TUM-008 | AFSCME — Public employees | US public | AFSCME, American Federation of State, County, and Municipal Employees |
| TUM-009 | NEA — Teachers | US education | NEA (National Education Association), AFT (American Federation of Teachers), teachers union |
| TUM-010 | AFT — Teachers | US education | AFT, American Federation of Teachers, UFT (NYC United Federation of Teachers) |
| TUM-011 | USW — Steelworkers | US industry | USW (United Steelworkers), USW Local 1011 |
| TUM-012 | Communications Workers — CWA | US comms | CWA (Communications Workers of America), CWA Local 1101 (NYC), Verizon CWA |
| TUM-013 | ILWU — Longshore | US west coast ports | ILWU (International Longshore and Warehouse Union), Local 10 (SF) |
| TUM-014 | ILA — East coast longshoremen | US east coast ports | ILA (International Longshoremen's Association), ILA Local 1814 |
| TUM-015 | SAG-AFTRA — Entertainment | US film/TV | SAG-AFTRA (Screen Actors Guild — American Federation of Television and Radio Artists), SAG card |
| TUM-016 | WGA — Writers Guild | US film/TV | WGA East/West (Writers Guild of America), WGA East member, WGA West member |
| TUM-017 | DGA — Directors Guild | US film/TV | DGA (Directors Guild of America), DGA member, DGA card |
| TUM-018 | Police union | US law enforcement | PBA (Police Benevolent Association), FOP (Fraternal Order of Police), Police union member |
| TUM-019 | Firefighters union | US public safety | IAFF (International Association of Fire Fighters), Local 94 |
| TUM-020 | UK TUC | UK federation | TUC (Trades Union Congress), TUC-affiliated union |
| TUM-021 | UK Unite the Union | UK general | Unite the Union, Unite member, Unite Local 123 |
| TUM-022 | UK UNISON | UK public sector | UNISON, UNISON member, UNISON public service union |
| TUM-023 | UK GMB | UK general | GMB Union, GMB General Workers, GMB member |
| TUM-024 | UK NEU — Teachers | UK education | NEU (National Education Union, formed 2017 from NUT + ATL) |
| TUM-025 | UK BMA — Doctors | UK medical | BMA (British Medical Association), BMA member |
| TUM-026 | UK Royal College of Nursing | UK nursing | RCN (Royal College of Nursing), RCN member |
| TUM-027 | DE DGB | German federation | DGB (Deutscher Gewerkschaftsbund), DGB-affiliated union |
| TUM-028 | DE IG Metall | German industry | IG Metall (Industriegewerkschaft Metall), largest in Europe, IG Metall Mitglied |
| TUM-029 | DE ver.di | German services | ver.di (Vereinte Dienstleistungsgewerkschaft), ver.di member |
| TUM-030 | DE GEW — Teachers | German education | GEW (Gewerkschaft Erziehung und Wissenschaft) |
| TUM-031 | FR CGT | French union | CGT (Confédération Générale du Travail), CGT-FO, syndiqué CGT |
| TUM-032 | FR CFDT | French union | CFDT (Confédération Française Démocratique du Travail), CFDT membre |
| TUM-033 | FR FO — Force Ouvrière | French union | Force Ouvrière, FO, FO syndicat |
| TUM-034 | FR Sud / Solidaires | French union | Solidaires, SUD (Solidaires Unitaires Démocratiques) |
| TUM-035 | IT CGIL | Italian union | CGIL (Confederazione Generale Italiana del Lavoro), iscritto CGIL |
| TUM-036 | IT CISL | Italian union | CISL (Confederazione Italiana Sindacati Lavoratori) |
| TUM-037 | IT UIL | Italian union | UIL (Unione Italiana del Lavoro) |
| TUM-038 | ES UGT / CCOO | Spanish unions | UGT (Unión General de Trabajadores), CCOO (Comisiones Obreras), CGT-E, USO |
| TUM-039 | NL FNV | Dutch union | FNV (Federatie Nederlandse Vakbeweging), CNV |
| TUM-040 | SE LO / TCO | Swedish union | LO (Landsorganisationen i Sverige), TCO (Tjänstemännens Centralorganisation), SACO |
| TUM-041 | NO LO Norway | Norwegian union | LO (Landsorganisasjonen i Norge), Fagforbundet |
| TUM-042 | DK LO / FH | Danish union | FH (Fagbevægelsens Hovedorganisation, formed from LO + FTF), 3F |
| TUM-043 | JP Rengo | Japanese union | Rengo (連合, Japanese Trade Union Confederation), 全労連 (Zenroren) |
| TUM-044 | KR KCTU / FKTU | Korean unions | KCTU (Korean Confederation of Trade Unions, 민주노총), FKTU (한국노총) |
| TUM-045 | AU ACTU | Australian union | ACTU (Australian Council of Trade Unions), Australian Workers' Union, CFMEU |
| TUM-046 | CA CLC | Canadian union | CLC (Canadian Labour Congress), CUPE (Canadian Union of Public Employees), Unifor |
| TUM-047 | BR CUT / Força Sindical | Brazilian union | CUT (Central Única dos Trabalhadores), Força Sindical |
| TUM-048 | International — IndustriALL | Global | IndustriALL Global Union, ITUC (International Trade Union Confederation) |
| TUM-049 | International — ITF | Transport | ITF (International Transport Workers' Federation), Maritime sector |
| TUM-050 | Union member ID | Identifier | Union Member #: 12345, UAW Card #: 67890, Member ID: U-12345 |
| TUM-051 | Union local number | Local chapter | Local 75 (Teamsters NYC), IBEW Local 3, SEIU Local 1199, UAW Local 235 |
| TUM-052 | Shop steward / delegate | Workplace rep | Shop Steward, Union Steward, Union Delegate, Shop Floor Rep |
| TUM-053 | Member in good standing | Status | Member in Good Standing, Dues current, Active member, Member good standing through 12/31/2024 |
| TUM-054 | Dues paying status | Financial | Dues paid: $XXX/quarter, Dues check-off, Auto-pay dues, Behind on dues |
| TUM-055 | Union dues deduction | Payroll | Union dues deducted from pay: $50/month, Payroll deduction code: UD |
| TUM-056 | Collective Bargaining Agreement (CBA) | Contract | Covered by CBA, Article 12 of CBA, CBA expiration 2025-12-31, CBA negotiated |
| TUM-057 | Union representation election | Process | Voted YES in NLRB election 2020, Card check authorization, Union organizing campaign |
| TUM-058 | Strike participation | Activism | Participated in 2023 strike, Walked the picket line, Strike captain |
| TUM-059 | Strike fund / hardship fund | Financial | Strike fund disbursement: $200/week, Hardship grant received |
| TUM-060 | Grievance filed | Workplace process | Grievance #G-2024-001 filed regarding [issue], Step 2 grievance |
| TUM-061 | Arbitration party | Dispute resolution | Named party in arbitration, AAA arbitration #12345 |
| TUM-062 | Right-to-Work state | Membership choice | "RTW state employee — opted to pay agency fee instead of dues"; "Not a union member (RTW state)" |
| TUM-063 | Public sector vs private | Sector distinction | Public sector union member (e.g., AFSCME), Private sector union member (e.g., UAW) |
| TUM-064 | Bargaining unit | Collective | Bargaining Unit Employee, Excluded from bargaining unit (supervisor), Non-supervisory |
| TUM-065 | Open vs closed shop | Workplace type | Closed shop (union membership required, illegal in US since 1947), Union shop, Agency shop |
| TUM-066 | Union officer / leadership | Role | Union President, Local President, Secretary-Treasurer, Business Agent, International VP |
| TUM-067 | Political action / PAC | Donations | UAW V-CAP (PAC), AFL-CIO COPE donations, Union PAC contribution |
| TUM-068 | Anti-union / decertification | Status change | Voted to decertify union, Decert election, "Right to Work" advocate |
| TUM-069 | NLRB / labor board case | Government | NLRB Case #29-CA-12345, ULP (Unfair Labor Practice) charge filed |
| TUM-070 | Union meeting attendance | Activism | Attended union meeting 2024-03-15, Voted at convention |
| TUM-071 | Apprenticeship program | Trade entry | IBEW apprentice, 5-year apprenticeship program, Joint Apprenticeship Committee (JATC) |
| TUM-072 | Pension fund participation | Retirement | Multi-employer pension plan (Taft-Hartley), Union pension fund member |
| TUM-073 | Health & welfare fund | Benefits | Union health & welfare fund, Taft-Hartley health benefits, Local 1199 benefit fund |
| TUM-074 | Trade union in JSON | Structured | "union_member": true, "union_name": "Teamsters Local 75", "member_id": "12345", "good_standing": true |
| TUM-075 | Trade union in KV | Form field | union_member=YES, UNION: UAW Local 235, MEMBER_ID: 12345 |
| TUM-076 | Trade union in XML | Markup | <union_member>true</union_member>, <union name="UAW" local="235">12345</union> |
| TUM-077 | Trade union in CSV | Tabular | "Smith","John","E12345","UAW Local 235","12345","Active" |
| TUM-078 | Multilingual context label | Various | Union (EN), Syndicat (FR), Gewerkschaft (DE), Sindicato (ES), Sindacato (IT), Sindicato (PT), 労働組合 (JP), 노동조합 (KR), 工会 (ZH), Профсоюз (RU), Sendika (TR), نقابة عمالية (AR), איגוד מקצועי (HE), สหภาพแรงงาน (TH) |
| TUM-079 | OCR-distorted union | Char substitution | Unlon (l for i), UAVV (VV for W), Sindicat0 (0 for o); l8EW (l for I, 8 for B) |
| TUM-080 | Masked / partial union | Privacy-redacted | Union: [REDACTED], Local: ***, Member ID: ****-1234 |
| TUM-081 | Anonymized placeholder | Standard generic | Union: <UNION_NAME>, Member: NO, Union: [PRIVATE] |
| TUM-082 | Sentence-boundary tricky | Trailing punctuation | "She joined the union.", "Was he UAW?", "Union member!" |
| TUM-083 | Adjacency-tight | No separator | "JohnSmithUAWLocal235", "MariaGarcíaSEIULocal1199" |
| TUM-084 | Union withdrawal / resignation | Membership end | Withdrew from union 2024-03-15, Resigned membership, Beck objector (financial-core only) |
| TUM-085 | Janus rights (public sector US) | 2018 SCOTUS | Janus rights: not paying agency fees (post-2018), Janus opt-out |
| TUM-086 | Industry-specific independent | Non-federation | Independent union, Company union (rare, often illegal), Affiliated independent |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | TUM-079 |
| Masked / partial / redacted | ✓ | TUM-080, TUM-081 |
| Multilingual context labels | ✓ | TUM-078 |
| Country / union coverage | ✓ | TUM-002 to TUM-049 (US 17 major unions, UK 7, DE 4, FR 4, IT 3, ES, NL, SE, NO, DK, JP, KR, AU, CA, BR + international) |
| Industry coverage | ✓ | TUM-003 (auto), TUM-004 (transport), TUM-005 (service), TUM-006 (electrical), TUM-007 (food/retail), TUM-008 (public), TUM-009-010 (teachers), TUM-011 (steel), TUM-012 (comms), TUM-013-014 (longshore), TUM-015-017 (entertainment), TUM-018-019 (public safety), TUM-025-026 (medical/nursing) |
| Member status / lifecycle | ✓ | TUM-053, TUM-054, TUM-055, TUM-084, TUM-085 |
| In structured data | ✓ | TUM-074, TUM-075, TUM-076, TUM-077 |
| Adjacency-tight | ✓ | TUM-083 |
| Sentence-boundary tricky | ✓ | TUM-082 |
| Domain-embedded (CBA/grievance/strike/NLRB/election) | ✓ | TUM-056 to TUM-061, TUM-069, TUM-070 |
| Shop / Workplace type | ✓ | TUM-062, TUM-063, TUM-064, TUM-065 |
| Union roles | ✓ | TUM-052, TUM-066 |
| Political activity | ✓ | TUM-067 |
| Benefits / pension | ✓ | TUM-072, TUM-073 |
| Apprenticeship | ✓ | TUM-071 |

**Total patterns for Trade_Union_Membership: 86**

---

## Entity 44: Allergy_Information

Allergy data — food, drug, environmental, insect. GDPR Article 9 (health) data. Critical for medical/emergency response.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| ALLG-001 | Food allergy — peanut | Common | Peanut allergy, Allergic to peanuts, Anaphylactic to peanuts |
| ALLG-002 | Food allergy — tree nuts | Common | Tree nut allergy, Allergic to almonds/cashews/walnuts/pecans, Tree nut sensitivity |
| ALLG-003 | Food allergy — milk / dairy | Common | Milk allergy (IgE-mediated), Dairy allergy, Lactose intolerance (note: not strictly allergy) |
| ALLG-004 | Food allergy — egg | Common | Egg allergy, Allergic to eggs (whites and yolks) |
| ALLG-005 | Food allergy — wheat / gluten | Common | Wheat allergy, Gluten intolerance (not same as celiac), Celiac disease (autoimmune, not allergy) |
| ALLG-006 | Food allergy — soy | Common | Soy allergy, Allergic to soybeans |
| ALLG-007 | Food allergy — fish | Common | Fish allergy (tuna, salmon, etc.), Allergic to fish |
| ALLG-008 | Food allergy — shellfish | Common | Shellfish allergy (shrimp, crab, lobster), Crustacean allergy, Mollusks |
| ALLG-009 | Food allergy — sesame | "9th major" | Sesame allergy (declared 9th major allergen by FDA in 2023) |
| ALLG-010 | Food allergy — corn | Less common | Corn allergy, Allergic to corn |
| ALLG-011 | Food allergy — mustard | Less common | Mustard allergy (common in Canada), Mustard seed allergy |
| ALLG-012 | Food allergy — sulfites | Additive | Sulfite allergy/sensitivity (in wine, dried fruit), Sulfite-induced asthma |
| ALLG-013 | Food allergy — fruit | OAS / specific | Stone fruit allergy (peach, cherry), Apple OAS (Oral Allergy Syndrome), Citrus allergy |
| ALLG-014 | Drug allergy — penicillin | Common | Penicillin allergy (PCN allergy), Allergic to amoxicillin, Beta-lactam allergy |
| ALLG-015 | Drug allergy — sulfa | Common | Sulfa drug allergy (sulfonamides), Bactrim allergy, sulfa-allergic |
| ALLG-016 | Drug allergy — NSAIDs | Common | NSAID allergy, Aspirin allergy, Ibuprofen allergy, AERD (Aspirin-Exacerbated Respiratory Disease) |
| ALLG-017 | Drug allergy — opioids | Specific | Codeine allergy, Morphine sensitivity, Opioid intolerance |
| ALLG-018 | Drug allergy — anesthetics | Procedural | Allergic to lidocaine, Allergic to novocaine, Local anesthetic allergy |
| ALLG-019 | Drug allergy — contrast dye | Radiology | Iodinated contrast allergy, Gadolinium allergy (MRI contrast), CT contrast reaction |
| ALLG-020 | Drug allergy — vaccine components | Vaccine | PEG allergy (mRNA vaccines), Egg-protein allergy (flu vaccine), Latex in vaccine vial |
| ALLG-021 | Drug allergy — chemotherapy | Severe | Allergic to taxanes, Reaction to carboplatin, Pre-medication required |
| ALLG-022 | Environmental — pollen | Seasonal | Pollen allergy, Hay fever, Allergic rhinitis (seasonal), Tree pollen, Grass pollen, Ragweed |
| ALLG-023 | Environmental — dust mites | Year-round | Dust mite allergy, Perennial allergic rhinitis |
| ALLG-024 | Environmental — mold | Year-round | Mold allergy, Aspergillus sensitivity, Alternaria allergy |
| ALLG-025 | Environmental — pet dander | Common | Cat allergy (Fel d 1), Dog allergy, Pet dander allergy |
| ALLG-026 | Environmental — animal proteins | Specific | Horse allergy, Bird allergen, Rabbit dander |
| ALLG-027 | Insect — bee sting | Severe potential | Bee sting allergy, Anaphylactic to bee venom, Apis mellifera venom allergy |
| ALLG-028 | Insect — wasp / hornet | Severe potential | Wasp sting allergy, Yellow jacket allergy, Hymenoptera venom allergy |
| ALLG-029 | Insect — fire ant | Regional severe | Fire ant allergy (US Southeast), Solenopsis invicta venom |
| ALLG-030 | Insect — mosquito | Mild typically | Severe mosquito reaction (Skeeter syndrome) |
| ALLG-031 | Latex allergy | Material | Latex allergy, Natural rubber latex sensitivity, Hevea brasiliensis allergy |
| ALLG-032 | Chemical — nickel | Contact | Nickel allergy (contact dermatitis), Allergic to jewelry, Nickel-free required |
| ALLG-033 | Chemical — fragrance | Contact | Fragrance allergy, Perfume sensitivity, Eau de toilette reaction |
| ALLG-034 | Chemical — preservative | Cosmetic | Paraben sensitivity, Methylisothiazolinone (MI) allergy |
| ALLG-035 | Adhesive / Tape | Material | Allergic to medical tape adhesive, Bandage adhesive reaction |
| ALLG-036 | Severity — anaphylaxis | Most severe | Anaphylactic reaction, Anaphylaxis history, History of anaphylaxis to peanuts |
| ALLG-037 | Severity — severe | Very severe | Severe allergic reaction, ICU admission for allergic reaction |
| ALLG-038 | Severity — moderate | Moderate | Moderate allergic reaction (hives, swelling, no breathing issue) |
| ALLG-039 | Severity — mild | Mild | Mild reaction (rash, sniffles), Minor allergic response |
| ALLG-040 | Reaction symptom — hives / urticaria | Skin | Hives, Urticaria, Wheals, Welts on contact |
| ALLG-041 | Reaction symptom — angioedema | Swelling | Angioedema, Facial swelling, Lip and tongue swelling |
| ALLG-042 | Reaction symptom — respiratory | Breathing | Wheezing, Shortness of breath, Bronchospasm, Stridor |
| ALLG-043 | Reaction symptom — GI | Stomach | Vomiting, Diarrhea, GI distress, Abdominal pain |
| ALLG-044 | Reaction symptom — cardiovascular | Severe | Hypotension, Cardiovascular collapse, Loss of consciousness |
| ALLG-045 | Prescription — EpiPen / Auvi-Q | Auto-injector | EpiPen Jr. (0.15 mg), EpiPen (0.30 mg), Auvi-Q, Adrenaclick — carry at all times |
| ALLG-046 | Prescription — antihistamine | Treatment | Carries Benadryl, Diphenhydramine 25-50 mg PRN, Cetirizine 10 mg daily |
| ALLG-047 | Prescription — steroid inhaler | Asthma | Albuterol inhaler PRN, Fluticasone (Flovent) BID, Asthma plan in place |
| ALLG-048 | Allergy bracelet / Medical alert | Visual | Wears MedicAlert bracelet listing peanut allergy, Medical ID necklace |
| ALLG-049 | Allergy test results | Lab | Skin prick test positive for peanut, IgE specific RAST for cat: Class 4 |
| ALLG-050 | Negative allergy test | Cleared | Skin prick test negative for shellfish, IgE Class 0 for milk, Outgrown milk allergy |
| ALLG-051 | Allergy in medical chart | Clinical | "Pt: Smith, John; Allergies: Penicillin (rash), Peanuts (anaphylaxis)" |
| ALLG-052 | "NKDA" — No Known Drug Allergies | Standard medical | NKDA, No Known Drug Allergies, NKA (No Known Allergies) |
| ALLG-053 | Allergy on school form | Education | "School Emergency Form: Severe peanut allergy, EpiPen in nurse's office" |
| ALLG-054 | Allergy on camp / activity form | Activities | Camp medical form: dairy allergy, peanut-free table required |
| ALLG-055 | Allergy on cruise / hotel form | Travel | Special meal request: gluten-free, Tree nut allergy noted at front desk |
| ALLG-056 | Allergy in restaurant order | Service | "Allergy alert: peanut allergy, please notify chef"; "Anaphylactic shellfish allergy" |
| ALLG-057 | Allergy on airline / flight | Travel | "Severe nut allergy — request peanut-free flight"; "EpiPen onboard" |
| ALLG-058 | Allergy in workplace | HR / safety | "Workplace nut-free zone requested for severe allergy"; "ADA accommodation: allergen-free workspace" |
| ALLG-059 | Allergy in family history | Genetics | "Family history of severe peanut allergy (mother, sibling)" |
| ALLG-060 | Outgrew allergy | Lifecycle | Outgrew milk allergy at age 5, Tolerated egg in oral food challenge |
| ALLG-061 | Recently diagnosed | New | Recently diagnosed peanut allergy (2024), New-onset allergy at age 35 |
| ALLG-062 | Oral food challenge result | Clinical | OFC: Passed (tolerated 2g peanut protein), OFC: Failed (reacted at 100mg) |
| ALLG-063 | Cross-reactive allergies | Related | "Allergic to ragweed → may cross-react with banana/cantaloupe (OAS)"; "Birch pollen → apple OAS" |
| ALLG-064 | Allergy in JSON | Structured | "allergies": [{"allergen": "peanut", "severity": "anaphylaxis", "reaction": "respiratory"}] |
| ALLG-065 | Allergy in KV | Form field | allergies=peanut,shellfish; ALLERGY: penicillin (rash); SEVERE_ALLERGY: peanut |
| ALLG-066 | Allergy in XML | Markup | <allergy><allergen>peanut</allergen><severity>anaphylaxis</severity></allergy> |
| ALLG-067 | Allergy in CSV | Tabular | "Smith","John","E12345","Peanut","Anaphylaxis","EpiPen" |
| ALLG-068 | Multilingual context label | Various | Allergies (EN), Allergies (FR), Allergien (DE), Alergias (ES), Allergie (IT), Alergias (PT), アレルギー (JP), 알레르기 (KR), 过敏 (ZH), Аллергии (RU), Alerji (TR), حساسية (AR), אלרגיה (HE), อาการแพ้ (TH) |
| ALLG-069 | Multilingual allergen names | Various | Peanut: cacahuète (FR), Erdnuss (DE), cacahuete (ES), arachide (IT), amendoim (PT), 落花生 (JP), 땅콩 (KR), 花生 (ZH), арахис (RU) |
| ALLG-070 | OCR-distorted allergy | Char substitution | Aiiergy (i for l), Allergen (allergen typed correctly but reaction text mangled), AnaphyiaxIs (i for l, I for x) |
| ALLG-071 | Masked / partial allergy | Privacy-redacted | Allergies: [REDACTED], Allergen: ***, Severe allergy: [PRIVATE] |
| ALLG-072 | Anonymized placeholder | Standard generic | Allergies: NKDA, Allergy: <ALLERGEN>, [NO ALLERGIES KNOWN] |
| ALLG-073 | Sentence-boundary tricky | Trailing punctuation | "He's allergic to peanuts.", "Is she allergic to penicillin?", "Severe allergy alert!" |
| ALLG-074 | Adjacency-tight | No separator | "JohnSmithE12345PeanutAnaphylaxis", "MariaGarcíaPenicillinHives" |
| ALLG-075 | Allergy action plan | Medical doc | "Allergy Action Plan: 1. Identify allergen, 2. Administer EpiPen, 3. Call 911, 4. Antihistamine" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | ALLG-070 |
| Masked / partial / redacted | ✓ | ALLG-071, ALLG-072 |
| Multilingual context labels | ✓ | ALLG-068 |
| Multilingual allergen names | ✓ | ALLG-069 |
| Allergen category coverage | ✓ | ALLG-001 to ALLG-013 (food — 9 FDA "Big 9" + others), ALLG-014 to ALLG-021 (drug), ALLG-022 to ALLG-026 (environmental), ALLG-027 to ALLG-030 (insect), ALLG-031 to ALLG-035 (material/chemical) |
| Severity tiers | ✓ | ALLG-036, ALLG-037, ALLG-038, ALLG-039 |
| Reaction types | ✓ | ALLG-040 (skin), ALLG-041 (angioedema), ALLG-042 (respiratory), ALLG-043 (GI), ALLG-044 (CV) |
| Treatment / prescription | ✓ | ALLG-045, ALLG-046, ALLG-047 |
| Documentation | ✓ | ALLG-048, ALLG-049, ALLG-050, ALLG-051, ALLG-052 |
| In structured data | ✓ | ALLG-064, ALLG-065, ALLG-066, ALLG-067 |
| Adjacency-tight | ✓ | ALLG-074 |
| Sentence-boundary tricky | ✓ | ALLG-073 |
| Domain-embedded (school/workplace/travel/restaurant/airline) | ✓ | ALLG-053 to ALLG-058 |
| Lifecycle (outgrew/new/test) | ✓ | ALLG-060, ALLG-061, ALLG-062 |
| Cross-reactivity | ✓ | ALLG-063 |
| Family history | ✓ | ALLG-059 |
| Action plan | ✓ | ALLG-075 |

**Total patterns for Allergy_Information: 75**

---

## Entity 45: Medical_Information

Diagnoses, medications, treatments, lab results, vital signs, procedures, mental health. GDPR Article 9 + HIPAA-protected. Most sensitive PII category alongside Crime.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| MED-001 | Diagnosis — chronic condition | Common | Type 2 Diabetes, Hypertension, Asthma, COPD, Hyperlipidemia |
| MED-002 | Diagnosis — cardiovascular | CV | Coronary Artery Disease (CAD), Atrial fibrillation, Heart failure (CHF), Hypertension HTN, Post-MI |
| MED-003 | Diagnosis — diabetes specifics | Endocrine | Type 1 DM (insulin-dependent), Type 2 DM, Gestational diabetes (GDM), Pre-diabetes, A1C 7.2% |
| MED-004 | Diagnosis — cancer (general) | Oncology | Cancer diagnosis, Carcinoma, Sarcoma, Lymphoma, Leukemia, History of cancer |
| MED-005 | Diagnosis — cancer specific | Specific oncology | Breast cancer (Stage II), Non-small cell lung cancer (Stage IV), Prostate cancer (Gleason 7), Pancreatic adenocarcinoma |
| MED-006 | Cancer staging | Severity | Stage 0/I/II/III/IV, T2N1M0 (TNM staging), Metastatic disease, Localized cancer |
| MED-007 | Diagnosis — HIV / AIDS | Sensitive | HIV-positive, AIDS diagnosis 2018, HIV viral load <50 (undetectable), CD4 count 450 |
| MED-008 | Diagnosis — Hepatitis | Liver | Hepatitis B (chronic), Hepatitis C (treated, SVR), Hep A (acute, resolved) |
| MED-009 | Diagnosis — Tuberculosis | Infectious | TB (Tuberculosis), Latent TB, Active TB, Pulmonary TB |
| MED-010 | Diagnosis — STI / STD | Sexual health | Chlamydia (treated), Gonorrhea, Syphilis (RPR positive), HPV, Herpes Simplex |
| MED-011 | Diagnosis — autoimmune | Immune | Lupus (SLE), Rheumatoid Arthritis (RA), Multiple Sclerosis (MS), Crohn's, Ulcerative Colitis |
| MED-012 | Diagnosis — neurological | Brain | Migraine, Epilepsy, Parkinson's Disease, Alzheimer's Disease, Stroke (CVA) history |
| MED-013 | Diagnosis — mental health (depression) | Psychiatric | Major Depressive Disorder (MDD), Persistent Depressive Disorder, Postpartum depression |
| MED-014 | Diagnosis — mental health (anxiety) | Psychiatric | Generalized Anxiety Disorder (GAD), Panic Disorder, Social Anxiety Disorder |
| MED-015 | Diagnosis — bipolar | Psychiatric | Bipolar I, Bipolar II, Cyclothymic Disorder, Manic episode |
| MED-016 | Diagnosis — schizophrenia spectrum | Psychiatric | Schizophrenia, Schizoaffective Disorder, Schizophreniform |
| MED-017 | Diagnosis — PTSD | Psychiatric | PTSD (Post-Traumatic Stress Disorder), Acute Stress Disorder, Military-related PTSD |
| MED-018 | Diagnosis — OCD | Psychiatric | OCD (Obsessive-Compulsive Disorder), OCPD (personality), Body Dysmorphic Disorder |
| MED-019 | Diagnosis — eating disorder | Psychiatric | Anorexia Nervosa, Bulimia Nervosa, Binge Eating Disorder (BED), ARFID |
| MED-020 | Diagnosis — autism / ADHD | Neurodevelopmental | Autism Spectrum Disorder (ASD), Asperger's (legacy term), ADHD (Combined / Inattentive / Hyperactive) |
| MED-021 | Diagnosis — substance use | Behavioral | Alcohol Use Disorder (AUD), Opioid Use Disorder (OUD), Cocaine dependence, Nicotine dependence, In recovery |
| MED-022 | Diagnosis — pregnancy related | OB | Pregnant (G2P1, EDD 06/15/2024), Preeclampsia, Gestational HTN, IUGR, History of miscarriage |
| MED-023 | Diagnosis — reproductive health | Repro | PCOS, Endometriosis, Infertility, Menopause, PMS/PMDD |
| MED-024 | Diagnosis — abortion (medical history) | Sensitive | History of therapeutic abortion (TAB), Spontaneous abortion (SAB / miscarriage) |
| MED-025 | Diagnosis — gender dysphoria | Sensitive | Gender Dysphoria, GD, Gender Identity Disorder (legacy term DSM-IV) |
| MED-026 | Diagnosis — rare disease | Specific | Cystic Fibrosis, Sickle Cell Disease, Huntington's, Marfan Syndrome, Hemophilia |
| MED-027 | Diagnosis — pediatric | Children | ADHD (pediatric), Asthma (childhood), Autism (early-onset), Down Syndrome, Cerebral Palsy |
| MED-028 | ICD-10 code | Classification | ICD-10: E11.9 (Type 2 DM without complications), I10 (Essential HTN), F32.9 (Depression unspecified), J45.909 (Asthma uncomplicated) |
| MED-029 | ICD-11 code | New classification | ICD-11: 5A11 (Type 2 DM), BA00.Z (Essential HTN), 6A70 (Depressive disorders) |
| MED-030 | DSM-5 code | Psychiatric | DSM-5: 296.32 (MDD Recurrent Moderate), 309.81 (PTSD), 314.01 (ADHD Combined) |
| MED-031 | Medication — by name | Prescription | Metformin 1000 mg BID, Lisinopril 20 mg daily, Atorvastatin 40 mg QHS, Sertraline 100 mg daily |
| MED-032 | Medication with dosing | Detailed | Insulin glargine 30 units SC HS, Warfarin 5 mg PO daily (target INR 2-3), Furosemide 40 mg PO BID |
| MED-033 | Controlled substance | DEA-regulated | Oxycodone 5 mg q4h PRN, Adderall 30 mg XR daily, Xanax 1 mg PRN (Schedule IV) |
| MED-034 | Chemotherapy regimen | Oncology | FOLFOX (5-FU + Oxaliplatin + Leucovorin), AC-T (Doxorubicin-Cyclophosphamide → Taxol), R-CHOP |
| MED-035 | Biologic medications | Specialty | Humira (adalimumab), Enbrel (etanercept), Keytruda (pembrolizumab), Ozempic (semaglutide) |
| MED-036 | Insulin types | Diabetes | Lantus (long-acting), Humalog (rapid), NovoLog 70/30, U-500 insulin |
| MED-037 | Birth control | Reproductive | Oral contraceptive (OCP), Mirena IUD, Depo-Provera, Plan B emergency contraception |
| MED-038 | HRT / Hormone therapy | Hormonal | Estradiol patch, Testosterone gel, Progesterone, GnRH analogs |
| MED-039 | Mental health medications | Psych | SSRIs (Sertraline, Fluoxetine), SNRIs (Venlafaxine), Antipsychotics (Risperidone, Quetiapine), Lithium |
| MED-040 | Anticoagulants | Blood thinners | Warfarin (Coumadin), Apixaban (Eliquis), Rivaroxaban (Xarelto), Heparin, Enoxaparin (Lovenox) |
| MED-041 | Prescription number | Rx ID | Rx #: 1234567, Prescription Number: RX-2024-12345, Pharmacy Rx: P12345-001 |
| MED-042 | Refill / quantity | Rx detail | Qty: 90 tablets, 30-day supply, Refills: 3, Last filled 2024-03-15 |
| MED-043 | Lab result — CBC | Hematology | CBC: WBC 7.2, RBC 4.5, Hgb 14.2, Hct 42, PLT 250, MCV 88 |
| MED-044 | Lab result — BMP / CMP | Chemistry | BMP: Na 138, K 4.2, Cl 102, CO2 24, BUN 18, Cr 1.0, Glucose 95 |
| MED-045 | Lab result — Lipid panel | Cholesterol | Total Chol 195, LDL 110, HDL 55, Triglycerides 130 |
| MED-046 | Lab result — A1C | Diabetes | A1C 7.2% (target <7%), HbA1c 6.5 |
| MED-047 | Lab result — Thyroid | Thyroid | TSH 2.4 (normal 0.4-4.0), Free T4 1.2, Free T3 3.5 |
| MED-048 | Lab result — Cardiac markers | CV | Troponin <0.04 (negative), BNP 250, NT-proBNP 850 |
| MED-049 | Lab result — Liver function | Hepatic | AST 32, ALT 28, Alk Phos 95, Total Bili 0.8, Albumin 4.0 |
| MED-050 | Lab result — Coagulation | Coag | PT 12.5, INR 1.1 (warfarin target 2-3), PTT 30, Fibrinogen 350 |
| MED-051 | Lab result — Pregnancy | OB | hCG 25 mIU/mL (positive), Beta-hCG 1500, AFP 32 |
| MED-052 | Lab result — HIV | Specific | HIV viral load: <50 copies/mL (undetectable), CD4 count: 450, HIV antibody positive |
| MED-053 | Lab result — Hepatitis | Specific | Hep B sAg negative, Hep C antibody positive (chronic HCV), HCV RNA 250,000 IU/mL |
| MED-054 | Genetic test result | Genomics | BRCA1 positive (variant: c.5266dupC), MTHFR C677T heterozygous, 23andMe APOE ε3/ε4 |
| MED-055 | Vital sign — BP | Hemodynamics | BP 120/80, BP 140/95 (Stage 1 HTN), 180/110 (hypertensive urgency) |
| MED-056 | Vital sign — Pulse | HR | HR 72, Pulse 110 (tachycardia), HR 45 (bradycardia) |
| MED-057 | Vital sign — Temperature | Temp | Temp 98.6°F (37°C), Fever 102°F, Hypothermia 95°F |
| MED-058 | Vital sign — Respiratory rate | RR | RR 16, RR 24 (tachypneic), RR 8 (bradypneic) |
| MED-059 | Vital sign — O2 saturation | SpO2 | SpO2 98% on RA, SpO2 88% (hypoxic), 95% on 2L NC |
| MED-060 | Vital sign — Pain score | Pain | Pain 4/10, Pain rating 8/10, FACES scale 3 |
| MED-061 | BMI / Weight | Anthropometric | BMI 24.5, Weight 165 lbs (75 kg), Height 5'10" (178 cm) |
| MED-062 | Procedure — surgery | Surgical | Appendectomy 2018, Cholecystectomy (laparoscopic), CABG x 3 vessels, Total knee replacement |
| MED-063 | Procedure — diagnostic | Diagnostic | EKG showing afib, Colonoscopy 2020 (clean), Mammogram (BIRADS 1), Stress test (negative) |
| MED-064 | Procedure — interventional | Cardiac | Cardiac cath, PCI with stent placement, Pacemaker insertion |
| MED-065 | Imaging — radiology | Imaging | CT chest with contrast, MRI brain (no acute findings), X-ray (right wrist fracture) |
| MED-066 | Procedure — abortion / D&C | Sensitive | Therapeutic abortion (TAB) 2018, D&C for incomplete miscarriage 2020 |
| MED-067 | Procedure — gender-affirming | Sensitive | Top surgery (mastectomy), Bottom surgery (vaginoplasty/phalloplasty), Hormone therapy |
| MED-068 | Vaccination — childhood | Routine | MMR series complete, Varicella, DTaP, Polio, HPV vaccinated (3-dose series) |
| MED-069 | Vaccination — adult | Routine | Tetanus booster 2020, Flu vaccine 2023-24 season, Pneumococcal (PPSV23, PCV13) |
| MED-070 | Vaccination — travel | Specific | Yellow fever vaccine (required for Brazil entry), Typhoid, Hepatitis A, Japanese encephalitis |
| MED-071 | Vaccination — COVID | Recent | COVID vaccinated (Pfizer x2 + bivalent booster 2023-09-15), J&J single-dose, mRNA-1273 |
| MED-072 | Diagnosis date | Time | Diagnosed 2018-06-15, Date of diagnosis: March 2020, Initial dx: 6 years ago |
| MED-073 | Doctor / Provider name | Provider | Primary Care: Dr. Sarah Chen, Endocrinologist: Dr. John Smith, Surgeon: Dr. Maria García MD |
| MED-074 | NPI — Provider ID (US) | National Provider Identifier | NPI: 1234567893 (10-digit), Provider NPI 9876543210 |
| MED-075 | DEA number | Controlled Rx | DEA: BC1234563, DEA Registration #: BS9876541 |
| MED-076 | Hospital / facility | Location | Admitted to Boston General, Discharged from Mayo Clinic, Office visit at Cleveland Clinic |
| MED-077 | Medical record number (MRN) | Hospital ID | MRN: 12345678 (hospital-specific), Med Rec #: 98765, Patient ID: P-12345 |
| MED-078 | Hospital admission | Inpatient | Admitted 2024-03-15 for acute MI, LOS 5 days, DC home 2024-03-20 |
| MED-079 | Emergency dept visit | ED | ED visit 2024-03-15 for chest pain, ECG normal, troponin negative, DC home |
| MED-080 | DNR / Advance Directive | End of life | DNR (Do Not Resuscitate), DNI (Do Not Intubate), POLST form completed, Healthcare proxy: Jane Doe |
| MED-081 | Insurance plan | Coverage | Aetna PPO, BCBS HMO, UnitedHealth Choice Plus, Medicare Part A/B/D, Medicaid |
| MED-082 | Insurance member ID / Group | ID | Member ID: W123456789, Group #: 12345, Plan: HMO |
| MED-083 | Prior authorization | Process | Prior Auth Approved (auth #: PA-12345); PA denied for X medication; Step therapy required |
| MED-084 | Clinical trial enrollment | Research | Enrolled in Phase III trial NCT12345678, Subject ID: 001, Trial: AbCDxR vs placebo |
| MED-085 | Disability — physical | Functional | Wheelchair user, Hearing impaired, Blind, Mobility-impaired, Use of cane required |
| MED-086 | Disability — cognitive | Functional | Cognitive impairment, Intellectual disability, Dementia, Memory loss |
| MED-087 | Disability — VA rating | Veterans | 70% service-connected disability (VA), 100% T&P (Total and Permanent), MST (military sexual trauma) |
| MED-088 | SOAP note format | Clinical | "S: pt c/o chest pain. O: BP 140/90, HR 110, ECG NSR. A: chest pain, r/o ACS. P: troponin, EKG, CXR" |
| MED-089 | Medical info in JSON | Structured | "diagnosis": ["Type 2 DM", "HTN"], "medications": ["Metformin", "Lisinopril"], "allergies": ["Penicillin"] |
| MED-090 | Medical info in KV | Form field | diagnosis=T2DM, BP: 120/80, HBA1C: 7.2 |
| MED-091 | Medical info in XML | Markup | <diagnosis code="E11.9">Type 2 DM</diagnosis>, <medication dose="1000mg">Metformin</medication> |
| MED-092 | Medical info in CSV | Tabular | "Smith","John","E12345","T2DM","Metformin","2018-06-15" |
| MED-093 | HL7 / FHIR format | Standards | HL7 v2 segment: PID|||MRN12345^^^HOSP||SMITH^JOHN; FHIR Patient resource |
| MED-094 | EMR system reference | EHR | Epic patient ID: 12345, Cerner MRN: 98765, Allscripts ID |
| MED-095 | Multilingual context label | Various | Medical History (EN), Antécédents médicaux (FR), Krankengeschichte (DE), Historia clínica (ES), Storia clinica (IT), História médica (PT), 病歴 (JP), 병력 (KR), 病史 (ZH), Медицинская история (RU), Tıbbi geçmiş (TR), التاريخ الطبي (AR), היסטוריה רפואית (HE), ประวัติการรักษา (TH) |
| MED-096 | OCR-distorted medical | Char substitution | Hypertenslon (l for i), Dlabetes (l for i), MedlcatlOn (l for i, O for o), 5SRl (5 for S, l for I) |
| MED-097 | OCR lab values | Number | "BP l2O/8O" (l for 1, O for 0), "A1C 7.Z%" (Z for 2), "HR 1OO" (O for 0) |
| MED-098 | Masked / partial medical | Privacy-redacted | Diagnosis: [REDACTED], Medications: ***, BP: ** |
| MED-099 | Anonymized placeholder | Standard generic | Diagnosis: <CONDITION>, Medication: TBD, [REDACTED MEDICAL] |
| MED-100 | Sentence-boundary tricky | Trailing punctuation | "He has diabetes.", "Is the BP 140/90?", "Diagnosed with cancer!" |
| MED-101 | Adjacency-tight | No separator | "JohnSmithE12345T2DMMetformin", "MariaGarcíaHIVPositive2018" |
| MED-102 | Family history | Genetic | "Family Hx: Father MI age 55, Mother breast cancer age 60, Sister T2DM" |
| MED-103 | Social history | Habits | "Social Hx: Smoker 1 PPD x 20 yrs, Occasional alcohol, No drugs, Married, 2 kids" |
| MED-104 | Sexual history | Sensitive | "Sexual Hx: MSM, 3 partners last 6 months, condom use inconsistent, on PrEP" |
| MED-105 | Mental health rating scales | Standardized | PHQ-9 score: 12 (moderate depression), GAD-7: 8 (mild anxiety), AUDIT-C: 5 |
| MED-106 | Pain scale outcomes | Functional | "Pain 8/10 → 3/10 post-treatment"; "VAS pain: 75/100 → 25/100" |
| MED-107 | Workers' comp medical | Injury claim | WC injury: 2023-06-15 (back strain at work), MMI reached 2024-03-15, 15% impairment rating |
| MED-108 | Disability claim documentation | SS/private | SSDI approved 2023 (based on RA + depression), LTD claim with major depression dx |
| MED-109 | Vaccination card / passport | Doc | "COVID-19 Vaccination Record Card: Pfizer Dose 1 (2021-01-15), Dose 2 (2021-02-12), Booster (2023-09-15)" |
| MED-110 | Pharmacy filled prescription | Dispensing record | "Walgreens Pharmacy filled Rx #1234567 for Metformin 1000 mg #60 on 2024-03-15, copay $5" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | MED-096, MED-097 |
| Masked / partial / redacted | ✓ | MED-098, MED-099 |
| Multilingual context labels | ✓ | MED-095 |
| Diagnosis category coverage | ✓ | MED-001 (chronic), MED-002 (CV), MED-003 (DM), MED-004-006 (cancer), MED-007-010 (infectious), MED-011 (autoimmune), MED-012 (neuro), MED-013-021 (psych/substance), MED-022-024 (OB/repro/abortion), MED-025 (gender), MED-026 (rare), MED-027 (pediatric) |
| Coding systems | ✓ | MED-028 (ICD-10), MED-029 (ICD-11), MED-030 (DSM-5), MED-093 (HL7/FHIR) |
| Medications coverage | ✓ | MED-031-042 (oral, dosed, controlled, chemo, biologic, insulin, BC, HRT, psych, anticoag) |
| Lab results | ✓ | MED-043-053 (CBC, BMP, lipid, A1C, thyroid, cardiac, liver, coag, pregnancy, HIV, hep) |
| Genetic | ✓ | MED-054 |
| Vital signs / Anthropometric | ✓ | MED-055 to MED-061 |
| Procedures / Imaging | ✓ | MED-062 to MED-067 |
| Vaccinations | ✓ | MED-068 to MED-071, MED-109 |
| Identifiers (NPI, DEA, MRN) | ✓ | MED-074, MED-075, MED-077 |
| Healthcare lifecycle (admission, ED, DNR) | ✓ | MED-078, MED-079, MED-080 |
| In structured data | ✓ | MED-089, MED-090, MED-091, MED-092 |
| Adjacency-tight | ✓ | MED-101 |
| Sentence-boundary tricky | ✓ | MED-100 |
| Domain-embedded (insurance, prior auth, trial, WC, SSDI) | ✓ | MED-081 to MED-084, MED-107, MED-108 |
| Disability | ✓ | MED-085, MED-086, MED-087 |
| History narratives (family, social, sexual) | ✓ | MED-102, MED-103, MED-104 |
| Rating scales | ✓ | MED-105, MED-106 |
| EMR-specific | ✓ | MED-094 |
| SOAP / clinical notes | ✓ | MED-088 |

**Total patterns for Medical_Information: 110**

---

## Entity 46: Social_Media_Identifiers

Usernames, handles, profile URLs, platform-specific IDs across social media platforms.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| SM-001 | Twitter / X — @handle | At-prefix | @johnsmith, @jane_doe, @sarah.chen, @maria_garcia |
| SM-002 | Twitter / X — profile URL | URL form | twitter.com/johnsmith, x.com/janedoe, https://twitter.com/sarah_chen |
| SM-003 | Twitter / X — numeric user ID | Internal ID | Twitter ID: 12345678, X User ID: 9876543210 |
| SM-004 | Twitter / X — verified marker | Blue check | @johnsmith ✓ (verified), @janedoe 🔵 (blue check), @company ✅ |
| SM-005 | Facebook — username URL | Profile | facebook.com/john.smith.123, fb.com/janedoe, facebook.com/sarah.chen.99 |
| SM-006 | Facebook — numeric user ID | Internal | Facebook UID: 100012345678901, FB ID: 1234567890 |
| SM-007 | Facebook — display name only | Display | "John Smith on Facebook", "Find me on Facebook as Jane Doe" |
| SM-008 | Instagram — @handle | Insta handle | @johnsmith_99, @jane.doe.travels, @sarah_chen, @maria.garcia |
| SM-009 | Instagram — profile URL | URL | instagram.com/johnsmith_99, instagr.am/janedoe, ig: @sarah_chen |
| SM-010 | LinkedIn — profile URL | Professional | linkedin.com/in/john-smith-12345, linkedin.com/in/janedoe, in/sarah-chen-engineer |
| SM-011 | LinkedIn — public ID | Slug | Public ID: john-smith-12345, LinkedIn Slug: sarah-chen-ml-engineer |
| SM-012 | LinkedIn — numeric ID | Internal | LinkedIn member ID: 12345678 |
| SM-013 | LinkedIn — company page | Org URL | linkedin.com/company/acme-corp, linkedin.com/school/stanford-university |
| SM-014 | TikTok — @handle | TikTok handle | @johnsmith.dance, @janedoe_cooks, @sarahchenmusic |
| SM-015 | TikTok — profile URL | URL | tiktok.com/@johnsmith.dance, vm.tiktok.com/ZMabc123 |
| SM-016 | Snapchat — username | Snap handle | Snapchat: johnsmith_snap, snap: jane.doe, Snap me: sarah_chen |
| SM-017 | Snapchat — snapcode reference | Visual code | "Add me on Snapchat — username: johnsmith_snap or scan my Snapcode" |
| SM-018 | YouTube — channel handle (@) | Modern format | @JohnSmith, @JaneDoeTravels, @SarahChenMusic (post-2022 handles) |
| SM-019 | YouTube — channel URL | URL | youtube.com/@JohnSmith, youtube.com/c/JaneDoeTravels, youtube.com/channel/UCabcdef123456 |
| SM-020 | YouTube — channel ID | Internal | Channel ID: UCabcdef1234567890, YouTube user ID: 12345 |
| SM-021 | Reddit — u/username | Reddit format | u/johnsmith_99, /u/janedoe, u/sarah_chen_dev |
| SM-022 | Reddit — profile URL | URL | reddit.com/u/johnsmith_99, reddit.com/user/janedoe, old.reddit.com/u/sarah_chen |
| SM-023 | Reddit — karma display | Profile signal | "u/johnsmith — 12,345 karma, 5-year Redditor"; Reddit cake day reference |
| SM-024 | Discord — username (new) | Modern format | @johnsmith (post-2023), @janedoe._.dev, @sarah_chen99 |
| SM-025 | Discord — username#discriminator (legacy) | Pre-2023 | johnsmith#1234, JaneDoe#5678, Sarah_Chen#0001 |
| SM-026 | Discord — server invite | Server link | discord.gg/abcd1234, discord.com/invite/example |
| SM-027 | Discord — user ID (numeric) | Internal | Discord ID: 123456789012345678 (snowflake), User: 987654321098765432 |
| SM-028 | Pinterest — username | Handle | pinterest.com/johnsmith99, @sarahchen on Pinterest |
| SM-029 | Telegram — @handle | T.me | @johnsmith_tg, t.me/janedoe, telegram.me/sarah_chen |
| SM-030 | Telegram — phone-linked | Number-based | Telegram: +1-917-555-0123 (phone-linked account) |
| SM-031 | WhatsApp — phone-linked | Phone-based | WhatsApp: +1-917-555-0123, WA: +44 20 7946 0958 |
| SM-032 | WhatsApp — Business handle | Business | WhatsApp Business: AcmeCorp, wa.me/19175550123 |
| SM-033 | WeChat — WeChat ID | China platform | WeChat ID: johnsmith99, 微信号: zhang_san_88, WeChat: sarah_chen_dev |
| SM-034 | Line — Line ID | Japan/Asia | Line ID: johnsmith_jp, Line: jane_doe_99, ライン: sarah_chen |
| SM-035 | KakaoTalk — Kakao ID | Korea | KakaoTalk ID: johnsmith_kr, 카카오톡: sarah_chen_seoul |
| SM-036 | VKontakte (VK) — handle | Russia | vk.com/johnsmith, VK: ivan_petrov_99, ВКонтакте: maria_sokolova |
| SM-037 | Weibo — handle | China micro-blog | Weibo: @johnsmith_weibo, 微博: 张三_88 |
| SM-038 | QQ — number-based | China legacy | QQ: 12345678 (numeric account), QQ号: 987654321 |
| SM-039 | Mastodon — fediverse handle | @user@instance | @johnsmith@mastodon.social, @janedoe@hachyderm.io, @sarah_chen@fosstodon.org |
| SM-040 | Bluesky — handle | AT Protocol | @johnsmith.bsky.social, @sarahchen.dev, bsky.app/profile/johnsmith.bsky.social |
| SM-041 | Threads — @handle | Meta | @johnsmith on Threads, threads.net/@janedoe |
| SM-042 | Twitch — username | Streaming | twitch.tv/johnsmith_streams, Twitch: jane_doe_gaming, t.tv/sarah_chen |
| SM-043 | GitHub — username | Dev platform | github.com/jsmith, @sarahchen on GitHub, gh: maria-garcia |
| SM-044 | Stack Overflow — user ID | Dev Q&A | stackoverflow.com/users/12345/john-smith, SO user 12345 |
| SM-045 | Dribbble / Behance — handle | Designer | dribbble.com/sarah_chen, behance.net/johnsmith |
| SM-046 | Medium — @handle | Writing | medium.com/@johnsmith, @sarah.chen on Medium |
| SM-047 | Substack — username | Newsletter | johnsmith.substack.com, substack.com/@janedoe |
| SM-048 | Patreon — username | Creator | patreon.com/johnsmith, Patreon: jane_doe |
| SM-049 | OnlyFans — username | Creator | onlyfans.com/sarah_chen (sensitive context — note adult platform) |
| SM-050 | Clubhouse — handle | Audio | clubhouse.com/@johnsmith, Clubhouse: @jane_doe |
| SM-051 | Tumblr — handle | Microblog | johnsmith.tumblr.com, @sarah_chen on Tumblr |
| SM-052 | Flickr — username | Photo | flickr.com/photos/johnsmith99, Flickr: jane_doe_photos |
| SM-053 | Vimeo — username | Video | vimeo.com/johnsmith, Vimeo: sarah_chen_films |
| SM-054 | Goodreads — username | Reading | goodreads.com/johnsmith_reads, Goodreads: sarah_chen_books |
| SM-055 | Strava — athlete ID | Fitness | strava.com/athletes/12345678, Strava: John Smith |
| SM-056 | Spotify — user URI | Music | spotify:user:johnsmith99, open.spotify.com/user/johnsmith99 |
| SM-057 | SoundCloud — username | Music | soundcloud.com/johnsmith_music, SC: sarah_chen_beats |
| SM-058 | Bandcamp — artist URL | Music | johnsmith.bandcamp.com, sarah-chen.bandcamp.com |
| SM-059 | Profile bio mention | Bio content | "📷 @johnsmith on IG | 🐦 @johnsmith_99 on Twitter | 💼 LinkedIn: john-smith-12345" |
| SM-060 | Cross-platform handle list | Multi-platform | "Find me everywhere: @johnsmith on Twitter/IG/TikTok/Threads, john-smith-12345 on LinkedIn" |
| SM-061 | Handle in email signature | Pro signature | "John Smith \| Senior Engineer \| Twitter: @johnsmith_dev \| LinkedIn: /in/john-smith-12345" |
| SM-062 | Mentioned in tweet / post | Inline | "Thanks @johnsmith for the heads up!"; "cc @janedoe, @sarah_chen on this update" |
| SM-063 | Display name + handle | Combined | "John Smith (@johnsmith_dev)"; "Sarah Chen ✓ @sarahchen" |
| SM-064 | Private / locked account marker | Privacy | "@johnsmith_priv (private account)"; "🔒 protected tweets"; "Locked profile" |
| SM-065 | Deactivated / suspended account | Status | "@johnsmith — account suspended"; "User deleted account 2024-03-15" |
| SM-066 | Anonymous / pseudonymous account | Throwaway | "@throwaway_acct_99", "@anon_user_12345", "u/throwaway-account" |
| SM-067 | Verified / blue check status | Verification | @johnsmith ✓ (Twitter Blue verified), @company ✅ (verified business), 🛡️ government account |
| SM-068 | Handle with country/locale suffix | Regional | @johnsmith_uk, @janedoe_au, @sarah.chen.jp, @maria_garcia_es |
| SM-069 | Handle with job role suffix | Pro | @johnsmith_dev, @janedoe_pm, @sarah_chen_ml, @maria_garcia_design |
| SM-070 | Handle with year suffix | Disambiguation | @johnsmith99, @janedoe_2020, @sarahchen_85 |
| SM-071 | Multilingual handle / non-Latin | Native script | @田中太郎 (JP), @иван_петров (RU), @محمد_احمد (AR), @שרה_כהן (HE) |
| SM-072 | Emoji in handle | Modern | @johnsmith_🚀, @janedoe_🌎, @sarah.chen.🎨 (some platforms allow) |
| SM-073 | Numeric-only handle | Numbers | @12345, @987654, @8675309 |
| SM-074 | OCR-distorted handle | Char substitution | @j0hnsm1th (0 for o, 1 for i), @j0hn_sm1th (zero for o), @sarahch3n (3 for e) |
| SM-075 | Masked / partial handle | Privacy-redacted | @joh***ith, @j***h on Twitter, @***** (redacted) |
| SM-076 | Anonymized placeholder | Standard generic | @username, @user1234, @example_user |
| SM-077 | Sentence-boundary tricky | Trailing punctuation | "Follow me @johnsmith.", "Was it @janedoe?", "DM me @sarah_chen!" |
| SM-078 | Adjacency-tight | No separator | "JohnSmith@johnsmith_devTwitter", "Sarah Chen@sarahchen.bsky.social" |
| SM-079 | Handle in JSON | Structured | "twitter_handle": "@johnsmith", "instagram": "johnsmith_99", "linkedin_slug": "john-smith-12345" |
| SM-080 | Handle in KV | Form field | twitter=@johnsmith, IG: johnsmith_99, LINKEDIN: john-smith-12345 |
| SM-081 | Handle in XML | Markup | <twitter>@johnsmith</twitter>, <social platform="instagram">johnsmith_99</social> |
| SM-082 | Handle in CSV | Tabular | "Smith","John","@johnsmith","johnsmith_99","john-smith-12345" |
| SM-083 | Multilingual context label | Various | Social Media (EN), Réseaux sociaux (FR), Soziale Medien (DE), Redes sociales (ES), Social media (IT), Mídias sociais (PT), ソーシャルメディア (JP), 소셜 미디어 (KR), 社交媒体 (ZH), Соцсети (RU), Sosyal medya (TR), وسائل التواصل (AR), מדיה חברתית (HE), โซเชียลมีเดีย (TH) |
| SM-084 | Handle in dating profile context | Identity | "Tinder: John, 32, NYC; IG: @johnsmith_99 for more"; "Hinge profile + Instagram tag" |
| SM-085 | Handle in job application | Recruitment | "LinkedIn: linkedin.com/in/john-smith-12345; GitHub: github.com/jsmith; Portfolio: johnsmith.dev" |
| SM-086 | Handle in legal / court | Discovery | "Defendant's social media discovery: Twitter @johnsmith, posts from 2020-2024 subpoenaed" |
| SM-087 | Handle in marketing / influencer | Brand | "Influencer @sarah.chen (250K followers), partnership rate $5K/post" |
| SM-088 | Handle linked to phone (recovery) | Account recovery | "Recovery phone for @johnsmith: +1-917-555-0123 (Twitter 2FA)" |
| SM-089 | Handle linked to email | Account recovery | "Account email for @johnsmith: johnsmith99@gmail.com" |
| SM-090 | Old / migrated handle | History | "Previously @johnsmith_old (changed to @johnsmith in 2023)"; "Migrated from Twitter to Bluesky" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | SM-074 |
| Masked / partial / redacted | ✓ | SM-075, SM-076 |
| Multilingual context labels | ✓ | SM-083 |
| Platform coverage | ✓ | SM-001 to SM-058 (covers 30+ platforms: Twitter/X, FB, IG, LinkedIn, TikTok, Snap, YouTube, Reddit, Discord, Pinterest, Telegram, WhatsApp, WeChat, Line, Kakao, VK, Weibo, QQ, Mastodon, Bluesky, Threads, Twitch, GitHub, Stack Overflow, Dribbble, Behance, Medium, Substack, Patreon, OnlyFans, Clubhouse, Tumblr, Flickr, Vimeo, Goodreads, Strava, Spotify, SoundCloud, Bandcamp) |
| Format types | ✓ | SM-002, SM-005, SM-009 (URLs), SM-003, SM-006, SM-012, SM-020, SM-027 (numeric IDs), SM-001, SM-008, SM-014 (handles) |
| Non-Latin scripts | ✓ | SM-033 (Chinese WeChat), SM-034 (Japanese Line), SM-035 (Korean), SM-036 (Russian), SM-037 (Chinese Weibo), SM-071 |
| Verification / privacy markers | ✓ | SM-004, SM-067 (verified), SM-064, SM-066 (private/anon), SM-065 (suspended) |
| In structured data | ✓ | SM-079, SM-080, SM-081, SM-082 |
| Adjacency-tight | ✓ | SM-078 |
| Sentence-boundary tricky | ✓ | SM-077 |
| Domain-embedded (bio/email sig/dating/job app/legal/marketing) | ✓ | SM-059, SM-061, SM-084, SM-085, SM-086, SM-087 |
| Cross-platform identity bundles | ✓ | SM-060, SM-085 |
| Recovery / linked credentials | ✓ | SM-088, SM-089 |
| Lifecycle (changed handle, migrated) | ✓ | SM-090 |
| Modern fediverse / decentralized | ✓ | SM-039, SM-040 |

**Total patterns for Social_Media_Identifiers: 90**

---

## Entity 47: Static_IP_Address

Internet Protocol addresses — IPv4 / IPv6, public / private, in various contexts.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| IP-001 | IPv4 dotted decimal — public | Standard | 8.8.8.8, 1.1.1.1, 142.250.80.46, 52.84.150.39 |
| IP-002 | IPv4 dotted decimal — private RFC 1918 | Private | 192.168.1.1, 10.0.0.1, 172.16.0.1, 10.1.2.3 |
| IP-003 | IPv4 with leading zeros (non-standard) | Padded | 192.168.001.001, 010.000.000.001 (technically valid but warning: octal) |
| IP-004 | IPv4 with label "IP:" | Form context | IP: 192.168.1.1, IP Address: 8.8.8.8, IPv4: 142.250.80.46 |
| IP-005 | IPv4 localhost | Loopback | 127.0.0.1, localhost, lo (interface) |
| IP-006 | IPv4 with port (host:port) | Service | 192.168.1.1:8080, 8.8.8.8:53, 10.0.0.1:22, [host]:port |
| IP-007 | IPv4 CIDR notation | Subnet | 192.168.1.0/24, 10.0.0.0/8, 172.16.0.0/12, 0.0.0.0/0 |
| IP-008 | IPv4 with subnet mask | Mask notation | 192.168.1.1 / 255.255.255.0; netmask 255.255.0.0 |
| IP-009 | IPv4 broadcast | Special | 255.255.255.255, 192.168.1.255 (subnet broadcast) |
| IP-010 | IPv4 multicast (224.0.0.0/4) | Group | 224.0.0.1 (all hosts), 239.255.255.250 (SSDP) |
| IP-011 | IPv4 reserved/link-local | APIPA | 169.254.1.100 (link-local APIPA), 0.0.0.0 (default route) |
| IP-012 | IPv6 full form | Standard | 2001:0db8:85a3:0000:0000:8a2e:0370:7334 |
| IP-013 | IPv6 compressed | Shorthand | 2001:db8:85a3::8a2e:370:7334, ::1 (loopback), ::ffff:192.0.2.1 |
| IP-014 | IPv6 localhost | Loopback | ::1, [::1] (URL form) |
| IP-015 | IPv6 with port (bracket form) | Service | [2001:db8::1]:8080, [::1]:443 |
| IP-016 | IPv6 prefix / CIDR | Subnet | 2001:db8::/32, 2001:db8:85a3::/48, ::/0 (default) |
| IP-017 | IPv6 link-local | Auto-config | fe80::1, fe80::a00:27ff:fe2e:9b51%eth0 (with zone) |
| IP-018 | IPv6 unique local (ULA) | Private equivalent | fc00::/7, fd12:3456:789a::1 (private IPv6) |
| IP-019 | IPv6 multicast | Group | ff02::1 (all-nodes link-local), ff02::2 (all-routers) |
| IP-020 | IPv6 dual-stack notation | Mixed | ::ffff:192.0.2.1 (IPv4-mapped), 2001:db8:0:0:0:0:1.2.3.4 |
| IP-021 | IPv6 with scope/zone ID | Interface | fe80::1%eth0, fe80::1%25eth0 (URL-encoded percent), fe80::1%lo0 |
| IP-022 | IPv4 in URL | Embedded | http://192.168.1.1/admin, https://8.8.8.8/, ssh://10.0.0.1 |
| IP-023 | IPv6 in URL | Embedded | https://[2001:db8::1]/, http://[::1]:8080 |
| IP-024 | IP in DNS A record | DNS | "example.com A 142.250.80.46"; "example.com IN A 8.8.8.8 (TTL 3600)" |
| IP-025 | IP in DNS AAAA record | DNS IPv6 | "example.com AAAA 2001:db8::1"; "example.com IN AAAA 2606:4700::1111" |
| IP-026 | IP in DNS PTR (reverse) | Reverse DNS | "46.80.250.142.in-addr.arpa. PTR example.com"; "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.2.ip6.arpa." |
| IP-027 | IP in HTTP header | Web | "X-Forwarded-For: 192.168.1.100, 142.250.80.46"; "X-Real-IP: 10.0.0.5"; "Client-IP: 8.8.8.8" |
| IP-028 | IP in email Received header | RFC 5322 | "Received: from mail.example.com ([8.8.8.8]) by smtp.example.com" |
| IP-029 | IP in firewall rule | Network | "ALLOW from 192.168.1.0/24 to any port 443"; "iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT" |
| IP-030 | IP in access log | Web log | "192.168.1.100 - - [15/Mar/2024:14:30:22 +0000] \"GET / HTTP/1.1\" 200" (Apache CLF); "8.8.8.8 GET /api" |
| IP-031 | IP in auth / SSH log | Security log | "Failed password for invalid user admin from 192.168.1.100 port 54321 ssh2"; "Accepted publickey from 10.0.0.5" |
| IP-032 | IP in VPN session log | VPN | "User johnsmith VPN connected from 142.250.80.46 (US) at 2024-03-15 09:15"; "WireGuard peer 10.0.0.5 connected" |
| IP-033 | IP with geo-IP context | Geolocation | "IP 8.8.8.8 → Mountain View, CA, USA (Google LLC)"; "GeoIP: 142.250.80.46 = US/CA" |
| IP-034 | IP with WHOIS data | Registration | "IP 142.250.80.46 — netname: GOOGLE — country: US — ASN: AS15169 Google LLC" |
| IP-035 | IP in network device config | Router/switch | "interface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"; "set interfaces ge-0/0/0 unit 0 family inet address 10.0.0.1/24" |
| IP-036 | IP in DHCP lease | DHCP | "192.168.1.100 johnsmith-laptop 24h lease, MAC aa:bb:cc:dd:ee:ff"; "DHCP lease 10.0.0.5 → 00:50:56:c0:00:08" |
| IP-037 | IP in MAC ARP pair | Layer 2 | "ARP: 192.168.1.100 at aa:bb:cc:dd:ee:ff on eth0"; "ARP cache: 10.0.0.5 → 00:1a:2b:3c:4d:5e" |
| IP-038 | IP in cloud allocation | Cloud | "AWS EC2 instance i-1234567890abcdef0: Private 10.0.0.5, Public 54.123.45.67"; "GCP VM external IP: 35.123.45.67" |
| IP-039 | IP in container / Kubernetes | K8s | "Pod IP: 10.244.1.5 (CNI assigned)"; "Service ClusterIP: 10.96.0.1"; "kubectl describe pod: 10.244.1.5" |
| IP-040 | IP in CDN / edge | CDN | "Cloudflare edge IP: 104.16.123.45"; "Fastly POP IP: 151.101.1.69"; "Akamai edge: 23.45.67.89" |
| IP-041 | IP — VPN exit / proxy | Anonymization | "VPN exit IP: 185.220.100.252 (Tor exit node)"; "Proxy: 192.0.2.50 (NordVPN London)" |
| IP-042 | IP in fraud / risk score | Security | "IP 192.0.2.5 — risk score 87/100 (known proxy, prior fraud)"; "Risk Engine: blacklisted IP" |
| IP-043 | IP in spam / abuse blocklist | RBL | "IP listed on Spamhaus SBL"; "Blocklist: 192.0.2.5 — SBL-12345"; "abuseipdb.com: 90% confidence" |
| IP-044 | IP in NetFlow / sFlow | Network telemetry | "NetFlow record: src 192.168.1.100 → dst 142.250.80.46:443, 5KB, TCP"; "sFlow sample" |
| IP-045 | IP in SIEM / incident | Security event | "SIEM alert: brute force from 192.0.2.5 — 500 failed logins in 1 hour"; "Splunk: src_ip=10.0.0.5" |
| IP-046 | IP in mail server (MX-resolved) | Email infra | "MX example.com → mail.example.com → A 142.250.80.46" |
| IP-047 | IP in router CLI output | Cisco/Juniper | "show ip interface brief\nGigabitEthernet0/0    192.168.1.1   YES NVRAM  up    up" |
| IP-048 | IP in BGP / routing | Routing protocol | "BGP advertise 192.0.2.0/24 to AS15169"; "AS-PATH: 65001 65002 65003"; "next-hop 10.0.0.1" |
| IP-049 | IP in OSPF / IGP | Interior | "OSPF neighbor 10.1.1.1 Full/DR on eth0"; "IS-IS neighbor 192.168.10.2" |
| IP-050 | IP in CGNAT range | Carrier-grade NAT | "100.64.0.5 (CGNAT range 100.64.0.0/10)"; "shared address space" |
| IP-051 | IP allocation by ISP / ARIN | Public allocation | "Comcast assigned: 73.45.67.89 (residential)"; "Verizon FiOS: 71.123.45.67"; "ARIN whois: AT&T" |
| IP-052 | IP — static vs dynamic flag | Type | "Static IP 192.168.1.50 (assigned)"; "Dynamic IP via DHCP, current lease 192.168.1.105" |
| IP-053 | IP in IoT device | IoT | "Nest thermostat IP: 192.168.1.42"; "Smart light bulb LIFX 192.168.1.55"; "Roomba 10.0.0.99" |
| IP-054 | IP in /etc/hosts | Host file | "10.0.0.1 example.local\n192.168.1.100 johnsmith-laptop" |
| IP-055 | IP in WHOIS / RIPE / APNIC | Regional registry | "RIPE whois: 81.2.69.142 — netname: EUROPE-NET"; "APNIC: 110.4.30.1 — China Telecom" |
| IP-056 | IP in JSON | Structured | "ip_address": "192.168.1.100", "remote_ip": "8.8.8.8", "ipv6": "2001:db8::1" |
| IP-057 | IP in KV | Form field | ip=192.168.1.100, REMOTE_IP: 8.8.8.8, IPV6: 2001:db8::1 |
| IP-058 | IP in XML | Markup | <ip_address>192.168.1.100</ip_address>, <remote_ip family="ipv6">::1</remote_ip> |
| IP-059 | IP in CSV | Tabular | "Smith","John","192.168.1.100","2024-03-15","Login" |
| IP-060 | OCR-distorted IP | Char substitution | "l92.l68.l.l" (l for 1), "lO.O.O.l" (O for 0); "8.8.8.8" → "8 8.8 8" (lost dot) |
| IP-061 | Masked / partial IP | Privacy-redacted | "192.168.1.***", "192.168.***.***", "8.8.8.x", "[IP redacted]" |
| IP-062 | Anonymized placeholder | Standard generic | "0.0.0.0", "192.0.2.1" (RFC 5737 documentation), "<IP>", "x.x.x.x" |
| IP-063 | Sentence-boundary tricky | Trailing punctuation | "His IP is 192.168.1.100.", "Was the IP 8.8.8.8?", "Server: 10.0.0.5!" |
| IP-064 | Adjacency-tight | No separator | "user192.168.1.100login", "John Smith 8.8.8.8 2024-03-15" |
| IP-065 | Multilingual context label | Various | IP Address (EN), Adresse IP (FR), IP-Adresse (DE), Dirección IP (ES), Indirizzo IP (IT), Endereço IP (PT), IPアドレス (JP), IP 주소 (KR), IP地址 (ZH), IP-адрес (RU), IP adresi (TR), عنوان IP (AR), כתובת IP (HE), ที่อยู่ IP (TH) |
| IP-066 | IP linked to user identity | Personally-identifying | "User johnsmith@acme.com logged in from 192.168.1.100 at 2024-03-15 14:30 UTC" |
| IP-067 | IP with hostname (FQDN) | Combined | "host: johnsmith-laptop.acme.local, IP: 192.168.1.100"; "fqdn: server.example.com, A: 142.250.80.46" |
| IP-068 | IP in court / legal discovery | Subpoena | "Subpoena to Comcast for subscriber identity behind IP 73.45.67.89 on 2024-03-15 14:30 EST" |
| IP-069 | IP in audit / compliance log | SOX / HIPAA audit | "Audit log: user accessed PHI from IP 10.0.0.5, action: view patient record, time: 2024-03-15" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | IP-060 |
| Masked / partial / redacted | ✓ | IP-061, IP-062 |
| Multilingual context labels | ✓ | IP-065 |
| IPv4 / IPv6 / dual-stack | ✓ | IP-001 to IP-011 (IPv4), IP-012 to IP-021 (IPv6), IP-020 (dual-stack) |
| Public / private / special | ✓ | IP-001 (public), IP-002 (private), IP-005 (loopback), IP-009 (broadcast), IP-010 (multicast), IP-011 (link-local), IP-050 (CGNAT) |
| Embedded in URL / port / CIDR | ✓ | IP-006, IP-007, IP-022, IP-023 |
| DNS / network protocol contexts | ✓ | IP-024 to IP-026 (DNS), IP-028 (email headers), IP-029 (firewall), IP-037 (ARP), IP-046 (mail), IP-048 (BGP), IP-049 (OSPF) |
| Logs / telemetry / SIEM | ✓ | IP-030, IP-031, IP-032, IP-044, IP-045 |
| Cloud / container / IoT | ✓ | IP-038, IP-039, IP-040, IP-053 |
| Geo / WHOIS / registry | ✓ | IP-033, IP-034, IP-055 |
| Security / risk / anonymization | ✓ | IP-041, IP-042, IP-043 |
| In structured data | ✓ | IP-056, IP-057, IP-058, IP-059 |
| Adjacency-tight | ✓ | IP-064 |
| Sentence-boundary tricky | ✓ | IP-063 |
| Domain-embedded (legal/audit) | ✓ | IP-066, IP-068, IP-069 |
| Allocation / lifecycle | ✓ | IP-036, IP-051, IP-052 |
| Combined identifiers (MAC, hostname, user) | ✓ | IP-037, IP-067, IP-066 |

**Total patterns for Static_IP_Address: 69**

---

## Entity 48: Password

Authentication credentials — plaintext, hashed, partial. Highest-sensitivity credential data.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| PWD-001 | Plaintext password in chat | Bad practice | "My password is hunter2"; "the pw is P@ssw0rd123"; "password = MySecret2024!" |
| PWD-002 | Plaintext with "Password:" label | Form / KV | Password: MySecret123!, PASSWORD: hunter2, Passwd: P@ssw0rd |
| PWD-003 | Plaintext in email body | Insecure transmission | "Your new password is TempPass2024! — please change it on first login" |
| PWD-004 | Password in URL query string | Insecure | https://example.com/login?user=john&pass=hunter2; ?password=secret123 |
| PWD-005 | Password in config file | Bad practice (.env etc) | DB_PASSWORD=MySecret123!; api_key="abc123"; SMTP_PASS=hunter2 |
| PWD-006 | Password in JSON | API request | "password": "hunter2", "pwd": "MySecret123!", "passwd": "P@ssw0rd" |
| PWD-007 | Password in KV | Form field | password=hunter2, PASSWORD: MySecret, pwd=P@ssw0rd123 |
| PWD-008 | Password in XML | Markup | <password>hunter2</password>, <pwd>MySecret123!</pwd> |
| PWD-009 | Password in CSV | Tabular (bad practice) | "Smith","John","jsmith","hunter2","2024-03-15" |
| PWD-010 | Default password | Factory-set | "admin/admin", "root/toor", "default/default", "user/password", "1234/1234" |
| PWD-011 | Common weak passwords | Insecure | password, 123456, qwerty, letmein, welcome, abc123, password1, iloveyou |
| PWD-012 | Strong password example | Best practice | "$Tr0ng_P@s5w0rd!2024", "correct horse battery staple" (passphrase) |
| PWD-013 | Passphrase | Multi-word | "correct horse battery staple"; "my dog likes blue cheese on Tuesdays"; "diceware: alarm clock daisy weekend" |
| PWD-014 | Temporary password | Reset | "Temporary password: Temp@2024!Reset — must change on next login"; "One-time password assigned" |
| PWD-015 | Password reset URL with token | Reset flow | "https://example.com/reset?token=eyJhbGciOiJ...Xb3c8"; "Reset link: example.com/reset/abc123def456" |
| PWD-016 | Email confirmation token | Verification | "https://example.com/verify?token=eyJhbGc..."; "Click to confirm: example.com/verify/xyz789" |
| PWD-017 | One-Time Password (OTP) | 2FA code | "Your OTP is 123456"; "Verification code: 654321"; "Authenticator code: 987654 (valid 30s)" |
| PWD-018 | TOTP token (Google Authenticator etc) | RFC 6238 | "TOTP code: 482915"; "Authenticator: 6-digit, refreshes every 30 seconds" |
| PWD-019 | HOTP token | Counter-based | "HOTP token: 123456 (counter 42)" |
| PWD-020 | SMS-delivered code | Text 2FA | "Your verification code is 123456. Don't share."; "SMS code from Twitter: 7-digit code" |
| PWD-021 | Email-delivered code | Email 2FA | "Your login code: 654321 (expires in 10 minutes)" |
| PWD-022 | Backup / recovery codes | Account recovery | "Backup codes:\n1. xz4f-7m9n-vb2k\n2. q8w7-e6r5-t4y3\n3. a1s2-d3f4-g5h6" |
| PWD-023 | Master password | Manager | "1Password master password"; "LastPass master: ********"; "Bitwarden vault password" |
| PWD-024 | PIN — numeric (4 digits) | ATM/phone | "PIN: 1234"; "Card PIN: 5678"; "Voicemail PIN: 9876" |
| PWD-025 | PIN — numeric (6 digits) | Newer | "PIN: 123456"; "Bank PIN: 654321"; "iPhone passcode: 654321" |
| PWD-026 | PIN — numeric (8 digits) | Enterprise | "PIN: 12345678"; "Long PIN for secure system" |
| PWD-027 | Pattern unlock (Android) | Mobile | "Pattern: top-left → center → bottom-right → top-right (5-dot pattern)" |
| PWD-028 | Biometric token (FaceID/TouchID) | Biometric | "FaceID enrolled"; "Touch ID enabled"; "Fingerprint hash: abc123def456" (template, not actual print) |
| PWD-029 | API key | API auth | "API_KEY=sk-proj-abc123def456ghi789"; "X-API-Key: 1234567890abcdef"; "api_key=AIzaSyD..." |
| PWD-030 | Bearer token | OAuth | "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."; "Access token: ya29.a0AfH6..." |
| PWD-031 | JWT (JSON Web Token) | Token format | "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NSJ9.abc123XYZsignature"; "JWT payload + signature" |
| PWD-032 | OAuth refresh token | Long-lived | "refresh_token: 1//0gRkjLM_XYZ-abc..."; "Refresh: tk_refresh_abc123def456" |
| PWD-033 | Personal Access Token (PAT) | Dev | "GitHub PAT: ghp_abc123def456ghi789"; "GitLab PAT: glpat-abc123"; "Personal Access Token" |
| PWD-034 | SSH private key (note) | Asymmetric | "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAA..."; "id_rsa file contents" |
| PWD-035 | App-specific password | Per-app | "Gmail app password: abcd efgh ijkl mnop (for IMAP)"; "Two-factor app password" |
| PWD-036 | Recovery / Secret question answer | Knowledge | "Security Q: First pet's name? A: Mittens"; "Mother's maiden name: Smith" |
| PWD-037 | Hashed password — MD5 | Weak hash | "5f4dcc3b5aa765d61d8327deb882cf99" (md5 of "password"); 32-char hex MD5 |
| PWD-038 | Hashed password — SHA-1 | Weak hash | "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8" (sha1 of "password"); 40-char hex SHA-1 |
| PWD-039 | Hashed password — SHA-256 | Stronger | "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8" (sha256 of "password"); 64-char hex SHA-256 |
| PWD-040 | Hashed password — bcrypt | Adaptive | "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"; bcrypt format $2a/$2b/$2y |
| PWD-041 | Hashed password — scrypt | Memory-hard | "$scrypt$N=16384,r=8,p=1$saltvalue$hashvalue" |
| PWD-042 | Hashed password — Argon2 | Modern | "$argon2id$v=19$m=65536,t=3,p=4$saltvalue$hashvalue" |
| PWD-043 | Hashed — PBKDF2 | KDF | "pbkdf2_sha256$390000$saltvalue$hashvalue"; Django format |
| PWD-044 | Salted hash | With salt | "salt: a1b2c3d4 + hash: f5e6d7c8..."; "$1$saltyhash$hashvalue (MD5 crypt)" |
| PWD-045 | Password in /etc/shadow | Unix shadow | "root:$6$saltvalue$hashvalue:19000:0:99999:7:::"; "john:$6$abc$xyz:..." |
| PWD-046 | NTLM / NT hash | Windows | "NT hash: 8846F7EAEE8FB117AD06BDD830B7586C"; LM:NT format |
| PWD-047 | Kerberos hash / keytab | Windows AD | "krb5 keytab; aes256-cts-hmac-sha1-96 key" |
| PWD-048 | Encrypted password — AES | Encrypted | "Encrypted password (AES-256-GCM): base64-encoded ciphertext + IV + tag" |
| PWD-049 | Password in database column | Bad practice | "users.password = 'plaintext_password'"; "INSERT INTO users (password) VALUES ('hunter2')" |
| PWD-050 | Password complexity description | Policy | "Min 12 chars, 1 upper, 1 lower, 1 number, 1 special, no repeats >2, no dictionary words" |
| PWD-051 | Password expiry / rotation | Policy | "Password expires 2024-09-15 (90 days)"; "Must change every 90 days"; "Last changed 2024-03-15" |
| PWD-052 | Password history (no reuse) | Policy | "Cannot reuse last 12 passwords"; "Password history: 5 previous" |
| PWD-053 | Account lockout after attempts | Policy | "Account locked after 5 failed attempts; reset by admin"; "Cooldown 30 min after lockout" |
| PWD-054 | Password manager export | Backup | "1Password export 1pif"; "LastPass CSV export"; "Bitwarden JSON export with passwords" |
| PWD-055 | Hashed in JSON | Structured | "password_hash": "$2b$12$...", "salt": "abc123", "algorithm": "bcrypt" |
| PWD-056 | Password in KV (env) | Env file | DB_PASSWORD=prod_password_123; DATABASE_PASSWORD="MyS3cret!" |
| PWD-057 | Password in XML | Markup | <password algorithm="bcrypt">$2b$12$...</password> |
| PWD-058 | Password in CSV | Tabular | "Smith","John","jsmith","$2b$12$...","2024-03-15" |
| PWD-059 | Multilingual context label | Various | Password (EN), Mot de passe (FR), Passwort (DE), Contraseña (ES), Password (IT), Senha (PT), パスワード (JP), 비밀번호 (KR), 密码 (ZH), Пароль (RU), Şifre (TR), كلمة المرور (AR), סיסמה (HE), รหัสผ่าน (TH) |
| PWD-060 | OCR-distorted password | Char substitution | "Pa55w0rd" (5 for s, 0 for o — common substitution), "P@$$w0rd!" (mixed); "hunter2" → "huntr2" |
| PWD-061 | Masked password | Display masking | "Password: ********"; "Pwd: •••••••"; "***" (typed); "[password redacted]" |
| PWD-062 | Anonymized placeholder | Standard generic | "Password: <REDACTED>"; "Password: ******"; "<PASSWORD>"; "Default: changeme" |
| PWD-063 | Sentence-boundary tricky | Trailing punctuation | "His password is hunter2.", "What's the pwd?", "Don't share your password!" |
| PWD-064 | Adjacency-tight | No separator | "johnsmithpasswordhunter2", "User:john_smith,PW:secret123" |
| PWD-065 | Password sticky note (visible) | Bad practice | "Password on monitor sticky note: WelcomeAcme2024!"; "Written under keyboard" |
| PWD-066 | Password leaked in data breach | Breach | "Found in HaveIBeenPwned: johnsmith@gmail.com — 12 breaches, password exposed"; "Combo list: email:password" |
| PWD-067 | Combo list / credential stuffing | Breach data | "user@example.com:password123"; "john.smith@gmail.com:Welcome2020" |
| PWD-068 | Wifi password / network key | WPA | "WiFi: MyHomeWiFi / Password: ihatemyneighbor"; "WPA2 key: HouseGuestNet2024"; "PSK: networkpassword123" |
| PWD-069 | Encryption passphrase | Crypto wallet | "BIP-39 mnemonic: abandon ability able about above absent absorb abstract absurd abuse access accident"; "12-word seed phrase" |
| PWD-070 | Recovery seed phrase | Crypto | "Wallet recovery: abandon ability able about... (12 or 24 words)"; "Ledger 24-word seed" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | PWD-060 |
| Masked / partial / redacted | ✓ | PWD-061, PWD-062 |
| Multilingual context labels | ✓ | PWD-059 |
| Plaintext contexts | ✓ | PWD-001 to PWD-009 (chat, label, email, URL, config, JSON, KV, XML, CSV) |
| Hash algorithm coverage | ✓ | PWD-037 (MD5), PWD-038 (SHA-1), PWD-039 (SHA-256), PWD-040 (bcrypt), PWD-041 (scrypt), PWD-042 (Argon2), PWD-043 (PBKDF2), PWD-044 (salted), PWD-045 (/etc/shadow), PWD-046 (NTLM), PWD-047 (Kerberos) |
| 2FA / OTP / Tokens | ✓ | PWD-017, PWD-018, PWD-019, PWD-020, PWD-021, PWD-022, PWD-030, PWD-031, PWD-032, PWD-033 |
| PIN / Pattern / Biometric | ✓ | PWD-024, PWD-025, PWD-026, PWD-027, PWD-028 |
| API / Token credentials | ✓ | PWD-029, PWD-030, PWD-031, PWD-032, PWD-033, PWD-034 |
| Recovery / Reset flows | ✓ | PWD-014, PWD-015, PWD-016, PWD-022 |
| In structured data | ✓ | PWD-006, PWD-007, PWD-008, PWD-009, PWD-055, PWD-056, PWD-057, PWD-058 |
| Adjacency-tight | ✓ | PWD-064 |
| Sentence-boundary tricky | ✓ | PWD-063 |
| Common weak / strong patterns | ✓ | PWD-010, PWD-011, PWD-012 |
| Policy / lifecycle | ✓ | PWD-050, PWD-051, PWD-052, PWD-053 |
| Domain-embedded (sticky note/breach/combo list/wifi) | ✓ | PWD-065, PWD-066, PWD-067, PWD-068 |
| Crypto wallet seed phrase | ✓ | PWD-069, PWD-070 |
| Knowledge-based / Q&A | ✓ | PWD-036 |

**Total patterns for Password: 70**

---

## Entity 49: Date_Time

Date and time values — when they identify or are tied to a specific person/event in a PII context.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| DT-001 | ISO 8601 date — basic | YYYY-MM-DD | 2024-03-15, 1985-07-22, 2030-12-31 |
| DT-002 | ISO 8601 datetime | Combined | 2024-03-15T14:30:22Z, 2024-03-15T14:30:22+05:30, 2024-03-15T14:30:22.123456Z |
| DT-003 | ISO 8601 with timezone offset | TZ-aware | 2024-03-15T14:30:22-05:00 (EST), 2024-03-15T09:30:22+00:00 (UTC), 2024-03-15T19:00:22+09:00 (JST) |
| DT-004 | ISO 8601 date with week | Week date | 2024-W11, 2024-W11-5 (Friday of week 11), 2024-W42-3 |
| DT-005 | ISO 8601 ordinal date | Day-of-year | 2024-074 (March 15, day 74 of 2024) |
| DT-006 | US date MM/DD/YYYY | Slash | 03/15/2024, 12/31/2025, 7/4/1776 |
| DT-007 | US date M/D/YY | Short year | 3/15/24, 12/31/25, 7/4/76 |
| DT-008 | European date DD/MM/YYYY | Day-first | 15/03/2024, 31/12/2025, 04/07/1776 (UK) |
| DT-009 | European date DD.MM.YYYY | Period sep | 15.03.2024 (DE), 31.12.2025, 04.07.1776 |
| DT-010 | European date DD-MM-YYYY | Dash sep | 15-03-2024 (NL), 31-12-2025 |
| DT-011 | Japanese date YYYY年MM月DD日 | Kanji format | 2024年3月15日, 令和6年3月15日 (Reiwa 6) |
| DT-012 | Korean date YYYY년 MM월 DD일 | Hangul | 2024년 3월 15일 |
| DT-013 | Chinese date YYYY年MM月DD日 | Chinese | 2024年3月15日, 2024年3月15日 |
| DT-014 | Written English — full | Word form | March 15, 2024; The fifteenth of March, 2024; March 15th, 2024 |
| DT-015 | Written English — abbreviated | Short month | Mar 15, 2024; 15 Mar 2024; 15-Mar-2024; Mar. 15, '24 |
| DT-016 | Written English — ordinal | "th"/"st"/"nd"/"rd" | March 15th, 2024; July 4th, 1776; the 22nd of July |
| DT-017 | Written French | French | 15 mars 2024, le 15 mars 2024, vendredi 15 mars 2024 |
| DT-018 | Written German | German | 15. März 2024, 15. März, Mittwoch der 15. März 2024 |
| DT-019 | Written Spanish | Spanish | 15 de marzo de 2024, viernes 15 de marzo de 2024 |
| DT-020 | Written Italian | Italian | 15 marzo 2024, venerdì 15 marzo 2024 |
| DT-021 | Written Portuguese | Portuguese | 15 de março de 2024, sexta-feira, 15 de março de 2024 |
| DT-022 | Written Dutch | Dutch | 15 maart 2024, vrijdag 15 maart 2024 |
| DT-023 | Written Russian | Russian | 15 марта 2024 г., 15.03.2024, пятница, 15 марта 2024 года |
| DT-024 | Written Arabic | Arabic | 15 مارس 2024, ١٥/٣/٢٠٢٤ (Arabic-Indic digits) |
| DT-025 | Written Hebrew | Hebrew | 15 במרץ 2024, יום שישי, 15 במרץ |
| DT-026 | Era-based — Japanese Reiwa | Era | 令和6年3月15日 (Reiwa 6), R6.3.15 |
| DT-027 | Era-based — Thai Buddhist | Buddhist Era | 15 มีนาคม 2567 (BE 2567 = 2024 CE), 2567 |
| DT-028 | Era-based — Hebrew | Hebrew calendar | כ"ב באדר ב' תשפ"ד (March 2024 equivalent), 22 Adar II 5784 |
| DT-029 | Era-based — Hijri / Islamic | Lunar | 5 رمضان 1445 هـ (March 2024 equivalent), 5 Ramadan 1445 AH |
| DT-030 | Era-based — Persian (Jalali) | Persian | 25 اسفند 1402 (15 March 2024) |
| DT-031 | Era-based — Korean Dangi | Korean | 단기 4357년 3월 15일 |
| DT-032 | Era-based — Chinese Lunar | Lunar | 农历2024年正月初六 (lunar new year 2024) |
| DT-033 | Time only — 24-hour | Military | 14:30, 09:15, 23:59, 00:00 |
| DT-034 | Time only — 12-hour with AM/PM | Standard US | 2:30 PM, 9:15 AM, 11:59 PM, 12:00 noon |
| DT-035 | Time with seconds | Precise | 14:30:22, 09:15:00, 2:30:45 PM |
| DT-036 | Time with milliseconds | High-res | 14:30:22.123, 14:30:22.123456789 (nanos) |
| DT-037 | Time with timezone abbreviation | TZ named | 14:30 EST, 09:15 PST, 19:00 GMT, 02:00 JST, 11:00 AEST |
| DT-038 | Time with IANA timezone | TZ ID | 14:30 America/New_York; 09:15 Europe/London; 19:00 Asia/Tokyo |
| DT-039 | UTC offset notation | ±HH:MM | UTC+05:30, GMT-08:00, +09:00, -05:00 |
| DT-040 | Unix timestamp (seconds) | Epoch | 1710519022 (2024-03-15 14:30:22 UTC), 1234567890 (2009-02-13) |
| DT-041 | Unix timestamp (milliseconds) | ms epoch | 1710519022000, Date.now() = 1710519022123 |
| DT-042 | Unix timestamp (microseconds/nanos) | Sub-ms | 1710519022000000 (μs), 1710519022000000000 (ns) |
| DT-043 | RFC 2822 / Email Date | Email header | "Date: Fri, 15 Mar 2024 14:30:22 -0500"; "Wed, 21 Oct 2015 07:28:00 GMT" |
| DT-044 | RFC 5322 timestamp | Mail header | "Thu, 14 Mar 2024 19:30:22 +0000" |
| DT-045 | HTTP Date header | HTTP | "Date: Fri, 15 Mar 2024 14:30:22 GMT"; "Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT" |
| DT-046 | Cookie expires | Cookie | "expires=Wed, 21 Oct 2025 07:28:00 GMT"; Max-Age=3600 |
| DT-047 | JWT exp claim | Token expiry | "exp": 1710519022 (Unix seconds); "iat": 1710432622 |
| DT-048 | File mtime / ctime | Filesystem | "modified 2024-03-15 14:30"; "stat: mtime=1710519022"; "ls -l: Mar 15 14:30 file.txt" |
| DT-049 | Database timestamp | SQL | DATETIME '2024-03-15 14:30:22'; TIMESTAMP WITH TIME ZONE '2024-03-15 14:30:22+05:30' |
| DT-050 | Log timestamp (syslog) | Syslog format | "<14>Mar 15 14:30:22 host program: message"; "2024-03-15 14:30:22.123 INFO" |
| DT-051 | Apache / nginx access log | CLF | "[15/Mar/2024:14:30:22 +0000]"; "[15/Mar/2024:14:30:22 -0500]" |
| DT-052 | Compact YYYYMMDD | No separators | 20240315, 19850722, YYYYMMDDHHMMSS = 20240315143022 |
| DT-053 | Compact YYMMDD | Short | 240315, 850722 (ambiguous century) |
| DT-054 | Quarter notation | Fiscal | Q1 2024, 2024 Q1, FQ1, FY24 Q1, 2024-Q1, Q3 FY2024 |
| DT-055 | Fiscal year | FY | FY2024, FY24, Fiscal Year 2024 (Apr 2023 - Mar 2024 for India/Japan; varies) |
| DT-056 | Half-year | H1/H2 | H1 2024, 2024-H1, 1H24, First Half 2024 |
| DT-057 | Month-year only | MM/YYYY | 03/2024, March 2024, 2024-03, Mar '24, Q1 2024 |
| DT-058 | Year only | YYYY | 2024, 1985, '24, '85, the year 2024 |
| DT-059 | Decade reference | Era | the 1980s, the '90s, mid-2010s, late twentieth century |
| DT-060 | Century reference | Era | 21st century, the twentieth century, 19th C., circa 1800s |
| DT-061 | Relative — past | "X ago" | 3 days ago, 2 weeks ago, last month, last year, yesterday |
| DT-062 | Relative — future | "in X" | in 3 days, tomorrow, next month, next year, in 2 weeks |
| DT-063 | Date range | Range | 2024-03-15 to 2024-03-19; March 15-19, 2024; Mar 15 — Mar 22 |
| DT-064 | Duration / interval | Length | 5 days, 3 weeks, 2 months, 1 year 6 months, 90-day period |
| DT-065 | ISO 8601 duration | Spec format | P3D (3 days), PT1H30M (1h30m), P1Y6M (1y6m), P1Y2M3DT4H5M6S |
| DT-066 | Day of week — English | Weekday | Monday, Tuesday, Wed., Thursday, Fri, Sat, Sunday |
| DT-067 | Day of week — multilingual | Other langs | Lundi (FR), Montag (DE), Lunes (ES), Lunedì (IT), 月曜日 (JP), 월요일 (KR), 星期一 (ZH), Понедельник (RU) |
| DT-068 | Time of day descriptive | Vague | early morning, dawn, noon, afternoon, evening, dusk, late night, midnight |
| DT-069 | Astronomical reference | Sky-based | sunrise (06:15), sunset (18:42), solar noon, new moon, full moon, equinox, solstice |
| DT-070 | Recurring schedule | Cadence | every Monday, weekly on Tuesdays, biweekly, monthly on the 15th, quarterly review |
| DT-071 | Specific event-based | Anchored | "the day Kennedy was shot (1963-11-22)", "9/11 anniversary", "Y2K", "COVID lockdown start" |
| DT-072 | Holiday-anchored | Holiday | Christmas Day 2024, Thanksgiving 2024 (4th Thu Nov), Lunar New Year 2024, Eid al-Fitr 2024 |
| DT-073 | Date with day name prefix | Full | Friday, March 15, 2024; Vendredi 15 mars 2024 |
| DT-074 | Date + time combined | Combined formats | 2024-03-15 14:30, March 15, 2024 at 2:30 PM, 15.03.2024 14:30 |
| DT-075 | Multilingual context label | Various | Date (EN), Date (FR), Datum (DE), Fecha (ES), Data (IT/PT), 日付 (JP), 날짜 (KR), 日期 (ZH), Дата (RU), Tarih (TR), تاريخ (AR), תאריך (HE), วันที่ (TH); Time / Heure / Uhrzeit / Hora / Ora / 時間 / 시간 / 时间 / Время / Saat / وقت / זמן / เวลา |
| DT-076 | OCR-distorted date | Char substitution | "2O24-O3-l5" (O for 0, l for 1), "Mar l5, 2O24" (l for 1, O for 0); 1985 → l985 |
| DT-077 | OCR-distorted time | Separator confusion | "l4:3O:22" (l for 1, O for 0), "2:3O PM" (O for 0); "14 30 22" (lost colons) |
| DT-078 | Masked / partial date | Privacy-redacted | "**/**/2024", "2024-03-**", "[DATE]", "Mar 15, ****" |
| DT-079 | Masked / partial time | Privacy-redacted | "**:30", "14:**:**", "[TIME]", "PM" |
| DT-080 | Anonymized placeholder | Standard generic | 1970-01-01 (Unix epoch), 2000-01-01, 1900-01-01, <DATE>, <TIME> |
| DT-081 | Sentence-boundary tricky | Trailing punctuation | "She left at 14:30.", "Was the date 2024-03-15?", "Meeting tomorrow at 9:30!" |
| DT-082 | Adjacency-tight | No separator | "JohnSmith2024-03-1514:30Login", "Mar15Maria Garcia09:15" |
| DT-083 | Date in JSON | Structured | "date": "2024-03-15", "timestamp": "2024-03-15T14:30:22Z", "created_at": 1710519022 |
| DT-084 | Date in KV | Form field | date=2024-03-15, TIMESTAMP: 2024-03-15T14:30:22Z, CREATED: 1710519022 |
| DT-085 | Date in XML | Markup | <date>2024-03-15</date>, <timestamp>2024-03-15T14:30:22Z</timestamp> |
| DT-086 | Date in CSV | Tabular | "Smith","John","2024-03-15","14:30:22","Login event" |
| DT-087 | Date in legal pleading | Court | "On or about March 15, 2024, the Plaintiff alleges..."; "Filed: 2024-03-15" |
| DT-088 | Date in medical chart | Clinical | "Visit date: 03/15/2024; Time in: 09:15, Time out: 09:45"; "DOS (date of service): 2024-03-15" |
| DT-089 | Date in financial record | Transaction | "Transaction date: 2024-03-15; Settlement: 2024-03-17 (T+2)"; "Effective Date: 03/15/2024" |
| DT-090 | Date adjacency-tight with PII | Combined | "John Smith,2024-03-15,123-45-6789,Login"; "EID12345-Hired20200601" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | DT-076, DT-077 |
| Masked / partial / redacted | ✓ | DT-078, DT-079, DT-080 |
| Multilingual context labels | ✓ | DT-075 |
| Date format coverage | ✓ | DT-001 (ISO), DT-006 (US), DT-008 (EU /), DT-009 (EU .), DT-010 (EU -), DT-011 to DT-013 (CJK) |
| Written / word forms | ✓ | DT-014 to DT-025 (12+ languages including Russian, Arabic, Hebrew) |
| Era-based / non-Gregorian | ✓ | DT-026 (Reiwa), DT-027 (Buddhist), DT-028 (Hebrew), DT-029 (Hijri), DT-030 (Persian), DT-031 (Dangi), DT-032 (Chinese Lunar) |
| Time formats | ✓ | DT-033 (24h), DT-034 (12h), DT-035 (seconds), DT-036 (sub-second) |
| Timezone | ✓ | DT-037 (abbreviation), DT-038 (IANA), DT-039 (offset) |
| Timestamps | ✓ | DT-040 (Unix sec), DT-041 (ms), DT-042 (μs/ns), DT-047 (JWT exp) |
| Protocol-specific | ✓ | DT-043 (RFC 2822), DT-044 (RFC 5322), DT-045 (HTTP), DT-046 (Cookie), DT-050 (syslog), DT-051 (Apache CLF) |
| Compact / no-separator | ✓ | DT-052, DT-053 |
| Business calendar | ✓ | DT-054 (quarter), DT-055 (fiscal), DT-056 (half), DT-057 (month-year) |
| Partial / range / duration | ✓ | DT-057 to DT-065 |
| Day of week | ✓ | DT-066, DT-067 |
| Descriptive / relative / recurring | ✓ | DT-061, DT-062, DT-068, DT-069, DT-070, DT-071, DT-072 |
| In structured data | ✓ | DT-083, DT-084, DT-085, DT-086 |
| Adjacency-tight | ✓ | DT-082, DT-090 |
| Sentence-boundary tricky | ✓ | DT-081 |
| Domain-embedded (legal/medical/financial) | ✓ | DT-087, DT-088, DT-089 |
| Date + time combined | ✓ | DT-074 |

**Total patterns for Date_Time: 90**

---

## Entity 50: Emergency_Contact_Details

Person designated to be contacted in an emergency. Combines name, phone, email, relationship.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| EC-001 | Name + Relationship + Phone | Standard | "Emergency Contact: Jane Smith (wife), 917-555-0100" |
| EC-002 | Name + Relationship + Phone + Email | Extended | "EC: Jane Smith, wife, 917-555-0100, jane.smith@gmail.com" |
| EC-003 | Multiple emergency contacts (primary/secondary) | Two-tier | "Primary EC: Jane Smith (wife), 917-555-0100\nSecondary EC: Mike Chen (brother), 415-555-0200" |
| EC-004 | EC label variations — English | Labels | Emergency Contact, EC, ICE (In Case of Emergency), Notify in emergency, Next of Kin (NOK), Emergency Contact Person (ECP) |
| EC-005 | EC for HR form | Onboarding | "Employee Emergency Contact: Jane Smith\nRelationship: Spouse\nPhone: 917-555-0100\nEmail: jane.smith@gmail.com" |
| EC-006 | EC for school form | School | "Parent/Guardian Emergency Contact:\n1. Jane Smith (Mother): 917-555-0100\n2. John Smith (Father): 917-555-0123" |
| EC-007 | EC for hospital / admission | Healthcare | "Hospital Admission EC: Jane Smith (spouse), 917-555-0100, jane.smith@gmail.com\nNext of kin: same" |
| EC-008 | EC for travel | Travel | "Travel Emergency Contact (US Embassy notification): Jane Smith, 917-555-0100, jane@email.com" |
| EC-009 | Healthcare Proxy / Agent | HCP | "Healthcare Proxy: Jane Smith\nRelation: Wife\nPhone: 917-555-0100\nAuthorized to make medical decisions" |
| EC-010 | Power of Attorney (POA) | Legal | "POA — Healthcare: Jane Smith (wife), 917-555-0100\nPOA — Financial: Mike Chen (brother), 415-555-0200" |
| EC-011 | Next of Kin (NOK) | Family priority | "Next of Kin: Jane Smith (wife), 917-555-0100"; "NOK: Mike Chen (son)" |
| EC-012 | Beneficiary contact | Insurance/will | "Beneficiary: Jane Smith (wife), 917-555-0100"; "Will executor: Mike Chen (brother)" |
| EC-013 | Domestic partner as EC | Non-married | "Domestic Partner: Jane Smith, 917-555-0100"; "Civil partner: Sarah Chen, 415-555-0200" |
| EC-014 | Adult child as EC | Family | "Adult Child: Mike Smith (son, age 25), 917-555-0150"; "Daughter Sarah, 415-555-0200" |
| EC-015 | Parent as EC | Family | "Parent: Robert Smith (father), 917-555-0150"; "Mother: Mary Smith, 415-555-0200" |
| EC-016 | Sibling as EC | Family | "Sibling: Mike Smith (brother), 917-555-0150"; "Sister: Sarah Smith, 415-555-0200" |
| EC-017 | Friend as EC | Non-family | "Friend: Jane Doe, 917-555-0100"; "Best friend: Mike Chen, 415-555-0200" |
| EC-018 | Coworker as EC | Workplace | "Coworker: Mike Chen (office colleague), 917-555-0100" |
| EC-019 | EC with full address | Detailed | "Jane Smith, Spouse, 123 Main St, Springfield IL 62701, 917-555-0100, jane.smith@gmail.com" |
| EC-020 | EC with relation only | Minimal | "EC: Spouse (no name on file)"; "Emergency: Next of kin" |
| EC-021 | EC for child / minor | Pediatric | "Emergency Contact for John Smith Jr. (age 8): Jane Smith (mother), 917-555-0100" |
| EC-022 | EC for elder / dementia patient | Geriatric | "EC for Margaret Smith (age 82, dementia): Daughter Sarah Smith, 917-555-0100" |
| EC-023 | EC in ICE phone entry | Phone contact | "ICE entry on phone: 'ICE Jane (Spouse) +1-917-555-0100'"; "Saved as 'ICE'" |
| EC-024 | EC on medical alert bracelet | Wearable | "Med Alert Bracelet: T1DM. ICE: 917-555-0100 (Jane, spouse)"; "Allergic to PCN. EC: 415-555-0200" |
| EC-025 | EC on patient ID wristband | Hospital | "Hospital Wristband: Smith, John; DOB 3/15/1985; MRN 12345; EC: Jane Smith 917-555-0100" |
| EC-026 | EC for jail / arrest | Criminal | "Booking arrest record: EC notified: Jane Smith (spouse), 917-555-0100 at 2024-03-15 22:30" |
| EC-027 | EC for military / service member | Military | "DD93 Form: Person Authorized to Direct Disposition (PADD): Jane Smith (spouse)"; "SGLI beneficiary" |
| EC-028 | EC for daycare / camp | Childcare | "Daycare EC: Mom (Jane Smith) 917-555-0100; Dad (John Smith) 917-555-0123; Backup: Grandma 415-555-0200" |
| EC-029 | EC with authorization to pick up | Pickup auth | "Authorized to pick up child: 1. Jane Smith (mom) 2. Sarah Chen (aunt) 3. Mike Smith (uncle)" |
| EC-030 | EC with do-not-contact note | Restricted | "DO NOT CONTACT: Mike Smith (estranged spouse). EC: Sister Sarah, 415-555-0200" |
| EC-031 | EC with restraining order | Protective | "Restraining order against John Smith — DO NOT use as EC. Alternate EC: Mom 917-555-0100" |
| EC-032 | International EC | Cross-border | "Overseas EC: Jane Smith (spouse), +44 20 7946 0958, jane.smith@email.co.uk" |
| EC-033 | EC on driver's license | License | "Driver's License EC (some states): Jane Smith 917-555-0100 — on file with DMV"; "ECP entry" |
| EC-034 | EC with relationship variation — multilingual | Various langs | Spouse / époux / Ehepartner / cónyuge / coniuge; Parent / parent / Eltern / padre/madre; Child / enfant / Kind / hijo/a |
| EC-035 | EC for HIPAA disclosure | Auth | "HIPAA-authorized contacts: Jane Smith (wife), 917-555-0100 — may receive medical info" |
| EC-036 | EC for school disclosure | FERPA | "FERPA-authorized parent contact: Jane Smith (mother), 917-555-0100, may discuss student records" |
| EC-037 | EC in JSON | Structured | "emergency_contact": {"name": "Jane Smith", "relationship": "spouse", "phone": "+1-917-555-0100", "email": "jane@email.com"} |
| EC-038 | EC in KV | Form field | ec_name=Jane Smith, EC_RELATION: spouse, EC_PHONE: 917-555-0100 |
| EC-039 | EC in XML | Markup | <emergency_contact><name>Jane Smith</name><relationship>spouse</relationship><phone>917-555-0100</phone></emergency_contact> |
| EC-040 | EC in CSV | Tabular | "Smith","John","E12345","Jane Smith","Spouse","917-555-0100","jane@email.com" |
| EC-041 | Multilingual context label | Various | Emergency Contact (EN), Personne à contacter en cas d'urgence (FR), Notfallkontakt (DE), Contacto de emergencia (ES), Contatto di emergenza (IT), Contato de emergência (PT), 緊急連絡先 (JP), 비상 연락처 (KR), 紧急联系人 (ZH), Контактное лицо для экстренной связи (RU), Acil durum kişisi (TR), جهة اتصال في حالات الطوارئ (AR), איש קשר לחירום (HE), ผู้ติดต่อในกรณีฉุกเฉิน (TH) |
| EC-042 | OCR-distorted EC | Char substitution | "Jane Smlth" (l for i), "Mlke Chen" (l for i); "Emergeney" (e for c); "9l7-555-Ol00" (l for 1, O for 0) |
| EC-043 | Masked / partial EC | Privacy-redacted | "EC: J*** Smith, spouse, 917-555-****"; "Emergency: [REDACTED]" |
| EC-044 | Anonymized placeholder | Standard generic | "EC: Jane Doe (placeholder)"; "EC: <NAME>, <RELATION>, <PHONE>"; "[EC]" |
| EC-045 | Sentence-boundary tricky | Trailing punctuation | "Call Jane in case of emergency.", "Who is your EC?", "EC: spouse, 917-555-0100!" |
| EC-046 | Adjacency-tight | No separator | "JohnSmithEC:JaneSmithSpouse917-555-0100", "EID12345EC:Mom415-555-0200" |
| EC-047 | EC with availability hours | Time-bound | "EC: Jane Smith, 917-555-0100, best contact 9 AM - 5 PM EST"; "Daytime: 917-555-0100; Evening: 917-555-0150" |
| EC-048 | EC alternate phone | Multiple | "EC: Jane Smith — Home: 917-555-0100; Mobile: 917-555-0150; Work: 212-555-0500" |
| EC-049 | EC for organ donation | Donation | "Organ donor — next of kin notification: Jane Smith (spouse), 917-555-0100" |
| EC-050 | EC for hospice / palliative | End-of-life | "Hospice EC: Jane Smith (HCP), 917-555-0100; DNR: yes; POLST on file" |
| EC-051 | EC for psychiatric admission | Mental health | "Psych admission EC: Jane Smith (wife) — authorized for treatment information per 5150 hold" |
| EC-052 | EC for student / university | Higher ed | "Student EC: Jane Smith (mother), 917-555-0100, jane.smith@gmail.com; FERPA: authorized" |
| EC-053 | EC chain (cascade) | Failover | "Try in order: 1. Jane Smith 917-555-0100; 2. Mike Smith 917-555-0150; 3. Sarah Chen 415-555-0200" |
| EC-054 | EC for sports / club | Recreation | "Gym EC: Jane Smith (spouse), 917-555-0100, allergic to PCN (medical context)" |
| EC-055 | EC with relationship in multilingual context | Bilingual | "EC: 妻 (wife) Jane Smith, +1-917-555-0100"; "EC: ぼうけい (Brother) Mike, +81-3-1234-5678" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | EC-042 |
| Masked / partial / redacted | ✓ | EC-043, EC-044 |
| Multilingual context labels | ✓ | EC-041 |
| Multilingual relationship terms | ✓ | EC-034, EC-055 |
| Relationship coverage | ✓ | EC-013 (domestic partner), EC-014 (child), EC-015 (parent), EC-016 (sibling), EC-017 (friend), EC-018 (coworker) |
| Primary / secondary tiers | ✓ | EC-003, EC-053 |
| Authorization roles (HCP, POA, NOK, beneficiary) | ✓ | EC-009, EC-010, EC-011, EC-012 |
| In structured data | ✓ | EC-037, EC-038, EC-039, EC-040 |
| Adjacency-tight | ✓ | EC-046 |
| Sentence-boundary tricky | ✓ | EC-045 |
| Domain-embedded (HR/school/hospital/travel/military/childcare/jail/psych/student) | ✓ | EC-005, EC-006, EC-007, EC-008, EC-026, EC-027, EC-028, EC-051, EC-052 |
| Restricted / safety-flag (no-contact, restraining order) | ✓ | EC-030, EC-031 |
| International / cross-border | ✓ | EC-032 |
| Privacy authorization (HIPAA/FERPA) | ✓ | EC-035, EC-036 |
| Wearable / ICE on device | ✓ | EC-023, EC-024 |
| End-of-life / organ donor | ✓ | EC-049, EC-050 |
| Pediatric / geriatric specific | ✓ | EC-021, EC-022 |

**Total patterns for Emergency_Contact_Details: 55**

---

## Entity 51: Org_Name

Organization names — companies, government agencies, non-profits, universities, hospitals, religious institutions, banks. The final entity in the v4 taxonomy.

### Natural Patterns

| ID | Pattern | Description | Examples |
|---|---|---|---|
| ORG-001 | Company name — full formal | Legal entity | Apple Inc., Microsoft Corporation, Alphabet Inc., JPMorgan Chase & Co. |
| ORG-002 | Company name — common / colloquial | Informal | Apple, Microsoft, Google, JPMorgan, Goldman |
| ORG-003 | Company name with legal suffix — US | Suffix | Apple, Inc.; Microsoft Corp.; Tesla, Inc.; Coca-Cola Company; LLC, LLP, P.C. |
| ORG-004 | Company name with legal suffix — UK | UK suffix | Vodafone Plc; Unilever PLC; BP p.l.c.; Acme Ltd; Acme Limited |
| ORG-005 | Company name with legal suffix — DE | DE suffix | Siemens AG; BMW AG; SAP SE; Bosch GmbH; Acme GmbH & Co. KG; UG (haftungsbeschränkt) |
| ORG-006 | Company name with legal suffix — FR | FR suffix | Total SA; LVMH SA; Carrefour SA; Acme SAS (société par actions simplifiée); SARL |
| ORG-007 | Company name with legal suffix — IT | IT suffix | Ferrari S.p.A.; Eni S.p.A.; Acme S.r.l.; Acme & C. S.r.l. |
| ORG-008 | Company name with legal suffix — ES | ES suffix | Banco Santander, S.A.; Telefónica, S.A.; Acme SL (Sociedad Limitada) |
| ORG-009 | Company name with legal suffix — NL | NL suffix | Royal Dutch Shell N.V.; ASML Holding N.V.; Heineken N.V.; Acme B.V. |
| ORG-010 | Company name with legal suffix — JP | JP suffix | Toyota Motor Corporation; トヨタ自動車株式会社 (kabushiki kaisha); Sony 株式会社 (KK) |
| ORG-011 | Company name with legal suffix — KR | KR suffix | Samsung 주식회사; 현대자동차 주식회사 (Hyundai); LG 전자(주); (주) Korean Inc. format |
| ORG-012 | Company name with legal suffix — CN | CN suffix | 阿里巴巴集团 (Alibaba Group); 腾讯控股有限公司 (Tencent Holdings Ltd.); 华为技术有限公司 (Huawei) |
| ORG-013 | Company name with legal suffix — BR | BR suffix | Petrobras S.A.; Vale S.A.; Acme Ltda. (Limitada); Acme Comércio S.A. |
| ORG-014 | Company name with legal suffix — IN | IN suffix | Tata Consultancy Services Limited; Reliance Industries Ltd.; Infosys Ltd.; Acme Pvt. Ltd.; Acme Private Limited |
| ORG-015 | Company name with legal suffix — MX | MX suffix | Cemex, S.A.B. de C.V.; América Móvil, S.A.B. de C.V.; Acme S. de R.L. de C.V. |
| ORG-016 | Company name with legal suffix — RU | RU suffix | ОАО Газпром (Gazprom PJSC); ПАО Сбербанк (Sberbank); ООО "Акме" (Acme LLC) |
| ORG-017 | Company name with legal suffix — AU | AU suffix | BHP Group Limited; Commonwealth Bank of Australia; Telstra Corporation Ltd; Acme Pty Ltd |
| ORG-018 | Company name with legal suffix — CA | CA suffix | Royal Bank of Canada (RBC); Shopify Inc.; Bombardier Inc.; Acme Ltée. (Limitée) |
| ORG-019 | Company name with legal suffix — SE | SE suffix | Volvo AB; H&M Hennes & Mauritz AB; Spotify AB; Ericsson AB |
| ORG-020 | Company name with legal suffix — CH | CH suffix | Nestlé S.A.; Roche Holding AG; UBS Group AG; Acme GmbH (CH) |
| ORG-021 | Stock ticker — US | NYSE/NASDAQ | AAPL (Apple), MSFT (Microsoft), GOOGL (Alphabet Class A), TSLA (Tesla), JPM (JPMorgan) |
| ORG-022 | Stock ticker — international | Foreign exchange | TSE: 7203 (Toyota), LSE: HSBA.L (HSBC), Euronext: MC.PA (LVMH), HKEx: 0700.HK (Tencent), SSE: 600519 (Moutai) |
| ORG-023 | Stock ticker with exchange prefix | Disambiguated | NYSE:AAPL, NASDAQ:MSFT, LSE:VOD, TSE:7203, BSE:RELIANCE.BO |
| ORG-024 | DBA (Doing Business As) | Trade name | Acme Holdings DBA "Acme Express"; trading as Acme Express; d/b/a Acme |
| ORG-025 | Parent / subsidiary relationship | Corp structure | "Acme Inc. (subsidiary of Acme Holdings)"; "Wholly-owned subsidiary"; "Acme is a division of Holdings Corp" |
| ORG-026 | Brand name vs legal name | Brand | "Lay's (legal: Frito-Lay, Inc., a PepsiCo subsidiary)"; "Olay (legal: Procter & Gamble)" |
| ORG-027 | Government agency — US federal | US gov | U.S. Department of Defense (DoD); Federal Bureau of Investigation (FBI); IRS; CIA; NSA; SEC; FDA; DHS |
| ORG-028 | Government agency — US state | State gov | California Department of Motor Vehicles (DMV); Texas Department of Public Safety (DPS); NY State Police |
| ORG-029 | Government agency — US local | Local gov | New York City Department of Education; Los Angeles County Sheriff's Department; Chicago Police Department |
| ORG-030 | Government agency — UK | UK gov | HMRC (His Majesty's Revenue and Customs); MI5; MI6; DVLA; NHS; Met Police; HM Treasury |
| ORG-031 | Government agency — EU | EU bodies | European Commission; European Central Bank (ECB); European Parliament; Europol; EUROSTAT; ESMA |
| ORG-032 | Government agency — international | UN / global | United Nations (UN); World Health Organization (WHO); IMF; World Bank; UNICEF; WTO; INTERPOL; OECD |
| ORG-033 | Government agency — DE / FR / JP / IN | International gov | Bundesnachrichtendienst (BND); Ministère de l'Économie (FR); Ministry of Finance (Japan); Reserve Bank of India (RBI) |
| ORG-034 | Military branch | Armed forces | US Army; US Navy; USMC (Marine Corps); USAF (Air Force); US Space Force; British Army; Royal Air Force (RAF); Bundeswehr |
| ORG-035 | Non-profit / NGO | 501(c)(3) | American Red Cross; Doctors Without Borders (MSF); Greenpeace; Amnesty International; UNICEF; The Wikimedia Foundation |
| ORG-036 | Religious institution — Church | Church | St. Mary's Catholic Church; First Baptist Church of Springfield; Mormon Church (LDS); Catholic Diocese of Boston |
| ORG-037 | Religious institution — Mosque | Mosque | Islamic Center of America; Al-Aqsa Mosque; Masjid Al-Noor; The Mosque Foundation |
| ORG-038 | Religious institution — Synagogue | Synagogue | Park East Synagogue; Temple Emanu-El; Congregation Beth Israel; Chabad House |
| ORG-039 | Religious institution — Temple | Temple | Hindu Temple of New York; BAPS Shri Swaminarayan Mandir; Buddhist Temple; Wat Thai LA |
| ORG-040 | University — public | Public uni | University of California, Berkeley (UC Berkeley); Texas A&M University; University of Michigan |
| ORG-041 | University — private | Private uni | Harvard University; Stanford University; MIT (Massachusetts Institute of Technology); Princeton University; Carnegie Mellon |
| ORG-042 | University — international | Non-US uni | University of Oxford; University of Cambridge; ETH Zürich; INSEAD; IIT Hyderabad; Peking University; University of Tokyo |
| ORG-043 | School — K-12 | Schools | Springfield High School; PS 87 Manhattan; Acme Elementary School; St. Mary's Academy; Phillips Exeter Academy |
| ORG-044 | Hospital / healthcare facility | Hospital | Massachusetts General Hospital (MGH); Mayo Clinic; Cleveland Clinic; Johns Hopkins Hospital; Mount Sinai Hospital |
| ORG-045 | Hospital system / network | Health system | Kaiser Permanente; Sutter Health; HCA Healthcare; UnitedHealth Group; Geisinger Health System |
| ORG-046 | Clinic / outpatient | Clinic | Acme Medical Clinic; OBGYN Associates of Springfield; FastMed Urgent Care; Dr. Smith's Family Practice |
| ORG-047 | Bank — major US | US bank | JPMorgan Chase; Bank of America; Wells Fargo; Citibank; Goldman Sachs; Morgan Stanley; Capital One |
| ORG-048 | Bank — international | Intl bank | HSBC; Deutsche Bank; BNP Paribas; UBS; Credit Suisse; Mitsubishi UFJ; Banco Santander; ICBC; Standard Chartered |
| ORG-049 | Investment / asset manager | Funds | BlackRock; Vanguard; State Street; Fidelity Investments; PIMCO; Bridgewater; Renaissance Technologies |
| ORG-050 | Insurance company | Insurance | State Farm; Allstate; Geico; Progressive; AIG; MetLife; Prudential; Northwestern Mutual; Lloyd's of London |
| ORG-051 | Big 4 accounting / consulting | Professional services | Deloitte; PwC (PricewaterhouseCoopers); EY (Ernst & Young); KPMG; McKinsey & Company; Bain; BCG; Accenture |
| ORG-052 | Big tech / FAANG / MAANG | Tech giants | Meta (Facebook); Apple; Amazon; Netflix; Google; Microsoft; Tesla; Nvidia |
| ORG-053 | Pharma / biotech | Pharma | Pfizer; Johnson & Johnson; Roche; Novartis; Merck; AstraZeneca; Moderna; BioNTech; Eli Lilly |
| ORG-054 | Aerospace / defense | A&D | Boeing; Lockheed Martin; Raytheon Technologies; Northrop Grumman; Airbus; BAE Systems; SpaceX; Blue Origin |
| ORG-055 | Automotive | Auto OEM | Ford Motor Company; General Motors (GM); Toyota; Volkswagen Group; Honda; BMW; Mercedes-Benz; Stellantis |
| ORG-056 | Retail — big box / e-commerce | Retail | Walmart; Target; Costco; Amazon; The Home Depot; Lowe's; Best Buy; IKEA; Aldi |
| ORG-057 | Fashion / luxury brands | Apparel | Nike; Adidas; LVMH (Louis Vuitton); Gucci; Chanel; Hermès; Zara (Inditex); H&M; Uniqlo (Fast Retailing) |
| ORG-058 | Food / beverage | F&B | Coca-Cola; PepsiCo; Nestlé; Unilever; Procter & Gamble; McDonald's; Starbucks; Anheuser-Busch InBev |
| ORG-059 | Energy / oil & gas | Energy | ExxonMobil; Chevron; Shell; BP; TotalEnergies; Saudi Aramco; Equinor; Eni; ConocoPhillips |
| ORG-060 | Telecom / utilities | Telco | Verizon; AT&T; T-Mobile; Vodafone; Deutsche Telekom; NTT; China Mobile; Comcast Xfinity; ConEd |
| ORG-061 | Media / entertainment | Media | The Walt Disney Company; Netflix; Warner Bros. Discovery; Comcast NBCUniversal; Paramount Global; Spotify |
| ORG-062 | Airlines | Aviation | American Airlines; Delta Air Lines; United Airlines; Southwest; Lufthansa; Air France-KLM; Emirates; Singapore Airlines |
| ORG-063 | Hotels / hospitality | Hospitality | Marriott International; Hilton Worldwide; Hyatt; IHG; Accor; Four Seasons; Ritz-Carlton |
| ORG-064 | Cloud / SaaS | Tech SaaS | Salesforce; Oracle; SAP; Anonymous Institution; Workday; Snowflake; Databricks; Atlassian; HubSpot; Adobe |
| ORG-065 | Semiconductor | Chips | Intel; Nvidia; AMD; TSMC; Samsung Electronics; Qualcomm; Broadcom; Applied Materials; ASML |
| ORG-066 | Sports — pro team | Team | New York Yankees; LA Lakers; Manchester United; FC Barcelona; Real Madrid; Boston Celtics; Dallas Cowboys |
| ORG-067 | Sports league / governing body | League | NFL; NBA; MLB; NHL; FIFA; UEFA; IOC; NCAA; Premier League; La Liga; Bundesliga; Serie A |
| ORG-068 | Industry classification — NAICS | NAICS code | NAICS: 541511 (Custom Computer Programming); NAICS: 622110 (General Medical and Surgical Hospitals) |
| ORG-069 | Industry classification — SIC | SIC code | SIC: 7372 (Prepackaged Software); SIC: 8062 (General Medical and Surgical Hospitals) |
| ORG-070 | Industry classification — GICS | Sector | GICS Sector 45 (Information Technology); GICS Industry 4510 (Software & Services) |
| ORG-071 | Industry classification — ISIC | UN ISIC | ISIC Section J (Information and Communication); ISIC 6201 (Computer programming activities) |
| ORG-072 | EIN-linked org | Tax ID | "Acme Inc., EIN: 12-3456789, NAICS 541511" |
| ORG-073 | LEI (Legal Entity Identifier) | ISO 17442 | LEI: 5493000IBP32UQZ0KL24 (20-char); LEI of JPMorgan Chase: 8I5DZWZKVSZI1NUHU748 |
| ORG-074 | DUNS number | D&B | DUNS: 123456789; D&B DUNS Number: 008-666-543 |
| ORG-075 | Companies House number (UK) | Company # | UK Company Number: 12345678; Companies House: SC123456 (Scotland); NI123456 (NI) |
| ORG-076 | SIRET / SIREN (France) | FR business reg | SIREN: 123 456 789; SIRET: 12345678901234 (SIREN + 5-digit NIC) |
| ORG-077 | Handelsregister number (Germany) | DE business reg | HRB 123456 (Limited liability — Berlin); HRA 12345 (Partnership) |
| ORG-078 | CNPJ (Brazil business) | BR business reg | CNPJ: 12.345.678/0001-90 (covered under Tax Reference too) |
| ORG-079 | Org URL / domain | Web | acme.com; www.acmecorp.com; acme.co.uk; acme.de; jpmorgan.com; nytimes.com |
| ORG-080 | Org logo / brand mark | Visual | Acme™; Acme® (registered); ™ (trademark); ® (registered TM); ℠ (service mark) |
| ORG-081 | Org abbreviation / acronym | Common short | IBM (International Business Machines); GE (General Electric); 3M; AT&T; HSBC; UBS; KFC; MSN |
| ORG-082 | Native script name | Original language | トヨタ自動車 (Toyota); 三星 (Samsung in Chinese); سعودي أرامكو (Saudi Aramco) |
| ORG-083 | Transliteration / Romanized | Latin script of native | Toyota (from トヨタ); Samsung (from 삼성); Bayer (from German); Aldi (from Albrecht-Diskont) |
| ORG-084 | Org with location qualifier | Location-disambig | "Acme Inc. (NYC office)"; "JPMorgan Chase (London branch)"; "Google Mountain View HQ" |
| ORG-085 | Org with department / division | Sub-unit | "JPMorgan Chase Investment Banking division"; "Microsoft Azure team"; "Google DeepMind research lab"; "Boeing Defense, Space & Security" |
| ORG-086 | Former / historical org name | Renamed | "Facebook (now Meta Platforms)"; "Google (now Alphabet parent)"; "Andersen Consulting (now Accenture)"; "Twitter (now X)" |
| ORG-087 | Defunct / acquired org | M&A history | "Lehman Brothers (defunct 2008)"; "WorldCom (defunct)"; "WhatsApp (acquired by Facebook 2014)" |
| ORG-088 | Joint venture / partnership | JV / partnership | "Sony Ericsson (JV)"; "Renault-Nissan-Mitsubishi Alliance"; "Sumitomo Mitsui Banking Corporation" |
| ORG-089 | Trade union as org | Union (cross-ref) | (See Trade_Union_Membership; SEIU Local 32BJ, Teamsters Local 705, UAW as organizations) |
| ORG-090 | Political party as org | Party (cross-ref) | (See Political_Party; Democratic Party, Republican Party, CDU, Labour Party as orgs) |
| ORG-091 | Government contractor | GovCon | "Lockheed Martin (DoD contractor)"; "Booz Allen Hamilton (intelligence contractor)"; "Leidos"; "SAIC" |
| ORG-092 | Law firm | Legal | Cravath, Swaine & Moore; Skadden Arps; Latham & Watkins; Wachtell Lipton; Sullivan & Cromwell; DLA Piper |
| ORG-093 | Investment bank — bulge bracket | I-bank | Goldman Sachs; Morgan Stanley; JPMorgan Chase; Citi; Bank of America; Barclays; UBS; Deutsche Bank; Credit Suisse |
| ORG-094 | Private equity / VC firm | PE / VC | Blackstone; KKR; Carlyle Group; Apollo Global Management; Sequoia Capital; Andreessen Horowitz (a16z); Benchmark Capital; Accel |
| ORG-095 | Crypto exchange / blockchain co | Crypto | Coinbase; Binance; Kraken; Gemini; Circle; Ripple Labs; Chainalysis; OpenSea |
| ORG-096 | Org in JSON | Structured | "company": "Acme Inc.", "employer": "JPMorgan Chase", "organization": "MIT" |
| ORG-097 | Org in KV | Form field | company=Acme Inc., EMPLOYER: JPMorgan Chase, ORG: MIT |
| ORG-098 | Org in XML | Markup | <company>Acme Inc.</company>, <organization type="university">MIT</organization> |
| ORG-099 | Org in CSV | Tabular | "Smith","John","E12345","Acme Inc.","Software Engineer","2020-01-15" |
| ORG-100 | Multilingual context label | Various | Organization (EN), Organisation (FR/DE), Organización (ES), Organizzazione (IT), Organização (PT), 組織 (JP), 조직 (KR), 组织 (ZH), Организация (RU), Kuruluş (TR), منظمة (AR), ארגון (HE), องค์กร (TH) |
| ORG-101 | OCR-distorted org name | Char substitution | "Mlcrosoft" (l for i), "Apple lnc." (l for I); "G00gle" (00 for oo); "Tesla" → "T3sla" (3 for e) |
| ORG-102 | OCR diacritic stripping | Lost accents | "Nestle" (was Nestlé); "Loreal" (was L'Oréal); "Munchen" → "München" |
| ORG-103 | Masked / partial org | Privacy-redacted | "Acme ***"; "J*** Chase"; "Employer: [REDACTED]"; "Company: ****" |
| ORG-104 | Anonymized placeholder | Standard generic | "Acme Corp" (canonical placeholder); "Example Corp"; "Foo Inc."; "<COMPANY>"; "ABC Company" |
| ORG-105 | Sentence-boundary tricky | Trailing punctuation | "He works at Apple.", "Is the company Tesla?", "Joined Microsoft last year!", "Hired by Goldman Sachs in 2020." |
| ORG-106 | Adjacency-tight | No separator | "JohnSmithAppleInc.SeniorEngineer", "MariaGarcíaJPMorganChase", "EID12345Microsoft" |
| ORG-107 | Org with employee count / size | Size metric | "Acme Inc. (5,000 employees)"; "Fortune 500 company"; "Small business <50 employees"; "SMB" |
| ORG-108 | Org with revenue / market cap | Financial | "Acme Inc., $2.5B revenue 2023"; "Apple market cap $3T"; "Unicorn (>$1B valuation)"; "Decacorn (>$10B)" |
| ORG-109 | Org with HQ / address | Location | "Apple Inc., 1 Apple Park Way, Cupertino, CA 95014"; "HQ: Cupertino, CA"; "Headquartered in Tokyo" |
| ORG-110 | Org as PII enabler | Combined identifier | "John Smith, Senior Engineer at JPMorgan Chase London" (org + role + location → identifies individual) |
| ORG-111 | Org in employment verification | Background check | "Employment Verification: Smith, John employed at Acme Inc. 2020-2024 as Senior Engineer; verified by HR 2024-03-15" |
| ORG-112 | Org in resume / CV | Career history | "EXPERIENCE\nSenior Engineer, JPMorgan Chase (2020 — Present)\nSoftware Engineer, Goldman Sachs (2018 — 2020)" |
| ORG-113 | Org in LinkedIn / professional | Profile | "Current: Senior Engineer at @Apple"; "Past: Microsoft, Google, Amazon"; "Education: Stanford, MIT" |
| ORG-114 | Org as financial counterparty | Banking | "Wire transfer recipient: JPMorgan Chase, NY; SWIFT: CHASUS33"; "Payment to: Apple Inc. via Wise" |
| ORG-115 | Org in legal / lawsuit | Court | "Smith v. Acme Inc. (2024-CV-12345)"; "United States v. Microsoft Corp. (1998)"; "EU vs Google antitrust" |

### Cross-Cutting Consistency Sweep

| Cross-cutting dimension | Status | Pattern IDs |
|---|---|---|
| OCR-distorted | ✓ | ORG-101, ORG-102 |
| Masked / partial / redacted | ✓ | ORG-103, ORG-104 |
| Multilingual context labels | ✓ | ORG-100 |
| Legal entity suffix — country coverage | ✓ | ORG-003 to ORG-020 (US, UK, DE, FR, IT, ES, NL, JP, KR, CN, BR, IN, MX, RU, AU, CA, SE, CH) — 18 countries |
| Native scripts / transliteration | ✓ | ORG-010, ORG-011, ORG-012, ORG-016, ORG-082, ORG-083 |
| Industry coverage | ✓ | ORG-040 to ORG-067 covering big tech, banks, asset managers, insurance, accounting/consulting, pharma, aerospace, automotive, retail, fashion, food, energy, telecom, media, airlines, hotels, cloud/SaaS, semiconductor, sports |
| Organization type coverage | ✓ | ORG-027 to ORG-039 (government — US fed/state/local, UK, EU, international, military), ORG-035 (non-profit), ORG-036 to ORG-039 (religious — church, mosque, synagogue, temple), ORG-040 to ORG-043 (universities, schools), ORG-044 to ORG-046 (hospitals/clinics), ORG-092 (law firms), ORG-094 (PE/VC), ORG-095 (crypto) |
| Industry classification codes | ✓ | ORG-068 (NAICS), ORG-069 (SIC), ORG-070 (GICS), ORG-071 (ISIC) |
| Org-specific identifiers | ✓ | ORG-021 to ORG-023 (stock tickers), ORG-072 (EIN), ORG-073 (LEI), ORG-074 (DUNS), ORG-075 to ORG-078 (Companies House, SIRET/SIREN, HRB, CNPJ) |
| Web / digital | ✓ | ORG-079 (domain), ORG-080 (TM/® marks) |
| Name variants (DBA, parent/sub, brand vs legal, abbreviation) | ✓ | ORG-024, ORG-025, ORG-026, ORG-081, ORG-084, ORG-085 |
| Lifecycle (former, defunct, JV) | ✓ | ORG-086, ORG-087, ORG-088 |
| In structured data | ✓ | ORG-096, ORG-097, ORG-098, ORG-099 |
| Adjacency-tight | ✓ | ORG-106 |
| Sentence-boundary tricky | ✓ | ORG-105 |
| Domain-embedded (employment verification/resume/LinkedIn/banking/legal) | ✓ | ORG-110, ORG-111, ORG-112, ORG-113, ORG-114, ORG-115 |
| Size / financial metadata | ✓ | ORG-107, ORG-108 |
| Cross-references to other entities | ✓ | ORG-089 (Trade Union), ORG-090 (Political Party) |
| HQ / address | ✓ | ORG-109 |

**Total patterns for Org_Name: 115**

---


<!-- END CONSOLIDATED PATTERN CATALOG -->

---

## §9. Catalog Closing — Acknowledgments and Citation

### Acknowledgments

This catalog was developed at Anonymous Institution under the supervision of Anonymous Author 3, with strategic and methodological input from Anonymous Author 2, Anonymous Author 4, and Anonymous Author 5. The cross-cutting consistency-sweep dimensions were refined through iterative review across catalog versions v1 (the generation team's seed) through v4 (this document).

The catalog supports the *Multilingual PII Detection Benchmark* project (working title; to be finalized at submission). Patterns are released under the same license as the benchmark codebase (TBD pending Anonymous Institution legal review for external release).

### Suggested Citation

```bibtex
@misc{anonymous2026piicatalog,
  title  = {{PII Pattern Catalog v4: A 51-Entity, 4,127-Pattern Surface-Form 
           Taxonomy for Multilingual PII Detection Benchmarking}},
  author = {Anonymous Authors},
  year   = {2026},
  note   = {Technical Report. To accompany the 
           Multilingual PII Detection Benchmark, EMNLP 2026 submission.}
}
```

### Versioning and Updates

| Version | Date | Changes |
|---|---|---|
| v1 | Feb 2026 | Initial seed (the generation team), 18 entities |
| v2 | Mar 2026 | Expanded to 43 entities, excluded 12 non-text entities |
| v3 | Apr 2026 | Expanded to 52 entities, ~750 patterns |
| **v4** | **May 2026** | **51 entities (Dietary merged into Religion), 4,127 patterns, formal 20-dim sweep** |

### Document Statistics

- **Total entities:** 51
- **Total patterns:** 4,127
- **Total length:** ~600KB markdown
- **Languages covered:** 21+
- **Scripts covered:** 10
- **Countries with locale-specific patterns:** 40+

---

*End of PII Pattern Catalog v4 Master Document.*
