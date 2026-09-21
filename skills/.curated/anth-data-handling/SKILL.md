---
name: anth-data-handling
description: 'Implement data privacy, PII handling, and compliance patterns for Claude
  API.

  Use when handling sensitive data, implementing PII redaction,

  or configuring data retention for GDPR/CCPA compliance with Claude.

  Trigger with phrases like "anthropic data privacy", "claude PII",

  "anthropic gdpr", "claude data handling", "redact data claude".

  '
allowed-tools: Read, Write, Edit, Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic Data Handling

## Overview

Anthropic's data policies: API inputs/outputs are NOT used for model training (commercial API). Zero-day retention is available. This skill covers PII redaction before sending to Claude and compliance patterns.

## Anthropic Data Policies

| Policy | Details |
|--------|---------|
| Training data | API data is NOT used for training (commercial API) |
| Data retention | 30-day default; 0-day available via agreement |
| Encryption | TLS 1.2+ in transit, AES-256 at rest |
| SOC 2 Type II | Certified |
| HIPAA BAA | Available for eligible customers |

## PII Redaction Before API Calls

```python
import re
import anthropic

def redact_pii(text: str) -> tuple[str, dict]:
    """Redact PII before sending to Claude, return redaction map for restoration."""
    redaction_map = {}
    patterns = [
        (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN', '[SSN-REDACTED-{}]'),
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL', '[EMAIL-REDACTED-{}]'),
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'PHONE', '[PHONE-REDACTED-{}]'),
        (r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', 'CARD', '[CARD-REDACTED-{}]'),
    ]

    counter = 0
    for pattern, label, replacement in patterns:
        for match in re.finditer(pattern, text):
            counter += 1
            placeholder = replacement.format(counter)
            redaction_map[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)

    return text, redaction_map

def restore_pii(text: str, redaction_map: dict) -> str:
    """Restore redacted PII in Claude's response."""
    for placeholder, original in redaction_map.items():
        text = text.replace(placeholder, original)
    return text

# Usage
user_input = "Contact John at john@example.com or 555-123-4567"
safe_input, redactions = redact_pii(user_input)
# safe_input: "Contact John at [EMAIL-REDACTED-1] or [PHONE-REDACTED-2]"

client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=256,
    messages=[{"role": "user", "content": safe_input}]
)
final_output = restore_pii(msg.content[0].text, redactions)
```

## Audit Logging

```python
import json
import logging
from datetime import datetime, timezone

audit_logger = logging.getLogger("claude.audit")

def audited_request(client, user_id: str, purpose: str, **kwargs):
    """Wrap Claude API calls with audit logging."""
    # Log request metadata (never log content)
    audit_logger.info(json.dumps({
        "event": "claude.request",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "purpose": purpose,
        "model": kwargs.get("model"),
        "max_tokens": kwargs.get("max_tokens"),
    }))

    response = client.messages.create(**kwargs)

    audit_logger.info(json.dumps({
        "event": "claude.response",
        "request_id": response._request_id,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
    }))

    return response
```

## Data Handling Checklist

- [ ] PII redacted before sending to Claude API
- [ ] Audit logs capture who accessed what and when
- [ ] Logs never contain message content or PII
- [ ] Data retention policy matches your compliance needs
- [ ] Zero-day retention enabled if required (contact Anthropic)
- [ ] HIPAA BAA in place if handling PHI
- [ ] User consent obtained for AI processing
- [ ] Data deletion procedures documented

## Error Handling

| Risk | Mitigation |
|------|------------|
| PII in prompts | Pre-call redaction pipeline |
| PII in responses | Post-call output scanning |
| Audit log gaps | Centralized logging with alerting |
| Data subject access request | Searchable audit trail by user_id |

## Prerequisites

- Define the data classification, processing purpose, legal basis or user consent, and retention owner before sending anything to the API.
- Provide an approved redaction policy, a secret-manager-backed API credential, and an allowlisted Anthropic workspace or service boundary.
- Prepare synthetic fixtures that exercise each PII class and a deletion test; do not use real customer records while validating the pipeline.

## Instructions

1. Classify the input and reject fields outside the approved purpose or destination. Apply deterministic redaction before constructing the request; keep any restoration map encrypted, access-controlled, and short-lived.
2. Run the redaction, prompt, and response scanners against synthetic fixtures. A failed scan, missing consent, or unexpected content block is a hard stop; do not retry with the original data.
3. Call the Messages API with the least-privileged credential and only the approved model, workspace, and retention configuration. Do not place prompts, responses, redaction maps, or secrets in logs, traces, metrics, or exception text.
4. Scan the response before restoration or release. Record only aggregate counts, policy decisions, request identifier, and token metadata, then enforce the documented retention and deletion procedure.
5. Verify deletion in the sandbox and retain a redacted audit receipt for the owner and compliance reviewer.

## Output

Produce a redacted data-handling receipt containing the purpose, policy version, environment, workspace class, redaction and response-scan outcomes, request identifier, token counts, retention deadline, deletion result, and reviewer. Exclude names, contact details, prompt/response text, raw identifiers, redaction maps, and credentials.

## Examples

For a synthetic fixture such as `customer_id=fixture-017; email=test@example.invalid; purpose=classification`, redact the email, call a sandbox workspace, assert `raw_pii_sent=0` and `sensitive_content_logged=0`, and emit `redaction=pass; output_scan=pass; retention=24h; deletion=verified`. Never substitute a real person or production record in this example.

## Resources

- [Anthropic Privacy Policy](https://www.anthropic.com/privacy)
- Anthropic Security
- Usage Policy

## Next Steps

For enterprise access control, see `anth-enterprise-rbac`.
