type RuntimeEnv = Record<string, string | undefined>;

function readProcessEnv(): RuntimeEnv | null {
  if (typeof process === "undefined" || !process.env) {
    return null;
  }

  return process.env;
}

export function readRuntimeEnv(name: string, fallback = ""): string {
  return readProcessEnv()?.[name] ?? fallback;
}

export function isRuntimeEnvEnabled(name: string): boolean {
  return readRuntimeEnv(name) === "true";
}
