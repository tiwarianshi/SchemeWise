"""Run from the server/ folder:  python apply_scheme007.py

1. eligibility.py: adds 8 profile fields for scheme-007 and registers them.
2. data/schemes.json: updates ONLY scheme-007 (benefits, eligibility text, required_documents, eligibility_rules).
3. data/eligibility_verification.md: appends the scheme-007 section.
Safe to re-run. rules_complete stays false and verified_at stays null until you run finalize_scheme007.py."""
import json
from pathlib import Path

NEW_BOOL = [
    "is_indian_national",
    "has_valid_disability_certificate",
    "studying_in_notified_institute",
    "is_regular_full_time_course",
    "has_received_top_class_award_before",
    "exceeds_disabled_children_limit_per_parents",
    "is_repeating_class",
]
ALL_NEW = ["disability_percentage"] + NEW_BOOL

# ---------- 1. eligibility.py ----------
path = Path("eligibility.py")
src = path.read_text(encoding="utf-8")

if "disability_percentage" not in src:
    anchor = "    class_8_marks_percentage: float | None = Field(default=None, ge=0, le=100)\n"
    assert src.count(anchor) == 1, "Run apply_nmmss.py first (class_8_marks_percentage not found)."
    block = ("\n    # Scheme-007 facts (Top Class Education scholarship for students with disabilities).\n"
             "    disability_percentage: float | None = Field(default=None, ge=0, le=100)\n")
    block += "".join(f"    {name}: StrictBool | None = None\n" for name in NEW_BOOL)
    src = src.replace(anchor, anchor + block, 1)

    vanchor = '    @field_validator("class_8_marks_percentage", mode="before")'
    assert src.count(vanchor) == 1, "Could not find the class_8_marks_percentage validator."
    validator = '''    @field_validator("disability_percentage", mode="before")
    @classmethod
    def validate_disability_percentage(cls, value):
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Disability percentage must be a number.")

        if not math.isfinite(value):
            raise ValueError("Disability percentage must be finite.")

        return float(value)

'''
    src = src.replace(vanchor, validator + vanchor, 1)

    sanchor = '    "class_8_marks_percentage",\n}'
    assert src.count(sanchor) == 1, "Could not find the end of SUPPORTED_FIELDS."
    src = src.replace(sanchor, '    "class_8_marks_percentage",\n' + "".join(f'    "{n}",\n' for n in ALL_NEW) + "}", 1)
    path.write_text(src, encoding="utf-8")
    print("eligibility.py: scheme-007 fields added.")
else:
    print("eligibility.py: scheme-007 fields already present; skipped.")

# ---------- 2. schemes.json ----------
URL = "https://scholarships.gov.in/public/schemeGuidelines/DEPDGuidelines.pdf"

def leaf(field, op, value, description):
    return {"field": field, "operator": op, "value": value,
            "description": description, "verified": True, "source_url": URL}

RULE = {"all_of": [
    leaf("is_indian_national", "eq", True,
         "The scholarship is open only to Indian nationals."),
    leaf("disability_percentage", "gte", 40,
         "The student must have a benchmark disability of 40% or more as defined in the Rights of Persons with Disabilities Act, 2016."),
    leaf("has_valid_disability_certificate", "eq", True,
         "The student must hold a valid disability certificate issued by the competent authority."),
    leaf("annual_family_income", "lte", 800000,
         "Parents'/guardians' income from all sources must not exceed Rs 8,00,000 per year."),
    leaf("education_level", "in", ["Diploma", "Undergraduate", "Postgraduate"],
         "The student must be pursuing a graduate or post-graduate degree or diploma course."),
    leaf("studying_in_notified_institute", "eq", True,
         "The institute must be on the list of Institutes of Excellence notified by DEPwD for this scholarship."),
    leaf("is_regular_full_time_course", "eq", True,
         "Distance-learning, part-time and week-end courses are not covered."),
    leaf("has_received_top_class_award_before", "eq", False,
         "The award is one-time: a student who has already received it cannot be awarded again."),
    leaf("exceeds_disabled_children_limit_per_parents", "eq", False,
         "Not more than two children with disabilities of the same parents can receive benefits under the scheme (twins of the second child are also covered)."),
    leaf("is_repeating_class", "eq", False,
         "The scholarship is not available for a class the student is repeating."),
]}

NOTE = ("Rules encoded from the DEPwD scheme 'Scholarships for Students with Disabilities' (effective 1 April 2022, hosted on scholarships.gov.in), "
        "cl. 1.6, 2(i)-(iv), 3, 14.1, 14.6. Before setting rules_complete to true: (1) check the DEPwD guidelines revision dated 4 September 2025 for changes; "
        "(2) confirm the notified institutes list. NOT encoded as a bar: holding another scholarship (cl. 2(v) lets the student choose one). "
        "Selection is competitive (300 slots, 50% for girls, merit) and is not modelled. See data/eligibility_verification.md.")

sp = Path("data/schemes.json")
data = json.loads(sp.read_text(encoding="utf-8"))
target = next((s for s in data if s.get("id") == "scheme-007"), None)
assert target is not None, "scheme-007 not found in data/schemes.json."
target["benefits"] = [
    "Reimbursement of tuition and non-refundable fees, up to the cap in the current guidelines.",
    "Maintenance allowance: Rs 3,000 per month for hostellers, Rs 1,500 per month for day scholars.",
    "Special disability allowance: Rs 2,000 per month.",
    "Books and stationery: Rs 5,000 per year.",
    "One-time grants: Rs 45,000 for a computer or laptop and Rs 30,000 for aids and assistive devices.",
]
target["eligibility"] = [
    "Indian national with a benchmark disability (40% or more) and a valid disability certificate.",
    "Parents'/guardians' income from all sources not more than Rs 8,00,000 per year.",
    "Studying a regular, full-time graduate or post-graduate degree or diploma course at an institute notified by DEPwD.",
    "Not previously awarded this scholarship, not repeating a class, and not more than two children with disabilities of the same parents benefiting (twins excepted).",
    "Selection is competitive: 300 slots a year, 50% reserved for girls, based on marks in the qualifying examination.",
]
target["required_documents"] = [
    "Photograph",
    "Proof of age",
    "Disability certificate (UDID card where available)",
    "Income certificate of parent or guardian",
    "Tuition fee receipt",
    "Last academic qualification certificate",
    "Aadhaar number or enrolment ID",
]
target["eligibility_rules"] = {
    "rules_complete": False,
    "source_url": URL,
    "verified_at": None,
    "rule": RULE,
    "verification_note": NOTE,
}
sp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("scheme-007 updated (rules_complete is still false).")

# ---------- 3. verification log ----------
LOG = '''

## Scheme ID: scheme-007 - Top Class Education Scholarship for Students with Disabilities

Source: DEPwD "Scheme of Scholarship for Students with Disabilities" (effective 1 April 2022), hosted at
scholarships.gov.in/public/schemeGuidelines/DEPDGuidelines.pdf - cl. 1.6, 2, 3, 4, 14.
Also read: the DEPwD "easy-read" Top Class page. It agrees on the main conditions but says tuition up to Rs 1.90 lakh while the PDF says Rs 2.00 lakh,
so the amount was left out of the data. The uploaded National Policy for Persons with Disabilities (2006) contains no scholarship rules.

- [x] Nationality (cl. 2(i)): Indian nationals only
- [x] Disability (cl. 1.6, 2(ii)): benchmark disability 40% or more, valid certificate
- [x] Income (cl. 3): parents/guardians income from all sources up to Rs 8,00,000 per year
- [x] Course and institute (cl. 14.1, 14.6): graduate / post-graduate degree or diploma in DEPwD-notified institutes; no distance, part-time or week-end courses
- [x] One-time award (cl. 14.6)
- [x] Children limit (cl. 2(iii)): max two children with disabilities of the same parents; twin proviso
- [x] Repeating a class (cl. 2(iv)): no scholarship for a repeated class
- [x] Other scholarships (cl. 2(v)): student may choose one - NOT encoded as a bar
- [x] Map every condition to a supported profile field
- [ ] Check the DEPwD guidelines revision dated 4 September 2025
- [ ] Check the notified institutes list is current (Annexure I of the 2022 PDF had 240 institutes)
- [ ] Selection (300 slots, 50% girls, state-wise slots, merit) - NOT modelled
- [ ] Run validate_scheme_data.py and pytest; manual API check

Status: INCOMPLETE (rules_complete = false)

### Exact question wording (frontend)
| Profile field | Ask the user | Rule |
|---|---|---|
| is_indian_national | Are you an Indian national? | must be Yes |
| disability_percentage | What is the disability percentage on your disability certificate or UDID card? | at least 40 |
| has_valid_disability_certificate | Do you have a valid disability certificate issued by the competent authority? | must be Yes |
| annual_family_income | Annual family income (parents/guardians, all sources) | at most 800000 |
| education_level | Education level | Diploma, Undergraduate or Postgraduate |
| studying_in_notified_institute | Is your institute on the list of Institutes of Excellence notified by DEPwD for this scholarship? | must be Yes |
| is_regular_full_time_course | Is your course regular and full-time (not distance, part-time or week-end)? | must be Yes |
| has_received_top_class_award_before | Have you already received the Top Class Education scholarship before? | must be No |
| exceeds_disabled_children_limit_per_parents | Do two or more of your brothers or sisters with disabilities (same parents) already receive benefits under the Scholarships for Students with Disabilities scheme? If you are a twin of the second such child, answer No. | must be No |
| is_repeating_class | Are you repeating a class or year that you have already studied? | must be No |
'''
log = Path("data/eligibility_verification.md")
text = log.read_text(encoding="utf-8") if log.exists() else "# Scheme Eligibility Verification Log\n"
if "scheme-007" not in text:
    log.write_text(text.rstrip() + LOG, encoding="utf-8")
    print("eligibility_verification.md: scheme-007 section added.")
print("Next: python validate_scheme_data.py && python -m pytest -v")