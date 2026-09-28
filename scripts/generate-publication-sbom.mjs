#!/usr/bin/env node
/**
 * Generate a reproducible CycloneDX SBOM for a publishable pnpm workspace.
 *
 * The npm CLI's `sbom` command requires a package-lock and therefore cannot
 * attest this pnpm workspace.  This script gets the resolved production graph
 * from pnpm itself and serializes the result as CycloneDX 1.6 JSON.
 */
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

// Package URL per the purl spec's npm type: a scope is the namespace segment
// and its "@" is percent-encoded (pkg:npm/%40scope/name@1.0.0). Each segment
// is encoded on its own, so no separator ever needs to be un-escaped.
export function purl(name, version) {
  const segments = name.startsWith('@') ? name.split('/') : [name];
  if (segments.length > 2 || segments.some((segment) => segment.length === 0)) {
    throw new Error(`invalid npm package name for purl: ${name}`);
  }
  return `pkg:npm/${segments.map(encodeURIComponent).join('/')}@${encodeURIComponent(version)}`;
}

export function buildBom(tree) {
  if (!tree || typeof tree.name !== 'string' || typeof tree.version !== 'string') {
    throw new Error('pnpm dependency tree must contain a package name and version');
  }
  const rootRef = purl(tree.name, tree.version);
  const components = new Map();
  const dependencies = new Map();

  const visit = (node, nameHint) => {
    const name = node.name ?? nameHint;
    if (typeof name !== 'string' || typeof node.version !== 'string') {
      throw new Error('pnpm dependency entry must contain a name and version');
    }
    const ref = purl(name, node.version);
    if (!components.has(ref)) {
      components.set(ref, {
        type: 'library',
        'bom-ref': ref,
        name,
        version: node.version,
        purl: ref,
        ...(typeof node.resolved === 'string'
          ? { externalReferences: [{ type: 'distribution', url: node.resolved }] }
          : {}),
      });
    }
    const children = Object.entries(node.dependencies ?? {});
    const childRefs = children
      .map(([childName, child]) => purl(child.name ?? childName, child.version))
      .sort();
    dependencies.set(ref, childRefs);
    for (const [childName, child] of children) visit(child, childName);
    return ref;
  };

  const rootChildren = Object.entries(tree.dependencies ?? {});
  dependencies.set(
    rootRef,
    rootChildren.map(([name, child]) => purl(child.name ?? name, child.version)).sort(),
  );
  for (const [name, child] of rootChildren) visit(child, name);
  components.delete(rootRef);

  return {
    bomFormat: 'CycloneDX',
    specVersion: '1.6',
    serialNumber: `urn:uuid:${createHash('sha256').update(rootRef).digest('hex').slice(0, 8)}-0000-4000-8000-000000000000`,
    version: 1,
    metadata: {
      component: {
        type: 'application',
        'bom-ref': rootRef,
        name: tree.name,
        version: tree.version,
        purl: rootRef,
      },
    },
    components: [...components.values()].sort((a, b) => a['bom-ref'].localeCompare(b['bom-ref'])),
    dependencies: [...dependencies.entries()]
      .map(([ref, dependsOn]) => ({ ref, ...(dependsOn.length ? { dependsOn } : {}) }))
      .sort((a, b) => a.ref.localeCompare(b.ref)),
  };
}

function usage() {
  throw new Error(
    'usage: generate-publication-sbom.mjs --package <package.json> --out <sbom.cdx.json> [--print-digest]',
  );
}

export function main(argv = process.argv.slice(2)) {
  const packageFlag = argv.indexOf('--package');
  const outFlag = argv.indexOf('--out');
  if (packageFlag < 0 || outFlag < 0 || !argv[packageFlag + 1] || !argv[outFlag + 1]) usage();
  const manifest = resolve(argv[packageFlag + 1]);
  const out = resolve(argv[outFlag + 1]);
  const workspace = relative(process.cwd(), dirname(manifest));
  if (workspace.startsWith('..')) throw new Error('package must be inside this repository');
  JSON.parse(readFileSync(manifest, 'utf8'));
  const result = spawnSync(
    'pnpm',
    [
      '--filter',
      workspace ? `./${workspace}` : '.',
      'list',
      '--prod',
      '--depth',
      'Infinity',
      '--json',
    ],
    {
      cwd: process.cwd(),
      encoding: 'utf8',
    },
  );
  if (result.status !== 0)
    throw new Error(`pnpm dependency graph failed: ${result.stderr || result.stdout}`);
  const trees = JSON.parse(result.stdout);
  if (!Array.isArray(trees) || trees.length !== 1)
    throw new Error('pnpm returned an ambiguous dependency graph');
  const rendered = `${JSON.stringify(buildBom(trees[0]), null, 2)}\n`;
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, rendered);
  const digest = `sha256:${createHash('sha256').update(rendered).digest('hex')}`;
  if (argv.includes('--print-digest')) process.stdout.write(`${digest}\n`);
  return digest;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
