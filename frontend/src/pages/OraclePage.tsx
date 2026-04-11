import { useEffect, useRef, useState } from "react";
import { MessageForm } from "../components/MessageForm";
import { decryptText, encryptText } from "../crypto/aesGcm";
import { fetchProcessingStageLogsForRequest, requestOracle } from "../services/client";
import type { PublicApiContext } from "../types/oracle";

const SHARED_KEY =
  import.meta.env.VITE_SHARED_KEY_BASE64 ?? "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";

const STEPS = {
  encrypt: "🔐 Encrypting...",
  send:    "📡 Consulting oracle...",
  decrypt: "🔓 Decrypting response...",
};

const BASE_WAITING_PHRASES = [
  "Aligning crystal matrices with local llama cortex...",
  "Consulting the stars, satellites, and one very sleepy GPU...",
  "Oracle pigeons are delivering your prompt to the model...",
  "Negotiating with the silicon spirits for better logits...",
  "Civilization council is debating your request this turn...",
  "Sims committee is routing your thought bubble to llama...",
  "Decoding tea leaves and token probabilities...",
];

function topicFromPrompt(prompt: string): string | null {
  const cleaned = prompt.trim().replace(/[?.!]+$/, "");
  if (!cleaned) return null;

  const prefixes = ["what is ", "who is ", "what are ", "tell me about ", "define ", "explain "];
  const lowered = cleaned.toLowerCase();
  for (const prefix of prefixes) {
    if (lowered.startsWith(prefix)) {
      return cleaned.slice(prefix.length).trim() || null;
    }
  }

  const words = cleaned.split(/\s+/).filter(Boolean);
  return words.length <= 5 ? cleaned : null;
}

function waitingPhrases(topic: string | null, publicContext: PublicApiContext | null): string[] {
  const focus = publicContext?.title ?? topic;
  if (!focus) return BASE_WAITING_PHRASES;

  return [
    `Dispatching Civ historians to the Wikipedia archives for ${focus}...`,
    `The Sims mailroom is stamping paperwork marked '${focus}'...`,
    `Oracle interns are highlighting the ${focus} scrolls from Wikipedia...`,
    `A llama librarian is skimming public records about ${focus}...`,
    `Cross-referencing ${focus} with public knowledge and mystical vibes...`,
    ...BASE_WAITING_PHRASES,
  ];
}

export function OraclePage() {
  const [message, setMessage]     = useState("");
  const [result, setResult]       = useState("");
  const [auditHash, setAuditHash] = useState("");
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [step, setStep]           = useState("");
  const [stepStatus, setStepStatus] = useState<"ok" | "warn" | "error" | "running">("running");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [publicContext, setPublicContext] = useState<PublicApiContext | null>(null);
  const [loaderSourceLabel, setLoaderSourceLabel] = useState<string | undefined>(undefined);
  const pollRef = useRef<number | null>(null);
  const tickRef = useRef<number | null>(null);
  const phraseRef = useRef<number | null>(null);
  const phrasePoolRef = useRef<string[]>(BASE_WAITING_PHRASES);

  const stopProgressPolling = () => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
    if (tickRef.current !== null) {
      window.clearInterval(tickRef.current);
      tickRef.current = null;
    }
    if (phraseRef.current !== null) {
      window.clearInterval(phraseRef.current);
      phraseRef.current = null;
    }
  };

  const startProgressPolling = (requestId: string) => {
    stopProgressPolling();
    pollRef.current = window.setInterval(async () => {
      try {
        const logs = await fetchProcessingStageLogsForRequest(requestId, 50);
        if (logs.length === 0) return;

        const latest = logs[logs.length - 1];
        const statusIcon = latest.status === "warn" ? "[WARN]" : latest.status === "error" ? "[ERR]" : "[OK]";
        setStep(`${statusIcon} ${latest.stage}: ${latest.message}`);
        if (latest.status === "warn" || latest.status === "error" || latest.status === "ok") {
          setStepStatus(latest.status);
        } else {
          setStepStatus("running");
        }

        if (latest.stage === "public_api_fetch" && latest.status === "ok") {
          const match = latest.message.match(/for\s+(.+)$/i);
          const title = match?.[1]?.trim();
          if (title) {
            setLoaderSourceLabel(`wikipedia: ${title}`);
            phrasePoolRef.current = waitingPhrases(title, null);
          }
        }
      } catch {
        // Keep UI responsive even if polling fails transiently.
      }
    }, 800);

    tickRef.current = window.setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);

    phraseRef.current = window.setInterval(() => {
      setPhraseIndex((i) => (i + 1) % phrasePoolRef.current.length);
    }, 2600);
  };

  useEffect(() => stopProgressPolling, []);

  const handleSubmit = async () => {
    if (!SHARED_KEY) {
      setError("Missing VITE_SHARED_KEY_BASE64 in environment.");
      return;
    }
    try {
      const requestId = crypto.randomUUID();
      setLoading(true);
      setError("");
      setResult("");
      setAuditHash("");
      setPublicContext(null);
      setLoaderSourceLabel(undefined);
      setElapsedSeconds(0);
      setStepStatus("running");
      phrasePoolRef.current = waitingPhrases(topicFromPrompt(message), null);
      setPhraseIndex(Math.floor(Math.random() * phrasePoolRef.current.length));

      setStep(STEPS.encrypt);
      const encrypted = await encryptText(SHARED_KEY, message);

      setStep(STEPS.send);
      startProgressPolling(requestId);
      const response = await requestOracle({ encrypted, request_id: requestId });
      if (response.public_api) {
        setPublicContext(response.public_api);
        setLoaderSourceLabel(`${response.public_api.provider}: ${response.public_api.title}`);
        phrasePoolRef.current = waitingPhrases(topicFromPrompt(message), response.public_api);
      }

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
      stopProgressPolling();
      setLoading(false);
      setStep("");
      setStepStatus("running");
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
        stepStatus={stepStatus}
        elapsedSeconds={elapsedSeconds}
        progressPhrase={phrasePoolRef.current[phraseIndex]}
        publicSourceLabel={loaderSourceLabel}
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

        {publicContext && (
          <div className="public-api-card">
            <p className="card__label">Public API Context</p>
            <p className="public-api-card__title">Wikipedia · {publicContext.title}</p>
            <p className="public-api-card__summary">{publicContext.summary}</p>
            <a className="public-api-card__link" href={publicContext.url} target="_blank" rel="noreferrer">
              Open source article
            </a>
          </div>
        )}

        {error && <p className="error-msg">{error}</p>}
      </div>
    </>
  );
}
