#!/usr/bin/env node
/**
 * scan-synced-content.mjs — deterministic supply-chain scanner for mirrored
 * external plugin content.
 *
 * WHY THIS EXISTS
 *   sync-external.mjs mirrors external repos (markdown, 60+ shell scripts, python,
 *   JSON hook/MCP configs) into plugins/** via a weekly auto-generated PR.
 *   sources.yaml pins nothing, so a compromised or rogue upstream author's next
 *   push rides into the marketplace and executes in users' agents. Nothing
 *   deterministic reads a sync diff for an injected payload, and an AI reviewer
 *   can miss a one-liner buried in a 100K-line diff. This scanner is that
 *   deterministic gate.
 *
 * GRADED FINDINGS (mirrors the escape-scan REFUSE / CHALLENGE / FLAG model — a
 * false-positive storm gets a gate disabled, so the grades are deliberately
 * separated so only genuinely-malicious content HARD-fails):
 *
 *   REFUSE    (exit 2, always fails)   high-confidence malicious, in a file that
 *             can AUTO-EXECUTE (a script, or a hook/MCP JSON/YAML config):
 *               - pipe-to-shell in an executable script (curl … | sh)
 *               - reverse-shell one-liners (bash -i >& /dev/tcp/…, nc -e /bin/sh)
 *               - decode-then-exec (base64 -d | sh, eval(atob(…)))
 *               - secret/env exfiltration to a network sink (env | curl,
 *                 cat ~/.ssh/… | curl, curl --data @~/.aws/credentials)
 *               - crypto-miner signatures (stratum+tcp://, xmrig, …)
 *             The SAME pattern inside a doc (README/SKILL.md prose) is graded
 *             CHALLENGE, not REFUSE — it doesn't auto-run and is often legit
 *             security-education content.
 *
 *   CHALLENGE (exit 1 unless --warn-only or waived)   dual-use, must be SEEN:
 *               - a documented `curl … | sh` install step (legit in a README,
 *                 but a human must confirm it — CHALLENGE, not REFUSE)
 *               - a malicious-class pattern (above) appearing in a DOC
 *               - a hook definition (.claude hooks auto-execute)
 *               - an MCP server config with a remote URL
 *               - an allowed-tools list that grants a network tool (WebFetch/WebSearch)
 *               - dynamic code exec (eval / new Function / os.system / shell=True)
 *               - outbound network calls in a shell/py script
 *
 *   FLAG      (exit 0, report-only)   smells worth a look:
 *               - an allowed-tools list that grants Bash (ubiquitous → FLAG, not
 *                 CHALLENGE, to avoid a false-positive storm)
 *               - very long single-line base64-ish blobs / heavy obfuscation
 *               - non-ASCII homoglyphs in code identifiers/commands
 *               - unusually large binary-ish files
 *               - JS outbound network calls (fetch/axios)
 *
 * USAGE
 *   node scripts/scan-synced-content.mjs                      # scan plugins/community/**
 *   node scripts/scan-synced-content.mjs --changed-only --base origin/main
 *   node scripts/scan-synced-content.mjs --changed-only --base HEAD   # working-tree diff
 *   node scripts/scan-synced-content.mjs path/a path/b        # explicit path list
 *   node scripts/scan-synced-content.mjs --warn-only ...      # CHALLENGE→exit 0 (REFUSE still 2)
 *   node scripts/scan-synced-content.mjs --json ...           # machine-readable findings
 *
 * ALLOWLIST
 *   scripts/scan-allowlist.txt holds `path:rule  reason` waivers. A waiver
 *   downgrades a CHALLENGE or FLAG to a reported-but-passing note. REFUSE is
 *   NEVER waivable via the allowlist (fail closed) — a real hard-block must be
 *   fixed at the source, not signed away.
 *
 * ANTI-EVASION (best-effort — this is a pattern scanner, defense in depth, NOT a
 * sandbox). We normalize before matching: strip comments, join `\`-continued
 * lines, and collapse quote/`+`/backslash string-concatenation so `"cur"+"l"`,
 * `c'u'rl`, and `cur\<nl>l` reduce toward `curl`. What we CANNOT catch — and do
 * not claim to — is enumerated at the bottom of this file (KNOWN BYPASSES).
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath, pathToFileURL } from 'url';
import { execFileSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, '..');
const ALLOWLIST_FILE = path.join(__dirname, 'scan-allowlist.txt');
const DEFAULT_SCAN_ROOT = 'plugins/community';

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
};

export const GRADE = { REFUSE: 'REFUSE', CHALLENGE: 'CHALLENGE', FLAG: 'FLAG' };

const SCANNABLE_EXT = new Set([
  '.md',
  '.mdx',
  '.markdown',
  '.txt',
  '.sh',
  '.bash',
  '.zsh',
  '.py',
  '.js',
  '.mjs',
  '.cjs',
  '.ts',
  '.tsx',
  '.jsx',
  '.json',
  '.yaml',
  '.yml',
]);

/** Classify a file by extension/path so grading can be context-aware. */
export function fileClass(relPath) {
  const ext = path.extname(relPath).toLowerCase();
  const base = path.basename(relPath).toLowerCase();
  if (['.md', '.mdx', '.markdown', '.txt'].includes(ext)) return 'doc';
  if (['.sh', '.bash', '.zsh'].includes(ext)) return 'shell';
  if (ext === '.py') return 'python';
  if (['.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx'].includes(ext)) return 'js';
  if (ext === '.json' || base === '.mcp.json') return 'json';
  if (['.yaml', '.yml'].includes(ext)) return 'yaml';
  return 'other';
}

const isScript = (cls) => cls === 'shell' || cls === 'python' || cls === 'js';

export function normalizeScanPath(candidate, pathApi = path) {
  return String(candidate).split(pathApi.sep).join('/');
}

export function isScannablePath(candidate, pathApi = path) {
  const rel = normalizeScanPath(candidate, pathApi);
  const ext = path.posix.extname(rel).toLowerCase();
  const inHooks = /(?:^|\/)hooks\//.test(rel);
  return SCANNABLE_EXT.has(ext) || inHooks;
}

// A malicious-pattern grade: REFUSE when it can auto-execute (a script, or a
// hook/MCP JSON/YAML config), CHALLENGE when it only appears in PROSE (a doc) —
// a reverse-shell string inside a README does not auto-run and is often
// legitimate security-education content, so a human confirms rather than a hard
// block nuking every pentest skill. (Known limitation: a doc-embedded payload a
// user copy-pastes is CHALLENGE, not REFUSE — see KNOWN BYPASSES.)
const refuseUnlessDoc = (cls) => (cls === 'doc' ? GRADE.CHALLENGE : GRADE.REFUSE);

// ─────────────────────────────────────────────────────────────────────────────
// Normalization (anti-evasion). Strip comments so commented-out text does not
// fire, join `\`-continued shell lines, and collapse quote/`+`/backslash
// string-concatenation so split dangerous tokens are revealed. We ALSO keep the
// raw text and scan both; a hit in EITHER view is reported (fail-closed).
// ─────────────────────────────────────────────────────────────────────────────

/** Remove `/* … *\/` block comments from JS/TS, preserving newlines/line count. */
function stripBlockComments(text) {
  return text.replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, ' '));
}

/**
 * Strip a single line's trailing/inline comment for the given language.
 * Quote-aware for the common cases; `//` inside `://` (URLs) is preserved.
 * Best-effort, documented — a determined attacker can still confuse it, which
 * is why we ALSO scan the raw line for the strong REFUSE patterns.
 */
function stripLineComment(line, cls) {
  const cutAt = (idx) => (idx >= 0 ? line.slice(0, idx) : line);
  if (cls === 'shell' || cls === 'python' || cls === 'yaml') {
    // Cut at the first `#` that is not inside single/double quotes.
    // Escape-aware: a backslash-escaped quote (`\"`) outside single quotes does
    // NOT toggle the string state, so `echo "x \" # " && curl url|sh` can't hide
    // the payload behind a fake trailing comment (red-team: escaped-quote bypass).
    let inS = false;
    let inD = false;
    let esc = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (esc) {
        esc = false;
        continue;
      }
      if (c === '\\' && !inS) {
        esc = true; // single quotes don't process backslash escapes in shell
        continue;
      }
      if (c === "'" && !inD) inS = !inS;
      else if (c === '"' && !inS) inD = !inD;
      else if (c === '#' && !inS && !inD) {
        // require start-of-line or preceding whitespace so `foo#bar` fragments
        // (rare) aren't mis-cut; a leading `#` still cuts.
        if (i === 0 || /\s/.test(line[i - 1])) return cutAt(i);
      }
    }
    return line;
  }
  if (cls === 'js') {
    // Cut at `//` that is not part of `://` and not inside a quote.
    // Escape-aware: an escaped quote inside a string (`"\""`, `'\''`, \`\\\`\`)
    // doesn't close it, so a `//` cut can't be smuggled past an escaped quote.
    let inS = false;
    let inD = false;
    let inB = false;
    let esc = false;
    for (let i = 0; i < line.length - 1; i++) {
      const c = line[i];
      if (esc) {
        esc = false;
        continue;
      }
      if (c === '\\' && (inS || inD || inB)) {
        esc = true; // backslash escapes only matter inside a string literal
        continue;
      }
      if (c === "'" && !inD && !inB) inS = !inS;
      else if (c === '"' && !inS && !inB) inD = !inD;
      else if (c === '`' && !inS && !inD) inB = !inB;
      else if (c === '/' && line[i + 1] === '/' && !inS && !inD && !inB) {
        if (i > 0 && line[i - 1] === ':') continue; // http:// etc
        return cutAt(i);
      }
    }
    return line;
  }
  return line; // doc / json / other → no line-comment stripping
}

/** Collapse quote/`+`/backslash concatenation, KEEPING unrelated spaces so `\s+`
 *  patterns still match. Reveals `"cur"+"l"` → `curl`, `"cur" + "l"` → `curl`,
 *  `c'u'rl` → `curl`. The whitespace AROUND a `+` is part of the concatenation
 *  and is dropped; other spaces are preserved. */
export function concatCollapse(line) {
  // Consume each whitespace run once. A leading \s* followed by a missing +
  // retries at every character of masked comments/strings (quadratic time).
  // Preserve whitespace unless it touched + in the original input, before
  // quotes and backslashes are removed, matching the normalization contract.
  return line.replace(/\s+|[+"'`\\]/g, (token, offset) =>
    /^\s/.test(token) && line[offset - 1] !== '+' && line[offset + token.length] !== '+'
      ? token
      : '',
  );
}

/**
 * Produce the logical lines to scan: comment-stripped, with `\`-continued
 * shell/js lines joined onto their starting line number. Returns
 * [{ n, text }] where n is the 1-based starting line number.
 */
export function normalizeLines(rawText, cls) {
  const text = cls === 'js' ? stripBlockComments(rawText) : rawText;
  const rawLines = text.split('\n');
  const stripped = rawLines.map((l) => stripLineComment(l, cls));
  const out = [];
  for (let i = 0; i < stripped.length; i++) {
    let text = stripped[i];
    const startN = i + 1;
    // Join trailing-backslash continuations (shell/js) so a pipe split across
    // a continuation is scanned as one logical line. Join with '' (not ' ') —
    // a shell line-continuation deletes the backslash-newline entirely, so
    // `cu\<NL>rl` is the token `curl`, not `cu rl` (red-team: continuation split).
    while ((cls === 'shell' || cls === 'js') && /\\\s*$/.test(text) && i + 1 < stripped.length) {
      text = text.replace(/\\\s*$/, '') + stripped[i + 1];
      i++;
    }
    out.push({ n: startN, text });
  }
  return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Line-level rules. Each is tested against BOTH the stripped line and its
// concat-collapsed form; a match in either is a finding (deduped by id+line).
// `grade` may be a function of the file class (e.g. pipe-to-shell is REFUSE in a
// script, CHALLENGE in a doc). `langs` limits which file classes a rule applies
// to ('*' = all).
// ─────────────────────────────────────────────────────────────────────────────
const LINE_RULES = [
  {
    id: 'pipe-to-shell',
    // json/yaml added (red-team F1): `.mcp.json` stdio commands + hook/config
    // YAML are canonical auto-execute surfaces, and `curl|sh` inside them was
    // previously invisible. Interpreters beyond sh added (F3): fetch-and-run via
    // python/node/perl/ruby is identical RCE. Process-substitution added (F2):
    // `bash <(curl …)` is unobfuscated textbook RCE the pipe anchor missed.
    langs: ['shell', 'python', 'js', 'doc', 'json', 'yaml'],
    re: /\b(?:curl|wget)\b[^\n|]{0,200}\|\s*(?:sudo\s+)?(?:sh|bash|zsh|dash|ksh|python[0-9.]*|node|perl|ruby)\b|(?:\b(?:sh|bash|zsh|dash|ksh|source)\b|(?:^|[;&|])\s*\.)\s+<\(\s*(?:curl|wget)\b/i,
    grade: (cls) => (cls === 'doc' ? GRADE.CHALLENGE : GRADE.REFUSE),
    label: 'pipe-to-shell (curl/wget fetched into a shell/interpreter)',
  },
  {
    id: 'reverse-shell',
    langs: '*',
    // Require the reverse-shell idiom (>& /dev/tcp, bash -i + /dev/tcp, 0>&1, or
    // nc -e). A plain connectivity check `echo > /dev/tcp/host/443` (no `&`, no
    // `-i`, no `0>&1`) intentionally does NOT match.
    re: /(?:>&\s*\/dev\/(?:tcp|udp)\/|\b(?:ba|z)?sh\b\s+-[a-z]*i[a-z]*\b[^\n]{0,80}\/dev\/(?:tcp|udp)\/|\/dev\/(?:tcp|udp)\/\S+\/\d+\s+0>&1|\bn(?:c|cat)\b[^\n]{0,40}-e\s*\/(?:bin|usr\/bin)\/(?:ba|z)?sh|mkfifo\b[^\n]{0,80}\|\s*n(?:c|cat)\b)/i,
    grade: refuseUnlessDoc,
    label: 'reverse-shell one-liner',
  },
  {
    id: 'decode-exec',
    langs: '*',
    re: /(?:\b(?:base64|base32|xxd|openssl\s+enc)\b[^\n|]{0,80}(?:-d|--decode|-D)\b[^\n]{0,80}\|\s*(?:sudo\s+)?(?:sh|bash|zsh|python[0-9.]*|node|perl|ruby)\b|\beval\s*\(\s*(?:atob|Buffer\.from|decodeURIComponent)\b|\b(?:exec|eval)\s*\(\s*base64\.b64decode|eval\s+"?\$\([^)]*\|\s*base64\s+(?:-d|--decode))/i,
    grade: refuseUnlessDoc,
    label: 'decode-then-execute',
  },
  {
    id: 'secret-exfil',
    langs: '*',
    re: /(?:\b(?:printenv|env|set)\b\s*\|\s*(?:curl|wget|nc|ncat|http)\b|\b(?:cat|less|head|tail|xxd|base64)\b\s+[^\n|]{0,80}(?:\.ssh\/|\.aws\/credentials|\/\.aws\/|\.env\b|\.netrc|id_rsa|id_ed25519|id_dsa)[^\n|]{0,80}\|\s*(?:curl|wget|nc|ncat)\b|\b(?:curl|wget)\b[^\n]{0,200}(?:--data|--data-binary|-d|-F|--form|--upload-file|-T)\b[^\n]{0,80}(?:\.ssh\/|\.aws\/credentials|\.env\b|id_rsa|id_ed25519|printenv|\$\{?HOME\}?\/\.ssh))/i,
    grade: refuseUnlessDoc,
    label: 'secret/env exfiltration to a network sink',
  },
  {
    id: 'crypto-miner',
    langs: '*',
    re: /(?:stratum\+(?:tcp|ssl):\/\/|\bxmrig\b|\bminerd\b|\bcryptonight\b|\bcoinhive\b|--donate-level\b|\bcpuminer\b)/i,
    grade: refuseUnlessDoc,
    label: 'crypto-miner signature',
  },
  {
    id: 'dynamic-exec',
    // json/yaml added (red-team F1): a config string value can carry an exec()
    // that runs when the config is loaded/executed.
    langs: ['shell', 'python', 'js', 'json', 'yaml'],
    // Dual-use dynamic code execution. redis `.eval(` (a Lua call, not code
    // exec) is excluded to match the repo's existing dangerous-pattern gate.
    re: /(?:\bnew\s+Function\s*\(|\bos\.system\s*\(|subprocess\.(?:run|call|Popen|check_output|check_call)\s*\([^\n]*shell\s*=\s*True|(?<!redis\.)(?<!\.redis)\beval\s*\(|(?<![.\w])exec\s*\()/i,
    grade: () => GRADE.CHALLENGE,
    label: 'dynamic code execution',
  },
  {
    id: 'outbound-network',
    // json/yaml added (red-team F1): an outbound call embedded in a config
    // string (e.g. an .mcp.json stdio command) must at least be SEEN (CHALLENGE).
    langs: ['shell', 'python', 'json', 'yaml'],
    re: /(?:\b(?:curl|wget|nc|ncat|telnet)\b|\brequests\.(?:get|post|put|delete|patch|head)\s*\(|\burllib(?:2|\.request)?\b|\bhttpx\b|\bhttp\.client\b|\bsocket\.connect\b)/i,
    grade: () => GRADE.CHALLENGE,
    label: 'outbound network call in a shell/py script',
  },
  {
    id: 'outbound-network-js',
    langs: ['js'],
    re: /(?:\bfetch\s*\(|\baxios\b|\bhttps?\.request\s*\(|\bXMLHttpRequest\b)/i,
    grade: () => GRADE.FLAG,
    label: 'outbound network call in a JS script',
  },
  {
    id: 'long-base64-blob',
    langs: '*',
    re: /[A-Za-z0-9+/]{160,}={0,2}/,
    grade: () => GRADE.FLAG,
    label: 'very long single-line base64-ish blob',
    concatSafe: false, // never test the concat view — collapse would create noise
  },
  {
    id: 'heavy-obfuscation',
    langs: ['shell', 'python', 'js'],
    re: /(?:(?:\\x[0-9a-fA-F]{2}){6,}|(?:\\u[0-9a-fA-F]{4}){6,}|String\.fromCharCode\s*\((?:[^)]*,){6,}|(?:chr\(\d+\)\s*\+\s*){5,})/,
    grade: () => GRADE.FLAG,
    label: 'heavy character-code / hex-escape obfuscation',
    concatSafe: false,
  },
];

// Homoglyph detection: Cyrillic (U+0400–04FF) or Greek (U+0370–03FF) letters
// appearing adjacent to ASCII letters in a code-ish line — a classic
// look-alike-identifier trick.
const HOMOGLYPH_RE = /[A-Za-z][Ͱ-ϿЀ-ӿ]|[Ͱ-ϿЀ-ӿ][A-Za-z]/;

// ─────────────────────────────────────────────────────────────────────────────
// File-level rules (whole-file signals, not line-anchored to a token).
// ─────────────────────────────────────────────────────────────────────────────

/** Detect a .claude hook definition (hooks auto-execute → must be seen). */
function detectHookDefinition(relPath, text, cls) {
  const findings = [];
  const inHooksDir = /(?:^|\/)hooks\//.test(relPath);
  const base = path.basename(relPath).toLowerCase();
  // Match BOTH quoted (JSON) and unquoted (YAML) keys (red-team F1): a YAML hook
  // block uses `hooks:` / `PostToolUse:` with no quotes, which the quoted-only
  // pattern missed entirely — so an unquoted-YAML hook did not even CHALLENGE.
  const hooksKey = /(?:"hooks"|(?:^|\n)[ \t]*hooks)\s*:/;
  const eventKey =
    /(?:"(?:PreToolUse|PostToolUse|PreCompact|SessionStart|SessionEnd|UserPromptSubmit|Notification|Stop|SubagentStop)"|(?:^|\n)[ \t]*(?:PreToolUse|PostToolUse|PreCompact|SessionStart|SessionEnd|UserPromptSubmit|Notification|Stop|SubagentStop))\s*:/;
  if (
    (cls === 'json' || cls === 'yaml' || cls === 'doc' || inHooksDir) &&
    (hooksKey.test(text) || eventKey.test(text) || (inHooksDir && isScript(cls)))
  ) {
    const line = lineOf(text, hooksKey) || lineOf(text, eventKey) || 1;
    findings.push({
      id: 'hook-definition',
      grade: GRADE.CHALLENGE,
      line,
      label: 'hook definition (auto-executes in the agent)',
      snippet: base,
    });
  }
  return findings;
}

// ── secret-exfil-cooccur helpers (split by READ fidelity, see #985 defect 1) ──
// A read call whose argument (inside quotes) can name a credential file. Anchored
// to a READ so a security *denylist* of credential-file names (e.g. the slack MCP
// server's `SENDABLE_BASENAME_DENY` regex literals `/^id_rsa$/`, `/^\.netrc$/`)
// is NOT mistaken for a read of those files — the denylist is defence, not theft.
const SECRET_READ_CALL = String.raw`(?:open|io\.open|readFileSync|readFile|read_text|Path\([^)]*\)\.read_text)`;
// FOREIGN credential stores — reading one and shipping it off-host is theft, never
// the own-config API-client shape. Explicit list (extend deliberately): SSH keys,
// AWS/kube/docker/gcloud creds, system password files, netrc/git/npm/pypi/gnupg
// token stores, and browser cookie/login/keychain databases.
const FOREIGN_CRED_PATHS = String.raw`(?:\.ssh\/|id_rsa|id_ed25519|id_dsa|\.aws\/credentials|\.aws\/|\.kube\/config|\.docker\/config\.json|\.config\/gcloud|/etc\/shadow|/etc\/passwd|\.netrc|\.git-credentials|\.npmrc|\.pypirc|\.gnupg|Cookies|Login Data|Keychains|keychain|\.mozilla)`;
// Foreign-store read in python/js — a read call consuming a foreign path literal.
const FOREIGN_READ_SCRIPT = new RegExp(
  `${SECRET_READ_CALL}\\s*\\(\\s*[^\\n)]{0,60}['"\`][^'"\`\\n]*${FOREIGN_CRED_PATHS}`,
);
// Foreign-store read in shell — a read command (cat/head/…/source) consuming one.
const FOREIGN_READ_SHELL = new RegExp(
  `(?:\\b(?:cat|head|tail|less|xxd|base64|od|read|source)\\b|(?:^|[;&|()\\n]|[\\t ])\\.\\s+)[^\\n]{0,80}${FOREIGN_CRED_PATHS}`,
);

// Shell reads embedded in a recognized process API are still executable theft.
// Resolve namespace/named import aliases before inspecting call arguments:
// generic `runner.run()` / RegExp `.exec()` methods are not process APIs, while
// `cp.exec()`, `sp.run()`, and imported `check_output()` are. This matcher also
// runs on concatCollapse() output, exposing split command/path tokens and nested
// quote styles without weakening the API authority boundary.
const SHELL_READ_VERBS = String.raw`(?:cat|head|tail|less|xxd|base64|od|read|source)`;
const NODE_PROCESS_METHODS = new Set([
  'exec',
  'execSync',
  'execFile',
  'execFileSync',
  'spawn',
  'spawnSync',
]);
const PYTHON_PROCESS_METHODS = {
  subprocess: new Set(['run', 'Popen', 'check_output', 'check_call']),
  os: new Set(['system', 'popen']),
};

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function importedNames(clause, allowed, separator) {
  const names = [];
  for (const item of clause.split(',')) {
    const parts = item
      .trim()
      .split(separator)
      .map((part) => part.trim());
    const original = parts[0];
    const local = parts[1] || original;
    if (allowed.has(original) && /^[A-Za-z_$][\w$]*$/.test(local)) names.push(local);
  }
  return names;
}

function maskPythonTripleQuotedStrings(text) {
  return text.replace(/(?:[rubf]{0,2})?(?:"""[\s\S]*?"""|'''[\s\S]*?''')/gi, (match) =>
    match.replace(/[^\n]/g, ' '),
  );
}

function jsRegexCanStart(chars, offset) {
  let previous = offset - 1;
  while (previous >= 0 && /\s/.test(chars[previous])) previous--;
  if (previous < 0) return true;
  if ('=(:,!&|?{};[]+-*%^~<>'.includes(chars[previous])) return true;
  if (chars[previous] === ')') {
    let depth = 1;
    let cursor = previous - 1;
    for (; cursor >= 0 && depth > 0; cursor--) {
      if (chars[cursor] === ')') depth++;
      else if (chars[cursor] === '(') depth--;
    }
    if (depth === 0) {
      while (cursor >= 0 && /\s/.test(chars[cursor])) cursor--;
      const headerEnd = cursor + 1;
      while (cursor >= 0 && /[\w$]/.test(chars[cursor])) cursor--;
      const header = chars.slice(cursor + 1, headerEnd).join('');
      if (/^(?:if|while|for|with)$/.test(header)) return true;
    }
  }
  // The longest keyword below is "instanceof" (10 characters). Keep its
  // preceding boundary character too; copying the entire file prefix for
  // every division slash makes minified bundles quadratic to scan.
  const prefix = chars.slice(Math.max(0, previous - 10), previous + 1).join('');
  // Every JavaScript keyword that can immediately precede an expression. Keep
  // this list centralized so regex literals cannot poison later authority
  // discovery merely by appearing in an uncommon expression context.
  const keyword =
    /(?:^|[^\w$])(await|case|default|delete|do|else|extends|in|instanceof|new|of|return|throw|typeof|void|yield)$/.exec(
      prefix,
    );
  return Boolean(keyword);
}

function maskJsAuthorityNonCode(text) {
  const chars = [...text];
  for (let i = 0; i < chars.length; i++) {
    if (chars[i] === '/' && chars[i + 1] === '/') {
      while (i < chars.length && chars[i] !== '\n') chars[i++] = ' ';
      i--;
      continue;
    }
    if (chars[i] === '/' && chars[i + 1] === '*') {
      chars[i++] = ' ';
      chars[i] = ' ';
      while (i + 1 < chars.length && !(chars[i] === '*' && chars[i + 1] === '/')) {
        if (chars[i] !== '\n') chars[i] = ' ';
        i++;
      }
      if (i + 1 < chars.length) {
        chars[i] = ' ';
        chars[i + 1] = ' ';
        i++;
      }
      continue;
    }

    if (chars[i] === '/' && jsRegexCanStart(chars, i)) {
      let escaped = false;
      let inClass = false;
      let end = -1;
      for (let j = i + 1; j < chars.length; j++) {
        const char = chars[j];
        if (char === '\n') break;
        if (escaped) {
          escaped = false;
          continue;
        }
        if (char === '\\') {
          escaped = true;
          continue;
        }
        if (char === '[') inClass = true;
        else if (char === ']') inClass = false;
        else if (char === '/' && !inClass) {
          end = j;
          while (/[A-Za-z]/.test(chars[end + 1] || '')) end++;
          break;
        }
      }
      if (end >= 0) {
        for (let j = i; j <= end; j++) chars[j] = ' ';
        i = end;
        continue;
      }
    }

    const quote = chars[i];
    if (quote !== '"' && quote !== "'" && quote !== '`') continue;
    let escaped = false;
    let multiline = false;
    let end = i;
    for (let j = i + 1; j < chars.length; j++) {
      const char = chars[j];
      end = j;
      if (char === '\n') multiline = true;
      if (escaped) {
        escaped = false;
        continue;
      }
      if (char === '\\') {
        escaped = true;
        continue;
      }
      if (char === quote) break;
    }
    if (multiline) {
      for (let j = i; j <= end; j++) {
        if (chars[j] !== '\n') chars[j] = ' ';
      }
    }
    i = end;
  }
  return chars.join('');
}

function processAuthorityText(text, cls) {
  let cleaned = text;
  if (cls === 'js' || cls === 'doc') {
    cleaned = maskJsAuthorityNonCode(cleaned);
  }
  if (cls === 'python' || cls === 'doc') {
    cleaned = maskPythonTripleQuotedStrings(cleaned)
      .split('\n')
      .map((line) => stripLineComment(line, 'python'))
      .join('\n');
  }
  const collapsed = cleaned.split('\n').map(concatCollapse).join('\n');
  return `${cleaned}\n${collapsed}`;
}

function processApiAnchors(authorityText, cls) {
  const text = processAuthorityText(authorityText, cls);
  const anchors = new Set();
  const addBare = (name) => anchors.add(`(?<![.\\w$])${escapeRegex(name)}`);
  const addNamespace = (name, methods) => {
    for (const method of methods) {
      anchors.add(`\\b${escapeRegex(name)}\\s*\\.\\s*${escapeRegex(method)}`);
    }
  };

  if (cls === 'js' || cls === 'doc') {
    // Sync method names are process-specific enough to recognize when imported
    // outside a snippet. Async bare names are added only from a proven named
    // import/destructure below, avoiding generic user-defined `exec()`/`spawn()`.
    for (const method of ['execSync', 'execFileSync', 'spawnSync']) addBare(method);
    // The quoted form must close on the exact module name; the normalized
    // unquoted form needs an identifier boundary. This prevents modules such as
    // child_process_extra from granting process-launch authority.
    const moduleToken = String.raw`(?:['"](?:node:)?child_process['"]|(?:node:)?child_process(?=\s|[);]|$))`;
    const requireToken = `require\\s*\\(\\s*${moduleToken}\\s*\\)`;
    const namespacePatterns = [
      new RegExp(
        `(?:^|\\n)\\s*(?:const|let|var)\\s+([A-Za-z_$][\\w$]*)\\s*=\\s*${requireToken}`,
        'g',
      ),
      new RegExp(
        `(?:^|\\n)\\s*import\\s+\\*\\s+as\\s+([A-Za-z_$][\\w$]*)\\s+from\\s+${moduleToken}`,
        'g',
      ),
    ];
    for (const pattern of namespacePatterns) {
      for (const match of text.matchAll(pattern)) addNamespace(match[1], NODE_PROCESS_METHODS);
    }

    const namedPatterns = [
      {
        pattern: new RegExp(
          `(?:^|\\n)\\s*(?:const|let|var)\\s*\\{([^}]+)\\}\\s*=\\s*${requireToken}`,
          'g',
        ),
        separator: /\s*:\s*/,
      },
      {
        pattern: new RegExp(`(?:^|\\n)\\s*import\\s*\\{([^}]+)\\}\\s*from\\s+${moduleToken}`, 'g'),
        separator: /\s+as\s+/,
      },
    ];
    for (const { pattern, separator } of namedPatterns) {
      for (const match of text.matchAll(pattern)) {
        for (const name of importedNames(match[1], NODE_PROCESS_METHODS, separator)) addBare(name);
      }
    }
  }

  if (cls === 'python' || cls === 'doc') {
    // Python permits multiple imports, aliases, semicolon-separated statements,
    // and trailing comments on the same physical line. Parse those statement
    // shapes explicitly instead of letting punctuation weaken module equality.
    for (const rawLine of text.split('\n')) {
      const codeLine = stripLineComment(rawLine, 'python');
      for (const rawStatement of codeLine.split(';')) {
        const statement = rawStatement.trim();
        const namespace = /^import\s+(.+)$/.exec(statement);
        if (namespace) {
          for (const item of namespace[1].split(',')) {
            const match = /^([A-Za-z_]\w*)(?:\s+as\s+([A-Za-z_]\w*))?$/.exec(item.trim());
            if (!match || !PYTHON_PROCESS_METHODS[match[1]]) continue;
            addNamespace(match[2] || match[1], PYTHON_PROCESS_METHODS[match[1]]);
          }
          continue;
        }

        const named = /^from\s+(subprocess|os)\s+import\s+(.+)$/.exec(statement);
        if (!named) continue;
        for (const name of importedNames(named[2], PYTHON_PROCESS_METHODS[named[1]], /\s+as\s+/)) {
          addBare(name);
        }
      }
    }
  }

  return [...anchors];
}

function hasForeignProcessRead(text, cls, authorityText = text) {
  const anchors = processApiAnchors(authorityText, cls);
  if (anchors.length === 0) return false;
  return new RegExp(
    `(?:${anchors.join('|')})\\s*\\(\\s*[^\\n)]{0,360}(?:\\b${SHELL_READ_VERBS}\\b|\\.\\s+)[^\\n)]{0,180}${FOREIGN_CRED_PATHS}`,
  ).test(text);
}

// Keep shell syntax out of executable Python/JavaScript classification. In
// particular, JavaScript permits whitespace (including a newline) around member
// access: `client . getCookies()` and `client\n  . getCookies()` are not shell
// dot-source commands. Documentation can contain either language, so it retains
// both matchers and is graded CHALLENGE rather than REFUSE below.
function hasForeignRead(text, cls, authorityText = text) {
  if (cls === 'shell') return FOREIGN_READ_SHELL.test(text);
  if (cls === 'doc') {
    return (
      FOREIGN_READ_SCRIPT.test(text) ||
      FOREIGN_READ_SHELL.test(text) ||
      hasForeignProcessRead(text, cls, authorityText)
    );
  }
  return FOREIGN_READ_SCRIPT.test(text) || hasForeignProcessRead(text, cls, authorityText);
}
// WHOLESALE environment harvest — dumping/iterating the ENTIRE environment (not a
// single named var). Theft-grade with a sink. The legit subprocess-merge idioms
// (`{ ...process.env }`, `Object.assign({}, process.env)`) are deliberately NOT
// here — a bundled runtime spreads the parent env into a child_process every day.
const ENV_HARVEST = new RegExp(
  '(?:dict\\s*\\(\\s*os\\.environ|os\\.environ\\.(?:copy|items|keys|values)\\s*\\(|' +
    '\\*\\*\\s*os\\.environ|json\\.dumps\\s*\\(\\s*os\\.environ|str\\s*\\(\\s*os\\.environ|' +
    'print\\s*\\(\\s*os\\.environ|for\\s+\\w+\\s+in\\s+os\\.environ|' +
    'JSON\\.stringify\\s*\\(\\s*process\\.env|Object\\.(?:keys|entries|values)\\s*\\(\\s*process\\.env|' +
    'for\\s*\\([^)]*\\bin\\s+process\\.env)',
);
// NAMED credential access — reading a SPECIFIC env var (`process.env.MYSERVICE_TOKEN`,
// `os.environ['X']`, `os.getenv('X')`). This is the standard API-client shape.
const NAMED_ENV_READ =
  /(?:process\.env\s*(?:\.[A-Za-z_$]|\[)|os\.environ\s*(?:\.get\s*\(|\[)|os\.getenv\s*\()/;
// A read of the skill's OWN local `.env` (config), anchored to a read call.
const LOCAL_ENV_READ = new RegExp(
  `${SECRET_READ_CALL}\\s*\\(\\s*[^\\n)]{0,60}['"\`][^'"\`\\n]*\\.env\\b`,
);
// Network SINK. curl/wget/nc added (beyond the py/js library calls) so a multi-line
// shell exfil (`CREDS=$(cat ~/.aws/credentials); curl --data …`) — which the
// single-line `secret-exfil` rule misses — co-occurs here.
const EXFIL_SINK =
  /(?:urllib\.request\.urlopen|urllib2\.urlopen|requests\.(?:post|put|patch)|httpx\.(?:post|put|patch)|http\.client|socket\.(?:connect|sendall)|\.sendall\s*\(|fetch\s*\(|axios\.(?:post|put)|https?\.request\s*\(|\b(?:curl|wget|ncat|nc)\b)/;

/**
 * Detect single-file secret exfiltration (red-team F4), graded by the FIDELITY of
 * the secret READ (#985 defect 1). The line-level `secret-exfil` rule is
 * curl/wget-piped-specific and misses the split-statement idiom
 * `open('~/.ssh/id_rsa').read()` … `urllib.request.urlopen(url, data)`; this is a
 * file-level co-occurrence check — a secret READ + a network SINK anywhere in the
 * same file.
 *
 * Grading split (both require a network sink present):
 *   REFUSE (theft — high-confidence) when the read is any of:
 *     • a FOREIGN credential store (another app's/user's secrets — ~/.aws, ~/.ssh,
 *       ~/.kube/config, /etc/shadow, browser cookie/keychain stores, …);
 *     • a WHOLESALE environment harvest (dumping/iterating all of process.env /
 *       os.environ) — the "scoop everything and POST it" shape;
 *     • OBFUSCATED — the secret read OR the sink is revealed only after the
 *       anti-evasion normalizer collapses split-token string concatenation.
 *     (doc → CHALLENGE, as before: prose does not auto-execute.)
 *   CHALLENGE (waivable, must be SEEN) when it is the OWN-CONFIG client shape:
 *     reads a SPECIFIC named env var / its own local `.env` and sends to a sink —
 *     the standard shape of every API-integration skill (its own token → its own
 *     service). Before #985 this hard-blocked the whole sync (mytradeledger mtl.py,
 *     the slack-channel MCP server, the governed-second-brain runtime). It is now a
 *     visible-but-waivable CHALLENGE; the sync PR runs `--warn-only`, so these
 *     surface without walling the pipeline while a real ~/.ssh harvester still
 *     REFUSEs (unwaivable by design).
 */
function detectSecretExfilCoOccurrence(relPath, text, cls) {
  const findings = [];
  if (!['shell', 'python', 'js', 'doc'].includes(cls)) return findings;

  // Concat-collapsed view (per-line, mirroring the line-rule scan) reveals
  // string-split tokens like `"fet"+"ch"(` → `fetch(` around the secret or sink.
  const collapsed = text.split('\n').map(concatCollapse).join('\n');

  const foreignRaw = hasForeignRead(text, cls);
  const harvestRaw = ENV_HARVEST.test(text);
  const namedRaw = NAMED_ENV_READ.test(text);
  const localEnvRaw = cls !== 'shell' && LOCAL_ENV_READ.test(text);
  const anySecretRaw = foreignRaw || harvestRaw || namedRaw || localEnvRaw;

  const sinkRaw = EXFIL_SINK.test(text);
  const sinkCollapsed = EXFIL_SINK.test(collapsed);
  if (!sinkRaw && !sinkCollapsed) return findings; // no network egress → not this rule

  // Obfuscation the normalizer flagged: a sink (or a secret read) that only
  // appears once split-token concatenation is collapsed. Scoped to the token so a
  // minified bundle's unrelated hex/escape noise does not trip it.
  const collapsedSecret =
    hasForeignRead(collapsed, cls, text) ||
    ENV_HARVEST.test(collapsed) ||
    NAMED_ENV_READ.test(collapsed);
  const obfuscated = (sinkCollapsed && !sinkRaw) || (collapsedSecret && !anySecretRaw);

  if (!anySecretRaw && !obfuscated) return findings; // sink but no secret read

  const theft = foreignRaw || harvestRaw || obfuscated;
  const line =
    lineOf(text, FOREIGN_READ_SCRIPT) ||
    lineOf(text, FOREIGN_READ_SHELL) ||
    lineOf(text, ENV_HARVEST) ||
    lineOf(text, NAMED_ENV_READ) ||
    lineOf(text, LOCAL_ENV_READ) ||
    lineOf(text, EXFIL_SINK) ||
    1;

  if (theft) {
    findings.push({
      id: 'secret-exfil-cooccur',
      grade: cls === 'doc' ? GRADE.CHALLENGE : GRADE.REFUSE,
      line,
      label:
        'foreign-store / wholesale-env / obfuscated secret read co-occurring with a network sink (single-file exfil)',
      snippet: path.basename(relPath),
    });
  } else {
    // Own-config client shape: a specific named credential / own `.env` → a sink.
    findings.push({
      id: 'secret-exfil-cooccur',
      grade: GRADE.CHALLENGE,
      line,
      label:
        'own-config credential + network sink — standard API-client shape; confirm the sink is the credential’s own service',
      snippet: path.basename(relPath),
    });
  }
  return findings;
}

/** Detect an MCP server config carrying a remote URL. */
function detectMcpRemote(relPath, text, cls) {
  const findings = [];
  const base = path.basename(relPath).toLowerCase();
  const looksMcp = base === '.mcp.json' || /"mcpServers"\s*:/.test(text);
  if (!looksMcp) return findings;
  const remoteUrl = /"url"\s*:\s*"https?:\/\//i;
  const remoteType = /"type"\s*:\s*"(?:http|sse|ws|websocket)"/i;
  if (remoteUrl.test(text) || remoteType.test(text)) {
    const line = lineOf(text, remoteUrl) || lineOf(text, remoteType) || 1;
    findings.push({
      id: 'mcp-remote',
      grade: GRADE.CHALLENGE,
      line,
      label: 'MCP server config with a remote URL',
      snippet: base,
    });
  }
  return findings;
}

/**
 * Detect an allowed-tools list that grants privileged tools. Graded split:
 *   - network tools (WebFetch / WebSearch) → CHALLENGE (rarer; a skill that can
 *     reach the network is the genuinely "must be seen" case for exfil).
 *   - Bash → FLAG only. Bash is table-stakes for skills (thousands declare it),
 *     so a CHALLENGE here would be a guaranteed false-positive storm — exactly
 *     what gets a gate disabled. A reviewer still sees the FLAG note.
 * (Without a base-vs-head diff we can't prove a grant is NEWLY added; on a
 * --changed-only run this only fires for a changed file, which is the closest
 * deterministic proxy for "adds".)
 */
function detectPrivilegedTools(relPath, text, cls) {
  if (!['doc', 'json', 'yaml'].includes(cls)) return [];
  const lines = text.split('\n');
  const findings = [];
  const header = /allowed[-_]tools\s*[:=]/i;
  const net = /\b(WebFetch|WebSearch)\b/;
  const bash = /\bBash\b/;
  for (let i = 0; i < lines.length; i++) {
    if (!header.test(lines[i])) continue;
    // Same line (inline list) or the following YAML/JSON list window.
    const windowText = lines.slice(i, i + 20).join('\n');
    if (net.test(windowText)) {
      findings.push({
        id: 'allowed-tools-network',
        grade: GRADE.CHALLENGE,
        line: i + 1,
        label: 'allowed-tools grants a network tool (WebFetch/WebSearch)',
        snippet: lines[i].trim().slice(0, 80),
      });
    } else if (bash.test(windowText)) {
      findings.push({
        id: 'allowed-tools-bash',
        grade: GRADE.FLAG,
        line: i + 1,
        label: 'allowed-tools grants Bash',
        snippet: lines[i].trim().slice(0, 80),
      });
    }
  }
  return findings;
}

/** 1-based line number of the first match of `re` in `text`, or 0. */
function lineOf(text, re) {
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) return i + 1;
  }
  return 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Core: scan one file's content → findings[]. Pure (no fs), so tests drive it
// directly with in-memory fixtures.
// ─────────────────────────────────────────────────────────────────────────────
/**
 * @param {string} text     file content (utf8)
 * @param {string} relPath  repo-relative path (drives file-class grading)
 * @returns {Array<{id,grade,line,label,snippet}>}
 */
export function scanContent(text, relPath) {
  const cls = fileClass(relPath);
  const findings = [];
  const seen = new Set();
  const push = (f) => {
    const key = `${f.id}:${f.line}`;
    if (seen.has(key)) return;
    seen.add(key);
    findings.push(f);
  };

  // File-level signals.
  for (const f of detectHookDefinition(relPath, text, cls)) push(f);
  for (const f of detectSecretExfilCoOccurrence(relPath, text, cls)) push(f);
  for (const f of detectMcpRemote(relPath, text, cls)) push(f);
  for (const f of detectPrivilegedTools(relPath, text, cls)) push(f);

  // Line-level signals over normalized (+ concat) views.
  const logical = normalizeLines(text, cls);
  for (const { n, text: lineText } of logical) {
    const collapsed = concatCollapse(lineText);
    for (const rule of LINE_RULES) {
      if (rule.langs !== '*' && !rule.langs.includes(cls)) continue;
      const views = rule.concatSafe === false ? [lineText] : [lineText, collapsed];
      let matched = null;
      for (const v of views) {
        const m = rule.re.exec(v);
        if (m) {
          matched = m[0];
          break;
        }
      }
      if (!matched) continue;
      const grade = typeof rule.grade === 'function' ? rule.grade(cls) : rule.grade;
      push({
        id: rule.id,
        grade,
        line: n,
        label: rule.label,
        snippet: matched.trim().slice(0, 100),
      });
    }
    // Homoglyph — only when there IS a non-ASCII letter adjacent to ASCII.
    if (HOMOGLYPH_RE.test(lineText)) {
      push({
        id: 'homoglyph',
        grade: GRADE.FLAG,
        line: n,
        label: 'non-ASCII homoglyph adjacent to ASCII in code',
        snippet: lineText.trim().slice(0, 80),
      });
    }
  }
  return findings;
}

/**
 * Scan a source's filtered files IN MEMORY for the REFUSE grade (high-confidence
 * malicious content in an auto-executing file). Returns the REFUSE findings,
 * each tagged with its repo-relative path.
 *
 * Blocker 62ye.2: the sync engine (sync-external.mjs) calls this per-source
 * BEFORE writing any file, so a poisoned source is quarantined — mirrors
 * nothing, nothing malicious touches disk (no revert), and co-synced clean
 * sources still sync — instead of the whole run walling. It lives HERE, in the
 * dependency-free scanner module, so the sync-time gate and its unit corpus stay
 * zero-install (sync-external.mjs pulls in js-yaml; the scanner does not). Pure
 * over the in-memory file list (`{ path, content }[]`), so it is unit-testable.
 */
export function refuseFindingsForSource(files, targetPath) {
  const out = [];
  for (const file of files || []) {
    const rel = targetPath ? `${targetPath}/${file.path}` : file.path;
    let text;
    try {
      text = Buffer.isBuffer(file.content) ? file.content.toString('utf8') : String(file.content);
    } catch {
      continue; // undecodable/binary — the content scanner is text-only
    }
    for (const f of scanContent(text, rel)) {
      if (f.grade === GRADE.REFUSE) out.push({ file: rel, id: f.id, label: f.label });
    }
  }
  return out;
}

// ─────────────────────────────────────────────────────────────────────────────
// Allowlist: `path:rule  reason`. Downgrades CHALLENGE/FLAG (never REFUSE).
// ─────────────────────────────────────────────────────────────────────────────
/** Parse allowlist text → [{ pathGlob, rule, reason }]. Reason is REQUIRED. */
export function parseAllowlist(text) {
  const out = [];
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    // Split off the reason: everything after the first run of 2+ spaces or a `#`.
    const m = /^(\S+?):([A-Za-z0-9-]+)(?:\s{2,}|\s*#\s*|\s+)(.+)$/.exec(line);
    if (!m) continue; // malformed (e.g. missing reason) → ignored, not honored
    const [, pathGlob, rule, reason] = m;
    if (!reason.trim()) continue;
    // `raw` (the trimmed source line) lets the one-shot waiver check (blocker
    // 62ye.3) compare a waiver against the lines a PR actually added.
    out.push({ pathGlob, rule, reason: reason.trim(), raw: line });
  }
  return out;
}

/** Glob (`*`/`**`) match for allowlist paths. */
function globMatch(glob, filePath) {
  const esc = glob
    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
    .replace(/\*\*/g, '<<DS>>')
    .replace(/\*/g, '[^/]*')
    .replace(/<<DS>>/g, '.*');
  return new RegExp('^' + esc + '$').test(filePath);
}

/** Is (filePath, ruleId) waived? REFUSE is never waivable. */
export function isWaived(waivers, filePath, ruleId, grade) {
  if (grade === GRADE.REFUSE) return null;
  for (const w of waivers) {
    if (w.rule !== ruleId) continue;
    if (w.pathGlob === filePath || globMatch(w.pathGlob, filePath)) return w.reason;
  }
  return null;
}

// Rules whose waiver is ONE-SHOT: honored only in the PR that introduces the
// allowlist line, never persistently after it lands on main. A standing
// `sources-change-unscanned` line would silently waive EVERY future sources.yaml
// change and kill the gate (blocker 62ye.3).
const ONE_SHOT_RULES = new Set(['sources-change-unscanned']);

/**
 * Drop one-shot waivers that were NOT added in the current PR's diff of the
 * allowlist. `addedLines` is the set of trimmed lines added to
 * scripts/scan-allowlist.txt vs the base. All other rules pass through unchanged
 * — their persistent-allowlist model is intentional. Pure, so it is unit-testable.
 * Fail-closed by construction: an empty `addedLines` set (diff uncomputable)
 * removes every one-shot waiver, so the gate re-fires rather than silently waiving.
 */
export function honoredWaivers(waivers, addedLines) {
  return waivers.filter((w) => !ONE_SHOT_RULES.has(w.rule) || (w.raw && addedLines.has(w.raw)));
}

// ─────────────────────────────────────────────────────────────────────────────
// Exit-code decision from a flat list of per-file findings.
// ─────────────────────────────────────────────────────────────────────────────
export function decideExit(findings, { warnOnly = false } = {}) {
  const active = findings.filter((f) => !f.waivedReason);
  const hasRefuse = active.some((f) => f.grade === GRADE.REFUSE);
  const hasChallenge = active.some((f) => f.grade === GRADE.CHALLENGE);
  if (hasRefuse) return 2;
  if (hasChallenge && !warnOnly) return 1;
  return 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// File collection.
// ─────────────────────────────────────────────────────────────────────────────
function isBinary(buf) {
  const n = Math.min(buf.length, 8000);
  for (let i = 0; i < n; i++) if (buf[i] === 0) return true;
  return false;
}

function walk(absDir, relPrefix, acc) {
  let entries;
  try {
    entries = fs.readdirSync(absDir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const ent of entries) {
    if (ent.name === '.git' || ent.name === 'node_modules') continue;
    const abs = path.join(absDir, ent.name);
    const rel = relPrefix ? `${relPrefix}/${ent.name}` : ent.name;
    if (ent.isDirectory()) walk(abs, rel, acc);
    else if (ent.isFile()) acc.push(rel);
  }
}

class GitEnumerationError extends Error {}

/** Files changed vs a base ref (committed diff + staged + untracked). */
function changedFiles(base) {
  const run = (args) => {
    try {
      return execFileSync('git', ['-C', ROOT_DIR, ...args], {
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'ignore'],
      })
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean);
    } catch (error) {
      const operation = args.includes('--cached') ? 'staged diff' : args[0];
      throw new GitEnumerationError(
        `Git enumeration failed (${operation}; ${error.code ?? error.status ?? 'unknown failure'})`,
      );
    }
  };
  const set = new Set([
    ...run(['diff', '--name-only', '--diff-filter=d', base]),
    ...run(['diff', '--name-only', '--diff-filter=d', '--cached', base]),
    ...run(['ls-files', '--others', '--exclude-standard']),
  ]);
  return [...set];
}

/** Trimmed lines ADDED to scripts/scan-allowlist.txt vs `base` (blocker 62ye.3).
 * Feeds honoredWaivers so a one-shot waiver counts only in the PR that adds it.
 * Fail-closed: returns an empty set when the diff can't be computed (e.g. a
 * missing base ref), so a one-shot waiver is not honored and the gate re-fires. */
function addedAllowlistLines(base) {
  try {
    const out = execFileSync(
      'git',
      ['-C', ROOT_DIR, 'diff', '--unified=0', base, '--', 'scripts/scan-allowlist.txt'],
      { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] },
    );
    return new Set(
      out
        .split('\n')
        .filter((l) => l.startsWith('+') && !l.startsWith('+++'))
        .map((l) => l.slice(1).trim())
        .filter(Boolean),
    );
  } catch {
    return new Set();
  }
}

/**
 * True when a changed file's ENTIRE diff vs `base` is inert frontmatter
 * metadata — i.e. every added/removed line (hunk headers excluded) is a lone
 * `version: X` (YAML frontmatter), `"version": "X"` (JSON manifest), or
 * `compatibility: …` (YAML frontmatter) line.
 *
 * Why: a mass version reconstruction / auto-bump — or the E3.11
 * portability-claim withdrawal, which rewrote one compatibility line in 2,700
 * files — edits a single metadata string in thousands of first-party
 * SKILL.md + plugin.json files. Those files then show
 * up as "changed vs base" and, in --changed-only mode, get FULLY re-scanned —
 * surfacing every pre-existing documented dual-use example (the classic
 * secret-exfil-cooccur false positive in SaaS-pack API docs) as a fresh
 * CHALLENGE, even though the PR injected nothing.
 *
 * Skipping is SAFE, not a bypass: a lone version or compatibility metadata
 * line is never executed and carries no executable / exfil / network content
 * (the compatibility field is prose policed by its own ratchet,
 * check-portability-claims.mjs), and the moment ANY other line in the
 * file changes, this returns false and the file is scanned in full — so a
 * payload cannot hide behind a co-changed version bump. Fail-closed: if the
 * diff can't be computed, returns false (scan the file).
 */
export function isVersionOnlyChange(diffText) {
  if (!diffText) return false;
  const changed = diffText
    .split('\n')
    .filter(
      (l) =>
        (l.startsWith('+') || l.startsWith('-')) && !l.startsWith('+++') && !l.startsWith('---'),
    );
  if (changed.length === 0) return false; // no content delta we can attribute — scan it
  const YAML_VERSION = /^[+-]\s*version:\s*['"]?[\w.+-]+['"]?\s*(#.*)?$/;
  const JSON_VERSION = /^[+-]\s*"version":\s*"[\w.+-]+",?\s*$/;
  // A lone compatibility metadata line: prose only — no quotes into shell,
  // no URLs-with-pipes; anything shaped like an execution vector fails the
  // metadata test and forces a full scan.
  const YAML_COMPAT = /^[+-]\s*compatibility:\s*['"]?[\w ,.()-]+['"]?\s*$/;
  return changed.every((l) => YAML_VERSION.test(l) || JSON_VERSION.test(l) || YAML_COMPAT.test(l));
}

function isVersionOnlyDiff(base, rel) {
  try {
    const out = execFileSync('git', ['-C', ROOT_DIR, 'diff', '--unified=0', base, '--', rel], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    return isVersionOnlyChange(out);
  } catch {
    return false; // fail closed — scan the file
  }
}

/** Resolve the list of repo-relative files to scan from CLI options. */
function collectTargets(opts) {
  let rels = [];
  if (opts.changedOnly) {
    // Scope to the sync's actual write surface (plugins/**). The mirrored
    // content is the threat model; first-party scripts/ + workflows are covered
    // by CodeQL/review and — critically — this scanner's OWN test fixtures live
    // under scripts/, so scanning them would self-flag the malicious sample
    // strings. sources.yaml-only PRs legitimately produce no plugin diff here;
    // their protection is the sync-time scan of the resulting mirrored content.
    const base = opts.base || 'origin/main';
    rels = changedFiles(base)
      .filter((r) => r.startsWith('plugins/'))
      // Drop files whose only change is the version string (mass version
      // reconstruction / auto-bump) — provably inert, see isVersionOnlyChange.
      .filter((r) => !isVersionOnlyDiff(base, r));
  } else if (opts.paths.length > 0) {
    for (const p of opts.paths) {
      const abs = path.resolve(ROOT_DIR, p);
      let st;
      try {
        st = fs.statSync(abs);
      } catch {
        continue;
      }
      if (st.isDirectory()) {
        const acc = [];
        walk(abs, path.relative(ROOT_DIR, abs), acc);
        rels.push(...acc);
      } else {
        rels.push(path.relative(ROOT_DIR, abs));
      }
    }
  } else {
    const acc = [];
    walk(path.join(ROOT_DIR, DEFAULT_SCAN_ROOT), DEFAULT_SCAN_ROOT, acc);
    rels = acc;
  }
  // Git paths and scanner policy are repository-relative POSIX paths. Convert
  // native Windows `path.relative()` results before extensionless hook checks.
  rels = rels.map((rel) => normalizeScanPath(rel));

  // Keep only existing, scannable files.
  return rels.filter((rel) => {
    if (!isScannablePath(rel)) return false;
    return fs.existsSync(path.resolve(ROOT_DIR, rel));
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// CLI
// ─────────────────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const opts = { changedOnly: false, base: null, warnOnly: false, json: false, paths: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--changed-only') opts.changedOnly = true;
    else if (a === '--warn-only') opts.warnOnly = true;
    else if (a === '--json') opts.json = true;
    else if (a === '--base') opts.base = argv[++i];
    else if (a.startsWith('--base=')) opts.base = a.slice('--base='.length);
    else if (a.startsWith('--')) {
      /* ignore unknown flags */
    } else opts.paths.push(a);
  }
  return opts;
}

function loadWaivers() {
  if (!fs.existsSync(ALLOWLIST_FILE)) return [];
  try {
    return parseAllowlist(fs.readFileSync(ALLOWLIST_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function log(msg, color = '') {
  console.log(`${color}${msg}${colors.reset}`);
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const waivers = loadWaivers();
  const targets = collectTargets(opts);

  const gradeColor = { REFUSE: colors.red, CHALLENGE: colors.yellow, FLAG: colors.magenta };
  const gradeIcon = { REFUSE: '✗', CHALLENGE: '⚠', FLAG: 'ℹ' };

  let all = [];
  let scanned = 0;
  const perFile = [];

  for (const rel of targets) {
    const abs = path.resolve(ROOT_DIR, rel);
    let buf;
    try {
      buf = fs.readFileSync(abs);
    } catch {
      continue;
    }
    scanned++;
    let findings = [];
    if (isBinary(buf)) {
      if (buf.length > 256 * 1024) {
        findings.push({
          id: 'large-binaryish',
          grade: GRADE.FLAG,
          line: 1,
          label: `unusually large binary-ish file (${Math.round(buf.length / 1024)} KB)`,
          snippet: path.basename(rel),
        });
      }
    } else {
      findings = scanContent(buf.toString('utf8'), rel);
    }
    for (const f of findings) {
      f.file = rel;
      f.waivedReason = isWaived(waivers, rel, f.id, f.grade);
    }
    if (findings.length) perFile.push({ rel, findings });
    all = all.concat(findings);
  }

  // F6/F7 — trust-surface change with nothing to scan must not pass silently.
  // In --changed-only mode we scope to plugins/**, so a root sources.yaml /
  // sources.lock.json edit (adding or repointing an upstream source) scans zero
  // files and would go green. The mirrored content of the new source is scanned
  // at sync time, but a human must still confirm the source is vetted + pinned —
  // so emit a waivable CHALLENGE (fails the gate loudly; a reviewer clears it with
  // a `sources.yaml:sources-change-unscanned  <reason>` line in scan-allowlist.txt).
  if (opts.changedOnly && scanned === 0) {
    const trustFiles = changedFiles(opts.base || 'origin/main').filter(
      (r) => r === 'sources.yaml' || r === 'sources.yml' || r === 'sources.lock.json',
    );
    if (trustFiles.length) {
      const f = {
        id: 'sources-change-unscanned',
        grade: GRADE.CHALLENGE,
        line: 1,
        label:
          'source-list change with no mirrored content in this diff — the changed source is ' +
          'scanned at sync time; confirm it is vetted and pinned in sources.lock.json',
        snippet: trustFiles.join(', ').slice(0, 100),
        file: trustFiles[0],
      };
      // One-shot (blocker 62ye.3): honor a sources-change-unscanned waiver only
      // if its allowlist line was added in THIS PR — a standing line on main
      // would waive every future sources.yaml change and silently kill the gate.
      const fresh = honoredWaivers(waivers, addedAllowlistLines(opts.base || 'origin/main'));
      f.waivedReason = isWaived(fresh, f.file, f.id, f.grade);
      perFile.push({ rel: f.file, findings: [f] });
      all = all.concat(f);
    }
  }

  const exitCode = decideExit(all, { warnOnly: opts.warnOnly });

  if (opts.json) {
    // Use process.stdout.write (not console.log + process.exit) so a large
    // report is fully flushed to a pipe before the process exits — process.exit
    // can truncate a big buffered write mid-flush.
    process.stdout.write(
      JSON.stringify({ scanned, findings: all, exitCode, warnOnly: opts.warnOnly }, null, 2) + '\n',
    );
    process.exitCode = exitCode;
    return;
  }

  log('🔒 Scanning synced content for injected payloads…\n', colors.bright + colors.cyan);
  log(
    `Scanned ${scanned} file(s)${opts.changedOnly ? ` (changed vs ${opts.base || 'origin/main'})` : ''}\n`,
    colors.dim,
  );

  const counts = { REFUSE: 0, CHALLENGE: 0, FLAG: 0, waived: 0 };
  for (const { rel, findings } of perFile) {
    for (const f of findings) {
      if (f.waivedReason) {
        counts.waived++;
        log(
          `  ✓ ${rel}:${f.line} [${f.grade} WAIVED] ${f.id} — ${f.label} (waived: ${f.waivedReason})`,
          colors.dim,
        );
      } else {
        counts[f.grade]++;
        const c = gradeColor[f.grade];
        log(`  ${gradeIcon[f.grade]} ${rel}:${f.line} [${f.grade}] ${f.id} — ${f.label}`, c);
        log(`      matched: ${f.snippet}`, colors.dim);
      }
    }
  }

  if (counts.REFUSE + counts.CHALLENGE + counts.FLAG === 0) {
    log('  ✓ No suspicious patterns detected', colors.green);
  }

  log(
    `\n📊 ${counts.REFUSE} REFUSE · ${counts.CHALLENGE} CHALLENGE · ${counts.FLAG} FLAG · ${counts.waived} waived\n`,
    colors.bright,
  );

  if (exitCode === 2) {
    log('❌ REFUSE — high-confidence malicious content. Sync/PR blocked.\n', colors.red);
  } else if (exitCode === 1) {
    log(
      '⚠️  CHALLENGE — dual-use content needs human sign-off. Add a `path:rule  reason` waiver\n' +
        '   to scripts/scan-allowlist.txt (in this PR) once reviewed, or fix the source.\n',
      colors.yellow,
    );
  } else if (opts.warnOnly && counts.CHALLENGE > 0) {
    log(
      '⚠️  CHALLENGE present but --warn-only set (REFUSE would still block). Review the auto-PR.\n',
      colors.yellow,
    );
  } else {
    log('✅ No blocking findings.\n', colors.green);
  }

  process.exitCode = exitCode;
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    if (!(error instanceof GitEnumerationError)) throw error;
    console.error(`scan-synced-content: ${error.message}`);
    process.exitCode = 1;
  }
}

/*
 * KNOWN BYPASSES (this is a pattern scanner, NOT a sandbox — defense in depth):
 *   - Command-name indirection via a RUNTIME value: `C=$(printf '\x63url'); $C … | sh`,
 *     an env-var-built binary name, or `${arr[@]}` reassembly. We collapse
 *     compile-time quote/`+` concatenation only.
 *   - A payload delivered as base64/gzip DATA that a *later* step or a fetched
 *     remote resource decodes+executes. We flag long base64 blobs (FLAG) but do
 *     not decode-and-re-scan, and we cannot see what a remote URL returns.
 *   - Logic split across MULTIPLE files (read secret in file A, POST in file B).
 *     Our exfil rules are single-logical-line.
 *   - Novel homoglyph ranges beyond Greek/Cyrillic, or an all-non-ASCII identifier.
 *   - Semantically-malicious but syntactically-benign code (a legit-looking API
 *     client that ships data to an attacker endpoint whose URL passes our checks).
 *   - Anything in a file type we don't scan, or below our size/threshold cutoffs.
 * The mitigation for all of these is layered review: REFUSE hard-blocks the
 * obvious classes; CHALLENGE forces a human onto the dual-use classes; the
 * auto-sync PR is itself reviewed before merge; and gitleaks/CodeQL run in
 * parallel. This scanner raises the cost of the cheap attacks, it does not
 * eliminate a determined, sandbox-grade adversary.
 */
