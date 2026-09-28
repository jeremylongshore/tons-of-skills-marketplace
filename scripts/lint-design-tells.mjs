#!/usr/bin/env node
/**
 * lint-design-tells.mjs — gate against AI-slop visual tells in marketplace/src.
 *
 * Driven by the VibeCheck 25/100 audit (2026-05-31). Fails CI if the codebase
 * regresses on:
 *   - linear-gradient (background chrome) — DESIGN.md §1 rejects gradient blobs
 *   - backdrop-blur / backdrop-filter   — DESIGN.md §1 rejects glassmorphism
 *   - bg-purple-*, bg-indigo-*, bg-violet-*  — anti-default accent
 *   - pure #000 / rgb(0,0,0) in CSS — DESIGN.md §2 says "near-black, never pure black"
 *   - em-dash density in visible chrome (Hero, key components, homepage hero block)
 *
 * Allowlist:
 *   - mask-image: linear-gradient(...) — progressive fades, not chrome
 *   - data files (src/data/**) — brand colors of third-party products
 *   - HTML/JS/CSS comments — not user-visible
 *
 * Usage:
 *   node scripts/lint-design-tells.mjs            # current marketplace/src
 *   node scripts/lint-design-tells.mjs --strict   # tighter thresholds
 */

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const STRICT = process.argv.includes('--strict');
const ROOT = 'marketplace/src';
const CHROME_PATHS = ['marketplace/src/components', 'marketplace/src/layouts'];
const HIGH_VIS_PAGES = [
  'marketplace/src/pages/index.astro',
  'marketplace/src/pages/explore.astro',
  'marketplace/src/pages/getting-started.astro',
];

const EM_DASH_THRESHOLD = STRICT ? 6 : 12;

function walk(dir, exts = ['.astro', '.css', '.ts', '.tsx', '.js', '.jsx']) {
  const out = [];
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return out;
  }
  for (const name of entries) {
    const p = join(dir, name);
    let s;
    try {
      s = statSync(p);
    } catch {
      continue;
    }
    if (s.isDirectory()) {
      // skip data + content dirs — they hold brand colors and prose
      if (/\/(data|content)(\/|$)/.test(p)) continue;
      out.push(...walk(p, exts));
    } else if (exts.some((e) => p.endsWith(e))) {
      out.push(p);
    }
  }
  return out;
}

function scanRegex(files, re, options = {}) {
  const hits = [];
  for (const file of files) {
    let text;
    try {
      text = readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (re.test(line)) {
        if (options.exclude && options.exclude.test(line)) continue;
        hits.push(`${file}:${i + 1}: ${line.trim().slice(0, 140)}`);
      }
    }
  }
  return hits;
}

const allFiles = walk(ROOT);
const failures = [];
const warnings = [];

// 1. Gradients in chrome (allowlist mask-image)
const gradients = scanRegex(allFiles, /linear-gradient/, {
  exclude: /mask-image|mask:|background-clip/,
});
if (gradients.length > 0) {
  failures.push({
    rule: 'no chrome gradients',
    detail:
      `${gradients.length} linear-gradient in chrome paths:\n  ` +
      gradients.slice(0, 5).join('\n  ') +
      (gradients.length > 5 ? `\n  ... and ${gradients.length - 5} more` : ''),
  });
}

// 2. Glassmorphism (allowlist `backdrop-filter: none` — explicit reset, not glass)
const blur = scanRegex(allFiles, /backdrop-(blur|filter)/, {
  exclude: /backdrop-filter:\s*none/,
});
if (blur.length > (STRICT ? 0 : 0)) {
  failures.push({
    rule: 'no glassmorphism',
    detail: `${blur.length} backdrop-(blur|filter) usages:\n  ` + blur.slice(0, 5).join('\n  '),
  });
}

// 3. Purple/indigo/violet utility classes
const purpleAccent = scanRegex(
  allFiles,
  /(bg|from|via|to|text|border)-(purple|indigo|violet)-[0-9]+/,
);
if (purpleAccent.length > 0) {
  failures.push({
    rule: 'no purple/indigo/violet accents',
    detail:
      `${purpleAccent.length} purple/indigo/violet utilities:\n  ` +
      purpleAccent.slice(0, 5).join('\n  '),
  });
}

// 4. Pure #000 in CSS (warning, not fail — some legit brand uses survive)
const pureBlackRe = /#000(?:000)?(?![0-9a-f])|rgb\s*\(\s*0\s*,\s*0\s*,\s*0/i;
const pureBlack = scanRegex(allFiles, pureBlackRe, {
  exclude: /data-accent|brand-color|<svg|<path|fill=|<circle|"#000"/,
});
if (pureBlack.length > (STRICT ? 0 : 4)) {
  warnings.push({
    rule: 'avoid pure #000 (DESIGN.md §2: "never pure black")',
    detail:
      `${pureBlack.length} pure-black usages in CSS chrome:\n  ` +
      pureBlack.slice(0, 6).join('\n  '),
  });
}

// 5. Em-dash density on visible chrome
function countEmDashesVisible(file) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    return 0;
  }
  // Strip all comments (HTML, JS/CSS block, JS line) before counting
  // 1 + 2. HTML comments and JS/CSS block comments (incl JSDoc /** ... */).
  // Repeat until nothing changes: one pass over `<!-<!-- x -->-` or a
  // similarly nested block can leave a fresh comment opener behind.
  let previous;
  do {
    previous = text;
    text = text.replace(/<!--[\s\S]*?-->/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
  } while (text !== previous);
  // 3. JS line comments (only standalone — not inside strings, but good enough for our heuristic)
  text = text.replace(/^\s*\/\/.*$/gm, '');
  const m = text.match(/—/g);
  return m ? m.length : 0;
}

const chromeFiles = [
  ...CHROME_PATHS.flatMap((p) => walk(p, ['.astro', '.ts', '.tsx'])),
  ...HIGH_VIS_PAGES,
];
let emDashCount = 0;
const perFile = {};
for (const f of chromeFiles) {
  const c = countEmDashesVisible(f);
  if (c > 0) perFile[f] = c;
  emDashCount += c;
}

if (emDashCount > EM_DASH_THRESHOLD) {
  failures.push({
    rule: `em-dash density in visible chrome (threshold ${EM_DASH_THRESHOLD})`,
    detail:
      `${emDashCount} em-dashes (excluding comments). Top offenders:\n  ` +
      Object.entries(perFile)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([f, c]) => `${c}  ${relative(process.cwd(), f)}`)
        .join('\n  '),
  });
}

// ─── Report ───
console.log('═'.repeat(64));
console.log('lint-design-tells.mjs — VibeCheck regression gate');
console.log('═'.repeat(64));
console.log(`Mode: ${STRICT ? 'strict' : 'normal'}`);
console.log(`Em-dash count in visible chrome: ${emDashCount} / threshold ${EM_DASH_THRESHOLD}`);
console.log();

if (warnings.length) {
  console.log('Warnings (non-blocking):');
  for (const w of warnings) {
    console.log(`  ! ${w.rule}`);
    console.log(`    ${w.detail.replace(/\n/g, '\n    ')}`);
  }
  console.log();
}

if (failures.length === 0) {
  console.log('OK All design-tell gates passed.');
  process.exit(0);
}

console.log('Failures (blocking):');
for (const f of failures) {
  console.log(`  X ${f.rule}`);
  console.log(`    ${f.detail.replace(/\n/g, '\n    ')}`);
}
console.log();
console.log(`${failures.length} blocking failure(s).`);
process.exit(1);
