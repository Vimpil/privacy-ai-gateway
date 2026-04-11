from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


class AuditService:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append_event(self, event_type: str, payload: dict[str, str]) -> str:
        previous_hash = self._read_previous_hash()
        timestamp = datetime.now(timezone.utc).isoformat()
        raw_record = {
            "timestamp": timestamp,
            "event_type": event_type,
            "payload": payload,
            "previous_hash": previous_hash,
        }
        record_hash = self._hash_record(raw_record)
        record = {**raw_record, "hash": record_hash}
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")
        return record_hash

    def read_all_logs(self) -> list[dict[str, object]]:
        """Return all audit records in insertion order."""
        if not self.log_path.exists():
            return []
        records: list[dict[str, object]] = []
        with self.log_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _read_previous_hash(self) -> str:
        if not self.log_path.exists():
            return "GENESIS"
        last_line = ""
        with self.log_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    last_line = line
        if not last_line:
            return "GENESIS"
        return json.loads(last_line).get("hash", "GENESIS")

    @staticmethod
    def _hash_record(record: dict[str, object]) -> str:
        canonical = json.dumps(record, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

