"""
Family A — Coverage metrics.

Per methodology §6.1:
  A1  Pattern coverage rate: fraction of catalog patterns exercised at least once
  A2  Per-entity-type floor: every entity has >=50 records
  A3  Language-tier coverage: P1/P2/P3 languages all represented
  A4  Pairwise axis coverage: every pair of axis values covered by at least
       one record
  A5  Behavioral matrix coverage: every (entity_type, behavioral_frame) cell has
       at least one record (where applicable)

Usage:
    python compute_coverage.py corpus.json --out coverage_report.json
"""

import json
import argparse
from collections import Counter, defaultdict
from itertools import combinations

# Language tiers per methodology §3.3
P1_LANGUAGES = {"EN", "FR", "DE", "IT", "ES", "PT_BR"}
P2_LANGUAGES = {"FR_CA", "JA", "NL"}
P3_LANGUAGES = {"SV", "FI", "CS", "HE", "HU", "KO", "NO", "PT_EU",
                "RU", "ZH_CN", "ZH_TW", "TH", "TR", "AR", "DA", "HI"}

ALL_LANGUAGES = P1_LANGUAGES | P2_LANGUAGES | P3_LANGUAGES

AXIS_NAMES = [
    "domain", "format", "difficulty", "length", "density",
    "code_switching", "language", "adjacency", "co_occurrence_pattern",
]


def compute_a1_pattern_coverage(records, pattern_catalog_size: int = 4127):
    """Fraction of patterns exercised."""
    seen = set()
    for r in records:
        pid = r.get("target_pattern_id")
        if pid:
            seen.add(pid)
    return {
        "patterns_exercised": len(seen),
        "catalog_size": pattern_catalog_size,
        "coverage_rate": round(len(seen) / pattern_catalog_size, 4),
        "pass": (len(seen) / pattern_catalog_size) >= 0.5,  # Soft target for v1
    }


def compute_a2_per_entity_floor(records, floor: int = 50):
    """Per-entity-type record count."""
    counts = Counter()
    for r in records:
        types_in_record = {e.get("entity_type", "") for e in r.get("entities", [])}
        for t in types_in_record:
            if t:
                counts[t] += 1

    below = {t: c for t, c in counts.items() if c < floor}
    return {
        "target_floor": floor,
        "min_type_count": min(counts.values()) if counts else 0,
        "max_type_count": max(counts.values()) if counts else 0,
        "n_types_below_floor": len(below),
        "n_types_at_or_above_floor": len(counts) - len(below),
        "pass": len(below) == 0,
        "types_below_floor": dict(sorted(below.items(), key=lambda x: x[1])),
        "all_counts": dict(sorted(counts.items(), key=lambda x: -x[1])),
    }


def compute_a3_language_coverage(records):
    """P1, P2, P3 language coverage."""
    lang_counts = Counter(r.get("axes", {}).get("language", "?") for r in records)
    p1_seen = set(lang_counts.keys()) & P1_LANGUAGES
    p2_seen = set(lang_counts.keys()) & P2_LANGUAGES
    p3_seen = set(lang_counts.keys()) & P3_LANGUAGES
    return {
        "p1_target": len(P1_LANGUAGES),
        "p1_seen": len(p1_seen),
        "p1_pass": len(p1_seen) == len(P1_LANGUAGES),
        "p1_missing": list(P1_LANGUAGES - p1_seen),
        "p2_target": len(P2_LANGUAGES),
        "p2_seen": len(p2_seen),
        "p2_pass": len(p2_seen) == len(P2_LANGUAGES),
        "p2_missing": list(P2_LANGUAGES - p2_seen),
        "p3_target": len(P3_LANGUAGES),
        "p3_seen": len(p3_seen),
        "p3_pass": len(p3_seen) == len(P3_LANGUAGES),
        "p3_missing": list(P3_LANGUAGES - p3_seen),
        "per_language_counts": dict(lang_counts.most_common()),
    }


def compute_a4_pairwise_axis_coverage(records):
    """Pairwise coverage of axis values."""
    # Build axis value sets
    axis_values = defaultdict(set)
    for r in records:
        axes = r.get("axes", {})
        for ax in AXIS_NAMES:
            v = axes.get(ax)
            if v is not None:
                axis_values[ax].add(v)

    # For each pair of axes, compute coverage
    pair_results = {}
    for ax1, ax2 in combinations(AXIS_NAMES, 2):
        expected = set()
        for v1 in axis_values[ax1]:
            for v2 in axis_values[ax2]:
                expected.add((v1, v2))
        seen = set()
        for r in records:
            axes = r.get("axes", {})
            v1, v2 = axes.get(ax1), axes.get(ax2)
            if v1 is not None and v2 is not None:
                seen.add((v1, v2))
        covered = len(seen & expected)
        total = len(expected)
        pair_results[f"{ax1}__{ax2}"] = {
            "expected": total,
            "seen": covered,
            "rate": round(covered / total, 4) if total else 1.0,
        }

    # Overall pass rate
    rates = [v["rate"] for v in pair_results.values()]
    mean_rate = sum(rates) / len(rates) if rates else 1.0

    return {
        "n_axis_pairs": len(pair_results),
        "mean_pairwise_coverage": round(mean_rate, 4),
        "target": ">=0.98 mean",
        "pass": mean_rate >= 0.98,
        "per_pair": pair_results,
    }


def compute_a5_behavioral_matrix(records):
    """(entity_type, behavioral_frame) coverage."""
    seen = defaultdict(set)
    for r in records:
        bf = r.get("behavioral_frame", "?")
        for e in r.get("entities", []):
            et = e.get("entity_type", "?")
            seen[et].add(bf)

    # Summary
    n_unique_combos = sum(len(s) for s in seen.values())
    n_entities = len(seen)
    return {
        "n_entity_types_covered": n_entities,
        "n_unique_entity_x_frame_combinations": n_unique_combos,
        "mean_frames_per_entity": round(n_unique_combos / n_entities, 2) if n_entities else 0,
        "per_entity_frame_count": {
            et: len(frames) for et, frames in sorted(seen.items())
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--out", default="coverage_report.json")
    p.add_argument("--floor", type=int, default=50)
    p.add_argument("--catalog-size", type=int, default=4127)
    args = p.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)

    print(f"Loaded {len(records):,} records")
    print("[A1] Pattern coverage...")
    a1 = compute_a1_pattern_coverage(records, args.catalog_size)
    print(f"     Patterns exercised: {a1['patterns_exercised']:,}/{a1['catalog_size']:,} "
          f"({a1['coverage_rate']:.1%})")

    print("[A2] Per-entity-type floor...")
    a2 = compute_a2_per_entity_floor(records, args.floor)
    print(f"     Min count: {a2['min_type_count']}, below floor: {a2['n_types_below_floor']}")

    print("[A3] Language tier coverage...")
    a3 = compute_a3_language_coverage(records)
    print(f"     P1: {a3['p1_seen']}/{a3['p1_target']}  "
          f"P2: {a3['p2_seen']}/{a3['p2_target']}  "
          f"P3: {a3['p3_seen']}/{a3['p3_target']}")

    print("[A4] Pairwise axis coverage...")
    a4 = compute_a4_pairwise_axis_coverage(records)
    print(f"     Mean pairwise coverage: {a4['mean_pairwise_coverage']:.1%}")

    print("[A5] Behavioral matrix coverage...")
    a5 = compute_a5_behavioral_matrix(records)
    print(f"     {a5['n_entity_types_covered']} entity types, "
          f"mean {a5['mean_frames_per_entity']} frames per entity")

    report = {
        "n_records": len(records),
        "A1_pattern_coverage": a1,
        "A2_per_entity_floor": a2,
        "A3_language_coverage": a3,
        "A4_pairwise_axis_coverage": a4,
        "A5_behavioral_matrix_coverage": a5,
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
