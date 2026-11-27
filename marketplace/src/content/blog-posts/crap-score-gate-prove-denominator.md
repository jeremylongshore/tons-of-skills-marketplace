---
title: "TypeScript CRAP Score Gate: Count Before It Passes"
description: "A CRAP score gate should count what it scored before it reports PASS. A TypeScript monorepo's CI quality gate now fails an empty measurement."
date: "2026-11-26"
tags: ["testing", "ci-cd", "typescript", "monorepo"]
featured: false
canonical: "https://startaitools.com/posts/crap-score-gate-prove-denominator/"
---
If you own a CI quality gate built on coverage or complexity scores, it can report PASS after measuring nothing, and your team will still believe the limit is enforced. By the end you will have four checks that make a score gate fail when its measurement is empty, partial or stale.

CRAP is a per-function risk score that combines cyclomatic complexity (the count of independent paths through a function) with test coverage. In the TypeScript monorepo behind this post, an open-source evaluation harness, the repository sets three limits. A production function fails above 30, a test function above 15, and the project average above 10.

The key idea is the denominator, the full set of files and functions a measurement must cover. A score only means something if the tool proves it looked at all of them.

## The gap

The repository's existing CRAP verification path could report success on an empty measurement. That is a PASS with no count behind it. Its own audit file had listed TypeScript CRAP scoring as incomplete.

Other checks in the same repository had already failed this way. An older test-bias scan read only 10 test declarations, found nothing, and an earlier audit had recorded that as a PASS. An older architecture check had never been configured. Neither one was a real zero-violation result.

## What the scorer measured

A stricter upstream scorer existed, but CI did not run it. In a local run against the 2026-11-10 snapshot, the inventory requested 352 files. The collector observed 344, and eight were type-only files that the scope excluded. The scorer returned a complete FAIL: 29 production functions and nine test functions exceeded the limits, and the project average was 9.14 against 10.

The 2026-11-26 local run inventoried 412 files. The collector observed 404, and eight were type-only. The collector finished in 348.482 seconds under a 600-second deadline.

The scorer returned a complete PASS over 1,667 production functions and 4,513 test functions. The highest production score was 29.211875, just under the limit of 30. The highest test score was 13.005322, and the project average was 1.925488.

The two local snapshots are not a before and after of one fix. Both the code and the inventory changed between them.

The exact-head CI run on the pull request scored 1,667 production functions and 4,519 test functions, with all 12 required checks green. The two runs measured different trees (the CI run covered the final reviewed head), so their test function counts differ by six.

## Four checks

The fix has four parts. Each one closes a specific way the old path could say PASS.

**Count the denominator.** The scope check requires the discovered file count to match the files passed in. Scored files plus type-only exclusions must equal that count. Discovered functions must equal scored functions. A run that scores files but zero functions is refused.

```ts
if (
  scope.discovered_files !== files ||
  Number(scope.scored_files) + Number(excluded) !== files ||
  scope.discovered_functions !== scope.scored_functions ||
  (Number(scope.scored_files) > 0 && Number(scope.scored_functions) === 0)
)
  throw new Error("Strict measurement omitted files or functions");
```

**Refuse disagreement between exit and result.** The scorer exits 0 for pass, 1 for a measured threshold breach, and 2 for an incomplete or invalid measurement. The adapter accepts only a result marked complete with a boolean pass field. It requires exit 0 to match pass true, in both directions. It also refuses any change to the 30, 15 and 10 limits.

**Bind collection and scoring to the same inputs.** Before scoring, the adapter deletes the previous summary and provider output, so a stale file cannot pass as current. It checks the collection receipt (a machine-written record proving a step really ran) for completeness and for a match against the current file inventory and coverage hash.

It also checks the identity of the coverage configuration, collector code, runtime and dependencies. It hashes the three scorer files. After scoring it checks all of it again, and any change during the run throws.

**Pin the scorer.** CI checks out the scorer from an immutable upstream commit, sparse-checked to three files, and runs it unchanged. Collection runs under a 600-second timeout. The workflow uploads the coverage and provider receipts with a rule that fails the job when nothing is found, so a run with no evidence cannot finish green.

## Where the measurement stops

The measurement is a proxy, and the proxy has edges. File-statement coverage stands in for function coverage over the declared package production code and shared Vitest tests. Spawned CLI processes run outside the inspector sessions, so their execution is not in the denominator. Root-tooling production code is outside it too.

The gate proves the declared set was fully scored. It does not prove the declared set covers every file in the repository.

The full change is the merged pull request at https://github.com/jeremylongshore/j-rig-skill-binary-eval/pull/460.

## Use this

- Compare the scorer's discovered and scored file and function counts with your own inventory. Fail the job when they differ, or when the scored function count is zero while files were scored.

- Compare each scorer exit code with its result field. A zero exit with a false pass, or a non-zero exit with a true pass, should fail the job.

- Hash your inputs before and after the scoring run, then upload the raw measurement files with a rule that fails the job when nothing is found.

## Related Posts

- [Earlier CRAP scoring post: join Go coverage by function, not by file](https://startaitools.com/posts/go-cover-func-coverage-join-by-file-crap-score/)

- [A green check with no teeth](https://startaitools.com/posts/passing-is-not-validating/)

- [Five fail-open bugs where empty results read as clean](https://startaitools.com/posts/empty-is-not-clean/)
