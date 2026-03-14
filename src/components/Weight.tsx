export function Weight({
  value,
  disabled,
  onChange,
}: {
  value: number;
  disabled: boolean;
  onChange: (value: number) => void;
}) {
  return (
    <div className="weight">
      {value !== 1 && (
        <button
          type="button"
          className="weight-reset"
          onClick={() => onChange(1)}
          disabled={disabled}
        >
          ↺
        </button>
      )}

      <input
        type="range"
        min="0"
        max="5"
        step="0.1"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number.parseFloat(e.target.value))}
      />
    </div>
  );
}
