---
name: posthog-debug-bundle
description: |
  Collect a redacted, reproducible PostHog diagnostic bundle without capturing secrets or raw customer data. Use when an integration failure needs escalation or handoff. Trigger with "PostHog debug bundle", "collect PostHog evidence", or "PostHog support ticket".
argument-hint: "[project-path] [output-directory]"
allowed-tools: Read, Bash(grep:*), Bash(curl:*), Bash(tar:*), Grep
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- debugging
compatibility: Designed for Claude Code
---
# PostHog Debug Bundle

## Overview

Collect diagnostic evidence for PostHog support tickets. Gathers SDK versions, API connectivity, feature flag status, event flow verification, and redacted configuration. All secrets are automatically redacted.

## Prerequisites

- PostHog SDK installed in project
- Access to environment variables
- `curl` and `jq` available

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Grep` to locate initialization, capture, flag, and credential boundaries.

### Step 1: Run Full Diagnostic Script

```bash
#!/bin/bash
set -euo pipefail

BUNDLE_DIR="posthog-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE_DIR"

echo "=== PostHog Debug Bundle ===" > "$BUNDLE_DIR/summary.txt"
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$BUNDLE_DIR/summary.txt"
echo "" >> "$BUNDLE_DIR/summary.txt"

# --- Environment ---
echo "--- Runtime Environment ---" >> "$BUNDLE_DIR/summary.txt"
echo "Node: $(node --version 2>/dev/null || echo 'not found')" >> "$BUNDLE_DIR/summary.txt"
echo "npm: $(npm --version 2>/dev/null || echo 'not found')" >> "$BUNDLE_DIR/summary.txt"
echo "Python: $(python3 --version 2>/dev/null || echo 'not found')" >> "$BUNDLE_DIR/summary.txt"
echo "OS: $(uname -srm)" >> "$BUNDLE_DIR/summary.txt"
echo "" >> "$BUNDLE_DIR/summary.txt"

# --- SDK Versions ---
echo "--- PostHog SDK Versions ---" >> "$BUNDLE_DIR/summary.txt"
npm list posthog-js posthog-node 2>/dev/null >> "$BUNDLE_DIR/summary.txt" || echo "No npm PostHog packages" >> "$BUNDLE_DIR/summary.txt"
pip3 show posthog 2>/dev/null | grep -E "Name|Version" >> "$BUNDLE_DIR/summary.txt" || true
echo "" >> "$BUNDLE_DIR/summary.txt"

# --- API Connectivity ---
echo "--- API Connectivity ---" >> "$BUNDLE_DIR/summary.txt"
echo -n "US Cloud ingest: " >> "$BUNDLE_DIR/summary.txt"
curl -s -o /dev/null -w "%{http_code} (%{time_total}s)" https://us.i.posthog.com/healthz >> "$BUNDLE_DIR/summary.txt" 2>&1
echo "" >> "$BUNDLE_DIR/summary.txt"
echo -n "EU Cloud ingest: " >> "$BUNDLE_DIR/summary.txt"
curl -s -o /dev/null -w "%{http_code} (%{time_total}s)" https://eu.i.posthog.com/healthz >> "$BUNDLE_DIR/summary.txt" 2>&1
echo "" >> "$BUNDLE_DIR/summary.txt"
echo -n "App API: " >> "$BUNDLE_DIR/summary.txt"
curl -s -o /dev/null -w "%{http_code} (%{time_total}s)" https://us.posthog.com/api/ >> "$BUNDLE_DIR/summary.txt" 2>&1
echo "" >> "$BUNDLE_DIR/summary.txt"

# --- Environment Variables (redacted) ---
echo "" >> "$BUNDLE_DIR/summary.txt"
echo "--- Environment Variables (redacted) ---" >> "$BUNDLE_DIR/summary.txt"
env | grep -i posthog | sed 's/=.*/=***REDACTED***/' >> "$BUNDLE_DIR/summary.txt" 2>/dev/null || echo "No POSTHOG env vars found" >> "$BUNDLE_DIR/summary.txt"
echo "" >> "$BUNDLE_DIR/summary.txt"

# --- Key Type Detection ---
echo "--- API Key Types ---" >> "$BUNDLE_DIR/summary.txt"
if [ -n "${NEXT_PUBLIC_POSTHOG_KEY:-}" ]; then
  echo "Project key prefix: $(echo "$NEXT_PUBLIC_POSTHOG_KEY" | head -c 4)_..." >> "$BUNDLE_DIR/summary.txt"
fi
if [ -n "${POSTHOG_PERSONAL_API_KEY:-}" ]; then
  echo "Personal key prefix: $(echo "$POSTHOG_PERSONAL_API_KEY" | head -c 4)_..." >> "$BUNDLE_DIR/summary.txt"
fi

echo "" >> "$BUNDLE_DIR/summary.txt"
echo "Bundle complete: $BUNDLE_DIR/" >> "$BUNDLE_DIR/summary.txt"
```

### Step 2: Test Event Capture Flow Only When Approved

```bash
set -euo pipefail
: "${POSTHOG_WRITE_PROBE_APPROVED:?Set only after the incident commander approves a synthetic write}"
test "$POSTHOG_WRITE_PROBE_APPROVED" = "yes"
: "${POSTHOG_PUBLIC_HOST:?Set the project's regional ingestion host}"

# Send a named synthetic event and verify receipt. A 200 does not prove ingestion.
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$POSTHOG_PUBLIC_HOST/i/v0/e/" \
  -H 'Content-Type: application/json' \
  -d "{
    \"api_key\": \"${NEXT_PUBLIC_POSTHOG_KEY}\",
    \"event\": \"debug_bundle_test\",
    \"distinct_id\": \"debug-$(date +%s)\",
    \"properties\": {\"test\": true}
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

echo "Capture test: HTTP $HTTP_CODE"
echo "Response: $BODY"

# Inspect the response for quota_limited and verify the named event plus ingestion warnings.
```

### Step 3: Check Feature Flag Status

```bash
set -euo pipefail
# Evaluate flags via the current public endpoint.
curl -s -X POST "$POSTHOG_PUBLIC_HOST/flags?v=2" \
  -H 'Content-Type: application/json' \
  -d "{
    \"api_key\": \"${NEXT_PUBLIC_POSTHOG_KEY}\",
    \"distinct_id\": \"debug-test\"
  }" | jq '{
    flags: .flags,
    errorsParsingFlags: .errorsParsingFlags
  }'
```

### Step 4: Verify Admin API Access

```bash
set -euo pipefail
# Test personal API key (if available)
if [ -n "${POSTHOG_PERSONAL_API_KEY:-}" ]; then
  curl -s "https://us.posthog.com/api/projects/" \
    -H "Authorization: Bearer $POSTHOG_PERSONAL_API_KEY" | \
    jq '[.[] | {id, name, created_at}]' > "$BUNDLE_DIR/projects.json" 2>/dev/null || \
    echo "Personal API key failed" >> "$BUNDLE_DIR/summary.txt"
fi
```

### Step 5: Package and Review

```bash
set -euo pipefail
# Review for any accidentally included secrets
grep -rn "phc_\|phx_\|Bearer " "$BUNDLE_DIR/" | grep -v REDACTED | grep -v "prefix:" && \
  echo "WARNING: Potential secret found — review before sharing" || \
  echo "No secrets detected in bundle"

# Package
tar -czf "$BUNDLE_DIR.tar.gz" "$BUNDLE_DIR"
echo "Bundle created: $BUNDLE_DIR.tar.gz ($(du -h "$BUNDLE_DIR.tar.gz" | cut -f1))"
```

## Checklist

| Item | Collected | Purpose |
|------|-----------|---------|
| Node/Python versions | Yes | SDK compatibility |
| PostHog SDK versions | Yes | Version-specific bugs |
| API connectivity | Yes | Network/firewall issues |
| Event capture test | Yes | End-to-end verification |
| Feature flag status | Yes | Flag evaluation issues |
| Environment vars (redacted) | Yes | Configuration problems |
| Key type detection | Yes | Wrong key type errors |

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| All connectivity fails | Corporate firewall | Check proxy settings, try VPN |
| Capture returns non-200 | Invalid API key | Verify `phc_` key in project settings |
| `/flags` fails | Key/host mismatch | Ensure the project token matches the selected host region |
| Personal API 401 | Expired key | Regenerate in Settings > Personal API Keys |

## Output

- `posthog-debug-YYYYMMDD-HHMMSS.tar.gz` archive containing:
  - `summary.txt` — Runtime, SDK versions, connectivity, redacted config
  - `projects.json` — Project list (if personal key available)
  - Test event capture and flag evaluation results

## Examples

For delayed server events, record SDK versions, configured region, sanitized option names, connectivity status, queue lifecycle, and a bounded log excerpt. Before packaging, scan the bundle for project secrets, personal keys, authorization headers, emails, and event payloads.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Status Page](https://status.posthog.com)
- [PostHog Support](https://posthog.com/docs/support)
- [PostHog API Overview](https://posthog.com/docs/api)

## Next Steps

For rate limit issues, see `posthog-rate-limits`.
