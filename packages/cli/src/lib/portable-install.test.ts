import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { installPortableTree } from './portable-install.js';
import {
  hashPortableTree,
  parsePortableInstallReceipt,
  PORTABLE_INSTALL_RECEIPT_FILE,
} from './portable-integrity.js';

const sourcePath = 'plugins/testing/demo-plugin/skills/demo-skill';
const skill =
  '---\nname: demo-skill\ndescription: Validate a deterministic portable installation fixture.\nallowed-tools: Read\nversion: 1.0.0\nauthor: Test\nlicense: MIT\ncompatibility: Node 22\ntags: [testing]\n---\n# Demo\n';
let root: string;
let source: string;
let destinationRoot: string;
let destination: string;
function git(...args: string[]): string {
  return execFileSync('git', args, {
    cwd: root,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}
function options(dryRun = false) {
  return {
    sourceDirectory: source,
    destinationRoot,
    harness: 'claude-code',
    scope: 'project' as const,
    registryVersion: 2,
    cliVersion: '3.0.0',
    dryRun,
  };
}
async function commit() {
  git('add', '.');
  git('update-index', '--chmod=+x', '--', `${sourcePath}/scripts/run.sh`);
  git('commit', '--quiet', '-m', 'test: portable fixture');
}
async function assertNoPartialInstall() {
  await expect(fs.lstat(destination)).rejects.toMatchObject({ code: 'ENOENT' });
  const names = await fs.readdir(destinationRoot).catch(() => []);
  expect(names.filter((name) => name.startsWith('.demo-skill.'))).toEqual([]);
}

describe('atomic portable installation', { timeout: 30_000 }, () => {
  beforeEach(async () => {
    // macOS exposes its temp directory through /var -> /private/var.
    root = await fs.realpath(await fs.mkdtemp(path.join(tmpdir(), 'ccpi-install-test-')));
    source = path.join(root, sourcePath);
    destinationRoot = path.join(root, 'consumer', '.claude', 'skills');
    destination = path.join(destinationRoot, 'demo-skill');
    await fs.mkdir(path.join(source, 'scripts'), { recursive: true });
    await fs.writeFile(path.join(source, 'SKILL.md'), skill);
    await fs.writeFile(path.join(source, 'scripts', 'run.sh'), '#!/bin/sh\nprintf fixture\n');
    await fs.chmod(path.join(source, 'scripts', 'run.sh'), 0o755);
    await fs.writeFile(path.join(root, '.gitignore'), '*.env\nnode_modules/\nconsumer/\n');
    git('init', '--quiet');
    git('config', 'user.name', 'Portable Test');
    git('config', 'user.email', 'portable@example.invalid');
    git('config', 'core.filemode', 'false');
    git('config', 'core.autocrlf', 'false');
    git('remote', 'add', 'origin', 'https://github.com/example/skills');
    await commit();
  });
  afterEach(async () => {
    vi.restoreAllMocks();
    await fs.rm(root, { recursive: true, force: true });
  });

  test('receipt binds installed bytes, executable modes, immutable source, and retained validation evidence', async () => {
    const receipt = await installPortableTree(options());
    expect(
      parsePortableInstallReceipt(
        await fs.readFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE)),
      ),
    ).toEqual(receipt);
    expect(receipt.source.commit.digest).toBe(git('rev-parse', 'HEAD'));
    expect(receipt.source.path).toBe(sourcePath);
    expect(receipt.source.repository).toBe('https://github.com/example/skills');
    const installed = await Promise.all(
      receipt.tree.entries.map(async (entry) => ({
        path: entry.path,
        bytes: await fs.readFile(path.join(destination, entry.path)),
        mode:
          process.platform === 'win32'
            ? entry.mode
            : (await fs.stat(path.join(destination, entry.path))).mode & 0o111
              ? ('100755' as const)
              : ('100644' as const),
      })),
    );
    expect(hashPortableTree(installed)).toEqual(receipt.tree);
    const digest = receipt.evidence[0].sha256.slice('sha256:'.length);
    const evidence = await fs.readFile(
      path.join(destinationRoot, '.ccpi-evidence', `${digest}.json`),
    );
    expect(createHash('sha256').update(evidence).digest('hex')).toBe(digest);
    expect(evidence.toString()).not.toContain(root);
    expect(JSON.parse(evidence.toString()).result.errors).toEqual([]);
    expect(receipt.validation.validator.name).toBe('ccpi-compatibility-validator');
    expect(await fs.readdir(destinationRoot)).toEqual(['.ccpi-evidence', 'demo-skill']);
  });

  test('dry run validates fully without creating harness paths', async () => {
    const result = await installPortableTree(options(true));
    expect(result.tree.fileCount).toBe(2);
    await expect(fs.lstat(destinationRoot)).rejects.toMatchObject({ code: 'ENOENT' });
  });

  test.each(['modified', 'ignored', 'untracked', 'invalid', 'private', 'symlink', 'mirror'])(
    'refuses %s source state without publishing',
    async (state) => {
      if (state === 'modified')
        await fs.writeFile(path.join(source, 'SKILL.md'), `${skill}changed`);
      if (state === 'ignored')
        await fs.writeFile(path.join(source, 'token.env'), 'not-a-real-secret');
      if (state === 'untracked') await fs.writeFile(path.join(source, 'extra.txt'), 'extra');
      if (state === 'invalid') {
        await fs.writeFile(path.join(source, 'SKILL.md'), 'not frontmatter');
        await commit();
      }
      if (state === 'private') {
        await fs.writeFile(path.join(source, 'scripts', 'credentials.json'), '{}');
        await commit();
      }
      if (state === 'symlink') {
        const linkedPath = `${sourcePath}/scripts/link`;
        await fs.writeFile(path.join(root, linkedPath), '../../../../../../outside');
        const blob = git('hash-object', '-w', '--', linkedPath);
        git('update-index', '--add', '--cacheinfo', `120000,${blob},${linkedPath}`);
        git('config', 'core.symlinks', 'false');
        git('commit', '--quiet', '-m', 'test: portable Git symlink');
      }
      if (state === 'mirror') {
        await fs.writeFile(path.join(root, 'plugins/testing/demo-plugin/.source.json'), '{}');
        await commit();
      }
      await expect(installPortableTree(options())).rejects.toThrow();
      await assertNoPartialInstall();
    },
  );

  test.each(['directory', 'file', 'symlink'])(
    'refuses an existing %s destination',
    async (kind) => {
      await fs.mkdir(destinationRoot, { recursive: true });
      if (kind === 'directory') await fs.mkdir(destination);
      if (kind === 'file') await fs.writeFile(destination, 'user data');
      if (kind === 'symlink') await fs.symlink(source, destination, 'junction');
      await expect(installPortableTree(options())).rejects.toThrow(/overwrite/);
      expect(await fs.lstat(destination)).toBeDefined();
    },
  );

  test('refuses symlinked destination parents', async () => {
    const outside = path.join(root, 'outside');
    await fs.mkdir(outside);
    await fs.mkdir(path.dirname(destinationRoot), { recursive: true });
    await fs.symlink(outside, destinationRoot, 'junction');
    await expect(installPortableTree(options())).rejects.toThrow(/real directories/);
    await expect(installPortableTree(options(true))).rejects.toThrow(/real directories/);
    expect(await fs.readdir(outside)).toEqual([]);
  });

  test('refuses tracked ignored files and untracked ancestor provenance markers', async () => {
    await fs.writeFile(path.join(root, '.gitignore'), '*.env\nREADME.md\nconsumer/\n');
    await fs.writeFile(path.join(source, 'README.md'), 'ignored despite being tracked');
    git('add', '-f', `${sourcePath}/README.md`);
    await commit();
    await expect(installPortableTree(options())).rejects.toThrow(/excluded by ignore rules/);
    await assertNoPartialInstall();
    await fs.rm(path.join(source, 'README.md'));
    await commit();
    await fs.writeFile(path.join(root, 'plugins/testing/.source.json'), '{}');
    await expect(installPortableTree(options())).rejects.toThrow(/mirror marker/);
    await assertNoPartialInstall();
  });

  test('rejects receipt corruption and a pre-existing corrupt evidence blob', async () => {
    const write = fs.writeFile.bind(fs);
    vi.spyOn(fs, 'writeFile').mockImplementation(async (file, ...args) => {
      const result = await write(file, ...args);
      if (String(file).endsWith(PORTABLE_INSTALL_RECEIPT_FILE))
        await write(file, Buffer.alloc((await fs.readFile(file)).length, 32));
      return result;
    });
    await expect(installPortableTree(options())).rejects.toThrow(/receipt/);
    await assertNoPartialInstall();
    vi.restoreAllMocks();
    const receipt = await installPortableTree(options(true));
    const evidenceRoot = path.join(destinationRoot, '.ccpi-evidence');
    await fs.mkdir(evidenceRoot, { recursive: true });
    await fs.writeFile(
      path.join(evidenceRoot, `${receipt.evidence[0].sha256.slice(7)}.json`),
      'corrupted',
    );
    await expect(installPortableTree(options())).rejects.toThrow(/changed identity or content/);
    await assertNoPartialInstall();
  });

  test.each(['staged file', 'evidence'])(
    'refuses %s replacement after opening its verification descriptor',
    async (phase) => {
      const open = fs.open.bind(fs);
      let replaced = false;
      vi.spyOn(fs, 'open').mockImplementation(async (file, ...args) => {
        const handle = await open(file, ...args);
        const target = String(file);
        if (
          !replaced &&
          (phase === 'evidence'
            ? target.includes('.ccpi-evidence')
            : target.includes('.install-') && path.basename(target) === 'run.sh')
        ) {
          replaced = true;
          const bytes = await fs.readFile(file);
          await fs.rename(file, `${target}.previous`);
          await fs.writeFile(file, bytes);
        }
        return handle;
      });
      await expect(installPortableTree(options())).rejects.toThrow(/changed identity/);
      expect(replaced).toBe(true);
      await assertNoPartialInstall();
    },
  );

  test.each(['copy', 'receipt', 'evidence', 'rename'])(
    'cleans staging after %s failure',
    async (phase) => {
      const write = fs.writeFile.bind(fs);
      if (phase === 'rename')
        vi.spyOn(fs, 'rename').mockRejectedValueOnce(new Error('injected rename failure'));
      else
        vi.spyOn(fs, 'writeFile').mockImplementation(async (file, ...args) => {
          const name = String(file);
          if (
            (phase === 'copy' && path.basename(name) === 'SKILL.md') ||
            (phase === 'receipt' && name.endsWith(PORTABLE_INSTALL_RECEIPT_FILE)) ||
            (phase === 'evidence' && name.includes('.ccpi-evidence'))
          )
            throw new Error(`injected ${phase} failure`);
          return write(file, ...args);
        });
      await expect(installPortableTree(options())).rejects.toThrow(/injected/);
      await assertNoPartialInstall();
    },
  );

  test('rejects staged byte corruption and source edits during staging', async () => {
    const write = fs.writeFile.bind(fs);
    vi.spyOn(fs, 'writeFile').mockImplementation(async (file, ...args) => {
      const result = await write(file, ...args);
      if (String(file).endsWith(path.join('scripts', 'run.sh'))) await write(file, 'corrupted');
      return result;
    });
    await expect(installPortableTree(options())).rejects.toThrow(/source digest/);
    await assertNoPartialInstall();
    vi.restoreAllMocks();
    vi.spyOn(fs, 'writeFile').mockImplementation(async (file, ...args) => {
      const result = await write(file, ...args);
      if (String(file).includes('.install-') && path.basename(String(file)) === 'SKILL.md') {
        await write(path.join(source, 'SKILL.md'), `${skill}changed during staging`);
      }
      return result;
    });
    await expect(installPortableTree(options())).rejects.toThrow(/modified/);
    await assertNoPartialInstall();
  });

  test('concurrent installs publish once without removing the other installer lock', async () => {
    const results = await Promise.allSettled([
      installPortableTree(options()),
      installPortableTree(options()),
    ]);
    expect(results.filter((result) => result.status === 'fulfilled')).toHaveLength(1);
    expect(results.filter((result) => result.status === 'rejected')).toHaveLength(1);
    expect(await fs.readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe(skill);
    expect(
      (await fs.readdir(destinationRoot)).filter((name) => name.includes('.install-')),
    ).toEqual([]);
  });

  test('refuses a destination created while staging and preserves its user files', async () => {
    const chmod = fs.chmod.bind(fs);
    vi.spyOn(fs, 'chmod').mockImplementation(async (file, mode) => {
      if (
        path.dirname(String(file)) === destinationRoot &&
        path.basename(String(file)).startsWith('.demo-skill.install-')
      ) {
        await fs.mkdir(destination);
        await fs.writeFile(path.join(destination, 'user.txt'), 'preserve me');
      }
      return chmod(file, mode);
    });
    await expect(installPortableTree(options())).rejects.toThrow(/overwrite/);
    expect(await fs.readFile(path.join(destination, 'user.txt'), 'utf8')).toBe('preserve me');
    expect(
      (await fs.readdir(destinationRoot)).filter((name) => name.includes('.install-')),
    ).toEqual([]);
  });
});
