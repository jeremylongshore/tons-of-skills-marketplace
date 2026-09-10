---
name: windsurf-deploy-integration
description: 'Deploy applications using Devin Desktop (formerly Windsurf)''s built-in deployment features and
  Cascade automation.

  Use when deploying apps from Windsurf, configuring Netlify/Vercel integration,

  or building deployment workflows with Cascade.

  Trigger with phrases like "deploy windsurf", "windsurf deploy",

  "windsurf netlify", "windsurf vercel", "cascade deploy".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(git:*)
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- deployment
- netlify
- vercel
compatibility: Designed for Claude Code
---
# Windsurf Deploy Integration

## Overview

Devin Desktop documents native App Deploys for Netlify. Use Cascade with reviewed provider CLIs or CI workflows for other targets, keeping build, approval, health-check, and rollback evidence explicit.

## Prerequisites

- Windsurf Pro plan or higher
- Deployment platform account (Netlify, Vercel, or cloud provider)
- Application ready to deploy
- Git repository configured

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.
- Use only the command-scoped `Bash` entries declared in frontmatter, with non-destructive checks before mutations.

## Instructions

### Step 1: Use Windsurf's Native Deploy (Netlify)

Windsurf has a first-party Netlify integration:

```
1. Open Cascade (Cmd/Ctrl+L)
2. Prompt: "Deploy this project to Netlify"
3. Cascade runs the build, connects to Netlify, and deploys
4. Preview URL appears in Cascade output
5. Click to verify in browser or use in-IDE Preview
```

For first-time setup:

```
Cascade prompt: "Set up Netlify deployment for this Next.js project.
Configure build command, output directory, and environment variables."
```

### Step 2: Create a Deployment Workflow

```markdown
<!-- .windsurf/workflows/deploy-staging.md -->
---
name: deploy-staging
description: Build, test, and deploy to staging
---

## Pre-Deploy Checks
// turbo-all
1. Run `git status` — abort if uncommitted changes
2. Run `npm run typecheck` — abort if type errors
3. Run `npm test` — abort if test failures
4. Run `npm run lint` — abort if lint errors

## Build and Deploy
5. Run `npm run build`
6. Run `npx netlify deploy --dir=dist --site=$NETLIFY_SITE_ID`
   Or: `npx vercel --yes`

## Post-Deploy Verification
7. Run `curl -sf $DEPLOY_URL/health | jq .`
8. Report: deploy URL, build time, health check result
```

### Step 3: Vercel Deployment via Cascade

```
Cascade prompt: "Prepare a Vercel preview deployment for this project.
- Run the repository build and tests first
- Do not deploy to production
- Do not read or print secret values
- Return the preview URL and rollback instructions"
```

Cascade will run:

```bash
set -euo pipefail
npm ci
npm test
npm run build

# Create a preview only; review provider output before any production promotion.
command -v vercel >/dev/null || { echo "Vercel CLI is not installed" >&2; exit 1; }
vercel --yes
```

Configure environment variables through the provider's approved secret surface. Treat production promotion, domain changes, and rollback as separate, explicitly approved operations.

### Step 4: Cloud Provider Deployment via Cascade

```markdown
<!-- AWS deployment workflow -->
Cascade prompt: "Deploy this Express API to AWS using:
1. Docker container on ECS Fargate
2. ECR for container registry
3. Application Load Balancer
4. RDS PostgreSQL for database
Generate the Dockerfile, task definition, and deployment script."
```

```markdown
<!-- Google Cloud Run deployment -->
Cascade prompt: "Deploy this to Cloud Run:
1. Build Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run with 512MB memory, 1 CPU
4. Set environment variables from .env.production"
```

### Step 5: Preview Deployments for PRs

```yaml
# .github/workflows/preview-deploy.yml
name: Preview Deploy
on: pull_request

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - name: Deploy preview
        run: npx netlify deploy --dir=dist --alias=pr-${{ github.event.number }}
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
      - name: Comment PR with preview URL
        run: |
          gh pr comment ${{ github.event.number }} \
            --body "Preview: https://pr-${{ github.event.number }}--your-site.netlify.app"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Step 6: Use Previews to Verify Before Deploy

```
1. Run build locally: Cascade > "Build and preview the app"
2. Windsurf opens in-IDE Preview tab
3. Click through pages, verify functionality
4. Send broken elements to Cascade: "Fix the layout on mobile"
5. Once Preview looks correct: Cascade > "Deploy to staging"
```

## Output

Return a deployment plan or reviewed change set with target environment, provider, authentication prerequisites, preflight results, immutable revision, health checks, evidence URL, and rollback command. Require explicit approval before any production mutation.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Deploy fails on build | Missing dependencies | Check `npm ci` runs clean |
| Environment variables missing | Not set in platform | Add via CLI or dashboard |
| Preview deploy 404 | Wrong output directory | Check build config: `dist/`, `.next/`, `build/` |
| Netlify integration not available | Older Windsurf version | Update Windsurf to latest |
| Cascade can't deploy | No platform CLI installed | Install netlify-cli, vercel, or gcloud |

## Examples

### Quick Deploy Commands

```
Cascade: "Deploy to Netlify production"
Cascade: "Deploy to Vercel with preview URL"
Cascade: "Build Docker image and push to ECR"
Cascade: "Deploy to Cloud Run with 1GB memory"
```

### Rollback via Cascade

```
Cascade: "Roll back the Netlify deployment to the previous version"
Cascade: "Revert Vercel to the last successful production deploy"
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Devin Desktop App Deploys](https://docs.devin.ai/desktop/cascade/app-deploys)
- [Windsurf Workflows](https://docs.devin.ai/desktop/cascade/workflows)
- [Windsurf Previews](https://docs.devin.ai/desktop/previews)

## Related Skill

Continue with `windsurf-multi-env-setup` to keep approved deployment commands, environment boundaries, and repository guidance consistent across the team.
