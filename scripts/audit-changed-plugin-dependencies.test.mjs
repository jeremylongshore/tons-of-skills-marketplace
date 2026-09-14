import test from 'node:test';
import assert from 'node:assert/strict';
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  symlinkSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  auditStandalonePackage,
  changedPathsFromGit,
  discoverChangedStandalonePackages,
  globMatches,
  parseWorkspacePatterns,
  summarizeAuditJson,
  workspaceIncludes,
} from './audit-changed-plugin-dependencies.mjs';

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'changed-plugin-deps-'));
  writeFileSync(
    join(root, 'pnpm-workspace.yaml'),
    "packages:\n  - 'plugins/mcp/*'\n  - 'plugins/saas-packs/*-pack'\n",
  );
  return root;
}

function writePackage(root, pluginRoot, manifest, lock = null) {
  const directory = join(root, pluginRoot);
  mkdirSync(directory, { recursive: true });
  writeFileSync(join(directory, 'package.json'), JSON.stringify(manifest));
  if (lock) writeFileSync(join(directory, lock), 'lockVersion: 9\n');
}

function scriptedRunner(results) {
  let index = 0;
  return () => results[index++] ?? { status: 0, stdout: '{}' };
}

test('workspace parser and glob matching identify existing workspace members', () => {
  const patterns = parseWorkspacePatterns(
    "packages:\n  - 'plugins/mcp/*'\n  - 'plugins/saas-packs/*-pack'\n",
  );
  assert.deepEqual(patterns, ['plugins/mcp/*', 'plugins/saas-packs/*-pack']);
  assert.equal(globMatches(patterns[0], 'plugins/mcp/example'), true);
  assert.equal(globMatches(patterns[1], 'plugins/saas-packs/example-pack'), true);
  assert.equal(globMatches(patterns[0], 'plugins/skill-enhancers/example'), false);
});

test('workspace YAML inline arrays and ordered negation preserve excluded standalone packages', () => {
  const patterns = parseWorkspacePatterns(
    "packages: ['plugins/**', '!plugins/skill-enhancers/standalone']\n",
  );
  assert.equal(workspaceIncludes(patterns, 'plugins/mcp/example'), true);
  assert.equal(workspaceIncludes(patterns, 'plugins/skill-enhancers/standalone'), false);
});

test('discovery is changed-root scoped and excludes workspaces and dependency-free manifests', () => {
  const repoRoot = fixture();
  writePackage(repoRoot, 'plugins/skill-enhancers/changed', { dependencies: { leftpad: '1.0.0' } });
  writePackage(repoRoot, 'plugins/skill-enhancers/docs-only', {
    scripts: { test: 'node test.js' },
  });
  writePackage(repoRoot, 'plugins/skill-enhancers/unchanged', {
    dependencies: { leftpad: '1.0.0' },
  });
  writePackage(repoRoot, 'plugins/mcp/workspace-member', { dependencies: { leftpad: '1.0.0' } });
  const found = discoverChangedStandalonePackages({
    repoRoot,
    changedPaths: [
      'plugins/skill-enhancers/changed/src/index.js',
      'plugins/skill-enhancers/docs-only/README.md',
      'plugins/mcp/workspace-member/package.json',
      'README.md',
    ],
  });
  assert.deepEqual(
    found.map((entry) => entry.root),
    ['plugins/skill-enhancers/changed'],
  );
});

test('empty changed scope succeeds without inventing package work', () => {
  const repoRoot = fixture();
  assert.deepEqual(
    discoverChangedStandalonePackages({
      repoRoot,
      changedPaths: ['README.md', 'scripts/example.mjs'],
    }),
    [],
  );
});

test('CI uses a complete manual-run range and disables standalone lifecycle scripts', () => {
  const workflow = readFileSync(
    new URL('../.github/workflows/validate-plugins.yml', import.meta.url),
    'utf8',
  );
  assert.match(workflow, /git fetch --no-tags --unshallow origin "\$AUDIT_DEFAULT_BRANCH"/);
  assert.match(workflow, /audit_base="origin\/\$AUDIT_DEFAULT_BRANCH"/);
  assert.doesNotMatch(workflow, /audit_base="HEAD\^"/);
  assert.match(
    workflow,
    /pnpm install --ignore-workspace --frozen-lockfile --ignore-scripts --ignore-pnpmfile/,
  );
  assert.match(
    workflow,
    /npm ci --ignore-scripts --no-audit --registry=https:\/\/registry\.npmjs\.org\//,
  );
  assert.match(workflow, /has no supported package-local lockfile/);
});

test('peer-only packages remain inside the dependency-audit denominator', () => {
  const repoRoot = fixture();
  writePackage(repoRoot, 'plugins/skill-enhancers/peer-only', {
    peerDependencies: { risky: '1.0.0' },
  });
  const found = discoverChangedStandalonePackages({
    repoRoot,
    changedPaths: ['plugins/skill-enhancers/peer-only/package.json'],
  });
  assert.deepEqual(
    found.map((entry) => entry.root),
    ['plugins/skill-enhancers/peer-only'],
  );
});

test('a changed symlinked package manifest is rejected instead of disappearing from scope', () => {
  const repoRoot = fixture();
  const packageRoot = 'plugins/skill-enhancers/symlink-manifest';
  const directory = join(repoRoot, packageRoot);
  mkdirSync(directory, { recursive: true });
  writeFileSync(
    join(repoRoot, 'outside.json'),
    JSON.stringify({ dependencies: { risky: '1.0.0' } }),
  );
  symlinkSync(join(repoRoot, 'outside.json'), join(directory, 'package.json'));
  assert.throws(
    () =>
      discoverChangedStandalonePackages({
        repoRoot,
        changedPaths: [`${packageRoot}/package.json`],
      }),
    /traverses symlink|regular non-symlink file/,
  );
});

test('workspace package symlinks are rejected before workspace exclusion', () => {
  const repoRoot = fixture();
  const packageRoot = 'plugins/mcp/workspace-symlink';
  const directory = join(repoRoot, packageRoot);
  mkdirSync(directory, { recursive: true });
  writeFileSync(
    join(repoRoot, 'outside.json'),
    JSON.stringify({ dependencies: { risky: '1.0.0' } }),
  );
  symlinkSync(join(repoRoot, 'outside.json'), join(directory, 'package.json'));
  assert.throws(
    () =>
      discoverChangedStandalonePackages({
        repoRoot,
        changedPaths: [`${packageRoot}/package.json`],
      }),
    /traverses symlink|regular non-symlink file/,
  );

  const linkedRoot = 'plugins/mcp/linked-directory';
  symlinkSync(directory, join(repoRoot, linkedRoot));
  assert.throws(
    () => discoverChangedStandalonePackages({ repoRoot, changedPaths: [linkedRoot] }),
    /traverses symlink/,
  );
});

test('broken plugin directory symlinks fail closed instead of disappearing', () => {
  const repoRoot = fixture();
  const linkedRoot = 'plugins/skill-enhancers/broken-plugin';
  mkdirSync(join(repoRoot, 'plugins/skill-enhancers'), { recursive: true });
  symlinkSync(join(repoRoot, 'missing-target'), join(repoRoot, linkedRoot));
  assert.throws(
    () => discoverChangedStandalonePackages({ repoRoot, changedPaths: [linkedRoot] }),
    /traverses symlink/,
  );
});

test('workspace membership changes cannot reclassify a package out of the audit', () => {
  const repoRoot = fixture();
  assert.throws(
    () =>
      discoverChangedStandalonePackages({
        repoRoot,
        changedPaths: ['pnpm-workspace.yaml', 'plugins/skill-enhancers/new-member/package.json'],
      }),
    /dedicated workspace-boundary review/,
  );
});

test('discovery selects the deepest actual package root and catches a deleted nested lock', () => {
  const repoRoot = fixture();
  writePackage(repoRoot, 'plugins/devops/sugar', { scripts: { test: 'node test.js' } });
  writePackage(repoRoot, 'plugins/devops/sugar/mcp-server', { dependencies: { risky: '1.0.0' } });
  const found = discoverChangedStandalonePackages({
    repoRoot,
    changedPaths: ['plugins/devops/sugar/mcp-server/pnpm-lock.yaml'],
  });
  assert.deepEqual(
    found.map((entry) => entry.root),
    ['plugins/devops/sugar/mcp-server'],
  );
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo: found[0],
    run: () => assert.fail('a deleted lock must fail before command execution'),
  });
  assert.equal(result.hardFailure, true);
  assert.match(result.messages[0], /no package-local lockfile/);
});

test('git discovery includes deletions and uses two-dot mode for push ranges', () => {
  let invocation;
  const paths = changedPathsFromGit(
    '/repo',
    'before-sha',
    'HEAD',
    (command, args) => {
      invocation = { command, args };
      return { status: 0, stdout: 'plugins/example/tool/pnpm-lock.yaml\0' };
    },
    'two-dot',
  );
  assert.deepEqual(paths, ['plugins/example/tool/pnpm-lock.yaml']);
  assert.deepEqual(invocation, {
    command: 'git',
    args: ['diff', '--name-only', '--diff-filter=ACMRDT', '-z', 'before-sha..HEAD'],
  });
});

test('git discovery includes a regular package manifest changed into a symlink', () => {
  const repoRoot = fixture();
  const packageRoot = 'plugins/skill-enhancers/type-change';
  writePackage(repoRoot, packageRoot, { dependencies: { risky: '1.0.0' } }, 'pnpm-lock.yaml');
  writeFileSync(
    join(repoRoot, 'outside.json'),
    JSON.stringify({ dependencies: { risky: '2.0.0' } }),
  );

  execFileSync('git', ['init', '-q'], { cwd: repoRoot });
  execFileSync('git', ['add', '.'], { cwd: repoRoot });
  execFileSync(
    'git',
    [
      '-c',
      'user.name=Security Test',
      '-c',
      'user.email=security@example.invalid',
      'commit',
      '-qm',
      'base',
    ],
    { cwd: repoRoot },
  );
  const base = execFileSync('git', ['rev-parse', 'HEAD'], {
    cwd: repoRoot,
    encoding: 'utf8',
  }).trim();

  unlinkSync(join(repoRoot, packageRoot, 'package.json'));
  symlinkSync(join(repoRoot, 'outside.json'), join(repoRoot, packageRoot, 'package.json'));
  execFileSync('git', ['add', '-A'], { cwd: repoRoot });
  execFileSync(
    'git',
    [
      '-c',
      'user.name=Security Test',
      '-c',
      'user.email=security@example.invalid',
      'commit',
      '-qm',
      'type change',
    ],
    { cwd: repoRoot },
  );

  const changedPaths = changedPathsFromGit(repoRoot, base, 'HEAD', undefined, 'two-dot');
  assert.ok(changedPaths.includes(`${packageRoot}/package.json`));
  assert.throws(
    () => discoverChangedStandalonePackages({ repoRoot, changedPaths }),
    /traverses symlink|regular non-symlink file/,
  );
});

test('a changed dependency package without an authoritative lock fails actionably', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/unlocked',
    manifest: { dependencies: { leftpad: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest);
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: () => assert.fail('must not run'),
  });
  assert.equal(result.ok, false);
  assert.equal(result.hardFailure, true);
  assert.match(result.messages[0], /no package-local lockfile/);
});

test('package-local npm configuration cannot redirect a standalone audit', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/redirected-audit',
    manifest: { dependencies: { risky: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'pnpm-lock.yaml');
  writeFileSync(join(repoRoot, packageInfo.root, '.npmrc'), 'registry=https://attacker.invalid/\n');
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: () => assert.fail('must reject configuration before executing a package manager'),
  });
  assert.equal(result.ok, false);
  assert.equal(result.hardFailure, true);
  assert.match(result.messages[0], /\.npmrc is not allowed/);
});

test('high and critical advisories retain package path, scope, and advisory IDs in report-only mode', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/vulnerable',
    manifest: { dependencies: { risky: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'pnpm-lock.yaml');
  const audit = JSON.stringify({
    vulnerabilities: {
      risky: {
        severity: 'critical',
        via: [
          {
            source: 12345,
            severity: 'critical',
            title: 'unsafe parsing',
            url: 'https://github.com/advisories/GHSA-test-1234',
          },
        ],
        nodes: ['node_modules/risky', 'node_modules/parent/node_modules/risky'],
      },
    },
  });
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: scriptedRunner([
      { status: 0, stdout: '' },
      { status: 1, stdout: audit },
      { status: 1, stdout: audit },
    ]),
    reportOnly: true,
  });
  assert.equal(result.ok, true);
  assert.equal(result.reportOnlyFailure, true);
  assert.deepEqual(
    result.findings.map((finding) => [finding.scope, finding.id, finding.dependencyPaths]),
    [
      [
        'production',
        'GHSA-test-1234',
        ['node_modules/parent/node_modules/risky', 'node_modules/risky'],
      ],
      ['full', 'GHSA-test-1234', ['node_modules/parent/node_modules/risky', 'node_modules/risky']],
    ],
  );
  assert.match(
    result.messages[0],
    /plugins\/skill-enhancers\/vulnerable production: critical risky \[GHSA-test-1234\]/,
  );
  assert.match(result.messages[0], /paths=node_modules\/parent\/node_modules\/risky/);
});

test('pnpm advisory format preserves GHSA IDs and dependency introduction paths', () => {
  const findings = summarizeAuditJson({
    advisories: {
      1120680: {
        id: 1120680,
        github_advisory_id: 'GHSA-g7r4-m6w7-qqqr',
        module_name: 'esbuild',
        severity: 'high',
        title: 'path traversal',
        url: 'https://github.com/advisories/GHSA-g7r4-m6w7-qqqr',
        findings: [{ paths: ['. > vite > esbuild', '. > tsx > esbuild'] }],
      },
    },
  });
  assert.deepEqual(findings, [
    {
      dependency: 'esbuild',
      severity: 'high',
      id: 'GHSA-g7r4-m6w7-qqqr',
      title: 'path traversal',
      url: 'https://github.com/advisories/GHSA-g7r4-m6w7-qqqr',
      dependencyPaths: ['. > tsx > esbuild', '. > vite > esbuild'],
    },
  ]);
});

test('a clean locked package passes both production and full audits', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/clean',
    manifest: { devDependencies: { safe: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'package-lock.json');
  const clean = JSON.stringify({ metadata: { vulnerabilities: { high: 0, critical: 0 } } });
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: scriptedRunner([
      { status: 0, stdout: '' },
      { status: 0, stdout: clean },
      { status: 0, stdout: clean },
    ]),
  });
  assert.equal(result.ok, true);
  assert.deepEqual(result.findings, []);
});

test('npm commands pin the trusted registry and ignore lifecycle scripts', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/npm-safe',
    manifest: { devDependencies: { safe: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'package-lock.json');
  const calls = [];
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: (command, args) => {
      calls.push({ command, args });
      return { status: 0, stdout: args.includes('audit') ? '{}' : '' };
    },
  });
  assert.equal(result.ok, true);
  assert.equal(calls.length, 3);
  assert.ok(calls.every((call) => call.command === 'npm'));
  assert.ok(calls[0].args.includes('--ignore-scripts'));
  assert.ok(calls.every((call) => call.args.includes('--registry=https://registry.npmjs.org/')));
});

test('pnpm commands disable executable hooks and pin the trusted audit registry', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/hook-safe',
    manifest: { dependencies: { safe: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'pnpm-lock.yaml');
  const calls = [];
  const priorRegistry = process.env.NPM_CONFIG_REGISTRY;
  const priorProxy = process.env.HTTPS_PROXY;
  const priorCorepackRegistry = process.env.COREPACK_NPM_REGISTRY;
  process.env.NPM_CONFIG_REGISTRY = 'https://attacker.invalid/';
  process.env.HTTPS_PROXY = 'https://attacker.invalid/';
  process.env.COREPACK_NPM_REGISTRY = 'https://attacker.invalid/';
  let result;
  try {
    result = auditStandalonePackage({
      repoRoot,
      packageInfo,
      run: (command, args, options) => {
        calls.push({ command, args, options });
        return { status: 0, stdout: args.includes('audit') ? '{}' : '' };
      },
    });
  } finally {
    if (priorRegistry === undefined) delete process.env.NPM_CONFIG_REGISTRY;
    else process.env.NPM_CONFIG_REGISTRY = priorRegistry;
    if (priorProxy === undefined) delete process.env.HTTPS_PROXY;
    else process.env.HTTPS_PROXY = priorProxy;
    if (priorCorepackRegistry === undefined) delete process.env.COREPACK_NPM_REGISTRY;
    else process.env.COREPACK_NPM_REGISTRY = priorCorepackRegistry;
  }
  assert.equal(result.ok, true);
  assert.equal(calls.length, 3);
  assert.ok(calls.every((call) => call.command === 'pnpm'));
  assert.ok(calls[0].args.includes('--ignore-scripts'));
  assert.ok(calls[0].args.includes('--ignore-pnpmfile'));
  assert.ok(calls.slice(1).every((call) => call.args.includes('--config.ignore-pnpmfile=true')));
  assert.ok(
    calls.every((call) => call.args.includes('--config.registry=https://registry.npmjs.org/')),
  );
  assert.ok(calls.every((call) => call.options.env.NPM_CONFIG_REGISTRY === undefined));
  assert.ok(calls.every((call) => call.options.env.HTTPS_PROXY === undefined));
  assert.ok(calls.every((call) => call.options.env.COREPACK_NPM_REGISTRY === undefined));
});

test('an audit transport or registry failure cannot masquerade as a clean report-only result', () => {
  const repoRoot = fixture();
  const packageInfo = {
    root: 'plugins/skill-enhancers/audit-error',
    manifest: { dependencies: { safe: '1.0.0' } },
  };
  writePackage(repoRoot, packageInfo.root, packageInfo.manifest, 'pnpm-lock.yaml');
  const result = auditStandalonePackage({
    repoRoot,
    packageInfo,
    run: scriptedRunner([
      { status: 0, stdout: '' },
      { status: 1, stdout: JSON.stringify({ error: { code: 'ENETUNREACH' } }) },
    ]),
    reportOnly: true,
  });
  assert.equal(result.ok, false);
  assert.equal(result.hardFailure, true);
  assert.match(result.messages[0], /audit infrastructure failure/);
});

test('audit parser ignores lower severities and keeps high advisory URLs', () => {
  const findings = summarizeAuditJson({
    vulnerabilities: {
      lowdep: { severity: 'low', via: [{ source: 1, severity: 'low', title: 'low' }] },
      highdep: {
        severity: 'high',
        via: [
          { severity: 'high', title: 'high', url: 'https://github.com/advisories/GHSA-abcd-1234' },
        ],
      },
    },
  });
  assert.deepEqual(
    findings.map(({ dependency, id }) => ({ dependency, id })),
    [{ dependency: 'highdep', id: 'GHSA-abcd-1234' }],
  );
});
