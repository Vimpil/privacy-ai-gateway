export type AuditLogEntry = {
  index: number;
  timestamp: string;
  event_type: string;
  hash: string;
  previous_hash: string;
};

