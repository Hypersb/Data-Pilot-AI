import { describe, expect, it } from "vitest";
import { ApiError, SessionExpiredError, isSessionExpiredError } from "@/lib/api";

describe("api errors", () => {
  it("identifies session expired errors", () => {
    const err = new SessionExpiredError();
    expect(isSessionExpiredError(err)).toBe(true);
    expect(isSessionExpiredError(new Error("x"))).toBe(false);
  });

  it("stores status on ApiError", () => {
    const err = new ApiError("bad", 500);
    expect(err.status).toBe(500);
    expect(err.message).toBe("bad");
  });
});
