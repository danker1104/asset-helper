import { expect, test } from "@playwright/test";

test("onboarding shows selected profile and hp calculator", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("email-input").fill("alice@example.com");
  await page.getByLabel("avatar-type-select").selectOption("character");
  await page.getByLabel("intensity-select").selectOption("3");
  await page.getByLabel("text-mode-toggle").check();

  await expect(page.getByTestId("onboarding-summary")).toContainText("alice@example.com");
  await expect(page.getByTestId("onboarding-summary")).toContainText("character");
  await expect(page.getByTestId("onboarding-summary")).toContainText("강도 3");
  await expect(page.getByTestId("onboarding-summary")).toContainText("텍스트 모드");
});
