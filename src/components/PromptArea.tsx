import { useState } from 'react';

type PromptAreaProps = {
  label: string;
  value: string;
  bound: boolean;
  onChange: (value: string) => void;
  onToggleBound: (bound: boolean) => void;
};

export function PromptArea({ label, value, bound, onChange, onToggleBound }: PromptAreaProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1000);
  }

  return (
    <section className="prompt-area">
      <div className="prompt-header">
        <label className="prompt-label">
          <span>{label}</span>
          <input type="checkbox" checked={!bound} onChange={(event) => onToggleBound(!event.target.checked)} />
          <span>Unbind</span>
        </label>
        <button type="button" onClick={handleCopy}>{copied ? 'Copied' : 'Copy'}</button>
      </div>
      <textarea
        aria-label={label}
        className={label === 'Negative prompt' ? 'negative-textarea' : 'positive-textarea'}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </section>
  );
}