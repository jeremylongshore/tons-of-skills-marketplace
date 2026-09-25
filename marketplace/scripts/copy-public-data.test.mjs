import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import {
  buildTimestamp,
  PROJECTED_FILES,
  projectPublicData,
  stampGeneratedAt,
  TIMESTAMPED_FILES,
} from './copy-public-data.mjs';

const STAMP = '2026-01-02T03:04:05.000Z';

function catalogSource(extra = {}) {
  return JSON.stringify(
    {
      schemaVersion: '3.6.0',
      level: 'full',
      skills: [{ slug: 'b-skill', name: 'b-skill' }],
      count: 1,
      ...extra,
      categories: ['devops'],
      allowedToolsUsed: ['Read'],
    },
    null,
    2,
  );
}

test('the public catalog differs from the tracked source by exactly one inserted line', () => {
  const source = catalogSource();
  const stamped = stampGeneratedAt(source, STAMP);
  const sourceLines = source.split('\n');
  const stampedLines = stamped.split('\n');
  assert.equal(stampedLines.length, sourceLines.length + 1);
  const inserted = stampedLines.filter((line) => !sourceLines.includes(line));
  assert.deepEqual(inserted, [`  "generatedAt": "${STAMP}",`]);
  assert.equal(stampedLines.filter((line) => !inserted.includes(line)).join('\n'), source);
});

test('generatedAt keeps its schema 3.4.0 position directly after count', () => {
  const keys = Object.keys(JSON.parse(stampGeneratedAt(catalogSource(), STAMP)));
  assert.deepEqual(keys, [
    'schemaVersion',
    'level',
    'skills',
    'count',
    'generatedAt',
    'categories',
    'allowedToolsUsed',
  ]);
});

test('an existing generatedAt is replaced, never duplicated or rejected', () => {
  const stale = catalogSource({ generatedAt: '2020-01-01T00:00:00.000Z' });
  const stamped = stampGeneratedAt(stale, STAMP);
  assert.equal(JSON.parse(stamped).generatedAt, STAMP);
  assert.equal(stamped.match(/"generatedAt"/g).length, 1);
});

test('a catalog without count still receives generatedAt', () => {
  const stamped = JSON.parse(stampGeneratedAt('{"skills":[]}', STAMP));
  assert.equal(stamped.generatedAt, STAMP);
});

test('invalid inputs fail closed', () => {
  assert.throws(() => stampGeneratedAt('[]', STAMP), /expected a JSON object/);
  assert.throws(() => stampGeneratedAt('null', STAMP), /expected a JSON object/);
  assert.throws(() => stampGeneratedAt(catalogSource(), 'not-a-date'), /invalid generatedAt/);
  assert.throws(() => stampGeneratedAt('{broken', STAMP), SyntaxError);
});

test('buildTimestamp honors SOURCE_DATE_EPOCH and otherwise uses the clock', () => {
  assert.equal(buildTimestamp({ SOURCE_DATE_EPOCH: '0' }), '1970-01-01T00:00:00.000Z');
  assert.equal(buildTimestamp({ SOURCE_DATE_EPOCH: '1767323045' }), '2026-01-02T03:04:05.000Z');
  assert.equal(buildTimestamp({}, () => new Date(STAMP)), STAMP);
  assert.equal(buildTimestamp({ SOURCE_DATE_EPOCH: '' }, () => new Date(STAMP)), STAMP);
  assert.throws(() => buildTimestamp({ SOURCE_DATE_EPOCH: '-5' }), /non-negative integer/);
  assert.throws(() => buildTimestamp({ SOURCE_DATE_EPOCH: '12.5' }), /non-negative integer/);
});

test('projectPublicData stamps only the catalog and copies the search index byte for byte', () => {
  const root = mkdtempSync(join(tmpdir(), 'copy-public-data-'));
  try {
    const srcDir = join(root, 'src');
    const publicDataDir = join(root, 'public', 'data');
    mkdirSync(srcDir);
    const search = '{\n  "meta": {\n    "version": "1.0.0"\n  }\n}';
    writeFileSync(join(srcDir, 'unified-search-index.json'), search);
    writeFileSync(join(srcDir, 'skills-catalog.json'), catalogSource());
    const logs = [];
    projectPublicData({ srcDir, publicDataDir, generatedAt: STAMP, log: (line) => logs.push(line) });
    assert.equal(readFileSync(join(publicDataDir, 'unified-search-index.json'), 'utf8'), search);
    assert.equal(
      JSON.parse(readFileSync(join(publicDataDir, 'skills-catalog.json'), 'utf8')).generatedAt,
      STAMP,
    );
    assert.equal(logs.length, PROJECTED_FILES.length);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('only projected files are timestamped', () => {
  for (const file of TIMESTAMPED_FILES) assert.ok(PROJECTED_FILES.includes(file), file);
});

test('the tracked skill projections carry no wall-clock timestamp', () => {
  for (const file of ['skills-catalog.json', 'skills-index.json']) {
    const parsed = JSON.parse(
      readFileSync(new URL(`../src/data/${file}`, import.meta.url), 'utf8'),
    );
    assert.equal(Object.hasOwn(parsed, 'generatedAt'), false, file);
  }
});
