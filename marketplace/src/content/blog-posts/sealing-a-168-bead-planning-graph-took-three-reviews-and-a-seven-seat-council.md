---
title: "Cryptography 45.0.6 Revoked; intent-blue-gold Epic 0 Sealed by Council"
description: "intent-blue-gold Epic 0 closed: cryptography 45.0.6 revoked in favor of 50.0.1, then a 168-Bead planning graph passed three adversarial reviews and a seven-seat council."
date: "2026-09-12"
tags: ["intent-blue-gold", "beads", "release-engineering", "supply-chain-security", "adversarial-review", "cryptography", "go", "python", "audit"]
featured: false
canonical: "https://startaitools.com/posts/sealing-a-168-bead-planning-graph-took-three-reviews-and-a-seven-seat-council/"
---
The day's shape is one milestone, one bug-find-fix arc, one new verifier, one planning baseline, three adversarial reviews, and one council vote, all on a single project before lunch on a Saturday and through the rest of the day. The milestone was Epic 0 of intent-blue-gold, the engineering foundation for a 169-requirement BLUE to GOLD to BLUE migration product. The bug was a revoked cryptography spike dependency. The verifier was an independent authorization check for Epic 2. The planning baseline was the Epic 0 to 5 Beads graph, published as 168 executable work Beads. The three reviewers were Ken Thompson, Andrej Karpathy, and Joe Armstrong personas. The council was a seven-seat ISEDC vote.

## Epic 0 closed across 40 child Beads and 9 PRs

Epic 0 is engineering foundation, CI/CD, and repository quality gates. Parent Bead: `intent-blue-gold-qv4`. The swarm molecule is `intent-blue-gold-94x`. The day closed every Epic 0 child Bead: 40 children in the qv4 series, plus the swarm molecule. PRs landed in this order, oldest first:

| PR | SHA | Time | Title |
|---|---|---|---|
| #2  | `ab9f26f` | 03:22 UTC | feat(epic-0): establish governed engineering foundation |
| #3  | `b0a9cbf` | 03:46 UTC | feat(quality): add canonical local repository gate |
| #4  | `3469fd6` | 05:34 UTC | feat(epic-0): enforce validation and pull-request CI |
| #5  | `158dd56` | 06:11 UTC | docs(epic-0): define release governance and exit readiness |
| #6  | `3c925ec` | 13:31 UTC | plan: publish audited Epic 0-5 execution baseline |
| #7  | `732b713` | 15:27 UTC | feat: execute Epic 1 evidence-contract tranche |
| #8  | `52ca95a` | 15:55 UTC | feat: select Epic 1 proof contracts and Epic 2 profile |
| #9  | `838cc7c` | 17:45 UTC | feat: add BLUE source boundary and Epic 2 authorization contracts |
| #10 | `bc5d5d4`  | 16:36 UTC | security: revalidate authorization cryptography |
| #11 | `0cc976d`  | 17:10 UTC | feat(epic-2): add independent authorization verifier |
| #12 | `3121a21`  | 17:42 UTC | Harden Epic 1 source-boundary proof |
| #13 | `67e7ad7`  | 18:24 UTC | feat: add bounded native source observations |
| #14 | `428610c`  | 20:54 UTC | fix: fail closed on malformed proof evidence |

Each PR above contributed a specific slice of the day's work. PR #2 brought the governed engineering foundation (toolchain contract, exact lockfile, clean bootstrap, supply-chain policy, Node 24 checkout). PR #3 brought the canonical 11-stage quality gate. PR #4 brought the validation and pull-request CI plus the contributor workflow. PR #5 closed Epic 0 by filing the release governance and the 16 area reconciliation matrix. PR #6 published the 168-Bead graph plus the planning review PDF. PR #7 closed 14 Epic 1 Beads in one merge. PR #8 selected the implementation stack (Go 1.26.7 spike), the media contract (exFAT plus per-object age envelope), and the integrity strategy (blue-integrity/v1 layered SHA-256). PR #9 added the BLUE source boundary proof in Go and the Epic 2 authorization contracts. PR #10 revoked and revalidated the cryptography spike. PR #11 landed the independent authorization verifier at 1,274 lines. PR #12 hardened fy6.17. PR #13 extended the same proof with bounded native source observations. PR #14 hardened the portable evidence producer so malformed or contradictory Go proof output cannot establish scoped PASS claims.The cumulative diff on the day was 38 changed files in the shortstat rollup, 67,676 insertions, 1,393 deletions. That number is dominated by `planning/epic-0-5/dependencies.json` at 4,067 lines and the SVG dependency graph at 4,197 lines; the actual code surface is smaller.

## The cryptography revocation is the day's real bug-find-fix arc

The original cryptography spike for Epic 2 used `cryptography` 45.0.6 with OpenSSL 3.5.2. That proof dependency was revoked on 2026-09-12 after an exact-version OSV query returned 13 advisories. The replacement spike pinned `cryptography` 50.0.1, `cffi` 2.1.1, `pycparser` 3.0, and the observed OpenSSL 4.0.2 backend. The same dated OSV query returned zero matches for the replacement set. The dependency was rewritten into `requirements-dev.lock` (three new pins), `security/dependency-policy.json` (added `cffi`, the new pinned candidates, and `MIT-0` to allowed licenses), and `planning/epic-2/decision-evidence/cryptography-advisory-review.json` (133 lines of structured advisory review).

DOC-072 captures the conditional status: `CONDITIONALLY REVALIDATED SYNTHETIC DECISION, NO PRODUCT OR DESTRUCTIVE AUTHORITY`. The spike is point-in-time, not timeless. The exact candidate environment passed the bounded e2.8 proof and the dependent e2.10 verifier tests; DOC-074 records e2.10's separate closure reviews.

The spike never implements Ed25519 itself. It uses the `cryptography` package. The constrained JCS profile permits only closed schemas with ASCII property names, NFC strings, safe integers, booleans, null, arrays, and objects. Floats are forbidden. Integers are bounded to the safe integer range. Timestamps are UTC RFC 3339 seconds in `YYYY-MM-DDTHH:MM:SSZ` form. Canonicalization never normalizes strings.

The spike library pin is one of three testable claims in the day's receipts. The other two are the verifier input hashes (`module_sha256` `18c354befae062c6661372f0ecc80fe2735d13642d5eed3eba94e4cbaa1470e1`) and the negative-case count (`41`).

## The Epic 2 independent authorization verifier

PR #11 closed `intent-blue-gold-e2.10` with an in-memory verifier that has no filesystem, device, product-state, signing, or destructive mutation authority. The module is `prototypes/gold/authorization_verifier.py`, 1,274 lines. The test file is `tests/gold/test_authorization_verifier.py`, 744 lines. The evidence script is `scripts/authorization-verifier-evidence.py`, 431 lines. The receipt is `planning/epic-2/verification-evidence/authorization-verifier-receipt.json`. The contract is `authorization-verifier-contract.json`.

The verifier turns authenticated current evidence into preflight eligibility only. Its final check intentionally invokes an external replay capability's atomic `consume_once` state transition. The caller must supply trusted roots, current state, live invariant checks, and that reset-resistant single-use capability. The authorization claim returned is `ELIGIBLE_FOR_INDEPENDENT_GOLD_PREFLIGHT`. Product readiness is `NOT_EVALUATED`. Destructive approval is `NOT_GRANTED`.

The bounded constants are explicit at the top of the module: `MAX_PAYLOAD_BYTES = 64 * 1024`, `MAX_OUTER_BYTES = 96 * 1024`, `MAX_TTL_SECONDS = 86_400`, `CLOCK_SKEW_SECONDS = 300`, `ROOT_THRESHOLD = 2`, `REQUIRED_CRYPTORAPHY_VERSION = "50.0.1"`, `MAX_EXTERNAL_ARTIFACT_BYTES = 4 * 1024 * 1024`, `MAX_EXTERNAL_ARTIFACT_TOTAL_BYTES = 16 * 1024 * 1024`.

The negative evidence covers 41 deterministic cases. The first three cases alone are enough to show the shape: `missing-envelope` expects `ENVELOPE_INVALID` and observes `ENVELOPE_INVALID`; `malformed-envelope` expects `ENVELOPE_INVALID` and observes `ENVELOPE_INVALID`; `outer-parser-bound` expects `ENVELOPE_INVALID` and observes `ENVELOPE_INVALID`. Every case is redacted in the published receipt and the case count is the auditable claim.

The verifier calls `consume_once` on an external replay capability. That is the only mechanism by which a signature turns into preflight eligibility. A successful signature alone is not eligibility. A successful live invariant check alone is not eligibility. The single-use consumption is the gate.

Here is the load-bearing part of the module header:

```python
AUTH_PAYLOAD_TYPE = "application/vnd.intentsolutions.blue-readiness-authorization-statement.v1+jcs"
TRUST_PAYLOAD_TYPE = "application/vnd.intentsolutions.blue-readiness-trust.v1+jcs"
KEY_ID_DOMAIN = b"intent-blue/readiness-key-id/v1\x00"
MAX_SAFE_INTEGER = 9_007_199_254_740_991
MAX_PAYLOAD_BYTES = 64 * 1024
MAX_OUTER_BYTES = 96 * 1024
MAX_TTL_SECONDS = 86_400
CLOCK_SKEW_SECONDS = 300
ROOT_THRESHOLD = 2
REQUIRED_CRYPTOGRAPHY_VERSION = "50.0.1"
MAX_EXTERNAL_ARTIFACT_BYTES = 4 * 1024 * 1024
MAX_EXTERNAL_ARTIFACT_TOTAL_BYTES = 16 * 1024 * 1024
```

The `MAX_SAFE_INTEGER` is the JavaScript safe-integer limit, which matters because the JCS profile permits integers only within that range and forbids floats entirely. `MAX_PAYLOAD_BYTES` and `MAX_OUTER_BYTES` bound the inputs the verifier will even attempt to parse. `CLOCK_SKEW_SECONDS` at 300 is the freshness window the verifier allows against its own trusted clock. `ROOT_THRESHOLD` at 2 means the trust manifest must carry at least 2 active Ed25519 roots for any signature check to advance. The cryptography version pin is the spike-library lock: anything other than the pinned version fails before the JCS parser runs.

The sensitive-text and secret detector regexes are also at the top of the module. The list rejects raw email patterns, file paths under known roots, `password` or `secret` assignments, PEM private-key headers, and a curated vocabulary of credential words. Every claimed evidence byte runs through these regexes before the verifier signs anything back.

## Epic 1 evidence tranche and fy6.17 hardening

PR #7 closed 11 Epic 1 Beads in one merge. The DOC files for those Beads all landed in the same diff: DOC-044 (document consistency), DOC-060 (safety invariants and failure matrix), DOC-061 (Omarchy legal and brand authority boundary), DOC-062 (Omarchy upstream release), DOC-063 (Windows migration support matrix), DOC-064 (hardware preflight boundary), DOC-065 (schema v2 contract), DOC-066 (Epic 1 proof architecture), DOC-067 (Stage 0 feasibility report). The DOC-067 report ends with an evidence-traced conditional GO for bounded synthetic Epic 1 implementation only, with explicit product, GOLD, destructive, and release STOP boundaries.

PR #12 then hardened `fy6.17`, the BLUE source boundary proof. The hardening added an explicit stdin key, a migration-scoped domain-separated HMAC reference, explicit personal attestation, strict SID parsing, and a deterministic portable evidence receipt. `make check` passes 14 of 14 stages; 235 Python tests plus the 13-stage Go proof gate run. PR #13 extended the same proof with bounded native source observations: SMBIOS identity, installed memory, firmware, Secure Boot, TPM, management, profile, and physical storage. The bounded parsers (`internal/nativeparse/smbios.go` 142 lines, `internal/nativeparse/storage.go` 235 lines) never write a handle and use desired access `0` for volume and disk handles. The collector (`internal/windowsadapter/collector_windows.go`) grew from 562 to 1,357 lines. PR #14 closed the loop by hardening the portable evidence producer so malformed or contradictory Go proof output cannot establish scoped PASS claims: the producer now requires the exact ordered, unique 13-stage `go-proof-gate/v1` denominator, requires successful process status and integer-zero exit codes for every stage, and emits `NOT_ESTABLISHED` claims on any failed or malformed gate.

The Bead stayed open. Genuine standard-user Windows 10/11 x86-64 client C01 to C09 evidence, BitLocker and EFS completion, independent write monitoring, and client source-unchanged proof remain absent.

## The Epic 0 to 5 Beads execution graph

PR #6 published the graph. The structured receipt is `planning/epic-0-5/audit-report.json`. The top-level summary:

```text
mapped_bead_count_excluding_root_epics_and_molecules: 168
graph_node_count: 176
graph_edge_count: 485
root_epic_count: 6
status: PASS
product_readiness: NOT_EVALUATED
release_readiness: NOT_EVALUATED
destructive_approval: NOT_GRANTED
errors: []
```

Per epic: 0 has 62 work Beads, 1 has 28, 2 has 16, 3 has 20, 4 has 21, 5 has 21. The audit checks are `absence_of_product_code_changes`, `blueprint_coverage`, `dependency_validity`, `graphviz_render`, `one_parent_mapping`, `published_count_consistency`, `risk_coverage`. Every check passes. The critical path is 45 Beads long. The deliverable PDF at `planning/epic-0-5/deliverables/intent-blue-gold-epic-0-5-planning-review.pdf` is 50,656 bytes, with a separate QA receipt confirming the white-glove review and email delivery.

The graph is at the useful limit of planning granularity. The DOC-058 wording is precise: "Add a Bead only for a demonstrated uncovered failure, missing accountable owner, or evidence bottleneck."

## Three adversarial reviews, three real findings

Grok 4.5 ran a headless adversarial audit first. It found three material defects. R-005 and R-006 had their canonical mappings swapped; portable synthetic proof was accidentally downstream of destructive hardware; and the audit did not explicitly enforce the full BLUE readiness ancestry. Risk evidence was also weaker for lost BLUE media, GOLD provenance, Windows malware, and Omarchy legal and brand authority. Every material finding was accepted and remediated at the planning layer.

Ken Thompson then reviewed. The finding list: a mutable audit trust boundary, an absent restore destination identity at the write boundary, a path time-of-check to time-of-use race, and fragmented secret-canary coverage. The remediation added `e4.21` (restore write identity binding) and `fy6.30` (lost BLUE confidentiality, requiring wrong-key, raw-media, lost-media, recovery, substitution, interruption, and interoperability proof).

Andrej Karpathy reviewed next. The finding list: novice-test ambiguity (the experiment contract said "run the complete physical workflow across BLUE backup, authorization, GOLD install, BLUE restore" while DOC-041 prohibits asking a participant to boot real hardware), candidate provenance after hardware proof, optional AI evaluation ambiguity, mixed performance environments, and planning PASS being too easy to confuse with runtime evidence. The remediation made `e5.11` prohibit participant-controlled disk mutation, real credentials, personal data, and unlabeled simulation. Optional AI is default-deferred. The deterministic WELCOME must complete its full sequence with deterministic logic alone. Any future model route requires versioned evals, privacy oracles, and drift triggers before it can ship.

Joe Armstrong reviewed last. The finding list: a closed-parent lifecycle error (`bd show intent-blue-gold-qv4` reported `CLOSED` while `qv4.17` and `qv4.17.1` were still `IN_PROGRESS`), missing single-writer recovery ownership, restore journal concurrency ambiguity, and no authoritative cross-stage partial-success ledger. The remediation added `e5.19` as the append-only migration ledger, single-writer fencing, restart reconciliation, partial states, retry limits, and the sole definition of COMPLETE. The closed-parent lifecycle error was caught by the audit integrity remediation, which now rejects closed parents with open descendants.

All P0 findings and material P1 findings were accepted. The audit pins its baseline, blueprint denominator, risk identity and severity, published counts, planning-only semantics, and input hashes. It has an independent receipt verifier.

## The seven-seat council vote

A seven-seat ISEDC executive council reviewed the remediated graph on 2026-09-12. The seats: CTO, GC, CMO, CFO, CSO, CISO, VP DevRel. The vote was 7 to 0 to approve the graph as canonical planning authority only. The vote was also 7 to 0 that planning reachability does not prove runtime enforcement, that planned risk coverage does not close risk, that further decomposition should stop until execution exposes a real gap, and that the owner-review package must remain separate from product, destructive, legal, and release approval.

The five durable decisions, all from DOC-059:

- **D1**: `APPROVE_CANONICAL_PLANNING_ONLY`. Every PASS must display `PLANNING_ONLY`, `product_readiness: NOT_EVALUATED`, and `destructive_approval: NOT_GRANTED` beside it.
- **D2**: `PLANNING_ORDER_GATES_PASS_RUNTIME_UNPROVEN`. BLUE-before-GOLD and portable-before-destructive reachability pass. Future mutation boundaries must independently enforce authorization, identity, provenance, containment, single-writer fencing, and terminal state even when invoked outside Beads.
- **D3**: `RISK_PATHS_ACCEPTED_RISKS_REMAIN_OPEN`. R-010 (confidentiality), R-011 (GOLD authenticity), R-018 (legal and upstream authority) block readiness whenever required evidence or authority is absent. Checksums do not prove authenticity. Research does not confer permission.
- **D4**: `FREEZE_TOPOLOGY_PENDING_EXECUTION_EVIDENCE`. The 168-work-Bead graph is at the useful limit. Add a Bead only for a demonstrated uncovered failure, missing accountable owner, or evidence bottleneck.
- **D5**: `DELIVER_OWNER_PLANNING_REVIEW_WITH_SEPARATE_AUTHORITIES`. Planning, runtime, participant consent, destructive safety, legal and upstream, and publication approvals cannot substitute for one another.

The five seats that selected "planning PASS being misread as product or destructive approval" as the most costly weakness outvoted the two seats that picked absent legal authority and premature upstream claims. All three are instances of an evidence type being granted authority it does not possess. The signed declaration reads: "I accept the council decision and binding constraints. This authorizes the Epic 0 to 5 graph as the canonical execution plan only and grants no product, destructive, legal, security-attestation, upstream, or release authority."

## intent-solutions-landing: customer-first release on the same day

The second repo shipped a separate doc-only pass on 2026-09-12. PR #53 (`24b3ebf`, 19:12 UTC) `Clarify Intent Solutions messaging and individual site journeys` rewrote 51 files: 1,217 insertions, 4,280 deletions. The site map is now governed (DOC-085), the brand family contract is filed (DOC-084), the estate visitor journey map is recorded (DOC-087), and a customer-first release document is filed (DOC-086). Sixteen superseded service and learning pages retain their URLs as noindex handoffs. The old survey confirmation stops claiming a submission or email occurred simply because someone opened the URL. Existing legal text is unchanged.

Two follow-up commits filed DOC-086 in 000-docs and updated the changelog. No code path was touched.

## The collaboration shape

Two models ran substantive work on the day. Codex under GPT-5.6 Sol drove the intent-blue-gold worktree sequence: each Epic 0 child Bead landed in an isolated worktree with a fresh base, and the integrating merge ran from root at the end of the tranche. That worktree sequence also produced the Epic 1 evidence tranche, the authoring of DOC-044 through DOC-067 plus the new planning artifacts, the 1,274-line verifier, the 744-line test file, the 431-line evidence script in one continuous PR #11 push, and the seven-seat ISEDC council session that signed the durable decision in DOC-059. Grok 4.5 ran the headless adversarial audit, and that model's session ID (`01a09662-9f1c-7082-9adf-eba6bfae5d48`) is preserved as the audit artifact.

Three persona reviews re-used Codex under GPT-5.6 Sol, but each loaded a different reviewer contract at the start. The Ken Thompson persona tracked trust-boundary failures and the mutable audit trust boundary. The Andrej Karpathy persona tracked evaluation rigor and the distinction between metadata coverage and runtime behavior. The Joe Armstrong persona tracked supervisor recovery, single-writer fencing, and partial-success ledgers. Every persona produced a finding list, never a verdict, and the council merged all three lists into a single remediation set with no scope creep between the personas.

The session log captures 4 operator course-corrections across the day's 992-minute span. One was the redirect from "merge everything and publish the planning review" to "treat every acceptance as scope-limited to planning, runtime, participant consent, destructive safety, legal authority, or publication" once the council chairs surfaced the conflation risk; DOC-059 now bakes that redirect in as decision D5. A second course-correction was the cryptography spike dependency refresh once the OSV query returned 13 advisories against the original pin.

## What it cost

Five fixed bugs across three personas, one revoked cryptography spike, one verbatim re-pinning against a different OpenSSL backend, one 1,274-line verifier with 744 lines of tests, one 168-Bead planning graph with a 4,067-line dependencies JSON and a 4,197-line SVG, one PDF deliverable, one 51-file marketing site clarification, one re-run of the planning auditors after every mutation, and one seven-seat vote. The day produced 58 commits on intent-blue-gold and 5 on intent-solutions-landing. The day's sealed graph is the planning authority. The day's product authority is unchanged: zero.

## Related Posts

- [Perception Is On the Way, on Its Own Domain](https://startaitools.com/posts/perception-is-on-the-way-on-its-own-domain/), 2026-09-11's Perception web and API launch and the same-day intent-blue-gold Beads Epic 0 decomposition
- [Hardening a Marketplace in One Day](https://startaitools.com/posts/hardening-a-marketplace-in-one-day/), 2026-09-08's C44 installable-tree gate and the portable install integrity contract pattern
- [Wrong Mode: Green Is Not a Gate](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/), the original case for why passing a quality gate is not the same thing as proving behavior
