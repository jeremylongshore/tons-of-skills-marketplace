/**
 * Extended rows for blueprint 727's Epic 1 scorecard.
 *
 * This module is intentionally side-effect free. It reads only paths supplied by
 * the caller (normally an immutable Git-index snapshot) and never shells out,
 * consults a clock, or queries mutable external state.
 */

import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, extname, isAbsolute, normalize, relative, resolve, sep } from 'node:path';
import yaml from 'js-yaml';

import { canonicalDocumentLinks, inspectAuthorityMetadata } from './check-doc-authority.mjs';
import { CORPUS_COHORTS, resolveCorpus } from './corpus-resolver.mjs';
import { scanDeadDomainPolicy } from './dead-domain-policy.mjs';
import { artifactRegistration } from './generated-artifact-registry.mjs';
import { inspectWorkflowEntries } from './check-privileged-action-pins.mjs';

const DEAD_DOMAIN_BASELINE_RECEIPT = Object.freeze({
  head_sha: '3543d5d167bd4e8d27666c8893080bca3bd72950',
  command:
    'git worktree add --detach <base-checkout> 3543d5d167bd4e8d27666c8893080bca3bd72950 && node scripts/check-dead-domain.mjs --json --root <base-checkout>',
  cohort:
    'case-insensitive tracked retired-domain references classified by the E1.13 policy scanner',
  counts: {
    all: { files: 125, occurrences: 356 },
    actionable: { files: 114, occurrences: 292 },
    first_party_source: { files: 94, occurrences: 260 },
    generated_projection: { files: 20, occurrences: 32 },
    retained: { files: 11, occurrences: 64 },
    frozen_record: { files: 2, occurrences: 4 },
    historical_snapshot: { files: 9, occurrences: 60 },
    provenance_mirror: { files: 0, occurrences: 0 },
    refused: 0,
  },
});

const UNRESOLVED_ROWS = new Map([
  [
    7,
    {
      reason_code: 'MISSING_STABLE_DIAGNOSTIC_CLASS_IDS',
      required_inputs: [
        'validator JSON records with stable body-section and frontmatter diagnostic IDs',
      ],
    },
  ],
  [
    8,
    {
      reason_code: 'MISSING_SAFETY_DIAGNOSTIC_CLASS_IDS',
      required_inputs: [
        'registered diagnostic IDs for unscoped Bash, tier-2 tool safety, orchestration, and link escape',
      ],
    },
  ],
  [
    9,
    {
      reason_code: 'MISSING_SECURITY_DIAGNOSTIC_RECORDS',
      required_inputs: [
        'path-bearing shell-substitution diagnostic records from the canonical validator',
      ],
    },
  ],
  [
    15,
    {
      reason_code: 'MISSING_MULTI_HARNESS_CLAIM_CLASSIFIER',
      required_inputs: [
        'machine-readable harness-claim vocabulary',
        'registered adapter artifact contract',
      ],
    },
  ],
  [
    16,
    {
      reason_code: 'MISSING_ADAPTER_REGISTRY',
      required_inputs: [
        'canonical-to-adapter path registry',
        'adapter thinness and byte-divergence contract',
      ],
    },
  ],
  [
    17,
    {
      reason_code: 'MISSING_FUNCTIONAL_MODEL_ID_CLASSIFIER',
      required_inputs: [
        'classifier separating executable model configuration from prose and generated mirrors',
      ],
    },
  ],
  [
    18,
    {
      reason_code: 'MISSING_PROSE_MODEL_REFERENCE_CLASSIFIER',
      required_inputs: [
        'classifier separating preserved prose comparisons from executable model configuration',
      ],
    },
  ],
  [
    19,
    {
      reason_code: 'MISSING_MODEL_ID_EXCLUSION_REGISTRY',
      required_inputs: [
        'model-ID grammar',
        'Bead-ID exclusion registry',
        'classifier regression fixtures',
      ],
    },
  ],
  [
    23,
    {
      reason_code: 'MISSING_COMMITTED_ARTIFACT_HISTORY',
      required_inputs: [
        'artifact generation commit',
        'catalog-entry introduction commit',
        'complete Git history',
      ],
    },
  ],
  [
    29,
    {
      reason_code: 'MISSING_PINNED_UPSTREAM_LICENSE_EVIDENCE',
      required_inputs: [
        'resolved upstream commit per mirror',
        'retained primary upstream license text',
      ],
    },
  ],
  [
    49,
    {
      reason_code: 'MISSING_MCP_DESTRUCTIVE_POLICY_REGISTRY',
      required_inputs: [
        'MCP plugin inventory',
        'destructive-operation policy field',
        'refusal-test registry',
      ],
    },
  ],
  [
    50,
    {
      reason_code: 'MISSING_CORRECTNESS_CRITICAL_COMMAND_REGISTRY',
      required_inputs: [
        'registry distinguishing bounded cleanup from correctness-critical failure swallowing',
      ],
    },
  ],
  [
    51,
    {
      reason_code: 'MISSING_SAFETY_CLAIM_BOUNDARY_REGISTRY',
      required_inputs: ['stable safety claim IDs', 'claim-to-enforcement-boundary relationships'],
    },
  ],
  [
    52,
    {
      reason_code: 'MISSING_COMMITTED_INVENTORY_RUN_ROWS',
      required_inputs: [
        'versioned discovery-run headers and row aggregates from the same database snapshot',
      ],
    },
  ],
  [
    53,
    {
      reason_code: 'MISSING_COMMITTED_LIVE_INVENTORY_HEAD',
      required_inputs: ['versioned latest database run ID', 'versioned latest export run ID'],
    },
  ],
  [
    54,
    {
      reason_code: 'MISSING_COMMITTED_FORGE_PROOF_LEDGER',
      required_inputs: [
        'versioned forge_proofs rows',
        'proof schema with class, hash, and foreign key',
      ],
    },
  ],
  [
    55,
    {
      reason_code: 'MISSING_RETAINED_PRIMARY_EVAL_ARTIFACTS',
      required_inputs: [
        'versioned E2/E3 proof denominator',
        'hash-linked retained primary artifacts',
      ],
    },
  ],
  [
    58,
    {
      reason_code: 'MISSING_HERMETIC_E2E_TEST_CONTRACT',
      required_inputs: [
        'registered scratch-database end-to-end scenario and its expected lifecycle assertions',
      ],
    },
  ],
  [
    60,
    {
      reason_code: 'MISSING_CERTIFICATION_RECORD_SCHEMA',
      required_inputs: [
        'G1-G10 and E1-E6 certification schema',
        'signed artifact evidence records',
      ],
    },
  ],
  [
    61,
    {
      reason_code: 'EXTERNAL_GITHUB_STATE_NOT_COMMITTED',
      required_inputs: [
        'versioned GitHub epic projection snapshot',
        'open Bead epic-cluster denominator',
      ],
    },
  ],
  [
    62,
    {
      reason_code: 'MISSING_COMMITTED_DISPOSITION_REGISTRY',
      required_inputs: ['launch-blocker registry', 'owner identity', 'signed disposition state'],
    },
  ],
]);

const DIMENSIONS = {
  5: 'Grade distribution',
  6: 'A/B artifacts failing the gate',
  7: 'Structural error classes',
  8: 'Safety error classes',
  9: 'Security class (shell substitution in YAML)',
  10: 'Agent errors and reported compliance rate',
  13: 'Malformed allowed-tools',
  14: 'Distinct free-text compatibility values',
  15: 'Multi-harness claims with zero adapter artifact',
  16: 'Adapter files byte-identical to canonical',
  17: 'Functional Claude model-ID lines and files',
  18: 'Prose and comparison model references',
  19: 'Bead-ID false positives in model-ID scans',
  20: 'docs.anthropic.com occurrences',
  21: 'Retired public domain',
  22: 'Tracked generated artifacts with no drift gate',
  23: 'Worst generated-artifact staleness',
  24: 'Published answers to how many skills',
  25: 'README metric writers',
  26: 'Public stats without an enforceable freshness bound',
  27: 'sources.yaml versus sources.lock.json keys',
  28: 'Mirrors shipping license text',
  29: 'Mirror SKILL.md contradicting upstream license',
  30: 'Provenance-marked mirror packages',
  31: 'Independent boundaries preventing mirror publication',
  32: 'Gate dependencies on the publish path',
  33: 'Release-path failures swallowed as warnings',
  34: 'release.yml skip_tests bypass',
  35: 'Software bills of materials',
  36: 'Third-party actions on mutable tags in privileged workflows',
  37: 'Dependabot configuration',
  38: 'Kernel, eval CLI, and harness pins',
  39: 'Kernel shadow report',
  40: 'Marketplace-tier validator runs that block a merge',
  41: 'ci-required needs documented versus actual',
  42: 'Documented schema version',
  43: 'Canonical document authority links',
  44: 'Documentation index entries versus tracked documents',
  45: 'Prose-anchor checker in CI',
  46: 'Tracked files invisible to gitleaks',
  47: 'Blocking pull-request scan for unverifiable secrets',
  48: 'Supply-chain scan coverage on push to main',
  49: 'MCP destructive policy and refusal tests',
  50: 'Unbounded correctness swallows',
  51: 'Safety claims mapped to an enforcement boundary',
  52: 'Inventory header versus rows',
  53: 'Tracked export lag',
  54: 'Forge proofs',
  55: 'Retained primary evaluation artifacts',
  56: 'Public verified claims with backing',
  57: 'eval-spec.yaml source adoption',
  58: 'Freshie test shape',
  59: 'Single-writer enforcement on Dolt',
  60: 'Artifacts meeting G1-G10 and E1-E6',
  61: 'Open GitHub issues labeled epic',
  62: 'Open launch-blocking legal and provenance items',
};

const TEXT_EXTENSIONS = new Set([
  '',
  '.astro',
  '.cjs',
  '.css',
  '.csv',
  '.html',
  '.js',
  '.json',
  '.jsonc',
  '.md',
  '.mdx',
  '.mjs',
  '.py',
  '.sh',
  '.toml',
  '.ts',
  '.tsx',
  '.txt',
  '.yaml',
  '.yml',
]);
const EXECUTABLE_SOURCE = /\.(?:cjs|js|mjs|py|sh|ts|tsx)$/;

function compareText(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

function posix(path) {
  return path.split(sep).join('/');
}

function assertInputs(root, paths, skillRows) {
  if (typeof root !== 'string' || root.length === 0) throw new TypeError('root must be a path');
  if (!Array.isArray(paths) || !Array.isArray(skillRows)) {
    throw new TypeError('paths and skillRows must be arrays');
  }
}

function makeReader(root, paths) {
  const repository = realpathSync(resolve(root));
  const normalized = [...new Set(paths.map((path) => posix(String(path))))].sort(compareText);
  for (const path of normalized) {
    if (path.length === 0 || isAbsolute(path) || path === '..' || path.startsWith('../')) {
      throw new Error(`scorecard path escapes repository: ${path}`);
    }
  }
  const pathSet = new Set(normalized);
  const cache = new Map();

  function text(path) {
    const normalizedPath = posix(path);
    if (!pathSet.has(normalizedPath)) return null;
    if (cache.has(normalizedPath)) return cache.get(normalizedPath);
    const candidate = resolve(repository, normalizedPath);
    const rel = relative(repository, candidate);
    if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) {
      throw new Error(`scorecard path escapes repository: ${normalizedPath}`);
    }
    const metadata = lstatSync(candidate);
    if (metadata.isSymbolicLink() || !metadata.isFile()) {
      cache.set(normalizedPath, null);
      return null;
    }
    const value = readFileSync(candidate, 'utf8');
    cache.set(normalizedPath, value);
    return value;
  }

  function json(path) {
    const value = text(path);
    if (value === null) return null;
    try {
      return JSON.parse(value);
    } catch {
      return null;
    }
  }

  return { json, paths: normalized, pathSet, root: repository, text };
}

function baseRow(number, status, cohort, source, values, extra = {}) {
  return {
    status,
    cohort,
    dimension: DIMENSIONS[number],
    reproduce: `pnpm run measure:e1 --row=${number} --stdout`,
    source: [...new Set(source)].sort(compareText),
    values,
    ...extra,
  };
}

function unresolved(number, cohort = null, source = [], measuredProxy = undefined) {
  const definition = UNRESOLVED_ROWS.get(number);
  if (!definition) throw new Error(`missing unresolved-row definition: ${number}`);
  return baseRow(number, 'not_reproducible', cohort, source, null, {
    reason_code: definition.reason_code,
    required_inputs: definition.required_inputs,
    ...(measuredProxy === undefined ? {} : { measured_proxy: measuredProxy }),
  });
}

function finiteCount(value) {
  return Number.isSafeInteger(value) && value >= 0 ? value : null;
}

function countLiteral(value, needle) {
  if (!value || !needle) return 0;
  let count = 0;
  let offset = 0;
  while ((offset = value.indexOf(needle, offset)) !== -1) {
    count += 1;
    offset += needle.length;
  }
  return count;
}

function textPaths(reader) {
  return reader.paths.filter((path) => TEXT_EXTENSIONS.has(extname(path).toLowerCase()));
}

function executableSources(reader) {
  return reader.paths.filter((path) => EXECUTABLE_SOURCE.test(path));
}

function isMeasurementInstrumentation(path) {
  return (
    /^scripts\/measure-epic-1(?:-scorecard)?(?:\.test)?\.mjs$/.test(path) ||
    path === '000-docs/742-RA-DATA-epic-1-scorecard.json'
  );
}

function isTestSource(path) {
  return /(?:^|\/)(?:__tests__|tests?)(?:\/|$)/.test(path) || /\.(?:spec|test)\.[^/]+$/.test(path);
}

function hasTrackedSourceAncestor(reader, path) {
  let parent = dirname(path);
  while (parent !== '.') {
    if (reader.pathSet.has(`${parent}/.source.json`)) return true;
    const next = dirname(parent);
    if (next === parent) break;
    parent = next;
  }
  return false;
}

function productionExecutableSources(reader) {
  return executableSources(reader).filter(
    (path) =>
      !isMeasurementInstrumentation(path) &&
      !isTestSource(path) &&
      !hasTrackedSourceAncestor(reader, path),
  );
}

function parseFrontmatter(content) {
  const match = content?.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) return { data: null, error: 'ABSENT_FRONTMATTER', raw: null };
  try {
    const data = yaml.load(match[1]);
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      return { data: null, error: 'FRONTMATTER_NOT_MAPPING', raw: match[1] };
    }
    return { data, error: null, raw: match[1] };
  } catch {
    return { data: null, error: 'MALFORMED_FRONTMATTER_YAML', raw: match[1] };
  }
}

function gradeRows(skillRows, tracked, root) {
  const repository = realpathSync(resolve(root));
  const normalized = [];
  const seen = new Set();
  for (const entry of skillRows) {
    if (!entry || typeof entry.path !== 'string') continue;
    let path = posix(entry.path);
    if (isAbsolute(entry.path)) {
      const rel = relative(repository, resolve(entry.path));
      if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) continue;
      path = posix(rel);
    }
    if (!tracked.has(path)) continue;
    if (seen.has(path)) throw new Error(`duplicate tracked validator row: ${path}`);
    seen.add(path);
    normalized.push({ ...entry, path });
  }
  return normalized.sort((a, b) => compareText(a.path, b.path));
}

function gradeMeasurements(rows) {
  const grades = { A: 0, B: 0, C: 0, D: 0, F: 0 };
  let scoreTotal = 0;
  let scoreCount = 0;
  for (const entry of rows) {
    if (Object.hasOwn(grades, entry.grade)) grades[entry.grade] += 1;
    if (Number.isFinite(entry.score)) {
      scoreTotal += entry.score;
      scoreCount += 1;
    }
  }
  const percentages = Object.fromEntries(
    Object.entries(grades).map(([grade, count]) => [
      grade,
      rows.length === 0 ? null : Number(((count * 100) / rows.length).toFixed(1)),
    ]),
  );
  return {
    average_score:
      scoreCount === rows.length && rows.length > 0
        ? Number((scoreTotal / rows.length).toFixed(1))
        : null,
    grade_distribution: grades,
    grade_percentages: percentages,
    rows: rows.length,
  };
}

function abFailures(rows) {
  const result = {
    a_error_total: 0,
    a_failing: 0,
    ab_error_total: 0,
    ab_failing: 0,
    b_error_total: 0,
    b_failing: 0,
  };
  for (const entry of rows) {
    const errors = finiteCount(entry.errors);
    if (errors === null || errors === 0 || !['A', 'B'].includes(entry.grade)) continue;
    result.ab_failing += 1;
    result.ab_error_total += errors;
    if (entry.grade === 'A') {
      result.a_failing += 1;
      result.a_error_total += errors;
    } else {
      result.b_failing += 1;
      result.b_error_total += errors;
    }
  }
  return result;
}

function allowedToolsCensus(reader, rows) {
  const values = {
    declared: 0,
    folded_scalar: 0,
    malformed_frontmatter: 0,
    malformed_shape: 0,
    missing: 0,
    rows: rows.length,
  };
  const compatibility = new Map();
  let invalidCompatibility = 0;
  for (const entry of rows) {
    const parsed = parseFrontmatter(reader.text(entry.path));
    if (parsed.error) {
      values.malformed_frontmatter += 1;
      continue;
    }
    if (!Object.hasOwn(parsed.data, 'allowed-tools')) {
      values.missing += 1;
    } else {
      values.declared += 1;
      const allowed = parsed.data['allowed-tools'];
      if (
        !(
          (typeof allowed === 'string' && allowed.trim().length > 0) ||
          (Array.isArray(allowed) &&
            allowed.length > 0 &&
            allowed.every((item) => typeof item === 'string' && item.trim().length > 0))
        )
      ) {
        values.malformed_shape += 1;
      }
      if (/^allowed-tools:\s*>-\s*$/m.test(parsed.raw)) values.folded_scalar += 1;
    }
    if (Object.hasOwn(parsed.data, 'compatibility')) {
      const compatibilityValue = parsed.data.compatibility;
      if (typeof compatibilityValue === 'string' && compatibilityValue.trim()) {
        compatibility.set(compatibilityValue, (compatibility.get(compatibilityValue) ?? 0) + 1);
      } else {
        invalidCompatibility += 1;
      }
    }
  }
  return {
    allowedTools: values,
    compatibility: {
      distinct_values: compatibility.size,
      invalid_or_empty: invalidCompatibility,
      values: [...compatibility.entries()]
        .map(([value, count]) => ({ count, value }))
        .sort((a, b) => compareText(a.value, b.value)),
    },
  };
}

function literalCensus(reader, needle, include = () => true) {
  const matches = [];
  for (const path of textPaths(reader)) {
    if (!include(path)) continue;
    const count = countLiteral(reader.text(path), needle);
    if (count > 0) matches.push({ count, path });
  }
  return {
    files: matches.length,
    occurrences: matches.reduce((sum, entry) => sum + entry.count, 0),
    paths: matches.map((entry) => entry.path),
  };
}

function writeTargetEvidence(source) {
  const targets = [];
  const calls =
    /(?:\b(?:fs\.)?(?:writeFileSync|writeFile|outputFile)|\bBun\.write)\s*\(\s*([^,\n]+)/g;
  for (const match of source.matchAll(calls)) {
    const expression = match[1].trim();
    let evidence = expression;
    const identifier = expression.match(/^[A-Za-z_$][\w$]*$/)?.[0];
    if (identifier) {
      const escaped = identifier.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const javascript = source.match(
        new RegExp(`\\b(?:const|let|var)\\s+${escaped}\\s*=\\s*([\\s\\S]*?);`),
      )?.[1];
      const python = source.match(new RegExp(`^${escaped}\\s*=\\s*(.+)$`, 'm'))?.[1];
      evidence = `${expression}\n${javascript ?? python ?? ''}`;
    }
    targets.push(evidence);
  }
  for (const match of source.matchAll(/([^\n;]+?)\.write_text\s*\(/g)) targets.push(match[1]);
  return targets;
}

function readTargetEvidence(source) {
  const targets = [];
  const calls = /(?:\b(?:fs\.)?(?:readFileSync|readFile))\s*\(\s*([^,\n]+)/g;
  for (const match of source.matchAll(calls)) {
    const expression = match[1].trim();
    let evidence = expression;
    const identifier = expression.match(/^[A-Za-z_$][\w$]*$/)?.[0];
    if (identifier) {
      const escaped = identifier.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      evidence = `${expression}\n${
        source.match(new RegExp(`\\b(?:const|let|var)\\s+${escaped}\\s*=\\s*([\\s\\S]*?);`))?.[1] ??
        ''
      }`;
    }
    targets.push(evidence);
  }
  return targets;
}

function targetNamesFile(target, basename) {
  const escaped = basename.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(?:^|[^A-Za-z0-9_-])${escaped}(?:$|[^A-Za-z0-9_.-])`).test(target);
}

function generatedArtifacts(reader) {
  const sources = productionExecutableSources(reader);
  const workflows = reader.paths.filter((path) => path.startsWith('.github/workflows/'));
  const candidates = reader.paths.filter((path) => /^marketplace\/src\/data\/.*\.json$/.test(path));
  const artifacts = [];
  for (const path of candidates) {
    const registration = artifactRegistration(path);
    if (
      registration &&
      (registration.kind !== 'generated_projection' || registration.tracking !== 'tracked')
    ) {
      continue;
    }
    const basename = path.slice(path.lastIndexOf('/') + 1);
    const producers = sources.filter((sourcePath) => {
      const source = reader.text(sourcePath) ?? '';
      return writeTargetEvidence(source).some((target) => targetNamesFile(target, basename));
    });
    if (producers.length === 0) continue;
    const legacyWiredCheckers = producers.filter((producer) => {
      const source = reader.text(producer) ?? '';
      if (
        !source.includes('--check') ||
        !readTargetEvidence(source).some((target) => targetNamesFile(target, basename)) ||
        !/(?:!==|Buffer\.compare|\.equals\s*\(|\bdiff\b)/.test(source) ||
        !/(?:process\.exitCode\s*=\s*1|process\.exit\s*\(\s*1\s*\)|throw\s+new\s+Error)/.test(
          source,
        )
      )
        return false;
      const producerName = producer.slice(producer.lastIndexOf('/') + 1);
      const invocation = new RegExp(
        `${producerName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^\\n]*--check`,
      );
      return workflows.some((workflow) => invocation.test(reader.text(workflow) ?? ''));
    });
    const registeredContentCheck =
      registration?.contentCheck === true &&
      typeof registration.regenerate === 'string' &&
      producers.some((producer) =>
        (reader.text(producer) ?? '').includes('check-generated-artifacts.mjs'),
      ) &&
      workflows.some((workflow) => (reader.text(workflow) ?? '').includes(registration.regenerate));
    const wiredCheckers = registeredContentCheck
      ? [...new Set([...legacyWiredCheckers, ...producers])]
      : legacyWiredCheckers;
    artifacts.push({
      content_drift_gate: wiredCheckers.length > 0,
      path,
      producers,
      wired_checkers: wiredCheckers,
    });
  }
  return artifacts.sort((a, b) => compareText(a.path, b.path));
}

function readmeMetricWriters(reader) {
  return productionExecutableSources(reader)
    .filter((path) => {
      const source = reader.text(path) ?? '';
      const writesRootReadme = writeTargetEvidence(source).some(
        (target) =>
          /['"]README\.md['"]/.test(target) &&
          !/(?:target_path|plugin|category|source\.)/i.test(target),
      );
      return (
        writesRootReadme &&
        /marketplace\.extended\.json/.test(source) &&
        /(?:skillCount|\bskills\b)/.test(source) &&
        /(?:agentCount|\bagents\b)/.test(source)
      );
    })
    .sort(compareText);
}

function publicSkillAnswers(reader) {
  return CORPUS_COHORTS.map((cohort) => ({
    cohort,
    value: resolveCorpus(cohort, { root: reader.root, paths: reader.paths }).length,
  })).sort((a, b) => compareText(a.cohort, b.cohort));
}

function publicStats(reader) {
  const paths = reader.paths.filter(
    (path) => /^marketplace\/src\/data\/.*stats.*\.json$/i.test(path) && reader.json(path),
  );
  const sources = paths.map((path) => {
    const value = reader.json(path);
    const bound = value?.max_age_hours;
    return {
      has_valid_max_age_hours: Number.isFinite(bound) && bound >= 0,
      path,
    };
  });
  return {
    sources,
    without_valid_bound: sources.filter((entry) => !entry.has_valid_max_age_hours).length,
  };
}

function sourceKeys(reader) {
  const sourceText = reader.text('sources.yaml');
  const lock = reader.json('sources.lock.json');
  if (
    sourceText === null ||
    !lock ||
    typeof lock.sources !== 'object' ||
    Array.isArray(lock.sources)
  ) {
    return null;
  }
  let parsed;
  try {
    parsed = yaml.load(sourceText);
  } catch {
    return null;
  }
  const entries = Array.isArray(parsed) ? parsed : parsed?.sources;
  if (!Array.isArray(entries)) return null;
  const yamlNames = entries
    .map((entry) => entry?.name)
    .filter((name) => typeof name === 'string' && name.length > 0)
    .sort(compareText);
  if (new Set(yamlNames).size !== yamlNames.length) return null;
  const lockNames = Object.keys(lock.sources).sort(compareText);
  return {
    lock_keys: lockNames.length,
    lock_only: lockNames.filter((name) => !yamlNames.includes(name)),
    yaml_keys: yamlNames.length,
    yaml_only: yamlNames.filter((name) => !lockNames.includes(name)),
  };
}

function mirrorInventory(reader) {
  const markers = reader.paths.filter((path) => path.endsWith('/.source.json')).sort(compareText);
  const roots = markers.map((marker) => dirname(marker));
  const licenses = roots.map((root) => {
    const prefix = `${root}/`;
    const files = reader.paths.filter(
      (path) =>
        path.startsWith(prefix) &&
        !path.slice(prefix.length).includes('/') &&
        /^(?:LICENSE|COPYING)(?:[.-].*)?$/i.test(path.slice(prefix.length)),
    );
    return { license_files: files, marker: `${root}/.source.json`, root };
  });
  const packages = roots
    .filter((root) => reader.pathSet.has(`${root}/package.json`))
    .map((root) => {
      const manifest = reader.json(`${root}/package.json`);
      return {
        marker: `${root}/.source.json`,
        name: typeof manifest?.name === 'string' ? manifest.name : null,
        package: `${root}/package.json`,
        private: manifest?.private === true,
      };
    });
  return { licenses, markers, packages, roots };
}

function publishWorkflows(reader) {
  return reader.paths
    .filter((path) => path.startsWith('.github/workflows/') && /\.ya?ml$/.test(path))
    .filter((path) => /(?:npm|pnpm)\s+publish\b/.test(reader.text(path) ?? ''))
    .sort(compareText);
}

function mirrorCapablePublishWorkflows(reader, publishers) {
  return publishers.filter((path) => {
    const source = reader.text(path) ?? '';
    return (
      source.includes('publish-candidate-report.mjs') ||
      /(?:^|[^A-Za-z0-9_@-])plugins\//m.test(source)
    );
  });
}

function releaseSwallows(reader) {
  const path = '.github/workflows/publish-changed-packages.yml';
  const source = reader.text(path) ?? '';
  const commands = [
    {
      id: 'tag_create',
      pattern: /git tag[\s\S]{0,240}?\|\|\s*\{|git tag[\s\S]{0,240}?failed to create tag/,
    },
    {
      id: 'tag_push',
      pattern:
        /git push origin[\s\S]{0,240}?\|\|\s*\{|git push origin[\s\S]{0,240}?failed to push tag/,
    },
    {
      id: 'github_release',
      pattern:
        /gh release create[\s\S]{0,320}?\|\|\s*\{|gh release create[\s\S]{0,320}?failed to create GitHub release/,
    },
  ];
  return commands.filter((entry) => entry.pattern.test(source)).map((entry) => entry.id);
}

function packagePins(reader) {
  const manifest = reader.json('package.json');
  const dependencies = { ...(manifest?.dependencies ?? {}), ...(manifest?.devDependencies ?? {}) };
  const names = [
    '@intentsolutions/audit-harness',
    '@intentsolutions/core',
    '@intentsolutions/jrig-cli',
  ];
  return Object.fromEntries(
    names.map((name) => {
      const version = typeof dependencies[name] === 'string' ? dependencies[name] : null;
      return [
        name,
        {
          exact: version === null ? null : /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$/.test(version),
          version,
        },
      ];
    }),
  );
}

function marketplaceInvocations(reader) {
  const results = [];
  for (const path of reader.paths.filter((item) => item.startsWith('.github/workflows/'))) {
    const lines = (reader.text(path) ?? '').split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      if (!/validate-skills-schema\.py.*--marketplace/.test(lines[index])) continue;
      const window = lines.slice(Math.max(0, index - 8), index + 2).join('\n');
      results.push({
        blocking_candidate:
          path === '.github/workflows/validate-plugins.yml' &&
          !/continue-on-error:\s*true/.test(window) &&
          !/\|\|\s*true/.test(lines[index]),
        line: index + 1,
        path,
      });
    }
  }
  return results;
}

function ciRequiredNeeds(reader) {
  const source = reader.text('.github/workflows/validate-plugins.yml');
  if (source === null) return { error: 'MISSING_VALIDATE_PLUGINS_WORKFLOW', needs: null };
  let parsed;
  try {
    parsed = yaml.load(source);
  } catch {
    return { error: 'MALFORMED_VALIDATE_PLUGINS_WORKFLOW', needs: null };
  }
  const value = parsed?.jobs?.['ci-required']?.needs;
  const needs = typeof value === 'string' ? [value] : value;
  if (
    !Array.isArray(needs) ||
    needs.length === 0 ||
    needs.some((item) => typeof item !== 'string' || item.length === 0) ||
    new Set(needs).size !== needs.length
  ) {
    return { error: 'MALFORMED_CI_REQUIRED_NEEDS', needs: null };
  }
  return { error: null, needs };
}

function schemaVersions(reader) {
  const runtime = (reader.text('scripts/validate-skills-schema.py') ?? '').match(
    /^SCHEMA_VERSION\s*=\s*["']([^"']+)["']/m,
  )?.[1];
  const docs = ['CLAUDE.md', '000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md']
    .filter((path) => reader.pathSet.has(path))
    .map((path) => ({
      path,
      version:
        (reader.text(path) ?? '').match(
          /(?:CURRENT SCHEMA:|Validator \(schema)\s*\*{0,2}([0-9]+\.[0-9]+\.[0-9]+)/i,
        )?.[1] ?? null,
    }));
  return { docs, runtime: runtime ?? null };
}

function authorityCensus(reader) {
  const standard = reader.text('STANDARDS.md') ?? '';
  const linked = canonicalDocumentLinks(standard, reader.pathSet);
  const claimants = [];
  for (const path of reader.paths.filter((item) => /^000-docs\/.*\.md$/.test(item))) {
    const inspection = inspectAuthorityMetadata(reader.text(path) ?? '');
    if (inspection.errors.length > 0) throw new Error(`ambiguous authority metadata: ${path}`);
    if (inspection.claim) claimants.push(path);
  }
  const authorityLinks = [...linked].sort(compareText);
  return {
    authority_links: authorityLinks,
    canonical_table_links: authorityLinks.length,
    declared: claimants.length,
    linked_declared: claimants.filter((path) => linked.has(path)).length,
    unlinked: claimants.filter((path) => !linked.has(path)),
  };
}

function docsIndex(reader) {
  const documents = reader.paths.filter(
    (path) =>
      path.startsWith('000-docs/') &&
      !['000-docs/000-INDEX.md', '000-docs/.gitignore'].includes(path),
  );
  const index = reader.text('000-docs/000-INDEX.md') ?? '';
  const entries = [...index.matchAll(/^- \[[^\]]+\]\(([^)]+)\)$/gm)].map((match) =>
    posix(normalize(`000-docs/${match[1]}`)),
  );
  return {
    index_entries: entries.length,
    missing_from_index: documents.filter((path) => !entries.includes(path)),
    tracked_documents: documents.length,
    untracked_index_entries: entries.filter((path) => !documents.includes(path)),
  };
}

function gitleaksVisibility(reader) {
  const source = reader.text('.gitleaks.toml');
  if (source === null) return null;
  const section = source.match(/\[allowlist\]([\s\S]*?)(?=^regexes\s*=)/m)?.[1] ?? '';
  const patternBlock = section.match(/paths\s*=\s*\[([\s\S]*?)\]/)?.[1] ?? '';
  const patterns = [...patternBlock.matchAll(/'''([\s\S]*?)'''/g)].map((match) => match[1]);
  const compiled = [];
  const invalid = [];
  for (const pattern of patterns) {
    try {
      const insensitive = pattern.startsWith('(?i)');
      compiled.push(new RegExp(insensitive ? pattern.slice(4) : pattern, insensitive ? 'i' : ''));
    } catch {
      invalid.push(pattern);
    }
  }
  const invisible = reader.paths.filter((path) => compiled.some((pattern) => pattern.test(path)));
  return {
    allowlist_patterns: patterns.length,
    invalid_patterns: invalid.length,
    invisible_files: invisible.length,
    tracked_files: reader.paths.length,
  };
}

function verifiedClaims(value) {
  let count = 0;
  function visit(node) {
    if (!node || typeof node !== 'object') return;
    if (node.verified === true) count += 1;
    for (const child of Object.values(node)) visit(child);
  }
  visit(value);
  return count;
}

function rowSources(...paths) {
  return paths.flat().filter(Boolean);
}

function freshieRunReceipt(reader, path, runId) {
  const report = reader.json(path);
  const coherence = report?.run_coherence;
  const headerTotal = finiteCount(coherence?.header_total_skills);
  const skillRows = finiteCount(coherence?.skill_rows);
  const skillDelta = Number.isSafeInteger(coherence?.skill_row_delta)
    ? coherence.skill_row_delta
    : null;
  const complianceRows = finiteCount(coherence?.skill_compliance_rows);
  const gradeExport = report?.grade_export;
  const gradeExportRows = finiteCount(gradeExport?.row_count);
  const gradeCounts = gradeExport?.grade_counts;
  const forgeProofs = report?.forge_proofs;
  const forgeProofRows = finiteCount(forgeProofs?.row_count);
  const forgeProofRecords = Array.isArray(forgeProofs?.records) ? forgeProofs.records : null;
  const forgeProofHash =
    forgeProofRecords === null
      ? null
      : createHash('sha256').update(canonicalJson(forgeProofRecords)).digest('hex');
  const forgeIdentities = new Set();
  const forgeClassCounts = { E0: 0, E1: 0, E2: 0, E3: 0 };
  let forgeRecordsValid = forgeProofRecords !== null;
  let computedE2E3 = 0;
  for (const record of forgeProofRecords ?? []) {
    const identity = `${record?.plugin_name ?? ''}:${record?.jrig_run_id ?? ''}`;
    if (
      typeof record?.plugin_name !== 'string' ||
      record.plugin_name.length === 0 ||
      finiteCount(record?.jrig_run_id) === null ||
      forgeIdentities.has(identity) ||
      !Object.hasOwn(forgeClassCounts, record?.evidence_class)
    ) {
      forgeRecordsValid = false;
      continue;
    }
    forgeIdentities.add(identity);
    forgeClassCounts[record.evidence_class] += 1;
    if (record.evidence_class === 'E2' || record.evidence_class === 'E3') {
      computedE2E3 += 1;
      if (
        typeof record.artifact_uri !== 'string' ||
        record.artifact_uri.length === 0 ||
        typeof record.artifact_sha256 !== 'string' ||
        !/^[a-f0-9]{64}$/.test(record.artifact_sha256) ||
        (record.evidence_class === 'E3' && typeof record.baseline_delta !== 'number')
      ) {
        forgeRecordsValid = false;
      }
    }
  }
  const valid =
    report?.schema_version === 'freshie-run-delta/v3' &&
    report?.run_id === runId &&
    new RegExp(`^run-${runId}(?:\\.\\d+)?$`).test(report?.to_tag ?? '') &&
    typeof report?.dolt_commit === 'string' &&
    /^[a-z0-9]{20,64}$/i.test(report.dolt_commit) &&
    coherence?.discovery_run_id === runId &&
    headerTotal !== null &&
    headerTotal > 0 &&
    skillRows !== null &&
    skillRows > 0 &&
    skillDelta === skillRows - headerTotal &&
    complianceRows !== null &&
    complianceRows > 0 &&
    gradeExportRows === complianceRows &&
    typeof gradeExport?.csv_sha256 === 'string' &&
    /^[a-f0-9]{64}$/.test(gradeExport.csv_sha256) &&
    gradeCounts !== null &&
    typeof gradeCounts === 'object' &&
    !Array.isArray(gradeCounts) &&
    Object.values(gradeCounts).every((count) => finiteCount(count) !== null) &&
    Object.values(gradeCounts).reduce((total, count) => total + count, 0) === gradeExportRows &&
    forgeProofRows !== null &&
    forgeProofRecords !== null &&
    forgeProofRows === forgeProofRecords.length &&
    forgeProofHash === forgeProofs?.records_sha256 &&
    forgeRecordsValid &&
    canonicalJson(forgeClassCounts) === canonicalJson(forgeProofs?.class_counts) &&
    finiteCount(forgeProofs?.total_e2_e3) === computedE2E3 &&
    finiteCount(forgeProofs?.retained_e2_e3) === computedE2E3;
  return {
    path,
    runId,
    report,
    coherence: { headerTotal, skillRows, skillDelta, complianceRows },
    valid,
  };
}

function latestFreshieRunReceipt(reader) {
  const candidates = reader.paths
    .map((path) => ({ match: /^freshie\/reports\/run-delta-(\d+)\.json$/.exec(path), path }))
    .filter((entry) => entry.match)
    .map((entry) => ({ path: entry.path, runId: Number(entry.match[1]) }))
    .sort((left, right) => left.runId - right.runId);
  if (candidates.length === 0) return null;

  const latest = candidates.at(-1);
  return freshieRunReceipt(reader, latest.path, latest.runId);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value)
      .sort(compareText)
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function forgeProofReceipt(reader, freshieRun) {
  const path = 'freshie/reports/legacy-forge-proofs-demotion.json';
  const payload = reader.json(path);
  const sourceRunId = finiteCount(payload?.source_run_id);
  const sourcePath = sourceRunId === null ? null : `freshie/reports/run-delta-${sourceRunId}.json`;
  const sourceRun = sourcePath === null ? null : freshieRunReceipt(reader, sourcePath, sourceRunId);
  const snapshot = sourceRun?.report?.forge_proofs;
  const currentSnapshot = freshieRun?.report?.forge_proofs;
  if (
    !freshieRun?.valid ||
    !sourceRun?.valid ||
    payload?.schema_version !== 'forge-proof-demotion/v2' ||
    !Array.isArray(payload.records) ||
    !Array.isArray(snapshot?.records) ||
    !Array.isArray(currentSnapshot?.records)
  ) {
    return { path, sourcePath, valid: false };
  }
  const identities = new Set();
  const classCounts = { E0: 0, E1: 0, E2: 0, E3: 0 };
  let invalidIdentities = 0;
  let unclassified = 0;
  for (const record of payload.records) {
    const identity = `${record?.plugin_name ?? ''}:${record?.jrig_run_id ?? ''}`;
    if (
      typeof record?.plugin_name !== 'string' ||
      record.plugin_name.length === 0 ||
      finiteCount(record?.jrig_run_id) === null ||
      identities.has(identity)
    ) {
      invalidIdentities += 1;
    }
    identities.add(identity);
    if (!Object.hasOwn(classCounts, record?.evidence_class)) {
      unclassified += 1;
      continue;
    }
    classCounts[record.evidence_class] += 1;
  }
  const legacyKeys = new Set(['databricks-pack:2', 'databricks-pack:4', 'databricks-pack:5']);
  const legacyE0 = payload.records.filter(
    (record) =>
      legacyKeys.has(`${record?.plugin_name ?? ''}:${record?.jrig_run_id ?? ''}`) &&
      record?.evidence_class === 'E0' &&
      record?.artifact_uri === null &&
      record?.artifact_sha256 === null,
  ).length;
  const recordsHash = createHash('sha256').update(canonicalJson(payload.records)).digest('hex');
  const linked =
    payload.source_run_id === sourceRun.runId &&
    payload.source_tag === sourceRun.report.to_tag &&
    payload.source_dolt_commit === sourceRun.report.dolt_commit &&
    payload.records_sha256 === snapshot.records_sha256 &&
    recordsHash === snapshot.records_sha256 &&
    canonicalJson(payload.records) === canonicalJson(snapshot.records);
  return {
    path,
    sourcePath,
    valid:
      linked &&
      payload.records.length === snapshot.row_count &&
      payload.records.length > 0 &&
      invalidIdentities === 0,
    values: {
      class_counts: classCounts,
      invalid_identities: invalidIdentities,
      legacy_e0_records: legacyE0,
      current_run_id: freshieRun.runId,
      retained_e2_e3: currentSnapshot.retained_e2_e3,
      source_dolt_commit: payload.source_dolt_commit,
      source_run_id: payload.source_run_id,
      source_tag: payload.source_tag,
      total_e2_e3: currentSnapshot.total_e2_e3,
      total_records: payload.records.length,
      unclassified,
    },
  };
}

function freshieHermeticContract(reader, executionShape = {}) {
  const testPath = 'tests/test_freshie_hermetic_cycle.py';
  const workflowPath = '.github/workflows/validate-plugins.yml';
  const source = reader.text(testPath) ?? '';
  const workflow = reader.text(workflowPath) ?? '';
  let parsed = null;
  try {
    parsed = yaml.load(workflow);
  } catch {
    // A malformed workflow cannot prove registration.
  }
  const testJob = parsed?.jobs?.test;
  const steps = Array.isArray(testJob?.steps) ? testJob.steps : [];
  const pythonIf = (step) => step?.if === "matrix.test-type == 'python-tests'";
  const doltStep = steps.find(
    (step) => step?.name === 'Install pinned Dolt for Freshie integration tests',
  );
  const hermeticStep = steps.find(
    (step) => step?.name === 'Run Freshie hermetic publication cycle',
  );
  const doltStepIndex = steps.indexOf(doltStep);
  const hermeticStepIndex = steps.indexOf(hermeticStep);
  const matrixTypes = testJob?.strategy?.matrix?.['test-type'];
  const ciNeedsRaw = parsed?.jobs?.['ci-required']?.needs;
  const ciNeeds = typeof ciNeedsRaw === 'string' ? [ciNeedsRaw] : ciNeedsRaw;
  const doltRun = typeof doltStep?.run === 'string' ? doltStep.run : '';
  const canonicalHermeticRun = `python3 - <<'PY'
import unittest
from tests.test_freshie_hermetic_cycle import HermeticFreshieCycleTests

method_name = "test_full_cycle_uses_only_scratch_state_and_refuses_live_server"
original_method = HermeticFreshieCycleTests.__dict__[method_name]
invocations = []

def guarded_method(self):
    invocations.append(1)
    return original_method(self)

setattr(HermeticFreshieCycleTests, method_name, guarded_method)
suite = unittest.TestSuite([HermeticFreshieCycleTests(method_name)])
result = unittest.TextTestRunner(verbosity=2).run(suite)
valid = (
    result.wasSuccessful()
    and result.testsRun == 1
    and not result.skipped
    and not result.expectedFailures
    and not result.unexpectedSuccesses
    and len(invocations) == 1
    and HermeticFreshieCycleTests.__dict__.get(method_name) is guarded_method
)
raise SystemExit(0 if valid else 1)
PY`;
  const doltLines = doltRun
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const canonicalDoltInstall =
    'sudo install -m 0755 "$dolt_extract/dolt-linux-amd64/bin/dolt" /usr/local/bin/dolt';
  const doltDestinationReferences = doltLines.filter((line) =>
    line.includes('/usr/local/bin/dolt'),
  );
  const jobDoltDestinationReferences = steps.flatMap((step) =>
    typeof step?.run === 'string'
      ? step.run
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter((line) => line.includes('/usr/local/bin/dolt'))
      : [],
  );
  const allowedPinnedDoltLines = [
    /^set -euo pipefail$/,
    /^readonly dolt_version='[^']+'$/,
    /^readonly dolt_sha256='[a-f0-9]{64}'$/,
    /^readonly dolt_archive="(?:\$\{RUNNER_TEMP\}|\/tmp)\/dolt-linux-amd64-v?\$\{?dolt_version\}?\.tar\.gz"$/,
    /^readonly dolt_extract="(?:\$\{RUNNER_TEMP\}|\/tmp)\/dolt-(?:v\$\{dolt_version\}|extract)"$/,
    /^mkdir -p "\$dolt_extract"$/,
    /^curl --fail --location --silent --show-error \\$/,
    /^"https:\/\/github\.com\/dolthub\/dolt\/releases\/download\/v\$\{dolt_version\}\/dolt-linux-amd64\.tar\.gz" \\$/,
    /^--output "\$dolt_archive"$/,
    /^printf '%s {2}%s\\n' "\$dolt_sha256" "\$dolt_archive" \| sha256sum --check --strict$/,
    /^tar -xzf "\$dolt_archive" -C "\$dolt_extract"$/,
    new RegExp(`^${canonicalDoltInstall.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`),
    /^installed_dolt_version="\$\(dolt version \| awk 'NR == 1 \{ print \$3 \}'\)"$/,
    /^readonly installed_dolt_version$/,
    /^test "\$installed_dolt_version" = "\$dolt_version"$/,
  ];
  const onlyPinnedDoltCommands = doltLines.every((line) =>
    allowedPinnedDoltLines.some((pattern) => pattern.test(line)),
  );
  const checks = {
    blocking_ci_registration:
      Array.isArray(matrixTypes) &&
      matrixTypes.includes('python-tests') &&
      Array.isArray(ciNeeds) &&
      ciNeeds.includes('test') &&
      pythonIf(hermeticStep) &&
      hermeticStep?.['continue-on-error'] !== true &&
      hermeticStep?.run?.trim() === canonicalHermeticRun,
    dependencies_fail_closed:
      !/@unittest\.skipUnless/.test(source) &&
      /def setUpClass\(cls\):/.test(source) &&
      /missing required tools/.test(source) &&
      /raise AssertionError/.test(source) &&
      executionShape.runner_fail_closed === true,
    full_cycle:
      executionShape.parsed === true &&
      executionShape.no_dead_code === true &&
      executionShape.reachable_full_cycle === true &&
      !/expected=\(0, 1\)/.test(source) &&
      !/UPDATE skill_compliance/.test(source),
    pinned_dolt:
      pythonIf(doltStep) &&
      onlyPinnedDoltCommands &&
      doltDestinationReferences.length === 1 &&
      doltDestinationReferences[0] === canonicalDoltInstall &&
      jobDoltDestinationReferences.length === 1 &&
      jobDoltDestinationReferences[0] === canonicalDoltInstall &&
      doltStepIndex >= 0 &&
      hermeticStepIndex === doltStepIndex + 1 &&
      /readonly dolt_version='[^']+'/.test(doltRun) &&
      /readonly dolt_sha256='[a-f0-9]{64}'/.test(doltRun) &&
      /printf[^\n]+"\$dolt_sha256"[^\n]+"\$dolt_archive"[^\n]+sha256sum --check --strict/.test(
        doltRun,
      ) &&
      /tar -xzf "\$dolt_archive" -C "\$dolt_extract"/.test(doltRun) &&
      /sudo install -m 0755 "\$dolt_extract\/dolt-linux-amd64\/bin\/dolt" \/usr\/local\/bin\/dolt/.test(
        doltRun,
      ) &&
      /installed_dolt_version="\$\(dolt version \| awk 'NR == 1 \{ print \$3 \}'\)"\s+readonly installed_dolt_version/.test(
        doltRun,
      ) &&
      /test "\$installed_dolt_version" = "\$dolt_version"/.test(doltRun),
    scratch_state:
      /TemporaryDirectory\(prefix=["']freshie-hermetic-/.test(source) &&
      /--dolt-dir/.test(source) &&
      /--grades-csv/.test(source) &&
      /--curated-dir/.test(source) &&
      executionShape.isolated_dolt_identity === true,
    server_refusal: executionShape.reachable_server_refusal === true,
    fake_remote_push: executionShape.reachable_fake_remote_push === true,
  };
  return {
    checks,
    sources: [testPath, workflowPath, 'scripts/measure-epic-1.mjs'].filter((path) =>
      reader.pathSet.has(path),
    ),
    targetMet: Object.values(checks).every(Boolean),
  };
}

/** Build every numbered row not owned by the core rows 1-4, 11, and 12. */
export function buildExtendedScorecardRows({
  hermeticTestContract,
  root,
  paths,
  skillRows,
  skillSummary,
  marketplaceSummary,
  agentSummary,
}) {
  assertInputs(root, paths, skillRows);
  const reader = makeReader(root, paths);
  const rows = gradeRows(skillRows, reader.pathSet, root);
  const frontmatter = allowedToolsCensus(reader, rows);
  const generated = generatedArtifacts(reader);
  const readmeWriters = readmeMetricWriters(reader);
  const stats = publicStats(reader);
  const keys = sourceKeys(reader);
  const mirrors = mirrorInventory(reader);
  const publishers = publishWorkflows(reader);
  const swallowed = releaseSwallows(reader);
  const pins = packagePins(reader);
  const invocations = marketplaceInvocations(reader);
  const needs = ciRequiredNeeds(reader);
  const versions = schemaVersions(reader);
  const authority = authorityCensus(reader);
  const index = docsIndex(reader);
  const visibility = gitleaksVisibility(reader);
  const output = {};

  output[5] = baseRow(
    5,
    gradeMeasurements(rows).average_score === null ? 'partial' : 'measured',
    'tracked path-bearing SKILL.md rows emitted by the canonical marketplace validator',
    ['scripts/validate-skills-schema.py'],
    gradeMeasurements(rows),
    gradeMeasurements(rows).average_score === null
      ? { limitations: ['average_score is null when the validator rows omit a numeric score'] }
      : {},
  );
  output[6] = baseRow(
    6,
    'measured',
    'tracked A- and B-grade SKILL.md validator rows with one or more errors',
    ['scripts/validate-skills-schema.py'],
    {
      ...abFailures(rows),
      certified_target: 0,
      skill_summary_rows: finiteCount(skillSummary?.rows),
    },
  );
  output[7] = unresolved(7, 'canonical validator diagnostics');
  output[8] = unresolved(8, 'canonical validator diagnostics');
  output[9] = unresolved(9, 'canonical validator diagnostics');
  output[10] = baseRow(
    10,
    'partial',
    'agent validator terminal summary; reported compliance may use a mixed numerator',
    ['scripts/validate-skills-schema.py'],
    {
      agent_errors: finiteCount(agentSummary?.errors),
      agent_files: finiteCount(agentSummary?.agents ?? agentSummary?.total_files),
      reported_compliance_percent: Number.isFinite(agentSummary?.compliance_percent)
        ? agentSummary.compliance_percent
        : null,
      target_errors: 0,
      target_percent_max: 100,
    },
    {
      limitations: [
        'the canonical terminal reporter can include plugin-manifest outcomes in its numerator',
      ],
    },
  );
  output[13] = baseRow(
    13,
    'partial',
    'tracked validator SKILL.md rows parsed as YAML frontmatter',
    ['scripts/validate-skills-schema.py', 'tests/test_validate_skills_schema_frontmatter.py'],
    { ...frontmatter.allowedTools, target_malformed: 0 },
    {
      limitations: [
        'unknown-tool vocabulary advisories are not exposed in the supplied validator rows',
      ],
    },
  );
  output[14] = baseRow(
    14,
    'measured',
    'nonempty compatibility strings in tracked validator SKILL.md rows',
    ['scripts/validate-skills-schema.py'],
    { ...frontmatter.compatibility, target_free_text_values: 0 },
  );
  output[15] = unresolved(15, 'tracked plugin and adapter artifacts');
  output[16] = unresolved(16, 'tracked plugin and adapter artifacts');
  output[17] = unresolved(17, 'tracked textual files');
  output[18] = unresolved(18, 'tracked textual files');
  output[19] = unresolved(19, 'tracked textual files');

  const debtSurface = (path) => !isMeasurementInstrumentation(path);
  const anthropicLinks = literalCensus(reader, 'docs.anthropic.com', debtSurface);
  output[20] = baseRow(
    20,
    'partial',
    'literal docs.anthropic.com occurrences in tracked text-like files',
    anthropicLinks.paths,
    null,
    {
      reason_code: 'MISSING_GENERATED_ARTIFACT_CLASSIFIER',
      required_inputs: [
        'machine-readable generated-artifact registry for source versus projection split',
      ],
      measured_proxy: anthropicLinks,
    },
  );
  const deadDomain = {
    ...scanDeadDomainPolicy({ root: reader.root, paths: reader.paths }),
    baseline_receipt: DEAD_DOMAIN_BASELINE_RECEIPT,
  };
  output[21] = baseRow(
    21,
    deadDomain.refused.length === 0 ? 'measured' : 'undefined',
    'tracked retired-domain references classified by first-party, generated, frozen, and provenance-owned policy',
    deadDomain.all_policy_surface.paths,
    deadDomain,
  );
  const ungatedGenerated = generated.filter((entry) => !entry.content_drift_gate);
  output[22] = baseRow(
    22,
    ungatedGenerated.length === 0 ? 'measured' : 'partial',
    'deterministic tracked marketplace projections classified by the artifact authority registry and executable writers',
    generated.flatMap((entry) => [...entry.producers, ...entry.wired_checkers]),
    {
      artifacts: generated,
      count_without_content_drift_gate: ungatedGenerated.length,
      target_without_content_drift_gate: 0,
    },
    {
      limitations: [
        'writer and drift-gate discovery is conservative static analysis; unregistered writer-backed JSON stays in the cohort and indirect runtime paths remain visible as a limitation',
      ],
    },
  );
  output[23] = unresolved(
    23,
    'tracked generated marketplace artifacts',
    generated.map((entry) => entry.path),
  );
  const answers = publicSkillAnswers(reader);
  output[24] = baseRow(
    24,
    'measured',
    'five named skill cohorts from the canonical corpus resolver',
    rowSources(
      'scripts/corpus-resolver.mjs',
      '.claude-plugin/marketplace.extended.json',
      'scripts/plugin-provenance.mjs',
      'skills/.curated/MANIFEST.json',
    ).filter((path) => reader.pathSet.has(path)),
    {
      answers,
      distinct_numeric_answers: new Set(answers.map((entry) => entry.value)).size,
      named_cohorts: answers.length,
    },
  );
  output[25] = baseRow(
    25,
    'partial',
    'tracked executable sources that write README.md and reference count-bearing marketplace facts',
    readmeWriters,
    { count: readmeWriters.length, target: 1, writers: readmeWriters },
    {
      limitations: [
        'static discovery requires both a README write and a metric signal; runtime-computed output aliases require an explicit contract to become fully measured',
      ],
    },
  );
  output[26] = baseRow(
    26,
    'partial',
    'tracked marketplace data files whose names identify public stats projections',
    stats.sources.map((entry) => entry.path),
    { ...stats, target_without_valid_bound: 0 },
    {
      limitations: [
        'no wall clock is consulted, so this row reports enforceable bounds rather than current age',
      ],
    },
  );
  output[27] = keys
    ? baseRow(
        27,
        'measured',
        'tracked source names and lock keys',
        ['sources.lock.json', 'sources.yaml'],
        { ...keys, target_equal: true },
      )
    : baseRow(
        27,
        'undefined',
        'tracked source registry files',
        ['sources.lock.json', 'sources.yaml'],
        null,
        {
          reason_code: 'MALFORMED_OR_MISSING_SOURCE_REGISTRY',
          required_inputs: [
            'parseable sources.yaml with unique names',
            'parseable sources.lock.json.sources',
          ],
        },
      );
  output[28] = baseRow(
    28,
    'measured',
    'directories identified only by a tracked .source.json marker',
    mirrors.markers,
    {
      missing_license_text: mirrors.licenses
        .filter((entry) => entry.license_files.length === 0)
        .map((entry) => entry.root),
      mirrors_shipping_license_text: mirrors.licenses.filter(
        (entry) => entry.license_files.length > 0,
      ).length,
      provenance_marked_mirrors: mirrors.roots.length,
      target_shipping_license_text: mirrors.roots.length,
    },
  );
  output[29] = unresolved(29, 'provenance-marked mirrors', mirrors.markers, {
    local_source_records_with_parseable_json: mirrors.markers.filter((path) => reader.json(path))
      .length,
  });
  output[30] = baseRow(
    30,
    'partial',
    'package.json at each directory carrying a tracked .source.json marker',
    rowSources(
      mirrors.markers,
      mirrors.packages.map((entry) => entry.package),
    ),
    {
      non_private: mirrors.packages.filter((entry) => !entry.private).map((entry) => entry.package),
      private_packages: mirrors.packages.filter((entry) => entry.private).length,
      repository_package_mirrors: mirrors.packages.length,
      scoped_packages: mirrors.packages.filter((entry) => entry.name?.startsWith('@')).length,
      target_publishable: 0,
    },
    {
      limitations: [
        'live npm publication and ownership classification are external state and are not inferred from names',
      ],
    },
  );
  const mirrorPublishers = mirrorCapablePublishWorkflows(reader, publishers);
  const privateBoundary =
    mirrors.packages.length > 0 && mirrors.packages.every((entry) => entry.private);
  const candidateReport = reader.text('scripts/publish-candidate-report.mjs') ?? '';
  const provenanceResolver = reader.text('scripts/plugin-provenance.mjs') ?? '';
  const provenanceBoundary =
    mirrorPublishers.length > 0 &&
    mirrorPublishers.every((path) =>
      (reader.text(path) ?? '').includes('publish-candidate-report.mjs'),
    ) &&
    /resolvePluginProvenance/.test(candidateReport) &&
    /\.source\.json/.test(provenanceResolver);
  output[31] = baseRow(
    31,
    'measured',
    'local repository publication boundaries for provenance-marked package mirrors',
    rowSources(
      mirrors.markers,
      mirrors.packages.map((entry) => entry.package),
      publishers,
      'scripts/plugin-provenance.mjs',
      'scripts/publish-candidate-report.mjs',
    ).filter((path) => reader.pathSet.has(path)),
    {
      boundaries_live: Number(privateBoundary) + Number(provenanceBoundary),
      mirror_capable_publishers: mirrorPublishers,
      package_private_boundary: privateBoundary,
      publisher_provenance_boundary: provenanceBoundary,
      target_boundaries: 2,
    },
  );
  const changedPublisher = reader.text('.github/workflows/publish-changed-packages.yml') ?? '';
  output[32] = baseRow(
    32,
    'partial',
    'tracked npm publishing workflows',
    publishers,
    {
      changed_publisher_workflow_run: /workflow_run:/.test(changedPublisher),
      exact_sha_preflight_all_publishers:
        publishers.length > 0 &&
        publishers.every((path) =>
          (reader.text(path) ?? '').includes('npm-publication-preflight.mjs'),
        ),
      npm_production_declared_all_publishers:
        publishers.length > 0 &&
        publishers.every((path) => /environment:\s*npm-production/.test(reader.text(path) ?? '')),
      publishers: publishers.length,
      required_locks: 3,
    },
    {
      limitations: [
        'GitHub Environment reviewer, bypass, and secret settings are not committed repository state',
      ],
    },
  );
  output[33] = baseRow(
    33,
    'measured',
    'tag and GitHub-release operations after npm publication in the changed-package publisher',
    reader.pathSet.has('.github/workflows/publish-changed-packages.yml')
      ? ['.github/workflows/publish-changed-packages.yml']
      : [],
    { swallowed_operations: swallowed, swallowed_total: swallowed.length, target: 0 },
  );
  const release = reader.text('.github/workflows/release.yml') ?? '';
  output[34] = baseRow(
    34,
    'measured',
    'tracked release workflow inputs and validation conditions',
    reader.pathSet.has('.github/workflows/release.yml') ? ['.github/workflows/release.yml'] : [],
    {
      skip_tests_bypass_present:
        /skip_tests\s*:/.test(release) && /if:\s*\$\{\{\s*!inputs\.skip_tests\s*\}\}/.test(release),
      target_present: false,
    },
  );
  const sboms = reader.paths.filter((path) =>
    /(?:^|\/)(?:sbom|[^/]+\.(?:cdx|spdx))\.(?:json|xml)$/i.test(path),
  );
  output[35] = baseRow(
    35,
    'measured',
    'tracked SPDX/CycloneDX or explicitly named SBOM files',
    sboms,
    { sboms: sboms.length, target_minimum: 15 },
  );
  const workflowEntries = reader.paths
    .filter((path) => /^\.github\/workflows\/[^/]+\.ya?ml$/.test(path))
    .map((path) => ({ path, text: reader.text(path) ?? '' }));
  const actionPins = inspectWorkflowEntries(workflowEntries);
  output[36] = baseRow(
    36,
    'measured',
    'tracked OIDC, npm-token, and signing workflows selected by the E7.9 privileged-action policy',
    actionPins.privilegedWorkflows,
    {
      distinct_actions: actionPins.distinctActions.length,
      mutable_uses: actionPins.unpinned.map((entry) => `${entry.path}:${entry.line}`),
      target_mutable_uses: 0,
      total_uses: actionPins.uses.length,
    },
  );
  const dependabot = reader.paths.filter((path) => /^\.github\/dependabot\.ya?ml$/.test(path));
  output[37] = baseRow(37, 'measured', 'tracked .github Dependabot configuration', dependabot, {
    present: dependabot.length === 1,
    target_present: true,
  });
  const epic9EvidencePath = '000-docs/810-RA-DATA-epic-9-boundary-evidence.json';
  const epic9Evidence = reader.json(epic9EvidencePath);
  const registryPackages = epic9Evidence?.package_registry?.packages ?? null;
  const pinNames = [
    '@intentsolutions/audit-harness',
    '@intentsolutions/core',
    '@intentsolutions/jrig-cli',
  ];
  const registryMatchesPins =
    registryPackages != null &&
    pinNames.every(
      (name) =>
        pins[name]?.exact === true &&
        typeof registryPackages[name]?.version === 'string' &&
        registryPackages[name].version === pins[name].version,
    );
  let couplingSteps = [];
  try {
    const couplingWorkflow = yaml.load(
      reader.text('.github/workflows/kernel-vendor-hash.yml') ?? '',
    );
    couplingSteps = couplingWorkflow?.jobs?.['kernel-vendor-hash']?.steps ?? [];
  } catch {
    couplingSteps = [];
  }
  const orderingStep = couplingSteps.find((step) =>
    String(step?.name ?? '').includes('Version-ordering invariant test corpus'),
  );
  const alertStep = couplingSteps.find((step) =>
    String(step?.name ?? '').includes('Alert Slack on kernel coupling violation'),
  );
  const orderingTestBlocking =
    orderingStep != null &&
    orderingStep['continue-on-error'] !== true &&
    String(orderingStep.run ?? '').includes('kernel-vendor-hash.test.mjs');
  const stalenessAlertRouted =
    alertStep != null &&
    String(alertStep.if ?? '').includes("steps.vendor-hash.outputs.violation == 'true'") &&
    String(alertStep.run ?? '').includes('curl');
  const singleResolvedCore =
    Array.isArray(epic9Evidence?.package_registry?.resolved_core_versions) &&
    epic9Evidence.package_registry.resolved_core_versions.length === 1 &&
    epic9Evidence.package_registry.resolved_core_versions[0] ===
      pins['@intentsolutions/core'].version;
  const pinsAtTarget =
    registryMatchesPins && orderingTestBlocking && stalenessAlertRouted && singleResolvedCore;
  const pinLimitations = [];
  if (!registryMatchesPins) {
    const mismatches = pinNames
      .filter((name) => registryPackages?.[name]?.version !== pins[name]?.version)
      .map(
        (name) =>
          `${name}: observed ${registryPackages?.[name]?.version ?? 'missing'}, pinned ${pins[name]?.version ?? 'missing'}`,
      );
    pinLimitations.push(
      `retained package-registry observation in ${epic9EvidencePath} does not match the exact root pins (${mismatches.join(', ')}); capture a new versioned boundary observation without rewriting retained evidence`,
    );
  }
  if (!singleResolvedCore) {
    pinLimitations.push(
      'the retained package graph does not resolve exactly one pinned core version',
    );
  }
  if (!orderingTestBlocking) {
    pinLimitations.push('the package version-ordering test corpus is not blocking');
  }
  if (!stalenessAlertRouted) {
    pinLimitations.push('the package-coupling staleness alert is not routed');
  }
  output[38] = epic9Evidence
    ? baseRow(
        38,
        pinsAtTarget ? 'target_met' : 'partial',
        'exact root pins, retained npm registry observation, and coupling workflow',
        [
          'package.json',
          'pnpm-lock.yaml',
          '.github/workflows/kernel-vendor-hash.yml',
          epic9EvidencePath,
        ].filter((path) => reader.pathSet.has(path)),
        {
          pins,
          published_latest_versions: Object.fromEntries(
            pinNames.map((name) => [name, registryPackages?.[name]?.version ?? null]),
          ),
          registry_matches_pins: registryMatchesPins,
          one_resolved_core_version: singleResolvedCore,
          ordering_test_blocking: orderingTestBlocking,
          staleness_alert_routed: stalenessAlertRouted,
          target_met: pinsAtTarget,
        },
        pinsAtTarget
          ? {}
          : {
              limitations: pinLimitations,
            },
      )
    : baseRow(38, 'not_reproducible', 'kernel, eval CLI, and harness pins', [], null, {
        reason_code: 'PACKAGE_REGISTRY_SNAPSHOT_NOT_TRACKED',
        required_inputs: ['versioned package-registry metadata snapshot'],
      });
  const shadowPath = epic9EvidencePath;
  const shadow = epic9Evidence?.kernel_shadow ?? null;
  const shadowHasBothLanes =
    shadow?.lanes?.['authoring/v1'] != null &&
    shadow?.lanes?.['authoring/v2']?.decision_relevant_metric === 'existing-PASS / kernel-FAIL' &&
    Number.isInteger(shadow?.lanes?.['authoring/v2']?.existing_pass_kernel_fail);
  const shadowCurrent =
    shadowHasBothLanes &&
    shadow.kernel_version === pins['@intentsolutions/core'].version &&
    shadow.kernel_pin === pins['@intentsolutions/core'].version;
  output[39] = shadow
    ? baseRow(
        39,
        shadowCurrent ? 'target_met' : 'stale_evidence',
        'retained exact-head kernel-shadow boundary report',
        [shadowPath, 'package.json'],
        { report: shadow, root_kernel_pin: pins['@intentsolutions/core'].version },
        {
          limitations: [
            'this is a point-in-time exact-head closure receipt; the advisory workflow remains the live recurring observation lane',
          ],
        },
      )
    : baseRow(39, 'not_reproducible', 'kernel shadow boundary output', [], null, {
        reason_code: 'KERNEL_SHADOW_REPORT_NOT_TRACKED',
        required_inputs: [
          'deterministic tracked shadow report generated at the current kernel pin',
        ],
      });
  output[40] = baseRow(
    40,
    'partial',
    'tracked workflow command lines invoking the canonical validator with --marketplace',
    [...new Set(invocations.map((entry) => entry.path))],
    {
      blocking_candidates: invocations.filter((entry) => entry.blocking_candidate).length,
      invocations,
      target_blocking: 1,
    },
    { limitations: ['static workflow analysis does not execute GitHub expression control flow'] },
  );
  output[41] = needs.error
    ? baseRow(
        41,
        'undefined',
        'ci-required needs list in validate-plugins.yml',
        reader.pathSet.has('.github/workflows/validate-plugins.yml')
          ? ['.github/workflows/validate-plugins.yml']
          : [],
        null,
        {
          reason_code: needs.error,
          required_inputs: [
            'parseable nonempty unique jobs.ci-required.needs in validate-plugins.yml',
          ],
        },
      )
    : baseRow(
        41,
        'partial',
        'ci-required needs list in validate-plugins.yml',
        ['.github/workflows/validate-plugins.yml'],
        {
          actual_needs: needs.needs,
          actual_needs_count: needs.needs.length,
          documented_needs: null,
        },
        {
          reason_code: 'MISSING_MACHINE_READABLE_DOCUMENTED_NEEDS_LIST',
          required_inputs: ['one machine-readable documented ci-required needs list'],
        },
      );
  output[42] = baseRow(
    42,
    'measured',
    'runtime schema constant and active schema banners',
    rowSources(
      'scripts/validate-skills-schema.py',
      versions.docs.map((entry) => entry.path),
    ).filter((path) => reader.pathSet.has(path)),
    {
      all_equal:
        versions.runtime !== null &&
        versions.docs.every((entry) => entry.version === versions.runtime),
      documented: versions.docs,
      runtime: versions.runtime,
    },
  );
  output[43] = baseRow(
    43,
    'measured',
    'effective top-level authority declarations in tracked 000-docs Markdown and STANDARDS links',
    rowSources('STANDARDS.md', authority.authority_links, authority.unlinked),
    { ...authority, target_unlinked: 0 },
  );
  output[44] = baseRow(
    44,
    'measured',
    'tracked 000-docs estate excluding the generated index and filing ignore ledger',
    ['000-docs/000-INDEX.md', '000-docs/761-AA-AACR-epic-1-social-image-count-cohort.md'],
    { ...index, target_equal: true },
  );
  const proseWorkflows = reader.paths
    .filter((path) => path.startsWith('.github/workflows/'))
    .filter((path) =>
      /(?:test_prose_anchors|parse-prose-anchors\.py)/.test(reader.text(path) ?? ''),
    );
  output[45] = baseRow(
    45,
    'measured',
    'tracked workflows invoking the prose-anchor checker or its regression suite',
    proseWorkflows,
    { target_workflows: 1, workflows: proseWorkflows.length },
  );
  output[46] = visibility
    ? baseRow(
        46,
        visibility.invalid_patterns === 0 ? 'measured' : 'partial',
        'tracked paths matching the gitleaks path allowlist',
        ['.gitleaks.toml'],
        { ...visibility, target_invisible_files: 0 },
        visibility.invalid_patterns === 0
          ? {}
          : {
              limitations: [
                'one or more Python-style allowlist regexes could not be represented by JavaScript RegExp',
              ],
            },
      )
    : baseRow(46, 'undefined', 'gitleaks path allowlist', [], null, {
        reason_code: 'MISSING_GITLEAKS_CONFIGURATION',
        required_inputs: ['tracked .gitleaks.toml'],
      });
  const unverifiable = reader.paths
    .filter((path) => path.startsWith('.github/workflows/'))
    .filter((path) => /trufflehog/i.test(reader.text(path) ?? ''))
    .map((path) => ({
      only_verified: /--only-verified/.test(reader.text(path) ?? ''),
      path,
      pull_request: /pull_request(?:_target)?\s*:/.test(reader.text(path) ?? ''),
    }));
  output[47] = baseRow(
    47,
    'partial',
    'tracked workflows invoking TruffleHog',
    unverifiable.map((entry) => entry.path),
    {
      blocking_unverifiable_pr_scans: unverifiable.filter(
        (entry) => entry.pull_request && !entry.only_verified,
      ).length,
      invocations: unverifiable,
      target_blocking: 1,
    },
    {
      limitations: [
        'required-status topology is external; this scan proves only committed trigger and flag configuration',
      ],
    },
  );
  const validationWorkflow = reader.text('.github/workflows/validate-plugins.yml') ?? '';
  const supplyChainMentions = [...validationWorkflow.matchAll(/supply[- ]chain/gi)].length;
  output[48] = baseRow(
    48,
    'partial',
    'supply-chain scanner configuration in the canonical validation workflow',
    reader.pathSet.has('.github/workflows/validate-plugins.yml')
      ? ['.github/workflows/validate-plugins.yml']
      : [],
    {
      push_trigger_present: /^\s{2}push:\s*$/m.test(validationWorkflow),
      scanner_mentions: supplyChainMentions,
      scanner_pr_only_guard_present:
        supplyChainMentions > 0 &&
        /github\.event_name\s*==\s*['"]pull_request['"]/.test(validationWorkflow),
    },
    {
      limitations: [
        'static workflow evidence cannot prove runtime scanner coverage without a registered scanner job contract',
      ],
    },
  );
  for (const number of [49, 50, 51]) output[number] = unresolved(number);
  const freshieRun = latestFreshieRunReceipt(reader);
  output[52] = freshieRun?.valid
    ? baseRow(
        52,
        freshieRun.coherence.skillDelta === 0 ? 'target_met' : 'partial',
        'latest tracked immutable Freshie run receipt',
        [freshieRun.path, 'freshie/scripts/dolt-sync.py', 'freshie/scripts/run-delta.py'],
        {
          dolt_commit: freshieRun.report.dolt_commit,
          header_total_skills: freshieRun.coherence.headerTotal,
          run_id: freshieRun.runId,
          skill_row_delta: freshieRun.coherence.skillDelta,
          skill_rows: freshieRun.coherence.skillRows,
          target_skill_row_delta: 0,
        },
      )
    : unresolved(52, 'latest tracked immutable Freshie run receipt', freshieRun?.path ?? []);

  const histogramPath = 'freshie/grade-histogram.json';
  const gradesPath = 'freshie/grades.csv';
  const histogram = reader.json(histogramPath);
  const gradesText = reader.text(gradesPath);
  const gradesSha256 =
    gradesText === null ? null : createHash('sha256').update(gradesText).digest('hex');
  if (
    freshieRun?.valid &&
    finiteCount(histogram?.run_id) !== null &&
    finiteCount(histogram?.total) !== null &&
    gradesSha256 !== null
  ) {
    const immutableExport = freshieRun.report.grade_export;
    const current =
      histogram.run_id === freshieRun.runId &&
      histogram.dolt_commit === freshieRun.report.dolt_commit &&
      histogram.grades_csv_sha256 === gradesSha256 &&
      gradesSha256 === immutableExport.csv_sha256 &&
      histogram.total === immutableExport.row_count &&
      immutableExport.row_count === freshieRun.coherence.complianceRows &&
      canonicalJson(histogram.grades) === canonicalJson(immutableExport.grade_counts);
    output[53] = baseRow(
      53,
      current ? 'target_met' : 'partial',
      'tracked grade exports against the latest immutable Freshie run receipt',
      [freshieRun.path, histogramPath, gradesPath],
      {
        compliance_rows: freshieRun.coherence.complianceRows,
        export_dolt_commit: histogram.dolt_commit ?? null,
        export_run_id: histogram.run_id,
        grades_csv_rows: immutableExport.row_count,
        grades_csv_sha256: gradesSha256,
        histogram_grades: histogram.grades ?? null,
        histogram_total: histogram.total,
        immutable_grade_counts: immutableExport.grade_counts,
        inventory_run_id: freshieRun.runId,
        inventory_dolt_commit: freshieRun.report.dolt_commit,
        target_lag_runs: 0,
      },
      current
        ? {}
        : {
            reason_code: 'FRESHIE_GRADE_EXPORT_DRIFT',
            required_inputs: ['a same-run grade export and immutable Freshie receipt'],
          },
    );
  } else {
    output[53] = unresolved(
      53,
      'tracked grade exports against the latest immutable Freshie run receipt',
      rowSources(freshieRun?.path, histogramPath, gradesPath).filter((path) =>
        reader.pathSet.has(path),
      ),
    );
  }

  const proofs = forgeProofReceipt(reader, freshieRun);
  if (proofs.valid) {
    const allClassified = proofs.values.unclassified === 0;
    const legacyDemoted = proofs.values.legacy_e0_records === 3;
    output[54] = baseRow(
      54,
      allClassified && legacyDemoted ? 'target_met' : 'partial',
      'tag-bound forge-proof ledger snapshot and legacy demotion receipt',
      [
        proofs.path,
        proofs.sourcePath,
        freshieRun.path,
        'freshie/scripts/dolt-sync.py',
        'freshie/scripts/run-delta.py',
        'scripts/record-jrig-proofs.mjs',
      ],
      { ...proofs.values, target_legacy_e0_records: 3, target_unclassified: 0 },
    );
    const retained = proofs.values.retained_e2_e3 === proofs.values.total_e2_e3;
    const hasClaims = proofs.values.total_e2_e3 > 0;
    output[55] = baseRow(
      55,
      retained && legacyDemoted ? 'target_met' : 'partial',
      'tag-bound evidence-class snapshot and canonical retention standard',
      [
        proofs.path,
        proofs.sourcePath,
        freshieRun.path,
        '000-docs/807-DR-STND-evaluation-evidence.md',
        'freshie/scripts/dolt-sync.py',
        'freshie/scripts/run-delta.py',
      ],
      {
        legacy_e0_records: proofs.values.legacy_e0_records,
        no_e2_e3_claims: !hasClaims,
        retained_e2_e3: proofs.values.retained_e2_e3,
        retention_percent: !hasClaims
          ? null
          : Number(((proofs.values.retained_e2_e3 * 100) / proofs.values.total_e2_e3).toFixed(2)),
        target_retention_percent: 100,
        total_e2_e3: proofs.values.total_e2_e3,
        unretained_e2_e3: proofs.values.total_e2_e3 - proofs.values.retained_e2_e3,
      },
      {
        limitations: hasClaims
          ? []
          : [
              'zero E2/E3 claims satisfies the safety target of zero unretained claims; retention_percent remains null rather than fabricating 100%',
            ],
      },
    );
  } else {
    output[54] = unresolved(54, 'tracked legacy forge-proof demotion receipt', [proofs.path]);
    output[55] = unresolved(55, 'tracked evidence-class receipt', [proofs.path]);
  }
  const jrigPath = 'marketplace/src/data/jrig-data.json';
  const projectionPresent = reader.pathSet.has(jrigPath);
  const claims = verifiedClaims(reader.json(jrigPath));
  output[56] = baseRow(
    56,
    projectionPresent || claims > 0 ? 'partial' : 'target_met',
    'legacy JRig marketplace verification projection',
    projectionPresent ? [jrigPath] : [],
    { public_verified_claims: claims, projection_present: projectionPresent },
    {
      reason_code: projectionPresent
        ? 'RETIRED_PUBLIC_PROJECTION_PRESENT'
        : 'NO_PUBLIC_JRIG_VERIFICATION_PROJECTION',
      required_inputs: projectionPresent
        ? [
            'remove the projection and producer, or replace every entry with a reasoned false verdict',
          ]
        : [],
      limitations: [
        'a future public verification surface requires retained, hash-matched evidence and an explicit consumer boundary',
      ],
    },
  );
  const sourceEvalSpecs = reader.paths.filter(
    (path) => path.startsWith('plugins/') && path.endsWith('/eval-spec.yaml'),
  );
  const pluginSkillFiles = reader.paths.filter((path) => /^plugins\/.+\/SKILL\.md$/.test(path));
  const curatedEvalSpecs = reader.paths.filter(
    (path) => path.startsWith('skills/.curated/') && path.endsWith('/eval-spec.yaml'),
  );
  output[57] = baseRow(
    57,
    'measured',
    'tracked plugin eval-spec.yaml files divided by tracked plugin SKILL.md validator rows',
    rowSources(sourceEvalSpecs, curatedEvalSpecs),
    {
      adoption_percent:
        pluginSkillFiles.length === 0
          ? null
          : Number(((sourceEvalSpecs.length * 100) / pluginSkillFiles.length).toFixed(2)),
      curated_copies: curatedEvalSpecs.length,
      plugin_skill_rows: pluginSkillFiles.length,
      source_eval_specs: sourceEvalSpecs.length,
      tracked_eval_specs: sourceEvalSpecs.length + curatedEvalSpecs.length,
    },
  );
  const hermetic = freshieHermeticContract(reader, hermeticTestContract);
  output[58] = baseRow(
    58,
    hermetic.targetMet ? 'target_met' : 'partial',
    'tracked Freshie hermetic-cycle test and blocking Python CI lane',
    hermetic.sources,
    { ...hermetic.checks, target_all_checks: true },
    hermetic.targetMet
      ? {}
      : {
          reason_code: 'FRESHIE_HERMETIC_CYCLE_NOT_BLOCKING',
          required_inputs: ['an unskipped scratch-database full cycle in blocking CI'],
        },
  );
  const doltSource = reader.text('freshie/scripts/dolt-sync.py') ?? '';
  const doltTests = reader.text('tests/test_dolt_sync.py') ?? '';
  output[59] = baseRow(
    59,
    'measured',
    'tracked Dolt sync writer and its focused tests',
    rowSources('freshie/scripts/dolt-sync.py', 'tests/test_dolt_sync.py').filter((path) =>
      reader.pathSet.has(path),
    ),
    {
      nonblocking_flock:
        /def acquire_lock\b/.test(doltSource) && /LOCK_EX\s*\|\s*fcntl\.LOCK_NB/.test(doltSource),
      refusal_tests: (
        doltTests.match(/def test_[^(]*(?:lock|server_running|single_writer)[^(]*\(/g) ?? []
      ).length,
      server_lock_refusal:
        /def refuse_if_server_running\b/.test(doltSource) && /sql-server\.lock/.test(doltSource),
      target_mechanical_refusal: true,
    },
  );
  for (const number of [60, 61, 62]) output[number] = unresolved(number);

  const expected = [
    5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62,
  ];
  const actual = Object.keys(output).map(Number);
  if (
    actual.length !== expected.length ||
    actual.some((number, index_) => number !== expected[index_])
  ) {
    throw new Error('extended scorecard row set is incomplete or out of order');
  }
  if (finiteCount(marketplaceSummary?.errors) === null && marketplaceSummary !== undefined) {
    output[10].limitations.push(
      'marketplace summary was supplied without a safe integer error count',
    );
  }
  return output;
}
