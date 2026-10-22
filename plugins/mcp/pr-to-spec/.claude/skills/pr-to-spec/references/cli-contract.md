# pr-to-spec CLI Contract

## Local Comparison Precedence

Local scan, check, and intent-analysis commands build exactly one Git diff:

1. `--staged` uses `git diff --cached`;
2. otherwise `--diff N` uses `HEAD~N`;
3. otherwise `--branch REF` uses `REF...HEAD`;
4. without a ref, branch comparison defaults to `main...HEAD`.

Use the same boundary for the initial scan and final check so evidence remains
comparable. Fetch a remote-tracking ref before relying on it.

## Intent and Governance State

The default state directory is `.pr-to-spec`; `PR_TO_SPEC_DIR` overrides it.
Relevant files include:

- `intent.yaml`: goal, expected and forbidden scopes, maximum risk, type, size
  budget, and approval lifecycle;
- `contracts.yaml`: deterministic verification contracts;
- `policy.yaml`: intent-gate policy;
- graph state: audit relationships and materialized gate results.

These files can affect exit status and release decisions. Review diffs and use
normal repository controls before committing them.

## Exit Status

| Code | Meaning | Operator response |
| --- | --- | --- |
| `0` | Clean for the selected boundary | Preserve evidence and continue |
| `1` | CLI, Git, input, or runtime error | Repair the invocation or state |
| `2` | High-risk change detected | Review `spec.risk_flags` |
| `3` | Intent drift or contract violation | Remediate or explicitly revise intent |
| `4` | Policy gate failed | Satisfy `gate_result.blocking_checks` |

`check` without an intent is deliberately scan-only: it can return `0` or `2`.
A nonzero exit can therefore accompany valid, parseable evidence.

## Agent Protocol

Use `--json` whenever another tool consumes the result. The envelope includes a
schema version, command, status, exit code, structured spec, and optional
intent, signals, gate, and contract results. Parse fields rather than scraping
human-readable prose.

## Remote Pull Requests

The root command analyzes a GitHub pull request:

```bash
pr-to-spec --repo OWNER/REPO --pr 42 --json
```

Use environment-based authentication. Prefer a fine-grained read-only token for
the target repository and never use `--token` where process arguments may be
visible. AI enhancement additionally requires its provider key and is optional;
do not enable it for deterministic local drift checks.

## Safety Boundaries

- Quote scope and forbidden globs.
- Treat repository refs and filenames as untrusted input.
- Do not print secrets or raw environment values in reports.
- Do not rewrite intent after the fact solely to silence drift.
- Preserve the selected diff boundary and JSON evidence across reruns.
- Review any project-state mutation before committing `.pr-to-spec` files.

## Repository Authorities

When documentation and implementation differ, consult:

1. `src/cli/check.ts` and `src/cli/scan.ts` for commands and exit behavior;
2. `src/cli/intent.ts` for intent lifecycle and gate status;
3. `src/core/sources/local.ts` for comparison precedence;
4. `src/core/protocol/envelope.ts` for JSON shape;
5. `src/core/*/storage.ts` for persistent state paths.
