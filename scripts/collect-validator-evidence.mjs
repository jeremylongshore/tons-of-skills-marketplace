#!/usr/bin/env node
/** Run independent, read-only canonical validator passes with bounded parallelism. */
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

export const VALIDATOR_PASSES = [
  ['skills', ['scripts/validate-skills-schema.py', '--marketplace', '--skills-only', '--json']],
  ['marketplace', ['scripts/validate-skills-schema.py', '--marketplace']],
  ['agents', ['scripts/validate-skills-schema.py', '--standard', '--agents-only']],
];

export function runValidator(
  args,
  { cwd = process.cwd(), timeoutMs = 180000, maxBytes = 64 * 1024 * 1024 } = {},
) {
  return new Promise((done, reject) => {
    const child = spawn('python3', args, { cwd, stdio: ['ignore', 'pipe', 'pipe'] });
    const stdout = [],
      stderr = [];
    let size = 0,
      failure;
    const stop = (message) => {
      failure ??= new Error(message);
      child.kill('SIGKILL');
    };
    const timer = setTimeout(() => stop('Canonical validator timed out'), timeoutMs);
    for (const [stream, chunks] of [
      [child.stdout, stdout],
      [child.stderr, stderr],
    ]) {
      stream.on('data', (chunk) => {
        size += chunk.length;
        if (size > maxBytes) stop('Canonical validator output limit exceeded');
        else chunks.push(chunk);
      });
    }
    child.on('error', (error) => {
      clearTimeout(timer);
      reject(error);
    });
    child.on('close', (status, signal) => {
      clearTimeout(timer);
      if (failure || signal || ![0, 1].includes(status))
        return reject(failure || new Error(`Canonical validator failed: ${signal || status}`));
      done({
        status,
        stdout: Buffer.concat(stdout).toString('utf8'),
        stderr: Buffer.concat(stderr).toString('utf8'),
      });
    });
  });
}

export async function collectValidatorEvidence({ run = runValidator, concurrency = 2 } = {}) {
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 2)
    throw new Error('Validator concurrency must be 1 or 2');
  const results = {};
  let next = 0;
  await Promise.all(
    Array.from({ length: concurrency }, async () => {
      while (next < VALIDATOR_PASSES.length) {
        const [name, args] = VALIDATOR_PASSES[next++];
        const result = await run(args);
        if (
          !result ||
          ![0, 1].includes(result.status) ||
          typeof result.stdout !== 'string' ||
          typeof result.stderr !== 'string'
        )
          throw new Error(`Invalid validator result: ${name}`);
        results[name] = result;
      }
    }),
  );
  return Object.fromEntries(VALIDATOR_PASSES.map(([name]) => [name, results[name]]));
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  collectValidatorEvidence()
    .then((results) => process.stdout.write(JSON.stringify(results)))
    .catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
}
