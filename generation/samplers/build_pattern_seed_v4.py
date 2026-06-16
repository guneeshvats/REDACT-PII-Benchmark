"""Parse PII_Pattern_Catalog_v4_MASTER.md → pattern_seed_data_v4.json.

The catalog markdown has 51 entity sections, each with:
  - A Natural Patterns table (id | pattern_name | description | examples)
  - A Cross-Cutting Consistency Sweep table (dimension | status | pattern_ids)
  - A "Total patterns for X: N" line

This script parses all of that into a structured JSON suitable for the
covering-array sampler and the v3 CO-### → v4 anchor lookup.

Output schema:

  {
    "version": "v4-1.0",
    "stats": {...},
    "categories": {<entity_name>: <category_name>},
    "entities": {
      <entity_name>: {
        "entity_number": int,
        "entity_category": str,
        "prefix": str,
        "description": str,
        "pattern_count": int,
        "patterns": [<pattern_obj>],
        "cross_cutting_sweep": {<dimension>: [pattern_ids]}
      }
    },
    "patterns_flat": [<pattern_obj>],  // all 4,127 entries
    "patterns_by_id": {<pattern_id>: <pattern_obj>}
  }

  where <pattern_obj> = {
    "pattern_id": "FUN-001",
    "entity_type": "Full_Name",
    "entity_number": 1,
    "entity_category": "Name Family",
    "name": "First Last (Western canonical)",
    "description": "Standard given + family order",
    "examples": ["John Smith", "Sarah Chen", ...],
    "dimensions": ["OCR-distorted", "Adjacency-tight", ...],  // from sweep cross-ref
    "language_hint": "EN" | "JP" | null  // inferred from name/desc when explicit
  }
"""

import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "PII_Pattern_Catalog_v4_MASTER 1.md"  # filename has " 1" per upload
DST = HERE / "pattern_seed_data_v4.json"

# ── Static category mapping (per Catalog §2.1 batches → 10 thematic categories)
CATEGORY_MAP = {
    # Name Family (4)
    "Full_Name": "Name Family",
    "First_Given_Name": "Name Family",
    "Last_Family_Name": "Name Family",
    "Preferred_Name": "Name Family",
    # Contact Information (6) + Business_Title from Employment? — checking original
    # Actually Catalog v3 grouped: Name Family (4), Contact Information (6), Demographic & Identity (10),
    # Geographic (5), Government IDs (4), Financial (4), Employment & Organization (8),
    # Sensitive Compliance (3), Health (2), Digital & Other (5)
    # But v4 catalog has Business_Title in Batch 1 (Names + Title) — putting it with Names.
    "Business_Title": "Name Family",
    # Contact (5 remaining)
    "Address_Work": "Contact Information",
    "Address_Personal": "Contact Information",
    "Telephone_Numbers_Work": "Contact Information",
    "Telephone_Numbers_Personal": "Contact Information",
    "Work_Email_Address": "Contact Information",
    "Personal_Email_Address": "Contact Information",
    # Demographic & Identity (8)
    "Date_of_Birth": "Demographic and Identity",
    "Age": "Demographic and Identity",
    "Place_of_Birth": "Demographic and Identity",
    "Gender": "Demographic and Identity",
    "Marital_Status": "Demographic and Identity",
    "Nationality": "Demographic and Identity",
    "Citizenship_Status": "Demographic and Identity",
    "Sex_Orientation": "Demographic and Identity",
    "Religion": "Demographic and Identity",
    "Political_Party": "Demographic and Identity",
    # Geographic (5)
    "Country_of_Residence": "Geographic",
    "State": "Geographic",
    "City": "Geographic",
    "Location": "Geographic",
    "Geolocation_Data": "Geographic",
    # Government IDs (4)
    "National_Identification_Number": "Government IDs",
    "Passport_Number": "Government IDs",
    "Driving_License_Number": "Government IDs",
    "Tax_Reference_Number": "Government IDs",
    # Financial (4)
    "Compensation_and_Salary": "Financial",
    "Credit_Card_Numbers": "Financial",
    "Customer_Reference_Number": "Financial",
    "Account_Statements": "Financial",
    # Employment & Organization (7 since Business_Title is in Name Family)
    "Employee_ID_Number": "Employment and Organization",
    "Building_Badge_Card_Number": "Employment and Organization",
    "Performance_Assessment": "Employment and Organization",
    "Disciplinary_Action": "Employment and Organization",
    "Sickness_Day_Records": "Employment and Organization",
    "Professional_Background": "Employment and Organization",
    "Org_Name": "Employment and Organization",
    # Sensitive Compliance (3)
    "Crime": "Sensitive Compliance",
    "PEP_Status": "Sensitive Compliance",
    "Trade_Union_Membership": "Sensitive Compliance",
    # Health (2)
    "Allergy_Information": "Health",
    "Medical_Information": "Health",
    # Digital & Other (5)
    "Social_Media_Identifiers": "Digital and Other",
    "Static_IP_Address": "Digital and Other",
    "Password": "Digital and Other",
    "Date_Time": "Digital and Other",
    "Emergency_Contact_Details": "Digital and Other",
}

# Language hint detection — pattern name/description tokens to language code
LANGUAGE_TOKENS = {
    "EN": ["english", "western canonical", "us standard"],
    "FR": ["french", "français", "canadian french"],
    "DE": ["german", "deutsch"],
    "IT": ["italian", "italiano"],
    "ES": ["spanish", "español"],
    "PT": ["portuguese", "brazilian", "português"],
    "JA": ["japanese", "japan", "kanji", "hiragana", "katakana", "tokyo", "yamada"],
    "ZH": ["chinese", "hanzi", "pinyin", "traditional chinese", "simplified chinese"],
    "KO": ["korean", "hangul"],
    "AR": ["arabic", "ibn", "bint", "kunya", "nasab"],
    "HE": ["hebrew"],
    "TH": ["thai", "buddhist era"],
    "RU": ["russian", "cyrillic", "patronymic"],
    "TR": ["turkish"],
    "PL": ["polish"],
    "NL": ["dutch"],
    "CS": ["czech"],
    "HU": ["hungarian"],
    "SV": ["swedish"],
    "FI": ["finnish"],
    "NO": ["norwegian"],
    "DA": ["danish"],
    "EL": ["greek"],
    "HI": ["hindi", "devanagari"],
    "VI": ["vietnamese"],
    "IS": ["icelandic"],
}


def split_examples_cell(cell: str) -> list:
    """Examples are comma-separated, sometimes with semicolons or pipes inside.
    Conservative split on commas only; preserve quoted multi-word names."""
    if not cell or cell.strip() == "—":
        return []
    # Don't split on commas inside parentheses or quotes
    out = []
    depth = 0
    in_quote = False
    current = []
    for ch in cell:
        if ch == '"' and (not current or current[-1] != "\\"):
            in_quote = not in_quote
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0 and not in_quote:
            ex = "".join(current).strip()
            if ex:
                out.append(ex)
            current = []
        else:
            current.append(ch)
    if current:
        ex = "".join(current).strip()
        if ex:
            out.append(ex)
    return out


def infer_language_hint(name: str, desc: str) -> str | None:
    """Match pattern name + description against language token table."""
    haystack = (name + " " + desc).lower()
    for lang, tokens in LANGUAGE_TOKENS.items():
        for tok in tokens:
            if tok in haystack:
                return lang
    return None


def parse_pattern_table_row(line: str) -> dict | None:
    """Parse one row of the Natural Patterns table.
    Expected: | ID | Pattern | Description | Examples |
    """
    if not line.strip().startswith("|") or not line.strip().endswith("|"):
        return None
    # Skip separator rows
    if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
        return None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4:
        return None
    pid = cells[0]
    # Pattern ID must match PREFIX-NNN format
    if not re.match(r"^[A-Z]{2,6}-\d{3}$", pid):
        return None
    return {
        "pattern_id": pid,
        "name": cells[1],
        "description": cells[2],
        "examples_raw": cells[3],
        "examples": split_examples_cell(cells[3]),
    }


def parse_sweep_table_row(line: str) -> tuple | None:
    """Parse one row of the Cross-Cutting Consistency Sweep table.
    Expected: | Dimension name | Status (✓/✗) | Pattern IDs (referenced) |
    """
    if not line.strip().startswith("|") or not line.strip().endswith("|"):
        return None
    if re.match(r"^\|[\s\-:|]+\|$", line.strip()):
        return None
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3:
        return None
    dim = cells[0]
    status = cells[1]
    refs_cell = cells[2]
    # Skip header row
    if dim.lower().startswith("cross-cutting") or dim.lower().startswith("dimension"):
        return None
    # Extract all pattern IDs referenced
    refs = re.findall(r"[A-Z]{2,6}-\d{3}", refs_cell)
    return dim, status, refs


def parse_entity_section(section_text: str, entity_name: str, entity_number: int) -> dict:
    """Parse one entity section. Returns the entity dict."""
    lines = section_text.split("\n")

    # 1. Extract description paragraph (between the H2 and the first H3)
    desc_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith("###"):
            break
        if line.strip() and not line.startswith("##"):
            desc_lines.append(line.strip())
    description = " ".join(desc_lines).strip()

    # 2. Find the Natural Patterns and Cross-Cutting Sweep table boundaries
    patterns_start = None
    sweep_start = None
    for i, line in enumerate(lines):
        if "### Natural Patterns" in line:
            patterns_start = i
        elif "### Cross-Cutting" in line or "Cross-Cutting Consistency Sweep" in line:
            sweep_start = i

    # 3. Parse Natural Patterns table
    patterns = []
    if patterns_start is not None:
        end = sweep_start if sweep_start else len(lines)
        for line in lines[patterns_start:end]:
            row = parse_pattern_table_row(line)
            if row:
                row["entity_type"] = entity_name
                row["entity_number"] = entity_number
                row["entity_category"] = CATEGORY_MAP.get(entity_name, "Unknown")
                row["language_hint"] = infer_language_hint(row["name"], row["description"])
                row["dimensions"] = []  # filled by sweep cross-ref below
                patterns.append(row)

    # 4. Parse Cross-Cutting Consistency Sweep table
    sweep_dimensions = {}  # {dimension_name: [pattern_ids]}
    if sweep_start is not None:
        for line in lines[sweep_start:]:
            parsed = parse_sweep_table_row(line)
            if parsed:
                dim, status, refs = parsed
                if "✓" in status or status.lower() in ("yes", "true"):
                    sweep_dimensions[dim] = refs

    # 5. Cross-reference dimensions back into individual patterns
    pid_to_dims = defaultdict(list)
    for dim, refs in sweep_dimensions.items():
        for pid in refs:
            pid_to_dims[pid].append(dim)
    for p in patterns:
        p["dimensions"] = pid_to_dims.get(p["pattern_id"], [])

    # 6. Extract the "Total patterns for X: N" line for validation
    total_match = re.search(r"\*\*Total patterns for [^:]+:\s*(\d+)\*\*", section_text)
    declared_count = int(total_match.group(1)) if total_match else None

    # 7. Determine prefix from first pattern
    prefix = patterns[0]["pattern_id"].split("-")[0] if patterns else None

    return {
        "entity_number": entity_number,
        "entity_category": CATEGORY_MAP.get(entity_name, "Unknown"),
        "prefix": prefix,
        "description": description,
        "pattern_count": len(patterns),
        "declared_count": declared_count,
        "patterns": patterns,
        "cross_cutting_sweep": sweep_dimensions,
    }


def main():
    text = SRC.read_text(encoding="utf-8")

    # Split into entity sections by the H2 entity headers
    entity_pattern = re.compile(r"^## Entity (\d+): (\w+)\s*$", re.MULTILINE)
    matches = list(entity_pattern.finditer(text))
    print(f"Found {len(matches)} entity sections")

    entities = {}
    all_patterns_flat = []
    patterns_by_id = {}
    parse_warnings = []

    for i, m in enumerate(matches):
        entity_num = int(m.group(1))
        entity_name = m.group(2)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end]

        entity_data = parse_entity_section(section, entity_name, entity_num)
        entities[entity_name] = entity_data

        # Track flat list and ID index
        for p in entity_data["patterns"]:
            all_patterns_flat.append(p)
            if p["pattern_id"] in patterns_by_id:
                parse_warnings.append(f"Duplicate pattern_id {p['pattern_id']}")
            patterns_by_id[p["pattern_id"]] = p

        # Validate count
        if entity_data["declared_count"] is not None:
            if entity_data["pattern_count"] != entity_data["declared_count"]:
                parse_warnings.append(
                    f"{entity_name}: declared {entity_data['declared_count']} but parsed {entity_data['pattern_count']}"
                )

    # ── Stats ────────────────────────────────────────────────────────────────
    patterns_per_entity = {name: ed["pattern_count"] for name, ed in entities.items()}
    patterns_per_category: dict = defaultdict(int)
    for name, ed in entities.items():
        patterns_per_category[ed["entity_category"]] += ed["pattern_count"]
    patterns_per_dimension: dict = defaultdict(int)
    for p in all_patterns_flat:
        for d in p["dimensions"]:
            patterns_per_dimension[d] += 1
    patterns_per_language: dict = defaultdict(int)
    for p in all_patterns_flat:
        if p["language_hint"]:
            patterns_per_language[p["language_hint"]] += 1

    output = {
        "version": "v4-1.0",
        "generated_on": "2026-05-19",
        "source": "PII_Pattern_Catalog_v4_MASTER 1.md",
        "stats": {
            "total_entities": len(entities),
            "total_patterns": len(all_patterns_flat),
            "patterns_per_entity": dict(sorted(patterns_per_entity.items())),
            "patterns_per_category": dict(sorted(patterns_per_category.items())),
            "patterns_per_dimension": dict(sorted(patterns_per_dimension.items(), key=lambda kv: -kv[1])),
            "patterns_per_language_hint": dict(sorted(patterns_per_language.items(), key=lambda kv: -kv[1])),
            "parse_warnings": parse_warnings,
        },
        "categories": dict(sorted(CATEGORY_MAP.items())),
        "entities": entities,
        "patterns_flat": all_patterns_flat,
        "patterns_by_id": patterns_by_id,
    }

    DST.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nWrote {DST}")
    print(f"Size: {DST.stat().st_size / 1024:.1f} KB")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n=== STATS ===")
    print(f"Entities: {len(entities)}")
    print(f"Total patterns: {len(all_patterns_flat)} (target: 4,127)")
    if len(all_patterns_flat) == 4127:
        print("  ✓ Pattern count matches target exactly")
    else:
        diff = 4127 - len(all_patterns_flat)
        print(f"  ⚠ Off by {diff} patterns")

    print(f"\nPer-category breakdown:")
    for cat, n in sorted(patterns_per_category.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:<35} {n}")

    print(f"\nTop 10 dimensions by pattern coverage:")
    top_dims = sorted(patterns_per_dimension.items(), key=lambda kv: -kv[1])[:10]
    for dim, n in top_dims:
        print(f"  {dim[:55]:<55} {n}")

    print(f"\nLanguage hints (inferred from pattern names):")
    for lang, n in sorted(patterns_per_language.items(), key=lambda kv: -kv[1])[:15]:
        print(f"  {lang:<5} {n}")

    if parse_warnings:
        print(f"\n=== WARNINGS ({len(parse_warnings)}) ===")
        for w in parse_warnings[:20]:
            print(f"  ⚠ {w}")


if __name__ == "__main__":
    main()
