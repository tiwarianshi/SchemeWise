# Scheme Eligibility Verification Log

## Scheme ID: scheme-009 — PM-KISAN

Source: PM-KISAN Operational Guidelines, revised as on 29.03.2020 (pmkisan.gov.in).
Also read: the 2019 FAQ PDF. It is OLDER than the guidelines: it still says "upto 2 hectare",
which the revised guidelines no longer contain. The guidelines were used wherever they differ.

- [x] Confirm the definition of an eligible farmer family (cl. 3: husband, wife, minor children who own cultivable land per land records)
- [x] Confirm landholding / land-record conditions (cl. 3, 5.1, 5.2: names in land records; cut-off 01.02.2019; succession on death excepted)
- [x] Record every exclusion category (cl. 4.1(a), 4.1(b)(i)-(vi), 4.1(c))
- [x] Check exceptions to exclusions (Multi Tasking Staff / Class IV / Group D excepted for employees and pensioners)
- [x] Check land-record date and transfers (cl. 5.3.3: buyers/donees after 01.02.2019 are not eligible)
- [ ] Check amendments / clarifications issued after 29.03.2020 (portal pages: "Amendment in Operational Guidelines", "Clarification to Operational Guidelines")
- [ ] Confirm current registration / eKYC rules (not modelled as eligibility conditions)
- [ ] State-specific mechanisms (North-East states, Jharkhand: cl. 5.5-5.6) — NOT modelled
- [x] Map every condition to a supported profile field
- [ ] Run validate_scheme_data.py and pytest
- [ ] Manual check of API results

Status: INCOMPLETE (rules_complete = false)
Reviewer:
Review date:
Outstanding questions: see the unchecked items above.

## Exact question wording (use this in the frontend)
"Family" always means husband, wife and minor children.

| Profile field | Ask the user | Rule |
|---|---|---|
| has_eligible_landholding | Does your family own cultivable land recorded in the State/UT land records, with ownership held on or before 1 Feb 2019 or inherited after the owner's death? | must be Yes |
| is_institutional_landholder | Is the land held by an institution rather than a family? | must be No |
| has_constitutional_post_exclusion_in_family | Is any family member a former or present holder of a constitutional post? | must be No |
| has_elected_official_exclusion_in_family | Is any family member a former or present minister, MP, MLA, MLC, mayor of a municipal corporation or chairperson of a district panchayat? | must be No |
| has_excluded_government_employee_in_family | Is any family member a serving or retired officer/employee of the Central or State government, a government PSE or autonomous body, or a regular local-body employee? Do NOT count Multi Tasking Staff, Class IV or Group D employees. | must be No |
| has_excluded_pensioner_in_family | Does any family member draw a pension of Rs 10,000 or more per month? Do NOT count retired Multi Tasking Staff, Class IV or Group D employees. | must be No |
| paid_income_tax_last_assessment_year_in_family | Did any family member pay income tax in the last assessment year? | must be No |
| has_practicing_registered_professional_in_family | Is any family member a doctor, engineer, lawyer, chartered accountant or architect registered with a professional body and practising? | must be No |
| is_nri_family | Is the family Non-Resident Indian under the Income Tax Act? (Applies to new applicants only — cl. 4.1(c).) | must be No |

If the user does not know an answer, send null — never false.