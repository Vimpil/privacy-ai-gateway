import { useEffect, useState } from "react";
import { fetchAuditLogs, fetchProcessingStageLogs } from "../services/client";
import type { AuditLogEntry, ProcessingStageEntry } from "../types/audit";

function truncate(value: string, length = 16): string {
  return value.length > length ? `${value.slice(0, length)}…` : value;
}

export function AuditPage() {
  const [logs, setLogs]       = useState<AuditLogEntry[]>([]);
  const [stages, setStages]   = useState<ProcessingStageEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const load = async () => {
    try {
      setLoading(true);
      setError("");
      const [data, stageData] = await Promise.all([
        fetchAuditLogs(),
        fetchProcessingStageLogs(),
      ]);
      setLogs(data.slice().reverse()); // newest first
      setStages(stageData.slice().reverse()); // newest first
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  return (
    <>
      <header className="oracle-header">
        <span className="oracle-header__badge">Tamper-Evident Chronicle</span>
        <h1 className="oracle-header__title">Audit Log</h1>
        <p className="oracle-header__subtitle">
          SHA-256 hash chain · Each record references the previous hash
        </p>
      </header>

      <div className="card audit-card">
        <div className="audit-toolbar">
          <p className="card__label">
            {logs.length} {logs.length === 1 ? "entry" : "entries"}
          </p>
          <button className="btn-primary btn-sm" onClick={load} disabled={loading}>
            {loading ? "Loading…" : "↺ Refresh"}
          </button>
        </div>

        {error && <p className="error-msg">{error}</p>}

        {!error && logs.length === 0 && !loading && (
          <p className="audit-empty">No events recorded yet.</p>
        )}

        {logs.length > 0 && (
          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Timestamp</th>
                  <th>Event</th>
                  <th>Hash</th>
                  <th>Prev Hash</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((entry) => (
                  <tr key={entry.index}>
                    <td className="audit-index">{entry.index}</td>
                    <td className="audit-ts">{new Date(entry.timestamp).toLocaleString()}</td>
                    <td>
                      <span className="audit-event-badge">{entry.event_type}</span>
                    </td>
                    <td>
                      <span className="audit-hash" title={entry.hash}>
                        {truncate(entry.hash, 12)}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`audit-hash ${entry.previous_hash === "GENESIS" ? "audit-hash--genesis" : ""}`}
                        title={entry.previous_hash}
                      >
                        {entry.previous_hash === "GENESIS" ? "GENESIS" : truncate(entry.previous_hash, 12)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card audit-card">
        <div className="audit-toolbar">
          <p className="card__label">
            Processing Stage Logs ({stages.length})
          </p>
        </div>

        {!error && stages.length === 0 && !loading && (
          <p className="audit-empty">No processing logs yet. Send a prompt to generate stage logs.</p>
        )}

        {stages.length > 0 && (
          <div className="audit-table-wrap">
            <table className="audit-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Timestamp</th>
                  <th>Request</th>
                  <th>Stage</th>
                  <th>Status</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {stages.map((entry) => (
                  <tr key={`${entry.index}-${entry.timestamp}`}>
                    <td className="audit-index">{entry.index}</td>
                    <td className="audit-ts">{new Date(entry.timestamp).toLocaleString()}</td>
                    <td>
                      <span className="audit-hash" title={entry.request_id}>
                        {truncate(entry.request_id, 12)}
                      </span>
                    </td>
                    <td>
                      <span className="audit-event-badge">{entry.stage}</span>
                    </td>
                    <td>
                      <span className={`audit-event-badge ${entry.status === "error" ? "audit-event-badge--error" : ""} ${entry.status === "warn" ? "audit-event-badge--warn" : ""}`}>
                        {entry.status}
                      </span>
                    </td>
                    <td>{entry.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}

