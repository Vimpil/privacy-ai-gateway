from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import base64

from dotenv import load_dotenv

INSECURE_DEFAULT_KEY_B64 = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

# Load backend/.env once so local config is respected even when launched from repo root.
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_sec: float
    ollama_retries: int
    ollama_retry_backoff_sec: float
    ollama_fallback_enabled: bool
    wikipedia_base_url: str
    wikipedia_timeout_sec: float
    wikipedia_enabled: bool
    gateway_shared_key_b64: str
    audit_log_path: str
    processing_log_path: str


def _validate_shared_key(shared_key_b64: str, allow_insecure_dev_key: bool) -> str:
    if not shared_key_b64:
        raise ValueError("GATEWAY_SHARED_KEY_BASE64 is required")

    if shared_key_b64 == INSECURE_DEFAULT_KEY_B64 and not allow_insecure_dev_key:
        raise ValueError(
            "Refusing to start with insecure default key. Set GATEWAY_SHARED_KEY_BASE64 "
            "to a strong 32-byte base64 key."
        )

    decoded = base64.b64decode(shared_key_b64)
    if len(decoded) not in (16, 24, 32):
        raise ValueError("GATEWAY_SHARED_KEY_BASE64 must decode to 16, 24, or 32 bytes")

    return shared_key_b64


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    allow_insecure = os.getenv("ALLOW_INSECURE_DEV_KEY", "false").lower() == "true"
    shared_key_b64 = _validate_shared_key(
        os.getenv("GATEWAY_SHARED_KEY_BASE64", ""),
        allow_insecure,
    )

    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        ollama_timeout_sec=float(os.getenv("OLLAMA_TIMEOUT_SEC", "120")),
        ollama_retries=int(os.getenv("OLLAMA_RETRIES", "1")),
        ollama_retry_backoff_sec=float(os.getenv("OLLAMA_RETRY_BACKOFF_SEC", "2")),
        ollama_fallback_enabled=os.getenv("OLLAMA_FALLBACK_ENABLED", "true").lower() == "true",
        wikipedia_base_url=os.getenv("WIKIPEDIA_BASE_URL", "https://en.wikipedia.org/api/rest_v1"),
        wikipedia_timeout_sec=float(os.getenv("WIKIPEDIA_TIMEOUT_SEC", "8")),
        wikipedia_enabled=os.getenv("WIKIPEDIA_ENABLED", "true").lower() == "true",
        gateway_shared_key_b64=shared_key_b64,
        audit_log_path=os.getenv("AUDIT_LOG_PATH", "data/audit.log"),
        processing_log_path=os.getenv("PROCESSING_LOG_PATH", "data/processing.log"),
    )

