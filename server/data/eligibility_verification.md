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

### scheme-008 review record
Reviewer: Pragati
Review date: 2026-10-29
Status: rules_complete = true for a student starting the scholarship in Class IX.
Resolved: scheme open for 2026-27 on NSP; one-scholarship clause not encoded (NSP 2026-27 notice).
Still not modelled: State/UT reservation and quota; continuation rules.

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

### scheme-007 review record
Reviewer: Pragati
Review date: 2026-10-29
Status: rules_complete = true.
Checked: DEPwD revision of 4 September 2025; notified institutes list.
Not modelled: selection (slots, girls' reservation, merit); holding another scholarship (student may choose).
