/**
 * sync-lockfile.test.mjs — unit corpus for the content-pinning lockfile.
 *
 * Covers the contract sync-external.mjs relies on to quarantine upstream
 * drift (see scripts/sync-lockfile.mjs for the threat model):
 *   - digest determinism (exact bytes in, stable "sha256:<hex>" out)
 *   - new-source vs unchanged vs drifted classification, incl. per-file
 *     added / removed / changed accounting
 *   - a drifted source classifies drifted even when only ONE byte of ONE
 *     file changed (the minimal-supply-chain-payload case)
 *   - deterministic lock serialization (insertion order never leaks; the
 *     git diff of sources.lock.json is the review surface)
 *   - loadLock fail-closed behavior on a corrupt lock file
 *
 * Run: node --test scripts/sync-lockfile.test.mjs
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import {
  LOCK_VERSION,
  buildLockEntry,
  computeFileDigest,
  diffSource,
  loadLock,
  saveLock,
  serializeLock,
} from './sync-lockfile.mjs';

function tmpLockPath() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sync-lockfile-test-'));
  return path.join(dir, 'sources.lock.json');
}

function digests(spec) {
  // spec: { 'path': 'content' } → [{ path, sha256 }]
  return Object.entries(spec).map(([p, content]) => ({
    path: p,
    sha256: computeFileDigest(Buffer.from(content)),
  }));
}

function lockWith(sourceName, currentFiles) {
  return {
    version: LOCK_VERSION,
    sources: {
      [sourceName]: buildLockEntry(
        { repo: 'owner/repo' },
        'abc123',
        currentFiles,
        '2026-07-06T00:00:00.000Z',
      ),
    },
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// computeFileDigest — determinism + exact-byte sensitivity.
// ─────────────────────────────────────────────────────────────────────────────
test('digest: deterministic for identical bytes', () => {
  const a = computeFileDigest(Buffer.from('hello'));
  const b = computeFileDigest(Buffer.from('hello'));
  assert.equal(a, b);
});

test('digest: known sha256 vector with the sha256: prefix', () => {
  // sha256("hello")
  assert.equal(
    computeFileDigest(Buffer.from('hello')),
    'sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
  );
});

test('digest: a single flipped byte produces a different digest', () => {
  const base = Buffer.from('#!/bin/sh\necho ok\n');
  const flipped = Buffer.from(base);
  flipped[flipped.length - 2] ^= 0x01;
  assert.notEqual(computeFileDigest(base), computeFileDigest(flipped));
});

test('digest: rejects non-Buffer input (strings can hide re-encoding corruption)', () => {
  assert.throws(() => computeFileDigest('hello'), TypeError);
});

// ─────────────────────────────────────────────────────────────────────────────
// diffSource — classification corpus.
// ─────────────────────────────────────────────────────────────────────────────
test('diffSource: no lock entry → new-source with every path listed as added', () => {
  const current = digests({ 'SKILL.md': 'skill', 'references/a.md': 'ref' });
  const d = diffSource({ version: 1, sources: {} }, 'fresh', current);
  assert.equal(d.status, 'new-source');
  assert.deepEqual(d.added, ['SKILL.md', 'references/a.md']);
  assert.deepEqual(d.removed, []);
  assert.deepEqual(d.changed, []);
});

test('diffSource: identical content → unchanged with empty diff lists', () => {
  const current = digests({ 'SKILL.md': 'skill', 'scripts/run.sh': '#!/bin/sh\n' });
  const lock = lockWith('steady', current);
  const d = diffSource(lock, 'steady', current);
  assert.equal(d.status, 'unchanged');
  assert.deepEqual(d.added, []);
  assert.deepEqual(d.removed, []);
  assert.deepEqual(d.changed, []);
});

test('diffSource: added + removed + changed are each attributed to the right list', () => {
  const locked = digests({
    'SKILL.md': 'v1',
    'scripts/run.sh': 'run',
    'references/gone.md': 'bye',
  });
  const lock = lockWith('moving', locked);
  const current = digests({
    'SKILL.md': 'v2', // changed
    'scripts/run.sh': 'run', // unchanged
    'hooks/new-hook.sh': 'curl evil', // added
  });
  const d = diffSource(lock, 'moving', current);
  assert.equal(d.status, 'drifted');
  assert.deepEqual(d.added, ['hooks/new-hook.sh']);
  assert.deepEqual(d.removed, ['references/gone.md']);
  assert.deepEqual(d.changed, ['SKILL.md']);
});

test('diffSource: ONE changed byte in ONE file is enough to classify drifted', () => {
  const original = Buffer.from('#!/bin/sh\necho safe\n');
  const tampered = Buffer.from(original);
  tampered[tampered.length - 2] ^= 0x01; // flip one bit of one byte
  const lock = lockWith('one-byte', [
    { path: 'scripts/install.sh', sha256: computeFileDigest(original) },
  ]);
  const d = diffSource(lock, 'one-byte', [
    { path: 'scripts/install.sh', sha256: computeFileDigest(tampered) },
  ]);
  assert.equal(d.status, 'drifted');
  assert.deepEqual(d.changed, ['scripts/install.sh']);
  assert.deepEqual(d.added, []);
  assert.deepEqual(d.removed, []);
});

test('diffSource: upstream emptied (all files removed) is drifted, not unchanged', () => {
  const lock = lockWith('emptied', digests({ 'SKILL.md': 'x', 'README.md': 'y' }));
  const d = diffSource(lock, 'emptied', []);
  assert.equal(d.status, 'drifted');
  assert.deepEqual(d.removed, ['README.md', 'SKILL.md']);
});

test('diffSource: only the named source entry is consulted', () => {
  const current = digests({ 'SKILL.md': 'a' });
  const lock = lockWith('other-source', digests({ 'SKILL.md': 'completely different' }));
  const d = diffSource(lock, 'this-source', current);
  assert.equal(d.status, 'new-source', 'a different source name must not match');
});

test('diffSource: a present-but-corrupt entry (no "files") THROWS — fail closed, never silent re-baseline', () => {
  // A rogue/truncated lock entry that is present but missing `files` must not be
  // laundered into a `new-source` re-baseline (which would skip drift quarantine).
  const lock = { version: LOCK_VERSION, sources: { rogue: { repo: 'o/r', resolved_ref: 'x' } } };
  assert.throws(
    () => diffSource(lock, 'rogue', digests({ 'SKILL.md': 'a' })),
    /corrupt or malformed/,
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// serializeLock / saveLock — deterministic, review-surface-stable output.
// ─────────────────────────────────────────────────────────────────────────────
test('serializeLock: insertion order of sources and files never leaks into output', () => {
  const entryA = buildLockEntry(
    { repo: 'o/a' },
    'sha-a',
    digests({ 'z.md': '1', 'a.md': '2' }),
    '2026-07-06T00:00:00.000Z',
  );
  const entryB = buildLockEntry(
    { repo: 'o/b' },
    'sha-b',
    digests({ 'm.md': '3' }),
    '2026-07-06T00:00:00.000Z',
  );

  const lockOrder1 = { version: 1, sources: { zzz: entryB, aaa: entryA } };
  const lockOrder2 = { version: 1, sources: { aaa: entryA, zzz: entryB } };
  const s1 = serializeLock(lockOrder1);
  const s2 = serializeLock(lockOrder2);
  assert.equal(s1, s2, 'byte-identical regardless of insertion order');

  const parsed = JSON.parse(s1);
  assert.deepEqual(Object.keys(parsed.sources), ['aaa', 'zzz'], 'source names sorted');
  assert.deepEqual(Object.keys(parsed.sources.aaa.files), ['a.md', 'z.md'], 'file paths sorted');
  assert.deepEqual(
    Object.keys(parsed.sources.aaa),
    ['repo', 'resolved_ref', 'locked_at', 'files'],
    'entry key order is fixed',
  );
  assert.ok(s1.endsWith('\n'), 'trailing newline');
});

test('serializeLock: repeated serialization of the same lock is byte-identical', () => {
  const lock = lockWith('stable', digests({ 'SKILL.md': 'x' }));
  assert.equal(serializeLock(lock), serializeLock(lock));
});

test('saveLock/loadLock: round-trip preserves entries; identical re-save is a no-op', () => {
  const lockPath = tmpLockPath();
  const lock = lockWith('round-trip', digests({ 'SKILL.md': 'body', 'refs/a.md': 'ref' }));

  assert.equal(saveLock(lockPath, lock), true, 'first save writes');
  const loaded = loadLock(lockPath);
  assert.equal(loaded.sources['round-trip'].repo, 'owner/repo');
  assert.equal(loaded.sources['round-trip'].resolved_ref, 'abc123');
  assert.deepEqual(
    diffSource(loaded, 'round-trip', digests({ 'SKILL.md': 'body', 'refs/a.md': 'ref' })).status,
    'unchanged',
    'a reloaded lock classifies the same content as unchanged',
  );
  assert.equal(saveLock(lockPath, loaded), false, 'byte-identical re-save skips the write');
});

test('loadLock: missing file → empty lock (bootstrap path, every source is new-source)', () => {
  const lock = loadLock(path.join(os.tmpdir(), 'definitely-missing', 'sources.lock.json'));
  assert.equal(lock.version, LOCK_VERSION);
  assert.deepEqual(lock.sources, {});
  const d = diffSource(lock, 'anything', digests({ 'SKILL.md': 'x' }));
  assert.equal(d.status, 'new-source');
});

test('loadLock: corrupt lock file THROWS (fail closed, never "unpinned")', () => {
  const lockPath = tmpLockPath();
  fs.writeFileSync(lockPath, '{ this is not json');
  assert.throws(() => loadLock(lockPath), /not valid JSON/);
});

test('loadLock: a JSON array is rejected (lock must be an object)', () => {
  const lockPath = tmpLockPath();
  fs.writeFileSync(lockPath, '[]\n');
  assert.throws(() => loadLock(lockPath), /must be a JSON object/);
});

test('loadLock: a present non-object "sources" field is rejected (fail closed, no silent re-baseline)', () => {
  const lockPath = tmpLockPath();
  fs.writeFileSync(lockPath, JSON.stringify({ version: 1, sources: [] }) + '\n');
  assert.throws(() => loadLock(lockPath), /invalid "sources" field/);
});

// ─────────────────────────────────────────────────────────────────────────────
// buildLockEntry — shape contract.
// ─────────────────────────────────────────────────────────────────────────────
test('buildLockEntry: null resolved ref is preserved as null (bootstrap has no clone)', () => {
  const e = buildLockEntry({ repo: 'o/r' }, null, digests({ 'a.md': 'x' }), '2026-07-06T00:00:00Z');
  assert.equal(e.resolved_ref, null);
  assert.equal(e.repo, 'o/r');
  assert.equal(e.locked_at, '2026-07-06T00:00:00Z');
  assert.match(e.files['a.md'], /^sha256:[0-9a-f]{64}$/);
});

// ── matchesPattern — include/exclude glob semantics (sync-external.mjs) ──
// Added 2026-07-08 with the anchored-pattern fix (#985 defect 6): a leading
// `/` anchors a pattern to the source root; anything else is auto-prefixed
// `**/` (recursive by design, for nested contributor layouts). The anchored
// form was dead code before this corpus existed — these tests keep it alive.
import {
  hasRootLicenseInclude,
  isRootLicenseFile,
  matchesPattern,
  unanchoredIncludes,
} from './sync-lockfile.mjs';

test('anchored /README.md matches only the root README', () => {
  assert.equal(matchesPattern('README.md', ['/README.md']), true);
  assert.equal(matchesPattern('examples/portaljs-catalog/README.md', ['/README.md']), false);
  assert.equal(matchesPattern('giftless/cloudflare/README.md', ['/README.md']), false);
});

test('anchored exact deep path matches itself and nothing nested above it', () => {
  assert.equal(matchesPattern('skills/llm-box/SKILL.md', ['/skills/llm-box/SKILL.md']), true);
  assert.equal(
    matchesPattern('contrib/skills/llm-box/SKILL.md', ['/skills/llm-box/SKILL.md']),
    false,
  );
});

test('anchored /skills/** matches the root skills tree only', () => {
  assert.equal(matchesPattern('skills/a/SKILL.md', ['/skills/**']), true);
  assert.equal(matchesPattern('skills/deep/nested/ref.md', ['/skills/**']), true);
  assert.equal(matchesPattern('nested/skills/a/SKILL.md', ['/skills/**']), false);
});

test('unanchored patterns stay recursive (the documented auto-prefix default)', () => {
  assert.equal(matchesPattern('README.md', ['README.md']), true);
  assert.equal(matchesPattern('examples/x/README.md', ['README.md']), true);
  assert.equal(matchesPattern('skills/tools/x/skills/x/SKILL.md', ['skills/**']), true);
});

test('single-star stays single-segment; ? stays single-char', () => {
  assert.equal(matchesPattern('docs/a.md', ['/docs/*.md']), true);
  assert.equal(matchesPattern('docs/sub/a.md', ['/docs/*.md']), false);
  assert.equal(matchesPattern('a.md', ['?.md']), true);
});

// ── unanchoredIncludes — the anchoring lint (blocker 62ye.6) ──
// Flags includes that matchesPattern will silently auto-prefix `**/` so the
// vetter is warned they admit files at ANY depth, not just the root.
test('unanchoredIncludes flags bare (auto-prefixed) includes', () => {
  assert.deepEqual(unanchoredIncludes(['README.md', 'references/**']), [
    'README.md',
    'references/**',
  ]);
});

test('unanchoredIncludes does not flag anchored or explicitly-recursive includes', () => {
  assert.deepEqual(unanchoredIncludes(['/README.md', '**/SKILL.md', '/skills/**']), []);
});

test('unanchoredIncludes on mixed list returns only the offenders', () => {
  assert.deepEqual(unanchoredIncludes(['/README.md', 'SKILL.md', '**/x.md', 'docs/**']), [
    'SKILL.md',
    'docs/**',
  ]);
});

test('unanchoredIncludes tolerates empty / missing input', () => {
  assert.deepEqual(unanchoredIncludes([]), []);
  assert.deepEqual(unanchoredIncludes(undefined), []);
  assert.deepEqual(unanchoredIncludes(null), []);
});

test('license policy requires an explicit root LICENSE or COPYING include', () => {
  assert.equal(hasRootLicenseInclude(['/LICENSE']), true);
  assert.equal(hasRootLicenseInclude(['COPYING']), true);
  assert.equal(hasRootLicenseInclude(['LICENSE.md']), true);
  assert.equal(hasRootLicenseInclude(['docs/LICENSE']), false);
  assert.equal(hasRootLicenseInclude(['**/LICENSE']), false);
  assert.equal(hasRootLicenseInclude(['SKILL.md']), false);
});

test('license policy only accepts a root license file in the mirrored artifact', () => {
  assert.equal(isRootLicenseFile('LICENSE'), true);
  assert.equal(isRootLicenseFile('COPYING.LESSER'), true);
  assert.equal(isRootLicenseFile('nested/LICENSE'), false);
  assert.equal(isRootLicenseFile('license.txt/README.md'), false);
});

// The lint pairs with the real hazard: a bare include IS recursive today.
test('a bare README.md include silently matches a deep README (the hazard being linted)', () => {
  assert.equal(matchesPattern('examples/x/README.md', ['README.md']), true);
  assert.ok(unanchoredIncludes(['README.md']).length === 1);
});

test('matchesPattern: regex metacharacters in a pattern are literal, never regex syntax', () => {
  assert.equal(matchesPattern('docs/a+b.md', ['/docs/a+b.md']), true);
  assert.equal(matchesPattern('docs/aab.md', ['/docs/a+b.md']), false, '+ is not a quantifier');
  assert.equal(matchesPattern('x/(v1).md', ['**/(v1).md']), true);
  assert.equal(matchesPattern('x/v1.md', ['**/(v1).md']), false, '() is not a group');
  assert.equal(matchesPattern('lib/[a].js', ['/lib/[a].js']), true);
  assert.equal(matchesPattern('lib/a.js', ['/lib/[a].js']), false, '[] is not a class');
  assert.equal(matchesPattern('a\\b', ['/a\\b']), true, 'backslash is literal');
  assert.equal(matchesPattern('$HOME/x', ['/$HOME/x']), true, '$ is literal');
});
