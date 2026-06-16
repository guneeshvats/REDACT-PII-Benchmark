"""
Corpus statistics — Table 1 generator.

Produces the descriptive statistics that go into Section 5.1 of the paper:
- Total records, total entity instances, mean entities/record
- Per-entity-type counts (51 rows)
- Per-language counts (25 rows)
- Per-axis distributions (9 axes)
- Sensitivity tier breakdown (HIGH / MEDIUM / LOW)
- Behavioral frame distribution (7 frames)
- Disclosure form distribution
- Adjacency × CO-### distribution
- Direct vs indirect identifier breakdown (if present in records)
- GDPR Article 9 entity counts

Usage:
    python compute_corpus_stats.py corpus.json --out corpus_stats.json
"""

import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path

ARTICLE_9_ENTITIES = {
    "Religion", "Sex_Orientation", "Political_Party",
    "Trade_Union_Membership", "Medical_Information",
    "Allergy_Information",
    # Crime is Article 10 (also strict)
    "Crime",
}


def compute_stats(records: list[dict]) -> dict:
    n_records = len(records)
    total_entities = 0
    per_entity = Counter()
    per_lang = Counter()
    per_domain = Counter()
    per_format = Counter()
    per_difficulty = Counter()
    per_density = Counter()
    per_length = Counter()
    per_code_switch = Counter()
    per_adjacency = Counter()
    per_co_pattern = Counter()
    per_behavioral_frame = Counter()
    per_sensitivity = Counter()
    per_disclosure_form = Counter()
    per_disclosed = Counter()
    per_direct_indirect = Counter()
    article_9_count_records = 0
    article_9_count_entities = 0
    entities_per_record_dist = []

    for r in records:
        axes = r.get("axes", {})
        per_lang[axes.get("language", "?")] += 1
        per_domain[axes.get("domain", "?")] += 1
        per_format[axes.get("format", "?")] += 1
        per_difficulty[axes.get("difficulty", "?")] += 1
        per_density[axes.get("density", "?")] += 1
        per_length[axes.get("length", "?")] += 1
        per_code_switch[axes.get("code_switching", "?")] += 1
        per_adjacency[axes.get("adjacency", "?")] += 1
        per_co_pattern[axes.get("co_occurrence_pattern", "?")] += 1
        per_behavioral_frame[r.get("behavioral_frame", "?")] += 1

        ents = r.get("entities", [])
        n_ents = len(ents)
        total_entities += n_ents
        entities_per_record_dist.append(n_ents)

        has_article_9 = False
        for e in ents:
            et = e.get("entity_type", "?")
            per_entity[et] += 1
            per_sensitivity[e.get("sensitivity_tier", "?")] += 1
            per_disclosure_form[e.get("disclosure_form", "?")] += 1
            per_disclosed["disclosed=true" if e.get("disclosed") else "disclosed=false"] += 1
            if et in ARTICLE_9_ENTITIES:
                article_9_count_entities += 1
                has_article_9 = True

        # Direct/indirect classification (optional field, present in some records)
        for dic in r.get("direct_indirect_classification", []):
            per_direct_indirect[dic.get("identifier_class", "?")] += 1

        if has_article_9:
            article_9_count_records += 1

    # Distributional summaries on entities-per-record
    if entities_per_record_dist:
        sorted_dist = sorted(entities_per_record_dist)
        mid = len(sorted_dist) // 2
        median = sorted_dist[mid]
        mean = total_entities / n_records
        mn, mx = sorted_dist[0], sorted_dist[-1]
    else:
        median = mean = mn = mx = 0

    stats = {
        "overall": {
            "n_records": n_records,
            "n_total_entities": total_entities,
            "mean_entities_per_record": round(mean, 2),
            "median_entities_per_record": median,
            "min_entities_per_record": mn,
            "max_entities_per_record": mx,
        },
        "per_entity_type": dict(per_entity.most_common()),
        "per_language": dict(per_lang.most_common()),
        "per_domain": dict(per_domain.most_common()),
        "per_format": dict(per_format.most_common()),
        "per_difficulty": dict(per_difficulty.most_common()),
        "per_density": dict(per_density.most_common()),
        "per_length": dict(per_length.most_common()),
        "per_code_switching": dict(per_code_switch.most_common()),
        "per_adjacency": dict(per_adjacency.most_common()),
        "per_co_occurrence_pattern": dict(per_co_pattern.most_common()),
        "per_behavioral_frame": dict(per_behavioral_frame.most_common()),
        "per_sensitivity_tier": dict(per_sensitivity.most_common()),
        "per_disclosure_form": dict(per_disclosure_form.most_common()),
        "per_disclosed": dict(per_disclosed.most_common()),
        "per_direct_indirect": dict(per_direct_indirect.most_common()),
        "article_9_summary": {
            "article_9_entity_count": article_9_count_entities,
            "article_9_records_count": article_9_count_records,
            "article_9_record_share": round(article_9_count_records / n_records, 3) if n_records else 0,
        },
    }
    return stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--out", default="corpus_stats.json")
    args = p.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)
    stats = compute_stats(records)
    with open(args.out, "w") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # Stdout summary
    o = stats["overall"]
    print(f"Records:              {o['n_records']:,}")
    print(f"Total entities:       {o['n_total_entities']:,}")
    print(f"Mean entities/record: {o['mean_entities_per_record']}")
    print(f"Languages:            {len(stats['per_language'])}")
    print(f"Entity types:         {len(stats['per_entity_type'])}")
    print(f"Article 9 records:    {stats['article_9_summary']['article_9_records_count']:,} "
          f"({stats['article_9_summary']['article_9_record_share']:.1%})")
    print(f"\nReport written to: {args.out}")


if __name__ == "__main__":
    main()
