type MessageFormProps = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
};

export function MessageForm({ value, onChange, onSubmit, loading }: MessageFormProps) {
  return (
    <div className="card">
      <h2>Cipher Oracle</h2>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={6}
        placeholder="Ask the oracle..."
      />
      <button onClick={onSubmit} disabled={loading || value.trim().length === 0}>
        {loading ? "Consulting..." : "Consult Oracle"}
      </button>
    </div>
  );
}

