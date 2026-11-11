#!/usr/bin/env bash
# Installs a new, separate worker. Never modifies the trusted-main or deploy workers.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
slot=${1:-1}
case $slot in 1) account=ci-ccpi-reviewed;; 2) account=ci-ccpi-reviewed-2;; *) exit 2;; esac
unit=gh-runner-${account#ci-}.service
if systemctl is-active --quiet "$unit"; then
 echo 'Refusing to reinstall or clear a running worker' >&2; exit 2
fi
src=$(cd -- "$(dirname -- "$0")" && pwd)
root=/home/$account/runner
seed=/home/ci-ccpi/runners/tasks
for tool in git curl jq tar sqlite3 shellcheck gh; do
 command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 2; }
done
cli_help=$(gh api --help)
[[ $cli_help == *--slurp* ]] || { echo 'GitHub CLI must support api --slurp' >&2; exit 2; }
[[ -x $seed/bin/Runner.Listener ]] || exit 2
[[ $(systemctl show ci.slice -p CPUQuotaPerSecUSec --value) == 4s ]] || exit 2
[[ $(systemctl show ci.slice -p MemoryMax --value) == 6442450944 ]] || exit 2
getent passwd "$account" >/dev/null || useradd --system --no-create-home --home-dir "$root/_work/_home" --shell /usr/sbin/nologin "$account"
[[ $(id -u "$account") != 0 ]] || exit 2
if id -nG "$account" | grep -Eq '(^| )(sudo|docker|lxd|root)( |$)'; then exit 2; fi
install -d -o root -g root -m 0755 "/home/$account" "$root" /usr/local/lib/ccpi-reviewed /etc/ccpi-reviewed
if [[ ! -x $root/bin/Runner.Listener ]]; then
 for entry in bin externals config.sh run.sh env.sh; do cp -a --reflink=auto "$seed/$entry" "$root/"; done
fi
install -o root -g root -m 0755 "$src/guard.py" "$src/job-started.sh" "$src/prepare.sh" "$src/register.sh" /usr/local/lib/ccpi-reviewed/
sed -e "s/ci-ccpi-reviewed/$account/g" -e "s@/prepare.sh@/prepare.sh $slot@" \
 "$src/gh-runner-ccpi-reviewed.service" > "/etc/systemd/system/$unit"
chmod 0644 "/etc/systemd/system/$unit"
if [[ ! -f /etc/ccpi-reviewed/admission.json ]]; then
 printf '%s\n' '{"schema":1,"repository":"jeremylongshore/tons-of-skills-marketplace","approved":[]}' > /etc/ccpi-reviewed/admission.json
 chmod 0644 /etc/ccpi-reviewed/admission.json
fi
install -d -o "$account" -g "$account" -m 0700 "$root/_diag"
/usr/local/lib/ccpi-reviewed/prepare.sh "$slot"
systemctl daemon-reload
