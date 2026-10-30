---
name: validating-authentication-implementations
description: Review authentication declarations and verify explicit local JWT trust profiles.
  Use when reviewing login systems or auth flows. Trigger with 'validate authentication',
  'check auth security', or 'review login'.
version: 1.28.0
allowed-tools: Read, Grep, Glob, Bash(security:*), Bash(scan:*), Bash(audit:*)
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - security
  - authentication
  - compliance
compatibility: Designed for Claude Code
---

# Validating Authentication Implementations

## Overview

Review authentication source/configuration and use the bundled local CLIs for
explicit declarations, JWT verification profiles and password-policy checks.
Keep input evidence, cryptographic verification and deployed enforcement separate.

## Prerequisites

- Identify the user's target project. `${CLAUDE_SKILL_DIR}` locates this skill's
  resources; it does not select the target codebase.
- Use Python 3.11+ for the supported verification environment. Local declaration
  review and token inspection use the standard library. Verification requires
  supported PyJWT and the pinned optional backend prerequisites listed in
  [scripts/requirements.txt](scripts/requirements.txt).
- Keep tokens, keys, candidates and configuration in private files. Confirm the
  intended local inputs and output destination. Script execution uses the
  operator's normal permission boundaries; scoped grants do not preapprove
  arbitrary shell commands or installing dependencies.
- Do not make live login, IdP, token refresh/revocation or breach-service calls.
  These helpers do not fetch JWKS, install tools, modify the audited project or
  provide an OS sandbox.

## Instructions

1. Use Glob to locate relevant project files, Read to inspect them and Grep to
   find authentication call sites without printing credential values. Record
   which flows and controls were actually reviewed; absence of a matching string
   does not prove absence of a control.
2. For configuration review, supply explicit JSON to `authentication_check.py`.
   It checks declared JWT, HTTPS web OAuth, session and API-key settings. Unknown
   methods/fields and malformed types are incomplete. Missing optional password,
   MFA or lockout sections are unassessed; configuration success never proves
   implementation, deployment or server-side enforcement.
3. For a local JWT, prefer `--file`. Default inspection reveals controlled
   metadata and supplied temporal problems, omits raw payload/signature data and
   returns unverified/nonzero. Decoding a claim is never authentication.
4. To verify a JWT, independently select a trusted local key file, one allowed
   algorithm, expected issuer and expected audience. Supply all four explicitly.
   The tool supports the existing twelve HS/RS/PS/ES routes through maintained
   PyJWT, requires expiration, checks provided temporal claims and rejects
   unsupported critical semantics. It never derives trust from received `alg`,
   `kid`, key URLs or embedded keys. Algorithm labels and key length do not prove
   key entropy, ownership or suitable trust for a real service.
5. Inspect the verification status and exit code. Missing/old backends, missing
   trust or unavailable input remain incomplete/unverified. Invalid signatures
   and rejected claims fail. Verification is local to the selected profile; it
   does not check revocation, replay state or a live authorization decision.
6. For password review, provide a typed local policy. The limited guidance
   profile distinguishes single-factor from declared MFA context, does not
   require arbitrary rotation/composition and checks supported declared KDF
   parameters. It cannot establish runtime hashing, rate limiting, salt quality,
   MFA assurance or full NIST compliance.
7. For candidate checks, prefer `--password-file` or `--password-stdin`; input is
   exact UTF-8 and whitespace is not stripped. Explicit local composition rules
   remain enforceable even when they generate a policy review flag. The legacy
   `rejected_patterns` field means exact blocked values, never regex or substring
   matching. Supplied blocklist coverage is limited to those values. History
   requirements cannot be checked from one candidate and stay incomplete.
8. Combine manual findings and tool reports without inventing a global score or
   compliance pass. Cite actual file/line and framework edition for any manual
   control mapping. Keep supplied declarations, verified observations and
   unassessed controls distinct. Propose remediation for review; do not apply it
   or change credentials automatically.

## Output

Retain one JSON report plus process exit status, selected input scope and tool
versions. Explicit `--output` uses atomic private replacement and refuses a
symlink destination or alias of a selected input file. Reports omit raw JWT payloads, signature values, keys and
password candidates; arbitrary error excerpts are suppressed. Protect inputs,
filenames and environment separately rather than assuming general redaction.

| Route               | 0                                              | 1                             | 2                                                       |
| ------------------- | ---------------------------------------------- | ----------------------------- | ------------------------------------------------------- |
| JWT                 | Verified under explicit local profile          | Invalid under selected checks | Unverified/incomplete/usage                             |
| Declarations/policy | No automated flags in supplied scope           | Findings/review               | Incomplete/usage                                        |
| Candidate           | Supplied local rules pass without policy flags | Rule failure/policy review    | Unassessed requested history/blocklist or input failure |

The `valid` JWT field is never true for decode-only inspection. Configuration
`runtime_verified` remains false. A candidate `password_valid` value addresses
local matching, not authentication; incomplete reports cannot pass the gate.
The candidate `score` is null because no strength/entropy estimate is computed.
No DoD/STIG/FIPS, ASVS, NIST or legal certification follows from these results.

## Error Handling

- Missing trust/backend: keep verification unverified/incomplete and nonzero.
  Do not infer issuer/audience from the received token or auto-install a library.
- Malformed JSON, duplicate fields, wrong types, non-finite numbers or unsupported
  declarations: stop the selected check and report incomplete/invalid scope;
  never use truthy strings as booleans.
- Unsupported framework/flow: use a separately scoped manual review and primary
  references. Native OAuth redirects, alternate client-authentication methods
  and arbitrary application/framework formats are not implemented by these CLIs.
- Missing runtime evidence: record it as unassessed. Do not claim OAuth state,
  PKCE, MFA, cookie or password-storage enforcement from a configuration flag.
- Private output failure: return nonzero and preserve existing symlink targets;
  do not fall back to publishing sensitive inputs or report bodies elsewhere.

## Examples

From the selected project directory, locate scripts via the resource directory:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/authentication_check.py" --config /private/auth.json --output /private/auth-report.json
python3 "${CLAUDE_SKILL_DIR}/scripts/jwt_analyzer.py" --file /private/token.jwt --output /private/inspection.json
python3 "${CLAUDE_SKILL_DIR}/scripts/jwt_analyzer.py" --file /private/token.jwt --key /private/issuer-public.pem --algorithm RS256 --issuer https://issuer.example.invalid --audience example-app --output /private/verification.json
python3 "${CLAUDE_SKILL_DIR}/scripts/password_policy_check.py" --policy /private/policy.json --password-file /private/candidate.txt --output /private/policy-result.json
```

The inspection example returns 2 without a verification profile. Example paths
and trust strings are placeholders to replace deliberately, not discovered keys
or evidence that an issuer is trusted. Dependency installation, if needed,
requires a separate approved action in the selected environment.

## Resources

- [CLI contracts and example declarations](scripts/README.md)
- [Primary references and supported review profiles](references/README.md)
- [Report-use guidance](assets/README.md)
