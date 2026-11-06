# Evidence contract: UNOFFICIAL CI INTEGRATION FOR COREWEAVE

Community-contributed; not affiliated with CoreWeave.

Supply a parsed workflow object with the string key `on`, protected_environments, cost_review_bound_to_revision and credential_cleanup_test_passed evidence. Use a YAML 1.2 parser; YAML 1.1 may coerce `on` to boolean. The helper rejects mixed PR/deployment workflows conservatively, unpinned remote actions and common secret-output commands. Repository environment settings and cleanup results must be independently supplied: naming an environment does not enforce reviewer protection. Shell detection is heuristic and does not replace code review of referenced actions, reusable workflows or scripts.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.
