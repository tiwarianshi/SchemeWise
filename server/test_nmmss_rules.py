"""Tests for the NMMSS (scheme-008) rule. rules_complete is switched on in memory only."""
import copy
import json
from pathlib import Path

import pytest

from eligibility import SUPPORTED_FIELDS, EligibilityProfile, evaluate_scheme

DATA = Path(__file__).parent / "data" / "schemes.json"

CLEAR = {
    "selected_in_nmmss_state_test": True,
    "annual_family_income": 200000,
    "school_type": "Government school",
    "social_category": "General",
    "class_8_marks_percentage": 60,
    "promoted_from_class_8_to_9": True,
}


@pytest.fixture(scope="module")
def shipped():
    return next(s for s in json.loads(DATA.read_text(encoding="utf-8")) if s["id"] == "scheme-008")


@pytest.fixture
def complete(shipped):
    s = copy.deepcopy(shipped)
    s["eligibility_rules"]["rules_complete"] = True
    return s


def run(scheme, **overrides):
    return evaluate_scheme(scheme, EligibilityProfile(**{**CLEAR, **overrides}))["status"]


def walk(node):
    if "field" in node:
        yield node
    for key in ("all_of", "any_of"):
        for child in node.get(key, []):
            yield from walk(child)


def test_every_leaf_is_verified_sourced_and_supported(shipped):
    for leaf in walk(shipped["eligibility_rules"]["rule"]):
        assert leaf["verified"] is True
        assert leaf["source_url"].startswith("https://")
        assert leaf["field"] in SUPPORTED_FIELDS


def test_clear_profile_is_eligible(complete):
    assert run(complete) == "eligible"


def test_income_boundary(complete):
    assert run(complete, annual_family_income=350000) == "eligible"
    assert run(complete, annual_family_income=350001) == "not_eligible"


@pytest.mark.parametrize("school", ["Government school", "Government-aided school", "Local body school"])
def test_allowed_school_types(complete, school):
    assert run(complete, school_type=school) == "eligible"


@pytest.mark.parametrize("school", [
    "Kendriya Vidyalaya or Jawahar Navodaya Vidyalaya",
    "Residential school run by Centre/State (with boarding and lodging)",
    "Private school", "Other"])
def test_excluded_school_types(complete, school):
    assert run(complete, school_type=school) == "not_eligible"


def test_marks_boundary_general(complete):
    assert run(complete, class_8_marks_percentage=55) == "eligible"
    assert run(complete, class_8_marks_percentage=54.9) == "not_eligible"


@pytest.mark.parametrize("category", ["SC", "ST"])
def test_marks_relaxation_for_sc_st(complete, category):
    assert run(complete, social_category=category, class_8_marks_percentage=50) == "eligible"
    assert run(complete, social_category=category, class_8_marks_percentage=49.9) == "not_eligible"


def test_no_relaxation_for_obc(complete):
    assert run(complete, social_category="OBC", class_8_marks_percentage=52) == "not_eligible"


def test_high_marks_pass_even_if_category_unanswered(complete):
    assert run(complete, social_category=None, class_8_marks_percentage=60) == "eligible"


def test_borderline_marks_need_category(complete):
    assert run(complete, social_category=None, class_8_marks_percentage=52) == "insufficient_information"


def test_not_selected_or_not_promoted(complete):
    assert run(complete, selected_in_nmmss_state_test=False) == "not_eligible"
    assert run(complete, promoted_from_class_8_to_9=False) == "not_eligible"


def test_definite_failure_stands_with_other_answers_missing(complete):
    assert run(complete, selected_in_nmmss_state_test=False, annual_family_income=None) == "not_eligible"


@pytest.mark.parametrize("field", ["selected_in_nmmss_state_test", "annual_family_income", "school_type",
                                   "class_8_marks_percentage", "promoted_from_class_8_to_9"])
def test_unanswered_required_question_is_insufficient(complete, field):
    assert run(complete, **{field: None}) == "insufficient_information"


def test_shipped_record_is_marked_complete_and_gives_a_definitive_answer(shipped):
    assert shipped["eligibility_rules"]["rules_complete"] is True
    assert shipped["eligibility_rules"]["verified_at"]
    assert run(shipped) == "eligible"


def test_profile_rejects_bad_marks():
    for bad in (101, -1, True, "60"):
        with pytest.raises(Exception):
            EligibilityProfile(class_8_marks_percentage=bad)