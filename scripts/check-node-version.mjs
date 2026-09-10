#!/usr/bin/env node

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

/**
 * Enforce the Node.js floor for repository-level commands.
 *
 * The root build and verification paths include the Astro marketplace. Keep
 * this check dependency-free so it can run before package installation.
 */

export const MIN_NODE_VERSION = readFileSync(
  new URL('../.node-version', import.meta.url),
  'utf8',
).trim();

function parseVersion(version) {
  const match = /^(\d+)\.(\d+)\.(\d+)$/.exec(version);
  if (!match) return null;
  return match.slice(1).map(Number);
}

export function isSupportedNodeVersion(actualVersion, minimumVersion = MIN_NODE_VERSION) {
  const actual = parseVersion(actualVersion);
  const minimum = parseVersion(minimumVersion);
  if (!actual || !minimum) return false;

  for (let index = 0; index < actual.length; index += 1) {
    if (actual[index] !== minimum[index]) return actual[index] > minimum[index];
  }
  return true;
}

export function assertSupportedNodeVersion(
  actualVersion = process.versions.node,
  minimumVersion = MIN_NODE_VERSION,
) {
  if (!isSupportedNodeVersion(actualVersion, minimumVersion)) {
    throw new Error(
      `Node.js ${actualVersion} is not supported. Repository-level commands and the Astro marketplace build require Node.js >= ${minimumVersion}. Install/use the version in .node-version, then retry.`,
    );
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    assertSupportedNodeVersion();
    console.log(
      `Node.js ${process.versions.node} satisfies the repository minimum (${MIN_NODE_VERSION}).`,
    );
  } catch (error) {
    console.error(`Node.js runtime preflight failed: ${error.message}`);
    process.exitCode = 1;
  }
}
