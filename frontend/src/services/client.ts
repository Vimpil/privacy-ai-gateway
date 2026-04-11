import type { OracleRequest, OracleResponse } from "../types/oracle";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function requestOracle(payload: OracleRequest): Promise<OracleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/oracle/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Oracle request failed");
  }

  return (await response.json()) as OracleResponse;
}

