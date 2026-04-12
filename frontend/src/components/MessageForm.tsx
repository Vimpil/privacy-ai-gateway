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
  mode: "ai" | "wikipedia_only";
  onModeChange: (mode: "ai" | "wikipedia_only") => void;
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
}: MessageFormProps) {
  const isRunning = stepStatus === "running";

  return (
    <div className="card">
      <p className="card__label">Your Prompt</p>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Ask the oracle..."
        disabled={loading}
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
      </div>
      <p className="mode-switch__hint">
        Wikipedia-only mode skips local AI and works best with clear topic prompts.
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
