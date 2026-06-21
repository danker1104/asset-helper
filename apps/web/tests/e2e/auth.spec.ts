import { expect, test } from "@playwright/test";

test("signup shows duplicate message when user_id/password/nickname overlaps", async ({ page }) => {
  const uniquePassword = `pw-${Date.now()}`;

  await page.goto("/");
  await page.getByLabel("auth-panel-toggle").click();

  await page.getByLabel("email-input").fill("dupe@example.com");

  await page.getByLabel("signup-user-id").fill(`dupe-user-${Date.now()}`);
  await page.getByLabel("signup-password").fill(uniquePassword);
  await page.getByLabel("signup-nickname").fill("중복닉");
  await page.getByLabel("signup-submit").click();

  await expect(page.getByLabel("login-user-id")).toBeVisible();

  await page.getByRole("button", { name: "회원가입" }).first().click();
  await page.getByLabel("signup-user-id").fill("new-user");
  await page.getByLabel("signup-password").fill(uniquePassword);
  await page.getByLabel("signup-nickname").fill("새닉");
  await page.getByLabel("signup-submit").click();

  await expect(page.getByTestId("signup-message")).toContainText("일치합니다.");
});

test("login success closes auth panel and onboarding shows only avatar type/intensity", async ({ page }) => {
  const uniquePassword = `pw-login-${Date.now()}`;
  const nickname = `로그인닉-${Date.now()}`;

  await page.goto("/");
  await page.getByLabel("auth-panel-toggle").click();

  await page.getByLabel("email-input").fill("login@example.com");
  await page.getByLabel("signup-user-id").fill(`login-user-${Date.now()}`);
  await page.getByLabel("signup-password").fill(uniquePassword);
  await page.getByLabel("signup-nickname").fill(nickname);
  await page.getByLabel("signup-submit").click();
  await expect(page.getByLabel("login-user-id")).toBeVisible();

  await page.getByLabel("login-password").fill(uniquePassword);
  await page.getByLabel("login-submit").click();

  await expect(page.getByLabel("auth-panel-toggle")).toHaveCount(0);
  await expect(page.getByLabel("logged-in-nickname")).toContainText(nickname);
  await expect(page.getByLabel("signup-user-id")).toHaveCount(0);
  await expect(page.getByLabel("email-input")).toHaveCount(0);
  await expect(page.getByLabel("text-mode-toggle")).toHaveCount(0);
  await expect(page.getByTestId("onboarding-summary")).toContainText("강도");
});
