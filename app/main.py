from fastapi import FastAPI

app = FastAPI(title="Digital Twin")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a static liveness status; no side effects."""
    return {"status": "healthy"}
