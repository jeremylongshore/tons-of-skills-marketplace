# Local CLI and input contracts

Use Python 3.11+ for the tested full verification environment. These scripts do
not install anything or call providers. Optional verification dependencies are
in [requirements.txt](requirements.txt); installation is a separate operator
choice. JSON/keys/candidates are local inputs, not executable configuration.

## Common behavior

Reports are one JSON document on stdout, or an atomic private 0600 `--output`
replacement. Symlink destinations and aliases of selected input files fail. Preserve exit status; the report being
written is not a passing verdict. Unknown fields/methods, duplicate JSON members,
wrong types and non-finite numbers fail. File inputs are bounded to 1 MiB, JWTs
and key files to 256 KiB. This is bounded local I/O, not an OS sandbox. Native
input/error values are omitted from diagnostics; private files and environment
still need protection.

`--verbose` remains accepted for compatibility and does not enable raw-secret
logging. There is no automated `--code`, `--scan`, live URL or account workflow.

## Authentication declarations

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/authentication_check.py" --config auth.json --output auth-report.json
```

Inputs select exactly one `method`: jwt, oauth, session or api_key, with its
matching object. See `auth_schema.py` for the accepted fields and types. Optional
password_policy, mfa and account_lockout declarations are checked if supplied;
missing optional sections are listed as unassessed. No result verifies runtime.

Minimal declared JWT profile, not proof of deployed JWT verification:

```json
{
  "method": "jwt",
  "jwt": {
    "algorithm": "HS256",
    "expiration_seconds": 600,
    "issuer": "https://issuer.example.invalid",
    "audience": "example-app"
  }
}
```

OAuth requires client_type public or confidential. The supported confidential
profile uses a supplied client_secret; other client-authentication methods need
separate review. Public clients do not require a confidential secret. Supply
redirect_uris, scopes, pkce_enabled and pkce_method S256. These are declared
HTTPS web-client checks, not native-app validation or server matching tests.

0 means no automated flags for supplied declarations; 1 findings/review;
2 incomplete/usage. `runtime_verified` is always false.

## JWT inspection and verification

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/jwt_analyzer.py" --file token.jwt
python3 "${CLAUDE_SKILL_DIR}/scripts/jwt_analyzer.py" --file token.jwt --key trusted.pem --algorithm RS256 --issuer https://issuer.example.invalid --audience example-app --output verification.json
```

Exactly one `--file` or legacy `--token` input. Prefer a private file to keep
bearer values out of process arguments/history. Complete verification needs
--key (local file), --algorithm (one explicit supported value), --issuer and
--audience. `--validate` remains accepted and never permits a missing profile to
pass. Otherwise well-formed inspection without all trust/profile inputs returns 2; malformed/invalid inputs may return 1. The valid field is never true without verification.

Supported algorithms: HS256/384/512, RS256/384/512, PS256/384/512, ES256/384/512.
PyJWT >=2.15.1,<3 is required at runtime; use the tested pinned requirements.
HMAC keys must meet the selected hash-size byte minimum; RSA keys must be at least
2048 bits, EC curves must match the selected algorithm. These checks do not
establish entropy or trust. Expiration is required; exp/nbf/iat must be finite
NumericDate values. Issuer/audience expectations are not read from the token.
Clock leeway is zero. Unsupported critical/unencoded-payload semantics fail.

No header-supplied key, JWK/JWKS fetch, revocation check, replay database or issuer
ownership verification. Reports show controlled metadata, not raw payloads,
signatures or kid values. 0 verified for this explicit profile; 1 invalid under
selected checks; 2 unverified/incomplete/usage.

## Password policy and candidates

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/password_policy_check.py" --policy policy.json
python3 "${CLAUDE_SKILL_DIR}/scripts/password_policy_check.py" --policy policy.json --password-file candidate.txt --output candidate-report.json
```

`--config` and `--policy` are exclusive aliases. Candidate sources are exclusive:
legacy --test/--test-password, --password-file, or --password-stdin. File/stdin
contents are exact UTF-8; a trailing newline remains part of the candidate.
The candidate and matched blocklist value are never printed.

Example declared policy for the supported local review (not a deployment claim):

```json
{
  "minimum_length": 15,
  "maximum_length": 128,
  "hashing": { "algorithm": "pbkdf2", "iterations": 600000 },
  "account_lockout": { "enabled": true, "max_attempts": 5 },
  "rejected_patterns": ["fictional-blocked-value"]
}
```

Default authentication_context is single-factor; explicitly declared mfa selects
its separate length profile without proving MFA. Required composition and
periodic-expiration declarations generate review flags rather than being
mandatory defaults. The legacy rejected_patterns list is exact values, never
regex or substring matching. Its adequacy/coverage is not assessed. Requested
history checking is incomplete without historical data; no strength score is
computed (`score` null). Hashing and throttling are declaration review only.

KDF metadata: pbkdf2 defaults to sha256 (600000 iterations); explicit sha512 uses 220000. Argon2id supports p=1 with memory/time profiles 47104/1, 19456/2, 12288/3,
9216/4 or 7168/5 (memory in KiB). Legacy bcrypt reviews cost>=10 and its 72-byte
limit. Other variants/parameters require review, not a compatibility verdict.

0 selected local checks pass without policy flags; 1 failures/review;
2 incomplete/usage. A candidate result is not an authentication decision.
