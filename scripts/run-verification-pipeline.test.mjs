import assert from 'node:assert/strict';
import test from 'node:test';

import {
  aggregateByPlugin,
  applyVerifications,
  buildSummary,
  describeResult,
  findDrift,
} from './run-verification-pipeline.mjs';

test('aggregates repository-relative and absolute validator paths', () => {
  const result = aggregateByPlugin([
    {
      path: 'plugins/saas-packs/snowflake-pack/skills/one/SKILL.md',
      score: 94,
      grade: 'A',
    },
    {
      path: '/checkout/plugins/saas-packs/snowflake-pack/skills/two/SKILL.md',
      score: 96,
      grade: 'A',
    },
    {
      path: '/checkout/plugins/saas-packs/other-pack/skills/one/SKILL.md',
      score: 80,
      grade: 'B',
    },
    { path: '/checkout/not-plugins/ignored/SKILL.md', score: 100, grade: 'A' },
    { path: '/checkout/plugins/saas-packs/fatal/skills/x/SKILL.md', fatal: true },
  ]);

  assert.deepEqual(result.get('./plugins/saas-packs/snowflake-pack'), {
    score: 95,
    grade: 'A',
    badge: 'gold',
    skillCount: 2,
  });
  assert.equal(result.size, 2);
});

test('targeted catalog update cannot rewrite an unrelated plugin', () => {
  const catalog = {
    plugins: [
      {
        name: 'snowflake-pack',
        source: './plugins/saas-packs/snowflake-pack',
        verification: { score: 1, grade: 'F', badge: null, lastValidated: 'old' },
      },
      {
        name: 'other-pack',
        source: './plugins/saas-packs/other-pack',
        verification: { score: 80, grade: 'B', badge: 'silver', lastValidated: 'keep' },
      },
    ],
  };
  const unrelatedBefore = JSON.parse(JSON.stringify(catalog.plugins[1]));
  const verifications = new Map([
    [
      './plugins/saas-packs/snowflake-pack',
      { score: 95, grade: 'A', badge: 'gold', skillCount: 6 },
    ],
    ['./plugins/saas-packs/other-pack', { score: 100, grade: 'A', badge: 'gold', skillCount: 1 }],
  ]);

  const updated = applyVerifications(
    catalog,
    verifications,
    'snowflake-pack',
    '2026-08-31T00:00:00.000Z',
  );

  assert.equal(updated, 1);
  assert.deepEqual(catalog.plugins[0].verification, {
    score: 95,
    grade: 'A',
    badge: 'gold',
    lastValidated: '2026-08-31T00:00:00.000Z',
  });
  assert.deepEqual(catalog.plugins[1], unrelatedBefore);
});

test('an unchanged verification result keeps its original date and is not counted', () => {
  const block = { score: 95, grade: 'A', badge: 'gold', lastValidated: '2026-09-11T00:00:00.000Z' };
  const catalog = { plugins: [{ name: 'p', source: './plugins/x/p', verification: { ...block } }] };
  const updated = applyVerifications(
    catalog,
    new Map([['./plugins/x/p', { score: 95, grade: 'A', badge: 'gold', skillCount: 3 }]]),
    null,
    '2026-09-25T00:00:00.000Z',
  );
  assert.equal(updated, 0);
  assert.deepEqual(catalog.plugins[0].verification, block);
});

test('any change to score, grade, or badge restamps the date', () => {
  for (const change of [{ score: 94 }, { grade: 'B' }, { badge: 'silver' }]) {
    const catalog = {
      plugins: [
        {
          name: 'p',
          source: './plugins/x/p',
          verification: { score: 95, grade: 'A', badge: 'gold', lastValidated: 'old' },
        },
      ],
    };
    const next = { score: 95, grade: 'A', badge: 'gold', skillCount: 3, ...change };
    const updated = applyVerifications(catalog, new Map([['./plugins/x/p', next]]), null, 'new');
    assert.equal(updated, 1, JSON.stringify(change));
    assert.equal(catalog.plugins[0].verification.lastValidated, 'new', JSON.stringify(change));
  }
});

test('a plugin without a verification block receives its first result', () => {
  const catalog = { plugins: [{ name: 'p', source: './plugins/x/p' }] };
  const updated = applyVerifications(
    catalog,
    new Map([['./plugins/x/p', { score: 60, grade: 'D', badge: 'bronze', skillCount: 1 }]]),
    null,
    'new',
  );
  assert.equal(updated, 1);
  assert.deepEqual(catalog.plugins[0].verification, {
    score: 60,
    grade: 'D',
    badge: 'bronze',
    lastValidated: 'new',
  });
});

function driftFixture() {
  return {
    plugins: [
      {
        name: 'stale',
        source: './plugins/x/stale',
        verification: { score: 81, grade: 'B', badge: 'silver', lastValidated: 'old' },
      },
      {
        name: 'current',
        source: './plugins/x/current',
        verification: { score: 95, grade: 'A', badge: 'gold', lastValidated: 'old' },
      },
      { name: 'unscored', source: './plugins/x/unscored' },
    ],
  };
}

const COMPUTED = new Map([
  ['./plugins/x/stale', { score: 97, grade: 'A', badge: 'gold', skillCount: 4 }],
  ['./plugins/x/current', { score: 95, grade: 'A', badge: 'gold', skillCount: 2 }],
]);

test('findDrift names only scored plugins whose recorded result differs', () => {
  const drift = findDrift(driftFixture(), COMPUTED);
  assert.deepEqual(
    drift.map(({ plugin, recorded, computed }) => [plugin.name, recorded.score, computed.score]),
    [['stale', 81, 97]],
  );
});

test('findDrift and the writer share one definition of drift', () => {
  const catalog = driftFixture();
  const expected = findDrift(catalog, COMPUTED).map(({ plugin }) => plugin.name);
  assert.equal(applyVerifications(catalog, COMPUTED, null, 'new'), expected.length);
  assert.deepEqual(findDrift(catalog, COMPUTED), [], 'after writing, nothing drifts');
});

test('a hand-set badge that the validator does not compute is drift', () => {
  const catalog = driftFixture();
  catalog.plugins[1].verification.badge = 'verified';
  assert.deepEqual(
    findDrift(catalog, COMPUTED).map(({ plugin }) => plugin.name),
    ['stale', 'current'],
  );
});

test('findDrift respects a targeted plugin', () => {
  assert.deepEqual(findDrift(driftFixture(), COMPUTED, 'current'), []);
  assert.equal(findDrift(driftFixture(), COMPUTED, './plugins/x/stale').length, 1);
});

test('the summary lists scored plugins with their drift flag and adds no generation timestamp', () => {
  const catalog = driftFixture();
  const summary = buildSummary(catalog, COMPUTED, findDrift(catalog, COMPUTED));
  assert.equal(summary.scored, 2);
  assert.equal(summary.catalogEntries, 3);
  assert.equal(summary.drift, 1);
  assert.deepEqual(
    summary.plugins.map(({ name, drift, computed }) => [name, drift, computed.skillCount]),
    [
      ['stale', true, 4],
      ['current', false, 2],
    ],
  );
  assert.doesNotMatch(JSON.stringify(summary), /generatedAt|"\d{4}-\d{2}-\d{2}T/);
});

test('describeResult renders missing and badge-less results readably', () => {
  assert.equal(describeResult(null), 'none');
  assert.equal(describeResult({ score: 40, grade: 'F', badge: null }), '40/F/no badge');
});
