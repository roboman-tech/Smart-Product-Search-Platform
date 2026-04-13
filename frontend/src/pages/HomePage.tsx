import { useNavigate } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import ProductGrid from "../components/ProductGrid";
import SearchBar from "../components/SearchBar";
import { useHomePageData } from "../hooks/useHomePageData";

const TRENDING_TAGS = [
  "Wireless Headphones", "Mechanical Keyboard", "Laptop Stand", "USB-C Hub",
  "Gaming Mouse", "Monitor", "Webcam", "Desk Lamp",
];

const CATEGORY_ICONS: Record<string, string> = {
  electronics: "💻",
  audio: "🎧",
  computers: "🖥️",
  gaming: "🎮",
  cameras: "📷",
  phones: "📱",
  accessories: "⌚",
  home: "🏠",
};

function getCategoryIcon(slug: string, name: string): string {
  const key = slug.toLowerCase();
  for (const [k, icon] of Object.entries(CATEGORY_ICONS)) {
    if (key.includes(k) || name.toLowerCase().includes(k)) return icon;
  }
  return "🛍️";
}

export default function HomePage() {
  const navigate = useNavigate();
  const { categories, brands, popular, loading, error, refetch } = useHomePageData();

  const handleSearch = (q: string) => {
    if (q) navigate(`/search?q=${encodeURIComponent(q)}`);
    else navigate("/search");
  };

  return (
    <div className="min-h-screen bg-canvas">
      {/* ─── Hero ─────────────────────────────────────────────────── */}
      <section className="hero-glow pt-32 pb-24 px-4 sm:px-6 lg:px-8 text-center relative overflow-hidden">
        {/* Decorative orbs */}
        <div className="pointer-events-none select-none absolute top-1/4 left-1/4 w-64 h-64 rounded-full
                        bg-brand/5 blur-3xl" />
        <div className="pointer-events-none select-none absolute top-1/3 right-1/4 w-80 h-80 rounded-full
                        bg-indigo-500/5 blur-3xl" />

        <div className="relative max-w-3xl mx-auto">
          {/* Kicker */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand/10 border border-brand/20
                          text-brand-soft text-xs font-semibold tracking-wide mb-8 animate-fade-up">
            <span className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
            Smart Product Discovery
          </div>

          {/* Headline */}
          <h1
            className="text-4xl sm:text-5xl lg:text-6xl font-black leading-tight tracking-tight mb-6 animate-fade-up"
            style={{ animationDelay: "60ms" }}
          >
            <span className="text-ink">Find Your Next</span>
            <br />
            <span className="brand-text">Favorite Product</span>
          </h1>

          {/* Subline */}
          <p
            className="text-base sm:text-lg text-muted max-w-xl mx-auto mb-10 leading-relaxed animate-fade-up"
            style={{ animationDelay: "120ms" }}
          >
            Search, filter, and discover thousands of products with smart recommendations
            tailored to your taste.
          </p>

          {/* Search bar */}
          <div className="animate-fade-up" style={{ animationDelay: "180ms" }}>
            <SearchBar
              variant="hero"
              onSearch={handleSearch}
              placeholder="Search products, brands, categories…"
            />
          </div>

          {/* Trending tags */}
          <div
            className="mt-8 flex flex-wrap items-center justify-center gap-2 animate-fade-up"
            style={{ animationDelay: "240ms" }}
          >
            <span className="text-xs text-muted font-medium mr-1">Trending:</span>
            {TRENDING_TAGS.map((tag) => (
              <button
                key={tag}
                onClick={() => handleSearch(tag)}
                className="px-3 py-1.5 rounded-full text-xs font-medium bg-raised border border-line
                           text-muted hover:text-ink hover:border-brand/40 hover:bg-brand/8 transition-all"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Stats bar */}
        <div
          className="mt-16 flex flex-wrap items-center justify-center gap-8 sm:gap-16 animate-fade-up"
          style={{ animationDelay: "300ms" }}
        >
          {[
            { label: "Products",   value: "50+" },
            { label: "Categories", value: `${categories.length || "—"}` },
            { label: "Brands",     value: `${brands.length    || "—"}` },
            { label: "In stock",   value: "100%" },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <div className="text-2xl font-black text-ink">{value}</div>
              <div className="text-xs text-muted mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Categories ───────────────────────────────────────────── */}
      {!loading && categories.length > 0 && (
        <section className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-end justify-between mb-8">
            <div>
              <p className="text-xs text-brand-soft font-semibold uppercase tracking-widest mb-2">Browse by</p>
              <h2 className="text-2xl font-bold text-ink">Categories</h2>
            </div>
            <button
              onClick={() => navigate("/search")}
              className="text-sm text-muted hover:text-ink transition-colors flex items-center gap-1.5"
            >
              View all
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {categories.slice(0, 12).map((cat, i) => (
              <button
                key={cat.id}
                onClick={() =>
                  navigate(`/search?category=${encodeURIComponent(cat.slug)}`)
                }
                className="group card flex flex-col items-center gap-3 p-5 text-center animate-fade-up"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <div className="w-12 h-12 rounded-2xl bg-brand/10 flex items-center justify-center text-2xl
                                group-hover:bg-brand/20 transition-colors">
                  {getCategoryIcon(cat.slug, cat.name)}
                </div>
                <span className="text-xs font-semibold text-muted group-hover:text-ink transition-colors truncate w-full">
                  {cat.name}
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* ─── Popular products ─────────────────────────────────────── */}
      <section className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-end justify-between mb-8">
          <div>
            <p className="text-xs text-brand-soft font-semibold uppercase tracking-widest mb-2">Trending now</p>
            <h2 className="text-2xl font-bold text-ink">Popular Products</h2>
          </div>
          <button
            onClick={() => navigate("/search?sort=popularity")}
            className="text-sm text-muted hover:text-ink transition-colors flex items-center gap-1.5"
          >
            See all
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {error ? (
          <ErrorMessage
            title="Couldn't load products"
            message={error.message}
            onRetry={refetch}
          />
        ) : (
          <ProductGrid products={popular} loading={loading} />
        )}
      </section>

      {/* ─── Brands ───────────────────────────────────────────────── */}
      {!loading && brands.length > 0 && (
        <section className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-line">
          <p className="text-xs text-muted font-semibold uppercase tracking-widest text-center mb-8">
            Top Brands
          </p>
          <div className="scroll-row justify-center">
            {brands.slice(0, 12).map((brand) => (
              <button
                key={brand.id}
                onClick={() =>
                  navigate(`/search?brand=${encodeURIComponent(brand.slug)}`)
                }
                className="shrink-0 px-5 py-3 rounded-2xl bg-raised border border-line
                           text-sm font-semibold text-muted hover:text-ink hover:border-brand/40
                           hover:bg-brand/8 transition-all"
              >
                {brand.name}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Loading state covers everything */}
      {loading && (
        <div className="flex items-center justify-center py-32">
          <Loader size="lg" label="Loading…" />
        </div>
      )}

      {/* ─── Footer ───────────────────────────────────────────────── */}
      <footer className="border-t border-line mt-8 py-10 text-center">
        <p className="text-xs text-faint">
          © {new Date().getFullYear()} NexusMarket · Built with React & Django
        </p>
      </footer>
    </div>
  );
}
