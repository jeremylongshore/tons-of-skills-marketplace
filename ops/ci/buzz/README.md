# Trusted CI workers on Buzz

Two repository-scoped workers, `buzz-ccpi-tasks` and `buzz-ccpi-stats`, use separate
labels so the daily npm crawl cannot queue the Python acceptance lane. Public PRs
continue on GitHub-hosted runners. The tasks worker admits protected-main Python
CI; the stats worker admits the main-branch daily stats workflow.

Each has a separate unprivileged identity (`ci-ccpi-tasks` or `ci-ccpi-stats`),
without sudo, Docker membership, deployment keys or a login shell. The task runner
cannot read the stats runner's process environment or credentials. Their root-owned
pre-step guard rejects PR events, other repositories,
non-main refs and workflows outside its explicit allowlist. Runner binaries,
credentials and guard configuration are read-only inside each service; only that
worker's work and diagnostics directories are writable. Tool/download caches live
inside its work directory. Separate mount namespaces hide other home directories.

`ci-ccpi.slice` caps the workers together at two CPUs and 3 GiB, beneath the estate's
existing `ci.slice` cap of four CPUs and 6 GiB. No estate cap is raised. The existing
`vps-deploy` runner and its guard are preserved. Fork code must never be assigned
these workers, even if a contributor copies a label into a workflow.

Host prerequisites are Git, curl, jq, tar and the `sqlite3` CLI. Install them before
registration; the worker has no package-manager privileges. The smoke workflow
checks SQLite alongside Node and Python, and the Freshie gate refuses to skip when
a required tool is missing.

Installation uses the established runner distribution already on Buzz. Copy this
directory to the host, review it, and run `sudo bash install.sh`. Register each
instance by piping a short-lived repository registration token to
`sudo bash register-instance.sh tasks` or `stats`; never put tokens in arguments,
logs or tracked files. Registration locks credentials root-owned and group-readable
only to the worker account. The services invoke Runner.Listener directly so the
read-only distribution does not need to rewrite a helper script on startup.

Run `python3 -m unittest tests.ci.test_buzz_ci_guard -v` before installation. Verify
online state using `gh api repos/jeremylongshore/tons-of-skills-marketplace/actions/runners`,
service cgroups and the relay's health afterward. `ci-buzz-smoke.yml` exercises the
actual main-branch execution boundary after merge, without publishing anything.

Rollback: return workflow runner selectors to `ubuntu-latest` through a reviewed
commit, then stop the two `gh-runner-ccpi@` services. Preserve the deployment runner,
its registration, and the estate resource caps. Runner binary updates remain a
reviewed host operation because automatic self-updates are disabled.
