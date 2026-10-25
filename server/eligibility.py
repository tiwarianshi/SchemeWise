from typing import Any, Literal

from pydantic import BaseModel, Field


class EligibilityProfile(BaseModel):
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


class EligibilityCheckRequest(BaseModel):
    profile: EligibilityProfile


SUPPORTED_OPERATORS = {
    "eq",
    "neq",
    "gte",
    "lte",
    "in",
    "not_in",
}

SUPPORTED_FIELDS = {
    "age",
    "state",
    "annual_family_income",
    "education_level",
    "social_category",
    "disability_status",
    "occupation",
}


def compare_values(
    actual: Any,
    operator: str,
    expected: Any,
) -> bool:
    """
    Compare a user-provided value against a verified scheme rule.
    """

    if operator not in SUPPORTED_OPERATORS:
        raise ValueError(f"Unsupported operator: {operator}")

    if operator in {"in", "not_in"}:
        if not isinstance(expected, list):
            raise ValueError(
                f"Operator '{operator}' requires a list value."
            )

    if operator == "eq":
        return actual == expected

    if operator == "neq":
        return actual != expected

    if operator == "gte":
        return actual >= expected

    if operator == "lte":
        return actual <= expected

    if operator == "in":
        return actual in expected

    if operator == "not_in":
        return actual not in expected

    raise ValueError(f"Unsupported operator: {operator}")


def evaluate_scheme(
    scheme: dict[str, Any],
    profile: EligibilityProfile,
) -> dict[str, Any]:
    """
    Return one of:
      - eligible
      - not_eligible
      - insufficient_information

    A scheme is eligible only when all required conditions
    are verified, satisfied, and declared complete.
    """

    rule_set = scheme.get("eligibility_rules") or {}

    conditions = rule_set.get("conditions", [])

    if not isinstance(conditions, list):
        return {
            "scheme_id": scheme.get("id"),
            "scheme_name": scheme.get("name"),
            "status": "insufficient_information",
            "reasons": [],
            "missing_information": [
                "Eligibility rules have an invalid format."
            ],
            "official_url": scheme.get("official_url", ""),
        }

    profile_data = profile.model_dump()

    reasons = []
    missing_information = []
    failed_condition = False

    for condition in conditions:
        if not isinstance(condition, dict):
            missing_information.append(
                "A scheme eligibility condition has an invalid format."
            )
            continue

        if not condition.get("verified", False):
            missing_information.append(
                condition.get(
                    "description",
                    "An eligibility condition has not been verified.",
                )
            )
            continue

        field = condition.get("field")
        operator = condition.get("operator")
        expected = condition.get("value")

        if field not in SUPPORTED_FIELDS:
            missing_information.append(
                f"Unsupported eligibility field: {field}"
            )
            continue

        if operator not in SUPPORTED_OPERATORS:
            missing_information.append(
                f"Unsupported eligibility operator: {operator}"
            )
            continue

        if "value" not in condition or expected is None:
            missing_information.append(
                condition.get(
                    "description",
                    f"The verified value for '{field}' is missing.",
                )
            )
            continue

        actual = profile_data.get(field)

        if actual is None:
            missing_information.append(
                f"Please provide your {field.replace('_', ' ')}."
            )
            continue

        try:
            matched = compare_values(
                actual,
                operator,
                expected,
            )
        except (TypeError, ValueError):
            missing_information.append(
                condition.get(
                    "description",
                    f"The rule for '{field}' could not be evaluated.",
                )
            )
            continue

        if matched:
            reasons.append(
                condition.get(
                    "description",
                    f"The condition for '{field}' is satisfied.",
                )
            )
        else:
            failed_condition = True
            reasons.append(
                condition.get(
                    "description",
                    f"The condition for '{field}' is not satisfied.",
                )
            )

    # A confirmed failed mandatory condition is enough to say
    # the applicant does not meet that scheme's rules.
    if failed_condition:
        status = "not_eligible"

    # Missing, unverified, or incomplete rules must never be
    # treated as proof that the applicant qualifies.
    elif (
        missing_information
        or not rule_set.get("rules_complete", False)
        or not conditions
    ):
        status = "insufficient_information"

        if not rule_set.get("rules_complete", False):
            missing_information.append(
                "The scheme's eligibility rules have not been "
                "fully verified."
            )

        if not conditions:
            missing_information.append(
                "No verified eligibility conditions are available."
            )

    else:
        status = "eligible"

    return {
        "scheme_id": scheme.get("id"),
        "scheme_name": scheme.get("name"),
        "status": status,
        "reasons": reasons,
        "missing_information": list(dict.fromkeys(missing_information)),
        "official_url": scheme.get("official_url", ""),
    }