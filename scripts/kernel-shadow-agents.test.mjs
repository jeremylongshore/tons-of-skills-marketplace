import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  chmodSync,
  copyFileSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import yaml from 'js-yaml';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const valid = {
  name: 'fixture-agent',
  description: 'Use when inspecting a synthetic read-only fixture.',
  tools: [],
  model: 'sonnet',
  color: 'blue',
  version: '1.0.0',
  author: 'Fixture',
  tags: [],
  disallowedTools: [],
  skills: [],
  background: false,
  hooks: {},
  mcpServers: [],
  permissionMode: 'default',
};
const agentPath = '.claude/agents/fixture.md';

function setup(t) {
  const root = mkdtempSync(join(tmpdir(), 'agent-kernel-shadow-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, 'scripts'), { recursive: true });
  symlinkSync(join(ROOT, 'node_modules'), join(root, 'node_modules'), 'dir');
  copyFileSync(join(ROOT, 'package.json'), join(root, 'package.json'));
  for (const name of [
    'kernel-shadow-agents.mjs',
    'kernel-shadow-agents.py',
    'validate-skills-schema.py',
  ]) {
    copyFileSync(join(ROOT, 'scripts', name), join(root, 'scripts', name));
  }
  return root;
}

function put(root, path, content) {
  mkdirSync(dirname(join(root, path)), { recursive: true });
  writeFileSync(join(root, path), content);
}

function agent(root, fm = valid, path = agentPath, body = 'Fixture body.') {
  put(root, path, `---\n${yaml.dump(fm)}---\n${body}\n`);
}

function run(root) {
  const summary = join(root, 'summary.md');
  const result = spawnSync(process.execPath, [join(root, 'scripts/kernel-shadow-agents.mjs')], {
    cwd: root,
    encoding: 'utf8',
    timeout: 30_000,
    env: { ...process.env, GITHUB_STEP_SUMMARY: summary },
  });
  assert.equal(result.error, undefined);
  const report = JSON.parse(
    readFileSync(join(root, 'scripts/.kernel-shadow/agents-report.json'), 'utf8'),
  );
  assert.equal(report.schemaVersion, 'agent-kernel-shadow/v1');
  assert.equal(report.blocking, false);
  assert.match(readFileSync(summary, 'utf8'), /Python\/R1 remain authoritative/);
  return { result, report, summary: readFileSync(summary, 'utf8') };
}

function stub(root, payload, exit = 0) {
  put(
    root,
    '.venv/bin/python3',
    `#!/usr/bin/env node\nconsole.log(${JSON.stringify(typeof payload === 'string' ? payload : JSON.stringify(payload))});\nprocess.exitCode = ${exit};\n`,
  );
  // A test-only interpreter boundary; schemas and the real JS CLI still run.
  chmodSync(join(root, '.venv/bin/python3'), 0o755);
}

function payload() {
  return {
    schema_version: 'agent-python-observation/v1',
    status: 'complete',
    validator_schema_version: 'fixture',
    validator_sha256: 'a'.repeat(64),
    discovered: 1,
    rows: [
      {
        path: agentPath,
        available: true,
        content_sha256: 'b'.repeat(64),
        frontmatter: yaml.dump(valid),
        fatal: null,
        errors: [],
        warnings: [],
      },
    ],
  };
}

test('real Python semver gap is captured by both complete composed schemas', (t) => {
  const root = setup(t);
  agent(root, { ...valid, version: 'not-semver' });
  const { result, report, summary } = run(root);
  assert.equal(result.status, 0);
  assert.equal(report.status, 'complete');
  assert.equal(report.rows[0].python.verdict, 'PASS');
  for (const family of ['authoring/v1', 'authoring/v2']) {
    assert.equal(report.lanes[family].counts.existingPassKernelFail, 1);
    assert.equal(report.lanes[family].schemas.length, 4);
    assert.ok(report.lanes[family].schemas.every((schema) => /^[a-f0-9]{64}$/.test(schema.sha256)));
    assert.ok(
      report.rows[0].kernels[family].errors.some(
        (error) => error.instancePath === '/version' && error.keyword === 'pattern',
      ),
    );
  }
  assert.match(summary, /authoring\/v2: Python-PASS\/kernel-FAIL \*\*1\*\*/);
});

test('v2 array/string disagreement is visible without coercing Python or input', (t) => {
  const root = setup(t);
  agent(root);
  const { result, report } = run(root);
  assert.equal(result.status, 0);
  assert.equal(report.rows[0].python.verdict, 'PASS');
  assert.equal(report.rows[0].kernels['authoring/v1'].verdict, 'PASS');
  assert.ok(
    report.rows[0].kernels['authoring/v2'].errors.some(
      (error) => error.instancePath === '/disallowedTools' && error.keyword === 'type',
    ),
  );
  assert.equal(report.lanes['authoring/v2'].counts.existingPassKernelFail, 1);
});

for (const [label, change, expectedPath] of [
  ['base color enum', { color: 'invisible' }, '/color'],
  ['overlay author minimum', { author: '' }, '/author'],
  ['universal security fold', { name: 'claude' }, '/name'],
  ['universal deprecation fold', { when_to_use: 'old field' }, ''],
  ['universal disclosure fold', { description: 'x'.repeat(1600) }, '/description'],
]) {
  test(`composed validation executes ${label}`, (t) => {
    const root = setup(t);
    agent(root, { ...valid, ...change });
    const { report } = run(root);
    for (const family of ['authoring/v1', 'authoring/v2']) {
      assert.equal(report.rows[0].kernels[family].verdict, 'FAIL');
      assert.ok(
        report.rows[0].kernels[family].errors.some((error) => error.instancePath === expectedPath),
      );
      if (label.startsWith('universal')) {
        assert.ok(
          report.rows[0].kernels[family].errors.some((error) =>
            error.schemaPath.includes(`/$defs/${label.split(' ')[1]}`),
          ),
        );
      }
    }
  });
}

test('canonical discovery includes three surfaces and fatal files but excludes build trees', (t) => {
  const root = setup(t);
  agent(root);
  agent(root, valid, 'plugins/example/agents/plugin.md');
  agent(root, valid, 'workspace/lab/agents/lab.md');
  agent(root, valid, 'plugins/example/node_modules/pkg/agents/excluded.md');
  put(root, 'plugins/example/agents/README.md', 'No frontmatter.');
  const { result, report } = run(root);
  assert.equal(result.status, 0);
  assert.equal(report.inventory.discovered, 4);
  assert.equal(report.rows.find((row) => row.path.endsWith('README.md')).python.verdict, 'FATAL');
  assert.equal(report.lanes['authoring/v1'].counts.parseFailures, 1);
  assert.match(report.inventory.sha256, /^[a-f0-9]{64}$/);
});

test('warnings pass; body-only Python failures remain explicitly raw scope comparisons', (t) => {
  const root = setup(t);
  agent(root, { ...valid, extraFixture: true });
  agent(root, valid, '.claude/agents/body.md', 'Call mcp__fixture__run now.');
  const { report, summary } = run(root);
  const warning = report.rows.find((row) => row.path === agentPath);
  assert.equal(warning.python.verdict, 'PASS');
  assert.ok(warning.python.warnings.length);
  const body = report.rows.find((row) => row.path.endsWith('body.md'));
  assert.equal(body.python.verdict, 'FAIL');
  assert.ok(body.python.errors.every((error) => error.startsWith('[agent] body')));
  assert.equal(body.kernels['authoring/v1'].verdict, 'PASS');
  assert.equal(report.lanes['authoring/v1'].counts.existingFailKernelPass, 1);
  assert.match(summary, /RAW verdict comparisons/);
  assert.match(summary, /may be a scope difference/);
  assert.equal(report.frontmatterAgreement, undefined);
});

test('malformed YAML is a retained fatal and kernel parse failure', (t) => {
  const root = setup(t);
  put(root, agentPath, '---\nname: [\n---\nBody.\n');
  const { result, report } = run(root);
  assert.equal(result.status, 0);
  assert.equal(report.rows[0].python.verdict, 'FATAL');
  assert.equal(report.lanes['authoring/v1'].counts.parseFailures, 1);
});

test('non-mapping YAML that crashes canonical Python is partial, never silently skipped', (t) => {
  const root = setup(t);
  agent(root, ['unexpected']);
  const { result, report } = run(root);
  assert.equal(result.status, 1);
  assert.equal(report.status, 'partial');
  assert.equal(report.inventory.discovered, 1);
  assert.equal(report.rows[0].python.verdict, 'UNAVAILABLE');
  assert.match(report.rows[0].python.reason, /AttributeError/);
  assert.equal(report.lanes['authoring/v2'].counts.unavailable, 1);
});

for (const [label, edit] of [
  [
    'empty inventory',
    (p) => {
      p.rows = [];
      p.discovered = 0;
    },
  ],
  [
    'duplicate rows',
    (p) => {
      p.rows.push(p.rows[0]);
      p.discovered = 2;
    },
  ],
  [
    'missing row',
    (p) => {
      p.discovered = 2;
    },
  ],
  [
    'missing verdict',
    (p) => {
      delete p.rows[0].errors;
    },
  ],
  [
    'escaping path',
    (p) => {
      p.rows[0].path = '../outside.md';
    },
  ],
  [
    'absolute path',
    (p) => {
      p.rows[0].path = '/outside.md';
    },
  ],
  [
    'false complete',
    (p) => {
      p.rows[0] = { path: agentPath, available: false, reason: 'unreadable' };
    },
  ],
]) {
  test(`${label} cannot report clean or complete evidence`, (t) => {
    const root = setup(t);
    const p = payload();
    edit(p);
    stub(root, p);
    const { result, report } = run(root);
    assert.equal(result.status, 1);
    assert.equal(report.status, 'unavailable');
    assert.ok(report.harnessErrors.length);
  });
}

for (const [label, value, exit] of [
  ['invalid JSON', 'not JSON', 0],
  ['failed process with plausible output', payload(), 1],
]) {
  test(`${label} cannot become clean evidence`, (t) => {
    const root = setup(t);
    stub(root, value, exit);
    const { result, report } = run(root);
    assert.equal(result.status, 1);
    assert.equal(report.status, 'unavailable');
  });
}

test('declared kernel pin drift is unavailable, not a different contract silently', (t) => {
  const root = setup(t);
  agent(root);
  const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  pkg.devDependencies['@intentsolutions/core'] = '^0.10.0';
  put(root, 'package.json', JSON.stringify(pkg));
  const { result, report } = run(root);
  assert.equal(result.status, 1);
  assert.match(report.harnessErrors[0], /kernel pin drift/);
});

test('missing composed-schema dependencies cannot fall back to inline rules', (t) => {
  const root = setup(t);
  agent(root);
  // Replace only this fixture's dependency symlink, never the real installation.
  rmSync(join(root, 'node_modules'));
  for (const name of ['ajv', 'ajv-formats', 'js-yaml']) {
    mkdirSync(join(root, 'node_modules'), { recursive: true });
    symlinkSync(join(ROOT, 'node_modules', name), join(root, 'node_modules', name), 'dir');
  }
  put(root, 'node_modules/@intentsolutions/core/package.json', '{"version":"0.10.0"}');
  const { result, report } = run(root);
  assert.equal(result.status, 1);
  assert.equal(report.status, 'unavailable');
  assert.match(report.harnessErrors[0], /ENOENT/);
});

test('unreadable discovered file is retained as partial evidence', (t) => {
  const root = setup(t);
  put(
    root,
    'scripts/validate-skills-schema.py',
    `
SCHEMA_VERSION = 'fixture'
def find_agent_files(root):
    return [root / '.claude/agents/disappeared.md']
`,
  );
  const { result, report } = run(root);
  assert.equal(result.status, 1);
  assert.equal(report.status, 'partial');
  assert.equal(report.rows[0].path, '.claude/agents/disappeared.md');
  assert.match(report.rows[0].python.reason, /FileNotFoundError/);
});

test('missing Python adapter writes unavailable evidence rather than leaving a stale report', (t) => {
  const root = setup(t);
  put(root, 'scripts/.kernel-shadow/agents-report.json', '{"status":"complete"}');
  rmSync(join(root, 'scripts/kernel-shadow-agents.py'));
  const { result, report } = run(root);
  assert.equal(result.status, 1);
  assert.equal(report.status, 'unavailable');
  assert.match(report.harnessErrors[0], /ENOENT/);
});

test('non-mapping YAML is a kernel parse failure even if a Python transport says PASS', (t) => {
  const root = setup(t);
  const p = payload();
  p.rows[0].frontmatter = '- unexpected';
  stub(root, p);
  const { result, report } = run(root);
  assert.equal(result.status, 0);
  assert.equal(report.lanes['authoring/v1'].counts.parseFailures, 1);
  assert.equal(report.lanes['authoring/v1'].counts.existingPassKernelFail, 1);
  assert.match(report.rows[0].kernels['authoring/v1'].parseError, /not a mapping/);
});

test('agent workflow remains advisory and uploads the separate real-corpus report', () => {
  const workflow = yaml.load(
    readFileSync(join(ROOT, '.github/workflows/kernel-shadow-validation.yml'), 'utf8'),
  );
  const steps = workflow.jobs['kernel-shadow'].steps;
  for (const command of [
    'node --test scripts/kernel-shadow-agents.test.mjs',
    'node scripts/kernel-shadow-agents.mjs',
  ]) {
    assert.equal(steps.find((step) => step.run === command)?.['continue-on-error'], true);
  }
  const artifact = steps.find((step) => step.uses?.startsWith('actions/upload-artifact@'));
  assert.equal(artifact.if, 'always()');
  assert.ok(artifact.with.path.includes('scripts/.kernel-shadow/agents-report.json'));
  for (const pattern of [
    'plugins/**/agents/**/*.md',
    '.claude/agents/**/*.md',
    'workspace/**/agents/**/*.md',
  ]) {
    assert.ok(workflow.on.pull_request.paths.includes(pattern));
  }
  assert.deepEqual(workflow.permissions, { contents: 'read' });
});
