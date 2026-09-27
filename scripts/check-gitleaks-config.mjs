#!/usr/bin/env node
// check-gitleaks-config.mjs — the E4.5 allowlist-shape ratchet (blueprint 727).
//
// The pre-E4.5 .gitleaks.toml excluded ~67% of tracked files through file-TYPE
// blankets (every SKILL.md / README.md / CHANGELOG.md / references/*.md /
// tests/ / fixtures/ / 000-docs/*.md), including the exact tests/fixtures/
// location other docs recommend for test secrets. This gate keeps that class
// of allowlist from coming back:
//
//   1. No path entry may re-introduce a banned file-type blanket.
//   2. Every path entry must be governed by a contiguous comment block
//      directly above it (shared blocks cover consecutive entries) carrying
//      both "reason:" and "expiry:" — a specific surface with a written
//      justification, never an anonymous exclusion.
//
// Values (placeholder examples) belong in the [allowlist] regexes/stopwords
// sections. Credential-shaped literals do not: historical findings belong in
// .gitleaksignore as commit-bound fingerprints, without retaining key material.

import { readFileSync } from 'node:fs';
import { resolve, dirname, posix } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { parse } from 'smol-toml';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
// v4.31.0 is a fixed annotated release predating this policy. Rotate this
// anchor only in a reviewed policy change that proves every retained
// fingerprint is still reachable; never move or recreate the existing tag.
export const TRUSTED_PROVENANCE_ANCHOR = Object.freeze({
  ref: 'refs/tags/v4.31.0',
  object: '742d4d45d090027618569f6ad1c82498535e8ca3',
});

// Second provenance anchor for history that landed after the release tag: a
// pinned commit that must itself already be on protected main. A pull request
// cannot make its own commit an ancestor of a commit that is already on main,
// and if it re-pins this constant to one of its own commits, the anchor is not
// yet on main during the PR run, so the required check fails. Advance it only
// in a reviewed change, to a commit that is already on main.
export const TRUSTED_MAIN_ANCHOR = Object.freeze({
  commit: '22e2983eeb1fb142489cf8027992813956c4b92f',
  branch: 'refs/remotes/origin/main',
});

// A path entry containing any of these re-creates a type blanket. Substring
// match against the raw TOML literal-string entry.
export const BANNED_FRAGMENTS = [
  'README\\.md',
  'CHANGELOG\\.md',
  'SKILL\\.md',
  '/references/',
  'tests?/',
  '__tests__',
  'fixtures/',
  '^000-docs/',
  '\\.(test|spec)\\.',
];

const GOOGLE_API_KEY_LITERAL = /AIza[0-9A-Za-z_-]{35}/;
const GOOGLE_API_KEY_GLOBAL = /AIza[0-9A-Za-z_-]{35}/g;
// Gitleaks' generic-api-key rule only fires on a line carrying one of these
// keywords, so a fingerprint whose line has none cannot point at the finding.
const GENERIC_KEY_KEYWORD = /access|auth|api|credential|creds|key|passw(or)?d|secret|token/i;

// Path exceptions are security policy, not an extensible regex language. A new
// exception therefore requires an explicit validator review in the same diff.
export const APPROVED_PATH_PATTERNS = [
  '^\\.gitleaks\\.toml$',
  '^scripts/validate-skills-schema\\.py$',
  '^plugins/security/penetration-tester/skills/scanning-for-hardcoded-secrets/scripts/scan_secrets\\.py$',
  '^skills/\\.curated/scanning-for-hardcoded-secrets/scripts/scan_secrets\\.py$',
  '^marketplace/src/data/skills-catalog\\.json$',
];
const APPROVED_PATH_PATTERN_SET = new Set(APPROVED_PATH_PATTERNS);
const APPROVED_ALLOWLIST_FIELDS = new Set(['description', 'paths', 'regexes', 'stopwords']);
const APPROVED_VALUE_REGEXES_SHA256 =
  'e77ec350a71ea17b150924256b2992e89b529b6291bae5dbb659312c4aee714b';
const APPROVED_STOPWORDS_SHA256 =
  'daa081cdc58be121ef5c0a1850462f324f91b4218a9049834c30db0e32d929b0';

const PERMANENT_EXCEPTIONS = new Map([
  [
    '^\\.gitleaks\\.toml$',
    {
      reason: 'this config file itself holds detector and allowlist regexes',
      expiry: 'none (self-referential by construction)',
    },
  ],
]);

function collectStrings(value, strings = []) {
  if (typeof value === 'string') strings.push(value);
  else if (Array.isArray(value)) value.forEach((entry) => collectStrings(entry, strings));
  else if (value && typeof value === 'object') {
    Object.values(value).forEach((entry) => collectStrings(entry, strings));
  }
  return strings;
}

function jsonDigest(value) {
  return createHash('sha256').update(JSON.stringify(value)).digest('hex');
}

function metadataValue(commentBlock, label) {
  const expression = new RegExp(`^#\\s*${label}\\s*:\\s*(.*)$`);
  const values = commentBlock
    .map((line) => line.match(expression))
    .filter(Boolean)
    .map((match) => match[1].trim());
  return values.length === 1 && values[0] !== '' ? values[0] : null;
}

function validExpiry(commentBlock, pattern) {
  const value = metadataValue(commentBlock, 'expiry');
  if (value === null) return false;
  if (/^none\b/i.test(value)) {
    const exception = PERMANENT_EXCEPTIONS.get(pattern);
    return (
      exception?.expiry === value && metadataValue(commentBlock, 'reason') === exception.reason
    );
  }
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})(?:\s+\(.+\))?$/);
  if (!match) return false;
  const [, year, month, day] = match;
  const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
  const isCalendarDate =
    date.getUTCFullYear() === Number(year) &&
    date.getUTCMonth() === Number(month) - 1 &&
    date.getUTCDate() === Number(day);
  if (!isCalendarDate) return false;
  const now = new Date();
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  return date.getTime() >= today;
}

function validReason(commentBlock) {
  return metadataValue(commentBlock, 'reason') !== null;
}

export function analyzeConfig(text) {
  const issues = [];
  let parsed;
  try {
    parsed = parse(text);
  } catch {
    issues.push({ code: 'TOML_PARSE_ERROR' });
  }

  if (parsed) {
    if (collectStrings(parsed).some((value) => GOOGLE_API_KEY_LITERAL.test(value))) {
      issues.push({ code: 'CREDENTIAL_LITERAL' });
    }
    if (Object.hasOwn(parsed, 'allowlists')) {
      issues.push({ code: 'UNSUPPORTED_GLOBAL_ALLOWLISTS' });
    }
    const globalAllowlist = parsed.allowlist;
    if (globalAllowlist && typeof globalAllowlist === 'object') {
      if (Object.keys(globalAllowlist).some((key) => !APPROVED_ALLOWLIST_FIELDS.has(key))) {
        issues.push({ code: 'UNSUPPORTED_GLOBAL_ALLOWLIST_FIELD' });
      }
      if (
        globalAllowlist.regexes !== undefined &&
        (!Array.isArray(globalAllowlist.regexes) ||
          jsonDigest(globalAllowlist.regexes) !== APPROVED_VALUE_REGEXES_SHA256)
      ) {
        issues.push({ code: 'UNAPPROVED_ALLOWLIST_REGEX' });
      }
      if (
        globalAllowlist.stopwords !== undefined &&
        (!Array.isArray(globalAllowlist.stopwords) ||
          jsonDigest(globalAllowlist.stopwords) !== APPROVED_STOPWORDS_SHA256)
      ) {
        issues.push({ code: 'UNAPPROVED_ALLOWLIST_STOPWORD' });
      }
    }
    if (parsed.rules !== undefined && !Array.isArray(parsed.rules)) {
      issues.push({ code: 'INVALID_RULES_SHAPE' });
    } else if (
      parsed.rules?.some(
        (rule) =>
          rule &&
          typeof rule === 'object' &&
          (Object.hasOwn(rule, 'allowlist') || Object.hasOwn(rule, 'allowlists')),
      )
    ) {
      issues.push({ code: 'UNSUPPORTED_RULE_ALLOWLIST' });
    }
  }

  const lines = text.split('\n');
  let inPaths = false;
  let inAllowlist = false;
  let commentBlock = [];
  let previousWasEntry = false;
  let entries = 0;
  const documentedPatterns = [];

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();
    if (
      GOOGLE_API_KEY_LITERAL.test(line) &&
      !issues.some((issue) => issue.code === 'CREDENTIAL_LITERAL')
    ) {
      issues.push({ code: 'CREDENTIAL_LITERAL', line: i + 1 });
    }
    if (!inPaths) {
      if (/^\[[^[]/.test(trimmed)) {
        inAllowlist = trimmed === '[allowlist]';
        continue;
      }
      if (inAllowlist && /^paths\s*=/.test(trimmed)) {
        if (!/^paths\s*=\s*\[\s*$/.test(trimmed)) {
          issues.push({ code: 'UNSUPPORTED_PATHS_SYNTAX', line: i + 1 });
        }
        inPaths = true;
      }
      continue;
    }
    if (trimmed === ']') break;
    if (trimmed === '') {
      commentBlock = [];
      previousWasEntry = false;
      continue;
    }
    if (trimmed.startsWith('#')) {
      if (previousWasEntry) commentBlock = [];
      commentBlock.push(trimmed);
      previousWasEntry = false;
      continue;
    }
    const entry = trimmed.match(/^'''(.*)''',?$/);
    if (!entry) {
      issues.push({ code: 'UNPARSEABLE_PATH_LINE', line: i + 1 });
      continue;
    }
    entries += 1;
    previousWasEntry = true;
    const pattern = entry[1];
    documentedPatterns.push(pattern);
    for (const banned of BANNED_FRAGMENTS) {
      if (pattern.includes(banned)) {
        issues.push({ code: 'TYPE_BLANKET', line: i + 1 });
      }
    }
    if (!APPROVED_PATH_PATTERN_SET.has(pattern)) {
      issues.push({ code: 'UNAPPROVED_PATH_PATTERN', line: i + 1 });
    }
    try {
      new RegExp(pattern);
    } catch {
      issues.push({ code: 'INVALID_PATH_REGEX', line: i + 1 });
    }
    if (!validReason(commentBlock) || metadataValue(commentBlock, 'expiry') === null) {
      issues.push({ code: 'UNDOCUMENTED_EXCEPTION', line: i + 1 });
    } else if (!validExpiry(commentBlock, pattern)) {
      issues.push({ code: 'INVALID_EXPIRY', line: i + 1 });
    }
    // A shared comment block may govern consecutive entries; keep it active.
  }

  if (!inPaths) issues.push({ code: 'NO_PATHS_SECTION' });
  const semanticPaths = parsed?.allowlist?.paths;
  if (parsed && !Array.isArray(semanticPaths)) {
    issues.push({ code: 'NO_PATHS_SECTION' });
  } else if (Array.isArray(semanticPaths) && semanticPaths.length !== entries) {
    issues.push({ code: 'PATH_ENTRY_COUNT_MISMATCH' });
  } else if (
    Array.isArray(semanticPaths) &&
    semanticPaths.some((pattern, index) => pattern !== documentedPatterns[index])
  ) {
    issues.push({ code: 'PATH_ENTRY_VALUE_MISMATCH' });
  }
  return { entries, issues, allow: issues.length === 0 };
}

function parseFingerprint(line) {
  const match = line.match(/^([0-9a-f]{40}):([^:\n]+):([a-z0-9-]+):([1-9][0-9]*)$/);
  if (!match) return null;
  return { commit: match[1], path: match[2], rule: match[3], line: Number(match[4]) };
}

function isNormalizedRepositoryPath(path) {
  return (
    path.length > 0 &&
    !path.startsWith('/') &&
    !path.startsWith('./') &&
    !path.includes('\\') &&
    !path.includes('//') &&
    posix.normalize(path) === path &&
    path !== '.' &&
    path !== '..' &&
    !path.startsWith('../')
  );
}

export function validateFingerprintSourceLine(sourceLine, rule = 'gcp-api-key') {
  if (rule === 'generic-api-key') {
    // A generic finding is suppressed only after it is classified synthetic
    // and documented under a "# reason:" header; this check only proves the
    // entry still points at a line the rule could have matched.
    return typeof sourceLine === 'string' && GENERIC_KEY_KEYWORD.test(sourceLine)
      ? { ok: true }
      : { ok: false, code: 'FINGERPRINT_FINDING_MISMATCH' };
  }
  const findings = sourceLine?.match(GOOGLE_API_KEY_GLOBAL) ?? [];
  if (findings.length === 0) return { ok: false, code: 'FINGERPRINT_FINDING_MISMATCH' };
  if (findings.length > 1) return { ok: false, code: 'AMBIGUOUS_FINGERPRINT_LINE' };
  return { ok: true };
}

// Rules that may be suppressed by an exact fingerprint. Anything else fails.
export const SUPPORTED_FINGERPRINT_RULES = Object.freeze(['gcp-api-key', 'generic-api-key']);

function git(root, args) {
  return execFileSync('git', ['-C', root, ...args], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'ignore'],
    maxBuffer: 10 * 1024 * 1024,
  });
}

function reachableFromReleaseAnchor(root, commit, anchor) {
  try {
    git(root, ['cat-file', '-e', `${anchor.ref}^{tag}`]);
    if (git(root, ['rev-parse', anchor.ref]).trim() !== anchor.object) return false;
    git(root, ['merge-base', '--is-ancestor', commit, `${anchor.ref}^{commit}`]);
    return true;
  } catch {
    return false;
  }
}

function reachableFromMainAnchor(root, commit, anchor) {
  if (!anchor) return false;
  try {
    git(root, ['cat-file', '-e', `${anchor.commit}^{commit}`]);
    // The anchor must already be on protected main...
    git(root, ['merge-base', '--is-ancestor', anchor.commit, anchor.branch]);
    // ...and the fingerprinted commit must be in the anchor's history.
    git(root, ['merge-base', '--is-ancestor', commit, anchor.commit]);
    return true;
  } catch {
    return false;
  }
}

export function verifyFingerprintInRepository(
  entry,
  root = ROOT,
  trustedAnchor = TRUSTED_PROVENANCE_ANCHOR,
  mainAnchor = TRUSTED_MAIN_ANCHOR,
) {
  const fingerprint = parseFingerprint(entry);
  if (!fingerprint) return { ok: false, code: 'NON_COMMIT_BOUND_FINGERPRINT' };
  if (!isNormalizedRepositoryPath(fingerprint.path)) {
    return { ok: false, code: 'INVALID_FINGERPRINT_PATH' };
  }
  if (!SUPPORTED_FINGERPRINT_RULES.includes(fingerprint.rule)) {
    return { ok: false, code: 'UNSUPPORTED_FINGERPRINT_RULE' };
  }

  let content;
  try {
    git(root, ['cat-file', '-e', `${fingerprint.commit}^{commit}`]);
    if (
      !reachableFromReleaseAnchor(root, fingerprint.commit, trustedAnchor) &&
      !reachableFromMainAnchor(root, fingerprint.commit, mainAnchor)
    ) {
      return { ok: false, code: 'FINGERPRINT_SOURCE_UNREACHABLE' };
    }
    content = git(root, ['show', `${fingerprint.commit}:${fingerprint.path}`]);
  } catch {
    return { ok: false, code: 'FINGERPRINT_SOURCE_UNREACHABLE' };
  }

  const sourceLine = content.split(/\r?\n/)[fingerprint.line - 1];
  return validateFingerprintSourceLine(sourceLine, fingerprint.rule);
}

export function analyzeIgnore(text, verifyEntry = (entry) => verifyFingerprintInRepository(entry)) {
  const issues = [];
  const entries = [];
  const seen = new Set();

  for (const [index, raw] of text.split('\n').entries()) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const fingerprint = parseFingerprint(line);
    if (!fingerprint) {
      issues.push({ code: 'NON_COMMIT_BOUND_FINGERPRINT', line: index + 1 });
      continue;
    }
    if (!isNormalizedRepositoryPath(fingerprint.path)) {
      issues.push({ code: 'INVALID_FINGERPRINT_PATH', line: index + 1 });
      continue;
    }
    if (seen.has(line)) {
      issues.push({ code: 'DUPLICATE_FINGERPRINT', line: index + 1 });
      continue;
    }
    seen.add(line);
    if (typeof verifyEntry !== 'function') {
      issues.push({ code: 'MISSING_FINGERPRINT_VERIFIER', line: index + 1 });
      continue;
    }
    const verification = verifyEntry(line);
    if (!verification.ok) {
      issues.push({ code: verification.code, line: index + 1 });
      continue;
    }
    entries.push(line);
  }

  return { entries: entries.length, issues, allow: issues.length === 0 };
}

export function formatIssue(issue) {
  return `gitleaks-config: ${issue.code} at line ${issue.line ?? '?'}`;
}

function main() {
  const text = readFileSync(resolve(ROOT, '.gitleaks.toml'), 'utf8');
  const result = analyzeConfig(text);
  const ignoreResult = analyzeIgnore(
    readFileSync(resolve(ROOT, '.gitleaksignore'), 'utf8'),
    (entry) => verifyFingerprintInRepository(entry),
  );
  const issues = [...result.issues, ...ignoreResult.issues];
  if (issues.length > 0) {
    for (const issue of issues) {
      console.error(formatIssue(issue));
    }
    console.error('gitleaks-config: FAIL — see the allowlist policy header in .gitleaks.toml');
    process.exit(1);
  }
  console.log(
    `gitleaks-config: OK (${result.entries} documented path exceptions; ${ignoreResult.entries} commit-bound fingerprint; no type blankets or credential literals)`,
  );
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
