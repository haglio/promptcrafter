import type { ReactNode } from 'react';
import { useState } from 'react';
import { copyTextToClipboard } from '../lib/clipboard';

function PromptHeader({
  label,
  value,
  mode,
  onToggleMode,
  extraActions,
}: {
  label: string;
  value: string;
  mode: 'auto' | 'manual';
  onToggleMode: () => void;
  extraActions?: ReactNode;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await copyTextToClipboard(value);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1000);
  }

  return (
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
        onClick={onToggleMode}
        aria-pressed={mode === 'manual'}
      >
        {mode === 'auto' ? 'manual' : 'auto'}
      </button>
      {extraActions}
      <label className="prompt-label"><h3>{label}</h3></label>
    </div>
  );
}

export function Prompt({ label, value, mode, onChange, onToggleMode, extraActions }: {
  label: string;
  value: string;
  mode: 'auto' | 'manual';
  onChange: (value: string) => void;
  onToggleMode: (mode: 'auto' | 'manual') => void;
  extraActions?: ReactNode;
}) {
  return (
    <section className="prompt-area">
      <PromptHeader
        label={label}
        value={value}
        mode={mode}
        onToggleMode={() => onToggleMode(mode === 'auto' ? 'manual' : 'auto')}
        extraActions={extraActions}
      />
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
