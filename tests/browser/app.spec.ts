import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";

async function send(page: import("@playwright/test").Page, text: string) {
  await page.getByLabel("Your SQL or database question").fill(text);
  await page
    .getByRole("button", { name: "Send question", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Cancel request" }),
  ).toHaveCount(0);
}

test("real query, follow-up, execution, explanation, plan and exports", async ({
  page,
  context,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/");
  await expect(
    page.getByText("Sample database connected", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: /Explore your customers/ }).click();
  await expect(page.getByLabel("Validated SQL")).toContainText("California");
  await expect(page.getByRole("tabpanel")).toContainText("30 rows returned");
  await send(page, "Sort by name");
  await expect(page.getByLabel("Validated SQL")).toContainText("ORDER BY");
  await expect(page.getByLabel("Validated SQL")).toContainText("California");
  await page.getByRole("button", { name: "Copy SQL", exact: true }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain(
    "SELECT",
  );
  const sqlDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download SQL", exact: true }).click();
  const sql = await sqlDownload;
  expect(await readFile((await sql.path())!, "utf8")).toContain("California");
  const csvDownload = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export CSV", exact: true }).click();
  const csv = await csvDownload;
  expect(await readFile((await csv.path())!, "utf8")).toContain("California");
  await page.getByRole("tab", { name: "Explanation", exact: true }).click();
  await expect(page.getByRole("tabpanel")).toContainText(
    "Independent validation",
  );
  await page.getByRole("tab", { name: "Query plan", exact: true }).click();
  await expect(page.getByRole("tabpanel")).toContainText(
    "SQLite planner heuristic",
  );
  expect(errors).toEqual([]);
});

test("schema, theme, history, debugging and refusal", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: /Settings.*help/i }),
  ).toHaveCount(0);
  await expect(page.locator('input[type="password"]')).toHaveCount(0);
  await page.getByRole("button", { name: "View schema", exact: true }).click();
  await expect(page.getByRole("dialog")).toContainText("customers");
  await page.getByRole("button", { name: "Close dialog" }).click();
  const theme = page.getByRole("switch", { name: "Dark mode", exact: true });
  await expect(theme).not.toBeChecked();
  await theme.focus();
  await page.keyboard.press("Space");
  await expect(theme).toBeChecked();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(
    page.getByRole("switch", { name: "Dark mode", exact: true }),
  ).toBeChecked();
  await send(page, "Monthly revenue for 2025");
  await expect(page.getByLabel("Validated SQL")).toContainText("STRFTIME");
  await page.getByRole("button", { name: "New conversation" }).click();
  await page.getByLabel("Task mode").selectOption("debug");
  await send(page, "SELECT name, hiredate FROM employees");
  await expect(page.getByLabel("Validated SQL")).toContainText("hire_date");
  await page.getByRole("tab", { name: "Explanation", exact: true }).click();
  await expect(page.getByRole("tabpanel")).toContainText(
    "Original query issue",
  );
  await page.getByLabel("Task mode").selectOption("generate");
  await send(page, "Who won the FIFA World Cup?");
  await expect(page.getByText("Out of scope", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Run query", exact: true }),
  ).toBeDisabled();
  await page.reload();
  await expect(page.getByText("Out of scope", { exact: true })).toBeVisible();
  await page
    .getByRole("navigation", { name: "Conversation history" })
    .getByRole("button", { name: "Monthly revenue for 2025", exact: true })
    .click();
  await expect(page.getByLabel("Validated SQL")).toContainText("STRFTIME");
});

test("history can be cleared from the sidebar without a settings page", async ({
  page,
}) => {
  await page.goto("/");
  await send(page, "Show all customers");
  await expect(page.getByLabel("Validated SQL")).toContainText("customers");
  page.once("dialog", (dialog) => dialog.dismiss());
  await page
    .getByRole("button", {
      name: "Clear all conversation history",
      exact: true,
    })
    .click();
  await expect(page.getByLabel("Validated SQL")).toContainText("customers");
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("button", {
      name: "Clear all conversation history",
      exact: true,
    })
    .click();
  await expect(
    page.getByText("Your conversations will appear here.", { exact: false }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Validated SQL")).toHaveCount(0);
});

test("mobile layout and screenshots", async ({ page }) => {
  await page.goto("/");
  await page.screenshot({ path: "artifacts/desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("button", { name: "Open navigation" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: /Explore your customers/ }).click();
  await expect(page.getByLabel("Validated SQL")).toContainText("California");
  await page.screenshot({ path: "artifacts/mobile.png", fullPage: true });
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(
    page.getByRole("button", { name: "New conversation" }),
  ).toBeVisible();
});

test("manual execution, empty rows and cap", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Auto-run queries").uncheck();
  await send(page, "SELECT name FROM customers WHERE id = -1");
  await expect(page.getByRole("tabpanel")).toContainText("Ready when you are");
  await page.getByRole("button", { name: "Run query", exact: true }).click();
  await expect(
    page.getByText("No records match this query.", { exact: false }),
  ).toBeVisible();
  await page.getByLabel("Auto-run queries").check();
  await send(page, "SELECT * FROM order_items");
  await expect(page.getByRole("tabpanel")).toContainText(
    "Results are capped at 500 rows",
  );
});

test("server error can be retried and bad storage does not crash", async ({
  page,
}) => {
  await page.addInitScript(() =>
    localStorage.setItem("queryatlas.v1", "not-json"),
  );
  await page.goto("/");
  await page.route("**/api/chat/stream", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        detail: "Temporary test outage. Retry the request.",
      }),
    }),
  );
  await send(page, "Show all customers");
  await expect(page.getByRole("alert")).toContainText("Temporary test outage");
  await expect(page.getByLabel("Your SQL or database question")).toHaveValue(
    "Show all customers",
  );
  await page.unroute("**/api/chat/stream");
  await page
    .getByRole("button", { name: "Send question", exact: true })
    .click();
  await expect(page.getByLabel("Validated SQL")).toContainText("customers");
});

test("CSV values are quoted and formula strings neutralized", async ({
  page,
}) => {
  await page.goto("/");
  await send(
    page,
    "SELECT '=1+1' AS formula, -12 AS negative, 'a,b' AS comma, NULL AS empty FROM customers LIMIT 1",
  );
  const promise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export CSV", exact: true }).click();
  const file = await promise;
  const text = await readFile((await file.path())!, "utf8");
  expect(text).toContain('"\'=1+1"');
  expect(text).toContain('"-12"');
  expect(text).toContain('"a,b"');
});

test("dark palette is readable across text, code, actions and status surfaces", async ({
  page,
}) => {
  await page.goto("/");
  const theme = page.getByRole("switch", { name: "Dark mode", exact: true });
  await expect(theme).toHaveText("");
  await theme.click();
  await expect(theme).toBeChecked();
  async function contrast(textSelector: string, backgroundSelector: string) {
    return page.evaluate(
      ({ textSelector, backgroundSelector }) => {
        const foreground = getComputedStyle(
          document.querySelector(textSelector)!,
        ).color;
        const background = getComputedStyle(
          document.querySelector(backgroundSelector)!,
        ).backgroundColor;
        const luminance = (color: string) => {
          const channels = color
            .match(/[\d.]+/g)!
            .slice(0, 3)
            .map(Number)
            .map((v) => v / 255)
            .map((v) =>
              v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4,
            );
          return (
            channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722
          );
        };
        const a = luminance(foreground),
          b = luminance(background);
        return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
      },
      { textSelector, backgroundSelector },
    );
  }
  expect(await contrast(".welcome > p", ".chat-panel")).toBeGreaterThanOrEqual(
    4.5,
  );
  await page.screenshot({ path: "artifacts/dark-welcome.png", animations: "disabled" });
  await send(page, "Monthly revenue for 2025");
  expect(
    await contrast(".message.assistant .message-body > p", ".chat-panel"),
  ).toBeGreaterThanOrEqual(4.5);
  expect(await contrast(".sql-keyword", ".code-scroll")).toBeGreaterThanOrEqual(
    4.5,
  );
  expect(await contrast(".sql-string", ".code-scroll")).toBeGreaterThanOrEqual(
    4.5,
  );
  expect(
    await contrast(".primary-button", ".primary-button"),
  ).toBeGreaterThanOrEqual(4.5);
  await page.screenshot({ path: "artifacts/dark-workspace.png", animations: "disabled" });
  await page.getByRole("tab", { name: "Query plan", exact: true }).click();
  expect(await contrast(".cost-tag", ".cost-tag")).toBeGreaterThanOrEqual(4.5);
  await page.screenshot({ path: "artifacts/dark-plan.png", animations: "disabled" });
  await send(page, "Who won the FIFA World Cup?");
  expect(
    await contrast(".status-label.refused", ".status-label.refused"),
  ).toBeGreaterThanOrEqual(4.5);
  await page.getByRole("button", { name: "View schema", exact: true }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.screenshot({ path: "artifacts/dark-schema.png", animations: "disabled" });
  await page.getByRole("button", { name: "Close dialog" }).click();
  await theme.click();
  await expect(theme).not.toBeChecked();
});

for (const viewport of [
  { width: 1440, height: 1000 },
  { width: 1366, height: 768 },
  { width: 1024, height: 640 },
  { width: 820, height: 900 },
  { width: 390, height: 844 },
  { width: 360, height: 640 },
  { width: 320, height: 568 },
]) {
  test(`fixed page and scrollable query workspace at ${viewport.width}x${viewport.height}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await expect(
      page
        .locator(".sidebar")
        .getByRole("button", { name: "Database explorer", exact: true }),
    ).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "View schema", exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "View schema", exact: true })
      .click();
    await expect(page.getByRole("dialog")).toContainText("customers");
    await page.getByRole("button", { name: "Close dialog" }).click();
    const query =
      "SELECT " +
      Array.from({ length: 40 }, (_, i) => `id AS customer_id_${i}`).join(
        ", ",
      ) +
      " FROM customers LIMIT 20";
    await send(page, query);
    const panel = page.getByRole("region", {
      name: "Query workspace",
      exact: true,
    });
    await expect(panel).toBeVisible();
    const scrollable = await panel.evaluate(
      (el) => el.scrollHeight > el.clientHeight,
    );
    expect(scrollable).toBe(true);
    const bounds = await panel.boundingBox();
    expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height);
    if (viewport.width > 980) {
      expect(bounds!.y).toBeLessThan(100);
      expect(bounds!.height).toBeGreaterThan(viewport.height - 150);
      const sidebar = await page.locator(".sidebar").boundingBox();
      const workbench = await page.locator(".workbench").boundingBox();
      expect(workbench!.width).toBeGreaterThanOrEqual(
        viewport.width - sidebar!.width - 40,
      );
    }
    await panel.hover();
    await page.mouse.wheel(0, 600);
    await expect
      .poll(() => panel.evaluate((el) => el.scrollTop))
      .toBeGreaterThan(0);
    await expect
      .poll(() =>
        page.evaluate(() => {
          const root = document.scrollingElement!;
          return (
            root.scrollTop === 0 &&
            root.scrollLeft === 0 &&
            root.scrollHeight <= innerHeight &&
            root.scrollWidth <= innerWidth
          );
        }),
      )
      .toBe(true);
    if (viewport.width <= 980) {
      await page
        .getByRole("group", { name: "Workspace view" })
        .getByRole("button", { name: "Chat", exact: true })
        .click();
      await expect(
        page.getByLabel("Your SQL or database question"),
      ).toBeVisible();
      await page
        .getByRole("group", { name: "Workspace view" })
        .getByRole("button", { name: "Query workspace", exact: true })
        .click();
      await expect(panel).toBeVisible();
    }
    const toggle = page.getByRole("switch", { name: "Dark mode", exact: true });
    await toggle.click();
    await expect(toggle).toBeChecked();
    await toggle.click();
    await expect(toggle).not.toBeChecked();
    if (viewport.width === 1366)
      await page.screenshot({ path: "artifacts/workspace-scroll.png" });
  });
}
