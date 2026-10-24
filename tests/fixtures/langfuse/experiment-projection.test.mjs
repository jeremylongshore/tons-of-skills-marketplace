// Synthetic fixtures matching @langfuse/client 6.0.2 result types; no SDK/provider execution.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, URL } from 'node:url';
import process from 'node:process';
import test from 'node:test';
import {
  captureTask,
  caseContentDigest,
  manifestCase,
  projectResult,
  ProjectionError,
} from '../../../plugins/saas-packs/langfuse-pack/skills/langfuse-experiment-guardian/scripts/project-result.mjs';

const comparePath = fileURLToPath(
  new URL(
    '../../../plugins/saas-packs/langfuse-pack/skills/langfuse-experiment-guardian/scripts/compare.py',
    import.meta.url,
  ),
);

function item(id = 'case-one') {
  return {
    input: { question: 'private prompt' },
    expectedOutput: { answer: 'private expected answer' },
    metadata: { guardian_case_id: id, locale: 'private locale' },
  };
}

function result(items, id = 'candidate-experiment') {
  return {
    experimentId: id,
    runName: 'a mutable display name',
    experimentUrl: 'https://private.invalid/experiment',
    itemResults: items.map((original) => ({
      item: original,
      input: original.input,
      expectedOutput: original.expectedOutput,
      output: 'private generated answer',
      evaluations: [{ name: 'correctness', value: 1, comment: 'private evaluation comment' }],
    })),
    runEvaluations: [{ name: 'correctness', value: 1 }],
    format: async () => 'private formatted output',
  };
}

function context() {
  return {
    project_id: 'project-fixture',
    dataset_id: 'local-fixture-dataset',
    dataset_version: 'reviewed-fixture-v1',
    application_ref: 'fixture-commit',
    evaluator_versions: { correctness: 'evaluator-v1' },
    export_complete: true,
    sdk_version: '6.0.2',
  };
}

async function evidence(items) {
  const recorder = captureTask(async () => 'synthetic success');
  for (const original of items) await recorder.task(original);
  return recorder.snapshot();
}

test('projection preserves experiment ID and excludes content, comments, URLs and aggregate scores', async () => {
  const items = [item()];
  const projected = projectResult(result(items), context(), await evidence(items));
  assert.equal(projected.run_id, 'candidate-experiment');
  assert.equal(projected.cases[0].task_state, 'ok');
  assert.equal(projected.cases[0].content_sha256, manifestCase(items[0], true).content_sha256);
  assert.deepEqual(projected.cases[0].evaluations, [{ name: 'correctness', value: 1 }]);
  assert.equal(JSON.stringify(projected).includes('private'), false);
});

test('content fingerprint is stable across object-key ordering and sensitive to metadata/array changes', () => {
  const before = {
    input: { b: 2, a: ['one', 'two'] },
    expectedOutput: null,
    metadata: { locale: 'en' },
  };
  const same = {
    metadata: { locale: 'en' },
    expectedOutput: null,
    input: { a: ['one', 'two'], b: 2 },
  };
  assert.equal(caseContentDigest(before), caseContentDigest(same));
  same.metadata.locale = 'fr';
  assert.notEqual(caseContentDigest(before), caseContentDigest(same));
  same.metadata.locale = 'en';
  same.input.a.reverse();
  assert.notEqual(caseContentDigest(before), caseContentDigest(same));
  assert.notEqual(caseContentDigest({}), caseContentDigest({ input: null }));
});

test('hosted and explicit local case identifiers work; conflicting identifiers are rejected', () => {
  const hosted = { id: 'hosted-case', input: 'synthetic' };
  assert.equal(manifestCase(hosted, true).case_id, 'hosted-case');
  assert.equal(manifestCase(item(), false).case_id, 'case-one');
  assert.throws(
    () => manifestCase({ ...item(), id: 'different-hosted-id' }, true),
    ProjectionError,
  );
  assert.throws(() => manifestCase({ input: 'synthetic' }, true), ProjectionError);
});

test('creating a recorder or projecting an existing result never executes a task', () => {
  let calls = 0;
  const recorder = captureTask(async () => calls++);
  const projected = projectResult(result([item()]), context(), recorder.snapshot());
  assert.equal(calls, 0);
  assert.equal(projected.cases[0].task_state, 'unknown');
});

test('recorder propagates the exact business error and never retries or retains its message', async () => {
  let calls = 0;
  const error = new Error('private failure message');
  const recorder = captureTask(async () => {
    calls++;
    throw error;
  });
  await assert.rejects(recorder.task(item()), (observed) => observed === error);
  assert.equal(calls, 1);
  assert.equal(recorder.snapshot()[0].state, 'error');
  assert.equal(JSON.stringify(recorder.snapshot()).includes('private'), false);
});

test('an unfinished execution or repeated caller invocation cannot become a single successful case', async () => {
  let finish;
  const recorder = captureTask(() => new Promise((resolve) => (finish = resolve)));
  const pending = recorder.task(item());
  assert.equal(recorder.snapshot()[0].state, 'unknown');
  finish('synthetic');
  await pending;
  assert.equal(recorder.snapshot()[0].state, 'ok');
  const repeated = recorder.task(item());
  finish('synthetic');
  await repeated;
  assert.equal(recorder.snapshot()[0].attempts, 2);
  assert.equal(recorder.snapshot()[0].state, 'unknown');
});

test('mutation after task entry invalidates execution evidence for the projected case content', async () => {
  const original = item();
  const recorder = captureTask(async (data) => {
    data.input.question = 'different private question';
  });
  await recorder.task(original);
  const projected = projectResult(result([original]), context(), recorder.snapshot());
  assert.equal(projected.cases[0].task_state, 'unknown');
});

test('missing evaluator results remain missing even when run-level aggregate is a pass', async () => {
  const items = [item()];
  const raw = result(items);
  raw.itemResults[0].evaluations = [];
  const projected = projectResult(raw, context(), await evidence(items));
  assert.deepEqual(projected.cases[0].evaluations, []);
});

test('unavailable scores remain null while booleans and unsafe numeric scores are rejected', () => {
  const raw = result([item()]);
  delete raw.itemResults[0].evaluations[0].value;
  assert.equal(projectResult(raw, context()).cases[0].evaluations[0].value, null);
  for (const value of [true, Infinity, NaN, Number.MAX_SAFE_INTEGER + 1]) {
    raw.itemResults[0].evaluations[0].value = value;
    assert.throws(() => projectResult(raw, context()), ProjectionError);
  }
});

test('conflicting content/run identities and duplicate result/evidence records are rejected', async () => {
  const items = [item()];
  const states = await evidence(items);
  let raw = result(items);
  raw.datasetRunId = 'different-experiment';
  assert.throws(() => projectResult(raw, context(), states), ProjectionError);
  raw = result(items);
  raw.itemResults[0].datasetRunId = 'another-experiment';
  assert.throws(() => projectResult(raw, context(), states), ProjectionError);
  raw = result(items);
  raw.itemResults[0].input = 'different input';
  assert.throws(() => projectResult(raw, context(), states), ProjectionError);
  raw = result(items);
  raw.itemResults.push(raw.itemResults[0]);
  assert.throws(() => projectResult(raw, context(), states), ProjectionError);
  assert.throws(
    () => projectResult(result(items), context(), [...states, ...states]),
    ProjectionError,
  );
});

test('non-JSON content, cycles, unsafe integers, accessors and excessive content are held', () => {
  let invoked = false;
  const getter = {};
  Object.defineProperty(getter, 'input', {
    enumerable: true,
    get() {
      invoked = true;
      return 'private';
    },
  });
  assert.throws(() => caseContentDigest(getter), ProjectionError);
  assert.equal(invoked, false);
  const cycle = {};
  cycle.self = cycle;
  for (const input of [
    cycle,
    new Date(),
    Number.MAX_SAFE_INTEGER + 1,
    Infinity,
    { toJSON: () => 'private' },
  ]) {
    assert.throws(() => caseContentDigest({ input }), ProjectionError);
  }
  assert.throws(
    () => caseContentDigest({ input: 'x'.repeat(2 * 1024 * 1024 + 1) }),
    ProjectionError,
  );
  assert.throws(
    () => caseContentDigest({ input: Object.assign(new Array(2), { 1: 'sparse' }) }),
    ProjectionError,
  );
});

test('projected receipts feed the actual Python gate; missing execution evidence and reused runs hold', async () => {
  const items = [item('case-one'), item('case-two')];
  const states = await evidence(items);
  const baseline = projectResult(result(items, 'baseline-experiment'), context(), states);
  const candidate = projectResult(result(items, 'candidate-experiment'), context(), states);
  const policy = {
    project_id: context().project_id,
    dataset_id: context().dataset_id,
    dataset_version: context().dataset_version,
    baseline_run_id: 'baseline-experiment',
    baseline_review_ref: 'fixture-reviewed-baseline',
    mode: 'all-required',
    expected_cases: items.map((original) => manifestCase(original, true)),
    evaluators: [
      {
        name: 'correctness',
        version: 'evaluator-v1',
        minimum: 0,
        maximum: 1,
        threshold: '0.8',
        direction: 'higher',
      },
    ],
  };
  const payload = { schema_version: 1, policy, baseline, candidate };
  function compare(expectedExit, expectedDecision) {
    const observed = spawnSync(
      process.env.LANGFUSE_GUARDIAN_TEST_PYTHON ?? 'python3',
      [comparePath],
      {
        input: JSON.stringify(payload),
        encoding: 'utf8',
        timeout: 10000,
      },
    );
    assert.equal(observed.status, expectedExit, observed.stderr);
    assert.equal(JSON.parse(observed.stdout).decision, expectedDecision);
    assert.equal(observed.stdout.includes('private'), false);
  }
  compare(0, 'pass');
  payload.candidate = projectResult(result(items), context());
  compare(1, 'inconclusive');
  payload.candidate = projectResult(result(items, 'baseline-experiment'), context(), states);
  compare(1, 'inconclusive');
});
