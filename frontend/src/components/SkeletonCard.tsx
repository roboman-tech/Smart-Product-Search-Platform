import { cn } from "../lib/cn";

interface SkeletonCardProps {
  className?: string;
}

function SkeletonBlock({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded-lg", className)} />;
}

export default function SkeletonCard({ className }: SkeletonCardProps) {
  return (
    <div className={cn("card overflow-hidden p-0", className)}>
      {/* Image placeholder */}
      <SkeletonBlock className="w-full aspect-square" />
      {/* Content */}
      <div className="p-4 space-y-3">
        <SkeletonBlock className="h-3 w-1/3" />
        <SkeletonBlock className="h-4 w-4/5" />
        <SkeletonBlock className="h-3.5 w-2/3" />
        <div className="pt-1 flex items-center justify-between">
          <SkeletonBlock className="h-6 w-1/3" />
          <SkeletonBlock className="h-4 w-1/4" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonGrid({ count = 12 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
