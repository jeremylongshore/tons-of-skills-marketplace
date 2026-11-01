#!/usr/bin/env bash
# Root only. One short-lived GitHub registration token on stdin; never argv/logs.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
instance=${1:?tasks or stats}
case $instance in tasks|stats) ;; *) exit 2;; esac
dir=/home/ci-ccpi/runners/$instance
if [[ ! -f $dir/.runner ]]; then
 IFS= read -r ACTIONS_RUNNER_INPUT_TOKEN
 [[ -n $ACTIONS_RUNNER_INPUT_TOKEN ]] || exit 2
 export ACTIONS_RUNNER_INPUT_TOKEN
 (cd "$dir" && runuser -u "ci-ccpi-$instance" -w ACTIONS_RUNNER_INPUT_TOKEN -- ./config.sh --unattended --url https://github.com/jeremylongshore/tons-of-skills-marketplace --name "buzz-ccpi-$instance" --labels "ccpi-$instance" --work _work --disableupdate)
 unset ACTIONS_RUNNER_INPUT_TOKEN
fi
# The unit makes this immutable to the job, including its authentication and hook config.
chown -R root:root "$dir/bin" "$dir/externals"
chown root:root "$dir"/*.sh "$dir"/*.template
chown "root:ci-ccpi-$instance" "$dir/.runner" "$dir/.credentials" "$dir/.credentials_rsaparams"
chmod 0640 "$dir/.runner" "$dir/.credentials" "$dir/.credentials_rsaparams"
printf 'LANG=C.UTF-8\nACTIONS_RUNNER_HOOK_JOB_STARTED=/usr/local/lib/ci-ccpi/job-started-guard.sh\nHOME=%s/_work/_home\nRUNNER_TOOL_CACHE=%s/_work/_tool\nAGENT_TOOLSDIRECTORY=%s/_work/_tool\n' "$dir" "$dir" "$dir" > "$dir/.env"
chown root:root "$dir/.env"
chmod 0644 "$dir/.env"
systemctl enable --now "gh-runner-ccpi@$instance.service"
systemctl is-active "gh-runner-ccpi@$instance.service"
