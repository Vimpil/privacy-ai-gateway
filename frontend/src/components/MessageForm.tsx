type MessageFormProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  step?: string;
};

export function MessageForm({ value, onChange, onSubmit, loading, step }: MessageFormProps) {
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
    </div>
  );
}
