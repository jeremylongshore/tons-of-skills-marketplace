/**
 * Hostile-repository corpus for the external-sync filesystem paths.
 * Drives the real exported sync functions against fake upstream checkouts and
 * mirror trees that contain planted links, special files and traversal
 * manifests, and proves nothing outside the intended target is read or written.
 *
 *   node --test scripts/sync-external-fs.test.mjs
 */

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  ensureCatalogEntry,
  mirrorFiles,
  mirrorTargetRel,
  pruneOrphans,
  readUpstreamFiles,
  readUpstreamLicense,
} from './sync-external.mjs';
import { loadLock, saveLock } from './sync-lockfile.mjs';

const IS_WINDOWS = process.platform === 'win32';
const quiet = () => {};

function sandbox() {
  const base = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'sync-fs-')));
  const dirs = {
    base,
    checkout: path.join(base, 'checkout'),
    repo: path.join(base, 'repo'),
    outside: path.join(base, 'outside'),
  };
  for (const d of [dirs.checkout, dirs.repo, dirs.outside]) fs.mkdirSync(d);
  fs.writeFileSync(path.join(dirs.outside, 'runner-secret'), 'RUNNER_TOKEN=abc');
  dirs.cleanup = () => fs.rmSync(base, { recursive: true, force: true });
  return dirs;
}

function put(root, rel, content = 'x') {
  const p = path.join(root, ...rel.split('/'));
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content);
  return p;
}

function linkDir(target, at) {
  fs.symlinkSync(target, at, IS_WINDOWS ? 'junction' : 'dir');
}

function linkFileOrSkip(t, target, at) {
  try {
    fs.symlinkSync(target, at, 'file');
    return true;
  } catch (error) {
    if (error.code === 'EPERM' || error.code === 'EACCES') {
      t.skip(`file symlinks need privilege here (${error.code})`);
      return false;
    }
    throw error;
  }
}

function outsideUntouched(s) {
  assert.deepEqual(fs.readdirSync(s.outside), ['runner-secret']);
  assert.equal(fs.readFileSync(path.join(s.outside, 'runner-secret'), 'utf8'), 'RUNNER_TOKEN=abc');
}

// ------------------------------------------------------------ target_path

test('target_path must be a directory under plugins/', () => {
  assert.equal(mirrorTargetRel('./plugins/community/x/'), 'plugins/community/x');
  for (const bad of [
    '.github/workflows',
    'plugins',
    '../plugins/x',
    '/plugins/x',
    'plugins/../scripts',
    'scripts/x',
  ]) {
    assert.throws(() => mirrorTargetRel(bad), `accepted ${bad}`);
  }
});

// ------------------------------------------------------------ upstream reads

test('upstream LICENSE that is a symlink to a runner file is refused, never read', (t) => {
  const s = sandbox();
  try {
    if (!linkFileOrSkip(t, path.join(s.outside, 'runner-secret'), path.join(s.checkout, 'LICENSE')))
      return;
    assert.throws(() => readUpstreamLicense(s.checkout, 'LICENSE'), /not a regular file/);
  } finally {
    s.cleanup();
  }
});

test('upstream license path must be a root LICENSE/COPYING file that exists', () => {
  const s = sandbox();
  try {
    assert.throws(() => readUpstreamLicense(s.checkout, 'LICENSE'), /unavailable/);
    fs.mkdirSync(path.join(s.checkout, 'LICENSE'));
    assert.throws(() => readUpstreamLicense(s.checkout, 'LICENSE'), /not a regular file/);
    assert.throws(() => readUpstreamLicense(s.checkout, 'docs/LICENSE'), /root LICENSE/);
    assert.throws(() => readUpstreamLicense(s.checkout, '../LICENSE'));
    assert.throws(() => readUpstreamLicense(s.checkout, 'README.md'), /root LICENSE/);
    put(s.checkout, 'COPYING', 'GPL text');
    const lic = readUpstreamLicense(s.checkout, 'COPYING');
    assert.equal(lic.path, 'COPYING');
    assert.equal(lic.content.toString(), 'GPL text');
  } finally {
    s.cleanup();
  }
});

test('upstream source_path whose parent is a link is refused, not walked', () => {
  const s = sandbox();
  try {
    put(s.outside, 'skills/x/SKILL.md', 'stolen');
    linkDir(s.outside, path.join(s.checkout, 'plugins'));
    assert.throws(() => readUpstreamFiles(s.checkout, 'plugins/skills'));
    assert.throws(() => readUpstreamFiles(s.checkout, 'plugins'));
  } finally {
    s.cleanup();
  }
});

test('upstream links inside the source tree are skipped and reported, never followed', () => {
  const s = sandbox();
  try {
    put(s.checkout, 'plugin/SKILL.md', 'real');
    put(s.checkout, 'plugin/.git/config', 'git');
    linkDir(s.outside, path.join(s.checkout, 'plugin', 'escape'));
    const { files, skipped } = readUpstreamFiles(s.checkout, './plugin/');
    assert.deepEqual(
      files.map((f) => f.path),
      ['SKILL.md'],
    );
    assert.deepEqual(
      skipped.map((x) => x.path),
      ['escape'],
    );
    assert.ok(!files.some((f) => f.content.toString().includes('RUNNER_TOKEN')));
    assert.deepEqual(
      readUpstreamFiles(s.checkout, '.').files.map((f) => f.path),
      ['plugin/SKILL.md'],
    );
  } finally {
    s.cleanup();
  }
});

// ------------------------------------------------------------ mirror writes

test('mirror writes land atomically with canonical modes, and a re-run is a no-op', () => {
  const s = sandbox();
  try {
    const files = [
      { path: 'SKILL.md', content: Buffer.from('skill'), mode: 0o100644 },
      { path: 'scripts/run.sh', content: Buffer.from('#!/bin/sh\n'), mode: 0o100755 },
    ];
    const first = mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet });
    assert.deepEqual(
      first.map((c) => c.action),
      ['new', 'new'],
    );
    assert.equal(fs.readFileSync(path.join(s.repo, 'plugins/c/x/SKILL.md'), 'utf8'), 'skill');
    if (!IS_WINDOWS) {
      assert.equal(
        fs.statSync(path.join(s.repo, 'plugins/c/x/scripts/run.sh')).mode & 0o777,
        0o755,
      );
      assert.equal(fs.statSync(path.join(s.repo, 'plugins/c/x/SKILL.md')).mode & 0o777, 0o644);
    }
    assert.deepEqual(
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }),
      [],
    );
    files[0].content = Buffer.from('changed');
    assert.deepEqual(
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }).map(
        (c) => c.action,
      ),
      ['modified'],
    );
  } finally {
    s.cleanup();
  }
});

test('dry run reports changes but writes nothing', () => {
  const s = sandbox();
  try {
    const files = [{ path: 'SKILL.md', content: Buffer.from('skill'), mode: 0o100644 }];
    const changes = mirrorFiles({
      root: s.repo,
      targetRel: 'plugins/c/x',
      files,
      dryRun: true,
      report: quiet,
    });
    assert.deepEqual(changes, [{ path: 'SKILL.md', action: 'new' }]);
    assert.equal(fs.existsSync(path.join(s.repo, 'plugins')), false);
  } finally {
    s.cleanup();
  }
});

test('a planted directory link in the mirror tree refuses the write', () => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.repo, 'plugins', 'c', 'x'), { recursive: true });
    linkDir(s.outside, path.join(s.repo, 'plugins', 'c', 'x', 'skills'));
    const files = [{ path: 'skills/evil.sh', content: Buffer.from('pwned'), mode: 0o100755 }];
    assert.throws(() =>
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }),
    );
    outsideUntouched(s);
  } finally {
    s.cleanup();
  }
});

test('a planted link on the target_path itself refuses the write', () => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.repo, 'plugins'));
    linkDir(s.outside, path.join(s.repo, 'plugins', 'c'));
    const files = [{ path: 'SKILL.md', content: Buffer.from('x'), mode: 0o100644 }];
    assert.throws(() =>
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }),
    );
    outsideUntouched(s);
  } finally {
    s.cleanup();
  }
});

test('a planted file link where a mirror file belongs is refused', (t) => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.repo, 'plugins', 'c', 'x'), { recursive: true });
    if (
      !linkFileOrSkip(
        t,
        path.join(s.outside, 'runner-secret'),
        path.join(s.repo, 'plugins/c/x/SKILL.md'),
      )
    )
      return;
    const files = [{ path: 'SKILL.md', content: Buffer.from('overwrite'), mode: 0o100644 }];
    assert.throws(() =>
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }),
    );
    outsideUntouched(s);
  } finally {
    s.cleanup();
  }
});

test('an upstream file name that fails path rules is refused before any write', () => {
  const s = sandbox();
  try {
    const files = [{ path: '../../escape.sh', content: Buffer.from('x'), mode: 0o100755 }];
    assert.throws(() =>
      mirrorFiles({ root: s.repo, targetRel: 'plugins/c/x', files, report: quiet }),
    );
    assert.equal(fs.existsSync(path.join(s.base, 'escape.sh')), false);
  } finally {
    s.cleanup();
  }
});

// ------------------------------------------------------------ orphan prune

test('prune removes only owned regular files and refuses traversal and links', (t) => {
  const s = sandbox();
  try {
    put(s.repo, 'plugins/c/x/old.md', 'old');
    put(s.repo, 'plugins/c/x/keep.md', 'keep');
    put(s.repo, 'scripts/important.py', 'do not delete');
    let fileLink = false;
    try {
      fs.symlinkSync(
        path.join(s.outside, 'runner-secret'),
        path.join(s.repo, 'plugins/c/x/link.md'),
        'file',
      );
      fileLink = true;
    } catch {
      t.diagnostic('file symlink unavailable; link case not exercised');
    }
    const { changes, refused } = pruneOrphans({
      root: s.repo,
      targetRel: 'plugins/c/x',
      priorFiles: ['old.md', 'keep.md', '../../../scripts/important.py', 'link.md', 42, 'gone.md'],
      ownedFiles: ['keep.md'],
      report: quiet,
    });
    assert.deepEqual(changes, [{ path: 'old.md', action: 'deleted' }]);
    const refusedPaths = refused.map((r) => r.path);
    assert.ok(refusedPaths.includes('../../../scripts/important.py'));
    if (fileLink) assert.ok(refusedPaths.includes('link.md'));
    assert.equal(
      fs.readFileSync(path.join(s.repo, 'scripts/important.py'), 'utf8'),
      'do not delete',
    );
    assert.equal(fs.existsSync(path.join(s.repo, 'plugins/c/x/keep.md')), true);
    outsideUntouched(s);
    assert.deepEqual(
      pruneOrphans({ root: s.repo, targetRel: 'plugins/c/x', priorFiles: null, ownedFiles: [] }),
      {
        changes: [],
        refused: [],
      },
    );
  } finally {
    s.cleanup();
  }
});

// ------------------------------------------------------------ catalog + lock

test('a symlinked catalog is refused, not written through', (t) => {
  const s = sandbox();
  try {
    const realCatalog = put(s.outside, 'catalog.json', JSON.stringify({ plugins: [] }));
    const catalogFile = path.join(s.repo, 'marketplace.extended.json');
    if (!linkFileOrSkip(t, realCatalog, catalogFile)) return;
    const source = { name: 'x', target_path: 'plugins/community/x', repo: 'o/x', license: 'MIT' };
    assert.throws(() => ensureCatalogEntry(source, { root: s.repo, catalogFile, dryRun: false }));
    assert.equal(fs.readFileSync(realCatalog, 'utf8'), JSON.stringify({ plugins: [] }));
  } finally {
    s.cleanup();
  }
});

test('a catalog outside the repository root is refused', () => {
  const s = sandbox();
  try {
    const catalogFile = put(s.outside, 'catalog.json', JSON.stringify({ plugins: [] }));
    const source = { name: 'x', target_path: 'plugins/community/x', repo: 'o/x' };
    assert.throws(
      () => ensureCatalogEntry(source, { root: s.repo, catalogFile, dryRun: false }),
      /outside/,
    );
  } finally {
    s.cleanup();
  }
});

test('catalog append is atomic and leaves no temp file', () => {
  const s = sandbox();
  try {
    const catalogFile = put(
      s.repo,
      'marketplace.extended.json',
      '{\n  "plugins": [\n    {\n      "name": "a"\n    }\n  ]\n}\n',
    );
    const source = { name: 'x', target_path: 'plugins/community/x', repo: 'o/x', license: 'MIT' };
    assert.equal(ensureCatalogEntry(source, { root: s.repo, catalogFile, dryRun: false }), true);
    const data = JSON.parse(fs.readFileSync(catalogFile, 'utf8'));
    assert.deepEqual(
      data.plugins.map((p) => p.name),
      ['a', 'x'],
    );
    assert.deepEqual(
      fs.readdirSync(s.repo).filter((n) => n.endsWith('.tmp')),
      [],
    );
    assert.equal(ensureCatalogEntry(source, { root: s.repo, catalogFile, dryRun: false }), false);
  } finally {
    s.cleanup();
  }
});

test('a symlinked sources.lock.json fails closed on load and save', (t) => {
  const s = sandbox();
  try {
    const real = put(s.outside, 'lock.json', '{"version":1,"sources":{}}');
    const lockPath = path.join(s.repo, 'sources.lock.json');
    if (!linkFileOrSkip(t, real, lockPath)) return;
    assert.throws(() => loadLock(lockPath));
    assert.throws(() =>
      saveLock(lockPath, { version: 1, sources: { a: { repo: 'o/a', files: {} } } }),
    );
    assert.equal(fs.readFileSync(real, 'utf8'), '{"version":1,"sources":{}}');
  } finally {
    s.cleanup();
  }
});
