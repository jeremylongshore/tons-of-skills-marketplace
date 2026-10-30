import test from 'node:test';
import assert from 'node:assert/strict';
import { buildNotices, publishNotices } from './forge-api-drift-issues.mjs';

const row = {
  plugin: 'plugins/productivity/plane',
  status: 'NAME_DRIFT',
  upstream_commit: 'a'.repeat(40),
  missing_tools: ['get_cycle'],
};
const report = (rows = [row]) => ({ schema_version: 1, results: rows });
const notice = () => buildNotices(report())[0];

test('name drift renders bounded evidence with the runtime claim ceiling', () => {
  const n = notice();
  assert.match(n.body, /`get_cycle`/);
  assert.match(n.body, /does not execute.*prove an outage/);
  assert.ok(n.body.startsWith(n.marker));
});

test('unknown is visible while no-name-drift does not create or close issues', async () => {
  const n = buildNotices(
    report([{ plugin: row.plugin, status: 'UNVERIFIED', reason: 'UPSTREAM_FETCH_FAILED' }]),
  );
  assert.match(n[0].body, /not a no-drift result/);
  const clean = buildNotices(report([{ plugin: row.plugin, status: 'NO_NAME_DRIFT' }]));
  assert.deepEqual(clean, []);
  await publishNotices(clean, () => {
    throw new Error('no API calls should be made');
  });
});

test('invalid reports and remote-shaped injection never reach the issue API', () => {
  for (const bad of [
    {},
    report([]),
    report([row, row]),
    report([{ ...row, missing_tools: ['x\n@everyone'] }]),
    report([{ ...row, upstream_commit: '../main' }]),
    report([{ ...row, plugin: 'plugins/x/y\n@everyone' }]),
    report([{ ...row, status: 'PASS' }]),
    report([
      { plugin: row.plugin, status: 'UNVERIFIED', reason: 'https://secret.invalid/?token=x' },
    ]),
  ]) {
    assert.throws(() => buildNotices(bad));
  }
});

test('global configuration failure produces an operational notice', () => {
  const notices = buildNotices({
    schema_version: 1,
    results: [],
    status: 'UNVERIFIED',
    reason: 'CONFIG_INVALID',
  });
  assert.equal(notices.length, 1);
  assert.match(notices[0].title, /configuration/);
});

test('first negative observation creates exactly one issue', async () => {
  const calls = [];
  const result = await publishNotices([notice()], async (...args) => {
    calls.push(args);
    return args[0] === 'GET' ? [] : { number: 1 };
  });
  assert.deepEqual(result, { created: 1, updated: 0 });
  assert.equal(calls.filter(([method]) => method === 'POST').length, 1);
});

test('repeat observation is silent; changed evidence updates the bot issue without a comment', async () => {
  const n = notice();
  const existing = { number: 12, user: { login: 'github-actions[bot]' }, ...n };
  const calls = [];
  const api = async (...args) => {
    calls.push(args);
    return args[0] === 'GET' ? [existing] : {};
  };
  assert.deepEqual(await publishNotices([n], api), { created: 0, updated: 0 });
  existing.body = n.marker + '\nolder evidence';
  assert.deepEqual(await publishNotices([n], api), { created: 0, updated: 1 });
  assert.ok(calls.some(([method, path]) => method === 'PATCH' && path === '/issues/12'));
  assert.ok(!calls.some(([, path]) => path.includes('comments')));
});

test('pagination finds existing bot issue while user-spoofed markers and PRs are untouched', async () => {
  const n = notice();
  const first = Array.from({ length: 100 }, (_, i) => ({
    number: i + 1,
    user: { login: 'someone' },
    body: `${n.marker}\nspoof`,
  }));
  const existing = { number: 101, user: { login: 'github-actions[bot]' }, ...n };
  const methods = [];
  const api = async (method, path) => {
    methods.push(method);
    if (new URL(`https://example.invalid${path}`).searchParams.get('page') === '1') return first;
    return [{ ...existing, pull_request: {} }, existing];
  };
  assert.deepEqual(await publishNotices([n], api), { created: 0, updated: 0 });
  assert.deepEqual(methods, ['GET', 'GET']);
});

test('incomplete inventory, duplicate owned issues and API refusal fail visibly', async () => {
  const n = notice();
  const existing = { number: 12, user: { login: 'github-actions[bot]' }, ...n };
  await assert.rejects(
    publishNotices([n], async () => [existing, existing]),
    /Duplicate/,
  );
  await assert.rejects(
    publishNotices([n], async () => {
      throw new Error('HTTP 403');
    }),
    /403/,
  );
  await assert.rejects(
    publishNotices([n], async () => Array(100).fill({})),
    /bounded pagination/,
  );
});
