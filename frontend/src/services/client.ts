import type { AuditLogEntry, ProcessingStageEntry } from "../types/audit";
import type { OracleRequest, OracleResponse } from "../types/oracle";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function requestOracle(payload: OracleRequest): Promise<OracleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Oracle request failed");
  return (await response.json()) as OracleResponse;
}

export async function fetchAuditLogs(): Promise<AuditLogEntry[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/audit/logs`);
  if (!response.ok) throw new Error("Failed to fetch audit logs");
  return (await response.json()) as AuditLogEntry[];
}

export async function fetchProcessingStageLogs(): Promise<ProcessingStageEntry[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/audit/stages`);
  if (!response.ok) throw new Error("Failed to fetch processing logs");
  return (await response.json()) as ProcessingStageEntry[];
}

