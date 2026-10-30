/* global process, console */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ownerId = 213859472; // jeremylongshore; this trial is owned by this account.
const environmentName = 'cosign-v3-trial';

export function assertTrialApproval(environment, policies, history) {
  assert.equal(environment.name, environmentName, 'unexpected approval environment');
  assert.ok(Number.isSafeInteger(environment.id) && environment.id > 0, 'missing environment ID');
  const rules = environment.protection_rules?.filter((rule) => rule.type === 'required_reviewers');
  assert.equal(rules?.length, 1, 'required owner-review rule is missing or ambiguous');
  const reviewers = rules[0].reviewers;
  assert.equal(reviewers?.length, 1, 'only the owner may approve this trial');
  assert.equal(reviewers[0].type, 'User', 'reviewer must be the owner account');
  assert.equal(reviewers[0].reviewer?.id, ownerId, 'reviewer is not the owner');
  assert.deepEqual(
    environment.deployment_branch_policy,
    {
      protected_branches: false,
      custom_branch_policies: true,
    },
    'environment must use a custom main-only branch policy',
  );
  assert.equal(policies.total_count, 1, 'environment must allow exactly one branch policy');
  assert.equal(policies.branch_policies?.length, 1, 'incomplete branch-policy response');
  assert.equal(policies.branch_policies[0].name, 'main', 'only main may run the trial');
  assert.equal(policies.branch_policies[0].type, 'branch', 'tags cannot substitute for main');
  assert.ok(Array.isArray(history), 'malformed workflow approval history');
  assert.ok(
    history.some(
      (review) =>
        review.state === 'approved' &&
        review.user?.id === ownerId &&
        Array.isArray(review.environments) &&
        review.environments.some(
          (entry) => entry.id === environment.id && entry.name === environmentName,
        ),
    ),
    'this workflow run has no recorded owner approval for the trial environment',
  );
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const files = process.argv.slice(2);
  assert.equal(files.length, 3, 'expected environment, branch-policy and run-approval JSON files');
  assertTrialApproval(...files.map((file) => JSON.parse(readFileSync(file, 'utf8'))));
  console.log('Cosign trial owner approval and main-only environment verified for this run');
}
