import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { INSTALL_SLUG, bareIntegers, checkContract, handProse } from './check-readme-contract.mjs';

const LIVE = readFileSync(new URL('../README.md', import.meta.url), 'utf-8');

test('the live README satisfies the full landing contract', () => {
  assert.deepEqual(checkContract(LIVE), []);
});

test('R6 red run — removing or normalizing the frozen slug fails', () => {
  const removed = LIVE.replace(INSTALL_SLUG, '/plugin marketplace add somewhere/else');
  assert.ok(checkContract(removed).some((v) => v.startsWith('R6')));
  const normalized = LIVE.replace(
    INSTALL_SLUG,
    '/plugin marketplace add jeremylongshore/claude-code-plugins-plus-skills',
  );
  assert.ok(
    checkContract(normalized).some((v) => v.includes('breaking API change')),
    'canonical-name substitution must be a red run',
  );
});

test('R4 red run — a planted bare count in hand prose fails', () => {
  const planted = LIVE.replace('## Ways in', 'We ship 469 plugins today.\n\n## Ways in');
  const violations = checkContract(planted);
  assert.ok(violations.some((v) => v.includes('R4') && v.includes('469')));
});

test('R4 — generated blocks, code, and link targets are not prose claims', () => {
  const prose = handProse(LIVE);
  assert.deepEqual(bareIntegers(prose), []);
  // the SCALE block's counts exist in the file but not in the stripped prose
  const scaleCount = LIVE.match(/\|\s*([\d,]+)\s*\| marketplace-visible skills/);
  assert.ok(scaleCount, 'the generated SCALE block must carry the marketplace-visible skill count');
  assert.ok(!prose.includes(scaleCount[1]));
});

test('R8 red run — deleting an artifact-class definition fails', () => {
  const gutted = LIVE.replace('**Upstream mirror**', '**Mystery blob**');
  assert.ok(checkContract(gutted).some((v) => v.includes('Upstream mirror')));
});

test('R9 red run — removing a navigation door fails', () => {
  const doorless = LIVE.replaceAll('https://tonsofskills.com/cowork', 'https://example.com/');
  assert.ok(checkContract(doorless).some((v) => v.includes('bundles')));
});

test('R5 red run — naming an adapterless harness as supported fails', () => {
  const oversold = LIVE.replace(
    'Five real questions',
    'Works great on Codex and OpenClaw. Five real questions',
  );
  const violations = checkContract(oversold);
  assert.ok(violations.some((v) => v.includes('Codex')));
  assert.ok(violations.some((v) => v.includes('OpenClaw')));
});

test('R10 red run — README spotlight prose and sentinels cannot return', () => {
  for (const planted of [
    `${LIVE}\n\n## Killer Skill of the Week\n\nA promoted skill.\n`,
    `${LIVE}\n\n<!-- KILLER-SKILL:START -->\nA generated spotlight.\n<!-- KILLER-SKILL:END -->\n`,
  ]) {
    assert.ok(
      checkContract(planted).some((v) => v.startsWith('R10:')),
      'retired README spotlight shape must be a red run',
    );
  }
});
