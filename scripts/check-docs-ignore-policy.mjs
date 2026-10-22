#!/usr/bin/env node
/**
 * check-docs-ignore-policy.mjs — pins the 000-docs ignore-policy invariant.
 *
 * The root 000-docs ignore rules live in 000-docs/.gitignore (ownership +
 * public-filing-ledger model; Mission 01 docs 720/726, bead claude-5awj.6).
 * This gate asserts the policy's observable behavior with `git check-ignore
 * --no-index`, which evaluates PATTERNS for hypothetical paths — no fixture
 * files are created. If any assertion fails, the ignore design regressed
 * (most likely someone sorted a .gitignore or moved rules back to the root).
 *
 * Exit 0 = policy intact. Exit 1 = regression (each mismatch printed).
 */
import { execFileSync } from 'node:child_process';

function isIgnored(path) {
  try {
    execFileSync('git', ['check-ignore', '-q', '--no-index', path]);
    return true; // exit 0 → matched an ignore pattern
  } catch {
    return false; // exit 1 → not ignored (trackable without -f)
  }
}

// [path, expectIgnored, why]
const FIXTURES = [
  // ── must be TRACKABLE (not ignored) ──
  ['000-docs/000-INDEX.md', false, 'mandatory index is always trackable'],
  ['000-docs/.gitignore', false, 'the policy file itself must be trackable'],
  ['000-docs/000-XX-STND-hypothetical-standard.md', false, 'canonical 000-* standards auto-public'],
  ['000-docs/agentskills-spec-snapshot.md', false, 'spec snapshot allowlisted'],
  ['000-docs/anthropic-skills-spec-snapshot.md', false, 'spec snapshot allowlisted'],
  [
    '000-docs/999-ZZ-TEST-ledger-fixture.md',
    false,
    'ledgered filing is trackable (permanent test ledger entry)',
  ],
  [
    '000-docs/999-ZZ-cluster-test/999-ZZ-TEST-nested-fixture.md',
    false,
    'ledgered filing inside a v4.4 cluster folder',
  ],
  [
    'plugins/productivity/000-jeremy-content-consistency-validator/fixtures/clean/000-docs/001-AT-ARCH-x.md',
    false,
    'consistency-validator golden fixture corpus must stay trackable (GH #991)',
  ],
  [
    'plugins/saas-packs/databricks-pack/000-docs/999-ZZ-TEST-new-record.md',
    false,
    'new Databricks pack records must be addable without force',
  ],
  [
    'plugins/saas-packs/databricks-pack/000-docs/research/999-ZZ-TEST-nested-record.md',
    false,
    'the Databricks exception includes nested public records',
  ],
  // ── must be IGNORED (local by default / private / runtime) ──
  [
    '000-docs/728-RA-REPT-unledgered.md',
    true,
    'unledgered filing fails closed (git add errors loudly)',
  ],
  [
    '000-docs/729-AT-DECR-future-internal-record.md',
    true,
    'future internal decision records are local by default',
  ],
  [
    '000-docs/.local-originals/example.ORIGINAL.md',
    true,
    'byte-exact local originals never leave the box',
  ],
  ['000-docs/680-AT-DECR-internal.md', true, 'held-out internal record stays local'],
  ['000-docs/683-AT-DECR-internal.md', true, 'held-out internal record stays local'],
  ['000-docs/scratch.tmp', true, 'runtime/temp files stay local'],
  ['plugins/other-pack/000-docs/private-notes.md', true, 'nested per-pack private docs stay local'],
  ['scripts/.kernel-shadow/report.json', true, 'generated CI artifacts stay local'],
  // Learning Lab: published teaching material linked from README L917/925/926 and
  // the eight /learning/* site pages. Wiped once already (CRITICAL RECOVERY
  // da09e99d7, 2025-12-21) — these assertions keep the ignore rule from re-hiding it.
  [
    'workspace/lab/GUIDE-00-START-HERE.md',
    false,
    'published Learning Lab guide must stay trackable',
  ],
  [
    'workspace/lab/GUIDE-99-BRAND-NEW.md',
    false,
    'a NEW Learning Lab guide must be trackable, not silently ignored',
  ],
  ['workspace/scratch-notes.md', true, 'workspace outside lab/ stays a scratch sandbox'],
  ['workspace/experiments/throwaway.py', true, 'workspace sandbox subdirs stay ignored'],
];

let failures = 0;
for (const [path, expectIgnored, why] of FIXTURES) {
  const actual = isIgnored(path);
  if (actual !== expectIgnored) {
    failures += 1;
    console.error(
      `✗ ${path}\n    expected ${expectIgnored ? 'IGNORED' : 'TRACKABLE'} but got ${actual ? 'IGNORED' : 'TRACKABLE'} — ${why}`,
    );
  }
}

// Grandfathered invariant: pattern-level ignore of an unledgered-but-tracked doc
// must NOT untrack it. (Tracked files are immune to ignore rules; this catches
// anyone "fixing" the design by un-tracking docs instead of ledgering them.)
const lsFiles = execFileSync('git', ['ls-files', '000-docs']).toString().trim().split('\n');
if (!lsFiles.includes('000-docs/716-RA-DATA-repo-state-baseline.md')) {
  failures += 1;
  console.error(
    '✗ grandfathered tracked doc 716-RA-DATA missing from git ls-files — tracked docs must stay tracked',
  );
}

if (failures) {
  console.error(
    `\ndocs-ignore-policy: ${failures} regression(s). See 000-docs/.gitignore header before changing rules.`,
  );
  process.exit(1);
}
console.log(`docs-ignore-policy: ${FIXTURES.length + 1} assertions OK`);
