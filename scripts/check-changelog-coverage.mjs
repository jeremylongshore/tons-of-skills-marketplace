#!/usr/bin/env node
/**
 * Fail closed unless every released version at or above the pinned floor has
 * exactly one release-note entry.
 */

import { execFileSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { safeReadFile, UnsafePathError } from './safe-fs.mjs';

export const FLOOR = '4.14.0';
const VERSION = /^\d+\.\d+\.\d+$/;
const TAG = /^v(\d+\.\d+\.\d+)$/;
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

function compareVersions(a, b) {
  const left = a.split('.').map(Number);
  const right = b.split('.').map(Number);
  for (let index = 0; index < 3; index += 1) {
    if (left[index] !== right[index]) return left[index] - right[index];
  }
  return 0;
}

function parseFrontmatterVersion(text, relativePath) {
  const normalized = text.replaceAll('\r\n', '\n');
  if (!normalized.startsWith('---\n')) return null;
  const closing = normalized.indexOf('\n---\n', 4);
  if (closing < 0) throw new Error(`${relativePath}: unterminated frontmatter`);

  const versionLines = normalized
    .slice(4, closing)
    .split('\n')
    .filter((line) => /^version\s*:/.test(line));
  if (versionLines.length > 1) {
    throw new Error(`${relativePath}: duplicate version fields`);
  }
  if (versionLines.length === 0) return null;

  const match = versionLines[0].match(/^version\s*:\s*(?:"([^"]+)"|'([^']+)'|([^\s#]+))\s*$/);
  const version = match?.[1] ?? match?.[2] ?? match?.[3];
  if (!version || !VERSION.test(version)) {
    throw new Error(`${relativePath}: malformed release-note version`);
  }
  return version;
}

function defaultTagReader(root) {
  return execFileSync('git', ['tag', '--list', 'v[0-9]*.[0-9]*.[0-9]*'], {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });
}

export function checkChangelogCoverage({ root = ROOT, readTags = defaultTagReader } = {}) {
  let rawTags;
  try {
    rawTags = readTags(root);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new Error(`Git tag enumeration failed: ${detail}`);
  }

  const tags = String(rawTags)
    .split('\n')
    .map((tag) => tag.trim())
    .filter(Boolean);
  const versions = [...new Set(tags.map((tag) => tag.match(TAG)?.[1]).filter(Boolean))].sort(
    compareVersions,
  );
  if (versions.length === 0) {
    throw new Error('no strict vX.Y.Z tags are visible; fetch complete tag evidence');
  }
  if (!versions.includes(FLOOR)) {
    throw new Error(`pinned floor tag v${FLOOR} is not visible; tag evidence is incomplete`);
  }

  const notesDirectory = join(root, 'marketplace', 'src', 'content', 'blog');
  let entries;
  try {
    entries = readdirSync(notesDirectory, { recursive: true });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new Error(`release-note enumeration failed: ${detail}`);
  }

  const documentedByVersion = new Map();
  for (const entry of entries) {
    const relativePath = String(entry);
    if (!relativePath.endsWith('.md')) continue;
    // One verified read (no follow, regular file, same inode before and after
    // open) instead of an lstat check followed by a separate read by name.
    let contents;
    try {
      contents = safeReadFile(notesDirectory, relativePath).content.toString('utf8');
    } catch (error) {
      if (error instanceof UnsafePathError) {
        throw new Error(`${relativePath}: release-note path is not a regular file`);
      }
      const detail = error instanceof Error ? error.message : String(error);
      throw new Error(`${relativePath}: release-note metadata unavailable: ${detail}`);
    }
    const version = parseFrontmatterVersion(contents, relativePath);
    if (!version) continue;
    const previous = documentedByVersion.get(version);
    if (previous) {
      throw new Error(`v${version} has duplicate release notes: ${previous}, ${relativePath}`);
    }
    documentedByVersion.set(version, relativePath);
  }

  if (!documentedByVersion.has(FLOOR)) {
    throw new Error(`pinned floor v${FLOOR} has no release notes`);
  }

  const inScope = versions.filter((version) => compareVersions(version, FLOOR) >= 0);
  const missing = inScope.filter((version) => !documentedByVersion.has(version));
  if (missing.length > 0) {
    throw new Error(
      `${missing.length} released version(s) have no release notes: ${missing
        .map((version) => `v${version}`)
        .join(', ')}`,
    );
  }

  return {
    documented: inScope.length,
    floor: FLOOR,
    grandfathered: versions.length - inScope.length,
    inScope: inScope.length,
    missing: [],
    tags: versions.length,
  };
}

export function main() {
  try {
    const result = checkChangelogCoverage();
    console.log(
      `changelog-coverage: floor v${result.floor} — ${result.inScope} in scope, ` +
        `${result.documented} documented, 0 missing (${result.grandfathered} older tags grandfathered)`,
    );
    console.log('changelog-coverage: every released tag has exactly one release-note entry');
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    console.error(`changelog-coverage: REFUSED — ${detail}`);
    process.exitCode = 1;
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
