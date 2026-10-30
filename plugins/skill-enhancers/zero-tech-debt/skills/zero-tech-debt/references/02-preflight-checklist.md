# Preflight for a structural refactor

Establish evidence before changing a boundary. Scale the depth to consequences:
a local internal rename needs different proof than a public API or persisted-data
redesign. Resolve a material unknown before the dependent change; independent
inspection or design can continue.

## Six questions

1. **What behavior is required?** Read requirements, contracts and relevant tests.
   Existing tests are evidence, not automatically the intended specification.
   Investigate disagreements before changing code or assertions. Add meaningful
   characterization/regression coverage when behavior or risk warrants it.
2. **Who depends on this surface?** Search code, config, docs, generated bindings,
   plugins, published APIs and available downstream consumers. Record exactly what
   was inspected. Repository search cannot prove the absence of dynamic or external
   users. For a public break, resolve supported-client and deprecation obligations.
3. **How can the change recover?** For local source edits, a focused revert may
   suffice. For deployed code or data, identify compatible rollback, restore or
   forward recovery and its limits. A new feature flag is an option, not a universal
   prerequisite. A code revert does not automatically reverse a schema migration.
4. **What end state is being built?** Describe the desired behavior, architecture
   and ownership in one to three paragraphs. Preserve the user's actual objective;
   do not substitute a smaller, easier-to-test result.
5. **What work overlaps?** Inspect current branches, dirty files and known migration
   work. Preserve unrelated edits. Resolve ownership conflicts before modifying
   overlapping state; continue independent work when possible.
6. **What operational dependencies change?** Inspect relevant logs, metrics, alerts,
   runbooks and config consumers. Update owned references in scope and record
   unresolved coordination. Do not contact people or operate live systems without
   authorization already provided for that action.

## Record limits honestly

Unknown caller coverage, unavailable integration environments or untested recovery
are limitations, not checked boxes. Choose evidence appropriate to the consequence,
retain a required compatibility boundary, or ask for the specific missing decision.
Do not add ceremonial tests or infrastructure merely to complete a checklist.
