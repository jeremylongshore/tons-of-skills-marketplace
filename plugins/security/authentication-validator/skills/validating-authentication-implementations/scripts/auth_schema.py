"""Types for the existing declared-configuration inputs; not runtime proof."""

import math

from auth_runtime import InputError

NUMBER = "number"
INTEGER = "integer"
TEXTS = "texts"


def check_object(value, fields):
    if not isinstance(value, dict) or set(value) - set(fields):
        raise InputError("unsupported configuration object or field")
    for name, item in value.items():
        kind = fields[name]
        if isinstance(kind, dict):
            check_object(item, kind)
        elif kind == NUMBER or kind == INTEGER:
            if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) or item < 0:
                raise InputError("configuration numeric value must be finite and nonnegative")
            if kind == INTEGER and type(item) is not int:
                raise InputError("configuration count must be an integer")
        elif kind == TEXTS:
            if not isinstance(item, list) or any(not isinstance(x, str) or not x for x in item):
                raise InputError("configuration list must contain nonempty text")
        elif type(item) is not kind:
            raise InputError("configuration field has the wrong type")


LOCKOUT = {"enabled": bool, "max_attempts": INTEGER, "lockout_duration_minutes": NUMBER}
HASHING = {
    "algorithm": str,
    "iterations": INTEGER,
    "work_factor": INTEGER,
    "memory_cost_kib": INTEGER,
    "time_cost": INTEGER,
    "parallelism": INTEGER,
    "prf": str,
}
PASSWORD = {
    "authentication_context": str,
    "rate_limiting_enabled": bool,
    "minimum_length": INTEGER,
    "maximum_length": INTEGER,
    "require_uppercase": bool,
    "require_lowercase": bool,
    "require_numbers": bool,
    "require_special_chars": bool,
    "require_mixed_case": bool,
    "no_consecutive_chars": bool,
    "password_history_count": INTEGER,
    "password_max_age_days": NUMBER,
    "password_min_age_days": NUMBER,
    "account_lockout": LOCKOUT,
    "hashing": HASHING,
    "rejected_patterns": TEXTS,
}
CONFIG = {
    "method": str,
    "jwt": {
        "algorithm": str,
        "use_public_key": bool,
        "expiration_seconds": NUMBER,
        "refresh_token": {"expiration_seconds": NUMBER},
        "audience": str,
        "issuer": str,
    },
    "oauth": {
        "client_type": str,
        "pkce_method": str,
        "client_secret": str,
        "redirect_uris": TEXTS,
        "scopes": TEXTS,
        "pkce_enabled": bool,
    },
    "session": {
        "cookie": {"secure": bool, "httponly": bool, "samesite": str},
        "timeout_seconds": NUMBER,
        "idle_timeout_seconds": NUMBER,
    },
    "api_key": {
        "store_plaintext": bool,
        "minimum_length": INTEGER,
        "rotation_enabled": bool,
        "rate_limiting_enabled": bool,
    },
    "password_policy": PASSWORD,
    "mfa": {"enabled": bool, "methods": TEXTS},
    "account_lockout": LOCKOUT,
}


def check_config(value):
    check_object(value, CONFIG)
    if value.get("method") not in ("jwt", "oauth", "session", "api_key"):
        raise InputError("authentication method missing or unsupported")
    selected = {"jwt": "jwt", "oauth": "oauth", "session": "session", "api_key": "api_key"}[value["method"]]
    if not value.get(selected):
        raise InputError("selected authentication configuration is absent")
    if value["method"] == "oauth" and value["oauth"].get("client_type") not in ("public", "confidential"):
        raise InputError("OAuth client type must be explicitly selected")
    if any(
        name not in {"sms", "email", "totp", "hotp", "webauthn", "push", "recovery_codes", "backup_codes"}
        for name in value.get("mfa", {}).get("methods", [])
    ):
        raise InputError("MFA method is outside the supported declaration profile")


def check_policy(value):
    check_object(value, PASSWORD)
    if not value:
        raise InputError("password policy is absent")
    if value.get("authentication_context", "single-factor") not in ("single-factor", "mfa"):
        raise InputError("unsupported declared authentication context")
    minimum, maximum = value.get("minimum_length"), value.get("maximum_length", 0)
    if minimum is None or minimum < 1 or maximum and maximum < minimum:
        raise InputError("password length constraints are missing or contradictory")
