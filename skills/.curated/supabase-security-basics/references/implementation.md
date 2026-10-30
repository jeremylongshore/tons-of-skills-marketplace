# Security Implementation Guide

## 1. Separate Configuration by Capability

Use the actual project URL and publishable key (or supported legacy anon key) for
normal application access. Public keys identify the project; database grants, RLS,
and verified user identity authorize access. They are not secret read/write scopes.
Store secret/service-role keys only in an isolated server environment, never browser
bundles, committed examples, or diagnostic output. Management API personal access
tokens are a separate credential, not the project's Data API key.

```gitignore
.env
.env.local
.env.*.local
```

## 2. Rotate Through the Actual Project Workflow

Inventory which services use the key, create the replacement through the supported
project key-management workflow, update the intended secret store, and verify a
bounded authorized application operation before revoking the old key. Plan rollback
and propagation; legacy JWT-key rotation has different consequences from replacing
a new publishable/secret key. Do not test project credentials against a fabricated
`https://api.supabase.com/health` endpoint or print them in a shell transcript.

## 3. Apply Least Privilege at the Correct Layer

| Use                      | Boundary                                                                      |
| ------------------------ | ----------------------------------------------------------------------------- |
| Browser                  | Publishable/anon key plus user identity and RLS                               |
| Cookie-authenticated SSR | Request-scoped user client; propagate cookies through the framework adapter   |
| Privileged maintenance   | Server-only secret/service-role client after explicit operation authorization |
| Management automation    | Separately scoped authorized Management API identity                          |

There are no generic `read, write, admin` project-key scopes in this example.
Staging is not a reason to grant admin access. Review table grants, Storage policies,
RPC execute privileges, and tenant boundaries explicitly. Never use a privileged
client to make an application authorization failure disappear.

[API keys](https://supabase.com/docs/guides/api/api-keys)
[RLS](https://supabase.com/docs/guides/database/postgres/row-level-security)
[SSR](https://supabase.com/docs/guides/auth/server-side/creating-a-client)
