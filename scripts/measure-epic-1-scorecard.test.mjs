import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';

// Run the pure-reader regressions through the existing measurement test lane.
import './ci-correctness-swallows.test.mjs';

import { DEAD_DOMAIN } from './dead-domain-policy.mjs';
import { buildExtendedScorecardRows } from './measure-epic-1-scorecard.mjs';
import { inspectFreshieHermeticTest } from './measure-epic-1.mjs';

const EXPECTED_ROWS = [
  5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
  57, 58, 59, 60, 61, 62,
];

function put(root, path, value = '') {
  const target = join(root, path);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, value);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 'epic-1-scorecard-'));
  t.after(() => rmSync(root, { force: true, recursive: true }));
  const doltCommit = 'a'.repeat(32);
  const gradesCsv = 'skill_path,grade,score\none,A,90\ntwo,B,80\n';
  const gradesHash = createHash('sha256').update(gradesCsv).digest('hex');
  const forgeRecords = [2, 4, 5].map((jrig_run_id) => ({
    plugin_name: 'databricks-pack',
    jrig_run_id,
    discovery_run_id: null,
    evidence_class: 'E0',
    artifact_uri: null,
    artifact_sha256: null,
    baseline_delta: null,
  }));
  const forgeHash = createHash('sha256').update(canonicalJson(forgeRecords)).digest('hex');
  const files = {
    '.github/dependabot.yml': 'version: 2\nupdates: []\n',
    '.github/workflows/publish-changed-packages.yml': `on:\n  workflow_run:\n    workflows: ['Validate Plugins']\njobs:\n  preflight:\n    steps:\n      - run: node scripts/npm-publication-preflight.mjs\n  publish:\n    environment: npm-production\n    steps:\n      - run: node scripts/publish-candidate-report.mjs && npm publish\n`,
    '.github/workflows/emit-evidence.yml': `permissions:\n  id-token: write\njobs:\n  sign:\n    steps:\n      - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803\n`,
    '.github/workflows/kernel-vendor-hash.yml': `jobs:\n  kernel-vendor-hash:\n    steps:\n      - name: Version-ordering invariant test corpus (blocking)\n        run: node --test scripts/kernel-vendor-hash.test.mjs\n      - name: Alert Slack on kernel coupling violation\n        if: steps.vendor-hash.outputs.violation == 'true'\n        run: curl --fail "$WEBHOOK"\n`,
    '.github/workflows/validate-plugins.yml': `on:\n  pull_request:\n  push:\n    branches: [main]\njobs:\n  validate:\n    steps:\n      - run: python3 scripts/validate-skills-schema.py --marketplace\n      - run: python3 -m unittest tests.test_prose_anchors\n  test:\n    needs: validate\n    strategy:\n      matrix:\n        test-type: [mcp-plugins, python-tests, validation-scripts]\n    steps:\n      - name: Install pinned Dolt for Freshie integration tests\n        if: matrix.test-type == 'python-tests'\n        run: |\n          readonly dolt_version='2.3.1'\n          readonly dolt_sha256='0a2a318f27c5e1088a2883038573c2054e00f356dc9752e74bca934f8321959a'\n          printf '%s  %s\\n' "$dolt_sha256" dolt.tar.gz | sha256sum --check --strict\n          sudo install -m 0755 dolt /usr/local/bin/dolt\n          dolt version\n      - name: Run Freshie hermetic publication cycle\n        if: matrix.test-type == 'python-tests'\n        run: python3 -m unittest tests.test_freshie_hermetic_cycle -v\n  ci-required:\n    needs:\n      - validate\n      - test\n`,
    '.gitleaks.toml': "[allowlist]\npaths = ['''(?i).*/README\\.md$''']\nregexes = []\n",
    '.claude-plugin/marketplace.extended.json': JSON.stringify({
      plugins: [
        { name: 'example', source: './plugins/example' },
        { name: 'local', source: './plugins/local' },
      ],
    }),
    '000-docs/000-INDEX.md': '- [canonical.md](canonical.md)\n',
    '000-docs/canonical.md': '# Canonical\n\n**Status:** AUTHORITATIVE\n',
    'CLAUDE.md': 'Validator (schema 4.0.0 — governed)\n',
    'STANDARDS.md':
      '## Canonical documents\n\n| Topic | Document |\n| --- | --- |\n| Fixture | [canonical](000-docs/canonical.md) |\n',
    '000-docs/807-DR-STND-evaluation-evidence.md': '# Evidence standard\n',
    '000-docs/810-RA-DATA-epic-9-boundary-evidence.json': JSON.stringify({
      package_registry: {
        packages: {
          '@intentsolutions/audit-harness': { version: '1.0.0' },
          '@intentsolutions/core': { version: '1.0.0' },
          '@intentsolutions/jrig-cli': { version: '1.0.0' },
        },
        resolved_core_versions: ['1.0.0'],
      },
      kernel_shadow: {
        kernel_version: '1.0.0',
        kernel_pin: '1.0.0',
        lanes: {
          'authoring/v1': { frontmatter_agree: 2, frontmatter_disagree: 0 },
          'authoring/v2': {
            decision_relevant_metric: 'existing-PASS / kernel-FAIL',
            existing_pass_kernel_fail: 0,
          },
        },
      },
    }),
    'freshie/grade-histogram.json': JSON.stringify({
      run_id: 9,
      total: 2,
      grades: { A: 1, B: 1 },
      dolt_commit: doltCommit,
      grades_csv_sha256: gradesHash,
    }),
    'freshie/grades.csv': gradesCsv,
    'freshie/reports/legacy-forge-proofs-demotion.json': JSON.stringify({
      schema_version: 'forge-proof-demotion/v2',
      source_run_id: 9,
      source_tag: 'run-9',
      source_dolt_commit: doltCommit,
      records_sha256: forgeHash,
      records: forgeRecords,
    }),
    'freshie/reports/run-delta-9.json': JSON.stringify({
      schema_version: 'freshie-run-delta/v3',
      run_id: 9,
      from_tag: 'run-8',
      to_tag: 'run-9',
      dolt_commit: doltCommit,
      run_coherence: {
        discovery_run_id: 9,
        header_total_skills: 2,
        skill_rows: 2,
        skill_row_delta: 0,
        skill_compliance_rows: 2,
      },
      grade_export: {
        row_count: 2,
        csv_sha256: gradesHash,
        grade_counts: { A: 1, B: 1 },
      },
      forge_proofs: {
        row_count: 3,
        records_sha256: forgeHash,
        class_counts: { E0: 3, E1: 0, E2: 0, E3: 0 },
        retained_e2_e3: 0,
        total_e2_e3: 0,
        records: forgeRecords,
      },
    }),
    'freshie/scripts/dolt-sync.py':
      'def acquire_lock():\n fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\ndef refuse_if_server_running():\n return ".dolt/sql-server.lock"\n',
    'marketplace/scripts/generate-alpha.mjs':
      "writeFileSync('marketplace/src/data/alpha.json', '{}')\n",
    'marketplace/src/data/alpha.json': '{}',
    'package.json': JSON.stringify({
      devDependencies: {
        '@intentsolutions/audit-harness': '1.0.0',
        '@intentsolutions/core': '1.0.0',
        '@intentsolutions/jrig-cli': '1.0.0',
      },
    }),
    'plugins/example/.source.json': JSON.stringify({
      synced_from: { repo: 'owner/repo', path: '/' },
    }),
    'plugins/example/LICENSE': 'fixture license\n',
    'plugins/example/package.json': JSON.stringify({ name: '@scope/example', private: true }),
    'plugins/example/skills/one/SKILL.md': `---\nname: one\nallowed-tools: Read\ncompatibility: Harness A\n---\nhttps://docs.anthropic.com\n`,
    'plugins/local/skills/two/SKILL.md': `---\nname: two\nallowed-tools: >-\n  Read Write\ncompatibility: Harness B\n---\n${DEAD_DOMAIN}\n`,
    'scripts/npm-publication-preflight.mjs': 'export const required = true;\n',
    'scripts/record-jrig-proofs.mjs': 'export const evidence = true;\n',
    'scripts/plugin-provenance.mjs':
      "export const SOURCE_FILE = '.source.json';\nexport function resolvePluginProvenance() {}\n",
    'scripts/publish-candidate-report.mjs':
      "import { resolvePluginProvenance } from './plugin-provenance.mjs';\nexport const report = resolvePluginProvenance;\n",
    'scripts/readme-metrics.mjs':
      "const catalog = '.claude-plugin/marketplace.extended.json'; const skillCount = 1; const agentCount = 1; writeFileSync('README.md', String(catalog) + skillCount + agentCount);\n",
    'scripts/validate-skills-schema.py': 'SCHEMA_VERSION = "4.0.0"\n',
    'sources.lock.json': JSON.stringify({ sources: { example: {} } }),
    'sources.yaml': 'sources:\n  - name: example\n',
    'tests/test_dolt_sync.py': 'def test_single_writer_lock():\n pass\n',
    'tests/test_freshie_hermetic_cycle.py': readFileSync(
      new URL('../tests/test_freshie_hermetic_cycle.py', import.meta.url),
      'utf8',
    ),
  };
  const workflowPath = '.github/workflows/validate-plugins.yml';
  files[workflowPath] = files[workflowPath].replace(
    `          printf '%s  %s\\n' "$dolt_sha256" dolt.tar.gz | sha256sum --check --strict
          sudo install -m 0755 dolt /usr/local/bin/dolt
          dolt version`,
    `          readonly dolt_archive="/tmp/dolt-linux-amd64-v\${dolt_version}.tar.gz"
          readonly dolt_extract="/tmp/dolt-extract"
          printf '%s  %s\\n' "$dolt_sha256" "$dolt_archive" | sha256sum --check --strict
          tar -xzf "$dolt_archive" -C "$dolt_extract"
          sudo install -m 0755 "$dolt_extract/dolt-linux-amd64/bin/dolt" /usr/local/bin/dolt
          installed_dolt_version="$(dolt version | awk 'NR == 1 { print $3 }')"
          readonly installed_dolt_version
          test "$installed_dolt_version" = "$dolt_version"`,
  );
  files[workflowPath] = files[workflowPath].replace(
    '        run: python3 -m unittest tests.test_freshie_hermetic_cycle -v',
    `        run: |
          python3 - <<'PY'
          import unittest
          from tests.test_freshie_hermetic_cycle import HermeticFreshieCycleTests

          method_name = "test_full_cycle_uses_only_scratch_state_and_refuses_live_server"
          original_method = HermeticFreshieCycleTests.__dict__[method_name]
          invocations = []

          def guarded_method(self):
              invocations.append(1)
              return original_method(self)

          setattr(HermeticFreshieCycleTests, method_name, guarded_method)
          suite = unittest.TestSuite([HermeticFreshieCycleTests(method_name)])
          result = unittest.TextTestRunner(verbosity=2).run(suite)
          valid = (
              result.wasSuccessful()
              and result.testsRun == 1
              and not result.skipped
              and not result.expectedFailures
              and not result.unexpectedSuccesses
              and len(invocations) == 1
              and HermeticFreshieCycleTests.__dict__.get(method_name) is guarded_method
          )
          raise SystemExit(0 if valid else 1)
          PY`,
  );
  for (const [path, value] of Object.entries(files)) put(root, path, value);
  return { root, paths: Object.keys(files).sort() };
}

function input(fixtureValue) {
  return {
    ...fixtureValue,
    agentSummary: { agents: 1, compliance_percent: 100, errors: 0 },
    hermeticTestContract: inspectFreshieHermeticTest(fixtureValue.root),
    marketplaceSummary: { errors: 1 },
    skillRows: [
      {
        errors: 1,
        grade: 'A',
        path: 'plugins/example/skills/one/SKILL.md',
        score: 90,
      },
      {
        errors: 0,
        grade: 'B',
        path: 'plugins/local/skills/two/SKILL.md',
        score: 80,
      },
    ],
    skillSummary: { rows: 2 },
  };
}

test('emits the exact extended numbered row set in deterministic order and shape', (t) => {
  const rows = buildExtendedScorecardRows(input(fixture(t)));
  assert.deepEqual(Object.keys(rows).map(Number), EXPECTED_ROWS);
  for (const number of EXPECTED_ROWS) {
    assert.deepEqual(Object.keys(rows[number]).slice(0, 6), [
      'status',
      'cohort',
      'dimension',
      'reproduce',
      'source',
      'values',
    ]);
    assert.equal(rows[number].reproduce, `pnpm run measure:e1 --row=${number} --stdout`);
  }
  const again = buildExtendedScorecardRows(input(fixture(t)));
  const firstWithoutRootSpecificData = JSON.stringify(rows);
  assert.equal(JSON.stringify(again), firstWithoutRootSpecificData);
});

test('discovers additional generated artifacts and README count writers dynamically', (t) => {
  const base = fixture(t);
  let rows = buildExtendedScorecardRows(input(base));
  assert.deepEqual(
    rows[22].values.artifacts.map((entry) => entry.path),
    ['marketplace/src/data/alpha.json'],
  );
  assert.deepEqual(rows[25].values.writers, ['scripts/readme-metrics.mjs']);

  put(
    base.root,
    'scripts/generate-third.mjs',
    "const catalog = 'marketplace.extended.json'; const skillCount = 3; const agents = 1; writeFileSync('marketplace/src/data/third.json', '{}'); writeFileSync('README.md', String(catalog) + skillCount + agents);\n",
  );
  put(base.root, 'marketplace/src/data/third.json', '{}');
  base.paths.push('marketplace/src/data/third.json', 'scripts/generate-third.mjs');
  rows = buildExtendedScorecardRows(input(base));
  assert.deepEqual(
    rows[22].values.artifacts.map((entry) => entry.path),
    ['marketplace/src/data/alpha.json', 'marketplace/src/data/third.json'],
  );
  assert.deepEqual(rows[25].values.writers, [
    'scripts/generate-third.mjs',
    'scripts/readme-metrics.mjs',
  ]);
});

test('requires call-bound production evidence and excludes measurement instrumentation', (t) => {
  const base = fixture(t);
  put(
    base.root,
    'scripts/measure-epic-1-scorecard.mjs',
    "const totalSkills = 99; const agents = 99; const catalog = 'marketplace.extended.json'; writeFileSync('README.md', 'alpha.json');\n",
  );
  put(
    base.root,
    'scripts/unrelated-writer.mjs',
    "const mentioned = 'alpha.json'; writeFileSync('README.md', mentioned);\n",
  );
  put(
    base.root,
    'packages/example/readme-writer.test.mjs',
    "const catalog = 'marketplace.extended.json'; const skills = 1; const agents = 1; writeFileSync('README.md', String(catalog) + skills + agents);\n",
  );
  put(base.root, 'plugins/mirrored/.source.json', '{"source":"upstream"}\n');
  put(
    base.root,
    'plugins/mirrored/readme-writer.mjs',
    "const catalog = 'marketplace.extended.json'; const skills = 1; const agents = 1; writeFileSync('README.md', String(catalog) + skills + agents);\n",
  );
  base.paths.push(
    'packages/example/readme-writer.test.mjs',
    'plugins/mirrored/.source.json',
    'plugins/mirrored/readme-writer.mjs',
    'scripts/measure-epic-1-scorecard.mjs',
    'scripts/unrelated-writer.mjs',
  );

  const rows = buildExtendedScorecardRows(input(base));
  assert.deepEqual(rows[22].values.artifacts[0].producers, [
    'marketplace/scripts/generate-alpha.mjs',
  ]);
  assert.deepEqual(rows[25].values.writers, ['scripts/readme-metrics.mjs']);
});

test('writer discovery matches exact basenames instead of catalog suffixes', (t) => {
  const base = fixture(t);
  put(base.root, 'marketplace/src/data/catalog.json', '{}');
  put(base.root, 'marketplace/src/data/skills-catalog.json', '{}');
  put(
    base.root,
    'marketplace/scripts/generate-skills-catalog.mjs',
    "const output = 'marketplace/src/data/skills-catalog.json'; writeFileSync(output, '{}');\n",
  );
  base.paths.push(
    'marketplace/src/data/catalog.json',
    'marketplace/src/data/skills-catalog.json',
    'marketplace/scripts/generate-skills-catalog.mjs',
  );

  const artifacts = buildExtendedScorecardRows(input(base))[22].values.artifacts;
  assert.equal(
    artifacts.some((entry) => entry.path === 'marketplace/src/data/catalog.json'),
    false,
  );
  assert.deepEqual(
    artifacts.find((entry) => entry.path === 'marketplace/src/data/skills-catalog.json')?.producers,
    ['marketplace/scripts/generate-skills-catalog.mjs'],
  );
});

test('counts only producer-integrated workflow checks as artifact drift gates', (t) => {
  const base = fixture(t);
  put(
    base.root,
    'scripts/consumer-check.mjs',
    "const input = 'alpha.json'; const check = process.argv.includes('--check'); console.log(input, check, 'drift');\n",
  );
  put(
    base.root,
    '.github/workflows/consumer-check.yml',
    'jobs:\n  check:\n    steps:\n      - run: node scripts/consumer-check.mjs --check\n',
  );
  base.paths.push('scripts/consumer-check.mjs', '.github/workflows/consumer-check.yml');
  let row = buildExtendedScorecardRows(input(base))[22];
  let artifact = row.values.artifacts[0];
  assert.equal(artifact.content_drift_gate, false);
  assert.deepEqual(artifact.wired_checkers, []);
  assert.equal(row.status, 'partial');

  put(
    base.root,
    'marketplace/scripts/generate-alpha.mjs',
    "const target = 'marketplace/src/data/alpha.json'; const check = process.argv.includes('--check'); const current = readFileSync(target, 'utf8'); const rendered = '{}'; if (check && current !== rendered) process.exit(1); writeFileSync(target, rendered);\n",
  );
  put(
    base.root,
    '.github/workflows/alpha-check.yml',
    'jobs:\n  check:\n    steps:\n      - run: node marketplace/scripts/generate-alpha.mjs --check\n',
  );
  base.paths.push('.github/workflows/alpha-check.yml');
  row = buildExtendedScorecardRows(input(base))[22];
  artifact = row.values.artifacts[0];
  assert.equal(artifact.content_drift_gate, true);
  assert.deepEqual(artifact.wired_checkers, ['marketplace/scripts/generate-alpha.mjs']);
  assert.equal(row.status, 'measured');
});

test('normalizes absolute validator paths into the tracked Git cohort', (t) => {
  const base = fixture(t);
  const values = input(base);
  values.skillRows = values.skillRows.map((entry) => ({
    ...entry,
    path: join(base.root, entry.path),
  }));
  const row = buildExtendedScorecardRows(values)[5];
  assert.equal(row.values.rows, 2);
  assert.deepEqual(row.values.grade_distribution, { A: 1, B: 1, C: 0, D: 0, F: 0 });
});

test('measures the merged provenance boundary, ci-required needs, and STANDARDS authority table', (t) => {
  const base = fixture(t);
  put(
    base.root,
    '.github/workflows/cli-publish.yml',
    "jobs:\n  publish:\n    environment: npm-production\n    steps:\n      - run: node scripts/npm-publication-preflight.mjs && npm publish\n        working-directory: packages/cli\n      - run: echo '@claude-code-plugins/ccp https://github.com/example/claude-code-plugins/tree/main/packages/cli'\n",
  );
  base.paths.push('.github/workflows/cli-publish.yml');
  const rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[31].values.publisher_provenance_boundary, true);
  assert.deepEqual(rows[31].values.mirror_capable_publishers, [
    '.github/workflows/publish-changed-packages.yml',
  ]);
  assert.deepEqual(rows[41].values.actual_needs, ['validate', 'test']);
  assert.equal(rows[43].values.declared, 1);
  assert.deepEqual(rows[43].values.authority_links, ['000-docs/canonical.md']);
});

test('fails closed on malformed ci-required needs', (t) => {
  const base = fixture(t);
  put(
    base.root,
    '.github/workflows/validate-plugins.yml',
    'jobs:\n  ci-required:\n    needs: [validate, validate]\n',
  );
  const row = buildExtendedScorecardRows(input(base))[41];
  assert.equal(row.status, 'undefined');
  assert.equal(row.values, null);
  assert.equal(row.reason_code, 'MALFORMED_CI_REQUIRED_NEEDS');
});

test('link instrumentation stays excluded while domain instrumentation cannot bypass policy', (t) => {
  const base = fixture(t);
  put(
    base.root,
    '000-docs/742-RA-DATA-epic-1-scorecard.json',
    JSON.stringify({ dimensions: ['docs.anthropic.com', DEAD_DOMAIN] }),
  );
  put(
    base.root,
    'scripts/measure-epic-1-scorecard.test.mjs',
    `const fixtures = ['docs.anthropic.com', '${DEAD_DOMAIN}'];\n`,
  );
  base.paths.push(
    '000-docs/742-RA-DATA-epic-1-scorecard.json',
    'scripts/measure-epic-1-scorecard.test.mjs',
  );
  const rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[20].measured_proxy.occurrences, 1);
  assert.equal(rows[21].values.actionable.occurrences, 3);
  assert.equal(
    rows[21].values.baseline_receipt.head_sha,
    '3543d5d167bd4e8d27666c8893080bca3bd72950',
  );
  assert.deepEqual(rows[21].values.baseline_receipt.counts.actionable, {
    files: 114,
    occurrences: 292,
  });
  assert.deepEqual(rows[21].values.baseline_receipt.counts.retained, {
    files: 11,
    occurrences: 64,
  });
  assert.deepEqual(rows[21].values.baseline_receipt.counts.frozen_record, {
    files: 2,
    occurrences: 4,
  });
  assert.equal(rows[20].source.includes('scripts/measure-epic-1-scorecard.test.mjs'), false);
  assert.equal(rows[21].source.includes('scripts/measure-epic-1-scorecard.test.mjs'), true);
});

test('unresolved rows fail closed with null values rather than fabricated zeroes', (t) => {
  const rows = buildExtendedScorecardRows(input(fixture(t)));
  for (const number of [7, 8, 9, 15, 16, 17, 18, 19, 23, 29, 49, 50, 51, 60, 61, 62]) {
    assert.equal(rows[number].values, null, `row ${number}`);
    assert.match(rows[number].reason_code, /^[A-Z][A-Z0-9_]+$/);
    assert.ok(rows[number].required_inputs.length > 0);
  }
});

test('Epic 9 pin and shadow rows require retained matching boundary evidence', (t) => {
  let base = fixture(t);
  let rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[38].status, 'target_met');
  assert.equal(rows[38].values.registry_matches_pins, true);
  assert.equal(rows[38].values.one_resolved_core_version, true);
  assert.equal(rows[38].values.ordering_test_blocking, true);
  assert.equal(rows[38].values.staleness_alert_routed, true);
  assert.equal(rows[39].status, 'target_met');
  assert.equal(rows[39].values.report.lanes['authoring/v2'].existing_pass_kernel_fail, 0);

  base = fixture(t);
  const evidencePath = '000-docs/810-RA-DATA-epic-9-boundary-evidence.json';
  const evidence = JSON.parse(readFileSync(join(base.root, evidencePath), 'utf8'));
  evidence.package_registry.packages['@intentsolutions/core'].version = '2.0.0';
  evidence.kernel_shadow.kernel_version = '2.0.0';
  put(base.root, evidencePath, JSON.stringify(evidence));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[38].status, 'partial');
  assert.equal(rows[38].values.target_met, false);
  assert.deepEqual(rows[38].limitations, [
    'retained package-registry observation in 000-docs/810-RA-DATA-epic-9-boundary-evidence.json does not match the exact root pins (@intentsolutions/core: observed 2.0.0, pinned 1.0.0); capture a new versioned boundary observation without rewriting retained evidence',
  ]);
  assert.equal(rows[39].status, 'stale_evidence');
});

test('Freshie exit rows use tracked receipts and fail closed on planted drift', (t) => {
  let base = fixture(t);
  let rows = buildExtendedScorecardRows(input(base));
  for (const number of [52, 53, 54, 58]) assert.equal(rows[number].status, 'target_met');
  assert.equal(rows[55].status, 'target_met');
  assert.equal(rows[55].values.retention_percent, null);
  assert.equal(rows[55].values.no_e2_e3_claims, true);
  assert.equal(rows[55].values.unretained_e2_e3, 0);

  const runPath = 'freshie/reports/run-delta-9.json';
  let driftedRun = JSON.parse(readFileSync(join(base.root, runPath), 'utf8'));
  driftedRun.run_coherence.header_total_skills = 3;
  driftedRun.run_coherence.skill_row_delta = -1;
  put(base.root, runPath, JSON.stringify(driftedRun));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[52].status, 'partial');

  base = fixture(t);
  const histogramPath = 'freshie/grade-histogram.json';
  let histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.dolt_commit = 'b'.repeat(32);
  put(base.root, histogramPath, JSON.stringify(histogram));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture(t);
  histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.grades = { A: 2, B: 0 };
  put(base.root, histogramPath, JSON.stringify(histogram));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture(t);
  put(base.root, 'freshie/grades.csv', 'skill_path,grade,score\none,B,90\ntwo,A,80\n');
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture(t);
  const proofPath = 'freshie/reports/legacy-forge-proofs-demotion.json';
  const proof = JSON.parse(readFileSync(join(base.root, proofPath), 'utf8'));
  proof.records.push({
    plugin_name: 'missing-artifact',
    jrig_run_id: 7,
    evidence_class: 'E2',
    artifact_uri: null,
    artifact_sha256: null,
  });
  put(base.root, proofPath, JSON.stringify(proof));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[54].status, 'not_reproducible');
  assert.equal(rows[55].status, 'not_reproducible');

  base = fixture(t);
  const workflowPath = '.github/workflows/validate-plugins.yml';
  const workflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - test\n',
    '',
  );
  put(base.root, workflowPath, workflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');

  base = fixture(t);
  put(
    base.root,
    'tests/test_freshie_hermetic_cycle.py',
    `import unittest
class HermeticFreshieCycleTests(unittest.TestCase):
    def setUp(self):
        self.env = {"HOME": "dolt-home"}
        self._run(["dolt", "config", "--global", "--add", "user.name", "Test"])
        self._run(["dolt", "config", "--global", "--add", "user.email", "test@example.invalid"])
    def _run(self, args, expected=0):
        if False:
            self.fail("returncode")
    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):
        if False:
            self._run([str(REBUILD)])
            self._run([str(VALIDATE)])
            self._run([str(SYNC)])
            self._run([str(PROMOTE)])
            self._run(["dolt", "push", "file://remote"])
            subprocess.Popen(["dolt", "sql-server"])
            self._run([str(SYNC)], expected=1)
            self.assertFalse(self.out / "blocked-grades.csv")
        pass
`,
  );
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');

  base = fixture(t);
  const skippedTest = readFileSync(
    join(base.root, 'tests/test_freshie_hermetic_cycle.py'),
    'utf8',
  ).replace(
    '    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):\n',
    '    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):\n        raise unittest.SkipTest("no cycle executed")\n',
  );
  put(base.root, 'tests/test_freshie_hermetic_cycle.py', skippedTest);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.full_cycle, false);

  base = fixture(t);
  const aliasedMutation = readFileSync(
    join(base.root, 'tests/test_freshie_hermetic_cycle.py'),
    'utf8',
  ).replace(
    '    def setUpClass(cls):\n',
    '    def setUpClass(cls):\n        mutator = setattr\n        mutator(cls, "test_full_cycle_uses_only_scratch_state_and_refuses_live_server", lambda self: None)\n',
  );
  put(base.root, 'tests/test_freshie_hermetic_cycle.py', aliasedMutation);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.full_cycle, false);

  base = fixture(t);
  const replacedMethod = readFileSync(
    join(base.root, 'tests/test_freshie_hermetic_cycle.py'),
    'utf8',
  ).replace(
    '    def setUpClass(cls):\n',
    '    def setUpClass(cls):\n        cls.test_full_cycle_uses_only_scratch_state_and_refuses_live_server = lambda self: None\n',
  );
  put(base.root, 'tests/test_freshie_hermetic_cycle.py', replacedMethod);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.full_cycle, false);

  base = fixture(t);
  const lifecycleSkip = readFileSync(
    join(base.root, 'tests/test_freshie_hermetic_cycle.py'),
    'utf8',
  ).replace(
    '    def setUpClass(cls):\n',
    '    def setUpClass(cls):\n        raise unittest.SkipTest("class skipped before cycle")\n',
  );
  put(base.root, 'tests/test_freshie_hermetic_cycle.py', lifecycleSkip);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.full_cycle, false);

  base = fixture(t);
  const generatorTest = readFileSync(
    join(base.root, 'tests/test_freshie_hermetic_cycle.py'),
    'utf8',
  ).replace(
    '    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):\n',
    '    def test_full_cycle_uses_only_scratch_state_and_refuses_live_server(self):\n        yield None\n',
  );
  put(base.root, 'tests/test_freshie_hermetic_cycle.py', generatorTest);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.full_cycle, false);

  base = fixture(t);
  const unsafeWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '"$dolt_extract/dolt-linux-amd64/bin/dolt"',
    '/tmp/unverified/dolt',
  );
  put(base.root, workflowPath, unsafeWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture(t);
  const aliasedOverwrite = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - name: Run Freshie hermetic publication cycle\n',
    '      - name: Overwrite Dolt through an alias\n        if: matrix.test-type == \'python-tests\'\n        env:\n          DOLT_DEST: /usr/local/bin/dolt\n        run: sudo /usr/bin/install -m 0755 /tmp/unverified/dolt "$DOLT_DEST"\n      - name: Run Freshie hermetic publication cycle\n',
  );
  put(base.root, workflowPath, aliasedOverwrite);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture(t);
  const separateStepOverwrite = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - name: Run Freshie hermetic publication cycle\n',
    "      - name: Overwrite Dolt after verification\n        if: matrix.test-type == 'python-tests'\n        run: sudo /usr/bin/install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n      - name: Run Freshie hermetic publication cycle\n",
  );
  put(base.root, workflowPath, separateStepOverwrite);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture(t);
  const alternateOverwriteWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '          test "$installed_dolt_version" = "$dolt_version"\n',
    '          test "$installed_dolt_version" = "$dolt_version"\n          sudo /usr/bin/install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n',
  );
  put(base.root, workflowPath, alternateOverwriteWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture(t);
  const overwrittenWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '          test "$installed_dolt_version" = "$dolt_version"\n',
    '          test "$installed_dolt_version" = "$dolt_version"\n          sudo install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n',
  );
  put(base.root, workflowPath, overwrittenWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture(t);
  const emptyGrades = 'skill_path,grade,score\n';
  const emptyHash = createHash('sha256').update(emptyGrades).digest('hex');
  put(base.root, 'freshie/grades.csv', emptyGrades);
  histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.total = 0;
  histogram.grades = {};
  histogram.grades_csv_sha256 = emptyHash;
  put(base.root, histogramPath, JSON.stringify(histogram));
  driftedRun = JSON.parse(readFileSync(join(base.root, runPath), 'utf8'));
  driftedRun.run_coherence.header_total_skills = 0;
  driftedRun.run_coherence.skill_rows = 0;
  driftedRun.run_coherence.skill_row_delta = 0;
  driftedRun.run_coherence.skill_compliance_rows = 0;
  driftedRun.grade_export.row_count = 0;
  driftedRun.grade_export.csv_sha256 = emptyHash;
  driftedRun.grade_export.grade_counts = {};
  put(base.root, runPath, JSON.stringify(driftedRun));
  rows = buildExtendedScorecardRows(input(base));
  assert.notEqual(rows[52].status, 'target_met');
  assert.notEqual(rows[53].status, 'target_met');

  base = fixture(t);
  put(base.root, runPath, '{not json');
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[52].status, 'not_reproducible');
  assert.equal(rows[52].values, null);
});

test('legacy forge-proof evidence remains bound to its source when a newer run is empty', (t) => {
  const base = fixture(t);
  const run9Path = 'freshie/reports/run-delta-9.json';
  const run10Path = 'freshie/reports/run-delta-10.json';
  const run10 = JSON.parse(readFileSync(join(base.root, run9Path), 'utf8'));
  run10.run_id = 10;
  run10.from_tag = null;
  run10.to_tag = 'run-10';
  run10.dolt_commit = 'b'.repeat(32);
  run10.run_coherence.discovery_run_id = 10;
  run10.forge_proofs = {
    row_count: 0,
    records_sha256: createHash('sha256').update('[]').digest('hex'),
    class_counts: { E0: 0, E1: 0, E2: 0, E3: 0 },
    retained_e2_e3: 0,
    total_e2_e3: 0,
    records: [],
  };
  put(base.root, run10Path, JSON.stringify(run10));
  base.paths.push(run10Path);
  const histogramPath = 'freshie/grade-histogram.json';
  const histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.run_id = 10;
  histogram.dolt_commit = run10.dolt_commit;
  put(base.root, histogramPath, JSON.stringify(histogram));

  let rows = buildExtendedScorecardRows(input(base));
  for (const number of [52, 53, 54, 55]) assert.equal(rows[number].status, 'target_met');
  assert.equal(rows[54].values.source_run_id, 9);
  assert.equal(rows[54].values.current_run_id, 10);
  assert.ok(rows[54].source.includes(run9Path));
  assert.ok(rows[54].source.includes(run10Path));

  const source = JSON.parse(readFileSync(join(base.root, run9Path), 'utf8'));
  source.dolt_commit = 'c'.repeat(32);
  put(base.root, run9Path, JSON.stringify(source));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[54].status, 'not_reproducible');
  assert.equal(rows[55].status, 'not_reproducible');
});

test('measures privileged workflow action pins and exposes mutable references', (t) => {
  const base = fixture(t);
  let row = buildExtendedScorecardRows(input(base))[36];
  assert.equal(row.status, 'measured');
  assert.deepEqual(row.values.mutable_uses, []);
  assert.equal(row.values.total_uses, 1);

  put(
    base.root,
    '.github/workflows/emit-evidence.yml',
    'permissions:\n  id-token: write\njobs:\n  sign:\n    steps:\n      - uses: actions/checkout@v6\n',
  );
  row = buildExtendedScorecardRows(input(base))[36];
  assert.deepEqual(row.values.mutable_uses, ['.github/workflows/emit-evidence.yml:6']);
});

test('measurements follow fixture inputs and do not preserve historical blueprint numbers', (t) => {
  const base = fixture(t);
  const first = buildExtendedScorecardRows(input(base));
  assert.equal(first[5].values.rows, 2);
  assert.equal(first[28].values.provenance_marked_mirrors, 1);

  put(
    base.root,
    'plugins/local/skills/three/SKILL.md',
    '---\nname: three\nallowed-tools: Read\ncompatibility: Harness C\n---\n',
  );
  base.paths.push('plugins/local/skills/three/SKILL.md');
  const changed = input(base);
  changed.skillRows.push({
    errors: 0,
    grade: 'C',
    path: 'plugins/local/skills/three/SKILL.md',
    score: 70,
  });
  const second = buildExtendedScorecardRows(changed);
  assert.equal(second[5].values.rows, 3);
  assert.notDeepEqual(second[5].values, first[5].values);

  const source = JSON.stringify(second);
  for (const stale of ['22962', '3680', '3679', '3678', '7687', '7433', '1454', '14041']) {
    assert.equal(source.includes(stale), false, `stale blueprint snapshot ${stale}`);
  }
});

test('rejects path traversal and ignores untracked validator rows', (t) => {
  const base = fixture(t);
  const values = input(base);
  values.skillRows.push({ errors: 0, grade: 'A', path: 'plugins/untracked/SKILL.md', score: 100 });
  assert.equal(buildExtendedScorecardRows(values)[5].values.rows, 2);
  assert.throws(
    () => buildExtendedScorecardRows({ ...values, paths: [...base.paths, '../escape'] }),
    /escapes repository/,
  );
});

test('scorecard corpus counts reject a supplied SKILL.md symlink', (t) => {
  const base = fixture(t);
  const linked = 'plugins/local/skills/linked/SKILL.md';
  mkdirSync(dirname(join(base.root, linked)), { recursive: true });
  symlinkSync(join(base.root, 'plugins/local/skills/two/SKILL.md'), join(base.root, linked));
  assert.throws(
    () => buildExtendedScorecardRows(input({ ...base, paths: [...base.paths, linked] })),
    /symbolic link is not a corpus authority/,
  );
});

function marketplaceGateFixture(t) {
  const base = fixture(t);
  const wrapper =
    'python3 scripts/check-marketplace-compliance-baseline.py --checkout-sha "$CHECKOUT_SHA"';
  const document = {
    on: { pull_request: null, push: { branches: ['main'] }, workflow_dispatch: null },
    jobs: {
      'marketplace-compliance-ratchet': {
        'runs-on': 'ubuntu-latest',
        steps: [
          { uses: 'actions/checkout@v7', with: { 'fetch-depth': 0 } },
          {
            name: 'Enforce marketplace ratchet',
            env: { CHECKOUT_SHA: '${{ github.sha }}' },
            run: wrapper,
          },
        ],
      },
      'ci-required': {
        if: 'always()',
        needs: ['marketplace-compliance-ratchet'],
        steps: [
          { uses: 'actions/checkout@v7' },
          {
            env: { NEEDS_JSON: '${{ toJSON(needs) }}' },
            run: 'python3 scripts/ci/fastlane.py gate',
          },
        ],
      },
    },
  };
  for (const path of [
    'scripts/check-marketplace-compliance-baseline.py',
    'scripts/ci/fastlane.py',
  ]) {
    put(base.root, path, readFileSync(new URL(`../${path}`, import.meta.url), 'utf8'));
    base.paths.push(path);
  }
  const measure = () => {
    put(base.root, '.github/workflows/validate-plugins.yml', JSON.stringify(document));
    return buildExtendedScorecardRows(input(base))[40];
  };
  return {
    base,
    document,
    wrapper,
    measure,
    job: document.jobs['marketplace-compliance-ratchet'],
    aggregate: document.jobs['ci-required'],
  };
}

test('row 40 counts one required wrapper job and labels the proof as static', (t) => {
  const state = marketplaceGateFixture(t);
  state.job.steps[1].run =
    'python3 -c "import yaml" 2>/dev/null || python3 -m pip install --quiet pyyaml\n' +
    state.wrapper;
  state.job.steps.push({
    if: "github.event_name == 'pull_request'",
    run: 'python3 scripts/check-marketplace-compliance-baseline.py --check-growth-only --base origin/main',
  });
  state.job.steps.push({ ...state.job.steps[1] });
  const row = state.measure();
  assert.equal(row.status, 'target_met');
  assert.equal(row.values.blocking_candidates, 1);
  assert.equal(row.values.proof_kind, 'static_required_job_wiring');
  assert.equal(row.values.invocations.filter((entry) => entry.blocking_candidate).length, 2);
  assert.ok(
    row.values.invocations.some(
      (entry) => entry.kind === 'unproven-reference' && !entry.blocking_candidate,
    ),
  );
  assert.match(row.limitations[0], /hosted red-run evidence/);
});

test('row 40 still recognizes an unsuppressed direct full marketplace validator', (t) => {
  const state = marketplaceGateFixture(t);
  state.job.steps[1].run = 'python3 scripts/validate-skills-schema.py --marketplace';
  delete state.job.steps[1].env;
  state.job.steps[0].with = {
    repository: '${{ github.repository }}',
    ref: '${{ github.sha }}',
    path: '.',
  };
  const row = state.measure();
  assert.equal(row.values.blocking_candidates, 1);
  assert.ok(
    row.values.invocations.some(
      (entry) => entry.kind === 'direct-marketplace-validator' && entry.blocking_candidate,
    ),
  );
  state.job.steps[0].with.repository = 'other/repo';
  assert.equal(state.measure().values.blocking_candidates, 0);
});

test('row 40 refuses broken required workflow wiring and policy bypasses', async (t) => {
  const cases = {
    'foreign enforcement repository': (s) => {
      s.job.steps[0].with.repository = 'other/repo';
    },
    'mutable enforcement revision': (s) => {
      s.job.steps[0].with.ref = 'old-branch';
    },
    'different enforcement checkout directory': (s) => {
      s.job.steps[0].with.path = 'other';
    },
    'conditional enforcement checkout': (s) => {
      s.job.steps[0].if = 'false';
    },
    'suppressed enforcement checkout': (s) => {
      s.job.steps[0]['continue-on-error'] = true;
    },
    'missing enforcement checkout': (s) => {
      s.job.steps.shift();
    },
    'checkout after enforcement': (s) => {
      s.job.steps.reverse();
    },
    'ambiguous multiple checkouts': (s) => {
      s.job.steps.unshift({ ...s.job.steps[0] });
    },
    'foreign aggregate repository': (s) => {
      s.aggregate.steps[0].with = { repository: 'other/repo' };
    },
    'missing required dependency': (s) => {
      s.aggregate.needs = ['another-job'];
    },
    'duplicate dependency': (s) => {
      s.aggregate.needs.push('marketplace-compliance-ratchet');
    },
    'conditional job': (s) => {
      s.job.if = "github.event_name == 'push'";
    },
    'job failure suppressed': (s) => {
      s.job['continue-on-error'] = true;
    },
    'job has potentially skipped upstream dependency': (s) => {
      s.job.needs = 'conditional-upstream';
    },
    'conditional step': (s) => {
      s.job.steps[1].if = "github.event_name == 'push'";
    },
    'step failure suppressed': (s) => {
      s.job.steps[1]['continue-on-error'] = true;
    },
    'path filter': (s) => {
      s.document.on.pull_request = { paths: ['plugins/**'] };
    },
    'branch filter': (s) => {
      s.document.on.pull_request = { branches: ['main'] };
    },
    'missing pull request trigger': (s) => {
      delete s.document.on.pull_request;
    },
    'aggregate not always reporting': (s) => {
      delete s.aggregate.if;
    },
    'aggregate tolerates failure': (s) => {
      s.aggregate['continue-on-error'] = true;
    },
    'aggregate reads fake needs': (s) => {
      s.aggregate.steps[1].env.NEEDS_JSON = '{}';
    },
    'aggregate bypass command': (s) => {
      s.aggregate.steps[1].run += ' || true';
    },
    'aggregate conditional command': (s) => {
      s.aggregate.steps[1].if = 'false';
    },
    'aggregate checkout wrong revision': (s) => {
      s.aggregate.steps[0].with = { ref: 'main' };
    },
    'aggregate writes a different checkout path': (s) => {
      s.aggregate.steps[0].with = { path: 'other' };
    },
    'unrecognized additional aggregate step': (s) => {
      s.aggregate.steps.push({ run: 'true' });
    },
    'missing checkout SHA binding': (s) => {
      delete s.job.steps[1].env;
    },
    'mutable checkout binding': (s) => {
      s.job.steps[1].env.CHECKOUT_SHA = '${{ github.head_ref }}';
    },
    'different working directory': (s) => {
      s.job.steps[1]['working-directory'] = 'fixture';
    },
    'workflow default working directory': (s) => {
      s.document.defaults = { run: { 'working-directory': 'fixture' } };
    },
    'unrecognized shell': (s) => {
      s.job.steps[1].shell = 'python {0}';
    },
    'missing canonical wrapper': (s) => {
      s.base.paths = s.base.paths.filter(
        (p) => p !== 'scripts/check-marketplace-compliance-baseline.py',
      );
    },
    'missing canonical aggregation policy': (s) => {
      s.base.paths = s.base.paths.filter((p) => p !== 'scripts/ci/fastlane.py');
    },
  };
  for (const [name, mutate] of Object.entries(cases)) {
    await t.test(name, (subtest) => {
      const state = marketplaceGateFixture(subtest);
      mutate(state);
      const row = state.measure();
      assert.equal(row.values.blocking_candidates, 0);
      assert.equal(row.status, 'partial');
    });
  }
});

test('row 40 treats unsupported shell text as references, never full corpus execution', async (t) => {
  const cases = {
    comment: (cmd) => `# ${cmd}`,
    echo: (cmd) => `echo '${cmd}'`,
    heredoc: (cmd) => `cat <<'EXAMPLE'\n${cmd}\nEXAMPLE`,
    'shell condition': (cmd) => `if false; then\n${cmd}\nfi`,
    'early success exit': (cmd) => `exit 0\n${cmd}`,
    'swallowed failure': (cmd) => `${cmd} || true`,
    pipeline: (cmd) => `${cmd} | cat`,
    'growth-only': (cmd) => `${cmd} --check-growth-only --base origin/main`,
    'fixture input': (cmd) => `${cmd} --current /tmp/passing.json`,
    'different corpus': (cmd) => `${cmd} --repo-root /tmp/fixture`,
    'alternate baseline': (cmd) => `${cmd} --baseline /tmp/permissive.json`,
  };
  for (const [name, transform] of Object.entries(cases)) {
    await t.test(name, (subtest) => {
      const state = marketplaceGateFixture(subtest);
      state.job.steps[1].run = transform(state.wrapper);
      const row = state.measure();
      assert.equal(row.values.blocking_candidates, 0);
      assert.ok(
        row.values.invocations.some((entry) =>
          entry.reason_codes.includes('UNPROVEN_FULL_CORPUS_COMMAND'),
        ),
      );
    });
  }
});

test('row 40 reports malformed workflow syntax without fabricating a blocking gate', (t) => {
  const state = marketplaceGateFixture(t);
  put(state.base.root, '.github/workflows/validate-plugins.yml', 'jobs: [');
  const row = buildExtendedScorecardRows(input(state.base))[40];
  assert.equal(row.values.blocking_candidates, 0);
  assert.equal(row.status, 'partial');
  assert.ok(
    row.values.parse_errors.some(
      (entry) => entry.path === '.github/workflows/validate-plugins.yml',
    ),
  );
});

function swallowFixture(t) {
  const base = fixture(t);
  const digest = (s) => createHash('sha256').update(s).digest('hex');
  const workflowPaths = [
    '.github/workflows/validate-plugins.yml',
    '.github/workflows/secret-scan.yml',
    '.github/workflows/skill-conform.yml',
  ];
  const job = { steps: [{ name: 'Unresolved scan', run: 'scan || true\n' }] };
  const documents = [
    {
      jobs: {
        validate: job,
        'ci-required': { needs: ['validate'], steps: [{ run: 'echo aggregate\n' }] },
      },
    },
    { jobs: { secrets: { steps: [{ run: 'echo opaque internals\n' }] } } },
    { jobs: { conform: { steps: [{ run: 'echo conform\n' }] } } },
  ];
  const files = Object.fromEntries(
    workflowPaths.map((path, i) => [path, JSON.stringify(documents[i])]),
  );
  files['scripts/ci/fastlane.py'] = '# synthetic policy\n';
  files['scripts/ci-correctness-swallows.json'] = JSON.stringify({
    schema_version: 1,
    repository_complete: false,
    workflows: workflowPaths.map((path) => ({ path, sha256: digest(files[path]) })),
    aggregate_policy: {
      path: 'scripts/ci/fastlane.py',
      sha256: digest(files['scripts/ci/fastlane.py']),
      authority: [],
    },
    expected: {
      sites: 1,
      site_containers: 1,
      workflows: 3,
      jobs: 4,
      containers: 4,
      run_containers: 4,
      opaque_actions: 0,
      conditional_envelopes: 0,
    },
    sites: [
      {
        id: 'unresolved-scan',
        workflow: workflowPaths[0],
        job: 'validate',
        step: 0,
        step_name: job.steps[0].name,
        job_sha256: digest(canonicalJson(job)),
        step_sha256: digest(canonicalJson(job.steps[0])),
        run_sha256: digest(job.steps[0].run),
        anchor: { line: 1, text: 'scan || true' },
        classification: 'unresolved',
        rationale: 'Synthetic unresolved scan has no bound authority.',
        owner: null,
        promotion: null,
        authority: [],
        deadline_marker: null,
      },
    ],
  });
  for (const [path, text] of Object.entries(files)) put(base.root, path, text);
  base.paths = [...new Set([...base.paths, ...Object.keys(files)])].sort();
  return base;
}

test('row 50 integrates a partial review while keeping primary totals unknown', (t) => {
  const row = buildExtendedScorecardRows(input(swallowFixture(t)))[50];
  assert.equal(row.status, 'partial');
  assert.equal(row.values.unbounded_correctness_total, null);
  assert.equal(row.values.repository_unbounded_total, null);
  assert.equal(row.values.reviewed_unbounded_correctness_lower_bound, 0);
  assert.equal(row.values.site_counts.unresolved, 1);
  assert.equal(row.values.target_met, false);
});

test('row 50 invalid registry reports unknown rather than zero', (t) => {
  const base = swallowFixture(t);
  put(base.root, 'scripts/ci-correctness-swallows.json', '{');
  const row = buildExtendedScorecardRows(input(base))[50];
  assert.equal(row.status, 'not_reproducible');
  assert.equal(row.values.site_counts, null);
  assert.equal(row.values.target_met, false);
});

for (const path of ['scripts/ci-correctness-swallows.json', '.github/workflows/secret-scan.yml']) {
  test(`row 50 refuses an actual symlink at ${path}`, (t) => {
    const base = swallowFixture(t);
    const target = join(base.root, 'outside-input');
    writeFileSync(target, readFileSync(join(base.root, path)));
    rmSync(join(base.root, path));
    symlinkSync(target, join(base.root, path));
    const row = buildExtendedScorecardRows(input(base))[50];
    assert.equal(row.status, 'not_reproducible');
    assert.ok(row.values === null || row.values.site_counts === null);
  });
}
