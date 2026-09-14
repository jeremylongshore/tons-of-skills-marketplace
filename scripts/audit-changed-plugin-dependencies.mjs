#!/usr/bin/env node
/**
 * Diff-scoped dependency auditing for standalone plugin packages.
 *
 * The root workspace lock covers workspace members. Package-bearing plugins
 * outside that workspace need their own lock and audit lane; otherwise CI may
 * execute a dependency tree that neither Dependabot nor the existing MCP-only
 * audit step can see. This script deliberately audits only changed standalone
 * plugin roots so an unrelated advisory cannot red-wall every pull request.
 */

import {
  closeSync,
  constants,
  existsSync,
  fstatSync,
  lstatSync,
  openSync,
  readFileSync,
  readdirSync,
} from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import yaml from 'js-yaml';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const DEFAULT_ROOT = resolve(SCRIPT_DIR, '..');
const LOCK_NAMES = ['pnpm-lock.yaml', 'package-lock.json', 'npm-shrinkwrap.json', 'yarn.lock'];
const DEPENDENCY_FIELDS = [
  'dependencies',
  'devDependencies',
  'optionalDependencies',
  'peerDependencies',
];

function normalizePath(value) {
  return value.split(sep).join('/').replace(/^\.\//, '').replace(/\/$/, '');
}

function readRegularNonSymlinkFile(path, label) {
  let descriptor;
  try {
    descriptor = openSync(path, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
    const openedStat = fstatSync(descriptor);
    const pathStat = lstatSync(path);
    if (
      !openedStat.isFile() ||
      pathStat.isSymbolicLink() ||
      !pathStat.isFile() ||
      openedStat.dev !== pathStat.dev ||
      openedStat.ino !== pathStat.ino
    ) {
      throw new Error(`${label} must be a stable regular non-symlink file`);
    }
    return readFileSync(descriptor, 'utf8');
  } catch (error) {
    if (error?.code === 'ELOOP') {
      throw new Error(`${label} must be a stable regular non-symlink file`, { cause: error });
    }
    throw error;
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
  }
}

export function parseWorkspacePatterns(text) {
  const parsed = yaml.load(text);
  if (!parsed || !Array.isArray(parsed.packages)) {
    throw new Error('pnpm-workspace.yaml must contain a packages array');
  }
  if (parsed.packages.some((pattern) => typeof pattern !== 'string' || pattern.trim() === '')) {
    throw new Error('pnpm-workspace.yaml package patterns must be non-empty strings');
  }
  return parsed.packages.map((pattern) => {
    const negated = pattern.startsWith('!');
    const normalized = normalizePath(negated ? pattern.slice(1) : pattern);
    return negated ? `!${normalized}` : normalized;
  });
}

export function globMatches(pattern, candidate) {
  const normalizedPattern = pattern.startsWith('!') ? pattern.slice(1) : pattern;
  const marker = '__DOUBLE_STAR__';
  const escaped = normalizedPattern
    .replace(/[.+?^${}()|[\]\\]/g, '\\$&')
    .replaceAll('**', marker)
    .replaceAll('*', '[^/]*')
    .replaceAll(marker, '.*');
  return new RegExp(`^${escaped}$`).test(normalizePath(candidate));
}

export function workspaceIncludes(patterns, candidate) {
  let included = false;
  for (const pattern of patterns) {
    const negated = pattern.startsWith('!');
    if (globMatches(pattern, candidate)) included = !negated;
  }
  return included;
}

function packageRoots(repoRoot) {
  const pluginsRoot = join(repoRoot, 'plugins');
  if (!existsSync(pluginsRoot)) return [];
  const roots = [];
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === 'node_modules' || entry.name === '.git') continue;
      const absolute = join(directory, entry.name);
      if (entry.isSymbolicLink()) {
        if (entry.name === 'package.json') {
          roots.push(normalizePath(relative(repoRoot, directory)));
        }
        continue;
      }
      if (entry.isDirectory()) {
        visit(absolute);
      } else if (entry.isFile() && entry.name === 'package.json') {
        roots.push(normalizePath(relative(repoRoot, directory)));
      }
    }
  };
  visit(pluginsRoot);
  return roots.sort((a, b) => b.length - a.length || a.localeCompare(b));
}

function assertChangedPluginPathsAreNotSymlinked(repoRoot, changedPaths) {
  for (const changedPath of changedPaths) {
    const normalized = normalizePath(changedPath);
    if (!normalized.startsWith('plugins/')) continue;
    let current = repoRoot;
    for (const part of normalized.split('/')) {
      current = join(current, part);
      let stat;
      try {
        stat = lstatSync(current);
      } catch (error) {
        if (error?.code === 'ENOENT') break;
        throw error;
      }
      if (stat.isSymbolicLink()) {
        throw new Error(
          `${normalized} traverses symlink ${normalizePath(relative(repoRoot, current))}`,
        );
      }
    }
  }
}

export function packageRootFor(changedPath, knownPackageRoots) {
  const normalized = normalizePath(changedPath);
  if (normalized.split('/').some((part) => part === '..')) return null;
  return (
    knownPackageRoots.find(
      (root) => normalized === `${root}/package.json` || normalized.startsWith(`${root}/`),
    ) ?? null
  );
}

function hasAuditableDependencies(manifest) {
  return DEPENDENCY_FIELDS.some((field) => {
    const value = manifest[field];
    return value && typeof value === 'object' && Object.keys(value).length > 0;
  });
}

export function discoverChangedStandalonePackages({ repoRoot, changedPaths }) {
  if (changedPaths.map(normalizePath).includes('pnpm-workspace.yaml')) {
    throw new Error(
      'pnpm-workspace.yaml changes require a dedicated workspace-boundary review; ' +
        'the standalone audit will not trust PR-controlled package reclassification',
    );
  }
  const workspacePath = join(repoRoot, 'pnpm-workspace.yaml');
  const workspacePatterns = existsSync(workspacePath)
    ? parseWorkspacePatterns(readFileSync(workspacePath, 'utf8'))
    : [];
  assertChangedPluginPathsAreNotSymlinked(repoRoot, changedPaths);
  const knownPackageRoots = packageRoots(repoRoot);
  const roots = [
    ...new Set(changedPaths.map((path) => packageRootFor(path, knownPackageRoots)).filter(Boolean)),
  ].sort();
  const packages = [];

  for (const root of roots) {
    const manifestPath = join(repoRoot, root, 'package.json');
    if (workspaceIncludes(workspacePatterns, root)) continue;
    const manifest = JSON.parse(readRegularNonSymlinkFile(manifestPath, `${root}/package.json`));
    if (!hasAuditableDependencies(manifest)) continue;
    packages.push({ root, manifestPath, manifest });
  }
  return packages;
}

export function resolvePackageLock(repoRoot, packageRoot) {
  const directory = join(repoRoot, packageRoot);
  const found = LOCK_NAMES.filter((name) => {
    const lockPath = join(directory, name);
    if (!existsSync(lockPath)) return false;
    const stat = lstatSync(lockPath);
    if (!stat.isFile() || stat.isSymbolicLink()) {
      throw new Error(`${packageRoot}/${name} must be a regular non-symlink file`);
    }
    return true;
  });
  if (found.length === 0) {
    return {
      ok: false,
      error:
        `${packageRoot}/package.json has dependencies but no package-local lockfile. ` +
        'Generate and commit pnpm-lock.yaml or package-lock.json from that directory.',
    };
  }
  if (found.length > 1) {
    return {
      ok: false,
      error: `${packageRoot} has multiple lockfiles (${found.join(', ')}); retain exactly one authoritative lock.`,
    };
  }
  const name = found[0];
  if (name === 'yarn.lock') {
    return {
      ok: false,
      error:
        `${packageRoot}/yarn.lock is not supported by this pnpm/npm audit lane; ` +
        'migrate to an authoritative pnpm or npm lock or extend the audited implementation.',
    };
  }
  return { ok: true, name, manager: name === 'pnpm-lock.yaml' ? 'pnpm' : 'npm' };
}

function advisoryId(via) {
  if (typeof via?.url === 'string') return via.url.split('/').filter(Boolean).at(-1) || via.url;
  if (typeof via?.source === 'number' || typeof via?.source === 'string') return String(via.source);
  return 'unknown-advisory';
}

export function summarizeAuditJson(value) {
  const findings = [];
  for (const detail of Object.values(value?.advisories ?? {})) {
    const severity = String(detail?.severity ?? 'unknown').toLowerCase();
    if (!['critical', 'high'].includes(severity)) continue;
    const dependencyPaths = Array.isArray(detail?.findings)
      ? detail.findings.flatMap((finding) =>
          Array.isArray(finding?.paths) ? finding.paths.map(String) : [],
        )
      : [];
    findings.push({
      dependency: String(detail?.module_name ?? 'unknown-dependency'),
      severity,
      id: String(detail?.github_advisory_id ?? detail?.id ?? 'unknown-advisory'),
      title: String(detail?.title ?? detail?.module_name ?? 'dependency advisory'),
      url: typeof detail?.url === 'string' ? detail.url : '',
      dependencyPaths: [...new Set(dependencyPaths)].sort(),
    });
  }
  for (const [dependency, detail] of Object.entries(value?.vulnerabilities ?? {})) {
    const severity = String(detail?.severity ?? 'unknown').toLowerCase();
    if (!['critical', 'high'].includes(severity)) continue;
    const advisoryObjects = Array.isArray(detail?.via)
      ? detail.via.filter((entry) => entry && typeof entry === 'object')
      : [];
    const dependencyPaths = Array.isArray(detail?.nodes)
      ? [...new Set(detail.nodes.map(String))].sort()
      : [];
    if (advisoryObjects.length === 0) {
      findings.push({
        dependency,
        severity,
        id: 'unknown-advisory',
        title: dependency,
        dependencyPaths,
      });
      continue;
    }
    for (const via of advisoryObjects) {
      const viaSeverity = String(via.severity ?? severity).toLowerCase();
      if (!['critical', 'high'].includes(viaSeverity)) continue;
      findings.push({
        dependency,
        severity: viaSeverity,
        id: advisoryId(via),
        title: String(via.title ?? via.name ?? dependency),
        url: typeof via.url === 'string' ? via.url : '',
        dependencyPaths,
      });
    }
  }
  return findings.sort((a, b) =>
    `${a.severity}:${a.dependency}:${a.id}`.localeCompare(`${b.severity}:${b.dependency}:${b.id}`),
  );
}

function safeAnnotation(value) {
  return String(value).replaceAll('%', '%25').replaceAll('\r', '%0D').replaceAll('\n', '%0A');
}

function auditCommands(manager, directory) {
  if (manager === 'pnpm') {
    return {
      lockCheck: {
        command: 'pnpm',
        args: [
          '--dir',
          directory,
          'install',
          '--ignore-workspace',
          '--frozen-lockfile',
          '--lockfile-only',
          '--ignore-scripts',
          '--ignore-pnpmfile',
          '--config.registry=https://registry.npmjs.org/',
        ],
      },
      audits: [
        {
          scope: 'production',
          command: 'pnpm',
          args: [
            '--dir',
            directory,
            '--ignore-workspace',
            '--config.ignore-pnpmfile=true',
            '--config.registry=https://registry.npmjs.org/',
            'audit',
            '--prod',
            '--audit-level',
            'high',
            '--json',
          ],
        },
        {
          scope: 'full',
          command: 'pnpm',
          args: [
            '--dir',
            directory,
            '--ignore-workspace',
            '--config.ignore-pnpmfile=true',
            '--config.registry=https://registry.npmjs.org/',
            'audit',
            '--audit-level',
            'high',
            '--json',
          ],
        },
      ],
    };
  }
  return {
    lockCheck: {
      command: 'npm',
      args: ['ci', '--ignore-scripts', '--no-audit', '--registry=https://registry.npmjs.org/'],
      cwd: directory,
    },
    audits: [
      {
        scope: 'production',
        command: 'npm',
        args: [
          'audit',
          '--omit=dev',
          '--audit-level=high',
          '--json',
          '--registry=https://registry.npmjs.org/',
        ],
        cwd: directory,
      },
      {
        scope: 'full',
        command: 'npm',
        args: ['audit', '--audit-level=high', '--json', '--registry=https://registry.npmjs.org/'],
        cwd: directory,
      },
    ],
  };
}

function invoke(run, spec) {
  const environment = Object.fromEntries(
    Object.entries(process.env).filter(
      ([name]) =>
        !/^(?:npm_config_|https?_proxy$|all_proxy$|no_proxy$|corepack_|pnpm_home$)/i.test(name),
    ),
  );
  return run(spec.command, spec.args, {
    cwd: spec.cwd,
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
    env: { ...environment, CI: 'true' },
  });
}

export function auditStandalonePackage({
  repoRoot,
  packageInfo,
  run = spawnSync,
  reportOnly = true,
}) {
  const lock = resolvePackageLock(repoRoot, packageInfo.root);
  if (!lock.ok) return { ok: false, hardFailure: true, messages: [lock.error], findings: [] };

  const directory = join(repoRoot, packageInfo.root);
  if (existsSync(join(directory, '.npmrc'))) {
    return {
      ok: false,
      hardFailure: true,
      messages: [
        `${packageInfo.root}/.npmrc is not allowed in a standalone audited package; ` +
          'package-local registry configuration can redirect or falsify dependency audits.',
      ],
      findings: [],
    };
  }
  const commands = auditCommands(lock.manager, directory);
  const lockResult = invoke(run, commands.lockCheck);
  if (lockResult.error || lockResult.status !== 0) {
    return {
      ok: false,
      hardFailure: true,
      messages: [
        `${packageInfo.root}/${lock.name} is stale or not reproducible with lifecycle scripts disabled. ` +
          `Regenerate it with ${lock.manager} and commit the exact lockfile.`,
      ],
      findings: [],
    };
  }

  const findings = [];
  const messages = [];
  let auditFailed = false;
  for (const spec of commands.audits) {
    const result = invoke(run, spec);
    if (result.error || result.status === null) {
      return {
        ok: false,
        hardFailure: true,
        messages: [`${packageInfo.root}: ${spec.scope} audit command could not execute.`],
        findings,
      };
    }
    let parsed;
    try {
      parsed = JSON.parse(result.stdout || '{}');
    } catch {
      return {
        ok: false,
        hardFailure: true,
        messages: [`${packageInfo.root}: ${spec.scope} audit did not return valid JSON.`],
        findings,
      };
    }
    const scoped = summarizeAuditJson(parsed).map((finding) => ({ ...finding, scope: spec.scope }));
    findings.push(...scoped);
    if (parsed?.error || (result.status !== 0 && scoped.length === 0)) {
      return {
        ok: false,
        hardFailure: true,
        messages: [
          `${packageInfo.root}: ${spec.scope} audit failed without parseable high/critical findings; ` +
            'treat this as an audit infrastructure failure, not a clean result.',
        ],
        findings,
      };
    }
    if (result.error || result.status !== 0 || scoped.length > 0) auditFailed = true;
  }
  for (const finding of findings) {
    const pathSummary = finding.dependencyPaths?.length
      ? ` paths=${finding.dependencyPaths.slice(0, 3).join(' | ')}${
          finding.dependencyPaths.length > 3 ? ` | +${finding.dependencyPaths.length - 3} more` : ''
        }`
      : '';
    messages.push(
      `${packageInfo.root} ${finding.scope}: ${finding.severity} ${finding.dependency} ` +
        `[${finding.id}] ${finding.title}${finding.url ? ` ${finding.url}` : ''}${pathSummary}`,
    );
  }
  return {
    ok: !auditFailed || reportOnly,
    hardFailure: false,
    reportOnlyFailure: auditFailed && reportOnly,
    messages,
    findings,
  };
}

export function changedPathsFromGit(
  repoRoot,
  base,
  head = 'HEAD',
  run = spawnSync,
  diffMode = 'three-dot',
) {
  if (!base) throw new Error('--base=<git-ref> is required');
  if (!['two-dot', 'three-dot'].includes(diffMode)) {
    throw new Error('--diff-mode must be two-dot or three-dot');
  }
  const separator = diffMode === 'two-dot' ? '..' : '...';
  const result = run(
    'git',
    ['diff', '--name-only', '--diff-filter=ACMRDT', '-z', `${base}${separator}${head}`],
    {
      cwd: repoRoot,
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  if (result.error || result.status !== 0) {
    throw new Error(`cannot resolve changed files for ${base}${separator}${head}`);
  }
  return result.stdout.split('\0').filter(Boolean);
}

function argument(name, fallback = '') {
  const prefix = `--${name}=`;
  return process.argv.find((value) => value.startsWith(prefix))?.slice(prefix.length) ?? fallback;
}

export function main() {
  const repoRoot = resolve(argument('repo-root', DEFAULT_ROOT));
  const base = argument('base', 'origin/main');
  const head = argument('head', 'HEAD');
  const diffMode = argument('diff-mode', 'three-dot');
  const blocking = process.argv.includes('--blocking');
  let changedPaths;
  try {
    changedPaths = changedPathsFromGit(repoRoot, base, head, spawnSync, diffMode);
  } catch (error) {
    console.error(`changed-plugin-deps: STRUCTURAL — ${error.message}`);
    return 1;
  }

  let packages;
  try {
    packages = discoverChangedStandalonePackages({ repoRoot, changedPaths });
  } catch (error) {
    console.error(`changed-plugin-deps: STRUCTURAL — ${error.message}`);
    return 1;
  }
  if (packages.length === 0) {
    console.log('changed-plugin-deps: OK — no changed standalone plugin dependency roots.');
    return 0;
  }

  let failed = false;
  for (const packageInfo of packages) {
    console.log(`changed-plugin-deps: auditing ${packageInfo.root}`);
    const result = auditStandalonePackage({ repoRoot, packageInfo, reportOnly: !blocking });
    for (const message of result.messages) {
      const level = result.hardFailure || blocking ? 'error' : 'warning';
      console.log(
        `::${level} file=${safeAnnotation(`${packageInfo.root}/package.json`)}::${safeAnnotation(message)}`,
      );
    }
    if (!result.ok) failed = true;
  }
  if (failed) {
    console.error(
      'changed-plugin-deps: FAIL — resolve the package-local lock or blocking audit findings above.',
    );
    return 1;
  }
  console.log(
    `changed-plugin-deps: OK — audited ${packages.length} changed standalone package(s)` +
      (blocking
        ? ' in blocking mode.'
        : '; high/critical findings are report-only until the documented deadline.'),
  );
  return 0;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (isMain) process.exit(main());
