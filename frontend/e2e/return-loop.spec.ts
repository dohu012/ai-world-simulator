import { expect, test } from "@playwright/test";

const response = {
  summary: {
    id: "summary-e2e",
    source_watermark: "a".repeat(64),
    claims: [
      {
        id: "claim-e2e",
        source_id: "scenario-rescue",
        epistemic_class: "outcome",
        text: "Ten rescue seats were allocated.",
        visible_at: "2026-07-07T08:01:00Z",
      },
    ],
    narrative: ["[outcome] Ten rescue seats were allocated."],
  },
  inbox: [
    {
      id: "inbox-e2e",
      title: "Fictional world summary is ready",
      preview: "One source-linked change.",
      read: false,
    },
  ],
  preferences: {
    push_enabled: false,
    timezone: "UTC",
    inbox_daily_cap: 4,
    push_daily_cap: 1,
  },
  debug: { summary_mode: "deterministic", provider_calls: 0 },
};

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(Notification, "requestPermission", {
      configurable: true,
      value: async () => {
        const windowWithCounter = window as typeof window & {
          permissionRequestCount?: number;
        };
        windowWithCounter.permissionRequestCount =
          (windowWithCounter.permissionRequestCount ?? 0) + 1;
        return "denied" as NotificationPermission;
      },
    });
  });
  await page.route("**/api/demo/worlds/gray-harbor/me/return-loop", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(response),
    }),
  );
  await page.route(
    "**/api/demo/worlds/gray-harbor/me/return-loop/inbox/**",
    (route) => {
      response.inbox[0].read = true;
      return route.fulfill({ status: 204, body: "" });
    },
  );
});

test("no-push return loop remains complete and installs the safe worker", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "离线期间发生了什么" }),
  ).toBeVisible();
  await expect(page.getByText("浏览器推送默认关闭")).toBeVisible();
  await expect(
    page.getByText("Ten rescue seats were allocated", { exact: false }),
  ).toBeVisible();
  await expect(page.getByText("模型/提供商调用").locator("..")).toContainText(
    "0",
  );
  await expect
    .poll(() =>
      page.evaluate(() => navigator.serviceWorker.ready.then(() => true)),
    )
    .toBe(true);
  await expect(page.getByRole("button", { name: "标为已读" })).toBeEnabled();
});

test("permission remains untouched and is offered only as a gesture control", async ({
  page,
}) => {
  await page.goto("/");
  const initial = await page.evaluate(() => Notification.permission);
  expect(initial).toBe("default");
  expect(
    await page.evaluate(
      () =>
        (window as typeof window & { permissionRequestCount?: number })
          .permissionRequestCount ?? 0,
    ),
  ).toBe(0);
  const button = page.getByRole("button", { name: "主动检查浏览器通知权限" });
  await expect(button).toBeVisible();
});
