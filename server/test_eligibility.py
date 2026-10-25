from eligibility import EligibilityProfile, evaluate_scheme


def make_test_scheme(maximum_income=200000):
    """
    Fictional test fixture.
    This is not an actual government scheme.
    """

    return {
        "id": "test-scheme",
        "name": "Fictional Test Scholarship",
        "official_url": "",
        "eligibility_rules": {
            "rules_complete": True,
            "conditions": [
                {
                    "field": "annual_family_income",
                    "operator": "lte",
                    "value": maximum_income,
                    "description": (
                        "Test income must not exceed ₹2,00,000."
                    ),
                    "verified": True,
                    "source_url": "https://example.invalid/test",
                }
            ],
        },
    }


def test_matching_profile_is_eligible():
    profile = EligibilityProfile(
        annual_family_income=150000,
    )

    result = evaluate_scheme(
        make_test_scheme(),
        profile,
    )

    assert result["status"] == "eligible"


def test_exceeding_income_limit_is_not_eligible():
    profile = EligibilityProfile(
        annual_family_income=250000,
    )

    result = evaluate_scheme(
        make_test_scheme(),
        profile,
    )

    assert result["status"] == "not_eligible"


def test_missing_income_is_insufficient_information():
    profile = EligibilityProfile()

    result = evaluate_scheme(
        make_test_scheme(),
        profile,
    )

    assert result["status"] == "insufficient_information"


def test_incomplete_rules_never_confirm_eligibility():
    profile = EligibilityProfile(
        annual_family_income=150000,
    )

    scheme = make_test_scheme()
    scheme["eligibility_rules"]["rules_complete"] = False

    result = evaluate_scheme(scheme, profile)

    assert result["status"] == "insufficient_information"