import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Button } from "@/shared/ui/button";

describe("Button", () => {
  it("renders with default props", () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole("button", { name: "Click me" });
    expect(button).toBeInTheDocument();
  });

  it("renders with variant", () => {
    render(<Button variant="destructive">Delete</Button>);
    const button = screen.getByRole("button", { name: "Delete" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("bg-destructive");
  });

  it("renders with size", () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByRole("button", { name: "Small" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("h-8");
  });

  it("renders with custom className", () => {
    render(<Button className="custom-class">Custom</Button>);
    const button = screen.getByRole("button", { name: "Custom" });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("custom-class");
  });

  it("handles click events", async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole("button", { name: "Click me" });
    button.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole("button", { name: "Disabled" });
    expect(button).toBeDisabled();
  });

  it("renders as child when asChild is true", () => {
    render(
      <Button asChild>
        <a href="/test">Link</a>
      </Button>,
    );
    const link = screen.getByRole("link", { name: "Link" });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/test");
  });

  it("passes through HTML button attributes", () => {
    render(
      <Button type="submit" form="test-form">
        Submit
      </Button>,
    );
    const button = screen.getByRole("button", { name: "Submit" });
    expect(button).toHaveAttribute("type", "submit");
    expect(button).toHaveAttribute("form", "test-form");
  });

  it("uses button text as a tooltip title by default", () => {
    render(<Button>Save changes</Button>);
    expect(screen.getByRole("button", { name: "Save changes" })).toHaveAttribute(
      "title",
      "Save changes",
    );
  });

  it("uses aria-label as a tooltip title for icon-only buttons", () => {
    render(<Button aria-label="Close dialog" size="icon" />);
    expect(screen.getByRole("button", { name: "Close dialog" })).toHaveAttribute(
      "title",
      "Close dialog",
    );
  });

  it("prefers an explicit title over aria-label and children", () => {
    render(
      <Button aria-label="Save" title="Persist form">
        Save changes
      </Button>,
    );

    expect(screen.getByRole("button", { name: "Save" })).toHaveAttribute("title", "Persist form");
  });

  it("joins string and number children for tooltip titles", () => {
    render(<Button>Page {2}</Button>);

    expect(screen.getByRole("button", { name: "Page 2" })).toHaveAttribute("title", "Page 2");
  });
});
