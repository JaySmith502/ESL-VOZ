import { test, expect, type Page } from "@playwright/test";

/**
 * Walking-skeleton E2E: splash → login → magic link → verify → intake →
 * consent → placement → recommended lesson.
 *
 * The backend returns the magic-link token in the JSON response when
 * ENVIRONMENT=development, so we intercept that response instead of waiting
 * for an email. This is the same path test_acceptance.py exercises on the
 * server, but driven through the real UI.
 */

const BACKEND = "http://127.0.0.1:8000";
const uniqueEmail = () => `e2e-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;

async function loginViaMagicLink(page: Page, email: string) {
  await page.goto("/en/login");
  await expect(page.getByRole("heading", { name: /welcome back/i })).toBeVisible();

  // Capture the dev-mode token from the magic-link POST response.
  const magicLinkResp = page.waitForResponse(
    (r) => r.url().endsWith("/auth/magic-link") && r.request().method() === "POST",
  );
  await page.getByPlaceholder(/enter your email/i).fill(email);
  await page.getByRole("button", { name: /send magic link/i }).click();
  const resp = await magicLinkResp;
  const body = await resp.json();
  expect(body.token, "backend should expose token in dev").toBeTruthy();

  await page.goto(`/en/login/verify?token=${body.token}`);
  await page.waitForURL(/\/en\/onboarding\/intake/, { timeout: 10_000 });
}

test.describe("walking skeleton", () => {
  test("learner can complete intake → consent → placement → first recommendation", async ({ page, request }) => {
    // Surface every backend request + every failed/console error to the test
    // log so flakes are easy to triage in CI.
    page.on("requestfailed", (req) =>
      console.log(`[requestfailed] ${req.method()} ${req.url()} — ${req.failure()?.errorText}`),
    );
    page.on("response", (r) => {
      if (r.url().startsWith(BACKEND) && r.status() >= 400) {
        console.log(`[backend ${r.status()}] ${r.request().method()} ${r.url()}`);
      }
    });
    page.on("pageerror", (e) => console.log(`[pageerror] ${e.message}`));

    // Backend liveness sanity check — fails fast if the API didn't start.
    const health = await request.get(`${BACKEND}/health`);
    expect(health.ok()).toBeTruthy();

    const email = uniqueEmail();
    await loginViaMagicLink(page, email);

    // -- Intake --------------------------------------------------------------
    // 7 required inputs identified by placeholder text. Backend validates
    // EmailStr on the first one, so it must be a real-looking email.
    await expect(page.getByRole("heading", { name: /let'?s get to know you/i })).toBeVisible();
    await page.getByPlaceholder("Email").fill(email);
    await page.getByPlaceholder(/native language/i).fill("es");
    await page.getByPlaceholder(/years in the u\.s\./i).fill("2");
    await page.getByPlaceholder(/studied english/i).fill("no");
    await page.getByPlaceholder(/highest education/i).fill("high_school");
    await page.getByPlaceholder(/primary goal/i).fill("work");
    await page.getByPlaceholder(/age band/i).fill("25-34");
    await page.getByRole("button", { name: /continue/i }).click();
    await page.waitForURL(/\/en\/onboarding\/consent/, { timeout: 10_000 });

    // -- Consent -------------------------------------------------------------
    // The first checkbox (platform terms) is required; the other two are
    // optional. Locate by the label's accessible text.
    await page.getByLabel(/platform terms/i).check();
    await page.getByRole("button", { name: /continue/i }).click();
    await page.waitForURL(/\/en\/onboarding\/placement/, { timeout: 10_000 });

    // -- Placement -----------------------------------------------------------
    // The page renders one card per item with an "I don't know" link. Click
    // every visible IDK link; that floors us to A1.1 which is fine for
    // skeleton coverage and avoids brittle per-item answer logic.
    await expect(page.getByRole("heading", { name: /placement check/i })).toBeVisible();
    const idkLinks = page.getByRole("button", { name: /i don'?t know/i });
    await expect(idkLinks.first()).toBeVisible();
    const idkCount = await idkLinks.count();
    expect(idkCount, "bank should expose at least one placement item").toBeGreaterThan(0);
    for (let i = 0; i < idkCount; i++) {
      await idkLinks.nth(i).click();
    }
    await page.getByRole("button", { name: /finish/i }).click();

    // -- Placement results --------------------------------------------------
    await expect(page.getByRole("heading", { name: /placement complete/i })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/your starting level/i)).toBeVisible();
    await page.getByRole("button", { name: /go to learn/i }).click();
    await page.waitForURL(/\/en\/learn/, { timeout: 10_000 });

    // -- Learn dashboard ----------------------------------------------------
    // The engine should fire and recommend a lesson.
    // Use getByRole heading to avoid matching Next's route announcer node,
    // which also contains the page title.
    await expect(page.getByRole("heading", { name: /your next activity/i })).toBeVisible();
    // The recommended-lesson CTA is a <Link>, not a button.
    const startLink = page.getByRole("link", { name: /start/i });
    await expect(startLink).toBeVisible();

    // -- Lesson player ------------------------------------------------------
    // The engine picks an uncompleted A1.1 Survival lesson for a fresh
    // learner. Which one it picks depends on tie-breakers among lessons with
    // identical estimated_minutes, so don't assert a specific title — just
    // assert the player rendered SOMETHING and the URL is the lesson route.
    await startLink.click();
    await page.waitForURL(/\/en\/learn\/lesson\/[\w_-]+$/, { timeout: 10_000 });
    // The lesson page renders the lesson title as the only h1 in <main>.
    await expect(page.locator("main h1").first()).toBeVisible();

    // Generic step loop: handle whichever step is on screen by probing for
    // its distinctive controls. Bounded so a regression can't hang the test.
    for (let i = 0; i < 20; i++) {
      if (await page.getByRole("heading", { name: /lesson complete/i }).isVisible().catch(() => false)) {
        break;
      }
      const input = page.locator('input[type="text"], input:not([type])').first();
      if (await input.isVisible().catch(() => false)) {
        // vocab_drill or production_speaking — any non-empty answer is fine.
        await input.fill("hello");
      }
      const check = page.getByRole("button", { name: /^check$/i });
      if (await check.isVisible().catch(() => false)) {
        await check.click();
      }
      await page.getByRole("button", { name: /^continue$/i }).first().click();
      // Tiny pause so the next step's DOM settles before the next probe.
      await page.waitForTimeout(150);
    }

    // Lesson finished — the player shows the completion card.
    await expect(page.getByRole("heading", { name: /lesson complete/i })).toBeVisible();
    // "Back to Learn" must be a locale-aware link, otherwise it 404s. Click
    // it and assert we land on the dashboard, not on a missing route.
    await page.getByRole("link", { name: /back to learn/i }).click();
    await page.waitForURL(/\/en\/learn$/, { timeout: 10_000 });
    await expect(page.getByRole("heading", { name: /your next activity/i })).toBeVisible();
  });
});
