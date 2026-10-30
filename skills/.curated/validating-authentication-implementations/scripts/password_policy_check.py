#!/usr/bin/env python3
"""Review declared password policy and local candidate rules, never authenticate.

0 no automated flags in selected scope; 1 findings/review; 2 incomplete/usage.
No password storage, online breach lookup, account operations or certification.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import sys

from auth_runtime import InputError, MAX_INPUT, load_object, read_bytes, write_report
from auth_schema import check_policy


class PasswordPolicyValidator:
    def __init__(self):
        self.findings = []
        self.warnings = []
        self.info = []

    def finding(self, issue):
        self.findings.append({"severity": "high", "issue": issue})

    def review(self, issue):
        self.warnings.append({"severity": "review", "issue": issue})

    def validate_policy(self, policy):
        check_policy(policy)
        self.findings, self.warnings, self.info = [], [], []
        required = 8 if policy.get("authentication_context") == "mfa" else 15
        if policy["minimum_length"] < required:
            self.finding("Declared minimum length is below the selected authentication-context guidance")
        if 0 < policy.get("maximum_length", 0) < 64:
            self.review("Declared maximum length is below 64 code points")
        if any(
            policy.get(name)
            for name in (
                "require_uppercase",
                "require_lowercase",
                "require_numbers",
                "require_special_chars",
                "require_mixed_case",
                "no_consecutive_chars",
            )
        ):
            self.review("Mandatory composition restrictions require review against NIST 800-63B-4")
        if policy.get("password_max_age_days", 0):
            self.review(
                "Periodic password expiration requires review; do not substitute it for compromise-driven changes"
            )
        if policy.get("password_min_age_days", 0):
            self.review("Minimum password age may prevent prompt compromised-password changes")
        if not policy.get("rejected_patterns"):
            self.review("No explicit local blocklist supplied; deployment blocklist checking is unassessed")
        lockout = policy.get("account_lockout", {})
        if not policy.get("rate_limiting_enabled") and not lockout.get("enabled"):
            self.review("Online throttling is not declared; runtime control remains unassessed")
        elif lockout.get("enabled") and not 1 <= lockout.get("max_attempts", 0) <= 100:
            self.finding("Declared consecutive-attempt limit is missing or exceeds 100")
        self._check_hashing(policy.get("hashing", {}))
        return self._generate_policy_report()

    def _check_hashing(self, config):
        algorithm = config.get("algorithm", "").lower()
        if algorithm in ("md5", "sha1", "sha256", "sha512", "plaintext"):
            self.finding("Declared storage algorithm is not an adaptive password KDF")
        elif algorithm == "pbkdf2":
            floor = {"sha256": 600000, "sha512": 220000}.get(config.get("prf", "sha256").lower())
            if floor is None:
                self.review("Declared PBKDF2 PRF is outside the supported review profiles")
            elif config.get("iterations", 0) < floor:
                self.finding("Declared PBKDF2 work factor is below the selected PRF review profile")
        elif algorithm == "bcrypt":
            if config.get("work_factor", 0) < 10:
                self.finding("Declared bcrypt work factor is below 10")
            self.review("Legacy bcrypt requires explicit handling of its 72-byte input limit")
        elif algorithm == "argon2id":
            profiles = ((47104, 1), (19456, 2), (12288, 3), (9216, 4), (7168, 5))
            if config.get("parallelism") != 1:
                self.review("Argon2id parallelism is outside the explicitly supported review profiles")
            if not any(
                config.get("memory_cost_kib", 0) >= memory and config.get("time_cost", 0) >= passes
                for memory, passes in profiles
            ):
                self.finding("Declared Argon2id cost is below the supported memory/time review profiles")
        else:
            self.review("Password KDF variant/parameters are absent or outside supported review profiles")

    def test_password(self, password, policy):
        policy_report = self.validate_policy(policy)
        if not isinstance(password, str) or len(password.encode("utf-8")) > MAX_INPUT:
            raise InputError("candidate missing or exceeds size limit")
        errors = []
        if not password:
            errors.append("Candidate is empty")
        if len(password) < policy["minimum_length"]:
            errors.append("Candidate is shorter than the declared minimum")
        if policy.get("maximum_length", 0) and len(password) > policy["maximum_length"]:
            errors.append("Candidate exceeds the declared maximum")
        checks = {
            "require_uppercase": any(c.isupper() for c in password),
            "require_lowercase": any(c.islower() for c in password),
            "require_numbers": any(c.isdecimal() for c in password),
            "require_special_chars": any(not c.isalnum() and not c.isspace() for c in password),
        }
        if any(policy.get(name) and not passed for name, passed in checks.items()):
            errors.append("Candidate fails a declared composition rule")
        if policy.get("require_mixed_case") and not (checks["require_uppercase"] and checks["require_lowercase"]):
            errors.append("Candidate fails the declared mixed-case rule")
        if policy.get("no_consecutive_chars") and any(a == b for a, b in zip(password, password[1:])):
            errors.append("Candidate fails the declared adjacent-repeat rule")
        # Legacy field name retained, with exact values, never regex execution
        # or substring matching presented as a compromised-password blocklist.
        if password in policy.get("rejected_patterns", []):
            errors.append("Candidate matches a supplied blocked value")
        if policy.get("hashing", {}).get("algorithm", "").lower() == "bcrypt" and len(password.encode("utf-8")) > 72:
            errors.append("Candidate exceeds the declared bcrypt byte limit; truncation is not accepted")
        unassessed = []
        if policy.get("password_history_count", 0):
            unassessed.append("history cannot be checked from a single supplied candidate")
        if not policy.get("rejected_patterns"):
            unassessed.append("candidate blocklist coverage is unavailable")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scope": "local candidate against supplied rules and exact local blocklist only",
            "runtime_verified": False,
            "complete": not unassessed,
            "password_valid": False if errors else None if unassessed else True,
            "errors": errors,
            "unassessed": unassessed,
            "warnings": policy_report["warnings"],
            "policy_findings": policy_report["findings"],
            "score": None,
            "score_note": "no strength/entropy estimate is computed",
            "strengths": [],
        }

    def _generate_policy_report(self):
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scope": "declared password policy; provided blocklist and selected KDF review profiles only",
            "runtime_verified": False,
            "complete": True,
            "summary": {
                "critical": 0,
                "high": len(self.findings),
                "medium": 0,
                "warning": len(self.warnings),
                "info": len(self.info),
                "passed": not self.findings and not self.warnings,
            },
            "findings": self.findings,
            "warnings": self.warnings,
            "info": self.info,
        }


def gate(report):
    if report.get("complete") is not True:
        return 2
    if "password_valid" in report:
        return 0 if report["password_valid"] is True and not report["warnings"] and not report["policy_findings"] else 1
    return 0 if report["summary"]["passed"] else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    policy = parser.add_mutually_exclusive_group(required=True)
    policy.add_argument("-c", "--config")
    policy.add_argument("-p", "--policy")
    candidate = parser.add_mutually_exclusive_group()
    candidate.add_argument(
        "-t",
        "--test",
        "-tp",
        "--test-password",
        dest="password",
        help="legacy inline candidate; prefer private --password-file",
    )
    candidate.add_argument("--password-file", help="exact UTF-8 bytes; no whitespace/newline stripping")
    candidate.add_argument("--password-stdin", action="store_true", help="exact UTF-8 input, not echoed")
    parser.add_argument("-o", "--output")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        declaration = load_object(args.config or args.policy)
        validator = PasswordPolicyValidator()
        password = args.password
        if args.password_file:
            password = read_bytes(args.password_file).decode("utf-8")
        elif args.password_stdin:
            raw = sys.stdin.buffer.read(MAX_INPUT + 1)
            if len(raw) > MAX_INPUT:
                raise InputError("candidate exceeds size limit")
            password = raw.decode("utf-8")
        report = (
            validator.validate_policy(declaration)
            if password is None
            else validator.test_password(password, declaration)
        )
        write_report(report, args.output, protected_inputs=(args.config or args.policy, args.password_file))
        return gate(report)
    except (InputError, OSError, UnicodeError, TypeError, ValueError, RecursionError, OverflowError):
        report = {
            "complete": False,
            "status": "incomplete",
            "summary": {"passed": False},
            "errors": ["password policy, candidate or report could not be assessed"],
        }
        if not args.output:
            write_report(report)
        else:
            print("ERROR: password policy, candidate or report could not be assessed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
