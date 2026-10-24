# Upstream and IS authoring contracts

The IS marketplace deliberately adds requirements to upstream specifications.
It does not promise that upstream-minimum output passes the marketplace gate.
See [authoring authority](source-of-truth.md) and the target schema changelog.

## Skills

The portable Agent Skills minimum contains `name` and `description`. Marketplace
output additionally needs top-level `allowed-tools`, `version`, `author`,
`license`, `compatibility` and `tags`. Missing any of the eight is a marketplace
error. Those fields are not downgraded to warnings because upstream permits a
smaller file. Nested metadata does not replace them.

Upstream runtime fields and IS tracking metadata serve different purposes.
Choose optional controls for the requested workflow and retain the current
validator's type, body, disclosure and permission findings.

## Agents

Anthropic's minimum and examples do not include the whole IS enterprise overlay.
Use the eleven-field plugin template; standalone agents additionally require
`hooks`, `mcpServers` and `permissionMode`. Agents use camelCase `disallowedTools`;
skills use kebab-case `disallowed-tools`. Agent validation is strict at every tier.

## Compatibility and migration

`compatibility` is supported free-text metadata. Deprecated `compatible-with`
should be migrated through the canonical tool when in scope. `when_to_use` is
recognized activation context, not a deprecated field. Inspect current schema
findings instead of carrying old copied field tables forward indefinitely.

## Evidence

A runtime-compatible file, a marketplace schema pass, a rubric grade, a package
check and an executed model evaluation are separate results. Record the actual
artifact and source versions. Kernel shadow reports do not waive the current
Python gate before its approved cutover. No authoring update changes that policy.
