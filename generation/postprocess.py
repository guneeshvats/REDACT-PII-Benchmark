#!/usr/bin/env python3
"""
postprocess_run1.py
-------------------
Applies three deterministic post-processing fixes to any coverage output file:

  Fix 1 (R13) – Non-canonical entity types → remapped or dropped
  Fix 2 (R14) – Empty sensitivity_tier → filled from entity-type→tier table
  Fix 3 (R4)  – Multi-mention completeness → missing mention_index entries added

Usage:
  python3 postprocess_run1.py <path/to/coverage_output.json>

Outputs (all under OUTPUT_DIR, named after the run tag derived from input filename):
  <run_tag>_clean_postprocessed.jsonl  — generation_status=ok records, all fixes applied
  <run_tag>_failed.jsonl               — json_error records that need re-running
  <run_tag>_postprocess_report.txt     — human-readable stats
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
_DEFAULT_INPUT = (
    "./"
    "run1_29may_coverage_output_2026-05-29_04-51-22.json"
)
INPUT_FILE = Path(sys.argv[1] if len(sys.argv) > 1 else _DEFAULT_INPUT)

# Derive run tag from filename: e.g. "run2_29may_coverage_output_...json" → "run2_29may"
_stem = INPUT_FILE.stem  # e.g. run2_29may_coverage_output_2026-06-07_01-02-47
_parts = _stem.split("_coverage_output")
RUN_TAG = _parts[0] if len(_parts) > 1 else _stem

OUTPUT_DIR = Path("./outputs")
OUT_CLEAN  = OUTPUT_DIR / f"{RUN_TAG}_clean_postprocessed.jsonl"
OUT_FAILED = OUTPUT_DIR / f"{RUN_TAG}_failed.jsonl"
OUT_REPORT = OUTPUT_DIR / f"{RUN_TAG}_postprocess_report.txt"

# ── 51 canonical entity types (R13 — from generation_prompt_v3.yaml §R13) ───
CANONICAL_TYPES: set[str] = {
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    "Address_Work", "Address_Personal",
    "Telephone_Numbers_Work", "Telephone_Numbers_Personal",
    "Work_Email_Address", "Personal_Email_Address",
    "Date_of_Birth", "Age", "Place_of_Birth", "Gender", "Marital_Status",
    "Nationality", "Citizenship_Status", "Sex_Orientation", "Religion",
    "Political_Party", "Country_of_Residence", "State", "City", "Location",
    "Geolocation_Data", "National_Identification_Number", "Passport_Number",
    "Driving_License_Number", "Tax_Reference_Number", "Compensation_and_Salary",
    "Credit_Card_Numbers", "Customer_Reference_Number", "Account_Statements",
    "Business_Title", "Org_Name", "Employee_ID_Number", "Building_Badge_Card_Number",
    "Performance_Assessment", "Disciplinary_Action", "Sickness_Day_Records",
    "Professional_Background", "Crime", "PEP_Status", "Trade_Union_Membership",
    "Allergy_Information", "Medical_Information", "Social_Media_Identifiers",
    "Static_IP_Address", "Password", "Date_Time", "Emergency_Contact_Details",
}

# ── Non-canonical → canonical remap (R13 repair) ────────────────────────────
# None means drop the entity (no safe canonical mapping exists)
TYPE_REMAP: dict[str, str | None] = {
    # typo
    "Drivers_License_Number":       "Driving_License_Number",
    # network
    "IP_Address":                   "Static_IP_Address",
    "IPv4_Address":                 "Static_IP_Address",
    "IPv6_Address":                 "Static_IP_Address",
    # account / financial
    "Bank_Account_Number":          "Account_Statements",
    "Financial_Account_Number":     "Account_Statements",
    "IBAN_Code":                    "Account_Statements",
    "IBAN":                         "Account_Statements",
    "BIC":                          "Account_Statements",
    "Swift_Code":                   "Account_Statements",
    "VIN":                          "Customer_Reference_Number",
    # geo
    "Postal_Code":                  "Location",
    "Zip_Code":                     "Location",
    # identity
    "SSN":                          "National_Identification_Number",
    "ID_Card":                      "National_Identification_Number",
    "Tax_ID":                       "Tax_Reference_Number",
    # contact
    "Phone_Number":                 "Telephone_Numbers_Personal",
    "Phone_Mobile":                 "Telephone_Numbers_Personal",
    "Mobile_Phone":                 "Telephone_Numbers_Personal",
    "Email_Address":                "Personal_Email_Address",
    "Email_Personal":               "Personal_Email_Address",
    "Email_Work":                   "Work_Email_Address",
    # online / digital
    "Username":                     "Social_Media_Identifiers",
    "User_ID":                      "Social_Media_Identifiers",
    "Handle":                       "Social_Media_Identifiers",
    "Username_Handle":              "Social_Media_Identifiers",
    "Online_Username":              "Social_Media_Identifiers",
    "Online_Username_Handle":       "Social_Media_Identifiers",
    "Online_Username_or_Handle":    "Social_Media_Identifiers",
    "Username_or_Handle":           "Social_Media_Identifiers",
    "Social_Media_Handle":          "Social_Media_Identifiers",
    "Alias":                        "Social_Media_Identifiers",
    "Nickname":                     "Preferred_Name",
    "Middle_Name":                  "Full_Name",
    # government / ID
    "Tax_Identification_Number":    "Tax_Reference_Number",
    "Tax_ID_Number":                "Tax_Reference_Number",
    "Tax_Number":                   "Tax_Reference_Number",
    "National_ID_Card_Number":      "National_Identification_Number",
    "National_ID_Document_Number":  "National_Identification_Number",
    "Drivers_Licence_Number":       "Driving_License_Number",
    "Driver_License_Number":        "Driving_License_Number",
    "License_Plate":                "Driving_License_Number",
    "License_Plate_Number":         "Driving_License_Number",
    "Vehicle_Registration_Number":  "Driving_License_Number",
    "Vehicle_Registration":         "Driving_License_Number",
    "Vehicle_Registration_Plate":   "Driving_License_Number",
    "Vehicle_Plate_Number":         "Driving_License_Number",
    "Vehicle_Plate":                "Driving_License_Number",
    "Vehicle_License_Plate":        "Driving_License_Number",
    "Vehicle_ID_Number":            "Driving_License_Number",
    "Vehicle_ID":                   "Driving_License_Number",
    "Vehicle_Identifier":           "Driving_License_Number",
    "Vehicle_Identification_Number": "Driving_License_Number",
    "Vehicle_Registration_Plate":   "Driving_License_Number",
    "Vehicle_Info":                 "Driving_License_Number",
    "Vehicle_Information":          "Driving_License_Number",
    # financial
    "Financial_Amount":             "Compensation_and_Salary",
    "Financial_Transaction_Amount": "Compensation_and_Salary",
    "Financial_Transaction":        "Account_Statements",
    "Financial_Information":        "Account_Statements",
    "Financial_Account_Balance":    "Account_Statements",
    "Bank_Account_Numbers":         "Account_Statements",
    "Banking_Information":          "Account_Statements",
    "Bank_Routing_Number":          "Account_Statements",
    "Bank_Routing_Code":            "Account_Statements",
    "IBAN_Number":                  "Account_Statements",
    "SWIFT_BIC_Code":               "Account_Statements",
    "Cryptocurrency_Wallet":        "Account_Statements",
    "Digital_Wallet_ID":            "Account_Statements",
    "Credit_Card_CVV":              "Credit_Card_Numbers",
    "Credit_Card_Expiry":           "Credit_Card_Numbers",
    "Credit_Card_Expiration":       "Credit_Card_Numbers",
    "PIN_Code":                     "Password",
    "PIN":                          "Password",
    "Password_or_PIN":              "Password",
    "Password_or_Key":              "Password",
    "API_Key":                      "Password",
    "API_Key_or_Secret":            "Password",
    "Security_Question_Answer":     "Password",
    # geographic
    "Country":                      "Country_of_Residence",
    "Country_of_Birth":             "Place_of_Birth",
    "Zip_Postal_Code":              "Address_Personal",
    "Address":                      "Address_Personal",
    "GPS_Coordinates":              "Geolocation_Data",
    # health
    "Blood_Type":                   "Medical_Information",
    "Medical_Insurance_Number":     "Medical_Information",
    "Medical_License_Number":       "Medical_Information",
    "Allergy_Severity":             "Allergy_Information",
    "Disability_Status":            "Medical_Information",
    # employment / org
    "Performance_Review":           "Performance_Assessment",
    "Performance_Rating":           "Performance_Assessment",
    "Professional_License_Number":  "Professional_Background",
    "Educational_Record":           "Professional_Background",
    "Education":                    "Professional_Background",
    "Test_Score":                   "Professional_Background",
    "Security_Clearance":           "Professional_Background",
    "Org_Registration_Number":      "Org_Name",
    "Org_Reference_Number":         "Org_Name",
    # digital / device
    "Device_ID":                    "Static_IP_Address",
    "Device_Identifier":            "Static_IP_Address",
    "Device_ID_Number":             "Static_IP_Address",
    "MAC_Address":                  "Static_IP_Address",
    "IMEI":                         "Static_IP_Address",
    "IMEI_Number":                  "Static_IP_Address",
    "Server_Name":                  "Static_IP_Address",
    "Server_IP_or_Hostname":        "Static_IP_Address",
    "Port_Number":                  "Static_IP_Address",
    "Serial_Number":                "Static_IP_Address",
    "Unique_Identifier":            "Static_IP_Address",
    "Digital_Identifier":           "Static_IP_Address",
    "Tracking_Number":              "Customer_Reference_Number",
    "URL":                          "Social_Media_Identifiers",
    # sensitive attributes
    "Sexual_Orientation":           "Sex_Orientation",
    "Gender_Identity":              "Gender",
    "Gender_Sexuality":             "Sex_Orientation",
    "Gender_and_Sexuality":         "Sex_Orientation",
    "Political_Affiliation":        "Political_Party",
    "Political_Opinion":            "Political_Party",
    "Union_Membership":             "Trade_Union_Membership",
    "Caste":                        "Religion",
    "Ethnic_Origin":                None,
    "Physical_Description":         None,
    "Physical_Characteristics":     None,
    "Physical_Attribute":           None,
    "Physical_Characteristic":      None,
    "Physical_Identifying_Characteristic": None,
    "Family_Relationship":          "Emergency_Contact_Details",
    "Number_of_Children":           None,
    "Dietary_Restriction":          None,
    # no safe canonical mapping — drop
    "Ethnicity":                    None,
    "Race_Ethnicity":               None,
    "Race":                         None,
    "Financial_Loss":               None,
    "Currency_Amount":              None,
    "Branch_Code":                  None,
}

# ── Sensitivity tier mapping (R14 — from generation_prompt_v3.yaml §R14) ────
TIER_HIGH: set[str] = {
    "National_Identification_Number", "Passport_Number", "Driving_License_Number",
    "Tax_Reference_Number", "Credit_Card_Numbers", "Account_Statements", "Password",
    "Religion", "Sex_Orientation", "Political_Party", "Trade_Union_Membership",
    "Crime", "PEP_Status", "Medical_Information", "Allergy_Information",
    "Date_of_Birth", "Address_Work", "Address_Personal", "Geolocation_Data",
    "Customer_Reference_Number", "Emergency_Contact_Details", "Building_Badge_Card_Number",
}
TIER_MEDIUM: set[str] = {
    "Full_Name", "First_Given_Name", "Last_Family_Name", "Preferred_Name",
    "Work_Email_Address", "Personal_Email_Address",
    "Telephone_Numbers_Work", "Telephone_Numbers_Personal",
    "Place_of_Birth", "Gender", "Marital_Status", "Nationality",
    "Citizenship_Status", "Compensation_and_Salary", "Static_IP_Address",
    "Social_Media_Identifiers", "Employee_ID_Number",
    "Performance_Assessment", "Disciplinary_Action", "Sickness_Day_Records",
    "Professional_Background",
}
TIER_LOW: set[str] = {
    "Age", "Country_of_Residence", "State", "City", "Location",
    "Business_Title", "Org_Name", "Date_Time",
}


def get_tier(entity_type: str) -> str:
    if entity_type in TIER_HIGH:
        return "HIGH"
    if entity_type in TIER_MEDIUM:
        return "MEDIUM"
    if entity_type in TIER_LOW:
        return "LOW"
    return "MEDIUM"   # conservative default for any unknown type


def remap_entity_type(etype: str) -> str | None:
    """Return canonical type string, or None to drop this entity."""
    if etype in CANONICAL_TYPES:
        return etype
    mapped = TYPE_REMAP.get(etype)
    if mapped is None and etype not in TYPE_REMAP:
        return etype   # unknown — keep as-is so stats can surface it
    return mapped      # None means drop


def fix_multi_mention(text: str, entities: list[dict]) -> tuple[list[dict], int]:
    """
    R4: every occurrence of an entity_string in text must have its own
    mention_index entry. Scans for missing occurrences and appends them,
    copying metadata from the first existing annotation for that string.
    Returns (updated_entities, count_added).
    """
    if not text or not entities:
        return entities, 0

    by_string: dict[str, list[dict]] = defaultdict(list)
    for e in entities:
        es = e.get("entity_string", "")
        if es:
            by_string[es].append(e)

    new_entities = list(entities)
    added = 0

    for es, anns in by_string.items():
        # Count all verbatim occurrences
        count, start = 0, 0
        while True:
            pos = text.find(es, start)
            if pos == -1:
                break
            count += 1
            start = pos + len(es)

        needed = count - len(anns)
        if needed > 0:
            template = anns[0].copy()
            next_idx = max((a.get("mention_index", 0) for a in anns), default=0) + 1
            for _ in range(needed):
                new_ann = template.copy()
                new_ann["mention_index"] = next_idx
                new_entities.append(new_ann)
                next_idx += 1
                added += 1

    return new_entities, added


def process_record(record: dict) -> tuple[dict, dict]:
    """Apply all three fixes. Returns (fixed_record, per_record_stats)."""
    stats: dict[str, int | list] = {
        "remapped_types": 0,
        "dropped_entities": 0,
        "tier_filled": 0,
        "mentions_added": 0,
        "unknown_types": [],
    }

    text = record.get("text", "")
    entities: list[dict] = list(record.get("entities") or [])

    # ── Fix 1: Canonical type remapping ──────────────────────────────────────
    fixed_entities: list[dict] = []
    for e in entities:
        etype = e.get("entity_type", "")
        canonical = remap_entity_type(etype)
        if canonical is None:
            stats["dropped_entities"] += 1   # type: ignore[operator]
            continue
        if canonical != etype:
            e = dict(e)
            e["entity_type"] = canonical
            stats["remapped_types"] += 1      # type: ignore[operator]
        if canonical not in CANONICAL_TYPES:
            stats["unknown_types"].append(canonical)  # type: ignore[union-attr]
        fixed_entities.append(e)

    # ── Fix 2: Sensitivity tier fill ─────────────────────────────────────────
    for e in fixed_entities:
        if not e.get("sensitivity_tier"):
            e["sensitivity_tier"] = get_tier(e.get("entity_type", ""))
            stats["tier_filled"] += 1         # type: ignore[operator]

    # ── Fix 3: Multi-mention completeness ────────────────────────────────────
    fixed_entities, added = fix_multi_mention(text, fixed_entities)
    stats["mentions_added"] = added

    # ── Rebuild di / dp lists to cover any newly added entity_strings ────────
    di_by_str = {
        e.get("entity_string"): e
        for e in (record.get("direct_indirect_classification") or [])
    }
    dp_by_str = {
        e.get("entity_string"): e
        for e in (record.get("disclosure_policy") or [])
    }

    # entity_string → entity_type from fixed list (first occurrence wins)
    etype_by_str: dict[str, str] = {}
    for e in fixed_entities:
        es = e.get("entity_string", "")
        if es and es not in etype_by_str:
            etype_by_str[es] = e.get("entity_type", "")

    di_list = list(record.get("direct_indirect_classification") or [])
    dp_list = list(record.get("disclosure_policy") or [])

    for es, etype in etype_by_str.items():
        if es not in di_by_str:
            di_list.append({
                "entity_type": etype,
                "entity_string": es,
                "identifier_class": (
                    "direct" if etype in TIER_HIGH or etype in TIER_MEDIUM
                    else "indirect"
                ),
            })
        if es not in dp_by_str:
            dp_list.append({
                "entity_type": etype,
                "entity_string": es,
                "policy": "may_disclose",
            })

    # ── Assemble fixed record ─────────────────────────────────────────────────
    record = dict(record)
    record["entities"] = fixed_entities
    record["entity_count"] = len(fixed_entities)
    record["direct_indirect_classification"] = di_list
    record["disclosure_policy"] = dp_list

    return record, stats


def main() -> None:
    print(f"Loading {INPUT_FILE} …")
    with open(INPUT_FILE, encoding="utf-8") as f:
        data: list[dict] = json.load(f)
    print(f"Total records in file: {len(data)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ok_records: list[dict] = []
    failed_records: list[dict] = []
    agg = defaultdict(int)
    unknown_type_counts: dict[str, int] = defaultdict(int)

    for record in data:
        if record.get("generation_status") != "ok" or not record.get("text"):
            failed_records.append(record)
            continue

        fixed, stats = process_record(record)
        ok_records.append(fixed)
        agg["remapped_types"]   += stats["remapped_types"]    # type: ignore[operator]
        agg["dropped_entities"] += stats["dropped_entities"]  # type: ignore[operator]
        agg["tier_filled"]      += stats["tier_filled"]       # type: ignore[operator]
        agg["mentions_added"]   += stats["mentions_added"]    # type: ignore[operator]
        for t in stats["unknown_types"]:                       # type: ignore[union-attr]
            unknown_type_counts[t] += 1

    # Write clean records
    with open(OUT_CLEAN, "w", encoding="utf-8") as f:
        for r in ok_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write failed records (for top-up re-run)
    with open(OUT_FAILED, "w", encoding="utf-8") as f:
        for r in failed_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Build report
    unknown_block = (
        "\n".join(
            f"  {t}: {c}"
            for t, c in sorted(unknown_type_counts.items(), key=lambda x: -x[1])
        )
        or "  none"
    )

    report = f"""
POST-PROCESS REPORT — {RUN_TAG}
=================================
Input file    : {INPUT_FILE.name}
Total records : {len(data)}

OUTCOME
  Processed (generation_status=ok) : {len(ok_records)}
  Skipped / failed (need re-run)   : {len(failed_records)}

FIXES APPLIED
  R13  non-canonical types remapped : {agg['remapped_types']}  entities
  R13  entities dropped (no mapping): {agg['dropped_entities']} entities
  R14  sensitivity_tier filled      : {agg['tier_filled']}  entities
  R4   mention_index entries added  : {agg['mentions_added']}  entities

REMAINING UNKNOWN entity types (not in canonical set or remap table):
{unknown_block}

OUTPUT FILES
  Clean JSONL  : {OUT_CLEAN}
  Failed JSONL : {OUT_FAILED}
  This report  : {OUT_REPORT}
"""
    print(report)
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
