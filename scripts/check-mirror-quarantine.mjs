#!/usr/bin/env node
/** Assert every external mirror has a non-publishable E8 disposition. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { createRequire } from 'node:module';

import { resolvePluginProvenance } from './plugin-provenance.mjs';
import { safeReadFile } from './safe-fs.mjs';

const require = createRequire(import.meta.url);
const { sourcePublicationDisposition } = require('./publication-policy.cjs');

function fail(message) {
  throw new Error(`check-mirror-quarantine: ${message}`);
}

function safeRepoPath(value, label) {
  if (typeof value !== 'string' || value.length === 0) fail(`${label} must be a non-empty path`);
  const normalized = value.replaceAll('\\', '/').replace(/^\.\//, '');
  if (
    path.posix.normalize(normalized) !== normalized ||
    normalized.startsWith('/') ||
    normalized.split('/').includes('..')
  ) {
    fail(`${label} escapes the repository: ${value}`);
  }
  return normalized;
}

function sameStrings(left, right) {
  const a = [...new Set(left)].sort();
  const b = [...new Set(right)].sort();
  return a.length === b.length && a.every((value, index) => value === b[index]);
}

function optionalJson(root, relativePath, fallback) {
  const absolute = path.join(root, relativePath);
  return fs.existsSync(absolute) ? JSON.parse(fs.readFileSync(absolute, 'utf8')) : fallback;
}

function markdownLinkTo(text, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`\\[${escaped}\\]\\(`, 'i').test(text);
}

export function checkMirrorQuarantine({ root = process.cwd() } = {}) {
  const ledger = JSON.parse(
    fs.readFileSync(path.join(root, 'freshie/disposition-ledger.json'), 'utf8'),
  );
  if (ledger?.schema_version !== 'disposition-ledger/v1' || !Array.isArray(ledger.artifacts)) {
    fail('disposition ledger is malformed');
  }
  const rows = new Map(ledger.artifacts.map((row) => [row.path, row]));
  const gradePaths = fs
    .readFileSync(path.join(root, 'freshie/grades.csv'), 'utf8')
    .trim()
    .split(/\r?\n/)
    .slice(1)
    .map((line) => `${line.split(',')[0]}/SKILL.md`);
  const mirrors = gradePaths.filter(
    (skill) => resolvePluginProvenance(path.posix.dirname(skill), { root }).status === 'mirror',
  );
  const bad = mirrors.filter(
    (skill) => !['QUARANTINE', 'CERTIFY-UPSTREAM'].includes(rows.get(skill)?.disposition),
  );
  if (bad.length) fail(`mirror without non-publishable disposition: ${bad.join(', ')}`);

  const manifestPath = path.join(root, 'skills/.curated/MANIFEST.json');
  const curated = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const curatedSources = new Set((curated.skills ?? []).map((row) => row.source_path));
  const leaked = mirrors.filter((skill) => curatedSources.has(skill));
  if (leaked.length)
    fail(`quarantined mirror appears in curated publication: ${leaked.join(', ')}`);

  const sourceDocument = yaml.load(fs.readFileSync(path.join(root, 'sources.yaml'), 'utf8'));
  if (!Array.isArray(sourceDocument?.sources)) fail('sources.yaml has no sources array');
  const catalogDocument = JSON.parse(
    fs.readFileSync(path.join(root, '.claude-plugin/marketplace.extended.json'), 'utf8'),
  );
  if (!Array.isArray(catalogDocument?.plugins)) fail('marketplace catalog has no plugins array');
  const catalogRows = new Map(catalogDocument.plugins.map((plugin) => [plugin?.name, plugin]));
  const installCatalog = JSON.parse(
    fs.readFileSync(path.join(root, '.claude-plugin/marketplace.json'), 'utf8'),
  );
  const siteCatalog = JSON.parse(
    fs.readFileSync(path.join(root, 'marketplace/src/data/catalog.json'), 'utf8'),
  );
  const skillsCatalog = JSON.parse(
    fs.readFileSync(path.join(root, 'marketplace/src/data/skills-catalog.json'), 'utf8'),
  );
  const skillsIndex = JSON.parse(
    fs.readFileSync(path.join(root, 'marketplace/src/data/skills-index.json'), 'utf8'),
  );
  const searchIndex = JSON.parse(
    fs.readFileSync(path.join(root, 'marketplace/src/data/unified-search-index.json'), 'utf8'),
  );
  const readmeSections = optionalJson(root, 'marketplace/src/data/readme-sections.json', {});
  const coworkManifest = optionalJson(root, 'marketplace/src/data/cowork-manifest.json', {
    plugins: [],
  });
  const spotlights = JSON.parse(
    fs.readFileSync(path.join(root, 'marketplace/src/data/spotlights.json'), 'utf8'),
  );
  const rootReadme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  const declared = new Map();

  const legalHolds = [];
  const evidencePaths = new Set();
  for (const source of sourceDocument.sources) {
    const disposition = sourcePublicationDisposition(source, {
      readEvidence: (evidence) => safeReadFile(root, evidence),
    });
    if (disposition === null) continue;
    if (catalogRows.get(source.name)?.publication !== 'quarantined') {
      fail(`${source.name} must remain an explicitly quarantined extended-catalog record`);
    }
    const leakedSurfaces = [];
    if ((installCatalog.plugins ?? []).some((plugin) => plugin?.name === source.name)) {
      leakedSurfaces.push('CLI install catalog');
    }
    if (
      (siteCatalog.plugins ?? []).some(
        (plugin) => plugin?.name === source.name || plugin?.slug === source.name,
      )
    ) {
      leakedSurfaces.push('website catalog');
    }
    if (
      (skillsCatalog.skills ?? []).some(
        (skill) =>
          skill?.parentPlugin?.name === source.name ||
          safeRepoPath(skill?.filePath ?? 'missing', 'skills catalog filePath').startsWith(
            `${safeRepoPath(source.target_path, `${source.name}.target_path`)}/`,
          ),
      )
    ) {
      leakedSurfaces.push('website skills catalog');
    }
    if ((skillsIndex.skills ?? []).some((skill) => skill?.parentPlugin === source.name)) {
      leakedSurfaces.push('website skills index');
    }
    if (
      (searchIndex.items ?? []).some(
        (item) => item?.name === source.name || item?.parentPlugin?.name === source.name,
      )
    ) {
      leakedSurfaces.push('unified search');
    }
    if (Object.hasOwn(readmeSections, source.name)) {
      leakedSurfaces.push('website README sections');
    }
    if ((coworkManifest.plugins ?? []).some((plugin) => plugin?.name === source.name)) {
      leakedSurfaces.push('Cowork downloads');
    }
    if ((spotlights.hallOfFame ?? []).some((item) => item?.pluginSlug === source.name)) {
      leakedSurfaces.push('community spotlight');
    }
    if (markdownLinkTo(rootReadme, source.name)) {
      leakedSurfaces.push('root README recommendation');
    }
    if (leakedSurfaces.length > 0) {
      fail(`${source.name} quarantine leaks through ${leakedSurfaces.join(', ')}`);
    }
    if (disposition.legal_hold) {
      legalHolds.push({
        target: source.target_path,
        hold: disposition.legal_hold,
      });
    }
    for (const artifact of disposition.artifacts) {
      if (evidencePaths.has(artifact.path)) {
        fail(`duplicate publication disposition: ${artifact.path}`);
      }
      evidencePaths.add(artifact.path);
      if (artifact.gate === 'G0') declared.set(artifact.path, artifact.reason_codes);
    }
  }

  const g0Mirrors = [];
  for (const row of ledger.artifacts.filter((artifact) => artifact?.gate === 'G0')) {
    const provenance = resolvePluginProvenance(path.posix.dirname(row.path), {
      root,
    });
    if (provenance.status !== 'mirror') {
      fail(`first-party G0 finding must be remediated, not dispositioned: ${row.path}`);
    }
    g0Mirrors.push(row.path);
    const reasonCodes = declared.get(row.path);
    if (!reasonCodes) fail(`G0 mirror has no source publication disposition: ${row.path}`);
    if (
      row.disposition !== 'QUARANTINE' ||
      !Array.isArray(row.reason_codes) ||
      !sameStrings(reasonCodes, row.reason_codes)
    ) {
      fail(`G0 mirror disposition contradicts the ledger: ${row.path}`);
    }
  }
  const staleDeclarations = [...declared.keys()].filter(
    (artifact) => !g0Mirrors.includes(artifact),
  );
  if (staleDeclarations.length) {
    fail(`publication disposition has no live G0 finding: ${staleDeclarations.join(', ')}`);
  }
  for (const row of ledger.artifacts.filter((artifact) => artifact.source_hold !== undefined)) {
    if (
      row.gate !== 'G1' ||
      !legalHolds.some(
        ({ target, hold }) =>
          row.path.startsWith(`${target}/`) && row.source_hold?.source === hold.source,
      )
    ) {
      fail(`G1 source association has no matching legal hold: ${row.path}`);
    }
  }
  for (const { target, hold } of legalHolds) {
    for (const row of ledger.artifacts.filter((artifact) =>
      artifact.path.startsWith(`${target}/`),
    )) {
      // Security takes precedence; its exact scanner coverage was checked above.
      if (row.gate === 'G0') continue;
      const associated = row.source_hold;
      if (
        row.gate !== 'G1' ||
        row.disposition !== 'QUARANTINE' ||
        associated?.source !== hold.source ||
        associated?.rationale !== hold.rationale ||
        !Array.isArray(associated?.artifacts) ||
        associated.artifacts.length !== hold.artifacts.length ||
        !Array.isArray(row.reason_codes) ||
        !hold.artifacts.every((evidence) => {
          const recorded = associated.artifacts.find((artifact) => artifact.path === evidence.path);
          return (
            Array.isArray(recorded?.reason_codes) &&
            sameStrings(recorded.reason_codes, evidence.reason_codes) &&
            evidence.reason_codes.every((reason) => row.reason_codes.includes(reason))
          );
        })
      ) {
        fail(`G1 source hold contradicts the ledger: ${row.path}`);
      }
    }
  }

  return {
    mirrors: mirrors.length,
    quarantined: mirrors.filter((skill) => rows.get(skill)?.disposition === 'QUARANTINE').length,
    g0Quarantined: g0Mirrors.length,
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = checkMirrorQuarantine();
    console.log(
      `mirror quarantine: OK (${result.quarantined}/${result.mirrors} quarantined; ` +
        `${result.g0Quarantined} G0 findings have zero publication channels)`,
    );
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
