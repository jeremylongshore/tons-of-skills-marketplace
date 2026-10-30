---
name: detecting-weak-cryptography
description: |
  Scan a source tree for weak cryptographic primitives: MD5 / SHA-1
  used for security purposes, DES / 3DES / RC4 ciphers, ECB block
  mode, custom-built crypto (XOR loops, hand-rolled HMAC),
  hardcoded IVs, predictable random (Math.random / java.util.Random
  for crypto seeds), missing certificate verification
  (verify=False, rejectUnauthorized: false).
  Use when: pre-merge gate on crypto-touching code, audit before
  SOC2 / PCI assessment, post-incident review when "we found a
  weakness in our token signing."
  Threshold: any call to a known-weak algorithm with non-test
  context, OR cert verification explicitly disabled, OR a custom
  crypto loop pattern.
  Trigger with: "scan weak crypto", "find MD5 usage", "check ECB
  mode", "audit ssl verify", "weak random".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Glob
  - Grep
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - static-analysis
  - cryptography
  - pentest
---

# Detecting Weak Cryptography

## Overview

Weak cryptography (CWE-327 Use of a Broken or Risky Cryptographic
Algorithm, CWE-330 Use of Insufficiently Random Values) shows up
when engineers use the convenient API instead of the cryptographic
one. `hashlib.md5(password)` is faster to type than the correct
bcrypt/argon2 invocation; `Math.random()` returns a number quickly
without needing to know about `crypto.randomBytes()`.

The fix is universal: use the modern primitive. SHA-256 for general
hashing, bcrypt/argon2/scrypt for passwords, AES-GCM for encryption,
HMAC-SHA256 for signing, `secrets` / `crypto.randomBytes` /
`SecureRandom` for randomness.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| MD5 used in security context | **HIGH** | hashlib.md5, MessageDigest.MD5, CryptoJS.MD5 | CWE-327 |
| SHA-1 used in security context | **HIGH** | hashlib.sha1, etc. | CWE-327 |
| DES / 3DES cipher | **CRITICAL** | DESCrypto, "DES/CBC", "DESede" | CWE-327 |
| RC4 cipher | **CRITICAL** | "ARC4", "RC4" | CWE-327 |
| AES ECB mode | **CRITICAL** | "AES/ECB" or `MODE_ECB` | CWE-327 |
| Hardcoded IV (initialization vector) | **CRITICAL** | IV literal in source | CWE-329 |
| Custom XOR-based "encryption" | **CRITICAL** | XOR loop over bytes | CWE-327 |
| Predictable random for crypto seed | **CRITICAL** | Math.random / java.util.Random / random.random for keys | CWE-330 |
| TLS cert verification disabled | **CRITICAL** | verify=False, rejectUnauthorized:false, ServerCertificateValidationCallback returning true | CWE-295 |
| Hardcoded HMAC secret | **HIGH** | Long literal in HMAC constructor | CWE-321 |
| Insecure password hashing (no salt, no KDF) | **CRITICAL** | hashlib.sha256(password) without bcrypt/argon2 | CWE-916 |

## Prerequisites

- Python 3.9+
- Source tree on local filesystem

## Instructions

### Run

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-weak-cryptography/scripts/scan_weak_crypto.py /path/to/repo
```

Options: `--output`, `--format`, `--min-severity`, `--include-tests`,
`--languages`, `--allow-md5-checksums` (excludes MD5 used in
non-security contexts like content-addressable storage).

### Interpret

CRITICAL = direct cryptographic break available against the
algorithm. CVEs, public attack tools, sometimes pre-computed
tables (rainbow tables for MD5/SHA-1).

HIGH = algorithm collision-broken (MD5, SHA-1) but the specific
use case may tolerate the weakness (file-deduplication checksums,
non-security HMAC). Verify the usage context.

### Remediation

See `references/PLAYBOOK.md` for per-primitive migration. Modern
defaults: SHA-256/SHA-3 for hashing, AES-256-GCM for encryption,
HMAC-SHA-256 for signing, secrets-grade random for keys, bcrypt /
argon2id for password storage.

## Examples

### Pre-merge gate

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-weak-cryptography/scripts/scan_weak_crypto.py \
    --min-severity high $(git diff --name-only main...HEAD | tr '\n' ' ')
```

### CI

```yaml
- name: Weak-crypto scan
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-weak-cryptography/scripts/scan_weak_crypto.py \
        . --min-severity high
```

## Output

JSON / JSONL / Markdown. Exit codes: 0 / 1 / 2.

## Error Handling

False positives common on:

- MD5 used for content-addressable storage (caches, content hashes)
  where collision resistance against ATTACKERS isn't needed — use
  `--allow-md5-checksums`.
- HMAC-MD5 — broken against adversaries but acceptable as an
  integrity check inside a TLS session where the channel is
  already authenticated.

Verify each finding by reading whether the algorithm's failure
mode (collision, preimage, etc.) is actually exploitable in
context.

## Resources

- `references/THEORY.md` — Per-primitive attack model (why MD5 /
  SHA-1 are collision-broken, why ECB leaks structure, why
  Math.random is non-crypto-grade)
- `references/PLAYBOOK.md` — Per-language modern-crypto recipes
  (Python cryptography library, Node crypto, Java JCA with
  modern algorithms, Go crypto/rand + crypto/cipher AEAD)
