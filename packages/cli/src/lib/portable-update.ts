import { promises as fs } from 'node:fs';
import path from 'node:path';
import { diagnosePortableSkill } from './portable-doctor.js';
import { installPortableTree, realDirectories } from './portable-install.js';
import { portableSourceCoordinates, type PortableInstallReceiptV1 } from './portable-integrity.js';

export type PreparedPortableUpdate = {
  destination: string;
  stagingRoot: string;
  stagedDestination: string;
  previous: { source: PortableInstallReceiptV1['source']; digest: string };
  replacement: PortableInstallReceiptV1;
};

/** Prepare only: the active directory is never renamed, overwritten or removed. */
export async function preparePortableUpdate(options: {
  sourceDirectory: string;
  sourceCommit: string;
  destinationRoot: string;
  harness: string;
  scope: 'project' | 'user';
  registryVersion: number;
  cliVersion: string;
}): Promise<PreparedPortableUpdate> {
  const coordinates = await portableSourceCoordinates(options.sourceDirectory);
  const name = path.posix.basename(coordinates.sourcePath);
  const root = path.resolve(options.destinationRoot);
  const destination = path.join(root, name);
  await realDirectories(root, false);
  const lock = path.join(root, `.${name}.install-lock`);
  await fs.mkdir(lock, { mode: 0o700 });
  let stagingRoot: string | undefined;
  try {
    const diagnose = () =>
      diagnosePortableSkill({
        destination,
        sourceRepo: coordinates.repoRoot,
        harness: options.harness,
        scope: options.scope,
      });
    const before = await diagnose();
    if (before.integrity === 'locally-modified') {
      throw new Error(
        'Preserve and export/diff local changes before explicitly choosing repair or reinstall',
      );
    }
    if (
      !['verified', 'outdated'].includes(before.integrity) ||
      !before.source ||
      !before.expectedDigest
    ) {
      throw new Error(`Cannot update an installation with ${before.integrity} integrity`);
    }
    if (
      before.source.repository !== coordinates.repository ||
      before.source.path !== coordinates.sourcePath
    ) {
      throw new Error('Update source identity differs from the installed receipt');
    }
    stagingRoot = await fs.mkdtemp(path.join(root, `.${name}.update-`));
    const replacement = await installPortableTree({
      ...options,
      destinationRoot: stagingRoot,
      dryRun: false,
    });
    if (replacement.tree.digest === before.expectedDigest) {
      throw new Error('Selected revision has no portable content change');
    }
    const after = await diagnose();
    if (
      !['verified', 'outdated'].includes(after.integrity) ||
      after.installedDigest !== before.installedDigest ||
      JSON.stringify(after.source) !== JSON.stringify(before.source)
    ) {
      throw new Error('Active installation changed while preparing its replacement');
    }
    const result: PreparedPortableUpdate = {
      destination,
      stagingRoot,
      stagedDestination: path.join(stagingRoot, name),
      previous: { source: before.source, digest: before.expectedDigest },
      replacement,
    };
    stagingRoot = undefined; // The caller owns the prepared tree; activation must reverify it.
    return result;
  } finally {
    try {
      if (stagingRoot) await fs.rm(stagingRoot, { recursive: true, force: true });
    } finally {
      await fs.rmdir(lock);
    }
  }
}
