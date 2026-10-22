# CI routing

`Validate Plugins` runs on every pull request, main push, and manual dispatch.
The required contexts remain `ci-required`, `gitleaks`, and `skill-conform`.
The latter two remain independent workflows without path filters.

## Reviewed change classes

Only modifications of existing regular, non-executable files at these exact
paths can select the lightweight lane:

| Class                    | Path                                             | Minimum checks                                                                                  |
| ------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| Funding metadata         | `.github/FUNDING.yml`                            | Strict funding schema, formatting, secrets, provenance, governance, and all retained jobs below |
| Community governance     | `CODE_OF_CONDUCT.md`                             | Markdown, formatting, secrets, document governance, and all retained jobs below                 |
| Standalone documentation | `docs/zcf-integration.md`                        | Markdown, formatting, secrets, document governance, and all retained jobs below                 |
| All other changes        | Every other path, or any mixed or uncertain diff | Full suite                                                                                      |

There is no Markdown extension or directory-wide exemption. Plugin READMEs
and marketplace Markdown feed published artifacts. Root README, canonical
standards, ownership/security/release documents, workflows, dependencies,
generated catalogs, skills, tests, and executable content select the full suite.
Adding another supported funding platform requires a validator change and full CI.

## Comparison boundary

The classifier runs from the immutable pull-request base commit. Its first
installation selects full CI because that base does not contain the policy.
Subsequent classifier or workflow edits themselves select full CI; a pull
request cannot expand its own allowlist through a modified classifier.

Classification requires complete history, exact base/head/checkout identities,
a merge checkout with the expected parents, and one unambiguous merge base.
It inspects both the cumulative authored change and the integrated change with
NUL-delimited raw Git diffs. It does not use a capped API file list, last-commit
diff, external diff driver, text conversion, or replacement objects.

Additions, deletions, renames, mode/type changes, empty diffs, incomplete history,
malformed comparison data, and unknown events select full CI. A failed
classification job fails the aggregate. Pushes and manual runs always use full
CI, which also provides a forced-full comparison for performance measurements.
Each run uploads a `ci-routing` receipt with its decision and comparison evidence.

This is a routing boundary within the reviewed workflow. It does not prevent a
pull request from rewriting the workflow itself; normal workflow review and
repository protections still apply.

## Retained gates and permitted skips

The initial lightweight lane skips exactly these unrelated jobs:

- `cli-smoke-tests`
- `shellcheck-skills`
- `skill-codeblock-syntax`
- `typescript-coverage-audit`
- `eslint-check`
- `ruff-check`
- `ruff-format-check`

All other aggregate dependencies must succeed. In particular, validation,
compliance, verification, the test matrix, marketplace validation, formatting,
Markdown, supply-chain scanning, curated projection, submission rules, commit
scope, CODEOWNERS, generated-content drift, document governance, and secret
diff scanning remain active. Signed-evidence tests, Snowflake collector integrity,
the Freshie hermetic publication cycle, schema smoke tests, CSP inventory, and
Cowork security checks retain their existing execution paths.

`scripts/ci/fastlane.py` owns the exact dependency and permitted-skip sets.
`ci-required` uses `always()` and rejects missing jobs, unknown jobs, missing or
invalid classification outputs, failures, cancellations, and unexpected skips.
A full-lane run requires success from every dependency. A lightweight run also
accepts success if an eligible job conservatively ran.

## Verification and measurement

Run the focused contract tests with:

```bash
python3 -m unittest tests.ci.test_fastlane tests.ci.test_fastlane_workflow tests.ci.test_funding -v
python3 scripts/ci/validate_funding.py .github/FUNDING.yml
```

The Git tests cover complete multi-commit diffs, more than 300 files, unsafe
paths mixed with safe prose, rename/type/mode attacks, malformed evidence, and
strict aggregation. Workflow tests exercise trusted-base execution and pin the
always-reporting contexts and retained checks.

Hosted measurements must identify the exact head/base commits, run IDs, routing
receipts, and job conclusions. Compare a lightweight PR run with a full run on
the same tree where possible. Report workflow execution wall time and summed
job execution minutes separately from queue time, with the sample size and
cancelled/retried attempts disclosed. Local timings are not hosted savings.
The initial seven-job reduction does not remove the runtime matrices or claim
their savings; completion evidence for the broader fast-lane work is tracked
in Beads `claude-lz24`.

The first paired observation used tree
`228cf55cdc6fcee42801f94d01047e76c68e1593`. Lightweight
[run 39769023664](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/39769023664)
executed 20 jobs and skipped seven: 471 seconds of workflow execution and
1,326 summed job seconds. Forced-full
[run 39769016410](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/39769016410)
executed all 27: 479 seconds and 1,326 summed job seconds. Initial queue times
were six and three seconds respectively. Both were successful first attempts;
an earlier failed attempt on a different tree is excluded. This single pair
shows eight seconds less elapsed execution and **no runner-second savings**.
These figures cover this workflow, not billing or separate review workflows.

The next optimization lets the unchanged test matrix run alongside validation
after classification. Neither job consumes outputs from the other, and the
aggregate still requires both. For proven lightweight changes, the MCP job
builds every MCP workspace and its workspace dependencies; the independent
marketplace job still builds the site and checks CSP and Cowork artifacts.
Full, missing, and unknown lane values retain the whole-workspace build.
The MCP job retains its full dependency installation, tests, coverage,
typechecking, and linting. The lightweight Python job installs the test tools
and the Lumera, penetration-tester, and trading-strategy requirements used by
the complete fixture suite. It still installs root requirements when present.
Full, missing, and unknown lanes retain recursive plugin provisioning. Python
test selection, coverage, and the pinned-Dolt publication fixture are unchanged.
Hosted savings from these changes require a new paired measurement.
