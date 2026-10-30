<!-- doc-class: record -->

# GitHub Actions run-volume investigation

Observation date: **2026-10-22 UTC**. Source: **`7b9cc14340aec0c2a3f244e9fb189b099582c08d`**. Tracking: **`claude-jbmk`**, [issue #1450](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1450). Machine-readable receipt: [819, CI run-volume data](819-RA-DATA-ci-run-volume.json).

## Finding and acceptance status

The retained metadata explains a substantial workload: hundreds of distinct main revisions, hundreds of PR revisions, multiple gates per revision, and completion-triggered publisher/explainer runs. It also directly demonstrates a publisher runner allocated only to reject an ineligible PR completion. These findings support the already shipped mitigation; they do not establish an uncontrolled same-head loop as the cause of the original reported total.

The reconstructed issue-time cohort contains **14,645 runs**, 17 above the issue's reported **14,628**. All 14 workflow counts printed in the issue match this cohort exactly. The printed table is partial (13,417 runs across its 14 rows); it is not itself arithmetically inconsistent. The original exact query timestamps are undocumented, and the 17-run overall-count difference remains unresolved.

**Acceptance remains open.** The [September 22 reconciliation](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1450#issuecomment-5786149518) retained a comparable 30-day post-fix measurement. Later seven-day notes do not explicitly waive that requirement. The first 30 complete UTC days after the October 3 merge are **October 4–November 2**, available **November 3 UTC**. This record publishes investigation evidence and implementation provenance without asserting closure.

## Collection and reproducibility

The issue was created September 5 at 19:03:56 UTC and labels its interval August 6–September 5. The audit enumerated the inclusive calendar envelope **August 6 00:00:00–September 5 23:59:59 UTC**: 14,818 distinct run IDs, 56 nonoverlapping query slices and 178 pages. Busy days were subdivided until each slice had fewer than 1,000 records. Returned records matched every slice's count; there were no missing expected records or duplicate IDs within this enumeration. Filtering this envelope through issue creation gives the 14,645-run cohort used below.

Queries used GitHub's repository Actions runs endpoint with a `created` UTC interval, `per_page=100`, and bounded page numbers. The dataset retains the query slices, daily totals, aggregate workflow/event/actor-login/branch counts, ordered run IDs and SHA-256 digests. It omits raw commit objects, emails, credentials and full logs. Digests identify the collected public-metadata projection; they are not independent attestations. Run IDs support later API reinspection, subject to retention and subsequent state changes.

A broad created-filter query repeatedly returned **2,500** for windows whose daily sums were larger. That broad result was withdrawn as an exact count. Daily subdivision gives **3,567** for September 22–October 21; this mixed pre/post interval is not the required 30-day post-fix comparison. The receipt records this observed saturation without claiming a universal documented API cap. Status and latest-attempt fields were read on the observation date, not reconstructed as they stood at issue filing.

## Historical attribution

For the 14,645-run issue-time cohort:

| Event                 | Run records |
| --------------------- | ----------: |
| `pull_request`        |       7,523 |
| `push`                |       3,600 |
| `workflow_run`        |       3,044 |
| `pull_request_target` |         278 |
| `schedule`            |          92 |
| `dynamic`             |          53 |
| `workflow_dispatch`   |          42 |
| `issues`              |          12 |
| `repository_dispatch` |           1 |

The credential principal `jeremylongshore` accounts for 13,585 records; `dependabot[bot]` accounts for 667 and `github-actions[bot]` for 102. Actor identity does not establish whether a person, a local agent or an automation used that credential. The data includes the remaining actor and branch cohorts rather than treating all owner-attributed activity as manual work.

The 1,513 Validate Plugins runs comprise 837 PR runs, 672 main-push runs and four manual runs. PR runs cover 829 distinct heads and 250 branches; main-push runs cover 671 distinct heads. There are 1,504 distinct `(event, branch, head SHA)` groups: nine additional run IDs repeat a group, with a maximum of two run IDs per group. Separately, 26 run records have a latest `run_attempt` greater than one (23 at two, three at three). That is not a count of 26 execution attempts.

August 26 and 27 account for 430 main-push Validate records across 429 distinct heads. This concentration of distinct revisions, each triggering several gates, is concrete volume attribution. It does not establish that every revision was necessary, that all were manually authored, or that no other feedback path exists.

## Trigger graph and bounded feedback findings

At the audited source, the completion-triggered edges are:

- Validate Plugins → publisher and CI Failure Explainer.
- PR Pre-screen → response workflow.
- Deploy → end-to-end workflow.

The explainer and pre-screen response write comments/status information rather than new source commits. The publisher creates package tags/releases; the examined Validate push trigger targets `main`, not those tags. No publisher-to-Validate feedback edge was found in these inspected workflows. This bounded source review and finite run history do not prove global absence of recursion.

The publisher trigger changed **during** the historical interval. Before [commit `33a9ef6`](https://github.com/jeremylongshore/tons-of-skills-marketplace/commit/33a9ef608f02c74ab6d5b5d3775bcbd7d074f152), it listened for main pushes affecting plugin paths. That August 15, 03:01:50 UTC change made it listen for Validate completion, with an eligibility check executed inside a runner. The issue-time cohort has 1,416 publisher records: 1,414 `workflow_run` and two `push`. A publisher record's own `head_branch: main` identifies the downstream workflow context, not proof that the upstream event was a main push.

Auto-bump has a real feedback edge: PR change → auto-bump → credentialed push to the PR branch → further PR checks. Its [base-version idempotency guard](https://github.com/jeremylongshore/tons-of-skills-marketplace/commit/d587ccf39e26ef8321b917b3b147a117493bdcd6) predates the window. It skips an already bumped version relative to the PR base. The 375 auto-bump records cover 372 distinct heads. Thirty-seven Validate PR heads carry the exact standard auto-generated bump subject, across 34 branches. Two apparent repeated bumps are identical patches replayed onto different commits; the dataset records both commit pairs and their matching `git patch-id --stable` values. Repeated bump subjects alone therefore do not prove repeated version increments or an unbounded loop.

The historical sync workflow has six run records; two `automation/sync-external-*` branches appear in Validate, with one run each. Failure conclusions do not prove a sync created no PR: a job can fail after creating one. These observations do not support attributing the entire original volume to sync.

## Publisher jobs: direct evidence and inference

A retained log from [publisher run 31973010125](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/31973010125) identifies successful [PR Validate run 31972765948](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/31972765948) as its upstream source. The publisher guard rejected it with `TRIGGER_EVENT_NOT_PUSH` and `HEAD_BRANCH_NOT_MAIN`. That guard had an assigned runner for five seconds; the other three jobs were skipped. This directly demonstrates avoidable runner allocation before the job-level filter.

The next eligible example, [run 31973602016](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/31973602016), completed its guard, preflight and detection jobs. Its [publish job](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/31973602016/job/95229743190) had no assigned runner and spanned August 16–September 15 before failing with the annotation “The deployment was rejected or didn't satisfy other protection rules.” That supports a protected-deployment wait, not 30 days of CPU use.

[Run 31974318999](https://github.com/jeremylongshore/tons-of-skills-marketplace/actions/runs/31974318999) has no returned jobs and was updated as cancelled one second after the next publisher arrived. Pending-run replacement in the shared `npm-publish-main` concurrency group is a supported inference, consistent with [GitHub's concurrency semantics](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency). This example is not proof that every cancelled historical run allocated zero runners. The 1,290 cancelled publisher records must not be counted as 1,290 completed publisher executions or converted into a billing estimate.

## Shipped controls and observed post-fix windows

[PR #1602](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1602) merged October 3 at 20:39:20 UTC as `f927ef62e5dd89231b3d4430ce4f376a8198f1df`, an ancestor of the audited source. Its controls remain present:

- The [publisher guard job](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/7b9cc14340aec0c2a3f244e9fb189b099582c08d/.github/workflows/publish-changed-packages.yml#L43-L55) only starts for a successful upstream push to `main`; the trusted guard and publication preflight remain in place. An ineligible completion can still create a workflow run record, while jobs are skipped.
- Secret Scan, Check Markdown Links, CLI tests, CodeQL and Actionlint have workflow/ref concurrency groups, cancelling superseded non-main work while preserving main runs. The dataset binds all six inspected workflow files to the immutable source and content hashes.

| Complete UTC calendar window        | All runs | Validate | Publisher | Explainer | Auto-bump | External sync |
| ----------------------------------- | -------: | -------: | --------: | --------: | --------: | ------------: |
| September 26–October 2, pre-fix     |      767 |       69 |        72 |        72 |        21 |             1 |
| October 4–10, first post-fix week   |    1,318 |      124 |       120 |       120 |        29 |             1 |
| October 15–21, latest complete week |      354 |       31 |        26 |        26 |        10 |             1 |

The first post-fix week **increased**, and the latest week decreased. These are observations under different source workloads, not a controlled estimate of mitigation effects. All totals reconcile with daily queries. Run-level attribution is complete for the latest 354-run week; the earlier collected samples cover only 500 of 1,318 first-post-week records and 100 of 767 pre-week records. Their partial attribution is not presented as full-window attribution.

All 26 latest-week publisher run IDs were inspected for jobs. Twenty-two cancelled records returned no jobs; two records had all five jobs skipped; two successful records each allocated guard, preflight and detection jobs and skipped publication/evidence. Across these responses: 20 job records, six assigned runners and 14 skipped jobs. The six assigned-job elapsed intervals sum to 82 seconds. Run counts, returned job counts, elapsed intervals and billed usage are different measures; no billing or savings claim follows from these figures.

## Remaining evidence boundary

This investigation establishes distinct-head workload, completion fan-out, an avoidable publisher runner, existing auto-bump idempotency, and the merged concurrency/job-filter mitigation. It preserves the unknown original query timestamps and 17-run discrepancy rather than fabricating an exact reproduction. Complete the October 4–November 2 comparison on or after November 3 UTC, using daily subdivision and separate job-allocation evidence. Any final disposition must acknowledge the original acceptance criteria and the unresolved snapshot limitation; this report does not close them.
