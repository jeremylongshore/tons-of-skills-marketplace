#!/usr/bin/env bash
# Install only the worker filesystem/sandbox; registration tokens arrive separately.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run as root' >&2; exit 1; }
for tool in git curl jq tar sqlite3; do
 command -v "$tool" >/dev/null || { echo "Missing host prerequisite: $tool (install before runner registration)" >&2; exit 2; }
done
source_dir=$(cd -- "$(dirname -- "$0")" && pwd)
seed=/home/ci-deploy/runners/tonsofskills
[[ -x $seed/bin/Runner.Listener ]] || { echo 'Missing established runner distribution' >&2; exit 1; }
for instance in tasks stats; do
 account=ci-ccpi-$instance
 getent passwd "$account" >/dev/null || useradd --system --no-create-home --home-dir "/home/ci-ccpi/runners/$instance/_work/_home" --shell /usr/sbin/nologin "$account"
 [[ $(id -u "$account") != 0 ]] || exit 2
 if id -nG "$account" | grep -Eq '(^| )(sudo|docker|lxd|root)( |$)'; then
  echo 'Refusing a privileged worker account' >&2; exit 2
 fi
done
install -d -o root -g root -m 0755 /home/ci-ccpi /home/ci-ccpi/runners
[[ $(systemctl show ci.slice -p CPUQuotaPerSecUSec --value) == 4s ]] || { echo 'Estate CPU cap differs; review before installing' >&2; exit 2; }
[[ $(systemctl show ci.slice -p MemoryMax --value) == 6442450944 ]] || { echo 'Estate memory cap differs; review before installing' >&2; exit 2; }
# No docker, sudo, relay keys or deployment credentials are granted to this account.
install -d -o root -g root -m 0755 /usr/local/lib/ci-ccpi
install -o root -g root -m 0755 "$source_dir/job-started-guard.sh" /usr/local/lib/ci-ccpi/job-started-guard.sh
install -o root -g root -m 0755 "$source_dir/register-instance.sh" /usr/local/lib/ci-ccpi/register-instance.sh
install -o root -g root -m 0644 "$source_dir/gh-runner-ccpi@.service" /etc/systemd/system/
install -o root -g root -m 0644 "$source_dir/ci-ccpi.slice" /etc/systemd/system/
for instance in tasks stats; do
 dir=/home/ci-ccpi/runners/$instance
 install -d -o "ci-ccpi-$instance" -g "ci-ccpi-$instance" -m 0750 "$dir"
 if [[ ! -x $dir/bin/Runner.Listener ]]; then
  for entry in bin externals config.sh run.sh runsvc.sh env.sh safe_sleep.sh run-helper.sh.template run-helper.cmd.template; do
   [[ ! -e $seed/$entry ]] || cp -a --reflink=auto "$seed/$entry" "$dir/"
  done
 fi
 install -d -o "ci-ccpi-$instance" -g "ci-ccpi-$instance" -m 0750 "$dir/_work" "$dir/_diag" "$dir/_work/_home" "$dir/_work/_tool"
 # Registration runs as the account; the final registration helper locks binaries again.
 chown "ci-ccpi-$instance:ci-ccpi-$instance" "$dir"
 chown -R "ci-ccpi-$instance:ci-ccpi-$instance" "$dir/_work" "$dir/_diag"
done
systemctl daemon-reload
