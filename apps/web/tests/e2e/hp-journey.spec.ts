import { expect, test } from "@playwright/test";

test("manual payment lowers hp on the dashboard", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("baseline-input").fill("30000");
  await page.getByLabel("amount-input").fill("60000");
  await page.getByRole("button", { name: "HP 계산하기" }).click();

  await expect(page.getByTestId("hp-value")).toHaveText("0");
  await expect(page.getByText("회복 액션을 권장합니다.")).toBeVisible();
});
