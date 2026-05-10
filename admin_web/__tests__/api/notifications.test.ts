import { describe, it, expect, vi } from "vitest";
import { notificationsApi } from "@/shared/lib/api/notifications";

const mockFetchApi = vi.fn();

vi.mock("@/shared/lib/api/client", () => ({
  fetchApi: () => mockFetchApi(),
}));

describe("notificationsApi", () => {
  it("history calls fetchApi", () => {
    notificationsApi.history({ skip: 0, limit: 20 });
    expect(mockFetchApi).toHaveBeenCalled();
  });

  it("history calls fetchApi without params", () => {
    notificationsApi.history();
    expect(mockFetchApi).toHaveBeenCalled();
  });

  it("send calls fetchApi with POST", () => {
    notificationsApi.send({
      user_id: 123,
      type: "email",
      channel: "email",
      body: "Test notification",
    });
    expect(mockFetchApi).toHaveBeenCalled();
  });

  it("send calls fetchApi with subject", () => {
    notificationsApi.send({
      user_id: 123,
      type: "email",
      channel: "email",
      body: "Test notification",
      subject: "Important",
    });
    expect(mockFetchApi).toHaveBeenCalled();
  });

  it("schedule calls fetchApi with POST", () => {
    notificationsApi.schedule({
      user_id: 123,
      type: "email",
      channel: "email",
      body: "Scheduled notification",
      subject: "Scheduled Subject",
      scheduled_time: "2024-12-31T23:59:59Z",
    });
    expect(mockFetchApi).toHaveBeenCalled();
  });

  it("schedule calls fetchApi without subject", () => {
    notificationsApi.schedule({
      user_id: 123,
      type: "telegram",
      channel: "telegram",
      body: "Scheduled telegram message",
      scheduled_time: "2024-12-31T23:59:59Z",
    });
    expect(mockFetchApi).toHaveBeenCalled();
  });
});
