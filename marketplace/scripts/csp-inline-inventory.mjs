#!/usr/bin/env node
/**
 * Exact inventory of executable inline script in the built marketplace (bead claude-i076).
 *
 * The CSP still allows script-src 'unsafe-inline'. Before that can be removed,
 * every executable inline <script> body and inline event-handler attribute in
 * the built HTML must be known and reviewed. This tool records them by SHA-256
 * in a tracked inventory and, in --check mode, fails when the build contains
 * anything the inventory does not name (a planted addition) or the inventory
 * names something the build no longer contains (a stale entry).
 *
 * Not executable, therefore ignored: <script src=...>, and <script type=...>
 * whose type is a data type such as application/ld+json or application/json.
 *
 * Usage (from marketplace/):
 *   node scripts/csp-inline-inventory.mjs --write   # regenerate ops/csp-inline-inventory.json
 *   node scripts/csp-inline-inventory.mjs --check   # CI gate, fails closed
 */

import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const MARKETPLACE = fileURLToPath(new URL('..', import.meta.url));
const DIST = join(MARKETPLACE, 'dist');
const INVENTORY = join(MARKETPLACE, 'ops', 'csp-inline-inventory.json');

// Script types a browser executes; anything else is data and outside script-src.
const EXECUTABLE_TYPES = new Set([
  '',
  'module',
  'text/javascript',
  'application/javascript',
  'text/ecmascript',
  'application/ecmascript',
]);

// Browsers close a script on `</script` followed by anything up to `>` (e.g. `</script\t\n bar>`).
const SCRIPT_RE = /<script\b([^>]*)>([\s\S]*?)<\/script\b[^>]*>/gi;
const HANDLER_RE = /\s(on[a-z]+)\s*=\s*("([^"]*)"|'([^']*)')/gi;

function attr(attrs, name) {
  const m = new RegExp(`\\b${name}\\s*=\\s*("([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i').exec(attrs);
  if (!m) return null;
  return m[2] ?? m[3] ?? m[4] ?? '';
}

const sha256 = (text) => createHash('sha256').update(text).digest('hex');
const sample = (text) => text.trim().replace(/\s+/g, ' ').slice(0, 80);

/** Collect executable inline script bodies and inline handlers from one HTML document. */
export function scanHtml(html) {
  const found = [];
  const scriptSpans = [];
  for (const m of html.matchAll(SCRIPT_RE)) {
    scriptSpans.push([m.index, m.index + m[0].length]);
    const [, attrs, body] = m;
    if (attr(attrs, 'src') !== null) continue;
    const type = (attr(attrs, 'type') ?? '').trim().toLowerCase();
    if (!EXECUTABLE_TYPES.has(type)) continue;
    if (body.trim() === '') continue;
    found.push({ kind: 'inline-script', sha256: sha256(body), sample: sample(body) });
  }
  // Handler attributes only count in markup, not inside script bodies, so skip
  // matches that fall within a script element's span (no rewriting of the HTML).
  const insideScript = (index) => scriptSpans.some(([start, end]) => index >= start && index < end);
  for (const m of html.matchAll(HANDLER_RE)) {
    if (insideScript(m.index)) continue;
    const name = m[1].toLowerCase();
    const value = m[3] ?? m[4] ?? '';
    found.push({ kind: 'event-handler', sha256: sha256(`${name}=${value}`), sample: sample(`${name}="${value}"`) });
  }
  return found;
}

function htmlFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) out.push(...htmlFiles(path));
    else if (entry.name.endsWith('.html')) out.push(path);
  }
  return out;
}

/** Build the inventory for a dist directory: one entry per distinct (kind, sha256). */
export function buildInventory(distDir) {
  if (!existsSync(distDir)) throw new Error(`csp-inline-inventory: ${distDir} does not exist; build the site first`);
  const files = htmlFiles(distDir);
  if (files.length === 0) throw new Error('csp-inline-inventory: no HTML files found; refusing to report an empty inventory');
  const entries = new Map();
  for (const file of files) {
    for (const item of scanHtml(readFileSync(file, 'utf8'))) {
      const key = `${item.kind}:${item.sha256}`;
      if (!entries.has(key)) entries.set(key, { ...item, example: relative(distDir, file) });
    }
  }
  return [...entries.values()].sort((a, b) => a.kind.localeCompare(b.kind) || a.sha256.localeCompare(b.sha256));
}

/** Compare a built inventory with the tracked one; returns { added, removed }. */
export function diffInventory(built, tracked) {
  const key = (e) => `${e.kind}:${e.sha256}`;
  const trackedKeys = new Set(tracked.map(key));
  const builtKeys = new Set(built.map(key));
  return {
    added: built.filter((e) => !trackedKeys.has(key(e))),
    removed: tracked.filter((e) => !builtKeys.has(key(e))),
  };
}

function main() {
  const mode = process.argv[2];
  if (mode !== '--write' && mode !== '--check') {
    console.error('usage: csp-inline-inventory.mjs --write | --check');
    process.exit(2);
  }
  const built = buildInventory(DIST);
  if (mode === '--write') {
    const doc = {
      $comment:
        "Generated by marketplace/scripts/csp-inline-inventory.mjs --write. Every executable inline script and inline event handler in the built site, by SHA-256. CI fails on any addition or stale entry. Removing script-src 'unsafe-inline' requires this list to reach zero (bead claude-i076).",
      entries: built.map(({ kind, sha256: hash, sample: text }) => ({ kind, sha256: hash, sample: text })),
    };
    writeFileSync(INVENTORY, JSON.stringify(doc, null, 2) + '\n');
    console.log(`csp-inline-inventory: wrote ${built.length} entries to ${relative(MARKETPLACE, INVENTORY)}`);
    return;
  }
  const tracked = JSON.parse(readFileSync(INVENTORY, 'utf8')).entries;
  const { added, removed } = diffInventory(built, tracked);
  for (const e of added) console.error(`ADDED   ${e.kind} ${e.sha256.slice(0, 12)} (${e.example}): ${e.sample}`);
  for (const e of removed) console.error(`STALE   ${e.kind} ${e.sha256.slice(0, 12)}: ${e.sample}`);
  if (added.length || removed.length) {
    console.error(
      `csp-inline-inventory: FAIL — ${added.length} unreviewed, ${removed.length} stale. New inline script must be reviewed; ` +
        'prefer a bundled module. If it is genuinely required, regenerate with --write and justify it in the PR.',
    );
    process.exit(1);
  }
  const scripts = built.filter((e) => e.kind === 'inline-script').length;
  console.log(`csp-inline-inventory: OK (${scripts} inline scripts, ${built.length - scripts} inline handlers, all reviewed)`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) main();
