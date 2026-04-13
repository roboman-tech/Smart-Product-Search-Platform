import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { cn } from "../lib/cn";

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-canvas/95 backdrop-blur-xl border-b border-line shadow-lg shadow-black/30"
          : "bg-transparent",
      )}
    >
      <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-6">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2.5 shrink-0 group"
          aria-label="NexusMarket home"
        >
          <div className="w-8 h-8 rounded-xl bg-brand/20 border border-brand/30 flex items-center justify-center group-hover:bg-brand/30 transition-colors">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="w-4.5 h-4.5 text-brand-soft"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
              />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight">
            <span className="text-ink">Nexus</span>
            <span className="brand-text">Market</span>
          </span>
        </Link>

        {/* Compact search — hidden on small screens */}
        <form
          onSubmit={handleSearch}
          className="hidden md:flex flex-1 max-w-lg relative"
        >
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search products, brands…"
            autoComplete="off"
            className="w-full h-9 pl-10 pr-4 rounded-xl bg-raised border border-line text-sm text-text
                       placeholder:text-faint input-glow transition-all"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-faint pointer-events-none"
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
        </form>

        {/* Spacer */}
        <div className="flex-1 md:hidden" />

        {/* Nav links */}
        <nav className="hidden sm:flex items-center gap-1">
          <Link
            to="/"
            className="px-3 py-2 rounded-lg text-sm text-muted hover:text-ink hover:bg-raised transition-all"
          >
            Home
          </Link>
          <Link
            to="/search"
            className="px-3 py-2 rounded-lg text-sm text-muted hover:text-ink hover:bg-raised transition-all"
          >
            Browse
          </Link>
        </nav>

        {/* CTA */}
        <Link
          to="/search"
          className="shrink-0 px-4 py-2 rounded-xl bg-brand hover:bg-brand-dim text-white text-sm font-semibold
                     transition-all shadow-lg shadow-brand/20 hover:shadow-brand/35"
        >
          <span className="hidden sm:inline">Explore</span>
          <span className="sm:hidden">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </span>
        </Link>
      </div>
    </header>
  );
}
