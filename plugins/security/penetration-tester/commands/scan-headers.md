---
name: scan-headers
description: Quick security header check for a single URL
shortcut: sh
---

# Quick Security Header Scan

Fast single-URL check for HTTP security headers. This is a shortcut for running
just the header analysis from the full pentest workflow.

## Usage

Ask the user for the target URL, then run:

Complete the approved ROE and scope gates first; legacy CLIs do not perform
that validation themselves. Preserve exit 2 as incomplete and exit 1 as a finding.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/security_scanner.py TARGET_URL --checks headers
```

## What Gets Checked

- Content-Security-Policy (CSP)
- Strict-Transport-Security (HSTS)
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- Server version disclosure
- X-XSS-Protection (deprecated, informational)

## Output

Present the results as a table showing each header, whether it's present, its
value, and any issues found. Include the overall header security score.

For any missing or misconfigured headers, provide the recommended value and
a brief explanation of what it protects against. Reference
`references/SECURITY_HEADERS.md` for implementation details.

## Authorization

Even though this only sends a single GET request, confirm the user has
authorization to test the target URL before scanning.
