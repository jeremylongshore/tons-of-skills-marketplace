---
name: supabase-ci-integration
description: |
  Configure Supabase continuous-integration and deployment pipelines with
  GitHub Actions: link projects, push migrations, deploy Edge Functions,
  generate types, and run tests against local Supabase instances.

  Use when setting up CI pipelines for Supabase, automating database
  migrations, deploying Edge Functions in CI, or running integration tests.

  Trigger with phrases like "supabase CI", "supabase GitHub Actions",
  "supabase deploy pipeline", "CI supabase migrations", "supabase preview branches".
allowed-tools: Write, Bash(npx:*), Bash(gh:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- ci-cd
- github-actions
- devops
compatibility: Designed for Claude Code
---
# Supabase CI Integration

## Overview

Build GitHub Actions workflows that automate the full Supabase lifecycle: link projects in CI, push migrations on merge, deploy Edge Functions, generate TypeScript types, run tests against a local Supabase instance, and create preview branches for pull requests. Every database change gets validated before it reaches production.

The pull-request CI pipeline runs these stages, all detailed in [ci-workflows.md](references/ci-workflows.md):

1. Start a local Supabase instance (unused services disabled for speed).
2. Apply every migration from scratch with `npx supabase db reset`.
3. Regenerate TypeScript types and fail the build on drift from the committed version.
4. Run pgTAP database tests and the application test suite against the local instance.
5. Stop Supabase (always, even on failure).

## Prerequisites

- GitHub repository with Actions enabled
- Supabase project created at [supabase.com/dashboard](https://supabase.com/dashboard)
- Supabase CLI initialized locally (`npx supabase init`)
- Node.js 22+ for the current SDK application and CI examples
- `@supabase/supabase-js` installed:

```bash
npm install @supabase/supabase-js
```

## Instructions

### Step 1: Configure GitHub Secrets and Link in CI

Store credentials as GitHub repository secrets. The CI pipeline uses these to authenticate with your Supabase project without exposing tokens in code.

```bash
# Set secrets via GitHub CLI
gh secret set SUPABASE_ACCESS_TOKEN --body "<your-access-token>"
gh secret set SUPABASE_DB_PASSWORD --body "<your-database-password>"
gh secret set SUPABASE_PROJECT_REF --body "<your-project-ref>"
```

Generate your access token at [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens). Find your project ref in Project Settings > General.

Link the project in any CI job that needs remote access:

```yaml
- name: Install Supabase CLI
  uses: supabase/setup-cli@v1
  with:
    version: latest

- name: Link Supabase project
  run: npx supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

### Step 2: CI Workflow — Test, Validate Migrations, and Generate Types

Add `.github/workflows/supabase-ci.yml` that runs on every pull request. It starts a local Supabase instance, runs `db reset` to apply all migrations from scratch, regenerates types and fails on drift (`git diff --exit-code`), then runs pgTAP and application tests. The default local dev keys are safe to commit — they only work against the local instance. Copy the complete workflow from [ci-workflows.md](references/ci-workflows.md).

### Step 3: Deploy Migrations and Edge Functions on Merge

Add `.github/workflows/supabase-deploy.yml`, scoped with `paths:` to `supabase/migrations/**` and `supabase/functions/**` so it only runs when database or function code changes on `main`. It links the remote project, runs `npx supabase db push`, deploys Edge Functions, and regenerates types from the production schema. Full workflow in [ci-workflows.md](references/ci-workflows.md).

## Preview Branches

Create isolated Supabase environments per pull request with `npx supabase branches create`, so reviewers test against real infrastructure with migrations applied. Preview branches require a Supabase Pro plan and incur compute costs while running. Workflow snippet in [ci-workflows.md](references/ci-workflows.md).

## Testing in CI

Two test layers run inside the CI workflow:

- **pgTAP database tests** in `supabase/tests/` validate that RLS is enabled on public tables and that policies behave correctly. Run locally with `npx supabase test db`.
- **Application tests** use `createClient` from `@supabase/supabase-js` pointed at `http://127.0.0.1:54321` with the local anon key.

Both patterns — the pgTAP SQL and the TypeScript client setup — are in [testing-patterns.md](references/testing-patterns.md).

## Output

After implementing these workflows:

- Pull requests run tests against a fresh local Supabase instance with all migrations applied
- TypeScript type drift is detected automatically — stale types block the PR
- Database migrations deploy to production only on merge to main
- Edge Functions deploy alongside migration changes
- pgTAP tests validate RLS policies and schema constraints in CI
- Preview branches provide isolated environments for PR review (Pro plan)
- GitHub secrets keep `SUPABASE_ACCESS_TOKEN` and `SUPABASE_DB_PASSWORD` out of code

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `supabase start` fails in CI | Docker not available | Use `ubuntu-latest` runner (includes Docker by default) |
| `supabase db push` returns "permission denied" | Invalid or expired access token | Regenerate token at supabase.com/dashboard/account/tokens |
| `supabase link` fails | Wrong project ref | Check project ref in Settings > General, must match `SUPABASE_PROJECT_REF` secret |
| Type drift detected in PR | Schema changed without regenerating types | Run `npx supabase gen types typescript --local > src/types/database.types.ts` |
| `supabase functions deploy` fails | Missing Deno types or syntax errors | Run `npx supabase functions serve` locally first to catch issues |
| pgTAP tests fail | Missing RLS policies or schema constraints | Add policies before merging — `npx supabase test db` runs locally |
| Preview branch creation fails | Free plan limitation | Preview branches require Supabase Pro plan |
| Migration conflict on push | Divergent migration history | Run `npx supabase db pull` to reconcile remote vs local migrations |

## Examples

**Minimal CI for a new project** — just migration validation and type checking:

```yaml
name: Supabase CI
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
        with: { version: latest }
      - run: npx supabase start -x realtime,storage-api,imgproxy,inbucket,edge-runtime
      - run: npx supabase db reset
      - run: npx supabase gen types typescript --local > /tmp/types.ts && diff src/types/database.types.ts /tmp/types.ts
      - if: always()
        run: npx supabase stop
```

For the full CI + deploy + preview workflows and an Edge Function deploy-with-verification snippet, see [ci-workflows.md](references/ci-workflows.md).

## Resources

- [Supabase CLI in CI/CD](https://supabase.com/docs/guides/local-development/cli/getting-started) — official setup guide
- Database Testing with pgTAP — writing and running database tests
- [Managing Environments](https://supabase.com/docs/guides/deployment/managing-environments) — staging, production, preview branches
- [Edge Functions Deployment](https://supabase.com/docs/guides/functions/deploy) — deploying Deno functions
- [Type Generation](https://supabase.com/docs/guides/api/rest/generating-types) — keeping TypeScript types in sync
- [Branching & Preview](https://supabase.com/docs/guides/deployment/branching) — per-PR database environments
- [@supabase/supabase-js Reference](https://supabase.com/docs/reference/javascript/introduction) — client SDK documentation

## Next Steps

For deploying Supabase-backed applications to hosting platforms, see `supabase-deploy-integration`. For configuring RLS policies, see `supabase-rls-policies`.
