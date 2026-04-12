type MessageFormProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  step?: string;
  progressPhrase?: string;
  elapsedSeconds?: number;
  stepStatus?: "ok" | "warn" | "error" | "running";
  publicSourceLabel?: string;
  mode: "ai" | "wikipedia_only" | "client_only";
  onModeChange: (mode: "ai" | "wikipedia_only" | "client_only") => void;
  passphrase: string;
  onPassphraseChange: (value: string) => void;
};

export function MessageForm({
  value,
  onChange,
  onSubmit,
  loading,
  step,
  progressPhrase,
  elapsedSeconds,
  stepStatus = "running",
  publicSourceLabel,
  mode,
  onModeChange,
  passphrase,
  onPassphraseChange,
}: MessageFormProps) {
  const isRunning = stepStatus === "running";
  const modeHint = mode === "wikipedia_only"
    ? "Wikipedia only: backend decrypts request, fetches Wikipedia, re-encrypts response, and writes audit log."
    : mode === "ai"
      ? "AI + Wikipedia: backend decrypts request, enriches with Wikipedia, calls Ollama, re-encrypts, and writes audit log."
      : "Client only (experimental): browser calls Wikipedia directly; backend pipeline and audit hash are skipped.";

  return (
    <div className="card">
      <p className="card__label">Your Prompt</p>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Ask the oracle..."
        disabled={loading}
      />
      <input
        type="password"
        className="passphrase-input"
        placeholder={mode === "client_only" ? "Passphrase not required in client-only mode" : "Passphrase (min 8 chars)"}
        value={passphrase}
        onChange={(e) => onPassphraseChange(e.target.value)}
        disabled={loading || mode === "client_only"}
      />
      <div className="card__actions">
        <button
          className="btn-primary"
          onClick={onSubmit}
          disabled={loading || value.trim().length === 0}
        >
          🔒 {loading ? "Processing..." : "Encrypt & Send"}
        </button>
        <span className={`step-indicator${step ? " visible" : ""}`}>
          {step}
        </span>
      </div>

      <div className="mode-switch" role="group" aria-label="Processing mode">
        <button
          type="button"
          className={`mode-switch__item${mode === "wikipedia_only" ? " mode-switch__item--active" : ""}`}
          onClick={() => onModeChange("wikipedia_only")}
          disabled={loading}
        >
          Wikipedia only
        </button>
        <button
          type="button"
          className={`mode-switch__item${mode === "ai" ? " mode-switch__item--active" : ""}`}
          onClick={() => onModeChange("ai")}
          disabled={loading}
        >
          AI + Wikipedia
        </button>
        <button
          type="button"
          className={`mode-switch__item${mode === "client_only" ? " mode-switch__item--active" : ""}`}
          onClick={() => onModeChange("client_only")}
          disabled={loading}
        >
          Client only (exp)
        </button>
      </div>
      <p className="mode-switch__hint">
        {modeHint}
      </p>

      {loading && (
        <div className="progress-panel" role="status" aria-live="polite">
          {publicSourceLabel && <p className="progress-source">Public source: {publicSourceLabel}</p>}
          <p className="progress-phrase" key={progressPhrase}>{progressPhrase}</p>
          <div className="progress-rail" aria-hidden="true">
            <span className="progress-rail__fill" />
          </div>
          <div className="progress-meta">
            <span className={`progress-stage progress-stage--${stepStatus}`}>
              {isRunning && <span className="progress-stage__dot" aria-hidden="true" />}
              {stepStatus}
            </span>
            <span className="progress-timer">{elapsedSeconds ?? 0}s</span>
          </div>
        </div>
      )}
    </div>
  );
}
