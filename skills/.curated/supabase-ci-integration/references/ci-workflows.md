# CI/CD Workflow Reference

Full GitHub Actions workflow files for the Supabase CI/CD pipeline. Copy these
into `.github/workflows/` and adjust paths to match your project layout.

## CI Workflow — Test, Validate Migrations, and Generate Types

This workflow starts a local Supabase instance, applies migrations, generates types, and runs your test suite on every pull request. It catches schema drift, broken migrations, and test failures before merge.

```yaml
# .github/workflows/supabase-ci.yml
name: Supabase CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Install dependencies
        run: npm ci

      - name: Install Supabase CLI
        uses: supabase/setup-cli@v1
        with:
          version: latest

      # Start local Supabase (disable unused services for speed)
      - name: Start local Supabase
        run: npx supabase start -x realtime,storage-api,imgproxy,inbucket

      # Apply all migrations and seed data from scratch
      - name: Validate migrations
        run: npx supabase db reset

      # Generate types and detect drift from committed version
      - name: Generate and verify TypeScript types
        run: |
          npx supabase gen types typescript --local > src/types/database.types.ts
          git diff --exit-code src/types/database.types.ts || {
            echo "::error::TypeScript types are out of sync with database schema"
            echo "Run: npx supabase gen types typescript --local > src/types/database.types.ts"
            exit 1
          }

      # Run pgTAP database tests
      - name: Run database tests
        run: npx supabase test db

      # Run application tests against local Supabase
      - name: Run application tests
        run: npm test
        env:
          SUPABASE_URL: http://127.0.0.1:54321
          SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
          SUPABASE_SERVICE_ROLE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

      - name: Type check
        run: npx tsc --noEmit

      - name: Stop Supabase
        if: always()
        run: npx supabase stop
```

The `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY` above are the default local development keys — safe to commit. They only work against your local Supabase instance.

## Deploy Migrations and Edge Functions on Merge

This workflow runs only when migration files or Edge Function source changes are pushed to `main`. It links the remote project and pushes changes to production.

```yaml
# .github/workflows/supabase-deploy.yml
name: Deploy to Supabase

on:
  push:
    branches: [main]
    paths:
      - 'supabase/migrations/**'
      - 'supabase/functions/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - name: Install Supabase CLI
        uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Link project
        run: npx supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      # Push pending migrations to production
      - name: Push database migrations
        run: npx supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}

      # Deploy all Edge Functions
      - name: Deploy Edge Functions
        run: npx supabase functions deploy
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      # Regenerate types from production schema
      - name: Generate production types
        run: |
          npx supabase gen types typescript --linked > src/types/database.types.ts
          echo "Types generated from production schema"
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
```

## Preview Branches

Create isolated Supabase environments for each pull request. Each preview branch gets its own database with migrations applied, so reviewers can test against real infrastructure.

```yaml
# Add to your PR workflow
preview:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4

    - name: Install Supabase CLI
      uses: supabase/setup-cli@v1
      with:
        version: latest

    - name: Link project
      run: npx supabase link --project-ref ${{ secrets.SUPABASE_PROJECT_REF }}
      env:
        SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

    - name: Create preview branch
      run: npx supabase branches create "preview-${{ github.event.number }}"
      env:
        SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

Preview branches require a Supabase Pro plan or higher. Each branch incurs compute costs while running.

## Edge Function Deploy with Verification

Deploy a single function and confirm it responds:

```bash
# Deploy a specific function and verify it's live
npx supabase functions deploy my-function --project-ref $PROJECT_REF
curl -s "https://$PROJECT_REF.supabase.co/functions/v1/my-function" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" | jq .
```
