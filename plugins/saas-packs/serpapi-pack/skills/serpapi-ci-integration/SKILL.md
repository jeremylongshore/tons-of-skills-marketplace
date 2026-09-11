---
name: serpapi-ci-integration
description: 'Gate SerpAPI code with sanitized fixtures and isolate optional live searches behind trusted CI environments and allowance controls. Use when adding integration tests to automation. Trigger with "add SerpAPI CI".'
argument-hint: "[github-actions|other-ci] [python|javascript]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit, Bash(gh:*)
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, serpapi, ci, testing, github-actions]
model: inherit
effort: high
compatibility: Designed for Claude Code; CI secret and workflow changes require repository approval, and fork pull requests must never receive the SerpAPI key
---
# SerpAPI Fixture-First CI Integration

## Overview

Make parsing and policy gates deterministic on every change while restricting live search to a separately approved, trusted workflow.

## Prerequisites

- Sanitized fixtures and an injected client boundary
- Repository CI conventions, required checks, and fork threat model
- A protected environment, allowance budget, and owner for any live smoke test

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect tests and workflows, `WebFetch` to verify current client behavior, `Write` or `Edit` for fixtures, tests, and CI, and `Bash(gh:*)` only to inspect or operate the approved GitHub workflow.

## Current Contract

Offline fixture tests require no SerpAPI credential or search allowance. A live search is external, variable, and potentially billable; untrusted pull-request code must not receive `SERPAPI_KEY`, including through unsafe workflow-trigger patterns.

## Authentication

Store `SERPAPI_KEY` only in a protected CI environment. Never expose it to fork PRs, logs, artifacts, command traces, caches, or fixture updates. Give live jobs read-only repository permissions unless a documented need proves otherwise.

## Instructions

1. Inventory CI triggers, fork behavior, permissions, secret scopes, environments, artifacts, and dependency installation.
2. Put parser, adapter, error, pagination, redaction, and policy tests on sanitized fixtures with network disabled.
3. Run fixture tests on every pull request and push using pinned actions and locked dependencies.
4. Define an optional live smoke job on a manual, scheduled, or trusted-main trigger; bind it to a protected environment and explicit concurrency/search budget.
5. Check account capacity first, execute one harmless request, and emit only status, search ID, and safe counts.
6. Make live failure diagnostically visible but decide deliberately whether it is required or advisory; never let provider variance weaken deterministic gates.
7. Test a fork PR path, secret redaction, cancellation, timeout, allowance exhaustion, and artifact contents before enabling the job.

## Approval Boundaries

Do not add secrets, approve a fork workflow, change required checks, or enable allowance-consuming schedules without repository and account-owner approval.

## Output

Return the trigger/permission matrix, fixture test results, live-job boundary and budget, secret-flow proof, fork test evidence, required/advisory decision, and rollback owner.

## Error Handling

| Condition | Response |
|---|---|
| Fork code can reach the secret | Block the workflow and redesign the event boundary. |
| Fixture job attempts network | Fail CI and replace the client dependency. |
| Live check returns 429 | Stop the job and classify throughput versus allowance via Account API. |
| Provider is unavailable | Preserve deterministic gates and report the live lane separately. |

## Example

```yaml
permissions:
  contents: read

jobs:
  fixture-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements.lock
      - run: python -m pytest tests/serpapi -q
```

## Resources

- [GitHub Actions security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Official Python client](https://github.com/serpapi/serpapi-python)
- [Account API](https://serpapi.com/account-api)

## Next Steps

Exercise the fork path and protected live lane, then document which evidence is release-blocking.
