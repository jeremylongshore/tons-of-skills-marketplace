import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import {
  HOME_ALLOWLIST,
  SECTION_INDEXES,
  buildMap,
  loadLiveUniverse,
  matcherId,
  normalize,
  renderCaddy,
} from './build-retired-path-redirects.mjs';

const read = (rel) => readFileSync(new URL(rel, import.meta.url), 'utf8');
const map = JSON.parse(read('../src/data/retired-path-redirects.json'));
const caddy = read('../ops/retired-path-redirects.caddy');
const inventory = JSON.parse(read('../src/data/retired-paths.json'));
const snowflake = JSON.parse(read('../src/data/skill-redirects.json')).redirects;
const live = loadLiveUniverse();
const redirects = map.entries.filter((e) => e.status === 301);
const dist = fileURLToPath(new URL('../dist/', import.meta.url));

test('tracked map and Caddy fragment are the exact generator output', () => {
  const fresh = buildMap();
  assert.deepEqual(map, fresh, 'run: node marketplace/scripts/build-retired-path-redirects.mjs');
  assert.equal(caddy, renderCaddy(fresh));
});

test('every observed 404 path is accounted for exactly once', () => {
  const observed = map.entries.flatMap((e) => e.observed).sort();
  assert.deepEqual(observed, [...inventory.paths].sort());
  assert.equal(new Set(map.entries.map((e) => e.from)).size, map.entries.length);
  for (const e of map.entries) {
    assert.ok(e.observed.every((p) => normalize(p) === e.from), `${e.from}: mixed observations`);
    assert.ok([301, 404].includes(e.status), `${e.from}: unexpected status ${e.status}`);
    assert.ok(e.rule, `${e.from}: decision has no recorded rule`);
    if (e.status === 404) assert.equal(e.to, undefined, `${e.from}: a kept 404 has a target`);
  }
  assert.equal(map.stats.redirected + map.stats.kept404, map.entries.length);
});

test('every redirect target exists in the current catalog', () => {
  for (const e of redirects) {
    assert.ok(live.routes.has(e.to), `${e.from} -> ${e.to}: target is not a live route`);
    assert.notEqual(normalize(e.to), e.from, `${e.from}: redirects to itself`);
  }
});

test('every redirect target exists in the built site when a build is present', (t) => {
  if (!existsSync(join(dist, 'index.html'))) {
    assert.ok(!process.env.CI, 'CI must build the marketplace before this test');
    t.skip('no marketplace/dist build present');
    return;
  }
  for (const e of redirects) {
    const page = join(dist, e.to, 'index.html');
    assert.ok(existsSync(page), `${e.from} -> ${e.to}: missing ${page}`);
  }
});

// Caddy evaluates `redir` before the static file handler, so a retired path that later
// becomes a real page again would be silently shadowed. Fail the build instead.
test('no redirected path is a live route in the current catalog or build', (t) => {
  for (const e of map.entries) {
    assert.equal(live.routes.has(`${e.from}/`), false, `${e.from}: retired path is a live catalog route`);
  }
  if (!existsSync(join(dist, 'index.html'))) {
    assert.ok(!process.env.CI, 'CI must build the marketplace before this test');
    t.skip('no marketplace/dist build present');
    return;
  }
  // Mirrors the site's try_files order: {path}, {path}/, {path}.html.
  for (const e of redirects) {
    const rel = e.from.slice(1);
    for (const candidate of [rel, join(rel, 'index.html'), `${rel}.html`]) {
      assert.equal(existsSync(join(dist, candidate)), false, `${e.from}: shadows built file ${candidate}`);
    }
  }
});

test('no redirect chains or loops', () => {
  const sources = new Set([
    ...map.entries.map((e) => e.from),
    ...snowflake.map((r) => `/skills/${r.from}`),
  ]);
  for (const e of redirects) {
    assert.equal(sources.has(normalize(e.to)), false, `${e.from} -> ${e.to}: target is itself redirected or retired`);
  }
});

test('nothing redirects to the home page outside the explicit allowlist', () => {
  assert.deepEqual(HOME_ALLOWLIST, []);
  for (const e of redirects) {
    if (normalize(e.to) === '/') assert.ok(HOME_ALLOWLIST.includes(e.from), `${e.from} -> /`);
  }
  for (const e of redirects.filter((r) => SECTION_INDEXES.includes(r.to))) {
    assert.match(e.rule, /section-index$/, `${e.from}: section-index target from rule ${e.rule}`);
  }
});

test('Caddy fragment preserves query strings and covers both slash forms', () => {
  const matchers = [...caddy.matchAll(/^(@retired[0-9a-f]{12}) path (\S+) (\S+)$/gm)];
  const redirs = [...caddy.matchAll(/^redir (@retired[0-9a-f]{12}) (\S+) permanent$/gm)];
  assert.equal(matchers.length, redirects.length);
  assert.equal(redirs.length, redirects.length);
  assert.equal(new Set(matchers.map((m) => m[1])).size, matchers.length, 'duplicate matcher ids');
  redirects.forEach((e, i) => {
    assert.deepEqual([matchers[i][2], matchers[i][3]], [e.from, `${e.from}/`]);
    assert.equal(matchers[i][1], matcherId(e.from), `${e.from}: matcher id is not path-stable`);
    assert.equal(redirs[i][1], matchers[i][1]);
    assert.equal(redirs[i][2], `${e.to}{?query}`, `${e.from}: query string would be dropped`);
  });
  assert.equal(/@redir\d/.test(caddy), false, 'must not reuse the hand-installed @redirNNN namespace');
});

// Exercises the real ingress semantics when a caddy binary is available (it is on the
// operator host and dev box; CI runners skip this and rely on the rendering test above).
test('real Caddy serves 301 with the query string preserved', async (t) => {
  if (spawnSync('caddy', ['version']).status !== 0) {
    t.skip('caddy binary not on PATH');
    return;
  }
  const dir = mkdtempSync(join(tmpdir(), 'retired-redirects-'));
  const port = 20000 + Math.floor(Math.random() * 20000);
  writeFileSync(join(dir, 'fragment.caddy'), caddy);
  writeFileSync(
    join(dir, 'Caddyfile'),
    `{\n\tadmin off\n\tauto_https off\n}\nhttp://127.0.0.1:${port} {\n\timport ${join(dir, 'fragment.caddy')}\n\trespond 404\n}\n`,
  );
  const server = spawn('caddy', ['run', '--config', join(dir, 'Caddyfile'), '--adapter', 'caddyfile'], {
    stdio: 'ignore',
  });
  try {
    const base = `http://127.0.0.1:${port}`;
    for (let i = 0; i < 50; i += 1) {
      try {
        await fetch(base);
        break;
      } catch {
        await new Promise((r) => setTimeout(r, 100));
      }
    }
    const sample = [redirects[0], redirects[Math.floor(redirects.length / 2)], redirects.at(-1)];
    for (const e of sample) {
      for (const [suffix, query] of [['', ''], ['/', '?utm_source=x&q=a%20b']]) {
        const res = await fetch(`${base}${e.from}${suffix}${query}`, { redirect: 'manual' });
        assert.equal(res.status, 301, `${e.from}${suffix}${query}`);
        assert.equal(new URL(res.headers.get('location'), base).pathname + new URL(res.headers.get('location'), base).search, `${e.to}${query}`);
      }
    }
    const kept = map.entries.find((e) => e.status === 404 && /^\/[a-z]/.test(e.from));
    const res = await fetch(`${base}${kept.from}`, { redirect: 'manual' });
    assert.equal(res.status, 404, `${kept.from}: a kept 404 must not be redirected`);
  } finally {
    server.kill();
    rmSync(dir, { recursive: true, force: true });
  }
});
