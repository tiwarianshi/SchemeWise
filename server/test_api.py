from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_scheme_listing_endpoint():
    response = client.get("/api/schemes")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "schemes" in data
    assert isinstance(data["schemes"], list)


def test_eligibility_endpoint_returns_expected_structure(monkeypatch):
    test_scheme = {
        "id": "test-scheme",
        "name": "Fictional Test Scheme",
        "state": "All India",
        "category": "Education",
        "beneficiary_group": "Students",
        "description": "A fictional testing record.",
        "benefits": [],
        "eligibility": [],
        "required_documents": [],
        "official_url": "https://example.gov.in/test",
        "last_verified": "2026-10-25",
        "is_sample": True,
        "eligibility_rules": {
            "rules_complete": True,
            "source_url": "https://example.gov.in/test",
            "verified_at": "2026-10-25",
            "rule": {
                "field": "age",
                "operator": "gte",
                "value": 18,
                "description": "Test applicant must be at least 18.",
                "verified": True,
                "source_url": "https://example.gov.in/test",
            },
        },
    }

    monkeypatch.setattr(
        main,
        "load_schemes",
        lambda: [test_scheme],
    )

    response = client.post(
        "/api/eligibility/check",
        json={
            "profile": {
                "age": 21,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert data["summary"]["eligible"] == 1
    assert data["results"][0]["status"] == "eligible"


def test_eligibility_endpoint_rejects_invalid_age():
    response = client.post(
        "/api/eligibility/check",
        json={
            "profile": {
                "age": 150,
            }
        },
    )

    assert response.status_code == 422


def test_eligibility_endpoint_rejects_unknown_profile_field():
    response = client.post(
        "/api/eligibility/check",
        json={
            "profile": {
                "age": 21,
                "unknown_field": "test",
            }
        },
    )

    assert response.status_code == 422