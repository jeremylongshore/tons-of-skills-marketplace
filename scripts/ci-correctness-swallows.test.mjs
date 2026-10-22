import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import yaml from 'js-yaml';
import { inspectCorrectnessSwallows, SWALLOWS_REGISTRY } from './ci-correctness-swallows.mjs';

const registry = JSON.parse(
  readFileSync(new URL('./ci-correctness-swallows.json', import.meta.url), 'utf8'),
);
const hash = (text) => createHash('sha256').update(text).digest('hex');
const typed = (value) =>
  JSON.stringify(value, (_, v) =>
    v && typeof v === 'object' && !Array.isArray(v)
      ? Object.fromEntries(
          Object.keys(v)
            .sort()
            .map((k) => [k, v[k]]),
        )
      : v,
  );
// Synthetic containers: the real registry supplies reviewed labels/anchors, never mutable workflow bodies.
// Workflow changes must make the real metric unknown, not introduce a new test gate.
function fixture() {
  const review = globalThis.structuredClone(registry);
  const data = Object.fromEntries(review.workflows.map((w) => [w.path, { jobs: {} }]));
  for (const site of review.sites) {
    const jobs = data[site.workflow].jobs;
    const job = (jobs[site.job] ??= { steps: [] });
    while (job.steps.length <= site.step) job.steps.push({ uses: 'example/opaque@v1' });
    const step = job.steps[site.step];
    if (!step.run) {
      delete step.uses;
      step.name = site.step_name;
      step.run =
        Array.from({ length: 60 }, (_, i) => `# synthetic line ${i + 1}`).join('\n') + '\n';
    }
    const lines = step.run.split('\n');
    lines[site.anchor.line - 1] = site.anchor.text;
    step.run = lines.join('\n');
    site.authority = site.authority.length
      ? [{ path: 'CLAUDE.md', line: 1, text: '# Synthetic authority' }]
      : [];
  }
  const first = review.workflows[0].path;
  const needs = Object.keys(data[first].jobs);
  data[first].jobs['ci-required'] = { needs, steps: [{ run: 'echo aggregate' }] };
  data[review.workflows[2].path].jobs.conform = {
    steps: [{ name: 'Conform', run: 'echo conform' }],
  };
  const markerLines = [
    ...new Set(review.sites.filter((s) => s.deadline_marker).map((s) => s.deadline_marker.line)),
  ].sort((a, b) => a - b);
  const markers = ['2026-10-31', '2026-11-17', '2026-10-31', '2026-10-31'].map(
    (date, i) => `# REPORT-ONLY-UNTIL: ${date} (synthetic marker ${i})`,
  );
  for (const site of review.sites)
    if (site.deadline_marker) {
      const index = markerLines.indexOf(site.deadline_marker.line);
      site.deadline_marker = { line: index + 1, sha256: hash(markers[index]) };
    }
  const files = {
    'CLAUDE.md': '# Synthetic authority\n',
    [review.aggregate_policy.path]: '# Synthetic aggregate policy\n',
  };
  review.aggregate_policy.sha256 = hash(files[review.aggregate_policy.path]);
  review.aggregate_policy.authority = [
    { path: 'CLAUDE.md', line: 1, text: '# Synthetic authority' },
  ];
  review.expected = {
    sites: 24,
    site_containers: 17,
    workflows: 3,
    jobs: 0,
    containers: 0,
    run_containers: 0,
    opaque_actions: 0,
    conditional_envelopes: 0,
  };
  for (const workflow of review.workflows) {
    files[workflow.path] =
      (workflow.path === first ? markers.join('\n') + '\n' : '') + yaml.dump(data[workflow.path]);
    workflow.sha256 = hash(files[workflow.path]);
    for (const job of Object.values(data[workflow.path].jobs)) {
      review.expected.jobs++;
      for (const step of job.steps) {
        review.expected.containers++;
        review.expected[step.run ? 'run_containers' : 'opaque_actions']++;
      }
    }
  }
  for (const site of review.sites) {
    const job = data[site.workflow].jobs[site.job],
      step = job.steps[site.step];
    site.job_sha256 = hash(typed(job));
    site.step_sha256 = hash(typed(step));
    site.run_sha256 = hash(step.run);
  }
  return { review, files, needs };
}
function inspect(f) {
  return inspectCorrectnessSwallows({
    reader: {
      text: (p) => (p === SWALLOWS_REGISTRY ? JSON.stringify(f.review) : (f.files[p] ?? null)),
    },
    requiredNeeds: { error: null, needs: f.needs },
  });
}
function unknown(result, reason) {
  assert.equal(result.valid, false);
  assert.match(result.reason, reason);
  assert.equal(result.values.unbounded_correctness_total, null);
  assert.equal(result.values.reviewed_unbounded_correctness_lower_bound, null);
  assert.equal(result.values.site_counts, null);
  assert.equal(result.values.target_met, false);
}
function rebindWorkflow(f, path) {
  f.review.workflows.find((w) => w.path === path).sha256 = hash(f.files[path]);
}

test('reviewed subset is reproducible without claiming repository totals or shell proof', () => {
  const f = fixture();
  const result = inspect(f);
  assert.equal(result.valid, true);
  assert.deepEqual(result.values.site_counts, {
    authorized_control_flow: 9,
    informational: 1,
    unbounded_correctness: 0,
    unresolved: 14,
  });
  assert.deepEqual(result.values.coverage, {
    ...Object.fromEntries(
      Object.entries(f.review.expected).filter(
        ([key]) => !['sites', 'site_containers'].includes(key),
      ),
    ),
    containers_with_sites: 17,
    unreviewed_run_containers: f.review.expected.run_containers - 17,
    counts_overlap: true,
  });
  assert.equal(result.values.reviewed_unbounded_correctness_lower_bound, 0);
  assert.equal(result.values.unbounded_correctness_total, null);
  assert.equal(result.values.repository_unbounded_total, null);
  assert.equal(result.values.target_met, false);
  assert.equal(result.values.sites.length, 24);
  assert.ok(result.values.sites.every((s) => s.owner === null && s.promotion === null));
  assert.deepEqual(
    result.values.sites.filter((s) => s.observed_deadline).map((s) => s.observed_deadline.date),
    ['2026-10-31', '2026-10-31', '2026-11-17', '2026-10-31', '2026-10-31'],
  );
  assert.equal(
    result.values.sites.find((s) => s.id === 'enterprise-validator-advisory').observed_deadline,
    null,
  );
});

test('missing registry preserves the original explicit unknown reason', () => {
  unknown(
    inspectCorrectnessSwallows({ reader: { text: () => null }, requiredNeeds: null }),
    /MISSING_CORRECTNESS_CRITICAL_COMMAND_REGISTRY/,
  );
});

for (const [name, mutate, reason] of [
  [
    'missing workflow',
    (f) => delete f.files[f.review.workflows[1].path],
    /MISSING_OR_UNSAFE_INPUT/,
  ],
  [
    'stale comments',
    (f) => (f.files[f.review.workflows[0].path] += '\n# changed\n'),
    /STALE_WORKFLOW/,
  ],
  ['missing workflow scope', (f) => f.review.workflows.pop(), /INCOMPLETE_WORKFLOW_SCOPE/],
  [
    'duplicate workflow scope',
    (f) => (f.review.workflows[1] = f.review.workflows[0]),
    /INCOMPLETE_WORKFLOW_SCOPE/,
  ],
  ['missing selected site', (f) => f.review.sites.pop(), /INCOMPLETE_SITE_COVERAGE/],
  ['duplicate site id', (f) => f.review.sites.push(f.review.sites[0]), /DUPLICATE_OR_MISSING_SITE/],
  [
    'duplicate operation under a new id',
    (f) => f.review.sites.push({ ...f.review.sites[0], id: 'duplicate' }),
    /DUPLICATE_OPERATION_SITE/,
  ],
  ['stale operation anchor', (f) => (f.review.sites[0].anchor.text = 'exit 1'), /AMBIGUOUS_ANCHOR/],
  ['stale run bytes', (f) => (f.review.sites[0].run_sha256 = '0'.repeat(64)), /STALE_SITE/],
  ['stale job bytes', (f) => (f.review.sites[0].job_sha256 = '0'.repeat(64)), /STALE_SITE/],
  ['stale step bytes', (f) => (f.review.sites[0].step_sha256 = '0'.repeat(64)), /STALE_SITE/],
  ['traversal site path', (f) => (f.review.sites[0].workflow = '../outside'), /MALFORMED_SITE/],
  [
    'absolute policy path',
    (f) => (f.review.aggregate_policy.path = '/tmp/policy'),
    /STALE_AGGREGATE_POLICY/,
  ],
  [
    'single backslash path',
    (f) => (f.review.sites[0].workflow = 'one' + String.fromCharCode(92) + 'two'),
    /MALFORMED_SITE/,
  ],
  [
    'NUL path',
    (f) => (f.review.sites[0].workflow = 'one' + String.fromCharCode(0) + 'two'),
    /MALFORMED_SITE/,
  ],
  ['absolute site path', (f) => (f.review.sites[0].workflow = '/tmp/workflow'), /MALFORMED_SITE/],
  ['drive site path', (f) => (f.review.sites[0].workflow = 'C:/workflow'), /MALFORMED_SITE/],
  [
    'malformed authority',
    (f) => (f.review.sites[0].authority = ['invented']),
    /MALFORMED_OR_STALE_AUTHORITY/,
  ],
  [
    'missing authority',
    (f) => (f.review.sites[0].authority = []),
    /MISSING_CLASSIFICATION_AUTHORITY/,
  ],
  [
    'stale authority',
    (f) => (f.review.aggregate_policy.authority[0].text += 'stale'),
    /MALFORMED_OR_STALE_AUTHORITY/,
  ],
  ['invented owner', (f) => (f.review.sites[0].owner = 'historical-person'), /MALFORMED_SITE/],
  [
    'invented bounded classification',
    (f) => (f.review.sites[0].classification = 'bounded_correctness'),
    /MALFORMED_SITE/,
  ],
  [
    'stale marker',
    (f) => (f.review.sites[8].deadline_marker.line += 1000),
    /STALE_DEADLINE_MARKER/,
  ],
  [
    'repository clean assertion',
    (f) => (f.review.repository_complete = true),
    /MALFORMED_REGISTRY/,
  ],
  ['aggregate graph mismatch', (f) => (f.needs = f.needs.slice(1)), /UNPROVEN_CI_REQUIRED_GRAPH/],
  [
    'aggregate policy drift',
    (f) => (f.files[f.review.aggregate_policy.path] += '\n'),
    /STALE_AGGREGATE_POLICY/,
  ],
])
  test(`${name} yields unknown semantic counts`, () => {
    const f = fixture();
    mutate(f);
    unknown(inspect(f), reason);
  });

for (const [name, key, reason] of [
  ['conditional step', 'if', /UNCOVERED_TOPOLOGY/],
  ['suppressed step', 'continue-on-error', /UNREVIEWED_CONTINUE_ON_ERROR/],
])
  test(`new ${name} cannot silently inherit review`, () => {
    const f = fixture(),
      path = f.review.workflows[2].path;
    const workflow = yaml.load(f.files[path]);
    workflow.jobs.conform.steps[0][key] = true;
    f.files[path] = yaml.dump(workflow);
    rebindWorkflow(f, path);
    unknown(inspect(f), reason);
  });

test('new uncovered run container remains unknown even with refreshed outer hash', () => {
  const f = fixture(),
    path = f.review.workflows[2].path;
  const workflow = yaml.load(f.files[path]);
  workflow.jobs.conform.steps.push({ run: 'echo uncovered' });
  f.files[path] = yaml.dump(workflow);
  rebindWorkflow(f, path);
  unknown(inspect(f), /UNCOVERED_TOPOLOGY/);
});

test('unsupported shell cannot inherit a selected operation review', () => {
  const f = fixture(),
    path = f.review.workflows[0].path;
  const workflow = yaml.load(f.files[path]);
  const site = f.review.sites[0];
  workflow.jobs[site.job].steps[site.step].shell = 'python';
  f.files[path] = yaml.dump(workflow);
  rebindWorkflow(f, path);
  unknown(inspect(f), /STALE_SITE/);
});

test('malformed and duplicate-key YAML cannot produce clean counts', () => {
  for (const text of ['jobs: [', 'jobs: {}\njobs: {}\n']) {
    const f = fixture(),
      path = f.review.workflows[2].path;
    f.files[path] = text;
    rebindWorkflow(f, path);
    unknown(inspect(f), /UNKNOWN_CORRECTNESS_SWALLOW_COVERAGE/);
  }
});

test('malformed and duplicate-key registry JSON fail closed', () => {
  for (const raw of [
    '{',
    JSON.stringify(registry).replace('"schema_version":1', '"schema_version":1,"schema_version":1'),
  ]) {
    unknown(
      inspectCorrectnessSwallows({ reader: { text: () => raw }, requiredNeeds: null }),
      /UNKNOWN_CORRECTNESS_SWALLOW_COVERAGE/,
    );
  }
});

test('unsafe or unreadable snapshot inputs fail closed', () => {
  unknown(
    inspectCorrectnessSwallows({
      reader: {
        text: (p) => {
          if (p === SWALLOWS_REGISTRY) return JSON.stringify(registry);
          throw new Error('unsafe symlink');
        },
      },
      requiredNeeds: null,
    }),
    /MALFORMED_OR_UNREADABLE_INPUT/,
  );
});
