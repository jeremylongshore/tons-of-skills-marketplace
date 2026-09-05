# Security boundaries and threat model

## Protected assets

- user source code, documents, credentials, and private prompts;
- repository history, contributor attribution, and release identities;
- validator authority and evidence integrity;
- external services reached through MCP or generated integrations;
- user trust in support and production-readiness claims.

## Threats and controls

| Threat                                      | Required control                                                                                                                        |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Malicious instructions in an imported skill | Treat imported content as untrusted data; inspect before execution; never inherit permissions implicitly.                               |
| Plaintext credential generation             | Use environment-variable references or host secret stores; scan generated output; never print secret values.                            |
| Overbroad tools or MCP methods              | Derive least privilege from actual workflow; undeclared capability fails; destructive methods require a confirmation boundary.          |
| Unsupported runtime claim                   | Consult the harness registry; unknown or candidate status is reported, never promoted in prose.                                         |
| Reviewer hallucination                      | Reproduce every material finding against code, tests, or a primary source before disposition.                                           |
| Evidence fabrication                        | Evidence records contain exact commands, exit codes, hashes, dates, and revisions; the producing agent cannot claim independent review. |
| Path traversal or symlink escape            | Resolve referenced evidence inside the selected root and reject symlinked evidence files.                                               |
| Dependency or bootstrap compromise          | Prefer existing pinned tooling; do not generate remote-pipe installers or unpinned executable dependencies.                             |
| Accidental publication or merge             | Stop at a status checkpoint; require explicit authorization bound to the exact candidate revision.                                      |
| Task-history loss                           | Use Beads when present and required; attach receipts before closure; disclose fallback persistence.                                     |

Portable skills pre-authorize only the minimum local file access required by
their role. Network research, shell commands, task tracking, and subagent
dispatch remain behind the active host's normal permission and project-policy
boundary; listing a workflow step never grants that capability.

## Subagent boundary

Research, architecture, verification, and security roles are read-only. Only the
implementation role may edit files, and it receives no publication authority.
Subagent output is advisory until the coordinator checks its evidence. If the
host cannot isolate roles, execute them sequentially and label the review as
self-review rather than independent review.

## MCP boundary

MCP creation starts from the protocol contract, but client configuration,
transport support, authentication, and approval UI are host-specific. Generated
servers must validate inputs, bound outputs and retries, avoid secret logging,
and separate read-only methods from mutations. High-impact methods require an
explicit confirmation token or remain recommend-only.
