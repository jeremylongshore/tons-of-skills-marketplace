/**
 * Hostile-path, race, short-write and rollback corpus for scripts/safe-fs.mjs.
 * Zero-install (node built-ins only) so it runs on Linux, macOS and Windows.
 *
 *   node --test scripts/safe-fs.test.mjs
 */

import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  NOFOLLOW_SUPPORTED,
  UnsafePathError,
  normalizeRelative,
  safeFileStatus,
  safeReadFile,
  safeReadFileIfExists,
  safeReadTree,
  safeRemoveFile,
  safeWriteFileAtomic,
  splitSafeRelative,
} from './safe-fs.mjs';

const IS_WINDOWS = process.platform === 'win32';

function sandbox() {
  const base = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'safe-fs-')));
  const root = path.join(base, 'root');
  const outside = path.join(base, 'outside');
  fs.mkdirSync(root);
  fs.mkdirSync(outside);
  fs.writeFileSync(path.join(outside, 'secret.txt'), 'SECRET');
  return { base, root, outside, cleanup: () => fs.rmSync(base, { recursive: true, force: true }) };
}

/** Make a directory link: a junction on Windows (no privilege needed), a symlink elsewhere. */
function linkDir(target, at) {
  fs.symlinkSync(target, at, IS_WINDOWS ? 'junction' : 'dir');
}

/** Make a file symlink, or skip the test where the OS forbids it (unprivileged Windows). */
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

function tempLeftovers(dir) {
  return fs.readdirSync(dir).filter((name) => name.endsWith('.tmp'));
}

// ---------------------------------------------------------------- lexical

test('lexical: traversal, absolute, drive, stream, device and odd segments are refused', () => {
  const bad = [
    '',
    '..',
    '../x',
    'a/../b',
    'a/./b',
    './a',
    'a//b',
    'a/',
    '/etc/passwd',
    '\\\\server\\share\\x',
    'C:\\Windows\\x',
    'c:x',
    'a\\..\\..\\b',
    'file.txt:stream',
    'CON',
    'nul.txt',
    'dir/COM1',
    'trailing.',
    'trailing ',
    'a\0b',
    'tab\there',
  ];
  for (const rel of bad) {
    assert.throws(() => splitSafeRelative(rel), UnsafePathError, `accepted ${JSON.stringify(rel)}`);
  }
  assert.deepEqual(splitSafeRelative('plugins/x/SKILL.md'), ['plugins', 'x', 'SKILL.md']);
  assert.deepEqual(splitSafeRelative('a\\b'), ['a', 'b']);
  assert.equal(normalizeRelative('./plugins/x/'), 'plugins/x');
  assert.throws(() => normalizeRelative('./../x'), UnsafePathError);
  assert.throws(() => splitSafeRelative(42), UnsafePathError);
});

test('root must be absolute', () => {
  assert.throws(() => safeFileStatus('relative/root', 'x'), UnsafePathError);
});

// ---------------------------------------------------------------- round trip

test('write then read round-trips bytes and mode; missing files report cleanly', () => {
  const s = sandbox();
  try {
    const bytes = Buffer.from([0, 1, 2, 255, 10, 13]);
    assert.equal(safeWriteFileAtomic(s.root, 'a/b/c.bin', bytes, { createParents: true }), true);
    const got = safeReadFile(s.root, 'a/b/c.bin');
    assert.ok(got.content.equals(bytes));
    if (!IS_WINDOWS) {
      assert.equal(got.mode & 0o777, 0o644);
      safeWriteFileAtomic(s.root, 'a/b/run.sh', '#!/bin/sh\n', { mode: 0o755 });
      assert.equal(safeReadFile(s.root, 'a/b/run.sh').mode & 0o777, 0o755);
    }
    assert.equal(safeReadFileIfExists(s.root, 'a/b/missing'), null);
    assert.equal(safeReadFileIfExists(s.root, 'no/such/dir/file'), null);
    assert.equal(safeFileStatus(s.root, 'no/such/file'), null);
    assert.deepEqual(tempLeftovers(path.join(s.root, 'a', 'b')), []);
    assert.throws(() => safeWriteFileAtomic(s.root, 'x/y', 'z'), { code: 'ENOENT' });
  } finally {
    s.cleanup();
  }
});

test('overwrite replaces content atomically and leaves no temp files', () => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'f.txt', 'one');
    safeWriteFileAtomic(s.root, 'f.txt', 'two, longer');
    assert.equal(fs.readFileSync(path.join(s.root, 'f.txt'), 'utf8'), 'two, longer');
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

test('an overwrite with no mode keeps the existing permission bits', { skip: IS_WINDOWS }, () => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'tool.sh', '#!/bin/sh\n', { mode: 0o755 });
    safeWriteFileAtomic(s.root, 'tool.sh', '#!/bin/sh\necho hi\n');
    assert.equal(fs.statSync(path.join(s.root, 'tool.sh')).mode & 0o777, 0o755);
    safeWriteFileAtomic(s.root, 'fresh.txt', 'x');
    assert.equal(fs.statSync(path.join(s.root, 'fresh.txt')).mode & 0o777, 0o644);
  } finally {
    s.cleanup();
  }
});

// ---------------------------------------------------------------- final symlinks

test('final symlink: read, status, write and remove all refuse and never touch the target', (t) => {
  const s = sandbox();
  try {
    if (!linkFileOrSkip(t, path.join(s.outside, 'secret.txt'), path.join(s.root, 'link.txt')))
      return;
    assert.throws(() => safeReadFile(s.root, 'link.txt'), UnsafePathError);
    assert.throws(() => safeFileStatus(s.root, 'link.txt'), UnsafePathError);
    assert.throws(() => safeWriteFileAtomic(s.root, 'link.txt', 'PWNED'), UnsafePathError);
    assert.throws(() => safeRemoveFile(s.root, 'link.txt'), UnsafePathError);
    assert.equal(fs.readFileSync(path.join(s.outside, 'secret.txt'), 'utf8'), 'SECRET');
    assert.ok(fs.lstatSync(path.join(s.root, 'link.txt')).isSymbolicLink());
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

test('dangling final symlink is refused, not created through', (t) => {
  const s = sandbox();
  try {
    const dest = path.join(s.outside, 'created-by-attack.txt');
    if (!linkFileOrSkip(t, dest, path.join(s.root, 'dangling'))) return;
    assert.throws(() => safeWriteFileAtomic(s.root, 'dangling', 'x'), UnsafePathError);
    assert.equal(fs.existsSync(dest), false);
  } finally {
    s.cleanup();
  }
});

// ---------------------------------------------------------------- parent links / junctions

test('symlinked or junctioned parent: every operation refuses', () => {
  const s = sandbox();
  try {
    linkDir(s.outside, path.join(s.root, 'evil'));
    assert.throws(() => safeReadFile(s.root, 'evil/secret.txt'), UnsafePathError);
    assert.throws(() => safeFileStatus(s.root, 'evil/secret.txt'), UnsafePathError);
    assert.throws(() => safeWriteFileAtomic(s.root, 'evil/new.txt', 'x'), UnsafePathError);
    assert.throws(
      () => safeWriteFileAtomic(s.root, 'evil/deep/new.txt', 'x', { createParents: true }),
      UnsafePathError,
    );
    assert.throws(() => safeRemoveFile(s.root, 'evil/secret.txt'), UnsafePathError);
    assert.throws(() => safeReadTree(s.root, 'evil'), UnsafePathError);
    assert.deepEqual(fs.readdirSync(s.outside).sort(), ['secret.txt']);
    assert.equal(fs.readFileSync(path.join(s.outside, 'secret.txt'), 'utf8'), 'SECRET');
  } finally {
    s.cleanup();
  }
});

test('a regular file used as a parent directory is refused', () => {
  const s = sandbox();
  try {
    fs.writeFileSync(path.join(s.root, 'plain'), 'x');
    assert.throws(() => safeWriteFileAtomic(s.root, 'plain/child', 'y', { createParents: true }));
    assert.throws(() => safeReadFile(s.root, 'plain/child'));
  } finally {
    s.cleanup();
  }
});

test('a symlink ABOVE the root is trusted (root is realpath-resolved)', () => {
  const s = sandbox();
  try {
    const alias = path.join(s.base, 'alias');
    linkDir(s.root, alias);
    safeWriteFileAtomic(alias, 'ok.txt', 'fine');
    assert.equal(safeReadFile(alias, 'ok.txt').content.toString(), 'fine');
  } finally {
    s.cleanup();
  }
});

// ---------------------------------------------------------------- special files

test('directory as final target is refused for read, write and remove', () => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.root, 'd'));
    assert.throws(() => safeReadFile(s.root, 'd'), UnsafePathError);
    assert.throws(() => safeWriteFileAtomic(s.root, 'd', 'x'), UnsafePathError);
    assert.throws(() => safeRemoveFile(s.root, 'd'), UnsafePathError);
    assert.ok(fs.statSync(path.join(s.root, 'd')).isDirectory());
  } finally {
    s.cleanup();
  }
});

test('FIFO is refused without hanging', { skip: IS_WINDOWS, timeout: 10_000 }, (t) => {
  const s = sandbox();
  try {
    try {
      execFileSync('mkfifo', [path.join(s.root, 'pipe')]);
    } catch {
      t.skip('mkfifo unavailable');
      return;
    }
    assert.throws(() => safeReadFile(s.root, 'pipe'), UnsafePathError);
    assert.throws(() => safeWriteFileAtomic(s.root, 'pipe', 'x'), UnsafePathError);
    assert.throws(() => safeRemoveFile(s.root, 'pipe'), UnsafePathError);
    const tree = safeReadTree(s.root);
    assert.deepEqual(tree.files, []);
    assert.equal(tree.skipped[0].reason, 'a FIFO');
  } finally {
    s.cleanup();
  }
});

test('character device is refused', { skip: IS_WINDOWS }, () => {
  assert.throws(() => safeReadFile('/dev', 'null'), UnsafePathError);
  assert.throws(() => safeWriteFileAtomic('/dev', 'null', 'x'), UnsafePathError);
});

// ---------------------------------------------------------------- short writes and rollback

test('short writes are looped until every byte lands', () => {
  const s = sandbox();
  try {
    const payload = Buffer.from('x'.repeat(10_000) + 'END');
    let calls = 0;
    const io = {
      writeSync(fd, buf, off, len, pos) {
        calls += 1;
        return fs.writeSync(fd, buf, off, Math.min(len, 7), pos);
      },
    };
    safeWriteFileAtomic(s.root, 'big.txt', payload, { io });
    assert.ok(calls > 1000, 'writes were chunked');
    assert.ok(fs.readFileSync(path.join(s.root, 'big.txt')).equals(payload));
  } finally {
    s.cleanup();
  }
});

test('a zero-progress write fails closed and rolls back', () => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'keep.txt', 'ORIGINAL');
    const io = { writeSync: () => 0 };
    assert.throws(() => safeWriteFileAtomic(s.root, 'keep.txt', 'NEW', { io }), /no progress/);
    assert.equal(fs.readFileSync(path.join(s.root, 'keep.txt'), 'utf8'), 'ORIGINAL');
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

test('a write error mid-stream leaves the original intact and no temp file', () => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'keep.txt', 'ORIGINAL');
    let n = 0;
    const io = {
      writeSync(fd, buf, off, len, pos) {
        n += 1;
        if (n === 2) {
          const error = new Error('ENOSPC: no space left on device');
          error.code = 'ENOSPC';
          throw error;
        }
        return fs.writeSync(fd, buf, off, Math.min(len, 3), pos);
      },
    };
    assert.throws(() => safeWriteFileAtomic(s.root, 'keep.txt', 'REPLACEMENT', { io }), {
      code: 'ENOSPC',
    });
    assert.equal(fs.readFileSync(path.join(s.root, 'keep.txt'), 'utf8'), 'ORIGINAL');
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

test('a failed rename rolls back: original intact, temp removed', () => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'keep.txt', 'ORIGINAL');
    const io = {
      renameSync() {
        const error = new Error('EXDEV: simulated');
        error.code = 'EXDEV';
        throw error;
      },
    };
    assert.throws(() => safeWriteFileAtomic(s.root, 'keep.txt', 'NEW', { io }), { code: 'EXDEV' });
    assert.equal(fs.readFileSync(path.join(s.root, 'keep.txt'), 'utf8'), 'ORIGINAL');
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

test('a failed fsync rolls back', () => {
  const s = sandbox();
  try {
    const io = {
      fsyncSync() {
        const error = new Error('EIO: simulated');
        error.code = 'EIO';
        throw error;
      },
    };
    assert.throws(() => safeWriteFileAtomic(s.root, 'new.txt', 'x', { io }), { code: 'EIO' });
    assert.equal(fs.existsSync(path.join(s.root, 'new.txt')), false);
    assert.deepEqual(tempLeftovers(s.root), []);
  } finally {
    s.cleanup();
  }
});

// ---------------------------------------------------------------- races

test('race: parent swapped to a link between validation and open is caught on write', () => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.root, 'dir'));
    const hooks = {
      afterValidate() {
        fs.rmSync(path.join(s.root, 'dir'), { recursive: true });
        linkDir(s.outside, path.join(s.root, 'dir'));
      },
    };
    assert.throws(
      () => safeWriteFileAtomic(s.root, 'dir/file.txt', 'PWNED', { hooks }),
      UnsafePathError,
    );
    assert.equal(fs.existsSync(path.join(s.outside, 'file.txt')), false);
    assert.deepEqual(
      fs.readdirSync(s.outside).filter((n) => n !== 'secret.txt'),
      [],
    );
  } finally {
    s.cleanup();
  }
});

test('race: target swapped for a link before commit is caught', (t) => {
  const s = sandbox();
  try {
    safeWriteFileAtomic(s.root, 'f.txt', 'ORIGINAL');
    let linked = true;
    const hooks = {
      beforeCommit(target) {
        fs.unlinkSync(target);
        try {
          fs.symlinkSync(path.join(s.outside, 'secret.txt'), target, 'file');
        } catch {
          linked = false;
          fs.writeFileSync(target, 'SWAPPED');
        }
      },
    };
    assert.throws(() => safeWriteFileAtomic(s.root, 'f.txt', 'NEW', { hooks }), UnsafePathError);
    assert.equal(fs.readFileSync(path.join(s.outside, 'secret.txt'), 'utf8'), 'SECRET');
    assert.deepEqual(tempLeftovers(s.root), []);
    if (!linked) t.diagnostic('file symlink unavailable; verified with a plain-file swap instead');
  } finally {
    s.cleanup();
  }
});

test('race: file swapped between validation and open is caught on read', () => {
  const s = sandbox();
  try {
    fs.writeFileSync(path.join(s.root, 'r.txt'), 'SAFE');
    const hooks = {
      afterValidate(target) {
        // Rename aside (not unlink) so the replacement cannot reuse the inode.
        fs.renameSync(target, `${target}.aside`);
        fs.writeFileSync(target, 'DIFFERENT INODE');
      },
    };
    assert.throws(
      () => safeReadFile(s.root, 'r.txt', { hooks }),
      /changed between validation and open/,
    );
  } finally {
    s.cleanup();
  }
});

test('race: parent swapped to a link and back is caught on read', () => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.root, 'p'));
    fs.writeFileSync(path.join(s.root, 'p', 'secret.txt'), 'INSIDE');
    const real = path.join(s.root, 'p');
    const hidden = path.join(s.root, 'p-hidden');
    const hooks = {
      afterValidate() {
        fs.renameSync(real, hidden);
        linkDir(s.outside, real);
      },
    };
    assert.throws(() => safeReadFile(s.root, 'p/secret.txt', { hooks }), UnsafePathError);
  } finally {
    s.cleanup();
  }
});

test('race: file swapped before removal is not removed', () => {
  const s = sandbox();
  try {
    fs.writeFileSync(path.join(s.root, 'orphan.txt'), 'old');
    const hooks = {
      afterValidate(target) {
        fs.renameSync(target, `${target}.aside`);
        fs.writeFileSync(target, 'someone else');
      },
    };
    assert.throws(() => safeRemoveFile(s.root, 'orphan.txt', { hooks }), UnsafePathError);
    assert.equal(fs.readFileSync(path.join(s.root, 'orphan.txt'), 'utf8'), 'someone else');
  } finally {
    s.cleanup();
  }
});

// ---------------------------------------------------------------- remove + tree

test('remove deletes only a regular file and reports absence', () => {
  const s = sandbox();
  try {
    fs.writeFileSync(path.join(s.root, 'gone.txt'), 'x');
    assert.equal(safeRemoveFile(s.root, 'gone.txt'), true);
    assert.equal(safeRemoveFile(s.root, 'gone.txt'), false);
    assert.equal(safeRemoveFile(s.root, 'no/such/dir/x'), false);
    assert.throws(() => safeRemoveFile(s.root, '../outside/secret.txt'), UnsafePathError);
    assert.equal(fs.readFileSync(path.join(s.outside, 'secret.txt'), 'utf8'), 'SECRET');
  } finally {
    s.cleanup();
  }
});

test('tree walk returns regular files, skips links and .git, never follows them', (t) => {
  const s = sandbox();
  try {
    fs.mkdirSync(path.join(s.root, 'src', 'nested'), { recursive: true });
    fs.mkdirSync(path.join(s.root, 'src', '.git'));
    fs.writeFileSync(path.join(s.root, 'src', '.git', 'HEAD'), 'ref');
    fs.writeFileSync(path.join(s.root, 'src', 'a.md'), 'A');
    fs.writeFileSync(path.join(s.root, 'src', 'nested', 'b.md'), 'B');
    linkDir(s.outside, path.join(s.root, 'src', 'escape'));
    let fileLink = false;
    try {
      fs.symlinkSync(
        path.join(s.outside, 'secret.txt'),
        path.join(s.root, 'src', 'LICENSE'),
        'file',
      );
      fileLink = true;
    } catch {
      t.diagnostic('file symlink unavailable on this runner');
    }
    const { files, skipped } = safeReadTree(s.root, 'src');
    assert.deepEqual(
      files.map((f) => [f.path, f.content.toString()]),
      [
        ['a.md', 'A'],
        ['nested/b.md', 'B'],
      ],
    );
    const skippedPaths = skipped.map((x) => x.path).sort();
    assert.deepEqual(skippedPaths, fileLink ? ['LICENSE', 'escape'] : ['escape']);
    assert.ok(!files.some((f) => f.content.toString() === 'SECRET'));
    assert.deepEqual(safeReadTree(s.root, 'missing'), { files: [], skipped: [] });
  } finally {
    s.cleanup();
  }
});

test('platform capability is reported honestly', () => {
  assert.equal(NOFOLLOW_SUPPORTED, typeof fs.constants.O_NOFOLLOW === 'number');
});
