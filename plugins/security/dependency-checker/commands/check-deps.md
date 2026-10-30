---
name: check-deps
description: Audit dependency reports and review declared license metadata
shortcut: depc
---

# Dependency Checker

Follow [analyzing-dependencies](../skills/analyzing-dependencies/SKILL.md).
Select the user's project root, not the skill resource directory. Read the
manifests and report supported, unsupported and missing coverage explicitly.

Use an existing report when sufficient. Before live auditing, confirm permission
to send package metadata to configured advisory services. Use the bundled
scanner for npm, pinned Python requirements, Composer, Bundler or Cargo. Preserve
its complete/status/errors fields and exit code: 0 no known findings in complete
selected scope, 1 findings/review, 2 incomplete. A display severity filter must
not change the gate result.

Do not install tools, resolve dependencies, create locks, apply fixes or silently
skip private packages. Do not invent vulnerability IDs, patch versions or safe
upgrade claims. Propose remediation only with actual advisory evidence and keep
execution separate from this audit.

For license metadata, use the installed npm tree or explicitly selected Python
environment. Preserve compound/unknown declarations for review; do not certify
compatibility from category labels. Include coverage, unknowns, review items and
partial findings in the final report. Outdated-version and Go auditing require
separate tooling and evidence.
