import { useState } from 'react';

export function Prompt({ label, value, mode, onChange, onToggleMode }: {
  label: string;
  value: string;
  mode: 'auto' | 'manual';
  onChange: (value: string) => void;
  onToggleMode: (mode: 'auto' | 'manual') => void;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1000);
  }

  return (
    <section className="prompt-area">
      <div className="prompt-header">
        <button
          type="button"
          className="copy-button"
          aria-label="Copy prompt"
          onClick={handleCopy}
        >
          {copied ? (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
              <path d="M9 16.2 4.8 12 3.4 13.4 9 19l12-12-1.4-1.4z"/>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
              <path d="M16 1H6a2 2 0 0 0-2 2v12h2V3h10V1zm3 4H10a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H10V7h9v14z"/>
            </svg>
          )}
        </button>
        <button
          type="button"
          className={`mode-toggle ${mode}`}
          onClick={() => onToggleMode(mode === 'auto' ? 'manual' : 'auto')}
          aria-pressed={mode === 'manual'}
        >
          {mode === 'auto' ? 'manual' : 'auto'}
        </button>
        <label className="prompt-label"><h3>{label}</h3></label>
      </div>
      <textarea
        aria-label={label}
        className={label === 'Negative prompt' ? 'negative-textarea' : 'positive-textarea'}
        value={value}
        disabled={mode === 'auto'}
        onChange={(event) => onChange(event.target.value)}
      />
    </section>
  );
}