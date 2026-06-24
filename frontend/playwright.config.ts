import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E config for the ESL-VOZ walking-skeleton flow.
 *
 * The frontend lives at :3000 and talks to the FastAPI backend at :8000.
 * In CI both servers are launched here via `webServer`; locally an already-
 * running dev stack is reused, which keeps the loop fast.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false, // tests share one sqlite-backed user space
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://localhost:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: [
    {
      command: ".venv\\Scripts\\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --log-level warning",
      cwd: "../backend",
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: "npm run dev",
      // Bare `/` 404s because next-intl middleware only routes locale prefixes,
      // so probe a real locale route to detect a running dev server.
      url: "http://localhost:3000/en",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
