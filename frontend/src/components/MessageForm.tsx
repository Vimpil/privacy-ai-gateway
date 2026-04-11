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
}: MessageFormProps) {
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

      {loading && (
        <div className="progress-panel">
          {publicSourceLabel && <p className="progress-source">Public source: {publicSourceLabel}</p>}
          <p className="progress-phrase" key={progressPhrase}>{progressPhrase}</p>
          <div className="progress-meta">
            <span className={`progress-stage progress-stage--${stepStatus}`}>{stepStatus}</span>
            <span className="progress-timer">{elapsedSeconds ?? 0}s</span>
          </div>
        </div>
      )}
    </div>
  );
}
