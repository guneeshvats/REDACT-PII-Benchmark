"""Paired-sweep sampler — Algorithm 2 from methodology §4.6.3.

Generates an 890-record paired-sweep subset that supports causal-comparison
claims (e.g., "holding content constant, F1 drops 18 points when format
changes from plain_text to json_record").

Design (§4.6.1):
  - 100 anchors authored per §4.6.2 stratification:
      30 stress-test  (very_large × high × hard combinations)
      30 Article 9    (Religion, Crime, Sex_Orientation, Medical_Information, PEP_Status)
      25 non-Latin    (CJK, Arabic, Devanagari, Hebrew, Thai)
      15 co_pattern   (one per CO-001..CO-015)
  - Sub-sweep allocation:
      50 anchors → format sweep   (× 7 formats  = 350 records)
      30 anchors → domain sweep   (× 12 domains = 360 records)
      20 anchors → diff×density   (× 9 combos   = 180 records)
  - Total: 890 records

Output: paired_sweep_plan.jsonl (and anchor library paired_sweep_anchors.json)

Usage:
  uv run python tasks/pii_generation/build_paired_sweep_plan.py
"""

import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
PATTERNS_JSON = HERE / "pattern_seed_data_v4.json"
ANCHORS_JSON = HERE / "paired_sweep_anchors.json"
PLAN_JSONL = HERE / "paired_sweep_plan.jsonl"
REPORT_JSON = HERE / "paired_sweep_plan_report.json"

RNG_SEED = 7  # different seed than the covering-array sampler

# ── Axis values (must match the covering-array sampler's AXES dict) ──────────
FORMATS = ["plain_text", "email", "chat_transcript", "ticket_worknotes",
           "json_record", "key_value_pairs", "log_entry"]
DOMAINS = ["healthcare", "legal", "finance", "education", "government",
           "technology", "HR", "insurance", "customer_service",
           "law_enforcement", "social_media", "e_commerce"]
DIFFICULTIES = ["easy", "medium", "hard"]
DENSITIES = ["low", "medium", "high"]

CO_PATTERNS = [f"CO-{i:03d}" for i in range(1, 16)]
NON_LATIN_LANGS = ["JA", "ZH_CN", "ZH_TW", "AR", "HE", "TH", "KO", "HI", "RU"]
ARTICLE_9_TYPES = ["Religion", "Sex_Orientation", "Crime", "Medical_Information",
                   "Trade_Union_Membership", "Political_Party", "PEP_Status",
                   "Allergy_Information"]

# ── Fictional-data pool ─────────────────────────────────────────────────────
# Each tuple = (Full_Name, First_Given_Name, Last_Family_Name, FN_pattern_id,
#               FGN_pattern_id, LFN_pattern_id, language)
NAME_POOL = [
    # Latin-script Western
    ("Sarah Chen",            "Sarah",    "Chen",     "FUN-001", "FGN-001", "LFN-001", "EN"),
    ("John Smith",            "John",     "Smith",    "FUN-001", "FGN-001", "LFN-001", "EN"),
    ("Maria García López",    "Maria",    "García López", "FUN-007", "FGN-014", "LFN-011", "EN"),
    ("Wolfgang Müller",       "Wolfgang", "Müller",   "FUN-055", "FGN-028", "LFN-014", "DE"),
    ("Pierre Dubois",         "Pierre",   "Dubois",   "FUN-001", "FGN-001", "LFN-001", "FR"),
    ("Giovanni Rossi",        "Giovanni", "Rossi",    "FUN-001", "FGN-001", "LFN-001", "IT"),
    ("João Silva Santos",     "João",     "Silva Santos", "FUN-008", "FGN-001", "LFN-012", "PT_BR"),
    ("Jan de Vries",          "Jan",      "de Vries", "FUN-039", "FGN-001", "LFN-003", "NL"),
    ("Erik Andersson",        "Erik",     "Andersson","FUN-001", "FGN-001", "LFN-001", "SV"),
    ("Krzysztof Kowalski",    "Krzysztof","Kowalski", "FUN-018", "FGN-014", "LFN-001", "PL"),
    ("Nagy László",           "László",   "Nagy",     "FUN-028", "FGN-001", "LFN-022", "HU"),
    ("Jan Novák",             "Jan",      "Novák",    "FUN-001", "FGN-001", "LFN-014", "CS"),
    # CJK
    ("山田太郎",                "太郎",      "山田",       "FUN-020", "FGN-008", "LFN-006", "JA"),
    ("王伟",                   "伟",       "王",        "FUN-023", "FGN-007", "LFN-007", "ZH_CN"),
    ("王偉",                   "偉",       "王",        "FUN-025", "FGN-007", "LFN-007", "ZH_TW"),
    ("김민수",                  "민수",      "김",         "FUN-026", "FGN-009", "LFN-008", "KO"),
    # Right-to-left
    ("أحمد بن سعيد العبدالله",   "أحمد",     "العبدالله",  "FUN-032", "FGN-010", "LFN-009", "AR"),
    ("דוד כהן",                "דוד",      "כהן",        "FUN-058", "FGN-011", "LFN-020", "HE"),
    # Other scripts
    ("สมชาย สุขสวัสดิ์",         "สมชาย",     "สุขสวัสดิ์",   "FUN-059", "FGN-012", "LFN-019", "TH"),
    ("Иван Петрович Сидоров",  "Иван",     "Сидоров",  "FUN-030", "FGN-013", "LFN-010", "RU"),
    ("राज शर्मा",                "राज",      "शर्मा",      "FUN-001", "FGN-027", "LFN-001", "HI"),
    ("Mehmet Yılmaz",         "Mehmet",   "Yılmaz",   "FUN-001", "FGN-001", "LFN-021", "TR"),
    ("Σπύρος Παπαδόπουλος",   "Σπύρος",   "Παπαδόπουλος","FUN-060", "FGN-026", "LFN-001", "EL"),
]

EMAIL_TEMPLATES = ["{first}.{last}@{org}.com", "{first}_{last}@{org}.org",
                   "{first}@{org}.io", "{f}{last}@{org}.net"]
ORG_NAMES = {
    "EN":  ["acmecorp", "northshore", "globaltech", "nexusbank", "lattice"],
    "DE":  ["techgmbh", "berlinerag"],
    "FR":  ["paristech", "europebanque"],
    "JA":  ["nipponcorp", "tokyobank"],
    "AR":  ["riyadhbank", "albayan"],
    "default": ["corp", "company"],
}

DOB_FORMATS = {
    "EN": "{m:02d}/{d:02d}/{y}",
    "DE": "{d:02d}.{m:02d}.{y}",
    "FR": "{d:02d}/{m:02d}/{y}",
    "ES": "{d:02d}/{m:02d}/{y}",
    "IT": "{d:02d}/{m:02d}/{y}",
    "PT_BR": "{d:02d}/{m:02d}/{y}",
    "JA": "{y}年{m}月{d}日",
    "ZH_CN": "{y}年{m}月{d}日",
    "ZH_TW": "{y}年{m}月{d}日",
    "KO": "{y}년 {m}월 {d}일",
    "AR": "{d:02d}/{m:02d}/{y}",
    "HE": "{d:02d}/{m:02d}/{y}",
    "TH": "{d:02d}/{m:02d}/{y_th}",
    "RU": "{d:02d}.{m:02d}.{y}",
    "HI": "{d:02d}/{m:02d}/{y}",
    "TR": "{d:02d}.{m:02d}.{y}",
    "PL": "{d:02d}.{m:02d}.{y}",
    "NL": "{d:02d}-{m:02d}-{y}",
    "SV": "{y}-{m:02d}-{d:02d}",
    "FI": "{d:02d}.{m:02d}.{y}",
    "CS": "{d:02d}.{m:02d}.{y}",
    "HU": "{y}.{m:02d}.{d:02d}",
    "NO": "{d:02d}.{m:02d}.{y}",
    "DA": "{d:02d}-{m:02d}-{y}",
    "EL": "{d:02d}/{m:02d}/{y}",
    "PT_EU": "{d:02d}/{m:02d}/{y}",
    "FR_CA": "{y}-{m:02d}-{d:02d}",
}

NID_FORMATS = {
    "EN": ("{a:03d}-{b:02d}-{c:04d}", "NID-001"),
    "PT_BR": ("{a:03d}.{b:03d}.{c:03d}-{d:02d}", "NID-007"),
    "DE": ("{a:02d} {b:03d} {c:03d} {d:03d}", "NID-003"),
    "FR": ("{a:1d} {b:02d} {c:02d} {d:02d} {e:03d} {f:03d} {g:02d}", "NID-004"),
    "JA": ("{a:04d} {b:04d} {c:04d}", "NID-008"),
    "default": ("{a:03d}-{b:02d}-{c:04d}", "NID-001"),
}

# Article 9 special-category vocabulary
A9_VOCAB = {
    "Religion": [("Catholic", "RE-002"), ("Muslim", "RE-001"), ("Hindu", "RE-001"),
                 ("Buddhist", "RE-001"), ("Jewish", "RE-001"), ("Sikh", "RE-001"),
                 ("مسلم", "RE-015"), ("仏教", "RE-014")],
    "Sex_Orientation": [("gay", "SO-001"), ("lesbian", "SO-001"), ("bisexual", "SO-001"),
                        ("heterosexual", "SO-001"), ("pansexual", "SO-002")],
    "Crime": [("fraud", "CRIME-001"), ("embezzlement", "CRIME-020"),
              ("insider trading", "CRIME-020"), ("tax evasion", "CRIME-020"),
              ("identity theft", "CRIME-001"), ("assault", "CRIME-001"),
              ("money laundering", "CRIME-020")],
    "Medical_Information": [("Type 2 diabetes", "MED-001"), ("hypertension", "MED-001"),
                            ("asthma", "MED-001"), ("PTSD", "MED-005"),
                            ("multiple sclerosis", "MED-006"), ("chronic fatigue syndrome", "MED-006")],
    "Trade_Union_Membership": [("UAW member", "TUM-001"), ("CGT membership", "TUM-003"),
                                ("IG Metall", "TUM-002"), ("FNV member", "TUM-008")],
    "Political_Party": [("Democrat", "PP-001"), ("Republican", "PP-001"),
                        ("Labour", "PP-002"), ("CDU", "PP-003"), ("PT", "PP-005")],
    "PEP_Status": [("PEP Level 1", "PEP-002"), ("classified as PEP", "PEP-001"),
                   ("PEP screening: positive", "PEP-004")],
    "Allergy_Information": [("Penicillin (anaphylaxis)", "ALLG-001"),
                            ("Peanut allergy (severe)", "ALLG-002"),
                            ("latex (mild)", "ALLG-003")],
}


def fictional_email(first: str, last: str, rng: random.Random, lang: str) -> str:
    """Generate a fictional email address based on a name + language hint."""
    tmpl = rng.choice(EMAIL_TEMPLATES)
    org = rng.choice(ORG_NAMES.get(lang, ORG_NAMES["default"]))
    # ASCII-fold the name for the local part
    first_l = "".join(c for c in first.lower() if c.isascii() and c.isalpha()) or "x"
    last_l = "".join(c for c in last.lower() if c.isascii() and c.isalpha()) or "y"
    return tmpl.format(first=first_l, last=last_l, f=first_l[0] if first_l else "x", org=org)


def fictional_dob(rng: random.Random, language: str) -> str:
    """Generate a DOB string in the locale format."""
    y = rng.randint(1950, 2005)
    m = rng.randint(1, 12)
    d = rng.randint(1, 28)
    fmt = DOB_FORMATS.get(language, DOB_FORMATS["EN"])
    return fmt.format(y=y, m=m, d=d, y_th=y + 543)


def fictional_nid(rng: random.Random, language: str) -> tuple:
    """Generate a fictional national ID + its v4 pattern_id."""
    fmt, pid = NID_FORMATS.get(language, NID_FORMATS["default"])
    digits = {k: rng.randint(0, 999_999_999) % (10**9) for k in "abcdefg"}
    try:
        return fmt.format(**digits), pid
    except (KeyError, IndexError):
        # Fall back to US format if locale format has issues
        return f"{rng.randint(100,999)}-{rng.randint(10,99)}-{rng.randint(1000,9999)}", "NID-001"


def fictional_mrn(rng: random.Random) -> str:
    """Patient medical record number."""
    return f"MED-{rng.randint(10000, 99999)}-{rng.choice('AB')}"


def fictional_employee_id(rng: random.Random) -> str:
    """Employee ID."""
    prefix = rng.choice(["EMP", "NOW", "SAP", "WD"])
    return f"{prefix}-{rng.randint(1000, 99999):05d}"


def fictional_business_title(rng: random.Random) -> tuple:
    """Pick a job title + v4 pattern."""
    titles = [
        ("Chief Compliance Officer", "BT-001"),
        ("Senior Software Engineer", "BT-008"),
        ("Director of Engineering", "BT-011"),
        ("Attending Physician", "BT-004"),
        ("Senior Partner", "BT-005"),
        ("Lieutenant Colonel", "BT-006"),
        ("Vice President", "BT-002"),
        ("Marketing Director", "BT-002"),
    ]
    return rng.choice(titles)


def fictional_org(rng: random.Random, domain: str) -> tuple:
    """Pick a fictional org name + pattern_id appropriate for the domain."""
    pools = {
        "healthcare": [("North Shore Hospital", "ORG-006"),
                       ("Mayo Clinic Affiliate", "ORG-006"),
                       ("Central General Hospital", "ORG-006")],
        "legal":      [("Lattice Capital Partners", "ORG-001"),
                       ("Sullivan & Cromwell", "ORG-020"),
                       ("Baker McKenzie", "ORG-020")],
        "finance":    [("JPMorgan Chase", "ORG-011"),
                       ("Deutsche Bank", "ORG-011"),
                       ("بنك الرياض", "ORG-014")],
        "government": [("Department of Compliance", "ORG-004"),
                       ("Federal Trade Agency", "ORG-004")],
        "technology": [("Acme Corporation", "ORG-001"),
                       ("Acme Tech Inc.", "ORG-001"),
                       ("Stripe", "ORG-012")],
        "HR":         [("Acme Corporation", "ORG-001"),
                       ("Acme Tech Inc.", "ORG-001")],
        "insurance":  [("National Insurance Co.", "ORG-001")],
        "customer_service": [("Acme Support", "ORG-001")],
        "law_enforcement":  [("State Police", "ORG-004"),
                             ("FBI", "ORG-004")],
        "social_media":     [("X (formerly Twitter)", "ORG-019")],
        "e_commerce":       [("Amazon", "ORG-001"),
                             ("Shopify", "ORG-012")],
    }
    return rng.choice(pools.get(domain, pools["technology"]))


# ── Anchor builders ─────────────────────────────────────────────────────────
def build_base_anchor(rng: random.Random, anchor_id: str, category: str,
                      language: str, default_axes: dict) -> dict:
    """Build a base anchor with full name + email + DOB + scenario."""
    name_candidates = [n for n in NAME_POOL if n[-1] == language]
    if not name_candidates:
        name_candidates = [n for n in NAME_POOL if n[-1] == "EN"]
    fn, fg, lf, fn_pid, fgn_pid, lfn_pid, lang = rng.choice(name_candidates)

    email = fictional_email(fg, lf, rng, language)
    dob = fictional_dob(rng, language)
    title, title_pid = fictional_business_title(rng)
    org, org_pid = fictional_org(rng, default_axes.get("domain", "technology"))

    frozen = [
        {"entity_type": "Full_Name", "entity_string": fn, "pattern_id": fn_pid},
        {"entity_type": "Date_of_Birth", "entity_string": dob, "pattern_id": "DOB-001"},
        {"entity_type": "Work_Email_Address", "entity_string": email, "pattern_id": "WE-001"},
        {"entity_type": "Business_Title", "entity_string": title, "pattern_id": title_pid},
        {"entity_type": "Org_Name", "entity_string": org, "pattern_id": org_pid},
    ]

    return {
        "anchor_id": anchor_id,
        "category": category,
        "language": language,
        "axes": dict(default_axes),
        "frozen_entity_values": frozen,
        "persona": f"{title} at {org} (anchor {anchor_id})",
        "narrative": f"A {default_axes.get('format', 'plain_text').replace('_', ' ')} document in {default_axes.get('domain', 'business')} context concerning {fn}.",
    }


def build_stress_test_anchor(rng: random.Random, idx: int) -> dict:
    """Stress-test anchor: very_large + high + hard."""
    lang = rng.choice(["EN", "FR", "DE", "ES", "JA"])  # mix of P1+P2
    axes = {
        "domain": rng.choice(DOMAINS),
        "format": rng.choice(FORMATS),
        "difficulty": "hard",
        "length": "very_large",
        "density": "high",
        "code_switching": rng.choice(["none", "light"]),
        "language": lang,
        "adjacency": rng.choice(["loose", "tight"]),
        "co_occurrence_pattern": "none",
    }
    if axes["adjacency"] == "tight":
        axes["co_occurrence_pattern"] = rng.choice(CO_PATTERNS)
    return build_base_anchor(rng, f"ST-{idx:03d}", "stress_test", lang, axes)


def build_article_9_anchor(rng: random.Random, idx: int) -> dict:
    """Article 9 anchor: includes at least one HIGH-sensitivity entity."""
    lang = rng.choice(["EN", "FR", "DE", "ES", "AR", "PT_BR"])
    a9_type = rng.choice(ARTICLE_9_TYPES)
    axes = {
        "domain": rng.choice(["healthcare", "legal", "finance", "HR", "government"]),
        "format": rng.choice(FORMATS),
        "difficulty": rng.choice(DIFFICULTIES),
        "length": rng.choice(["medium", "large"]),
        "density": rng.choice(["medium", "high"]),
        "code_switching": "none",
        "language": lang,
        "adjacency": rng.choice(["loose", "tight"]),
        "co_occurrence_pattern": "none",
    }
    if axes["adjacency"] == "tight":
        axes["co_occurrence_pattern"] = rng.choice(CO_PATTERNS)
    anchor = build_base_anchor(rng, f"A9-{idx:03d}", "article_9", lang, axes)
    # Add an Article 9 entity to frozen list
    a9_value, a9_pid = rng.choice(A9_VOCAB[a9_type])
    anchor["frozen_entity_values"].append({
        "entity_type": a9_type, "entity_string": a9_value, "pattern_id": a9_pid,
    })
    anchor["narrative"] += f" Article 9 element: {a9_type.lower()} = '{a9_value}'."
    return anchor


def build_non_latin_anchor(rng: random.Random, idx: int) -> dict:
    """Non-Latin script anchor: language in {CJK, AR, HE, TH, HI, RU, EL}."""
    lang = rng.choice(NON_LATIN_LANGS)
    axes = {
        "domain": rng.choice(DOMAINS),
        "format": rng.choice(FORMATS),
        "difficulty": rng.choice(DIFFICULTIES),
        "length": rng.choice(["small", "medium", "large"]),
        "density": rng.choice(["medium", "high"]),
        "code_switching": rng.choice(["none", "light"]),
        "language": lang,
        "adjacency": rng.choice(["loose", "tight"]),
        "co_occurrence_pattern": "none",
    }
    if axes["adjacency"] == "tight":
        axes["co_occurrence_pattern"] = rng.choice(CO_PATTERNS)
    return build_base_anchor(rng, f"NL-{idx:03d}", "non_latin", lang, axes)


def build_co_pattern_anchor(rng: random.Random, co_id: str, idx: int) -> dict:
    """CO-pattern anchor: adjacency=tight with a specific CO-### pattern."""
    lang = rng.choice(["EN", "FR", "DE", "ES", "JA", "AR"])
    axes = {
        "domain": rng.choice(DOMAINS),
        "format": rng.choice(FORMATS),
        "difficulty": rng.choice(["medium", "hard"]),
        "length": rng.choice(["small", "medium"]),
        "density": rng.choice(["medium", "high"]),
        "code_switching": "none",
        "language": lang,
        "adjacency": "tight",
        "co_occurrence_pattern": co_id,
    }
    return build_base_anchor(rng, f"CO-{idx:03d}", "co_pattern", lang, axes)


# ── Sub-sweep executors ─────────────────────────────────────────────────────
def sweep_format(anchor: dict) -> list:
    """Emit 7 variants, one per format."""
    variants = []
    for fmt in FORMATS:
        v = json.loads(json.dumps(anchor))  # deep copy
        v["axes"]["format"] = fmt
        v["sweep_axis"] = "text_format"
        v["sweep_value"] = fmt
        variants.append(v)
    return variants


def sweep_domain(anchor: dict) -> list:
    """Emit 12 variants, one per domain."""
    variants = []
    for dom in DOMAINS:
        v = json.loads(json.dumps(anchor))
        v["axes"]["domain"] = dom
        v["sweep_axis"] = "text_domain"
        v["sweep_value"] = dom
        variants.append(v)
    return variants


def sweep_difficulty_density(anchor: dict) -> list:
    """Emit 9 variants, one per (difficulty × density)."""
    variants = []
    for diff in DIFFICULTIES:
        for dens in DENSITIES:
            v = json.loads(json.dumps(anchor))
            v["axes"]["difficulty"] = diff
            v["axes"]["density"] = dens
            v["sweep_axis"] = "difficulty_x_density"
            v["sweep_value"] = f"{diff}_x_{dens}"
            variants.append(v)
    return variants


def enrich_variant_with_target(variant: dict, pattern_data: dict, rng: random.Random) -> dict:
    """Pick a target pattern for the variant — use the first frozen entity as
    the target unless the anchor was Article 9 (in which case use the A9 entity)."""
    # Prefer Article 9 entity if present
    a9_types = set(ARTICLE_9_TYPES)
    a9_entity = next((e for e in variant["frozen_entity_values"] if e["entity_type"] in a9_types), None)
    if a9_entity:
        target_entity = a9_entity["entity_type"]
        target_pid = a9_entity["pattern_id"]
    else:
        # Fall back to a non-Full_Name entity (most informative target)
        target = next((e for e in variant["frozen_entity_values"]
                      if e["entity_type"] not in ("Full_Name", "First_Given_Name", "Last_Family_Name")),
                     variant["frozen_entity_values"][0])
        target_entity = target["entity_type"]
        target_pid = target["pattern_id"]

    target_pattern = pattern_data["patterns_by_id"].get(target_pid)
    return {
        **variant,
        "mode": "paired_sweep",
        "target_entity_type": target_entity,
        "target_pattern_id": target_pid,
        "target_pattern_desc": target_pattern["description"] if target_pattern else None,
        "target_pattern_example": (
            target_pattern["examples"][0] if target_pattern and target_pattern.get("examples") else None
        ),
        "behavioral_frame": "co_occurrence" if variant["axes"]["adjacency"] == "tight" else "isolation",
    }


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    rng = random.Random(RNG_SEED)
    pattern_data = json.loads(PATTERNS_JSON.read_text())
    print(f"Loaded {len(pattern_data['patterns_flat'])} v4 patterns")

    # ── Build 100 anchors per §4.6.2 stratification ────────────────────────
    print(f"\n=== Building 100 anchors ===")
    anchors = []
    for i in range(30):
        anchors.append(build_stress_test_anchor(rng, i))
    for i in range(30):
        anchors.append(build_article_9_anchor(rng, i))
    for i in range(25):
        anchors.append(build_non_latin_anchor(rng, i))
    for i, co in enumerate(CO_PATTERNS):
        anchors.append(build_co_pattern_anchor(rng, co, i))
    print(f"  Authored {len(anchors)} anchors")
    print(f"  stress_test : {sum(1 for a in anchors if a['category'] == 'stress_test')}")
    print(f"  article_9   : {sum(1 for a in anchors if a['category'] == 'article_9')}")
    print(f"  non_latin   : {sum(1 for a in anchors if a['category'] == 'non_latin')}")
    print(f"  co_pattern  : {sum(1 for a in anchors if a['category'] == 'co_pattern')}")

    # Save anchor library
    ANCHORS_JSON.write_text(json.dumps({"anchors": anchors, "count": len(anchors)},
                                       indent=2, ensure_ascii=False))
    print(f"  Wrote {ANCHORS_JSON}")

    # ── Allocate anchors to sub-sweeps ─────────────────────────────────────
    print(f"\n=== Allocating to sub-sweeps ===")
    shuffled = list(anchors)
    rng.shuffle(shuffled)
    format_anchors = shuffled[:50]
    domain_anchors = shuffled[50:80]
    diff_density_anchors = shuffled[80:100]
    print(f"  format sweep      : {len(format_anchors)} anchors × 7 formats = {len(format_anchors) * 7}")
    print(f"  domain sweep      : {len(domain_anchors)} anchors × 12 domains = {len(domain_anchors) * 12}")
    print(f"  diff×density sweep: {len(diff_density_anchors)} anchors × 9 combos = {len(diff_density_anchors) * 9}")

    # ── Execute sub-sweeps ─────────────────────────────────────────────────
    plan = []
    for a in format_anchors:
        plan.extend(sweep_format(a))
    for a in domain_anchors:
        plan.extend(sweep_domain(a))
    for a in diff_density_anchors:
        plan.extend(sweep_difficulty_density(a))

    # ── Enrich each variant with target_pattern + frame ────────────────────
    enriched = [enrich_variant_with_target(v, pattern_data, rng) for v in plan]

    # Assign record IDs
    for i, row in enumerate(enriched, start=1):
        row["record_id"] = i

    # ── Write JSONL ────────────────────────────────────────────────────────
    with PLAN_JSONL.open("w") as f:
        for row in enriched:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"\nWrote {PLAN_JSONL} ({PLAN_JSONL.stat().st_size / 1024:.0f} KB)")

    # ── Verification & report ───────────────────────────────────────────────
    fmt_records = [r for r in enriched if r["sweep_axis"] == "text_format"]
    dom_records = [r for r in enriched if r["sweep_axis"] == "text_domain"]
    dd_records  = [r for r in enriched if r["sweep_axis"] == "difficulty_x_density"]

    fmt_coverage = Counter(r["sweep_value"] for r in fmt_records)
    dom_coverage = Counter(r["sweep_value"] for r in dom_records)
    dd_coverage  = Counter(r["sweep_value"] for r in dd_records)

    # Per-anchor verification: every anchor in format-sweep should produce 7 records
    anchor_ids_in_format = Counter(r["anchor_id"] for r in fmt_records)
    anchor_ids_in_domain = Counter(r["anchor_id"] for r in dom_records)
    anchor_ids_in_dd     = Counter(r["anchor_id"] for r in dd_records)

    report = {
        "total_records": len(enriched),
        "anchor_count": len(anchors),
        "anchor_breakdown": {
            "stress_test": sum(1 for a in anchors if a["category"] == "stress_test"),
            "article_9":   sum(1 for a in anchors if a["category"] == "article_9"),
            "non_latin":   sum(1 for a in anchors if a["category"] == "non_latin"),
            "co_pattern":  sum(1 for a in anchors if a["category"] == "co_pattern"),
        },
        "sweep_counts": {
            "text_format":          len(fmt_records),
            "text_domain":          len(dom_records),
            "difficulty_x_density": len(dd_records),
        },
        "format_sweep_coverage":       dict(fmt_coverage),
        "domain_sweep_coverage":       dict(dom_coverage),
        "diff_density_sweep_coverage": dict(dd_coverage),
        "format_anchors_complete":       sum(1 for c in anchor_ids_in_format.values() if c == 7),
        "domain_anchors_complete":       sum(1 for c in anchor_ids_in_domain.values() if c == 12),
        "diff_density_anchors_complete": sum(1 for c in anchor_ids_in_dd.values() if c == 9),
        "patterns_attached":             sum(1 for r in enriched if r["target_pattern_id"]),
        "language_distribution":         dict(Counter(r["axes"]["language"] for r in enriched)),
        "co_pattern_distribution":       dict(Counter(r["axes"]["co_occurrence_pattern"] for r in enriched
                                                       if r["axes"]["co_occurrence_pattern"] != "none")),
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Wrote {REPORT_JSON}")

    # ── Print summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PAIRED-SWEEP PLAN SUMMARY")
    print("=" * 70)
    print(f"Total records:   {len(enriched)} (target 890)")
    print()
    print(f"Sub-sweep records:")
    print(f"  text_format          : {len(fmt_records):>4} (target 350)")
    print(f"  text_domain          : {len(dom_records):>4} (target 360)")
    print(f"  difficulty × density : {len(dd_records):>4} (target 180)")
    print()
    print(f"Format-sweep coverage (target 50 per value):")
    for fmt in FORMATS:
        print(f"  {fmt:<22} {fmt_coverage.get(fmt, 0)}")
    print()
    print(f"Domain-sweep coverage (target 30 per value):")
    for dom in DOMAINS:
        print(f"  {dom:<22} {dom_coverage.get(dom, 0)}")
    print()
    print(f"Diff × density coverage (target 20 per combo):")
    for diff in DIFFICULTIES:
        for dens in DENSITIES:
            k = f"{diff}_x_{dens}"
            print(f"  {k:<22} {dd_coverage.get(k, 0)}")
    print()
    print(f"Anchors with complete sweeps:")
    print(f"  format (×7):       {report['format_anchors_complete']} / 50")
    print(f"  domain (×12):      {report['domain_anchors_complete']} / 30")
    print(f"  diff×density (×9): {report['diff_density_anchors_complete']} / 20")
    print()
    print(f"Pattern attachment: {report['patterns_attached']} / {len(enriched)}")
    print()
    print(f"CO-### usage (in tight-adjacency records):")
    for co in CO_PATTERNS:
        c = report['co_pattern_distribution'].get(co, 0)
        if c > 0:
            print(f"  {co}: {c}")


if __name__ == "__main__":
    main()
