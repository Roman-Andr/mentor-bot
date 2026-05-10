import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FormDialog } from "@/shared/ui/form-dialog";

vi.mock("next-intl", () => ({
  useTranslations: (ns?: string) => (key: string) => `${ns ? ns + "." : ""}${key}`,
}));

vi.mock("@/shared/hooks/use-translations", () => ({
  useTranslations: (ns?: string) => (key: string) => `${ns ? ns + "." : ""}${key}`,
}));

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  title: "Test Dialog",
  onSubmit: vi.fn(),
  onCancel: vi.fn(),
  children: <div>Form content</div>,
};

describe("FormDialog", () => {
  it("renders title and children", () => {
    render(<FormDialog {...defaultProps} />);
    expect(screen.getByText("Test Dialog")).toBeDefined();
    expect(screen.getByText("Form content")).toBeDefined();
  });

  it("renders description when provided", () => {
    render(<FormDialog {...defaultProps} description="A description" />);
    expect(screen.getByText("A description")).toBeDefined();
  });

  it("calls onSubmit when submit button clicked", () => {
    const onSubmit = vi.fn();
    render(<FormDialog {...defaultProps} onSubmit={onSubmit} />);
    fireEvent.click(screen.getAllByRole("button")[1]);
    expect(onSubmit).toHaveBeenCalledOnce();
  });

  it("calls onCancel when cancel button clicked", () => {
    const onCancel = vi.fn();
    render(<FormDialog {...defaultProps} onCancel={onCancel} />);
    fireEvent.click(screen.getAllByRole("button")[0]);
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("disables buttons when isSubmitting=true", () => {
    render(<FormDialog {...defaultProps} isSubmitting={true} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons[0]).toHaveProperty("disabled", true);
    expect(buttons[1]).toHaveProperty("disabled", true);
  });

  it("disables submit when canSubmit=false", () => {
    render(<FormDialog {...defaultProps} canSubmit={false} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons[1]).toHaveProperty("disabled", true);
  });

  it('shows "save" label in edit mode', () => {
    render(<FormDialog {...defaultProps} mode="edit" />);
    expect(screen.getByText("common.save")).toBeDefined();
  });

  it('shows "add" label in create mode', () => {
    render(<FormDialog {...defaultProps} mode="create" />);
    expect(screen.getByText("common.add")).toBeDefined();
  });

  it("shows custom submitLabel when provided", () => {
    render(<FormDialog {...defaultProps} submitLabel="Custom Submit" />);
    expect(screen.getByText("Custom Submit")).toBeDefined();
  });

  it("shows custom cancelLabel when provided", () => {
    render(<FormDialog {...defaultProps} cancelLabel="Go Back" />);
    expect(screen.getByText("Go Back")).toBeDefined();
  });

  it("shows saving text when isSubmitting and no submitLabel", () => {
    render(<FormDialog {...defaultProps} isSubmitting={true} />);
    expect(screen.getByText("common.saving")).toBeDefined();
  });

  it("shows saving text even when submitLabel is provided", () => {
    render(<FormDialog {...defaultProps} submitLabel="Send" isSubmitting={true} />);
    expect(screen.getByText("common.saving")).toBeDefined();
    expect(screen.queryByText("Send")).toBeNull();
  });
});
