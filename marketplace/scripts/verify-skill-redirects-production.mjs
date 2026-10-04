import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const redirects = JSON.parse(
  readFileSync(new URL('../src/data/skill-redirects.json', import.meta.url), 'utf8'),
).redirects;
const base = (process.argv[2] || 'https://tonsofskills.com').replace(/\/$/, '');

for (const redirect of redirects) {
  for (const suffix of ['', '/']) {
    const response = await fetch(`${base}/skills/${redirect.from}${suffix}`, {
      method: 'HEAD',
      redirect: 'manual',
    });
    assert.equal(response.status, 301, `${redirect.from}${suffix}: expected 301`);
    assert.equal(
      response.headers.get('location'),
      `/skills/${redirect.to}/`,
      `${redirect.from}${suffix}: wrong Location`,
    );
  }
}

console.log(`verified ${redirects.length * 2} production redirect variants at ${base}`);

// Retired-path map (ops/retired-path-redirects.caddy): sample three redirects spread across
// the map — first, middle, last — and require 301, the exact Location and the query string
// carried through. Then require one live target to serve 200, so a redirect onto a broken
// page cannot pass.
const retired = JSON.parse(
  readFileSync(new URL('../src/data/retired-path-redirects.json', import.meta.url), 'utf8'),
).entries.filter((entry) => entry.status === 301);
const sample = [...new Set([0, Math.floor(retired.length / 2), retired.length - 1])].map(
  (index) => retired[index],
);
const query = '?utm_source=redirect-verify&q=a%20b';
for (const entry of sample) {
  const response = await fetch(`${base}${entry.from}${query}`, {
    method: 'HEAD',
    redirect: 'manual',
  });
  assert.equal(response.status, 301, `${entry.from}: expected 301`);
  const location = new URL(response.headers.get('location') ?? '', base);
  assert.equal(
    `${location.pathname}${location.search}`,
    `${entry.to}${query}`,
    `${entry.from}: wrong Location or query string dropped`,
  );
}
const livePage = sample[0].to;
const liveResponse = await fetch(`${base}${livePage}`, { method: 'HEAD', redirect: 'manual' });
assert.equal(liveResponse.status, 200, `${livePage}: redirect target must serve 200`);
console.log(
  `verified ${sample.length} retired-path redirects (query preserved) and live target ${livePage} at ${base}`,
);
