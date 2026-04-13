import { cn } from "../lib/cn";

type Variant = "brand" | "success" | "danger" | "warning" | "neutral" | "outline";

interface BadgeProps {
  children: React.ReactNode;
  variant?: Variant;
  size?: "sm" | "md";
  className?: string;
}

const variantClass: Record<Variant, string> = {
  brand:   "bg-brand/15 text-brand-soft border border-brand/25",
  success: "bg-success/15 text-success  border border-success/25",
  danger:  "bg-danger/15  text-danger   border border-danger/25",
  warning: "bg-warning/15 text-warning  border border-warning/25",
  neutral: "bg-raised text-muted border border-line",
  outline: "bg-transparent text-muted border border-line",
};

export default function Badge({
  children,
  variant = "neutral",
  size = "sm",
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full font-medium leading-none",
        size === "sm" ? "px-2.5 py-1 text-[10px] tracking-wide uppercase" : "px-3 py-1.5 text-xs",
        variantClass[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
