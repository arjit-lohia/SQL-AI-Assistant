// Shared single-server launcher for local review and browser tests.
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
const python =
  process.platform === "win32"
    ? ".venv/Scripts/python.exe"
    : ".venv/bin/python";
const port = process.env.QUERYATLAS_PORT || "8000";
if (!existsSync("dist/index.html")) throw new Error("Run npm run build first.");
const child = spawn(
  python,
  ["-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", port],
  { stdio: "inherit", env: process.env },
);
process.on("SIGTERM", () => child.kill());
process.on("SIGINT", () => child.kill());
child.on("exit", (code) => process.exit(code || 0));
