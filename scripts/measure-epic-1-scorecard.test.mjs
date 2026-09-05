import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, readFileSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';

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

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'epic-1-scorecard-'));
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

test('emits the exact extended numbered row set in deterministic order and shape', () => {
  const rows = buildExtendedScorecardRows(input(fixture()));
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
  const again = buildExtendedScorecardRows(input(fixture()));
  const firstWithoutRootSpecificData = JSON.stringify(rows);
  assert.equal(JSON.stringify(again), firstWithoutRootSpecificData);
});

test('discovers additional generated artifacts and README count writers dynamically', () => {
  const base = fixture();
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

test('requires call-bound production evidence and excludes measurement instrumentation', () => {
  const base = fixture();
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

test('writer discovery matches exact basenames instead of catalog suffixes', () => {
  const base = fixture();
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

test('counts only producer-integrated workflow checks as artifact drift gates', () => {
  const base = fixture();
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

test('normalizes absolute validator paths into the tracked Git cohort', () => {
  const base = fixture();
  const values = input(base);
  values.skillRows = values.skillRows.map((entry) => ({
    ...entry,
    path: join(base.root, entry.path),
  }));
  const row = buildExtendedScorecardRows(values)[5];
  assert.equal(row.values.rows, 2);
  assert.deepEqual(row.values.grade_distribution, { A: 1, B: 1, C: 0, D: 0, F: 0 });
});

test('measures the merged provenance boundary, ci-required needs, and STANDARDS authority table', () => {
  const base = fixture();
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

test('fails closed on malformed ci-required needs', () => {
  const base = fixture();
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

test('link instrumentation stays excluded while domain instrumentation cannot bypass policy', () => {
  const base = fixture();
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

test('unresolved rows fail closed with null values rather than fabricated zeroes', () => {
  const rows = buildExtendedScorecardRows(input(fixture()));
  for (const number of [7, 8, 9, 15, 16, 17, 18, 19, 23, 29, 49, 50, 51, 60, 61, 62]) {
    assert.equal(rows[number].values, null, `row ${number}`);
    assert.match(rows[number].reason_code, /^[A-Z][A-Z0-9_]+$/);
    assert.ok(rows[number].required_inputs.length > 0);
  }
});

test('Epic 9 pin and shadow rows require retained matching boundary evidence', () => {
  let base = fixture();
  let rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[38].status, 'target_met');
  assert.equal(rows[38].values.registry_matches_pins, true);
  assert.equal(rows[38].values.one_resolved_core_version, true);
  assert.equal(rows[38].values.ordering_test_blocking, true);
  assert.equal(rows[38].values.staleness_alert_routed, true);
  assert.equal(rows[39].status, 'target_met');
  assert.equal(rows[39].values.report.lanes['authoring/v2'].existing_pass_kernel_fail, 0);

  base = fixture();
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

test('Freshie exit rows use tracked receipts and fail closed on planted drift', () => {
  let base = fixture();
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

  base = fixture();
  const histogramPath = 'freshie/grade-histogram.json';
  let histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.dolt_commit = 'b'.repeat(32);
  put(base.root, histogramPath, JSON.stringify(histogram));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture();
  histogram = JSON.parse(readFileSync(join(base.root, histogramPath), 'utf8'));
  histogram.grades = { A: 2, B: 0 };
  put(base.root, histogramPath, JSON.stringify(histogram));
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture();
  put(base.root, 'freshie/grades.csv', 'skill_path,grade,score\none,B,90\ntwo,A,80\n');
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[53].status, 'partial');

  base = fixture();
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

  base = fixture();
  const workflowPath = '.github/workflows/validate-plugins.yml';
  const workflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - test\n',
    '',
  );
  put(base.root, workflowPath, workflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');

  base = fixture();
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

  base = fixture();
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

  base = fixture();
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

  base = fixture();
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

  base = fixture();
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

  base = fixture();
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

  base = fixture();
  const unsafeWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '"$dolt_extract/dolt-linux-amd64/bin/dolt"',
    '/tmp/unverified/dolt',
  );
  put(base.root, workflowPath, unsafeWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture();
  const aliasedOverwrite = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - name: Run Freshie hermetic publication cycle\n',
    '      - name: Overwrite Dolt through an alias\n        if: matrix.test-type == \'python-tests\'\n        env:\n          DOLT_DEST: /usr/local/bin/dolt\n        run: sudo /usr/bin/install -m 0755 /tmp/unverified/dolt "$DOLT_DEST"\n      - name: Run Freshie hermetic publication cycle\n',
  );
  put(base.root, workflowPath, aliasedOverwrite);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture();
  const separateStepOverwrite = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '      - name: Run Freshie hermetic publication cycle\n',
    "      - name: Overwrite Dolt after verification\n        if: matrix.test-type == 'python-tests'\n        run: sudo /usr/bin/install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n      - name: Run Freshie hermetic publication cycle\n",
  );
  put(base.root, workflowPath, separateStepOverwrite);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture();
  const alternateOverwriteWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '          test "$installed_dolt_version" = "$dolt_version"\n',
    '          test "$installed_dolt_version" = "$dolt_version"\n          sudo /usr/bin/install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n',
  );
  put(base.root, workflowPath, alternateOverwriteWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture();
  const overwrittenWorkflow = readFileSync(join(base.root, workflowPath), 'utf8').replace(
    '          test "$installed_dolt_version" = "$dolt_version"\n',
    '          test "$installed_dolt_version" = "$dolt_version"\n          sudo install -m 0755 /tmp/unverified/dolt /usr/local/bin/dolt\n',
  );
  put(base.root, workflowPath, overwrittenWorkflow);
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[58].status, 'partial');
  assert.equal(rows[58].values.pinned_dolt, false);

  base = fixture();
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

  base = fixture();
  put(base.root, runPath, '{not json');
  rows = buildExtendedScorecardRows(input(base));
  assert.equal(rows[52].status, 'not_reproducible');
  assert.equal(rows[52].values, null);
});

test('legacy forge-proof evidence remains bound to its source when a newer run is empty', () => {
  const base = fixture();
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

test('measures privileged workflow action pins and exposes mutable references', () => {
  const base = fixture();
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

test('measurements follow fixture inputs and do not preserve historical blueprint numbers', () => {
  const base = fixture();
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

test('rejects path traversal and ignores untracked validator rows', () => {
  const base = fixture();
  const values = input(base);
  values.skillRows.push({ errors: 0, grade: 'A', path: 'plugins/untracked/SKILL.md', score: 100 });
  assert.equal(buildExtendedScorecardRows(values)[5].values.rows, 2);
  assert.throws(
    () => buildExtendedScorecardRows({ ...values, paths: [...base.paths, '../escape'] }),
    /escapes repository/,
  );
});

test('scorecard corpus counts reject a supplied SKILL.md symlink', () => {
  const base = fixture();
  const linked = 'plugins/local/skills/linked/SKILL.md';
  mkdirSync(dirname(join(base.root, linked)), { recursive: true });
  symlinkSync(join(base.root, 'plugins/local/skills/two/SKILL.md'), join(base.root, linked));
  assert.throws(
    () => buildExtendedScorecardRows(input({ ...base, paths: [...base.paths, linked] })),
    /symbolic link is not a corpus authority/,
  );
});
