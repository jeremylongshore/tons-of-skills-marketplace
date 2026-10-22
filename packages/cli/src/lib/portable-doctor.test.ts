import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { diagnosePortableSkill } from './portable-doctor.js';
import { installPortableTree } from './portable-install.js';
import {
  PORTABLE_INSTALL_RECEIPT_FILE,
  serializePortableInstallReceipt,
} from './portable-integrity.js';

const sourcePath = 'plugins/testing/demo/skills/demo-skill';
const skill =
  '---\nname: demo-skill\ndescription: Diagnose a portable skill installation.\nallowed-tools: Read\n---\n# Demo\n';
let root: string;
let destinationRoot: string;
let destination: string;
let receipt: Awaited<ReturnType<typeof installPortableTree>>;
const git = (...args: string[]) =>
  execFileSync('git', args, {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
const diagnose = () =>
  diagnosePortableSkill({
    destination,
    sourceRepo: root,
    harness: 'claude-code',
    scope: 'project',
  });
async function commit() {
  git('add', '.');
  git('commit', '--quiet', '-m', 'test: source revision');
}
async function snapshot(directory: string): Promise<Record<string, string>> {
  const result: Record<string, string> = {};
  async function walk(relative: string) {
    const entries = await fs.readdir(path.join(directory, relative), { withFileTypes: true });
    for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
      const child = path.join(relative, entry.name);
      const file = path.join(directory, child);
      if (entry.isDirectory()) await walk(child);
      else {
        const handle = await fs.open(file, 'r');
        try {
          const opened = await handle.stat();
          result[child] = `${opened.mode}:${opened.mtimeMs}:${createHash('sha256')
            .update(await handle.readFile())
            .digest('hex')}`;
        } finally {
          await handle.close();
        }
      }
    }
  }
  await walk('');
  return result;
}

describe('read-only portable doctor', { timeout: 30_000 }, () => {
  beforeEach(async () => {
    root = await fs.realpath(await fs.mkdtemp(path.join(tmpdir(), 'ccpi-doctor-test-')));
    destinationRoot = path.join(root, 'consumer', '.claude', 'skills');
    destination = path.join(destinationRoot, 'demo-skill');
    await fs.mkdir(path.join(root, sourcePath), { recursive: true });
    await fs.writeFile(path.join(root, sourcePath, 'SKILL.md'), skill);
    await fs.writeFile(path.join(root, '.gitignore'), 'consumer/\n');
    git('init', '--quiet');
    git('config', 'user.name', 'Portable Test');
    git('config', 'user.email', 'portable@example.invalid');
    git('config', 'core.filemode', 'false');
    git('config', 'core.autocrlf', 'false');
    git('remote', 'add', 'origin', 'https://github.com/example/skills');
    await commit();
    receipt = await installPortableTree({
      sourceDirectory: path.join(root, sourcePath),
      destinationRoot,
      harness: 'claude-code',
      scope: 'project',
      registryVersion: 2,
      cliVersion: '3.0.1',
      dryRun: false,
    });
  });
  afterEach(async () => {
    vi.restoreAllMocks();
    await fs.rm(root, { recursive: true, force: true });
  });

  test('verifies bytes and source, retains quality boundary, and changes no files or Git index', async () => {
    const before = await snapshot(root);
    const result = await diagnose();
    expect(result).toMatchObject({
      integrity: 'verified',
      quality: 'not-assessed',
      source: receipt.source,
      expectedDigest: receipt.tree.digest,
      installedDigest: receipt.tree.digest,
      upstream: { state: 'current' },
    });
    expect(await diagnose()).toEqual(result);
    expect(await snapshot(root)).toEqual(before);
  });

  test('compares historical receipt bytes with local HEAD without checking out or repairing', async () => {
    await fs.writeFile(path.join(root, sourcePath, 'SKILL.md'), skill + 'New source revision.\n');
    await commit();
    const before = await snapshot(root);
    const result = await diagnose();
    expect(result.integrity).toBe('outdated');
    expect(result.upstream.commit).toBe(git('rev-parse', 'HEAD'));
    expect(result.upstream.digest).not.toBe(result.installedDigest);
    expect(await snapshot(root)).toEqual(before);
  });

  test('unrelated newer commits and dirty source checkout do not invent a byte update', async () => {
    await fs.writeFile(path.join(root, 'README.md'), 'unrelated');
    await commit();
    await fs.writeFile(path.join(root, sourcePath, 'SKILL.md'), 'uncommitted local work');
    expect(await diagnose()).toMatchObject({
      integrity: 'verified',
      upstream: { state: 'current' },
    });
  });

  test.each(['bytes', 'missing-file', 'extra-file', 'mode'])(
    'detects local %s drift separately from upstream',
    async (kind) => {
      const file = path.join(destination, 'SKILL.md');
      if (kind === 'bytes') await fs.writeFile(file, skill.replace('Demo', 'Edit'));
      if (kind === 'missing-file') await fs.unlink(file);
      if (kind === 'extra-file') await fs.writeFile(path.join(destination, 'local.txt'), 'local');
      if (kind === 'mode') {
        if (process.platform === 'win32') return;
        await fs.chmod(file, 0o755);
      }
      const before = await snapshot(root);
      expect(await diagnose()).toMatchObject({
        integrity: 'locally-modified',
        upstream: { state: 'current' },
      });
      expect(await snapshot(root)).toEqual(before);
    },
  );

  test('local modifications take precedence over an available update', async () => {
    await fs.writeFile(path.join(root, sourcePath, 'SKILL.md'), skill + 'upstream');
    await commit();
    await fs.writeFile(path.join(destination, 'SKILL.md'), skill + 'personal');
    expect(await diagnose()).toMatchObject({
      integrity: 'locally-modified',
      upstream: { state: 'outdated' },
    });
  });

  test('missing destination has explicit unavailable receipt evidence', async () => {
    await fs.rm(destination, { recursive: true });
    expect(await diagnose()).toMatchObject({
      integrity: 'missing',
      source: null,
      expectedDigest: null,
    });
    await expect(fs.lstat(destination)).rejects.toMatchObject({ code: 'ENOENT' });
  });

  test.each(['missing', 'malformed', 'noncanonical', 'wrong-scope', 'spoofed-repository'])(
    'fails closed for a %s receipt',
    async (kind) => {
      const file = path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE);
      if (kind === 'missing') await fs.unlink(file);
      if (kind === 'malformed') await fs.writeFile(file, '{');
      if (kind === 'noncanonical') await fs.appendFile(file, '\n');
      if (kind === 'wrong-scope') {
        receipt.installation.scope = 'user';
        await fs.writeFile(file, serializePortableInstallReceipt(receipt));
      }
      if (kind === 'spoofed-repository') {
        receipt.source.repository = 'https://github.com/attacker/skills';
        await fs.writeFile(file, serializePortableInstallReceipt(receipt));
      }
      expect((await diagnose()).integrity).toBe('unverifiable');
    },
  );

  test.each(['missing', 'corrupt'])('fails closed for %s retained evidence', async (kind) => {
    const file = path.join(
      destinationRoot,
      '.ccpi-evidence',
      `${receipt.evidence[0].sha256.slice(7)}.json`,
    );
    if (kind === 'missing') await fs.unlink(file);
    else await fs.appendFile(file, ' ');
    expect((await diagnose()).integrity).toBe('unverifiable');
  });

  test('does not trust a self-consistent receipt without the selected matching repository', async () => {
    git('remote', 'set-url', 'origin', 'https://github.com/another/source');
    const result = await diagnose();
    expect(result.integrity).toBe('unverifiable');
    expect(result.installedDigest).toBe(receipt.tree.digest);
    expect(result.upstream.state).toBe('unavailable');
  });

  test('rejects a valid receipt from a commit outside the selected HEAD history', async () => {
    const original = git('branch', '--show-current');
    git('checkout', '--quiet', '-b', 'other-history');
    await fs.writeFile(path.join(root, sourcePath, 'SKILL.md'), skill + 'Other branch');
    await commit();
    await fs.rm(destination, { recursive: true });
    await installPortableTree({
      sourceDirectory: path.join(root, sourcePath),
      destinationRoot,
      harness: 'claude-code',
      scope: 'project',
      registryVersion: 2,
      cliVersion: '3.0.1',
      dryRun: false,
    });
    git('checkout', '--quiet', original);
    expect((await diagnose()).integrity).toBe('unverifiable');
  });

  test('rejects a rehashed evidence report for another validation target', async () => {
    const originalFile = path.join(
      destinationRoot,
      '.ccpi-evidence',
      `${receipt.evidence[0].sha256.slice(7)}.json`,
    );
    const report = JSON.parse(await fs.readFile(originalFile, 'utf8'));
    report.result.file = 'another/SKILL.md';
    const content = JSON.stringify(report);
    const digest = createHash('sha256').update(content).digest('hex');
    receipt.evidence[0].sha256 = `sha256:${digest}`;
    receipt.evidence[0].uri = `urn:sha256:${digest}`;
    await fs.writeFile(path.join(destinationRoot, '.ccpi-evidence', `${digest}.json`), content);
    await fs.writeFile(
      path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE),
      serializePortableInstallReceipt(receipt),
    );
    expect((await diagnose()).integrity).toBe('unverifiable');
  });

  test('separates verified original bytes from a source withdrawn at local HEAD', async () => {
    await fs.rm(path.join(root, sourcePath), { recursive: true });
    await commit();
    expect(await diagnose()).toMatchObject({
      integrity: 'verified',
      upstream: { state: 'unavailable' },
    });
  });

  test('refuses symlinked installation and evidence directories without following them', async () => {
    const moved = path.join(root, 'moved');
    await fs.rename(destination, moved);
    await fs.symlink(moved, destination, 'junction');
    expect((await diagnose()).integrity).toBe('unverifiable');
    await fs.unlink(destination);
    await fs.rename(moved, destination);
    const evidence = path.join(destinationRoot, '.ccpi-evidence');
    await fs.rename(evidence, moved);
    await fs.symlink(moved, evidence, 'junction');
    expect((await diagnose()).integrity).toBe('unverifiable');
  });
});
