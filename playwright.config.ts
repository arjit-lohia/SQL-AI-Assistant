import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/browser",
  timeout: 30000,
  expect: { timeout: 10000 },
  fullyParallel: false,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://127.0.0.1:8001",
    viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  webServer: {
    command: "node scripts/serve.mjs",
    url: "http://127.0.0.1:8001/api/health",
    reuseExistingServer: false,
    env: {
      QUERYATLAS_PORT: "8001",
      GROQ_API_KEY: "",
      GROQ_MODEL: "openai/gpt-oss-120b",
    },
    timeout: 30000,
  },
});
