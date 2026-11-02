"""Run from the server/ folder:  python apply_nmmss.py

1. eligibility.py: adds 4 NMMSS profile fields + registers them, and fixes evaluate_scheme so a
   definite answer is not blocked by unrelated unanswered questions.
2. data/schemes.json: replaces eligibility_rules, benefits and eligibility text of scheme-008 ONLY.
3. data/eligibility_verification.md: appends the NMMSS section.
Safe to re-run. Stops with an error if your files do not look as expected.
rules_complete stays false and verified_at stays null until YOU confirm the open items."""
import json
from pathlib import Path

# ---------- 1. eligibility.py ----------
path = Path("eligibility.py")
src = path.read_text(encoding="utf-8")

if "selected_in_nmmss_state_test" not in src:
    anchor = "    is_nri_family: StrictBool | None = None\n"
    assert src.count(anchor) == 1, "Run apply_pmkisan.py first (is_nri_family not found)."
    src = src.replace(anchor, anchor + (
        "\n    # NMMSS facts (see data/eligibility_verification.md for exact question wording).\n"
        "    selected_in_nmmss_state_test: StrictBool | None = None\n"
        "    promoted_from_class_8_to_9: StrictBool | None = None\n"
        "    school_type: str | None = None\n"
        "    class_8_marks_percentage: float | None = Field(default=None, ge=0, le=100)\n"), 1)

    vanchor = '    @field_validator("annual_family_income", mode="before")'
    assert src.count(vanchor) == 1, "Could not find the income validator."
    validator = '''    @field_validator("class_8_marks_percentage", mode="before")
    @classmethod
    def validate_class_8_marks(cls, value):
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Class 8 marks must be a number.")

        if not math.isfinite(value):
            raise ValueError("Class 8 marks must be finite.")

        return float(value)

'''
    src = src.replace(vanchor, validator + vanchor, 1)

    sanchor = '    "is_nri_family",\n}'
    assert src.count(sanchor) == 1, "Could not find the end of SUPPORTED_FIELDS."
    src = src.replace(sanchor, '    "is_nri_family",\n    "selected_in_nmmss_state_test",\n'
                      '    "promoted_from_class_8_to_9",\n    "school_type",\n'
                      '    "class_8_marks_percentage",\n}', 1)
    print("eligibility.py: NMMSS fields added.")
else:
    print("eligibility.py: NMMSS fields already present; skipped.")

old_status = '''    if not complete or missing or evaluation_value is None:
        status = "insufficient_information"
    elif evaluation_value is True:
        status = "eligible"
    else:
        status = "not_eligible"
'''
new_status = '''    decided = complete and evaluation_value is not None

    if not decided:
        status = "insufficient_information"
    else:
        # A definite result comes only from verified conditions, so it stands
        # even when unrelated questions (e.g. an unused alternative) are unanswered.
        status = "eligible" if evaluation_value is True else "not_eligible"
        missing = []
'''
if "decided = complete" not in src:
    assert src.count(old_status) == 1, "Could not find the status block in evaluate_scheme."
    src = src.replace(old_status, new_status, 1)
    print("eligibility.py: evaluate_scheme updated.")
path.write_text(src, encoding="utf-8")

# ---------- 2. schemes.json ----------
URL = "https://dsel.education.gov.in/sites/default/files/NMMSS_Guidelines_22.pdf"

def leaf(field, op, value, description):
    return {"field": field, "operator": op, "value": value,
            "description": description, "verified": True, "source_url": URL}

RULE = {"all_of": [
    leaf("selected_in_nmmss_state_test", "eq", True,
         "The student must have been selected through the State/UT Class VIII selection test (MAT and SAT) within the State/UT quota."),
    leaf("annual_family_income", "lte", 350000,
         "Parental income from all sources must not exceed Rs 3,50,000 per year at the time of selection."),
    leaf("school_type", "in", ["Government school", "Government-aided school", "Local body school"],
         "The student must study as a regular student in a Government, Government-aided or local body school. Kendriya Vidyalayas, Jawahar Navodaya Vidyalayas, residential schools with boarding and private schools are not eligible."),
    {"any_of": [
        leaf("class_8_marks_percentage", "gte", 55,
             "The student must have scored at least 55% (or equivalent grade) in the Class VIII examination."),
        {"all_of": [
            leaf("social_category", "in", ["SC", "ST"],
                 "SC/ST students get a 5% relaxation on the Class VIII marks requirement."),
            leaf("class_8_marks_percentage", "gte", 50,
                 "SC/ST students must have scored at least 50% in the Class VIII examination."),
        ]},
    ]},
    leaf("promoted_from_class_8_to_9", "eq", True,
         "The student must have been cleanly promoted from Class VIII to Class IX to start the scholarship."),
]}

NOTE = ("Rules encoded from the NMMSS Revised Guidelines on dsel.education.gov.in (cl. 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 6.1), for a student STARTING the scholarship in Class IX. "
        "Before setting rules_complete to true, confirm: (1) the scheme is approved for 2026-27 - the guidelines say it runs 5 years beyond March 2021; "
        "(2) NSP's 2026-27 rule of one merit-based scheme per year; (3) your State/UT's reservation and quota. "
        "Continuation rules (60% in Class X, clear promotion in Classes X and XII) are not modelled. See data/eligibility_verification.md.")

sp = Path("data/schemes.json")
data = json.loads(sp.read_text(encoding="utf-8"))
target = next((s for s in data if s.get("id") == "scheme-008"), None)
assert target is not None, "scheme-008 not found in data/schemes.json."
target["benefits"] = ["Rs 12,000 per year (Rs 1,000 per month) for up to four years, Class IX to XII, subject to scheme rules."]
target["eligibility"] = [
    "Selected through the State/UT Class VIII selection test within the State/UT quota.",
    "Parental income from all sources not more than Rs 3,50,000 per year.",
    "Regular student in a Government, Government-aided or local body school (not Kendriya Vidyalaya, Jawahar Navodaya Vidyalaya, residential or private schools).",
    "At least 55% marks in Class VIII (50% for SC/ST students) and clear promotion to Class IX.",
]
target["eligibility_rules"] = {
    "rules_complete": False,
    "source_url": URL,
    "verified_at": None,
    "rule": RULE,
    "verification_note": NOTE,
}
sp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("scheme-008 updated (rules_complete is still false).")

# ---------- 3. verification log ----------
LOG = '''

## Scheme ID: scheme-008 - NMMSS (fresh award, Class IX start)

Source: NMMSS Revised Guidelines, dsel.education.gov.in (Ministry of Education). Publication date not shown on the PDF.
The NSP FAQ PDFs only describe the application process; they contain no NMMSS rules.

- [x] Income limit (cl. 1.1): Rs 3,50,000 per year, parental income from all sources, at time of selection
- [x] School type (cl. 1.2, 2.2): Government / Government-aided / local body only; KV, JNV, residential and private schools excluded
- [x] Marks (cl. 2.2, 3.2): 55% in Class VII to appear and in Class VIII at selection; 5% relaxation for SC/ST
- [x] Selection test (cl. 2.1, 3.1): MAT + SAT, 40% aggregate (32% SC/ST) - modelled as "selected in the State/UT test"
- [x] Promotion (cl. 6.1): clear promotion from Class VIII to IX to start
- [x] Map every condition to a supported profile field
- [ ] Confirm the scheme continues for 2026-27 (guidelines: "5 years beyond March 2021")
- [ ] Confirm NSP 2026-27 rule: one merit-based scheme per year (guideline cl. 4.1 says one central scholarship only; the newer NSP notice may supersede it)
- [ ] State/UT reservation and quota norms (cl. 1.1) - NOT modelled
- [ ] Continuation rules (60% in Class X, first-attempt promotion in X and XII) - NOT modelled
- [ ] Run validate_scheme_data.py and pytest; manual API check

Assumption: the Class VII 55% condition to sit the test is enforced by the State when it selects students, so it is covered by "selected".
Status: INCOMPLETE (rules_complete = false)

### Exact question wording (frontend)
| Profile field | Ask the user | Rule |
|---|---|---|
| selected_in_nmmss_state_test | Were you selected for the NMMSS scholarship through your State/UT Class VIII selection test? | must be Yes |
| annual_family_income | Annual family income (parents, all sources) | at most 350000 |
| school_type | What type of school are you studying in? | Government, Government-aided or Local body |
| class_8_marks_percentage | What percentage did you score in the Class VIII examination? | at least 55 (50 if SC/ST) |
| social_category | Social category | used for the SC/ST relaxation |
| promoted_from_class_8_to_9 | Were you promoted from Class VIII to Class IX without being held back? | must be Yes |
'''
log = Path("data/eligibility_verification.md")
text = log.read_text(encoding="utf-8") if log.exists() else "# Scheme Eligibility Verification Log\n"
if "scheme-008" not in text:
    log.write_text(text.rstrip() + LOG, encoding="utf-8")
    print("eligibility_verification.md: NMMSS section added.")
print("Next: python validate_scheme_data.py && python -m pytest -v")