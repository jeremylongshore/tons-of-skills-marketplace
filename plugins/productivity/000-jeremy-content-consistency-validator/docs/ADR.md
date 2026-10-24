# ADR: 000-jeremy-content-consistency-validator — per-fact-class authority registry, deterministic/judged split, fixture-gated Phase 1

> Filed at `docs/ADR.md` beside the rest of the submission set, per
> `000-docs/700-DR-GUID-skill-submission-standard.md` §2 and the first-party `docs/`
> convention (databricks-pack backfill precedent, PR #989). Supersedes the 2026-07-07 ADR
> ("single-pass read-only skill with a report-only contract"), which documented the shell
> this decision deletes.

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-07-09
**Status:** Accepted (Phase 1 of the issue #991 rebuild, per the 11-seat design council synthesized 2026-07-07)

## Context

Two implementations of one command coexisted: the global `~/.claude` skill (the 358-line
engine that actually runs — project-type detection, 9 deterministic drift checks,
severity rules) and the marketplace plugin (a shadowed 682-word shell). They contradict
each other on the truth axiom itself — the engine's reference declares "Code Is Truth"
while the shell hard-codes "Website Is Truth" — so the same fact could be arbitrated in
opposite directions depending on which copy resolved. Issue #991 originally dictated a
multi-agent rebuild; an 11-seat design council (8 thinker canons + 3 engineers, 11
independent structured reviews) returned 11/11 approval for the core fold and 0/11
approval for the dictated scope. Doing nothing leaves the marketplace's flagship
first-party plugin as dead weight and leaves two contradicting authority models live in
the same estate.

## Decision

Five coupled decisions, all council-constrained:

1. **Fold and delete.** Move the global engine into the plugin verbatim where possible;
   delete the shell and its website-is-truth axiom outright. The plugin becomes canonical;
   net LOC goes down versus shell + skill combined.
2. **Authority is a registry, not a ranking.** Source of truth is declared per
   fact-class as data — a versioned, checked-in authority registry (`sot-map.yaml`, home:
   intent-os) with rows `fact_class → owner → mirrors[] → determinism → depth_tier →
   staleness_bound → criticality → volatile`. Validation collapses to: read the fact from
   its declared owner, read the mirrors, diff within the staleness bound (a fast surface
   leading a slow one inside the bound is replication lag, Info-level, not drift). **No
   registry row → no adjudication**: emit "unowned fact-class — human adjudication
   needed" and stop; never guess. Auto-detection survives only as a bootstrap for
   drafting registry rows, never as runtime authority.
3. **Deterministic and judged are structurally separate.** The existing 9 checks are the
   deterministic tier (T1, value equality after non-LLM normalization). Judged/semantic
   checks (T2) are opt-in, advisory-only, and can never be Critical or blocking. T0
   (existence/reachability) is universal and needs no registry row.
4. **Fixture-gated development.** A golden fixture corpus — a clean copy plus N seeded
   drifts — is the plugin's required CI check, with evals asserting findings ("exactly
   these N, zero invented"), not procedure. Nothing else proceeds until red/green exists.
5. **Brain posture: rules, not facts.** The registry is one data file with two consumers —
   the validator reads it, and the brain compiles and cites it as a corpus input; no
   second authority system (Hickey). The brain arbitrates **asserted** company/doctrine
   claims only; **generated** facts (versions, deploy state, counts) stay with their
   generators and never enter the append-only store; the validator never reads the brain
   as ground truth for generated facts, and the brain ingests only findings that survived
   verification and human adjudication. *Conservative fallback, documented:* Torvalds and
   Beck would make the brain a pure consumer with zero arbiter role — if maximum safety
   is preferred over provenance elegance, that is the fallback (open decision 1).
   The record substrate — hash-chained evidence bundles vs plain dated markdown + JSONL —
   is explicitly **deferred** (open decision 4): cheap to add in Phase 2, expensive to
   retrofit later, and not needed to gate Phase 1.

## Alternatives considered

| Alternative                                            | Why rejected                                                                                                                                                                                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Keep a global source-of-truth ranking (either axiom)   | The estate ran both rankings simultaneously and they contradict on the same facts. A ranking arbitrates by position; the registry names the actual producer per fact-class. Hickey, Kleppmann, Pike, and backend-architect independently converged on near-identical registry schemas. |
| Auto-detect authority at runtime (project-type markers) | Silently picks an axiom and can pick the wrong one per fact — cut by Hickey, Huyen, Armstrong, security-auditor. Detection is kept only as a bootstrap convenience for drafting registry rows.                                                                              |
| Multi-agent roster now (the issue's dictated scope)    | 0/11 council approval for v1: Torvalds rejected the whole roster; Pike, Cunningham, Beck, backend-architect concur; Hickey caps any roster at 3 roles. Deferred at most to the Phase-3 judged tail; the conflict with the Fable recommendation is Jeremy's open decision 5. |
| LLM-judged findings on par with deterministic ones     | Judged findings can hallucinate; letting them block would poison the gate — cut by ai-engineer, Hickey, Huyen. Judged stays advisory-only, with re-grounding required before any human sign-off (Phase 3).                                                                  |
| Hash-chained evidence bundles from day one             | Rigor vs ceremony not yet decided (Kleppmann favors chaining). Deferred as open decision 4 rather than resolved implicitly by this PR.                                                                                                                                       |

**Dissents noted, not erased.** Torvalds rejects the depth-tier enum entirely; mitigation
adopted: T0/T1 stay emergent-by-default (run whatever inputs exist), and registry rows are
required only for staleness bounds and T2 promotion. Torvalds/Beck dissent on the brain
arbiter role; their pure-consumer position is the documented conservative fallback above.

## Consequences

**Positive:**

- One engine, one axiom: the shadowing defect is resolved by making the plugin canonical,
  and the code-vs-website contradiction is deleted rather than papered over.
- Authority becomes reviewable data: changing an owner is a diffed, human-reviewed edit
  to `sot-map.yaml`, not an emergent runtime behavior.
- The failure mode improves from "confidently wrong arbitration" to "explicit
  adjudication ask" — an unowned fact-class cannot be silently mis-resolved.
- The fixture corpus makes "it works" falsifiable: exactly-N / zero-invented is a
  regression gate every future change must pass, including the eventual T2 and agent
  work.
- One declaration, two consumers: the registry serves the validator and the brain without
  creating a second authority system.

**Negative / accepted tradeoffs:**

- Registry coverage starts small (7 rows), so early runs will emit "unowned fact-class"
  frequently. Accepted: that noise **is** the adjudication queue — it is the honest
  alternative to guessing.
- Registry maintenance is a standing human cost: every new fact-class needs an
  adjudicated row before the validator will arbitrate it.
- Phase 1 deliberately ships less than issue #991's original ask — no agents, no new
  surfaces. Accepted: the council's build order gates everything on the axiom fix and the
  fixture corpus.
- Judged checks being deferred means semantic capability-claim drift (the classic README
  overclaim) is only shallowly covered in Phase 1. Accepted: T2 is gated on the
  deterministic core holding precision ≥ 0.9 on the corpus (Huyen).
- The staleness-bound model tolerates real drift for up to the bound's duration on
  volatile fact-classes. Accepted: the alternative is flagging every replication lag as
  drift, which trains operators to ignore the report.

## Tool-permission scope

Phase-1 contract for the folded skill — carried from the global engine's grant minus the
cuts. Dropped relative to the two prior implementations: `Agent` (the roster is cut for
v1), `WebSearch` (banned from the grant — council cut list), `WebFetch` (no web surfaces
in Phase 1), and — as always — no `Write`, no `Edit`, no git mutation (read-only is the
contract).

| Tool   | Why it's needed                                                                                                        |
| ------ | ----------------------------------------------------------------------------------------------------------------------- |
| `Read` | Load manifests, docs, workflow YAML, and `sot-map.yaml` for owner-vs-mirror comparison                                  |
| `Glob` | Inventory documentation artifacts; index-vs-filesystem and dead-reference checks (3.1, 3.4, 3.8)                        |
| `Grep` | Deterministic extraction of versions, claims, stale-phase language, and banned-coinage hits across surfaces             |
| `Bash` | Read-only probes the checks require: `git` tag/remote reads and `diff` — scoped invocations (`Bash(git:*)`, `Bash(diff:*)`, `Bash(echo:*)`), never mutation, no network probes (`live_host` rows are adjudicated by the operator running `dig` themselves; the skill only reports the registered expectation) |

## Local report filing addendum — 2026-10-24

The separately requested `claude-flwe.3` work adds durable local reports while
preserving the Phase-1 audit and registry behavior above. A bundled Python helper
uses the destination Intent OS C8 `evidence-ingest` adapter before writing a
plain dated `NNN-AA-AUDR` record and appending its existing index. The skill adds
`Bash(python3:*)` for that helper as a workflow instruction, not a process
sandbox. Its required `--audited-root` guard refuses report/index destinations
inside the declared audited tree. The writer does not repair source or registry
content, contact providers, ingest into the brain or schedule work. The
destination-owned adapter is trusted policy code reviewed by that checkout.

Accepted payloads and content-free receipts must agree; a successful process
exit alone cannot authorize persistence. Rejected or unavailable policy holds
the write. Repair notes remain caller-reported and require supplied evidence;
the helper does not independently certify them. Separate report and index writes
can leave an accepted record needing indexing if the append fails; that result
is explicit and evidence is retained. Plain Markdown plus content-free digests
does not resolve the deferred hash-chain substrate or multi-agent decisions.

The unchanged golden fixture gate still checks audit behavior. Focused portable
tests cover filing and adapter transport; separately selected integration tests
exercise the real unvendored C8 policy copied into scratch destinations. No real Intent OS
record is needed to run those tests.
