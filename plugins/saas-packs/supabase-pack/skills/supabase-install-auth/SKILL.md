---
name: supabase-install-auth
description: 'Install and configure Supabase SDK, CLI, and project authentication.

  Use when setting up a new Supabase project, installing @supabase/supabase-js,

  configuring environment variables, or initializing the Supabase client.

  Trigger with "install supabase", "setup supabase", "supabase auth config",

  "configure supabase", "supabase init", "add supabase to project".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Bash(npx:*), Bash(pnpm:*), Bash(pip:*),
  Bash(supabase:*), Grep, Glob
version: 1.55.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- supabase
- setup
- authentication
- sdk
compatibility: Designed for Claude Code
---
# Supabase Install & Auth

## Overview

Install the Supabase SDK, CLI, and project credentials from scratch — covering package install, environment configuration, client initialization, and connection verification for both TypeScript (`@supabase/supabase-js`) and Python (`supabase`).

**Key facts:**

- **npm package:** `@supabase/supabase-js`
- **Python package:** `supabase` (via pip)
- **Client factory:** `createClient()` — never `new SupabaseClient()`
- **Dashboard:** https://supabase.com/dashboard (Settings > API for keys)
- **Docs:** https://supabase.com/docs

## Prerequisites

- Node.js 22+ for current JS SDK releases, or Python 3.9+ for the Python SDK
- Package manager: npm, pnpm, or yarn (JS) / pip (Python)
- A Supabase project created at https://supabase.com/dashboard
- Docker Desktop (only if using local development via `supabase start`)

## Instructions

### Step 1 — Install the SDK and CLI

Install the SDK and the Supabase CLI:

**JavaScript / TypeScript:**

```bash
# Install the SDK
npm install @supabase/supabase-js

# For SSR frameworks (Next.js, SvelteKit, Nuxt), also install:
npm install @supabase/ssr

# Install the Supabase CLI (for types, migrations, local dev)
npm install -D supabase
```

**Python:**

```bash
# Install the SDK
pip install supabase

# Optional CLI through project Node tooling (requires Node.js 20+)
npm install --save-dev supabase
```

For a global CLI command, use the official Homebrew or Scoop installation for your platform instead of global npm installation. Pin the project dependency for team reproducibility. See the [CLI installation guide](https://supabase.com/docs/guides/local-development/cli/getting-started).

Verify the installed CLI is available:

```bash
npx supabase --version
```

### Step 2 — Configure Environment Variables

Retrieve project credentials from the Supabase Dashboard (Settings > API) and create the env file:

```bash
# .env.local (or .env)
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...          # anon key — safe for client-side
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1...  # admin key — server-side ONLY
```

Add env files to `.gitignore` immediately:

```
.env
.env.local
.env.*.local
```

**Security rules:**

- The **anon key** (`SUPABASE_KEY`) is safe for client-side code. It respects Row Level Security (RLS) policies.
- The **service role key** (`SUPABASE_SERVICE_ROLE_KEY`) bypasses RLS entirely. Use only on the server. Never bundle into client code or expose in browser.

### Step 3 — Initialize the Client and Verify

Create a client singleton and verify connectivity:

**TypeScript — client-side (anon key):**

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!
)

export default supabase
```

**TypeScript — server-side (service role key):**

```typescript
// lib/supabase-admin.ts
import { createClient } from '@supabase/supabase-js'

export const supabaseAdmin = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  }
)
```

**Python — client initialization:**

```python
# lib/supabase_client.py
import os
from supabase import create_client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]

supabase = create_client(url, key)
```

**Verify an approved existing diagnostic table and query scope:**

The `_health_check` table below must already exist with the reviewed grants and RLS policy. This step does not create it or prove broader service health.

```typescript
// Quick connectivity check
const { data, error } = await supabase.from('_health_check').select('*').limit(1)
if (error) throw new Error(`Approved query failed: ${error.code}`)
console.log('Approved table query accepted; broader health and RLS remain unverified')
```

`PGRST116` means a singular response returned zero or multiple rows (HTTP 406), not a missing table. Missing-relation/table errors include `42P01` and `PGRST205`; none is a successful health probe. See [PostgREST errors](https://docs.postgrest.org/en/stable/references/errors.html).

**Optional — generate TypeScript types from the database schema:**

```text
npx supabase login
npx supabase link --project-ref <your-project-ref>
npx supabase gen types typescript --linked > lib/database.types.ts
```

Then add the type parameter to the client:

```typescript
import type { Database } from './database.types'
const supabase = createClient<Database>(url, key)
```

## Output

Completing all three steps produces:

- `@supabase/supabase-js` or `supabase` Python package installed
- Supabase CLI available via `npx supabase`
- `.env.local` containing `SUPABASE_URL`, `SUPABASE_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`
- Client singleton module (`lib/supabase.ts` or `lib/supabase_client.py`)
- Server-side admin client (`lib/supabase-admin.ts`, TypeScript only)
- Verified connectivity to the Supabase project

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `FetchError: request failed` | Wrong `SUPABASE_URL` | Verify URL at Dashboard > Settings > API |
| `Invalid API key` | Wrong or expired key | Copy fresh anon key from Dashboard > Settings > API |
| `PGRST301: JWSError` | Malformed JWT in key | Remove trailing whitespace/newlines from env var |
| `Cannot find module '@supabase/supabase-js'` | SDK not installed | Run `npm install @supabase/supabase-js` |
| `ModuleNotFoundError: No module named 'supabase'` | Python SDK not installed | Run `pip install supabase` |
| `supabase: command not found` | CLI not installed | Run `npm install -D supabase`, then use `npx supabase` |
| `Error: supabase start` fails | Docker not running | Start Docker Desktop, then retry `npx supabase start` |
| `TypeError: SupabaseClient is not a constructor` | Wrong import pattern | Use `createClient()` — not `new SupabaseClient()` |

## Examples

Full TypeScript and Python examples with auth sign-up, sign-in, session management, SSR patterns, and type-safe queries: [examples](references/examples.md)

## Resources

- [SDK runtime support](https://github.com/supabase/supabase-js#nodejs) and [Python package requirements](https://pypi.org/project/supabase/) — recheck the selected release before installing
- [Supabase JS Client Reference](https://supabase.com/docs/reference/javascript/initializing) — `createClient` options, auth, database, storage, realtime
- [Supabase Python Client Reference](https://supabase.com/docs/reference/python/initializing) — Python SDK setup and usage
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli/introduction) — local dev, migrations, type generation
- [Supabase Auth Guide](https://supabase.com/docs/guides/auth) — email/password, OAuth, magic links, RLS
- [Generating TypeScript Types](https://supabase.com/docs/guides/api/rest/generating-types) — type-safe database queries
- [Supabase Dashboard](https://supabase.com/dashboard) — project settings, API keys, database editor

## Next Steps

After successful setup, continue with:

- **supabase-hello-world** — run your first database query
- **supabase-rls-policies** — secure your tables with Row Level Security
- **supabase-email-auth** — set up email/password authentication flows
