// @ts-check
/**
 * Claude Code plugin hook for agent-city (watch-only): forwards the hook input it reads on stdin to the local
 * agent-city daemon, exactly like the hooks `npx agent-city-ai install-claude` writes into settings.json.
 *
 * - Authenticates with the hooks-only token derived from ~/.agent-city/token (never the token itself).
 * - Stays silent when install-claude's hooks are already in the user settings, so each event reaches the city once.
 * - Prints nothing on stdout, never blocks or steers Claude, and always exits 0: a stopped daemon, a missing token
 *   or a timeout only skips this one event.
 *
 * Plain Node (≥ 20) with no dependencies, because the plugin is installed from git without a build step. Its
 * constants mirror packages/protocol and packages/claude-bridge; plugin-forward.test.ts pins them together.
 * Installed copies update only when `version` in ../.claude-plugin/plugin.json changes: bump it with any change here.
 */
import { createHmac } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const DAEMON_HOST = "127.0.0.1";
const DAEMON_DEFAULT_PORT = 4646;
const DAEMON_PORT_ENV = "AGENT_CITY_PORT";
const MAX_PORT = 65_535;
const STATE_DIR = ".agent-city";
const TOKEN_FILE = "token";
const CLAUDE_HOOKS_PATH = "/hooks/claude-code";
const HOOK_TOKEN_LABEL = "agent-city/claude-code-hooks/v1";
const MAX_HOOK_BODY_BYTES = 4 * 1_048_576;
/** Below the hook's own `timeout` in hooks.json, so the request is abandoned before Claude cancels the hook. */
const REQUEST_TIMEOUT_MS = 2_000;
const SETTINGS_DIR_ENV = "CLAUDE_CONFIG_DIR";
const SETTINGS_DIR = ".claude";
const SETTINGS_FILE = "settings.json";
/** Trailing shell comment of install-claude's SessionStart command handler. */
const INSTALL_COMMAND_MARKER = "# agent-city";
/** @type {Readonly<Record<string, true>>} */
const LOOPBACK_HOSTNAMES = { "127.0.0.1": true, localhost: true, "[::1]": true };
const LOG_PREFIX = "agent-city plugin:";

/** @param {string} reason */
function skip(reason) {
  process.stderr.write(`${LOG_PREFIX} ${reason}\n`);
}

/** @param {NodeJS.ProcessEnv} env @returns {number | null} */
function daemonPort(env) {
  const raw = env[DAEMON_PORT_ENV];
  const port = raw === undefined || raw === "" ? DAEMON_DEFAULT_PORT : Number(raw);
  return Number.isInteger(port) && port >= 1 && port <= MAX_PORT ? port : null;
}

/** @param {unknown} value @returns {value is Record<string, unknown>} */
function isObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Same test as install-claude's `isAgentCityHandler` (packages/claude-bridge/src/settings.ts). @param {unknown} handler */
function isInstallClaudeHandler(handler) {
  if (!isObject(handler)) return false;
  if (handler.type === "http" && typeof handler.url === "string") {
    if (!URL.canParse(handler.url)) return false;
    const url = new URL(handler.url);
    return url.pathname === CLAUDE_HOOKS_PATH && Object.hasOwn(LOOPBACK_HOSTNAMES, url.hostname);
  }
  return handler.type === "command" && typeof handler.command === "string" && handler.command.endsWith(INSTALL_COMMAND_MARKER);
}

/** Whether install-claude's hooks are in the user settings (the only file it writes). @param {NodeJS.ProcessEnv} env */
function installClaudeHooksPresent(env) {
  const path = join(env[SETTINGS_DIR_ENV] || join(homedir(), SETTINGS_DIR), SETTINGS_FILE);
  if (!existsSync(path)) return false;
  /** @type {unknown} */
  let settings;
  try {
    settings = JSON.parse(readFileSync(path, "utf8"));
  } catch {
    return false;
  }
  if (!isObject(settings) || !isObject(settings.hooks)) return false;
  for (const groups of Object.values(settings.hooks)) {
    if (!Array.isArray(groups)) continue;
    for (const group of groups) {
      if (isObject(group) && Array.isArray(group.hooks) && group.hooks.some(isInstallClaudeHandler)) return true;
    }
  }
  return false;
}

/** @returns {Promise<Buffer | null>} null when the input exceeds what the daemon accepts */
async function readStdin() {
  /** @type {Buffer[]} */
  const chunks = [];
  let size = 0;
  for await (const chunk of process.stdin) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(String(chunk));
    size += buffer.length;
    if (size > MAX_HOOK_BODY_BYTES) return null;
    chunks.push(buffer);
  }
  return Buffer.concat(chunks);
}

/** @param {NodeJS.ProcessEnv} env */
async function forward(env) {
  const body = await readStdin();
  if (installClaudeHooksPresent(env)) return; // install-claude's hooks already send this event
  if (body === null) return skip(`hook input exceeds ${MAX_HOOK_BODY_BYTES} bytes`);
  const port = daemonPort(env);
  if (port === null) return skip(`${DAEMON_PORT_ENV}=${env[DAEMON_PORT_ENV] ?? ""} is not a port`);
  const tokenFile = join(homedir(), STATE_DIR, TOKEN_FILE);
  if (!existsSync(tokenFile)) return skip(`${tokenFile} is missing: start the city once with npx agent-city-ai`);
  const hookToken = createHmac("sha256", readFileSync(tokenFile, "utf8").trim()).update(HOOK_TOKEN_LABEL).digest("hex");
  const response = await fetch(`http://${DAEMON_HOST}:${port}${CLAUDE_HOOKS_PATH}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${hookToken}` },
    body,
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) skip(`daemon answered ${response.status}`);
}

try {
  await forward(process.env);
} catch (error) {
  skip(`daemon not reachable (${error instanceof Error ? error.message : String(error)})`);
}
process.exit(0);
