---
name: coreweave-ci-integration
description: 'Unofficial CI integration for CoreWeave deployments using GitHub Actions.

  Use when automating container builds, deploying inference services from CI,

  or validating GPU manifests in pull requests.

  Trigger with phrases like "coreweave CI", "coreweave github actions",

  "coreweave pipeline", "automate coreweave deploy".

  '
allowed-tools: Read, Write, Edit, Bash(gh:*), Bash(kubectl:*)
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- gpu-cloud
- kubernetes
- inference
- coreweave
compatibility: Designed for Claude Code
metadata:
  display-name: UNOFFICIAL CI INTEGRATION FOR COREWEAVE
---
# UNOFFICIAL CI INTEGRATION FOR COREWEAVE

> **Community-contributed.** Not affiliated with, endorsed by, or sponsored by CoreWeave, Inc. CoreWeave is a registered trademark of CoreWeave, Inc.

## Overview

Separate credential-free pull-request tests from an approved, post-merge staging deployment.
Use Read to inspect the workflow and locked project dependencies, Write the proposed workflow, and Edit it only after the repository owner reviews its trust boundaries.
The example assumes an npm project with `package-lock.json`, `npm test`, and a reviewed `k8s/staging.yaml`; adapt these to the actual repository.

## Prerequisites

- A protected main branch and a protected `coreweave-staging` environment with required reviewers.
- Environment variables `CW_CONTEXT`, `CW_NAMESPACE`, `CW_DEPLOYMENT` and a reviewed staging manifest targeting that exact namespace.
- A dedicated, least-privilege kubeconfig stored as environment secret `COREWEAVE_KUBECONFIG_B64`.
- A runner with kubectl compatible with the cluster; install it through the project’s pinned toolchain before the deploy step.
- A known-good prior manifest/revision, capacity budget and a non-sensitive workload acceptance check.

## Cost and safety gate

Before any billable action, follow the [mandatory cost gate](references/cost-gate.md).
Use the local `scripts/review-cost-plan.py` helper to inspect the exact plan;
then obtain explicit user confirmation through the trusted approval channel.
No plan, missing price, changed digest or expired approval means no execution.
Default to offline inspection; server dry-run and Terraform plan are account calls.

## Instructions

1. Run local unit/manifest checks before push. Run PR tests on an isolated hosted runner with no CKS credential.
2. Permit deployment only for a push to the repository’s protected main branch, after tests pass and environment approval is granted.
3. Materialize the kubeconfig in a private temporary file for the deploy step; never print its contents or place its value in command arguments.
4. Verify the explicit context/namespace and server dry-run the exact reviewed manifest before applying it. Keep billable workload approval separate from offline unit tests.
5. Check rollout and application acceptance. On failure, preserve sanitized events and have the owner apply the retained recovery revision; never weaken branch or environment protection.

## Examples

```yaml
name: Unofficial CI integration for CoreWeave
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
        with:
          persist-credentials: false
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7
        with:
          node-version: '22'
      - run: npm ci
      - run: npm test
  staging:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: unit-tests
    runs-on: ubuntu-latest
    environment: coreweave-staging
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
        with:
          persist-credentials: false
      # Use the project’s reviewed pinned kubectl installation step here.
      - name: Apply approved staging manifest
        env:
          KUBECONFIG_B64: ${{ secrets.COREWEAVE_KUBECONFIG_B64 }}
          CW_CONTEXT: ${{ vars.CW_CONTEXT }}
          CW_NAMESPACE: ${{ vars.CW_NAMESPACE }}
          CW_DEPLOYMENT: ${{ vars.CW_DEPLOYMENT }}
        shell: bash
        run: |
          set -euo pipefail
          : "${KUBECONFIG_B64:?}" "${CW_CONTEXT:?}" "${CW_NAMESPACE:?}" "${CW_DEPLOYMENT:?}"
          umask 077
          export KUBECONFIG
          KUBECONFIG=$(mktemp "$RUNNER_TEMP/coreweave-kubeconfig.XXXXXX")
          trap 'rm -f -- "$KUBECONFIG"' EXIT
          printf '%s' "$KUBECONFIG_B64" | base64 --decode > "$KUBECONFIG"
          kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" auth can-i patch deployments.apps
          kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply --dry-run=server -f k8s/staging.yaml
          kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" apply -f k8s/staging.yaml
          kubectl --context="$CW_CONTEXT" --namespace="$CW_NAMESPACE" rollout status "deployment/$CW_DEPLOYMENT" --timeout=10m
```

The environment must actually require approval; configure that in repository settings.
Review namespace fields inside the manifest as well as the CLI flag, including any cluster-scoped objects.
Run the project’s own model-readiness and acceptance check after rollout before promotion.

## Output

- A workflow with separate PR-test and protected staging-deploy trust boundaries.
- A receipt containing source SHA, image digest, namespace, rollout and acceptance results.
- A recovery decision with explicit unknowns; no production-readiness claim from unit tests alone.

## Error Handling

| Failure | Response |
|---|---|
| Secret or environment variable absent | Stop the deploy; never substitute default context or broader credentials. |
| Tests or server dry-run fail | Fix the reviewed source/manifest; do not skip the gate. |
| Pending GPU workload or rollout timeout | Inspect scoped events and quota/capacity with the platform owner. |
| Credential exposure | Revoke/rotate the staging identity and restrict logs/artifacts before retrying. |

## Resources

- [CI trust, dependencies and recovery](references/operator-notes.md)
- [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [CKS access](https://docs.coreweave.com/products/cks/auth-access/managed-auth/kubeconfig)

## Evidence status

This workflow is a reviewed example, not a live deployment receipt. Offline checks do not establish that the target environment, secret, capacity or application acceptance test exists.
