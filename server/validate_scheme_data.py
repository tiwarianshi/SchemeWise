import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "schemes.json"

REQUIRED_FIELDS = {
    "id",
    "name",
    "state",
    "category",
    "beneficiary_group",
    "description",
    "benefits",
    "eligibility",
    "required_documents",
    "official_url",
    "last_verified",
    "is_sample",
    "eligibility_rules",
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

SUPPORTED_OPERATORS = {
    "eq",
    "neq",
    "gte",
    "lte",
    "in",
    "not_in",
}


def validate_expression(expression, path="rule"):
    errors = []

    if not isinstance(expression, dict):
        return [f"{path}: rule must be an object"]

    if "field" in expression:
        if expression.get("field") not in SUPPORTED_FIELDS:
            errors.append(f"{path}: unsupported field")

        if expression.get("operator") not in SUPPORTED_OPERATORS:
            errors.append(f"{path}: unsupported operator")

        if expression.get("verified") is not True:
            errors.append(f"{path}: condition is not verified")

        source = expression.get("source_url", "")

        if not isinstance(source, str) or not source.startswith("https://"):
            errors.append(f"{path}: HTTPS source URL is required")

        if expression.get("value") is None:
            errors.append(f"{path}: expected value is missing")

        return errors

    group_keys = [
        key for key in ("all_of", "any_of", "if_then")
        if key in expression
    ]

    if len(group_keys) != 1:
        return [
            f"{path}: expected exactly one of all_of, any_of, if_then, or a condition"
        ]

    group = group_keys[0]

    if group in {"all_of", "any_of"}:
        children = expression[group]

        if not isinstance(children, list) or not children:
            return [f"{path}.{group}: a non-empty list is required"]

        for index, child in enumerate(children):
            errors.extend(
                validate_expression(
                    child,
                    f"{path}.{group}[{index}]",
                )
            )

    elif group == "if_then":
        conditional = expression[group]

        if not isinstance(conditional, dict):
            return [f"{path}.if_then: must be an object"]

        if "if" not in conditional or "then" not in conditional:
            return [f"{path}.if_then: both if and then are required"]

        errors.extend(
            validate_expression(conditional["if"], f"{path}.if")
        )
        errors.extend(
            validate_expression(conditional["then"], f"{path}.then")
        )

    return errors


def main():
    with DATA_FILE.open(encoding="utf-8") as file:
        schemes = json.load(file)

    if not isinstance(schemes, list):
        raise SystemExit("ERROR: schemes.json must contain a list.")

    errors = []
    seen_ids = set()

    for index, scheme in enumerate(schemes):
        prefix = f"scheme[{index}]"

        if not isinstance(scheme, dict):
            errors.append(f"{prefix}: record must be an object")
            continue

        missing = REQUIRED_FIELDS - scheme.keys()

        if missing:
            errors.append(
                f"{prefix}: missing fields {sorted(missing)}"
            )

        scheme_id = scheme.get("id")

        if scheme_id in seen_ids:
            errors.append(
                f"{prefix}: duplicate scheme ID {scheme_id}"
            )

        seen_ids.add(scheme_id)

        rules = scheme.get("eligibility_rules")

        if not isinstance(rules, dict):
            errors.append(
                f"{prefix}: eligibility_rules must be an object"
            )
            continue

        if rules.get("rules_complete") is True:
            if not isinstance(rules.get("rule"), dict):
                errors.append(
                    f"{prefix}: complete rules require a rule object"
                )
                continue

            errors.extend(
                validate_expression(
                    rules["rule"],
                    f"{prefix}.eligibility_rules.rule",
                )
            )

            verified_at = rules.get("verified_at")

            if not verified_at:
                errors.append(
                    f"{prefix}: complete rules require verified_at"
                )

            source_url = rules.get("source_url", "")

            if (
                not isinstance(source_url, str)
                or not source_url.startswith("https://")
            ):
                errors.append(
                    f"{prefix}: complete rules require an HTTPS source URL"
                )

    if errors:
        print("SCHEME DATA VALIDATION FAILED:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print(f"Validation passed for {len(schemes)} scheme records.")


if __name__ == "__main__":
    main()