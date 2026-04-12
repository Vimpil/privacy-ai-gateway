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

export async function fetchProcessingStageLogsForRequest(
  requestId: string,
  limit = 100,
): Promise<ProcessingStageEntry[]> {
  const query = new URLSearchParams({ request_id: requestId, limit: String(limit) });
  const response = await fetch(`${API_BASE_URL}/api/v1/audit/stages?${query.toString()}`);
  if (!response.ok) throw new Error("Failed to fetch processing logs");
  return (await response.json()) as ProcessingStageEntry[];
}

export async function fetchWikipediaSummaryClient(topic: string): Promise<{ title: string; summary: string; url: string } | null> {
  const normalized = topic.trim().replace(/\s+/g, "_");
  if (!normalized) return null;
  const response = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(normalized)}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) return null;
  const data = (await response.json()) as {
    title?: string;
    extract?: string;
    content_urls?: { desktop?: { page?: string } };
  };
  if (!data.extract) return null;
  return {
    title: data.title ?? topic,
    summary: data.extract,
    url: data.content_urls?.desktop?.page ?? "https://en.wikipedia.org",
  };
}

