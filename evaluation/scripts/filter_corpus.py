"""
Corpus filter for PII Benchmark.

Applies the post-hoc filter + auto-repair pipeline to combine and clean
Run 1 + Run 2 (or any number of runs) into a paper-ready corpus.

Filter rules (drop):
    F1 - generation_status == "json_error"
    F2 - text empty/whitespace-only
    F3 - any entity has sensitivity_tier not in {HIGH, MEDIUM, LOW}
    F4 - any entity has entity_type not in 51-type canonical set
    F5 - any entity has disclosure_form not in {complete, partial, obfuscated}

Auto-repair (fix, don't drop):
    R1 - Multi-mention expansion: if entity_string appears K times in text
         but only M<K annotations exist, expand to K with mention_index 0..K-1
    R2 - Offset recomputation: deterministically assign (start, end) via
         text.find() with mention_index; verify text[start:end] == entity_string

Usage:
    python filter_corpus.py run1.json [run2.json ...] --out clean_corpus.json

Output:
    clean_corpus.json     # filtered + repaired records
    filter_report.json    # detailed counts and per-record drop reasons
"""

import json
import argparse
import sys
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

CANONICAL_ENTITY_TYPES = {
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    "Work_Email_Address", "Personal_Email_Address",
    "Telephone_Numbers_Work", "Telephone_Numbers_Personal",
    "Address_Work", "Address_Personal",
    "Date_of_Birth", "Age", "Gender", "Marital_Status", "Nationality",
    "Religion", "Sex_Orientation", "Political_Party", "Place_of_Birth",
    "Citizenship_Status",
    "Country_of_Residence", "State", "City", "Location", "Geolocation_Data",
    "National_Identification_Number", "Passport_Number",
    "Driving_License_Number", "Tax_Reference_Number",
    "Compensation_and_Salary", "Credit_Card_Numbers",
    "Customer_Reference_Number", "Account_Statements",
    "Business_Title", "Org_Name", "Employee_ID_Number",
    "Building_Badge_Card_Number", "Performance_Assessment",
    "Disciplinary_Action", "Sickness_Day_Records", "Professional_Background",
    "Crime", "PEP_Status", "Trade_Union_Membership",
    "Allergy_Information", "Medical_Information",
    "Social_Media_Identifiers", "Static_IP_Address", "Password",
    "Date_Time", "Emergency_Contact_Details",
}

VALID_SENSITIVITY_TIERS = {"HIGH", "MEDIUM", "LOW"}
VALID_DISCLOSURE_FORMS = {"complete", "partial", "obfuscated"}


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------

def filter_record(record: dict) -> tuple[bool, list[str]]:
    """
    Returns (keep, drop_reasons).
    keep=True means the record passes all filters and can proceed to repair.
    """
    reasons = []

    # F1
    if record.get("generation_status") == "json_error":
        reasons.append("F1_json_error")

    # F2
    text = record.get("text", "")
    if not isinstance(text, str) or not text.strip():
        reasons.append("F2_empty_text")
        return False, reasons  # No point checking further

    entities = record.get("entities", [])
    if not isinstance(entities, list):
        reasons.append("F0_entities_not_list")
        return False, reasons

    # F3, F4, F5 — record fails if ANY entity violates
    for e in entities:
        if not isinstance(e, dict):
            reasons.append("F0_entity_not_dict")
            break
        if e.get("sensitivity_tier") not in VALID_SENSITIVITY_TIERS:
            reasons.append(f"F3_invalid_sensitivity:{e.get('sensitivity_tier')!r}")
            break
        if e.get("entity_type") not in CANONICAL_ENTITY_TYPES:
            reasons.append(f"F4_non_canonical_type:{e.get('entity_type')}")
            break
        if e.get("disclosure_form") not in VALID_DISCLOSURE_FORMS:
            reasons.append(f"F5_invalid_disclosure_form:{e.get('disclosure_form')!r}")
            break

    return (len(reasons) == 0), reasons


# ---------------------------------------------------------------------------
# Auto-repair
# ---------------------------------------------------------------------------

def repair_record(record: dict) -> tuple[dict, dict]:
    """
    Apply R1 (multi-mention expansion) and R2 (offset recomputation).
    Returns (repaired_record, repair_stats).

    repair_stats fields:
        original_entity_count, repaired_entity_count
        multi_mentions_expanded     # number of (type, string) pairs that needed expansion
        new_entities_added          # total new entries created
        offset_assignments          # total entities with assigned (start, end)
        offset_mismatches           # entities where text[start:end] != entity_string
                                    # (should be 0 after repair)
    """
    text = record["text"]
    original_entities = record.get("entities", [])

    # Group original entities by (entity_type, entity_string) so we can keep
    # original metadata (disclosed, disclosure_form, sensitivity_tier) when
    # expanding multi-mentions.
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for e in original_entities:
        key = (e.get("entity_type", ""), e.get("entity_string", ""))
        grouped[key].append(e)

    repaired_entities = []
    multi_mentions_expanded = 0
    new_entities_added = 0
    offset_mismatches = 0

    for (et, es), original_list in grouped.items():
        if not es:
            continue
        # How many times does es occur in text?
        occurrences = []
        start = 0
        while True:
            idx = text.find(es, start)
            if idx == -1:
                break
            occurrences.append(idx)
            start = idx + 1
        k = len(occurrences)
        m = len(original_list)

        if k == 0:
            # entity_string not found in text — keep original entry as-is,
            # but flag offset_mismatch
            for orig in original_list:
                e = deepcopy(orig)
                e["start"] = None
                e["end"] = None
                e["repair_status"] = "string_not_in_text"
                repaired_entities.append(e)
                offset_mismatches += 1
            continue

        if m < k:
            multi_mentions_expanded += 1
            new_entities_added += (k - m)

        # Use the first original entry as the metadata template
        template = original_list[0]

        # Emit K entries with mention_index 0..K-1 and computed offsets
        for mi in range(k):
            e = deepcopy(template)
            e["mention_index"] = mi
            start_idx = occurrences[mi]
            end_idx = start_idx + len(es)
            e["start"] = start_idx
            e["end"] = end_idx
            e["repair_status"] = "ok" if m < k else "no_change"
            # Verify
            if text[start_idx:end_idx] != es:
                offset_mismatches += 1
                e["repair_status"] = "offset_verify_failed"
            repaired_entities.append(e)

    # Sort by (start, end) for consistency
    repaired_entities.sort(key=lambda e: (e.get("start") if e.get("start") is not None else 1e9,
                                            e.get("end") if e.get("end") is not None else 1e9))

    repaired_record = deepcopy(record)
    repaired_record["entities"] = repaired_entities
    repaired_record["entity_count"] = len(repaired_entities)
    repaired_record["_repair_applied"] = True

    stats = {
        "original_entity_count": len(original_entities),
        "repaired_entity_count": len(repaired_entities),
        "multi_mentions_expanded": multi_mentions_expanded,
        "new_entities_added": new_entities_added,
        "offset_assignments": len(repaired_entities),
        "offset_mismatches": offset_mismatches,
    }
    return repaired_record, stats


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter + repair PII Benchmark corpus(es)"
    )
    parser.add_argument(
        "corpus_paths",
        nargs="+",
        help="Path(s) to corpus JSON file(s). Multiple paths are concatenated.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="clean_corpus.json",
        help="Output path for the filtered + repaired corpus",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="filter_report.json",
        help="Output path for the detailed filter report",
    )
    args = parser.parse_args()

    # Load all input corpora
    all_records: list[dict] = []
    for path in args.corpus_paths:
        with open(path) as f:
            records = json.load(f)
        if not isinstance(records, list):
            print(f"ERROR: {path} is not a JSON list", file=sys.stderr)
            return 1
        # Tag each record with its source file for traceability
        for r in records:
            if isinstance(r, dict):
                r["_source_file"] = Path(path).name
        all_records.extend(records)
        print(f"Loaded {len(records):,} records from {path}")

    total_loaded = len(all_records)
    print(f"\nTotal records loaded: {total_loaded:,}")
    print()

    # Filter
    kept_records: list[dict] = []
    drop_reasons_by_record: list[dict] = []
    drop_category_counts: Counter = Counter()

    for r in all_records:
        keep, reasons = filter_record(r)
        if keep:
            kept_records.append(r)
        else:
            drop_reasons_by_record.append({
                "record_id": r.get("record_id"),
                "source_file": r.get("_source_file", "unknown"),
                "reasons": reasons,
            })
            for reason in reasons:
                category = reason.split(":")[0]
                drop_category_counts[category] += 1

    print("FILTER STAGE")
    print("-" * 60)
    print(f"Records loaded:    {total_loaded:>10,}")
    print(f"Records kept:      {len(kept_records):>10,} ({len(kept_records)/total_loaded:.1%})")
    print(f"Records dropped:   {total_loaded - len(kept_records):>10,} "
          f"({(total_loaded - len(kept_records))/total_loaded:.1%})")
    print()
    print("Drop reasons (records may fail multiple criteria; counted by primary):")
    for cat, c in drop_category_counts.most_common():
        print(f"  {cat:<35} {c:>6,}")
    print()

    # Repair
    print("REPAIR STAGE (R1 multi-mention expansion + R2 offset assignment)")
    print("-" * 60)
    repaired_records: list[dict] = []
    total_multi_expanded = 0
    total_new_entities = 0
    total_offset_mismatches = 0

    for r in kept_records:
        repaired, stats = repair_record(r)
        repaired_records.append(repaired)
        total_multi_expanded += stats["multi_mentions_expanded"]
        total_new_entities += stats["new_entities_added"]
        total_offset_mismatches += stats["offset_mismatches"]

    print(f"Records repaired:           {len(repaired_records):>10,}")
    print(f"Multi-mention groups expanded: {total_multi_expanded:>10,}")
    print(f"New entity entries added:   {total_new_entities:>10,}")
    print(f"Residual offset mismatches: {total_offset_mismatches:>10,}")
    print()

    if total_offset_mismatches > 0:
        print(f"WARN: {total_offset_mismatches} entities still have offset mismatches "
              f"after repair. These usually indicate entity_string is not present "
              f"in the text. Inspect filter_report.json for details.")
        print()

    # Strip internal fields before writing
    for r in repaired_records:
        r.pop("_source_file", None)
        # Keep _repair_applied for downstream traceability

    # Write output
    with open(args.out, "w") as f:
        json.dump(repaired_records, f, indent=2, ensure_ascii=False)

    # Write report
    report = {
        "input_files": args.corpus_paths,
        "total_loaded": total_loaded,
        "total_kept": len(kept_records),
        "total_dropped": total_loaded - len(kept_records),
        "drop_rate": (total_loaded - len(kept_records)) / total_loaded if total_loaded else 0,
        "drop_category_counts": dict(drop_category_counts.most_common()),
        "repair_stats": {
            "records_repaired": len(repaired_records),
            "multi_mention_groups_expanded": total_multi_expanded,
            "new_entity_entries_added": total_new_entities,
            "residual_offset_mismatches": total_offset_mismatches,
        },
        "final_corpus_size": len(repaired_records),
        "drop_details": drop_reasons_by_record[:200],  # cap for readability
    }
    with open(args.report, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Clean corpus written to: {args.out}")
    print(f"Filter report written to: {args.report}")
    print()
    print(f"FINAL: {len(repaired_records):,} clean records ready for analysis")

    return 0


if __name__ == "__main__":
    sys.exit(main())
