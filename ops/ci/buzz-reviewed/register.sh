#!/usr/bin/env bash
# Root only; short-lived repository registration token arrives on stdin.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
slot=${1:-1}
case $slot in 1) account=ci-ccpi-reviewed; runner_name=buzz-ccpi-reviewed;; 2) account=ci-ccpi-reviewed-2; runner_name=buzz-ccpi-reviewed-2;; *) exit 2;; esac
root=/home/$account/runner
[[ ! -f $root/.runner ]] || { echo 'Already registered; refusing token replacement' >&2; exit 2; }
IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN
[[ -n $ACTIONS_RUNNER_INPUT_TOKEN ]] || exit 2
export ACTIONS_RUNNER_INPUT_TOKEN
trap 'chown root:root "$root"' EXIT
chown "$account:$account" "$root"
(cd "$root" && runuser -u "$account" -w ACTIONS_RUNNER_INPUT_TOKEN -- ./config.sh --unattended --url https://github.com/jeremylongshore/tons-of-skills-marketplace --name "$runner_name" --labels ccpi-reviewed --work _work --disableupdate)
unset ACTIONS_RUNNER_INPUT_TOKEN
chown root:root "$root"
chown -R root:root "$root/bin" "$root/externals"
chown root:root "$root"/*.sh
chown "root:$account" "$root/.runner" "$root/.credentials" "$root/.credentials_rsaparams"
chmod 0640 "$root/.runner" "$root/.credentials" "$root/.credentials_rsaparams"
printf 'LANG=C.UTF-8\nACTIONS_RUNNER_HOOK_JOB_STARTED=/usr/local/lib/ccpi-reviewed/job-started.sh\n' > "$root/.env"
chown root:root "$root/.env"
chmod 0644 "$root/.env"
systemctl enable --now "gh-runner-${account#ci-}.service"
