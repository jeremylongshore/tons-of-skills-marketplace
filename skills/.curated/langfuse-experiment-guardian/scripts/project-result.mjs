/** Project existing @langfuse/client v6 experiment results without exporting content. */
import { createHash } from 'node:crypto';
import { Buffer } from 'node:buffer';

const MAX_BYTES = 2 * 1024 * 1024;

export class ProjectionError extends Error {}

function require(condition, code) {
  if (!condition) throw new ProjectionError(code);
}

function object(value) {
  return (
    value !== null &&
    typeof value === 'object' &&
    Object.getPrototypeOf(value) === Object.prototype &&
    Object.values(Object.getOwnPropertyDescriptors(value)).every((descriptor) =>
      Object.hasOwn(descriptor, 'value'),
    )
  );
}

function identity(value) {
  require(typeof value === 'string' &&
    value.length > 0 &&
    value.length <= 256 &&
    value.trim(), 'invalid-identity');
  return value;
}

/** Stable JSON: UTF-16-sorted keys, JSON.stringify scalars, no toJSON/getters. */
function canonical(value) {
  const parts = [];
  const active = new Set();
  let bytes = 0;
  let nodes = 0;
  function emit(token) {
    bytes += Buffer.byteLength(token);
    require(bytes <= MAX_BYTES, 'case-content-too-large');
    parts.push(token);
  }
  function visit(item, depth) {
    require(depth <= 64 && ++nodes <= 200000, 'case-content-too-complex');
    if (item === null || typeof item === 'boolean') return emit(JSON.stringify(item));
    if (typeof item === 'string') {
      require(item.length <= MAX_BYTES, 'case-content-too-large');
      return emit(JSON.stringify(item));
    }
    if (typeof item === 'number') {
      require(Number.isFinite(item) &&
        (!Number.isInteger(item) || Number.isSafeInteger(item)), 'unsafe-json-number');
      return emit(JSON.stringify(item));
    }
    require(Array.isArray(item) || object(item), 'case-content-must-be-json');
    require(!active.has(item), 'cyclic-case-content');
    active.add(item);
    const keys = Object.keys(item);
    if (Array.isArray(item)) {
      require(keys.length === item.length &&
        keys.every((key, index) => key === String(index)), 'non-json-array');
      emit('[');
    } else {
      keys.sort();
      emit('{');
    }
    for (let index = 0; index < keys.length; index++) {
      const key = keys[index];
      const descriptor = Object.getOwnPropertyDescriptor(item, key);
      require(Object.hasOwn(descriptor, 'value'), 'case-content-accessor');
      if (index) emit(',');
      if (!Array.isArray(item)) emit(JSON.stringify(key) + ':');
      visit(descriptor.value, depth + 1);
    }
    emit(Array.isArray(item) ? ']' : '}');
    active.delete(item);
  }
  visit(value, 0);
  return parts.join('');
}

function caseId(item) {
  require(object(item), 'invalid-experiment-item');
  const hosted = item.id;
  const local = object(item.metadata) ? item.metadata.guardian_case_id : undefined;
  require(hosted === undefined ||
    local === undefined ||
    hosted === local, 'ambiguous-case-identity');
  return identity(hosted ?? local);
}

/** Includes every supplied input/expectedOutput/metadata field, including local case ID. */
export function caseContentDigest(item) {
  require(object(item), 'invalid-experiment-item');
  const content = {};
  for (const key of ['input', 'expectedOutput', 'metadata']) {
    const descriptor = Object.getOwnPropertyDescriptor(item, key);
    if (!descriptor) continue;
    require(Object.hasOwn(descriptor, 'value'), 'case-content-accessor');
    if (descriptor.value !== undefined) content[key] = descriptor.value;
  }
  return createHash('sha256').update(canonical(content)).digest('hex');
}

/** Build the reviewed manifest from the actual dataset, before running an experiment. */
export function manifestCase(item, critical) {
  require(typeof critical === 'boolean', 'missing-critical-classification');
  return { case_id: caseId(item), content_sha256: caseContentDigest(item), critical };
}

/** Optional execution-boundary recorder. Never invokes a task until its caller does. */
export function captureTask(task) {
  require(typeof task === 'function', 'invalid-task');
  const records = new Map();
  return {
    async task(item) {
      const id = caseId(item);
      const hash = caseContentDigest(item);
      let record = records.get(id);
      if (!record) {
        record = {
          case_id: id,
          content_sha256: hash,
          attempts: 0,
          settled: 0,
          errors: 0,
          changed: false,
        };
        records.set(id, record);
      }
      record.attempts++;
      record.changed ||= record.content_sha256 !== hash;
      try {
        // This recorder does not retry business logic after a task or tracing error.
        return await task(item);
      } catch (error) {
        record.errors++;
        throw error;
      } finally {
        record.settled++;
      }
    },
    snapshot() {
      return [...records.values()].map((record) => ({
        case_id: record.case_id,
        content_sha256: record.content_sha256,
        attempts: record.attempts,
        state:
          record.attempts !== 1 || record.settled !== 1 || record.changed
            ? 'unknown'
            : record.errors
              ? 'error'
              : 'ok',
      }));
    },
  };
}

/** Normalize an already-produced ExperimentResult; this function never runs an experiment. */
export function projectResult(result, context, executionEvidence = []) {
  require(object(result) && object(context), 'invalid-result-or-context');
  const runId = identity(result.experimentId);
  require(result.datasetRunId === undefined ||
    result.datasetRunId === runId, 'conflicting-experiment-identities');
  require(Array.isArray(result.itemResults) &&
    result.itemResults.length <= 10000, 'invalid-item-results');
  require(object(context.evaluator_versions), 'missing-evaluator-versions');
  require(context.export_complete === true ||
    context.export_complete === false ||
    context.export_complete === null, 'missing-export-completeness');
  require(Array.isArray(executionEvidence) &&
    executionEvidence.length <= 10000, 'invalid-execution-evidence');
  const states = new Map();
  for (const record of executionEvidence) {
    require(object(record), 'invalid-execution-record');
    const id = identity(record.case_id);
    require(!states.has(id), 'duplicate-execution-record');
    require(['ok', 'error', 'unknown'].includes(record.state), 'invalid-task-state');
    states.set(id, record);
  }
  const cases = [];
  const seen = new Set();
  let outputBytes = 0;
  for (const row of result.itemResults) {
    require(object(row), 'invalid-item-result');
    require(row.datasetRunId === undefined ||
      row.datasetRunId === runId, 'item-belongs-to-another-experiment');
    const id = caseId(row.item);
    require(!seen.has(id), 'duplicate-result-case');
    seen.add(id);
    const hash = caseContentDigest(row.item);
    for (const key of ['input', 'expectedOutput']) {
      if (row[key] !== undefined) {
        require(canonical(row[key]) === canonical(row.item[key]), 'conflicting-item-content');
      }
    }
    require(Array.isArray(row.evaluations) && row.evaluations.length <= 128, 'invalid-evaluations');
    const evaluations = row.evaluations.map((evaluation) => {
      require(object(evaluation), 'invalid-evaluation');
      const name = identity(evaluation.name);
      const value = evaluation.value ?? null;
      require(value === null ||
        (typeof value === 'number' &&
          Number.isFinite(value) &&
          (!Number.isInteger(value) || Number.isSafeInteger(value))) ||
        (typeof value === 'string' && value.length <= 128), 'invalid-evaluation-value');
      return { name, value };
    });
    const record = states.get(id);
    const state =
      record?.content_sha256 === hash && record.attempts === 1 ? record.state : 'unknown';
    const projected = { case_id: id, content_sha256: hash, task_state: state, evaluations };
    outputBytes += Buffer.byteLength(JSON.stringify(projected));
    require(outputBytes <= MAX_BYTES, 'projected-result-too-large');
    cases.push(projected);
  }
  const receipt = {
    run_id: runId,
    ...Object.fromEntries(
      ['project_id', 'dataset_id', 'dataset_version', 'application_ref'].map((key) => [
        key,
        context[key] == null ? null : identity(context[key]),
      ]),
    ),
    evaluator_versions: Object.fromEntries(
      Object.entries(context.evaluator_versions).map(([name, version]) => [
        identity(name),
        version === null ? null : identity(version),
      ]),
    ),
    export_complete: context.export_complete,
    source_sdk_version: identity(context.sdk_version),
    projection_contract: 'langfuse-js-experiment-result-v6',
    cases,
  };
  require(Buffer.byteLength(JSON.stringify(receipt)) <= MAX_BYTES, 'projected-result-too-large');
  return receipt;
}
