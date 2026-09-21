#!/usr/bin/env node
/**
 * check-internal-doc-links.mjs — fail the build when a first-party doc links to
 * a file that does not exist.
 *
 * WHY THIS EXISTS RATHER THAN JUST GATING check-links.yml
 * ------------------------------------------------------
 * The repo already runs lychee on every markdown PR, and it has been finding
 * these every week — 500 errors on the last completed run. Both lychee
 * invocations are configured `fail: false`, so the job reports success
 * regardless, and 391 of those 500 were dead links to paths inside this repo.
 *
 * Simply flipping lychee to `fail: true` does not work, and the config comment
 * says why: rate limits and TLS resets produced ~200 false failures. That is the
 * nature of network checking — it is NON-DETERMINISTIC, so it cannot be a
 * required check without flaking the merge queue.
 *
 * This script gates the half that IS deterministic: links to paths inside the
 * repo. No network, no rate limits, no flakes — the same input always gives the
 * same answer, which is the only kind of check that belongs in `ci-required`.
 * External link rot stays with the weekly lychee report, where a false positive
 * costs a glance instead of a blocked merge.
 *
 * WHAT IS DELIBERATELY NOT COUNTED
 * --------------------------------
 * Of the 391 file-not-found errors, only a small minority are defects in our
 * own docs. Counting the rest would make the gate a liar:
 *
 *   - External mirror plugins (their dir carries `.source.json`). These links
 *     are correct in the contributor's own repo and broken only in our mirror.
 *     CLAUDE.md's never-clobber rule forbids editing them, and the next sync
 *     would revert us anyway. Upstreaming is the only correct route, so a gate
 *     demanding a local fix would demand a rule violation.
 *   - `skills/.curated/**` — a GENERATED mirror of the best plugin skills. The
 *     plugin skill is the source of truth; editing the mirror is wrong and
 *     `promote-curated-check` already guards the pairing.
 *   - `tests/fixtures/**` — deliberately arbitrary content, already excluded in
 *     `.lychee.toml`.
 *   - Anything inside a fenced code block. `](url)`, `](path)` and
 *     `](references/file.md)` in a usage example are illustrations, not links.
 *     Counting them would train authors to contort their examples.
 *
 * RATCHETING, NOT ZERO
 * --------------------
 * Same contract as scripts/lint-design-tokens.mjs: the count may fall, never
 * rise, and the script REFUSES to raise its own baseline. A zero baseline would
 * be dishonest today (a handful of genuinely-missing docs remain, which is a
 * content gap rather than a path typo) and would tempt whoever hits it into
 * excluding a whole directory to get green.
 *
 * Usage:  node scripts/check-internal-doc-links.mjs [--list]
 */

import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');

/**
 * Maximum tolerated count. Keep this at zero so a broken relative link cannot
 * enter the tracked first-party Markdown corpus.
 */
const BASELINE = 0;

/** Links that are illustrations inside fenced code, not navigation. */
function stripFencedCode(text) {
  const out = [];
  let fence = null;
  for (const line of text.split('\n')) {
    const m = /^\s*(```+|~~~+)/.exec(line);
    if (m) {
      if (fence === null) fence = m[1][0];
      else if (m[1][0] === fence) fence = null;
      out.push(''); // keep line numbering intact
      continue;
    }
    out.push(fence === null ? line : '');
  }
  // Also blank out INLINE code spans. Skill docs teach link syntax by example —
  // `[text](path)`, `[[N]](url)`, `[file](references/file.md)` — and every one of
  // those is an illustration of the syntax, not a link to follow. Counting them
  // would push authors into contorting their own documentation to appease a gate.
  return out.join('\n').replace(/`+[^`\n]*`+/g, (m) => ' '.repeat(m.length));
}

function isExcluded(file) {
  const parts = file.split('/');
  if (parts[0] === 'tests' && parts.includes('fixtures')) return true;
  if (file.startsWith('skills/.curated/')) return true;
  // External mirror: plugins/<category>/<name>/ containing .source.json
  if (parts[0] === 'plugins' && parts.length >= 3) {
    if (existsSync(join(ROOT, parts[0], parts[1], parts[2], '.source.json'))) return true;
  }
  return false;
}

const LINK = /\]\((?!https?:|#|mailto:|tel:|data:)([^)\s#]+)(?:#[^)]*)?\)/g;

function main() {
  // maxBuffer: the tracked markdown list is >1 MB in this repo, which overflows
  // execFileSync's 1 MB default and throws with the whole list in the message.
  const files = execFileSync('git', ['ls-files', '*.md'], {
    cwd: ROOT,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
    .split('\n')
    .filter(Boolean)
    .filter((f) => !isExcluded(f));

  const broken = [];
  for (const file of files) {
    let text;
    try {
      text = readFileSync(join(ROOT, file), 'utf8');
    } catch {
      continue; // unreadable is not a link defect
    }
    const body = stripFencedCode(text);
    for (const m of body.matchAll(LINK)) {
      const target = m[1].trim();
      // Absolute site paths (/blog/...) are routes, not files — not our business.
      if (!target || target.startsWith('/')) continue;
      if (!existsSync(join(ROOT, dirname(file), target))) {
        broken.push({ file, target });
      }
    }
  }

  const list = process.argv.includes('--list');
  if (list || broken.length > BASELINE) {
    for (const b of broken) console.log(`  ${b.file} -> ${b.target}`);
    if (list) console.log('');
  }

  console.log(`internal doc links: ${broken.length} unresolved (baseline ${BASELINE})`);

  if (broken.length > BASELINE) {
    console.error(
      `\nFAIL: ${broken.length} unresolved internal links exceeds the baseline of ${BASELINE}.\n` +
        `Fix the link (or the missing file) rather than raising the baseline — this\n` +
        `script will not raise it, and a rising count is how 391 of these accumulated\n` +
        `behind a green check in the first place.`,
    );
    process.exit(1);
  }
  if (broken.length < BASELINE) {
    console.log(
      `\n${BASELINE - broken.length} fewer than baseline — lower BASELINE to ${broken.length} ` +
        `in ${'scripts/check-internal-doc-links.mjs'} to lock the gain in.`,
    );
  }
}

main();
