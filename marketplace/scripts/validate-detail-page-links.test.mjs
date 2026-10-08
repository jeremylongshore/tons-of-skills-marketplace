import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { auditDetailPageLinks } from './validate-detail-page-links.mjs';

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), 'validate-detail-page-links.mjs');

function page(distDirectory, route, body) {
  const directory = join(distDirectory, route);
  mkdirSync(directory, { recursive: true });
  writeFileSync(join(directory, 'index.html'), `<!DOCTYPE html><html><body>${body}</body></html>`);
}

function fixture(build) {
  const distDirectory = mkdtempSync(join(tmpdir(), 'detail-links-'));
  try {
    page(distDirectory, '', '<a href="/skills/">skills</a>');
    page(distDirectory, 'skills', '');
    page(distDirectory, 'plugins', '');
    build(distDirectory);
    return auditDetailPageLinks(distDirectory);
  } finally {
    rmSync(distDirectory, { recursive: true, force: true });
  }
}

test('passes absolute, anchor, and existing root-relative links', () => {
  const result = fixture((dist) => {
    page(
      dist,
      'skills/demo',
      [
        '<a href="/skills/">all</a>',
        '<a href="/plugins/demo-pack/">plugin</a>',
        '<a href="#usage">anchor</a>',
        '<a href="https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/plugins/x/references/a.md">src</a>',
        '<a href="mailto:a@b.c">mail</a>',
      ].join(''),
    );
    page(dist, 'plugins/demo-pack', '<a href="/skills/demo/">skill</a>');
  });
  assert.equal(result.pages, 2);
  assert.deepEqual(result.broken, []);
});

test('fails on page-relative reference links and reports both 404 forms', () => {
  const result = fixture((dist) => {
    page(dist, 'skills/demo', '<a href="references/official-docs.md#x">docs</a>');
    page(dist, 'plugins/demo-pack', '<a href="README.fr.md">fr</a>');
  });
  assert.deepEqual(
    result.broken.map(({ route, href, reason, resolvesTo }) => ({ route, href, reason, resolvesTo })),
    [
      {
        route: '/plugins/demo-pack/',
        href: 'README.fr.md',
        reason: 'page-relative link',
        resolvesTo: ['/plugins/demo-pack/README.fr.md', '/plugins/README.fr.md'],
      },
      {
        route: '/skills/demo/',
        href: 'references/official-docs.md',
        reason: 'page-relative link',
        resolvesTo: ['/skills/demo/references/official-docs.md', '/skills/references/official-docs.md'],
      },
    ],
  );
});

test('fails on root-relative .md links that were never built', () => {
  const result = fixture((dist) => {
    page(dist, 'skills/demo', '<a href="/skills/references/x.md">x</a>');
  });
  assert.equal(result.broken.length, 1);
  assert.equal(result.broken[0].reason, 'target not built');
  assert.equal(result.broken[0].href, '/skills/references/x.md');
});

test('CLI exits non-zero on a broken page and on an empty dist', () => {
  const distDirectory = mkdtempSync(join(tmpdir(), 'detail-links-cli-'));
  try {
    const empty = spawnSync(process.execPath, [SCRIPT, '--dist', distDirectory], { encoding: 'utf8' });
    assert.equal(empty.status, 1, 'an empty dist must not pass vacuously');

    page(distDirectory, 'skills/demo', '<a href="references/a.md">a</a>');
    const red = spawnSync(process.execPath, [SCRIPT, '--dist', distDirectory], { encoding: 'utf8' });
    assert.equal(red.status, 1);
    assert.match(red.stderr, /\/skills\/references\/a\.md/);

    page(distDirectory, 'skills/demo', '<a href="/skills/demo/">self</a>');
    const green = spawnSync(process.execPath, [SCRIPT, '--dist', distDirectory], { encoding: 'utf8' });
    assert.equal(green.status, 0, green.stderr);
  } finally {
    rmSync(distDirectory, { recursive: true, force: true });
  }
});
