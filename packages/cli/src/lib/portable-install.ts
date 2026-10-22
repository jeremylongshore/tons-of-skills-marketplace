import { createHash } from 'node:crypto';
import { constants, promises as fs } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import {
  assertReceiptMatchesAcquisition,
  hashPortableTree,
  parsePortableInstallReceipt,
  portableSourceCoordinates,
  PORTABLE_INSTALL_RECEIPT_FILE,
  PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION,
  readPortableTreeFromCleanCommit,
  serializePortableInstallReceipt,
  type PortableInstallReceiptV1,
  type PortableTreeInput,
  type PortableTreeManifest,
} from './portable-integrity.js';
import { validateSkillFile } from './validator/skills.js';

const RESOURCE_DIRECTORIES = new Set(['assets', 'examples', 'references', 'scripts', 'templates']);
const ROOT_FILES = new Set(['SKILL.md', 'README.md', 'LICENSE', 'LICENSE.md', 'eval-spec.yaml']);
const PRIVATE_COMPONENT =
  /^(?:\..*|node_modules|__pycache__|cache|coverage|dist|build|credentials(?:\..*)?|secrets?(?:\..*)?|id_(?:rsa|dsa|ecdsa|ed25519))(?:$)/i;
const PRIVATE_EXTENSION = /\.(?:key|pem|p12|pfx|pyc|log|sqlite|db)$/i;

export async function readRegularFile(file: string, expectedSize: number) {
  const handle = await fs.open(
    file,
    constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0),
  );
  try {
    const info = await handle.stat({ bigint: true });
    const check = async () => {
      const current = await fs.lstat(file, { bigint: true });
      const opened = await handle.stat({ bigint: true });
      if (
        !info.isFile() ||
        !current.isFile() ||
        current.isSymbolicLink() ||
        current.dev !== info.dev ||
        current.ino !== info.ino ||
        opened.size !== BigInt(expectedSize) ||
        opened.mtimeNs !== info.mtimeNs ||
        opened.ctimeNs !== info.ctimeNs
      )
        throw new Error('Portable file changed identity or content while being verified');
    };
    await check();
    const bytes = await handle.readFile();
    await check();
    if (bytes.length !== expectedSize) throw new Error('Portable file size changed during read');
    return { bytes, mode: info.mode };
  } finally {
    await handle.close();
  }
}

export function admitFiles(files: PortableTreeInput[]): void {
  for (const file of files) {
    const segments = file.path.split('/');
    if (
      !(segments.length === 1
        ? ROOT_FILES.has(file.path)
        : RESOURCE_DIRECTORIES.has(segments[0])) ||
      segments.some((segment) => PRIVATE_COMPONENT.test(segment)) ||
      PRIVATE_EXTENSION.test(file.path)
    )
      throw new Error(`Refusing non-portable or private source file: ${file.path}`);
  }
}

async function absent(destination: string): Promise<void> {
  try {
    await fs.lstat(destination);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return;
    throw error;
  }
  throw new Error(`Refusing to overwrite existing portable skill: ${destination}`);
}

export async function realDirectories(directory: string, create = true): Promise<void> {
  const absolute = path.resolve(directory);
  let current = path.parse(absolute).root;
  for (const segment of absolute.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, segment);
    if (create) {
      try {
        await fs.mkdir(current);
      } catch (error) {
        if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
      }
    }
    const info = await fs.lstat(current).catch((error: NodeJS.ErrnoException) => {
      if (!create && error.code === 'ENOENT') return null;
      throw error;
    });
    if (!info) return;
    if (!info.isDirectory() || info.isSymbolicLink()) {
      throw new Error(`Portable installation requires real directories: ${current}`);
    }
  }
}

export async function stagedTree(
  directory: string,
  expected: PortableTreeManifest,
): Promise<PortableTreeInput[]> {
  const files: PortableTreeInput[] = [];
  const entries = new Map(expected.entries.map((entry) => [entry.path, entry]));
  async function walk(relative: string): Promise<void> {
    for (const name of await fs.readdir(path.join(directory, relative))) {
      if (!relative && name === PORTABLE_INSTALL_RECEIPT_FILE) continue;
      const child = relative ? `${relative}/${name}` : name;
      const absolute = path.join(directory, child);
      const info = await fs.lstat(absolute);
      if (info.isDirectory() && !info.isSymbolicLink()) await walk(child);
      else if (info.isFile() && !info.isSymbolicLink()) {
        const entry = entries.get(child);
        if (!entry || info.size !== entry.size)
          throw new Error(`Staged file differs from source digest: ${child}`);
        const verified = await readRegularFile(absolute, entry.size);
        files.push({
          path: child,
          bytes: verified.bytes,
          // Windows does not represent POSIX executable bits; retain the source Git metadata.
          mode:
            process.platform === 'win32'
              ? entry.mode
              : (verified.mode & 0o111n) !== 0n
                ? '100755'
                : '100644',
        });
      } else throw new Error(`Unsupported staged file: ${child}`);
    }
  }
  await walk('');
  return files;
}

/** Installs Git object bytes, never a recursive copy of a mutable checkout. */
export async function installPortableTree(options: {
  sourceDirectory: string;
  destinationRoot: string;
  harness: string;
  scope: 'project' | 'user';
  registryVersion: number;
  cliVersion: string;
  dryRun: boolean;
}): Promise<PortableInstallReceiptV1> {
  const coordinates = await portableSourceCoordinates(options.sourceDirectory);
  const acquisition = await readPortableTreeFromCleanCommit(coordinates);
  admitFiles(acquisition.files);
  const name = path.basename(acquisition.sourcePath);
  const root = path.resolve(options.destinationRoot);
  const destination = path.join(root, name);
  await realDirectories(root, false);
  await absent(destination);
  let lock: string | undefined;
  let staging: string | undefined;
  try {
    if (!options.dryRun) {
      await realDirectories(root);
      const candidate = path.join(root, `.${name}.install-lock`);
      // Exclusive ownership serializes cooperating installers; never remove another installer's lock.
      await fs.mkdir(candidate, { mode: 0o700 });
      lock = candidate;
      await absent(destination);
    }
    staging = await fs.mkdtemp(path.join(options.dryRun ? tmpdir() : root, `.${name}.install-`));
    for (const file of acquisition.files) {
      const target = path.join(staging, file.path);
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.writeFile(target, file.bytes, {
        flag: 'wx',
        mode: file.mode === '100755' ? 0o755 : 0o644,
      });
      await fs.chmod(target, file.mode === '100755' ? 0o755 : 0o644);
    }
    const validation = await validateSkillFile(
      path.join(staging, 'SKILL.md'),
      `${acquisition.sourcePath}/SKILL.md`,
    );
    if (validation.fatal || validation.errors.length) {
      throw new Error(
        `Portable skill validation failed: ${validation.fatal ?? validation.errors.join('; ')}`,
      );
    }
    const validator = { name: 'ccpi-compatibility-validator', version: options.cliVersion };
    const skillSchemaVersion = 'ccpi-skill-compatibility-v1';
    // This compatibility receipt is not a marketplace grade or behavioral certification.
    const evidence = JSON.stringify({
      format: 'ccpi-portable-validation-v1',
      validator,
      skillSchemaVersion,
      source: {
        repository: acquisition.repository,
        commit: acquisition.commit,
        path: acquisition.sourcePath,
      },
      treeDigest: acquisition.manifest.digest,
      result: validation,
    });
    const evidenceHash = createHash('sha256').update(evidence).digest('hex');
    const receipt = assertReceiptMatchesAcquisition(
      {
        schemaVersion: PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION,
        source: {
          repository: acquisition.repository,
          commit: acquisition.commit,
          tree: acquisition.sourceTree,
          path: acquisition.sourcePath,
        },
        installation: { harness: options.harness, scope: options.scope },
        validation: {
          validator,
          skillSchemaVersion,
          harnessRegistryVersion: options.registryVersion,
        },
        tree: acquisition.manifest,
        evidence: [
          {
            kind: 'compatibility-validation',
            uri: `urn:sha256:${evidenceHash}`,
            sha256: `sha256:${evidenceHash}`,
            retention: 'indefinite',
          },
        ],
      },
      acquisition,
    );
    const receiptPath = path.join(staging, PORTABLE_INSTALL_RECEIPT_FILE);
    const serializedReceipt = serializePortableInstallReceipt(receipt);
    await fs.writeFile(receiptPath, serializedReceipt, {
      flag: 'wx',
      mode: 0o644,
    });
    assertReceiptMatchesAcquisition(
      parsePortableInstallReceipt(
        (await readRegularFile(receiptPath, Buffer.byteLength(serializedReceipt))).bytes,
      ),
      acquisition,
    );
    if (
      hashPortableTree(await stagedTree(staging, acquisition.manifest)).digest !==
      acquisition.manifest.digest
    ) {
      throw new Error('Staged portable skill does not match its immutable source digest');
    }
    const currentSource = await readPortableTreeFromCleanCommit(coordinates);
    assertReceiptMatchesAcquisition(receipt, currentSource);
    if (!options.dryRun) {
      const evidenceRoot = path.join(root, '.ccpi-evidence');
      await realDirectories(evidenceRoot);
      const evidenceFile = path.join(evidenceRoot, `${evidenceHash}.json`);
      try {
        await fs.writeFile(evidenceFile, evidence, { flag: 'wx', mode: 0o600 });
      } catch (error) {
        if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
      }
      const retained = await readRegularFile(evidenceFile, Buffer.byteLength(evidence));
      if (retained.bytes.toString('utf8') !== evidence) {
        throw new Error('Retained portable validation evidence does not match its digest');
      }
      await fs.chmod(staging, 0o755);
      await absent(destination);
      await fs.rename(staging, destination);
      staging = undefined;
    }
    return receipt;
  } finally {
    try {
      if (staging) await fs.rm(staging, { recursive: true, force: true });
    } finally {
      if (lock) await fs.rmdir(lock);
    }
  }
}
