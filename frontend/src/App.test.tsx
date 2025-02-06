import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renders without crashing", () => {
    render(<App />);
    expect(screen.getByText("PDF Booklet Tools")).toBeDefined();
  });

  it("shows tool options", () => {
    render(<App />);
    expect(screen.getByText("Reorder booklet pages")).toBeDefined();
    expect(screen.getByText("Scale to portrait")).toBeDefined();
  });
});
