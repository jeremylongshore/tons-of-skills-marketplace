#!/usr/bin/env node
/**
 * Generate the deterministic denominator and ordered review queue for the
 * repeated SaaS tutorial lattice tracked by Bead claude-juoz.3.11.
 *
 * A family-name match is a review signal, never a quality verdict. Final
 * KEEP/DEEPEN/REPLACE/RETIRE decisions require pack-specific evidence.
 */

import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

import { resolveCorpus } from './corpus-resolver.mjs';
import { assertGeneratedContentCurrent } from './check-generated-artifacts.mjs';
import { resolvePluginProvenance } from './plugin-provenance.mjs';
import { parseFrontmatter } from '../marketplace/scripts/discover-skills.mjs';

const require = createRequire(import.meta.url);
const { publishedPlugins } = require('./publication-policy.cjs');

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CATALOG_PATH = '.claude-plugin/marketplace.extended.json';
const CURATED_MANIFEST_PATH = 'skills/.curated/MANIFEST.json';
const JSON_PATH = 'freshie/saas-tutorial-lattice.json';
const REPORT_PATH = '000-docs/813-RA-AUDT-saas-tutorial-lattice.md';

export const TUTORIAL_FAMILIES = Object.freeze([
  'advanced-troubleshooting',
  'architecture-variants',
  'ci-integration',
  'common-errors',
  'core-workflow-a',
  'core-workflow-b',
  'cost-tuning',
  'data-handling',
  'debug-bundle',
  'deploy-integration',
  'enterprise-rbac',
  'hello-world',
  'incident-runbook',
  'install-auth',
  'known-pitfalls',
  'local-dev-loop',
  'load-scale',
  'migration-deep-dive',
  'multi-env-setup',
  'observability',
  'performance-tuning',
  'policy-guardrails',
  'prod-checklist',
  'rate-limits',
  'reference-architecture',
  'reliability-patterns',
  'sdk-patterns',
  'security-basics',
  'upgrade-migration',
  'webhooks-events',
]);

// Versioned aliases for historical pack/skill naming drift. Keeping these
// explicit includes real lattice slots without admitting arbitrary suffix
// matches such as `langchain-otel-observability`.
export const PACK_PREFIX_OVERRIDES = Object.freeze({
  'anthropic-pack': 'anth',
  'claude-pack': 'clade',
  'langchain-py-pack': 'langchain',
});

export const EXPLICIT_NON_CANDIDATES = Object.freeze({
  'customerio-pack/customerio-primary-workflow':
    'content-specific Customer.io campaign workflow, not the generic core-workflow-a family',
  'customerio-pack/customerio-core-feature':
    'content-specific Customer.io transactional messaging workflow, not the generic core-workflow-b family',
  'customerio-pack/customerio-deploy-pipeline':
    'content-specific deployment workflow, not the generic deploy-integration family',
});

const BLAST_RADIUS_CHECKS = Object.freeze([
  'catalog',
  'curated_projection',
  'npm_publication_history',
  'compatibility_redirects',
  'repository_references',
  'mirror_ownership',
]);

function fail(message) {
  throw new Error(`generate-saas-tutorial-lattice: ${message}`);
}

function codePointSort(left, right) {
  return left < right ? -1 : left > right ? 1 : 0;
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function repositoryPath(root, absolute) {
  return path.relative(root, absolute).split(path.sep).join('/');
}

function secureOutputPath(root, value, kind) {
  const absolute = path.resolve(root, value);
  const relative = repositoryPath(root, absolute);
  const requiredPrefix = kind === 'json' ? 'freshie/' : '000-docs/';
  const requiredExtension = kind === 'json' ? '.json' : '.md';
  if (
    relative === '..' ||
    relative.startsWith('../') ||
    path.isAbsolute(relative) ||
    !relative.startsWith(requiredPrefix) ||
    !relative.endsWith(requiredExtension)
  ) {
    fail(`${kind} output must be a ${requiredExtension} file below ${requiredPrefix}`);
  }
  const parent = path.dirname(absolute);
  let realParent;
  try {
    realParent = fs.realpathSync(parent);
  } catch (error) {
    fail(`${kind} output parent must already exist: ${error.message}`);
  }
  if (realParent !== parent || !realParent.startsWith(`${root}${path.sep}`)) {
    fail(`${kind} output parent is not a canonical repository directory`);
  }
  if (fs.existsSync(absolute)) {
    const metadata = fs.lstatSync(absolute);
    if (metadata.isSymbolicLink() || !metadata.isFile()) {
      fail(`${kind} output is not a regular file: ${relative}`);
    }
  }
  return absolute;
}

function parseArgs(argv) {
  const options = { root: ROOT, check: false, json: JSON_PATH, report: REPORT_PATH };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--check') options.check = true;
    else if (value === '--root') options.root = argv[++index];
    else if (value === '--json') options.json = argv[++index];
    else if (value === '--report') options.report = argv[++index];
    else fail(`unknown argument ${value}`);
  }
  if (!options.root) fail('--root requires a directory');
  if (!options.json) fail('--json requires a file');
  if (!options.report) fail('--report requires a file');
  options.root = fs.realpathSync(path.resolve(options.root));
  options.json = secureOutputPath(options.root, options.json, 'json');
  options.report = secureOutputPath(options.root, options.report, 'report');
  if (options.json === options.report) fail('JSON and report outputs must be distinct');
  return options;
}

function readJson(root, repositoryPath) {
  try {
    return JSON.parse(fs.readFileSync(path.join(root, repositoryPath), 'utf8'));
  } catch (error) {
    fail(`cannot parse ${repositoryPath}: ${error.message}`);
  }
}

function safeSource(root, plugin) {
  if (
    typeof plugin.source !== 'string' ||
    !plugin.source.startsWith('./plugins/saas-packs/') ||
    plugin.source.includes('..')
  ) {
    fail(`${plugin.name ?? '<unnamed>'} has an unsafe SaaS source: ${plugin.source}`);
  }
  const source = plugin.source.slice(2).replace(/\/$/, '');
  const expected = path.join(root, source);
  const actual = fs.realpathSync(expected);
  if (actual !== expected || !actual.startsWith(`${root}${path.sep}`)) {
    fail(`${plugin.name} source is not a canonical repository directory: ${source}`);
  }
  return source;
}

function packPrefix(packName) {
  return PACK_PREFIX_OVERRIDES[packName] ?? packName.replace(/-pack$/, '');
}

export function tutorialFamily(packName, skillName) {
  const prefix = packPrefix(packName);
  return TUTORIAL_FAMILIES.find((family) => skillName === `${prefix}-${family}`) ?? null;
}

function suffixOnlyFamily(skillName) {
  return TUTORIAL_FAMILIES.find((family) => skillName.endsWith(`-${family}`)) ?? null;
}

function packageIncludesSkills(files) {
  return (
    Array.isArray(files) &&
    files.some((entry) => {
      if (typeof entry !== 'string' || entry.startsWith('!')) return false;
      const normalized = entry.replace(/^\.\//, '').replace(/\/$/, '');
      return normalized === 'skills' || normalized.startsWith('skills/');
    })
  );
}

function curatedBySource(root) {
  const manifest = readJson(root, CURATED_MANIFEST_PATH);
  if (!Array.isArray(manifest.skills) || manifest.count !== manifest.skills.length) {
    fail('curated manifest count contradicts its skill rows');
  }
  const curatedSkillPaths = new Set(resolveCorpus('curated-mirror', { root }));
  const canonicalSourcePaths = new Set(
    resolveCorpus('graded', { root }).map((skillPath) => skillPath.slice(0, -'/SKILL.md'.length)),
  );
  const rows = new Map();
  const curatedNames = new Set();
  for (const [index, row] of manifest.skills.entries()) {
    if (
      typeof row?.source_path !== 'string' ||
      typeof row?.curated_name !== 'string' ||
      !/^[a-z0-9]+(?:-[a-z0-9]+)*(?:__[a-z0-9]+(?:-[a-z0-9]+)*)?$/.test(row.curated_name) ||
      path.posix.normalize(row.source_path) !== row.source_path ||
      path.posix.isAbsolute(row.source_path) ||
      row.source_path === '..' ||
      row.source_path.startsWith('../') ||
      curatedNames.has(row.curated_name) ||
      rows.has(row.source_path)
    ) {
      fail(`invalid or duplicate curated manifest row ${index}`);
    }
    const mirrorPath = `skills/.curated/${row.curated_name}/SKILL.md`;
    if (!curatedSkillPaths.has(mirrorPath)) {
      fail(`curated manifest row ${index} has no tracked mirror: ${mirrorPath}`);
    }
    if (!canonicalSourcePaths.has(row.source_path)) {
      fail(`curated manifest row ${index} has no tracked canonical source: ${row.source_path}`);
    }
    let mirrorMetadata;
    try {
      mirrorMetadata = fs.lstatSync(path.join(root, mirrorPath));
    } catch (error) {
      fail(`curated manifest row ${index} mirror is unreadable: ${mirrorPath}: ${error.message}`);
    }
    if (mirrorMetadata.isSymbolicLink() || !mirrorMetadata.isFile()) {
      fail(`curated manifest row ${index} mirror is not a regular file: ${mirrorPath}`);
    }
    const sourceSkillPath = path.join(root, row.source_path, 'SKILL.md');
    let sourceMetadata;
    try {
      sourceMetadata = fs.lstatSync(sourceSkillPath);
    } catch (error) {
      fail(
        `curated manifest row ${index} canonical source is unreadable: ${row.source_path}: ${error.message}`,
      );
    }
    if (sourceMetadata.isSymbolicLink() || !sourceMetadata.isFile()) {
      fail(
        `curated manifest row ${index} canonical source is not a regular file: ${row.source_path}`,
      );
    }
    curatedNames.add(row.curated_name);
    rows.set(row.source_path, row);
  }
  return { rows, raw: fs.readFileSync(path.join(root, CURATED_MANIFEST_PATH)) };
}

function visibleFilesystemSkills(root, source) {
  const skillsDirectory = path.join(root, source, 'skills');
  return fs
    .readdirSync(skillsDirectory, { withFileTypes: true })
    .filter(
      (entry) =>
        entry.isDirectory() && fs.existsSync(path.join(skillsDirectory, entry.name, 'SKILL.md')),
    )
    .map((entry) => `${source}/skills/${entry.name}/SKILL.md`)
    .sort(codePointSort);
}

function trackedRegularFiles(root, source) {
  if (!fs.existsSync(path.join(root, '.git'))) {
    const files = [];
    const walk = (directory) => {
      for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
        const absolute = path.join(directory, entry.name);
        const relative = repositoryPath(root, absolute);
        if (entry.isSymbolicLink()) fail(`tracked pack input crosses a symlink: ${relative}`);
        if (entry.isDirectory()) walk(absolute);
        else if (entry.isFile()) files.push(relative);
        else fail(`tracked pack input is not a regular repository file: ${relative}`);
      }
    };
    walk(path.join(root, source));
    return files.sort(codePointSort);
  }
  const result = spawnSync('git', ['ls-files', '--stage', '-z', '--', source], {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 128 * 1024 * 1024,
  });
  if (result.error || result.status !== 0) {
    fail(
      `cannot enumerate tracked pack files for ${source}: ${result.error?.message ?? result.stderr}`,
    );
  }
  const files = result.stdout
    .split('\0')
    .filter(Boolean)
    .map((record) => {
      const match = record.match(/^(\d{6}) [0-9a-f]+ (\d)\t(.+)$/);
      if (!match || match[2] !== '0') fail(`unresolved Git index entry below ${source}`);
      if (match[1] !== '100644' && match[1] !== '100755') {
        fail(`non-regular tracked pack input: ${match[3]} (mode ${match[1]})`);
      }
      return match[3];
    })
    .sort(codePointSort);
  if (files.length === 0) fail(`${source} has no tracked files`);
  for (const file of files) {
    let candidate = root;
    const segments = file.split('/');
    for (const [index, segment] of segments.entries()) {
      candidate = path.join(candidate, segment);
      let metadata;
      try {
        metadata = fs.lstatSync(candidate);
      } catch (error) {
        fail(`tracked pack input is unreadable: ${file}: ${error.message}`);
      }
      if (metadata.isSymbolicLink()) fail(`tracked pack input crosses a symlink: ${file}`);
      const final = index === segments.length - 1;
      if ((final && !metadata.isFile()) || (!final && !metadata.isDirectory())) {
        fail(`tracked pack input is not a regular repository file: ${file}`);
      }
    }
  }
  return files;
}

function ratioBasisPoints(numerator, denominator) {
  return denominator === 0 ? 0 : Math.round((numerator * 10_000) / denominator);
}

export function buildReport({ root }) {
  const catalogRaw = fs.readFileSync(path.join(root, CATALOG_PATH));
  const catalog = readJson(root, CATALOG_PATH);
  const plugins = publishedPlugins(catalog.plugins, 'extended catalog').filter(
    (plugin) => plugin.category === 'saas-packs',
  );
  if (plugins.length === 0) fail('catalog contains no active SaaS packs');

  const marketplaceVisible = resolveCorpus('marketplace-visible', { root });
  const curated = curatedBySource(root);
  const seenNames = new Set();
  const seenSources = new Set();
  const seenPackageNames = new Set();
  const inventoryHasher = crypto.createHash('sha256');
  inventoryHasher.update(catalogRaw);
  inventoryHasher.update(curated.raw);

  const packs = plugins.map((plugin) => {
    if (typeof plugin.name !== 'string' || plugin.name.length === 0)
      fail('catalog pack has no name');
    if (seenNames.has(plugin.name)) fail(`duplicate SaaS pack name: ${plugin.name}`);
    seenNames.add(plugin.name);
    const source = safeSource(root, plugin);
    if (seenSources.has(source)) fail(`duplicate SaaS pack source: ${source}`);
    seenSources.add(source);

    const manifestPath = `${source}/.claude-plugin/plugin.json`;
    const packagePath = `${source}/package.json`;
    const manifest = readJson(root, manifestPath);
    const packageManifest = readJson(root, packagePath);
    const packFiles = trackedRegularFiles(root, source);
    const packFileSet = new Set(packFiles);
    const packHasher = crypto.createHash('sha256');
    const candidateHasher = crypto.createHash('sha256');
    packHasher.update(`catalog-entry\0${JSON.stringify(plugin)}\0`);
    if (!packFileSet.has(manifestPath) || !packFileSet.has(packagePath)) {
      fail(`${plugin.name} manifest and package metadata must be tracked`);
    }
    if (manifest.name !== plugin.name || manifest.version !== plugin.version) {
      fail(`${plugin.name} identity/version differs between catalog and plugin manifest`);
    }
    if (
      typeof packageManifest.name !== 'string' ||
      packageManifest.name.length === 0 ||
      seenPackageNames.has(packageManifest.name)
    ) {
      fail(`${plugin.name} has a missing or duplicate npm package name: ${packageManifest.name}`);
    }
    seenPackageNames.add(packageManifest.name);
    if (!packageIncludesSkills(packageManifest.files)) {
      fail(`${plugin.name} npm package does not include skills/`);
    }
    for (const packFile of packFiles) {
      const bytes = fs.readFileSync(path.join(root, packFile));
      inventoryHasher.update(`\0${packFile}\0`).update(bytes);
      packHasher.update(`pack-file\0${packFile}\0`).update(bytes);
    }

    const prefix = `${source}/skills/`;
    const skillFiles = marketplaceVisible
      .filter(
        (entry) =>
          entry.startsWith(prefix) &&
          entry.endsWith('/SKILL.md') &&
          entry.slice(prefix.length).split('/').length === 2,
      )
      .sort(codePointSort);
    const filesystemSkills = visibleFilesystemSkills(root, source);
    if (JSON.stringify(skillFiles) !== JSON.stringify(filesystemSkills)) {
      const resolved = new Set(skillFiles);
      const untracked = filesystemSkills.filter((entry) => !resolved.has(entry));
      fail(
        `${plugin.name} filesystem differs from the marketplace-visible corpus` +
          (untracked.length ? `; untracked skills: ${untracked.join(', ')}` : ''),
      );
    }
    if (plugin.components?.skills !== skillFiles.length) {
      fail(
        `${plugin.name} declares ${plugin.components?.skills} skills but resolves ${skillFiles.length}`,
      );
    }

    const packProvenance = resolvePluginProvenance(source, { root });
    if (packProvenance.status === 'refused') {
      fail(`${plugin.name} provenance refused: ${packProvenance.reasonCode}`);
    }
    const provenanceMarkers = new Set();

    const skills = skillFiles.map((skillPath) => {
      const directoryName = skillPath.split('/').at(-2);
      const sourcePath = skillPath.slice(0, -'/SKILL.md'.length);
      const content = fs.readFileSync(path.join(root, skillPath));
      let frontmatter;
      try {
        frontmatter = parseFrontmatter(content.toString('utf8'));
      } catch (error) {
        fail(`${skillPath} has invalid frontmatter: ${error.message}`);
      }
      const publicName = frontmatter?.name;
      if (typeof publicName !== 'string' || publicName.length === 0) {
        fail(`${skillPath} has no public frontmatter name`);
      }
      if (publicName !== directoryName) {
        fail(
          `${skillPath} public name ${JSON.stringify(publicName)} differs from directory ${JSON.stringify(directoryName)}`,
        );
      }
      const provenance = resolvePluginProvenance(path.posix.dirname(skillPath), { root });
      if (provenance.status === 'refused') {
        fail(`${skillPath} provenance refused: ${provenance.reasonCode}`);
      }
      if (
        provenance.status !== packProvenance.status ||
        (provenance.status === 'mirror' && provenance.markerPath !== packProvenance.markerPath)
      ) {
        fail(`${skillPath} crosses a nested provenance boundary`);
      }
      if (provenance.status === 'mirror') provenanceMarkers.add(provenance.markerPath);
      const curatedRow = curated.rows.get(sourcePath);
      if (curatedRow) {
        packHasher.update(`curated-row\0${JSON.stringify(curatedRow)}\0`);
      }
      const family = tutorialFamily(plugin.name, publicName);
      return {
        directory_name: directoryName,
        public_name: publicName,
        path: skillPath,
        family,
        suffix_only_family: suffixOnlyFamily(publicName),
        ownership:
          provenance.status === 'mirror'
            ? {
                status: 'mirror',
                upstream: provenance.upstream,
                marker: repositoryPath(root, provenance.markerPath),
              }
            : { status: 'first-party' },
        curated: curatedRow
          ? { present: true, curated_name: curatedRow.curated_name }
          : { present: false, curated_name: null },
      };
    });
    for (const markerPath of [...provenanceMarkers].sort(codePointSort)) {
      const markerBytes = fs.readFileSync(markerPath);
      const markerRepositoryPath = repositoryPath(root, markerPath);
      if (!packFileSet.has(markerRepositoryPath)) {
        inventoryHasher.update(`\0${markerRepositoryPath}\0`).update(markerBytes);
        packHasher.update(`provenance\0${markerRepositoryPath}\0`).update(markerBytes);
      }
      candidateHasher.update(`provenance\0${markerRepositoryPath}\0`).update(markerBytes);
    }
    const candidates = skills.filter((skill) => skill.family !== null);
    for (const candidate of candidates) {
      candidateHasher.update(
        `candidate\0${candidate.path}\0${candidate.public_name}\0${candidate.family}\0${JSON.stringify(candidate.ownership)}\0`,
      );
      const candidateRoot = candidate.path.slice(0, -'/SKILL.md'.length);
      const candidateFiles = packFiles.filter(
        (packFile) => packFile === candidate.path || packFile.startsWith(`${candidateRoot}/`),
      );
      if (!candidateFiles.includes(candidate.path)) {
        fail(`${candidate.path} is absent from the tracked candidate subtree`);
      }
      for (const candidateFile of candidateFiles) {
        candidateHasher
          .update(`candidate-file\0${candidateFile}\0`)
          .update(fs.readFileSync(path.join(root, candidateFile)));
      }
      const curatedRow = curated.rows.get(candidateRoot);
      if (curatedRow) candidateHasher.update(`curated-row\0${JSON.stringify(curatedRow)}\0`);
    }
    const prefixMismatches = skills.filter(
      (skill) => skill.family === null && skill.suffix_only_family !== null,
    );
    return {
      name: plugin.name,
      source,
      version: plugin.version,
      verification: {
        grade: plugin.verification?.grade ?? null,
        score: Number.isInteger(plugin.verification?.score) ? plugin.verification.score : null,
      },
      npm_candidate: {
        name: packageManifest.name ?? null,
        version: packageManifest.version ?? null,
        private: packageManifest.private === true,
        files_include_skills: packageIncludesSkills(packageManifest.files),
        live_registry_check: 'REQUIRED_BEFORE_MUTATION',
      },
      publication: plugin.publication ?? 'published',
      ownership:
        packProvenance.status === 'mirror'
          ? {
              status: 'mirror',
              upstream: packProvenance.upstream,
              marker: repositoryPath(root, packProvenance.markerPath),
            }
          : { status: 'first-party' },
      pack_inventory_sha256: packHasher.digest('hex'),
      candidate_set_sha256: candidateHasher.digest('hex'),
      skill_count: skills.length,
      catalog_declared_skill_count: plugin.components?.skills ?? null,
      tutorial_lattice_count: candidates.length,
      tutorial_lattice_basis_points: ratioBasisPoints(candidates.length, skills.length),
      curated_skill_count: skills.filter((skill) => skill.curated.present).length,
      candidate_curated_count: candidates.filter((skill) => skill.curated.present).length,
      candidate_skills: candidates.map((skill) => ({
        directory_name: skill.directory_name,
        public_name: skill.public_name,
        path: skill.path,
        family: skill.family,
        match_rule: PACK_PREFIX_OVERRIDES[plugin.name]
          ? `explicit-prefix-alias:${PACK_PREFIX_OVERRIDES[plugin.name]}`
          : 'canonical-pack-prefix',
        curated: skill.curated,
        ownership: skill.ownership,
        disposition: 'REVIEW_REQUIRED',
      })),
      prefix_mismatch_skills: prefixMismatches.map((skill) => ({
        directory_name: skill.directory_name,
        public_name: skill.public_name,
        path: skill.path,
        suffix_only_family: skill.suffix_only_family,
      })),
      non_lattice_skills: skills
        .filter((skill) => skill.family === null)
        .map((skill) => skill.public_name),
      required_blast_radius_checks: BLAST_RADIUS_CHECKS,
    };
  });

  const affected = packs.filter((pack) => pack.tutorial_lattice_count > 0);
  const queue = [...affected]
    .sort(
      (left, right) =>
        right.tutorial_lattice_basis_points - left.tutorial_lattice_basis_points ||
        (left.verification.score ?? -1) - (right.verification.score ?? -1) ||
        right.tutorial_lattice_count - left.tutorial_lattice_count ||
        codePointSort(left.name, right.name),
    )
    .map((pack, index) => ({
      rank: index + 1,
      pack: pack.name,
      candidate_skills: pack.tutorial_lattice_count,
      skill_count: pack.skill_count,
      candidate_basis_points: pack.tutorial_lattice_basis_points,
      verification_grade: pack.verification.grade,
      verification_score: pack.verification.score,
      pack_inventory_sha256: pack.pack_inventory_sha256,
      candidate_set_sha256: pack.candidate_set_sha256,
      next_action: 'ENSURE_EXACTLY_ONE_PACK_DISPOSITION_CHILD',
    }));
  const suffixFrequency = Object.fromEntries(
    TUTORIAL_FAMILIES.map((family) => [
      family,
      packs.reduce(
        (count, pack) =>
          count + pack.candidate_skills.filter((skill) => skill.family === family).length,
        0,
      ),
    ]),
  );
  const totalSkills = packs.reduce((count, pack) => count + pack.skill_count, 0);
  const candidateSkills = affected.reduce((count, pack) => count + pack.tutorial_lattice_count, 0);

  return {
    schema_version: 'saas-tutorial-lattice/v1',
    authority: 'Bead claude-juoz.3.11; active published catalog and marketplace-visible corpus',
    semantics:
      'Family-name matches are review candidates, not automatic quality or retirement verdicts.',
    sources: {
      catalog: CATALOG_PATH,
      catalog_sha256: sha256(catalogRaw),
      curated_manifest: CURATED_MANIFEST_PATH,
      curated_manifest_sha256: sha256(curated.raw),
      tracked_inventory_sha256: inventoryHasher.digest('hex'),
    },
    family_definition: TUTORIAL_FAMILIES,
    prefix_policy:
      'A candidate must equal <pack-prefix>-<family>; versioned aliases cover known historical naming drift, while other suffix-only matches are reported but excluded.',
    prefix_overrides: PACK_PREFIX_OVERRIDES,
    explicit_non_candidates: EXPLICIT_NON_CANDIDATES,
    scope_exclusions: [
      {
        cohort: 'local ignored or untracked SaaS directories',
        reason_code: 'NOT_TRACKED_NOT_CATALOG_AUTHORITY',
        policy:
          'Filesystem-only pack roots cannot change this deterministic report; a pack must be tracked and published in the extended catalog.',
      },
      {
        cohort: 'tracked unpublished or quarantined catalog entries',
        reason_code: 'NOT_ACTIVE_PUBLICATION',
        policy: 'Publication policy excludes them from the active marketplace denominator.',
      },
    ],
    summary: {
      active_saas_packs: packs.length,
      active_skills: totalSkills,
      tutorial_lattice_skills: candidateSkills,
      affected_packs: affected.length,
      fully_lattice_packs: affected.filter(
        (pack) => pack.tutorial_lattice_count === pack.skill_count,
      ).length,
      at_least_80_percent_lattice_packs: affected.filter(
        (pack) => pack.tutorial_lattice_basis_points >= 8_000,
      ).length,
      unaffected_packs: packs.length - affected.length,
      prefix_mismatch_skills: packs.reduce(
        (count, pack) => count + pack.prefix_mismatch_skills.length,
        0,
      ),
      prefix_override_candidate_skills: packs.reduce(
        (count, pack) =>
          count +
          pack.candidate_skills.filter((skill) =>
            skill.match_rule.startsWith('explicit-prefix-alias:'),
          ).length,
        0,
      ),
    },
    suffix_frequency: suffixFrequency,
    queue_policy: {
      completion_authority: 'Beads under claude-juoz.3.11',
      ordering:
        'candidate share descending, verification score ascending, candidate count descending, pack name ascending',
      selection:
        'Select the lowest-ranked pack without an existing direct claude-juoz.3.11 disposition child.',
      duplicate_prevention:
        'Search existing direct children before creation; never create a second disposition child for the same pack.',
      wip_limit: 1,
      wip: 'At most one pack disposition child may be OPEN or IN_PROGRESS. Create the next only after the prior child is CLOSED or explicitly BLOCKED on a real prerequisite.',
      allowed_dispositions: ['KEEP', 'DEEPEN', 'REPLACE', 'RETIRE'],
      required_blast_radius_checks: BLAST_RADIUS_CHECKS,
    },
    queue,
    packs: packs.sort((left, right) => codePointSort(left.name, right.name)),
  };
}

function percent(basisPoints) {
  return `${(basisPoints / 100).toFixed(2)}%`;
}

export function renderMarkdown(report) {
  const families = Object.entries(report.suffix_frequency).sort(
    ([leftName, leftCount], [rightName, rightCount]) =>
      rightCount - leftCount || codePointSort(leftName, rightName),
  );
  return [
    '<!-- doc-class: generated -->',
    '',
    '# SaaS Tutorial-Lattice Audit',
    '',
    '> Generated by `node scripts/generate-saas-tutorial-lattice.mjs`. Do not hand-edit counts.',
    '',
    '**Status:** denominator and ordered review queue for Bead `claude-juoz.3.11`',
    '',
    '## Decision boundary',
    '',
    'A matching skill name proves structural repetition only. It does **not** prove that the skill is filler, unsafe, inaccurate, or disposable. Every pack receives a bounded evidence review before any mutation, and every candidate receives one of `KEEP`, `DEEPEN`, `REPLACE`, or `RETIRE`.',
    '',
    '## Current denominator',
    '',
    '| Measure | Count |',
    '| --- | ---: |',
    `| Active SaaS packs | ${report.summary.active_saas_packs} |`,
    `| Active skills | ${report.summary.active_skills} |`,
    `| Tutorial-lattice candidates | ${report.summary.tutorial_lattice_skills} |`,
    `| Packs containing candidates | ${report.summary.affected_packs} |`,
    `| Packs entirely inside the lattice | ${report.summary.fully_lattice_packs} |`,
    `| Packs at least 80% inside the lattice | ${report.summary.at_least_80_percent_lattice_packs} |`,
    `| Packs with no lattice candidates | ${report.summary.unaffected_packs} |`,
    `| Candidates admitted by explicit prefix aliases | ${report.summary.prefix_override_candidate_skills} |`,
    `| Suffix-only names excluded by prefix policy | ${report.summary.prefix_mismatch_skills} |`,
    '',
    `- Catalog SHA-256: \`${report.sources.catalog_sha256}\``,
    `- Tracked inventory SHA-256: \`${report.sources.tracked_inventory_sha256}\``,
    '',
    'The earlier 2,011-candidate census used 24 base families and literal pack-name stems. This version expands the family set with `advanced-troubleshooting`, `architecture-variants`, `known-pitfalls`, `load-scale`, `policy-guardrails`, and `reliability-patterns`, then applies versioned exact aliases for `anthropic-pack`, `claude-pack`, and `langchain-py-pack`. The current generated counts above are authoritative. Suffix-only near-matches such as `langchain-otel-observability` and the explicitly recorded content-specific Customer.io workflows remain excluded.',
    '',
    '## Repeated family frequency',
    '',
    '| Family | Skills |',
    '| --- | ---: |',
    ...families.map(([family, count]) => `| \`${family}\` | ${count} |`),
    '',
    '## Required disposition contract',
    '',
    '- `KEEP`: distinct, accurate operator value with sufficient implementation and tests.',
    '- `DEEPEN`: useful operator problem, but the current skill needs source-backed implementation or stronger tests.',
    '- `REPLACE`: the slot is generic or misleading, while a different operator workflow deserves the compatibility surface.',
    '- `RETIRE`: no distinct operator value remains; remove only after catalog, curated, npm, redirect, reference, and mirror checks.',
    '',
    'Beads is the completion authority. Search direct children before creation, select the lowest-ranked pack without a child, and permit at most one `OPEN` or `IN_PROGRESS` pack child. Create the next only after the prior child is `CLOSED` or explicitly `BLOCKED` on a real prerequisite. Never create a duplicate child for a pack. Live npm state is checked inside each Bead because registry observations are not deterministic repository inputs.',
    '',
    '## Ordered pack queue',
    '',
    '| Rank | Pack | Candidates | Total | Share | Grade | Score |',
    '| ---: | --- | ---: | ---: | ---: | :---: | ---: |',
    ...report.queue.map(
      (entry) =>
        `| ${entry.rank} | \`${entry.pack}\` | ${entry.candidate_skills} | ${entry.skill_count} | ${percent(entry.candidate_basis_points)} | ${entry.verification_grade ?? '—'} | ${entry.verification_score ?? '—'} |`,
    ),
    '',
    '## Reproduce',
    '',
    '```bash',
    'pnpm run generate:saas-lattice',
    'pnpm run validate:saas-lattice',
    '```',
    '',
    'Complete per-pack paths, curated joins, package coordinates, provenance, and hashes: [`freshie/saas-tutorial-lattice.json`](../freshie/saas-tutorial-lattice.json).',
    '',
  ].join('\n');
}

function assertCurrent(file, expected, root) {
  const actual = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : null;
  if (actual !== expected) {
    const repositoryPath = path.relative(root, file).split(path.sep).join('/');
    fail(
      `${repositoryPath} is stale (expected sha256 ${sha256(expected)}, actual ${actual === null ? 'missing' : sha256(actual)})`,
    );
  }
}

function assertInputIndexParity(root) {
  if (!fs.existsSync(path.join(root, '.git'))) return;
  const inputs = [
    CATALOG_PATH,
    CURATED_MANIFEST_PATH,
    'plugins/saas-packs',
    'scripts/generate-saas-tutorial-lattice.mjs',
    'scripts/corpus-resolver.mjs',
    'scripts/plugin-provenance.mjs',
    'scripts/publication-policy.cjs',
    'marketplace/scripts/discover-skills.mjs',
  ];
  const result = spawnSync('git', ['diff', '--no-ext-diff', '--quiet', '--', ...inputs], {
    cwd: root,
    encoding: 'utf8',
  });
  if (result.error || result.status === null || result.status > 1) {
    fail(
      `cannot compare generator inputs with the Git index: ${result.error?.message ?? result.stderr}`,
    );
  }
  if (result.status === 1) {
    fail('generator inputs differ between the worktree and Git index; stage them before --check');
  }
}

function buildReportFromIndex(root) {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'saas-lattice-index-'));
  const checkout = path.join(scratch, 'tree');
  const archive = path.join(scratch, 'tree.tar');
  fs.mkdirSync(checkout);
  try {
    const tree = spawnSync('git', ['write-tree'], { cwd: root, encoding: 'utf8' });
    if (tree.error || tree.status !== 0 || !/^[0-9a-f]{40,64}$/.test(tree.stdout.trim())) {
      fail(`cannot freeze Git index tree: ${tree.error?.message ?? tree.stderr}`);
    }
    const archived = spawnSync(
      'git',
      ['archive', '--format=tar', `--output=${archive}`, tree.stdout.trim()],
      { cwd: root, encoding: 'utf8' },
    );
    if (archived.error || archived.status !== 0) {
      fail(`cannot archive frozen Git index tree: ${archived.error?.message ?? archived.stderr}`);
    }
    const extracted = spawnSync('tar', ['-xf', archive, '-C', checkout], {
      cwd: root,
      encoding: 'utf8',
    });
    if (extracted.error || extracted.status !== 0) {
      fail(`cannot extract frozen Git index tree: ${extracted.error?.message ?? extracted.stderr}`);
    }
    return buildReport({ root: checkout });
  } finally {
    fs.rmSync(scratch, { recursive: true, force: true });
  }
}

function writeAtomically(file, contents, root) {
  const relative = repositoryPath(root, file);
  const temporary = path.join(
    path.dirname(file),
    `.${path.basename(file)}.${process.pid}.${crypto.randomBytes(8).toString('hex')}.tmp`,
  );
  let descriptor;
  try {
    descriptor = fs.openSync(temporary, 'wx', 0o600);
    fs.writeFileSync(descriptor, contents);
    fs.fsyncSync(descriptor);
    fs.closeSync(descriptor);
    descriptor = undefined;
    fs.renameSync(temporary, file);
  } catch (error) {
    if (descriptor !== undefined) fs.closeSync(descriptor);
    try {
      fs.unlinkSync(temporary);
    } catch (cleanupError) {
      if (cleanupError?.code !== 'ENOENT') {
        fail(`cannot clean temporary output for ${relative}: ${cleanupError.message}`);
      }
    }
    fail(`cannot atomically write ${relative}: ${error.message}`);
  }
}

export function main(argv = process.argv.slice(2), { afterInputParity = () => {} } = {}) {
  const options = parseArgs(argv);
  if (options.check) {
    assertInputIndexParity(options.root);
    afterInputParity();
  }
  const report = options.check
    ? buildReportFromIndex(options.root)
    : buildReport({ root: options.root });
  if (options.check) assertInputIndexParity(options.root);
  const json = `${JSON.stringify(report, null, 2)}\n`;
  const markdown = renderMarkdown(report);
  if (options.check) {
    assertCurrent(options.json, json, options.root);
    assertCurrent(options.report, markdown, options.root);
    assertGeneratedContentCurrent(
      [
        { path: repositoryPath(options.root, options.json), contents: json },
        { path: repositoryPath(options.root, options.report), contents: markdown },
      ],
      { root: options.root },
    );
  } else {
    writeAtomically(options.json, json, options.root);
    writeAtomically(options.report, markdown, options.root);
  }
  return report;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const report = main();
    process.stdout.write(
      `saas tutorial lattice: ${report.summary.tutorial_lattice_skills} candidates across ${report.summary.affected_packs} packs\n`,
    );
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
