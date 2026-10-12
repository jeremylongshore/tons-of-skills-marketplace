import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const matched = {
  mode: 'shadow-advisory',
  available: true,
  required_match: true,
  hand_authored_always_required: ['name'],
  kernel_effective_required: ['name'],
  required_only_in_hand_authored: [],
  required_only_in_kernel: [],
  disallowed_tools: { in_hand_authored_registry: true, in_kernel_properties: true, match: true },
  plugin_manifest: {
    available: true,
    fields_match: true,
    hand_authored_fields: ['name'],
    kernel_fields: ['name'],
    stale_missing_from_hand_authored: [],
    only_in_hand_authored: [],
  },
};

function exercise(t, label, shadowEntries) {
  const dir = mkdtempSync(join(tmpdir(), 'kernel-shadow-registry-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  mkdirSync(join(dir, 'scripts'), { recursive: true });
  mkdirSync(join(dir, '.venv', 'bin'), { recursive: true });
  symlinkSync(join(root, 'node_modules'), join(dir, 'node_modules'), 'dir');
  for (const name of ['kernel-shadow-validation.mjs', 'kernel-shadow-registry.mjs']) {
    const source = join(root, 'scripts', name);
    if (existsSync(source)) copyFileSync(source, join(dir, 'scripts', name));
  }
  // Supply a deterministic Python batch boundary; execute the real JS CLI,
  // installed kernel schemas, report writer, and GitHub summary writer.
  writeFileSync(join(dir, 'scripts', 'validate-skills-schema.py'), '# fixture\n');
  const batch = [{ path: 'SKILL.md', errors: 0, error_details: [] }, ...shadowEntries];
  writeFileSync(
    join(dir, '.venv', 'bin', 'python3'),
    `#!/usr/bin/env node\nconsole.log(${JSON.stringify(JSON.stringify(batch))});\n`,
    { mode: 0o755 },
  );
  writeFileSync(
    join(dir, 'SKILL.md'),
    '---\nname: registry-probe\ndescription: Inspect a deterministic registry fixture.\n' +
      'version: 1.0.0\nauthor: Fixture\nlicense: MIT\ncompatibility: Claude Code\n' +
      'tags: [testing]\nallowed-tools: Read\n---\n\n## Overview\nFixture.\n',
  );
  const summaryPath = join(dir, 'summary.md');
  const run = spawnSync(process.execPath, [join(dir, 'scripts', 'kernel-shadow-validation.mjs')], {
    encoding: 'utf8',
    env: { ...process.env, GITHUB_STEP_SUMMARY: summaryPath },
    timeout: 30_000,
  });
  assert.equal(run.status, 0, run.stderr || run.error?.message);
  const reportText = readFileSync(join(dir, 'scripts', '.kernel-shadow', 'report.json'), 'utf8');
  const report = JSON.parse(reportText);
  const summary = readFileSync(summaryPath, 'utf8');
  assert.equal(report.blocking, false);
  assert.equal(report.totals.files, 1, 'registry data must not become a corpus file');
  assert.ok(report.lanes['authoring/v1']);
  assert.ok(report.lanes['authoring/v2']);
  // Retain labeled fixture evidence alongside the real report in advisory CI.
  // These are synthetic transport proofs, never real-corpus currency claims.
  const evidence = join(root, 'scripts', '.kernel-shadow', 'registry-fixture-proof');
  mkdirSync(evidence, { recursive: true });
  writeFileSync(
    join(evidence, `${label}.json`),
    JSON.stringify(
      { evidenceKind: 'synthetic-registry-transport', fixture: label, report },
      null,
      2,
    ) + '\n',
  );
  writeFileSync(join(evidence, `${label}.md`), `Synthetic fixture: ${label}\n\n${summary}`);
  return { report, summary, stdout: run.stdout };
}

test('matching plugin registry is retained separately from corpus comparisons', (t) => {
  const { report, summary } = exercise(t, 'match', [{ kernel_shadow: matched }]);
  assert.equal(report.registryShadow.comparisons.plugin_manifest.status, 'match');
  assert.deepEqual(report.registryShadow.raw, matched);
  assert.match(summary, /plugin_manifest.*match/);
});

for (const [label, missing, extra] of [
  ['missing-field', ['future-field'], []],
  ['extra-field', [], ['local-field']],
]) {
  test(`${label} is visible in the retained report and job summary without blocking`, (t) => {
    const shadow = globalThis.structuredClone(matched);
    shadow.plugin_manifest = {
      ...shadow.plugin_manifest,
      fields_match: false,
      hand_authored_fields: ['name', ...extra],
      kernel_fields: ['name', ...missing],
      stale_missing_from_hand_authored: missing,
      only_in_hand_authored: extra,
    };
    const { report, summary, stdout } = exercise(t, label, [{ kernel_shadow: shadow }]);
    assert.equal(report.registryShadow.comparisons.plugin_manifest.status, 'mismatch');
    assert.deepEqual(report.registryShadow.raw, shadow);
    for (const field of [...missing, ...extra]) {
      assert.ok(summary.includes(field));
      assert.ok(stdout.includes(field));
    }
  });
}

test('unavailable plugin schema remains explicitly unavailable', (t) => {
  const shadow = { ...matched, plugin_manifest: { available: false, note: 'schema absent' } };
  const { report, summary } = exercise(t, 'unavailable', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.comparisons.plugin_manifest.status, 'unavailable');
  assert.match(summary, /schema absent/);
});

test('missing shadow output cannot look like matching registries', (t) => {
  const { report, summary } = exercise(t, 'missing-output', []);
  assert.equal(report.registryShadow.status, 'missing');
  assert.match(summary, /missing/);
});

test('malformed plugin comparison cannot look like a match', (t) => {
  const shadow = { ...matched, plugin_manifest: { available: true, fields_match: 'true' } };
  const { report, summary } = exercise(t, 'malformed', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.comparisons.plugin_manifest.status, 'invalid');
  assert.match(summary, /invalid/);
});

test('duplicate or null shadow entries are invalid and do not crash corpus reporting', (t) => {
  const { report, summary } = exercise(t, 'duplicate', [
    { kernel_shadow: matched },
    { kernel_shadow: null },
  ]);
  assert.equal(report.registryShadow.status, 'invalid');
  assert.match(summary, /invalid/);
});

test('a true flag cannot conceal a field-set disagreement', (t) => {
  const shadow = globalThis.structuredClone(matched);
  shadow.plugin_manifest.kernel_fields.push('unreported-field');
  const { report, summary } = exercise(t, 'inconsistent-flag', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.comparisons.plugin_manifest.status, 'invalid');
  assert.match(summary, /deltas disagree/);
});

test('unavailable kernel evidence remains visible with no registry-match claim', (t) => {
  const shadow = { mode: 'shadow-advisory', available: false, note: 'kernel unavailable' };
  const { report, summary } = exercise(t, 'kernel-unavailable', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.status, 'unavailable');
  assert.equal(report.registryShadow.comparisons, undefined);
  assert.match(summary, /kernel unavailable/);
});

test('required-field match flags must agree with their supporting sets', (t) => {
  const shadow = globalThis.structuredClone(matched);
  shadow.kernel_effective_required.push('future-required');
  const { report, summary } = exercise(t, 'required-inconsistent', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.comparisons.skill_required.status, 'invalid');
  assert.match(summary, /skill_required.*invalid/);
});

test('disallowed-tools match flags must agree with observed presence', (t) => {
  const shadow = globalThis.structuredClone(matched);
  shadow.disallowed_tools.in_kernel_properties = false;
  const { report, summary } = exercise(t, 'tools-inconsistent', [{ kernel_shadow: shadow }]);
  assert.equal(report.registryShadow.comparisons.disallowed_tools.status, 'invalid');
  assert.match(summary, /disallowed_tools.*invalid/);
});
