import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { CORPUS_COHORTS, resolveCorpus } from './corpus-resolver.mjs';

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'corpus-resolver-'));
  fs.mkdirSync(path.join(root, '.claude-plugin'), { recursive: true });
  fs.writeFileSync(
    path.join(root, '.claude-plugin', 'marketplace.extended.json'),
    JSON.stringify({
      plugins: [
        { name: 'owned', source: './plugins/core/owned' },
        { name: 'mirror', source: './plugins/community/mirror' },
      ],
    }),
  );
  return root;
}

function write(root, relativePath, value = '# skill\n') {
  const target = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, value);
}

test('exact graded refs resolve deleted historical files without the worktree', (t) => {
  const root = fixture();
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const run = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
  run('init', '-q');
  run('config', 'user.email', 'test@example.com');
  run('config', 'user.name', 'Test');
  const skill = 'plugins/core/owned/skills/historical/SKILL.md';
  write(root, skill);
  run('add', '.');
  run('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'baseline');
  const ref = run('rev-parse', 'HEAD');
  fs.rmSync(path.join(root, skill));
  assert.deepEqual(resolveCorpus('graded', { root, ref }), [skill]);
  assert.throws(() => resolveCorpus('graded', { root, ref: 'HEAD' }), /exact.*SHA/);
  assert.throws(() => resolveCorpus('graded', { root, ref: ref.slice(0, 8) }), /exact.*SHA/);
  assert.throws(() => resolveCorpus('graded', { root, ref: 'a'.repeat(40) }), /historical tree/);
  const blob = run('rev-parse', `${ref}:${skill}`);
  assert.throws(() => resolveCorpus('graded', { root, ref: blob }), /commit object/);
  assert.throws(() => resolveCorpus('curriculum', { root, ref }), /only the graded cohort/);
  assert.throws(() => resolveCorpus('graded', { root, ref, paths: [] }), /cannot be combined/);

  fs.symlinkSync('/outside/SKILL.md', path.join(root, skill));
  run('add', '.');
  run('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'symlink');
  assert.throws(
    () => resolveCorpus('graded', { root, ref: run('rev-parse', 'HEAD') }),
    /not a regular file/,
  );
});

function source(
  root,
  relativeDirectory,
  value = { synced_from: { repo: 'owner/repo', path: 'skills' } },
) {
  write(root, `${relativeDirectory}/.source.json`, JSON.stringify(value));
}

function corpusFixture() {
  const root = fixture();
  const paths = [
    'plugins/core/owned/skills/alpha/SKILL.md',
    'plugins/core/owned/SKILL.md',
    'plugins/core/owned/.codex/skills/hidden/SKILL.md',
    'plugins/community/mirror/skills/upstream/SKILL.md',
    'plugins/community/orphan/skills/orphan/SKILL.md',
    'skills/01-foundations/alpha/SKILL.md',
    'skills/.curated/alpha/SKILL.md',
    'skills/.curated/MANIFEST.json',
    'skills/.experimental/lab/SKILL.md',
  ];
  for (const entry of paths.filter((entry) => !entry.endsWith('MANIFEST.json'))) write(root, entry);
  write(
    root,
    'skills/.curated/MANIFEST.json',
    JSON.stringify({ count: 1, skills: [{ curated_name: 'alpha' }] }),
  );
  source(root, 'plugins/community/mirror');
  return { root, paths };
}

test('resolves every named cohort from one deterministic path authority', () => {
  const { root, paths } = corpusFixture();
  assert.deepEqual(CORPUS_COHORTS, [
    'marketplace-visible',
    'graded',
    'first-party',
    'curated-mirror',
    'curriculum',
  ]);
  assert.deepEqual(resolveCorpus('marketplace-visible', { root, paths }), [
    'plugins/community/mirror/skills/upstream/SKILL.md',
    'plugins/core/owned/SKILL.md',
    'plugins/core/owned/skills/alpha/SKILL.md',
  ]);
  assert.deepEqual(resolveCorpus('graded', { root, paths }), [
    'plugins/community/mirror/skills/upstream/SKILL.md',
    'plugins/community/orphan/skills/orphan/SKILL.md',
    'plugins/core/owned/.codex/skills/hidden/SKILL.md',
    'plugins/core/owned/SKILL.md',
    'plugins/core/owned/skills/alpha/SKILL.md',
    'skills/01-foundations/alpha/SKILL.md',
  ]);
  assert.deepEqual(resolveCorpus('first-party', { root, paths }), [
    'plugins/community/orphan/skills/orphan/SKILL.md',
    'plugins/core/owned/.codex/skills/hidden/SKILL.md',
    'plugins/core/owned/SKILL.md',
    'plugins/core/owned/skills/alpha/SKILL.md',
  ]);
  assert.deepEqual(resolveCorpus('curated-mirror', { root, paths }), [
    'skills/.curated/alpha/SKILL.md',
  ]);
  assert.deepEqual(resolveCorpus('curriculum', { root, paths }), [
    'skills/01-foundations/alpha/SKILL.md',
  ]);
});

test('deduplicates, normalizes, and sorts fixture paths', () => {
  const { root, paths } = corpusFixture();
  const duplicated = [...paths, './plugins/core/owned/skills/alpha/SKILL.md', paths[0]];
  assert.deepEqual(resolveCorpus('curriculum', { root, paths: duplicated }), [
    'skills/01-foundations/alpha/SKILL.md',
  ]);
});

test('red proof: the legacy raw plugin count admits hidden and orphaned skills', () => {
  const { root, paths } = corpusFixture();
  const legacy = paths.filter(
    (entry) => entry.startsWith('plugins/') && entry.endsWith('/SKILL.md'),
  );
  const governed = resolveCorpus('marketplace-visible', { root, paths });
  assert.equal(legacy.length, 5, 'RED PROOF: the old raw walker admits every plugin skill');
  assert.equal(governed.length, 3);
  assert.ok(!governed.some((entry) => entry.includes('/.codex/')));
  assert.ok(!governed.some((entry) => entry.includes('/orphan/')));
});

test('sibling provenance does not taint first-party skills', () => {
  const { root, paths } = corpusFixture();
  source(root, 'plugins/core/sibling');
  assert.ok(
    resolveCorpus('first-party', { root, paths }).includes(
      'plugins/core/owned/skills/alpha/SKILL.md',
    ),
  );
});

test('unknown cohorts and path traversal fail closed', () => {
  const { root, paths } = corpusFixture();
  assert.throws(() => resolveCorpus('everything', { root, paths }), /unknown cohort/);
  assert.throws(
    () => resolveCorpus('graded', { root, paths: [...paths, '../outside/SKILL.md'] }),
    /path escapes repository/,
  );
  assert.throws(
    () => resolveCorpus('graded', { root, paths: [...paths, 'C:/outside/SKILL.md'] }),
    /path escapes repository/,
  );
});

test('marketplace membership follows catalog source roots, never matching names', () => {
  const { root, paths } = corpusFixture();
  const collision = 'plugins/other/owned/skills/collision/SKILL.md';
  write(root, collision);
  write(root, 'plugins/other/owned/.claude-plugin/plugin.json', JSON.stringify({ name: 'owned' }));
  assert.ok(
    !resolveCorpus('marketplace-visible', { root, paths: [...paths, collision] }).includes(
      collision,
    ),
  );
});

test('malformed and contradictory provenance fail closed', () => {
  for (const marker of ['{bad-json', JSON.stringify({})]) {
    const { root, paths } = corpusFixture();
    write(root, 'plugins/core/owned/.source.json', marker);
    assert.throws(() => resolveCorpus('first-party', { root, paths }), /SOURCE_RECORD/);
  }
});

test('nested provenance excludes descendants and non-regular provenance fails closed', () => {
  const { root, paths } = corpusFixture();
  source(root, 'plugins/core/owned/skills');
  assert.ok(
    !resolveCorpus('first-party', { root, paths }).includes(
      'plugins/core/owned/skills/alpha/SKILL.md',
    ),
  );

  const second = corpusFixture();
  fs.mkdirSync(path.join(second.root, 'plugins/core/owned/.source.json'));
  assert.throws(
    () => resolveCorpus('first-party', { root: second.root, paths: second.paths }),
    /SOURCE_RECORD_NOT_REGULAR/,
  );
});

test('curated manifest drift fails closed', () => {
  const { root, paths } = corpusFixture();
  write(
    root,
    'skills/.curated/MANIFEST.json',
    JSON.stringify({ count: 1, skills: [{ curated_name: 'different' }] }),
  );
  assert.throws(
    () =>
      resolveCorpus('curated-mirror', {
        root,
        paths,
      }),
    /manifest membership contradicts/,
  );
});

test('duplicate curated manifest rows cannot mask an omitted skill', () => {
  const { root, paths } = corpusFixture();
  write(root, 'skills/.curated/beta/SKILL.md');
  write(
    root,
    'skills/.curated/MANIFEST.json',
    JSON.stringify({
      count: 2,
      skills: [{ curated_name: 'alpha' }, { curated_name: 'alpha' }],
    }),
  );
  assert.throws(
    () =>
      resolveCorpus('curated-mirror', {
        root,
        paths: [...paths, 'skills/.curated/beta/SKILL.md'],
      }),
    /manifest membership contradicts/,
  );
});

test('curated files without a tracked manifest fail closed', () => {
  const { root, paths } = corpusFixture();
  assert.throws(
    () =>
      resolveCorpus('curated-mirror', {
        root,
        paths: paths.filter((entry) => entry !== 'skills/.curated/MANIFEST.json'),
      }),
    /without a tracked MANIFEST/,
  );
});

test('tracked SKILL.md symlinks fail closed from the real Git index', () => {
  const root = fixture();
  const externalDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'corpus-resolver-external-'));
  const external = path.join(externalDirectory, 'SKILL.md');

  try {
    fs.writeFileSync(external, '# external\n');
    const skill = path.join(root, 'plugins', 'core', 'owned', 'skills', 'linked', 'SKILL.md');
    fs.mkdirSync(path.dirname(skill), { recursive: true });
    fs.symlinkSync(external, skill);
    execFileSync('git', ['init', '-q'], { cwd: root });
    execFileSync('git', ['add', '.'], { cwd: root });
    assert.throws(() => resolveCorpus('marketplace-visible', { root }), /symbolic link/);
    assert.throws(
      () =>
        resolveCorpus('marketplace-visible', {
          root,
          paths: ['plugins/core/owned/skills/linked/SKILL.md'],
        }),
      /symbolic link/,
    );
    const redirected = path.join(root, 'plugins', 'core', 'owned', 'skills', 'redirected');
    fs.symlinkSync(externalDirectory, redirected);
    assert.throws(
      () =>
        resolveCorpus('marketplace-visible', {
          root,
          paths: ['plugins/core/owned/skills/redirected/SKILL.md'],
        }),
      /symbolic link/,
    );
  } finally {
    fs.rmSync(externalDirectory, { force: true, recursive: true });
    fs.rmSync(root, { force: true, recursive: true });
  }
});

test('CLI batches multiple named cohorts in one resolver process', () => {
  const { root } = corpusFixture();
  const resolver = path.join(path.dirname(fileURLToPath(import.meta.url)), 'corpus-resolver.mjs');
  const payload = JSON.parse(
    execFileSync(
      process.execPath,
      [resolver, '--root', root, '--cohort', 'graded', '--cohort', 'first-party', '--json'],
      { encoding: 'utf8' },
    ),
  );
  assert.deepEqual(Object.keys(payload.cohorts), ['graded', 'first-party']);
  assert.equal(payload.cohorts.graded.count, 6);
  assert.equal(payload.cohorts['first-party'].count, 4);
});
