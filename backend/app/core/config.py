from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_sec: float
    ollama_retries: int
    ollama_retry_backoff_sec: float
    ollama_fallback_enabled: bool
    gateway_shared_key_b64: str
    audit_log_path: str
    processing_log_path: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        ollama_timeout_sec=float(os.getenv("OLLAMA_TIMEOUT_SEC", "120")),
        ollama_retries=int(os.getenv("OLLAMA_RETRIES", "1")),
        ollama_retry_backoff_sec=float(os.getenv("OLLAMA_RETRY_BACKOFF_SEC", "2")),
        ollama_fallback_enabled=os.getenv("OLLAMA_FALLBACK_ENABLED", "true").lower() == "true",
        gateway_shared_key_b64=os.getenv(
            "GATEWAY_SHARED_KEY_BASE64",
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        ),
        audit_log_path=os.getenv("AUDIT_LOG_PATH", "data/audit.log"),
        processing_log_path=os.getenv("PROCESSING_LOG_PATH", "data/processing.log"),
    )

