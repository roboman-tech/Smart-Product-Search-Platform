import { useState } from "react";
import { cn } from "../lib/cn";
import type { Brand, Category } from "../types/product";
import type { SearchState } from "../utils/searchParamsConfig";

interface FilterSidebarProps {
  categories: Category[];
  brands: Brand[];
  state: SearchState;
  onChange: (patch: Partial<SearchState>) => void;
  onClearAll?: () => void;
  className?: string;
}

function Section({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-line py-4">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center justify-between w-full text-left group"
      >
        <span className="text-sm font-semibold text-ink group-hover:text-brand-soft transition-colors">
          {title}
        </span>
        <svg
          className={cn(
            "w-4 h-4 text-faint transition-transform duration-200",
            open && "rotate-180",
          )}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
}

function FilterOption({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2.5 w-full px-2.5 py-1.5 rounded-lg text-sm transition-all text-left",
        active
          ? "bg-brand/12 text-brand-soft font-medium"
          : "text-muted hover:text-ink hover:bg-raised",
      )}
    >
      <span
        className={cn(
          "w-4 h-4 rounded-[4px] border flex items-center justify-center shrink-0 transition-all",
          active ? "bg-brand border-brand" : "border-line",
        )}
      >
        {active && (
          <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </span>
      {children}
    </button>
  );
}

export default function FilterSidebar({
  categories,
  brands,
  state,
  onChange,
  onClearAll,
  className,
}: FilterSidebarProps) {
  const hasFilters = !!(
    state.category || state.brand || state.min_price || state.max_price || state.rating || state.in_stock
  );

  const ratingOptions = ["4", "3", "2", "1"];

  return (
    <aside className={cn("w-full", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-brand-soft" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 010 2H4a1 1 0 01-1-1zM6 10h12M9 16h6" />
          </svg>
          <h2 className="text-sm font-bold text-ink">Filters</h2>
        </div>
        {hasFilters && onClearAll && (
          <button
            onClick={onClearAll}
            className="text-xs text-danger/70 hover:text-danger transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Category */}
      {categories.length > 0 && (
        <Section title="Category">
          <div className="space-y-0.5 max-h-52 overflow-y-auto pr-1">
            {categories.map((cat) => (
              <FilterOption
                key={cat.id}
                active={state.category === cat.slug}
                onClick={() =>
                  onChange({ category: state.category === cat.slug ? "" : cat.slug })
                }
              >
                {cat.name}
              </FilterOption>
            ))}
          </div>
        </Section>
      )}

      {/* Brand */}
      {brands.length > 0 && (
        <Section title="Brand" defaultOpen={false}>
          <div className="space-y-0.5 max-h-52 overflow-y-auto pr-1">
            {brands.map((brand) => (
              <FilterOption
                key={brand.id}
                active={state.brand === brand.slug}
                onClick={() =>
                  onChange({ brand: state.brand === brand.slug ? "" : brand.slug })
                }
              >
                {brand.name}
              </FilterOption>
            ))}
          </div>
        </Section>
      )}

      {/* Price range */}
      <Section title="Price Range" defaultOpen={false}>
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-faint">$</span>
            <input
              type="number"
              min={0}
              placeholder="Min"
              value={state.min_price ?? ""}
              onChange={(e) => onChange({ min_price: e.target.value })}
              className="w-full h-9 pl-6 pr-2 rounded-lg bg-raised border border-line text-sm text-text
                         placeholder:text-faint input-glow transition-all"
            />
          </div>
          <span className="text-faint text-xs shrink-0">—</span>
          <div className="relative flex-1">
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-xs text-faint">$</span>
            <input
              type="number"
              min={0}
              placeholder="Max"
              value={state.max_price ?? ""}
              onChange={(e) => onChange({ max_price: e.target.value })}
              className="w-full h-9 pl-6 pr-2 rounded-lg bg-raised border border-line text-sm text-text
                         placeholder:text-faint input-glow transition-all"
            />
          </div>
        </div>
      </Section>

      {/* Rating */}
      <Section title="Minimum Rating" defaultOpen={false}>
        <div className="space-y-0.5">
          {ratingOptions.map((r) => (
            <FilterOption
              key={r}
              active={state.rating === r}
              onClick={() => onChange({ rating: state.rating === r ? "" : r })}
            >
              <div className="flex items-center gap-1.5">
                <span className="text-warning text-sm">{"★".repeat(Number(r))}</span>
                <span className="text-muted text-xs">& up</span>
              </div>
            </FilterOption>
          ))}
        </div>
      </Section>

      {/* Stock */}
      <Section title="Availability" defaultOpen={false}>
        <FilterOption
          active={state.in_stock === "true"}
          onClick={() =>
            onChange({ in_stock: state.in_stock === "true" ? "" : "true" })
          }
        >
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success shrink-0" />
            In stock only
          </span>
        </FilterOption>
      </Section>
    </aside>
  );
}
