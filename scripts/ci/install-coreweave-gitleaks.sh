#!/usr/bin/env bash
# Dependency setup only: pin and verify the scanner before unpacking it.
set -euo pipefail
install_dir="${1:?destination required}"
version=8.24.3
archive="gitleaks_${version}_linux_x64.tar.gz"
expected=9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || { echo 'Unsupported scanner platform' >&2; exit 1; }
mkdir -p "$install_dir"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
curl --fail --location --silent --show-error --retry 2 \
  "https://github.com/gitleaks/gitleaks/releases/download/v${version}/${archive}" -o "$scratch/$archive"
(cd "$scratch" && printf '%s  %s\n' "$expected" "$archive" | sha256sum --check --status)
tar -xzf "$scratch/$archive" -C "$scratch" gitleaks
install -m 0755 "$scratch/gitleaks" "$install_dir/gitleaks"
