
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SchemeWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Temporary sample data for development.
# Replace these examples with verified official scheme data.
schemes = [
    {
        "id": 1,
        "name": "Sample Student Scholarship",
        "category": "Education",
        "state": "Uttar Pradesh",
        "description": (
            "Sample record for developing the SchemeWise interface."
        ),
        "official_url": None,
    },
    {
        "id": 2,
        "name": "Sample Education Assistance Scheme",
        "category": "Education",
        "state": "All India",
        "description": (
            "Sample record for testing the scheme listing API."
        ),
        "official_url": None,
    },
]


@app.get("/")
def home():
    return {"message": "SchemeWise API is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/schemes")
def get_schemes():
    return {"count": len(schemes), "schemes": schemes}


@app.get("/api/schemes/{scheme_id}")
def get_scheme(scheme_id: int):
    for scheme in schemes:
        if scheme["id"] == scheme_id:
            return scheme

    from fastapi import HTTPException
    raise HTTPException(
        status_code=404,
        detail="Scheme not found",
    )
