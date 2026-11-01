#!/usr/bin/env bash
# Root-owned pre-step boundary for this public repository's trusted Buzz workers.
set -euo pipefail
repo=jeremylongshore/tons-of-skills-marketplace
ref=refs/heads/main
refuse() { echo "::error::Buzz CI refused: $*" >&2; exit 1; }
[[ ${GITHUB_REPOSITORY:-} == "$repo" && ${GITHUB_REF:-} == "$ref" ]] || refuse 'wrong repository or ref'
case ${GITHUB_EVENT_NAME:-} in push|workflow_dispatch|schedule) ;; *) refuse 'untrusted event' ;; esac
case ${GITHUB_WORKFLOW_REF:-} in
 "$repo/.github/workflows/validate-plugins.yml@$ref"|"$repo/.github/workflows/update-npm-stats.yml@$ref"|"$repo/.github/workflows/check-links.yml@$ref"|"$repo/.github/workflows/ci-buzz-smoke.yml@$ref") ;;
 *) refuse 'workflow is not admitted' ;;
esac
payload=${GITHUB_EVENT_PATH:-}
[[ -r $payload ]] || refuse 'missing event payload'
[[ $(jq -er '.repository.full_name' "$payload") == "$repo" ]] || refuse 'payload repository mismatch'
if [[ $GITHUB_EVENT_NAME == push ]]; then
 [[ $(jq -er '.ref' "$payload") == "$ref" ]] || refuse 'payload ref mismatch'
fi
echo "Buzz CI admitted $GITHUB_EVENT_NAME on protected main"
