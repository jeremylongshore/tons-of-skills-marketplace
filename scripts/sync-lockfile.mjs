/**
 * sync-lockfile.mjs — content-pinning lockfile for the external plugin sync.
 *
 * THREAT MODEL: sources.yaml pins nothing — scripts/sync-external.mjs mirrors
 * each upstream's live default branch every Monday. A source vetted once at
 * listing silently absorbs every later upstream push, so a compromised or
 * rogue upstream author's next commit rides straight into the marketplace and
 * executes in users' agents.
 *
 * MITIGATION: sources.lock.json (repo root) records, per source, the upstream
 * commit the sync resolved plus a sha256 digest of every mirrored file. On
 * each sync run the engine diffs the freshly-cloned upstream content against
 * the lock BEFORE writing anything:
 *
 *   - new-source  → first sync of a human-listed source: mirror + record the
 *                   baseline (vetting-at-listing is the existing human gate).
 *   - unchanged   → mirror as today (no-op diffs).
 *   - drifted     → QUARANTINE: the source is skipped this run and the run is
 *                   flagged like a partial sync. The lock only advances via an
 *                   explicit --relock=<source> / --relock-all after a human
 *                   reviews the upstream diff.
 *
 * The lock file is deterministic (sorted keys, stable entry shape) so its git
 * diff IS the security review surface.
 *
 * This module is pure and testable: no I/O beyond reading/writing the lock
 * file at the path the caller passes. The sync engine (sync-external.mjs)
 * owns all cloning/mirroring; the one-time baseline bootstrap is documented
 * in the PR that introduced this file.
 *
 * Tests: node --test scripts/sync-lockfile.test.mjs
 */

import crypto from 'crypto';
import path from 'path';
import { safeReadFileIfExists, safeWriteFileAtomic } from './safe-fs.mjs';

// The lock is addressed as (its directory, its file name) so a symlinked or
// special-file lock is refused and the write is atomic (see safe-fs.mjs).
function lockLocation(lockPath) {
  const abs = path.resolve(lockPath);
  return { root: path.dirname(abs), rel: path.basename(abs) };
}

export const LOCK_VERSION = 1;

export const LOCK_COMMENT =
  'Content-pinning lockfile for the sources.yaml mirrors (scripts/sync-external.mjs). ' +
  'Each entry pins one upstream source: the resolved upstream commit and a sha256 per mirrored file. ' +
  'The diff of this file is the security review surface — a drifted source is quarantined by the sync ' +
  'and only re-baselined via an explicit --relock=<source> / --relock-all after human review. ' +
  'Managed by scripts/sync-lockfile.mjs; do not hand-edit digests.';

/**
 * Digest a file's exact bytes. Returns "sha256:<hex>".
 *
 * KNOWN LIMITATION (deliberate, 2026-07 ops review): the digest is CONTENT-ONLY
 * — the file mode (executable bit) is not folded in, so a mode-only upstream
 * change classifies as 'unchanged' and is NOT quarantined, yet the engine
 * self-heals the exec bit on write (sync-external.mjs reason='mode'). This
 * weakens the "lock unchanged ⇒ working tree unchanged" invariant for exactly
 * one low-impact class: an already-vetted, byte-identical script flipping ±x.
 * We accept it because (a) folding mode into the digest string would mismatch
 * every existing lock entry → mass drift-quarantine → a forced --relock-all,
 * the exact bulk rubber-stamp this lockfile exists to prevent; (b) a
 * backward-compatible `{sha256, mode}` entry shape adds branching to
 * buildLockEntry/diffSource/serializeLock for a gap whose payload (content) is
 * still pinned; and (c) the compensating control already exists — git records
 * the mode flip as an `old mode/new mode` hunk in the sync PR's diff, so the
 * reviewer sees it there even though sources.lock.json stays quiet. Revisit if
 * the lock format ever takes a version bump for another reason.
 */
export function computeFileDigest(buffer) {
  if (!Buffer.isBuffer(buffer)) {
    throw new TypeError('computeFileDigest expects a Buffer (exact bytes, not a decoded string)');
  }
  return `sha256:${crypto.createHash('sha256').update(buffer).digest('hex')}`;
}

/**
 * Build a lock entry for one source from its current upstream state.
 *
 * @param {{repo: string}} source        sources.yaml entry (only .repo is read)
 * @param {string|null} resolvedRef      upstream HEAD sha the sync resolved (null if unknown)
 * @param {Array<{path: string, sha256: string}>} currentFiles
 * @param {string} lockedAt              ISO timestamp of the baseline approval
 */
export function buildLockEntry(source, resolvedRef, currentFiles, lockedAt) {
  const files = {};
  for (const f of [...currentFiles].sort((a, b) => a.path.localeCompare(b.path))) {
    files[f.path] = f.sha256;
  }
  return {
    repo: source.repo,
    resolved_ref: resolvedRef ?? null,
    locked_at: lockedAt,
    files,
  };
}

/**
 * Load the lock file. A missing file yields an empty lock (every source then
 * classifies as new-source — the backward-compatible bootstrap path). A file
 * that EXISTS but cannot be parsed throws: fail closed rather than silently
 * treating a corrupted lock as "nothing is pinned".
 */
export function loadLock(lockPath) {
  const { root, rel } = lockLocation(lockPath);
  // Throws (fails closed) for a symlinked, directory or special-file lock.
  const existing = safeReadFileIfExists(root, rel);
  if (!existing) {
    return { $comment: LOCK_COMMENT, version: LOCK_VERSION, sources: {} };
  }
  let parsed;
  try {
    parsed = JSON.parse(existing.content.toString('utf8'));
  } catch (err) {
    throw new Error(
      `sources lock at ${lockPath} exists but is not valid JSON (${err.message}) — ` +
        'refusing to treat a corrupt lock as "unpinned". Fix or restore it from git.',
    );
  }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`sources lock at ${lockPath} must be a JSON object`);
  }
  // A present `sources` field that is not a JSON object (array, string, null)
  // must fail closed. Silently defaulting to `{}` would classify every pinned
  // source as new-source and re-baseline the whole lock — exactly the drift
  // quarantine bypass this file exists to prevent. An ABSENT `sources` field is
  // still fine (the empty-lock bootstrap path).
  if (
    parsed.sources !== undefined &&
    (parsed.sources === null || typeof parsed.sources !== 'object' || Array.isArray(parsed.sources))
  ) {
    throw new Error(
      `sources lock at ${lockPath} has an invalid "sources" field (must be a JSON object) — ` +
        'refusing to silently re-baseline every source. Fix or restore it from git.',
    );
  }
  return {
    $comment: typeof parsed.$comment === 'string' ? parsed.$comment : LOCK_COMMENT,
    version: typeof parsed.version === 'number' ? parsed.version : LOCK_VERSION,
    sources: parsed.sources ?? {},
  };
}

/**
 * Serialize a lock object deterministically: fixed top-level key order,
 * source names sorted, per-entry key order fixed (repo, resolved_ref,
 * locked_at, files), file paths sorted. Insertion order never leaks into the
 * output, so the git diff of the file is stable and reviewable.
 */
export function serializeLock(lock) {
  const out = {
    $comment: lock.$comment ?? LOCK_COMMENT,
    version: lock.version ?? LOCK_VERSION,
    sources: {},
  };
  const sources = lock.sources || {};
  for (const name of Object.keys(sources).sort()) {
    const e = sources[name] || {};
    const files = {};
    for (const p of Object.keys(e.files || {}).sort()) {
      files[p] = e.files[p];
    }
    out.sources[name] = {
      repo: e.repo,
      resolved_ref: e.resolved_ref ?? null,
      locked_at: e.locked_at,
      files,
    };
  }
  return JSON.stringify(out, null, 2) + '\n';
}

/**
 * Write the lock file (deterministic serialization). Skips the write when the
 * on-disk bytes are already identical, so an all-unchanged sync run does not
 * touch the file's mtime.
 */
export function saveLock(lockPath, lock) {
  const serialized = serializeLock(lock);
  const { root, rel } = lockLocation(lockPath);
  const existing = safeReadFileIfExists(root, rel);
  if (existing && existing.content.toString('utf8') === serialized) return false;
  safeWriteFileAtomic(root, rel, serialized);
  return true;
}

/**
 * Classify a source's freshly-fetched upstream content against the lock.
 *
 * @param {object} lock                  loaded lock object
 * @param {string} sourceName            sources.yaml `name`
 * @param {Array<{path: string, sha256: string}>} currentFiles
 * @returns {{status: 'unchanged'|'new-source'|'drifted', added: string[], removed: string[], changed: string[]}}
 */
export function diffSource(lock, sourceName, currentFiles) {
  const current = new Map(currentFiles.map((f) => [f.path, f.sha256]));
  const hasEntry =
    lock?.sources != null && Object.prototype.hasOwnProperty.call(lock.sources, sourceName);
  const entry = hasEntry ? lock.sources[sourceName] : null;

  // Only a genuinely ABSENT source is new. A source that is present in the lock
  // but whose entry is corrupt (missing/invalid `files`) must fail closed — not
  // be silently treated as new-source, which would re-baseline it and skip the
  // drift quarantine.
  if (!hasEntry) {
    return {
      status: 'new-source',
      added: [...current.keys()].sort(),
      removed: [],
      changed: [],
    };
  }

  if (!entry || !entry.files || typeof entry.files !== 'object' || Array.isArray(entry.files)) {
    throw new Error(
      `lock entry for source "${sourceName}" is corrupt or malformed (missing/invalid "files") — ` +
        'refusing to silently re-baseline it as a new source.',
    );
  }

  const locked = entry.files;
  const added = [];
  const removed = [];
  const changed = [];

  for (const [p, digest] of current) {
    if (!(p in locked)) {
      added.push(p);
    } else if (locked[p] !== digest) {
      changed.push(p);
    }
  }
  for (const p of Object.keys(locked)) {
    if (!current.has(p)) removed.push(p);
  }

  added.sort();
  removed.sort();
  changed.sort();

  const status = added.length + removed.length + changed.length === 0 ? 'unchanged' : 'drifted';
  return { status, added, removed, changed };
}

/**
 * Check if a path matches any of the glob patterns.
 *
 * Pattern semantics (matches sources.yaml's intent):
 *   - Bare filename (`SKILL.md`)   → matches at any depth (treated as `**\/SKILL.md`)
 *   - Plain dir glob (`references/**`) → matches at any depth (treated as `**\/references/**`)
 *   - Leading `**\/` or `/`        → explicit path semantics, no auto-prefix
 *   - `**`                          → zero or more dirs (translated to `.*`)
 *   - `*`                           → one path segment (no `/`)
 *   - `?`                           → single char
 *
 * Why the auto-prefix: sources.yaml includes typically list `SKILL.md`,
 * `README.md`, `references/**` with the intent "any depth," but the older
 * regex anchored at the root of source_path. Many upstream repos nest one
 * extra layer (e.g. skills/tools/<plugin>/skills/<plugin>/SKILL.md), so
 * the strict match dropped real files. Auto-prefixing fixes that without
 * needing every sources.yaml entry rewritten.
 */
export function matchesPattern(filePath, patterns) {
  if (!patterns || patterns.length === 0) return true;

  return patterns.some((rawPattern) => {
    // Auto-prefix `**/` unless the pattern already starts with `**` or `/`.
    // A leading `/` means "anchored to the source root": skip the auto-prefix
    // AND strip the slash, because candidate paths are root-relative (a
    // pattern compiled to ^/skills/... could never match 'skills/...' — the
    // anchor form was dead code until 2026-07-08, #985 defect 6).
    const pattern = rawPattern.startsWith('**')
      ? rawPattern
      : rawPattern.startsWith('/')
        ? rawPattern.slice(1)
        : `**/${rawPattern}`;

    // Order matters: handle `?` (single-char glob) BEFORE we insert any
    // literal `?` chars (like `(?:.*/)?`) into the regex pattern. Then
    // substitute glob tokens left-to-right via unique placeholders so
    // they don't overlap.
    const escaped = pattern
      .replace(/\?/g, '<<<Q>>>') // glob `?` placeholder (before we add literal `?`)
      .replace(/\./g, '\\.') // escape literal dots (`.md` etc)
      .replace(/\*\*\//g, '<<<DSS>>>') // `**/` → zero or more dirs
      .replace(/\*\*/g, '<<<DS>>>') // bare `**` → anything
      .replace(/\*/g, '[^/]*') // `*` → single segment
      .replace(/<<<DSS>>>/g, '(?:.*/)?') // ← contains literal `?`, must come AFTER /\?/g
      .replace(/<<<DS>>>/g, '.*')
      .replace(/<<<Q>>>/g, '.');

    const regex = new RegExp('^' + escaped + '$');
    return regex.test(filePath);
  });
}

/**
 * Include patterns that matchesPattern will silently auto-prefix with `**\/`
 * — i.e. those that start with neither `/` (root-anchored) nor `**` (explicitly
 * recursive). Blocker 62ye.6: a vetter reading `README.md` per the source-
 * vetting playbook believes it mirrors the ROOT README, but the auto-prefix
 * makes it `**\/README.md`, admitting every README at any depth (unvetted
 * examples/, vendored dirs, …). Returning the offenders lets the sync flow warn
 * the vetter so intent is explicit — anchor with `/README.md` or write the
 * recursion out as `**\/README.md`. Pure (no side effects) so it is unit-testable;
 * NON-breaking — matchesPattern's behavior is unchanged, this only surfaces it.
 */
export function unanchoredIncludes(patterns) {
  return (patterns || []).filter(
    (p) => typeof p === 'string' && !p.startsWith('/') && !p.startsWith('**'),
  );
}

/**
 * A mirror's declared include list must explicitly carry a license file. The
 * sync engine installs the selected upstream file at the mirror root, so a
 * nested glob is not sufficient: consumers must receive the text alongside
 * the mirrored bytes. Kept pure so both the runtime gate and CI can share the
 * exact policy.
 */
export function hasRootLicenseInclude(patterns) {
  return (patterns || []).some(
    (pattern) =>
      typeof pattern === 'string' && /^\/?(?:LICENSE|COPYING)(?:[.-][^/]*)?$/i.test(pattern),
  );
}

/**
 * A license file must land at the root of every mirror, not only somewhere in
 * a nested upstream directory. This is intentionally stricter than the
 * include matcher, whose ordinary bare-file behavior is recursive.
 */
export function isRootLicenseFile(filePath) {
  return typeof filePath === 'string' && /^(?:LICENSE|COPYING)(?:[.-][^/]*)?$/i.test(filePath);
}
