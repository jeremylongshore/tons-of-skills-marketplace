#!/usr/bin/env node
/**
 * fetch-npm-stats.mjs
 *
 * Enumerates every `package.json` in the monorepo, checks which are actually
 * published on npm, fetches day/week/month downloads for each, and emits:
 *   1. marketplace/src/data/npm-stats.json  (consumed by website marquee)
 *   2. README.md bounded block between NPM-STATS:START/END sentinels
 *
 * Covers both `@intentsolutionsio/*` scoped packages and legacy-named ones
 * (claude-cowork, claude-plugin-validator, pr-to-spec, etc.) — anything that
 * resolves to HTTP 200 on the npm registry is counted.
 *
 * Intended to run daily via a GitHub Actions cron; the workflow opens a PR
 * with any diff (since `main` is branch-protected).
 *
 * Usage:
 *   node scripts/fetch-npm-stats.mjs
 *   node scripts/fetch-npm-stats.mjs --dry-run   # print, don't write
 *
 * Exit codes:
 *   0 — success (any count of packages probed cleanly)
 *   1 — one or more registry probes hit persistent rate-limits or server errors,
 *       making the published/unpublished counts unreliable. Surfaces as a red
 *       cron run instead of silently undercounting.
 */

import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import prettier from 'prettier';

const THIS_FILE = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(THIS_FILE), '..');
const OUT_JSON = join(ROOT, 'marketplace', 'src', 'data', 'npm-stats.json');
const README = join(ROOT, 'README.md');

const START_SENTINEL = '<!-- NPM-STATS:START — do not edit; daily cron updates this -->';
const END_SENTINEL = '<!-- NPM-STATS:END -->';

// Skip build/dependency dirs when walking.
const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.astro']);

// Packages "established" longer than this are considered baseline traffic.
// Newer publishes get a separate aggregate so a bulk-publish event doesn't
// dominate the headline number.
const ESTABLISHED_THRESHOLD_MS = 30 * 24 * 60 * 60 * 1000;

function walkPackageJsons(dir) {
  const out = [];
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const ent of entries) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) {
      if (SKIP_DIRS.has(ent.name)) continue;
      out.push(...walkPackageJsons(p));
    } else if (ent.isFile() && ent.name === 'package.json') {
      out.push(p);
    }
  }
  return out;
}

function readPkg(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf-8'));
  } catch {
    return null;
  }
}

// Tagged-result fetcher: caller can tell apart 404 from rate-limit/server-error,
// instead of the previous "any failure → null" collapse that silently hid
// rate-limited packages from the published count.
async function fetchRegistryMetadata(name) {
  const enc = encodeURIComponent(name);
  const url = `https://registry.npmjs.org/${enc}`;
  let lastError = null;
  // 6 retries with exponential backoff up to ~64 s, so we ride through
  // brief 429 waves instead of giving up at 15 s.
  for (let i = 0; i < 6; i++) {
    let res;
    try {
      res = await fetch(url);
    } catch (err) {
      lastError = err;
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
      continue;
    }
    if (res.status === 404) return { kind: 'not-found' };
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 2000 * Math.pow(2, i)));
      continue;
    }
    if (res.status >= 500) {
      lastError = new Error(`HTTP ${res.status}`);
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
      continue;
    }
    if (!res.ok) {
      return { kind: 'forbidden', status: res.status };
    }
    try {
      const meta = await res.json();
      return { kind: 'found', meta };
    } catch (err) {
      lastError = err;
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
    }
  }
  // Retries exhausted. Distinguish rate-limit from generic server error by
  // whether we ever saw a non-429 status. If lastError is set we saw a 5xx
  // or network/JSON error; otherwise every attempt was 429.
  if (lastError) return { kind: 'server-error', error: lastError.message };
  return { kind: 'rate-limited' };
}

export function downloadWindow(endDay) {
  if (typeof endDay !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(endDay))
    throw new Error('Invalid npm download-window end day');
  const end = new Date(`${endDay}T00:00:00Z`);
  if (!Number.isFinite(end.getTime()) || end.toISOString().slice(0, 10) !== endDay)
    throw new Error('Invalid npm download-window end day');
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - 29);
  return { start: start.toISOString().slice(0, 10), end: end.toISOString().slice(0, 10) };
}

export function downloadWindowTotals(body, name) {
  const window = downloadWindow(body?.end);
  if (
    !body ||
    body.package !== name ||
    body.start !== window.start ||
    body.end !== window.end ||
    !Array.isArray(body.downloads) ||
    body.downloads.length !== 30
  ) {
    throw new Error('Incomplete or mismatched npm download range');
  }
  const rows = new Map();
  for (const row of body.downloads) {
    if (
      !row ||
      typeof row.day !== 'string' ||
      rows.has(row.day) ||
      !Number.isSafeInteger(row.downloads) ||
      row.downloads < 0
    ) {
      throw new Error('Invalid npm daily download count');
    }
    rows.set(row.day, row.downloads);
  }
  const counts = [];
  const day = new Date(`${window.start}T00:00:00Z`);
  for (let index = 0; index < 30; index++) {
    const key = day.toISOString().slice(0, 10);
    if (!rows.has(key)) throw new Error('Missing npm download day');
    counts.push(rows.get(key));
    day.setUTCDate(day.getUTCDate() + 1);
  }
  const sum = (values) =>
    values.reduce((total, count) => {
      if (!Number.isSafeInteger(total + count)) throw new Error('Unsafe npm download total');
      return total + count;
    }, 0);
  return { lastDay: counts.at(-1), lastWeek: sum(counts.slice(-7)), lastMonth: sum(counts) };
}

async function fetchDownloadsRange(name) {
  const enc = encodeURIComponent(name);
  const url = `https://api.npmjs.org/downloads/range/last-month/${enc}`;
  let lastError = null;
  // 6 retries with exponential backoff up to ~64 s.
  for (let i = 0; i < 6; i++) {
    let res;
    try {
      res = await fetch(url);
    } catch (err) {
      lastError = err;
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
      continue;
    }
    if (res.status === 404) return { kind: 'not-found' };
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 2000 * Math.pow(2, i)));
      continue;
    }
    if (res.status >= 500) {
      lastError = new Error(`HTTP ${res.status}`);
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
      continue;
    }
    if (!res.ok) return { kind: 'error', status: res.status };
    try {
      return { kind: 'ok', body: await res.json() };
    } catch (err) {
      lastError = err;
      await new Promise((r) => setTimeout(r, 500 * (i + 1)));
    }
  }
  if (lastError) return { kind: 'server-error', error: lastError.message };
  return { kind: 'rate-limited' };
}

// Unscoped names can collide with popular 3rd-party packages (axiom,
// marketplace, etc.). We only count a name as "ours" when our configured
// OWNERS set appears in the package's maintainer list. Scoped names under
// @intentsolutionsio/ are always ours.
const OWNERS = new Set(['jeremylongshore', 'intentsolutionsio']);
const OURS_SCOPES = ['@intentsolutionsio/'];

function isOurs(name, meta) {
  if (OURS_SCOPES.some((s) => name.startsWith(s))) return true;
  if (!meta) return false;
  const maintainers = meta.maintainers || [];
  for (const m of maintainers) {
    const uname = typeof m === 'string' ? m.split('<')[0].trim() : m?.name;
    if (uname && OWNERS.has(uname.toLowerCase())) return true;
  }
  return false;
}

function packageCreatedAt(meta) {
  // npm's `time.created` is the first publish timestamp. Falls back to the
  // earliest version timestamp if `created` is missing on older packages.
  const time = meta?.time || {};
  if (time.created) return new Date(time.created).getTime();
  const versionDates = Object.entries(time)
    .filter(([k]) => k !== 'modified' && k !== 'created')
    .map(([, v]) => new Date(v).getTime())
    .filter((t) => !Number.isNaN(t));
  return versionDates.length ? Math.min(...versionDates) : null;
}

// Per-package outcome: {status, ...payload}. status is one of:
//   'published'    — counted with downloads
//   'unpublished'  — registry returned 404
//   'foreign'      — registry has it but it's not ours (3rd-party collision)
//   'rate-limited' — propagates upward as a hard failure
//   'error'        — generic transient/network/server error
export async function statsFor(name) {
  const metaResult = await fetchRegistryMetadata(name);
  if (metaResult.kind === 'not-found') return { name, status: 'unpublished' };
  if (metaResult.kind === 'rate-limited') return { name, status: 'rate-limited' };
  if (metaResult.kind === 'server-error') {
    return { name, status: 'error', detail: metaResult.error };
  }
  if (metaResult.kind === 'forbidden') {
    return { name, status: 'error', detail: `HTTP ${metaResult.status}` };
  }

  const { meta } = metaResult;
  if (!isOurs(name, meta)) return { name, status: 'foreign' };

  // npm's relative range reports the same data cutoff as its point aliases.
  // The available cutoff can lag UTC yesterday; explicit calendar dates can
  // append unavailable, zero-filled days and silently change all three totals.
  const result = await fetchDownloadsRange(name);
  if (result.kind === 'rate-limited') return { name, status: 'rate-limited' };
  if (!['ok', 'not-found'].includes(result.kind))
    return { name, status: 'error', detail: result.error || `downloads ${result.kind}` };
  let totals;
  try {
    totals =
      result.kind === 'not-found'
        ? { lastDay: 0, lastWeek: 0, lastMonth: 0 }
        : downloadWindowTotals(result.body, name);
  } catch (error) {
    return { name, status: 'error', detail: error.message };
  }
  const { lastDay, lastWeek, lastMonth } = totals;
  const createdAt = packageCreatedAt(meta);
  const latestVersion = meta?.['dist-tags']?.latest ?? null;

  return {
    name,
    status: 'published',
    lastDay,
    lastWeek,
    lastMonth,
    createdAt,
    latestVersion,
  };
}

async function collectStats(pkgNames, { concurrency = 1, throttleMs = 250 } = {}) {
  const counts = {
    candidates: pkgNames.length,
    probed: 0,
    published: 0,
    unpublished: 0,
    foreign: 0,
    rateLimited: 0,
    errors: 0,
  };
  const published = [];
  const rateLimitedNames = [];
  const errorDetails = [];
  let i = 0;

  async function worker() {
    while (i < pkgNames.length) {
      const idx = i++;
      const name = pkgNames[idx];
      let result;
      try {
        result = await statsFor(name);
      } catch (err) {
        counts.probed += 1;
        counts.errors += 1;
        errorDetails.push({ name, detail: err.message });
        if (throttleMs) await new Promise((r) => setTimeout(r, throttleMs));
        continue;
      }
      counts.probed += 1;
      switch (result.status) {
        case 'published':
          counts.published += 1;
          published.push(result);
          break;
        case 'unpublished':
          counts.unpublished += 1;
          break;
        case 'foreign':
          counts.foreign += 1;
          break;
        case 'rate-limited':
          counts.rateLimited += 1;
          rateLimitedNames.push(name);
          break;
        case 'error':
          counts.errors += 1;
          errorDetails.push({ name, detail: result.detail });
          break;
      }
      // Inter-request throttle so we stay under npm's per-IP cap. With
      // concurrency=1 + 250ms = 4 req/sec, well below the observed
      // rate-limit threshold (~280 req/min in CI).
      if (throttleMs) await new Promise((r) => setTimeout(r, throttleMs));
    }
  }

  const workers = Array.from({ length: concurrency }, () => worker());
  await Promise.all(workers);
  return { counts, published, rateLimitedNames, errorDetails };
}

function fmt(n) {
  return Number(n || 0).toLocaleString('en-US');
}

export function buildReadmeBlock(agg) {
  const lines = [
    START_SENTINEL,
    '',
    '### 📦 Live npm Downloads',
    '',
    // Single entry on purpose: these were two array items joined by "\n", which
    // left a dangling space at end-of-line and tripped markdownlint MD009 in the
    // generated README — turning main red on every nightly refresh.
    `Across **${agg.publishedCount} published packages** in the [claude-code-plugins](https://www.npmjs.com/~jeremylongshore) namespace. Updated daily by GitHub Actions.`,
    '',
    '| Window | All packages | Established (>30d) |',
    '|--------|-------------:|-------------------:|',
    `| Last 24 hours | ${fmt(agg.totalDay)} | ${fmt(agg.establishedDay)} |`,
    `| Last 7 days | ${fmt(agg.totalWeek)} | ${fmt(agg.establishedWeek)} |`,
    `| Last 30 days | ${fmt(agg.totalMonth)} | ${fmt(agg.establishedMonth)} |`,
    '',
    `<sub>"Established" excludes packages first published within the last 30 days, so a bulk-publish event doesn't dominate the headline.</sub>`,
    '',
    '**Top 10 by last 30 days:**',
    '',
    '| # | Package | Last 30d |',
    '|---|---------|---------:|',
    ...agg.top.slice(0, 10).map((p, i) => {
      const url = `https://www.npmjs.com/package/${p.name}`;
      return `| ${i + 1} | [\`${p.name}\`](${url}) | ${fmt(p.lastMonth)} |`;
    }),
    '',
    `<sub>Last refreshed ${agg.generatedAt}.</sub>`,
    '',
    END_SENTINEL,
  ];
  return lines.join('\n');
}

export function spliceReadmeStats(readme, block) {
  const s = readme.indexOf(START_SENTINEL);
  const e = readme.indexOf(END_SENTINEL);
  if (s === -1 || e === -1) {
    throw new Error(
      `README.md missing NPM-STATS sentinels. Add:\n${START_SENTINEL}\n${END_SENTINEL}\nwhere the stats block belongs.`,
    );
  }
  return readme.slice(0, s) + block + readme.slice(e + END_SENTINEL.length);
}

export async function prepareStatsArtifacts(
  agg,
  {
    readme = readFileSync(README, 'utf-8'),
    formatter = prettier,
    prettierOptions = {},
    filepath = README,
  } = {},
) {
  const jsonOutput = JSON.stringify(agg, null, 2) + '\n';
  const spliced = spliceReadmeStats(readme, buildReadmeBlock(agg));
  const readmeOutput = await formatter.format(spliced, {
    ...prettierOptions,
    filepath,
  });
  return { jsonOutput, readmeOutput };
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');

  // 1. Enumerate every package.json in the monorepo
  console.log('Enumerating package.json files...');
  const pkgFiles = walkPackageJsons(ROOT);
  const candidates = new Set();
  for (const f of pkgFiles) {
    const p = readPkg(f);
    if (!p) continue;
    if (p.private) continue;
    if (!p.name) continue;
    candidates.add(p.name);
  }
  const names = Array.from(candidates).sort();
  console.log(`  candidates: ${names.length}`);

  // 2. Probe each name. Tagged-result fetchers distinguish 404 from
  //    rate-limit / server-error so we can surface drops loudly instead of
  //    silently undercounting.
  console.log('Fetching npm registry metadata + download stats...');
  // collectStats takes an OPTIONS OBJECT; the previous positional `4` here
  // was silently ignored, so the run has always been serial (concurrency 1,
  // 250ms throttle ≈ 4 req/s — the documented npm-cap-safe rate). Kept
  // serial deliberately; the argument is dropped so the code says what runs.
  const { counts, published, rateLimitedNames, errorDetails } = await collectStats(names);

  // 3. Aggregate
  const now = Date.now();
  const established = published.filter(
    (p) => p.createdAt && now - p.createdAt > ESTABLISHED_THRESHOLD_MS,
  );
  const totalDay = published.reduce((s, p) => s + p.lastDay, 0);
  const totalWeek = published.reduce((s, p) => s + p.lastWeek, 0);
  const totalMonth = published.reduce((s, p) => s + p.lastMonth, 0);
  const establishedDay = established.reduce((s, p) => s + p.lastDay, 0);
  const establishedWeek = established.reduce((s, p) => s + p.lastWeek, 0);
  const establishedMonth = established.reduce((s, p) => s + p.lastMonth, 0);
  const top = [...published].sort((a, b) => b.lastMonth - a.lastMonth);

  const agg = {
    generatedAt: new Date().toISOString(),
    // Freshness bound consumed by scripts/check-stats-freshness.mjs (see
    // fetch-github-stats.mjs for the rationale behind 72h).
    max_age_hours: 72,
    publishedCount: published.length,
    establishedCount: established.length,
    candidateCount: names.length,
    totalDay,
    totalWeek,
    totalMonth,
    establishedDay,
    establishedWeek,
    establishedMonth,
    top,
    telemetry: counts,
  };

  // 4. Telemetry — single-line summary plus drop-list if anything got skipped.
  console.log('');
  console.log(
    `Telemetry: candidates=${counts.candidates} probed=${counts.probed} ` +
      `published=${counts.published} unpublished=${counts.unpublished} ` +
      `foreign=${counts.foreign} rate-limited=${counts.rateLimited} errors=${counts.errors}`,
  );
  if (rateLimitedNames.length) {
    console.warn(`\n⚠ Rate-limited (${rateLimitedNames.length}):`);
    for (const n of rateLimitedNames) console.warn(`    ${n}`);
  }
  if (errorDetails.length) {
    console.warn(`\n⚠ Errors (${errorDetails.length}):`);
    for (const e of errorDetails) console.warn(`    ${e.name}: ${e.detail}`);
  }

  console.log('\nTotals (all published):');
  console.log(`  day=${fmt(totalDay)}  week=${fmt(totalWeek)}  month=${fmt(totalMonth)}`);
  console.log(`Totals (established >30d, ${established.length} pkgs):`);
  console.log(
    `  day=${fmt(establishedDay)}  week=${fmt(establishedWeek)}  month=${fmt(establishedMonth)}`,
  );
  console.log('\nTop 10:');
  for (const [i, p] of top.slice(0, 10).entries()) {
    console.log(`  ${i + 1}. ${p.name.padEnd(50)}  ${fmt(p.lastMonth)}`);
  }

  if (dryRun) {
    console.log('\n(--dry-run: no files written)');
  } else {
    // 5. Prepare BOTH generated artifacts before writing either one. Prettier
    // is a required dependency, not an optional enhancement: publishing fresh
    // JSON while silently retaining a stale README makes the public surfaces
    // contradict one another. Any import/config/format failure reaches the
    // top-level catch and turns the automation run red.
    const options = (await prettier.resolveConfig(README)) || {};
    const currentReadme = readFileSync(README, 'utf-8');
    const { jsonOutput, readmeOutput: updatedReadme } = await prepareStatsArtifacts(agg, {
      readme: currentReadme,
      prettierOptions: options,
    });

    writeFileSync(OUT_JSON, jsonOutput);
    console.log(`\nWrote ${OUT_JSON}`);

    if (updatedReadme !== currentReadme) {
      writeFileSync(README, updatedReadme);
      console.log('Updated README NPM-STATS block');
    } else {
      console.log('README NPM-STATS block already current');
    }
  }

  // 6. Exit non-zero if rate-limits or server-errors happened — the published
  //    count is unreliable and the cron should turn red so we notice instead
  //    of silently shipping stale data.
  if (counts.rateLimited > 0 || counts.errors > 0) {
    console.error(
      `\n✗ ${counts.rateLimited} rate-limited, ${counts.errors} errored — counts unreliable.`,
    );
    process.exit(1);
  }
}

if (process.argv[1] && resolve(process.argv[1]) === THIS_FILE) {
  main().catch((err) => {
    console.error('fetch-npm-stats failed:', err);
    process.exit(1);
  });
}
