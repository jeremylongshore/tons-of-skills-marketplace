import assert from 'node:assert/strict';
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join, relative, win32 } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import {
  buildPackageJson,
  isRepositoryGeneratedTrackingManifest,
  isPathAtOrBelow,
  reconcileGeneratedPackageMetadata,
  repositoryRelativePath,
  slugFromPath,
  trackingPostinstall,
} from './generate-plugin-package-jsons.mjs';

const canonicalRepository = {
  type: 'git',
  url: 'git+https://github.com/jeremylongshore/tons-of-skills-marketplace.git',
  directory: 'plugins/testing/example-plugin',
};

const repositoryRoot = dirname(dirname(fileURLToPath(import.meta.url)));
function runNpm(args, options) {
  // Windows resolves npm through npm.cmd. The arguments below are fixed test
  // constants, never package-controlled input, so shell resolution adds no
  // interpolation boundary.
  return spawnSync('npm', args, { ...options, shell: process.platform === 'win32' });
}

function sourcePackageRows(root) {
  const rows = [];
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === 'node_modules' || entry.name === '.git' || entry.isSymbolicLink())
        continue;
      const fullPath = join(directory, entry.name);
      if (entry.isDirectory()) walk(fullPath);
      else if (entry.name === '.source.json') {
        const pluginDir = dirname(fullPath);
        const packagePath = join(pluginDir, 'package.json');
        if (existsSync(packagePath)) {
          rows.push({
            directory: relative(root, pluginDir).replaceAll('\\', '/'),
            package: JSON.parse(readFileSync(packagePath, 'utf8')),
          });
        }
      }
    }
  }
  walk(join(root, 'plugins'));
  return rows.sort((left, right) => left.directory.localeCompare(right.directory));
}

const expectedManagedMirrorDirectories = [
  'plugins/ai-agency/tonone',
  'plugins/api-development/x-twitter-scraper',
  'plugins/community/ejentum-anti-deception',
  'plugins/community/ejentum-code',
  'plugins/community/ejentum-memory',
  'plugins/community/ejentum-reasoning',
  'plugins/community/hermes-tweet',
  'plugins/community/mnemos',
  'plugins/community/portaljs',
  'plugins/community/quit-sponsor',
  'plugins/community/skillcrossroads',
  'plugins/community/skills-janitor',
  'plugins/crypto/aomi',
  'plugins/design/brand-forge',
  'plugins/design/uizze',
  'plugins/devops/sugar',
  'plugins/mcp/dolt-mcp-vcs',
  'plugins/mcp/governed-second-brain',
  'plugins/mcp/servicegraph',
  'plugins/productivity/box-cloud-filesystem',
  'plugins/productivity/claude-workflow-skills',
  'plugins/productivity/claudebase',
  'plugins/productivity/content-multiplier',
  'plugins/productivity/obsidian-project-documentation',
  'plugins/productivity/over-50s-health',
  'plugins/productivity/pair-programmer',
  'plugins/productivity/publishing-skills',
  'plugins/productivity/schedule-after-usage-reset',
  'plugins/productivity/skyvern',
  'plugins/testing/cli-ux-tester',
  'plugins/testing/kobiton-automate',
];

const expectedUpstreamMirrorDirectories = [
  'plugins/ai-agency/hyperflow',
  'plugins/community/llm-box',
  'plugins/mcp/pr-to-spec',
  'plugins/mcp/slack-channel',
  'plugins/mcp/x-bug-triage',
  'plugins/productivity/cli-power-skills',
];

function managedMirrorPackage(directory = 'plugins/community/example-plugin') {
  const slug = directory.split('/').at(-1);
  return {
    name: `@intentsolutionsio/${slug}`,
    private: true,
    version: '1.0.0',
    repository: {
      type: 'git',
      url: 'git+https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git',
      directory,
    },
    bugs: 'https://github.com/jeremylongshore/claude-code-plugins-plus-skills/issues',
    publishConfig: { access: 'public' },
    scripts: { postinstall: trackingPostinstall(slug) },
  };
}

test('classifies a repository-generated mirror only when all strong sentinels match', () => {
  const directory = 'plugins/community/example-plugin';
  const input = managedMirrorPackage(directory);
  assert.equal(isRepositoryGeneratedTrackingManifest(input, directory), true);

  for (const mutation of [
    (pkg) => (pkg.name = '@intentsolutionsio/other-plugin'),
    (pkg) => (pkg.repository.url = 'git+https://github.com/upstream/example-plugin.git'),
    (pkg) => (pkg.repository.directory = 'plugins/community/other-plugin'),
    (pkg) => (pkg.scripts.postinstall = 'echo tracking/proof'),
  ]) {
    const mutated = JSON.parse(JSON.stringify(input));
    mutation(mutated);
    assert.equal(isRepositoryGeneratedTrackingManifest(mutated, directory), false);
  }
});

test('source-owned scaffolds are private tracking manifests without public access', () => {
  const sourceOwned = buildPackageJson(
    '/tmp/plugins/community/example-plugin',
    { description: 'An upstream plugin' },
    { sourceOwned: true },
  );
  assert.equal(sourceOwned.private, true);
  assert.equal(Object.hasOwn(sourceOwned, 'publishConfig'), false);
  assert.equal(sourceOwned.scripts.postinstall, trackingPostinstall('example-plugin'));

  const firstParty = buildPackageJson('/tmp/plugins/community/example-plugin', {
    description: 'A first-party plugin',
  });
  assert.equal(firstParty.private, undefined);
  assert.deepEqual(firstParty.publishConfig, { access: 'public' });
});

test('first-party generated metadata preserves public access', () => {
  const input = {
    name: '@intentsolutionsio/example-plugin',
    repository: canonicalRepository,
    publishConfig: { access: 'public' },
  };
  const result = reconcileGeneratedPackageMetadata(input, canonicalRepository.directory);
  assert.equal(result.changed, false);
  assert.deepEqual(result.pkg.publishConfig, { access: 'public' });
});

test('managed mirror reconciliation removes only public access and preserves non-public fields', () => {
  const input = managedMirrorPackage();
  input.publishConfig = {
    access: 'public',
    registry: 'https://registry.example.invalid/',
    provenance: false,
  };
  const result = reconcileGeneratedPackageMetadata(input, 'plugins/community/example-plugin', {
    sourceOwned: true,
  });

  assert.equal(result.changed, true);
  assert.deepEqual(result.pkg.publishConfig, {
    registry: 'https://registry.example.invalid/',
    provenance: false,
  });
  assert.equal(
    result.pkg.repository.url,
    'git+https://github.com/jeremylongshore/tons-of-skills-marketplace.git',
  );
  assert.equal(
    result.pkg.bugs,
    'https://github.com/jeremylongshore/tons-of-skills-marketplace/issues',
  );
});

test('managed mirror with only public access removes the empty publishConfig object', () => {
  const result = reconcileGeneratedPackageMetadata(
    managedMirrorPackage(),
    'plugins/community/example-plugin',
    { sourceOwned: true },
  );
  assert.equal(Object.hasOwn(result.pkg, 'publishConfig'), false);
});

test('managed source mirror reconciliation restores private true as defense in depth', () => {
  const input = managedMirrorPackage();
  input.private = false;
  const result = reconcileGeneratedPackageMetadata(input, 'plugins/community/example-plugin', {
    sourceOwned: true,
  });

  assert.equal(result.changed, true);
  assert.equal(result.pkg.private, true);
  assert.equal(Object.hasOwn(result.pkg, 'publishConfig'), false);
});

test('upstream-owned source package remains byte/object unchanged', () => {
  const input = {
    name: '@intentsolutionsio/example-plugin',
    repository: {
      type: 'git',
      url: 'git+https://github.com/upstream/example-plugin.git',
      directory: 'plugins/community/example-plugin',
    },
    publishConfig: {
      access: 'restricted',
      registry: 'https://registry.example.invalid/',
    },
    scripts: { postinstall: 'node upstream-install.js' },
  };
  const before = JSON.stringify(input);
  assert.equal(
    isRepositoryGeneratedTrackingManifest(input, 'plugins/community/example-plugin'),
    false,
  );
  const result = reconcileGeneratedPackageMetadata(input, 'plugins/community/example-plugin', {
    sourceOwned: true,
  });
  assert.equal(result.changed, false);
  assert.equal(result.pkg, input);
  assert.equal(JSON.stringify(result.pkg), before);
});

test('current source-owned package census has exactly 31 managed and 6 upstream manifests', () => {
  const rows = sourcePackageRows(repositoryRoot);
  const managed = rows
    .filter((row) => isRepositoryGeneratedTrackingManifest(row.package, row.directory))
    .map((row) => row.directory);
  const upstream = rows
    .filter((row) => !isRepositoryGeneratedTrackingManifest(row.package, row.directory))
    .map((row) => row.directory);

  assert.equal(rows.length, 37);
  assert.deepEqual(managed, expectedManagedMirrorDirectories);
  assert.deepEqual(upstream, expectedUpstreamMirrorDirectories);
});

test('managed mirror reconciliation is deterministic and drift-free on its second run', () => {
  for (const directory of expectedManagedMirrorDirectories) {
    const packagePath = join(repositoryRoot, directory, 'package.json');
    const input = JSON.parse(readFileSync(packagePath, 'utf8'));
    input.publishConfig = { ...(input.publishConfig ?? {}), access: 'public' };
    const first = reconcileGeneratedPackageMetadata(input, directory, { sourceOwned: true });
    const second = reconcileGeneratedPackageMetadata(first.pkg, directory, { sourceOwned: true });

    assert.equal(first.changed, true, directory);
    assert.equal(second.changed, false, directory);
    assert.deepEqual(second.pkg, first.pkg, directory);
  }
});

test('npm dry-run does not announce public access for a repaired mirror', () => {
  const root = mkdtempSync(join(tmpdir(), 'mirror-npm-dry-run-'));
  try {
    const repaired = reconcileGeneratedPackageMetadata(
      managedMirrorPackage('plugins/community/example-plugin'),
      'plugins/community/example-plugin',
      { sourceOwned: true },
    ).pkg;
    writeFileSync(join(root, 'package.json'), JSON.stringify(repaired, null, 2) + '\n');
    const result = runNpm(['publish', '--dry-run', '--ignore-scripts', '--json'], {
      cwd: root,
      encoding: 'utf8',
      env: { ...process.env, npm_config_offline: 'true' },
      timeout: 10_000,
    });

    assert.equal(result.error, undefined, result.error?.message);
    assert.equal(result.status, 0, result.stderr);
    assert.doesNotMatch(`${result.stdout}\n${result.stderr}`, /public access/i);
    assert.doesNotThrow(() => JSON.parse(result.stdout));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('real npm publish path refuses a private mirror before loopback connection', () => {
  const root = mkdtempSync(join(tmpdir(), 'mirror-npm-private-'));
  try {
    const repaired = reconcileGeneratedPackageMetadata(
      managedMirrorPackage('plugins/community/example-plugin'),
      'plugins/community/example-plugin',
      { sourceOwned: true },
    ).pkg;
    writeFileSync(join(root, 'package.json'), JSON.stringify(repaired, null, 2) + '\n');
    const result = runNpm(
      [
        'publish',
        '--force',
        '--registry=http://127.0.0.1:9',
        '--ignore-scripts',
        '--json',
        '--//127.0.0.1:9/:_authToken=fake-local-token',
      ],
      { cwd: root, encoding: 'utf8', timeout: 10_000 },
    );

    assert.equal(result.error, undefined, result.error?.message);
    assert.equal(result.status, 1, result.stderr);
    assert.match(`${result.stdout}\n${result.stderr}`, /EPRIVATE/);
    assert.doesNotMatch(`${result.stdout}\n${result.stderr}`, /ECONNREFUSED|ENOTFOUND/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('derives Windows plugin slugs without leaking an absolute path into the npm name', () => {
  const pluginDir = String.raw`C:\repo\plugins\saas-packs\skill-databases\windsurf`;
  assert.equal(slugFromPath(pluginDir, win32), 'windsurf');
});

test('normalizes Windows repository directories to portable package metadata paths', () => {
  const root = String.raw`C:\repo`;
  const pluginDir = String.raw`C:\repo\plugins\security\example-plugin`;
  assert.equal(repositoryRelativePath(root, pluginDir, win32), 'plugins/security/example-plugin');
});

test('matches excluded Windows subtrees on path boundaries only', () => {
  const excluded = String.raw`C:\repo\plugins\saas-packs\skill-databases`;
  assert.equal(isPathAtOrBelow(excluded, excluded, win32), true);
  assert.equal(isPathAtOrBelow(excluded, `${excluded}\\windsurf`, win32), true);
  assert.equal(isPathAtOrBelow(excluded, `${excluded}-archive\\windsurf`, win32), false);
});

test('reconciles stale repository metadata on generated package manifests', () => {
  const input = {
    name: '@intentsolutionsio/example-plugin',
    version: '1.2.3',
    repository: {
      type: 'git',
      url: 'git+https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git',
      directory: 'plugins/testing/example-plugin',
    },
    bugs: 'https://github.com/jeremylongshore/claude-code-plugins-plus-skills/issues',
  };

  const result = reconcileGeneratedPackageMetadata(input, 'plugins/testing/example-plugin');

  assert.equal(result.changed, true);
  assert.deepEqual(result.pkg.repository, canonicalRepository);
  assert.equal(
    result.pkg.bugs,
    'https://github.com/jeremylongshore/tons-of-skills-marketplace/issues',
  );
  assert.equal(result.pkg.version, '1.2.3');
});

test('leaves already canonical generated metadata byte-shape stable', () => {
  const input = {
    name: '@intentsolutionsio/example-plugin',
    repository: canonicalRepository,
    bugs: 'https://github.com/jeremylongshore/tons-of-skills-marketplace/issues',
  };

  const result = reconcileGeneratedPackageMetadata(input, 'plugins/testing/example-plugin');

  assert.equal(result.changed, false);
  assert.equal(result.pkg, input);
});

test('does not rewrite upstream-owned package metadata', () => {
  const input = {
    name: 'upstream-plugin',
    repository: 'https://example.com/upstream/plugin',
    bugs: 'https://example.com/upstream/plugin/issues',
  };

  const result = reconcileGeneratedPackageMetadata(input, 'plugins/community/upstream-plugin');

  assert.equal(result.changed, false);
  assert.equal(result.pkg, input);
});

test('reconciles a repository-managed manifest that uses an older Intent scope', () => {
  const input = {
    name: '@intentsolutions/example-plugin',
    repository: {
      type: 'git',
      url: 'git+https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git',
      directory: 'plugins/testing/example-plugin',
    },
  };

  const result = reconcileGeneratedPackageMetadata(input, 'plugins/testing/example-plugin');

  assert.equal(result.changed, true);
  assert.deepEqual(result.pkg.repository, canonicalRepository);
});

test('does not invent missing metadata while replacing legacy repository URLs', () => {
  const input = {
    name: '@intentsolutionsio/example-plugin',
    repository: {
      type: 'git',
      url: 'git+https://github.com/jeremylongshore/claude-code-plugins.git',
      directory: 'plugins/testing/example-plugin',
    },
  };

  const result = reconcileGeneratedPackageMetadata(input, 'plugins/testing/example-plugin');

  assert.equal(result.changed, true);
  assert.deepEqual(result.pkg.repository, canonicalRepository);
  assert.equal(Object.hasOwn(result.pkg, 'bugs'), false);
});

test('does not rewrite a scoped manifest owned by a source-marked mirror', () => {
  const input = {
    name: '@intentsolutionsio/upstream-plugin',
    repository: {
      type: 'git',
      url: 'git+https://github.com/upstream/upstream-plugin.git',
    },
    bugs: 'https://github.com/jeremylongshore/claude-code-plugins-plus-skills/issues',
  };

  assert.equal(
    isRepositoryGeneratedTrackingManifest(input, 'plugins/community/upstream-plugin'),
    false,
  );
  const result = reconcileGeneratedPackageMetadata(input, 'plugins/community/upstream-plugin', {
    sourceOwned: true,
  });

  assert.equal(result.changed, false);
  assert.equal(result.pkg, input);
});
