#!/usr/bin/env node
/**
 * Generate Blueprint 727 §8's first-match-wins legacy disposition ledger.
 *
 * The Freshie grade export is the graded-artifact authority.  It contains
 * skill-directory paths, whereas validator output contains SKILL.md paths;
 * this script normalizes that boundary, verifies every row still exists, and
 * refuses stale or ambiguous input rather than emitting a partial ledger.
 *
 * First-match-wins gate order (Blueprint 727 §8):
 *   G0 SECURITY          -> QUARANTINE
 *   G1 LEGAL/PROVENANCE -> QUARANTINE
 *   G2 TRUTHFULNESS     -> QUARANTINE
 *   G3 OWNERSHIP        -> CERTIFY-UPSTREAM or QUARANTINE
 *   G4 UNSAFE-BY-DESIGN -> DEEP-REMEDIATE
 *   G5 STRUCTURAL-ONLY  -> AUTO-MIGRATE
 *   G6 CLEAN + PROVEN   -> CERTIFY (emitted only by the retained-evidence evaluator)
 *   G7 CLEAN, NO EVIDENCE -> CERTIFY-PENDING-EVIDENCE
 *
 * Usage:
 *   node scripts/generate-disposition-ledger.mjs
 *   node scripts/generate-disposition-ledger.mjs --check
 *   node scripts/generate-disposition-ledger.mjs --out path/to/ledger.json
 */

import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import yaml from 'js-yaml';

import { resolveCorpus } from './corpus-resolver.mjs';
import { resolvePluginProvenance } from './plugin-provenance.mjs';
import { GRADE, scanContent } from './scan-synced-content.mjs';
import { safeReadFile, safeReadFileIfExists } from './safe-fs.mjs';

const require = createRequire(import.meta.url);
const { sourcePublicationDisposition } = require('./publication-policy.cjs');
const SOURCE_HOLDS = Symbol('source-legal-holds');

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const STRUCTURAL_ERROR =
  /^(?:\[frontmatter\] Missing required field:|\[body\] Required section missing:|\[relative-link\]|\[body\] Line \d+: uses backslashes)/;
const UNSAFE_ERROR = /^\[tier2:(?:tool-safety|orchestration-bounds)\]/;
const SHELL_SUBSTITUTION_ERROR =
  /^\[security\] YAML field '.+' contains shell substitution \(e\.g\. \$\(\.\.\.\), backticks, or \$\{VAR\}\) that will not evaluate:/;
const TRUTHFULNESS_ERROR =
  /(?:Linked file not found|Reference escapes skill directory|contains absolute\/OS-specific path)/;
const BUCKETS = new Set([
  'QUARANTINE',
  'CERTIFY-UPSTREAM',
  'DEEP-REMEDIATE',
  'AUTO-MIGRATE',
  'CERTIFY',
  'CERTIFY-PENDING-EVIDENCE',
]);

function fail(message) {
  throw new Error(`generate-disposition-ledger: ${message}`);
}

function relative(root, value) {
  const resolved = path.resolve(value);
  const output = path.relative(root, resolved).split(path.sep).join('/');
  if (!output || output === '..' || output.startsWith('../') || path.isAbsolute(output)) {
    fail(`path escapes repository: ${value}`);
  }
  return output;
}

function parseArgs(argv) {
  const options = { root: ROOT, out: null, check: false };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--check') options.check = true;
    else if (value === '--root') options.root = argv[++index];
    else if (value === '--out') options.out = argv[++index];
    else fail(`unknown argument ${value}`);
  }
  if (!options.root) fail('--root requires a directory');
  if (options.out === undefined) fail('--out requires a file');
  options.root = fs.realpathSync(path.resolve(options.root));
  options.out = path.resolve(options.root, options.out ?? 'freshie/disposition-ledger.json');
  return options;
}

export function parseGrades(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.shift() !== 'skill_path,grade,score') fail('grades export has an unexpected header');
  const seen = new Set();
  const rows = lines.map((line, index) => {
    const fields = line.split(',');
    if (fields.length !== 3 || !/^[A-F]$/.test(fields[1]) || !/^\d+$/.test(fields[2])) {
      fail(`invalid grades row ${index + 2}`);
    }
    const skillPath = `${fields[0]}/SKILL.md`;
    if (
      !fields[0] ||
      fields[0].startsWith('/') ||
      fields[0].includes('..') ||
      seen.has(skillPath)
    ) {
      fail(`unsafe or duplicate skill path on grades row ${index + 2}`);
    }
    seen.add(skillPath);
    return { path: skillPath, grade: fields[1], score: Number(fields[2]) };
  });
  if (rows.length === 0) fail('grades export has no rows');
  // `localeCompare` varies with the runner locale. The ledger is a
  // byte-addressed artifact, so order paths by code point instead.
  return rows.sort((left, right) => (left.path < right.path ? -1 : left.path > right.path ? 1 : 0));
}

export function assertGradeCorpusParity(
  root,
  gradeRows,
  gradedPaths = resolveCorpus('graded', { root }),
) {
  const gradePaths = new Set(gradeRows.map((row) => row.path));
  const corpusPaths = new Set(gradedPaths);
  const omitted = [...corpusPaths]
    .filter((entry) => !gradePaths.has(entry))
    .sort((left, right) => (left < right ? -1 : left > right ? 1 : 0));
  const stale = [...gradePaths]
    .filter((entry) => !corpusPaths.has(entry))
    .sort((left, right) => (left < right ? -1 : left > right ? 1 : 0));

  if (omitted.length === 0 && stale.length === 0) return;

  const details = [];
  if (omitted.length > 0) {
    details.push(`grades export omits ${omitted.length} graded artifact(s): ${omitted.join(', ')}`);
  }
  if (stale.length > 0) {
    details.push(
      `grades export contains ${stale.length} artifact(s) outside the graded corpus: ${stale.join(', ')}`,
    );
  }
  fail(details.join('; '));
}

function validatorJson(root, args, maxBuffer) {
  try {
    return execFileSync('python3', args, {
      cwd: root,
      encoding: 'utf8',
      maxBuffer,
      stdio: ['ignore', 'pipe', 'ignore'],
    });
  } catch (error) {
    // Validation failures are facts used to classify an artifact; they must
    // not prevent the ledger from recording a non-certifying disposition.
    if (typeof error?.stdout === 'string' && error.stdout.length > 0) return error.stdout;
    fail(`validator did not emit JSON: ${error.message}`);
  }
}

function validateRows(root, gradeRows) {
  const output = validatorJson(
    root,
    [
      'scripts/validate-skills-schema.py',
      '--marketplace',
      '--skills-only',
      '--json',
      '--repo-root',
      root,
    ],
    64 * 1024 * 1024,
  );
  let parsed;
  try {
    parsed = JSON.parse(output);
  } catch (error) {
    fail(`validator did not emit JSON: ${error.message}`);
  }
  const rows = new Map();
  for (const entry of parsed) {
    if (!entry || typeof entry.path !== 'string') continue;
    const entryPath = relative(root, entry.path);
    rows.set(entryPath, entry);
  }

  // A few legacy paths are deliberately excluded from the normal validator
  // discovery set but are still present in Freshie's graded export. Validate
  // only that explicit remainder; this keeps one command reproducible without
  // weakening the inventory boundary.
  for (const gradeRow of gradeRows) {
    if (rows.has(gradeRow.path)) continue;
    const absolute = path.join(root, gradeRow.path);
    if (!fs.statSync(absolute).isFile()) fail(`graded artifact is missing: ${gradeRow.path}`);
    let single;
    try {
      single = JSON.parse(
        validatorJson(
          root,
          [
            'scripts/validate-skills-schema.py',
            '--marketplace',
            '--json',
            '--repo-root',
            root,
            absolute,
          ],
          4 * 1024 * 1024,
        ),
      );
    } catch (error) {
      fail(`cannot validate graded artifact ${gradeRow.path}: ${error.message}`);
    }
    const record = single.find((candidate) => candidate?.path);
    if (!record) fail(`validator omitted graded artifact ${gradeRow.path}`);
    rows.set(gradeRow.path, record);
  }
  return rows;
}

function sourceCommit(markerPath) {
  try {
    const source = JSON.parse(fs.readFileSync(markerPath, 'utf8'));
    const value = source?.synced_from?.source_commit ?? source?.source_commit;
    return typeof value === 'string' && /^[0-9a-f]{7,64}$/i.test(value) ? value : null;
  } catch {
    return null;
  }
}

function sourceLegalHolds(root) {
  const sourceFile = safeReadFileIfExists(root, 'sources.yaml');
  const holds = new Map();
  if (sourceFile === null) return holds;
  const document = yaml.load(sourceFile.content.toString('utf8'));
  if (!Array.isArray(document?.sources)) fail('sources.yaml has no sources array');
  for (const source of document.sources) {
    const disposition = sourcePublicationDisposition(source, {
      readEvidence: (evidence) => safeReadFile(root, evidence),
    });
    if (!disposition?.legal_hold) continue;
    if (holds.has(source.target_path)) fail(`duplicate G1 source target: ${source.target_path}`);
    holds.set(source.target_path, disposition.legal_hold);
  }
  return holds;
}

function mirrorRefuseFindings(root, markerPath) {
  const mirrorRoot = relative(root, path.dirname(markerPath));
  const paths = execFileSync('git', ['ls-files', '-z', '--', mirrorRoot], {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  })
    .split('\0')
    .filter(Boolean);
  const findings = [];
  for (const entry of paths) {
    let content;
    try {
      content = fs.readFileSync(path.join(root, entry), 'utf8');
    } catch {
      continue;
    }
    for (const finding of scanContent(content, entry)) {
      if (finding.grade === GRADE.REFUSE) findings.push(`${entry}:${finding.id}`);
    }
  }
  return findings.sort();
}

function errorsFor(record) {
  // The Python validator aggregates some facts from unordered collections.
  // Preserve every diagnostic, but canonicalize their serialization so a
  // ledger generated on CI byte-matches one generated locally.
  if (Array.isArray(record?.errors)) return [...record.errors].sort();
  if (!Number.isInteger(record?.errors) || record.errors < 0) return ['VALIDATOR_FACT_UNAVAILABLE'];
  if (!Array.isArray(record.error_details)) return ['VALIDATOR_DIAGNOSTICS_UNAVAILABLE'];
  return [...record.error_details].sort();
}

export function classifyArtifact({ root, row, validation, cache = new Map() }) {
  const absolute = path.join(root, row.path);
  fs.readFileSync(absolute, 'utf8');
  const diagnostics = errorsFor(validation);
  const errorCount = Array.isArray(validation.errors)
    ? validation.errors.length
    : validation.errors;
  const provenance = resolvePluginProvenance(path.dirname(row.path), { root });
  const reasonCodes = [];
  const resolved = {
    path: row.path,
    grade: row.grade,
    score: row.score,
    diagnostics,
  };

  // G0: non-waivable security facts take precedence over every later gate.
  // Consume the canonical validator diagnostic instead of maintaining a
  // second, inevitably divergent shell-substitution parser here. This covers
  // all three validator forms: $(...), backticks, and unguarded ${VAR}.
  if (diagnostics.some((diagnostic) => SHELL_SUBSTITUTION_ERROR.test(diagnostic))) {
    return {
      ...resolved,
      disposition: 'QUARANTINE',
      gate: 'G0',
      reason_codes: ['SHELL_SUBSTITUTION'],
    };
  }
  if (provenance.status === 'mirror') {
    const marker = provenance.markerPath;
    let refuses = cache.get(marker);
    if (!refuses) {
      refuses = mirrorRefuseFindings(root, marker);
      cache.set(marker, refuses);
    }
    if (refuses.length > 0) {
      return {
        ...resolved,
        disposition: 'QUARANTINE',
        gate: 'G0',
        reason_codes: refuses,
      };
    }
  }

  // G1: unresolved/malformed provenance and unpinned mirror commits are legal
  // blockers, never quality debt that can be remediated locally.
  if (provenance.status === 'refused') reasonCodes.push(provenance.reasonCode);
  if (provenance.status === 'mirror' && !sourceCommit(provenance.markerPath)) {
    reasonCodes.push('SOURCE_COMMIT_UNPINNED');
  }
  let holds = cache.get(SOURCE_HOLDS);
  if (!holds) {
    holds = sourceLegalHolds(root);
    cache.set(SOURCE_HOLDS, holds);
  }
  let legalHold = null;
  for (const [target, hold] of holds) {
    if (row.path.startsWith(`${target}/`)) {
      legalHold = hold;
      for (const artifact of hold.artifacts) reasonCodes.push(...artifact.reason_codes);
      break;
    }
  }
  if (reasonCodes.length > 0) {
    return {
      ...resolved,
      disposition: 'QUARANTINE',
      gate: 'G1',
      reason_codes: [...new Set(reasonCodes)].sort(),
      ...(legalHold ? { source_hold: legalHold } : {}),
    };
  }

  // G2: objective broken references and capability-path claims are quarantined.
  const truthfulness = diagnostics.filter((diagnostic) => TRUTHFULNESS_ERROR.test(diagnostic));
  if (truthfulness.length > 0) {
    return {
      ...resolved,
      disposition: 'QUARANTINE',
      gate: 'G2',
      reason_codes: truthfulness.sort(),
    };
  }

  // G3: upstream-owned trees are never remediated locally.
  if (provenance.status === 'mirror') {
    return errorCount === 0 && ['A', 'B'].includes(row.grade)
      ? {
          ...resolved,
          disposition: 'CERTIFY-UPSTREAM',
          gate: 'G3',
          reason_codes: ['MIRROR_CLEAN'],
        }
      : {
          ...resolved,
          disposition: 'QUARANTINE',
          gate: 'G3',
          reason_codes: ['MIRROR_NOT_CLEAN'],
        };
  }

  // G4: high-risk authoring safety failures receive a human-only remediation.
  const unsafe = diagnostics.filter((diagnostic) => UNSAFE_ERROR.test(diagnostic));
  if (unsafe.length > 0) {
    return {
      ...resolved,
      disposition: 'DEEP-REMEDIATE',
      gate: 'G4',
      reason_codes: unsafe.sort(),
    };
  }

  // G5: only enumerated deterministic structural failures are eligible for an
  // automatic migration. Any unknown error stays with human remediation.
  if (errorCount > 0 && diagnostics.every((diagnostic) => STRUCTURAL_ERROR.test(diagnostic))) {
    return {
      ...resolved,
      disposition: 'AUTO-MIGRATE',
      gate: 'G5',
      reason_codes: diagnostics.sort(),
    };
  }
  if (errorCount > 0) {
    return {
      ...resolved,
      disposition: 'DEEP-REMEDIATE',
      gate: 'G4',
      reason_codes: ['NON_STRUCTURAL_VALIDATION_FAILURE'],
    };
  }

  // No retained E1–E6 evidence record is manufactured by this generator.
  // Clean first-party artifacts therefore remain explicitly pending evidence.
  return {
    ...resolved,
    disposition: 'CERTIFY-PENDING-EVIDENCE',
    gate: 'G7',
    reason_codes: ['REPRODUCIBLE_EVIDENCE_NOT_RETAINED'],
  };
}

export function buildLedger({ root, grades, validations }) {
  const cache = new Map();
  cache.set(SOURCE_HOLDS, sourceLegalHolds(root));
  const artifacts = grades.map((row) => {
    const validation = validations.get(row.path);
    if (!validation) fail(`validator has no result for graded artifact ${row.path}`);
    return classifyArtifact({ root, row, validation, cache });
  });
  const paths = new Set(artifacts.map((artifact) => artifact.path));
  if (paths.size !== grades.length) fail('ledger contains duplicate artifact paths');
  const counts = Object.fromEntries([...BUCKETS].sort().map((bucket) => [bucket, 0]));
  for (const artifact of artifacts) {
    if (!BUCKETS.has(artifact.disposition)) fail(`unknown disposition ${artifact.disposition}`);
    counts[artifact.disposition] += 1;
  }
  const gradesHash = crypto
    .createHash('sha256')
    .update(fs.readFileSync(path.join(root, 'freshie/grades.csv')))
    .digest('hex');
  return {
    schema_version: 'disposition-ledger/v1',
    authority: 'Blueprint 727 §8; Freshie graded export',
    source: {
      path: 'freshie/grades.csv',
      sha256: gradesHash,
      artifact_count: artifacts.length,
    },
    rule_order: ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9'],
    counts,
    artifacts,
  };
}

export function main(argv = process.argv.slice(2)) {
  const options = parseArgs(argv);
  const gradePath = path.join(options.root, 'freshie/grades.csv');
  const grades = parseGrades(fs.readFileSync(gradePath, 'utf8'));
  assertGradeCorpusParity(options.root, grades);
  for (const row of grades) {
    if (!fs.existsSync(path.join(options.root, row.path)))
      fail(`graded artifact is missing: ${row.path}`);
  }
  const ledger = buildLedger({
    root: options.root,
    grades,
    validations: validateRows(options.root, grades),
  });
  const rendered = `${JSON.stringify(ledger, null, 2)}\n`;
  if (options.check) {
    const actual = fs.existsSync(options.out) ? fs.readFileSync(options.out, 'utf8') : null;
    if (actual !== rendered) {
      const expectedDigest = crypto.createHash('sha256').update(rendered).digest('hex');
      const actualDigest = actual
        ? crypto.createHash('sha256').update(actual).digest('hex')
        : 'missing';
      fail(
        `${relative(options.root, options.out)} is stale; rerun generate-disposition-ledger.mjs ` +
          `(expected sha256 ${expectedDigest}, actual sha256 ${actualDigest})`,
      );
    }
  } else {
    fs.writeFileSync(options.out, rendered);
  }
  return ledger;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    const ledger = main();
    process.stdout.write(`disposition ledger: ${ledger.source.artifact_count} artifacts\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
