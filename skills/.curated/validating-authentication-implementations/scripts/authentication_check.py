#!/usr/bin/env python3
"""Review explicitly supplied authentication declarations, not live enforcement.

JSON-only local --config input; no code scan, login, provider or installation.
0 no automated flags in supplied scope; 1 findings/review; 2 incomplete/usage.
"""

import argparse
import sys
from typing import Dict, Any
from datetime import datetime
from urllib.parse import urlsplit

from auth_runtime import InputError, load_object, write_report
from auth_schema import check_config
from jwt_analyzer import ALGORITHMS
from password_policy_check import PasswordPolicyValidator


class AuthenticationValidator:
    """Validates authentication implementations."""

    def __init__(self):
        """Initialize the authentication validator."""
        self.findings = []
        self.warnings = []
        self.info = []

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate authentication configuration.

        Args:
            config: Authentication configuration dictionary

        Returns:
            Validation report dictionary
        """
        self.findings = []
        self.warnings = []
        self.info = []
        check_config(config)

        # Determine auth method and validate accordingly
        auth_method = config.get("method", "unknown")

        if auth_method == "jwt":
            self._validate_jwt(config)
        elif auth_method == "oauth":
            self._validate_oauth(config)
        elif auth_method == "session":
            self._validate_session(config)
        elif auth_method == "api_key":
            self._validate_api_key(config)
        else:
            self.warnings.append(
                {
                    "severity": "warning",
                    "issue": "Unknown authentication method",
                    "description": f"Authentication method '{auth_method}' is not recognized",
                }
            )

        # Only inspect supplied declarations. Their absence is explicit coverage,
        # not proof an API client needs local password storage or interactive MFA.
        if "password_policy" in config:
            self._check_password_policy(config)
        if "mfa" in config:
            self._check_mfa(config)
        if "account_lockout" in config:
            self._check_account_lockout(config)
        self.unassessed = [name for name in ("password_policy", "mfa", "account_lockout") if name not in config]

        return self._generate_report()

    def _validate_jwt(self, config: Dict[str, Any]) -> None:
        """Validate JWT configuration."""
        jwt_config = config.get("jwt", {})

        # Check signing algorithm
        algorithm = jwt_config.get("algorithm", "")
        if not algorithm:
            self.findings.append(
                {
                    "severity": "critical",
                    "issue": "No signing algorithm specified",
                    "description": "JWT configuration missing algorithm",
                    "recommendation": "Specify a strong algorithm (e.g., HS256, RS256)",
                }
            )
        elif algorithm not in ALGORITHMS or (algorithm.startswith("HS") and jwt_config.get("use_public_key")):
            self.findings.append(
                {"severity": "critical", "issue": "Unsupported or incompatible JWT algorithm/key declaration"}
            )
        else:
            self.info.append(
                {"severity": "info", "issue": "Recognized declared JWT algorithm; implementation not verified"}
            )

        # Check token expiration
        expiration = jwt_config.get("expiration_seconds")
        if not expiration:
            self.findings.append(
                {
                    "severity": "high",
                    "issue": "No token expiration set",
                    "description": "JWT tokens without expiration present a security risk",
                    "recommendation": "Set expiration to a reasonable value (e.g., 3600 seconds)",
                }
            )
        elif expiration > 86400:  # More than 24 hours
            self.warnings.append(
                {
                    "severity": "high",
                    "issue": f"Very long token expiration: {expiration} seconds",
                    "description": "Token expiration exceeds 24 hours, increasing compromise risk",
                    "recommendation": "Reduce expiration to 1-24 hours depending on use case",
                }
            )

        # Check refresh token
        refresh_token = jwt_config.get("refresh_token", {})
        if refresh_token:
            refresh_expiration = refresh_token.get("expiration_seconds")
            if refresh_expiration and expiration and refresh_expiration <= expiration:
                self.findings.append(
                    {
                        "severity": "high",
                        "issue": "Refresh token expiration <= access token expiration",
                        "description": "Refresh token should have longer expiration than access token",
                        "recommendation": "Set refresh token expiration to 7-30 days",
                    }
                )

        # Check audience and issuer
        if not jwt_config.get("audience"):
            self.warnings.append(
                {
                    "severity": "medium",
                    "issue": "JWT audience not specified",
                    "description": "Audience claim helps prevent token misuse",
                    "recommendation": "Add audience validation to JWT validation",
                }
            )

        if not jwt_config.get("issuer"):
            self.warnings.append(
                {
                    "severity": "medium",
                    "issue": "JWT issuer not specified",
                    "description": "Issuer claim helps identify token source",
                    "recommendation": "Add issuer validation to JWT validation",
                }
            )

    def _validate_oauth(self, config: Dict[str, Any]) -> None:
        """Validate OAuth configuration."""
        oauth_config = config.get("oauth", {})

        client_type = oauth_config["client_type"]
        if client_type == "confidential" and not oauth_config.get("client_secret"):
            self.findings.append(
                {"severity": "critical", "issue": "Shared-secret confidential-client profile lacks its declared secret"}
            )
        if client_type == "public" and oauth_config.get("client_secret"):
            self.warnings.append(
                {
                    "severity": "review",
                    "issue": "Public-client embedded secret does not establish confidential-client identity",
                }
            )
        redirects = oauth_config.get("redirect_uris", [])
        if not redirects:
            self.findings.append({"severity": "high", "issue": "No redirect URI declarations supplied"})
        for uri in redirects:
            try:
                parsed = urlsplit(uri)
                port = parsed.port
            except ValueError as error:
                raise InputError("malformed redirect URI") from error
            if any(ord(char) <= 32 or ord(char) == 127 for char in uri):
                raise InputError("redirect URI contains control/space characters")
            if "*" in uri or parsed.fragment or parsed.username is not None or parsed.password is not None:
                self.findings.append(
                    {"severity": "high", "issue": "Redirect declaration contains wildcard, fragment or userinfo"}
                )
            elif parsed.scheme != "https" or not parsed.hostname or port == 0:
                self.warnings.append(
                    {"severity": "review", "issue": "Redirect is outside the supported HTTPS web-client review profile"}
                )
        if not oauth_config.get("scopes"):
            self.warnings.append({"severity": "review", "issue": "OAuth permission scope is not declared"})
        elif any("*" in scope for scope in oauth_config["scopes"]):
            self.warnings.append({"severity": "review", "issue": "Wildcard OAuth scope requires justification"})
        if not oauth_config.get("pkce_enabled") or oauth_config.get("pkce_method") != "S256":
            target = self.findings if client_type == "public" else self.warnings
            target.append(
                {"severity": "high" if client_type == "public" else "review", "issue": "S256 PKCE is not declared"}
            )

    def _validate_session(self, config: Dict[str, Any]) -> None:
        """Validate session-based authentication."""
        session_config = config.get("session", {})

        # Check cookie attributes
        cookie_config = session_config.get("cookie", {})

        if not cookie_config.get("secure"):
            self.findings.append(
                {
                    "severity": "critical",
                    "issue": "Secure flag not set on session cookie",
                    "description": "Session cookie can be transmitted over HTTP",
                    "recommendation": "Set 'Secure' flag on session cookie",
                }
            )

        if not cookie_config.get("httponly"):
            self.findings.append(
                {
                    "severity": "high",
                    "issue": "HttpOnly flag not set on session cookie",
                    "description": "Session cookie can be accessed via JavaScript (XSS vulnerability)",
                    "recommendation": "Set 'HttpOnly' flag on session cookie",
                }
            )

        samesite = cookie_config.get("samesite", "").lower()
        if samesite not in ["strict", "lax"]:
            self.findings.append(
                {
                    "severity": "high",
                    "issue": "SameSite declaration requires contextual CSRF review",
                    "description": "SameSite metadata alone cannot establish CSRF protection",
                    "recommendation": "Review cross-site requirements and independently enforced CSRF defenses",
                }
            )

        # Check session timeout
        timeout = session_config.get("timeout_seconds")
        if not timeout:
            self.warnings.append(
                {
                    "severity": "high",
                    "issue": "No session timeout configured",
                    "description": "Sessions should have a timeout for security",
                }
            )
        elif timeout > 86400:  # More than 24 hours
            self.warnings.append(
                {
                    "severity": "high",
                    "issue": f"Very long session timeout: {timeout} seconds",
                    "description": "Session timeout exceeds 24 hours",
                    "recommendation": "Reduce session timeout to 30 minutes to 8 hours",
                }
            )

        # Check idle timeout
        idle_timeout = session_config.get("idle_timeout_seconds")
        if not idle_timeout:
            self.warnings.append(
                {
                    "severity": "medium",
                    "issue": "No idle timeout configured",
                    "description": "Sessions should timeout after inactivity",
                }
            )

    def _validate_api_key(self, config: Dict[str, Any]) -> None:
        """Validate API key authentication."""
        api_key_config = config.get("api_key", {})

        # Check key storage
        if api_key_config.get("store_plaintext"):
            self.findings.append(
                {
                    "severity": "critical",
                    "issue": "API keys stored in plaintext",
                    "description": "API keys should never be stored in plaintext",
                    "recommendation": "Review server-side storage for the actual key generation and verification design",
                }
            )

        # Check key length
        min_length = api_key_config.get("minimum_length", 0)
        if min_length < 32:
            self.warnings.append(
                {
                    "severity": "high",
                    "issue": f"Short API key minimum length: {min_length}",
                    "description": "API keys should be at least 32 characters",
                    "recommendation": "Verify generation entropy and key handling; character count alone is insufficient",
                }
            )

        if "rotation_enabled" in api_key_config:
            self.info.append(
                {"severity": "info", "issue": "Rotation metadata declared; lifecycle enforcement not tested"}
            )

        # Check rate limiting
        if not api_key_config.get("rate_limiting_enabled"):
            self.warnings.append(
                {
                    "severity": "medium",
                    "issue": "Rate limiting not enabled for API keys",
                    "description": "API keys should have rate limiting to prevent abuse",
                }
            )

    def _check_password_policy(self, config: Dict[str, Any]) -> None:
        """Check password policy configuration."""
        result = PasswordPolicyValidator().validate_policy(config["password_policy"])
        self.findings.extend(result["findings"])
        self.warnings.extend(result["warnings"])
        self.info.extend(result["info"])

    def _check_mfa(self, config: Dict[str, Any]) -> None:
        """Check multi-factor authentication configuration."""
        mfa_config = config.get("mfa", {})

        if not mfa_config or not mfa_config.get("enabled"):
            self.warnings.append(
                {
                    "severity": "high",
                    "issue": "Multi-factor authentication not enabled",
                    "description": "MFA provides additional account protection",
                    "recommendation": "Enable and enforce MFA for all users or sensitive operations",
                }
            )
        else:
            mfa_methods = mfa_config.get("methods", [])
            if not mfa_methods:
                self.findings.append(
                    {
                        "severity": "high",
                        "issue": "No MFA methods configured",
                        "description": "At least one MFA method should be available",
                    }
                )
            elif set(mfa_methods) <= {"sms", "email"}:
                self.warnings.append(
                    {
                        "severity": "medium",
                        "issue": "Only SMS/email MFA methods are declared",
                        "description": "Review authenticator choice and phishing resistance in the actual implementation",
                    }
                )

    def _check_account_lockout(self, config: Dict[str, Any]) -> None:
        """Check account lockout policy."""
        lockout_config = config.get("account_lockout", {})

        if not lockout_config or not lockout_config.get("enabled"):
            self.findings.append(
                {
                    "severity": "high",
                    "issue": "Account lockout not configured",
                    "description": "Account lockout helps prevent brute force attacks",
                    "recommendation": "Enable account lockout after N failed attempts",
                }
            )
        else:
            max_attempts = lockout_config.get("max_attempts", 0)
            if max_attempts == 0 or max_attempts > 100:
                self.warnings.append(
                    {
                        "severity": "medium",
                        "issue": "Consecutive-attempt limit missing or above 100",
                        "description": "Assess throttling and recovery; a lockout flag alone does not prove protection",
                    }
                )

    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "complete": True,
            "scope": "supplied declared configuration only; runtime enforcement not verified",
            "runtime_verified": False,
            "unassessed_controls": getattr(self, "unassessed", []),
            "summary": {
                "critical": len([f for f in self.findings if f.get("severity") == "critical"]),
                "high": len([f for f in self.findings if f.get("severity") == "high"]),
                "medium": len([f for f in self.findings if f.get("severity") == "medium"]),
                "warning": len(self.warnings),
                "info": len(self.info),
                "passed": len(self.findings) == 0 and len(self.warnings) == 0,
            },
            "findings": self.findings,
            "warnings": self.warnings,
            "info": self.info,
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate authentication implementations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  authentication_check.py --config auth.json
  authentication_check.py --config auth.json --output report.json
        """,
    )

    parser.add_argument("-c", "--config", type=str, help="Path to authentication configuration JSON file")
    parser.add_argument("-o", "--output", type=str, help="Output file for JSON report (stdout if not specified)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if not args.config:
        parser.error("--config is required")

    try:
        config = load_object(args.config)
        validator = AuthenticationValidator()
        report = validator.validate_config(config)
        write_report(report, args.output, protected_inputs=(args.config,))

        # The gate covers every reported finding/review flag, not only CRITICAL.
        return 0 if report["summary"]["passed"] else 1

    except (InputError, OSError, TypeError, ValueError, RecursionError, OverflowError):
        report = {
            "complete": False,
            "status": "incomplete",
            "summary": {"passed": False},
            "errors": ["authentication configuration or report could not be assessed"],
        }
        if not args.output:
            write_report(report)
        else:
            print("ERROR: authentication configuration or report could not be assessed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
