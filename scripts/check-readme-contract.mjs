#!/usr/bin/env node
/**
 * check-readme-contract.mjs — the § 6A landing-contract assertions the TOC
 * generator cannot express (blueprint 727, Epic 2 bead 2.13).
 *
 * Division of labor: generate-readme-toc.mjs enforces R1 (no per-plugin rows)
 * and R2 (byte budgets) at emit time and re-verifies them in --check. This
 * checker owns the surface-level contract:
 *
 *   R4  — no bare integer outside a generated block. Hand prose routes
 *         numbers through the SCALE block (cohort + command) or omits them.
 *         Link/image targets, code fences, and inline code are data, not
 *         prose claims, and are stripped before scanning.
 *   R6  — the frozen public install slug appears verbatim, at least once,
 *         and the canonical repo name is never substituted into the install
 *         command (§ 6A.3: a rename here is a breaking API change).
 *   R8  — all four artifact classes are defined on the surface.
 *   R9  — the five navigation doors are present and point at live generated
 *         surfaces (the category table anchor + four marketplace routes).
 *   R5  — no harness other than Claude Code is named as supported while the
 *         adapter registry does not exist (Epic 3 replaces this list with a
 *         generated adapters[] cross-check).
 *   R10 — the retired README spotlight cannot be restored by prose or by the
 *         former KILLER-SKILL generated-block sentinels. Website editorial
 *         spotlights are a separate surface and remain supported.
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');

const GENERATED_BLOCKS = [
  ['<!-- SCALE:START', '<!-- SCALE:END -->'],
  ['<!-- NPM-STATS:START', '<!-- NPM-STATS:END -->'],
  ['<!-- AUTO-TOC:START', '<!-- AUTO-TOC:END -->'],
  ['<!-- CERTIFICATION:START', '<!-- CERTIFICATION:END -->'],
];

export const INSTALL_SLUG = '/plugin marketplace add jeremylongshore/claude-code-plugins';

/** Strip generated blocks, code, and link/image targets → the hand prose. */
export function handProse(readme) {
  let text = readme;
  for (const [start, end] of GENERATED_BLOCKS) {
    const s = text.indexOf(start);
    const e = text.indexOf(end);
    if (s !== -1 && e !== -1 && e > s) text = text.slice(0, s) + text.slice(e + end.length);
  }
  return text
    .replace(/```[\s\S]*?```/g, ' ') // fenced code (the install commands)
    .replace(/<!--[\s\S]*?-->/g, ' ') // comments (the frozen-slug note)
    .replace(/`[^`]*`/g, ' ') // inline code
    .replace(/\]\([^)]*\)/g, ']( )') // link + image targets
    .replace(/https?:\/\/\S+/g, ' '); // bare URLs
}

/** R4 — bare integers in hand prose. Returns offending matches. */
export function bareIntegers(prose) {
  return (prose.match(/\b\d+\b/g) || []).filter(Boolean);
}

export function checkContract(readme) {
  const violations = [];

  // R10 — the oversized README spotlight is retired permanently. Keep this
  // check scoped to README bytes so the website editorial spotlight remains.
  if (
    /killer skill of the week/i.test(readme) ||
    /<!--\s*KILLER-SKILL:(?:START|END)\s*-->/i.test(readme)
  ) {
    violations.push(
      'R10: retired README Killer Skill spotlight or generated-block sentinel reintroduced',
    );
  }

  // R6 — frozen slug, verbatim, and never "corrected" to the canonical name.
  if (!readme.includes(INSTALL_SLUG)) {
    violations.push(`R6: frozen install slug missing or altered ("${INSTALL_SLUG}")`);
  }
  if (readme.includes('/plugin marketplace add jeremylongshore/claude-code-plugins-plus-skills')) {
    violations.push(
      'R6: install command was "normalized" to the canonical repo name — breaking API change',
    );
  }

  // R4 — no bare integers outside generated blocks.
  for (const n of bareIntegers(handProse(readme))) {
    violations.push(
      `R4: bare integer "${n}" in hand prose — route it through the SCALE block or spell it out`,
    );
  }

  // R8 — the four artifact classes.
  for (const cls of [
    'Canonical skill',
    'Generated adapter',
    'First-party package',
    'Upstream mirror',
  ]) {
    if (!readme.includes(cls))
      violations.push(`R8: artifact class "${cls}" not defined on the surface`);
  }

  // R9 — the five doors.
  const doors = [
    ['category table', '#browse-by-category'],
    ['plugin browse', 'https://tonsofskills.com/explore'],
    ['skill search', 'https://tonsofskills.com/skills'],
    ['bundles', 'https://tonsofskills.com/cowork'],
    ['certification section', '#certification'],
  ];
  for (const [label, target] of doors) {
    if (!readme.includes(target))
      violations.push(`R9: navigation door "${label}" (${target}) missing`);
  }

  // R5 — interim: no foreign harness presented as supported without adapters.
  const prose = handProse(readme);
  for (const harness of ['Codex', 'OpenClaw', 'Gemini CLI', 'Cursor IDE']) {
    if (new RegExp(`\\b${harness}\\b`).test(prose)) {
      violations.push(
        `R5: harness "${harness}" named without a declared adapter (Epic 3 owns the registry)`,
      );
    }
  }

  return violations;
}

const isMain = process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href;
if (isMain) {
  const readme = readFileSync(join(REPO_ROOT, 'README.md'), 'utf-8');
  const violations = checkContract(readme);
  for (const v of violations) console.error(`readme-contract: VIOLATION — ${v}`);
  if (violations.length > 0) {
    console.error(
      `readme-contract: FAIL — ${violations.length} violation(s) of the § 6A landing contract.`,
    );
    process.exit(1);
  }
  console.log('readme-contract: OK (R4/R5/R6/R8/R9/R10 hold; R1/R2 enforced by the generator)');
}
