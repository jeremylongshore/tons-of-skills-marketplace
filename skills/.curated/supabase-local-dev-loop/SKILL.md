---
name: supabase-local-dev-loop
description: 'Configure Supabase local development with the CLI, Docker, and migration
  workflow.

  Use when initializing a Supabase project locally, starting the local stack,

  writing migrations, seeding data, or iterating on schema changes.

  Trigger with phrases like "supabase local dev", "supabase start",

  "supabase init", "supabase db reset", "supabase local setup".

  '
allowed-tools: Read, Write, Edit, Bash(npx:*), Bash(supabase:*), Bash(docker:*), Bash(curl:*),
  Grep
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- local-development
- docker
- postgres
compatibility: Designed for Claude Code
---
# Supabase Local Dev Loop

## Overview

Run the full Supabase stack locally — Postgres, Auth, Storage, Realtime, Edge Functions, and Studio — using Docker and the Supabase CLI. Local development mirrors production APIs exactly, enabling offline work, fast iteration, and repeatable migration workflows. Schema changes flow through `supabase db diff` to generate migrations, and `supabase db reset` replays them cleanly.

## Prerequisites

- Docker Desktop installed and running (required for all local services)
- Node.js 20+ for the npm CLI; Node.js 22+ for current SDK application examples
- Project CLI dependency installed with `npm install --save-dev supabase`; commands use `npx supabase`

## Instructions

### Step 1: Initialize Project and Start Local Stack

```bash
# Initialize Supabase in your project root
npx supabase init
```

This creates a `supabase/` directory:

```
supabase/
├── config.toml          # Local stack configuration (ports, auth settings)
├── migrations/          # SQL migration files (version-controlled)
└── seed.sql             # Seed data (runs after migrations on db reset)
```

Start the local stack (first run pulls Docker images — takes a few minutes):

```bash
npx supabase start
```

The CLI prints all local endpoints and keys:

```
API URL:          http://localhost:54321
GraphQL URL:      http://localhost:54321/graphql/v1
S3 Storage URL:   http://localhost:54321/storage/v1/s3
DB URL:           postgresql://postgres:postgres@localhost:54322/postgres
Studio URL:       http://localhost:54323
Inbucket URL:     http://localhost:54324
anon key:         eyJhbGciOiJI...
service_role key: eyJhbGciOiJI...
```

Create `.env.local` from these values (git-ignored):

```text
# .env.local
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<anon-key-from-supabase-start>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key-from-supabase-start>
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
```

Verify the stack is running:

```bash
npx supabase status
```

### Step 2: Create Migrations and Seed Data

Create a migration file with a descriptive name:

```bash
npx supabase migration new create_profiles
# Creates: supabase/migrations/<timestamp>_create_profiles.sql
```

Write the migration SQL:

```sql
-- supabase/migrations/<timestamp>_create_profiles.sql
create table public.profiles (
  id uuid references auth.users(id) primary key,
  username text unique not null,
  avatar_url text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Always enable RLS on public tables
alter table public.profiles enable row level security;

create policy "Public profiles are viewable by everyone"
  on public.profiles for select
  using (true);

create policy "Users can update own profile"
  on public.profiles for update
  using (auth.uid() = id);

-- Auto-create profile on signup via trigger
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, username)
  values (new.id, new.raw_user_meta_data->>'username');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

Add seed data for local development:

```sql
-- supabase/seed.sql (runs automatically after migrations on db reset)
insert into auth.users (id, email, raw_user_meta_data)
values
  ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'alice@example.com',
   '{"username": "alice"}'),
  ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'bob@example.com',
   '{"username": "bob"}');
```

Apply migrations and seed data in one command:

```bash
npx supabase db reset
# Drops the database, replays all migrations, runs seed.sql
```

### Step 3: Iterate with Diff-Based Migrations

The core iteration loop: make changes in Studio, diff them into migration files, then verify with a clean reset.

Open Studio at `http://localhost:54323` and make schema changes interactively (add columns, create tables, modify RLS policies). Then capture those changes as a migration:

```bash
# Generate a migration from the diff between migrations and current DB state
npx supabase db diff -f add_bio_to_profiles

# Review the generated file
cat supabase/migrations/*_add_bio_to_profiles.sql
```

The generated migration captures exactly what changed:

```sql
-- Auto-generated by supabase db diff
alter table public.profiles add column bio text;
```

Verify the full migration chain replays cleanly:

```bash
npx supabase db reset
# Success = all migrations + seed apply without errors
```

Push verified migrations to a remote Supabase project:

```text
# Link to remote project first (one-time)
npx supabase link --project-ref <your-project-ref>

# Push migrations to remote
npx supabase db push
```

Daily workflow summary:

```bash
# Start of day
npx supabase start

# After schema changes in Studio
npx supabase db diff -f descriptive_name
npx supabase db reset          # Verify clean replay

# Before committing
npx supabase db reset          # Final verification
npm test                       # Run tests against local instance

# End of day
npx supabase stop
```

## Output

- Local Supabase stack running all services via Docker (Postgres, Auth, Storage, Realtime, Studio)
- Version-controlled migration files in `supabase/migrations/`
- Seed data for repeatable local state
- Diff-based migration workflow for safe schema iteration
- `.env.local` with local connection credentials

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot connect to Docker daemon` | Docker not running | Start Docker Desktop, then retry `npx supabase start` |
| `Port 54321 already in use` | Previous instance still running | Run `npx supabase stop` then `npx supabase start` |
| `supabase db reset` fails | Syntax error in migration SQL | Check the failing migration file, fix SQL, re-run reset |
| `Permission denied` on start | Docker socket permissions | Add user to `docker` group: `sudo usermod -aG docker $USER` |
| `supabase db diff` empty | No schema changes detected | Verify changes were made in the local DB, not just Studio UI cache |
| `relation "auth.users" does not exist` | Running migration outside Supabase | Auth schema only exists in the Supabase-managed Postgres instance |

## Examples

### Connect from Application Code

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,       // http://localhost:54321 locally
  process.env.SUPABASE_ANON_KEY!   // Local anon key from supabase start
)

// Fetch profiles — works identically in local and production
const { data, error } = await supabase
  .from('profiles')
  .select('username, avatar_url')
  .limit(10)
```

### Test Against Local Instance with Vitest

```typescript
import { createClient } from '@supabase/supabase-js'
import { describe, it, expect, beforeAll } from 'vitest'

const supabase = createClient(
  'http://localhost:54321',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'  // Local anon key
)

describe('profiles', () => {
  beforeAll(async () => {
    // Seed data is already loaded via supabase db reset
  })

  it('fetches public profiles', async () => {
    const { data, error } = await supabase
      .from('profiles')
      .select('username')
      .limit(1)

    expect(error).toBeNull()
    expect(data).toHaveLength(1)
    expect(data![0].username).toBeDefined()
  })

  it('enforces RLS on update', async () => {
    // Anon users cannot update profiles (no auth.uid())
    const { error } = await supabase
      .from('profiles')
      .update({ username: 'hacker' })
      .eq('username', 'alice')

    expect(error).not.toBeNull()
  })
})
```

### Edge Function Local Development

```bash
# Create and serve an Edge Function with hot reload
npx supabase functions new hello-world
npx supabase functions serve --env-file .env.local

# Test it
curl -X POST http://localhost:54321/functions/v1/hello-world \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

## Resources

- [Local Development Overview](https://supabase.com/docs/guides/local-development/overview)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli/introduction)
- [Database Migrations](https://supabase.com/docs/guides/deployment/database-migrations)
- [Edge Functions Quickstart](https://supabase.com/docs/guides/functions/quickstart)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)

## Next Steps

Proceed to `supabase-sdk-patterns` for production-ready client initialization, typed queries, and real-time subscriptions.
