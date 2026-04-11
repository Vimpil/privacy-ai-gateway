import { useMemo, useState } from "react";
import { requestOracle } from "../api/client";
import { MessageForm } from "../components/MessageForm";
import { decryptText, encryptText } from "../crypto/aesGcm";

const SHARED_KEY =
  import.meta.env.VITE_SHARED_KEY_BASE64 ?? "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";

export function OraclePage() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState("");
  const [auditHash, setAuditHash] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const hasKey = useMemo(() => SHARED_KEY.length > 0, []);

  const handleSubmit = async () => {
    if (!hasKey) {
      setError("Missing VITE_SHARED_KEY_BASE64 in frontend environment.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const encrypted = await encryptText(SHARED_KEY, message);
      const response = await requestOracle({ encrypted });
      const decrypted = await decryptText(
        SHARED_KEY,
        response.encrypted.nonce,
        response.encrypted.ciphertext,
      );
      setResult(decrypted);
      setAuditHash(response.audit_hash);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="layout">
      <MessageForm value={message} onChange={setMessage} onSubmit={handleSubmit} loading={loading} />
      <div className="card">
        <h3>Oracle Response</h3>
        <pre>{result || "No response yet."}</pre>
        <p className="muted">Audit Hash: {auditHash || "N/A"}</p>
        {error && <p className="error">{error}</p>}
      </div>
    </main>
  );
}

