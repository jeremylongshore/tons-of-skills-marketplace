#!/usr/bin/env node
/** Audit the shared production lock once, with explicit MCP importer coverage. */
import { createHash } from 'node:crypto';
import { existsSync, lstatSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import yaml from 'js-yaml';
import {
  parseWorkspacePatterns,
  summarizeAuditJson,
  workspaceIncludes,
} from './audit-changed-plugin-dependencies.mjs';

const fields = ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies'];
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

export function inventory(repoRoot) {
  const lockBytes = readFileSync(join(repoRoot, 'pnpm-lock.yaml'));
  const lock = yaml.load(lockBytes.toString());
  if (!lock?.importers || typeof lock.importers !== 'object') {
    throw new Error('Shared pnpm lock has no importer inventory');
  }
  const patterns = parseWorkspacePatterns(
    readFileSync(join(repoRoot, 'pnpm-workspace.yaml'), 'utf8'),
  );
  const packages = [];
  for (const entry of readdirSync(join(repoRoot, 'plugins/mcp'), { withFileTypes: true })) {
    if (entry.isSymbolicLink()) throw new Error(`MCP directory is a symlink: ${entry.name}`);
    if (!entry.isDirectory()) continue;
    const root = `plugins/mcp/${entry.name}`;
    const manifestPath = join(repoRoot, root, 'package.json');
    if (!existsSync(manifestPath)) continue;
    if (lstatSync(manifestPath).isSymbolicLink())
      throw new Error(`MCP manifest is a symlink: ${root}`);
    const bytes = readFileSync(manifestPath);
    const manifest = JSON.parse(bytes);
    const hasDependencies = fields.some((field) => Object.keys(manifest[field] ?? {}).length > 0);
    const row = { root, manifestSha256: sha256(bytes), status: 'no-node-dependencies' };
    if (hasDependencies) {
      if (!workspaceIncludes(patterns, root) || !Object.hasOwn(lock.importers, root)) {
        row.status = 'uncovered';
        row.reason = 'Dependency-bearing MCP package lacks a shared-lock importer';
      } else {
        row.status = 'shared-workspace-lock';
        // A matching importer name alone is not coverage of the current manifest.
        const importer = lock.importers[root];
        for (const field of ['dependencies', 'devDependencies', 'optionalDependencies']) {
          const declared = manifest[field] ?? {};
          const locked = importer[field] ?? {};
          if (
            Object.keys(declared).length !== Object.keys(locked).length ||
            Object.keys(declared).some((name) => !Object.hasOwn(locked, name))
          ) {
            row.status = 'uncovered';
            row.reason = `Shared-lock ${field} do not match the manifest`;
          }
        }
        if (Object.keys(manifest.peerDependencies ?? {}).length > 0) {
          row.status = 'uncovered';
          row.reason = 'Peer dependency coverage requires a separately reviewed consumer graph';
        }
      }
    }
    packages.push(row);
  }
  return {
    schemaVersion: 1,
    scope:
      'entire shared workspace production lock; findings are not attributed to individual MCP packages',
    lock: { path: 'pnpm-lock.yaml', sha256: sha256(lockBytes) },
    packages: packages.sort((a, b) => a.root.localeCompare(b.root)),
  };
}

export function runInventory(repoRoot, run = spawnSync) {
  const report = inventory(repoRoot);
  const env = Object.fromEntries(
    Object.entries(process.env).filter(
      ([key]) => !/^(npm_config_|https?_proxy$|all_proxy$|no_proxy$)/i.test(key),
    ),
  );
  // Delegate specifier/override semantics to pnpm, rather than reimplementing
  // selectors (the root security overrides legitimately change specifiers).
  const lockCheck = run(
    'pnpm',
    [
      'install',
      '--frozen-lockfile',
      '--lockfile-only',
      '--ignore-scripts',
      '--ignore-pnpmfile',
      '--config.registry=https://registry.npmjs.org/',
    ],
    {
      cwd: repoRoot,
      env: { ...env, CI: 'true' },
      encoding: 'utf8',
      timeout: 120000,
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  if (
    lockCheck.error ||
    lockCheck.status !== 0 ||
    sha256(readFileSync(join(repoRoot, 'pnpm-lock.yaml'))) !== report.lock.sha256
  ) {
    report.audit = {
      status: 'incomplete',
      reason: 'Shared lock failed frozen validation or changed during validation',
    };
    return report;
  }
  const result = run(
    'pnpm',
    [
      '--config.ignore-pnpmfile=true',
      '--config.registry=https://registry.npmjs.org/',
      'audit',
      '--prod',
      '--audit-level',
      'high',
      '--json',
    ],
    {
      cwd: repoRoot,
      env: { ...env, CI: 'true' },
      encoding: 'utf8',
      timeout: 120000,
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  let audit;
  try {
    audit = JSON.parse(result.stdout);
  } catch {
    report.audit = { status: 'incomplete', reason: 'Audit returned no valid JSON' };
    return report;
  }
  const counts = audit?.metadata?.vulnerabilities;
  const validCounts =
    counts &&
    ['info', 'low', 'moderate', 'high', 'critical'].every(
      (key) => Number.isSafeInteger(counts[key]) && counts[key] >= 0,
    );
  const findings = summarizeAuditJson(audit);
  const severities = ['info', 'low', 'moderate', 'high', 'critical'];
  const advisories = audit?.advisories;
  const completeAdvisories =
    advisories &&
    typeof advisories === 'object' &&
    !Array.isArray(advisories) &&
    Object.values(advisories).every(
      (entry) =>
        entry &&
        severities.includes(entry.severity) &&
        typeof entry.module_name === 'string' &&
        entry.module_name.trim().length > 0 &&
        ((typeof entry.github_advisory_id === 'string' &&
          entry.github_advisory_id.trim().length > 0) ||
          (typeof entry.id === 'string' && entry.id.trim().length > 0) ||
          (Number.isSafeInteger(entry.id) && entry.id >= 0)),
    ) &&
    validCounts &&
    severities.every(
      (severity) =>
        Object.values(advisories).filter((entry) => entry.severity === severity).length ===
        counts[severity],
    );
  const total = validCounts ? Object.values(counts).reduce((sum, count) => sum + count, 0) : 0;
  if (
    result.error ||
    ![0, 1].includes(result.status) ||
    audit.error ||
    !validCounts ||
    !completeAdvisories ||
    result.status !== (total > 0 ? 1 : 0)
  ) {
    report.audit = {
      status: 'incomplete',
      reason: 'Audit failed or returned inconsistent evidence',
      findings,
    };
  } else {
    report.audit = {
      status: findings.length ? 'findings' : 'below-high-threshold',
      counts,
      findings,
    };
  }
  return report;
}

export function exitCode(report) {
  // Findings remain advisory. Missing coverage or audit evidence is not a clean scan.
  return report.audit.status === 'incomplete' ||
    report.packages.some((row) => row.status === 'uncovered')
    ? 1
    : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const report = runInventory(process.cwd());
    const output = `${JSON.stringify(report, null, 2)}\n`;
    const outputPath = process.argv.find((arg) => arg.startsWith('--output='))?.slice(9);
    if (outputPath) writeFileSync(outputPath, output);
    console.log(output);
    if (report.audit.status === 'findings') {
      console.log(
        '::warning::Shared workspace production audit has high/critical findings; see retained JSON. Findings are not MCP-specific.',
      );
    }
    process.exitCode = exitCode(report);
  } catch (error) {
    console.error(`MCP dependency inventory incomplete: ${error.message}`);
    process.exitCode = 1;
  }
}
