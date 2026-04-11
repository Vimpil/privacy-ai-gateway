import { useEffect, useState } from "react";
import { fetchAuditLogs } from "../services/client";
import type { AuditLogEntry } from "../types/audit";

function truncate(value: string, length = 16): string {
  return value.length > length ? `${value.slice(0, length)}…` : value;
}

export function AuditPage() {
  const [logs, setLogs]       = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const load = async () => {
    try {
      setLoading(true);
      setError("");
      const data = await fetchAuditLogs();
      setLogs(data.slice().reverse()); // newest first
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
    </>
  );
}

