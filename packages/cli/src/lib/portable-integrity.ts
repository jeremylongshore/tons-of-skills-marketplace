import { Buffer } from 'node:buffer';
import { execFile as execFileCallback } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstat, realpath } from 'node:fs/promises';
import path from 'node:path';
import { promisify } from 'node:util';

export const PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION = 'portable-install-receipt/v1' as const;
export const PORTABLE_TREE_FORMAT = 'portable-skill-tree/v1' as const;
export const PORTABLE_TREE_ALGORITHM = 'sha256-tree-v1' as const;
export const PORTABLE_INSTALL_RECEIPT_FILE = '.ccpi-portable-install.json' as const;

const MAX_RECEIPT_BYTES = 1024 * 1024;
const MAX_TREE_ENTRIES = 10_000;
const MAX_EVIDENCE_ENTRIES = 64;
const MAX_GIT_OUTPUT_BYTES = 64 * 1024 * 1024;
const MAX_TREE_BYTES = 64 * 1024 * 1024;
const MIN_HARNESS_REGISTRY_VERSION = 2;
const SHA256_PATTERN = /^sha256:[0-9a-f]{64}$/;
const SHA1_OBJECT_PATTERN = /^[0-9a-f]{40}$/;
const SHA256_OBJECT_PATTERN = /^[0-9a-f]{64}$/;
const SAFE_TOKEN_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._+-]{0,127}$/;
const HARNESS_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const PORTABLE_COMPONENT_PATTERN = /^[A-Za-z0-9._()+&-]+$/;
const CANONICAL_SOURCE_PATTERN =
  /^plugins\/[a-z0-9]+(?:-[a-z0-9]+)*\/[a-z0-9]+(?:-[a-z0-9]+)*\/skills\/[a-z0-9]+(?:-[a-z0-9]+)*$/;
const WINDOWS_RESERVED_PATTERN = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i;
const execFile = promisify(execFileCallback);

export type PortableGitMode = '100644' | '100755';

export type PortableTreeInput = {
  path: string;
  bytes: Uint8Array;
  mode: PortableGitMode;
};

export type PortableTreeEntry = {
  path: string;
  mode: PortableGitMode;
  size: number;
  sha256: string;
};

export type PortableTreeManifest = {
  format: typeof PORTABLE_TREE_FORMAT;
  algorithm: typeof PORTABLE_TREE_ALGORITHM;
  digest: string;
  fileCount: number;
  byteCount: number;
  entries: PortableTreeEntry[];
};

export type GitObjectId = {
  algorithm: 'sha1' | 'sha256';
  digest: string;
};

export type PortableInstallReceiptV1 = {
  schemaVersion: typeof PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION;
  source: {
    repository: string;
    commit: GitObjectId;
    tree: GitObjectId;
    path: string;
  };
  installation: {
    harness: string;
    scope: 'project' | 'user';
  };
  validation: {
    validator: { name: string; version: string };
    skillSchemaVersion: string;
    harnessRegistryVersion: number;
  };
  tree: PortableTreeManifest;
  evidence: Array<{
    kind: string;
    uri: string;
    sha256: string;
    retention: 'indefinite';
  }>;
};

export type ImmutablePortableTree = {
  repository: string;
  commit: GitObjectId;
  sourcePath: string;
  sourceTree: GitObjectId;
  manifest: PortableTreeManifest;
  files: PortableTreeInput[];
};

type HashLike = ReturnType<typeof createHash>;

function fail(message: string): never {
  throw new Error(`Portable integrity contract violation: ${message}`);
}

function record(value: unknown, label: string): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail(`${label} must be an object`);
  }
  return value as Record<string, unknown>;
}

function exactKeys(value: Record<string, unknown>, expected: string[], label: string): void {
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    fail(`${label} must contain exactly: ${wanted.join(', ')}`);
  }
}

function nonEmptyString(value: unknown, label: string, pattern?: RegExp, maxLength = 512): string {
  if (typeof value !== 'string' || value.length === 0 || value.length > maxLength) {
    fail(`${label} must be a non-empty bounded string`);
  }
  if (
    [...value].some((character) => {
      const codePoint = character.codePointAt(0) ?? 0;
      return (
        codePoint <= 31 ||
        codePoint === 127 ||
        codePoint === 0x061c ||
        codePoint === 0x200e ||
        codePoint === 0x200f ||
        (codePoint >= 0x202a && codePoint <= 0x202e) ||
        (codePoint >= 0x2066 && codePoint <= 0x2069)
      );
    })
  ) {
    fail(`${label} contains a control or bidirectional formatting character`);
  }
  if (pattern && !pattern.test(value)) fail(`${label} has an invalid format`);
  return value;
}

function safeCount(value: unknown, label: string): number {
  if (!Number.isSafeInteger(value) || (value as number) < 0) {
    fail(`${label} must be a non-negative safe integer`);
  }
  return value as number;
}

function sha256(value: Uint8Array): string {
  return `sha256:${createHash('sha256').update(value).digest('hex')}`;
}

function writeUint64(hash: HashLike, value: number): void {
  const encoded = Buffer.alloc(8);
  encoded.writeBigUInt64BE(BigInt(value));
  hash.update(encoded);
}

function writeField(hash: HashLike, value: Uint8Array): void {
  writeUint64(hash, value.byteLength);
  hash.update(value);
}

function validatePortableComponent(component: string): void {
  if (!PORTABLE_COMPONENT_PATTERN.test(component)) {
    fail(`tree path component is not portable ASCII: ${JSON.stringify(component)}`);
  }
  if (component.endsWith('.') || component.endsWith(' ')) {
    fail(`tree path component has a trailing dot or space: ${JSON.stringify(component)}`);
  }
  if (component.toLowerCase() === '.git' || WINDOWS_RESERVED_PATTERN.test(component)) {
    fail(`tree path component is reserved: ${JSON.stringify(component)}`);
  }
}

export function normalizePortablePath(input: string): string {
  const value = nonEmptyString(input, 'tree path', undefined, 4096);
  if (value.includes('\\')) fail(`tree path uses a backslash: ${JSON.stringify(value)}`);
  if (value.startsWith('/') || /^[A-Za-z]:/.test(value) || value.startsWith('//')) {
    fail(`tree path is absolute: ${JSON.stringify(value)}`);
  }
  const segments = value.split('/');
  if (segments.some((segment) => segment === '' || segment === '.' || segment === '..')) {
    fail(`tree path contains an empty, current, or parent segment: ${JSON.stringify(value)}`);
  }
  for (const segment of segments) validatePortableComponent(segment);
  const normalized = segments.map((segment) => segment.normalize('NFC')).join('/');
  if (normalized !== value) fail(`tree path is not NFC-normalized: ${JSON.stringify(value)}`);
  if (Buffer.byteLength(normalized, 'utf8') > 4096) fail('tree path exceeds 4096 UTF-8 bytes');
  if (
    segments.some(
      (segment) => segment.toLowerCase() === PORTABLE_INSTALL_RECEIPT_FILE.toLowerCase(),
    )
  ) {
    fail(`tree path uses the reserved receipt name: ${JSON.stringify(value)}`);
  }
  return normalized;
}

export function validateCanonicalSkillSourcePath(input: string): string {
  const sourcePath = normalizePortablePath(input);
  if (!CANONICAL_SOURCE_PATTERN.test(sourcePath)) {
    fail(
      'source.path must identify plugins/<category>/<plugin>/skills/<skill>; generated root skills/ and arbitrary directories are forbidden',
    );
  }
  return sourcePath;
}

function validateMode(value: unknown, label: string): PortableGitMode {
  if (value !== '100644' && value !== '100755') {
    fail(`${label} must be regular-file mode 100644 or 100755`);
  }
  return value;
}

function canonicalEntries(entries: PortableTreeEntry[]): PortableTreeEntry[] {
  if (entries.length === 0) fail('tree must contain at least SKILL.md');
  if (entries.length > MAX_TREE_ENTRIES) fail(`tree exceeds ${MAX_TREE_ENTRIES} entries`);
  const exact = new Set<string>();
  const portable = new Map<string, string>();
  const normalized = entries.map((entry, index) => {
    const entryPath = normalizePortablePath(entry.path);
    if (exact.has(entryPath)) fail(`duplicate normalized path: ${entryPath}`);
    exact.add(entryPath);
    const portabilityKey = entryPath.toLowerCase();
    const prior = portable.get(portabilityKey);
    if (prior) fail(`case-insensitive path collision: ${prior} and ${entryPath}`);
    portable.set(portabilityKey, entryPath);
    return {
      path: entryPath,
      mode: validateMode(entry.mode, `tree.entries[${index}].mode`),
      size: safeCount(entry.size, `tree.entries[${index}].size`),
      sha256: nonEmptyString(entry.sha256, `tree.entries[${index}].sha256`, SHA256_PATTERN),
    };
  });
  for (const entryPath of exact) {
    const segments = entryPath.split('/');
    for (let index = 1; index < segments.length; index += 1) {
      const prefix = segments.slice(0, index).join('/');
      if (exact.has(prefix)) fail(`file/directory prefix collision: ${prefix} and ${entryPath}`);
    }
  }
  if (!exact.has('SKILL.md')) fail('tree must contain root SKILL.md');
  return normalized.sort((left, right) =>
    Buffer.compare(Buffer.from(left.path, 'utf8'), Buffer.from(right.path, 'utf8')),
  );
}

export function digestPortableTreeEntries(entries: PortableTreeEntry[]): string {
  const ordered = canonicalEntries(entries);
  const hash = createHash('sha256');
  hash.update(Buffer.from(`${PORTABLE_TREE_FORMAT}\0${PORTABLE_TREE_ALGORITHM}\0`, 'utf8'));
  writeUint64(hash, ordered.length);
  for (const entry of ordered) {
    writeField(hash, Buffer.from(entry.path, 'utf8'));
    writeField(hash, Buffer.from(entry.mode, 'ascii'));
    writeUint64(hash, entry.size);
    hash.update(Buffer.from(entry.sha256.slice('sha256:'.length), 'hex'));
    hash.update(Uint8Array.of(0xff));
  }
  return `sha256:${hash.digest('hex')}`;
}

export function hashPortableTree(inputs: PortableTreeInput[]): PortableTreeManifest {
  if (inputs.length > MAX_TREE_ENTRIES) fail(`tree exceeds ${MAX_TREE_ENTRIES} entries`);
  const entries = inputs.map((input, index) => {
    if (!(input.bytes instanceof Uint8Array)) fail(`tree input ${index} bytes are invalid`);
    const bytes = Buffer.from(input.bytes.buffer, input.bytes.byteOffset, input.bytes.byteLength);
    return {
      path: normalizePortablePath(input.path),
      mode: validateMode(input.mode, `tree input ${index} mode`),
      size: bytes.byteLength,
      sha256: sha256(bytes),
    };
  });
  const ordered = canonicalEntries(entries);
  const byteCount = ordered.reduce((total, entry) => total + entry.size, 0);
  if (!Number.isSafeInteger(byteCount) || byteCount > MAX_TREE_BYTES) {
    fail(`tree exceeds the ${MAX_TREE_BYTES}-byte portable limit`);
  }
  return {
    format: PORTABLE_TREE_FORMAT,
    algorithm: PORTABLE_TREE_ALGORITHM,
    digest: digestPortableTreeEntries(ordered),
    fileCount: ordered.length,
    byteCount,
    entries: ordered,
  };
}

function objectId(value: unknown, label: string): GitObjectId {
  const object = record(value, label);
  exactKeys(object, ['algorithm', 'digest'], label);
  if (object.algorithm !== 'sha1' && object.algorithm !== 'sha256') {
    fail(`${label}.algorithm must be sha1 or sha256`);
  }
  const digest = nonEmptyString(object.digest, `${label}.digest`);
  const valid =
    object.algorithm === 'sha1'
      ? SHA1_OBJECT_PATTERN.test(digest)
      : SHA256_OBJECT_PATTERN.test(digest);
  if (!valid) fail(`${label}.digest does not match ${object.algorithm}`);
  return { algorithm: object.algorithm, digest };
}

function objectIdFromDigest(digest: string, label: string): GitObjectId {
  if (SHA1_OBJECT_PATTERN.test(digest)) return { algorithm: 'sha1', digest };
  if (SHA256_OBJECT_PATTERN.test(digest)) return { algorithm: 'sha256', digest };
  fail(`${label} must be a full lowercase Git SHA-1 or SHA-256 object ID`);
}

function canonicalRepository(value: unknown): string {
  const repository = nonEmptyString(value, 'source.repository');
  if (!/^[\x20-\x7e]+$/.test(repository))
    fail('source.repository must contain portable ASCII only');
  let parsed: URL;
  try {
    parsed = new URL(repository);
  } catch {
    fail('source.repository must be an absolute HTTPS URL');
  }
  const segments = parsed.pathname.split('/').filter(Boolean);
  if (
    parsed.protocol !== 'https:' ||
    parsed.username ||
    parsed.password ||
    parsed.port ||
    parsed.search ||
    parsed.hash ||
    segments.length < 2 ||
    segments.some((segment) => !/^[A-Za-z0-9._~-]+$/.test(segment)) ||
    segments.at(-1)?.toLowerCase().endsWith('.git') ||
    parsed.pathname.endsWith('/') ||
    parsed.toString() !== repository
  ) {
    fail('source.repository must be a canonical, credential-free HTTPS repository URL');
  }
  return repository;
}

function validateTree(value: unknown): PortableTreeManifest {
  const tree = record(value, 'tree');
  exactKeys(tree, ['algorithm', 'byteCount', 'digest', 'entries', 'fileCount', 'format'], 'tree');
  if (tree.format !== PORTABLE_TREE_FORMAT) fail(`tree.format must be ${PORTABLE_TREE_FORMAT}`);
  if (tree.algorithm !== PORTABLE_TREE_ALGORITHM)
    fail(`tree.algorithm must be ${PORTABLE_TREE_ALGORITHM}`);
  const digest = nonEmptyString(tree.digest, 'tree.digest', SHA256_PATTERN);
  const fileCount = safeCount(tree.fileCount, 'tree.fileCount');
  const byteCount = safeCount(tree.byteCount, 'tree.byteCount');
  if (!Array.isArray(tree.entries)) fail('tree.entries must be an array');
  const entries = tree.entries.map((value, index) => {
    const entry = record(value, `tree.entries[${index}]`);
    exactKeys(entry, ['mode', 'path', 'sha256', 'size'], `tree.entries[${index}]`);
    return {
      path: nonEmptyString(entry.path, `tree.entries[${index}].path`, undefined, 4096),
      mode: validateMode(entry.mode, `tree.entries[${index}].mode`),
      size: safeCount(entry.size, `tree.entries[${index}].size`),
      sha256: nonEmptyString(entry.sha256, `tree.entries[${index}].sha256`, SHA256_PATTERN),
    };
  });
  const ordered = canonicalEntries(entries);
  if (entries.some((entry, index) => entry.path !== ordered[index]?.path)) {
    fail('tree.entries must be sorted by canonical UTF-8 path bytes');
  }
  if (fileCount !== ordered.length) fail('tree.fileCount does not match tree.entries');
  const expectedBytes = ordered.reduce((total, entry) => total + entry.size, 0);
  if (!Number.isSafeInteger(expectedBytes)) fail('tree byte count is unsafe');
  if (expectedBytes > MAX_TREE_BYTES) {
    fail(`tree exceeds the ${MAX_TREE_BYTES}-byte portable limit`);
  }
  if (byteCount !== expectedBytes) {
    fail('tree.byteCount does not match tree.entries');
  }
  if (digest !== digestPortableTreeEntries(ordered)) {
    fail('tree.digest does not match the canonical entry manifest');
  }
  return {
    format: PORTABLE_TREE_FORMAT,
    algorithm: PORTABLE_TREE_ALGORITHM,
    digest,
    fileCount,
    byteCount,
    entries: ordered,
  };
}

export function validatePortableInstallReceipt(value: unknown): PortableInstallReceiptV1 {
  const receipt = record(value, 'receipt');
  exactKeys(
    receipt,
    ['evidence', 'installation', 'schemaVersion', 'source', 'tree', 'validation'],
    'receipt',
  );
  if (receipt.schemaVersion !== PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION) {
    fail(`schemaVersion must be ${PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION}`);
  }
  const source = record(receipt.source, 'source');
  exactKeys(source, ['commit', 'path', 'repository', 'tree'], 'source');
  const sourcePath = validateCanonicalSkillSourcePath(nonEmptyString(source.path, 'source.path'));
  const commit = objectId(source.commit, 'source.commit');
  const sourceTree = objectId(source.tree, 'source.tree');
  if (commit.algorithm !== sourceTree.algorithm)
    fail('source commit and tree object algorithms must match');

  const installation = record(receipt.installation, 'installation');
  exactKeys(installation, ['harness', 'scope'], 'installation');
  const harness = nonEmptyString(installation.harness, 'installation.harness', HARNESS_PATTERN);
  if (installation.scope !== 'project' && installation.scope !== 'user') {
    fail('installation.scope must be project or user');
  }

  const validation = record(receipt.validation, 'validation');
  exactKeys(
    validation,
    ['harnessRegistryVersion', 'skillSchemaVersion', 'validator'],
    'validation',
  );
  const validator = record(validation.validator, 'validation.validator');
  exactKeys(validator, ['name', 'version'], 'validation.validator');
  const validatorName = nonEmptyString(
    validator.name,
    'validation.validator.name',
    SAFE_TOKEN_PATTERN,
  );
  const validatorVersion = nonEmptyString(
    validator.version,
    'validation.validator.version',
    SAFE_TOKEN_PATTERN,
  );
  const skillSchemaVersion = nonEmptyString(
    validation.skillSchemaVersion,
    'validation.skillSchemaVersion',
    SAFE_TOKEN_PATTERN,
  );
  const harnessRegistryVersion = safeCount(
    validation.harnessRegistryVersion,
    'validation.harnessRegistryVersion',
  );
  if (harnessRegistryVersion < MIN_HARNESS_REGISTRY_VERSION) {
    fail(`validation.harnessRegistryVersion must be ${MIN_HARNESS_REGISTRY_VERSION} or newer`);
  }

  if (!Array.isArray(receipt.evidence) || receipt.evidence.length === 0) {
    fail('evidence must be a non-empty array');
  }
  if (receipt.evidence.length > MAX_EVIDENCE_ENTRIES)
    fail(`evidence exceeds ${MAX_EVIDENCE_ENTRIES} entries`);
  const evidence = receipt.evidence.map((value, index) => {
    const item = record(value, `evidence[${index}]`);
    exactKeys(item, ['kind', 'retention', 'sha256', 'uri'], `evidence[${index}]`);
    const uri = nonEmptyString(item.uri, `evidence[${index}].uri`, /^urn:sha256:[0-9a-f]{64}$/);
    const digest = nonEmptyString(item.sha256, `evidence[${index}].sha256`, SHA256_PATTERN);
    if (uri.slice('urn:'.length) !== digest) fail(`evidence[${index}] URI and digest must match`);
    if (item.retention !== 'indefinite') fail(`evidence[${index}].retention must be indefinite`);
    return {
      kind: nonEmptyString(item.kind, `evidence[${index}].kind`, SAFE_TOKEN_PATTERN),
      uri,
      sha256: digest,
      retention: 'indefinite' as const,
    };
  });

  return {
    schemaVersion: PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION,
    source: {
      repository: canonicalRepository(source.repository),
      commit,
      tree: sourceTree,
      path: sourcePath,
    },
    installation: { harness, scope: installation.scope },
    validation: {
      validator: { name: validatorName, version: validatorVersion },
      skillSchemaVersion,
      harnessRegistryVersion,
    },
    tree: validateTree(receipt.tree),
    evidence,
  };
}

export function serializePortableInstallReceipt(value: unknown): string {
  return JSON.stringify(validatePortableInstallReceipt(value));
}

export function parsePortableInstallReceipt(value: string | Uint8Array): PortableInstallReceiptV1 {
  const bytes = typeof value === 'string' ? Buffer.from(value, 'utf8') : Buffer.from(value);
  if (bytes.byteLength === 0 || bytes.byteLength > MAX_RECEIPT_BYTES) {
    fail(`receipt must contain 1-${MAX_RECEIPT_BYTES} UTF-8 bytes`);
  }
  let text: string;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    fail('receipt must be valid UTF-8');
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    fail('receipt must be valid JSON');
  }
  const receipt = validatePortableInstallReceipt(parsed);
  if (JSON.stringify(receipt) !== text) {
    fail('receipt must use the canonical minified encoding and contain no duplicate keys');
  }
  return receipt;
}

/** Structural validation alone is not trust. This binds every provenance field to a clean acquisition. */
export function assertReceiptMatchesAcquisition(
  value: unknown,
  acquisition: ImmutablePortableTree,
): PortableInstallReceiptV1 {
  const receipt = validatePortableInstallReceipt(value);
  if (receipt.source.repository !== acquisition.repository) {
    fail('receipt repository does not match the immutable acquisition');
  }
  if (
    receipt.source.commit.algorithm !== acquisition.commit.algorithm ||
    receipt.source.commit.digest !== acquisition.commit.digest
  ) {
    fail('receipt commit does not match the immutable acquisition');
  }
  if (
    receipt.source.tree.algorithm !== acquisition.sourceTree.algorithm ||
    receipt.source.tree.digest !== acquisition.sourceTree.digest
  ) {
    fail('receipt source tree does not match the immutable acquisition');
  }
  if (receipt.source.path !== acquisition.sourcePath) {
    fail('receipt source path does not match the immutable acquisition');
  }
  if (JSON.stringify(receipt.tree) !== JSON.stringify(acquisition.manifest)) {
    fail('receipt tree manifest does not match the immutable acquisition');
  }
  return receipt;
}

async function git(repoRoot: string, args: string[]): Promise<Buffer> {
  try {
    const result = await execFile('git', ['--no-optional-locks', ...args], {
      cwd: repoRoot,
      encoding: 'buffer',
      maxBuffer: MAX_GIT_OUTPUT_BYTES,
      windowsHide: true,
    });
    return Buffer.from(result.stdout);
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    fail(`git ${args[0] ?? 'operation'} failed: ${detail}`);
  }
}

async function gitObjectExists(repoRoot: string, spec: string): Promise<boolean> {
  const separator = spec.indexOf(':');
  // Empty ls-tree output proves absence. A Git failure must never masquerade as absence.
  return (
    (
      await git(repoRoot, [
        'ls-tree',
        '-z',
        spec.slice(0, separator),
        '--',
        spec.slice(separator + 1),
      ])
    ).length > 0
  );
}

function decodeGitText(bytes: Uint8Array, label: string): string {
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    fail(`${label} is not valid UTF-8`);
  }
}

function canonicalizeGitRemote(value: string): string {
  const scpLike = /^git@([A-Za-z0-9.-]+):(.+)$/.exec(value);
  if (scpLike) {
    const repositoryPath = scpLike[2].replace(/\.git$/i, '').replace(/\/$/, '');
    return canonicalRepository(`https://${scpLike[1]}/${repositoryPath}`);
  }

  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    fail('origin must be a canonical HTTPS or git@ SSH repository URL');
  }
  if (
    parsed.protocol !== 'https:' &&
    !(parsed.protocol === 'ssh:' && parsed.username === 'git' && !parsed.password && !parsed.port)
  ) {
    fail('origin must be a canonical HTTPS or git@ SSH repository URL');
  }
  const repositoryPath = parsed.pathname
    .replace(/^\//, '')
    .replace(/\.git$/i, '')
    .replace(/\/$/, '');
  return canonicalRepository(`https://${parsed.hostname}/${repositoryPath}`);
}

/** Resolve coordinates only; acquisition below still verifies every trust boundary. */
export async function portableSourceCoordinates(directory: string): Promise<{
  repoRoot: string;
  repository: string;
  commit: string;
  sourcePath: string;
}> {
  const requested = path.resolve(directory);
  const info = await lstat(requested);
  if (!info.isDirectory() || info.isSymbolicLink()) fail('source must be a real directory');
  const absolute = await realpath(requested);
  const repoRoot = (await git(absolute, ['rev-parse', '--show-toplevel'])).toString('utf8').trim();
  const commit = (await git(repoRoot, ['rev-parse', '--verify', 'HEAD'])).toString('ascii').trim();
  const origin = (await git(repoRoot, ['remote', 'get-url', 'origin'])).toString('utf8').trim();
  return {
    repoRoot,
    repository: canonicalizeGitRemote(origin),
    commit,
    sourcePath: path.relative(repoRoot, absolute).split(path.sep).join('/'),
  };
}

async function assertCleanCheckout(
  repoRoot: string,
  sourcePath: string,
  commit: string,
): Promise<void> {
  const head = (await git(repoRoot, ['rev-parse', '--verify', 'HEAD'])).toString('ascii').trim();
  if (head !== commit) fail('the checked-out HEAD must equal the immutable source commit');
  const status = await git(repoRoot, [
    'status',
    '--porcelain=v1',
    '-z',
    '--untracked-files=all',
    '--ignored=matching',
    '--',
    sourcePath,
  ]);
  if (status.byteLength !== 0) {
    fail('source tree contains staged, modified, deleted, untracked, or ignored state');
  }
  let current = repoRoot;
  async function refuseMirror(directory: string): Promise<void> {
    try {
      await lstat(path.join(directory, '.source.json'));
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') return;
      throw error;
    }
    fail('source is beneath a working-tree upstream/generated mirror marker');
  }
  await refuseMirror(current);
  for (const segment of sourcePath.split('/')) {
    current = path.join(current, segment);
    const details = await lstat(current).catch(() => null);
    if (!details?.isDirectory() || details.isSymbolicLink()) {
      fail(`source path ancestor is missing, not a directory, or a symlink: ${segment}`);
    }
    await refuseMirror(current);
  }
}

type PortableAcquisitionInput = {
  repoRoot: string;
  repository: string;
  commit: string;
  sourcePath: string;
};

export function readPortableTreeFromCleanCommit(input: PortableAcquisitionInput) {
  return readPortableTree(input, true);
}

/** Read committed history without changing the checkout or refreshing its index. */
export function readPortableTreeFromCommit(input: PortableAcquisitionInput) {
  return readPortableTree(input, false);
}

export async function portableRepositoryHead(repoRoot: string) {
  return {
    repository: canonicalizeGitRemote(
      (await git(repoRoot, ['remote', 'get-url', 'origin'])).toString('utf8').trim(),
    ),
    commit: (await git(repoRoot, ['rev-parse', '--verify', 'HEAD'])).toString('ascii').trim(),
  };
}

async function readPortableTree(
  input: PortableAcquisitionInput,
  cleanCheckout: boolean,
): Promise<ImmutablePortableTree> {
  const sourcePath = validateCanonicalSkillSourcePath(input.sourcePath);
  const repository = canonicalRepository(input.repository);
  const commit = objectIdFromDigest(input.commit, 'commit');
  const requestedRoot = path.resolve(input.repoRoot);
  const requestedRootDetails = await lstat(requestedRoot).catch(() => null);
  if (!requestedRootDetails?.isDirectory() || requestedRootDetails.isSymbolicLink()) {
    fail('repoRoot must be a real directory, not a symbolic link');
  }
  const resolvedRoot = await realpath(requestedRoot).catch(() => fail('repoRoot does not exist'));
  const discoveredRoot = (await git(resolvedRoot, ['rev-parse', '--show-toplevel']))
    .toString('utf8')
    .trim();
  if ((await realpath(discoveredRoot)) !== resolvedRoot)
    fail('repoRoot must be the Git worktree root');
  const origin = (await git(resolvedRoot, ['remote', 'get-url', 'origin'])).toString('utf8').trim();
  if (canonicalizeGitRemote(origin) !== repository) {
    fail('origin repository identity does not match the requested canonical repository');
  }

  const commitType = (await git(resolvedRoot, ['cat-file', '-t', commit.digest]))
    .toString('ascii')
    .trim();
  if (commitType !== 'commit') fail('commit must identify a Git commit object');
  if (cleanCheckout) await assertCleanCheckout(resolvedRoot, sourcePath, commit.digest);
  else await git(resolvedRoot, ['merge-base', '--is-ancestor', commit.digest, 'HEAD']);

  const sourceSegments = sourcePath.split('/');
  for (let index = 1; index <= sourceSegments.length; index += 1) {
    const ancestor = sourceSegments.slice(0, index).join('/');
    const ancestorType = (
      await git(resolvedRoot, ['cat-file', '-t', `${commit.digest}:${ancestor}`])
    )
      .toString('ascii')
      .trim();
    if (ancestorType !== 'tree') fail(`source ancestor is not a Git tree: ${ancestor}`);
  }
  if (await gitObjectExists(resolvedRoot, `${commit.digest}:.source.json`)) {
    fail('source is beneath a repository-level upstream/generated mirror marker');
  }
  for (let index = 1; index <= sourceSegments.length; index += 1) {
    const ancestor = sourceSegments.slice(0, index).join('/');
    if (await gitObjectExists(resolvedRoot, `${commit.digest}:${ancestor}/.source.json`)) {
      fail(`source is an upstream/generated mirror beneath ${ancestor}`);
    }
  }

  const sourceTreeDigest = (
    await git(resolvedRoot, ['rev-parse', '--verify', `${commit.digest}:${sourcePath}`])
  )
    .toString('ascii')
    .trim();
  const sourceTree = objectIdFromDigest(sourceTreeDigest, 'source tree');
  if (sourceTree.algorithm !== commit.algorithm)
    fail('Git commit and source tree algorithms differ');

  const listing = await git(resolvedRoot, [
    '-c',
    'core.quotePath=false',
    'ls-tree',
    '-r',
    '-z',
    '--full-tree',
    commit.digest,
    '--',
    `${sourcePath}/`,
  ]);
  if (listing.length === 0) fail('source tree contains no files');
  if (listing.at(-1) !== 0) fail('git ls-tree output is not NUL-terminated');
  const records = listing
    .subarray(0, listing.length - 1)
    .toString('binary')
    .split('\0');
  if (records.length > MAX_TREE_ENTRIES) fail(`tree exceeds ${MAX_TREE_ENTRIES} entries`);
  const inputs: PortableTreeInput[] = [];
  let totalBytes = 0;
  for (const rawRecord of records) {
    const recordBytes = Buffer.from(rawRecord, 'binary');
    const tab = recordBytes.indexOf(0x09);
    if (tab < 0) fail('git ls-tree emitted a malformed record');
    const metadata = recordBytes.subarray(0, tab).toString('ascii').split(' ');
    if (metadata.length !== 3) fail('git ls-tree emitted malformed metadata');
    const [mode, type, oid] = metadata;
    if ((mode !== '100644' && mode !== '100755') || type !== 'blob') {
      fail(`source contains unsupported Git entry mode/type ${mode} ${type}`);
    }
    const repositoryPath = decodeGitText(recordBytes.subarray(tab + 1), 'Git path');
    const prefix = `${sourcePath}/`;
    if (!repositoryPath.startsWith(prefix))
      fail('git ls-tree emitted a path outside the source tree');
    const relativePath = normalizePortablePath(repositoryPath.slice(prefix.length));
    if (cleanCheckout)
      try {
        await execFile('git', ['check-ignore', '--no-index', '--quiet', '--', repositoryPath], {
          cwd: resolvedRoot,
        });
        fail(`tracked source file is excluded by ignore rules: ${relativePath}`);
      } catch (error) {
        // check-ignore returns exactly 1 for a non-ignored path; every other failure refuses.
        if ((error as { code?: number }).code !== 1) throw error;
      }
    const bytes = await git(resolvedRoot, ['cat-file', 'blob', oid]);
    totalBytes += bytes.byteLength;
    if (!Number.isSafeInteger(totalBytes) || totalBytes > MAX_TREE_BYTES) {
      fail(`tree exceeds the ${MAX_TREE_BYTES}-byte portable limit`);
    }
    inputs.push({ path: relativePath, mode, bytes });
  }
  return {
    repository,
    commit,
    sourcePath,
    sourceTree,
    manifest: hashPortableTree(inputs),
    files: inputs,
  };
}
