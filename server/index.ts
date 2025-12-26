import { spawn } from "child_process";

console.log("Starting Flask application...");

const flask = spawn("python", ["main.py"], {
  stdio: "inherit",
  env: { ...process.env },
});

flask.on("error", (err) => {
  console.error("Failed to start Flask:", err);
  process.exit(1);
});

flask.on("close", (code) => {
  console.log(`Flask process exited with code ${code}`);
  process.exit(code || 0);
});

process.on("SIGINT", () => {
  flask.kill("SIGINT");
});

process.on("SIGTERM", () => {
  flask.kill("SIGTERM");
});
