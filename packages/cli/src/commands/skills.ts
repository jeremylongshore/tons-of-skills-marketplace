import { promises as fs } from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { installPortableTree } from '../lib/portable-install.js';
import { realDirectories } from '../lib/portable-install.js';
import { diagnosePortableSkill } from '../lib/portable-doctor.js';

type Scope = 'project' | 'user';
type Support =
  | 'verified-native'
  | 'standard-compatible'
  | 'native-extension'
  | 'research-required'
  | 'unsupported';
export type Harness = {
  id: string;
  displayName: string;
  support: Support;
  projectPath: string | null;
  userPath: string | null;
};

export type PortableInstallResult = {
  harness: string;
  support: Support;
  scope: Scope;
  source: string;
  destination: string;
  dryRun: boolean;
  receipt: string;
};

async function registry(): Promise<{ schemaVersion: number; harnesses: Harness[] }> {
  const file = new URL('../../registry/harness-registry.json', import.meta.url);
  return JSON.parse(await fs.readFile(file, 'utf8')) as {
    schemaVersion: number;
    harnesses: Harness[];
  };
}

function asScope(scope: string): Scope {
  if (scope === 'project' || scope === 'user') return scope;
  throw new Error(`Invalid scope: ${scope}. Use project or user.`);
}

function target(harness: Harness, scope: Scope): string {
  const value = scope === 'project' ? harness.projectPath : harness.userPath;
  if (!value) throw new Error(`${harness.displayName} has no ${scope}-scope portable-skill path`);
  return value.startsWith('~/') ? path.join(os.homedir(), value.slice(2)) : path.resolve(value);
}

async function portableSource(source: string): Promise<{ directory: string; name: string }> {
  const candidate = path.resolve(source);
  const directory = path.basename(candidate) === 'SKILL.md' ? path.dirname(candidate) : candidate;
  const skillFile = path.join(directory, 'SKILL.md');
  const info = await fs.stat(skillFile).catch(() => null);
  if (!info?.isFile())
    throw new Error(`Portable source must be a skill directory containing SKILL.md: ${source}`);
  const name = path.basename(directory);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) {
    throw new Error(`Portable skill directory must be lowercase kebab-case: ${name}`);
  }
  return { directory, name };
}

async function selectedHarness(id: string): Promise<Harness> {
  const harness = (await registry()).harnesses.find((item) => item.id === id);
  if (!harness) throw new Error(`Unknown harness: ${id}`);
  return harness;
}

export async function listHarnesses(json: boolean): Promise<void> {
  const { harnesses } = await registry();
  console.log(
    json
      ? JSON.stringify(harnesses, null, 2)
      : harnesses.map((h) => `${h.id}\t${h.support}\t${h.displayName}`).join('\n'),
  );
}

export async function doctorSkills(
  id: string,
  scope: Scope,
  json: boolean,
  sourceRepo = process.cwd(),
  skill?: string,
): Promise<void> {
  const resolvedScope = asScope(scope);
  const harness = await selectedHarness(id);
  const destination = target(harness, resolvedScope);
  if (skill && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(skill))
    throw new Error('Skill name must be lowercase kebab-case');
  await realDirectories(destination, false);
  const names = skill
    ? [skill]
    : await fs.readdir(destination).then(
        (items) => items.filter((name) => !name.startsWith('.')).sort(),
        (error: NodeJS.ErrnoException) => {
          if (error.code === 'ENOENT') return [];
          throw error;
        },
      );
  const diagnoses = [];
  for (const name of names)
    diagnoses.push(
      await diagnosePortableSkill({
        destination: path.join(destination, name),
        sourceRepo,
        harness: id,
        scope: resolvedScope,
      }),
    );
  const result = {
    schemaVersion: 'ccpi-portable-doctor/v1',
    harness: id,
    support: harness.support,
    scope: resolvedScope,
    destination,
    sourceRepo: path.resolve(sourceRepo),
    verificationScope: 'source-and-installed-bytes',
    quality: 'not-assessed',
    skills: diagnoses,
    exists: await fs
      .stat(destination)
      .then(() => true)
      .catch(() => false),
  };
  console.log(
    json
      ? JSON.stringify(result, null, 2)
      : diagnoses.length
        ? diagnoses
            .map(
              (item) =>
                `${item.name}: ${item.integrity} (byte integrity; quality not assessed)\n` +
                `  Source: ${item.source?.commit.digest ?? 'unavailable'} ${item.source?.path ?? 'unavailable'}\n` +
                `  Digest: expected ${item.expectedDigest ?? 'unavailable'}; installed ${item.installedDigest ?? 'unavailable'}\n` +
                `  Local HEAD: ${item.upstream.state}; ${item.upstream.commit ?? 'unavailable'}\n` +
                `  ${item.reason}\n  ${item.nextAction}`,
            )
            .join('\n')
        : `${result.exists ? 'No installed skills in' : 'Missing'} ${destination}`,
  );
}

export async function installPortableSkill(
  source: string,
  id: string,
  scope: string,
  dryRun: boolean,
  json: boolean,
): Promise<void> {
  const resolvedScope = asScope(scope);
  const harness = await selectedHarness(id);
  if (harness.support !== 'verified-native') {
    throw new Error(
      `${harness.displayName} is ${harness.support}; installation is available only for verified-native harnesses.`,
    );
  }
  const portable = await portableSource(source);
  const root = target(harness, resolvedScope);
  const destination = path.join(root, portable.name);
  const result: PortableInstallResult = {
    harness: harness.id,
    support: harness.support,
    scope: resolvedScope,
    source: portable.directory,
    destination,
    dryRun,
    receipt: path.join(destination, '.ccpi-portable-install.json'),
  };
  const packageMetadata = JSON.parse(
    await fs.readFile(new URL('../../package.json', import.meta.url), 'utf8'),
  ) as { version: string };
  await installPortableTree({
    sourceDirectory: portable.directory,
    destinationRoot: root,
    harness: harness.id,
    scope: resolvedScope,
    registryVersion: (await registry()).schemaVersion,
    cliVersion: packageMetadata.version,
    dryRun,
  });
  console.log(
    json
      ? JSON.stringify(result, null, 2)
      : `${dryRun ? 'Would install' : 'Installed'} ${portable.name} at ${destination}`,
  );
}
