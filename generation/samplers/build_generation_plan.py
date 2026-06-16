"""Covering-array sampler — Algorithm 1 from methodology §4.4.

Generates a 5,510-record generation plan that:
  (a) is strength-2 pairwise complete over the 9 diversity axes
  (b) guarantees every entity_type has at least N=50 records as target
  (c) covers every CO-### co-occurrence pattern at least once
  (d) stratifies behavioral_frame values across the 7-frame matrix

Output: generation_plan.jsonl — one config per line, consumed by the
generator (Stage 2) which fills in the user prompt template.

Usage:
  uv run --with allpairspy python tasks/pii_generation/build_generation_plan.py
"""

import json
import random
from collections import defaultdict, Counter
from pathlib import Path

try:
    from allpairspy import AllPairs
except ImportError:
    raise SystemExit(
        "allpairspy not installed. Run via:\n"
        "  uv run --with allpairspy python tasks/pii_generation/build_generation_plan.py"
    )

HERE = Path(__file__).parent
PATTERNS_JSON = HERE / "pattern_seed_data_v4.json"
PLAN_JSONL = HERE / "generation_plan.jsonl"
REPORT_JSON = HERE / "generation_plan_report.json"

# ── Configuration ────────────────────────────────────────────────────────────
TARGET_CORPUS_SIZE = 5510
PER_ENTITY_FLOOR = 50
RNG_SEED = 42

# ── The 9 diversity axes (methodology §4.1) ──────────────────────────────────
AXES = {
    "domain": [
        "healthcare", "legal", "finance", "education", "government",
        "technology", "HR", "insurance", "customer_service",
        "law_enforcement", "social_media", "e_commerce",
    ],
    "format": [
        "plain_text", "email", "chat_transcript", "ticket_worknotes",
        "json_record", "key_value_pairs", "log_entry",
    ],
    "difficulty": ["easy", "medium", "hard"],
    "length": ["small", "medium", "large", "very_large"],
    "density": ["low", "medium", "high"],
    "code_switching": ["none", "light", "heavy"],
    "language": [
        # P1 (6)
        "EN", "FR", "DE", "IT", "ES", "PT_BR",
        # P2 (3)
        "FR_CA", "JA", "NL",
        # P3 (16)
        "SV", "FI", "CS", "HE", "HU", "KO", "NO", "PT_EU",
        "RU", "ZH_CN", "ZH_TW", "TH", "TR", "AR", "DA", "HI",
    ],
    "adjacency": ["none", "loose", "tight"],
    # co_occurrence_pattern is conditional on adjacency=tight — handled separately
}

# Co-occurrence patterns when adjacency=tight (15 named clusters)
CO_PATTERNS = [f"CO-{i:03d}" for i in range(1, 16)]

# Canonical 51 entity types (v4)
ENTITY_TYPES = [
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    "Business_Title",
    "Address_Work", "Address_Personal",
    "Telephone_Numbers_Work", "Telephone_Numbers_Personal",
    "Work_Email_Address", "Personal_Email_Address",
    "Date_of_Birth", "Age", "Place_of_Birth", "Gender", "Marital_Status",
    "Nationality", "Citizenship_Status", "Sex_Orientation", "Religion",
    "Political_Party",
    "Country_of_Residence", "State", "City", "Location", "Geolocation_Data",
    "National_Identification_Number", "Passport_Number",
    "Driving_License_Number", "Tax_Reference_Number",
    "Compensation_and_Salary", "Credit_Card_Numbers",
    "Customer_Reference_Number", "Account_Statements",
    "Employee_ID_Number", "Building_Badge_Card_Number",
    "Performance_Assessment", "Disciplinary_Action", "Sickness_Day_Records",
    "Professional_Background",
    "Crime", "PEP_Status", "Trade_Union_Membership",
    "Allergy_Information", "Medical_Information",
    "Social_Media_Identifiers", "Static_IP_Address", "Password",
    "Date_Time", "Emergency_Contact_Details", "Org_Name",
]

# Behavioral frame distribution (gap A5 + B3 coverage)
BEHAVIORAL_FRAMES = [
    ("isolation", 0.40),
    ("co_occurrence", 0.15),  # forced when adjacency=tight
    ("hypothetical", 0.10),
    ("negation", 0.10),
    ("partial", 0.10),
    ("instructional", 0.08),
    ("cross_sentence", 0.07),
]

# Scenario seed templates by (domain, format) — minimal v1; expand later
SCENARIO_TEMPLATES = {
    ("healthcare", "plain_text"): "Clinical note about a patient's recent visit.",
    ("healthcare", "email"): "Email between two clinicians coordinating patient care.",
    ("healthcare", "chat_transcript"): "Chat between clinician and on-call nurse about a patient.",
    ("healthcare", "ticket_worknotes"): "Hospital IT ticket related to patient data access.",
    ("healthcare", "json_record"): "EHR system patient export.",
    ("healthcare", "key_value_pairs"): "Patient intake form fields.",
    ("healthcare", "log_entry"): "Hospital system audit log entry.",
    ("legal", "plain_text"): "A legal pleading or court document excerpt.",
    ("legal", "email"): "Email between counsel and client regarding a case.",
    ("legal", "chat_transcript"): "Internal legal-team chat about a case.",
    ("legal", "ticket_worknotes"): "Compliance ticket regarding a regulatory matter.",
    ("legal", "json_record"): "Case-management system record export.",
    ("legal", "key_value_pairs"): "Court filing intake form.",
    ("legal", "log_entry"): "Document-management system access log.",
    ("finance", "plain_text"): "Bank statement or financial advisory note.",
    ("finance", "email"): "Customer email regarding an account or transaction.",
    ("finance", "chat_transcript"): "Customer support chat about a bank account.",
    ("finance", "ticket_worknotes"): "Finance compliance investigation ticket.",
    ("finance", "json_record"): "KYC/AML system export.",
    ("finance", "key_value_pairs"): "Loan or account-opening form.",
    ("finance", "log_entry"): "Transaction-processing system log entry.",
    ("education", "plain_text"): "Academic record narrative or transcript note.",
    ("education", "email"): "Email between a student and registrar.",
    ("education", "chat_transcript"): "Student-advisor chat session.",
    ("education", "ticket_worknotes"): "Registrar support ticket.",
    ("education", "json_record"): "Student information system record.",
    ("education", "key_value_pairs"): "Course-registration form.",
    ("education", "log_entry"): "LMS access log entry.",
    ("government", "plain_text"): "Government memo or policy document excerpt.",
    ("government", "email"): "Citizen-government correspondence.",
    ("government", "chat_transcript"): "Internal agency chat about a case file.",
    ("government", "ticket_worknotes"): "Government IT system support ticket.",
    ("government", "json_record"): "Government registry record.",
    ("government", "key_value_pairs"): "Government application form.",
    ("government", "log_entry"): "Border-control or registry log entry.",
    ("technology", "plain_text"): "Internal product spec or design doc excerpt.",
    ("technology", "email"): "Engineering team correspondence.",
    ("technology", "chat_transcript"): "Slack/Teams chat between engineers.",
    ("technology", "ticket_worknotes"): "JIRA / Anonymous Institution incident ticket.",
    ("technology", "json_record"): "User profile or analytics record.",
    ("technology", "key_value_pairs"): "Onboarding form for an internal tool.",
    ("technology", "log_entry"): "Application or auth-service log entry.",
    ("HR", "plain_text"): "HR memo or employee performance review.",
    ("HR", "email"): "Email between HR and an employee.",
    ("HR", "chat_transcript"): "Manager-employee one-on-one chat.",
    ("HR", "ticket_worknotes"): "HR support ticket.",
    ("HR", "json_record"): "HRIS employee record export.",
    ("HR", "key_value_pairs"): "Onboarding or benefits-enrollment form.",
    ("HR", "log_entry"): "Time-and-attendance system log.",
    ("insurance", "plain_text"): "Insurance claim narrative.",
    ("insurance", "email"): "Email between a claimant and adjuster.",
    ("insurance", "chat_transcript"): "Insurance support chat.",
    ("insurance", "ticket_worknotes"): "Claims-processing ticket.",
    ("insurance", "json_record"): "Policy record export.",
    ("insurance", "key_value_pairs"): "Insurance application form.",
    ("insurance", "log_entry"): "Claims-system audit log.",
    ("customer_service", "plain_text"): "Customer service interaction summary.",
    ("customer_service", "email"): "Customer-support email thread.",
    ("customer_service", "chat_transcript"): "Live-chat support transcript.",
    ("customer_service", "ticket_worknotes"): "Support ticket worknotes.",
    ("customer_service", "json_record"): "CRM customer record.",
    ("customer_service", "key_value_pairs"): "Support intake form.",
    ("customer_service", "log_entry"): "Help-desk system log entry.",
    ("law_enforcement", "plain_text"): "Police report or investigative narrative.",
    ("law_enforcement", "email"): "Investigative correspondence.",
    ("law_enforcement", "chat_transcript"): "Internal investigator chat.",
    ("law_enforcement", "ticket_worknotes"): "Case-management ticket.",
    ("law_enforcement", "json_record"): "Records-management system export.",
    ("law_enforcement", "key_value_pairs"): "Booking or intake form.",
    ("law_enforcement", "log_entry"): "Records-access audit log.",
    ("social_media", "plain_text"): "User-generated post or comment.",
    ("social_media", "email"): "Platform notification email.",
    ("social_media", "chat_transcript"): "DM exchange between users.",
    ("social_media", "ticket_worknotes"): "Content-moderation ticket.",
    ("social_media", "json_record"): "Post or user-profile API response.",
    ("social_media", "key_value_pairs"): "Account-creation form.",
    ("social_media", "log_entry"): "Platform audit log entry.",
    ("e_commerce", "plain_text"): "Order confirmation or product review.",
    ("e_commerce", "email"): "Shipping or order-status email.",
    ("e_commerce", "chat_transcript"): "Customer-support live chat.",
    ("e_commerce", "ticket_worknotes"): "Order-issue ticket.",
    ("e_commerce", "json_record"): "Order or customer record.",
    ("e_commerce", "key_value_pairs"): "Checkout or shipping-address form.",
    ("e_commerce", "log_entry"): "Order-processing log entry.",
}


def make_scenario_seed(axes: dict, target_entity: str) -> str:
    """Pick a scenario template; append entity-type-specific hint."""
    key = (axes["domain"], axes["format"])
    base = SCENARIO_TEMPLATES.get(key, f"A {axes['format'].replace('_', ' ')} in the {axes['domain']} domain.")
    return f"{base} (target entity: {target_entity})"


def pick_target_pattern(axes: dict, pattern_data: dict, entity_type: str, rng: random.Random):
    """Select a v4 pattern that matches the axis constraints.

    Filtering priority:
      1. entity_type match (required)
      2. language match if language-specific patterns exist for this entity
      3. adjacency-tight if axes['adjacency'] == 'tight'
    Fall back through filters if no candidates remain.
    """
    flat = pattern_data["patterns_flat"]
    candidates = [p for p in flat if p["entity_type"] == entity_type]
    if not candidates:
        return None

    # Filter by language if any language-specific patterns exist
    if axes["language"] != "EN":
        lang_match = [p for p in candidates if p["language_hint"] == axes["language"]]
        if lang_match:
            candidates = lang_match

    # Prefer adjacency-tight patterns if axis says tight
    if axes["adjacency"] == "tight":
        tight_match = [p for p in candidates if "Adjacency-tight" in p["dimensions"]]
        if tight_match:
            candidates = tight_match

    # Prefer masked/partial patterns if behavioral_frame is "partial" — but
    # we don't know behavioral_frame yet at this point; skip.

    return rng.choice(candidates)


def pick_behavioral_frame(axes: dict, rng: random.Random) -> str:
    """Behavioral frame selection.

    - If adjacency=tight, force co_occurrence (the CO-### pattern IS the frame)
    - Otherwise, sample by weight
    """
    if axes["adjacency"] == "tight":
        return "co_occurrence"
    frames, weights = zip(*[(f, w) for f, w in BEHAVIORAL_FRAMES if f != "co_occurrence"])
    # Re-normalize weights since co_occurrence removed
    total = sum(weights)
    weights = [w / total for w in weights]
    return rng.choices(frames, weights=weights, k=1)[0]


def pick_co_pattern(axes: dict, rng: random.Random) -> str:
    """If adjacency=tight, pick a CO-### pattern; else 'none'."""
    if axes["adjacency"] != "tight":
        return "none"
    return rng.choice(CO_PATTERNS)


def enrich_row(axes: dict, target_entity: str, pattern_data: dict,
               rng: random.Random, source: str) -> dict:
    """Take an axes dict + target entity, attach pattern + frame + scenario."""
    axes = dict(axes)  # don't mutate
    axes["co_occurrence_pattern"] = pick_co_pattern(axes, rng)
    pattern = pick_target_pattern(axes, pattern_data, target_entity, rng)
    frame = pick_behavioral_frame(axes, rng)
    return {
        "mode": "coverage",
        "source": source,  # "covering_array" | "floor_supplement" | "diversity_fill"
        "axes": axes,
        "target_entity_type": target_entity,
        "target_pattern_id": pattern["pattern_id"] if pattern else None,
        "target_pattern_desc": pattern["description"] if pattern else None,
        "target_pattern_example": (
            pattern["examples"][0] if pattern and pattern.get("examples") else None
        ),
        "behavioral_frame": frame,
        "scenario_seed": make_scenario_seed(axes, target_entity),
    }


def main():
    rng = random.Random(RNG_SEED)
    pattern_data = json.loads(PATTERNS_JSON.read_text())
    print(f"Loaded {len(pattern_data['patterns_flat'])} v4 patterns")

    # ── Step 1: Build strength-2 covering array over 8 axes ─────────────────
    parameters = list(AXES.values())
    axis_keys = list(AXES.keys())
    print(f"\n=== Step 1: Strength-2 covering array ===")
    print(f"  Axes: {axis_keys}")
    print(f"  Value counts: {[len(v) for v in parameters]}")
    print(f"  Full factorial size: {1}", end="")
    fact = 1
    for v in parameters:
        fact *= len(v)
    print(f" → actual: {fact:,}")
    print(f"  Computing strength-2 covering array...")
    pairs = list(AllPairs(parameters))
    mandatory_rows = [
        {axis_keys[i]: row[i] for i in range(len(axis_keys))}
        for row in pairs
    ]
    print(f"  Covering array size: {len(mandatory_rows)} configs (vs full factorial {fact:,})")

    # ── Step 2: Enrich mandatory rows with target entity + pattern + frame ──
    print(f"\n=== Step 2: Enriching mandatory rows ===")
    plan_rows = []
    entity_counts: Counter = Counter()
    co_pattern_counts: Counter = Counter()
    for axes in mandatory_rows:
        target_entity = rng.choice(ENTITY_TYPES)
        row = enrich_row(axes, target_entity, pattern_data, rng, source="covering_array")
        plan_rows.append(row)
        entity_counts[target_entity] += 1
        co = row["axes"]["co_occurrence_pattern"]
        if co != "none":
            co_pattern_counts[co] += 1

    # ── Step 3: CO-### coverage supplement ──────────────────────────────────
    # Ensure every CO-001..CO-015 has at least 3 records
    print(f"\n=== Step 3: CO-### supplement ===")
    co_supplement = []
    for co in CO_PATTERNS:
        deficit = 3 - co_pattern_counts.get(co, 0)
        for _ in range(max(0, deficit)):
            axes = {k: rng.choice(v) for k, v in AXES.items()}
            axes["adjacency"] = "tight"  # force tight so CO-### is meaningful
            axes["co_occurrence_pattern"] = co
            target_entity = rng.choice(ENTITY_TYPES)
            row = enrich_row(axes, target_entity, pattern_data, rng, source="co_supplement")
            row["axes"]["co_occurrence_pattern"] = co  # override to enforce the CO
            co_supplement.append(row)
            entity_counts[target_entity] += 1
    print(f"  CO-### supplement: {len(co_supplement)} records ensuring 3 records per CO-001..CO-015")

    # ── Step 4: Per-entity floor (N≥50 for every entity type) ────────────────
    print(f"\n=== Step 4: Per-entity floor (N≥{PER_ENTITY_FLOOR}) ===")
    floor_supplement = []
    for entity in ENTITY_TYPES:
        deficit = PER_ENTITY_FLOOR - entity_counts.get(entity, 0)
        if deficit > 0:
            for _ in range(deficit):
                axes = {k: rng.choice(v) for k, v in AXES.items()}
                row = enrich_row(axes, entity, pattern_data, rng, source="floor_supplement")
                floor_supplement.append(row)
                entity_counts[entity] += 1
    print(f"  Floor supplement: {len(floor_supplement)} records")

    # ── Step 5: Diversity fill to reach TARGET_CORPUS_SIZE ──────────────────
    current_total = len(plan_rows) + len(co_supplement) + len(floor_supplement)
    diversity_count = max(0, TARGET_CORPUS_SIZE - current_total)
    print(f"\n=== Step 5: Diversity fill ===")
    print(f"  Current: {current_total}; target: {TARGET_CORPUS_SIZE}; fill: {diversity_count}")
    diversity_supplement = []
    for _ in range(diversity_count):
        axes = {k: rng.choice(v) for k, v in AXES.items()}
        target_entity = rng.choice(ENTITY_TYPES)
        row = enrich_row(axes, target_entity, pattern_data, rng, source="diversity_fill")
        diversity_supplement.append(row)
        entity_counts[target_entity] += 1

    # ── Step 6: Combine, shuffle, assign final record_ids ───────────────────
    final_plan = plan_rows + co_supplement + floor_supplement + diversity_supplement
    rng.shuffle(final_plan)
    for i, row in enumerate(final_plan, start=1):
        row["record_id"] = i

    # ── Step 7: Write JSONL + report ────────────────────────────────────────
    with PLAN_JSONL.open("w") as f:
        for row in final_plan:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nWrote {PLAN_JSONL} ({PLAN_JSONL.stat().st_size / 1024:.0f} KB)")

    # Build verification report
    source_counts = Counter(r["source"] for r in final_plan)
    final_entity_counts = Counter(r["target_entity_type"] for r in final_plan)
    final_co_counts = Counter(r["axes"]["co_occurrence_pattern"] for r in final_plan)
    frame_counts = Counter(r["behavioral_frame"] for r in final_plan)
    lang_counts = Counter(r["axes"]["language"] for r in final_plan)
    domain_counts = Counter(r["axes"]["domain"] for r in final_plan)
    format_counts = Counter(r["axes"]["format"] for r in final_plan)
    adj_counts = Counter(r["axes"]["adjacency"] for r in final_plan)

    # Verify pairwise coverage on a sample of axis pairs
    def verify_pair_coverage(rows, axis_a, axis_b, values_a, values_b):
        seen = set()
        for r in rows:
            seen.add((r["axes"][axis_a], r["axes"][axis_b]))
        expected = set((a, b) for a in values_a for b in values_b)
        return len(seen & expected), len(expected)

    pairs_to_check = [
        ("language", "domain"),
        ("language", "format"),
        ("language", "adjacency"),
        ("domain", "format"),
        ("difficulty", "density"),
        ("length", "density"),
    ]
    pair_coverage = {}
    for a, b in pairs_to_check:
        seen, total = verify_pair_coverage(final_plan, a, b, AXES[a], AXES[b])
        pair_coverage[f"{a} × {b}"] = {"observed": seen, "expected": total,
                                         "pct": round(100 * seen / total, 1)}

    report = {
        "total_records": len(final_plan),
        "source_breakdown": dict(source_counts),
        "per_entity_floor_target": PER_ENTITY_FLOOR,
        "entities_below_floor": [e for e in ENTITY_TYPES if final_entity_counts[e] < PER_ENTITY_FLOOR],
        "entity_count_min": min(final_entity_counts.values()),
        "entity_count_max": max(final_entity_counts.values()),
        "entity_count_mean": round(sum(final_entity_counts.values()) / len(final_entity_counts), 1),
        "co_pattern_min": min(final_co_counts.get(co, 0) for co in CO_PATTERNS),
        "co_pattern_max": max(final_co_counts.get(co, 0) for co in CO_PATTERNS),
        "behavioral_frame_distribution": dict(frame_counts),
        "language_distribution": dict(lang_counts),
        "domain_distribution": dict(domain_counts),
        "format_distribution": dict(format_counts),
        "adjacency_distribution": dict(adj_counts),
        "pairwise_coverage_spot_checks": pair_coverage,
        "patterns_attached": sum(1 for r in final_plan if r["target_pattern_id"]),
        "patterns_missing": sum(1 for r in final_plan if r["target_pattern_id"] is None),
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Wrote {REPORT_JSON}")

    # ── Print summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("GENERATION PLAN SUMMARY")
    print("=" * 70)
    print(f"Total records:        {len(final_plan)}")
    print(f"  covering_array:     {source_counts['covering_array']}")
    print(f"  co_supplement:      {source_counts.get('co_supplement', 0)}")
    print(f"  floor_supplement:   {source_counts.get('floor_supplement', 0)}")
    print(f"  diversity_fill:     {source_counts.get('diversity_fill', 0)}")
    print()
    print(f"Per-entity floor (≥{PER_ENTITY_FLOOR}):")
    print(f"  min count: {report['entity_count_min']}")
    print(f"  max count: {report['entity_count_max']}")
    print(f"  mean:      {report['entity_count_mean']}")
    if report["entities_below_floor"]:
        print(f"  ⚠ below floor: {report['entities_below_floor']}")
    else:
        print(f"  ✓ ALL 51 entities ≥{PER_ENTITY_FLOOR}")
    print()
    print(f"CO-### coverage:")
    print(f"  min: {report['co_pattern_min']}")
    print(f"  max: {report['co_pattern_max']}")
    print(f"  ✓ all CO-001..CO-015 covered" if report['co_pattern_min'] >= 1 else f"  ⚠ some CO-### missing")
    print()
    print(f"Behavioral frames:")
    for frame, pct in BEHAVIORAL_FRAMES:
        c = frame_counts.get(frame, 0)
        print(f"  {frame:<18} {c:>5} ({100 * c / len(final_plan):.1f}%, target {100*pct:.0f}%)")
    print()
    print(f"Pairwise coverage spot-checks (target: 100%):")
    for pair_name, cov in pair_coverage.items():
        flag = "✓" if cov["pct"] >= 99 else "⚠"
        print(f"  {flag} {pair_name:<28} {cov['observed']:>4} / {cov['expected']:<4}  ({cov['pct']:.1f}%)")
    print()
    print(f"Pattern attachment:")
    print(f"  ✓ patterns_attached: {report['patterns_attached']}")
    print(f"  patterns_missing:    {report['patterns_missing']}")


if __name__ == "__main__":
    main()
