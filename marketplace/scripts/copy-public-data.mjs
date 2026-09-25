#!/usr/bin/env node
/**
 * copy-public-data.mjs — project the large generated data files from their
 * canonical home (`src/data/`) into `public/data/`, where Astro serves them as
 * static assets at runtime (`/data/<file>.json`).
 *
 * Canonical: `marketplace/src/data/*.json` — written by discover-skills.mjs and
 * generate-unified-search.mjs, and read at BUILD time by every generator.
 * Projection: `marketplace/public/data/*.json` — read only at RUNTIME by the
 * browser (skills/index.astro, explore.astro, BaseLayout.astro) and by anyone
 * fetching the public `/data/*.json` URLs.
 *
 * The projection is deliberately NOT tracked in git (see .gitignore): it is
 * regenerated here, and tracking it duplicated ~28.5 MB of the repository
 * payload while giving a second, silently-divergeable claimant to a fact that
 * `src/data/` already owns.
 *
 * Every projected file is a byte-identical copy except one field.
 * `skills-catalog.json` gets `generatedAt`, the time this public copy was
 * built. The tracked source carries no timestamp, because a wall-clock value
 * changed its bytes on every regeneration and made unrelated pull requests
 * conflict. Schema 3.4.0 documents `generatedAt` in the public catalog, so it
 * is stamped here, where the value means "when the file you downloaded was
 * built". `SOURCE_DATE_EPOCH` (seconds), when set, pins the value for
 * reproducible builds.
 *
 * Extracted from build.mjs so `predev` can run it too — without it, a fresh clone
 * running `astro dev` (which serves `public/` as-is, with no build step) 404s on
 * both runtime fetches.
 */
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
export const PROJECTED_FILES = ['unified-search-index.json', 'skills-catalog.json'];
export const TIMESTAMPED_FILES = new Set(['skills-catalog.json']);

/** Resolve the build time, honoring SOURCE_DATE_EPOCH for reproducible builds. */
export function buildTimestamp(env = process.env, now = () => new Date()) {
  const epoch = env.SOURCE_DATE_EPOCH;
  if (epoch === undefined || epoch === '') return now().toISOString();
  if (!/^\d+$/.test(epoch)) {
    throw new Error(`SOURCE_DATE_EPOCH must be a non-negative integer, got "${epoch}"`);
  }
  return new Date(Number(epoch) * 1000).toISOString();
}

/**
 * Return the catalog bytes with `generatedAt` placed after `count`, the position
 * the public schema has always used. An existing value is replaced rather than
 * rejected: keeping timestamps out of the tracked bytes is the job of the
 * `--check` drift gate, and this step also runs from `predev` on checkouts
 * that may predate the change, so failing here would only break the build.
 */
export function stampGeneratedAt(bytes, generatedAt) {
  const value = JSON.parse(bytes);
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('expected a JSON object');
  }
  if (!Number.isFinite(Date.parse(generatedAt))) {
    throw new Error(`invalid generatedAt "${generatedAt}"`);
  }
  const stamped = {};
  for (const [key, entry] of Object.entries(value)) {
    if (key === 'generatedAt') continue;
    stamped[key] = entry;
    if (key === 'count') stamped.generatedAt = generatedAt;
  }
  if (!Object.hasOwn(stamped, 'generatedAt')) stamped.generatedAt = generatedAt;
  return JSON.stringify(stamped, null, 2);
}

export function projectPublicData({
  srcDir = resolve(__dirname, '..', 'src', 'data'),
  publicDataDir = resolve(__dirname, '..', 'public', 'data'),
  generatedAt = buildTimestamp(),
  log = console.log,
} = {}) {
  mkdirSync(publicDataDir, { recursive: true });
  for (const file of PROJECTED_FILES) {
    const from = resolve(srcDir, file);
    const to = resolve(publicDataDir, file);
    if (TIMESTAMPED_FILES.has(file)) {
      writeFileSync(to, stampGeneratedAt(readFileSync(from, 'utf8'), generatedAt));
      log(`[data:copy] ${file} → public/data/${file} (generatedAt ${generatedAt})`);
    } else {
      copyFileSync(from, to);
      log(`[data:copy] ${file} → public/data/${file}`);
    }
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  projectPublicData();
}
