# CW-PACK-ADR: Local analysis with explicit execution boundaries

| Metadata | Value |
| --- | --- |
| Status / owner / reviewers | In development / Jeremy Longshore / technical reviewer assignment pending |
| Schema / template | Local envelope 1.0 / Blueprint Docs 3.0.0 |
| Updated / classification / review | 2026-11-05 / public technical / before release |
| Sources / assumptions / unknowns | Owner scope and repository evidence / priority by operator value / live compatibility and model behavior untested |
| Related / supersession | [Authoritative pack blueprint](BLUEPRINT.md) / additive summary, no historical record replaced |

Community-contributed; not affiliated with CoreWeave.

## Decision and rationale

Use portable skills with self-contained local helpers and references. Shared cost
and evidence code is copied byte-for-byte into installed skills and checked for
drift. Operators supply scoped, timestamped observations. Helpers return findings
and uncertainty; the human or protected deployment environment owns authorization.

Three plugin-root agents preload related skills and review findings without shell,
write or dynamic Skill access. Their tool scope cannot execute the commands in a
preloaded skill. No hooks or MCP connection are installed: these offline workflows
need neither automatic interception nor account discovery.

## Alternatives and consequences

A live account adapter would add authentication, egress and spend risk beyond this
scope. Pure model arithmetic would make financial results less reproducible. A
single Terraform root cannot safely discover a NodePool CRD in a not-yet-created
cluster, so provisioning is split into cluster/VPC and node-pool stages. Copying
shared helpers adds bytes but keeps standalone installs valid; drift is blocking.

## Trust and rollout

Untrusted logs/manifests enter parsers, never a shell. Supplied approval JSON is not
an authorization authority. Schema checks, fixture execution and secret scanning
block malformed releases; model behavior and live readiness require separate future
evidence. No gate is weakened to publish this pack. See each skill blueprint for
residual risks, acceptance authority and test mapping.
