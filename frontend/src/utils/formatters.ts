export function formatPrice(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) {
    return String(value);
  }
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
  }).format(n);
}

export function formatRating(value: string | number): string {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) {
    return String(value);
  }
  return n.toFixed(1);
}
