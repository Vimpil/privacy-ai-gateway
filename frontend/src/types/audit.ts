export type AuditLogEntry = {
  index: number;
  timestamp: string;
  event_type: string;
  hash: string;
  previous_hash: string;
};

export type ProcessingStageEntry = {
  index: number;
  timestamp: string;
  request_id: string;
  stage: string;
  status: string;
  message: string;
};

