import { test, expect } from "@playwright/test";

test.describe("Prisma AI smoke", () => {
  test("landing page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Turn Data Into/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Upload/i }).first()).toBeVisible();
  });

  test("upload page loads", async ({ page }) => {
    await page.goto("/upload");
    await expect(page.getByText(/upload|dataset/i).first()).toBeVisible();
  });

  test("404 page is branded", async ({ page }) => {
    await page.goto("/this-route-does-not-exist");
    await expect(page.getByText("Page not found")).toBeVisible();
  });
});
