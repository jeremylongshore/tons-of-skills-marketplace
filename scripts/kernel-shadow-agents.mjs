#!/usr/bin/env node
/**
 * Composed agent-definition v1/v2 shadow (DR-049; advisory only).
 * Python and R1 remain authoritative. Raw comparisons include Python body and
 * enterprise checks: agreement is not proof of equivalent contract coverage.
 * Exit 0 for a complete observation, even with disagreements; exit 1 for
 * unavailable/partial evidence. The CI step always uses continue-on-error.
 */
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import yaml from 'js-yaml';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PIN = '0.10.0';
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const strings = (value) => Array.isArray(value) && value.every((item) => typeof item === 'string');
const hash = (value) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);

function loadSchemas() {
  const kernelRoot = join(ROOT, 'node_modules', '@intentsolutions', 'core');
  const installed = JSON.parse(readFileSync(join(kernelRoot, 'package.json'), 'utf8')).version;
  const declared = JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf8')).devDependencies?.[
    '@intentsolutions/core'
  ];
  if (installed !== PIN || declared !== PIN) {
    throw new Error(
      `kernel pin drift: expected ${PIN}, installed ${installed}, declared ${declared}`,
    );
  }
  return ['v1', 'v2'].map((family) => {
    const ajv = new Ajv2020({ allErrors: true, strict: false });
    addFormats(ajv);
    const schemas = [
      `upstream-base/agent-definition.${family}.json`,
      `is-overlay/agent-definition.${family}.json`,
      'marketplace-tier.schema.json',
      'agent-definition.schema.json',
    ].map((name) => {
      const path = `schemas/authoring/${family}/${name}`;
      const bytes = readFileSync(join(kernelRoot, path));
      const schema = JSON.parse(bytes);
      ajv.addSchema(schema);
      return { path, id: schema.$id, sha256: sha256(bytes) };
    });
    const composed = schemas.at(-1).id;
    return {
      family: `authoring/${family}`,
      composedSchema: composed,
      schemas,
      validate: ajv.getSchema(composed),
    };
  });
}

function loadPython() {
  const local = join(ROOT, '.venv', 'bin', 'python3');
  const run = spawnSync(
    existsSync(local) ? local : 'python3',
    ['-B', join(ROOT, 'scripts', 'kernel-shadow-agents.py')],
    {
      cwd: ROOT,
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
    },
  );
  if (run.error || run.status !== 0) {
    throw new Error(
      `Python observation failed: ${run.error?.message || run.stderr || `exit ${run.status}`}`,
    );
  }
  const payload = JSON.parse(run.stdout);
  if (
    payload?.schema_version !== 'agent-python-observation/v1' ||
    !['complete', 'partial'].includes(payload.status) ||
    typeof payload.validator_schema_version !== 'string' ||
    !hash(payload.validator_sha256) ||
    !Array.isArray(payload.rows) ||
    !payload.rows.length ||
    payload.discovered !== payload.rows.length
  )
    throw new Error('Invalid or empty Python inventory');
  const seen = new Set();
  for (const row of payload.rows) {
    if (
      typeof row?.path !== 'string' ||
      row.path.includes('\\') ||
      row.path.includes('\0') ||
      row.path.split('/').some((part) => ['', '.', '..'].includes(part)) ||
      seen.has(row.path) ||
      typeof row.available !== 'boolean'
    )
      throw new Error('Invalid or duplicate Python inventory path');
    seen.add(row.path);
    if (row.available) {
      if (
        !hash(row.content_sha256) ||
        !(row.frontmatter === null || typeof row.frontmatter === 'string') ||
        !(row.fatal === null || (typeof row.fatal === 'string' && row.fatal.length > 0)) ||
        !strings(row.errors) ||
        !strings(row.warnings)
      ) {
        throw new Error(`Malformed Python verdict: ${row.path}`);
      }
    } else if (typeof row.reason !== 'string' || !row.reason) {
      throw new Error(`Missing unavailable reason: ${row.path}`);
    }
  }
  if ((payload.status === 'complete') !== payload.rows.every((row) => row.available)) {
    throw new Error('Python completeness contradicts inventory');
  }
  payload.rows.sort((a, b) => a.path.localeCompare(b.path, 'en'));
  return payload;
}

function frontmatter(text) {
  try {
    if (text === null) throw new Error('No frontmatter found');
    const data = yaml.load(text);
    if (data === null || typeof data !== 'object' || Array.isArray(data)) {
      throw new Error('Frontmatter is not a mapping');
    }
    return { data };
  } catch (error) {
    return { error: error.message };
  }
}

function observe(report) {
  const validators = loadSchemas();
  const python = loadPython();
  report.python = {
    adapter: 'scripts/kernel-shadow-agents.py',
    validator: 'scripts/validate-skills-schema.py',
    schemaVersion: python.validator_schema_version,
    sha256: python.validator_sha256,
  };
  report.inventory = {
    discovered: python.discovered,
    sha256: sha256(
      JSON.stringify(python.rows.map((row) => [row.path, row.content_sha256 ?? null])),
    ),
  };
  report.status = python.status;
  report.rows = python.rows.map((row) => ({
    path: row.path,
    contentSha256: row.content_sha256 ?? null,
    python: row.available
      ? {
          verdict: row.fatal ? 'FATAL' : row.errors.length ? 'FAIL' : 'PASS',
          fatal: row.fatal,
          errors: row.errors,
          warnings: row.warnings,
        }
      : { verdict: 'UNAVAILABLE', reason: row.reason },
    kernels: {},
  }));
  for (const lane of validators) {
    const counts = {
      compared: 0,
      unavailable: 0,
      parseFailures: 0,
      bothPass: 0,
      bothFail: 0,
      existingPassKernelFail: 0,
      existingFailKernelPass: 0,
    };
    python.rows.forEach((row, index) => {
      const output = report.rows[index];
      if (!row.available) {
        counts.unavailable += 1;
        output.kernels[lane.family] = { verdict: 'UNAVAILABLE' };
        return;
      }
      const parsed = frontmatter(row.frontmatter);
      const pass = !parsed.error && lane.validate(parsed.data);
      counts.compared += 1;
      if (parsed.error) counts.parseFailures += 1;
      output.kernels[lane.family] = {
        verdict: pass ? 'PASS' : 'FAIL',
        parseError: parsed.error ?? null,
        errors: parsed.error ? [] : globalThis.structuredClone(lane.validate.errors ?? []),
      };
      const existingPass = output.python.verdict === 'PASS';
      const counter = existingPass
        ? pass
          ? 'bothPass'
          : 'existingPassKernelFail'
        : pass
          ? 'existingFailKernelPass'
          : 'bothFail';
      counts[counter] += 1;
    });
    report.lanes[lane.family] = {
      composedSchema: lane.composedSchema,
      schemas: lane.schemas,
      counts,
    };
  }
}

function main() {
  const git = spawnSync('git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8' });
  const status = spawnSync('git', ['status', '--porcelain', '--untracked-files=normal'], {
    cwd: ROOT,
    encoding: 'utf8',
  });
  const report = {
    schemaVersion: 'agent-kernel-shadow/v1',
    mode: 'shadow-advisory',
    blocking: false,
    status: 'unavailable',
    observedAt: new Date().toISOString(),
    sourceCommit: git.status === 0 ? git.stdout.trim() : null,
    sourceDirty: status.status === 0 ? status.stdout.length > 0 : null,
    implementation: [],
    kernelPackage: '@intentsolutions/core',
    kernelPin: PIN,
    scopeNote:
      'RAW verdict comparisons: Python includes enterprise and body/tool checks; kernels validate frontmatter only. Python-FAIL/kernel-PASS may be a scope difference. Both failing does not establish equivalent rules. No authority flip or clean-corpus claim follows from this report.',
    inventory: null,
    python: null,
    lanes: {},
    rows: [],
    harnessErrors: [],
  };
  try {
    report.implementation = ['kernel-shadow-agents.mjs', 'kernel-shadow-agents.py'].map((name) => ({
      path: `scripts/${name}`,
      sha256: sha256(readFileSync(join(ROOT, 'scripts', name))),
    }));
    observe(report);
  } catch (error) {
    report.status = report.inventory ? 'partial' : 'unavailable';
    report.harnessErrors.push(error.message);
  }
  const lines = [
    '### Agent kernel shadow — advisory',
    '',
    `Evidence: **${report.status}**. Python/R1 remain authoritative.`,
    '',
    report.scopeNote,
    '',
  ];
  for (const family of ['authoring/v2', 'authoring/v1']) {
    const counts = report.lanes[family]?.counts;
    if (counts)
      lines.push(
        `${family}: Python-PASS/kernel-FAIL **${counts.existingPassKernelFail}**; Python-FAIL/kernel-PASS ${counts.existingFailKernelPass}; both PASS ${counts.bothPass}; both FAIL ${counts.bothFail}; compared ${counts.compared}/${report.inventory.discovered}; unavailable ${counts.unavailable}; unparseable ${counts.parseFailures}.`,
        '',
      );
  }
  for (const error of report.harnessErrors) lines.push(`Harness error: ${error}`, '');
  const dir = join(ROOT, 'scripts', '.kernel-shadow');
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'agents-report.json'), JSON.stringify(report, null, 2) + '\n');
  const summary = lines.join('\n') + '\n';
  console.log(summary);
  if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary);
  process.exitCode = report.status === 'complete' && !report.harnessErrors.length ? 0 : 1;
}

main();
