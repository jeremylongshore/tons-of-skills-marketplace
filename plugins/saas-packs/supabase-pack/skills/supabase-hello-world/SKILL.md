---
name: supabase-hello-world
description: "Run your first Supabase query \u2014 insert a row and read it back.\n\
  Use when starting a new Supabase project, verifying your connection works,\nor learning\
  \ the basic insert-then-select pattern with @supabase/supabase-js.\nTrigger with\
  \ phrases like \"supabase hello world\", \"first supabase query\",\n\"supabase quick\
  \ start\", \"test supabase connection\", \"supabase insert and select\".\n"
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(supabase:*)
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- database
- getting-started
compatibility: Designed for Claude Code
---
# Supabase Hello World — First Query

## Overview

Execute your first real Supabase query: create a `todos` table in the dashboard, insert a row with the JS client, and read it back. This validates that your project URL, anon key, and Row Level Security are configured correctly before you build anything else.

## Prerequisites

- Completed `supabase-install-auth` setup (project URL + anon key in `.env`)
- `@supabase/supabase-js` v2+ installed (`npm install @supabase/supabase-js`)
- A Supabase project at [supabase.com/dashboard](https://supabase.com/dashboard)

## Instructions

The workflow is three steps: create the table (dashboard SQL), insert a row
with the JS client, and read it back to prove the round-trip. The skeleton
below is enough to follow along; the fully annotated code for every step —
including the error-branch comments and expected console output — lives in
[the full implementation walkthrough](references/implementation.md).

### Step 1: Create the `todos` Table

In the Supabase dashboard **SQL Editor**, create the table, enable Row Level
Security (required for anon-key access), and add permissive read + insert
policies for the hello-world exercise:

```sql
create table public.todos (
  id bigint generated always as identity primary key,
  task text not null,
  is_complete boolean default false,
  inserted_at timestamptz default now()
);

alter table public.todos enable row level security;

create policy "Allow public read" on public.todos
  for select using (true);

create policy "Allow public insert" on public.todos
  for insert with check (true);
```

Lock these policies down before production. Verify the table appears under
**Table Editor** before continuing.

### Step 2: Insert a Row

Create the client from your env vars, then insert. Chain `.select()` to get
the inserted row back — `.insert()` alone returns `{ data: null }`:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

const { data, error } = await supabase
  .from('todos')
  .insert({ task: 'Hello from Supabase!' })
  .select()
```

### Step 3: Read It Back

Select all rows and confirm the row you inserted is present:

```typescript
const { data: todos } = await supabase.from('todos').select('*')
// [{ id: 1, task: "Hello from Supabase!", is_complete: false, ... }]
```

Open the **Table Editor** in the dashboard to visually confirm the row is
there. See [implementation.md](references/implementation.md) for the fully
error-handled version of each step.

## Output

- `todos` table created with RLS enabled
- One row inserted via the JS client
- Same row read back with `.select('*')`
- Dashboard confirms the data round-trip

## Error Handling

| Error | Cause | Solution |
| ------- | ------- | ---------- |
| `relation "public.todos" does not exist` | Table not created | Run the Step 1 SQL in the dashboard SQL Editor |
| `new row violates row-level security policy` | RLS blocks the insert | Add the permissive insert policy from Step 1 |
| `Invalid API key` | Wrong anon key in `.env` | Copy from Settings > API in the dashboard |
| `FetchError: request to https://... failed` | Wrong project URL | Verify `SUPABASE_URL` matches dashboard URL |
| `data` is `null` after insert | Missing `.select()` chain | Add `.select()` after `.insert()` |
| Empty array returned from select | RLS blocks reads | Add the select policy from Step 1 |

## Examples

Complete, runnable end-to-end scripts live in
[references/examples.md](references/examples.md) — a full TypeScript script
(insert with `.single()`, then an ordered/limited read-back) and the Python
equivalent. Minimal TypeScript shape:

```typescript
const { data } = await supabase
  .from('todos')
  .insert({ task: 'Hello!' })
  .select()
  .single()
```

- **TypeScript** — [full script](references/examples.md)
- **Python** — [full script](references/examples.md) (`pip install supabase`)

## Resources

- [Supabase Getting Started](https://supabase.com/docs/guides/getting-started)
- [JS Client — Insert](https://supabase.com/docs/reference/javascript/insert)
- [JS Client — Select](https://supabase.com/docs/reference/javascript/select)
- [Python Client](https://supabase.com/docs/reference/python/introduction)
- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)

## Next Steps

Once the round-trip works, proceed to `supabase-local-dev-loop` for the local
development workflow with the Supabase CLI — running Postgres locally, applying
migrations, and syncing schema to your hosted project. Before shipping,
replace the permissive `using (true)` / `with check (true)` policies from
Step 1 with real per-user Row Level Security rules, since the hello-world
policies expose the table to anyone holding the anon key.
