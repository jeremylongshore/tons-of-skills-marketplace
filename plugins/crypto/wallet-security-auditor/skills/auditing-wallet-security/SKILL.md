---
name: auditing-wallet-security
description: 'Audit wallet security by analyzing token approvals, permissions, and
  transaction patterns.

  Use when checking wallet security, reviewing approvals, or assessing risk exposure.

  Trigger with phrases like "audit wallet", "check approvals", "security scan", or
  "revoke tokens".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(crypto:wallet-*)
version: 1.18.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- crypto
- security
- audit
compatibility: Designed for Claude Code
---
# Wallet Security Auditor

## Overview

Security analysis tool for cryptocurrency wallets. Scans ERC20 token approvals, analyzes transaction patterns, calculates security risk scores, and provides actionable recommendations to improve wallet security.

**Important**: This is a read-only analysis tool. It does NOT execute transactions, manage private keys, or perform revocations.

## Prerequisites

Before using this skill, ensure you have:

- Python 3.8+ with `requests` library installed
- Optional: `ETHERSCAN_API_KEY` environment variable for higher rate limits
- Network access to blockchain RPC endpoints (public RPCs included)
- Target wallet address (hex format, 0x...)

## Instructions

### 1. List Token Approvals

Scan wallet for all active ERC20 token approvals:

```text
cd ${CLAUDE_SKILL_DIR}/scripts
python wallet_auditor.py approvals <address> --chain <chain>
```

Options:

1. `--chain`: ethereum, bsc, polygon, arbitrum, optimism, base (default: ethereum)
2. `--unlimited`: Show only unlimited approvals
3. `--verbose`: Detailed output

### 2. Full Security Scan

Comprehensive security analysis including approvals, transaction history, and patterns:

```bash
python wallet_auditor.py scan <address> --verbose
```

Analyzes:
4. Active token approvals (unlimited, risky)
5. Transaction history patterns
6. Contract interactions (verified vs unverified)
7. Suspicious activity detection

### 3. Calculate Security Score

Get weighted security risk score (0-100, higher = safer):

```text
python wallet_auditor.py score <address>
python wallet_auditor.py score <address> --json  # JSON output
```

Score components:
8. Approvals (40%): Unlimited, risky, stale approvals
9. Interactions (30%): Contract verification, flagged addresses
10. Patterns (20%): Transaction frequency, diversity
11. Age (10%): Wallet maturity

Risk levels:
12. 90-100: SAFE
13. 70-89: LOW
14. 50-69: MEDIUM
15. 30-49: HIGH
16. 0-29: CRITICAL

### 4. Analyze Transaction History

Review recent contract interactions and patterns:

```bash
python wallet_auditor.py history <address> --days 30
```

Detects:
17. Rapid approval patterns
18. Interaction bursts (many contracts in short time)
19. High failure rates
20. Dust attacks

### 5. Generate Revoke List

Get prioritized list of approvals to revoke:

```text
python wallet_auditor.py revoke-list <address>
```

Flags:
21. Unlimited approvals to unknown contracts
22. Risky/flagged spenders
23. Stale approvals (>6 months)

### 6. Generate Full Report

Create comprehensive security audit report:

```bash
python wallet_auditor.py report <address> --output report.txt
python wallet_auditor.py report <address> --json  # JSON format
```

### 7. List Supported Chains

```bash
python wallet_auditor.py chains
```

## Output

### Security Score Report

```
╔═══════════════════════════════════════════════════════════════════╗
║                    WALLET SECURITY SCORE                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  Overall Score:  [████████████████····] 82/100                    ║
║  Risk Level:     🟢 LOW                                           ║
╠═══════════════════════════════════════════════════════════════════╣
║  Component Scores:                                                ║
║    Approvals:     [██████████████······] 70/100                   ║
║    Interactions:  [██████████████████··] 90/100                   ║
║    Patterns:      [████████████████████] 100/100                  ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Approval Summary

- Total active approvals count
- Unlimited approvals flagged
- Risky approvals with severity
- Unique spenders and tokens

### Risk Factors

- [CRITICAL] Unlimited approval to unknown contract
- [HIGH] Approval to flagged contract
- [MEDIUM] Many unlimited approvals (>5)
- [LOW] Interaction with unverified contract

### Recommendations

- Priority 1: Revoke risky approvals immediately
- Priority 2: Review unnecessary unlimited approvals
- Priority 3: Audit all approvals periodically

## Error Handling

See [`references/errors.md`](references/errors.md) for comprehensive error handling:

| Error | Cause | Solution |
|-------|-------|----------|
| Address validation failed | Invalid format | Use 0x + 40 hex characters |
| RPC timeout | Node unresponsive | Retry or use different RPC |
| Rate limited | Too many requests | Add ETHERSCAN_API_KEY |
| No approvals found | Wallet clean | Normal - no action needed |

## Examples

See [`references/examples.md`](references/examples.md) for detailed examples.

### Quick Security Check

```bash
# Check wallet approvals
python wallet_auditor.py approvals 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Full security scan
python wallet_auditor.py scan 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --verbose

# Get security score
python wallet_auditor.py score 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Check other chains
python wallet_auditor.py approvals 0x... --chain polygon
python wallet_auditor.py approvals 0x... --chain arbitrum
```

### Generate Audit Report

```bash
# Text report
python wallet_auditor.py report 0x... --output security_audit.txt

# JSON for integration
python wallet_auditor.py report 0x... --json --output audit.json
```

## Resources

- **revoke.cash**: Web UI for revoking approvals
- **Etherscan Token Approval Checker**: View/revoke on block explorer
- **Etherscan API**: https://docs.etherscan.io/api-endpoints
- **ERC20 Approval Event**: Topic `0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925`
- **GoPlus Security API**: Additional contract risk data
