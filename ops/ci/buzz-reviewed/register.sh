#!/usr/bin/env bash
# Root only; short-lived repository registration token arrives on stdin.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
root=/home/ci-ccpi-reviewed/runner
[[ ! -f $root/.runner ]] || { echo 'Already registered; refusing token replacement' >&2; exit 2; }
IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN
[[ -n $ACTIONS_RUNNER_INPUT_TOKEN ]] || exit 2
export ACTIONS_RUNNER_INPUT_TOKEN
trap 'chown root:root "$root"' EXIT
chown ci-ccpi-reviewed:ci-ccpi-reviewed "$root"
(cd "$root" && runuser -u ci-ccpi-reviewed -w ACTIONS_RUNNER_INPUT_TOKEN -- ./config.sh --unattended --url https://github.com/jeremylongshore/tons-of-skills-marketplace --name buzz-ccpi-reviewed --labels ccpi-reviewed --work _work --disableupdate)
unset ACTIONS_RUNNER_INPUT_TOKEN
chown root:root "$root"
chown -R root:root "$root/bin" "$root/externals"
chown root:root "$root"/*.sh
chown root:ci-ccpi-reviewed "$root/.runner" "$root/.credentials" "$root/.credentials_rsaparams"
chmod 0640 "$root/.runner" "$root/.credentials" "$root/.credentials_rsaparams"
printf 'LANG=C.UTF-8\nACTIONS_RUNNER_HOOK_JOB_STARTED=/usr/local/lib/ccpi-reviewed/job-started.sh\n' > "$root/.env"
chown root:root "$root/.env"
chmod 0644 "$root/.env"
systemctl enable --now gh-runner-ccpi-reviewed.service
