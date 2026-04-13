import { useState } from "react";
import ActiveFilterChips from "../components/ActiveFilterChips";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import FilterSidebar from "../components/FilterSidebar";
import Pagination from "../components/Pagination";
import ProductGrid from "../components/ProductGrid";
import SearchBar from "../components/SearchBar";
import { SkeletonGrid } from "../components/SkeletonCard";
import SortDropdown from "../components/SortDropdown";
import { useCatalogMeta } from "../hooks/useCatalogMeta";
import { useSearchParamsState } from "../hooks/useSearchParamsState";
import { useSearchResults } from "../hooks/useSearchResults";
import type { SearchState } from "../utils/searchParamsConfig";

export default function SearchPage() {
  const { state, patchState } = useSearchParamsState();
  const { data, loading, error, refetch } = useSearchResults(state);
  const { categories, brands } = useCatalogMeta();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSearch = (q: string) => patchState({ q });

  const handlePageChange = (page: number) => {
    patchState({ page: String(page) });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleClearAll = () => {
    patchState({
      category: "", brand: "", min_price: "", max_price: "",
      rating: "", in_stock: "", page: "1",
    });
  };

  const handleRemoveFilter = (key: keyof SearchState) => {
    patchState({ [key]: "" });
  };

  const currentPage = Number(state.page || 1);
  const pageSize   = Number(state.page_size || 20);
  const total      = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-canvas pt-16">
      {/* ─── Top search bar ────────────────────────────────────────── */}
      <div className="sticky top-16 z-40 bg-canvas/95 backdrop-blur-xl border-b border-line">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <SearchBar
            variant="page"
            initialQuery={state.q || ""}
            onSearch={handleSearch}
            placeholder="Search products, brands…"
            className="max-w-xl"
          />
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* ─── Filter sidebar (desktop) ─────────────────────────── */}
          <aside className="hidden lg:block w-60 shrink-0">
            <div className="sticky top-36">
              <FilterSidebar
                categories={categories}
                brands={brands}
                state={state}
                onChange={patchState}
                onClearAll={handleClearAll}
              />
            </div>
          </aside>

          {/* ─── Main content ─────────────────────────────────────── */}
          <div className="flex-1 min-w-0">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
              {/* Left: result count + mobile filter toggle */}
              <div className="flex items-center gap-3">
                {/* Mobile filter button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="lg:hidden flex items-center gap-1.5 px-3 py-2 rounded-xl bg-raised border border-line
                             text-sm text-muted hover:text-ink hover:border-brand/40 transition-all"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h18M6 10h12M9 16h6" />
                  </svg>
                  Filters
                </button>
                {/* Result count */}
                <div className="text-sm text-muted">
                  {loading ? (
                    <span className="animate-pulse">Searching…</span>
                  ) : error ? null : (
                    <>
                      <span className="font-semibold text-ink">{total.toLocaleString()}</span>
                      {" result"}{total !== 1 ? "s" : ""}
                      {state.q && (
                        <span className="ml-1">
                          for <span className="text-brand-soft font-medium">"{state.q}"</span>
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* Right: sort */}
              <SortDropdown
                value={state.sort || "relevance"}
                onChange={(v) => patchState({ sort: v })}
              />
            </div>

            {/* Active filter chips */}
            <ActiveFilterChips
              state={state}
              onRemove={handleRemoveFilter}
              onClearAll={handleClearAll}
              className="mb-5"
            />

            {/* Content states */}
            {error ? (
              <ErrorMessage
                title="Search failed"
                message={error.message}
                onRetry={refetch}
              />
            ) : loading ? (
              <SkeletonGrid count={12} />
            ) : data && data.results.length > 0 ? (
              <>
                <ProductGrid products={data.results} />
                <div className="mt-10">
                  <Pagination
                    page={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              </>
            ) : (
              <EmptyState
                title="No products found"
                message={
                  state.q
                    ? `We couldn't find anything matching "${state.q}". Try different keywords or clear the filters.`
                    : "Adjust your filters to discover products."
                }
                actionLabel="Clear all filters"
                onAction={handleClearAll}
              />
            )}
          </div>
        </div>
      </div>

      {/* ─── Mobile filter drawer ──────────────────────────────────── */}
      {sidebarOpen && (
        <>
          <div
            className="fixed inset-0 z-50 bg-canvas/80 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 z-50 w-72 bg-surface border-r border-line p-6
                          overflow-y-auto lg:hidden animate-fade-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-base font-bold text-ink">Filters</h2>
              <button
                onClick={() => setSidebarOpen(false)}
                className="w-8 h-8 rounded-xl flex items-center justify-center text-muted
                           hover:bg-raised hover:text-ink transition-all"
                aria-label="Close filters"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <FilterSidebar
              categories={categories}
              brands={brands}
              state={state}
              onChange={(patch) => { patchState(patch); setSidebarOpen(false); }}
              onClearAll={() => { handleClearAll(); setSidebarOpen(false); }}
            />
          </div>
        </>
      )}
    </div>
  );
}
