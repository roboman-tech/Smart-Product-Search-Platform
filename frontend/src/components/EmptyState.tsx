import { cn } from "../lib/cn";

interface EmptyStateProps {
  title?: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
  className?: string;
}

function DefaultIcon() {
  return (
    <svg
      className="w-10 h-10 text-faint"
      fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.25}
    >
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
    </svg>
  );
}

export default function EmptyState({
  title = "No results found",
  message = "Try adjusting your search terms or clearing the filters.",
  actionLabel,
  onAction,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center py-20 px-6",
        className,
      )}
      aria-live="polite"
    >
      {/* Glow ring */}
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-3xl bg-raised border border-line flex items-center justify-center">
          {icon ?? <DefaultIcon />}
        </div>
        <div className="absolute inset-0 rounded-3xl bg-brand/5 blur-xl" />
      </div>
      <h3 className="text-xl font-semibold text-ink mb-2">{title}</h3>
      <p className="text-sm text-muted max-w-xs leading-relaxed">{message}</p>
      {onAction && actionLabel && (
        <button
          onClick={onAction}
          className="mt-6 px-6 py-2.5 rounded-xl bg-raised border border-line text-sm font-medium
                     text-text hover:border-brand/40 hover:text-ink transition-all"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
