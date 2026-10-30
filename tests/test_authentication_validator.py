"""Exercise bundled authentication CLIs with fictional local inputs only."""

import base64
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "plugins/security/authentication-validator/skills/validating-authentication-implementations/scripts"
)


def encode_part(value):
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")


def fictional_token(expiration):
    return ".".join(
        [
            encode_part({"alg": "RS256", "typ": "JWT"}),
            encode_part(
                {"iss": "https://issuer.invalid", "aud": "fictional-app", "sub": "fictional-person", "exp": expiration}
            ),
            encode_part("fictional-not-a-signature"),
        ]
    )


def invoke(tmp_path, script, *arguments, python_flags=(), fixture_env=None):
    return subprocess.run(
        [sys.executable, *python_flags, str(SCRIPTS / script), *arguments],
        cwd=tmp_path,
        env={"PATH": str(tmp_path), "PYTHONNOUSERSITE": "1", **(fixture_env or {})},
        text=True,
        capture_output=True,
        timeout=10,
    )


@pytest.mark.parametrize("expiration", [4102444800, 1])
def test_unchecked_or_expired_token_cannot_authenticate(tmp_path, expiration):
    token_file = tmp_path / "fictional.jwt"
    token_file.write_text(fictional_token(expiration))
    token_file.chmod(0o600)
    result = invoke(tmp_path, "jwt_analyzer.py", "--file", str(token_file))
    report = json.loads(result.stdout)
    assert report.get("valid") is not True
    assert result.returncode != 0


def test_failed_password_policy_returns_a_failed_gate(tmp_path):
    policy = tmp_path / "policy.json"
    policy.write_text("{}")
    result = invoke(tmp_path, "password_policy_check.py", "--config", str(policy))
    report = json.loads(result.stdout)
    assert report["summary"]["passed"] is False
    assert result.returncode != 0


def test_unrecognized_authentication_scope_does_not_pass(tmp_path):
    config = tmp_path / "auth.json"
    config.write_text('{"method":"fictional-unsupported-method"}')
    result = invoke(tmp_path, "authentication_check.py", "--config", str(config))
    json.loads(result.stdout)
    assert result.returncode != 0


@pytest.fixture
def trust_profile(tmp_path):
    import jwt
    from importlib.metadata import version

    assert version("PyJWT") == "2.15.1", "Install the pinned verification fixture requirements"
    key = b"fictional-local-fixture-key-not-a-credential-" * 3
    key_file = tmp_path / "key.bin"
    key_file.write_bytes(key)
    key_file.chmod(0o600)
    profile = [
        "--key",
        str(key_file),
        "--algorithm",
        "HS256",
        "--issuer",
        "https://issuer.invalid",
        "--audience",
        "fictional-app",
    ]
    return jwt, key, key_file, profile


def signed_raw_fixture(claims, key, headers=None):
    """Mint malformed synthetic bytes without the encoder normalizing them."""
    import hashlib
    import hmac

    message = encode_part(headers or {"alg": "HS256", "typ": "JWT"}) + "." + encode_part(claims)
    signature = hmac.new(key, message.encode(), hashlib.sha256).digest()
    return message + "." + base64.urlsafe_b64encode(signature).decode().rstrip("=")


def signed_claims():
    import time

    return {
        "iss": "https://issuer.invalid",
        "aud": "fictional-app",
        "sub": "fictional-subject",
        "exp": int(time.time()) + 600,
    }


def run_token(tmp_path, token, *arguments):
    path = tmp_path / "input.jwt"
    path.write_text(token)
    path.chmod(0o600)
    return invoke(tmp_path, "jwt_analyzer.py", "--file", str(path), *arguments)


def test_complete_explicit_profile_verifies_without_disclosing_claims(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    claims = {**signed_claims(), "private_secret": "fictional-private-value-never-print"}
    token = jwt.encode(claims, key, algorithm="HS256")
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["valid"] is True and report["complete"] is True
    assert report["signature"]["verified"] is True
    assert report["claims_verified"] is True
    for value in (token, "fictional-private-value-never-print", "fictional-subject", key.decode()):
        assert value not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "failure",
    [
        "expired",
        "future-nbf",
        "future-iat",
        "wrong-audience",
        "wrong-issuer",
        "missing-exp",
        "wrong-key",
        "wrong-algorithm",
    ],
)
def test_signed_token_rejected_by_selected_profile(tmp_path, trust_profile, failure):
    import time

    jwt, key, key_file, profile = trust_profile
    claims = signed_claims()
    if failure == "expired":
        claims["exp"] = 1
    if failure == "future-nbf":
        claims["nbf"] = int(time.time()) + 600
    if failure == "future-iat":
        claims["iat"] = int(time.time()) + 600
    if failure == "wrong-audience":
        claims["aud"] = "different-app"
    if failure == "wrong-issuer":
        claims["iss"] = "https://different.invalid"
    if failure == "missing-exp":
        del claims["exp"]
    token = jwt.encode(claims, key, algorithm="HS512" if failure == "wrong-algorithm" else "HS256")
    if failure == "wrong-key":
        key_file.write_bytes(b"other-fictional-key-" * 5)
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 1, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is False


@pytest.mark.parametrize(
    "field,value", [("exp", True), ("exp", "4102444800"), ("nbf", []), ("iat", None), ("iss", 17), ("aud", [])]
)
def test_malformed_registered_claims_cannot_verify(tmp_path, trust_profile, field, value):
    jwt, key, _, profile = trust_profile
    claims = {**signed_claims(), field: value}
    token = signed_raw_fixture(claims, key)
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 1
    assert json.loads(result.stdout)["valid"] is False


@pytest.mark.parametrize("field", ["crit", "b64"])
def test_unsupported_critical_semantics_are_incomplete(tmp_path, trust_profile, field):
    jwt, key, _, profile = trust_profile
    token = signed_raw_fixture(
        signed_claims(), key, {"alg": "HS256", field: ["fictional"] if field == "crit" else True}
    )
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 2
    assert json.loads(result.stdout)["complete"] is False


@pytest.mark.parametrize(
    "algorithm",
    ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512"],
)
def test_advertised_algorithm_routes_use_maintained_backend(tmp_path, trust_profile, algorithm):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, rsa

    jwt, secret, key_file, _ = trust_profile
    if algorithm.startswith("HS"):
        signing = secret
        public = secret
    else:
        signing = (
            rsa.generate_private_key(public_exponent=65537, key_size=2048)
            if algorithm.startswith(("RS", "PS"))
            else ec.generate_private_key(
                {"ES256": ec.SECP256R1, "ES384": ec.SECP384R1, "ES512": ec.SECP521R1}[algorithm]()
            )
        )
        public = signing.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    key_file.write_bytes(public)
    token = jwt.encode(signed_claims(), signing, algorithm=algorithm)
    result = run_token(
        tmp_path,
        token,
        "--key",
        str(key_file),
        "--algorithm",
        algorithm,
        "--issuer",
        "https://issuer.invalid",
        "--audience",
        "fictional-app",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["signature"]["verified"] is True


def test_missing_profile_field_stays_unverified(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    token = jwt.encode(signed_claims(), key, algorithm="HS256")
    result = run_token(tmp_path, token, *profile[:-2])
    assert result.returncode == 2
    assert json.loads(result.stdout)["valid"] is not True


def test_verification_does_not_use_token_jwks_urls(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    token = jwt.encode(
        signed_claims(),
        key,
        algorithm="HS256",
        headers={"jku": "https://fictional.invalid/keys", "kid": "fictional-credential-do-not-echo"},
    )
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 0
    assert "fictional.invalid/keys" not in result.stdout
    assert "fictional-credential-do-not-echo" not in result.stdout


def test_output_is_private_and_stdout_remains_machine_clean(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    path = tmp_path / "report.json"
    path.write_text("preserve until replacement")
    path.chmod(0o644)
    result = run_token(tmp_path, jwt.encode(signed_claims(), key, algorithm="HS256"), *profile, "--output", str(path))
    assert result.returncode == 0 and result.stdout == ""
    assert json.loads(path.read_text())["valid"] is True
    assert path.stat().st_mode & 0o777 == 0o600


def test_missing_backend_is_incomplete_without_install_attempt(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    path = tmp_path / "input.jwt"
    path.write_text(jwt.encode(signed_claims(), key, algorithm="HS256"))
    result = invoke(tmp_path, "jwt_analyzer.py", "--file", str(path), *profile, python_flags=("-S",))
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["complete"] is False and report["valid"] is not True
    assert "backend unavailable" in result.stdout


def test_old_backend_metadata_does_not_enable_verification(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    metadata = tmp_path / "pyjwt-2.10.1.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: PyJWT\nVersion: 2.10.1\n")
    path = tmp_path / "input.jwt"
    path.write_text(jwt.encode(signed_claims(), key, algorithm="HS256"))
    result = invoke(
        tmp_path, "jwt_analyzer.py", "--file", str(path), *profile, fixture_env={"PYTHONPATH": str(tmp_path)}
    )
    assert result.returncode == 2
    assert "requires supported PyJWT" in result.stdout


def test_public_key_cannot_be_used_as_hmac_secret(tmp_path, trust_profile):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    _, _, key_file, profile = trust_profile
    signing = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = signing.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    key_file.write_bytes(public)
    token = signed_raw_fixture(signed_claims(), public)
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 2
    assert json.loads(result.stdout)["valid"] is not True


def test_short_hmac_trust_key_cannot_verify(tmp_path, trust_profile):
    _, _, key_file, profile = trust_profile
    short_key = b"fictional-short"
    key_file.write_bytes(short_key)
    token = signed_raw_fixture(signed_claims(), short_key)
    result = run_token(tmp_path, token, *profile)
    assert result.returncode == 2
    assert json.loads(result.stdout)["valid"] is not True


def test_utc_verification_is_independent_of_process_timezone(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    path = tmp_path / "input.jwt"
    path.write_text(jwt.encode(signed_claims(), key, algorithm="HS256"))
    result = invoke(tmp_path, "jwt_analyzer.py", "--file", str(path), *profile, fixture_env={"TZ": "Pacific/Honolulu"})
    assert result.returncode == 0


def test_output_symlink_cannot_overwrite_target(tmp_path, trust_profile):
    jwt, key, _, profile = trust_profile
    target = tmp_path / "target"
    target.write_text("preserve")
    output = tmp_path / "report.json"
    output.symlink_to(target)
    result = run_token(tmp_path, jwt.encode(signed_claims(), key, algorithm="HS256"), *profile, "--output", str(output))
    assert result.returncode == 2
    assert target.read_text() == "preserve" and output.is_symlink()


@pytest.mark.parametrize("payload", [b'{"exp":1,"exp":4102444800}', b'{"exp":NaN}', b'{"exp":1e999}', b"[]"])
def test_ambiguous_claim_objects_are_rejected_before_verification(tmp_path, payload):
    token = (
        encode_part({"alg": "HS256"})
        + "."
        + base64.urlsafe_b64encode(payload).decode().rstrip("=")
        + "."
        + encode_part("fictional")
    )
    result = run_token(tmp_path, token)
    assert result.returncode == 1
    assert json.loads(result.stdout)["valid"] is False


def test_non_utf8_jwt_claim_encoding_is_not_accepted(tmp_path):
    payload = json.dumps({"exp": 4102444800}).encode("utf-16")
    token = (
        encode_part({"alg": "HS256"})
        + "."
        + base64.urlsafe_b64encode(payload).decode().rstrip("=")
        + "."
        + encode_part("fictional")
    )
    result = run_token(tmp_path, token)
    assert result.returncode == 1
    assert json.loads(result.stdout)["valid"] is False


def policy_fixture():
    return {
        "minimum_length": 15,
        "maximum_length": 128,
        "hashing": {"algorithm": "pbkdf2", "iterations": 600000},
        "account_lockout": {"enabled": True, "max_attempts": 5, "lockout_duration_minutes": 30},
        "rejected_patterns": ["fictional-blocked"],
    }


def run_policy(tmp_path, policy, *arguments):
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy))
    return invoke(tmp_path, "password_policy_check.py", "--config", str(path), *arguments)


def test_policy_does_not_require_composition_history_or_periodic_rotation(tmp_path):
    result = run_policy(tmp_path, policy_fixture())
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["summary"]["passed"] is True


def test_periodic_rotation_and_mandatory_composition_need_review(tmp_path):
    policy = {
        **policy_fixture(),
        "password_max_age_days": 90,
        "password_history_count": 5,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True,
    }
    result = run_policy(tmp_path, policy)
    assert result.returncode == 1
    assert json.loads(result.stdout)["summary"]["passed"] is False


def test_password_cannot_pass_an_empty_policy(tmp_path):
    result = run_policy(tmp_path, {}, "--test-password", "Fictional violet phrase")
    assert result.returncode == 2
    assert json.loads(result.stdout)["complete"] is False


@pytest.mark.parametrize("value", ["true", 1, None])
def test_boolean_policy_controls_are_not_truthy_coerced(tmp_path, value):
    result = run_policy(tmp_path, {**policy_fixture(), "require_uppercase": value})
    assert result.returncode == 2
    assert json.loads(result.stdout)["complete"] is False


def test_unknown_hashing_declaration_is_not_silently_strong(tmp_path):
    result = run_policy(tmp_path, {**policy_fixture(), "hashing": {"algorithm": "fictional-unknown-kdf"}})
    assert result.returncode != 0


def test_password_exact_blocklist_is_applied_without_echo(tmp_path):
    secret = "fictional-blocked"
    result = run_policy(tmp_path, policy_fixture(), "--test-password", secret)
    assert result.returncode == 1
    assert secret not in result.stdout + result.stderr
    assert json.loads(result.stdout)["password_valid"] is False


def run_auth_config(tmp_path, config, *arguments):
    path = tmp_path / "auth.json"
    path.write_text(json.dumps(config))
    return invoke(tmp_path, "authentication_check.py", "--config", str(path), *arguments)


def jwt_config_fixture(algorithm="HS256"):
    return {
        "method": "jwt",
        "jwt": {
            "algorithm": algorithm,
            "expiration_seconds": 600,
            "issuer": "https://issuer.invalid",
            "audience": "fictional-app",
        },
    }


def test_declared_jwt_config_does_not_claim_runtime_or_unselected_controls(tmp_path):
    result = run_auth_config(tmp_path, jwt_config_fixture())
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["runtime_verified"] is False
    assert set(report["unassessed_controls"]) == {"password_policy", "mfa", "account_lockout"}
    assert "Strong" not in result.stdout


@pytest.mark.parametrize("algorithm", ["none", "fictional-unknown-algorithm"])
def test_unsupported_configured_algorithm_is_not_declared_strong(tmp_path, algorithm):
    result = run_auth_config(tmp_path, jwt_config_fixture(algorithm))
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["summary"]["critical"] >= 1
    assert report["summary"]["passed"] is False


def test_config_reuses_the_same_password_policy_review(tmp_path):
    result = run_auth_config(tmp_path, {**jwt_config_fixture(), "password_policy": policy_fixture()})
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "config",
    [
        [],
        {"method": "jwt"},
        {"method": "jwt", "jwt": {"algorithm": ["HS256"]}},
        {"method": "session", "session": {"cookie": {"secure": "true"}}},
        {"method": "api_key", "api_key": {"minimum_length": True}},
        {"method": "jwt", "jwt": {"expiration_seconds": -1}},
        {"method": "jwt", "jwt": {"unknown_field": True}},
    ],
)
def test_malformed_declared_configuration_is_incomplete(tmp_path, config):
    result = run_auth_config(tmp_path, config)
    assert result.returncode == 2
    assert json.loads(result.stdout)["complete"] is False


def test_exact_blocklist_does_not_reject_a_substring(tmp_path):
    result = run_policy(tmp_path, policy_fixture(), "--test-password", "prefix-fictional-blocked-suffix")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["password_valid"] is True


def test_history_is_unassessed_for_a_single_candidate(tmp_path):
    result = run_policy(
        tmp_path, {**policy_fixture(), "password_history_count": 5}, "--test-password", "Fictional violet ocean phrase"
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["password_valid"] is None


def oauth_config_fixture():
    return {
        "method": "oauth",
        "oauth": {
            "client_type": "public",
            "redirect_uris": ["https://app.invalid/callback"],
            "scopes": ["profile.read"],
            "pkce_enabled": True,
            "pkce_method": "S256",
        },
    }


def test_public_web_client_does_not_require_a_confidential_secret(tmp_path):
    result = run_auth_config(tmp_path, oauth_config_fixture())
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["runtime_verified"] is False


def test_oauth_missing_client_context_is_incomplete(tmp_path):
    config = oauth_config_fixture()
    del config["oauth"]["client_type"]
    result = run_auth_config(tmp_path, config)
    assert result.returncode == 2


@pytest.mark.parametrize(
    "uri",
    [
        "https://*.invalid/callback",
        "https://app.invalid/*",
        "https://app.invalid/callback#fragment",
        "https://fictional-credential@app.invalid/callback",
    ],
)
def test_redirect_declarations_do_not_accept_patterns_or_echo_userinfo(tmp_path, uri):
    config = oauth_config_fixture()
    config["oauth"]["redirect_uris"] = [uri]
    result = run_auth_config(tmp_path, config)
    assert result.returncode == 1
    assert "fictional-credential" not in result.stdout + result.stderr


def test_public_client_requires_declared_s256_pkce(tmp_path):
    config = oauth_config_fixture()
    config["oauth"]["pkce_method"] = "plain"
    result = run_auth_config(tmp_path, config)
    assert result.returncode == 1


def test_webauthn_plus_sms_is_not_described_as_only_sms(tmp_path):
    config = {**jwt_config_fixture(), "mfa": {"enabled": True, "methods": ["webauthn", "sms"]}}
    result = run_auth_config(tmp_path, config)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Only SMS" not in result.stdout


def test_unknown_mfa_method_is_unassessed_not_strong(tmp_path):
    result = run_auth_config(
        tmp_path, {**jwt_config_fixture(), "mfa": {"enabled": True, "methods": ["fictional-unsupported"]}}
    )
    assert result.returncode == 2


@pytest.mark.parametrize(
    "policy",
    [
        {**policy_fixture(), "minimum_length": 8, "authentication_context": "mfa"},
        {**policy_fixture(), "hashing": {"algorithm": "pbkdf2", "prf": "sha512", "iterations": 220000}},
        {
            **policy_fixture(),
            "hashing": {"algorithm": "argon2id", "memory_cost_kib": 47104, "time_cost": 1, "parallelism": 1},
        },
        {
            **policy_fixture(),
            "hashing": {"algorithm": "argon2id", "memory_cost_kib": 19456, "time_cost": 2, "parallelism": 1},
        },
    ],
)
def test_supported_declared_password_review_profiles(tmp_path, policy):
    result = run_policy(tmp_path, policy)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["runtime_verified"] is False


@pytest.mark.parametrize("script", ["authentication_check.py", "password_policy_check.py"])
def test_configuration_duplicate_keys_never_clear_gate(tmp_path, script):
    path = tmp_path / "ambiguous.json"
    path.write_text('{"minimum_length":1,"minimum_length":15}')
    result = invoke(tmp_path, script, "--config", str(path))
    assert result.returncode == 2
    assert json.loads(result.stdout)["complete"] is False


def test_empty_candidate_is_tested_instead_of_silently_reviewing_only_policy(tmp_path):
    result = run_policy(tmp_path, policy_fixture(), "--test-password", "")
    assert result.returncode == 1
    assert json.loads(result.stdout)["password_valid"] is False


def test_password_file_is_not_echoed_or_trimmed(tmp_path):
    secret = "Fictional violet ocean phrase\n"
    path = tmp_path / "candidate.txt"
    path.write_text(secret)
    path.chmod(0o600)
    policy = {**policy_fixture(), "maximum_length": len(secret) - 1}
    result = run_policy(tmp_path, policy, "--password-file", str(path))
    assert result.returncode == 1
    assert json.loads(result.stdout)["password_valid"] is False
    assert "Fictional violet ocean phrase" not in result.stdout + result.stderr


@pytest.mark.parametrize(
    "script,fixture", [("authentication_check.py", jwt_config_fixture), ("password_policy_check.py", policy_fixture)]
)
def test_declared_reports_are_private_single_document_outputs(tmp_path, script, fixture):
    config = tmp_path / "config.json"
    config.write_text(json.dumps(fixture()))
    output = tmp_path / "report.json"
    result = invoke(tmp_path, script, "--config", str(config), "--output", str(output))
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    assert json.loads(output.read_text())["complete"] is True
    assert output.stat().st_mode & 0o777 == 0o600


def test_jwt_report_cannot_replace_the_selected_trust_key(tmp_path, trust_profile):
    jwt, key, key_file, profile = trust_profile
    result = run_token(
        tmp_path, jwt.encode(signed_claims(), key, algorithm="HS256"), *profile, "--output", str(key_file)
    )
    assert result.returncode == 2
    assert key_file.read_bytes() == key


@pytest.mark.parametrize(
    "script,fixture", [("authentication_check.py", jwt_config_fixture), ("password_policy_check.py", policy_fixture)]
)
def test_report_cannot_replace_its_configuration_input(tmp_path, script, fixture):
    path = tmp_path / "input.json"
    original = json.dumps(fixture())
    path.write_text(original)
    result = invoke(tmp_path, script, "--config", str(path), "--output", str(path))
    assert result.returncode == 2
    assert path.read_text() == original


def test_claim_rejection_cannot_keep_a_verified_claims_flag(tmp_path, trust_profile, monkeypatch):
    """A clock/profile disagreement must not erase a local claim rejection."""
    import importlib.util

    jwt, key, _, _ = trust_profile
    spec = importlib.util.spec_from_file_location("auth_jwt_clock_fixture", SCRIPTS / "jwt_analyzer.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.syspath_prepend(str(SCRIPTS))
    spec.loader.exec_module(module)
    claims = {"iss": "https://issuer.invalid", "aud": "fictional-app", "exp": 4102444800, "iat": 1}
    token = jwt.encode(claims, key, algorithm="HS256")
    # Real backend cryptography/claims remain active; only the inspector clock
    # disagrees, exercising a failed local predicate after successful decoding.
    monkeypatch.setattr(module.time, "time", lambda: 0)
    report = module.JWTAnalyzer().analyze_token(
        token, "HS256", key=key, issuer="https://issuer.invalid", audience="fictional-app"
    )
    assert report["status"] == "invalid" and report["valid"] is False
    assert report["signature"]["verified"] is True
    assert report["claims_verified"] is False
