"""
Schema validator for PII Benchmark corpus records.

Verifies each record matches the expected v3.2 schema before downstream validation
metrics are computed. Fails fast on malformed records so that subsequent metric
computation isn't polluted by garbage data.

Usage:
    python schema_validator.py path/to/corpus.json

Outputs:
    schema_validation_report.json   # Detailed per-record findings
    stdout summary                  # Pass/fail count and top error categories

Authors: Anonymous Authors
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Any
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Schema spec
# ---------------------------------------------------------------------------

# 51 canonical entity types per methodology v3.2 §3.1.
# Renames documented in Appendix H of methodology_final.md.
CANONICAL_ENTITY_TYPES = {
    # Name family
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    # Contact
    "Work_Email_Address", "Personal_Email_Address",
    "Telephone_Numbers_Work", "Telephone_Numbers_Personal",
    "Address_Work", "Address_Personal",
    # Demographic and identity
    "Date_of_Birth", "Age", "Gender", "Marital_Status", "Nationality",
    "Religion", "Sex_Orientation", "Political_Party", "Place_of_Birth",
    "Citizenship_Status",
    # Geographic
    "Country_of_Residence", "State", "City", "Location", "Geolocation_Data",
    # Government IDs
    "National_Identification_Number", "Passport_Number",
    "Driving_License_Number", "Tax_Reference_Number",
    # Financial
    "Compensation_and_Salary", "Credit_Card_Numbers",
    "Customer_Reference_Number", "Account_Statements",
    # Employment and organization
    "Business_Title", "Org_Name", "Employee_ID_Number",
    "Building_Badge_Card_Number", "Performance_Assessment",
    "Disciplinary_Action", "Sickness_Day_Records", "Professional_Background",
    # Sensitive compliance
    "Crime", "PEP_Status", "Trade_Union_Membership",
    # Health
    "Allergy_Information", "Medical_Information",
    # Digital and other
    "Social_Media_Identifiers", "Static_IP_Address", "Password",
    "Date_Time", "Emergency_Contact_Details",
}

REQUIRED_RECORD_FIELDS = {
    "record_id", "mode", "axes", "target_entity_type", "target_pattern_id",
    "behavioral_frame", "text", "entities", "entity_count", "generation_status",
}

REQUIRED_AXIS_FIELDS = {
    "domain", "format", "difficulty", "length", "density",
    "code_switching", "language", "adjacency", "co_occurrence_pattern",
}

REQUIRED_ENTITY_FIELDS = {
    "entity_type", "entity_string", "mention_index",
    "disclosed", "disclosure_form", "sensitivity_tier",
}

VALID_SENSITIVITY_TIERS = {"HIGH", "MEDIUM", "LOW"}
VALID_DISCLOSURE_FORMS = {"complete", "partial", "obfuscated"}
VALID_MODES = {"coverage", "paired_sweep"}
VALID_ADJACENCY = {"none", "loose", "tight"}
VALID_GENERATION_STATUS = {"ok", "verified", "repaired", "failed"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_record(record: dict[str, Any], record_index: int) -> list[str]:
    """
    Validate a single record. Returns a list of error strings (empty = pass).

    Errors are short, specific, and include the field name so they can be
    aggregated by error category in the summary.
    """
    errors: list[str] = []

    # Top-level required fields
    missing = REQUIRED_RECORD_FIELDS - set(record.keys())
    if missing:
        errors.append(f"missing_top_level_fields:{','.join(sorted(missing))}")

    # Axes
    if "axes" in record:
        if not isinstance(record["axes"], dict):
            errors.append("axes_not_dict")
        else:
            missing_axes = REQUIRED_AXIS_FIELDS - set(record["axes"].keys())
            if missing_axes:
                errors.append(f"missing_axis_fields:{','.join(sorted(missing_axes))}")

            adj = record["axes"].get("adjacency")
            if adj is not None and adj not in VALID_ADJACENCY:
                errors.append(f"invalid_adjacency:{adj}")

    # Mode
    mode = record.get("mode")
    if mode is not None and mode not in VALID_MODES:
        errors.append(f"invalid_mode:{mode}")

    # Generation status
    status = record.get("generation_status")
    if status is not None and status not in VALID_GENERATION_STATUS:
        errors.append(f"invalid_generation_status:{status}")

    # Text presence and type
    text = record.get("text")
    if text is None or not isinstance(text, str):
        errors.append("text_missing_or_not_str")
    elif len(text) == 0:
        errors.append("text_empty")

    # Entities
    entities = record.get("entities")
    if entities is None or not isinstance(entities, list):
        errors.append("entities_missing_or_not_list")
        return errors  # Cannot continue entity-level checks

    # entity_count consistency
    declared_count = record.get("entity_count")
    if declared_count is not None and declared_count != len(entities):
        errors.append(
            f"entity_count_mismatch:declared={declared_count},actual={len(entities)}"
        )

    # Per-entity validation
    for ei, entity in enumerate(entities):
        if not isinstance(entity, dict):
            errors.append(f"entity[{ei}]:not_dict")
            continue

        missing_e = REQUIRED_ENTITY_FIELDS - set(entity.keys())
        if missing_e:
            errors.append(
                f"entity[{ei}]:missing_fields:{','.join(sorted(missing_e))}"
            )
            continue  # Skip further checks on this entity

        et = entity["entity_type"]
        if et not in CANONICAL_ENTITY_TYPES:
            errors.append(f"entity[{ei}]:non_canonical_type:{et}")

        es = entity["entity_string"]
        if not isinstance(es, str) or len(es) == 0:
            errors.append(f"entity[{ei}]:entity_string_invalid")

        mi = entity["mention_index"]
        if not isinstance(mi, int) or mi < 0:
            errors.append(f"entity[{ei}]:mention_index_invalid:{mi}")

        d = entity["disclosed"]
        if not isinstance(d, bool):
            errors.append(f"entity[{ei}]:disclosed_not_bool:{d}")

        df = entity["disclosure_form"]
        if df not in VALID_DISCLOSURE_FORMS:
            errors.append(f"entity[{ei}]:invalid_disclosure_form:{df}")

        st = entity["sensitivity_tier"]
        if st not in VALID_SENSITIVITY_TIERS:
            errors.append(f"entity[{ei}]:invalid_sensitivity_tier:{st}")

    # mention_index uniqueness per (entity_type, entity_string)
    seen: dict[tuple[str, str], set[int]] = defaultdict(set)
    for ei, entity in enumerate(entities):
        if not isinstance(entity, dict):
            continue
        if "entity_type" not in entity or "entity_string" not in entity:
            continue
        key = (entity["entity_type"], entity["entity_string"])
        mi = entity.get("mention_index")
        if not isinstance(mi, int):
            continue
        if mi in seen[key]:
            errors.append(
                f"entity[{ei}]:duplicate_mention_index:"
                f"{entity['entity_type']}:{entity['entity_string']}:{mi}"
            )
        seen[key].add(mi)

    return errors


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Schema validator for PII Benchmark corpus records"
    )
    parser.add_argument(
        "corpus_path",
        type=str,
        help="Path to corpus JSON file (a JSON list of records)",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="schema_validation_report.json",
        help="Output path for the detailed validation report",
    )
    args = parser.parse_args()

    corpus_path = Path(args.corpus_path)
    if not corpus_path.exists():
        print(f"ERROR: corpus file not found: {corpus_path}", file=sys.stderr)
        return 1

    with open(corpus_path) as f:
        records = json.load(f)

    if not isinstance(records, list):
        print("ERROR: corpus file is not a JSON list", file=sys.stderr)
        return 1

    total = len(records)
    pass_count = 0
    fail_count = 0
    error_counter: Counter = Counter()
    per_record_findings = []

    for ri, record in enumerate(records):
        errors = validate_record(record, ri)
        rid = record.get("record_id", ri) if isinstance(record, dict) else ri
        if not errors:
            pass_count += 1
        else:
            fail_count += 1
            for e in errors:
                # Aggregate by error prefix (before the colon, for grouping)
                category = e.split(":")[0]
                error_counter[category] += 1
        per_record_findings.append({
            "record_id": rid,
            "record_index": ri,
            "n_errors": len(errors),
            "errors": errors,
        })

    report = {
        "total_records": total,
        "passed": pass_count,
        "failed": fail_count,
        "pass_rate": pass_count / total if total else 0.0,
        "top_error_categories": error_counter.most_common(20),
        "records": per_record_findings,
    }

    out_path = Path(args.out)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Stdout summary
    print("=" * 60)
    print("SCHEMA VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total records:     {total}")
    print(f"Passed:            {pass_count} ({pass_count / total:.1%})")
    print(f"Failed:            {fail_count} ({fail_count / total:.1%})")
    print()
    if error_counter:
        print("Top error categories:")
        for category, count in error_counter.most_common(10):
            print(f"  {category:<40} {count:>6}")
    print()
    print(f"Detailed report written to: {out_path}")

    # Exit code 0 if all pass, 1 if any fail
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
