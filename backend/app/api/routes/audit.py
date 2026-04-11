from fastapi import APIRouter

from app.audit.audit_service import AuditService
from app.core.config import get_settings
from app.schemas.audit import AuditEntry

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=list[AuditEntry])
def get_audit_logs() -> list[AuditEntry]:
    settings = get_settings()
    raw = AuditService(settings.audit_log_path).read_all_logs()
    return [
        AuditEntry(
            index=i + 1,
            timestamp=str(entry["timestamp"]),
            event_type=str(entry["event_type"]),
            hash=str(entry["hash"]),
            previous_hash=str(entry["previous_hash"]),
        )
        for i, entry in enumerate(raw)
    ]

