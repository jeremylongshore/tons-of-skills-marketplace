# Local Development Implementation

## Project Structure and Configuration

Keep application migrations and tests in the project. Store actual credentials in
ignored local configuration, not committed fixtures. Install the SDK and CLI through
your chosen supported package workflow; use the [local development guide](../SKILL.md)
for stack startup, migration, and reset procedures. Do not run those operations just
to check that a client object can be constructed.

```text
src/supabase/client.ts
src/index.ts
tests/supabase.test.ts
supabase/migrations/
.env.example
.env.local              # ignored; actual configuration
```

A development script can use `tsx watch src/index.ts`; that requires a deliberately
installed project dev dependency. A test runner such as Vitest is likewise an
explicit project prerequisite, not an SDK feature.

## Client Construction Test Without Provider Requests

This Vitest example calls no query, auth, storage, or Realtime methods. It verifies
only local construction, not connectivity or the validity of a key. The key is a
synthetic non-secret fixture, and persistence/refresh are disabled.

```typescript
import { describe, it, expect } from 'vitest';
import { createClient } from '@supabase/supabase-js';

describe('Supabase client construction', () => {
  it('constructs an HTTP client without calling the provider', () => {
    const client = createClient('http://127.0.0.1:54321', 'synthetic-public-test-key', {
      auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
    });
    expect(typeof client.from).toBe('function');
  });
});
```

Keep local-stack integration tests separate. Those tests need an explicitly started
local stack, migrated fixture tables, and the keys emitted for that stack. Never
point them at production or infer that this construction test exercises SQL or RLS.

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
