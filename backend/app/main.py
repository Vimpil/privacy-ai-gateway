from fastapi import FastAPI

from app.api.routes.oracle import router as oracle_router

app = FastAPI(title="Cipher Oracle Gateway", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(oracle_router, prefix="/api/v1")

