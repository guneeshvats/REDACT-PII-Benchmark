"""
Family B (Annotation Integrity) + Family A2 (Per-entity floor).

This script computes the methodology's CRITICAL release-gate metrics — the
ones that, if violated, block corpus release entirely.

Metrics:
    B1 - Offset accuracy
        Fraction of entities for which text[start:end] == entity_string
        where (start, end) is computed deterministically by Python from
        entity_string + mention_index. Target: 100.0%.

    B2 - Zero-entity rate
        Records with 0 entities / total records. Target: <= 0.5%.

    B3 - Validation-dropped rate
        Mean over records of (dropped / extracted) ratio. Currently not
        computable from output schema (no `dropped` field), so reported
        as not_computable.

    B4 - Triple-name rule compliance
        For every Full_Name span "First Last", a First_Given_Name "First"
        and a Last_Family_Name "Last" must appear in the same record.
        Target: 100%.

    B5 - Canonical-type compliance
        Fraction of entities whose entity_type is in the 51-type set.
        Target: 100%.

    B6 - Multi-mention completeness
        For each (entity_type, entity_string) that appears more than once
        in the text, are all occurrences emitted as separate entity entries
        with distinct mention_index values? Target: >= 95%.

    B7 - Nesting consistency
        For each entity whose string is a substring of another entity in
        the same record, log this as a nesting case. (Methodology's B7 asks
        whether nested entries have a `nesting_parent`; the current schema
        doesn't include that field, so we just report nesting counts.)

    A2 - Per-entity-type floor
        Minimum count of records (across the corpus) covering each of the
        51 entity types. Target: every type >= 50 records.

Usage:
    python compute_critical_gates.py path/to/corpus.json
"""

import json
import argparse
import sys
from pathlib import Path
from collections import Counter, defaultdict


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


# ---------------------------------------------------------------------------
# B1 - Offset accuracy
# ---------------------------------------------------------------------------

def compute_offset_for_entity(text: str, entity_string: str,
                                mention_index: int) -> tuple[int, int] | None:
    """
    Find the (start, end) of the mention_index-th occurrence of entity_string
    in text. Returns None if not enough occurrences exist.

    This is the deterministic alignment procedure that the methodology says
    happens at Stage 3 of the pipeline. It must return correct offsets for
    100% of entities; any failure here is a B1 violation.
    """
    if not entity_string:
        return None
    start = 0
    for _ in range(mention_index + 1):
        idx = text.find(entity_string, start)
        if idx == -1:
            return None
        start = idx + 1  # start next search just after this match start
    # idx is the index of the (mention_index)-th occurrence
    return idx, idx + len(entity_string)


def check_offset_accuracy(record: dict) -> tuple[int, int, list[dict]]:
    """
    Returns (n_total, n_aligned, failures).
    n_aligned is the count of entities for which text[start:end] == entity_string.
    failures is a list of {entity_index, entity_type, entity_string, reason}.
    """
    text = record.get("text", "")
    entities = record.get("entities", [])
    n_total = len(entities)
    n_aligned = 0
    failures: list[dict] = []

    for ei, entity in enumerate(entities):
        es = entity.get("entity_string", "")
        mi = entity.get("mention_index", 0)
        et = entity.get("entity_type", "")
        offsets = compute_offset_for_entity(text, es, mi)
        if offsets is None:
            failures.append({
                "entity_index": ei,
                "entity_type": et,
                "entity_string": es,
                "mention_index": mi,
                "reason": "not_found_in_text",
            })
            continue
        start, end = offsets
        substring = text[start:end]
        if substring == es:
            n_aligned += 1
        else:
            failures.append({
                "entity_index": ei,
                "entity_type": et,
                "entity_string": es,
                "mention_index": mi,
                "reason": "substring_mismatch",
                "found_substring": substring,
            })

    return n_total, n_aligned, failures


# ---------------------------------------------------------------------------
# B4 - Triple-name rule
# ---------------------------------------------------------------------------

def check_triple_name_rule(record: dict) -> tuple[int, int, list[dict]]:
    """
    For each Full_Name in the record, check that there exists a First_Given_Name
    matching the first token and a Last_Family_Name matching the rest.

    Returns (n_full_names, n_compliant, violations).

    NOTE: This is the SIMPLE case (Western "First Last"). Methodology R11
    documents 8 decomposition cases — CJK without space, double surnames,
    patronymic, etc. — that this baseline does not handle. The baseline is
    sufficient as a sanity check; report-level tuning may be needed once we
    see the generation team's full corpus and adjust per-language rules.
    """
    entities = record.get("entities", [])
    full_names = [e for e in entities
                  if e.get("entity_type") == "Full_Name"]
    first_names = {e.get("entity_string") for e in entities
                   if e.get("entity_type") == "First_Given_Name"}
    last_names = {e.get("entity_string") for e in entities
                  if e.get("entity_type") == "Last_Family_Name"}

    n_total = len(full_names)
    n_compliant = 0
    violations: list[dict] = []

    for fn in full_names:
        fn_str = fn.get("entity_string", "")
        # Simple Western parse: first token = first name, rest = last name
        # Methodology R11 documents 8 cases; this handles the dominant one.
        tokens = fn_str.split()
        if len(tokens) < 2:
            # Single-token name (e.g. mononym) - mark as compliant by exception
            n_compliant += 1
            continue
        first_token = tokens[0]
        rest = " ".join(tokens[1:])

        first_match = first_token in first_names
        last_match = rest in last_names

        if first_match and last_match:
            n_compliant += 1
        else:
            violations.append({
                "full_name": fn_str,
                "expected_first": first_token,
                "expected_last": rest,
                "first_match": first_match,
                "last_match": last_match,
            })

    return n_total, n_compliant, violations


# ---------------------------------------------------------------------------
# B5 - Canonical-type compliance
# ---------------------------------------------------------------------------

def check_canonical_types(record: dict) -> tuple[int, int, list[str]]:
    """Returns (n_total, n_canonical, non_canonical_types_found)."""
    entities = record.get("entities", [])
    n_total = len(entities)
    n_canonical = 0
    non_canonical: list[str] = []
    for e in entities:
        et = e.get("entity_type", "")
        if et in CANONICAL_ENTITY_TYPES:
            n_canonical += 1
        else:
            non_canonical.append(et)
    return n_total, n_canonical, non_canonical


# ---------------------------------------------------------------------------
# B6 - Multi-mention completeness
# ---------------------------------------------------------------------------

def check_multi_mention_completeness(record: dict) -> tuple[int, int, list[dict]]:
    """
    For each unique (entity_type, entity_string) in the entity list, check
    whether all occurrences in the text are emitted as separate entries
    with distinct mention_index values.

    Returns (n_unique_strings, n_complete, missing_mentions).

    "Complete" means: if entity_string appears K times in the text and the
    annotations include mention_indices 0..K-1, that's complete. If the
    annotations only cover M < K occurrences, that's a violation.
    """
    text = record.get("text", "")
    entities = record.get("entities", [])

    # Group emitted entities by (entity_type, entity_string)
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for e in entities:
        key = (e.get("entity_type", ""), e.get("entity_string", ""))
        grouped[key].append(e.get("mention_index", 0))

    n_unique = len(grouped)
    n_complete = 0
    missing: list[dict] = []

    for (et, es), mentions in grouped.items():
        if not es:
            continue
        # Count occurrences of es in text
        n_in_text = text.count(es)
        if n_in_text >= len(mentions):
            # Are all mention_indices 0..len(mentions)-1 present?
            expected = set(range(len(mentions)))
            actual = set(mentions)
            if expected == actual and n_in_text == len(mentions):
                n_complete += 1
            elif n_in_text == len(mentions):
                # Index mismatch (non-contiguous), still a problem
                missing.append({
                    "entity_type": et,
                    "entity_string": es,
                    "occurrences_in_text": n_in_text,
                    "mentions_emitted": len(mentions),
                    "indices": sorted(mentions),
                    "issue": "non_contiguous_indices",
                })
            else:
                # n_in_text > emitted: a real coverage gap
                missing.append({
                    "entity_type": et,
                    "entity_string": es,
                    "occurrences_in_text": n_in_text,
                    "mentions_emitted": len(mentions),
                    "issue": "missing_mentions",
                })
        # If n_in_text < len(mentions), that's a different bug (false annotations
        # claiming more mentions than exist) - caught by B1 offset accuracy.

    return n_unique, n_complete, missing


# ---------------------------------------------------------------------------
# A2 - Per-entity-type floor (corpus-level)
# ---------------------------------------------------------------------------

def compute_per_entity_floor(records: list[dict]) -> dict:
    """
    For each of the 51 canonical types, count the number of *records* that
    contain at least one entity of that type. Target: >= 50 per type.

    Returns a dict {entity_type: count, ...} for all 51 types.
    """
    counts = Counter()
    # Track per-record presence (not per-entity), since a record with 5
    # Full_Name spans should count as 1, not 5, toward "records covering"
    for r in records:
        types_in_record = {e.get("entity_type", "")
                          for e in r.get("entities", [])}
        types_in_record &= CANONICAL_ENTITY_TYPES
        for t in types_in_record:
            counts[t] += 1

    result = {t: counts.get(t, 0) for t in CANONICAL_ENTITY_TYPES}
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute Family B (Annotation Integrity) + A2 (Per-entity floor) metrics"
    )
    parser.add_argument("corpus_path", type=str)
    parser.add_argument("--out", type=str, default="critical_gates_report.json")
    parser.add_argument(
        "--floor-target",
        type=int,
        default=50,
        help="Per-entity-type floor target (methodology default: 50)",
    )
    args = parser.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)

    n_records = len(records)
    if n_records == 0:
        print("ERROR: empty corpus", file=sys.stderr)
        return 1

    # Aggregates
    total_entities = 0
    total_aligned = 0
    b1_failures_per_record: list[dict] = []

    n_zero_entity = 0
    n_full_names = 0
    n_triple_name_compliant = 0
    b4_violations_per_record: list[dict] = []

    n_canonical_entities = 0
    b5_violations_per_record: list[dict] = []
    non_canonical_types_seen: Counter = Counter()

    multi_mention_total = 0
    multi_mention_complete = 0
    b6_violations_per_record: list[dict] = []

    for record in records:
        rid = record.get("record_id", "unknown")
        ents = record.get("entities", [])

        # B2: zero-entity check
        if len(ents) == 0:
            n_zero_entity += 1

        # B1: offset accuracy
        n_e, n_a, b1_fails = check_offset_accuracy(record)
        total_entities += n_e
        total_aligned += n_a
        if b1_fails:
            b1_failures_per_record.append({"record_id": rid, "failures": b1_fails})

        # B4: triple-name
        n_fn, n_compl, b4_viols = check_triple_name_rule(record)
        n_full_names += n_fn
        n_triple_name_compliant += n_compl
        if b4_viols:
            b4_violations_per_record.append({"record_id": rid, "violations": b4_viols})

        # B5: canonical types
        n_e5, n_canon, non_canon = check_canonical_types(record)
        n_canonical_entities += n_canon
        for nc in non_canon:
            non_canonical_types_seen[nc] += 1
        if non_canon:
            b5_violations_per_record.append({"record_id": rid, "non_canonical": non_canon})

        # B6: multi-mention completeness
        n_uniq, n_compl, b6_missing = check_multi_mention_completeness(record)
        multi_mention_total += n_uniq
        multi_mention_complete += n_compl
        if b6_missing:
            b6_violations_per_record.append({"record_id": rid, "missing": b6_missing})

    # A2: per-entity floor (corpus-level)
    per_type_counts = compute_per_entity_floor(records)
    types_below_floor = {
        t: c for t, c in per_type_counts.items() if c < args.floor_target
    }
    types_at_or_above = {
        t: c for t, c in per_type_counts.items() if c >= args.floor_target
    }
    min_type_count = min(per_type_counts.values())
    floor_pass = min_type_count >= args.floor_target

    # Compose report
    report = {
        "summary": {
            "n_records": n_records,
            "n_total_entities": total_entities,
            "mean_entities_per_record": total_entities / n_records,
        },
        "B1_offset_accuracy": {
            "n_total": total_entities,
            "n_aligned": total_aligned,
            "accuracy": total_aligned / total_entities if total_entities else 0.0,
            "target": 1.0,
            "pass": (total_aligned == total_entities) if total_entities else False,
            "n_records_with_failures": len(b1_failures_per_record),
            "failures": b1_failures_per_record[:50],  # cap for report readability
        },
        "B2_zero_entity_rate": {
            "n_zero_entity_records": n_zero_entity,
            "rate": n_zero_entity / n_records,
            "target_max": 0.005,
            "pass": (n_zero_entity / n_records) <= 0.005,
        },
        "B3_validation_dropped_rate": {
            "status": "not_computable",
            "reason": "schema does not include 'dropped'/'extracted' fields per record",
        },
        "B4_triple_name_rule": {
            "n_full_names": n_full_names,
            "n_compliant": n_triple_name_compliant,
            "compliance": (
                n_triple_name_compliant / n_full_names if n_full_names else 1.0
            ),
            "target": 1.0,
            "pass": (n_triple_name_compliant == n_full_names) if n_full_names else True,
            "n_records_with_violations": len(b4_violations_per_record),
            "violations": b4_violations_per_record[:50],
            "_note": (
                "Baseline implementation assumes Western 'First Last' decomposition. "
                "Methodology R11 documents 8 decomposition cases (CJK, patronymic, double-"
                "surname, etc.) requiring per-language extension. Review violations to "
                "distinguish real failures from decomposition-rule gaps."
            ),
        },
        "B5_canonical_type_compliance": {
            "n_total_entities": total_entities,
            "n_canonical": n_canonical_entities,
            "compliance": (
                n_canonical_entities / total_entities if total_entities else 1.0
            ),
            "target": 1.0,
            "pass": n_canonical_entities == total_entities,
            "non_canonical_types_seen": dict(non_canonical_types_seen.most_common(20)),
            "n_records_with_non_canonical": len(b5_violations_per_record),
        },
        "B6_multi_mention_completeness": {
            "n_unique_string_per_record": multi_mention_total,
            "n_complete": multi_mention_complete,
            "completeness": (
                multi_mention_complete / multi_mention_total
                if multi_mention_total else 1.0
            ),
            "target": 0.95,
            "pass": (
                (multi_mention_complete / multi_mention_total) >= 0.95
                if multi_mention_total else True
            ),
            "n_records_with_missing": len(b6_violations_per_record),
            "examples": b6_violations_per_record[:20],
        },
        "A2_per_entity_floor": {
            "target_floor": args.floor_target,
            "min_type_count": min_type_count,
            "pass": floor_pass,
            "n_types_below_floor": len(types_below_floor),
            "n_types_at_or_above_floor": len(types_at_or_above),
            "types_below_floor": dict(sorted(types_below_floor.items(),
                                              key=lambda x: x[1])),
            "all_type_counts": dict(sorted(per_type_counts.items(),
                                             key=lambda x: -x[1])),
        },
    }

    # Critical gate decision
    critical_gates = {
        "B1_offset_accuracy": report["B1_offset_accuracy"]["pass"],
        "B2_zero_entity_rate": report["B2_zero_entity_rate"]["pass"],
        "B4_triple_name_rule": report["B4_triple_name_rule"]["pass"],
        "B5_canonical_type_compliance": report["B5_canonical_type_compliance"]["pass"],
        "B6_multi_mention_completeness": report["B6_multi_mention_completeness"]["pass"],
        "A2_per_entity_floor": report["A2_per_entity_floor"]["pass"],
    }
    report["critical_gates_pass"] = all(critical_gates.values())
    report["critical_gates_breakdown"] = critical_gates

    # Write report
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Stdout summary
    print("=" * 70)
    print("CRITICAL GATES + PER-ENTITY FLOOR — SUMMARY")
    print("=" * 70)
    print(f"Records:                     {n_records:>10,}")
    print(f"Total entities:              {total_entities:>10,}")
    print(f"Mean entities/record:        {total_entities/n_records:>10.1f}")
    print()
    print(f"{'Metric':<35}{'Result':>15}{'Pass':>10}")
    print("-" * 70)

    def fmt_pct(x):
        return f"{x*100:>13.2f}%"

    print(f"{'B1 Offset accuracy':<35}{fmt_pct(report['B1_offset_accuracy']['accuracy'])}"
          f"{'✓' if critical_gates['B1_offset_accuracy'] else '✗':>10}")
    print(f"{'B2 Zero-entity rate':<35}{fmt_pct(report['B2_zero_entity_rate']['rate'])}"
          f"{'✓' if critical_gates['B2_zero_entity_rate'] else '✗':>10}")
    print(f"{'B4 Triple-name compliance':<35}{fmt_pct(report['B4_triple_name_rule']['compliance'])}"
          f"{'✓' if critical_gates['B4_triple_name_rule'] else '✗':>10}")
    print(f"{'B5 Canonical-type compliance':<35}{fmt_pct(report['B5_canonical_type_compliance']['compliance'])}"
          f"{'✓' if critical_gates['B5_canonical_type_compliance'] else '✗':>10}")
    print(f"{'B6 Multi-mention completeness':<35}{fmt_pct(report['B6_multi_mention_completeness']['completeness'])}"
          f"{'✓' if critical_gates['B6_multi_mention_completeness'] else '✗':>10}")
    print(f"{'A2 Per-entity floor (min)':<35}{report['A2_per_entity_floor']['min_type_count']:>14}"
          f"{'✓' if critical_gates['A2_per_entity_floor'] else '✗':>10}")
    print("-" * 70)
    print(f"{'OVERALL CRITICAL GATES':<35}{'PASS' if report['critical_gates_pass'] else 'FAIL':>15}")
    print()

    if types_below_floor:
        print(f"Types below floor ({args.floor_target}): {len(types_below_floor)} types")
        for t, c in sorted(types_below_floor.items(), key=lambda x: x[1])[:15]:
            print(f"  {t:<40} {c:>6}")
        if len(types_below_floor) > 15:
            print(f"  ... and {len(types_below_floor) - 15} more")
        print()

    print(f"Detailed report: {args.out}")

    return 0 if report["critical_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
