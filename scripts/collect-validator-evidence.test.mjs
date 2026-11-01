import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  collectValidatorEvidence,
  VALIDATOR_PASSES,
  runValidator,
} from './collect-validator-evidence.mjs';

test('all canonical passes run with bounded overlap, deterministic ordering and original statuses', async () => {
  let active = 0,
    peak = 0;
  const seen = [];
  const result = await collectValidatorEvidence({
    run: async (args) => {
      active++;
      peak = Math.max(peak, active);
      seen.push(args);
      await new Promise((resolve) => setTimeout(resolve, 10));
      active--;
      return { status: 1, stdout: JSON.stringify(args), stderr: '' };
    },
  });
  assert.equal(peak, 2);
  assert.deepEqual(
    seen,
    VALIDATOR_PASSES.map(([, args]) => args),
  );
  assert.deepEqual(
    Object.keys(result),
    VALIDATOR_PASSES.map(([name]) => name),
  );
  assert.ok(Object.values(result).every((row) => row.status === 1));
});
test('operational failures and invalid output cannot become evidence', async () => {
  await assert.rejects(
    collectValidatorEvidence({ run: async () => ({ status: 2, stdout: '', stderr: '' }) }),
  );
  await assert.rejects(
    collectValidatorEvidence({
      run: async () => {
        throw Error('fixture failure');
      },
    }),
    /fixture failure/,
  );
  await assert.rejects(collectValidatorEvidence({ concurrency: 3 }));
  await assert.rejects(
    runValidator(['-c', 'import time; time.sleep(10)'], { timeoutMs: 30 }),
    /timed out/,
  );
  await assert.rejects(runValidator(['-c', 'print("x"*10000)'], { maxBytes: 100 }), /output limit/);
});
