#!/usr/bin/env -S node --experimental-strip-types
/**
 * ci/emit-evidence/assemble-manifest.ts — combine the emit skeleton with the
 * cosign-produced sigstore bundles into the final `report-manifest.json` the
 * intent-eval-dashboard fetches for the `ccp` row.
 *
 * Runs AFTER `ci/emit-evidence/emit-evidence.ts` (which wrote the skeleton +
 * canonical bundle files) and AFTER CI has signed each `bundle-<i>.json` with
 * `cosign sign-blob --bundle bundle-<i>.sigstore.json`. For each skeleton row
 * it reads back the canonical bundle object + its sigstore bundle and
 * assembles:
 *
 *   { repo, signing, rows: [ { bundle, sigstoreBundle, sourceSha,
 *                             evidencePayload, gateResults } ] }
 *
 * This is EXACTLY the shape the dashboard's `isReportManifestShape` accepts:
 * each row carries `bundle` + `sigstoreBundle` + a string `sourceSha`. The
 * dashboard binds evidencePayload to the signed storage_key and derives its
 * rendered predicates from the statements. gateResults is a redundant
 * compatibility projection that must agree with those predicates.
 *
 * Fail-closed: a missing bundle file, a missing sigstore bundle, or a
 * structural mismatch aborts (exit 1) rather than publishing a half-built
 * manifest.
 *
 * Usage:
 *   node --experimental-strip-types ci/emit-evidence/assemble-manifest.ts \
 *     [--dir build/evidence] [--out build/evidence/report-manifest.json]
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { basename, join } from 'node:path';
import { EvidenceBundleSchema } from '@intentsolutions/core/validators/v1/evidence-bundle';
import { EvidenceBundlePayloadSchema } from '@intentsolutions/core/validators/v1/evidence-statement';
import { evidencePayloadMetadata, stableStringify } from './emit-evidence.ts';

interface SkeletonRow {
  readonly bundleFile: string;
  readonly gateResults: readonly unknown[];
  readonly evidencePayload: unknown;
  readonly sourceSha: string;
}
interface Skeleton {
  readonly repo: string;
  readonly signing: {
    readonly issuer: string;
    readonly subject: string;
    readonly workflowRef: string;
  };
  readonly rows: readonly SkeletonRow[];
}

interface ManifestRow {
  readonly bundle: unknown;
  readonly sigstoreBundle: unknown;
  readonly sourceSha: string;
  readonly gateResults: readonly unknown[];
  readonly evidencePayload: unknown;
}
interface ReportManifest {
  readonly repo: string;
  readonly signing: Skeleton['signing'];
  readonly rows: readonly ManifestRow[];
}

/** Mirror of the dashboard's `isReportManifestShape` (kept in sync by review). */
function isReportManifestShape(value: unknown): value is ReportManifest {
  if (typeof value !== 'object' || value === null) return false;
  const v = value as Record<string, unknown>;
  if (typeof v['repo'] !== 'string') return false;
  const signing = v['signing'];
  if (typeof signing !== 'object' || signing === null) return false;
  const s = signing as Record<string, unknown>;
  if (typeof s['issuer'] !== 'string') return false;
  if (typeof s['subject'] !== 'string') return false;
  if (typeof s['workflowRef'] !== 'string') return false;
  if (!Array.isArray(v['rows'])) return false;
  return v['rows'].every((r) => {
    if (typeof r !== 'object' || r === null) return false;
    const row = r as Record<string, unknown>;
    return 'bundle' in row && 'sigstoreBundle' in row && typeof row['sourceSha'] === 'string';
  });
}

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function assemble(dir: string): ReportManifest {
  const skeletonPath = join(dir, 'manifest-skeleton.json');
  if (!existsSync(skeletonPath)) {
    throw new Error(`missing ${skeletonPath} — run ci/emit-evidence/emit-evidence.ts first`);
  }
  const skeleton = readJson(skeletonPath) as Skeleton;

  const rows: ManifestRow[] = skeleton.rows.map((row) => {
    const bundlePath = join(dir, row.bundleFile);
    const sigPath = join(dir, `${basename(row.bundleFile, '.json')}.sigstore.json`);
    if (!existsSync(bundlePath)) throw new Error(`missing bundle file ${bundlePath}`);
    if (!existsSync(sigPath)) {
      throw new Error(
        `missing sigstore bundle ${sigPath} — was cosign sign-blob run for ${row.bundleFile}?`,
      );
    }
    const bundle = readJson(bundlePath);
    const parsedBundle = EvidenceBundleSchema.parse(bundle);
    const payload = EvidenceBundlePayloadSchema.parse(row.evidencePayload);
    for (const [key, expected] of Object.entries(evidencePayloadMetadata(row.evidencePayload))) {
      if (
        stableStringify(parsedBundle[key as keyof typeof parsedBundle]) !==
        stableStringify(expected)
      ) {
        throw new Error(`evidencePayload does not match signed bundle ${key}`);
      }
    }
    if (
      stableStringify(row.gateResults) !==
      stableStringify(payload.map((statement) => statement.predicate))
    ) {
      throw new Error('gateResults do not match evidencePayload predicates');
    }
    return {
      bundle,
      sigstoreBundle: readJson(sigPath),
      sourceSha: row.sourceSha,
      gateResults: row.gateResults,
      evidencePayload: row.evidencePayload,
    };
  });

  const manifest: ReportManifest = { repo: skeleton.repo, signing: skeleton.signing, rows };
  if (!isReportManifestShape(manifest)) {
    throw new Error(
      'assembled manifest failed the report-manifest shape check (would be rejected at ingest)',
    );
  }
  return manifest;
}

function parseArgs(argv: readonly string[]): { dir: string; out: string } {
  let dir = 'build/evidence';
  let out = '';
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--dir') {
      dir = argv[i + 1] ?? dir;
      i++;
    } else if (argv[i] === '--out') {
      out = argv[i + 1] ?? out;
      i++;
    }
  }
  if (out === '') out = join(dir, 'report-manifest.json');
  return { dir, out };
}

const invokedDirectly = process.argv[1]?.endsWith('assemble-manifest.ts') === true;
if (invokedDirectly) {
  try {
    const { dir, out } = parseArgs(process.argv.slice(2));
    const manifest = assemble(dir);
    writeFileSync(out, JSON.stringify(manifest), 'utf8');
    console.log(`assemble-manifest OK: ${manifest.rows.length} signed row(s) -> ${out}`);
    process.exit(0);
  } catch (err: unknown) {
    console.error(
      'assemble-manifest FAILED (fail-closed):',
      err instanceof Error ? err.message : String(err),
    );
    process.exit(1);
  }
}
