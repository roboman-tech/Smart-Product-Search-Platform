import { useEffect, useState } from "react";
import { cn } from "../lib/cn";
import type { ProductImage } from "../types/product";

interface ProductImageGalleryProps {
  images: ProductImage[];
  productName: string;
  className?: string;
}

export default function ProductImageGallery({
  images,
  productName,
  className,
}: ProductImageGalleryProps) {
  const [activeIdx, setActiveIdx] = useState(0);

  useEffect(() => {
    setActiveIdx(0);
  }, [images]);

  if (images.length === 0) {
    return (
      <div className={cn("aspect-square rounded-2xl bg-raised border border-line flex items-center justify-center", className)}>
        <svg
          className="w-16 h-16 text-faint"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}
        >
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 19.5h18M3 4.5h18" />
        </svg>
      </div>
    );
  }

  const active = images[activeIdx];

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      {/* Main image */}
      <div
        className="relative aspect-square rounded-2xl overflow-hidden bg-raised border border-line
                   group cursor-zoom-in"
      >
        <img
            key={active.image_url}
            src={active.image_url}
            alt={productName}
            className="w-full h-full object-cover transition-all duration-500 group-hover:scale-105"
          />
        {/* Zoom hint */}
        <div className="absolute bottom-3 right-3 w-8 h-8 rounded-xl bg-surface/70 backdrop-blur-sm
                        border border-line flex items-center justify-center opacity-0 group-hover:opacity-100
                        transition-opacity">
          <svg className="w-4 h-4 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M15 10h-2m0 0H11m2 0V8m0 2v2M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
        </div>

        {/* Navigation arrows for multiple images */}
        {images.length > 1 && (
          <>
            <button
              onClick={() => setActiveIdx((i) => (i - 1 + images.length) % images.length)}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-xl bg-surface/80
                         backdrop-blur-sm border border-line flex items-center justify-center
                         text-muted hover:text-ink transition-all opacity-0 group-hover:opacity-100"
              aria-label="Previous image"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={() => setActiveIdx((i) => (i + 1) % images.length)}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-xl bg-surface/80
                         backdrop-blur-sm border border-line flex items-center justify-center
                         text-muted hover:text-ink transition-all opacity-0 group-hover:opacity-100"
              aria-label="Next image"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </>
        )}
      </div>

      {/* Thumbnails */}
      {images.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1 scroll-row">
          {images.map((img, idx) => (
            <button
              key={img.id}
              onClick={() => setActiveIdx(idx)}
              aria-label={`View image ${idx + 1}`}
              className={cn(
                "shrink-0 w-16 h-16 rounded-xl overflow-hidden border-2 transition-all",
                idx === activeIdx
                  ? "border-brand shadow-lg shadow-brand/25"
                  : "border-line hover:border-brand/40 opacity-60 hover:opacity-100",
              )}
            >
              <img
                src={img.image_url}
                alt={`${productName} ${idx + 1}`}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
