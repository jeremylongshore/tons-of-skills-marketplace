/* global URL, structuredClone */

import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { EvidenceBundlePayloadSchema } from '@intentsolutions/core/validators/v1/evidence-statement';
import { assemble } from './assemble-manifest.ts';
import { buildRows, stableStringify, writeEmit } from './emit-evidence.ts';

// The dashboard consumes this same producer-generated vector in its binding
// suite. It is unsigned: real signature/mutation coverage lives at ingest.
const fixture = JSON.parse(
  readFileSync(new URL('./canonical-payload.fixture.json', import.meta.url)),
);

function emitted(t) {
  const dir = mkdtempSync(join(tmpdir(), 'ccp-canonical-payload-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const rows = buildRows(fixture.outcomes, {
    ...fixture.context,
    rand16: () => new Uint8Array(16),
  });
  const skeleton = writeEmit(rows, 'refs/heads/main', dir);
  for (let i = 0; i < rows.length; i++) {
    // Assembly transports sigstore bytes; it does not claim to verify them.
    writeFileSync(join(dir, `bundle-${i}.sigstore.json`), '{}');
  }
  return { dir, rows, skeleton };
}

test('producer and assembler preserve the dashboard interoperability vector', (t) => {
  const { dir, rows } = emitted(t);
  const row = rows[0];
  assert.deepEqual(row, fixture.row);
  EvidenceBundlePayloadSchema.parse(row.evidencePayload);
  const payloadBytes = readFileSync(join(dir, 'evidence-payload-0.json'), 'utf8');
  assert.equal(payloadBytes, stableStringify(row.evidencePayload));
  const digest = createHash('sha256').update(payloadBytes).digest('hex');
  assert.equal(row.bundle.storage_key, `sha256:${digest}`);
  assert.deepEqual(assemble(dir).rows[0], {
    bundle: row.bundle,
    sigstoreBundle: {},
    sourceSha: row.sourceSha,
    evidencePayload: row.evidencePayload,
    gateResults: [row.gateResult],
  });
});

for (const field of ['storage_key', 'row_count', 'subject_set', 'predicate_uri_set']) {
  test(`assembly rejects a changed signed ${field}`, (t) => {
    const { dir, rows } = emitted(t);
    const bundle = structuredClone(rows[0].bundle);
    bundle[field] = {
      storage_key: `sha256:${'f'.repeat(64)}`,
      row_count: 2,
      subject_set: [],
      predicate_uri_set: [],
    }[field];
    writeFileSync(join(dir, 'bundle-0.json'), stableStringify(bundle));
    assert.throws(() => assemble(dir), new RegExp(`signed bundle ${field}`));
  });
}

for (const variant of ['payload', 'body', 'missing-payload', 'statement-invariant']) {
  test(`assembly refuses ${variant} mutation without a legacy downgrade`, (t) => {
    const { dir, skeleton } = emitted(t);
    const row = skeleton.rows[0];
    if (variant === 'payload') row.evidencePayload[0].extensions = { tampered: true };
    if (variant === 'body')
      row.gateResults[0] = { ...row.gateResults[0], gate_reasons: ['tampered'] };
    if (variant === 'missing-payload') delete row.evidencePayload;
    if (variant === 'statement-invariant') row.evidencePayload[0].subject[0].name = 'wrong';
    writeFileSync(join(dir, 'manifest-skeleton.json'), JSON.stringify(skeleton));
    const expected = {
      payload: /signed bundle storage_key/,
      body: /gateResults do not match evidencePayload predicates/,
      'missing-payload': /expected array, received undefined/,
      'statement-invariant': /subject\[0\]\.name must equal predicate\.gate_id/,
    }[variant];
    assert.throws(() => assemble(dir), expected);
  });
}
