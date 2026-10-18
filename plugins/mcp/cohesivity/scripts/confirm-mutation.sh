#!/usr/bin/env bash
# confirm-mutation.sh — PreToolUse gate for the Cohesivity tools that change state.
#
# create_tenant creates a project, provision_resource adds a service to it and
# claim_tenant starts the claim that makes it permanent. The MCP server is remote
# HTTP, so this host-side hook is the local enforcement point: it returns
# permissionDecision "ask" so the host prompts the user before the call is sent.
# Read-only tools (tenant_status, get_cohesivity_documentation) and give_feedback
# are not matched and run normally.
set -euo pipefail

cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This Cohesivity call creates a project, adds a service to it, or starts a claim. Confirm it matches what you asked for."
  }
}
JSON
