// Start the pinned upstream runtime; keep protocol stdout untouched.
import { spawn } from "node:child_process";

const windows = process.platform === "win32";
const command = windows ? (process.env.ComSpec || "cmd.exe") : "npx";
const args = windows
  ? ["/d", "/s", "/c", "npx -y rea-agents@6.4.0 mcp"]
  : ["-y", "rea-agents@6.4.0", "mcp"];
const child = spawn(command, args, { stdio: "inherit", windowsHide: true });
child.on("error", (error) => {
  process.stderr.write(`Cannot start REA 6.4.0: ${error.message}\n`);
  process.exitCode = 1;
});
child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exitCode = code ?? 1;
});
for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => child.kill(signal));
}
