"""Application entry point."""

from fastapi import FastAPI

from app.api import router

app = FastAPI(
    title="Service Management API",
    description="A practical backend engineering portfolio project.",
    version="0.1.0",
)
app.include_router(router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness probe; does not check database readiness."""
    return {"status": "ok"}
