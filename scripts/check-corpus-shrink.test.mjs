import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { checkCorpusShrink, withdrawnPaths } from './check-corpus-shrink.mjs';

const CLI = fileURLToPath(new URL('./check-corpus-shrink.mjs', import.meta.url));
const CATALOG = '.claude-plugin/marketplace.extended.json';
const A = { name: 'alpha', source: './plugins/core/alpha' };
const B = { name: 'beta', source: './plugins/core/beta' };

function fixture(t, plugins = [A, B], files) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'corpus-shrink-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const git = (...args) =>
    execFileSync('git', args, {
      cwd: root,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    }).trim();
  const write = (name, value = '# skill\n') => {
    fs.mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
    fs.writeFileSync(path.join(root, name), value);
  };
  const catalog = (rows) => write(CATALOG, JSON.stringify({ plugins: rows }));
  const commit = () => {
    git('add', '.');
    git('-c', 'core.hooksPath=/dev/null', 'commit', '--allow-empty', '-qm', 'fixture');
    return git('rev-parse', 'HEAD');
  };
  git('init', '-q');
  git('config', 'user.email', 'test@example.com');
  git('config', 'user.name', 'Test');
  files ??= Array.from(
    { length: 100 },
    (_, i) => `plugins/core/${i < 60 ? 'alpha' : 'beta'}/skills/skill-${i}/SKILL.md`,
  );
  catalog(plugins);
  files.forEach((file) => write(file));
  const baseline = commit();
  const remove = (count) =>
    files.slice(0, count).forEach((file) => fs.rmSync(path.join(root, file)));
  const check = (current, extra = {}) =>
    checkCorpusShrink(
      { baseline_count: files.length, current_count: current, baseline_sha: baseline, ...extra },
      { root },
    );
  return { root, git, write, catalog, commit, files, baseline, remove, check };
}

test('integer tolerance accepts exactly 2 percent but refuses more', (t) => {
  const f = fixture(t);
  f.remove(2);
  f.commit();
  assert.equal(f.check(98).allowed, true);
  fs.rmSync(path.join(f.root, f.files[2]));
  f.commit();
  const result = f.check(97);
  assert.equal(result.allowed, false);
  assert.equal(result.withdrawn_count, 0);
  assert.equal(result.unmatched_net_loss, 3);
});

test('actual withdrawal and quarantine credit only unique removed baseline files', async (t) => {
  for (const quarantine of [false, true])
    await t.test(String(quarantine), (t) => {
      const f = fixture(t, [A, { ...A, name: 'alpha-alias' }, B]);
      f.remove(60);
      f.catalog(
        quarantine
          ? [
              { ...A, publication: 'quarantined' },
              { ...A, name: 'alpha-alias', publication: 'quarantined' },
              B,
            ]
          : [B],
      );
      f.commit();
      const result = f.check(40);
      assert.equal(result.allowed, true);
      assert.equal(result.removed_count, 60);
      assert.equal(result.withdrawn_count, 60);
      assert.equal(new Set(result.withdrawn_paths).size, 60);
      assert.equal(result.unmatched_net_loss, 0);
    });
});

test('remaining alias, relocated identity, ancestor, descendant and prefix sibling cannot fake withdrawal', async (t) => {
  const cases = [
    ['alias', [{ ...A, name: 'alpha-alias' }, B]],
    ['relocated', [{ ...A, source: './plugins/other/alpha' }, B]],
    ['same-root-new-name', [{ name: 'replacement', source: './plugins/core/alpha' }, B]],
    ['descendant', [{ name: 'nested', source: './plugins/core/alpha/nested' }, B]],
  ];
  for (const [name, catalog] of cases)
    await t.test(name, (t) => {
      const f = fixture(t, [A, { ...A, name: 'alpha-alias' }, B]);
      f.remove(60);
      f.catalog(catalog);
      f.commit();
      assert.equal(f.check(40).withdrawn_count, 0);
      assert.equal(f.check(40).allowed, false);
    });
  await t.test('prefix sibling is distinct', (t) => {
    const f = fixture(t);
    f.remove(60);
    f.catalog([{ name: 'sibling', source: './plugins/core/alpha-extra' }, B]);
    f.commit();
    assert.equal(f.check(40).withdrawn_count, 60);
  });
});

test('nested baseline ownership is ambiguous and earns no credit', (t) => {
  const file = 'plugins/core/alpha/nested/skills/one/SKILL.md';
  const f = fixture(t, [A, { name: 'nested', source: './plugins/core/alpha/nested' }], [file]);
  f.remove(1);
  f.catalog([]);
  f.commit();
  assert.equal(f.check(0).withdrawn_count, 0);
  assert.equal(f.check(0).allowed, false);
});

test('a current published ancestor prevents credit for a withdrawn nested root', (t) => {
  const file = 'plugins/core/alpha/nested/skills/one/SKILL.md';
  const f = fixture(t, [{ name: 'nested', source: './plugins/core/alpha/nested' }], [file]);
  f.remove(1);
  f.catalog([A]);
  f.commit();
  assert.equal(f.check(0).withdrawn_count, 0);
  assert.equal(f.check(0).allowed, false);
});

test('curriculum and unpublished orphan losses receive no withdrawal credit', (t) => {
  const f = fixture(
    t,
    [],
    ['skills/01-course/one/SKILL.md', 'plugins/core/orphan/skills/one/SKILL.md'],
  );
  f.remove(2);
  f.commit();
  assert.equal(f.check(0).withdrawn_count, 0);
  assert.equal(f.check(0).allowed, false);
});

test('readded catalog identity revokes earlier withdrawal credit', (t) => {
  const f = fixture(t);
  f.remove(60);
  f.catalog([B]);
  f.commit();
  assert.equal(f.check(40).allowed, true);
  f.catalog([A, B]);
  f.commit();
  assert.equal(f.check(40).withdrawn_count, 0);
});

test('metadata-only catalog edits do not excuse deletion; new fake entries earn no extra credit', (t) => {
  const f = fixture(t);
  f.remove(60);
  f.catalog([{ ...A, description: 'updated' }, B, { name: 'fake', source: './plugins/new/fake' }]);
  f.commit();
  assert.equal(f.check(40).withdrawn_count, 0);
  assert.equal(f.check(40).allowed, false);
});

test('excluded-but-still-tracked files and file-to-directory conversions earn zero credit', () => {
  const file = 'plugins/core/alpha/skills/one/SKILL.md';
  const catalog = [{ name: 'alpha', root: 'plugins/core/alpha' }];
  assert.deepEqual(withdrawnPaths([file], [], [file], catalog, []), []);
  assert.deepEqual(withdrawnPaths([file], [], [`${file}/retained.txt`], catalog, []), []);
  assert.equal(withdrawnPaths([file, file], [], [], catalog, []).length, 1);
});

test('symlink or gitlink ancestor replacements fail closed', async (t) => {
  for (const mode of ['symlink', 'gitlink'])
    await t.test(mode, (t) => {
      const f = fixture(t);
      fs.rmSync(path.join(f.root, 'plugins/core/alpha'), { recursive: true });
      f.catalog([B]);
      if (mode === 'symlink') fs.symlinkSync('/outside', path.join(f.root, 'plugins/core/alpha'));
      else {
        f.git('add', '.');
        f.git('update-index', '--add', '--cacheinfo', `160000,${f.baseline},plugins/core/alpha`);
        f.git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'gitlink');
        // An uninitialized gitlink directory is clean; no submodule code is checked out.
        fs.mkdirSync(path.join(f.root, 'plugins/core/alpha'));
        assert.throws(() => f.check(40), /non-directory ancestor/);
        return;
      }
      f.commit();
      assert.throws(() => f.check(40), /non-directory ancestor/);
    });
});

test('counts, exact refs, ancestry and checkout identity must match actual Git evidence', (t) => {
  const f = fixture(t);
  for (const bad of [true, -1, 1.5, '100', null, Number.MAX_SAFE_INTEGER + 1]) {
    assert.throws(() => f.check(100, { baseline_count: bad }), /safe integer/);
    assert.throws(() => f.check(100, { current_count: bad }), /safe integer/);
  }
  assert.throws(() => f.check(100, { baseline_count: 0 }), /safe integer/);
  assert.throws(() => f.check(99), /checkout Git census/);
  assert.throws(() => f.check(100, { baseline_count: 99 }), /baseline Git census/);
  assert.throws(() => f.check(100, { baseline_sha: 'HEAD' }), /exact.*SHA/);
  assert.throws(() => f.check(100, { baseline_sha: 'a'.repeat(40) }));
  const blob = f.git('rev-parse', `${f.baseline}:${CATALOG}`);
  assert.throws(() => f.check(100, { baseline_sha: blob }), /commit object/);
  const tree = f.git('rev-parse', 'HEAD^{tree}');
  const unrelated = f.git('commit-tree', tree, '-m', 'unrelated');
  assert.throws(() => f.check(100, { baseline_sha: unrelated }), /ancestor/);
  assert.throws(() => f.check(100, { checkout_sha: unrelated }), /does not match HEAD/);
  assert.throws(() => f.check(100, { unexpected: true }), /unknown input field/);
});

test('untracked files cannot affect census; tracked dirty state is refused', (t) => {
  const f = fixture(t);
  f.write('plugins/new/untracked/skills/new/SKILL.md');
  assert.equal(f.check(100).allowed, true);
  f.write(f.files[0], '# changed\n');
  assert.throws(() => f.check(100), /must be clean/);
  f.git('add', f.files[0]);
  assert.throws(() => f.check(100), /must be clean/);
});

test('Git replacement objects cannot substitute the immutable baseline census', (t) => {
  const f = fixture(t);
  f.remove(3);
  const current = f.commit();
  f.git('replace', f.baseline, current);
  const result = f.check(97);
  assert.equal(result.baseline_count, 100);
  assert.equal(result.removed_count, 3);
  assert.equal(result.allowed, false);
});

test('missing and malformed catalogs and publication states fail closed', async (t) => {
  const cases = [
    null,
    {},
    { plugins: 'bad' },
    { plugins: [{ ...A, publication: 'hidden' }] },
    { plugins: [A, A] },
    { plugins: [{ ...A, source: '../outside' }] },
    { plugins: [{ ...A, source: './plugins/core/../alpha' }] },
    { plugins: [{ publication: 'quarantined' }] },
  ];
  for (const [index, value] of cases.entries())
    await t.test(String(index), (t) => {
      const f = fixture(t);
      f.write(CATALOG, JSON.stringify(value));
      f.commit();
      assert.throws(() => f.check(100));
    });
  await t.test('absent', (t) => {
    const f = fixture(t);
    fs.rmSync(path.join(f.root, CATALOG));
    f.commit();
    assert.throws(() => f.check(100), /regular tracked file/);
  });
});

test('CLI emits structured verdicts and refuses invalid payloads with exit 2', (t) => {
  const f = fixture(t);
  const invoke = (input) =>
    spawnSync(process.execPath, [CLI, '--repo-root', f.root], {
      input: JSON.stringify(input),
      encoding: 'utf8',
    });
  const input = {
    baseline_count: 100,
    current_count: 100,
    baseline_sha: f.baseline,
    checkout_sha: f.baseline,
  };
  const pass = invoke(input);
  assert.equal(pass.status, 0, pass.stderr);
  assert.equal(JSON.parse(pass.stdout).allowed, true);
  for (const value of [[], null, {}, { ...input, current_count: 99 }]) {
    const result = invoke(value);
    assert.equal(result.status, 2);
    assert.equal(result.stdout, '');
  }
  f.remove(3);
  f.commit();
  const refused = invoke({ ...input, checkout_sha: f.git('rev-parse', 'HEAD'), current_count: 97 });
  assert.equal(refused.status, 0, refused.stderr);
  assert.equal(JSON.parse(refused.stdout).allowed, false);
});
