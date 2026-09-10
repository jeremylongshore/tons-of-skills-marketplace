#!/usr/bin/env node
/**
 * promote-spotlight.mjs
 *
 * One-command rotation of the Killer-Skill-of-the-Week spotlight.
 *
 * Workflow:
 *   1. Engineer writes the new spotlight content into a JSON file (or pipes
 *      it via stdin) following the same shape as `spotlights.json` >
 *      `spotlight`.
 *   2. Runs `node scripts/promote-spotlight.mjs path/to/new.json`.
 *   3. The script:
 *        a. Loads the current `spotlights.json`.
 *        b. Moves the existing `spotlight` into `hallOfFame` at the top,
 *           tagged with the previous `week` value.
 *        c. Sets the new spotlight = the JSON file's content.
 *        d. Sets `week` to today's ISO week (YYYY-Wnn).
 *        e. Sets `meta.lastUpdated` to today's date.
 *        f. Bumps `meta.version` minor.
 *
 * Usage:
 *   node scripts/promote-spotlight.mjs new-spotlight.json
 *   node scripts/promote-spotlight.mjs --stdin < new-spotlight.json
 *   node scripts/promote-spotlight.mjs --dry-run new-spotlight.json
 *
 * Required fields in the new-spotlight JSON:
 *   pluginSlug, headline, author, authorGithub, grade, category, link
 *
 * Optional fields:
 *   whyKiller, quote, skillCount, assets:{prd,adr,onePager,cfo}
 *
 * Exit codes:
 *   0 — success
 *   1 — bad input or write failure
 *   2 — missing required field in new-spotlight JSON
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SPOTLIGHTS = join(ROOT, 'marketplace', 'src', 'data', 'spotlights.json');

const REQUIRED = ['pluginSlug', 'headline', 'author', 'authorGithub', 'grade', 'category', 'link'];

function todayISO() {
  // YYYY-MM-DD in UTC. ISO-week computed separately.
  return new Date().toISOString().slice(0, 10);
}

function todayISOWeek() {
  // ISO 8601 week number. Implementation: shift to Thursday of the week,
  // then January 4th-rule. Matches `date +%G-W%V`.
  const d = new Date();
  d.setUTCHours(0, 0, 0, 0);
  // Thursday in current week decides the year.
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
  return `${d.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
}

function bumpMinor(version) {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec((version || '0.0.0').trim());
  if (!m) return '0.1.0';
  return `${m[1]}.${parseInt(m[2], 10) + 1}.0`;
}

function readNewSpotlight(args) {
  if (args.includes('--stdin')) {
    return JSON.parse(readFileSync(0, 'utf-8'));
  }
  const positional = args.filter((a) => !a.startsWith('--'));
  if (positional.length !== 1) {
    throw new Error(
      'Pass a path to the new-spotlight JSON file, or use --stdin to pipe it in.\n' +
        'Example: node scripts/promote-spotlight.mjs new-spotlight.json',
    );
  }
  const path = resolve(positional[0]);
  if (!existsSync(path)) throw new Error(`No such file: ${path}`);
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function validateSpotlight(s) {
  const missing = REQUIRED.filter((k) => !s[k]);
  if (missing.length) {
    console.error(`✗ new-spotlight JSON missing required fields: ${missing.join(', ')}`);
    console.error(`  Required: ${REQUIRED.join(', ')}`);
    process.exit(2);
  }
  if (s.assets !== undefined) {
    if (!s.assets || typeof s.assets !== 'object' || Array.isArray(s.assets)) {
      console.error(
        '✗ new-spotlight assets must be an object with optional prd, adr, onePager, and cfo links',
      );
      process.exit(2);
    }
    const invalid = Object.entries(s.assets).filter(
      ([key, value]) =>
        !['prd', 'adr', 'onePager', 'cfo'].includes(key) ||
        typeof value !== 'string' ||
        !value.trim(),
    );
    if (invalid.length) {
      console.error(
        '✗ new-spotlight assets accepts only non-empty prd, adr, onePager, and cfo string links',
      );
      process.exit(2);
    }
  }
}

function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');

  const newSpotlight = readNewSpotlight(args);
  validateSpotlight(newSpotlight);

  const current = JSON.parse(readFileSync(SPOTLIGHTS, 'utf-8'));
  const previous = current.spotlight;
  const previousWeek = current.week || 'unknown';

  // Build the new shape
  const next = {
    week: todayISOWeek(),
    title: current.title || 'Killer Skill of the Week',
    spotlight: newSpotlight,
    hallOfFame: [
      // Previous spotlight gets pushed into the front of hallOfFame, tagged
      // with whatever week it was running under.
      { week: previousWeek, ...previous },
      ...(current.hallOfFame || []),
    ],
    meta: {
      version: bumpMinor(current.meta?.version),
      lastUpdated: todayISO(),
      curatedBy: current.meta?.curatedBy || 'Jeremy Longshore',
    },
  };

  console.log(`Rotating spotlight:`);
  console.log(`  ${previous?.pluginSlug || '(none)'} (${previousWeek}) → hallOfFame`);
  console.log(`  ${newSpotlight.pluginSlug} → spotlight (${next.week})`);
  console.log(`  meta.version: ${current.meta?.version || '0.0.0'} → ${next.meta.version}`);

  if (dryRun) {
    console.log('\n(--dry-run; no files written)');
    return;
  }

  writeFileSync(SPOTLIGHTS, JSON.stringify(next, null, 2) + '\n');
  console.log(`\n✓ Wrote ${SPOTLIGHTS}`);

  console.log('\nNext steps:');
  console.log(`  git add marketplace/src/data/spotlights.json`);
  console.log(`  git commit -m "feat(spotlight): ${newSpotlight.pluginSlug} (${next.week})"`);
  console.log(`  git push && gh pr create --fill`);
}

try {
  main();
} catch (err) {
  console.error(err.message || err);
  process.exit(1);
}
