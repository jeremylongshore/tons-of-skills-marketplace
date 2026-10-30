---
name: validate-auth
description: Review declared authentication configuration and explicit local JWT verification profiles
shortcut: auth
---

# Review Authentication

Follow [validating-authentication-implementations](../skills/validating-authentication-implementations/SKILL.md).
Select the user's target project and private input files. Use Read, Grep and Glob
for the manual review; the bundled scripts consume explicit local inputs and do
not discover application controls automatically.

Separate declared configuration, unverified JWT inspection, cryptographic
verification under a selected trust profile, and local candidate-policy checks.
Retain complete/status/scope/error fields and process exit codes. Never treat a
decoded token as authenticated or a configuration declaration as deployed proof.
Do not install prerequisites, change credentials, call an identity provider or
apply remediation automatically. Report unassessed controls and propose
source-backed next actions with their verification requirements.
