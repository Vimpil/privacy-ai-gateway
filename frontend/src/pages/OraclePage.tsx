import { useState } from "react";
import { MessageForm } from "../components/MessageForm";
import { decryptText, encryptText } from "../crypto/aesGcm";
import { requestOracle } from "../services/client";

const SHARED_KEY =
  import.meta.env.VITE_SHARED_KEY_BASE64 ?? "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";

const STEPS = {
  encrypt: "🔐 Encrypting...",
  send:    "📡 Consulting oracle...",
  decrypt: "🔓 Decrypting response...",
};

export function OraclePage() {
  const [message, setMessage]     = useState("");
  const [result, setResult]       = useState("");
  const [auditHash, setAuditHash] = useState("");
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [step, setStep]           = useState("");

  const handleSubmit = async () => {
    if (!SHARED_KEY) {
      setError("Missing VITE_SHARED_KEY_BASE64 in environment.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      setResult("");
      setAuditHash("");

      setStep(STEPS.encrypt);
      const encrypted = await encryptText(SHARED_KEY, message);

      setStep(STEPS.send);
      const response = await requestOracle({ encrypted });

      setStep(STEPS.decrypt);
      const decrypted = await decryptText(
        SHARED_KEY,
        response.encrypted.nonce,
        response.encrypted.ciphertext,
      );

      setResult(decrypted);
      setAuditHash(response.audit_hash);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
      setStep("");
    }
  };

  return (
    <>
      <header className="oracle-header">
        <span className="oracle-header__badge">Privacy-First AI Gateway</span>
        <h1 className="oracle-header__title">Cipher Oracle</h1>
        <p className="oracle-header__subtitle">
          End-to-end encrypted · Local AI inference · Tamper-evident audit log
        </p>
      </header>

      <MessageForm
        value={message}
        onChange={setMessage}
        onSubmit={handleSubmit}
        loading={loading}
        step={step}
      />

      <div className="card">
        <p className="card__label">Oracle Response</p>
        <div className={`response-content${result ? "" : " empty"}`}>
          {result || "Awaiting the oracle…"}
        </div>

        {auditHash && (
          <div className="audit-row">
            <span className="audit-row__label">Audit</span>
            <span className="audit-row__hash" title={auditHash}>{auditHash}</span>
          </div>
        )}

        {error && <p className="error-msg">{error}</p>}
      </div>
    </>
  );
}
