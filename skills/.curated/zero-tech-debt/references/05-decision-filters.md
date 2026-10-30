# Decision Filters + Anti-Patterns

When the audit has produced candidates and the workflow is in motion, choices accumulate fast. These filters resolve them. The anti-patterns at the bottom name the failure modes to refuse on sight.

## Decision Filters — when choosing between implementations

Prefer the option that:

- **Removes more complexity** — fewer concepts to memorize
- **Reduces future branching** — fewer `if (mode === ...)` paths
- **Reduces special cases** — fewer "this is true except when"
- **Improves discoverability** — a new hire finds it without being told where to look
- **Eliminates hidden behavior** — no surprise side effects, no shared mutable state
- **Centralizes ownership** — one module owns one concept
- **Lowers operational ambiguity** — on-call can act on the alert without paging the author
- **Makes intent obvious from structure** — the directory layout tells you what's where

## Tiebreakers — when the filters above are equal

- **Prefer the option a new hire would understand without a meeting.**
- **Prefer the option that fails loudly over one that fails silently.** Silent fallbacks are how production gets weirder over time.
- **Prefer the option with fewer configuration knobs.** Every config key is a future bug surface.
- **Prefer structure that explains ordinary behavior.** Preserve comments that explain non-obvious domain, security or interoperability constraints.
- **Prefer the option that survives unchanged when the next adjacent feature ships.** Tight coupling to the next feature means you'll be back here in two months.

## Anti-Patterns — refuse on sight

These appear under different names but are the same shape: complexity preserved as an end in itself.

### Architectural anti-patterns

- **Preserving compatibility without checking its purpose.** Establish supported consumers and obligations before either keeping or removing a path; unknown usage is not proof of dead code
- **"Safe" wrappers that hide bad architecture** — moving the smell behind a facade doesn't remove it
- **Generic frameworks for single-use problems** — the YAGNI principle, lived
- **Feature flags that became permanent architecture** — a flag with no plan to remove it is a config knob in disguise
- **Duplicated state ownership** — two stores believing they own the same field is a recipe for divergence
- **Configuration-driven chaos** — when every value is in a YAML, refactoring the code doesn't help; the YAML _is_ the code
- **Indirection without operational value** — if removing the abstraction doesn't make anything worse, the abstraction wasn't doing work
- **Abstractions created solely to avoid touching old code** — the abstraction is the debt

### Process anti-patterns specific to this skill

- **Treating `git blame` as architectural authority.** _Who wrote this_ is not _why it should stay_. The original author may have been correcting an even worse decision that's since been undone.
- **Refactoring tests to match the new code instead of validating intended behavior.** If the test breaks, the test might be right and the refactor wrong. Don't assume.
- **Splitting a replacement into broken intermediate states.** Separate independently useful changes when possible; keep tightly coupled replacement and caller updates atomic when needed.
- **Renaming without redirecting callers** — leaving a search-and-find trail of broken references. Every rename updates every caller in the same commit.
- **Deleting telemetry, metrics, or alerts along with the code they instrumented** without acknowledging it. The dashboard breaks silently and on-call learns about it the hard way.
- **Confusing "fewer lines" with "simpler."** Density is not clarity. A 200-line function can be simpler than ten 20-line ones that pass state through a chain.

## When the operator pushes back on a filter

The filters are heuristics, not laws. If the operator has context you don't have — a regulatory requirement, a contract with a downstream consumer, a known-bug they're tracking — the operator wins. Document the deviation in the PR summary so the next reader doesn't undo it.

But: if the operator's pushback amounts to "this is how we've always done it," that's not context, that's inertia. Push back politely with the filter that resolves the choice and let them decide.
