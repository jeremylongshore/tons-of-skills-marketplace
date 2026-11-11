#!/usr/bin/env bash
# Root-only fixed-path reset; systemd has killed the previous job's whole cgroup.
set -euo pipefail
[[ $EUID == 0 ]] || exit 1
slot=${1:-1}
case $slot in 1) account=ci-ccpi-reviewed;; 2) account=ci-ccpi-reviewed-2;; *) exit 2;; esac
root=/home/$account/runner
[[ -d $root && ! -L $root && $(stat -c %u "$root") == 0 ]] || exit 2
[[ ! -L $root/_work ]] || exit 2
# The parent is root-owned; the worker cannot replace _work or any ancestor.
if [[ -d $root/_work && ! -L $root/_work ]]; then
 find "$root/_work" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
fi
install -d -o "$account" -g "$account" -m 0700 "$root/_work"
install -d -o "$account" -g "$account" -m 0700 "$root/_work/_home" "$root/_work/_tool"
