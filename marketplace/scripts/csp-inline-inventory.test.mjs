import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';

import { buildInventory, diffInventory, scanHtml } from './csp-inline-inventory.mjs';

test('executable inline scripts and handlers are inventoried; data and external scripts are not', () => {
  const found = scanHtml(`
    <script>console.log(1)</script>
    <script type="module">import('/x.js')</script>
    <script type="application/ld+json">{"@type":"Thing"}</script>
    <script type="application/json" id="d">{"a":1}</script>
    <script src="/_astro/app.js"></script>
    <script type="module" src="/_astro/m.js"></script>
    <button onclick="go()">x</button>
    <a href="#" ONMOUSEOVER='hover()'>y</a>
  `);
  assert.deepEqual(
    found.map((f) => f.kind),
    ['inline-script', 'inline-script', 'event-handler', 'event-handler'],
  );
  assert.match(found[2].sample, /^onclick="go\(\)"$/);
  assert.match(found[3].sample, /^onmouseover="hover\(\)"$/);
});

test('handler-like text inside a script body is not double-counted as an attribute', () => {
  const found = scanHtml(`<script>el.innerHTML = '<b onclick="x()">'</script>`);
  assert.deepEqual(found.map((f) => f.kind), ['inline-script']);
});

test('a planted addition and a removed script are both reported', () => {
  const dir = mkdtempSync(join(tmpdir(), 'csp-inv-'));
  try {
    mkdirSync(join(dir, 'a'));
    writeFileSync(join(dir, 'index.html'), '<script>keep()</script>');
    writeFileSync(join(dir, 'a', 'index.html'), '<script>keep()</script>');
    const tracked = buildInventory(dir);
    assert.equal(tracked.length, 1, 'identical scripts on two pages collapse to one entry');

    writeFileSync(join(dir, 'a', 'index.html'), '<script>keep()</script><script>planted()</script>');
    let { added, removed } = diffInventory(buildInventory(dir), tracked);
    assert.equal(added.length, 1);
    assert.match(added[0].sample, /planted/);
    assert.equal(removed.length, 0);

    writeFileSync(join(dir, 'index.html'), '');
    writeFileSync(join(dir, 'a', 'index.html'), '');
    ({ added, removed } = diffInventory(buildInventory(dir), tracked));
    assert.equal(added.length, 0);
    assert.equal(removed.length, 1, 'a script no longer built is a stale entry');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('an empty or missing build fails closed instead of reporting zero', () => {
  const dir = mkdtempSync(join(tmpdir(), 'csp-inv-empty-'));
  try {
    assert.throws(() => buildInventory(dir), /no HTML files found/);
    assert.throws(() => buildInventory(join(dir, 'missing')), /does not exist/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
