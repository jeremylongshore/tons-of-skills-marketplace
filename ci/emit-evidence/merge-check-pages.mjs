/* global process */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// gh api --paginate --slurp yields one array of page objects. The producer
// consumes one report object, with every check included before duplicate checks.
export function mergeCheckPages(pages) {
  assert.ok(Array.isArray(pages) && pages.length > 0, 'missing check-run pages');
  const total = pages[0].total_count;
  assert.ok(Number.isSafeInteger(total) && total >= 0, 'invalid check-run total');
  const checks = [];
  for (const page of pages) {
    assert.equal(page.total_count, total, 'check-run count changed during pagination');
    assert.ok(Array.isArray(page.check_runs), 'malformed check-run page');
    checks.push(...page.check_runs);
  }
  assert.equal(checks.length, total, 'check-run pages are incomplete or inconsistent');
  return { total_count: total, check_runs: checks };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.stdout.write(JSON.stringify(mergeCheckPages(JSON.parse(readFileSync(0, 'utf8')))) + '\n');
}
