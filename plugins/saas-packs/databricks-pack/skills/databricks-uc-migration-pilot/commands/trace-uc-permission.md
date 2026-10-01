---
name: trace-uc-permission
description: Trace a Unity Catalog permission error to the exact missing grant or group
aliases: [uc-perm, trace-permission]
---

# /trace-uc-permission

Diagnoses a Unity Catalog access failure by invoking the `uc-permission-tracer`
subagent — turning a `PERMISSION_DENIED` / `AccessDenied` into a single actionable
fix instead of an afternoon of doc-spelunking.

## Usage

```
/trace-uc-permission <user> <error>
```

- `<user>` — the affected principal, e.g. `alice@corp.com`.
- `<error>` — the verbatim error, e.g. `PERMISSION_DENIED: SELECT on main.sales.orders`
  or `AccessDenied on s3://bucket/warehouse/orders`.

## What it does

Routes to the `uc-permission-tracer` subagent, which walks the model end to end:

- **UC object error** → account-admin / metastore-admin short-circuit (admin roles
  do NOT inherit `SELECT`) → the full grant chain (`USE CATALOG` → `USE SCHEMA` →
  `SELECT`) → direct and **nested** group membership → the minimal fix.
- **Cloud `AccessDenied`** → the external location + storage credential covering the
  path → the IAM role's bucket trust/permission (read-only `aws` inspection) → the
  credential fix.

## Output

One resolution line naming the exact fix and the grantor, e.g.:

> Add `alice@corp.com` to `data-analysts` **AND** run
> `GRANT SELECT ON TABLE main.sales.orders TO \`data-analysts\`` as metastore
> admin `bob@corp.com`. (Alice is neither account- nor metastore-admin, so the
> grant will not inherit.)

The command diagnoses only — it never runs a `GRANT`; you hand the emitted command
to a metastore admin.
