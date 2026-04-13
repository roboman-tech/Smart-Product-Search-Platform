import { cn } from "../lib/cn";
import type { SearchState } from "../utils/searchParamsConfig";

interface ActiveFilterChipsProps {
  state: SearchState;
  onRemove: (key: keyof SearchState) => void;
  onClearAll: () => void;
  className?: string;
}

const LABEL_MAP: Partial<Record<keyof SearchState, string>> = {
  category:  "Category",
  brand:     "Brand",
  min_price: "Min price",
  max_price: "Max price",
  rating:    "Rating",
  in_stock:  "In stock",
};

const FILTER_KEYS: (keyof SearchState)[] = [
  "category", "brand", "min_price", "max_price", "rating", "in_stock",
];

function formatValue(key: keyof SearchState, value: string): string {
  if (key === "in_stock") return "In stock only";
  if (key === "rating") return `${value}+ stars`;
  if (key === "min_price") return `From $${value}`;
  if (key === "max_price") return `To $${value}`;
  return value;
}

export default function ActiveFilterChips({
  state,
  onRemove,
  onClearAll,
  className,
}: ActiveFilterChipsProps) {
  const active = FILTER_KEYS.filter(
    (k) => state[k] && state[k] !== "" && state[k] !== "false",
  );

  if (active.length === 0) return null;

  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      <span className="text-xs text-muted font-medium uppercase tracking-wider shrink-0">
        Filters:
      </span>
      {active.map((key) => (
        <button
          key={key}
          onClick={() => onRemove(key)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                     bg-brand/12 text-brand-soft border border-brand/25
                     hover:bg-brand/20 hover:border-brand/40 transition-colors"
        >
          <span className="text-muted text-[10px] uppercase tracking-wide">
            {LABEL_MAP[key]}:
          </span>
          {formatValue(key, state[key]!)}
          <span className="text-brand-soft/60 hover:text-brand-soft ml-0.5">✕</span>
        </button>
      ))}
      <button
        onClick={onClearAll}
        className="text-xs text-danger/80 hover:text-danger transition-colors px-2 py-1.5 
                   rounded-full hover:bg-danger/10"
      >
        Clear all
      </button>
    </div>
  );
}
