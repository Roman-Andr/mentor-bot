import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/shared/ui/dialog";

describe("Dialog primitives", () => {
  it("detects nested descriptions and preserves wheel events inside content", () => {
    const onWheel = vi.fn();

    render(
      <Dialog open>
        <DialogContent onWheel={onWheel}>
          <>
            <DialogTitle>Details</DialogTitle>
            <DialogDescription>Nested description</DialogDescription>
          </>
        </DialogContent>
      </Dialog>,
    );

    const dialog = screen.getByRole("dialog");
    fireEvent.wheel(dialog);

    expect(dialog).toHaveAttribute("aria-describedby");
    expect(onWheel).toHaveBeenCalledOnce();
  });

  it("allows an explicit aria-describedby override", () => {
    render(
      <Dialog open>
        <DialogContent aria-describedby="custom-description">
          <DialogTitle>Details</DialogTitle>
          <DialogDescription id="custom-description">Custom description</DialogDescription>
        </DialogContent>
      </Dialog>,
    );

    expect(screen.getByRole("dialog")).toHaveAttribute("aria-describedby", "custom-description");
  });

  it("stops wheel events by default", () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogTitle>Details</DialogTitle>
        </DialogContent>
      </Dialog>,
    );

    const event = new WheelEvent("wheel", { bubbles: true });
    const stopPropagation = vi.spyOn(event, "stopPropagation");
    screen.getByRole("dialog").dispatchEvent(event);

    expect(stopPropagation).toHaveBeenCalledOnce();
  });
});
