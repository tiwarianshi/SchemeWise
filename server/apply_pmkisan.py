"""Run from the server/ folder:  python apply_pmkisan.py

1. Adds the PM-KISAN profile fields to eligibility.py (profile class + SUPPORTED_FIELDS).
2. Replaces ONLY eligibility_rules of scheme-009 in data/schemes.json.
Safe to re-run. It stops with an error if your files don't look as expected.
It leaves rules_complete = false and verified_at = null on purpose (see the message at the end)."""
import json
from pathlib import Path

NEW_FIELDS = [
    "has_eligible_landholding",
    "is_institutional_landholder",
    "has_constitutional_post_exclusion_in_family",
    "has_elected_official_exclusion_in_family",
    "has_excluded_government_employee_in_family",
    "has_excluded_pensioner_in_family",
    "paid_income_tax_last_assessment_year_in_family",
    "has_practicing_registered_professional_in_family",
    "is_nri_family",
]

# ---------- 1. eligibility.py ----------
path = Path("eligibility.py")
src = path.read_text(encoding="utf-8")

if "has_eligible_landholding" not in src:
    imp = "from pydantic import BaseModel, ConfigDict, Field, field_validator"
    assert imp in src, "Could not find the pydantic import line."
    src = src.replace(imp, "from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator", 1)

    anchor = "    occupation: str | None = None\n"
    assert src.count(anchor) == 1, "Could not find the occupation field in EligibilityProfile."
    block = "\n    # PM-KISAN facts (see data/eligibility_verification.md for exact question wording).\n"
    block += "".join(f"    {name}: StrictBool | None = None\n" for name in NEW_FIELDS)
    src = src.replace(anchor, anchor + block, 1)

    anchor2 = '    "occupation",\n}'
    assert src.count(anchor2) == 1, "Could not find SUPPORTED_FIELDS."
    extra = "".join(f'    "{name}",\n' for name in NEW_FIELDS)
    src = src.replace(anchor2, '    "occupation",\n' + extra + "}", 1)
    path.write_text(src, encoding="utf-8")
    print("eligibility.py updated.")
else:
    print("eligibility.py already has the PM-KISAN fields; skipped.")

# ---------- 2. schemes.json ----------
SRC_URL = "https://pmkisan.gov.in/Documents/RevisedPM-KISANOperationalGuidelines(English).pdf"

def leaf(field, value, description):
    return {"field": field, "operator": "eq", "value": value,
            "description": description, "verified": True, "source_url": SRC_URL}

RULE = {"all_of": [
    leaf("has_eligible_landholding", True,
         "The farmer family must own cultivable land recorded in the State/UT land records (held on 1 February 2019, or inherited after the owner's death)."),
    leaf("is_institutional_landholder", False,
         "Institutional landholders are not eligible."),
    leaf("has_constitutional_post_exclusion_in_family", False,
         "Families with a former or present holder of a constitutional post are not eligible."),
    leaf("has_elected_official_exclusion_in_family", False,
         "Families with a former or present minister, MP, MLA, MLC, mayor of a municipal corporation or district panchayat chairperson are not eligible."),
    leaf("has_excluded_government_employee_in_family", False,
         "Families with a serving or retired government, PSE or autonomous-body officer or employee, or a regular local-body employee, are not eligible (Multi Tasking Staff / Class IV / Group D are excepted)."),
    leaf("has_excluded_pensioner_in_family", False,
         "Families with a retired pensioner drawing Rs 10,000 or more per month are not eligible (Multi Tasking Staff / Class IV / Group D are excepted)."),
    leaf("paid_income_tax_last_assessment_year_in_family", False,
         "Families in which anyone paid income tax in the last assessment year are not eligible."),
    leaf("has_practicing_registered_professional_in_family", False,
         "Families with a practising registered professional (doctor, engineer, lawyer, chartered accountant or architect) are not eligible."),
    leaf("is_nri_family", False,
         "New applicants whose family is Non-Resident Indian under the Income Tax Act are not eligible."),
]}

NOTE = ("Rules encoded from the PM-KISAN Operational Guidelines (revised as on 29.03.2020), clauses 3, 4.1, 4.1(c), 5.2-5.3. "
        "Before setting rules_complete to true: check the portal's 'Amendment in Operational Guidelines' and 'Clarification' pages for changes after 29.03.2020, "
        "and review data/eligibility_verification.md. eKYC, Aadhaar and bank-account requirements are registration steps, not modelled here.")

sp = Path("data/schemes.json")
data = json.loads(sp.read_text(encoding="utf-8"))
target = next((s for s in data if s.get("id") == "scheme-009"), None)
assert target is not None, "scheme-009 not found in data/schemes.json."
target["eligibility_rules"] = {
    "rules_complete": False,
    "source_url": SRC_URL,
    "verified_at": None,
    "rule": RULE,
    "verification_note": NOTE,
}
sp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("scheme-009 eligibility_rules updated (rules_complete is still false).")
print("Next: python validate_scheme_data.py && python -m pytest -v")