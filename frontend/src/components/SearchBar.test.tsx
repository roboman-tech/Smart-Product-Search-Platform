import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import SearchBar from "./SearchBar";

describe("SearchBar", () => {
  it("calls onSearch when form is submitted", async () => {
    const user = userEvent.setup();
    const onSearch = vi.fn();
    render(<SearchBar onSearch={onSearch} />);
    await user.type(screen.getByRole("searchbox"), "laptop");
    await user.click(screen.getByRole("button", { name: /^go$/i }));
    expect(onSearch).toHaveBeenCalledWith("laptop");
  });
});
