---
name: algolia-ci-integration
description: >-
  Build and review a bounded CI gate for Algolia index configuration and disposable-index smoke tests. Use when search changes need pull-request evidence without mutating production. Trigger with "Algolia CI", "test Algolia in GitHub Actions", or "search deployment gate".
argument-hint: "[repository-path] [test-index-prefix]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- algolia
- ci
model: inherit
effort: medium
compatibility: Designed for Claude Code
---
# Algolia CI Integration

## Overview

This skill adds a deterministic CI lane for code that owns Algolia records, settings, or query behavior. It separates offline contract tests from an optional network smoke test against an explicitly disposable index.

## Prerequisites

- A named repository, environment, and Algolia application or index in scope
- The local lockfile and installed client types as implementation authority
- A safe read-only query or explicitly disposable test target
- Current first-party documentation for any provider behavior that affects the change

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local code, configuration names, tests, and dependency versions. Use `WebFetch` only for current official Algolia documentation. Use `Write` or `Edit` only after identifying the target files, constraints, and verification plan.

## Current Contract

- Pin the Node dependency and runner version already supported by the repository.
- Keep production application IDs, index names, and write credentials out of pull-request workflows.
- Name disposable indices with a run-specific suffix and record their cleanup result.
- Test the exact client methods used by the application; for JavaScript v5, index operations live on the client.

## Authentication

Use a repository secret containing a custom key limited to the disposable index and required ACLs. Do not use an Admin key or expose any write key to forked pull requests.

## Instructions

1. Map the package manager, test runner, Algolia wrapper, and current CI event permissions.
2. Add offline tests for record shaping, settings serialization, and query contracts.
3. Make the live smoke job opt-in or protected, with a unique non-production index name.
4. Create records, wait for the task, perform one known query, and collect request IDs on failure.
5. Delete the disposable index in a guaranteed cleanup step and report cleanup failure separately.
6. Verify untrusted forks cannot read secrets or execute the credentialed job.

## Approval Boundaries

Do not enable secrets for untrusted fork code, reuse a production index, or delete an index whose generated name was not validated. Require review for workflow-permission changes.

## Output

Return the workflow diff, secret and ACL requirements, offline results, smoke-test evidence, cleanup receipt, and the exact conditions under which the network job runs.

## Error Handling

| Condition | Response |
|---|---|
| Secret unavailable | Skip the protected smoke job while keeping offline tests required. |
| Index name is not disposable | Fail before the first write. |
| Task does not complete | Capture task ID and request ID; preserve cleanup. |
| Cleanup fails | Fail the job and identify the retained test index. |

## Examples

Use this compact input and expected handoff to calibrate scope and evidence quality.

Input:

```text
repository=search-service; event=pull_request; smoke=protected
```

Expected handoff:

```text
offline=pass; live=skipped-for-fork; production-writes=0
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [JavaScript API client](https://www.algolia.com/doc/libraries/javascript)
- [API keys](https://www.algolia.com/doc/guides/security/api-keys)
- [JavaScript v5 upgrade](https://www.algolia.com/doc/libraries/sdk/upgrade/javascript)
