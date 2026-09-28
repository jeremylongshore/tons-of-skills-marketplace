#!/usr/bin/env node
/**
 * Evaluate certification from machine facts only.
 *
 * Usage:
 *   node scripts/evaluate-certification.mjs \
 *     --validator validator.json --scanner scanner.json --ledger ledger.json \
 *     --dispositions dispositions.json [--out certification-report.json]
 *     [--max-age-hours 24]
 *
 * Input contracts deliberately stay small and explicit:
 * - validator: { artifacts: [{ path, errors, gates: { G1..G10: boolean } }] }
 * - scanner: { findings: [{ path|artifact_path, class|severity|status }] }
 * - ledger: { records: [{ artifact_path|path, evidence_class, artifact_uri,
 *                         artifact_sha256, baseline_delta, recorded_by_identity,
 *                         producing_identity, provenance_hash }] }
 * - dispositions: { artifacts: [{ path|artifact_path, disposition }] }
 *
 * These are the only decision inputs. Missing, unreadable, malformed, or stale
 * input becomes a written NOT-CERTIFIED report with E-EVIDENCE-UNAVAILABLE;
 * it never becomes inferred success.
 */

import fs from 'node:fs';
import path from 'node:path';

const GATES = Object.freeze(Array.from({ length: 10 }, (_, index) => `G${index + 1}`));
const EVIDENCE_RANK = Object.freeze({ E0: 0, E1: 1, E2: 2, E3: 3 });

function fail(message) {
  const error = new Error(message);
  error.isCliFailure = true;
  throw error;
}

function parseArgs(argv) {
  const values = {};
  const allowed = new Set([
    '--validator',
    '--scanner',
    '--ledger',
    '--dispositions',
    '--out',
    '--max-age-hours',
  ]);
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (!allowed.has(flag)) fail(`Unknown argument: ${flag}`);
    if (values[flag]) fail(`${flag} may be supplied only once`);
    const value = argv[++index];
    if (!value) fail(`${flag} requires a path`);
    values[flag] = value;
  }
  for (const flag of ['--validator', '--scanner', '--ledger', '--dispositions']) {
    if (!values[flag]) fail(`Missing required argument: ${flag}`);
  }
  const maxAgeHours = Number(values['--max-age-hours'] ?? 24);
  if (!Number.isFinite(maxAgeHours) || maxAgeHours <= 0) {
    fail('--max-age-hours must be a positive number');
  }
  return {
    validator: values['--validator'],
    scanner: values['--scanner'],
    ledger: values['--ledger'],
    dispositions: values['--dispositions'],
    out: values['--out'] ?? 'certification-report.json',
    maxAgeMs: maxAgeHours * 60 * 60 * 1000,
  };
}

function readInput(label, file, maxAgeMs) {
  // Open once and take metadata and bytes from the same descriptor, so the
  // file checked is the file read. O_NONBLOCK keeps a FIFO from hanging.
  let fd;
  try {
    fd = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NONBLOCK ?? 0));
  } catch (error) {
    return { label, code: 'MISSING_OR_UNREADABLE', detail: error.message };
  }
  let raw;
  try {
    const stat = fs.fstatSync(fd);
    if (!stat.isFile()) {
      return { label, code: 'MISSING_OR_UNREADABLE', detail: 'not a regular file' };
    }
    if (Date.now() - stat.mtimeMs > maxAgeMs) {
      return { label, code: 'STALE', detail: `mtime ${new Date(stat.mtimeMs).toISOString()}` };
    }
    raw = fs.readFileSync(fd, 'utf8');
  } catch (error) {
    return { label, code: 'MISSING_OR_UNREADABLE', detail: error.message };
  } finally {
    fs.closeSync(fd);
  }
  try {
    return { label, value: JSON.parse(raw) };
  } catch (error) {
    return { label, code: 'MALFORMED', detail: error.message };
  }
}

function unavailableReport(failures) {
  return {
    schema_version: 'certification-report/v1',
    verdict: 'NOT-CERTIFIED',
    certified: 0,
    pending: 0,
    reason_codes: ['E-EVIDENCE-UNAVAILABLE'],
    input_failures: failures,
    artifacts: [],
  };
}

function arrayAt(payload, label, key) {
  if (
    !payload ||
    typeof payload !== 'object' ||
    Array.isArray(payload) ||
    !Array.isArray(payload[key])
  ) {
    fail(`${label} input must be an object with a ${JSON.stringify(key)} array`);
  }
  return payload[key];
}

function artifactPath(row) {
  const value = row?.artifact_path ?? row?.path;
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function indexByPath(rows, label) {
  const indexed = new Map();
  for (const row of rows) {
    const key = artifactPath(row);
    if (!key) fail(`${label} row is missing path or artifact_path`);
    if (indexed.has(key)) fail(`${label} contains duplicate artifact path: ${key}`);
    indexed.set(key, row);
  }
  return indexed;
}

function scannerFindings(rows) {
  const indexed = new Map();
  for (const row of rows) {
    const key = artifactPath(row);
    if (!key) fail('scanner finding is missing path or artifact_path');
    const kind = String(row.class ?? row.severity ?? row.status ?? '').toUpperCase();
    if (!indexed.has(key)) indexed.set(key, []);
    indexed.get(key).push(kind);
  }
  return indexed;
}

function evidenceClass(ledger) {
  const value = ledger?.evidence_class;
  return Object.hasOwn(EVIDENCE_RANK, value) ? value : 'E0';
}

function evaluateArtifact({ path: artifact, validator, disposition, ledger, scanner }) {
  const reasons = [];
  if (!validator || !Number.isInteger(validator.errors) || validator.errors < 0) {
    reasons.push('E-VALIDATOR-FACT-UNAVAILABLE');
  } else if (validator.errors > 0) {
    reasons.push('G1-VALIDATOR-ERRORS');
  }

  for (const gate of GATES.slice(1)) {
    if (validator?.gates?.[gate] !== true) reasons.push(`${gate}-UNSATISFIED`);
  }

  for (const finding of scanner ?? []) {
    if (finding === 'REFUSE') reasons.push('G2-REFUSE');
    else if (finding === 'CHALLENGE') reasons.push('G2-CHALLENGE');
    else if (finding === 'SECURITY' || finding === 'SECURITY-CLASS') reasons.push('G2-SECURITY');
  }

  if (!disposition) reasons.push('D-DISPOSITION-MISSING');
  else if (disposition.disposition !== 'CERTIFY') reasons.push('D-DISPOSITION-NOT-CERTIFY');

  const klass = evidenceClass(ledger);
  if (!ledger) {
    reasons.push('E-EVIDENCE-MISSING');
  } else {
    if (EVIDENCE_RANK[klass] < EVIDENCE_RANK.E1) reasons.push('E1-DETERMINISTIC-MISSING');
    if (EVIDENCE_RANK[klass] < EVIDENCE_RANK.E2) reasons.push('E2-BEHAVIORAL-MISSING');
    if (!ledger.artifact_uri || !ledger.artifact_sha256) reasons.push('E3-ARTIFACT-UNRETAINED');
    if (EVIDENCE_RANK[klass] < EVIDENCE_RANK.E3 || ledger.baseline_delta == null) {
      reasons.push('E4-BASELINE-DELTA-MISSING');
    }
    if (
      !ledger.recorded_by_identity ||
      !ledger.producing_identity ||
      ledger.recorded_by_identity === ledger.producing_identity
    ) {
      reasons.push('E5-INDEPENDENT-RECORDER-MISSING');
    }
    if (!ledger.provenance_hash) reasons.push('E6-PROVENANCE-HASH-MISSING');
  }

  const uniqueReasons = [...new Set(reasons)].sort();
  return {
    path: artifact,
    verdict: uniqueReasons.length === 0 ? 'CERTIFIED' : 'NOT-CERTIFIED',
    evidence_class: klass,
    reason_codes: uniqueReasons,
  };
}

export function evaluate({ validator, scanner, ledger, dispositions }) {
  const validatorRows = arrayAt(validator, 'validator', 'artifacts');
  const scannerRows = arrayAt(scanner, 'scanner', 'findings');
  const ledgerRows = arrayAt(ledger, 'ledger', 'records');
  const dispositionRows = arrayAt(dispositions, 'dispositions', 'artifacts');
  const validatorByPath = indexByPath(validatorRows, 'validator');
  const ledgerByPath = indexByPath(ledgerRows, 'ledger');
  const dispositionByPath = indexByPath(dispositionRows, 'dispositions');
  const findingsByPath = scannerFindings(scannerRows);

  const artifacts = [...validatorByPath.keys()].sort().map((artifact) =>
    evaluateArtifact({
      path: artifact,
      validator: validatorByPath.get(artifact),
      disposition: dispositionByPath.get(artifact),
      ledger: ledgerByPath.get(artifact),
      scanner: findingsByPath.get(artifact),
    }),
  );
  const certified = artifacts.filter((artifact) => artifact.verdict === 'CERTIFIED').length;
  return {
    schema_version: 'certification-report/v1',
    certified,
    pending: artifacts.length - certified,
    artifacts,
  };
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  const inputs = [
    readInput('validator', args.validator, args.maxAgeMs),
    readInput('scanner', args.scanner, args.maxAgeMs),
    readInput('ledger', args.ledger, args.maxAgeMs),
    readInput('dispositions', args.dispositions, args.maxAgeMs),
  ];
  const failures = inputs
    .filter((input) => input.code)
    .map(({ label, code, detail }) => ({ label, code, detail }));
  const report = failures.length
    ? unavailableReport(failures)
    : evaluate({
        validator: inputs[0].value,
        scanner: inputs[1].value,
        ledger: inputs[2].value,
        dispositions: inputs[3].value,
      });
  fs.writeFileSync(args.out, `${JSON.stringify(report, null, 2)}\n`);
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    main();
  } catch (error) {
    console.error(`[evaluate-certification] ERROR: ${error.message}`);
    process.exit(1);
  }
}
