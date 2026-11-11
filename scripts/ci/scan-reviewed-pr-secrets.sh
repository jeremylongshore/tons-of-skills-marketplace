#!/usr/bin/env bash
# Same PR range and detector outcome classes as the Docker action; no host socket.
set -euo pipefail
[[ ${PR_BASE_SHA:-} =~ ^[0-9a-f]{40}$ && ${PR_HEAD_SHA:-} =~ ^[0-9a-f]{40}$ ]] || exit 2
[[ $PR_BASE_SHA != "$PR_HEAD_SHA" ]] || exit 2
version=3.95.9
checksum=f6d1106b85107d79527ed7a5b98b592beadd8b770dc3c9e8c1ad99e1b2cf127e
scratch=$(mktemp -d "${RUNNER_TEMP:?}/trufflehog.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
curl --fail --silent --show-error --location --proto '=https' --tlsv1.2 \
 "https://github.com/trufflesecurity/trufflehog/releases/download/v${version}/trufflehog_${version}_linux_amd64.tar.gz" \
 --output "$scratch/release.tgz"
printf '%s  %s\n' "$checksum" "$scratch/release.tgz" | sha256sum --check --status
tar -xzf "$scratch/release.tgz" -C "$scratch" trufflehog
"$scratch/trufflehog" git "file://$PWD/" --since-commit "$PR_BASE_SHA" --branch "$PR_HEAD_SHA" \
 --fail --no-update --github-actions --results=verified,unknown
