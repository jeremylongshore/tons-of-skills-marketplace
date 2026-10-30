# Audit Patterns — Concrete Things to Grep For

This is the hands-on toolkit for step 2 of the workflow (Audit Reality Against Intent). Each pattern below is a _candidate_ for deletion, not an automatic delete. Examine the context, then decide.

## Marker comments

The most reliable signal of intentional debt: someone already flagged it.

```
rg -n "TODO: remove after|DEPRECATED|legacy|temp:|hack:|XXX:|FIXME"
```

Look especially for `// TODO: remove after <date>` where the date is past, and `// temporary` comments that have been there for over a year.

## Versioned identifiers

Functions, files, classes, types, or modules whose name encodes a version or generation:

```
rg -n "_v2|_v3|_new|_old|_legacy|V2$|V3$|Legacy[A-Z]"
fd -e ts -e tsx -e py -e go -e rs "(_v2|_new|_old|_legacy)"
```

These are usually one of three things:

1. A successful migration where the `_old` should be deleted
2. A failed migration where the `_new` should be deleted
3. An in-flight migration — confirm with the owner before touching

## Stale feature flags

Feature flags older than ~6 months that still default to a single branch:

- Check the flag-management system's "default value never changed" view
- Grep for `if (flags.<flagName>)` and check how many code paths each side has
- A flag with a one-line `else` branch (or no `else` at all) is a candidate for inlining

## Pass-through wrappers

Wrappers whose only job is renaming arguments or repackaging return values:

```python
def get_user(user_id):
    return fetch_user(user_id)

def fetch_user(user_id):
    return _user_repo.find(user_id)
```

Check for distinct policy, instrumentation, test seams or supported interfaces. Collapse layers only when those responsibilities are redundant or deliberately relocated.

## Delegating route handlers

Route handlers that only delegate to other route handlers (often a legacy URL alias kept "just in case"):

```js
app.get('/api/v1/users', (req, res) => app._router.handle({ ...req, url: '/api/users' }, res));
```

Inspect supported clients, redirects and deprecation obligations. Remove an obsolete alias when evidence and the requested scope support it; otherwise document its responsibility.

## Dual-mode forks

`if (env === 'old' || env === 'legacy')` or `if (clientVersion < N)` branches:

- The "old mode" path is rarely tested
- It accumulates new bugs because nobody exercises it
- Killing it requires confirming all consumers are off the old mode — but the data to confirm is usually accessible

## Duplicate config keys

Config keys with near-identical names that diverged over time:

- `database_url` and `db_url`
- `retry_count` and `max_retries`
- `enabled` and `is_enabled`

Choose a canonical key and inspect config producers and persisted values. Set compatibility and retirement timing from actual consumer and release requirements rather than an arbitrary one-release deadline.

## Naming-vs-behavior mismatches

Comments explaining why a name is "actually" different from its behavior:

```js
// note: getUser actually returns a UserProfile, not a User
```

The comment suggests a naming mismatch; inspect the contract and callers before selecting a rename or changing responsibility.

## Tests asserting historical bugs

Tests whose assertions describe behavior the operator/user never wanted:

```js
it('returns null when input is empty (legacy behavior)', () => { ... })
```

Compare the assertion with actual requirements and supported behavior. Neither a legacy label nor a new implementation proves which is correct; reproduce the mismatch and resolve the contract before changing the expectation.

## Indirection without callers

Abstract classes, interfaces or factories with one implementation are inspection candidates. They may define useful policy, substitution, testing or ownership boundaries. Inline only when the seam has no required responsibility or that responsibility is deliberately preserved elsewhere.

## Configuration-driven chaos

Code shaped like:

```python
HANDLERS = {
    "type_a": handle_a,
    "type_b": handle_b,
    "type_c": handle_c,  # only used by one old code path
}
```

Inspect runtime registration, serialization and extension contracts before changing the registry. One caller does not prove an entry is unused or that inlining improves ownership.

## What to do with each match

For each candidate:

1. **Inspect callers and contracts** (workflow step 2), recording coverage and unknowns
2. **Decide**: keep / delete / rename
3. **If deleting**: confirm no telemetry references the names you're removing (workflow pre-flight)
4. **Document** in the PR summary as one line: `deleted: <name> — <one-sentence reason>`

A clean audit produces a punch list. The workflow turns that punch list into commits.
