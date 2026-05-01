/* eslint-disable no-console */
type LogLevel = "info" | "warn" | "error" | "debug";

const LEVEL_LABEL: Record<LogLevel, string> = {
  debug: "DEBUG",
  info: "INFO",
  warn: "WARNING",
  error: "ERROR",
};

function pad(n: number, w = 2): string {
  return String(n).padStart(w, "0");
}

function formatTimestamp(d: Date): string {
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}.${pad(d.getMilliseconds(), 3)}`
  );
}

function getCallerLocation(): string {
  const stack = new Error().stack?.split("\n") ?? [];
  for (let i = 3; i < stack.length; i++) {
    const line = stack[i];
    if (!line) continue;
    if (line.includes("logger.ts")) continue;
    const m = line.match(/at (?:(.+?) \()?(.+?):(\d+):\d+\)?$/);
    if (!m) continue;
    const fn = m[1] && m[1] !== "<anonymous>" ? m[1] : "<module>";
    const file = m[2]
      .replace(/^file:\/\//, "")
      .replace(/^.*\/admin_web\//, "")
      .replace(/^.*\/\.next\//, ".next/");
    return `${file}:${fn}:${m[3]}`;
  }
  return "?:?:?";
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === "development";

  private format(
    level: LogLevel,
    message: string,
    context: Record<string, unknown> | undefined,
    location: string,
  ): string {
    const ts = formatTimestamp(new Date());
    const lvl = LEVEL_LABEL[level].padEnd(8, " ");
    const ctx = context ? ` ${JSON.stringify(context)}` : "";
    return `${ts} | ${lvl} | ${location} - ${message}${ctx}`;
  }

  private log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    const location = getCallerLocation();

    if (this.isDevelopment) {
      const formatted = this.format(level, message, context, location);
      switch (level) {
        case "error":
          console.error(formatted);
          break;
        case "warn":
          console.warn(formatted);
          break;
        case "debug":
          console.debug(formatted);
          break;
        default:
          console.log(formatted);
      }
    } else if (level === "error") {
      console.error(
        JSON.stringify({
          level,
          message,
          context,
          location,
          timestamp: new Date().toISOString(),
        }),
      );
    }
  }

  info(message: string, context?: Record<string, unknown>): void {
    this.log("info", message, context);
  }

  warn(message: string, context?: Record<string, unknown>): void {
    this.log("warn", message, context);
  }

  error(message: string, context?: Record<string, unknown>): void {
    this.log("error", message, context);
  }

  debug(message: string, context?: Record<string, unknown>): void {
    this.log("debug", message, context);
  }
}

export const logger = new Logger();
