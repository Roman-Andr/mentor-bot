// Spawn the inner server command and reformat each output line into the same
// "YYYY-MM-DD HH:mm:ss.SSS | LEVEL    | location - message" shape that the
// Python services emit via loguru. Lines that already look formatted are
// passed through untouched.

import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

const [cmd, ...args] = process.argv.slice(2);

if (!cmd) {
  process.stderr.write("log-wrap: no command provided\n");
  process.exit(2);
}

const ALREADY_FORMATTED = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \| /;
// eslint-disable-next-line no-control-regex
const ANSI_RE = /\x1b\[[0-9;]*[A-Za-z]/g;

const pad = (n, w = 2) => String(n).padStart(w, "0");

function ts() {
  const d = new Date();
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}.${pad(d.getMilliseconds(), 3)}`
  );
}

function detectLevel(text) {
  const t = text.toLowerCase();
  if (/\b(error|fatal|fail(ed|ure)?)\b/.test(t)) return "ERROR";
  if (/\bwarn(ing)?\b/.test(t)) return "WARNING";
  if (/^\s*debug\b/.test(t)) return "DEBUG";
  return "INFO";
}

function format(line, location) {
  const cleaned = line.replace(/\r$/, "");
  if (!cleaned.trim()) return cleaned;
  if (ALREADY_FORMATTED.test(cleaned.replace(ANSI_RE, ""))) return cleaned;
  const stripped = cleaned.replace(ANSI_RE, "");
  const lvl = detectLevel(stripped).padEnd(8, " ");
  const msg = cleaned.replace(/^\s+/, "");
  return `${ts()} | ${lvl} | ${location} - ${msg}`;
}

function pipe(input, output, location) {
  const rl = createInterface({ input, crlfDelay: Infinity });
  rl.on("line", (line) => {
    output.write(format(line, location) + "\n");
  });
}

const child = spawn(cmd, args, {
  stdio: ["inherit", "pipe", "pipe"],
  env: process.env,
});

pipe(child.stdout, process.stdout, "next:stdout:0");
pipe(child.stderr, process.stderr, "next:stderr:0");

for (const sig of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  process.on(sig, () => {
    if (!child.killed) child.kill(sig);
  });
}

child.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 0);
});

child.on("error", (err) => {
  process.stderr.write(`log-wrap: failed to spawn ${cmd}: ${err.message}\n`);
  process.exit(1);
});
