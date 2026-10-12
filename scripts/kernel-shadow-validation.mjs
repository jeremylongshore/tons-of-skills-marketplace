#!/usr/bin/env node
/**
 * kernel-shadow-validation.mjs — DR-049 dual-validator shadow mode (ADVISORY ONLY)
 *
 * Consumer-cutover STEP 1 for @intentsolutions/core (the Spec Authority Kernel).
 *
 * WHAT THIS IS
 * ------------
 * Runs the kernel's published machine-specs — the authoring/v1 and strict
 * authoring/v2 `skill-frontmatter` JSON Schemas from @intentsolutions/core@0.10.0 —
 * over the SAME SKILL.md corpus the
 * existing prose-spec validator (scripts/validate-skills-schema.py) already grades,
 * and reports the per-file AGREE / DISAGREE rate between the two.
 *
 * This is a SHADOW. It NEVER gates, NEVER mutates, NEVER replaces the existing
 * validator. It compares two independent encodings of the SAME contract:
 *
 *   - prose-spec  : the 5,100-line validate-skills-schema.py, MARKETPLACE tier
 *                   (the IS 8-field required set is an ERROR-on-missing there).
 *   - machine-spec: @intentsolutions/core schemas/authoring/v1 and v2
 *                   skill-frontmatter.schema.json compositions. v1 is the published
 *                   baseline; v2 is the strict, decision-relevant cutover candidate.
 *
 * The two are deliberately tier-matched: both require the 8-field marketplace set
 * {name, description, allowed-tools, version, author, license, compatibility, tags}.
 *
 * SCOPE DISTINCTION — WHY THE RAW DEVIATION IS NOT THE CUTOVER SIGNAL
 * ------------------------------------------------------------------
 * The kernel `skill-frontmatter` schema is a FRONTMATTER CONTRACT only — it grades
 * the YAML frontmatter block and nothing else. The prose-spec validator grades BOTH
 * the frontmatter AND the markdown BODY (required `## Overview` / `## Instructions` /
 * `## Output` / … sections at marketplace tier; body errors are prefixed `[body]`).
 *
 * So the RAW per-file PASS/FAIL deviation conflates two different scopes: a file with
 * valid frontmatter but missing body sections is existing-FAIL (the prose-spec fails it
 * on `[body]` errors) yet kernel-PASS (the frontmatter is genuinely valid). That is NOT
 * a kernel gap — it is a SCOPE DIFFERENCE. Body-section linting is the prose-spec
 * validator's separate concern, deliberately outside the kernel's frontmatter contract.
 *
 * This shadow therefore scopes the existing-validator verdict to FRONTMATTER (the
 * kernel's actual scope) and emits BOTH numbers:
 *
 *   - frontmatterDeviationPct : the CUTOVER-RELEVANT signal. A file counts as a
 *                               frontmatter deviation only when the kernel and the
 *                               FRONTMATTER-SCOPED prose-spec verdict disagree. The
 *                               frontmatter-scoped existing verdict is PASS iff the file
 *                               has zero NON-`[body]` errors (i.e. every `[body]`-prefixed
 *                               error is filtered out before counting). A near-zero value
 *                               here is the "zero-on-corpus shadow signal" from DR-049 and
 *                               the precondition for any future blocking cutover (NOT this PR).
 *   - bodyScopeOnlyCount      : INFORMATIONAL. The count of files the kernel passes that
 *                               the prose-spec validator fails on BODY sections ONLY
 *                               (every error is `[body]`-prefixed). NOT a kernel gap — a
 *                               scope difference. These are excluded from the frontmatter
 *                               deviation because the kernel never claimed to lint the body.
 *
 * VERDICT DEFINITIONS (per file)
 * ------------------------------
 *   kernel-PASS        := ajv validate against the composed skill-frontmatter schema == true.
 *   existing-PASS-raw  := validate-skills-schema.py --marketplace reports errors == 0
 *                         (a `fatal` entry counts as existing-FAIL).
 *   existing-PASS-fm   := the file has ZERO non-`[body]` errors (frontmatter-scoped PASS).
 *                         Computed from the batch `error_details` error strings and filtering
 *                         out every error message starting with `[body]`.
 *   RAW DISAGREE       := existing-PASS-raw !== kernel-PASS (conflates frontmatter + body).
 *   FRONTMATTER DISAGREE := existing-PASS-fm !== kernel-PASS (the cutover-relevant deviation;
 *                         a remaining one here would be a REAL kernel gap to surface).
 *   BODY-SCOPE-ONLY    := existing-FAIL-raw && kernel-PASS && every error is `[body]` (a scope
 *                         difference, NOT a deviation).
 *
 * The batch `--json` run includes `error_details`, the full error-string array per file.
 * The single-file form is retained only as a compatibility fallback for older output.
 *
 * OUTPUT
 * ------
 *   - Human summary + FRONTMATTER-DISAGREE listing + body-scope count to stdout.
 *   - Machine report JSON to scripts/.kernel-shadow/report.json (CI artifact).
 *   - GitHub Step Summary markdown when $GITHUB_STEP_SUMMARY is set.
 *
 * EXIT CODE
 * ---------
 *   Always 0 on a successful run (advisory). A non-zero exit only happens on a
 *   harness error (e.g. the kernel package or the existing validator is missing) —
 *   and even then the calling workflow uses continue-on-error so it can NEVER fail
 *   the build. The deviation rate itself is REPORTED, never enforced.
 *
 * KERNEL PIN: @intentsolutions/core is pinned EXACTLY to 0.10.0 in package.json
 * (no ^/~). This shadow reads the schema straight out of node_modules so the
 * comparison is always against the pinned, published contract.
 *
 * Beads: bd_000-projects-26ef (dual-validator shadow mode).
 */

import { spawnSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import yaml from 'js-yaml';
import { collectRegistryShadow, registrySummaryLines } from './kernel-shadow-registry.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..');
const KERNEL_PIN = '0.10.0';

// Each composed skill-frontmatter contract is a pure allOf of three $ref'd layers.
// ajv resolves $ref by $id, so every layer must be registered. marketplace-tier
// supplies the universalFolds $def the composition references.
const LANES = [
  {
    id: 'authoring/v1',
    strict: false,
    files: [
      'upstream-base/skill-frontmatter.v1.json',
      'is-overlay/skill-frontmatter.v1.json',
      'marketplace-tier.schema.json',
      'skill-frontmatter.schema.json',
    ],
    schemaId:
      'https://github.com/jeremylongshore/intent-eval-core/schemas/authoring/v1/skill-frontmatter.schema.json',
  },
  {
    id: 'authoring/v2',
    strict: true,
    files: [
      'upstream-base/skill-frontmatter.v1.json',
      'is-overlay/skill-frontmatter.v2.json',
      'marketplace-tier.schema.json',
      'skill-frontmatter.schema.json',
    ],
    schemaId:
      'https://github.com/jeremylongshore/intent-eval-core/schemas/authoring/v2/skill-frontmatter.schema.json',
  },
];

const FRONTMATTER_RE = /^---\s*\n([\s\S]*?)\n---\s*\n/;

function die(msg) {
  console.error(`[kernel-shadow] HARNESS ERROR: ${msg}`);
  process.exit(1);
}

function loadKernelVersion() {
  const pkgPath = join(REPO_ROOT, 'node_modules', '@intentsolutions', 'core', 'package.json');
  if (!existsSync(pkgPath)) {
    die(
      `@intentsolutions/core not installed at ${pkgPath}. Run: pnpm install --filter claude-code-plugins-monorepo`,
    );
  }
  const v = JSON.parse(readFileSync(pkgPath, 'utf8')).version;
  if (v !== KERNEL_PIN) {
    die(
      `kernel version drift: expected EXACTLY ${KERNEL_PIN} (the pinned contract), found ${v}. ` +
        `package.json must pin @intentsolutions/core to an exact version, never a range.`,
    );
  }
  return v;
}

function buildKernelValidator(lane) {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  const schemaDir = join(
    REPO_ROOT,
    'node_modules',
    '@intentsolutions',
    'core',
    'schemas',
    'authoring',
    lane.id.slice('authoring/'.length),
  );
  for (const rel of lane.files) {
    const p = join(schemaDir, rel);
    if (!existsSync(p)) {
      die(
        `${lane.id} kernel schema layer missing: ${p}. Is @intentsolutions/core@${KERNEL_PIN} intact?`,
      );
    }
    ajv.addSchema(JSON.parse(readFileSync(p, 'utf8')));
  }
  const validate = ajv.getSchema(lane.schemaId);
  if (!validate) {
    die(`could not resolve ${lane.id} composed schema by $id ${lane.schemaId}`);
  }
  return validate;
}

/**
 * Resolve the python interpreter (prefer the venv — the validator needs pyyaml) and
 * the validator script path. Shared by the batch run and the per-file string fetch.
 */
function resolvePythonContext() {
  const venvPy = join(REPO_ROOT, '.venv', 'bin', 'python3');
  const py = existsSync(venvPy) ? venvPy : 'python3';
  const script = join(REPO_ROOT, 'scripts', 'validate-skills-schema.py');
  if (!existsSync(script)) {
    die(`existing validator not found at ${script}`);
  }
  return { py, script };
}

/**
 * Drive the existing prose-spec validator (batch mode) to get its per-file MARKETPLACE
 * verdict and batch error strings.
 * Returns per-file verdicts and the separate advisory field-registry evidence.
 */
function loadExistingVerdicts(py, script) {
  const res = spawnSync(py, [script, '--marketplace', '--json'], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    maxBuffer: 256 * 1024 * 1024,
  });
  if (res.error) {
    die(`failed to spawn existing validator: ${res.error.message}`);
  }
  // The validator may exit non-zero on findings; --json still emits the array on stdout.
  let parsed;
  try {
    parsed = JSON.parse(res.stdout);
  } catch {
    die(
      `could not parse existing validator --json output (exit ${res.status}). ` +
        `stderr head: ${(res.stderr || '').slice(0, 400)}`,
    );
  }
  if (!Array.isArray(parsed)) die('existing validator --json output is not an array');
  const registryShadow = collectRegistryShadow(parsed);
  const map = new Map();
  for (const entry of parsed) {
    // Registry evidence is retained separately; it is never a corpus file.
    if (!entry || Object.hasOwn(entry, 'kernel_shadow') || typeof entry.path !== 'string') continue;
    const abs = resolve(REPO_ROOT, entry.path);
    if ('fatal' in entry) {
      map.set(abs, { pass: false, errors: 0, errorStrings: null, fatal: true });
    } else {
      const errors = entry.errors ?? 0;
      const errorStrings = Array.isArray(entry.error_details)
        ? entry.error_details.map(String)
        : null;
      map.set(abs, { pass: errors === 0, errors, errorStrings, fatal: false });
    }
  }
  return { verdicts: map, registryShadow };
}

const BODY_PREFIX = '[body]';

/**
 * Is every error in the list a body-section error? (`[body]`-prefixed). An empty
 * list is vacuously body-only-FALSE in the way that matters: callers only ask this
 * when the file is existing-FAIL, so there is at least one error.
 */
function allErrorsAreBodyScope(errorStrings) {
  return errorStrings.length > 0 && errorStrings.every((e) => String(e).startsWith(BODY_PREFIX));
}

/** Count errors that are NOT body-section errors — the frontmatter-scoped error count. */
function nonBodyErrorCount(errorStrings) {
  return errorStrings.filter((e) => !String(e).startsWith(BODY_PREFIX)).length;
}

/**
 * Fetch the full per-file error STRING list from the existing validator.
 *
 * Older validator output may omit batch `error_details`; the SINGLE-FILE `--json`
 * invocation supplies the same strings as a backward-compatible fallback.
 *
 * Returns { ok: true, errors: string[] } or { ok: false, reason } on a harness hiccup
 * (the caller degrades gracefully — an unscopable file stays a raw disagreement).
 */
function fetchFileErrorStrings(pyInterp, scriptPath, absPath) {
  const res = spawnSync(pyInterp, [scriptPath, '--marketplace', '--json', absPath], {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    maxBuffer: 32 * 1024 * 1024,
  });
  if (res.error) {
    return { ok: false, reason: `spawn failed: ${res.error.message}` };
  }
  let parsed;
  try {
    parsed = JSON.parse(res.stdout);
  } catch {
    return { ok: false, reason: `unparseable single-file --json (exit ${res.status})` };
  }
  const entry = Array.isArray(parsed) ? parsed[0] : parsed;
  if (!entry) {
    return { ok: false, reason: 'empty single-file --json result' };
  }
  if ('fatal' in entry) {
    // A fatal file has no scopable error list — treat as not-body-only (stays a deviation).
    return { ok: true, errors: [`[fatal] ${entry.fatal}`] };
  }
  const errs = Array.isArray(entry.errors) ? entry.errors.map(String) : [];
  return { ok: true, errors: errs };
}

function parseFrontmatter(absPath) {
  let content;
  try {
    content = readFileSync(absPath, 'utf8');
  } catch (e) {
    return { ok: false, reason: `unreadable: ${e.message}` };
  }
  const m = FRONTMATTER_RE.exec(content);
  if (!m) {
    return { ok: false, reason: 'no YAML frontmatter block' };
  }
  let data;
  try {
    data = yaml.load(m[1]);
  } catch (e) {
    return { ok: false, reason: `YAML parse error: ${e.message}` };
  }
  if (data === null || typeof data !== 'object' || Array.isArray(data)) {
    return { ok: false, reason: 'frontmatter is not a mapping' };
  }
  return { ok: true, data };
}

function relTo(absPath) {
  return absPath.startsWith(REPO_ROOT + '/') ? absPath.slice(REPO_ROOT.length + 1) : absPath;
}

function main() {
  const kernelVersion = loadKernelVersion();
  const validateKernel = buildKernelValidator(LANES[0]);
  const validateStrictKernel = buildKernelValidator(LANES[1]);
  const { py, script } = resolvePythonContext();
  const { verdicts: existing, registryShadow } = loadExistingVerdicts(py, script);

  let total = 0;
  let agree = 0;
  // RAW disagreements (conflate frontmatter + body scope).
  const rawDisagreements = [];
  // The strict v2 lane deliberately gets its own raw comparison. Its
  // existing-PASS / kernel-FAIL count is the only decision-relevant number for
  // a future authority flip: it identifies files the current required validator
  // accepts but the strict candidate would newly reject.
  const strictDisagreements = [];
  let kernelParseFailures = 0;
  let strictKernelParseFailures = 0;

  for (const [absPath, ex] of existing.entries()) {
    total += 1;
    const fm = parseFrontmatter(absPath);

    let kernelPass;
    let kernelErrors = [];
    let strictKernelPass;
    let strictKernelErrors = [];
    if (!fm.ok) {
      // The kernel schema cannot validate a file with no parseable frontmatter
      // mapping; treat as kernel-FAIL (matches the prose-spec's fatal handling).
      kernelPass = false;
      kernelErrors = [{ instancePath: '', message: fm.reason }];
      strictKernelPass = false;
      strictKernelErrors = [{ instancePath: '', message: fm.reason }];
      kernelParseFailures += 1;
      strictKernelParseFailures += 1;
    } else {
      kernelPass = validateKernel(fm.data) === true;
      if (!kernelPass) {
        kernelErrors = (validateKernel.errors || []).map((e) => ({
          instancePath: e.instancePath,
          message: e.message,
          params: e.params,
        }));
      }
      strictKernelPass = validateStrictKernel(fm.data) === true;
      if (!strictKernelPass) {
        strictKernelErrors = (validateStrictKernel.errors || []).map((e) => ({
          instancePath: e.instancePath,
          message: e.message,
          params: e.params,
        }));
      }
    }

    if (ex.pass === kernelPass) {
      agree += 1;
    } else {
      rawDisagreements.push({
        absPath,
        path: relTo(absPath),
        existing: ex.pass ? 'PASS' : ex.fatal ? 'FATAL' : 'FAIL',
        existingErrorCount: ex.errors,
        errorStrings: ex.errorStrings,
        kernel: kernelPass ? 'PASS' : 'FAIL',
        kernelPass,
        kernelErrors: kernelErrors.slice(0, 6),
        direction: ex.pass ? 'existing-PASS / kernel-FAIL' : 'existing-FAIL / kernel-PASS',
      });
    }
    if (ex.pass !== strictKernelPass) {
      strictDisagreements.push({
        path: relTo(absPath),
        existing: ex.pass ? 'PASS' : ex.fatal ? 'FATAL' : 'FAIL',
        existingErrorCount: ex.errors,
        kernel: strictKernelPass ? 'PASS' : 'FAIL',
        kernelErrors: strictKernelErrors.slice(0, 6),
        direction: ex.pass ? 'existing-PASS / kernel-FAIL' : 'existing-FAIL / kernel-PASS',
      });
    }
  }

  // ---- RAW (scope-conflated) deviation ----
  const rawDisagree = rawDisagreements.length;
  const rawRate = total === 0 ? 0 : (rawDisagree / total) * 100;
  const rawRateStr = rawRate.toFixed(2);

  // ---- FRONTMATTER-SCOPED deviation ----
  // The kernel is a FRONTMATTER contract; the prose-spec also lints the BODY. A raw
  // existing-FAIL / kernel-PASS file is a frontmatter deviation ONLY if the prose-spec
  // failure is NOT body-only. Use batch error strings and fall back to a single-file
  // lookup only when an older validator omits them.
  let bodyScopeOnlyCount = 0; // kernel-PASS, existing-FAIL on BODY sections only (a scope diff, not a deviation)
  const bodyScopeOnlyFiles = [];
  const frontmatterDisagreements = []; // the cutover-relevant set (REAL kernel gaps if any remain)

  for (const d of rawDisagreements) {
    if (d.direction === 'existing-FAIL / kernel-PASS') {
      // Could be a pure body-scope difference. Prefer the batch strings.
      const fetched =
        d.errorStrings !== null
          ? { ok: true, errors: d.errorStrings }
          : fetchFileErrorStrings(py, script, d.absPath);
      if (fetched.ok) {
        const bodyOnly = allErrorsAreBodyScope(fetched.errors);
        const fmErrCount = nonBodyErrorCount(fetched.errors);
        if (bodyOnly) {
          // Kernel passes valid frontmatter; prose-spec fails on missing body sections only.
          // NOT a kernel gap — a scope difference. Excluded from frontmatter deviation.
          bodyScopeOnlyCount += 1;
          bodyScopeOnlyFiles.push({
            path: d.path,
            existingErrorCount: d.existingErrorCount,
            sampleBodyErrors: fetched.errors.slice(0, 4),
          });
          continue;
        }
        // Frontmatter-scoped existing verdict is FAIL (non-body errors remain) while the
        // kernel PASSES → a genuine frontmatter disagreement (real kernel gap to surface).
        frontmatterDisagreements.push({
          path: d.path,
          existing: d.existing,
          existingErrorCount: d.existingErrorCount,
          existingNonBodyErrorCount: fmErrCount,
          kernel: d.kernel,
          sampleNonBodyErrors: fetched.errors
            .filter((e) => !String(e).startsWith(BODY_PREFIX))
            .slice(0, 6),
          direction: d.direction,
        });
      } else {
        // Could not scope this file — keep it as a frontmatter disagreement conservatively
        // (do not silently absorb an unscopable file into body-scope).
        frontmatterDisagreements.push({
          path: d.path,
          existing: d.existing,
          existingErrorCount: d.existingErrorCount,
          existingNonBodyErrorCount: null,
          kernel: d.kernel,
          scopeFetchError: fetched.reason,
          direction: d.direction,
        });
      }
    } else {
      // existing-PASS / kernel-FAIL: the prose-spec passed (zero errors, so zero `[body]`
      // errors too) but the kernel rejected the frontmatter. This is ALWAYS a frontmatter
      // disagreement regardless of scope — the kernel is stricter on the frontmatter here.
      frontmatterDisagreements.push({
        path: d.path,
        existing: d.existing,
        existingErrorCount: d.existingErrorCount,
        existingNonBodyErrorCount: 0,
        kernel: d.kernel,
        kernelErrors: d.kernelErrors,
        direction: d.direction,
      });
    }
  }

  const frontmatterDisagree = frontmatterDisagreements.length;
  const frontmatterRate = total === 0 ? 0 : (frontmatterDisagree / total) * 100;
  const frontmatterRateStr = frontmatterRate.toFixed(2);

  // Direction breakdown (raw).
  const existingPassKernelFail = rawDisagreements.filter(
    (d) => d.direction === 'existing-PASS / kernel-FAIL',
  ).length;
  const existingFailKernelPass = rawDisagreements.filter(
    (d) => d.direction === 'existing-FAIL / kernel-PASS',
  ).length;
  const strictExistingPassKernelFail = strictDisagreements.filter(
    (d) => d.direction === 'existing-PASS / kernel-FAIL',
  ).length;
  const strictExistingFailKernelPass = strictDisagreements.length - strictExistingPassKernelFail;
  const strictDecisionRate = total === 0 ? 0 : (strictExistingPassKernelFail / total) * 100;

  const report = {
    mode: 'shadow-advisory',
    blocking: false,
    kernelPackage: '@intentsolutions/core',
    kernelVersion,
    kernelPin: KERNEL_PIN,
    registryShadow,
    comparedAgainst: 'scripts/validate-skills-schema.py --marketplace --json',
    composedSchema: LANES[0].schemaId,
    lanes: {
      'authoring/v1': {
        composedSchema: LANES[0].schemaId,
        strict: false,
      },
      'authoring/v2': {
        composedSchema: LANES[1].schemaId,
        strict: true,
        decisionRelevantMetric: 'existing-PASS / kernel-FAIL',
        existingPassKernelFail: strictExistingPassKernelFail,
        existingPassKernelFailPct: Number(strictDecisionRate.toFixed(2)),
        existingFailKernelPass: strictExistingFailKernelPass,
        rawDisagree: strictDisagreements.length,
        kernelUnparseableFrontmatter: strictKernelParseFailures,
        disagreements: strictDisagreements,
      },
    },
    scopeNote:
      'The kernel skill-frontmatter schema is a FRONTMATTER contract; the prose-spec ' +
      'validator lints frontmatter AND markdown body sections (errors prefixed `[body]`). ' +
      'frontmatterDeviationPct is the cutover-relevant signal (body errors filtered out); ' +
      'bodyScopeOnlyCount is informational (files the kernel passes that the prose-spec ' +
      'fails on body sections ONLY — a scope difference, NOT a kernel gap).',
    totals: {
      files: total,
      agree,
      // Cutover-relevant, FRONTMATTER-SCOPED signal:
      frontmatterAgree: total - frontmatterDisagree,
      frontmatterDisagree,
      frontmatterDeviationPct: Number(frontmatterRateStr),
      // Informational: scope difference, not a deviation:
      bodyScopeOnlyCount,
      // Raw (scope-conflated) numbers, retained for transparency:
      rawDisagree,
      rawDeviationRatePct: Number(rawRateStr),
      kernelUnparseableFrontmatter: kernelParseFailures,
    },
    directionBreakdown: {
      'existing-PASS / kernel-FAIL': existingPassKernelFail,
      'existing-FAIL / kernel-PASS': existingFailKernelPass,
    },
    // The cutover-relevant deviations (real kernel gaps if non-empty):
    frontmatterDisagreements,
    // Informational: kernel-PASS / existing-FAIL-on-body-only files (scope difference):
    bodyScopeOnlyFiles,
    // Raw scope-conflated disagreements (transparency):
    rawDisagreements: rawDisagreements.map(({ absPath, kernelPass, errorStrings, ...rest }) => {
      void absPath;
      void kernelPass;
      void errorStrings;
      return rest;
    }),
    generatedAt: new Date().toISOString(),
  };

  const outDir = join(REPO_ROOT, 'scripts', '.kernel-shadow');
  mkdirSync(outDir, { recursive: true });
  const outPath = join(outDir, 'report.json');
  writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n');

  // ---- Human console summary ----
  console.log('');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log('  KERNEL SHADOW VALIDATION (advisory · non-blocking · DR-049)');
  console.log('═══════════════════════════════════════════════════════════════');
  console.log(`  kernel        : @intentsolutions/core@${kernelVersion} (pinned ${KERNEL_PIN})`);
  console.log('  prose-spec    : validate-skills-schema.py --marketplace --json');
  console.log('  machine-spec  : authoring/v1 baseline + authoring/v2 strict (composed)');
  console.log('  scope         : kernel = FRONTMATTER contract; prose-spec also lints BODY');
  console.log('  ───────────────────────────────────────────────────────────');
  console.log(`  corpus files                 : ${total}`);
  console.log('  ── STRICT authoring/v2 — DECISION-RELEVANT ──');
  console.log(
    `  existing-PASS / kernel-FAIL  : ${strictExistingPassKernelFail} (${strictDecisionRate.toFixed(2)}%)`,
  );
  console.log(`  existing-FAIL / kernel-PASS  : ${strictExistingFailKernelPass}`);
  console.log(`  strict raw DISAGREE          : ${strictDisagreements.length}`);
  console.log('  ── FRONTMATTER-SCOPED (the cutover-relevant signal) ──');
  console.log(`  FRONTMATTER AGREE            : ${total - frontmatterDisagree}`);
  console.log(`  FRONTMATTER DISAGREE         : ${frontmatterDisagree}`);
  console.log(`  FRONTMATTER DEVIATION RATE   : ${frontmatterRateStr}%`);
  console.log('  ── INFORMATIONAL (scope difference, NOT a kernel gap) ──');
  console.log(`  body-scope-only (kernel-PASS / prose-spec-FAIL on body) : ${bodyScopeOnlyCount}`);
  console.log('  ── RAW (scope-conflated — frontmatter + body together) ──');
  console.log(`  raw DISAGREE                 : ${rawDisagree}`);
  console.log(`  raw DEVIATION RATE           : ${rawRateStr}%`);
  console.log(`     existing-PASS / kernel-FAIL : ${existingPassKernelFail}`);
  console.log(`     existing-FAIL / kernel-PASS : ${existingFailKernelPass}`);
  console.log('  ───────────────────────────────────────────────────────────');

  if (frontmatterDisagree > 0) {
    const shown = frontmatterDisagreements.slice(0, 40);
    console.log(
      `  REAL FRONTMATTER deviations — kernel gaps to surface (showing ${shown.length} of ${frontmatterDisagree}):`,
    );
    for (const d of shown) {
      const why =
        d.scopeFetchError != null
          ? `(scope fetch failed: ${d.scopeFetchError})`
          : d.direction === 'existing-PASS / kernel-FAIL'
            ? d.kernelErrors && d.kernelErrors[0]
              ? `${d.kernelErrors[0].instancePath || '/'} ${d.kernelErrors[0].message}`
              : ''
            : (d.sampleNonBodyErrors && d.sampleNonBodyErrors[0]) || '';
      console.log(`    [${d.direction}] ${d.path}  ${why}`);
    }
    if (frontmatterDisagree > shown.length) {
      console.log(`    … and ${frontmatterDisagree - shown.length} more (see ${relTo(outPath)})`);
    }
  } else {
    console.log('  Zero FRONTMATTER deviations — the kernel reproduces the prose-spec');
    console.log('  verdict on the FRONTMATTER scope it actually owns. (Any raw disagreements');
    console.log('  are body-section-only, which the kernel deliberately does not lint.)');
  }
  if (bodyScopeOnlyCount > 0) {
    const sample = bodyScopeOnlyFiles.slice(0, 5).map((f) => f.path);
    console.log(
      `  Note: ${bodyScopeOnlyCount} file(s) the kernel passes fail the prose-spec on BODY sections only`,
    );
    console.log(`        (e.g. missing ## Overview / ## Instructions) — a scope difference, not a`);
    console.log(
      `        kernel gap. Sample: ${sample.join(', ')}${bodyScopeOnlyCount > sample.length ? ', …' : ''}`,
    );
  }
  console.log('═══════════════════════════════════════════════════════════════');
  console.log(`  Full machine report: ${relTo(outPath)}`);
  console.log(registrySummaryLines(registryShadow).join('\n'));
  console.log('  ADVISORY ONLY — this run never fails CI or blocks a PR.');
  console.log('');

  // ---- GitHub Step Summary ----
  if (process.env.GITHUB_STEP_SUMMARY) {
    const lines = [];
    lines.push('## Kernel shadow validation (advisory · non-blocking)');
    lines.push('');
    lines.push(
      'Dual-validator shadow per DR-049. The kernel machine-spec ' +
        `(\`@intentsolutions/core@${kernelVersion}\`, pinned \`${KERNEL_PIN}\`) is run over the ` +
        'same SKILL.md corpus the existing prose-spec validator grades, at **marketplace tier**, ' +
        'and the per-file PASS/FAIL verdicts are compared. **This gate is advisory — it can never ' +
        'fail the build or block a PR.**',
    );
    lines.push('');
    lines.push(
      '**Scope:** the kernel `skill-frontmatter` schema is a **frontmatter contract**; the ' +
        'prose-spec validator also lints the markdown **body** (`[body]`-prefixed errors). ' +
        '`frontmatter deviation` filters out `[body]` errors and is the **cutover-relevant** ' +
        'signal; `body-scope-only` files are a scope difference (kernel passes valid frontmatter; ' +
        'the prose-spec fails them on missing body sections) — **not** a kernel gap.',
    );
    lines.push('');
    lines.push('| metric | value |');
    lines.push('| --- | --- |');
    lines.push(`| corpus files | ${total} |`);
    lines.push(
      `| **strict v2 existing-PASS / kernel-FAIL (decision-relevant)** | **${strictExistingPassKernelFail} (${strictDecisionRate.toFixed(2)}%)** |`,
    );
    lines.push(`| strict v2 existing-FAIL / kernel-PASS | ${strictExistingFailKernelPass} |`);
    lines.push(`| strict v2 raw DISAGREE | ${strictDisagreements.length} |`);
    lines.push(`| frontmatter AGREE | ${total - frontmatterDisagree} |`);
    lines.push(`| frontmatter DISAGREE | ${frontmatterDisagree} |`);
    lines.push(`| **frontmatter deviation rate** | **${frontmatterRateStr}%** |`);
    lines.push(`| body-scope-only (informational) | ${bodyScopeOnlyCount} |`);
    lines.push(`| raw DISAGREE (scope-conflated) | ${rawDisagree} |`);
    lines.push(`| raw deviation rate | ${rawRateStr}% |`);
    lines.push(`| existing-PASS / kernel-FAIL | ${existingPassKernelFail} |`);
    lines.push(`| existing-FAIL / kernel-PASS | ${existingFailKernelPass} |`);
    lines.push('');
    lines.push(...registrySummaryLines(registryShadow));
    if (frontmatterDisagree > 0) {
      lines.push(
        '<details><summary>REAL frontmatter deviations — kernel gaps (first 40)</summary>',
      );
      lines.push('');
      lines.push('| direction | file | first non-body / kernel error |');
      lines.push('| --- | --- | --- |');
      for (const d of frontmatterDisagreements.slice(0, 40)) {
        let why;
        if (d.scopeFetchError != null) {
          why = `(scope fetch failed: ${d.scopeFetchError})`;
        } else if (d.direction === 'existing-PASS / kernel-FAIL') {
          const k0 = d.kernelErrors && d.kernelErrors[0];
          why = k0 ? `\`${k0.instancePath || '/'}\` ${k0.message}` : '';
        } else {
          why = (d.sampleNonBodyErrors && d.sampleNonBodyErrors[0]) || '';
        }
        lines.push(`| ${d.direction} | \`${d.path}\` | ${why} |`);
      }
      lines.push('');
      lines.push('</details>');
    } else {
      lines.push(
        'Zero **frontmatter** deviations — the kernel reproduces the prose-spec verdict on the ' +
          'frontmatter scope it actually owns. Any raw disagreements are body-section-only, which ' +
          'the kernel deliberately does not lint.',
      );
    }
    if (bodyScopeOnlyCount > 0) {
      lines.push('');
      lines.push(
        `<details><summary>Body-scope-only — kernel-PASS / prose-spec-FAIL on body only (${bodyScopeOnlyCount})</summary>`,
      );
      lines.push('');
      lines.push('| file | prose-spec error count | sample body errors |');
      lines.push('| --- | --- | --- |');
      for (const f of bodyScopeOnlyFiles.slice(0, 40)) {
        lines.push(
          `| \`${f.path}\` | ${f.existingErrorCount} | ${(f.sampleBodyErrors || []).join('; ')} |`,
        );
      }
      lines.push('');
      lines.push('</details>');
    }
    lines.push('');
    try {
      writeFileSync(process.env.GITHUB_STEP_SUMMARY, lines.join('\n') + '\n', { flag: 'a' });
    } catch (e) {
      console.error(`[kernel-shadow] could not write step summary: ${e.message}`);
    }
  }

  // Advisory: always succeed on a completed run.
  process.exit(0);
}

main();
