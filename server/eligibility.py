from typing import Any, Literal
import math

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

class EligibilityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int | None = Field(default=None, ge=0, le=120)

    state: str | None = None

    annual_family_income: float | None = Field(
        default=None,
        ge=0,
    )

    education_level: str | None = None

    social_category: str | None = None

    disability_status: bool | None = None

    occupation: str | None = None

    # PM-KISAN facts (see data/eligibility_verification.md for exact question wording).
    has_eligible_landholding: StrictBool | None = None
    is_institutional_landholder: StrictBool | None = None
    has_constitutional_post_exclusion_in_family: StrictBool | None = None
    has_elected_official_exclusion_in_family: StrictBool | None = None
    has_excluded_government_employee_in_family: StrictBool | None = None
    has_excluded_pensioner_in_family: StrictBool | None = None
    paid_income_tax_last_assessment_year_in_family: StrictBool | None = None
    has_practicing_registered_professional_in_family: StrictBool | None = None
    is_nri_family: StrictBool | None = None

    @field_validator("age", mode="before")
    @classmethod
    def validate_age(cls, value):
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Age must be a whole number.")

        return value

    @field_validator("annual_family_income", mode="before")
    @classmethod
    def validate_income(cls, value):
        if value is None:
            return None

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
        ):
            raise ValueError(
                "Annual family income must be a number."
            )

        if not math.isfinite(value):
            raise ValueError(
                "Annual family income must be finite."
            )

        return float(value)


class EligibilityCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: EligibilityProfile


SUPPORTED_FIELDS = {
    "age",
    "state",
    "annual_family_income",
    "education_level",
    "social_category",
    "disability_status",
    "occupation",
    "has_eligible_landholding",
    "is_institutional_landholder",
    "has_constitutional_post_exclusion_in_family",
    "has_elected_official_exclusion_in_family",
    "has_excluded_government_employee_in_family",
    "has_excluded_pensioner_in_family",
    "paid_income_tax_last_assessment_year_in_family",
    "has_practicing_registered_professional_in_family",
    "is_nri_family",
}

SUPPORTED_OPERATORS = {
    "eq",
    "neq",
    "gte",
    "lte",
    "in",
    "not_in",
}

MAX_RULE_DEPTH = 12
MAX_RULE_NODES = 200


def normalize(value: Any) -> Any:
    """Normalize strings for case-insensitive comparison."""
    if isinstance(value, str):
        return value.strip().casefold()

    return value


def compare_values(
    actual: Any,
    operator: str,
    expected: Any,
) -> bool:
    """Compare compatible, validated values."""

    if operator in {"eq", "neq"}:
        if isinstance(actual, bool) != isinstance(expected, bool):
            raise ValueError("Incompatible Boolean value.")

        left = normalize(actual)
        right = normalize(expected)

        return left == right if operator == "eq" else left != right

    if operator in {"gte", "lte"}:
        if (
            isinstance(actual, bool)
            or isinstance(expected, bool)
            or not isinstance(actual, (int, float))
            or not isinstance(expected, (int, float))
        ):
            raise ValueError("Numeric values are required.")

        return (
            actual >= expected
            if operator == "gte"
            else actual <= expected
        )

    if operator in {"in", "not_in"}:
        if not isinstance(expected, list) or not expected:
            raise ValueError("A non-empty list is required.")

        left = normalize(actual)
        right = [normalize(item) for item in expected]

        matched = left in right

        return matched if operator == "in" else not matched

    raise ValueError(f"Unsupported operator: {operator}")


def evaluate_expression(
    expression: Any,
    profile: dict[str, Any],
    depth: int = 0,
    budget: list[int] | None = None,
) -> dict[str, Any]:
    """
    Evaluate a rule expression.

    Returns:
        value: True, False, or None
        reasons: list of human-readable explanations
        missing: list of unresolved information
    """

    if budget is None:
        budget = [0]

    budget[0] += 1

    if depth > MAX_RULE_DEPTH or budget[0] > MAX_RULE_NODES:
        return {
            "value": None,
            "reasons": [],
            "missing": ["The eligibility rule structure is too complex."],
        }

    if not isinstance(expression, dict):
        return {
            "value": None,
            "reasons": [],
            "missing": ["An eligibility rule has an invalid format."],
        }

    # A leaf condition.
    if "field" in expression:
        field = expression.get("field")
        operator = expression.get("operator")
        expected = expression.get("value")
        description = expression.get("description")

        if expression.get("verified") is not True:
            return {
                "value": None,
                "reasons": [],
                "missing": [
                    description or "An eligibility condition is unverified."
                ],
            }

        source_url = expression.get("source_url")

        if (
            not isinstance(source_url, str)
            or not source_url.startswith("https://")
        ):
            return {
                "value": None,
                "reasons": [],
                "missing": [
                    description or "A verified condition has no valid source."
                ],
            }

        if field not in SUPPORTED_FIELDS:
            return {
                "value": None,
                "reasons": [],
                "missing": [f"Unsupported eligibility field: {field}"],
            }

        if operator not in SUPPORTED_OPERATORS:
            return {
                "value": None,
                "reasons": [],
                "missing": [f"Unsupported operator: {operator}"],
            }

        if "value" not in expression or expected is None:
            return {
                "value": None,
                "reasons": [],
                "missing": [
                    description or f"The rule value for '{field}' is missing."
                ],
            }

        actual = profile.get(field)

        if actual is None:
            return {
                "value": None,
                "reasons": [],
                "missing": [
                    f"Please provide your {field.replace('_', ' ')}."
                ],
            }

        try:
            matched = compare_values(actual, operator, expected)
        except (TypeError, ValueError):
            return {
                "value": None,
                "reasons": [],
                "missing": [
                    description or f"The rule for '{field}' could not be evaluated."
                ],
            }

        return {
            "value": matched,
            "reasons": [
                description
                or f"The condition for '{field}' "
                + ("is satisfied." if matched else "is not satisfied.")
            ],
            "missing": [],
        }

    # An alternative route: any child may pass.
    if "any_of" in expression:
        children = expression["any_of"]

        if not isinstance(children, list) or not children:
            return {
                "value": None,
                "reasons": [],
                "missing": ["The alternative eligibility routes are incomplete."],
            }

        results = [
            evaluate_expression(child, profile, depth + 1, budget)
            for child in children
        ]

        if any(result["value"] is True for result in results):
            value = True
        elif all(result["value"] is False for result in results):
            value = False
        else:
            value = None

        return {
            "value": value,
            "reasons": [
                reason
                for result in results
                for reason in result["reasons"]
            ],
            "missing": [
                item
                for result in results
                for item in result["missing"]
            ],
        }

    # A mandatory group: every child must pass.
    if "all_of" in expression:
        children = expression["all_of"]

        if not isinstance(children, list) or not children:
            return {
                "value": None,
                "reasons": [],
                "missing": ["The mandatory eligibility rules are incomplete."],
            }

        results = [
            evaluate_expression(child, profile, depth + 1, budget)
            for child in children
        ]

        if any(result["value"] is False for result in results):
            value = False
        elif all(result["value"] is True for result in results):
            value = True
        else:
            value = None

        return {
            "value": value,
            "reasons": [
                reason
                for result in results
                for reason in result["reasons"]
            ],
            "missing": [
                item
                for result in results
                for item in result["missing"]
            ],
        }

    # A conditional requirement:
    # if the prerequisite is false, the dependent rule does not apply.
    if "if_then" in expression:
        conditional = expression["if_then"]

        if (
            not isinstance(conditional, dict)
            or "if" not in conditional
            or "then" not in conditional
        ):
            return {
                "value": None,
                "reasons": [],
                "missing": ["The conditional eligibility rule is incomplete."],
            }

        prerequisite = evaluate_expression(
            conditional["if"],
            profile,
            depth + 1,
            budget,
        )

        if prerequisite["value"] is False:
            return {
                "value": True,
                "reasons": [
                    "The conditional requirement does not apply."
                ],
                "missing": [],
            }

        if prerequisite["value"] is None:
            return {
                "value": None,
                "reasons": prerequisite["reasons"],
                "missing": prerequisite["missing"],
            }

        dependent = evaluate_expression(
            conditional["then"],
            profile,
            depth + 1,
            budget,
        )

        return {
            "value": dependent["value"],
            "reasons": prerequisite["reasons"] + dependent["reasons"],
            "missing": prerequisite["missing"] + dependent["missing"],
        }

    return {
        "value": None,
        "reasons": [],
        "missing": [
            "The rule must contain a condition, all_of, any_of, or if_then."
        ],
    }


def evaluate_scheme(
    scheme: dict[str, Any],
    profile: EligibilityProfile,
) -> dict[str, Any]:
    """Produce a conservative, explainable scheme assessment."""

    rule_set = scheme.get("eligibility_rules")

    reasons: list[str] = []
    missing: list[str] = []

    complete = (
        isinstance(rule_set, dict)
        and rule_set.get("rules_complete") is True
    )

    if not isinstance(rule_set, dict):
        rule_set = {}

    expression = rule_set.get("rule")

    if not complete:
        missing.append(
            "The scheme's complete eligibility rules have not been verified."
        )

    if not isinstance(expression, dict):
        missing.append("No structured eligibility rules are available.")
        evaluation_value = None
    else:
        result = evaluate_expression(
            expression,
            profile.model_dump(),
        )

        evaluation_value = result["value"]
        reasons.extend(result["reasons"])
        missing.extend(result["missing"])

    if not complete or missing or evaluation_value is None:
        status = "insufficient_information"
    elif evaluation_value is True:
        status = "eligible"
    else:
        status = "not_eligible"

    return {
        "scheme_id": scheme.get("id"),
        "scheme_name": scheme.get("name"),
        "status": status,
        "reasons": list(dict.fromkeys(reasons)),
        "missing_information": list(dict.fromkeys(missing)),
        "official_url": scheme.get("official_url", ""),
    }