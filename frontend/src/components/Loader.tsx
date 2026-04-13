import { cn } from "../lib/cn";

interface LoaderProps {
  fullPage?: boolean;
  size?: "sm" | "md" | "lg";
  label?: string;
  className?: string;
}

const sizeMap = {
  sm: "w-6 h-6 border-2",
  md: "w-9 h-9 border-[3px]",
  lg: "w-14 h-14 border-4",
};

export default function Loader({
  fullPage = false,
  size = "md",
  label = "Loading…",
  className,
}: LoaderProps) {
  const spinner = (
    <div
      role="status"
      aria-label={label}
      className={cn("flex flex-col items-center gap-3", className)}
    >
      <div
        className={cn(
          "rounded-full border-brand/20 border-t-brand animate-spin",
          sizeMap[size],
        )}
      />
      {size !== "sm" && (
        <span className="text-sm text-muted animate-pulse">{label}</span>
      )}
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-canvas/80 backdrop-blur-sm">
        {spinner}
      </div>
    );
  }

  return spinner;
}
