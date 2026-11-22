import { execFileSync } from 'node:child_process';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { tmpdir } from 'node:os';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { installPortableTree } from './portable-install.js';
import { preparePortableUpdate } from './portable-update.js';
import { PORTABLE_INSTALL_RECEIPT_FILE } from './portable-integrity.js';

const skill =
  '---\nname: demo-skill\ndescription: Test bounded portable updates.\nallowed-tools: Read\n---\n# Demo\n';
let root: string;
let source: string;
let destinationRoot: string;
let destination: string;
let selected: string;
let originalReceipt: Buffer;
const git = (...args: string[]) =>
  execFileSync('git', args, { cwd: root, encoding: 'utf8', stdio: 'pipe' }).trim();
const options = () => ({
  sourceDirectory: source,
  sourceCommit: selected,
  destinationRoot,
  harness: 'claude-code',
  scope: 'project' as const,
  registryVersion: 2,
  cliVersion: '3.0.3',
});
const commit = () => {
  git('add', '.');
  git('commit', '--quiet', '-m', 'test: revision');
  return git('rev-parse', 'HEAD');
};
beforeEach(async () => {
  root = await fs.realpath(await fs.mkdtemp(path.join(tmpdir(), 'portable-update-')));
  source = path.join(root, 'plugins/testing/demo/skills/demo-skill');
  destinationRoot = path.join(root, 'consumer');
  destination = path.join(destinationRoot, 'demo-skill');
  await fs.mkdir(source, { recursive: true });
  await fs.writeFile(path.join(source, 'SKILL.md'), skill);
  await fs.writeFile(path.join(root, '.gitignore'), 'consumer/\n');
  git('init', '--quiet');
  git('config', 'user.name', 'Test');
  git('config', 'user.email', 'test@example.invalid');
  git('config', 'core.autocrlf', 'false');
  git('remote', 'add', 'origin', 'https://github.com/example/skills');
  selected = commit();
  await installPortableTree({ ...options(), dryRun: false });
  originalReceipt = await fs.readFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE));
  await fs.writeFile(path.join(source, 'SKILL.md'), skill + '\nUpdated revision\n');
  selected = commit();
});
afterEach(async () => {
  vi.restoreAllMocks();
  await fs.rm(root, { recursive: true, force: true });
});
async function noStage() {
  expect((await fs.readdir(destinationRoot)).filter((n) => n.startsWith('.demo-skill.'))).toEqual(
    [],
  );
}
test('prepares verified immutable replacement while preserving active tree and receipt', async () => {
  const result = await preparePortableUpdate(options());
  expect(result.replacement.source.commit.digest).toBe(selected);
  expect(await fs.readFile(path.join(result.stagedDestination, 'SKILL.md'), 'utf8')).toContain(
    'Updated revision',
  );
  expect(await fs.readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe(skill);
  expect(await fs.readFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE))).toEqual(
    originalReceipt,
  );
  expect(await fs.readdir(path.join(result.stagingRoot, '.ccpi-evidence'))).toHaveLength(1);
});
test('local modifications refuse update without overwriting or exporting them', async () => {
  await fs.writeFile(path.join(destination, 'SKILL.md'), 'local changes');
  await expect(preparePortableUpdate(options())).rejects.toThrow(/local changes/);
  expect(await fs.readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe('local changes');
  await noStage();
});
test('unverifiable receipt refuses preparation', async () => {
  await fs.writeFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE), '{}');
  await expect(preparePortableUpdate(options())).rejects.toThrow(/unverifiable/);
  await noStage();
});
test('invalid replacement leaves the old installation intact and removes only owned staging', async () => {
  await fs.writeFile(path.join(source, 'SKILL.md'), 'not a skill');
  selected = commit();
  await expect(preparePortableUpdate(options())).rejects.toThrow(/validation/);
  expect(await fs.readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe(skill);
  await noStage();
});
test('concurrent active edits are preserved and invalidate the prepared replacement', async () => {
  const rename = fs.rename.bind(fs);
  vi.spyOn(fs, 'rename').mockImplementation(async (from, to) => {
    await rename(from, to);
    await fs.writeFile(path.join(destination, 'SKILL.md'), 'concurrent local edit');
  });
  await expect(preparePortableUpdate(options())).rejects.toThrow(/changed while preparing/);
  expect(await fs.readFile(path.join(destination, 'SKILL.md'), 'utf8')).toBe(
    'concurrent local edit',
  );
  await noStage();
});
test('an existing installer lock is preserved and blocks preparation', async () => {
  const lock = path.join(destinationRoot, '.demo-skill.install-lock');
  await fs.mkdir(lock);
  await expect(preparePortableUpdate(options())).rejects.toMatchObject({ code: 'EEXIST' });
  expect((await fs.lstat(lock)).isDirectory()).toBe(true);
});

test('same portable content refuses a no-op and cleans its owned staging', async () => {
  const receipt = JSON.parse(originalReceipt.toString('utf8'));
  await expect(
    preparePortableUpdate({ ...options(), sourceCommit: receipt.source.commit.digest }),
  ).rejects.toThrow(/no portable content change/);
  expect(await fs.readFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE))).toEqual(
    originalReceipt,
  );
  await noStage();
});

test('symlink destination cannot redirect an update into another tree', async () => {
  const saved = path.join(root, 'preserved-original');
  await fs.rename(destination, saved);
  await fs.symlink(saved, destination, process.platform === 'win32' ? 'junction' : 'dir');
  await expect(preparePortableUpdate(options())).rejects.toThrow(/unverifiable/);
  expect(await fs.readFile(path.join(saved, 'SKILL.md'), 'utf8')).toBe(skill);
  expect((await fs.lstat(destination)).isSymbolicLink()).toBe(true);
  await noStage();
});
