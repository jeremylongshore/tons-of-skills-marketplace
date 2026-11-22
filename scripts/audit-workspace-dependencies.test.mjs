import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, symlinkSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { inventory, classify, runInventory } from './audit-workspace-dependencies.mjs';

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'workspace-audit-test-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const put = (path, bytes) => {
    mkdirSync(join(root, path, '..'), { recursive: true });
    writeFileSync(join(root, path), bytes);
  };
  put(
    'package.json',
    JSON.stringify({ name: 'root', version: '1.0.0', scripts: { preinstall: 'must-not-run' } }),
  );
  put('plugins/mcp/example/package.json', JSON.stringify({ name: 'example', version: '1.0.0' }));
  put('pnpm-workspace.yaml', "packages:\n  - 'plugins/mcp/*'\n");
  put('pnpm-lock.yaml', "lockfileVersion: '9.0'\nimporters:\n  .: {}\n  plugins/mcp/example: {}\n");
  return { root, put };
}
const report = (severity) => ({
  advisories: severity
    ? {
        1: {
          severity,
          module_name: 'example',
          findings: [{ paths: ['plugins__mcp__example>example'] }],
        },
      }
    : {},
  metadata: {
    vulnerabilities: {
      info: 0,
      low: 0,
      moderate: 0,
      high: 0,
      critical: 0,
      ...(severity ? { [severity]: 1 } : {}),
    },
  },
});
const result = (value, status = 0) => ({ status, stdout: JSON.stringify(value) });

test('maps actual workspace importers and hashes every original input', (t) => {
  const { root } = fixture(t);
  const value = inventory(root);
  assert.deepEqual(value.packages, ['plugins/mcp/example']);
  assert.equal(value.inputs.size, 4);
  assert.equal(value.lockSha256.length, 64);
  assert.equal(value.manifests.get('package.json').scripts, undefined);
});

test('missing importer and standalone MCP package refuse coverage instead of inferring lock ownership', (t) => {
  const { root, put } = fixture(t);
  put('pnpm-lock.yaml', "lockfileVersion: '9.0'\nimporters:\n  .: {}\n");
  assert.equal(runInventory({ root }).state, 'incomplete');
  put('pnpm-lock.yaml', "lockfileVersion: '9.0'\nimporters:\n  .: {}\n  plugins/mcp/example: {}\n");
  put('pnpm-workspace.yaml', "packages:\n  - 'packages/*'\n");
  put('plugins/mcp/example/package-lock.json', '{}');
  assert.equal(runInventory({ root }).state, 'incomplete');
});

test('missing lock, symlinked manifest and suppression policy fail closed', (t) => {
  const { root, put } = fixture(t);
  rmSync(join(root, 'pnpm-lock.yaml'));
  assert.throws(() => inventory(root), /ENOENT/);
  put('pnpm-lock.yaml', "lockfileVersion: '9.0'\nimporters:\n  .: {}\n  plugins/mcp/example: {}\n");
  put('package.json', JSON.stringify({ pnpm: { auditConfig: { ignoreGhsas: ['ignored'] } } }));
  assert.throws(() => inventory(root), /unsupported_manifest/);
  put('package.json', '{}');
  rmSync(join(root, 'plugins/mcp/example/package.json'));
  symlinkSync(join(root, 'package.json'), join(root, 'plugins/mcp/example/package.json'));
  assert.throws(() => inventory(root), /symlinked_input/);
});

test('classification distinguishes clean, below-threshold and high/critical findings', () => {
  assert.equal(classify(result(report())).state, 'clean');
  assert.equal(classify(result(report('moderate'), 1)).state, 'clean');
  for (const severity of ['high', 'critical'])
    assert.equal(classify(result(report(severity), 1)).state, 'findings');
});

test('tool errors, invalid JSON, absent metrics and inconsistent counts never become clean', () => {
  for (const value of [
    { error: new Error('timeout'), status: null },
    { signal: 'SIGKILL', status: null },
    { status: 2 },
    { status: 0, stdout: 'not json' },
    result({}),
    result({ ...report(), error: 'registry down' }),
    result(report('high')),
    result(report(), 1),
    result({ ...report(), advisories: { 1: { severity: 'high' } } }),
  ])
    assert.equal(classify(value).state, 'incomplete');
  const lie = report();
  lie.metadata.vulnerabilities.high = 1;
  assert.equal(classify(result(lie, 1)).reason, 'audit_count_mismatch');
});

test('scratch execution excludes credentials/config/hooks and retains exact raw result plus coverage', (t) => {
  const { root, put } = fixture(t);
  put('.npmrc', '//evil.test/:_authToken=fixture-not-a-real-token');
  const calls = [];
  const receipt = runInventory({
    root,
    output: join(root, 'out'),
    environment: {
      PATH: '/bin',
      NODE_OPTIONS: '--require evil',
      GITHUB_TOKEN: 'fixture',
      HTTPS_PROXY: 'fixture',
    },
    run(command, args, options) {
      calls.push({ command, args, options });
      assert.equal(command, 'pnpm');
      assert.equal(options.env.GITHUB_TOKEN, undefined);
      assert.equal(options.env.NODE_OPTIONS, undefined);
      assert.equal(options.env.HTTPS_PROXY, undefined);
      assert.equal(readFileSync(options.env.npm_config_userconfig, 'utf8'), '');
      assert.equal(JSON.parse(readFileSync(join(options.cwd, 'package.json'))).scripts, undefined);
      assert.equal(options.timeout, 120000);
      if (args.includes('--version')) return { status: 0, stdout: '9.15.9\n' };
      if (args.includes('install')) {
        assert.ok(args.includes('--offline'));
        assert.ok(args.includes('--ignore-scripts'));
        return { status: 0 };
      }
      assert.ok(args.includes('--prod'));
      assert.ok(args.includes('--audit-level=high'));
      assert.ok(args.includes('--config.fetch-retries=0'));
      return result(report('high'), 1);
    },
  });
  assert.equal(receipt.state, 'findings');
  assert.equal(calls.length, 3);
  assert.equal(
    JSON.parse(readFileSync(join(root, 'out/audit.json'))).metadata.vulnerabilities.high,
    1,
  );
  assert.throws(() => readFileSync(join(calls[0].options.cwd, 'pnpm-lock.yaml')), /ENOENT/);
});

test('stale frozen graph prevents network audit and preserves incomplete receipt', (t) => {
  const { root } = fixture(t);
  let calls = 0;
  const receipt = runInventory({
    root,
    run(_command, args) {
      calls++;
      return args.includes('--version')
        ? { status: 0, stdout: '9.15.9' }
        : { status: 1, stderr: 'private failure detail' };
    },
  });
  assert.equal(receipt.state, 'incomplete');
  assert.equal(receipt.reason, 'lock_coherence_unproven');
  assert.equal(calls, 2);
  assert.ok(!JSON.stringify(receipt).includes('private failure detail'));
});

test('changed original bytes invalidate otherwise successful audit', (t) => {
  const { root, put } = fixture(t);
  const receipt = runInventory({
    root,
    run(_command, args) {
      if (args.includes('--version')) return { status: 0, stdout: '9.15.9' };
      if (args.includes('install')) return { status: 0 };
      put('plugins/mcp/example/package.json', '{"version":"2.0.0"}');
      return result(report());
    },
  });
  assert.equal(receipt.state, 'incomplete');
  assert.equal(receipt.reason, 'source_changed_during_audit');
});

// pnpm9 JSON mode returns nonzero for all severities and enriches paths without
// rewriting registry occurrence counts (installed audit handler/lockfile audit).
test('multiple paths and registry occurrences remain distinct from advisory count', () => {
  const value = report('high');
  value.advisories[1].findings[0].paths.push('other>example');
  value.metadata.vulnerabilities.high = 2;
  const actual = classify(result(value, 1));
  assert.equal(actual.state, 'findings');
  assert.equal(actual.counts.high, 2);
  assert.equal(actual.uniqueAdvisories.high, 1);
});

test('new or removed MCP target invalidates complete coverage after the audit', (t) => {
  for (const change of ['addition', 'removal']) {
    const { root, put } = fixture(t);
    const receipt = runInventory({
      root,
      run(_command, args) {
        if (args.includes('--version')) return { status: 0, stdout: '9.15.9' };
        if (args.includes('install')) return { status: 0 };
        if (change === 'addition') put('plugins/mcp/new/package.json', '{}');
        else rmSync(join(root, 'plugins/mcp/example/package.json'));
        return result(report());
      },
    });
    assert.equal(receipt.state, 'incomplete');
  }
});

test('workspace members outside MCP cannot disappear from the lock coverage denominator', (t) => {
  const { root, put } = fixture(t);
  put('pnpm-workspace.yaml', "packages:\n  - 'plugins/mcp/*'\n  - 'plugins/saas-packs/*-pack'\n");
  put('plugins/saas-packs/new-pack/package.json', '{}');
  const receipt = runInventory({
    root,
    run() {
      assert.fail('must not invoke audit for uncovered member');
    },
  });
  assert.equal(receipt.reason, 'workspace_importers_mismatch');
  assert.ok(receipt.workspaceMembers.includes('plugins/saas-packs/new-pack'));
});

test('unsupported workspace patterns and symlink members refuse rather than reduce coverage', (t) => {
  const { root, put } = fixture(t);
  put('pnpm-workspace.yaml', "packages:\n  - 'plugins/**'\n");
  assert.throws(() => inventory(root), /unsupported_workspace_pattern/);
  put('pnpm-workspace.yaml', "packages:\n  - 'plugins/mcp/*'\n  - '!plugins/mcp/excluded?'\n");
  assert.throws(() => inventory(root), /unsupported_workspace_pattern/);
  put('pnpm-workspace.yaml', "packages:\n  - 'plugins/mcp/*'\n");
  symlinkSync(join(root, 'plugins/mcp/example'), join(root, 'plugins/mcp/linked'));
  assert.throws(() => inventory(root), /symlinked_workspace_member/);
});

test('official pinned pnpm9 response preserves unequal occurrence and unique advisory counts', () => {
  const value = JSON.parse(
    readFileSync(new URL('../tests/fixtures/pnpm-audit/pnpm-9-counts.json', import.meta.url)),
  );
  const actual = classify(result(value, 1));
  assert.equal(actual.state, 'findings');
  assert.equal(actual.counts.moderate, 17);
  assert.equal(actual.uniqueAdvisories.moderate, 15);
  assert.equal(actual.counts.high, 21);
  assert.equal(actual.uniqueAdvisories.high, 20);
});

test('tool refusal retains private bounded diagnostics without exposing stderr in summary', (t) => {
  const { root } = fixture(t);
  const output = join(root, 'evidence');
  const receipt = runInventory({
    root,
    output,
    run(_command, args) {
      if (args.includes('--version')) return { status: 0, stdout: '9.15.9' };
      if (args.includes('install')) return { status: 0, stdout: '' };
      assert.ok(args.includes('--config.fetch-timeout=30000'));
      return {
        status: 1,
        stdout: '',
        stderr: 'parser-refusal-fixture',
        error: { code: 'ETIMEDOUT' },
      };
    },
  });
  assert.equal(receipt.state, 'incomplete');
  assert.ok(!JSON.stringify(receipt).includes('parser-refusal-fixture'));
  const detail = JSON.parse(readFileSync(join(output, 'tool-diagnostics.json')));
  assert.equal(detail[2].stderr, 'parser-refusal-fixture');
  assert.equal(detail[2].errorCode, 'ETIMEDOUT');
  assert.equal(receipt.toolPhases[2].errorCode, 'ETIMEDOUT');
});
