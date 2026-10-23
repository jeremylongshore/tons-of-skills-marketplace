# JavaScript v1-to-v2 Migration Examples

## Keep the Client Factory; Migrate the Actual Methods

Both versions use `createClient(projectUrl, projectKey)`. The migration is not a
rename from a generic `Client({ key })` to `SupabaseClient({ apiKey })`.
The class is exported, but its constructor takes URL and key positional arguments;
use the documented factory in examples.

```typescript
import { createClient } from '@supabase/supabase-js';

export function createStatelessClient(url: string, publishableKey: string) {
  return createClient(url, publishableKey, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
}
```

## Password Sign-In

```typescript
// v1 API, shown only as migration input (do not run with v2):
// await client.auth.signIn({ email, password })

// v2 API: client is an appropriately scoped application client.
import type { SupabaseClient } from '@supabase/supabase-js';

export async function signIn(client: SupabaseClient, email: string, password: string) {
  const { data, error } = await client.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data.user;
}
```

Review the rest of the [upgrade workflow](../SKILL.md), including async auth
methods and Realtime channels. Test returned-error paths as well as thrown
exceptions, and test cookie-session behavior with the supported SSR adapter.
Never globally share one user's authenticated server client with other requests.

## Rollback Is a Reviewed Dependency and Application Change

Retain the exact previous lockfile and source revision before upgrading. If rollback
is needed, restore those approved artifacts through the project's normal review
process and rerun its compatibility/security checks. Do not install the nonexistent
literal version `1.x.x`, choose an arbitrary old release, or assume an SDK downgrade
reverses database migrations or auth configuration. A deprecated v1 release may no
longer satisfy the application's security/support requirements.

[Official v2 upgrade guide](https://supabase.com/docs/reference/javascript/v1/upgrade-guide)

---

_[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)_
