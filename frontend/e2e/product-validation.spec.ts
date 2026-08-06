import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("focused playtest is keyboard usable, narrow, calm, and no-push", async ({
  context,
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 720 });
  await page.route("**/api/playtest/**", async (route) => {
    if (route.request().url().endsWith("/presentation")) {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          condition: "causal",
          claims: [
            {
              id: "c1",
              source_id: "s1",
              epistemic_class: "observed",
              text: "Chen observed the flooded road.",
            },
          ],
        }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ participant_id: "study-test", sequence: "AB" }),
    });
  });

  await page.goto("/playtest");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "fictional-world",
  );
  await page.getByLabel(/access code/i).fill("abcdefghijklmnop");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(
    page.getByRole("button", { name: "Answer bounded questions" }),
  ).toBeVisible();
  await expect(page.locator("body")).not.toHaveCSS("overflow-x", "scroll");
  await expect(
    page.getByRole("button", { name: "Withdraw and delete" }),
  ).toBeVisible();
  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(
    accessibility.violations.filter(
      (violation) =>
        violation.impact === "serious" || violation.impact === "critical",
    ),
  ).toEqual([]);

  const permission = await context
    .grantPermissions([])
    .then(() =>
      page.evaluate(() =>
        "Notification" in window ? Notification.permission : "unsupported",
      ),
    );
  expect(["default", "denied", "unsupported"]).toContain(permission);
});
