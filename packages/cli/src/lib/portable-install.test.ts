import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { installPortableTree } from './portable-install.js';
import { diagnosePortableSkill } from './portable-doctor.js';
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

  test('synthetic contributing-clanker source excludes private neighbors and refuses installed source', async () => {
    const canonical = 'plugins/community/contributing-clanker/skills/contribute';
    const selected = path.join(root, canonical);
    await fs.mkdir(selected, { recursive: true });
    await fs.writeFile(
      path.join(selected, 'SKILL.md'),
      skill.replace('name: demo-skill', 'name: contribute'),
    );
    git('add', '--', canonical);
    git('commit', '--quiet', '-m', 'test: canonical contributing-clanker fixture');
    const privateNames = [
      '.claude/hooks/private.json',
      'dossiers/private.md',
      'logs/private.log',
      'credentials/session.json',
      '.cache/private.txt',
      'runtime/state.json',
      'personal/home/notes.md',
      'private.env',
    ];
    const pluginDirectory = path.dirname(path.dirname(canonical));
    const privateState = privateNames.flatMap((relative) => [
      relative,
      path.posix.join(pluginDirectory, relative),
    ]);
    const marker = 'FIXTURE_ONLY_PRIVATE_STATE_1321';
    for (const relative of privateState) {
      await fs.mkdir(path.dirname(path.join(root, relative)), { recursive: true });
      await fs.writeFile(path.join(root, relative), `${marker}:${relative}`);
    }
    const before = {
      head: git('rev-parse', 'HEAD'),
      tree: git('rev-parse', 'HEAD^{tree}'),
      index: git('ls-files', '--stage'),
      status: git('status', '--porcelain', '--untracked-files=all'),
      source: await fs.readFile(path.join(selected, 'SKILL.md'), 'utf8'),
    };
    const registry = JSON.parse(
      await fs.readFile(
        new URL('../../../../config/harness-registry.json', import.meta.url),
        'utf8',
      ),
    ) as {
      schemaVersion: number;
      harnesses: { id: string; support: string; projectPath: string | null }[];
    };
    const native = registry.harnesses.filter((harness) => harness.support === 'verified-native');
    expect(native.length).toBeGreaterThan(0);
    for (const harness of native) {
      expect(harness.projectPath).not.toBeNull();
      const targetRoot = path.join(root, 'consumer', harness.projectPath!);
      const target = path.join(targetRoot, 'contribute');
      const result = await installPortableTree({
        ...options(),
        sourceDirectory: selected,
        destinationRoot: targetRoot,
        harness: harness.id,
        registryVersion: registry.schemaVersion,
      });
      expect(result.source.path).toBe(canonical);
      expect(result.tree.entries.map((entry) => entry.path)).toEqual(['SKILL.md']);
      expect((await fs.readdir(target)).sort()).toEqual(
        [PORTABLE_INSTALL_RECEIPT_FILE, 'SKILL.md'].sort(),
      );
      expect(await fs.readFile(path.join(target, 'SKILL.md'), 'utf8')).toBe(before.source);
      const savedReceipt = await fs.readFile(
        path.join(target, PORTABLE_INSTALL_RECEIPT_FILE),
        'utf8',
      );
      expect(JSON.parse(savedReceipt)).toEqual(result);
      const evidenceRoot = path.join(targetRoot, '.ccpi-evidence');
      const evidenceFiles = await fs.readdir(evidenceRoot);
      expect(evidenceFiles.sort()).toEqual(
        result.evidence.map((entry) => `${entry.sha256.slice(7)}.json`).sort(),
      );
      const evidence = await Promise.all(
        evidenceFiles.map((file) => fs.readFile(path.join(evidenceRoot, file), 'utf8')),
      );
      for (const serialized of [JSON.stringify(result), savedReceipt, ...evidence]) {
        expect(serialized).not.toContain(marker);
        expect(serialized).not.toContain(root);
        expect(serialized).not.toContain(JSON.stringify(root).slice(1, -1));
        for (const relative of privateState) expect(serialized).not.toContain(relative);
      }
      const diagnose = () =>
        diagnosePortableSkill({
          destination: target,
          sourceRepo: root,
          harness: harness.id,
          scope: 'project',
        });
      const pristineDiagnosis = await diagnose();
      expect(pristineDiagnosis.integrity).toBe('verified');
      await fs.writeFile(path.join(target, 'local-private.md'), marker);
      const driftDiagnosis = await diagnose();
      expect(driftDiagnosis.integrity).toBe('locally-modified');
      for (const diagnosis of [pristineDiagnosis, driftDiagnosis]) {
        // destination is intentionally public diagnostic context; private contents are not.
        const serialized = JSON.stringify(diagnosis);
        expect(diagnosis.destination).toBe(target);
        expect(serialized).not.toContain(marker);
        for (const relative of privateState) expect(serialized).not.toContain(relative);
      }
      await expect(
        installPortableTree({
          ...options(),
          sourceDirectory: target,
          destinationRoot: targetRoot,
          harness: harness.id,
          registryVersion: registry.schemaVersion,
        }),
      ).rejects.toThrow(/source\.path must identify/);
      const installedLink = path.join(root, 'consumer', `${harness.id}-installed-link`);
      await fs.symlink(target, installedLink, 'dir');
      await expect(
        installPortableTree({
          ...options(),
          sourceDirectory: installedLink,
          destinationRoot: targetRoot,
          harness: harness.id,
          registryVersion: registry.schemaVersion,
        }),
      ).rejects.toThrow(/real directory|symlink/i);
      expect(await fs.readFile(path.join(target, 'local-private.md'), 'utf8')).toBe(marker);
    }
    expect(git('rev-parse', 'HEAD')).toBe(before.head);
    expect(git('rev-parse', 'HEAD^{tree}')).toBe(before.tree);
    expect(git('ls-files', '--stage')).toBe(before.index);
    expect(git('status', '--porcelain', '--untracked-files=all')).toBe(before.status);
    expect(await fs.readFile(path.join(selected, 'SKILL.md'), 'utf8')).toBe(before.source);
    for (const relative of privateState) {
      expect(await fs.readFile(path.join(root, relative), 'utf8')).toBe(`${marker}:${relative}`);
    }
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
