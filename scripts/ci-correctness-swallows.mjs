/** Pure, byte-bound review reader. This is not a shell interpreter or a CI gate. */
import { createHash } from 'node:crypto';
import yaml from 'js-yaml';

export const SWALLOWS_REGISTRY = 'scripts/ci-correctness-swallows.json';
const WORKFLOWS = [
  '.github/workflows/validate-plugins.yml',
  '.github/workflows/secret-scan.yml',
  '.github/workflows/skill-conform.yml',
];
const POLICY = 'scripts/ci/fastlane.py';
const CLASSES = ['authorized_control_flow', 'informational', 'unbounded_correctness', 'unresolved'];
const LIMITATIONS = [
  'Partial static review only: no shell interpretation, execution, or runtime coverage proof.',
  'Opaque actions, invoked-script internals, unsupported shell and broad conditions remain coverage gaps.',
  'Historical issue references do not establish current owners; observed dates are not expiry adjudications.',
  'Coverage gaps overlap and are not additive; primary and repository totals remain unknown.',
];
class ReviewError extends Error {}
const hash = (text) => createHash('sha256').update(text).digest('hex');
// Typed YAML values, independent of mapping insertion order. Raw workflow hashes also bind comments.
function typed(value) {
  if (Array.isArray(value)) return `[${value.map(typed).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${typed(value[key])}`)
      .join(',')}}`;
  }
  return JSON.stringify(value);
}
const safePath = (path) =>
  typeof path === 'string' &&
  !path.startsWith('/') &&
  !/^[A-Za-z]:/.test(path) &&
  !path.includes('\\') &&
  !path.includes('\0') &&
  path.split('/').every((part) => part && part !== '.' && part !== '..');
function unknown(reason) {
  return {
    valid: false,
    reason,
    values: {
      unbounded_correctness_total: null,
      repository_unbounded_total: null,
      reviewed_unbounded_correctness_lower_bound: null,
      site_counts: null,
      coverage: null,
      target: 0,
      target_met: false,
    },
    limitations: LIMITATIONS,
  };
}

/** reader.text must use the caller's immutable, tracked, symlink-safe snapshot. */
export function inspectCorrectnessSwallows({ reader, requiredNeeds }) {
  const read = (path) => {
    if (!safePath(path)) throw new ReviewError('UNSAFE_REGISTRY_PATH');
    const value = reader.text(path);
    if (typeof value !== 'string') throw new ReviewError(`MISSING_OR_UNSAFE_INPUT:${path}`);
    return value;
  };
  try {
    const raw = reader.text(SWALLOWS_REGISTRY);
    if (raw === null) return unknown('MISSING_CORRECTNESS_CRITICAL_COMMAND_REGISTRY');
    // JSON syntax plus YAML's duplicate-key rejection; JSON.parse alone silently accepts duplicates.
    const registry = JSON.parse(raw);
    yaml.load(raw, { schema: yaml.JSON_SCHEMA });
    if (
      registry?.schema_version !== 1 ||
      registry.repository_complete !== false ||
      !Array.isArray(registry.workflows) ||
      !Array.isArray(registry.sites)
    )
      throw new ReviewError('MALFORMED_REGISTRY');
    if (
      registry.workflows.length !== WORKFLOWS.length ||
      new Set(registry.workflows.map((w) => w.path)).size !== WORKFLOWS.length ||
      WORKFLOWS.some((path) => !registry.workflows.some((w) => w.path === path))
    )
      throw new ReviewError('INCOMPLETE_WORKFLOW_SCOPE');
    if (
      registry.aggregate_policy?.path !== POLICY ||
      hash(read(POLICY)) !== registry.aggregate_policy.sha256
    )
      throw new ReviewError('STALE_AGGREGATE_POLICY');
    const validateAuthority = (refs) => {
      if (!Array.isArray(refs)) throw new ReviewError('MALFORMED_AUTHORITY');
      for (const ref of refs) {
        if (
          !ref ||
          !safePath(ref.path) ||
          !Number.isInteger(ref.line) ||
          ref.line < 1 ||
          typeof ref.text !== 'string' ||
          !ref.text.trim() ||
          read(ref.path).split('\n')[ref.line - 1] !== ref.text
        )
          throw new ReviewError('MALFORMED_OR_STALE_AUTHORITY');
      }
    };
    validateAuthority(registry.aggregate_policy.authority);
    const parsed = new Map();
    const sources = new Map();
    const coverage = {
      workflows: 0,
      jobs: 0,
      containers: 0,
      run_containers: 0,
      opaque_actions: 0,
      conditional_envelopes: 0,
    };
    for (const workflow of registry.workflows) {
      const source = read(workflow.path);
      if (hash(source) !== workflow.sha256)
        throw new ReviewError(`STALE_WORKFLOW:${workflow.path}`);
      const data = yaml.load(source);
      if (!data?.jobs || typeof data.jobs !== 'object' || Array.isArray(data.jobs))
        throw new ReviewError('MALFORMED_WORKFLOW');
      parsed.set(workflow.path, data);
      sources.set(workflow.path, source);
      coverage.workflows++;
      for (const job of Object.values(data.jobs)) {
        if (!job || typeof job !== 'object' || !Array.isArray(job.steps))
          throw new ReviewError('UNSUPPORTED_JOB_TOPOLOGY');
        coverage.jobs++;
        if (Object.hasOwn(job, 'if')) coverage.conditional_envelopes++;
        if (Object.hasOwn(job, 'continue-on-error'))
          throw new ReviewError('UNREVIEWED_CONTINUE_ON_ERROR');
        for (const step of job.steps) {
          if (
            !step ||
            typeof step !== 'object' ||
            (typeof step.run === 'string') === (typeof step.uses === 'string')
          )
            throw new ReviewError('MALFORMED_STEP');
          if (Object.hasOwn(step, 'continue-on-error'))
            throw new ReviewError('UNREVIEWED_CONTINUE_ON_ERROR');
          coverage.containers++;
          coverage[typeof step.run === 'string' ? 'run_containers' : 'opaque_actions']++;
          if (Object.hasOwn(step, 'if')) coverage.conditional_envelopes++;
        }
      }
    }
    const jobs = parsed.get(WORKFLOWS[0]).jobs;
    const graph = jobs['ci-required']?.needs;
    if (
      requiredNeeds?.error ||
      !Array.isArray(requiredNeeds?.needs) ||
      !Array.isArray(graph) ||
      new Set(graph).size !== graph.length ||
      typed([...graph].sort()) !== typed([...requiredNeeds.needs].sort()) ||
      typed(Object.keys(jobs).sort()) !== typed([...graph, 'ci-required'].sort()) ||
      graph.includes('skill-conform')
    )
      throw new ReviewError('UNPROVEN_CI_REQUIRED_GRAPH');
    for (const [key, count] of Object.entries(coverage))
      if (registry.expected?.[key] !== count) throw new ReviewError(`UNCOVERED_TOPOLOGY:${key}`);
    const ids = new Set();
    const anchors = new Set();
    const containers = new Set();
    const counts = Object.fromEntries(CLASSES.map((key) => [key, 0]));
    const sites = [];
    for (const site of registry.sites) {
      if (typeof site.id !== 'string' || !site.id || ids.has(site.id))
        throw new ReviewError('DUPLICATE_OR_MISSING_SITE');
      ids.add(site.id);
      if (
        !safePath(site.workflow) ||
        !parsed.has(site.workflow) ||
        !Number.isInteger(site.step) ||
        site.step < 0 ||
        !CLASSES.includes(site.classification) ||
        typeof site.rationale !== 'string' ||
        !site.rationale ||
        site.owner !== null ||
        site.promotion !== null ||
        !Array.isArray(site.authority)
      )
        throw new ReviewError('MALFORMED_SITE');
      validateAuthority(site.authority);
      if (
        ['authorized_control_flow', 'informational'].includes(site.classification) &&
        site.authority.length === 0
      )
        throw new ReviewError('MISSING_CLASSIFICATION_AUTHORITY');
      const job = parsed.get(site.workflow).jobs[site.job];
      const step = job?.steps?.[site.step];
      if (
        !step ||
        typeof step.run !== 'string' ||
        step.name !== site.step_name ||
        hash(typed(job)) !== site.job_sha256 ||
        hash(typed(step)) !== site.step_sha256 ||
        hash(step.run) !== site.run_sha256
      )
        throw new ReviewError(`STALE_SITE:${site.id}`);
      const lines = step.run.split('\n');
      const anchor = site.anchor;
      if (
        !anchor ||
        !Number.isInteger(anchor.line) ||
        anchor.line < 1 ||
        typeof anchor.text !== 'string' ||
        !anchor.text.trim() ||
        lines[anchor.line - 1] !== anchor.text ||
        lines.filter((line) => line === anchor.text).length !== 1
      )
        throw new ReviewError(`AMBIGUOUS_ANCHOR:${site.id}`);
      const key = `${site.workflow}:${site.job}:${site.step}`;
      const anchorKey = `${key}:${anchor.line}`;
      if (anchors.has(anchorKey)) throw new ReviewError('DUPLICATE_OPERATION_SITE');
      anchors.add(anchorKey);
      containers.add(key);
      let deadline = null;
      if (site.deadline_marker !== null) {
        const marker = site.deadline_marker;
        const sourceLine = sources.get(site.workflow).split('\n')[marker?.line - 1];
        if (
          !Number.isInteger(marker?.line) ||
          marker.line < 1 ||
          typeof sourceLine !== 'string' ||
          hash(sourceLine) !== marker.sha256
        )
          throw new ReviewError('STALE_DEADLINE_MARKER');
        const match = sourceLine.match(/^\s*# REPORT-ONLY-UNTIL: (\d{4}-\d{2}-\d{2})(?:\s|$)/);
        if (!match) throw new ReviewError('MALFORMED_DEADLINE_MARKER');
        deadline = { date: match[1], source_line: marker.line, expiry_adjudicated: false };
      }
      counts[site.classification]++;
      sites.push({
        id: site.id,
        workflow: site.workflow,
        job: site.job,
        step: site.step,
        run_line: anchor.line,
        classification: site.classification,
        rationale: site.rationale,
        owner: null,
        promotion: null,
        authority: site.authority,
        observed_deadline: deadline,
      });
    }
    if (
      registry.expected.sites !== sites.length ||
      registry.expected.site_containers !== containers.size
    )
      throw new ReviewError('INCOMPLETE_SITE_COVERAGE');
    return {
      valid: true,
      values: {
        unbounded_correctness_total: null,
        repository_unbounded_total: null,
        reviewed_unbounded_correctness_lower_bound: counts.unbounded_correctness,
        site_counts: counts,
        coverage: {
          ...coverage,
          containers_with_sites: containers.size,
          unreviewed_run_containers: coverage.run_containers - containers.size,
          counts_overlap: true,
        },
        sites,
        target: 0,
        target_met: false,
      },
      limitations: LIMITATIONS,
    };
  } catch (error) {
    return unknown(
      `UNKNOWN_CORRECTNESS_SWALLOW_COVERAGE:${error instanceof ReviewError ? error.message : 'MALFORMED_OR_UNREADABLE_INPUT'}`,
    );
  }
}
