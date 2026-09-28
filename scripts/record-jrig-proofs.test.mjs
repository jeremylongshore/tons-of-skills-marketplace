/**
 * record-jrig-proofs.test.mjs — unit tests for the eval→forge_proofs write
 * path (issue #935).
 *
 * Covers:
 *   (a) fresh insert — a well-formed `j-rig eval --json` result lands as one
 *       tier3-jrig row with the contracted column bindings;
 *   (b) idempotent re-run — same (plugin, jrig_run_id) upserts in place, never
 *       duplicates; changed scorecards update the existing row;
 *   (c) malformed result JSON — rejected loudly with a non-zero exit;
 *   (d) runner freshie-path guard — scripts/run-jrig-eval.sh refuses any
 *       j-rig scratch DB path containing 'freshie' (and non-/dev/shm paths);
 *   (e) stub guard — ground_truth:false results are refused without
 *       --allow-stub.
 *
 * Run: node --test scripts/record-jrig-proofs.test.mjs
 * Needs the `sqlite3` CLI on PATH.
 */

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { enforceRecorderIdentity } from './record-jrig-proofs.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RECORD_SCRIPT = path.join(__dirname, 'record-jrig-proofs.mjs');
const RUNNER_SCRIPT = path.join(__dirname, 'run-jrig-eval.sh');

function tmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'record-jrig-test-'));
}

/** Minimal fixture matching the `j-rig eval --json` model-keyed map shape. */
function fixtureResult({
  passed = 7,
  total = 7,
  decision = 'ship',
  groundTruth = true,
  model = 'deepseek-v4-flash',
} = {}) {
  return {
    [model]: {
      provider: groundTruth ? 'deepseek' : 'stub',
      model,
      ground_truth: groundTruth,
      pkgReport: { summary: { passed: 5, errors: 0 } },
      scoreCard: {
        total_criteria: total,
        passed,
        failed: total - passed,
        unsure: 0,
        blocker_failures: 0,
        sacred_regressions: 0,
        pass_rate: total > 0 ? passed / total : 0,
      },
      decision,
      report: {
        skill_name: 'fixture-skill',
        timestamp: '2026-07-09T00:00:00.000Z',
        decision,
        blockers: [],
        warnings: [],
        reasoning: `${passed}/${total} criteria passed.`,
      },
    },
  };
}

function writeFixture(dir, name, value) {
  const file = path.join(dir, name);
  fs.writeFileSync(file, typeof value === 'string' ? value : JSON.stringify(value, null, 2));
  return file;
}

function freshDb(dir) {
  // A zero-length file is a valid empty SQLite database; the script's
  // CREATE TABLE IF NOT EXISTS provisions forge_proofs.
  const db = path.join(dir, 'inventory-copy.sqlite');
  fs.writeFileSync(db, '');
  return db;
}

// The recorder labels a run "github-actions:<actor>" whenever GITHUB_ACTOR is
// set, which CI always does. Tests that assert the local-run identity must
// not inherit that, or they pass on a laptop and fail in CI.
function localEnv(extra = {}) {
  const env = { ...process.env, ...extra };
  delete env.GITHUB_ACTOR;
  return env;
}

function record(args) {
  return execFileSync(process.execPath, [RECORD_SCRIPT, ...args], {
    encoding: 'utf8',
    env: localEnv(),
  });
}

function recordExpectFail(args) {
  const result = spawnSync(process.execPath, [RECORD_SCRIPT, ...args], {
    encoding: 'utf8',
    env: localEnv(),
  });
  assert.notEqual(
    result.status,
    0,
    `expected non-zero exit, got ${result.status}\nstdout: ${result.stdout}`,
  );
  return result.stderr;
}

function queryRows(db, sql) {
  const out = execFileSync('sqlite3', ['-batch', '-json', db, sql], { encoding: 'utf8' }).trim();
  return out ? JSON.parse(out) : [];
}

test('(identity) E2/E3 self-approval and local writes to the real ledger are refused', () => {
  assert.throws(
    () =>
      enforceRecorderIdentity({
        evidenceClass: 'E2',
        recordedByIdentity: 'ci',
        producingIdentity: 'ci',
        dbPath: '/tmp/scratch.sqlite',
      }),
    /must be independent/,
  );
  assert.throws(
    () =>
      enforceRecorderIdentity({
        evidenceClass: 'E3',
        recordedByIdentity: 'local-untrusted',
        producingIdentity: 'lab',
        dbPath: '/repo/freshie/inventory.sqlite',
        realInventoryPath: '/repo/freshie/inventory.sqlite',
      }),
    /local recorder identity/,
  );
  assert.doesNotThrow(() =>
    enforceRecorderIdentity({
      evidenceClass: 'E2',
      recordedByIdentity: 'github-actions:reviewer',
      producingIdentity: 'lab',
      dbPath: '/repo/freshie/inventory.sqlite',
      realInventoryPath: '/repo/freshie/inventory.sqlite',
    }),
  );
});

test('(a) fresh insert lands one tier3-jrig row with the contracted bindings', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const result = writeFixture(
    dir,
    'result.json',
    fixtureResult({ passed: 6, total: 7, decision: 'warn' }),
  );

  const stdout = record([
    '--db',
    db,
    '--plugin',
    'coreweave-pack',
    '--jrig-run-id',
    '42',
    '--result',
    result,
  ]);
  assert.match(stdout, /Upserted tier3-jrig row for 'coreweave-pack' \(jrig_run_id=42\)/);

  const rows = queryRows(db, 'SELECT * FROM forge_proofs;');
  assert.equal(rows.length, 1);
  const row = rows[0];
  assert.equal(row.plugin_name, 'coreweave-pack');
  assert.equal(row.jrig_run_id, 42);
  assert.equal(row.verification_type, 'tier3-jrig');
  assert.equal(row.passed, 0); // decision 'warn' !== 'ship'
  assert.equal(row.layers_passed, 6); // scoreCard.passed
  assert.equal(row.total_layers, 7); // scoreCard.total_criteria
  assert.equal(row.baseline_delta, null);
  assert.equal(row.evidence_class, 'E0');
  assert.equal(row.artifact_uri, path.resolve(result));
  assert.equal(
    row.artifact_sha256,
    createHash('sha256').update(fs.readFileSync(result)).digest('hex'),
  );
  assert.equal(row.provider, 'deepseek');
  assert.equal(row.model, 'deepseek-v4-flash');
  assert.equal(row.recorded_by_identity, 'local-untrusted');
  assert.ok(row.verified_at);

  const evidence = JSON.parse(row.evidence);
  assert.equal(evidence.source, 'j-rig eval --json');
  assert.equal(evidence.stub, false);
  assert.equal(evidence.artifact_uri, path.resolve(result));
  assert.equal(
    evidence.artifact_sha256,
    createHash('sha256').update(fs.readFileSync(result)).digest('hex'),
    'the ledger hashes the exact retained result bytes',
  );
  assert.equal(evidence.models.length, 1);
  assert.equal(evidence.models[0].model, 'deepseek-v4-flash');
  assert.equal(evidence.models[0].scoreCard.passed, 6);
});

test('(a1) a supplied discovery run is FK-checked and stored separately from j-rig run id', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const result = writeFixture(dir, 'result.json', fixtureResult({ decision: 'ship' }));
  // Bootstrap the recorder schema, then seed the parent row in its real table.
  record(['--db', db, '--plugin', 'bootstrap', '--jrig-run-id', '1', '--result', result]);
  execFileSync('sqlite3', [db, 'INSERT INTO discovery_runs (id) VALUES (99);']);

  record([
    '--db',
    db,
    '--plugin',
    'linked-pack',
    '--jrig-run-id',
    '7',
    '--discovery-run-id',
    '99',
    '--result',
    result,
  ]);
  const [linked] = queryRows(
    db,
    "SELECT jrig_run_id, discovery_run_id FROM forge_proofs WHERE plugin_name='linked-pack';",
  );
  assert.deepEqual(linked, { jrig_run_id: 7, discovery_run_id: 99 });

  const stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'invalid-link',
    '--jrig-run-id',
    '8',
    '--discovery-run-id',
    '100',
    '--result',
    result,
  ]);
  assert.match(stderr, /FOREIGN KEY constraint failed/);
});

test('(a2) all-ship multi-model result records passed=1 with the weakest layer count', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const multi = {
    ...fixtureResult({ passed: 7, total: 7, model: 'deepseek-v4-flash' }),
    ...fixtureResult({ passed: 5, total: 7, model: 'other-model' }),
  };
  const result = writeFixture(dir, 'result.json', multi);

  record(['--db', db, '--plugin', 'multi-pack', '--jrig-run-id', '1', '--result', result]);

  const [row] = queryRows(db, "SELECT * FROM forge_proofs WHERE plugin_name='multi-pack';");
  assert.equal(row.passed, 1); // both decisions are 'ship'
  assert.equal(row.layers_passed, 5); // min across models
  assert.equal(row.total_layers, 7);
  assert.equal(JSON.parse(row.evidence).models.length, 2);
});

test('(a3) the three unretained legacy proofs migrate to E0 with separate run namespaces', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  execFileSync('sqlite3', [
    db,
    "CREATE TABLE forge_proofs (id INTEGER PRIMARY KEY, plugin_name TEXT NOT NULL, run_id INTEGER, verification_type TEXT NOT NULL, passed INTEGER NOT NULL, evidence TEXT, layers_passed INTEGER, total_layers INTEGER, baseline_delta REAL, verified_at TEXT, UNIQUE(plugin_name, verification_type, run_id)); INSERT INTO forge_proofs (plugin_name, run_id, verification_type, passed, evidence) VALUES ('databricks-pack', 2, 'tier3-jrig', 1, '{\"retention\":\"not retained\"}'), ('databricks-pack', 4, 'tier3-jrig', 1, '{\"retention\":\"not retained\"}'), ('databricks-pack', 5, 'tier3-jrig', 1, '{\"retention\":\"not retained\"}');",
  ]);
  const result = writeFixture(dir, 'result.json', fixtureResult());

  record(['--db', db, '--plugin', 'legacy-pack', '--jrig-run-id', '77', '--result', result]);
  const columns = queryRows(db, 'PRAGMA table_info(forge_proofs);').map((row) => row.name);
  assert.ok(columns.includes('jrig_run_id'));
  assert.ok(!columns.includes('run_id'));
  const legacy = queryRows(
    db,
    "SELECT jrig_run_id, evidence_class, artifact_uri, artifact_sha256 FROM forge_proofs WHERE plugin_name='databricks-pack' ORDER BY jrig_run_id;",
  );
  assert.deepEqual(legacy, [
    { jrig_run_id: 2, evidence_class: 'E0', artifact_uri: null, artifact_sha256: null },
    { jrig_run_id: 4, evidence_class: 'E0', artifact_uri: null, artifact_sha256: null },
    { jrig_run_id: 5, evidence_class: 'E0', artifact_uri: null, artifact_sha256: null },
  ]);
  const [row] = queryRows(
    db,
    "SELECT jrig_run_id FROM forge_proofs WHERE plugin_name='legacy-pack';",
  );
  assert.equal(row.jrig_run_id, 77);
});

test('(b) idempotent re-run: same jrig_run_id upserts in place, never duplicates', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const first = writeFixture(
    dir,
    'r1.json',
    fixtureResult({ passed: 7, total: 7, decision: 'ship' }),
  );
  const second = writeFixture(
    dir,
    'r2.json',
    fixtureResult({ passed: 4, total: 7, decision: 'block' }),
  );

  record(['--db', db, '--plugin', 'plane', '--jrig-run-id', '100', '--result', first]);
  record(['--db', db, '--plugin', 'plane', '--jrig-run-id', '100', '--result', first]); // identical re-run
  let rows = queryRows(db, "SELECT * FROM forge_proofs WHERE plugin_name='plane';");
  assert.equal(rows.length, 1);
  assert.equal(rows[0].passed, 1);
  assert.equal(rows[0].layers_passed, 7);

  record(['--db', db, '--plugin', 'plane', '--jrig-run-id', '100', '--result', second]); // changed verdict, same key
  rows = queryRows(db, "SELECT * FROM forge_proofs WHERE plugin_name='plane';");
  assert.equal(rows.length, 1, 'still exactly one row for the key');
  assert.equal(rows[0].passed, 0);
  assert.equal(rows[0].layers_passed, 4);

  record(['--db', db, '--plugin', 'plane', '--jrig-run-id', '101', '--result', first]); // new jrig run = new row
  rows = queryRows(
    db,
    "SELECT * FROM forge_proofs WHERE plugin_name='plane' ORDER BY jrig_run_id;",
  );
  assert.equal(rows.length, 2);
});

test('(c) malformed result JSON is rejected loudly with a non-zero exit', () => {
  const dir = tmpDir();
  const db = freshDb(dir);

  // Not JSON at all.
  const garbage = writeFixture(dir, 'garbage.json', 'this is not json {');
  let stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'p',
    '--jrig-run-id',
    '1',
    '--result',
    garbage,
  ]);
  assert.match(stderr, /not valid JSON/);

  // Valid JSON, wrong shape (no scoreCard anywhere).
  const wrongShape = writeFixture(dir, 'wrong.json', { hello: 'world' });
  stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'p',
    '--jrig-run-id',
    '1',
    '--result',
    wrongShape,
  ]);
  assert.match(stderr, /No model entries with a scoreCard/);

  // scoreCard present but non-integer fields.
  const badCard = fixtureResult();
  badCard['deepseek-v4-flash'].scoreCard.passed = 'seven';
  const badCardFile = writeFixture(dir, 'badcard.json', badCard);
  stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'p',
    '--jrig-run-id',
    '1',
    '--result',
    badCardFile,
  ]);
  assert.match(stderr, /Malformed scoreCard/);

  // Invalid decision.
  const badDecision = fixtureResult();
  badDecision['deepseek-v4-flash'].decision = 'maybe';
  const badDecisionFile = writeFixture(dir, 'baddecision.json', badDecision);
  stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'p',
    '--jrig-run-id',
    '1',
    '--result',
    badDecisionFile,
  ]);
  assert.match(stderr, /decision must be one of/);

  // Non-integer jrig run id (would break the UNIQUE upsert key).
  const ok = writeFixture(dir, 'ok.json', fixtureResult());
  stderr = recordExpectFail(['--db', db, '--plugin', 'p', '--jrig-run-id', 'abc', '--result', ok]);
  assert.match(stderr, /--jrig-run-id must be a non-negative integer/);

  // Nothing was written by any failing invocation.
  const rows = queryRows(
    db,
    "SELECT COUNT(*) AS n FROM sqlite_master WHERE type='table' AND name='forge_proofs';",
  );
  assert.equal(rows[0].n, 0, 'failing runs must not touch the DB');
});

test('(e) stub results (ground_truth:false) are refused without --allow-stub', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const stub = writeFixture(dir, 'stub.json', fixtureResult({ groundTruth: false }));

  const stderr = recordExpectFail([
    '--db',
    db,
    '--plugin',
    'p',
    '--jrig-run-id',
    '7',
    '--result',
    stub,
  ]);
  assert.match(stderr, /Refusing to record non-ground-truth evidence/);

  // Opting in records the row and marks the evidence as stub.
  record(['--db', db, '--plugin', 'p', '--jrig-run-id', '7', '--result', stub, '--allow-stub']);
  const [row] = queryRows(db, "SELECT * FROM forge_proofs WHERE plugin_name='p';");
  assert.equal(JSON.parse(row.evidence).stub, true);
});

test('(f) result artifacts under /dev/shm are refused because they are not retained evidence', () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const result = path.join('/dev/shm', `jrig-unretained-${process.pid}-${Date.now()}.json`);
  fs.writeFileSync(result, JSON.stringify(fixtureResult()));
  try {
    const stderr = recordExpectFail([
      '--db',
      db,
      '--plugin',
      'p',
      '--jrig-run-id',
      '8',
      '--result',
      result,
    ]);
    assert.match(stderr, /must be retained outside \/dev\/shm/);
  } finally {
    fs.rmSync(result, { force: true });
  }
});

test('(g) runner atomically retains primary JSON outside /dev/shm and records its hash', () => {
  const dir = tmpDir();
  const skillDir = path.join(dir, 'skill');
  const artifactDir = path.join(dir, 'retained-artifacts');
  const db = path.join('/dev/shm', `jrig-inventory-${process.pid}-${Date.now()}.sqlite`);
  const fakeJrig = path.join(dir, 'fake-jrig.sh');
  fs.mkdirSync(skillDir);
  fs.writeFileSync(db, '');
  fs.writeFileSync(
    fakeJrig,
    `#!/usr/bin/env bash\nprintf '%s\\n' '${JSON.stringify(fixtureResult({ groundTruth: false }))}'\n`,
    { mode: 0o755 },
  );

  try {
    const result = spawnSync(
      'bash',
      [
        RUNNER_SCRIPT,
        '--skill-dir',
        skillDir,
        '--plugin',
        'retained-pack',
        '--inventory-db',
        db,
        '--jrig-run-id',
        '55',
        '--artifact-dir',
        artifactDir,
        '--stub',
      ],
      { encoding: 'utf8', env: { ...process.env, JRIG_BIN: fakeJrig } },
    );
    assert.equal(result.status, 0, result.stderr);

    const artifact = path.join(artifactDir, 'retained-pack.jrig-run-55.json');
    // Stat and hash through one descriptor so the file checked is the file hashed.
    const artifactFd = fs.openSync(artifact, 'r');
    let artifactMode;
    let artifactBytes;
    try {
      artifactMode = fs.fstatSync(artifactFd).mode;
      artifactBytes = fs.readFileSync(artifactFd);
    } finally {
      fs.closeSync(artifactFd);
    }
    assert.equal(artifactMode & 0o777, 0o600, 'primary JSON is retained with owner-only mode');
    const [row] = queryRows(
      db,
      "SELECT evidence FROM forge_proofs WHERE plugin_name='retained-pack';",
    );
    const evidence = JSON.parse(row.evidence);
    assert.equal(evidence.artifact_uri, artifact);
    assert.equal(
      evidence.artifact_sha256,
      createHash('sha256').update(artifactBytes).digest('hex'),
    );
  } finally {
    fs.rmSync(db, { force: true });
  }
});

test("(d) runner guard refuses j-rig scratch DB paths containing 'freshie'", () => {
  const dir = tmpDir();
  const db = freshDb(dir);
  const skillDir = path.join(dir, 'skill');
  fs.mkdirSync(skillDir);

  // Guard fires before any sops/pnpm/j-rig work, so this is spend-free.
  const result = spawnSync(
    'bash',
    [
      RUNNER_SCRIPT,
      '--skill-dir',
      skillDir,
      '--plugin',
      'p',
      '--inventory-db',
      db,
      '--scratch-db',
      '/dev/shm/freshie-scratch.db',
      '--stub',
    ],
    { encoding: 'utf8' },
  );
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /refusing scratch DB path containing 'freshie'/);

  // Scratch DBs outside /dev/shm are refused too.
  const outside = spawnSync(
    'bash',
    [
      RUNNER_SCRIPT,
      '--skill-dir',
      skillDir,
      '--plugin',
      'p',
      '--inventory-db',
      db,
      '--scratch-db',
      path.join(dir, 'scratch.db'),
      '--stub',
    ],
    { encoding: 'utf8' },
  );
  assert.notEqual(outside.status, 0);
  assert.match(outside.stderr, /scratch DB must live under \/dev\/shm/);

  // Static belt-and-suspenders: the guard text exists in the runner source.
  const source = fs.readFileSync(RUNNER_SCRIPT, 'utf8');
  assert.match(source, /\*freshie\*\)/, 'freshie case-glob guard present in run-jrig-eval.sh');
  assert.match(source, /artifact directory must be durable and outside \/dev\/shm/);
  assert.match(source, /install -m 600 "\$result_json" "\$artifact_tmp"/);
  assert.match(source, /--result "\$artifact_json"/);
});
