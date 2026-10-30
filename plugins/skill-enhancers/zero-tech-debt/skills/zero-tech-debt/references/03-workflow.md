# The 7-Step Workflow

This is the operational core of zero-tech-debt. Walk the steps in order. Don't skip step 1.

## 1. Define the Intended End State

Before touching code, describe in 1-3 concise paragraphs:

- **What the final UX should feel like** — what the user / operator / caller sees and does
- **What the clean architecture should look like** — one coherent flow, one source of truth, one ownership boundary
- **What the public surface area actually needs to be** — identify which interfaces must remain supported, including compatibility obligations
- **What developers should intuitively expect** — what a new hire would guess without reading the code

If the intended end state is unclear, **stop and clarify before refactoring**. Code is the wrong medium for thinking through architecture; prose is faster and revisable.

## 2. Audit Reality Against Intent

Identify everything in the current implementation that doesn't serve the end state:

- Compatibility shims, legacy wrappers, route aliases, duplicate flows
- Feature flags that became permanent architecture
- State duplicated across layers
- "Just in case" abstractions that turned out never to be needed
- Dead props, modes, handlers, and APIs
- Historical naming that no longer reflects product intent

Document, for each candidate for removal:

- **Why it exists** — what problem was it solving when it was written?
- **Who currently calls it** — is anyone still using it, or is it cargo-culted?
- **Whether it still provides real value** — does the user-visible behavior change if it's gone?

See [`04-audit-patterns.md`](04-audit-patterns.md) for concrete grep targets.

## 3. Delete Before Adding

Before introducing **a new abstraction / hook / config layer / flag / adapter / state container**, attempt to:

- Remove obsolete logic
- Collapse duplicated paths
- Simplify ownership boundaries
- Unify flows
- Flatten unnecessary indirection

**Prefer subtraction over architecture theater.** A refactor that adds three new abstractions to "fix" tech debt has not paid down debt — it has moved it.

Sequence removals and replacements so every reviewable state remains coherent. Use separate steps when independently useful, or one atomic change when the replacement and its callers must move together. Fewer abstractions is a design preference, not permission to remove a required boundary.

## 4. Optimize Around the Final Shape

Refactor toward the system that **should exist today**, not the system that minimizes diff.

Do not preserve bad boundaries simply because:

- They existed historically
- They reduced diff size
- They avoided touching multiple files
- They were once needed during migration

Prefer:

- One coherent flow
- One authoritative source of truth
- One obvious ownership boundary
- One naming system
- One predictable state model

## 5. Collapse Duplicate Decision Logic

Rules should exist in one place. Don't duplicate:

- Permission checks
- Feature gating
- Route logic
- URL parsing
- State derivation
- Validation rules
- Retry behavior
- Command naming
- Orchestration logic

**View components should not secretly own domain policy.** If your React component has a permission check inline, that policy is now duplicated wherever else the resource is accessed. Lift it to one authoritative location.

## 6. Remove Historical Leakage

The codebase should describe **current product intent**, **current domain language**, **current operational reality** — not old implementation history.

Rename:

- Legacy terminology that no longer matches the product
- Migration-oriented naming (`*_v2`, `*_new`, `Legacy*`)
- Implementation-leaked concepts (e.g., a class called `MongoOrderStore` when Mongo was replaced with Postgres last year)
- Misleading abstractions whose names suggest one responsibility but implement another

Prefer names aligned with:

- User behavior
- Domain intent
- System responsibility

A rename without redirecting callers leaves a search-and-find trail of broken references. Update all known owned callers atomically. For published or external consumers, honor the supported contract and document migration or deprecation; do not assume repository search reaches them.

## 7. Validate the New Shape

After refactoring, verify:

- **Deletion evidence covers the intended scope** — re-search tests, config, docs and CI; inspect available downstream contracts and state any unknown or dynamic consumers
- **Navigation still works** — for UI work, click through the affected flows manually, don't rely on snapshot tests
- **Persisted state still behaves correctly** — use an isolated authorized fixture or sanitized snapshot to check mapping, constraints and recovery. Test reversible down/up paths only when supported; otherwise verify restore or forward recovery. Never run migration drills against production by default
- **Permission boundaries remain correct** — check relevant allowed/denied behavior with authorized fixtures or an approved test environment; do not assume a live account is available
- **APIs remain coherent** — for public surfaces, run any contract tests; for internal APIs, walk the call graph
- **Tests validate intended behavior** — a reference to a deleted concept may expose a real regression or contract. Investigate against independent requirements before changing expectations

Add regression coverage for:

- Removed assumptions
- State transitions
- Orchestration boundaries
- Routing behavior
- Migration-sensitive logic

The new tests should describe the _intended shape_, not the historical shape. If you find yourself writing a test that asserts the old behavior, stop and ask whether the old behavior was actually correct.
