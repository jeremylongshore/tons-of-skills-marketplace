import { test } from 'node:test';
import assert from 'node:assert/strict';
import { planChecks, checkEnvironment } from './prepush-checks.mjs';

test('checks changed workflows and tests without shell interpolation or mutation', () => {
  const files = new Set(['.github/workflows/a.yml', 'scripts/a.test.mjs']);
  assert.deepEqual(
    planChecks(['.github/workflows/a.yml', 'scripts/a.mjs', 'scripts/a.test.mjs'], (p) =>
      files.has(p),
    ),
    [
      ['actionlint', '.github/workflows/a.yml'],
      ['node', '--test', 'scripts/a.test.mjs'],
    ],
  );
});
test('only affected first-party packages are typechecked; mirrors are preserved', () => {
  const files = new Set(['plugins/mcp/a/package.json', 'plugins/mcp/mirror/.source.json']);
  assert.deepEqual(
    planChecks(
      ['plugins/mcp/a/src/a.ts', 'plugins/mcp/mirror/x.ts'],
      (p) => files.has(p),
      () => JSON.stringify({ scripts: { typecheck: 'tsc --noEmit' } }),
    ),
    [['pnpm', '--filter', './plugins/mcp/a', 'typecheck']],
  );
  assert.deepEqual(planChecks(['README.md']), []);
});

test('hook Git state cannot leak into temporary test repositories', () => {
  const original = {
    PATH: process.env.PATH,
    GIT_DIR: '/wrong/repository',
    GIT_WORK_TREE: '/wrong/tree',
    GIT_INDEX_FILE: '/wrong/index',
    GIT_CONFIG_PARAMETERS: 'unsafe',
    GIT_PREFIX: 'nested/',
  };
  const env = checkEnvironment(original);
  assert.deepEqual(env, { PATH: process.env.PATH });
  assert.equal(original.GIT_DIR, '/wrong/repository');
});
