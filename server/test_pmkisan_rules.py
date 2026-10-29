"""Tests for the PM-KISAN (scheme-009) rule. Uses the real schemes.json,
with rules_complete switched on in memory only, so the test works before you flip the flag."""
import copy
import json
from pathlib import Path

import pytest

from eligibility import SUPPORTED_FIELDS, EligibilityProfile, evaluate_scheme

DATA = Path(__file__).parent / "data" / "schemes.json"

CLEAR = {
    "has_eligible_landholding": True,
    "is_institutional_landholder": False,
    "has_constitutional_post_exclusion_in_family": False,
    "has_elected_official_exclusion_in_family": False,
    "has_excluded_government_employee_in_family": False,
    "has_excluded_pensioner_in_family": False,
    "paid_income_tax_last_assessment_year_in_family": False,
    "has_practicing_registered_professional_in_family": False,
    "is_nri_family": False,
}


@pytest.fixture(scope="module")
def shipped():
    return next(s for s in json.loads(DATA.read_text(encoding="utf-8")) if s["id"] == "scheme-009")


@pytest.fixture
def complete(shipped):
    s = copy.deepcopy(shipped)
    s["eligibility_rules"]["rules_complete"] = True
    return s


def run(scheme, **overrides):
    return evaluate_scheme(scheme, EligibilityProfile(**{**CLEAR, **overrides}))


def test_every_leaf_is_verified_sourced_and_supported(shipped):
    leaves = shipped["eligibility_rules"]["rule"]["all_of"]
    assert leaves
    for leaf in leaves:
        assert leaf["verified"] is True
        assert leaf["source_url"].startswith("https://")
        assert leaf["field"] in SUPPORTED_FIELDS


def test_all_conditions_met_is_eligible(complete):
    assert run(complete)["status"] == "eligible"


def test_no_landholding_is_not_eligible(complete):
    assert run(complete, has_eligible_landholding=False)["status"] == "not_eligible"


@pytest.mark.parametrize("field", [f for f in CLEAR if f != "has_eligible_landholding"])
def test_each_exclusion_makes_family_not_eligible(complete, field):
    assert run(complete, **{field: True})["status"] == "not_eligible"


@pytest.mark.parametrize("field", list(CLEAR))
def test_unanswered_question_is_insufficient_information(complete, field):
    result = evaluate_scheme(complete, EligibilityProfile(**{**CLEAR, field: None}))
    assert result["status"] == "insufficient_information"
    assert result["missing_information"]


def test_shipped_record_is_marked_complete_and_gives_a_definitive_answer(shipped):
    assert shipped["eligibility_rules"]["rules_complete"] is True
    assert shipped["eligibility_rules"]["verified_at"]
    assert run(shipped)["status"] == "eligible"


def test_exclusion_stands_even_if_other_answers_are_missing(complete):
    result = evaluate_scheme(
        complete,
        EligibilityProfile(is_institutional_landholder=True),
    )
    assert result["status"] == "not_eligible"


def test_profile_rejects_non_boolean_answers():
    with pytest.raises(Exception):
        EligibilityProfile(is_nri_family="no")