# How Exactly One Benchmark Record Is Created

**A complete step-by-step walkthrough with every detail**

---

## Step 0: The Starting Point — Seed Pattern File

Everything begins with a JSON file called `expanded_seed_data.json`. Each row in this file represents one specific way a PII entity can appear in text.

There are **713 unique patterns** across **52 entity types**.

One row looks like this:

```json
{
  "id": 147,
  "pattern_id": "P-033",
  "entity_type": "PERSON",
  "pattern_desc": "OCR-distorted full name (character substitution errors from scanning)",
  "examples": "J0hn Srnith, Micheal Johsnon, Sarali Clen, Rlchard Wllson"
}
```

Another row might be:

```json
{
  "id": 312,
  "pattern_id": "AD-017",
  "entity_type": "ADDRESS",
  "pattern_desc": "Japanese residential address format",
  "examples": "東京都新宿区西新宿2-8-1 マンション301号室, 大阪府大阪市北区梅田1-1-3"
}
```

Each pattern gets exactly **one record** per pipeline run. To create more records, the seed file is expanded by copying each pattern multiple times (e.g., ×11 = 7,843 rows). Each copy gets a completely different random configuration in Step 1, so the same pattern is tested under different conditions.

---

## Step 1: Diversity Sampler — Random Configuration Assignment

**What happens:** For the seed row above (P-033, OCR-distorted person name), the sampler independently rolls a random value for each of 8 axes. No LLM is involved — this is pure random sampling with weighted probabilities.

### Axis 1: Text Domain
**Selects 1 from 12 options:**

| Option | Weight (approx) |
|---|---|
| Healthcare or medical record | Higher |
| Legal or judicial proceedings | Higher |
| Finance or banking | Higher |
| Education or academic | Medium |
| Government or public sector | Medium |
| Technology or IT systems | Medium |
| Human resources or employee records | Medium |
| Insurance or claims processing | Medium |
| Customer service or support tickets | Higher |
| Law enforcement or criminal justice | Lower |
| Social media or online communication | Lower |
| E-commerce or retail | Lower |

**Selected for our example:** `healthcare or medical record`

### Axis 2: Text Format
**Selects 1 from 7 options:**

| Option | What it means |
|---|---|
| plain_text | Narrative prose, letters, reports, articles |
| email | Must have From/To/Subject headers, greeting, body, signature |
| chat_transcript | Must have timestamps, speaker names, turn-taking ([14:32] Sarah:) |
| ticket_worknotes | IT ticket with Priority, Status, Assigned To, timestamps, work notes |
| json_record | Structured JSON with nested fields, curly braces, keys and values |
| key_value_pairs | Form-like layout: "Field: Value" on each line |
| log_entry | System log with timestamps, severity levels, event codes |

**Selected for our example:** `email`

### Axis 3: Difficulty
**Selects 1 from 3 options:**

| Option | What the LLM is instructed to do |
|---|---|
| easy | PII is clearly visible, standard formats, obvious context. A human could spot it instantly. |
| medium | PII is embedded in flowing text, mixed formats, requires reading carefully to identify everything. |
| hard | PII is obfuscated, OCR-distorted, encoded, split across sentences, uses homoglyphs, buried in dense technical prose. Deliberately tricky. |

**Selected for our example:** `hard`

### Axis 4: Context Length
**Selects 1 from 4 options:**

| Option | Character range | What it looks like |
|---|---|---|
| small | Up to 1,000 characters | ~1 short paragraph, a brief note |
| medium | 1,000–4,000 characters | ~1–2 paragraphs, a typical email or ticket |
| large | 4,000–8,000 characters | ~2–4 paragraphs, a detailed report |
| very_large | 8,000–16,000 characters | ~4+ paragraphs, a full multi-page document |

**Selected for our example:** `medium (1,000-4,000 characters, 1-2 paragraphs)`

### Axis 5: Entity Density
**Selects 1 from 3 options:**

| Option | Target entity count | What it means |
|---|---|---|
| low | Up to 5 entities | Sparse PII — just a few items in the text |
| medium | 5–15 entities | Moderate — a realistic amount of PII for a business document |
| high | More than 15 entities | Dense — text is packed with PII (like a form or detailed record) |

**Selected for our example:** `medium (include 5-15 PII entities total)`

### Axis 6: Code-Switching Level
**Selects 1 from 2 or 3 options depending on config:**

For English-only config (EN):

| Option | What it means |
|---|---|
| none | Pure monolingual text. No foreign words at all. |
| light | Occasional foreign words or phrases scattered in ("por favor", "danke schön") |
| heavy | Frequent bilingual alternation within and across sentences (full Spanglish, Franglais) |

For Code-Switching config (CS): `none` was removed in V1 fix, so only `light` and `heavy`.

**Selected for our example:** `none (single language only, no mixing)`

### Axis 7: Language
**Selects 1 from the configured language list:**

For EN config: `English`
For CS config: `English with code-switching`
For multilingual configs: One of — Spanish, French, German, Dutch, Italian, Japanese, Brazilian Portuguese, Swedish, etc.

**Selected for our example:** `English`

### Axis 8: Additional Entity Types
**Selects 1 combination from 12 predefined groupings:**

These are extra entity types the LLM must include alongside the target pattern. They reflect realistic co-occurrence:

| Combo | When it makes sense |
|---|---|
| PERSON + DATE_TIME | Basic — almost any document |
| PERSON + EMAIL + PHONE | Contact-heavy documents |
| ADDRESS + PHONE + EMAIL | Correspondence, forms |
| PERSON + SALARY + ORG_NAME + JOB_POSITION | HR, payroll, financial |
| PERSON + DOB + ADDRESS | Medical, government forms |
| PERSON + DATE_TIME + CRIME | Legal, law enforcement |
| PERSON + RELIGION + NATIONALITY | Immigration, diversity docs |
| PERSON + AGE + MEDICAL_INFO | Healthcare records |
| PERSON + PASSWORD + USERNAME + IP_ADDRESS | IT security incidents |
| PERSON + CREDIT_CARD + BANK_ACCOUNT | Financial transactions |
| PERSON + PASSPORT + CITIZENSHIP | Travel, immigration |
| PERSON + PERFORMANCE + DISCIPLINARY | HR records |

**Selected for our example:** `PERSON + DOB + ADDRESS`

### After Step 1: The Complete Configuration

```
Seed Pattern:    P-033 (OCR-distorted full name)
Domain:          healthcare or medical record
Format:          email
Difficulty:      hard
Context Length:  medium (1,000-4,000 chars)
Entity Density:  medium (5-15 entities)
Code-Switching:  none
Language:        English
Additional Types: PERSON + DOB + ADDRESS
```

This configuration is now passed to the LLM in Step 2.

---

## Step 2: Text Generation — Claude Large (temperature = 0.9)

**What happens:** The configuration from Step 1 is assembled into a detailed prompt and sent to Claude Large via API call.

### The Prompt (simplified)

The actual prompt includes all of the above configuration plus specific instructions:

```
You are generating realistic synthetic text for a PII detection benchmark.

TARGET PATTERN: OCR-distorted full name — names with character substitution 
errors as if scanned through a poor-quality OCR system. Examples: J0hn Srnith, 
Micheal Johsnon, Sarali Clen.

REQUIREMENTS:
- Domain: healthcare or medical record
- Format: email (must include From, To, Subject headers, greeting, body, signature)
- Difficulty: hard (PII should be obfuscated, OCR-distorted, embedded in dense text)
- Context length: 1,000-4,000 characters
- Entity density: include 5-15 PII entities total
- Language: English only, no code-switching
- The text MUST contain at least one instance of the target pattern (OCR-distorted name)
- Also include these entity types naturally: PERSON names, DATE_OF_BIRTH, ADDRESS
- All PII must be completely fictional — do not use real people's information
- Make the text realistic — it should read like a genuine document from this domain
```

### Why temperature = 0.9

Temperature controls randomness in the LLM's output:
- 0.0 = always picks the most likely next word (deterministic, repetitive)
- 0.5 = moderate variety
- 0.9 = high variety (creative, diverse, unpredictable)
- 1.0 = maximum randomness

We use 0.9 because we want each record to be different. If we ran the same pattern with the same config twice at temp=0.0, we'd get nearly identical text. At 0.9, we get genuinely different documents each time.

### Max output: 8,192 tokens

This supports very_large contexts up to ~16,000 characters.

### The Output

Claude generates a complete text passage. For our example:

```
Subject: Urgent - Patient Trnasfer Documentation Required
From: Dr. Micheal Johsnon <m.johsnon@cityhospital.org>
To: Records Department <records@stmary.org>
CC: Nurse Practitioner Sarali Clen <s.clen@cityhospital.org>
Date: March 15, 2024 2:47 PM

Dear Records Team,

I am writing regarding the urgent transfer of patient Jmaes Thomspon 
(DOB: 07/22/1985, MRN: MED-2024-0847) from our emergency department 
at City General Hospital to St. Mary's cardiology unit. Mr. Thomspon 
was admitted on March 14, 2024 at approximately 11:30 PM following 
acute chest pain reported at his residence at 2847 Oak Avenue, Apt 4B, 
Springfield, IL 62704.

Initial assessment was performed by Dr. Micheal Johsnon (Employee ID: 
EMP-4821) and attending cardiologist Dr. Rlchard Wllson. Patient's 
emergency contact is listed as Marla Thomspon (spouse) at (555) 
234-8901, residing at the same address.

Please ensure all transfer documentation references the correct patient 
identifiers. Note that our OCR scanning system has been experiencing 
intermittent issues with name rendering in digital records.

Regards,
Dr. Micheal Johsnon, MD
Emergency Department
City General Hospital
Phone: (555) 678-2345
Email: m.johsnon@cityhospital.org
```

**Note the OCR distortions:** "Micheal Johsnon" (not Michael Johnson), "Sarali Clen" (not Sarah Chen), "Jmaes Thomspon" (not James Thompson), "Rlchard Wllson" (not Richard Wilson), "Marla Thomspon" (not Maria Thompson). This is exactly what the P-033 pattern requires.

**Note the format:** Proper email with Subject/From/To/CC/Date headers, greeting, body, signature — as required by the "email" format.

**Note the additional entities:** DOB (07/22/1985), Address (2847 Oak Avenue, Apt 4B, Springfield, IL 62704), Phone numbers, Employee ID — as required by the additional entity types.

This text is now saved in the pipeline state and passed to Step 3.

---

## Step 3: Entity Extraction — Claude Large (temperature = 0.0)

**What happens:** A completely separate API call. Claude receives ONLY the generated text (not the generation prompt). It must identify every PII entity with exact character positions.

### The Prompt (simplified)

```
You are extracting PII entities from the following text. For EVERY piece of 
personally identifiable information, extract:
- entity_type: one of [Full_Name, First_Name, Last_Name, Email, Phone, Address, 
  Date_of_Birth, Date_Time, Age, Salary, Job_Position, Org_Name, Location, City, 
  State, Country, Password, Religion, Nationality, Political_Party, Crime, 
  Sex_Orientation, SSN, ID_Card, Passport_Number, ...]
- text: the exact text as it appears (copy character-for-character)
- start: 0-indexed character position where the entity begins
- end: exclusive end position (Python convention: text[start:end] == entity text)

RULES:
- Extract EXHAUSTIVELY — do not skip any PII
- Triple name rule: for every person, extract Full_Name AND First_Name AND Last_Name
- Copy text EXACTLY as it appears — including typos, OCR errors, diacritics
- Offsets must be precise — text[start:end] must exactly equal the entity text
- Return a JSON array of entities

TEXT:
[the entire generated text from Step 2 is inserted here]
```

### Why temperature = 0.0

Extraction must be deterministic and consistent. If we ran extraction on the same text twice:
- At temp=0.0: identical output both times (same entities, same offsets)
- At temp=0.9: might extract different entities, miss some, add others randomly

Ground-truth labels cannot have randomness. That's why extraction is at zero temperature.

### The Output

Claude returns a JSON array:

```json
[
  {"entity_type": "Full_Name", "text": "Micheal Johsnon", "start": 67, "end": 82},
  {"entity_type": "Email", "text": "m.johsnon@cityhospital.org", "start": 84, "end": 110},
  {"entity_type": "Full_Name", "text": "Sarali Clen", "start": 158, "end": 169},
  {"entity_type": "Email", "text": "s.clen@cityhospital.org", "start": 171, "end": 194},
  {"entity_type": "Date_Time", "text": "March 15, 2024 2:47 PM", "start": 201, "end": 223},
  {"entity_type": "Full_Name", "text": "Jmaes Thomspon", "start": 289, "end": 303},
  {"entity_type": "Date_of_Birth", "text": "07/22/1985", "start": 311, "end": 321},
  {"entity_type": "ID_Card", "text": "MED-2024-0847", "start": 328, "end": 341},
  {"entity_type": "Date_Time", "text": "March 14, 2024", "start": 412, "end": 426},
  {"entity_type": "Address", "text": "2847 Oak Avenue, Apt 4B, Springfield, IL 62704", "start": 510, "end": 556},
  {"entity_type": "Full_Name", "text": "Rlchard Wllson", "start": 620, "end": 634},
  {"entity_type": "Full_Name", "text": "Marla Thomspon", "start": 678, "end": 692},
  {"entity_type": "Phone", "text": "(555) 234-8901", "start": 707, "end": 721},
  {"entity_type": "Org_Name", "text": "City General Hospital", "start": 845, "end": 866},
  {"entity_type": "Phone", "text": "(555) 678-2345", "start": 880, "end": 894},
  {"entity_type": "Email", "text": "m.johsnon@cityhospital.org", "start": 903, "end": 929}
]
```

**What each field means:**
- `start: 67` = if you count from the beginning of the text (starting at 0), the entity starts at character position 67
- `end: 82` = the entity ends at position 82 (exclusive — position 82 itself is NOT included)
- `text[67:82]` in Python would give you `"Micheal Johsnon"` — that's 15 characters

This entity list is now passed to Step 4 for verification.

---

## Step 4: Cross-Model Verification — GPT-4o-mini (temperature = 0.0)

**What happens:** A DIFFERENT model (GPT-4o-mini from OpenAI, not Claude from Anthropic) receives BOTH the text AND Claude's entity list from Step 3.

### Why a different model?

Claude and GPT-4o-mini are built by different companies with different training data and different failure modes. If Claude systematically misses a certain pattern (say, it never extracts OCR-distorted emails), a second Claude call would likely miss it too — they have correlated blind spots. GPT-4o-mini might catch what Claude misses, and vice versa.

This is the same principle as ensemble methods in machine learning: diversity among models improves robustness.

### What GPT-4o-mini does (5 checks)

1. **Offset verification:** For each entity, does the claimed text actually exist at positions [start:end]?
2. **Hallucination removal:** If Claude extracted an entity that doesn't appear in the text at all, GPT-4o-mini removes it
3. **Offset correction:** If the entity text exists but at a different position, fixes the offset
4. **Completeness check:** Scans the full text for any PII that Claude missed and adds it
5. **Type verification:** Checks if entity types are correct (is "City General Hospital" really an Org_Name?)

### Critical V1 prompt additions

**Completeness guardrail:**
```
If this text contains any PII at all, your entity list MUST NOT be empty.
An empty entity list is only valid if the text genuinely contains zero PII.
```

**Empty list recovery:**
```
If the received entity list is EMPTY but the text contains any PII (names, 
emails, dates, addresses, phone numbers, etc.), the prior extraction step 
FAILED. You MUST extract all PII from scratch yourself. Never return an 
empty entity list for a text that visibly contains PII.
```

### The Output

GPT-4o-mini returns a corrected entity list. This output **completely replaces** Claude's extraction from Step 3. Whatever GPT-4o-mini returns is now the entity list going forward.

For our example, suppose GPT-4o-mini:
- Confirmed all 16 entities from Claude
- Fixed one offset that was off by 2 characters
- Added 1 missed entity: `{"entity_type": "Employee_ID", "text": "EMP-4821", ...}` that Claude missed
- Removed nothing (no hallucinations)

Result: 17 entities in the corrected list.

---

## Step 5: Programmatic Validation — Python Lambda (deterministic)

**What happens:** Pure Python code (no LLM) runs exact verification on every entity. This is the critical quality guarantee.

### The Algorithm

```python
for each entity in the entity list from Step 4:
    
    # Get the text at the claimed position
    actual_text = generated_text[entity["start"] : entity["end"]]
    
    if actual_text == entity["text"]:
        # CASE 1: Perfect match. Offset is correct.
        # Keep entity as-is. Nothing to fix.
        pass
    
    elif entity["text"] in generated_text:
        # CASE 2: Entity text exists but at a DIFFERENT position.
        # The LLM miscounted character positions (common LLM error).
        # Search for the correct position and fix it.
        correct_start = generated_text.find(entity["text"])
        entity["start"] = correct_start
        entity["end"] = correct_start + len(entity["text"])
        # Now text[start:end] == entity["text"] is guaranteed.
        # Entity is KEPT with corrected offset.
    
    else:
        # CASE 3: Entity text does not exist anywhere in the passage.
        # The LLM hallucinated this entity — it made up text that
        # isn't in the document. 
        # DROP this entity entirely.
        remove(entity)
        validation_dropped += 1

# After processing all entities:
# Deduplicate: remove exact duplicates by (entity_type, text, start, end)
deduplicate(entity_list)
```

### Why this step is necessary

LLMs are fundamentally unreliable at counting character positions. They generate text token-by-token, not character-by-character. An LLM might say "Mike Johnson starts at position 77" when it actually starts at position 79. The LLM isn't lying — it genuinely can't count characters accurately.

The Python lambda doesn't have this problem. `generated_text.find("Mike Johnson")` will always return the exact correct position. This is why we achieve **100% offset accuracy** — every single entity in the final dataset has `text[start:end] == entity_text`, verified programmatically.

### What gets recorded

- The number of dropped hallucinations is saved in `validation_dropped` field
- The number of offset corrections is tracked internally
- The final clean entity list replaces the Step 4 output

For our example: 17 entities → 1 had wrong offset (fixed) → 0 hallucinations dropped → 17 entities remain with 100% correct offsets.

---

## Step 6: Schema Enrichment — Python (optional)

**What happens:** Each entity is classified along two dimensions. No LLM involved — this is rule-based Python code using the entity type.

### Classification 1: Identifier Type

| Category | Rule | Entity Types |
|---|---|---|
| Direct identifier | Can uniquely identify a person alone | Full_Name, Email, Phone, SSN, Passport, Credit_Card, etc. |
| Indirect identifier | Contributes to identification when combined with others | Age, City, Job_Position, Salary, Org_Name, etc. |

### Classification 2: Sensitivity Tier

| Tier | Rule | Entity Types |
|---|---|---|
| High | Most damaging if leaked | SSN, Password, Credit_Card, Crime, Sex_Orientation, Medical_Info |
| Medium | Significant privacy risk | Full_Name, Address, DOB, Religion, Political_Party |
| Low | Limited privacy risk alone | City, State, Country, Org_Name, Job_Position |

### Output

Each entity now has additional metadata:

```json
{
  "entity_type": "Full_Name",
  "text": "Micheal Johsnon",
  "start": 67,
  "end": 82,
  "identifier_type": "direct",
  "sensitivity": "medium"
}
```

This metadata is optional for Track 1 (Detection) evaluation but enables weighted metrics and supports Tracks 2–4.

---

## Final Output: The Complete Record

After all 6 steps, one record in the output JSON file looks like this:

```json
{
  "id": 147,
  "pattern_id": "P-033",
  "entity_type": "PERSON",
  "pattern_desc": "OCR-distorted full name (character substitution errors)",

  "text_domain": "healthcare or medical record",
  "text_format": "email",
  "difficulty": "hard",
  "context_length": "medium (1,000-4,000 characters, 1-2 paragraphs)",
  "entity_density": "medium (include 5-15 PII entities total)",
  "context_switching": "none (single language only, no mixing)",
  "language": "English",

  "generated_text": "Subject: Urgent - Patient Trnasfer Documentation Required\nFrom: Dr. Micheal Johsnon <m.johsnon@cityhospital.org>\nTo: Records Department <records@stmary.org>\n...[full text]...",

  "entities": [
    {
      "entity_type": "Full_Name",
      "text": "Micheal Johsnon",
      "start": 67,
      "end": 82
    },
    {
      "entity_type": "Email",
      "text": "m.johsnon@cityhospital.org",
      "start": 84,
      "end": 110
    },
    {
      "entity_type": "Date_of_Birth",
      "text": "07/22/1985",
      "start": 311,
      "end": 321
    },
    {
      "entity_type": "Address",
      "text": "2847 Oak Avenue, Apt 4B, Springfield, IL 62704",
      "start": 510,
      "end": 556
    }
    // ... 13 more entities ...
  ],

  "entity_count": 17,
  "validation_dropped": 0,
  
  "direct_identifiers": ["Full_Name", "Email", "Phone", "Date_of_Birth", "ID_Card"],
  "indirect_identifiers": ["Address", "Date_Time", "Org_Name"],
  
  "risk_metadata": {
    "sensitivity": "medium",
    "highest_risk_entity": "Date_of_Birth"
  }
}
```

---

## Summary: What Happens at Each Step

| Step | Who Does It | Input | Output | Key Property |
|---|---|---|---|---|
| 0. Seed | Pre-existing file | Nothing | Pattern row | 713 patterns × 52 types |
| 1. Sample | Python (random) | Pattern row | Pattern + 8-axis config | No LLM, pure random with weights |
| 2. Generate | Claude Large (τ=0.9) | Config | Realistic text passage | High creativity, diverse output |
| 3. Extract | Claude Large (τ=0.0) | Text only | Entity list with offsets | Deterministic, exhaustive |
| 4. Verify | GPT-4o-mini (τ=0.0) | Text + entity list | Corrected entity list | Cross-model, catches errors |
| 5. Validate | Python (deterministic) | Text + entity list | Verified entity list | 100% offset accuracy guaranteed |
| 6. Enrich | Python (rule-based) | Entity list | Classified entity list | Direct/indirect + sensitivity |

**Total API calls per record:** 3 (one generate + one extract + one verify)
**Total time per record:** ~4-5 seconds (varies by context length)
**Offset accuracy after pipeline:** 100%
