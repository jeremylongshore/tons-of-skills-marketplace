#!/usr/bin/env -S node --experimental-strip-types
/**
 * ci/emit-evidence/emit-evidence.ts — produce this repo's own signed-ready
 * testing evidence for the intent-eval-dashboard reports hub
 * (labs.intentsolutions.io, repo row key `ccp`).
 *
 * ── Why this lives in `ci/emit-evidence/`, NOT `scripts/` ──
 *
 * `scripts/` is the repo's operational toolbox (validators, sync, publish
 * helpers) and is linted/formatted under the root gates. This emitter is a
 * CI-only artifact producer with its own pinned dependency
 * (`@intentsolutions/core` — the kernel validators, pinned to the EXACT
 * version the dashboard verifies with). It has its own private, non-workspace
 * `package.json` + lockfile so the root workspace, the publish surfaces
 * (`plugins/**`, `packages/**`, pnpm-workspace globs), and the published npm
 * packages are all untouched. Nothing under `ci/` ships anywhere.
 *
 * This is the deterministic artifact half of the emit. It re-runs two real
 * blocking validation steps and, when supplied with the exact GitHub
 * check-runs response, attests the three protected-branch contexts. It shapes
 * each outcome into a kernel
 * `gate-result/v1` body, wraps each in a kernel `EvidenceBundle`, and writes:
 *
 *   build/evidence/bundle-<i>.json          — CANONICAL EvidenceBundle bytes
 *   build/evidence/gate-result-<i>.json     — the gate-result/v1 predicate body
 *   build/evidence/evidence-payload-<i>.json — canonical statement-array bytes
 *   build/evidence/manifest-skeleton.json   — for ci/emit-evidence/assemble-manifest.ts
 *
 * Signing + Rekor + final report-manifest.json assembly happen in CI
 * (.github/workflows/emit-evidence.yml). This script does NO crypto and
 * writes only to the gitignored `build/` dir.
 *
 * ── Gate selection (honest, no fake evidence) ──
 *
 * Deterministic local steps (both are blocking steps of `validate` →
 * `ci-required`):
 *   - catalog-invariants  — scripts/validate-catalog-invariants.py
 *                           (plugin FS path == catalog category, entry parity)
 *   - unicode-hygiene     — scripts/validate-unicode-hygiene.py
 *                           (invisible tag chars / Trojan Source / zero-width
 *                           defense; blocks on BLOCKER findings)
 *
 * The three required contexts are separately provided by a completed
 * check-runs response. This avoids pretending that these two local commands
 * represent the entire aggregate. Deliberately excluded after recon
 * (would be fake/degraded evidence):
 *   - `audit-harness verify`     — its hash-pinning surface is currently EMPTY
 *                                  in this repo (see validate-plugins.yml
 *                                  comment), so it trivially exits 0: no signal.
 *   - full-corpus skill grading  — report-only with hundreds of known errors;
 *                                  not a pass/fail gate on main.
 *   - kernel-shadow / vendor-hash lanes — advisory by design (soak), never
 *                                  blocking; unfit for SIGNED pass evidence.
 *
 * ── Contract (matches the dashboard ingest, verified against its source) ──
 *
 *   - Each `bundle` validates against `EvidenceBundleSchema` (kernel pinned to
 *     the EXACT version the dashboard verifies with).
 *   - Canonical bytes use the dashboard's `stableStringify` so cosign's
 *     signature round-trips through the dashboard's re-canonicalisation.
 *   - `signing_mode: 'rekor_production'`, `rekor_log_indices: []` (real index
 *     lives in the sigstore Bundle the dashboard's Rekor check verifies).
 *
 * Usage:
 *   node --experimental-strip-types ci/emit-evidence/emit-evidence.ts \
 *     [--out build/evidence] [--ref refs/heads/main] [--self-check]
 */

import { execFileSync } from 'node:child_process';
import { createHash, randomBytes } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  GateResultV1Schema,
  GATE_RESULT_V1_URI,
} from '@intentsolutions/core/validators/v1/gate-result-v1';
import { EvidenceBundleSchema } from '@intentsolutions/core/validators/v1/evidence-bundle';
import {
  EvidenceBundlePayloadSchema,
  IN_TOTO_STATEMENT_V1_TYPE,
  type EvidenceBundlePayload,
} from '@intentsolutions/core/validators/v1/evidence-statement';

const GITHUB_REPO = 'jeremylongshore/tons-of-skills-marketplace';
const REPO_KEY = 'ccp';

/** Source files whose bytes define the local and protected-context policy. */
const POLICY_FILES = [
  'scripts/validate-catalog-invariants.py',
  'scripts/validate-unicode-hygiene.py',
  'scripts/evaluate-certification.mjs',
  '.github/workflows/validate-plugins.yml',
  '.github/workflows/secret-scan.yml',
  '.github/workflows/skill-conform.yml',
] as const;

interface GateOutcome {
  readonly gateName: string;
  readonly gateVersion: string;
  readonly decision: 'pass' | 'fail' | 'advisory' | 'error';
  readonly reasons: readonly string[];
  readonly dimensionsEvaluated: readonly string[];
  readonly dimensionsSkipped: readonly string[];
  readonly advisorySeverity?: 'info' | 'warn' | 'error';
  readonly failureMode?: string;
  readonly inputHash?: string;
  readonly metadata?: Record<string, unknown>;
}

interface EmitContext {
  readonly nowIso: string;
  readonly nowMs: number;
  readonly commitSha: string;
  readonly sourceSha: string;
  readonly policyHash: string;
  readonly runnerVersion: string;
  readonly rand16: () => Uint8Array;
}

// ── Canonicalisation (MUST match the dashboard's content-address.ts) ──

function sortDeep(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortDeep);
  if (value !== null && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>)
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([k, v]) => [k, sortDeep(v)] as const);
    return Object.fromEntries(entries);
  }
  return value;
}

/** Canonical JSON string (sorted keys, no whitespace) — dashboard-identical. */
export function stableStringify(value: unknown): string {
  return JSON.stringify(sortDeep(value));
}

function sha256Hex(s: string): string {
  return createHash('sha256').update(Buffer.from(s, 'utf8')).digest('hex');
}

/** Generate a kernel-valid UUIDv7 from a 16-byte source + ms timestamp. */
export function uuidv7(nowMs: number, rand: Uint8Array): string {
  const b = Buffer.from(rand.slice(0, 16));
  const ts = BigInt(nowMs);
  b[0] = Number((ts >> 40n) & 0xffn);
  b[1] = Number((ts >> 32n) & 0xffn);
  b[2] = Number((ts >> 24n) & 0xffn);
  b[3] = Number((ts >> 16n) & 0xffn);
  b[4] = Number((ts >> 8n) & 0xffn);
  b[5] = Number(ts & 0xffn);
  b[6] = (b[6]! & 0x0f) | 0x70; // version 7
  b[8] = (b[8]! & 0x3f) | 0x80; // variant 10
  const h = b.toString('hex');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20, 32)}`;
}

/** A built row: the kernel-valid bundle + its canonical bytes + the gate body. */
export interface EmitRow {
  readonly bundle: unknown;
  readonly canonicalBundle: string;
  readonly gateResult: unknown;
  readonly evidencePayload: EvidenceBundlePayload;
  readonly sourceSha: string;
}

/**
 * Build + kernel-validate a gate-result/v1 body for one outcome. Throws (fail
 * closed) if the result is not kernel-schema-valid.
 */
export function buildGateResult(o: GateOutcome, ctx: EmitContext): Record<string, unknown> {
  const gateId = `${REPO_KEY}:ci:${o.gateName}`;
  const inputHash =
    o.inputHash ?? `sha256:${sha256Hex(`${ctx.commitSha}:${o.gateName}:${ctx.policyHash}`)}`;
  const body: Record<string, unknown> = {
    gate_id: gateId,
    gate_name: o.gateName,
    gate_version: o.gateVersion,
    gate_decision: o.decision,
    gate_reasons: [...o.reasons],
    coverage: {
      dimensions_evaluated: [...o.dimensionsEvaluated],
      dimensions_skipped: [...o.dimensionsSkipped],
    },
    policy_ref: `${ctx.policyHash}:${POLICY_FILES.join('+')}`,
    policy_hash: ctx.policyHash,
    input_hash: inputHash,
    evaluated_at: ctx.nowIso,
    runner: `ccpi-emit@${ctx.runnerVersion}`,
    commit_sha: ctx.commitSha,
    ...(o.advisorySeverity !== undefined ? { advisory_severity: o.advisorySeverity } : {}),
    ...(o.failureMode !== undefined ? { failure_mode: o.failureMode } : {}),
    ...(o.metadata !== undefined ? { metadata: o.metadata } : {}),
  };
  GateResultV1Schema.parse(body); // fail-closed
  return body;
}

/**
 * Wrap a predicate in the kernel's invariant-checked in-toto statement array.
 */
export function buildEvidencePayload(gateResult: Record<string, unknown>): EvidenceBundlePayload {
  const body = GateResultV1Schema.parse(gateResult);
  return EvidenceBundlePayloadSchema.parse([
    {
      _type: IN_TOTO_STATEMENT_V1_TYPE,
      subject: [{ name: body.gate_id, digest: { sha256: body.input_hash.slice(7) } }],
      predicateType: GATE_RESULT_V1_URI,
      predicate: body,
    },
  ]);
}

/** Signed metadata is derived from the complete ordered statement payload. */
export function evidencePayloadMetadata(payloadRaw: unknown) {
  const payload = EvidenceBundlePayloadSchema.parse(payloadRaw);
  const subjects = new Map(
    payload.flatMap((statement) =>
      statement.subject.map((subject) => [stableStringify(subject), subject] as const),
    ),
  );
  return {
    predicate_uri_set: [...new Set(payload.map((statement) => statement.predicateType))],
    row_count: payload.length,
    subject_set: [...subjects.values()],
    storage_key: `sha256:${sha256Hex(stableStringify(payloadRaw))}`,
  };
}

/** Build kernel-valid signed metadata for a canonical evidence payload. */
export function buildEvidenceBundle(
  evidencePayload: EvidenceBundlePayload,
  ctx: EmitContext,
): Record<string, unknown> {
  const bundle: Record<string, unknown> = {
    id: uuidv7(ctx.nowMs, ctx.rand16()),
    eval_run_id: uuidv7(ctx.nowMs, ctx.rand16()),
    created_at: ctx.nowIso,
    ...evidencePayloadMetadata(evidencePayload),
    signing_mode: 'rekor_production',
    rekor_log_indices: [], // real index lives in the sigstore Bundle (see header)
    verification_status: 'unverified', // the dashboard re-verifies; we don't self-attest
    verification_last_checked_at: ctx.nowIso,
  };
  EvidenceBundleSchema.parse(bundle); // fail-closed
  return bundle;
}

/** Build all rows from outcomes. */
export function buildRows(outcomes: readonly GateOutcome[], ctx: EmitContext): EmitRow[] {
  return outcomes.map((o) => {
    const evidencePayload = buildEvidencePayload(buildGateResult(o, ctx));
    // The redundant projection comes from the validated statement itself,
    // so future kernel normalization cannot make the two fields disagree.
    const gateResult = evidencePayload[0]!.predicate;
    const bundle = buildEvidenceBundle(evidencePayload, ctx);
    return {
      bundle,
      canonicalBundle: stableStringify(bundle),
      gateResult,
      evidencePayload,
      sourceSha: ctx.sourceSha,
    };
  });
}

/** The manifest skeleton CI signs + assembles into the final report-manifest.json. */
export interface ManifestSkeleton {
  readonly repo: string;
  readonly signing: {
    readonly issuer: string;
    readonly subject: string;
    readonly workflowRef: string;
  };
  readonly rows: readonly {
    readonly bundleFile: string;
    readonly gateResults: readonly unknown[];
    readonly evidencePayload: EvidenceBundlePayload;
    readonly sourceSha: string;
  }[];
}

/**
 * Compute the OIDC signing claims this CI run will assert. The emit workflow
 * runs on push to main (plus a main-only workflow_dispatch guard), so `ref` is
 * always `refs/heads/main` in CI — these are exactly the claims the dashboard
 * pins for the `ccp` row:
 *   issuer      https://token.actions.githubusercontent.com
 *   subject     repo:jeremylongshore/tons-of-skills-marketplace:ref:refs/heads/main
 *   workflowRef jeremylongshore/tons-of-skills-marketplace/.github/workflows/emit-evidence.yml@refs/heads/main
 */
export function signingClaims(
  ref: string,
  workflowRef = `${GITHUB_REPO}/.github/workflows/emit-evidence.yml@${ref}`,
): ManifestSkeleton['signing'] {
  return {
    issuer: 'https://token.actions.githubusercontent.com',
    subject: `repo:${GITHUB_REPO}:ref:${ref}`,
    workflowRef,
  };
}

/** Write all emit artifacts under `outDir`. Returns the skeleton written. */
export function writeEmit(
  rows: readonly EmitRow[],
  ref: string,
  outDir: string,
  workflowRef?: string,
): ManifestSkeleton {
  mkdirSync(outDir, { recursive: true });
  const skeletonRows = rows.map((row, i) => {
    const bundleFile = `bundle-${i}.json`;
    writeFileSync(join(outDir, bundleFile), row.canonicalBundle, 'utf8');
    writeFileSync(join(outDir, `gate-result-${i}.json`), stableStringify(row.gateResult), 'utf8');
    writeFileSync(
      join(outDir, `evidence-payload-${i}.json`),
      stableStringify(row.evidencePayload),
      'utf8',
    );
    return {
      bundleFile,
      gateResults: [row.gateResult],
      evidencePayload: row.evidencePayload,
      sourceSha: row.sourceSha,
    };
  });
  const skeleton: ManifestSkeleton = {
    repo: REPO_KEY,
    signing: signingClaims(ref, workflowRef),
    rows: skeletonRows,
  };
  writeFileSync(join(outDir, 'manifest-skeleton.json'), JSON.stringify(skeleton, null, 2), 'utf8');
  return skeleton;
}

// ── Gate collection (CI-run; runs the repo's real blocking gates) ──

function run(cmd: string, args: readonly string[]): { ok: boolean; out: string } {
  try {
    const out = execFileSync(cmd, args as string[], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return { ok: true, out };
  } catch (err: unknown) {
    const e = err as { stdout?: string; stderr?: string; message?: string };
    return { ok: false, out: `${e.stdout ?? ''}${e.stderr ?? ''}${e.message ?? ''}` };
  }
}

/**
 * Catalog invariant gate: every catalog entry's filesystem path matches its
 * declared category (and entry parity holds). Real, deterministic, stdlib-only
 * Python; a blocking step of the `validate` job on main.
 */
function catalogInvariantsOutcome(): GateOutcome {
  const r = run('python3', ['scripts/validate-catalog-invariants.py']);
  return {
    gateName: 'catalog-invariants',
    gateVersion: '1.0.0',
    decision: r.ok ? 'pass' : 'fail',
    reasons: r.ok
      ? [firstLines(r.out, 1) || 'catalog invariant check passed']
      : [firstLines(r.out, 8) || 'catalog invariants violated'],
    dimensionsEvaluated: ['catalog-path-category-parity'],
    dimensionsSkipped: [],
    ...(r.ok ? {} : { failureMode: 'catalog-invariant-violation' }),
  };
}

/**
 * Unicode-hygiene gate: invisible tag characters (Socket TrapDoor vector),
 * bidi overrides (Trojan Source), zero-width/format chars, mixed-script
 * identifiers. Blocks on BLOCKER findings. Real, deterministic, stdlib-only
 * Python; a blocking step of the `validate` job on main.
 */
function unicodeHygieneOutcome(): GateOutcome {
  const r = run('python3', ['scripts/validate-unicode-hygiene.py']);
  return {
    gateName: 'unicode-hygiene',
    gateVersion: '1.0.0',
    decision: r.ok ? 'pass' : 'fail',
    reasons: r.ok
      ? ['no BLOCKER-severity unicode findings (tag chars, bidi overrides)']
      : [firstLines(r.out, 8) || 'BLOCKER-severity unicode findings present'],
    dimensionsEvaluated: ['invisible-tag-chars', 'bidi-overrides', 'zero-width-format-chars'],
    dimensionsSkipped: [],
    ...(r.ok ? {} : { failureMode: 'unicode-hygiene-blocker' }),
  };
}

type CertificationArtifact = {
  readonly path: string;
  readonly verdict: 'CERTIFIED' | 'NOT-CERTIFIED';
  readonly evidence_class: string;
  readonly reason_codes: readonly string[];
};

/**
 * Immutable facts emitted by a publisher after an artifact is actually
 * accepted by its registry.  This deliberately models completed publication,
 * not a candidate or dry-run: a signed row must never claim a release that
 * did not happen.
 */
type PublicationArtifact = {
  readonly channel: 'npm' | 'mcp-registry' | 'github-release';
  readonly name: string;
  readonly version?: string;
  readonly release_tag?: string;
  readonly artifact_digest?: string;
  readonly package_name?: string;
  readonly sbom_digest?: string;
  readonly sbom_format?: 'CycloneDX';
};

type RequiredCheck = {
  readonly name: string;
  readonly status: string;
  readonly conclusion: string | null;
  readonly html_url?: string;
};

const REQUIRED_CONTEXTS = ['ci-required', 'gitleaks', 'skill-conform'] as const;

/**
 * Convert the exact three protected-branch contexts into evidence rows.  The
 * caller must provide a completed GitHub check-runs response for the exact
 * source SHA; missing, duplicate, or in-progress contexts are a hard error,
 * never an implicit pass.
 */
export function requiredCheckOutcomes(report: unknown): GateOutcome[] {
  if (!report || typeof report !== 'object' || Array.isArray(report)) {
    throw new Error('required-check report must be an object');
  }
  const checks = (report as Record<string, unknown>)['check_runs'];
  if (!Array.isArray(checks)) throw new Error('required-check report must contain check_runs');
  return REQUIRED_CONTEXTS.map((context) => {
    const matches = checks.filter(
      (raw): raw is RequiredCheck =>
        Boolean(raw) &&
        typeof raw === 'object' &&
        !Array.isArray(raw) &&
        (raw as Record<string, unknown>)['name'] === context,
    );
    if (matches.length !== 1) {
      throw new Error(
        `required context ${context} must appear exactly once (found ${matches.length})`,
      );
    }
    const check = matches[0]!;
    if (check.status !== 'completed' || typeof check.conclusion !== 'string') {
      throw new Error(`required context ${context} is not completed`);
    }
    const passed = check.conclusion === 'success';
    return {
      gateName: context,
      gateVersion: '1.0.0',
      decision: passed ? 'pass' : 'fail',
      reasons: [
        passed ? `${context} completed successfully` : `${context} concluded ${check.conclusion}`,
      ],
      dimensionsEvaluated: ['protected-branch-required-context'],
      dimensionsSkipped: [],
      metadata: {
        check_name: context,
        conclusion: check.conclusion,
        ...(typeof check.html_url === 'string' ? { check_url: check.html_url } : {}),
      },
      ...(passed ? {} : { failureMode: `required-context-${check.conclusion}` }),
    };
  });
}

/**
 * Turn every evaluator verdict into its own kernel gate-result row. The input
 * digest binds each signed row to the exact verdict facts, rather than to a
 * mutable aggregate count. Malformed reports abort the whole emission: an
 * incomplete certification report must never silently become signed evidence.
 */
export function certificationOutcomes(report: unknown): GateOutcome[] {
  if (!report || typeof report !== 'object' || Array.isArray(report)) {
    throw new Error('certification report must be an object');
  }
  const payload = report as Record<string, unknown>;
  if (payload['schema_version'] !== 'certification-report/v1') {
    throw new Error('certification report must use certification-report/v1');
  }
  if (!Array.isArray(payload['artifacts'])) {
    throw new Error('certification report must contain an artifacts array');
  }
  return payload['artifacts'].map((raw, index) => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      throw new Error(`certification artifact ${index} must be an object`);
    }
    const artifact = raw as CertificationArtifact;
    if (typeof artifact.path !== 'string' || artifact.path.length === 0) {
      throw new Error(`certification artifact ${index} missing path`);
    }
    if (artifact.verdict !== 'CERTIFIED' && artifact.verdict !== 'NOT-CERTIFIED') {
      throw new Error(`certification artifact ${artifact.path} has invalid verdict`);
    }
    if (typeof artifact.evidence_class !== 'string' || !Array.isArray(artifact.reason_codes)) {
      throw new Error(`certification artifact ${artifact.path} has invalid evidence facts`);
    }
    if (!artifact.reason_codes.every((code) => typeof code === 'string')) {
      throw new Error(`certification artifact ${artifact.path} has non-string reason code`);
    }
    const verdict = {
      path: artifact.path,
      verdict: artifact.verdict,
      evidence_class: artifact.evidence_class,
      reason_codes: [...artifact.reason_codes],
    };
    return {
      gateName: `certification-verdict-${index + 1}`,
      gateVersion: '1.0.0',
      decision: artifact.verdict === 'CERTIFIED' ? 'pass' : 'fail',
      reasons: artifact.verdict === 'CERTIFIED' ? [] : [...artifact.reason_codes],
      dimensionsEvaluated: ['certification-verdict'],
      dimensionsSkipped: [],
      inputHash: `sha256:${sha256Hex(stableStringify(verdict))}`,
      metadata: { artifact_path: artifact.path, evidence_class: artifact.evidence_class },
      ...(artifact.verdict === 'CERTIFIED' ? {} : { failureMode: 'not-certified' }),
    };
  });
}

/** Convert every completed publication into a separate, content-bound row. */
export function publicationOutcomes(report: unknown): GateOutcome[] {
  if (!report || typeof report !== 'object' || Array.isArray(report)) {
    throw new Error('publication report must be an object');
  }
  const payload = report as Record<string, unknown>;
  if (payload['schema_version'] !== 'publication-report/v1') {
    throw new Error('publication report must use publication-report/v1');
  }
  if (!Array.isArray(payload['publications']) || payload['publications'].length === 0) {
    throw new Error('publication report must contain a non-empty publications array');
  }
  return payload['publications'].map((raw, index) => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
      throw new Error(`publication ${index} must be an object`);
    }
    const publication = raw as PublicationArtifact;
    if (!['npm', 'mcp-registry', 'github-release'].includes(publication.channel)) {
      throw new Error(`publication ${index} has an invalid channel`);
    }
    if (typeof publication.name !== 'string' || publication.name.length === 0) {
      throw new Error(`publication ${index} missing name`);
    }
    if (publication.package_name !== undefined && typeof publication.package_name !== 'string') {
      throw new Error(`publication ${publication.name} has invalid package_name`);
    }
    if (!/^sha256:[a-f0-9]{64}$/.test(publication.sbom_digest ?? '')) {
      throw new Error(`publication ${publication.name} missing or invalid sbom_digest`);
    }
    if (publication.sbom_format !== 'CycloneDX') {
      throw new Error(`publication ${publication.name} must declare CycloneDX sbom_format`);
    }
    if (publication.version !== undefined && typeof publication.version !== 'string') {
      throw new Error(`publication ${publication.name} has invalid version`);
    }
    if (publication.release_tag !== undefined && typeof publication.release_tag !== 'string') {
      throw new Error(`publication ${publication.name} has invalid release_tag`);
    }
    if (
      publication.artifact_digest !== undefined &&
      !/^sha256:[a-f0-9]{64}$/.test(publication.artifact_digest)
    ) {
      throw new Error(`publication ${publication.name} has invalid artifact_digest`);
    }
    const fact = {
      channel: publication.channel,
      name: publication.name,
      ...(publication.package_name === undefined ? {} : { package_name: publication.package_name }),
      ...(publication.version === undefined ? {} : { version: publication.version }),
      ...(publication.release_tag === undefined ? {} : { release_tag: publication.release_tag }),
      ...(publication.artifact_digest === undefined
        ? {}
        : { artifact_digest: publication.artifact_digest }),
      sbom_digest: publication.sbom_digest,
      sbom_format: publication.sbom_format,
    };
    return {
      gateName: `publication-${index + 1}`,
      gateVersion: '1.0.0',
      decision: 'pass',
      reasons: [`published ${publication.channel} artifact ${publication.name}`],
      dimensionsEvaluated: ['completed-publication'],
      dimensionsSkipped: [],
      inputHash: `sha256:${sha256Hex(stableStringify(fact))}`,
      metadata: fact,
    };
  });
}

function readCertificationReport(reportPath: string): GateOutcome[] {
  let raw: string;
  try {
    raw = readFileSync(reportPath, 'utf8');
  } catch (error) {
    throw new Error(
      `unable to read certification report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  try {
    return certificationOutcomes(JSON.parse(raw));
  } catch (error) {
    throw new Error(
      `invalid certification report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function readPublicationReport(reportPath: string): GateOutcome[] {
  let raw: string;
  try {
    raw = readFileSync(reportPath, 'utf8');
  } catch (error) {
    throw new Error(
      `unable to read publication report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  try {
    return publicationOutcomes(JSON.parse(raw));
  } catch (error) {
    throw new Error(
      `invalid publication report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function readRequiredChecksReport(reportPath: string): GateOutcome[] {
  let raw: string;
  try {
    raw = readFileSync(reportPath, 'utf8');
  } catch (error) {
    throw new Error(
      `unable to read required-check report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
  try {
    return requiredCheckOutcomes(JSON.parse(raw));
  } catch (error) {
    throw new Error(
      `invalid required-check report ${reportPath}: ${error instanceof Error ? error.message : String(error)}`,
    );
  }
}

function firstLines(s: string, n: number): string {
  return s
    .split('\n')
    .filter((l) => l.trim().length > 0)
    .slice(0, n)
    .join(' ')
    .slice(0, 500);
}

function gitSha(): string {
  const r = run('git', ['rev-parse', 'HEAD']);
  return r.ok ? r.out.trim() : '0'.repeat(40);
}

/**
 * policy_hash = sha256 over the raw bytes of the policy sources (in fixed
 * order, filename-delimited). The policy an emitted row attests under IS the
 * validator source at this commit — recomputable by any auditor from the tree.
 */
function gatePolicyHash(): string {
  const h = createHash('sha256');
  for (const f of POLICY_FILES) {
    h.update(Buffer.from(`${f}\n`, 'utf8'));
    h.update(readFileSync(join(process.cwd(), f)));
  }
  return `sha256:${h.digest('hex')}`;
}

// ── Self-check (locally-runnable correctness proof) ──

function selfCheck(): void {
  const ctx = synthCtx();
  const outcomes: GateOutcome[] = [
    {
      gateName: 'catalog-invariants',
      gateVersion: '1.0.0',
      decision: 'pass',
      reasons: ['catalog invariant check passed (462 plugins)'],
      dimensionsEvaluated: ['catalog-path-category-parity'],
      dimensionsSkipped: [],
    },
    {
      gateName: 'unicode-hygiene',
      gateVersion: '1.0.0',
      decision: 'fail',
      reasons: ['BLOCKER: U+E0041 invisible tag character in install command'],
      dimensionsEvaluated: ['invisible-tag-chars', 'bidi-overrides', 'zero-width-format-chars'],
      dimensionsSkipped: [],
      failureMode: 'unicode-hygiene-blocker',
    },
  ];
  const rows = buildRows(outcomes, ctx); // throws if any artifact is kernel-invalid
  for (const row of rows) {
    if (stableStringify(JSON.parse(row.canonicalBundle)) !== row.canonicalBundle) {
      throw new Error('canonical bundle is not stable under re-canonicalisation');
    }
  }
  if (rows.length !== 2) throw new Error('expected 2 rows');
  console.log(`self-check OK: ${rows.length} kernel-valid, canonical-stable rows built`);
}

function synthCtx(): EmitContext {
  let n = 0;
  return {
    nowIso: '2026-07-08T00:00:00.000Z',
    nowMs: 1783209600000,
    commitSha: 'a'.repeat(40),
    sourceSha: 'a'.repeat(40),
    policyHash: `sha256:${'b'.repeat(64)}`,
    runnerVersion: '4.33.0',
    // Deterministic, non-random 16-byte source so self-check output is stable.
    rand16: () => {
      n += 1;
      return Uint8Array.from(Array.from({ length: 16 }, (_v, i) => (n * 31 + i) & 0xff));
    },
  };
}

function packageVersion(): string {
  try {
    const pkg = JSON.parse(readFileSync(join(process.cwd(), 'package.json'), 'utf8')) as {
      version?: string;
    };
    return pkg.version ?? '0.0.0';
  } catch {
    return '0.0.0';
  }
}

function ciCtx(): EmitContext {
  const sha = gitSha();
  return {
    nowIso: new Date().toISOString(),
    nowMs: Date.now(),
    commitSha: sha,
    sourceSha: sha,
    policyHash: gatePolicyHash(),
    runnerVersion: packageVersion(),
    rand16: () => Uint8Array.from(randomBytes(16)),
  };
}

function parseArgs(argv: readonly string[]): {
  out: string;
  selfCheck: boolean;
  ref: string;
  certificationReport?: string;
  certificationOnly: boolean;
  publicationReport?: string;
  publicationOnly: boolean;
  requiredChecksReport?: string;
  workflowRef?: string;
  commitSha?: string;
} {
  let out = 'build/evidence';
  let ref = process.env['GITHUB_REF'] ?? 'refs/heads/main';
  let sc = false;
  let certificationReport: string | undefined;
  let certificationOnly = false;
  let publicationReport: string | undefined;
  let publicationOnly = false;
  let requiredChecksReport: string | undefined;
  let workflowRef: string | undefined;
  let commitSha: string | undefined;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--out') {
      out = argv[i + 1] ?? out;
      i++;
    } else if (argv[i] === '--ref') {
      ref = argv[i + 1] ?? ref;
      i++;
    } else if (argv[i] === '--self-check') {
      sc = true;
    } else if (argv[i] === '--certification-report') {
      certificationReport = argv[i + 1];
      if (!certificationReport) throw new Error('--certification-report requires a path');
      i++;
    } else if (argv[i] === '--certification-only') {
      certificationOnly = true;
    } else if (argv[i] === '--publication-report') {
      publicationReport = argv[i + 1];
      if (!publicationReport) throw new Error('--publication-report requires a path');
      i++;
    } else if (argv[i] === '--publication-only') {
      publicationOnly = true;
    } else if (argv[i] === '--required-checks-report') {
      requiredChecksReport = argv[i + 1];
      if (!requiredChecksReport) throw new Error('--required-checks-report requires a path');
      i++;
    } else if (argv[i] === '--workflow-ref') {
      workflowRef = argv[i + 1];
      if (!workflowRef) throw new Error('--workflow-ref requires a value');
      i++;
    } else if (argv[i] === '--commit-sha') {
      commitSha = argv[i + 1];
      if (!/^[a-f0-9]{40}$/.test(commitSha ?? '')) {
        throw new Error('--commit-sha requires a 40-character lowercase SHA');
      }
      i++;
    }
  }
  if (certificationOnly && !certificationReport) {
    throw new Error('--certification-only requires --certification-report');
  }
  if (publicationOnly && !publicationReport) {
    throw new Error('--publication-only requires --publication-report');
  }
  if (certificationOnly && publicationOnly) {
    throw new Error('--certification-only and --publication-only cannot be combined');
  }
  return {
    out,
    selfCheck: sc,
    ref,
    certificationReport,
    certificationOnly,
    publicationReport,
    publicationOnly,
    requiredChecksReport,
    workflowRef,
    commitSha,
  };
}

function main(argv: readonly string[]): number {
  const args = parseArgs(argv);
  if (args.selfCheck) {
    selfCheck();
    return 0;
  }
  const ctx = {
    ...ciCtx(),
    ...(args.commitSha === undefined
      ? {}
      : { commitSha: args.commitSha, sourceSha: args.commitSha }),
  };
  mkdirSync(args.out, { recursive: true });
  const outcomes: GateOutcome[] =
    args.certificationOnly || args.publicationOnly
      ? []
      : [catalogInvariantsOutcome(), unicodeHygieneOutcome()];
  if (args.certificationReport) outcomes.push(...readCertificationReport(args.certificationReport));
  if (args.publicationReport) outcomes.push(...readPublicationReport(args.publicationReport));
  if (args.requiredChecksReport)
    outcomes.push(...readRequiredChecksReport(args.requiredChecksReport));
  const rows = buildRows(outcomes, ctx);
  writeEmit(rows, args.ref, args.out, args.workflowRef);
  console.log(
    `emit-evidence OK: ${rows.length} kernel-valid gate-result/v1 row(s) written to ${args.out}\n` +
      `  decisions: ${outcomes.map((o) => `${o.gateName}=${o.decision}`).join(', ')}\n` +
      `  next (CI): cosign sign-blob each bundle-<i>.json -> assemble-manifest.ts -> report-manifest.json`,
  );
  return 0;
}

// Only run when invoked directly (not when imported by a sibling assembler).
const invokedDirectly = process.argv[1]?.endsWith('emit-evidence.ts') === true;
if (invokedDirectly) {
  try {
    process.exit(main(process.argv.slice(2)));
  } catch (err: unknown) {
    console.error(
      'emit-evidence FAILED (fail-closed):',
      err instanceof Error ? err.message : String(err),
    );
    process.exit(1);
  }
}
