"""
Family E — Format compliance & checksum validation.

For entities that have well-defined formats (credit cards, IBANs, country-
specific national IDs, emails, IPs), verify that the entity strings produced
are actually structurally valid.

  E1  Email RFC 5322 compliance (regex-based)
  E2  Credit card Luhn check (cards with 13-19 digits)
  E3  IBAN mod-97 check
  E4  US SSN format (heuristic — no real-data lookup)
  E5  IP address valid format (IPv4 / IPv6)
  E6  Per-entity-type format compliance rate (overall)

Per methodology §6.5, target = >=95% format compliance for entities that
have a defined checksum / format spec.

Dependencies: none (pure Python).

Usage:
    python compute_format_checksum.py corpus.json --out format_report.json
"""

import json
import argparse
import re
import ipaddress
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# E1 — Email RFC 5322 (simplified)
# ---------------------------------------------------------------------------

EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9][a-zA-Z0-9-]*(\.[a-zA-Z0-9][a-zA-Z0-9-]*)+$"
)


def check_email(s: str) -> bool:
    return bool(EMAIL_RE.match(s.strip()))


# ---------------------------------------------------------------------------
# E2 — Credit card Luhn check
# ---------------------------------------------------------------------------

def check_luhn(s: str) -> bool:
    digits = [int(c) for c in s if c.isdigit()]
    if not (13 <= len(digits) <= 19):
        return False
    total = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


# ---------------------------------------------------------------------------
# E3 — IBAN mod-97
# ---------------------------------------------------------------------------

def check_iban(s: str) -> bool:
    s = re.sub(r"\s+", "", s).upper()
    if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$", s):
        return False
    # Rearrange + numericize
    rearranged = s[4:] + s[:4]
    numeric = ""
    for ch in rearranged:
        if ch.isdigit():
            numeric += ch
        else:
            numeric += str(ord(ch) - 55)  # A=10, B=11, ...
    try:
        return int(numeric) % 97 == 1
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# E4 — US SSN format (heuristic)
# ---------------------------------------------------------------------------

SSN_RE = re.compile(r"^(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}$")


def check_us_ssn(s: str) -> bool:
    s = s.strip()
    # Try with dashes
    if SSN_RE.match(s):
        return True
    # Try compact (9 digits, no dashes)
    if re.match(r"^\d{9}$", s):
        # Insert dashes and re-check
        return bool(SSN_RE.match(f"{s[:3]}-{s[3:5]}-{s[5:]}"))
    return False


# ---------------------------------------------------------------------------
# E5 — IP address
# ---------------------------------------------------------------------------

def check_ip(s: str) -> bool:
    try:
        ipaddress.ip_address(s.strip())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Format checkers by entity type
# ---------------------------------------------------------------------------

FORMAT_CHECKERS = {
    "Work_Email_Address": check_email,
    "Personal_Email_Address": check_email,
    "Credit_Card_Numbers": check_luhn,
    "Static_IP_Address": check_ip,
}


def check_iban_or_skip(s: str) -> tuple[bool, bool]:
    """Returns (is_valid, was_checked). IBAN format is specific — check only
    if the string superficially looks like an IBAN."""
    cleaned = re.sub(r"\s+", "", s).upper()
    if re.match(r"^[A-Z]{2}\d{2}", cleaned):
        return check_iban(s), True
    return True, False  # not an IBAN-shaped string, skip


def check_us_ssn_or_skip(s: str) -> tuple[bool, bool]:
    """Check SSN format only if the string looks SSN-shaped. Otherwise skip
    (since NID covers many countries)."""
    if re.match(r"^\d{3}-?\d{2}-?\d{4}$", s.strip()):
        return check_us_ssn(s), True
    return True, False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--out", default="format_report.json")
    args = p.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)

    n_records = len(records)
    print(f"Loaded {n_records:,} records")

    results = defaultdict(lambda: {"checked": 0, "passed": 0, "failures": []})
    iban_checked = 0
    iban_passed = 0
    us_ssn_checked = 0
    us_ssn_passed = 0

    for r in records:
        for e in r.get("entities", []):
            et = e.get("entity_type", "")
            es = e.get("entity_string", "")
            if et in FORMAT_CHECKERS:
                ok = FORMAT_CHECKERS[et](es)
                results[et]["checked"] += 1
                if ok:
                    results[et]["passed"] += 1
                else:
                    if len(results[et]["failures"]) < 30:
                        results[et]["failures"].append({
                            "record_id": r.get("record_id"),
                            "entity_string": es[:80],
                        })
            # IBAN check on Customer_Reference / Account_Statements where
            # the string superficially looks like an IBAN
            if et in ("Customer_Reference_Number", "Account_Statements"):
                is_iban, was_checked = check_iban_or_skip(es)
                if was_checked:
                    iban_checked += 1
                    if is_iban:
                        iban_passed += 1
            # US SSN check on National_ID where string looks SSN-shaped
            if et == "National_Identification_Number":
                is_valid, was_checked = check_us_ssn_or_skip(es)
                if was_checked:
                    us_ssn_checked += 1
                    if is_valid:
                        us_ssn_passed += 1

    # Build report
    summary = {}
    for et, counts in sorted(results.items()):
        rate = counts["passed"] / counts["checked"] if counts["checked"] else 1.0
        summary[et] = {
            "checked": counts["checked"],
            "passed": counts["passed"],
            "rate": round(rate, 4),
            "pass": rate >= 0.95,
            "example_failures": counts["failures"][:10],
        }

    iban_rate = iban_passed / iban_checked if iban_checked else 1.0
    ssn_rate = us_ssn_passed / us_ssn_checked if us_ssn_checked else 1.0

    report = {
        "n_records": n_records,
        "E1_E2_E5_by_entity_type": summary,
        "E3_iban_check": {
            "checked": iban_checked,
            "passed": iban_passed,
            "rate": round(iban_rate, 4),
            "pass": iban_rate >= 0.95,
        },
        "E4_us_ssn_check": {
            "checked": us_ssn_checked,
            "passed": us_ssn_passed,
            "rate": round(ssn_rate, 4),
            "pass": ssn_rate >= 0.95,
        },
        "_targets": "Per methodology §6.5: >=95% compliance per checker",
    }

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\nFormat compliance results:")
    print("-" * 60)
    for et, s in summary.items():
        mark = "✓" if s["pass"] else "✗"
        print(f"  {et:<35} {s['passed']:>5}/{s['checked']:<5} ({s['rate']:.1%}) {mark}")
    print(f"  {'IBAN format':<35} {iban_passed:>5}/{iban_checked:<5} ({iban_rate:.1%})")
    print(f"  {'US SSN format':<35} {us_ssn_passed:>5}/{us_ssn_checked:<5} ({ssn_rate:.1%})")
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
