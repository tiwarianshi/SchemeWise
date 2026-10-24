
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SchemeWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).parent / "data" / "schemes.json"


def load_schemes():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Scheme data must be a JSON list.")

        return data

    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to load scheme data.",
        ) from error


@app.get("/")
def home():
    return {"message": "SchemeWise API is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/schemes")
def get_schemes(
    search: str = Query(default="", max_length=100),
    state: str = Query(default="", max_length=100),
    category: str = Query(default="", max_length=100),
    beneficiary_group: str = Query(default="", max_length=100),
):
    schemes = load_schemes()

    filtered_schemes = []

    for scheme in schemes:
        # Search across the main descriptive fields.
        searchable_text = " ".join(
            [
                scheme.get("name", ""),
                scheme.get("description", ""),
                scheme.get("state", ""),
                scheme.get("category", ""),
                scheme.get("beneficiary_group", ""),
                " ".join(scheme.get("benefits", [])),
                " ".join(scheme.get("eligibility", [])),
            ]
        ).casefold()

        if search.strip().casefold() not in searchable_text:
            continue

        if (
            state.strip()
            and scheme.get("state", "").casefold()
            != state.strip().casefold()
        ):
            continue

        if (
            category.strip()
            and scheme.get("category", "").casefold()
            != category.strip().casefold()
        ):
            continue

        if (
            beneficiary_group.strip()
            and scheme.get("beneficiary_group", "").casefold()
            != beneficiary_group.strip().casefold()
        ):
            continue

        filtered_schemes.append(scheme)

    return {
        "count": len(filtered_schemes),
        "schemes": filtered_schemes,
    }


@app.get("/api/schemes/{scheme_id}")
def get_scheme(scheme_id: str):
    schemes = load_schemes()

    for scheme in schemes:
        if scheme.get("id") == scheme_id:
            return scheme

    raise HTTPException(
        status_code=404,
        detail="Scheme not found",
    )
