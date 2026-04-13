import { useEffect, useRef, useState } from "react";
import { MessageForm } from "../components/MessageForm";
import { decryptText, encryptText } from "../crypto/aesGcm";
import { fetchProcessingStageLogsForRequest, fetchWikipediaSummaryClient, requestOracle } from "../services/client";
import type { PublicApiContext } from "../types/oracle";
import { buildWaitingPhrases, pickRandomPhraseIndex } from "./oracleLoaderPhrases";

const STEPS = {
  encrypt: "🔐 Encrypting...",
  send:    "📡 Consulting oracle...",
  decrypt: "🔓 Decrypting response...",
};

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
  const [mode, setMode] = useState<"ai" | "wikipedia_only" | "client_only">("wikipedia_only");
  const [passphrase, setPassphrase] = useState("");
  const [loaderSourceLabel, setLoaderSourceLabel] = useState<string | undefined>(undefined);
  const [responseFresh, setResponseFresh] = useState(false);
  const pollRef = useRef<number | null>(null);
  const tickRef = useRef<number | null>(null);
  const phraseRef = useRef<number | null>(null);
  const phrasePoolRef = useRef<string[]>(buildWaitingPhrases());
  const recentPhraseRef = useRef<number[]>([]);
  const lastWikiTitleRef = useRef<string | null>(null);

  const pickNextPhrase = (previous?: number) => {
    const next = pickRandomPhraseIndex(
      phrasePoolRef.current.length,
      previous,
      recentPhraseRef.current,
    );
    recentPhraseRef.current = [...recentPhraseRef.current.slice(-14), next];
    return next;
  };

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
          if (title && lastWikiTitleRef.current !== title) {
            lastWikiTitleRef.current = title;
            setLoaderSourceLabel(`wikipedia: ${title}`);
            phrasePoolRef.current = buildWaitingPhrases(title, title);
            recentPhraseRef.current = [];
            setPhraseIndex(pickNextPhrase());
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
      setPhraseIndex((i) => pickNextPhrase(i));
    }, 6200);
  };

  useEffect(() => stopProgressPolling, []);

  useEffect(() => {
    if (!responseFresh) return;
    const timer = window.setTimeout(() => setResponseFresh(false), 900);
    return () => window.clearTimeout(timer);
  }, [responseFresh]);

  const handleSubmit = async () => {
    const trimmedPassphrase = passphrase.trim();

    if (mode === "ai" && trimmedPassphrase.length < 8) {
      setError("AI + Wikipedia mode requires a passphrase with at least 8 characters.");
      return;
    }

    if (mode === "wikipedia_only" && trimmedPassphrase.length > 0 && trimmedPassphrase.length < 8) {
      setError("Passphrase must be at least 8 characters, or leave it empty for Wikipedia-only mode.");
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
      lastWikiTitleRef.current = null;
      setElapsedSeconds(0);
      setStepStatus("running");
      phrasePoolRef.current = buildWaitingPhrases(topicFromPrompt(message), null);
      recentPhraseRef.current = [];
      setPhraseIndex(pickNextPhrase());

      if (mode === "client_only") {
        setStep("🌐 Fetching Wikipedia from browser...");
        const wiki = await fetchWikipediaSummaryClient(message);
        if (!wiki) {
          setResult("The system whispers... No Wikipedia context found for this prompt.");
          setAuditHash("");
        } else {
          setResult(`The Cipher Oracle reveals... ${wiki.summary}`);
          setPublicContext({ provider: "wikipedia", title: wiki.title, summary: wiki.summary, url: wiki.url });
          setAuditHash("");
        }
        setResponseFresh(true);
        return;
      }

      const effectivePassphrase =
        mode === "wikipedia_only" && trimmedPassphrase.length === 0
          ? `wiki-${crypto.randomUUID()}`
          : trimmedPassphrase;

      setStep(STEPS.encrypt);
      const cryptoPacket = await encryptText(effectivePassphrase, message);

      setStep(STEPS.send);
      startProgressPolling(requestId);
      const response = await requestOracle({
        encrypted: cryptoPacket.encrypted,
        request_id: requestId,
        mode,
        passphrase: effectivePassphrase,
        kdf_salt: cryptoPacket.kdf.salt,
        kdf_iterations: cryptoPacket.kdf.iterations,
      });
      if (response.public_api) {
        setPublicContext(response.public_api);
        lastWikiTitleRef.current = response.public_api.title;
        setLoaderSourceLabel(`${response.public_api.provider}: ${response.public_api.title}`);
        phrasePoolRef.current = buildWaitingPhrases(topicFromPrompt(message), response.public_api.title);
        recentPhraseRef.current = [];
        setPhraseIndex(pickNextPhrase());
      }

      setStep(STEPS.decrypt);
      const decrypted = await decryptText(
        effectivePassphrase,
        response.encrypted.nonce,
        response.encrypted.ciphertext,
        cryptoPacket.kdf,
      );

      setResult(decrypted);
      setResponseFresh(true);
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
        mode={mode}
        onModeChange={setMode}
        passphrase={passphrase}
        onPassphraseChange={setPassphrase}
        loading={loading}
        step={step}
        stepStatus={stepStatus}
        elapsedSeconds={elapsedSeconds}
        progressPhrase={phrasePoolRef.current[phraseIndex]}
        publicSourceLabel={loaderSourceLabel}
      />

      <div className="card">
        <p className="card__label">Oracle Response</p>
        <div className={`response-content${result ? "" : " empty"}${responseFresh ? " response-content--fresh" : ""}`}>
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
