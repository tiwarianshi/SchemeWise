"""Run from the server/ folder:  python cleanup_pmkisan.py
Replaces the OLD verification_note on scheme-009 (it still says 'Before setting rules_complete to true...').
Changes nothing else. Safe to re-run."""
import json
from pathlib import Path

NOTE = ("Rules encoded from the PM-KISAN Operational Guidelines (revised as on 29.03.2020), clauses 3, 4.1, 4.1(c), 5.2-5.3. "
        "rules_complete was set to true on the verified_at date by the project owner. "
        "Re-check the portal's 'Amendment in Operational Guidelines' and 'Clarification' pages whenever the guidelines change. "
        "eKYC, Aadhaar and bank-account requirements are registration steps, not modelled here; "
        "State-specific procedures (North-East states, Jharkhand) are not modelled.")

path = Path("data/schemes.json")
data = json.loads(path.read_text(encoding="utf-8"))
scheme = next((s for s in data if s.get("id") == "scheme-009"), None)
assert scheme is not None, "scheme-009 not found."
scheme["eligibility_rules"]["verification_note"] = NOTE
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("scheme-009 verification_note updated.")