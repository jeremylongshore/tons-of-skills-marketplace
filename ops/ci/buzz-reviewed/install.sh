#!/usr/bin/env bash
# Installs a new, separate worker. Never modifies the trusted-main or deploy workers.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
if systemctl is-active --quiet gh-runner-ccpi-reviewed.service; then
 echo 'Refusing to reinstall or clear a running worker' >&2; exit 2
fi
src=$(cd -- "$(dirname -- "$0")" && pwd)
root=/home/ci-ccpi-reviewed/runner
seed=/home/ci-ccpi/runners/tasks
for tool in git curl jq tar sqlite3 shellcheck gh; do
 command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 2; }
done
[[ -x $seed/bin/Runner.Listener ]] || exit 2
[[ $(systemctl show ci.slice -p CPUQuotaPerSecUSec --value) == 4s ]] || exit 2
[[ $(systemctl show ci.slice -p MemoryMax --value) == 6442450944 ]] || exit 2
getent passwd ci-ccpi-reviewed >/dev/null || useradd --system --no-create-home --home-dir "$root/_work/_home" --shell /usr/sbin/nologin ci-ccpi-reviewed
if id -nG ci-ccpi-reviewed | grep -Eq '(^| )(sudo|docker|lxd|root)( |$)'; then exit 2; fi
install -d -o root -g root -m 0755 /home/ci-ccpi-reviewed "$root" /usr/local/lib/ccpi-reviewed /etc/ccpi-reviewed
if [[ ! -x $root/bin/Runner.Listener ]]; then
 for entry in bin externals config.sh run.sh env.sh; do cp -a --reflink=auto "$seed/$entry" "$root/"; done
fi
install -o root -g root -m 0755 "$src/guard.py" "$src/job-started.sh" "$src/prepare.sh" "$src/register.sh" /usr/local/lib/ccpi-reviewed/
install -o root -g root -m 0644 "$src/gh-runner-ccpi-reviewed.service" /etc/systemd/system/
if [[ ! -f /etc/ccpi-reviewed/admission.json ]]; then
 printf '%s\n' '{"schema":1,"repository":"jeremylongshore/tons-of-skills-marketplace","approved":[]}' > /etc/ccpi-reviewed/admission.json
 chmod 0644 /etc/ccpi-reviewed/admission.json
fi
install -d -o ci-ccpi-reviewed -g ci-ccpi-reviewed -m 0700 "$root/_diag"
/usr/local/lib/ccpi-reviewed/prepare.sh
systemctl daemon-reload
