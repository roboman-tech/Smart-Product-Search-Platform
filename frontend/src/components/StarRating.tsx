import { cn } from "../lib/cn";

interface StarRatingProps {
  rating: number;
  count?: number;
  size?: "sm" | "md" | "lg";
  showCount?: boolean;
  className?: string;
}

/* Stable gradient IDs keyed on index — no Math.random() */
function StarIcon({
  filled,
  partial,
  gradId,
}: {
  filled: boolean;
  partial?: number;
  gradId: string;
}) {
  const PATH =
    "M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z";

  if (partial !== undefined && partial > 0 && partial < 1) {
    return (
      <svg viewBox="0 0 20 20" fill="none" className="w-full h-full">
        <defs>
          <linearGradient id={gradId}>
            <stop offset={`${partial * 100}%`} stopColor="#fbbf24" />
            <stop offset={`${partial * 100}%`} stopColor="#3a4a6e" />
          </linearGradient>
        </defs>
        <path d={PATH} fill={`url(#${gradId})`} />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 20 20" fill="none" className="w-full h-full">
      <path d={PATH} fill={filled ? "#fbbf24" : "#3a4a6e"} />
    </svg>
  );
}

/* sm shrunk to w-3/h-3 so 5 stars + text fit in narrow card columns */
const sizeClass = { sm: "w-3 h-3", md: "w-4 h-4", lg: "w-5 h-5" };
const textClass = { sm: "text-[11px]", md: "text-sm", lg: "text-base" };

export default function StarRating({
  rating,
  count,
  size = "sm",
  showCount = true,
  className,
}: StarRatingProps) {
  const clamped = Math.max(0, Math.min(5, rating));

  const stars = Array.from({ length: 5 }, (_, i) => {
    const val = clamped - i;
    if (val >= 1) return { filled: true, partial: undefined };
    if (val > 0)  return { filled: false, partial: val };
    return { filled: false, partial: undefined };
  });

  return (
    <div className={cn("flex items-center gap-1 flex-nowrap", className)}>
      {/* Stars block — never shrinks */}
      <div className="flex items-center gap-0.5 shrink-0">
        {stars.map((s, i) => (
          <span key={i} className={sizeClass[size]}>
            <StarIcon filled={s.filled} partial={s.partial} gradId={`sr-grad-${i}`} />
          </span>
        ))}
      </div>

      {/* Text — kept on one line */}
      {showCount && (
        <span
          className={cn(
            "whitespace-nowrap font-medium text-muted leading-none",
            textClass[size],
          )}
        >
          {clamped.toFixed(1)}
          {count !== undefined && (
            <span className="ml-1 text-faint">({count.toLocaleString()})</span>
          )}
        </span>
      )}
    </div>
  );
}
