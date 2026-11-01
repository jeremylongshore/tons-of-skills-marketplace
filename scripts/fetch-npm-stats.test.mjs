import assert from 'node:assert/strict';
import test from 'node:test';

import prettier from 'prettier';

import {
  buildReadmeBlock,
  prepareStatsArtifacts,
  spliceReadmeStats,
  downloadWindow,
  downloadWindowTotals,
  statsFor,
} from './fetch-npm-stats.mjs';

const SAMPLE = {
  generatedAt: '2026-09-02T03:47:05.535Z',
  max_age_hours: 72,
  publishedCount: 394,
  establishedCount: 394,
  candidateCount: 423,
  totalDay: 641,
  totalWeek: 3272,
  totalMonth: 11794,
  establishedDay: 641,
  establishedWeek: 3272,
  establishedMonth: 11794,
  top: [
    {
      name: '@intentsolutionsio/openrouter-pack',
      status: 'published',
      lastDay: 21,
      lastWeek: 100,
      lastMonth: 400,
      createdAt: 1,
      latestVersion: '1.0.0',
    },
  ],
  telemetry: {
    candidates: 423,
    probed: 423,
    published: 394,
    unpublished: 27,
    foreign: 2,
    rateLimited: 0,
    errors: 0,
  },
};

const README_FIXTURE = [
  '# Marketplace',
  '',
  '<!-- NPM-STATS:START — do not edit; daily cron updates this -->',
  'stale stats',
  '<!-- NPM-STATS:END -->',
  '',
  'Footer',
  '',
].join('\n');

test('prepared JSON and README describe the same exact snapshot', async () => {
  const { jsonOutput, readmeOutput } = await prepareStatsArtifacts(SAMPLE, {
    readme: README_FIXTURE,
    prettierOptions: { proseWrap: 'preserve' },
    filepath: 'README.md',
  });

  assert.deepEqual(JSON.parse(jsonOutput), SAMPLE);
  assert.match(readmeOutput, /Across \*\*394 published packages\*\*/);
  assert.match(readmeOutput, /\| Last 24 hours\s+\|\s+641 \|\s+641 \|/);
  assert.match(readmeOutput, /\| Last 7 days\s+\|\s+3,272 \|\s+3,272 \|/);
  assert.match(readmeOutput, /\| Last 30 days\s+\|\s+11,794 \|\s+11,794 \|/);
  assert.match(readmeOutput, /Last refreshed 2026-09-02T03:47:05\.535Z/);
  assert.doesNotMatch(readmeOutput, /stale stats/);
});

test('missing README sentinels fail instead of producing a partial snapshot', async () => {
  await assert.rejects(
    prepareStatsArtifacts(SAMPLE, { readme: '# No generated block\n' }),
    /missing NPM-STATS sentinels/,
  );
});

test('formatter failures propagate instead of silently skipping the README', async () => {
  const failingFormatter = {
    async format() {
      throw new Error('formatter unavailable');
    },
  };

  await assert.rejects(
    prepareStatsArtifacts(SAMPLE, {
      readme: README_FIXTURE,
      formatter: failingFormatter,
    }),
    /formatter unavailable/,
  );
});

test('the rendered block can only replace its bounded README region', () => {
  const block = buildReadmeBlock(SAMPLE);
  const updated = spliceReadmeStats(README_FIXTURE, block);

  assert.ok(updated.startsWith('# Marketplace\n\n'));
  assert.ok(updated.endsWith('\n\nFooter\n'));
});

test('API-reported UTC range preserves day/week/month counts across leap-year boundaries', () => {
  const window = downloadWindow('2024-02-29');
  assert.deepEqual(window, { start: '2024-01-31', end: '2024-02-29' });
  const date = new Date(window.start + 'T00:00:00Z');
  const downloads = Array.from({ length: 30 }, (_, index) => {
    const row = { day: date.toISOString().slice(0, 10), downloads: index + 1 };
    date.setUTCDate(date.getUTCDate() + 1);
    return row;
  });
  const body = { package: '@intentsolutionsio/fixture', ...window, downloads };
  assert.deepEqual(downloadWindowTotals(body, body.package), {
    lastDay: 30,
    lastWeek: 189,
    lastMonth: 465,
  });
  for (const mutate of [
    (b) => b.downloads.pop(),
    (b) => (b.downloads[0].downloads = -1),
    (b) => (b.downloads[0].downloads = Infinity),
    (b) => (b.downloads[0].downloads = 0.5),
    (b) => (b.downloads[0].day = b.downloads[1].day),
    (b) => (b.downloads[0].day = '1900-01-01'),
    (b) => (b.package = 'foreign'),
    (b) => (b.end = '2024-02-28'),
  ]) {
    const bad = globalThis.structuredClone(body);
    mutate(bad);
    assert.throws(() => downloadWindowTotals(bad, body.package));
  }
});

test('published-package collection uses two requests and keeps explicit 404 zeros without accepting malformed success', async () => {
  const name = '@intentsolutionsio/fixture',
    window = downloadWindow('2024-02-29');
  const date = new Date(window.start + 'T00:00:00Z');
  const downloads = Array.from({ length: 30 }, () => {
    const row = { day: date.toISOString().slice(0, 10), downloads: 1 };
    date.setUTCDate(date.getUTCDate() + 1);
    return row;
  });
  const original = globalThis.fetch;
  try {
    for (const mode of ['ok', 'missing', 'malformed']) {
      const calls = [];
      globalThis.fetch = async (url) => {
        calls.push(url);
        if (calls.length === 1)
          return {
            ok: true,
            status: 200,
            json: async () => ({
              'dist-tags': { latest: '1.0.0' },
              time: { created: '2020-01-01T00:00:00Z' },
            }),
          };
        if (mode === 'missing') return { ok: false, status: 404 };
        return {
          ok: true,
          status: 200,
          json: async () => (mode === 'malformed' ? {} : { package: name, ...window, downloads }),
        };
      };
      const result = await statsFor(name);
      assert.equal(calls.length, 2);
      assert.match(calls[1], /downloads\/range\/last-month\//);
      assert.equal(result.status, mode === 'malformed' ? 'error' : 'published');
      if (mode !== 'malformed')
        assert.deepEqual(
          [result.lastDay, result.lastWeek, result.lastMonth],
          mode === 'missing' ? [0, 0, 0] : [1, 7, 30],
        );
    }
  } finally {
    globalThis.fetch = original;
  }
});

test('download windows reject malformed or normalized calendar dates', () => {
  for (const end of [
    undefined,
    '',
    'not-a-date',
    '2024-02-30',
    '2024-13-01',
    '2024-2-29',
    '2024-02-29T00:00:00Z',
  ]) {
    assert.throws(() => downloadWindow(end));
  }
});
