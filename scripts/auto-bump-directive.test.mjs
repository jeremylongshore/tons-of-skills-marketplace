import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { hasSkipDirective } from './auto-bump-directive.mjs';

test('only a standalone body directive opts out', () => {
  for (const body of [
    '[skip auto-bump]',
    'Reason\n\n[skip auto-bump]\n',
    'Reason\r\n  [skip auto-bump] \t\r\n',
  ]) {
    assert.equal(hasSkipDirective(body), true, JSON.stringify(body));
  }
  for (const body of [
    null,
    undefined,
    '',
    'This PR does NOT use [skip auto-bump].',
    '`[skip auto-bump]`',
    '> [skip auto-bump]',
    '- [skip auto-bump]',
    '    [skip auto-bump]',
    '\t[skip auto-bump]',
    '[skip auto-bump] explanation',
    '[SKIP AUTO-BUMP]',
  ]) {
    assert.equal(hasSkipDirective(body), false, JSON.stringify(body));
  }
});

test('examples and comments do not suppress a bump', () => {
  for (const body of [
    '```md\n[skip auto-bump]\n```',
    '~~~\n[skip auto-bump]\n~~~',
    '````\n```\n[skip auto-bump]\n````',
    '<!--\n[skip auto-bump]\n-->',
    '<!--\n[skip auto-bump]',
    '```\n[skip auto-bump]',
  ]) {
    assert.equal(hasSkipDirective(body), false, body);
  }
  assert.equal(hasSkipDirective('```md\nexample\n```\n[skip auto-bump]'), true);
  assert.equal(hasSkipDirective('~~~\nexample\n~~~~\n[skip auto-bump]'), true);
});

test('CLI reads PR text as data and emits only its boolean output', () => {
  const root = mkdtempSync(path.join(tmpdir(), 'auto-bump-directive-'));
  try {
    const event = path.join(root, 'event.json');
    const output = path.join(root, 'output');
    const script = fileURLToPath(new URL('./auto-bump-directive.mjs', import.meta.url));
    for (const [body, expected] of [
      ['Do NOT use [skip auto-bump]; $(exit 99)', false],
      ['[skip auto-bump]', true],
      [null, false],
    ]) {
      writeFileSync(event, JSON.stringify({ pull_request: { body } }));
      writeFileSync(output, '');
      const result = spawnSync(process.execPath, [script], {
        env: { ...process.env, GITHUB_EVENT_PATH: event, GITHUB_OUTPUT: output },
        encoding: 'utf8',
      });
      assert.equal(result.status, 0, result.stderr);
      assert.equal(readFileSync(output, 'utf8'), `skip=${expected}\n`);
    }
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
