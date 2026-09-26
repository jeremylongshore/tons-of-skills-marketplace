/**
 * Contained, fail-closed filesystem I/O for privileged automation.
 *
 * Every path is addressed as (root, relative path). The root is trusted: it
 * is resolved once with realpath, so a symlink ABOVE the root (for example a
 * home directory mounted through a link) is fine. Everything BELOW the root
 * is untrusted: an upstream repository or a hand-edited manifest can plant a
 * symlink, a junction, a FIFO or a device where a regular file is expected,
 * or swap a directory for a link while we work.
 *
 * Guarantees, on every platform:
 *   - Lexical: relative paths only; no `..`, `.`, empty segments, drive
 *     letters, colons (Windows streams), NUL bytes, trailing dots or spaces,
 *     or Windows device names. Backslash is a separator everywhere.
 *   - Structural: every existing component under the root is checked with
 *     lstat. A symbolic link or junction anywhere, a non-directory parent, or
 *     a final entry that is not a regular file is refused.
 *   - Identity: a descriptor is opened only after the walk, then its fstat
 *     identity (device + inode) must equal the path's lstat identity both
 *     before and after the open. A parent swapped to a link and back between
 *     the walk and the open is therefore detected. Where the platform reports
 *     no inode, the operation fails closed.
 *   - No-follow: O_NOFOLLOW is added where the platform defines it, and
 *     O_NONBLOCK on reads so a FIFO can never hang the process.
 *   - Writes: bytes go to an exclusive (O_EXCL) sibling temp file, written in
 *     a loop that tolerates short writes, fsynced, chmodded through the
 *     descriptor, re-verified, then renamed over the target. Readers never see
 *     partial content, and any failure removes the temp file and leaves the
 *     original untouched.
 *
 * Node exposes no openat/unlinkat, so a removal is pathname-based. It is
 * bracketed by a fresh walk and an identity check immediately before unlink.
 *
 * Dependency-free on purpose: it is imported by zero-install unit workflows.
 */

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const C = fs.constants;
const IS_WINDOWS = process.platform === 'win32';
const CASE_INSENSITIVE = IS_WINDOWS || process.platform === 'darwin';
const O_NOFOLLOW = typeof C.O_NOFOLLOW === 'number' ? C.O_NOFOLLOW : 0;
const O_NONBLOCK = typeof C.O_NONBLOCK === 'number' ? C.O_NONBLOCK : 0;
const O_DIRECTORY = typeof C.O_DIRECTORY === 'number' ? C.O_DIRECTORY : 0;

/** True where the kernel refuses to follow a final symlink on open. */
export const NOFOLLOW_SUPPORTED = O_NOFOLLOW !== 0;

const WINDOWS_DEVICE = /^(con|prn|aux|nul|com[0-9]|lpt[0-9]|conin\$|conout\$)(\.[^.]*)?$/i;

export class UnsafePathError extends Error {
  constructor(message, relPath) {
    super(relPath === undefined ? message : `${message}: ${relPath}`);
    this.name = 'UnsafePathError';
    this.code = 'EUNSAFEPATH';
    this.relPath = relPath;
  }
}

/**
 * Split a relative path into validated segments or throw UnsafePathError.
 * Accepts `/` and `\` as separators on every platform so a path means the
 * same thing on Linux, macOS and Windows.
 */
export function splitSafeRelative(relPath) {
  if (typeof relPath !== 'string' || relPath.length === 0) {
    throw new UnsafePathError('path must be a non-empty string', String(relPath));
  }
  if (relPath.includes('\0')) throw new UnsafePathError('path contains a NUL byte', relPath);
  if (/^[\\/]/.test(relPath) || /^[A-Za-z]:/.test(relPath)) {
    throw new UnsafePathError('path must be relative', relPath);
  }
  const segments = relPath.split(/[\\/]/);
  for (const seg of segments) {
    if (seg === '' || seg === '.' || seg === '..') {
      throw new UnsafePathError('path has an empty, "." or ".." segment', relPath);
    }
    if (seg.includes(':')) throw new UnsafePathError('path segment contains ":"', relPath);
    if (/[. ]$/.test(seg)) {
      throw new UnsafePathError('path segment ends in a dot or space', relPath);
    }
    if (WINDOWS_DEVICE.test(seg)) {
      throw new UnsafePathError('path segment is a reserved device name', relPath);
    }
    // eslint-disable-next-line no-control-regex
    if (/[\x00-\x1f]/.test(seg)) throw new UnsafePathError('path has a control character', relPath);
  }
  return segments;
}

/** Normalize a trusted-ish relative prefix such as `./plugins/x/` then validate it. */
export function normalizeRelative(relPath) {
  const trimmed = String(relPath ?? '')
    .replace(/^(\.[\\/])+/, '')
    .replace(/[\\/]+$/, '');
  return splitSafeRelative(trimmed).join('/');
}

function realRoot(root) {
  if (typeof root !== 'string' || !path.isAbsolute(root)) {
    throw new UnsafePathError('root must be an absolute path', String(root));
  }
  const real = fs.realpathSync(root);
  const st = fs.lstatSync(real);
  if (!st.isDirectory()) throw new UnsafePathError('root is not a directory', root);
  return real;
}

function samePath(a, b) {
  return CASE_INSENSITIVE ? a.toLowerCase() === b.toLowerCase() : a === b;
}

function lstatOrNull(p) {
  try {
    return fs.lstatSync(p, { bigint: true });
  } catch (error) {
    if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return null;
    throw error;
  }
}

function assertIdentityAvailable(st, relPath) {
  if (st.ino === 0n && st.dev === 0n) {
    throw new UnsafePathError('filesystem reports no file identity; refusing', relPath);
  }
}

function sameIdentity(a, b) {
  return a.dev === b.dev && a.ino === b.ino;
}

function describeKind(st) {
  if (st.isSymbolicLink()) return 'a symbolic link or junction';
  if (st.isDirectory()) return 'a directory';
  if (st.isFIFO()) return 'a FIFO';
  if (st.isCharacterDevice() || st.isBlockDevice()) return 'a device';
  if (st.isSocket()) return 'a socket';
  return 'not a regular file';
}

/**
 * Walk every parent component of `segments` under `rootReal`. Each must be a
 * real directory (never a link). With `create`, missing directories are made
 * one level at a time and re-checked. Returns absolute parent + final paths.
 */
function walkParents(rootReal, segments, relPath, { create = false } = {}) {
  let current = rootReal;
  for (let i = 0; i < segments.length - 1; i += 1) {
    current = path.join(current, segments[i]);
    let st = lstatOrNull(current);
    if (!st && create) {
      try {
        fs.mkdirSync(current, { mode: 0o755 });
      } catch (error) {
        if (error.code !== 'EEXIST') throw error;
      }
      st = lstatOrNull(current);
    }
    if (!st) {
      const error = new Error(`ENOENT: parent directory missing: ${relPath}`);
      error.code = 'ENOENT';
      throw error;
    }
    if (st.isSymbolicLink() || !st.isDirectory()) {
      throw new UnsafePathError(
        `parent "${segments.slice(0, i + 1).join('/')}" is ${describeKind(st)}`,
        relPath,
      );
    }
  }
  // Belt and braces for reparse points Node does not surface as links.
  if (segments.length > 1 && !samePath(fs.realpathSync(current), current)) {
    throw new UnsafePathError('parent directory resolves elsewhere', relPath);
  }
  return { parent: current, target: path.join(current, segments[segments.length - 1]) };
}

/** lstat the final entry: null when absent, bigint Stats when a regular file, else throw. */
function lstatRegularOrNull(target, relPath) {
  const st = lstatOrNull(target);
  if (!st) return null;
  if (!st.isFile() || st.isSymbolicLink()) {
    throw new UnsafePathError(`target is ${describeKind(st)}`, relPath);
  }
  assertIdentityAvailable(st, relPath);
  return st;
}

function resolve(root, relPath, opts) {
  const segments = splitSafeRelative(relPath);
  const rootReal = realRoot(root);
  const { parent, target } = walkParents(rootReal, segments, relPath, opts);
  return { rootReal, segments, parent, target };
}

/**
 * Return { size, mode } for a regular file, null when absent. Throws for a
 * link, directory or special file anywhere on the path.
 */
export function safeFileStatus(root, relPath) {
  let resolved;
  try {
    resolved = resolve(root, relPath);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
  const st = lstatRegularOrNull(resolved.target, relPath);
  return st ? { size: Number(st.size), mode: Number(st.mode) } : null;
}

/**
 * Read a regular file under root. Returns { content: Buffer, mode: number }.
 * Throws ENOENT when absent (use safeReadFileIfExists for optional reads).
 */
export function safeReadFile(root, relPath, { maxBytes = 64 * 1024 * 1024, hooks = {} } = {}) {
  const { rootReal, segments, target } = resolve(root, relPath);
  const before = lstatRegularOrNull(target, relPath);
  if (!before) {
    const error = new Error(`ENOENT: no such file: ${relPath}`);
    error.code = 'ENOENT';
    throw error;
  }
  hooks.afterValidate?.(target);
  const fd = fs.openSync(target, C.O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
  try {
    const opened = fs.fstatSync(fd, { bigint: true });
    if (!opened.isFile())
      throw new UnsafePathError(`opened descriptor is ${describeKind(opened)}`, relPath);
    if (!sameIdentity(opened, before)) {
      throw new UnsafePathError('file changed between validation and open', relPath);
    }
    if (opened.size > BigInt(maxBytes))
      throw new UnsafePathError('file exceeds the size limit', relPath);
    const chunks = [];
    let total = 0;
    const buf = Buffer.allocUnsafe(64 * 1024);
    for (;;) {
      const n = fs.readSync(fd, buf, 0, buf.length, null);
      if (n === 0) break;
      total += n;
      if (total > maxBytes) throw new UnsafePathError('file exceeds the size limit', relPath);
      chunks.push(Buffer.from(buf.subarray(0, n)));
    }
    // Re-walk after the read: the path must still name the inode we read.
    const again = walkParents(rootReal, segments, relPath);
    const after = lstatRegularOrNull(again.target, relPath);
    if (!after || !sameIdentity(after, opened)) {
      throw new UnsafePathError('file changed during read', relPath);
    }
    return { content: Buffer.concat(chunks, total), mode: Number(opened.mode) };
  } finally {
    fs.closeSync(fd);
  }
}

/** safeReadFile, but null when the file (or a parent directory) is absent. */
export function safeReadFileIfExists(root, relPath, options) {
  try {
    return safeReadFile(root, relPath, options);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

function tempName(base) {
  const tag = `${process.pid}.${crypto.randomBytes(6).toString('hex')}`;
  const room = 200 - tag.length;
  return `.${base.slice(0, Math.max(1, room))}.${tag}.tmp`;
}

function fsyncDirectory(dir, io) {
  if (IS_WINDOWS) return;
  let fd;
  try {
    fd = io.openSync(dir, C.O_RDONLY | O_DIRECTORY | O_NOFOLLOW);
    io.fsyncSync(fd);
  } catch (error) {
    if (!['EINVAL', 'ENOTSUP', 'EPERM', 'EISDIR', 'EBADF'].includes(error.code)) throw error;
  } finally {
    if (fd !== undefined) fs.closeSync(fd);
  }
}

/**
 * Atomically replace (or create) a regular file under root.
 *
 * options.mode          final permission bits (default: keep the existing file's bits,
 *                       else 0o644; ignored on Windows)
 * options.createParents create missing parent directories (never through links)
 * options.io            fs-like overrides for tests (writeSync, renameSync, fsyncSync, openSync)
 * options.hooks         test hooks: afterValidate(targetPath), beforeCommit(targetPath)
 */
export function safeWriteFileAtomic(root, relPath, data, options = {}) {
  const { createParents = false, hooks = {} } = options;
  const io = { ...fs, ...(options.io ?? {}) };
  const buffer = Buffer.isBuffer(data) ? data : Buffer.from(String(data), 'utf8');
  const { rootReal, segments, parent, target } = resolve(root, relPath, { create: createParents });
  const existing = lstatRegularOrNull(target, relPath);
  const mode = options.mode ?? (existing ? Number(existing.mode) & 0o777 : 0o644);

  const tmp = path.join(parent, tempName(segments[segments.length - 1]));
  hooks.afterValidate?.(target);
  let fd = io.openSync(tmp, C.O_WRONLY | C.O_CREAT | C.O_EXCL | O_NOFOLLOW, mode);
  let tmpIdentity = null;
  let committed = false;
  try {
    tmpIdentity = fs.fstatSync(fd, { bigint: true });
    if (!tmpIdentity.isFile())
      throw new UnsafePathError('temp descriptor is not a regular file', relPath);
    assertIdentityAvailable(tmpIdentity, relPath);

    let offset = 0;
    while (offset < buffer.length) {
      const written = io.writeSync(fd, buffer, offset, buffer.length - offset, null);
      if (!Number.isInteger(written) || written <= 0) {
        throw new Error(`write made no progress at byte ${offset} of ${buffer.length}: ${relPath}`);
      }
      offset += written;
    }
    if (!IS_WINDOWS) fs.fchmodSync(fd, mode);
    io.fsyncSync(fd);
    fs.closeSync(fd);
    fd = undefined;

    hooks.beforeCommit?.(target);
    // Re-verify the whole path right before the rename.
    const again = walkParents(rootReal, segments, relPath);
    const tmpNow = lstatOrNull(path.join(again.parent, path.basename(tmp)));
    if (!tmpNow || tmpNow.isSymbolicLink() || !sameIdentity(tmpNow, tmpIdentity)) {
      throw new UnsafePathError('temp file changed before commit', relPath);
    }
    const targetNow = lstatRegularOrNull(again.target, relPath);
    if (existing ? !targetNow || !sameIdentity(targetNow, existing) : targetNow) {
      throw new UnsafePathError('target changed while writing', relPath);
    }

    io.renameSync(tmp, target);
    committed = true;
    const landed = lstatOrNull(target);
    if (!landed || !sameIdentity(landed, tmpIdentity)) {
      throw new UnsafePathError('target does not hold the written file after rename', relPath);
    }
    fsyncDirectory(parent, io);
    return true;
  } catch (error) {
    if (fd !== undefined) {
      try {
        fs.closeSync(fd);
      } catch {
        // already closed
      }
    }
    if (!committed && tmpIdentity) {
      const leftover = lstatOrNull(tmp);
      if (leftover && !leftover.isSymbolicLink() && sameIdentity(leftover, tmpIdentity)) {
        try {
          fs.unlinkSync(tmp);
        } catch {
          // best effort; the identity check above means we only remove our own file
        }
      }
    }
    throw error;
  }
}

/**
 * Remove a regular file under root. Returns false when it is already absent.
 * Refuses (throws) for a link, directory or special file, or a path whose
 * parents are not real directories.
 */
export function safeRemoveFile(root, relPath, { hooks = {} } = {}) {
  let resolved;
  try {
    resolved = resolve(root, relPath);
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
  const before = lstatRegularOrNull(resolved.target, relPath);
  if (!before) return false;
  hooks.afterValidate?.(resolved.target);
  const again = walkParents(resolved.rootReal, resolved.segments, relPath);
  const now = lstatRegularOrNull(again.target, relPath);
  if (!now || !sameIdentity(now, before)) {
    throw new UnsafePathError('file changed before removal', relPath);
  }
  fs.unlinkSync(again.target);
  return true;
}

/**
 * Walk a directory tree under root and return every regular file as
 * { path, content, mode } relative to `relDir` ('' for the root itself).
 * Links, junctions and special files are never followed or read; they are
 * returned in `skipped` with a reason so the caller can report them.
 */
export function safeReadTree(root, relDir = '', { exclude = ['.git'], maxBytes } = {}) {
  const files = [];
  const skipped = [];
  const rootReal = realRoot(root);
  const startSegments = relDir ? splitSafeRelative(relDir) : [];
  const startPath = path.join(rootReal, ...startSegments);
  if (startSegments.length) {
    const { target } = walkParents(rootReal, startSegments, relDir);
    const st = lstatOrNull(target);
    if (!st) return { files, skipped };
    if (st.isSymbolicLink() || !st.isDirectory()) {
      throw new UnsafePathError(`directory is ${describeKind(st)}`, relDir);
    }
    if (!samePath(fs.realpathSync(target), target)) {
      throw new UnsafePathError('directory resolves elsewhere', relDir);
    }
  }

  const visit = (absDir, relPrefix, identity) => {
    const entries = fs.readdirSync(absDir);
    const now = lstatOrNull(absDir);
    if (
      !now ||
      now.isSymbolicLink() ||
      !now.isDirectory() ||
      (identity && !sameIdentity(now, identity))
    ) {
      throw new UnsafePathError('directory changed during walk', relPrefix || '.');
    }
    for (const name of entries.sort()) {
      if (exclude.includes(name)) continue;
      const rel = relPrefix ? `${relPrefix}/${name}` : name;
      try {
        splitSafeRelative(rel);
      } catch (error) {
        skipped.push({ path: rel, reason: error.message });
        continue;
      }
      const abs = path.join(absDir, name);
      const st = lstatOrNull(abs);
      if (!st) continue;
      if (st.isSymbolicLink()) {
        skipped.push({ path: rel, reason: 'symbolic link or junction (not followed)' });
      } else if (st.isDirectory()) {
        visit(abs, rel, st);
      } else if (st.isFile()) {
        const relFromRoot = [...startSegments, ...rel.split('/')].join('/');
        const { content, mode } = safeReadFile(rootReal, relFromRoot, { maxBytes });
        files.push({ path: rel, content, mode });
      } else {
        skipped.push({ path: rel, reason: describeKind(st) });
      }
    }
  };
  visit(startPath, '', startSegments.length ? lstatOrNull(startPath) : null);
  return { files, skipped };
}
