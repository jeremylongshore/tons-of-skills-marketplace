<!-- doc-class: record -->

# PR Pre-screen System — Operator Runbook

Status: production, advisory (never a required check).
Owner: Jeremy Longshore.
Replaces: `.github/workflows/gemini-code-review.yml` (deleted in Phase 3).

## What it does

For every external PR opened against `main`, the `PR Pre-screen` workflow
runs the deterministic `validate-skills-schema.py --marketplace --json`
scanner, classifies the result via `scripts/pr-prescreen/classify.py`,
optionally asks MiniMax for a 5-line human summary via
`scripts/pr-prescreen/summarize.py`, and emits one of three verdicts:

| Verdict             | What it means                                                                                | PR action              | Slack action                         |
| ------------------- | -------------------------------------------------------------------------------------------- | ---------------------- | ------------------------------------ |
| `PASS`              | zero errors, every changed skill graded C or better                                          | comment on PR          | ping `#operation-hired`              |
| `CHANGES_REQUESTED` | validator errors OR any skill graded D/F                                                     | request-changes review | silent — contributor is the audience |
| `HARD_BLOCK`        | structural concern (fatal frontmatter, missing catalog entry, no implementation files, etc.) | request-changes review | ping `#operation-hired`              |

The workflow is **advisory**. A failure here NEVER blocks a merge. The
required checks are still `validate` and `marketplace-validation`.

## How it stays fork-safe

The workflow is split into **two jobs** that pass an artifact between
them. This makes the fork-safe design **structural** instead of a
per-review invariant.

> **Update 2026-10-08 (bead `claude-j5gs`).** The July split put `respond` in
> the same `pull_request` workflow, gated on `vars.ENABLE_PR_PRESCREEN`. GitHub
> passes no repository variables or secrets to fork `pull_request` runs, so both
> jobs were skipped on every fork PR (e.g. runs 37250406168, 37534515952, 37689026376) — the pre-screen never reached outside contributors. The
> privileged half now lives in its own `workflow_run` workflow:

```
  pr-prescreen.yml          (pull_request) — checks out main + PR; runs the
                                             validator + classifier; uploads
                                             verdict.json + meta.json. NO
                                             secrets, read-only token, no vars
                                             gate (so fork PRs run too).
       ↓ artifact (attacker-controllable on fork PRs)
  pr-prescreen-respond.yml  (workflow_run) — base token; holds the kill switch.
                                             Checks out MAIN only (default
                                             self-checkout). NO PR checkout.
```

The responder treats the artifact as untrusted input:

- The PR number and head SHA come from GitHub — `workflow_run.head_sha` plus
  the pulls API — never from `meta.json`.
- On `pull_request`, GitHub takes the workflow file from the PR's merge commit,
  so a PR that edits `pr-prescreen.yml` could forge any verdict. Such PRs get a
  neutral `error` status ("Not evaluated") and nothing else. A PR that does not
  touch the file ran byte-identical base workflow code, so its verdict is sound.
- The verdict must be `PASS`, `CHANGES_REQUESTED` or `HARD_BLOCK`; the
  artifact's `head_sha` must equal the trusted head SHA; `diff_count` must be
  numeric; each file is capped at 2 MB.
- `actions/checkout@v7` refuses fork-PR checkouts under `workflow_run` unless
  `allow-unsafe-pr-checkout` is set; the responder never overrides `ref`, so
  the guard never applies and no opt-in exists.
- The Slack ping was removed with the split (Slack is retired).

`tests/ci/test_prescreen_trust_split.py` pins these properties and runs the
responder's artifact check against forged bundles.

The MiniMax prompt (`scripts/pr-prescreen/summarize.py`) explicitly
treats the payload as data, not as instructions. Prompt-injection
resistance is unit-tested in `scripts/pr-prescreen/test_summarize.py`.
The payload itself is the validator's JSON output (paths, grades,
errors) — never any PR-controlled text. The MiniMax call reads
`MINIMAX_API_KEY` from the workflow env and defaults to
`https://api.minimax.io/v1/chat/completions` with model `MiniMax-M3`.
Both can be overridden via `LLM_API_URL` / `LLM_MODEL` if the vendor
changes.

## How to disable in an emergency

```bash
# Flip the repo variable to false. Workflow no-ops on next run.
gh variable set ENABLE_PR_PRESCREEN --body false
```

Workflow stays defined in `.github/workflows/pr-prescreen.yml`; only the
`if:` guard short-circuits. Re-enable by setting the variable back to
`true`.

## How to debug

1. **The workflow didn't run at all.**
   Check `gh variable list` for `ENABLE_PR_PRESCREEN=true`. The whole
   job is gated on that.

2. **The workflow ran but posted no comment.**
   Check the run logs for the `Compute changed plugin paths` step. If
   the PR doesn't touch any `plugins/...` paths, the classifier emits
   `PASS: no plugin paths matched the PR diff.` That's expected, but no
   comment is posted in that case to avoid noise. (Comment-on-empty is
   a future change if needed.)

3. **Comment posted but no MiniMax summary.**
   Look for `LLM status:` in the comment body. Common reasons:
   - `skipped: no api key` → `MINIMAX_API_KEY` secret missing.
   - `failed: http 402` → MiniMax account out of credit or key revoked.
   - `failed: http 429` → MiniMax rate limit hit; will recover
     on next run.
   - `failed: TimeoutError` → 5s deadline exceeded; usually transient.
     The deterministic verdict is always present regardless of MiniMax state.

4. **Slack ping never arrived.**
   `SLACK_OPERATION_HIRED_WEBHOOK_URL` secret must be set. The workflow
   exits 0 silently if it's missing (matches the rest of the Slack
   surfaces in this repo).

5. **The verdict feels wrong.**
   Reproduce locally:
   ```bash
   python3 scripts/validate-skills-schema.py --marketplace --json > /tmp/v.json
   jq '[.[] | select(.path | contains("plugins/<cat>/<plugin>"))]' /tmp/v.json \
     | python3 scripts/pr-prescreen/classify.py -
   ```

## How to query the audit log

Every pre-screen run appends one row to `freshie/inventory.sqlite` table
`pr_prescreen_log`. Example queries:

```bash
# Verdict distribution over the last 30 days
sqlite3 freshie/inventory.sqlite "
  SELECT verdict, COUNT(*) AS n
  FROM pr_prescreen_log
  WHERE created_at > datetime('now', '-30 day')
  GROUP BY verdict ORDER BY n DESC;
"

# Average end-to-end latency by verdict
sqlite3 freshie/inventory.sqlite "
  SELECT verdict, AVG(latency_ms) AS avg_ms, COUNT(*) AS n
  FROM pr_prescreen_log
  GROUP BY verdict;
"

# Optional LLM hit rate (status + counts)
sqlite3 freshie/inventory.sqlite "
  SELECT llm_status, COUNT(*) AS n
  FROM pr_prescreen_log GROUP BY llm_status;
"
```

The audit step is `continue-on-error: true`, so a DB write failure can
never mask the primary signal (the PR comment + Slack ping already
fired before this step runs).

## Operator-provisioned secrets and variables

| Name                                | Type     | Scope | Purpose                                                                                                                                                                        |
| ----------------------------------- | -------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SLACK_OPERATION_HIRED_WEBHOOK_URL` | secret   | repo  | Incoming webhook to `#operation-hired`. Shared with 3 other workflows.                                                                                                         |
| `MINIMAX_API_KEY`                   | secret   | repo  | OpenAI-compatible key from MiniMax (paid annual plan). Optional — workflow falls back to deterministic-only if absent. Used by `summarize.py` for the 5-line reviewer summary. |
| `ENABLE_PR_PRESCREEN`               | variable | repo  | `true` enables the workflow. Set to `false` to disable in an emergency.                                                                                                        |

## Critical files

| File                                     | Role                                                |
| ---------------------------------------- | --------------------------------------------------- |
| `.github/workflows/pr-prescreen.yml`     | The workflow itself.                                |
| `scripts/pr-prescreen/classify.py`       | Pure function: validator JSON → verdict.            |
| `scripts/pr-prescreen/summarize.py`      | Optional MiniMax layer with deterministic fallback. |
| `scripts/pr-prescreen/audit.py`          | Appends one row per run to the audit log.           |
| `scripts/pr-prescreen/test_classify.py`  | Unit tests for the classifier (12 tests).           |
| `scripts/pr-prescreen/test_summarize.py` | Unit tests for the summarizer (9 tests).            |

Run all tests locally:

```bash
python3 scripts/pr-prescreen/test_classify.py
python3 scripts/pr-prescreen/test_summarize.py
```

## Deferred (separate beads, not in scope here)

- Adding a second LLM provider (NVIDIA Nemotron) as a true fallback — only if
  MiniMax becomes a real constraint.
- Retroactive run against the `claude-tcss` PR backlog.
- Cross-repo rollout to other Intent Solutions repos.
- Promoting any pre-screen verdict to auto-merge — explicit non-goal.
  Humans still approve all merges.
