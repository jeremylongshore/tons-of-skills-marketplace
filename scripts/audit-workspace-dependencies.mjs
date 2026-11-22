#!/usr/bin/env node
// GH1814: audit the lock that CI actually installs, without executing package code.
import { createHash } from 'node:crypto';
import {
  constants,
  openSync,
  closeSync,
  fstatSync,
  lstatSync,
  readFileSync,
  readdirSync,
  mkdirSync,
  mkdtempSync,
  writeFileSync,
  rmSync,
} from 'node:fs';
import { dirname, join, resolve, relative, sep } from 'node:path';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import yaml from 'js-yaml';
import {
  parseWorkspacePatterns,
  workspaceIncludes,
  globMatches,
} from './audit-changed-plugin-dependencies.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const LEVELS = ['info', 'low', 'moderate', 'high', 'critical'];
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const object = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);

function readInput(root, path) {
  const full = resolve(root, path);
  if (relative(root, full).split(sep).includes('..')) throw new Error('input_outside_root');
  let current = root;
  for (const part of relative(root, full).split(sep)) {
    current = join(current, part);
    if (lstatSync(current).isSymbolicLink()) throw new Error('symlinked_input');
  }
  const fd = openSync(full, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const before = fstatSync(fd);
    const pathStat = lstatSync(full);
    if (
      !before.isFile() ||
      before.dev !== pathStat.dev ||
      before.ino !== pathStat.ino ||
      before.size > 32 * 1024 * 1024
    )
      throw new Error('invalid_input_file');
    const bytes = readFileSync(fd);
    const after = fstatSync(fd);
    if (before.size !== after.size || before.mtimeMs !== after.mtimeMs)
      throw new Error('input_changed');
    return bytes;
  } finally {
    closeSync(fd);
  }
}

function workspaceMembers(root, patterns) {
  const found = new Set(['.']);
  for (const pattern of patterns) {
    // Deliberately support the current repository's exact paths and single-star
    // segment globs; unknown patterns must not silently omit installed packages.
    if (
      pattern.startsWith('!') ||
      pattern.includes('**') ||
      [...pattern].some((char) => '?{}[]\\'.includes(char) || char.charCodeAt(0) < 32) ||
      pattern.split('/').some((part) => !part || part === '..' || part === '.')
    )
      throw new Error('unsupported_workspace_pattern');
    let parents = [''];
    for (const segment of pattern.split('/')) {
      const next = [];
      for (const parent of parents) {
        for (const entry of readdirSync(join(root, parent), { withFileTypes: true })) {
          if (!globMatches(segment, entry.name)) continue;
          if (entry.isSymbolicLink()) throw new Error('symlinked_workspace_member');
          if (entry.isDirectory()) next.push(parent ? `${parent}/${entry.name}` : entry.name);
        }
      }
      parents = next;
    }
    for (const path of parents) {
      if (!workspaceIncludes(patterns, path)) continue;
      try {
        lstatSync(join(root, path, 'package.json'));
        found.add(path);
      } catch (error) {
        if (error.code !== 'ENOENT') throw error;
      }
    }
  }
  return [...found].sort();
}

export function inventory(root) {
  const inputs = new Map();
  const read = (path) => {
    const bytes = readInput(root, path);
    inputs.set(path, bytes);
    return bytes;
  };
  const workspace = read('pnpm-workspace.yaml');
  const workspaceConfig = yaml.load(workspace.toString());
  if (!object(workspaceConfig) || Object.keys(workspaceConfig).some((key) => key !== 'packages'))
    throw new Error('unsupported_workspace_policy');
  const patterns = parseWorkspacePatterns(workspace.toString());
  const lock = yaml.load(read('pnpm-lock.yaml').toString());
  if (!object(lock) || !object(lock.importers) || !Object.keys(lock.importers).length)
    throw new Error('missing_importers');
  const packages = readdirSync(join(root, 'plugins/mcp'), { withFileTypes: true })
    .filter((entry) => entry.isDirectory() || entry.isSymbolicLink())
    .map((entry) => `plugins/mcp/${entry.name}`)
    .filter((path) => {
      try {
        lstatSync(join(root, path, 'package.json'));
        return true;
      } catch (error) {
        if (error.code === 'ENOENT') return false;
        throw error;
      }
    })
    .sort();
  if (!packages.length) throw new Error('empty_mcp_inventory');
  const coverage = packages.map((path) => ({
    path,
    lock: 'pnpm-lock.yaml',
    importer: path,
    workspaceMember: workspaceIncludes(patterns, path),
    importerPresent: Object.hasOwn(lock.importers, path),
    execution: 'root frozen workspace install; no MCP standalone override',
  }));
  const members = workspaceMembers(root, patterns);
  const importerKeys = Object.keys(lock.importers).sort();
  const workspaceComplete = JSON.stringify(members) === JSON.stringify(importerKeys);
  const manifests = new Map();
  for (const importer of [
    ...new Set([...Object.keys(lock.importers), ...packages, ...members]),
  ].sort()) {
    if (
      importer !== '.' &&
      (importer.startsWith('/') ||
        importer.split('/').some((part) => !part || part === '..' || part === '.') ||
        importer.includes('\\'))
    )
      throw new Error('unsafe_importer');
    const path = importer === '.' ? 'package.json' : `${importer}/package.json`;
    const manifest = JSON.parse(read(path).toString());
    if (!object(manifest) || manifest.pnpm?.auditConfig)
      throw new Error('unsupported_manifest_audit_policy');
    // Keep dependency/override declarations for a frozen-lock coherence check.
    // No executable or registry configuration is copied into the scratch tree.
    const safe = {};
    for (const key of [
      'name',
      'version',
      'private',
      'packageManager',
      'dependencies',
      'devDependencies',
      'optionalDependencies',
      'peerDependencies',
      'peerDependenciesMeta',
      'dependenciesMeta',
      'pnpm',
    ]) {
      if (manifest[key] !== undefined) safe[key] = manifest[key];
    }
    if (
      safe.pnpm &&
      Object.keys(safe.pnpm).some(
        (key) =>
          ![
            'overrides',
            'patchedDependencies',
            'peerDependencyRules',
            'packageExtensions',
            'neverBuiltDependencies',
            'onlyBuiltDependencies',
            'ignoredBuiltDependencies',
          ].includes(key),
      )
    )
      throw new Error('unsupported_pnpm_policy');
    if (safe.pnpm?.patchedDependencies) throw new Error('patch_inputs_require_inventory');
    manifests.set(path, safe);
  }
  return {
    inputs,
    manifests,
    packages,
    coverage,
    members,
    workspaceComplete,
    lockSha256: digest(inputs.get('pnpm-lock.yaml')),
  };
}

export function classify(result) {
  if (result.error || result.signal || ![0, 1].includes(result.status))
    return { state: 'incomplete', reason: 'audit_process_failed' };
  let raw;
  try {
    raw = JSON.parse(result.stdout);
  } catch {
    return { state: 'incomplete', reason: 'audit_invalid_json' };
  }
  if (
    !object(raw) ||
    raw.error ||
    !object(raw.advisories) ||
    !object(raw.metadata?.vulnerabilities)
  )
    return { state: 'incomplete', reason: 'audit_invalid_schema' };
  const counts = raw.metadata.vulnerabilities;
  if (LEVELS.some((level) => !Number.isSafeInteger(counts[level]) || counts[level] < 0))
    return { state: 'incomplete', reason: 'audit_invalid_counts' };
  const observed = Object.fromEntries(LEVELS.map((level) => [level, 0]));
  for (const advisory of Object.values(raw.advisories)) {
    if (
      !object(advisory) ||
      !LEVELS.includes(advisory.severity) ||
      typeof advisory.module_name !== 'string' ||
      !advisory.module_name ||
      !Array.isArray(advisory.findings)
    )
      return { state: 'incomplete', reason: 'audit_invalid_advisory' };
    observed[advisory.severity]++;
  }
  // pnpm9 preserves registry occurrence counts; they need not equal unique advisories.
  if (LEVELS.some((level) => observed[level] > 0 !== counts[level] > 0))
    return { state: 'incomplete', reason: 'audit_count_mismatch' };
  const findings = counts.high + counts.critical > 0;
  if (result.status !== (LEVELS.some((level) => counts[level] > 0) ? 1 : 0))
    return { state: 'incomplete', reason: 'audit_exit_mismatch' };
  return { state: findings ? 'findings' : 'clean', counts, uniqueAdvisories: observed };
}

export function runInventory({
  root = ROOT,
  output,
  run = spawnSync,
  environment = process.env,
} = {}) {
  const startedAt = new Date().toISOString();
  const receipt = {
    schema: 'workspace-audit/v1',
    startedAt,
    scope:
      'entire root pnpm workspace, production plus optional dependencies; high/critical policy',
    state: 'incomplete',
    commands: [],
  };
  let scratch;
  let raw = '';
  const diagnostics = [];
  try {
    const snapshot = inventory(root);
    receipt.lockSha256 = snapshot.lockSha256;
    receipt.inputs = Object.fromEntries(
      [...snapshot.inputs].map(([path, bytes]) => [path, digest(bytes)]),
    );
    receipt.packages = snapshot.coverage;
    receipt.workspaceMembers = snapshot.members;
    if (!snapshot.workspaceComplete) throw new Error('workspace_importers_mismatch');
    if (snapshot.coverage.some((entry) => !entry.workspaceMember || !entry.importerPresent))
      throw new Error('uncovered_packages');
    scratch = mkdtempSync(join(tmpdir(), 'workspace-audit-'));
    const put = (path, data) => {
      const full = join(scratch, path);
      mkdirSync(dirname(full), { recursive: true });
      writeFileSync(full, data, { mode: 0o600 });
    };
    put('pnpm-lock.yaml', snapshot.inputs.get('pnpm-lock.yaml'));
    put('pnpm-workspace.yaml', snapshot.inputs.get('pnpm-workspace.yaml'));
    for (const [path, manifest] of snapshot.manifests) put(path, JSON.stringify(manifest));
    put('empty-userconfig', '');
    put('empty-globalconfig', '');
    const env = {
      PATH: environment.PATH,
      CI: 'true',
      LANG: 'C.UTF-8',
      COREPACK_ENABLE_NETWORK: '0',
      COREPACK_ENABLE_DOWNLOAD_PROMPT: '0',
      npm_config_userconfig: join(scratch, 'empty-userconfig'),
      npm_config_globalconfig: join(scratch, 'empty-globalconfig'),
    };
    const invoke = (args) => {
      receipt.commands.push(['pnpm', ...args]);
      const result = run('pnpm', args, {
        cwd: scratch,
        env,
        encoding: 'utf8',
        timeout: 120000,
        killSignal: 'SIGKILL',
        maxBuffer: 16 * 1024 * 1024,
      });
      diagnostics.push({
        phase: args.includes('--version')
          ? 'version'
          : args.includes('install')
            ? 'coherence'
            : 'audit',
        status: result.status,
        signal: result.signal ?? null,
        errorCode: typeof result.error?.code === 'string' ? result.error.code : null,
        stdout: result.stdout ?? '',
        stderr: result.stderr ?? '',
      });
      return result;
    };
    const version = invoke(['--version']);
    if (version.error || version.status !== 0 || version.stdout.trim() !== '9.15.9')
      throw new Error('unsupported_pnpm_version');
    receipt.pnpm = version.stdout.trim();
    const flags = [
      '--config.registry=https://registry.npmjs.org/',
      '--config.ignore-pnpmfile=true',
    ];
    const coherence = invoke([
      ...flags,
      'install',
      '--offline',
      '--lockfile-only',
      '--frozen-lockfile',
      '--ignore-scripts',
    ]);
    if (coherence.error || coherence.status !== 0) throw new Error('lock_coherence_unproven');
    if (digest(readFileSync(join(scratch, 'pnpm-lock.yaml'))) !== snapshot.lockSha256)
      throw new Error('lock_changed_during_check');
    const result = invoke([
      ...flags,
      '--config.fetch-retries=0',
      '--config.fetch-timeout=30000',
      'audit',
      '--prod',
      '--audit-level=high',
      '--json',
    ]);
    raw = result.stdout ?? '';
    Object.assign(receipt, classify(result), { auditExit: result.status });
    const after = inventory(root);
    if (
      JSON.stringify(after.members) !== JSON.stringify(snapshot.members) ||
      JSON.stringify(after.packages) !== JSON.stringify(snapshot.packages) ||
      JSON.stringify([...after.inputs.keys()]) !== JSON.stringify([...snapshot.inputs.keys()])
    )
      throw new Error('inventory_changed_during_audit');
    for (const [path, bytes] of snapshot.inputs)
      if (digest(after.inputs.get(path)) !== digest(bytes))
        throw new Error('source_changed_during_audit');
  } catch (error) {
    receipt.state = 'incomplete';
    // Do not emit arbitrary tool stderr/config values into the CI console.
    receipt.reason = /^[a-z_]+(?::plugins\/mcp\/[a-z0-9-]+)?$/.test(error.message)
      ? error.message
      : 'inventory_or_io_error';
  } finally {
    if (scratch) rmSync(scratch, { recursive: true, force: true });
  }
  receipt.completedAt = new Date().toISOString();
  receipt.rawAuditSha256 = digest(raw);
  receipt.toolPhases = diagnostics.map(({ phase, status, signal, errorCode }) => ({
    phase,
    status,
    signal,
    errorCode,
  }));
  if (output) {
    mkdirSync(output, { recursive: true });
    writeFileSync(join(output, 'receipt.json'), JSON.stringify(receipt, null, 2) + '\n', {
      mode: 0o600,
    });
    writeFileSync(join(output, 'audit.json'), raw, { mode: 0o600 });
    writeFileSync(
      join(output, 'tool-diagnostics.json'),
      JSON.stringify(diagnostics, null, 2) + '\n',
      { mode: 0o600 },
    );
  }
  return receipt;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  if (args.length !== 2 || args[0] !== '--output')
    throw new Error('Usage: audit-workspace-dependencies.mjs --output DIRECTORY');
  const receipt = runInventory({ output: resolve(args[1]) });
  console.log(
    `workspace-audit: ${receipt.state}; ${receipt.packages?.length ?? 0} MCP packages; ${receipt.reason ?? 'production high/critical inventory'}`,
  );
  process.exitCode = receipt.state === 'clean' ? 0 : receipt.state === 'findings' ? 1 : 2;
}
