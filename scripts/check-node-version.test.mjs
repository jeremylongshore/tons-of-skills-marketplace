import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  assertSupportedNodeVersion,
  isSupportedNodeVersion,
  MIN_NODE_VERSION,
} from './check-node-version.mjs';

const repoRoot = join(fileURLToPath(new URL('.', import.meta.url)), '..');

test('accepts the repository minimum and newer Node releases', () => {
  assert.equal(isSupportedNodeVersion(MIN_NODE_VERSION), true);
  assert.equal(isSupportedNodeVersion('22.12.1'), true);
  assert.equal(isSupportedNodeVersion('23.0.0'), true);
});

test('rejects Node versions below the repository minimum', () => {
  assert.equal(isSupportedNodeVersion('22.11.9'), false);
  assert.equal(isSupportedNodeVersion('20.20.2'), false);
  assert.equal(isSupportedNodeVersion('not-a-version'), false);
  assert.equal(isSupportedNodeVersion('22.12.0foo'), false);
  assert.equal(isSupportedNodeVersion('22.12.0-rc.1'), false);
  assert.equal(isSupportedNodeVersion('22.12.0/evil'), false);
});

test('reports an actionable failure for an unsupported runtime', () => {
  assert.throws(
    () => assertSupportedNodeVersion('20.20.2'),
    /Node\.js 20\.20\.2 is not supported.*require Node\.js >= 22\.12\.0.*\.node-version/,
  );
});

test('the preflight uses the current process runtime by default', () => {
  assert.doesNotThrow(() => assertSupportedNodeVersion(process.versions.node, MIN_NODE_VERSION));
});

test('the direct marketplace build invokes the same preflight', () => {
  const rootPackage = JSON.parse(readFileSync(join(repoRoot, 'package.json'), 'utf8'));
  const marketplacePackage = JSON.parse(
    readFileSync(join(repoRoot, 'marketplace', 'package.json'), 'utf8'),
  );
  const versionFile = readFileSync(join(repoRoot, '.node-version'), 'utf8').trim();

  assert.equal(versionFile, MIN_NODE_VERSION);
  assert.equal(rootPackage.engines.node, `>=${MIN_NODE_VERSION}`);
  assert.equal(marketplacePackage.scripts.prebuild, 'node ../scripts/check-node-version.mjs');
  assert.match(marketplacePackage.scripts.predev, /^node \.\.\/scripts\/check-node-version\.mjs/);
  assert.equal(marketplacePackage.engines.node, `>=${MIN_NODE_VERSION}`);
});

test('full-repository workflows invoke the runtime preflight explicitly', () => {
  const workflowExpectations = new Map([
    ['e2e-tests.yml', 2],
    ['release.yml', 1],
    ['skill-conform.yml', 1],
  ]);

  for (const [workflow, expectedCount] of workflowExpectations) {
    const source = readFileSync(join(repoRoot, '.github', 'workflows', workflow), 'utf8');
    const matches = source.match(/run: node scripts\/check-node-version\.mjs/g) ?? [];
    assert.equal(matches.length, expectedCount, `${workflow} explicit preflight count`);
  }
});
