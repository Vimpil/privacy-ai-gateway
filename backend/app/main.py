from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.audit import router as audit_router
from app.api.routes.oracle import router as oracle_router
from app.middleware import ErrorHandlingMiddleware, RateLimitMiddleware

app = FastAPI(
    title="Cipher Oracle Gateway",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# ── Middleware (order matters) ────────────────────────────────────────────────

# Rate limiting must be early to reject spam before processing
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Error handling wraps everything
app.add_middleware(ErrorHandlingMiddleware)

# CORS allows frontend dev server to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # fallback for typical React dev
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length"],
    max_age=3600,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(oracle_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


