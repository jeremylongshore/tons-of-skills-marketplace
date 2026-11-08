# Reviewed PR worker on Buzz

This is a separate pool of two workers for explicitly reviewed revisions in this public repository.
The existing `tasks`, `stats` and deployment workers keep their protected-main guards.
No fork code is admitted. This is a restricted host account, **not a VM sandbox**;
review of the complete admitted revision remains required.

## Admission and lifecycle

`CCPI_REVIEWED_PR_RUNNER=enabled` routes same-repository PR jobs to `ccpi-reviewed`.
Forks and other events retain their existing runner routing. The root-owned job-start
hook independently requires the repository, PR event/number, base branch, workflow
allowlist, exact head commit and exact synthetic merge commit to match a root-owned
admission record. A PR cannot approve itself by changing workflow labels or policy
files in its checkout. A changed head or base needs a fresh review and admission.

Each worker has its own no-login Unix identity, no sudo or Docker group, and no
host Docker socket. Mount namespaces hide other homes. The service runs one job,
exits, kills its process group and clears its work/home/tool directories before the
next listener starts. Diagnostics stay outside that reset for incident review.
Each root-owned distribution and admission configuration are read-only to jobs.
All CI remains under the existing estate limit of four CPUs and 6 GiB. Each worker
has a two-CPU/three-GiB ceiling within that limit; the pool does not raise estate capacity.

The PR diff secret scan uses the checksum-pinned upstream TruffleHog 3.95.9 binary
with the same base/head range, fail-on-findings behavior, and verified/unknown
result classes. This avoids granting a root-equivalent host Docker socket. The
hosted action remains in place for hosted PR execution. Windows evidence still
requires a Windows worker; no Linux run is represented as native Windows evidence.

## Install and operate

Review the source and run `python3 -m unittest tests.ci.test_reviewed_runner_guard
tests.ci.test_buzz_ci_guard` and shellcheck before installation. Install Git, curl,
jq, tar, SQLite, shellcheck and gh with `api --slurp` support as host prerequisites.
The live setup uses the official GitHub CLI 2.87.3 archive with SHA256
`c6e5537631fca45f277ef405ce8751d139b491e9402cc20891a003525a8773b2`;
the installer refuses the older Ubuntu CLI that lacks this flag. Copy this directory to
Buzz and run `sudo bash install.sh 1` and `sudo bash install.sh 2`. It installs only the new worker and starts
with an empty admission policy. Pipe a short-lived repository registration token
to `sudo /usr/local/lib/ccpi-reviewed/register.sh 1` or
`sudo /usr/local/lib/ccpi-reviewed/register.sh 2`; never log the token or put it in
command arguments. Registration is separate from revision admission.

After reviewing and pushing a complete revision, fetch the PR through GitHub's
API and verify that its head equals that reviewed commit, its head and base repos
are this repository, its base is main, and its synthetic merge commit has exactly
the expected base/head parents. Atomically install a root-owned 0644 JSON record
at `/etc/ccpi-reviewed/admission.json`:

```json
{
  "schema": 1,
  "repository": "jeremylongshore/tons-of-skills-marketplace",
  "approved": [
    { "pr": 123, "head": "<reviewed 40-character SHA>", "merge": "<verified merge SHA>" }
  ]
}
```

The example is illustrative and will be rejected as written. Never populate this
file automatically from arbitrary queued PRs. Revoke a row once merged or when
review is withdrawn. The workspace is disposable; keep authoritative evidence in
CI artifacts and the review issue. Failed admission is a failed job, not a pass.

Verify online state, guard refusals, one-job restarts, cleanup and resource limits
on the actual worker before declaring deployment complete. Retain all required
contexts and test coverage. To roll back routing, remove the repository variable;
then stop the two dedicated services when idle. Preserve other workers and their guards.
