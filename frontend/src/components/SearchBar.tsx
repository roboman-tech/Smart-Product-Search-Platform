import { useEffect, useState } from "react";
import { cn } from "../lib/cn";

interface SearchBarProps {
  initialQuery?: string;
  onSearch: (query: string) => void;
  placeholder?: string;
  variant?: "hero" | "page";
  className?: string;
}

export default function SearchBar({
  initialQuery = "",
  onSearch,
  placeholder = "Search products, brands, categories…",
  variant = "page",
  className,
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    setQuery(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSearch(query.trim());
  };

  const handleClear = () => {
    setQuery("");
    onSearch("");
  };

  if (variant === "hero") {
    return (
      <form
        onSubmit={handleSubmit}
        className={cn("relative w-full max-w-2xl mx-auto", className)}
        role="search"
      >
        <div
          className="relative flex items-center rounded-2xl overflow-hidden
                     bg-surface/90 backdrop-blur-sm border border-line
                     focus-within:border-brand/60 focus-within:shadow-[0_0_0_3px_rgba(124,58,237,0.18)]
                     transition-all duration-200"
        >
          <svg
            className="absolute left-5 w-5 h-5 text-muted pointer-events-none"
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            autoComplete="off"
            aria-label="Search products"
            className="flex-1 h-14 pl-14 pr-4 text-base text-ink bg-transparent
                       placeholder:text-muted focus:outline-none"
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 mr-2 text-faint hover:text-muted transition-colors rounded-lg"
              aria-label="Clear search"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          <button
            type="submit"
            className="m-1.5 px-6 h-11 rounded-xl bg-brand hover:bg-brand-dim text-white font-semibold text-sm
                       transition-all shadow-lg shadow-brand/25 hover:shadow-brand/40 shrink-0"
          >
            Search
          </button>
        </div>
      </form>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={cn("relative flex items-center", className)}
      role="search"
    >
      <svg
        className="absolute left-3.5 w-4 h-4 text-faint pointer-events-none"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round"
          d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
      </svg>
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        autoComplete="off"
        aria-label="Search products"
        className="w-full h-10 pl-10 pr-10 rounded-xl bg-raised border border-line text-sm text-text
                   placeholder:text-faint input-glow transition-all"
      />
      {query && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-10 p-1.5 text-faint hover:text-muted transition-colors"
          aria-label="Clear search"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
      <button
        type="submit"
        className="absolute right-1.5 px-3 h-7 rounded-lg bg-brand/15 hover:bg-brand/25
                   text-brand-soft text-xs font-semibold transition-colors"
        aria-label="Submit search"
      >
        Go
      </button>
    </form>
  );
}
