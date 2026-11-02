import pytest

from eligibility import (
    EligibilityProfile,
    evaluate_scheme,
)


SOURCE = "https://example.gov.in/test-guidelines"


def condition(field, operator, value):
    return {
        "field": field,
        "operator": operator,
        "value": value,
        "description": f"Test rule for {field}",
        "verified": True,
        "source_url": SOURCE,
    }


def make_scheme(rule, rules_complete=True):
    return {
        "id": "test-scheme",
        "name": "Fictional Test Scheme",
        "official_url": SOURCE,
        "eligibility_rules": {
            "rules_complete": rules_complete,
            "source_url": SOURCE,
            "verified_at": "2026-10-25",
            "rule": rule,
        },
    }


def evaluate(rule, profile, rules_complete=True):
    return evaluate_scheme(
        make_scheme(rule, rules_complete),
        EligibilityProfile(**profile),
    )


def test_all_of_passes():
    rule = {
        "all_of": [
            condition("age", "gte", 18),
            condition("annual_family_income", "lte", 200000),
        ]
    }

    result = evaluate(
        rule,
        {
            "age": 21,
            "annual_family_income": 150000,
        },
    )

    assert result["status"] == "eligible"


def test_all_of_fails():
    rule = {
        "all_of": [
            condition("age", "gte", 18),
            condition("annual_family_income", "lte", 200000),
        ]
    }

    result = evaluate(
        rule,
        {
            "age": 21,
            "annual_family_income": 250000,
        },
    )

    assert result["status"] == "not_eligible"


def test_missing_information_is_unknown():
    rule = condition("annual_family_income", "lte", 200000)

    result = evaluate(rule, {})

    assert result["status"] == "insufficient_information"


def test_incomplete_rules_never_confirm_status():
    rule = condition("age", "gte", 18)

    result = evaluate(
        rule,
        {"age": 21},
        rules_complete=False,
    )

    assert result["status"] == "insufficient_information"


def test_any_of_accepts_a_matching_route():
    rule = {
        "any_of": [
            condition("social_category", "eq", "SC"),
            condition("social_category", "eq", "ST"),
        ]
    }

    result = evaluate(
        rule,
        {"social_category": "ST"},
    )

    assert result["status"] == "eligible"


def test_any_of_fails_only_when_all_routes_fail():
    rule = {
        "any_of": [
            condition("social_category", "eq", "SC"),
            condition("social_category", "eq", "ST"),
        ]
    }

    result = evaluate(
        rule,
        {"social_category": "General"},
    )

    assert result["status"] == "not_eligible"


def test_any_of_is_unknown_if_no_route_passes_and_one_is_unknown():
    rule = {
        "any_of": [
            condition("social_category", "eq", "SC"),
            condition("annual_family_income", "lte", 200000),
        ]
    }

    result = evaluate(
        rule,
        {"social_category": "General"},
    )

    assert result["status"] == "insufficient_information"


def test_income_boundary_is_inclusive():
    rule = condition("annual_family_income", "lte", 200000)

    result = evaluate(
        rule,
        {"annual_family_income": 200000},
    )

    assert result["status"] == "eligible"


def test_income_above_boundary_fails():
    rule = condition("annual_family_income", "lte", 200000)

    result = evaluate(
        rule,
        {"annual_family_income": 200001},
    )

    assert result["status"] == "not_eligible"


def test_conditional_requirement_applies():
    rule = {
        "if_then": {
            "if": condition("education_level", "eq", "Postgraduate"),
            "then": condition("occupation", "eq", "Student"),
        }
    }

    result = evaluate(
        rule,
        {
            "education_level": "Postgraduate",
            "occupation": "Student",
        },
    )

    assert result["status"] == "eligible"


def test_conditional_requirement_does_not_apply():
    rule = {
        "if_then": {
            "if": condition("education_level", "eq", "Postgraduate"),
            "then": condition("occupation", "eq", "Student"),
        }
    }

    result = evaluate(
        rule,
        {
            "education_level": "Undergraduate",
            "occupation": "Employed",
        },
    )

    assert result["status"] == "eligible"


def test_unverified_condition_is_not_accepted():
    rule = condition("age", "gte", 18)
    rule["verified"] = False

    result = evaluate(rule, {"age": 21})

    assert result["status"] == "insufficient_information"


def test_invalid_operator_is_not_accepted():
    rule = condition("age", "approximately", 18)

    result = evaluate(rule, {"age": 21})

    assert result["status"] == "insufficient_information"


def test_boolean_cannot_be_used_as_numeric_value():
    rule = condition("age", "gte", 18)

    # Pydantic may coerce input types unless strict validation is
    # enabled. We test the comparison function's behavior separately.
    from eligibility import compare_values

    with pytest.raises(ValueError):
        compare_values(True, "gte", 18)
def test_missing_income_is_unknown_not_ineligible():
    rule = condition("annual_family_income", "lte", 200000)

    result = evaluate(
        rule,
        {"annual_family_income": None},
    )

    assert result["status"] == "insufficient_information"