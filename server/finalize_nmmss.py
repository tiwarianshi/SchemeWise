"""Run from the server/ folder:  python finalize_nmmss.py

Marks scheme-008 (NMMSS) as complete: rules_complete = true and verified_at = today.
It asks you to confirm first, because only YOU can confirm that you checked the scheme page on NSP.
Changes only scheme-008 and appends a review record to data/eligibility_verification.md."""
import json
from datetime import date
from pathlib import Path

NOTE = ("Rules encoded from the NMMSS Revised Guidelines (dsel.education.gov.in), clauses 1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 6.1, "
        "for a student STARTING the scholarship in Class IX. NSP shows the scheme open for 2026-27. "
        "Not modelled: State/UT reservation and quota norms, and continuation rules (60% in Class X, clear promotion in Classes X and XII). "
        "Guideline clause 4.1 (only one central scholarship) is not encoded because NSP's 2026-27 notice allows one merit-based scheme plus welfare-based schemes. "
        "Re-check the guidelines and the NSP scheme page every academic year.")

print("Before continuing, open scholarships.gov.in, find the National Means-cum-Merit Scholarship Scheme,")
print("and confirm it is open for 2026-27 and its income limit is still Rs 3,50,000.")
if input("Have you checked this? Type YES to continue: ").strip() != "YES":
    raise SystemExit("Stopped. Nothing was changed.")
reviewer = input("Your name (for the log): ").strip() or "(not given)"

path = Path("data/schemes.json")
data = json.loads(path.read_text(encoding="utf-8"))
scheme = next((s for s in data if s.get("id") == "scheme-008"), None)
assert scheme is not None, "scheme-008 not found."
rules = scheme["eligibility_rules"]
assert isinstance(rules.get("rule"), dict), "Run apply_nmmss.py first."

today = date.today().isoformat()
rules["rules_complete"] = True
rules["verified_at"] = today
rules["verification_note"] = NOTE
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

log = Path("data/eligibility_verification.md")
text = log.read_text(encoding="utf-8") if log.exists() else ""
text = text.rstrip() + f"""

### scheme-008 review record
Reviewer: {reviewer}
Review date: {today}
Status: rules_complete = true for a student starting the scholarship in Class IX.
Resolved: scheme open for 2026-27 on NSP; one-scholarship clause not encoded (NSP 2026-27 notice).
Still not modelled: State/UT reservation and quota; continuation rules.
"""
log.write_text(text, encoding="utf-8")
print(f"scheme-008 marked complete (verified_at = {today}). Now run: python validate_scheme_data.py && python -m pytest -v")