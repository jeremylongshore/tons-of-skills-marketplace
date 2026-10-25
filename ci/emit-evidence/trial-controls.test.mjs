/* global structuredClone */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { assertTrialApproval } from './check-trial-approval.mjs';
import { mergeCheckPages } from './merge-check-pages.mjs';
import { requiredCheckOutcomes } from './emit-evidence.ts';

// GitHub documents the approvals response with user + environments (plural):
// https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run
// This is a contract fixture, not a captured live approval or activation proof.
function approved() {
  return [
    {
      id: 12,
      name: 'cosign-v3-trial',
      protection_rules: [
        { type: 'required_reviewers', reviewers: [{ type: 'User', reviewer: { id: 213859472 } }] },
      ],
      deployment_branch_policy: { protected_branches: false, custom_branch_policies: true },
    },
    { total_count: 1, branch_policies: [{ name: 'main', type: 'branch' }] },
    [
      {
        state: 'approved',
        user: { id: 213859472 },
        environments: [{ id: 12, name: 'cosign-v3-trial' }],
      },
    ],
  ];
}

test('accepts the configured owner gate and actual run approval together', () => {
  assert.doesNotThrow(() => assertTrialApproval(...approved()));
});

for (const [name, mutate] of [
  [
    'unprotected auto-created environment',
    (x) => {
      x[0].protection_rules = [];
    },
  ],
  [
    'different reviewer',
    (x) => {
      x[0].protection_rules[0].reviewers[0].reviewer.id = 1;
    },
  ],
  [
    'additional reviewer could bypass owner',
    (x) => {
      x[0].protection_rules[0].reviewers.push({ type: 'User', reviewer: { id: 1 } });
    },
  ],
  [
    'wildcard branch',
    (x) => {
      x[1].branch_policies[0].name = '*';
    },
  ],
  [
    'tag named main',
    (x) => {
      x[1].branch_policies[0].type = 'tag';
    },
  ],
  [
    'no run approval',
    (x) => {
      x[2] = [];
    },
  ],
  [
    'other actor approved or bypassed',
    (x) => {
      x[2][0].user.id = 1;
    },
  ],
  [
    'rejected review',
    (x) => {
      x[2][0].state = 'rejected';
    },
  ],
  [
    'approval for another environment',
    (x) => {
      x[2][0].environments[0].id = 99;
    },
  ],
]) {
  test(`refuses ${name}`, () => {
    const fixture = structuredClone(approved());
    mutate(fixture);
    assert.throws(() => assertTrialApproval(...fixture));
  });
}

test('joins two pages before evaluating required-context duplicates', () => {
  const checks = [
    { name: 'ci-required', status: 'completed', conclusion: 'success' },
    { name: 'gitleaks', status: 'completed', conclusion: 'success' },
    { name: 'skill-conform', status: 'completed', conclusion: 'success' },
    { name: 'ci-required', status: 'in_progress', conclusion: null },
  ];
  const report = mergeCheckPages([
    { total_count: 4, check_runs: checks.slice(0, 2) },
    { total_count: 4, check_runs: checks.slice(2) },
  ]);
  assert.deepEqual(report.check_runs, checks);
  assert.throws(() => requiredCheckOutcomes(report), /must appear exactly once/);
  const valid = mergeCheckPages([
    { total_count: 3, check_runs: checks.slice(0, 1) },
    { total_count: 3, check_runs: checks.slice(1, 3) },
  ]);
  assert.equal(requiredCheckOutcomes(valid).length, 3);
  assert.equal(report.check_runs.filter((check) => check.name === 'ci-required').length, 2);
  assert.equal(JSON.parse(JSON.stringify(report)).check_runs.length, 4);
});

test('refuses truncated, changing and malformed page responses', () => {
  for (const pages of [
    [],
    {},
    [{ total_count: 2, check_runs: [] }],
    [
      { total_count: 0, check_runs: [] },
      { total_count: 1, check_runs: [] },
    ],
    [{ total_count: 0 }],
    [{ total_count: '0', check_runs: [] }],
  ]) {
    assert.throws(() => mergeCheckPages(pages));
  }
});
