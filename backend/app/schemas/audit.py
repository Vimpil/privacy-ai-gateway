from pydantic import BaseModel


class AuditEntry(BaseModel):
    index: int
    timestamp: str
    event_type: str
    hash: str
    previous_hash: str

