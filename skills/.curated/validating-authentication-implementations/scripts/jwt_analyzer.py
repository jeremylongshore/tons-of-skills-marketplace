#!/usr/bin/env python3
"""Inspect local compact JWTs, or verify an explicit local trust/claim profile.

0 verified; 1 invalid under selected checks; 2 unverified/incomplete/usage.
No token-selected keys/algorithms, remote JWKS, installs or identity certification.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
from importlib import metadata
import math
import re
import sys
import time

from auth_runtime import InputError, parse_object, read_bytes, write_report

ALGORITHMS = frozenset(
    ("HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512")
)
MAX_TOKEN = 256 * 1024


def decode_part(segment):
    if not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", segment):
        raise InputError("invalid compact JWT encoding")
    try:
        raw = base64.b64decode(segment + "=" * (-len(segment) % 4), altchars=b"-_", validate=True)
    except ValueError as error:
        raise InputError("invalid compact JWT encoding") from error
    if base64.urlsafe_b64encode(raw).decode().rstrip("=") != segment.rstrip("="):
        raise InputError("non-canonical JWT encoding")
    return raw


def backend():
    try:
        version = metadata.version("PyJWT")
        match = re.fullmatch(r"2\.(\d+)\.(\d+)(?:\.post\d+)?", version)
        if not match or (int(match[1]), int(match[2])) < (15, 1):
            raise InputError("verification requires supported PyJWT >=2.15.1,<3")
        import jwt

        if jwt.__version__ != version:
            raise InputError("JWT backend identity/version mismatch")
        return jwt, version
    except (metadata.PackageNotFoundError, ImportError) as error:
        raise InputError("verification backend unavailable; no installation attempted") from error


class JWTAnalyzer:
    VALID_ALGORITHMS = ALGORITHMS

    def analyze_token(self, token, algorithm=None, *, key=None, issuer=None, audience=None):
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "valid": None,
            "complete": False,
            "status": "unverified",
            "scope": "local compact JWT and explicitly selected trust/claim profile only",
            "signature": {"verified": False},
            "claims_verified": False,
            "findings": [],
            "warnings": [],
            "errors": [],
            "info": [],
            "header": {},
            "payload": {},
        }
        try:
            if not isinstance(token, str) or not token or len(token.encode("utf-8")) > MAX_TOKEN:
                raise InputError("token missing or exceeds size limit")
            parts = token.split(".")
            if len(parts) != 3:
                raise InputError("expected compact signed JWT with three parts")
            header = parse_object(decode_part(parts[0]).decode("utf-8"))
            payload = parse_object(decode_part(parts[1]).decode("utf-8"))
            decode_part(parts[2])
            # Only controlled metadata is included; raw claims, signature, kid,
            # header URLs and attacker-supplied diagnostic strings are omitted.
            report["header"] = {"algorithm": header.get("alg") if header.get("alg") in ALGORITHMS else "unsupported"}
            report["payload"] = {
                "registered_claims_present": [
                    name for name in ("iss", "aud", "sub", "exp", "nbf", "iat", "jti") if name in payload
                ],
                "custom_claim_count": len(set(payload) - {"iss", "aud", "sub", "exp", "nbf", "iat", "jti"}),
            }
            if not isinstance(header.get("alg"), str) or header["alg"] not in ALGORITHMS:
                raise InputError("unsupported or unsigned JWT algorithm")
            if "crit" in header or "b64" in header:
                report["errors"].append("critical/unencoded payload extensions are unsupported")
                report["status"] = "incomplete"
                return report
            if "typ" in header and not isinstance(header["typ"], str):
                raise InputError("invalid token type")
            if "exp" not in payload:
                raise InputError("required expiration claim is absent")
            now = time.time()
            for name in ("exp", "nbf", "iat"):
                if name in payload:
                    value = payload[name]
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                        raise InputError("time claims must be finite NumericDate values")
            if payload["exp"] <= now:
                report["findings"].append({"severity": "high", "issue": "Token expiration has passed"})
            if payload.get("nbf", now) > now:
                report["findings"].append({"severity": "high", "issue": "Token is not yet valid"})
            if payload.get("iat", now) > now:
                report["findings"].append({"severity": "high", "issue": "Issued-at time is in the future"})
            if any(name in payload and not isinstance(payload[name], str) for name in ("iss", "sub", "jti")):
                raise InputError("invalid registered text claim")
            if "aud" in payload and not (
                isinstance(payload["aud"], str)
                or isinstance(payload["aud"], list)
                and payload["aud"]
                and all(isinstance(x, str) and x for x in payload["aud"])
            ):
                raise InputError("invalid audience claim")
        except (InputError, UnicodeError, RecursionError, OverflowError, TypeError) as error:
            report.update(valid=False, status="invalid", complete=True)
            report["errors"].append(str(error) if isinstance(error, InputError) else "malformed JWT data")
            return report

        if key is None or not algorithm or not issuer or not audience:
            report["errors"].append("verification requires local key, explicit algorithm, issuer and audience")
            if report["findings"]:
                report["valid"] = False
            return report
        if algorithm not in ALGORITHMS or header["alg"] != algorithm:
            report.update(valid=False, status="invalid", complete=True)
            report["errors"].append("token algorithm does not match the selected profile")
            return report
        try:
            if not isinstance(key, bytes) or not key or len(key) > 256 * 1024:
                raise InputError("verification key missing or exceeds size limit")
            if not isinstance(issuer, str) or not issuer or not isinstance(audience, str) or not audience:
                raise InputError("issuer and audience must be explicit nonempty text")
            jwt, version = backend()
            report["backend"] = {"name": "PyJWT", "version": version}
            # Never build this list from received claims, headers or key URLs.
            prepared = jwt.get_algorithm_by_name(algorithm).prepare_key(key)
            if algorithm.startswith("HS") and len(prepared) < int(algorithm[2:]) // 8:
                raise InputError("HMAC key is shorter than the selected hash size")
            if algorithm.startswith(("RS", "PS")) and prepared.key_size < 2048:
                raise InputError("RSA verification requires a key of at least 2048 bits")
            if (
                algorithm.startswith("ES")
                and prepared.curve.name != {"ES256": "secp256r1", "ES384": "secp384r1", "ES512": "secp521r1"}[algorithm]
            ):
                raise InputError("EC key curve does not match selected algorithm")
            verified = jwt.decode(
                token,
                prepared,
                algorithms=[algorithm],
                issuer=issuer,
                audience=audience,
                options={
                    "require": ["exp", "iss", "aud"],
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_sub": True,
                    "verify_jti": True,
                },
                leeway=0,
            )
            if verified != payload:
                raise InputError("verified payload differs from inspected payload")
            report.update(valid=True, complete=True, status="verified", claims_verified=True)
            report["signature"]["verified"] = True
            # Earlier timestamp findings remain a failed gate even at a boundary.
            if report["findings"]:
                report.update(valid=False, status="invalid", claims_verified=False)
        except InputError as error:
            report["errors"].append(str(error))
            report["status"] = "incomplete"
        except (ImportError, NotImplementedError, AttributeError):
            report["errors"].append("selected verification backend/algorithm unavailable")
            report["status"] = "incomplete"
        except Exception as error:
            # Backend exception messages may contain input/key data. Categorize
            # known token rejection separately from key/setup/operational errors.
            try:
                from jwt.exceptions import InvalidKeyError, InvalidTokenError

                invalid = isinstance(error, InvalidTokenError) and not isinstance(error, InvalidKeyError)
            except ImportError:
                invalid = False
            report.update(
                valid=False if invalid else None, complete=invalid, status="invalid" if invalid else "incomplete"
            )
            report["errors"].append(
                "token rejected by selected verification profile" if invalid else "verification could not be completed"
            )
        return report


def gate(report):
    return (
        0 if report["status"] == "verified" and report["valid"] is True else 1 if report["status"] == "invalid" else 2
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-t", "--token", help="legacy inline input; prefer a private --file to avoid shell history")
    source.add_argument("-f", "--file", help="private local token file")
    parser.add_argument("-a", "--algorithm", choices=sorted(ALGORITHMS), help="operator-selected allowed algorithm")
    parser.add_argument("--key", help="local trusted key file; never a token-provided key")
    parser.add_argument("--issuer", help="operator-selected expected issuer")
    parser.add_argument("--audience", help="operator-selected expected audience")
    parser.add_argument("--validate", action="store_true", help="require a complete verification profile")
    parser.add_argument("-o", "--output")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        token = args.token if args.token is not None else read_bytes(args.file, MAX_TOKEN).decode("utf-8").strip()
        key = read_bytes(args.key, 256 * 1024) if args.key else None
        report = JWTAnalyzer().analyze_token(token, args.algorithm, key=key, issuer=args.issuer, audience=args.audience)
        write_report(report, args.output, protected_inputs=(args.file, args.key))
        return gate(report)
    except (InputError, UnicodeError):
        report = {
            "valid": None,
            "complete": False,
            "status": "incomplete",
            "errors": ["cannot read/write selected token, key or report"],
        }
        try:
            if not args.output:
                write_report(report)
            else:
                print("ERROR: cannot read/write selected token, key or report", file=sys.stderr)
        except OSError:
            pass
        return 2


if __name__ == "__main__":
    sys.exit(main())
