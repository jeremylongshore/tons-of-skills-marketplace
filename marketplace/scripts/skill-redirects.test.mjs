import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { renderSkillRedirects } from './render-skill-redirects-caddy.mjs';

const redirects = JSON.parse(
  readFileSync(new URL('../src/data/skill-redirects.json', import.meta.url), 'utf8'),
).redirects;
const catalog = JSON.parse(
  readFileSync(new URL('../src/data/skills-catalog.json', import.meta.url), 'utf8'),
);
const caddyFragment = readFileSync(
  new URL('../ops/snowflake-v2-redirects.caddy', import.meta.url),
  'utf8',
);

test('skill tombstones are unique permanent redirects to live skills', () => {
  const live = new Set(catalog.skills.map((skill) => skill.slug));
  const seen = new Set();

  assert.equal(redirects.length, 59);
  assert.equal(redirects.filter((redirect) => redirect.from.startsWith('snowflake-')).length, 30);
  assert.deepEqual(
    redirects
      .filter((redirect) => redirect.from.startsWith('ga4-'))
      .map(({ from, to }) => ({ from, to })),
    [
      { from: 'ga4-auth-setup', to: 'ga4-report-forensics' },
      { from: 'ga4-data-api-query', to: 'ga4-report-forensics' },
      { from: 'ga4-common-reports', to: 'ga4-report-forensics' },
      { from: 'ga4-realtime-api', to: 'ga4-measurement-verifier' },
      { from: 'ga4-bigquery-export', to: 'ga4-export-guardian' },
    ],
  );
  const langfuse = redirects.filter((redirect) => redirect.from.startsWith('langfuse-'));
  assert.equal(langfuse.length, 24);
  assert.deepEqual([...new Set(langfuse.map((redirect) => redirect.to))].sort(), [
    'langfuse-cost-forensics',
    'langfuse-data-boundary-auditor',
    'langfuse-experiment-guardian',
    'langfuse-prompt-release-guardian',
    'langfuse-trace-ingestion-medic',
  ]);
  for (const redirect of redirects) {
    assert.match(redirect.from, /^[a-z0-9][a-z0-9-]+$/);
    assert.match(redirect.to, /^[a-z0-9][a-z0-9-]+$/);
    assert.equal(redirect.status, 301);
    assert.notEqual(redirect.from, redirect.to);
    assert.equal(seen.has(redirect.from), false, `duplicate redirect: ${redirect.from}`);
    assert.equal(live.has(redirect.from), false, `retired slug is still live: ${redirect.from}`);
    assert.equal(live.has(redirect.to), true, `redirect target is missing: ${redirect.to}`);
    seen.add(redirect.from);
  }
});

test('Caddy fragment is the exact generated ingress projection', () => {
  assert.equal(caddyFragment, renderSkillRedirects(redirects));
  assert.equal((caddyFragment.match(/^@redir\d+ path /gm) || []).length, 59);
  assert.equal((caddyFragment.match(/ permanent$/gm) || []).length, 59);
});

test('retired slugs are not emitted as Astro static routes', () => {
  const routeSource = readFileSync(
    new URL('../src/pages/skills/[slug].astro', import.meta.url),
    'utf8',
  );
  assert.equal(routeSource.includes('skill-redirects.json'), false);
  assert.equal(routeSource.includes('Astro.redirect'), false);
});
