from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes.audit import router as audit_router
from app.api.routes.oracle import router as oracle_router
from app.middleware import RateLimitMiddleware

app = FastAPI(
    title="Cipher Oracle Gateway",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# ── Middleware (order matters) ────────────────────────────────────────────────

# Rate limiting must be early to reject spam before processing
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

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


def _error_response(message: str, status_code: int, details: object | None = None) -> JSONResponse:
    body: dict[str, object] = {"status": "error", "error": message}
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(message, exc.status_code)


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError) -> JSONResponse:
    return _error_response("Invalid request", 422, details=exc.errors())


@app.exception_handler(Exception)
async def handle_unexpected_exception(_: Request, __: Exception) -> JSONResponse:
    return _error_response("Internal server error", 500)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(oracle_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


