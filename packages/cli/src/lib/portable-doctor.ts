import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import {
  assertReceiptMatchesAcquisition,
  hashPortableTree,
  parsePortableInstallReceipt,
  portableRepositoryHead,
  PORTABLE_INSTALL_RECEIPT_FILE,
  readPortableTreeFromCommit,
  type PortableInstallReceiptV1,
} from './portable-integrity.js';
import { admitFiles, readRegularFile, realDirectories, stagedTree } from './portable-install.js';

type Verdict = 'verified' | 'outdated' | 'locally-modified' | 'missing' | 'unverifiable';
export type PortableDiagnosis = {
  name: string;
  destination: string;
  integrity: Verdict;
  quality: 'not-assessed';
  source: PortableInstallReceiptV1['source'] | null;
  expectedDigest: string | null;
  installedDigest: string | null;
  upstream: {
    basis: 'selected-local-repository-HEAD';
    state: 'unavailable' | 'current' | 'outdated';
    commit: string | null;
    digest: string | null;
    reason: string | null;
  };
  reason: string;
  nextAction: string;
};

const detail = (error: unknown) => (error instanceof Error ? error.message : String(error));

async function boundedFile(file: string): Promise<Buffer> {
  const info = await fs.lstat(file);
  if (!info.isFile() || info.isSymbolicLink() || info.size > 1024 * 1024)
    throw new Error('Receipt/evidence must be a bounded regular file');
  return (await readRegularFile(file, info.size)).bytes;
}

async function verifyEvidence(root: string, receipt: PortableInstallReceiptV1) {
  const evidence = receipt.evidence.filter((item) => item.kind === 'compatibility-validation');
  if (evidence.length !== 1) throw new Error('One retained compatibility report is required');
  const item = evidence[0];
  const digest = item.sha256.slice('sha256:'.length);
  if (item.uri !== `urn:sha256:${digest}`) throw new Error('Unsupported evidence location');
  const directory = path.join(root, '.ccpi-evidence');
  await realDirectories(directory, false);
  const bytes = await boundedFile(path.join(directory, `${digest}.json`));
  if (createHash('sha256').update(bytes).digest('hex') !== digest)
    throw new Error('Retained evidence digest mismatch');
  const report = JSON.parse(bytes.toString('utf8'));
  if (
    report.format !== 'ccpi-portable-validation-v1' ||
    receipt.validation.validator.name !== 'ccpi-compatibility-validator' ||
    receipt.validation.skillSchemaVersion !== 'ccpi-skill-compatibility-v1' ||
    JSON.stringify(report.validator) !== JSON.stringify(receipt.validation.validator) ||
    report.skillSchemaVersion !== receipt.validation.skillSchemaVersion ||
    report.source?.repository !== receipt.source.repository ||
    JSON.stringify(report.source?.commit) !== JSON.stringify(receipt.source.commit) ||
    report.source?.path !== receipt.source.path ||
    report.treeDigest !== receipt.tree.digest ||
    report.result?.file !== `${receipt.source.path}/SKILL.md` ||
    report.result?.fatal ||
    !Array.isArray(report.result?.errors) ||
    report.result.errors.length !== 0
  )
    throw new Error('Retained compatibility report does not match the receipt');
}

/** No network acquisition, checkout, index refresh, repair, or writes. */
export async function diagnosePortableSkill(options: {
  destination: string;
  sourceRepo: string;
  harness: string;
  scope: 'project' | 'user';
}): Promise<PortableDiagnosis> {
  const destination = path.resolve(options.destination);
  const result: PortableDiagnosis = {
    name: path.basename(destination),
    destination,
    integrity: 'unverifiable',
    quality: 'not-assessed',
    source: null,
    expectedDigest: null,
    installedDigest: null,
    upstream: {
      basis: 'selected-local-repository-HEAD',
      state: 'unavailable',
      commit: null,
      digest: null,
      reason: null,
    },
    reason: '',
    nextAction:
      'Preserve this installation; select its trusted source repository and retained evidence.',
  };
  let receipt: PortableInstallReceiptV1;
  try {
    await realDirectories(path.dirname(destination), false);
    const info = await fs.lstat(destination).catch((error: NodeJS.ErrnoException) => {
      if (error.code === 'ENOENT') return null;
      throw error;
    });
    if (!info) {
      result.integrity = 'missing';
      result.reason = 'The selected skill destination does not exist; no receipt is available.';
      result.nextAction = 'Install from a reviewed canonical source directory.';
      return result;
    }
    if (!info.isDirectory() || info.isSymbolicLink())
      throw new Error('Installed skill must be a real directory');
    receipt = parsePortableInstallReceipt(
      await boundedFile(path.join(destination, PORTABLE_INSTALL_RECEIPT_FILE)),
    );
    result.source = receipt.source;
    result.expectedDigest = receipt.tree.digest;
    if (
      receipt.installation.harness !== options.harness ||
      receipt.installation.scope !== options.scope ||
      path.posix.basename(receipt.source.path) !== result.name
    )
      throw new Error('Receipt does not belong to this skill, harness, and scope');
    await verifyEvidence(path.dirname(destination), receipt);
  } catch (error) {
    result.reason = detail(error);
    return result;
  }

  let modified = false;
  try {
    result.installedDigest = hashPortableTree(await stagedTree(destination, receipt.tree)).digest;
    modified = result.installedDigest !== receipt.tree.digest;
  } catch (error) {
    if (['EACCES', 'EPERM', 'EIO'].includes((error as NodeJS.ErrnoException).code ?? '')) {
      result.reason = detail(error);
      return result;
    }
    modified = true;
    result.reason = detail(error);
  }

  const coordinates = {
    repoRoot: path.resolve(options.sourceRepo),
    repository: receipt.source.repository,
    commit: receipt.source.commit.digest,
    sourcePath: receipt.source.path,
  };
  try {
    const original = await readPortableTreeFromCommit(coordinates);
    admitFiles(original.files);
    assertReceiptMatchesAcquisition(receipt, original);
  } catch (error) {
    result.reason = `Source provenance could not be verified: ${detail(error)}`;
    result.upstream.reason = result.reason;
    return result;
  }

  try {
    const head = await portableRepositoryHead(coordinates.repoRoot);
    result.upstream.commit = head.commit;
    const current = await readPortableTreeFromCommit({ ...coordinates, commit: head.commit });
    result.upstream.digest = current.manifest.digest;
    result.upstream.state =
      current.manifest.digest === receipt.tree.digest ? 'current' : 'outdated';
  } catch (error) {
    result.upstream.reason = detail(error);
  }
  result.integrity = modified
    ? 'locally-modified'
    : result.upstream.state === 'outdated'
      ? 'outdated'
      : 'verified';
  result.reason = modified
    ? result.reason || 'Installed bytes or executable modes differ from the immutable source.'
    : 'Installed bytes, receipt, and retained compatibility evidence match the immutable source.';
  result.nextAction = modified
    ? 'Preserve local changes and compare them with the source before any explicit update.'
    : result.upstream.state === 'outdated'
      ? 'Review the selected repository HEAD before explicitly updating.'
      : result.upstream.state === 'unavailable'
        ? 'Preserve the verified bytes; inspect why the source path is unavailable at local HEAD.'
        : 'No byte repair needed. Quality and behavioral certification have not been assessed.';
  return result;
}
