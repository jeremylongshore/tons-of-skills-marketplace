#!/usr/bin/env node

/** R3: reconcile the immutable baseline corpus with actual catalog withdrawals. */
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { resolveCorpus } from './corpus-resolver.mjs';

const require = createRequire(import.meta.url);
const { isPublishedPlugin } = require('./publication-policy.cjs');
const CATALOG = '.claude-plugin/marketplace.extended.json';

function fail(message) {
  throw new Error(`corpus-shrink: ${message}`);
}

function git(root, args) {
  return execFileSync('git', args, {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 128 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, GIT_NO_REPLACE_OBJECTS: '1' },
  });
}

function exactCommit(root, value, label) {
  if (typeof value !== 'string' || !/^[0-9a-f]{40}$/.test(value)) {
    fail(`${label} must be an exact 40-character commit SHA`);
  }
  if (git(root, ['cat-file', '-t', value]).trim() !== 'commit') {
    fail(`${label} must identify a commit object`);
  }
  return value;
}

function hasControls(value) {
  return [...value].some(
    (character) => character.codePointAt(0) < 32 || character.codePointAt(0) === 127,
  );
}

function publishedCatalog(root, ref) {
  const record = git(root, ['ls-tree', '-z', ref, '--', CATALOG]);
  if (!/^100(?:644|755) blob [0-9a-f]{40}\t/.test(record)) {
    fail(`catalog at ${ref} must be a regular tracked file`);
  }
  const catalog = JSON.parse(git(root, ['show', `${ref}:${CATALOG}`]));
  if (!catalog || typeof catalog !== 'object' || !Array.isArray(catalog.plugins)) {
    fail(`catalog at ${ref} must contain a plugins array`);
  }
  const names = new Set();
  const published = [];
  for (const [index, plugin] of catalog.plugins.entries()) {
    const active = isPublishedPlugin(plugin, `catalog entry ${index}`);
    if (
      typeof plugin.name !== 'string' ||
      !plugin.name.trim() ||
      plugin.name !== plugin.name.trim() ||
      hasControls(plugin.name) ||
      names.has(plugin.name)
    ) {
      fail(`catalog entry ${index} has an invalid or duplicate name`);
    }
    names.add(plugin.name);
    if (typeof plugin.source !== 'string') fail(`catalog entry ${index} has no source path`);
    const source = plugin.source.replace(/^\.\//, '').replace(/\/$/, '');
    const segments = source.split('/');
    if (
      segments[0] !== 'plugins' ||
      segments.length < 3 ||
      segments.some((segment) => !segment || segment === '.' || segment === '..') ||
      source.includes('\\') ||
      hasControls(source)
    ) {
      fail(`catalog entry ${index} has an invalid repository source path`);
    }
    if (active) published.push({ name: plugin.name, root: source });
  }
  return published;
}

function within(entry, root) {
  return entry.startsWith(`${root}/`);
}

function overlaps(left, right) {
  return left === right || within(left, right) || within(right, left);
}

export function withdrawnPaths(
  baselineFiles,
  currentFiles,
  trackedPaths,
  baselineCatalog,
  currentCatalog,
) {
  const baselineRoots = new Map();
  for (const plugin of baselineCatalog) {
    if (!baselineRoots.has(plugin.root)) baselineRoots.set(plugin.root, new Set());
    baselineRoots.get(plugin.root).add(plugin.name);
  }
  const retiredRoots = new Set();
  for (const [oldRoot, aliases] of baselineRoots) {
    if (
      !currentCatalog.some((plugin) => aliases.has(plugin.name) || overlaps(oldRoot, plugin.root))
    ) {
      retiredRoots.add(oldRoot);
    }
  }
  const currentSet = new Set(currentFiles);
  const currentTree = new Set(trackedPaths);
  const withdrawn = [];
  for (const entry of new Set(baselineFiles)) {
    // Resolver-policy exclusions and file-to-directory conversions are not deletions.
    if (
      currentSet.has(entry) ||
      currentTree.has(entry) ||
      trackedPaths.some((file) => within(file, entry))
    )
      continue;
    const owners = [...baselineRoots.keys()].filter((oldRoot) => within(entry, oldRoot));
    // Unmapped curriculum/orphans and ambiguous nested ownership receive no credit.
    if (owners.length !== 1 || !retiredRoots.has(owners[0])) continue;
    const segments = entry.split('/');
    for (let depth = 1; depth < segments.length; depth += 1) {
      if (currentTree.has(segments.slice(0, depth).join('/'))) {
        fail(`removed path has a tracked non-directory ancestor: ${entry}`);
      }
    }
    withdrawn.push(entry);
  }
  return withdrawn.sort();
}

export function checkCorpusShrink(payload, { root = process.cwd() } = {}) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload))
    fail('input must be an object');
  const allowedKeys = new Set(['baseline_count', 'current_count', 'baseline_sha', 'checkout_sha']);
  if (Object.keys(payload).some((key) => !allowedKeys.has(key))) fail('unknown input field');
  for (const [key, minimum] of [
    ['baseline_count', 1],
    ['current_count', 0],
  ]) {
    if (!Number.isSafeInteger(payload[key]) || payload[key] < minimum) {
      fail(`${key} must be a safe integer >= ${minimum}`);
    }
  }
  root = fs.realpathSync(root);
  const checkout = exactCommit(root, git(root, ['rev-parse', 'HEAD']).trim(), 'HEAD');
  if (payload.checkout_sha !== undefined) {
    exactCommit(root, payload.checkout_sha, 'checkout_sha');
    if (payload.checkout_sha !== checkout) fail('checkout_sha does not match HEAD');
  }
  if (git(root, ['status', '--porcelain=v1', '-z', '--untracked-files=no'])) {
    fail('tracked index and worktree must be clean at HEAD');
  }
  const baseline = exactCommit(root, payload.baseline_sha, 'baseline_sha');
  try {
    git(root, ['merge-base', '--is-ancestor', baseline, checkout]);
  } catch {
    fail('baseline_sha must be an ancestor of HEAD');
  }

  const baselineFiles = resolveCorpus('graded', { root, ref: baseline });
  const currentFiles = resolveCorpus('graded', { root, ref: checkout });
  if (baselineFiles.length !== payload.baseline_count)
    fail('baseline_count contradicts baseline Git census');
  if (currentFiles.length !== payload.current_count)
    fail('current_count contradicts checkout Git census');
  const baselineCatalog = publishedCatalog(root, baseline);
  const currentCatalog = publishedCatalog(root, checkout);
  const currentSet = new Set(currentFiles);
  const removed = baselineFiles.filter((entry) => !currentSet.has(entry));
  const currentTree = git(root, ['ls-tree', '-r', '-z', '--name-only', '--full-tree', checkout])
    .split('\0')
    .filter(Boolean);
  const withdrawn = withdrawnPaths(
    baselineFiles,
    currentFiles,
    currentTree,
    baselineCatalog,
    currentCatalog,
  );
  const adjusted = BigInt(currentFiles.length) + BigInt(withdrawn.length);
  return {
    allowed: adjusted * 100n >= BigInt(baselineFiles.length) * 98n,
    baseline_count: baselineFiles.length,
    current_count: currentFiles.length,
    removed_count: removed.length,
    withdrawn_count: withdrawn.length,
    unmatched_net_loss: baselineFiles.length - currentFiles.length - withdrawn.length,
    baseline_sha: baseline,
    checkout_sha: checkout,
    withdrawn_paths: withdrawn,
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 0 && (args.length !== 2 || args[0] !== '--repo-root' || !args[1])) {
      fail('usage: check-corpus-shrink.mjs [--repo-root PATH] < payload.json');
    }
    const result = checkCorpusShrink(JSON.parse(fs.readFileSync(0, 'utf8')), { root: args[1] });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 2;
  }
}
