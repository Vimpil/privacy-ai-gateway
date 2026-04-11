from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class StageLogService:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        request_id: str,
        stage: str,
        status: str,
        message: str,
    ) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "stage": stage,
            "status": status,
            "message": message,
        }
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def read_all(self) -> list[dict[str, str]]:
        if not self.log_path.exists():
            return []

        logs: list[dict[str, str]] = []
        with self.log_path.open("r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    logs.append(json.loads(line))
        return logs

