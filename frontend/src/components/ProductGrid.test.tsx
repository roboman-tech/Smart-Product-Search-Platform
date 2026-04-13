import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import type { ProductListItem } from "../types/product";
import ProductGrid from "./ProductGrid";

const sample: ProductListItem = {
  id: 1,
  name: "Test Product",
  slug: "test-product",
  price: 10,
  discount_price: null,
  rating: 4.5,
  review_count: 3,
  stock_quantity: 2,
  brand: { id: 1, name: "B" },
  category: { id: 1, name: "C" },
  primary_image: null,
};

describe("ProductGrid", () => {
  it("renders product cards", () => {
    render(
      <MemoryRouter>
        <ProductGrid products={[sample]} />
      </MemoryRouter>
    );
    expect(screen.getByText("Test Product")).toBeInTheDocument();
  });
});
