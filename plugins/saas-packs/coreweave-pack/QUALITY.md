# CoreWeave community pack: evidence and limits

Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

**Review date:** 2026-11-07. **Scope:** 26 skills, their individual blueprints, three restricted reviewer agents, shared cost gates, eight new offline evidence reviewers and three existing diagnostic helpers.

## Observed results

| Check | Observed result | What it establishes |
| --- | --- | --- |
| Focused Python regressions | 205 passed on Python 3.12.3; zero failures, errors or skips | Cost gates, evidence contracts, diagnostic behavior, CI examples, archive integrity and installed link boundaries |
| CI regressions | 41 passed | Existing routing, PR title and injection checks remain intact |
| Pack gate | 26 skills and three agents pass canonical static validation | All skill rubric grades A; advisory warnings retained in the receipt |
| Eval packages | All 11 pass J-Rig package checks | Specification integrity; model judgments NOT run |
| Fixture replay | 85 contract fixtures across eight reviewers, plus three diagnostic self-tests pass | Deterministic offline helper behavior; supplied snapshots are not account attestations |
| Terraform | Two mock-provider plan tests pass with Terraform 1.14.3 | Original private cluster/VPC and bounded node-pool templates parse and satisfy mock assertions |
| Artifact inspection | 193 archive files byte-match source; 26 guides, 26 blueprints, 11 eval specs, three agents and two provider lockfiles included | Actual npm archive, required inventory and installed reference boundaries checked; fixtures run from extracted files |
| Hygiene | Gitleaks 8.24.3, Markdown lint, strict Unicode, Ruff, actionlint and shellcheck pass | Tested static surfaces and scoped secret scan; not a security certification |

See [offline-results.json](offline-results.json) for source hashes, individual scores, warnings and explicit limits. This is an unsigned local receipt. The implementation base commit records branch ancestry; per-file hashes bind the tested source changes atop it. Generated catalog commits may follow. Full [static advisory messages](docs/QUALITY-ADVISORIES.md) remain available and are not waived.

CI routing, Terraform mock-provider, actionlint, shellcheck and broad conformance results are retained from the prior review with unchanged scoped inputs; they were not rerun for this health correction. Current validation reruns focused Python tests, installed package fixtures, static skill checks, Markdown/Unicode/Ruff and Gitleaks.

## Safety boundaries tested

Cost-plan validation rejects missing/non-finite rates, stale approvals, changed artifact digests, over-budget totals, duplicate JSON keys and mismatched scope. A matching approval JSON is only a receipt: it cannot authenticate a human or authorize execution. Actual artifact bytes must be rehashed and trusted-channel approval checked immediately before a billable operation.

Evidence helpers preserve missing/stale data, refuse mismatched scope and do not execute instructions embedded in logs. Fixture runs intercept Python socket and subprocess operations and omit account credentials; this is targeted boundary testing, not a universal operating-system sandbox. RBAC group expansion, arbitrary shell semantics and unsupported GPU sharing modes require separate review.

Diagnostic regressions cover RDMA resource defaulting and per-container separation, selected transport versus warnings, GPU-direct evidence, device-specific Xid/remap attribution, non-finite/malformed cost inputs, confirmed versus estimated savings, report escaping and preservation, and private CI credential cleanup after a mocked failure. Terraform review allows a computed VPC ID only when it resolves to the reviewed same-plan root resource; unknown settings remain blocked.

Workload health accepts plain decimal string GPU quantities, reports terminating Pods as incomplete, and checks sample age against evaluation time. Explicit observations separate scheduling, readiness, allocation and activity, preserving Pod/device identity and evidence ages. The 17 health fixtures assert these outputs and refusal cases.

## Coverage that remains open

The 15 guides without eval specs have static metadata, link, packaging and disclaimer checks, plus shared cost-gate coverage where applicable. They do not inherit another skill's behavioral pass. The workload-health blueprint now maps its requirements to installed fixture evidence; native-host permission acceptance remains open. Other blueprints retain proposed acceptance criteria that exceed the observed offline coverage.

No live CoreWeave account, GPU workload, model upload, capacity reservation, billing invoice, recovery or real deployment was exercised. No paid model evaluation, trigger-quality measurement, baseline value comparison, model variance result, production certification, endorsement or partnership is claimed. Plugin agents were checked statically; their skill preloads and tool restrictions still need runtime verification in the deployment environment.

Before live use, the authorized operator must validate account scope, platform versions, pricing, workload acceptance and recovery in a bounded environment. [CoreWeave's official skills](https://github.com/coreweave/skills) are a separate distribution; this pack's implementation is original and does not copy their proprietary code.
