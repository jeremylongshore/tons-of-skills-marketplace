#!/usr/bin/env node

/**
 * Canonical skill-corpus resolver.
 *
 * Every caller receives sorted repository-relative SKILL.md paths. Production
 * resolution uses Git's tracked tree so ignored or untracked local files cannot
 * change published counts. Tests may inject an explicit path inventory.
 */

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { resolvePluginProvenance } from './plugin-provenance.mjs';

const require = createRequire(import.meta.url);
const { publishedPlugins } = require('./publication-policy.cjs');

export const CORPUS_COHORTS = Object.freeze([
  'marketplace-visible',
  'graded',
  'first-party',
  'curated-mirror',
  'curriculum',
]);

const EXCLUDED_GRADED_SEGMENTS = new Set([
  '.curated',
  '.experimental',
  '.git',
  '.venv',
  '000-docs',
  '002-workspaces',
  '010-archive',
  '__pycache__',
  'archive',
  'backup',
  'backups',
  'node_modules',
]);

function fail(message) {
  throw new Error(`corpus-resolver: ${message}`);
}

function toPosix(value) {
  return value.split(path.sep).join('/');
}

function normalizePath(value) {
  if (typeof value !== 'string' || value.length === 0 || value.includes('\0')) {
    fail('path inventory contains an invalid entry');
  }
  const normalized = path.posix.normalize(value.replaceAll('\\', '/').replace(/^\.\//, ''));
  if (
    normalized === '..' ||
    normalized.startsWith('../') ||
    path.posix.isAbsolute(normalized) ||
    /^[A-Za-z]:\//.test(normalized)
  ) {
    fail(`path escapes repository: ${value}`);
  }
  return normalized;
}

function trackedPaths(root) {
  if (!fs.existsSync(path.join(root, '.git'))) return filesystemPaths(root);
  try {
    return execFileSync('git', ['ls-files', '--stage', '-z'], {
      cwd: root,
      encoding: 'utf8',
      maxBuffer: 128 * 1024 * 1024,
    })
      .split('\0')
      .filter(Boolean)
      .map((record) => {
        const separator = record.indexOf('\t');
        if (separator < 0) fail('cannot parse tracked tree entry');
        const metadata = record.slice(0, separator).split(' ');
        const entry = record.slice(separator + 1);
        if (metadata.length !== 3 || metadata[2] !== '0') {
          fail(`tracked tree has an unresolved index entry: ${entry}`);
        }
        if (metadata[0] === '120000' && entry.endsWith('/SKILL.md')) {
          fail(`symbolic link is not a corpus authority: ${entry}`);
        }
        return entry;
      });
  } catch (error) {
    if (error instanceof Error && error.message.startsWith('corpus-resolver:')) throw error;
    fail(`cannot read tracked tree: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function filesystemPaths(root) {
  const output = [];
  const walk = (directory) => {
    let entries;
    try {
      entries = fs.readdirSync(directory, { withFileTypes: true });
    } catch (error) {
      fail(
        `cannot read ${toPosix(path.relative(root, directory))}: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
    for (const entry of entries) {
      if (entry.name === '.git' || entry.name === 'node_modules') continue;
      const absolute = path.join(directory, entry.name);
      if (entry.isSymbolicLink())
        fail(`symbolic link is not a corpus authority: ${toPosix(path.relative(root, absolute))}`);
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile()) output.push(toPosix(path.relative(root, absolute)));
    }
  };
  walk(root);
  return output;
}

function skillPaths(paths) {
  return [...new Set(paths.map(normalizePath).filter((entry) => entry.endsWith('/SKILL.md')))].sort(
    (left, right) => left.localeCompare(right),
  );
}

function assertSuppliedSkillPaths(root, entries) {
  const inspected = new Map();
  for (const entry of entries) {
    let candidate = root;
    const segments = entry.split('/');
    for (const [index, segment] of segments.entries()) {
      candidate = path.join(candidate, segment);
      let metadata = inspected.get(candidate);
      if (!metadata) {
        try {
          metadata = fs.lstatSync(candidate);
        } catch (error) {
          fail(
            `cannot inspect supplied path ${entry}: ${error instanceof Error ? error.message : String(error)}`,
          );
        }
        inspected.set(candidate, metadata);
      }
      if (metadata.isSymbolicLink()) {
        fail(`symbolic link is not a corpus authority: ${entry}`);
      }
      const finalSegment = index === segments.length - 1;
      if ((finalSegment && !metadata.isFile()) || (!finalSegment && !metadata.isDirectory())) {
        fail(`supplied path is not a regular repository file: ${entry}`);
      }
    }
  }
}

function readCatalog(root) {
  const catalogPath = path.join(root, '.claude-plugin', 'marketplace.extended.json');
  let catalog;
  try {
    catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  } catch (error) {
    fail(
      `cannot read marketplace catalog: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  if (!Array.isArray(catalog?.plugins)) fail('marketplace catalog has no plugins array');

  const names = new Set();
  const roots = new Set();
  for (const [index, plugin] of publishedPlugins(catalog.plugins, 'extended catalog').entries()) {
    if (typeof plugin?.name !== 'string' || plugin.name.length === 0) {
      fail(`catalog plugin ${index} has no name`);
    }
    names.add(plugin.name);
    if (typeof plugin.source !== 'string') fail(`catalog plugin ${index} has no source path`);
    const source = normalizePath(plugin.source);
    if (!source.startsWith('plugins/')) {
      fail(`catalog plugin ${index} source is outside plugins/: ${plugin.source}`);
    }
    const pluginRoot = source.replace(/\/$/, '');
    roots.add(pluginRoot);
  }
  return { names, roots };
}

function isPluginSkill(entry) {
  return entry.startsWith('plugins/');
}

function isCurriculumSkill(entry) {
  if (!entry.startsWith('skills/')) return false;
  const segments = entry.split('/');
  return (
    /^\d{2}-/.test(segments[1] ?? '') && !segments.some((segment) => segment === '.experimental')
  );
}

function isLegacySkill(entry) {
  return entry.startsWith('003-skills/') && entry.endsWith('/SKILL.md');
}

// Grading intentionally includes hidden harness adapter trees such as .codex/.
// Visibility is a separate marketplace cohort rule; promotion remains safe by
// intersecting graded paths with the provenance-derived first-party cohort.
function isGradedSkill(entry) {
  if (!isPluginSkill(entry) && !isCurriculumSkill(entry) && !isLegacySkill(entry)) return false;
  const segments = entry.split('/');
  if (segments.some((segment) => EXCLUDED_GRADED_SEGMENTS.has(segment))) return false;
  if (segments.some((segment) => segment.startsWith('skills-backup-'))) return false;

  if (isCurriculumSkill(entry) || isLegacySkill(entry)) return true;
  const atPluginRoot = /^plugins\/[^/]+\/[^/]+\/SKILL\.md$/.test(entry);
  const inSkillDirectory = /\/skills\/[^/]+\/SKILL\.md$/.test(entry);
  return atPluginRoot || inSkillDirectory;
}

function marketplacePluginName(entry, root) {
  const segments = entry.split('/');
  let current = path.dirname(path.join(root, entry));
  // The bound is defensive; declared plugin roots are no more than four
  // levels deep today, while malformed ancestry must never walk indefinitely.
  for (let depth = 0; depth < 10 && current.startsWith(root); depth += 1) {
    const manifest = path.join(current, '.claude-plugin', 'plugin.json');
    if (fs.existsSync(manifest)) {
      const relative = toPosix(path.relative(root, current));
      const parts = relative.split('/');
      const skillsIndex = parts.indexOf('skills');
      // A manifest at a plugin root (or directly below a bare skills/ tree)
      // owns the plugin identity; manifests nested inside a skill do not.
      if (skillsIndex < 0 || skillsIndex === parts.length - 1) {
        let value;
        try {
          value = JSON.parse(fs.readFileSync(manifest, 'utf8'));
        } catch (error) {
          fail(
            `cannot read plugin manifest ${relative}/.claude-plugin/plugin.json: ${error instanceof Error ? error.message : String(error)}`,
          );
        }
        return typeof value?.name === 'string' && value.name.length > 0
          ? value.name
          : path.basename(current);
      }
    }
    if (current === root) break;
    current = path.dirname(current);
  }
  // Manifest-free fixtures and legacy roots encode the plugin in their path.
  const skillsIndex = segments.indexOf('skills');
  if (skillsIndex >= 2) return segments[skillsIndex - 1];
  return segments.length >= 3 ? segments[2] : null;
}

function marketplaceVisible(entries, root) {
  const catalog = readCatalog(root);
  return entries.filter((entry) => {
    if (!isPluginSkill(entry)) return false;
    const segments = entry.split('/');
    if (segments.some((segment) => segment.startsWith('.'))) return false;
    const withinCatalogSource = [...catalog.roots].some(
      (pluginRoot) => entry === `${pluginRoot}/SKILL.md` || entry.startsWith(`${pluginRoot}/`),
    );
    if (!withinCatalogSource) return false;
    const pluginName = marketplacePluginName(entry, root);
    return pluginName !== null && catalog.names.has(pluginName);
  });
}

function firstParty(entries, root) {
  const output = [];
  // Provenance is intentionally resolved per skill so nested markers cannot be
  // missed; this is the slowest cohort, but correctness outranks scan speed.
  for (const entry of entries.filter(isPluginSkill)) {
    const result = resolvePluginProvenance(path.posix.dirname(entry), { root });
    if (result.status === 'refused') {
      fail(`${result.reasonCode} while resolving ${entry}`);
    }
    if (result.status === 'first-party') output.push(entry);
  }
  return output;
}

function curatedMirror(entries, root, inventory) {
  const files = entries.filter((entry) => entry.startsWith('skills/.curated/'));
  if (!inventory.includes('skills/.curated/MANIFEST.json')) {
    if (files.length > 0) fail('curated-mirror files exist without a tracked MANIFEST.json');
    return files;
  }

  let manifest;
  try {
    manifest = JSON.parse(
      fs.readFileSync(path.join(root, 'skills', '.curated', 'MANIFEST.json'), 'utf8'),
    );
  } catch (error) {
    fail(`cannot read curated manifest: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!Array.isArray(manifest?.skills) || manifest.count !== manifest.skills.length) {
    fail('curated manifest count contradicts its skill rows');
  }
  const declared = manifest.skills.map((entry, index) => {
    if (typeof entry?.curated_name !== 'string' || entry.curated_name.length === 0) {
      fail(`curated manifest row ${index} has no curated_name`);
    }
    return `skills/.curated/${entry.curated_name}/SKILL.md`;
  });
  const declaredSet = new Set(declared);
  const fileSet = new Set(files);
  if (
    declaredSet.size !== declared.length ||
    declaredSet.size !== fileSet.size ||
    declared.some((entry) => !fileSet.has(entry))
  ) {
    fail('curated manifest membership contradicts the tracked curated-mirror cohort');
  }
  return files;
}

/**
 * Every tracked repository path (POSIX, repository-relative). Falls back to a
 * filesystem walk outside a git checkout, exactly as resolveCorpus does.
 */
export function listTrackedPaths(root = process.cwd()) {
  let rootPath;
  try {
    rootPath = fs.realpathSync(path.resolve(root));
  } catch (error) {
    fail(
      `cannot resolve repository root: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  return trackedPaths(rootPath).map(normalizePath);
}

export function resolveCorpus(cohort, { root = process.cwd(), paths } = {}) {
  if (!CORPUS_COHORTS.includes(cohort)) {
    fail(`unknown cohort ${JSON.stringify(cohort)}; expected ${CORPUS_COHORTS.join(', ')}`);
  }
  let rootPath;
  try {
    rootPath = fs.realpathSync(path.resolve(root));
  } catch (error) {
    fail(
      `cannot resolve repository root: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  const inventory = (paths ?? trackedPaths(rootPath)).map(normalizePath);
  const entries = skillPaths(inventory);
  if (paths !== undefined) assertSuppliedSkillPaths(rootPath, entries);

  switch (cohort) {
    case 'marketplace-visible':
      return marketplaceVisible(entries, rootPath);
    case 'graded':
      return entries.filter(isGradedSkill);
    case 'first-party':
      return firstParty(entries, rootPath);
    case 'curated-mirror':
      return curatedMirror(entries, rootPath, inventory);
    case 'curriculum':
      return entries.filter(isCurriculumSkill);
    default:
      fail(`unreachable cohort ${cohort}`);
  }
}

function parseCli(argv) {
  const options = { cohorts: [], root: process.cwd() };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--cohort') options.cohorts.push(argv[++index]);
    else if (argument.startsWith('--cohort='))
      options.cohorts.push(argument.slice('--cohort='.length));
    else if (argument === '--root') options.root = argv[++index];
    else if (argument.startsWith('--root=')) options.root = argument.slice('--root='.length);
    else if (argument !== '--json') fail(`unknown argument ${argument}`);
  }
  if (options.cohorts.length === 0 || options.cohorts.some((cohort) => !cohort)) {
    fail('--cohort is required');
  }
  if (new Set(options.cohorts).size !== options.cohorts.length) {
    fail('duplicate --cohort values are not allowed');
  }
  return options;
}

const invokedPath = process.argv[1] ? path.resolve(process.argv[1]) : null;
if (invokedPath === fileURLToPath(import.meta.url)) {
  try {
    const options = parseCli(process.argv.slice(2));
    const resolved = options.cohorts.map((cohort) => {
      const files = resolveCorpus(cohort, { root: options.root });
      return { cohort, count: files.length, files };
    });
    const payload =
      resolved.length === 1
        ? resolved[0]
        : { cohorts: Object.fromEntries(resolved.map((entry) => [entry.cohort, entry])) };
    process.stdout.write(`${JSON.stringify(payload)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}
