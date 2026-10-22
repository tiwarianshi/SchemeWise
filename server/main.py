from fastapi import FastAPI

app = FastAPI(title="SchemeWise API")


@app.get("/")
def home():
    return {"message": "SchemeWise API is running!"}


@app.get("/health")
def health():
    return {"status": "healthy"}