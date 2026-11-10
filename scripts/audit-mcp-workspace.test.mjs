import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { exitCode, inventory, runInventory } from './audit-mcp-workspace.mjs';

function fixture(t, { importer = true, spec = '^1.0.0', peer = false } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'mcp-inventory-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'plugins/mcp/server'), { recursive: true });
  mkdirSync(join(root, 'plugins/mcp/tracking'), { recursive: true });
  writeFileSync(
    join(root, 'plugins/mcp/server/package.json'),
    JSON.stringify({
      dependencies: { example: '^1.0.0' },
      ...(peer ? { peerDependencies: { peer: '*' } } : {}),
    }),
  );
  writeFileSync(join(root, 'plugins/mcp/tracking/package.json'), '{"private":true}');
  writeFileSync(join(root, 'pnpm-workspace.yaml'), "packages: ['plugins/mcp/*']\n");
  writeFileSync(
    join(root, 'pnpm-lock.yaml'),
    JSON.stringify({
      importers: importer
        ? {
            'plugins/mcp/server': {
              dependencies: { example: { specifier: spec, version: '1.0.0' } },
            },
          }
        : {},
    }),
  );
  return root;
}

const clean = {
  advisories: {},
  metadata: { vulnerabilities: { info: 0, low: 0, moderate: 0, high: 0, critical: 0 } },
};
const response =
  (value, status = 0) =>
  (_command, args = []) =>
    args.includes('install') ? { status: 0 } : { status, stdout: JSON.stringify(value) };

test('shared importer coverage audits once and does not attribute workspace findings to MCP packages', (t) => {
  const root = fixture(t);
  let calls = 0;
  const report = runInventory(root, (command, args, options) => {
    calls++;
    assert.equal(command, 'pnpm');
    if (args.includes('install')) {
      assert.ok(args.includes('--frozen-lockfile'));
      assert.ok(args.includes('--ignore-scripts'));
      return { status: 0 };
    }
    assert.ok(args.includes('--prod'));
    assert.equal(options.cwd, root);
    assert.ok(args.includes('--config.ignore-pnpmfile=true'));
    return response(clean)();
  });
  assert.equal(calls, 2);
  assert.deepEqual(
    report.packages.map((row) => row.status),
    ['shared-workspace-lock', 'no-node-dependencies'],
  );
  assert.match(report.scope, /not attributed/);
  assert.match(report.lock.sha256, /^[a-f0-9]{64}$/);
  assert.equal(exitCode(report), 0);
});

for (const options of [{ importer: false }, { peer: true }]) {
  test(`missing or stale graph cannot pass: ${JSON.stringify(options)}`, (t) => {
    const report = runInventory(fixture(t, options), response(clean));
    assert.equal(report.packages[0].status, 'uncovered');
    assert.equal(exitCode(report), 1);
  });
}

test('high findings stay advisory and are retained', (t) => {
  const report = runInventory(
    fixture(t),
    response(
      {
        metadata: { vulnerabilities: { ...clean.metadata.vulnerabilities, high: 1 } },
        advisories: {
          one: { severity: 'high', module_name: 'example', id: 'GHSA-example', findings: [] },
        },
      },
      1,
    ),
  );
  assert.equal(report.audit.status, 'findings');
  assert.equal(report.audit.findings.length, 1);
  assert.equal(exitCode(report), 0);
});

test('pnpm JSON exit 1 for moderate-only findings does not promote them to blocking', (t) => {
  const report = runInventory(
    fixture(t),
    response(
      {
        metadata: { vulnerabilities: { ...clean.metadata.vulnerabilities, moderate: 1 } },
        advisories: { one: { severity: 'moderate', module_name: 'example', id: 'GHSA-example' } },
      },
      1,
    ),
  );
  assert.equal(report.audit.status, 'below-high-threshold');
  assert.equal(report.audit.counts.moderate, 1);
  assert.equal(exitCode(report), 0);
});

test('partially suppressed advisories cannot pass as complete evidence', (t) => {
  const report = runInventory(
    fixture(t),
    response(
      {
        metadata: { vulnerabilities: { ...clean.metadata.vulnerabilities, high: 2 } },
        advisories: { one: { severity: 'high', module_name: 'example', id: 'GHSA-example' } },
      },
      1,
    ),
  );
  assert.equal(report.audit.status, 'incomplete');
  assert.equal(exitCode(report), 1);
});

for (const result of [
  { status: 0, stdout: '{}' },
  { status: 0, stdout: JSON.stringify({ metadata: clean.metadata }) },
  { status: 0, stdout: JSON.stringify({ ...clean, advisories: 'not-a-map' }) },
  { status: 0, stdout: JSON.stringify({ ...clean, advisories: [] }) },
  {
    status: 1,
    stdout: JSON.stringify({
      advisories: { one: { severity: 'high' } },
      metadata: { vulnerabilities: { ...clean.metadata.vulnerabilities, high: 1 } },
    }),
  },
  { status: 0, stdout: 'invalid' },
  { status: 1, stdout: JSON.stringify(clean) },
  { status: null, error: new Error('timeout'), stdout: JSON.stringify(clean) },
  { status: 0, stdout: JSON.stringify({ ...clean, error: { code: 'ENOLOCK' } }) },
  {
    status: 0,
    stdout: JSON.stringify({
      ...clean,
      metadata: { vulnerabilities: { ...clean.metadata.vulnerabilities, high: 1 } },
    }),
  },
]) {
  test(`incomplete audit fails closed: ${JSON.stringify(result)}`, (t) => {
    const report = runInventory(fixture(t), (_command, args) =>
      args.includes('install') ? { status: 0 } : result,
    );
    assert.equal(report.audit.status, 'incomplete');
    assert.equal(exitCode(report), 1);
  });
}

test('a failed frozen lock check stops before audit', (t) => {
  let calls = 0;
  const report = runInventory(fixture(t, { spec: '^2.0.0' }), () => {
    calls++;
    return { status: 1 };
  });
  assert.equal(calls, 1);
  assert.equal(exitCode(report), 1);
  assert.match(report.audit.reason, /frozen/);
});

test('a lock mutation during frozen validation is not accepted', (t) => {
  const root = fixture(t);
  const report = runInventory(root, () => {
    writeFileSync(join(root, 'pnpm-lock.yaml'), '{}');
    return { status: 0 };
  });
  assert.equal(exitCode(report), 1);
});

test('inventory binds manifest bytes', (t) => {
  const root = fixture(t);
  const before = inventory(root);
  writeFileSync(
    join(root, 'plugins/mcp/tracking/package.json'),
    '{"private":true,"name":"tracking"}',
  );
  assert.notEqual(before.packages[1].manifestSha256, inventory(root).packages[1].manifestSha256);
});
