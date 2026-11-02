"""Tests for scheme-007 (Top Class Education scholarship for students with disabilities).
rules_complete is switched on in memory only, so the tests work before and after finalize_scheme007.py."""
import copy
import json
from pathlib import Path

import pytest

from eligibility import SUPPORTED_FIELDS, EligibilityProfile, evaluate_scheme

DATA = Path(__file__).parent / "data" / "schemes.json"

CLEAR = {
    "is_indian_national": True,
    "disability_percentage": 50,
    "has_valid_disability_certificate": True,
    "annual_family_income": 500000,
    "education_level": "Undergraduate",
    "studying_in_notified_institute": True,
    "is_regular_full_time_course": True,
    "has_received_top_class_award_before": False,
    "exceeds_disabled_children_limit_per_parents": False,
    "is_repeating_class": False,
}


@pytest.fixture(scope="module")
def shipped():
    return next(s for s in json.loads(DATA.read_text(encoding="utf-8")) if s["id"] == "scheme-007")


@pytest.fixture
def complete(shipped):
    s = copy.deepcopy(shipped)
    s["eligibility_rules"]["rules_complete"] = True
    return s


def run(scheme, **overrides):
    return evaluate_scheme(scheme, EligibilityProfile(**{**CLEAR, **overrides}))["status"]


def test_every_leaf_is_verified_sourced_and_supported(shipped):
    for leaf in shipped["eligibility_rules"]["rule"]["all_of"]:
        assert leaf["verified"] is True
        assert leaf["source_url"].startswith("https://")
        assert leaf["field"] in SUPPORTED_FIELDS


def test_clear_profile_is_eligible(complete):
    assert run(complete) == "eligible"


def test_disability_boundary(complete):
    assert run(complete, disability_percentage=40) == "eligible"
    assert run(complete, disability_percentage=39.9) == "not_eligible"


def test_income_boundary(complete):
    assert run(complete, annual_family_income=800000) == "eligible"
    assert run(complete, annual_family_income=800001) == "not_eligible"


@pytest.mark.parametrize("level", ["Diploma", "Undergraduate", "Postgraduate"])
def test_covered_course_levels(complete, level):
    assert run(complete, education_level=level) == "eligible"


@pytest.mark.parametrize("level", ["School", "Doctoral", "Other"])
def test_uncovered_course_levels(complete, level):
    assert run(complete, education_level=level) == "not_eligible"


@pytest.mark.parametrize("field,bad_value", [
    ("is_indian_national", False),
    ("has_valid_disability_certificate", False),
    ("studying_in_notified_institute", False),
    ("is_regular_full_time_course", False),
    ("has_received_top_class_award_before", True),
    ("exceeds_disabled_children_limit_per_parents", True),
    ("is_repeating_class", True),
])
def test_each_failed_condition_is_not_eligible(complete, field, bad_value):
    assert run(complete, **{field: bad_value}) == "not_eligible"


@pytest.mark.parametrize("field", list(CLEAR))
def test_unanswered_question_is_insufficient(complete, field):
    assert run(complete, **{field: None}) == "insufficient_information"


def test_definite_failure_stands_with_other_answers_missing(complete):
    assert run(complete, is_indian_national=False, annual_family_income=None) == "not_eligible"


def test_shipped_record_behaviour_matches_completeness(shipped):
    expected = "eligible" if shipped["eligibility_rules"]["rules_complete"] is True else "insufficient_information"
    assert run(shipped) == expected


@pytest.mark.parametrize("bad", [101, -1, True, "50"])
def test_profile_rejects_bad_disability_percentage(bad):
    with pytest.raises(Exception):
        EligibilityProfile(disability_percentage=bad)