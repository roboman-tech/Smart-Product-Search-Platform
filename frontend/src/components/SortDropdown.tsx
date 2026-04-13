import { cn } from "../lib/cn";

export const SORT_OPTIONS = [
  { value: "relevance",    label: "Most Relevant" },
  { value: "price_asc",   label: "Price: Low to High" },
  { value: "price_desc",  label: "Price: High to Low" },
  { value: "newest",      label: "Newest First" },
  { value: "rating",      label: "Highest Rated" },
  { value: "popularity",  label: "Most Popular" },
] as const;

interface SortDropdownProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export default function SortDropdown({ value, onChange, className }: SortDropdownProps) {
  return (
    <div className={cn("relative flex items-center gap-2", className)}>
      <span className="hidden sm:block text-xs text-muted font-medium whitespace-nowrap">Sort:</span>
      <div className="relative">
        <select
          value={value || "relevance"}
          onChange={(e) => onChange(e.target.value)}
          aria-label="Sort results"
          className="appearance-none h-9 pl-3 pr-8 rounded-xl bg-raised border border-line
                     text-sm text-text cursor-pointer input-glow transition-all
                     hover:border-brand/40 hover:text-ink"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <svg
          className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-faint pointer-events-none"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}
