"""Run from the server/ folder:  python finalize_scheme007.py
Marks scheme-007 complete (rules_complete = true, verified_at = today) after YOU confirm the two open checks."""
import json
from datetime import date
from pathlib import Path

NOTE = ("Rules encoded from the DEPwD scheme 'Scholarships for Students with Disabilities' (effective 1 April 2022, hosted on scholarships.gov.in), "
        "cl. 1.6, 2(i)-(iv), 3, 14.1, 14.6, and checked against the DEPwD revision of 4 September 2025 and the notified institutes list on the review date. "
        "Not encoded as a bar: holding another scholarship (cl. 2(v) lets the student choose one). "
        "Selection is competitive (300 slots, 50% for girls, merit) and is not modelled. Re-check every academic year.")

print("Before continuing, confirm BOTH:")
print("  1. You read the DEPwD guidelines revision dated 4 September 2025 and Rs 8 lakh income / 40% disability / notified institutes are unchanged.")
print("  2. The notified institutes list you rely on is current.")
if input("Have you checked both? Type YES to continue: ").strip() != "YES":
    raise SystemExit("Stopped. Nothing was changed.")
reviewer = input("Your name (for the log): ").strip() or "(not given)"

path = Path("data/schemes.json")
data = json.loads(path.read_text(encoding="utf-8"))
scheme = next((s for s in data if s.get("id") == "scheme-007"), None)
assert scheme is not None, "scheme-007 not found."
rules = scheme["eligibility_rules"]
assert isinstance(rules.get("rule"), dict), "Run apply_scheme007.py first."
today = date.today().isoformat()
rules["rules_complete"] = True
rules["verified_at"] = today
rules["verification_note"] = NOTE
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

log = Path("data/eligibility_verification.md")
text = log.read_text(encoding="utf-8") if log.exists() else ""
log.write_text(text.rstrip() + f"""

### scheme-007 review record
Reviewer: {reviewer}
Review date: {today}
Status: rules_complete = true.
Checked: DEPwD revision of 4 September 2025; notified institutes list.
Not modelled: selection (slots, girls' reservation, merit); holding another scholarship (student may choose).
""", encoding="utf-8")
print(f"scheme-007 marked complete (verified_at = {today}). Now run: python validate_scheme_data.py && python -m pytest -v")