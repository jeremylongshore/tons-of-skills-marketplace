---
title: "grep Exit Code 2 in CI: Only Exit 1 Means No Match"
description: "grep exit code 2 means it could not search; exit 1 means no match. Treat only 1 as clean in CI scans, since || true passes unreadable paths as clean."
date: "2026-10-22"
tags: ["ci-cd", "bash", "github-actions", "testing", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/grep-exit-code-2-ci-scan-reports-clean/"
---
A CI scan can read nothing and still print a green result. This post shows how grep causes that, and how to make the step fail instead. At the end you will know which grep exit code means clean, and how to prove a scan fails when it cannot search.

## The guard that hides the error

A dangerous-pattern scan in the CI of tons-of-skills-marketplace, a public Claude Code plugin catalog, ended its grep pipeline with `|| true`. That suppressed every nonzero status, not only the one that means no match.

grep has three exit codes that matter here:

- 0: at least one line matched.
- 1: nothing matched. This is the only clean result.
- 2: grep could not search. A missing path, an unreadable file or a bad pattern all return 2.

A local check on GNU grep 3.11 showed the difference:

- Searching a path that does not exist printed "No such file or directory" and exited 2.
- Searching a real directory with no matches exited 1.
- `R=$(grep -r -E rm nope 2>/dev/null | grep -v /var/ || true)` exited 0 with `R` empty.

The third line is the failure. The search error is hidden twice. `2>/dev/null` drops the message, and the pipeline's status comes from the last filter, which returns 1 on empty input. `|| true` then turns that 1 into 0. The step reports nothing found.

An [earlier post](https://startaitools.com/posts/bash-2-devnull-pipefail-first-deploy/) recommended `|| true` for a read that is expected to fail. That advice still holds for expected failures. A scan that must have read its input has no expected failure, so there the guard hides the one result that matters.

Adding `set -o pipefail` is not enough on its own. Pipefail reports the rightmost nonzero status in a pipeline. When the search fails and the filter then finds no lines, the filter's 1 is the status that wins. In the same check, `PIPESTATUS` was `2 1` and the exit status was 1. An `if` reads that 1 as no match.

The fix needs one more step. Each stage has to turn its own 1 into success, so pipefail can surface a 2 from any earlier stage.

## The wrapper

```bash
set -e -o pipefail
grep_allow_no_match() {
  local grep_status
  if grep "$@"; then
    return 0
  else
    grep_status=$?
  fi
  if [ "$grep_status" -eq 1 ]; then
    return 0
  fi
  return "$grep_status"
}
DANGEROUS_RM=$(grep_allow_no_match -r -E "rm\s+-rf\s+/(\s|$|\*)" plugins/ | grep_allow_no_match -v "/var/" | grep_allow_no_match -v "/tmp/" | grep_allow_no_match -v "/prometheus/")
```

With a missing path, the search stage returns 2 and the filter, reading nothing, returns 1. The wrapper maps that 1 to 0. Pipefail then reports the 2, the assignment fails, `set -e` stops the step, and the clean line never prints.

With no matches, every stage ends at 0 and the step continues, as intended.

Test discovery had the same shape: a `find` piped through two `grep -v` filters and ending in `|| true`. The same wrapper replaces that `|| true`. A `find` that prints partial matches and then fails now stops the step before pytest runs.

## Inside an if, check the status instead

The wrapper only works where `set -e` can fire, such as the assignment above. Bash suspends `set -e` inside an `if` condition, and the wrapper would also flip the branch, because a no match now returns 0. The warning scans keep their `if grep` and check the status in the else branch:

```bash
if grep -r -E "base64\s+-d" plugins/ 2>/dev/null; then
  echo "WARNING: base64 decoding detected"
else
  fail_on_grep_error "$?"
fi
```

`fail_on_grep_error` exits with any status above 1. When the condition is a pipeline, the fix passes `"${PIPESTATUS[@]}"` instead of `$?`, because `$?` there is the filter's 1. The plugin test loop's `if ! grep -q` checks got a helper that returns 1 when nothing matches and exits on anything higher. An unreadable package file now fails the step instead of passing as a plugin without tests.

## The test that proves the failure

The repo's test file, `tests/test_ci_scan_failures.py`, runs the real step, not a copy. It loads the workflow YAML, takes the step's `run:` script, and runs it under `bash -e`. Each test writes a small input tree. The error cases get their failure from a missing directory or from fake `grep` or `find` commands placed first on `PATH`.

Two cases matter most:

- The dangerous-pattern scan runs against a tree with no `plugins/` directory. The step must exit 2 and must not print "No dangerous patterns detected".
- `find` prints real matches and then fails. The step must fail, and pytest must never run.

The same file checks three controls. A real `rm -rf /` still fails the step. Paths under `/var/` still pass. No match still skips pytest.

At the first fix, the fixed steps passed all 11 extracted-workflow cases. The unchanged steps failed four of them, all operational-error cases. The file grew to 20 tests as the later scan fixes landed.

## What is still open

The repo keeps a registry, `scripts/ci-correctness-swallows.json`, of every place the three required workflows deliberately swallow a failure. It lists 24 such sites. After the first scan fix it still marked 16 as unresolved. A fix to the agent dependency install step brought that to 15. Reclassifying one already-guarded site as authorized brought it to 14. The plugin test loop site is still marked unresolved: its grep errors now fail the step, but the registry leaves its discovery policy open. This is a partial correction, and the registry covers only those three workflows.

The pipeline wrapper is in [pull request #1714](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1714). The else-branch checks are in [#1725](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1725) and the plugin test loop helper is in [#1724](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1724).

## Also shipped

- The agent dependency install step no longer ends in success after an install failure (#1717).

## Use this

- Run each CI scan once against a path that does not exist. If the step still prints its clean message, it treats status 2 as clean.
- Replace `|| true` on grep pipelines with a wrapper that turns only status 1 into success, under `set -e -o pipefail`. For `if grep`, check `$?` (or `PIPESTATUS`) in the else branch and fail on anything above 1.
- Add one test that runs the real step from the workflow file against a tree where grep must fail, and asserts a nonzero exit with no clean message.

## Related Posts

- [2>/dev/null hides stderr but not the exit code under pipefail](https://startaitools.com/posts/bash-2-devnull-pipefail-first-deploy/)
- [Five fail-open bugs where nothing to check counted as checked and clean](https://startaitools.com/posts/empty-is-not-clean/)
- [Safety gates fail open or closed, and a swallowed error decides which](https://startaitools.com/posts/every-safety-gate-has-a-failure-direction/)
