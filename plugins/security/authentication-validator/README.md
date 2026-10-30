# Authentication Validator

Review supplied authentication declarations, inspect local JWTs, verify an
explicit JWT trust profile, and test local password-policy rules. These tools do
not log in to services, scan applications automatically or certify deployments.

## Installation and use

```text
/plugin install authentication-validator@claude-code-plugins-plus
/validate-auth
```

The command shortcut is `/auth`. Select the project and private input files
explicitly. The skill resource directory is not the project under review.

## Existing CLI routes

| Script                   | Selected scope                                                                        | Exit statuses                                                            |
| ------------------------ | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| authentication_check.py  | Supplied JSON declarations for JWT, HTTPS web OAuth, session or API-key configuration | 0 no automated flags; 1 findings/review; 2 incomplete/usage              |
| jwt_analyzer.py          | Compact local JWT inspection or explicit local verification profile                   | 0 verified; 1 invalid for selected checks; 2 unverified/incomplete/usage |
| password_policy_check.py | Declared policy and candidate matching against local rules/exact supplied blocklist   | 0 no automated flags; 1 findings/review; 2 incomplete/usage              |

Configuration success does not establish runtime enforcement. Missing optional
control sections are listed as unassessed. Fields are typed; unknown fields,
unsupported scope and ambiguous JSON fail rather than silently pass.

JWT inspection without a trusted key, explicitly selected algorithm, expected
issuer and audience is unverified and returns 2 for otherwise well-formed inputs; malformed inputs may return 1. Verification supports the twelve
existing HS/RS/PS/ES routes through maintained PyJWT, requires expiration, checks
provided temporal claims and uses no clock leeway. It does not fetch keys, follow
header key URLs, check revocation or establish issuer/key ownership. Reports omit
raw claims, signatures and key material. Prefer private token/key files over
inline arguments and shell history.

The declared policy review uses current, limited NIST password and OWASP KDF
review profiles. It does not require arbitrary periodic rotation or mandatory
composition. Explicit candidate rules are still evaluated, and policy review
flags remain nonzero. `rejected_patterns` retains its legacy name but means exact
blocked values, not regex or substring matching. No online password lookup occurs;
history cannot be verified from one candidate. The old heuristic strength score
is no longer presented as a security measurement.

## Prerequisites and reports

Python 3.11+ is the supported full verification environment. Configuration review
and inspection use the standard library; signature verification additionally
requires the pinned optional dependencies in
[requirements.txt](skills/validating-authentication-implementations/scripts/requirements.txt).
Installation is a separate operator action; the scripts never install anything.

```bash
# After separately approving installation into the selected environment:
python3 -m pip install -r "${CLAUDE_SKILL_DIR}/scripts/requirements.txt"
```

JSON goes to stdout as one document, or to an explicit atomic 0600 output file.
Symlink destinations and aliases of selected input files are rejected. Preserve process status and report scope.
There is no general secret-redaction service or OS sandbox; protect the private
inputs and environment. Local inputs are bounded; error excerpts are omitted.

See the [skill workflow](skills/validating-authentication-implementations/SKILL.md),
[CLI/input contracts](skills/validating-authentication-implementations/scripts/README.md)
and [primary references](skills/validating-authentication-implementations/references/README.md).
The fixture suite in `tests/test_authentication_validator.py` invokes actual CLIs
with synthetic data and local fixture keys; it does not establish production,
DoD/STIG/FIPS, legal or application compliance.

## License

MIT. See [LICENSE](LICENSE).
