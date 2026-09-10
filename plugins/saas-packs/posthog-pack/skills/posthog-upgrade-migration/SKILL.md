---
name: posthog-upgrade-migration
description: |
  Upgrade PostHog SDKs through release-note review, configuration-default comparison, focused tests, canary evidence, and rollback. Use when changing a PostHog package version or defaults date. Trigger with "upgrade PostHog SDK", "PostHog breaking change", or "PostHog version migration".
argument-hint: "[project-path] [target-version]"
allowed-tools: Read, Write, Edit, Grep, Bash(npm:*), Bash(npx:*), Bash(git:*), Bash(pip:*), Bash(pip3:*), Bash(grep:*)
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- api
- migration
compatibility: Designed for Claude Code
---
# PostHog Upgrade & Migration

## Overview

Upgrade PostHog SDKs from the versions actually locked by the target project to explicit target versions. Build the change list from current release notes and type surfaces, then prove capture, identity, consent, flags, flushing, and rollback behavior in the environments the application uses.

## Prerequisites

- PostHog SDK currently installed
- Git for branching
- Test suite covering PostHog integration
- Staging environment for validation

## Instructions

### Tool discipline

Use `Read` and `Grep` to inspect manifests, lockfiles, initialization, and release-sensitive options before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass. Use `npm`, `npx`, `pip`, and `git` Bash commands only in the selected project and preserve the recorded rollback versions.

### Step 1: Audit Current Versions

```bash
set -euo pipefail
# Check installed versions
echo "=== posthog-js ==="
npm list posthog-js 2>/dev/null || echo "Not installed"
echo "=== posthog-node ==="
npm list posthog-node 2>/dev/null || echo "Not installed"
echo "=== Python posthog ==="
pip3 show posthog 2>/dev/null | grep Version || echo "Not installed"

# Check latest available versions
echo "=== Latest available ==="
npm view posthog-js version 2>/dev/null
npm view posthog-node version 2>/dev/null
```

### Step 2: Build the Version Delta

Read every release note between the locked and target versions, plus the current SDK reference for each configured option. Produce a small evidence table with: package, locked version, target version, runtime requirement, changed default or API, affected source locations, required test, and rollback version. Pay particular attention to browser `defaults` dates, autocapture and persistence, consent, replay, server flush semantics, feature-flag evaluation, and whether events attach flag properties. Do not infer compatibility from a major-version number or a remembered migration note.

### Step 3: Upgrade Procedure

```bash
set -euo pipefail
# Create upgrade branch
git checkout -b upgrade/posthog-sdks

: "${POSTHOG_NODE_TARGET:?Set the reviewed posthog-node target version}"
: "${POSTHOG_JS_TARGET:?Set the reviewed posthog-js target version}"

# Install the exact reviewed versions and let the lockfile record them.
npm install "posthog-node@$POSTHOG_NODE_TARGET" "posthog-js@$POSTHOG_JS_TARGET"
# Check for type errors
npx tsc --noEmit 2>&1 | grep -i posthog || echo "No PostHog type errors"

# Run tests
npm test

# If Python
pip install --upgrade posthog
```

### Step 4: Search for Deprecated Patterns

```bash
set -euo pipefail
# Find files using PostHog
grep -rn "posthog\|PostHog" --include="*.ts" --include="*.tsx" --include="*.js" src/ | \
  grep -v node_modules | grep -v ".d.ts"

# Check for patterns that may need updating
echo "=== Checking for deprecated patterns ==="

# Direct API key in code (should be env var)
grep -rn "phc_\|phx_" --include="*.ts" --include="*.tsx" src/ && \
  echo "WARNING: Hardcoded API key found" || echo "No hardcoded keys"

# Inventory options whose behavior must be checked against the target release.
grep -rn "defaults\|autocapture\|before_send\|sendFeatureFlags\|personalApiKey\|flushAt\|flushInterval" \
  --include="*.ts" --include="*.tsx" --include="*.js" src/ || true
```

### Step 5: Validate in Staging

```typescript
// Post-upgrade validation script
import { PostHog } from 'posthog-node';

async function validateUpgrade() {
  const ph = new PostHog(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
    host: 'https://us.i.posthog.com',
    personalApiKey: process.env.POSTHOG_FEATURE_FLAGS_SECURE_API_KEY,
  });

  const checks = {
    capture: false,
    flags: false,
    identify: false,
  };

  try {
    // Test capture
    ph.capture({ distinctId: 'upgrade-test', event: 'sdk_upgrade_validated' });
    checks.capture = true;

    // Test feature flags
    const flags = await ph.getAllFlags('upgrade-test');
    checks.flags = typeof flags === 'object';

    // Test identify
    ph.identify({ distinctId: 'upgrade-test', properties: { upgraded: true } });
    checks.identify = true;

    await ph.flush();
  } catch (error) {
    console.error('Validation failed:', error);
  } finally {
    await ph.shutdown();
  }

  console.log('Upgrade validation:', checks);
  const allPassed = Object.values(checks).every(Boolean);
  process.exit(allPassed ? 0 : 1);
}

validateUpgrade();
```

### Step 6: Rollback if Needed

```bash
set -euo pipefail
: "${POSTHOG_NODE_PREVIOUS:?Set the previously locked posthog-node version}"
: "${POSTHOG_JS_PREVIOUS:?Set the previously locked posthog-js version}"
npm install "posthog-node@$POSTHOG_NODE_PREVIOUS" "posthog-js@$POSTHOG_JS_PREVIOUS" --save-exact

# Verify rollback
npm test
```

## Upgrade Evidence

Attach the completed version-delta table, dependency and lockfile diff, focused test output, staging event/flag evidence, canary window, observed ingestion warnings, and exact rollback commands. If any behavior cannot be confirmed from current official documentation or a controlled test, stop and record it as unresolved rather than guessing.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Type errors after upgrade | API changed | Check changelog, update types |
| Flags differ after upgrade | Changed evaluation or event-enrichment behavior | Compare release notes, targeting context, and controlled flag tests |
| Autocapture differs after upgrade | Changed default or configuration interpretation | Compare the chosen `defaults` date and emitted event sample |
| Test failures | Mock structure changed | Update mocks to match new SDK exports |

## Output

- Upgraded PostHog SDK to the explicit reviewed target version
- Deprecated patterns identified and fixed
- All tests passing with new version
- Rollback procedure documented

## Examples

For a `posthog-js` upgrade, record the current and target versions, compare the configured `defaults` date and changed options, run capture, identity, flag, consent, and replay tests, then canary with a reversible version pin. Never infer compatibility from a stale hard-coded major-version table.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [posthog-node Changelog](https://github.com/PostHog/posthog-node/releases)
- [posthog-js Changelog](https://github.com/PostHog/posthog-js/releases)
- [PostHog Migration Guides](https://posthog.com/docs/migrate)

## Next Steps

For CI integration during upgrades, see `posthog-ci-integration`.
