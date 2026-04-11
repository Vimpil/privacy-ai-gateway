from fastapi import APIRouter, Query

from app.audit.audit_service import AuditService
from app.audit.stage_log_service import StageLogService
from app.core.config import get_settings
from app.schemas.audit import AuditEntry, ProcessingStageEntry

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


@router.get("/stages", response_model=list[ProcessingStageEntry])
def get_processing_stage_logs(
    request_id: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
) -> list[ProcessingStageEntry]:
    settings = get_settings()
    raw = StageLogService(settings.processing_log_path).read_all()
    if request_id:
        raw = [entry for entry in raw if str(entry.get("request_id")) == request_id]
    raw = raw[-limit:]
    return [
        ProcessingStageEntry(
            index=i + 1,
            timestamp=str(entry["timestamp"]),
            request_id=str(entry["request_id"]),
            stage=str(entry["stage"]),
            status=str(entry["status"]),
            message=str(entry["message"]),
        )
        for i, entry in enumerate(raw)
    ]


