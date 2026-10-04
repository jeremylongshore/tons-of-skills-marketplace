# Testing After Upgrade

## Post-Upgrade Verification Checklist

Run this checklist after every Sentry SDK major version upgrade.

### 1. Version Confirmation

```bash
# JavaScript — verify all packages aligned
npm ls 2>/dev/null | command grep "@sentry/" | sort

# Python — verify version
python -c "import sentry_sdk; print(sentry_sdk.VERSION)"
```

### 2. Runtime Verification Script (JavaScript v8)

```typescript
// test-upgrade.mjs — run with: node --import ./instrument.mjs test-upgrade.mjs
import * as Sentry from '@sentry/node';

async function runVerification() {
  const results: Record<string, string> = {};

  // Check 1: SDK version
  results['SDK Version'] = Sentry.SDK_VERSION;
  console.log(`SDK Version: ${Sentry.SDK_VERSION}`);

  // Check 2: Error capture
  try {
    throw new Error('Upgrade verification error');
  } catch (e) {
    const eventId = Sentry.captureException(e);
    results['Error Capture'] = eventId ? 'PASS' : 'FAIL';
    console.log(`Error Capture: ${results['Error Capture']}`);
  }

  // Check 3: Message capture
  const msgId = Sentry.captureMessage('Upgrade verification message', 'info');
  results['Message Capture'] = msgId ? 'PASS' : 'FAIL';
  console.log(`Message Capture: ${results['Message Capture']}`);

  // Check 4: Scoped context (v8 API)
  Sentry.withScope((scope) => {
    scope.setTag('test', 'upgrade-verify');
    scope.setUser({ id: 'test-user', email: 'test@example.com' });
    scope.setExtra('verification_time', new Date().toISOString());
    Sentry.captureMessage('Scoped context test');
  });
  results['Scoped Context'] = 'PASS';
  console.log(`Scoped Context: ${results['Scoped Context']}`);

  // Check 5: Performance spans (v8 API — replaces startTransaction)
  await Sentry.startSpan(
    { name: 'upgrade-verification', op: 'test' },
    async (rootSpan) => {
      // Nested child span
      await Sentry.startSpan(
        { name: 'child-operation', op: 'test.child' },
        async (childSpan) => {
          childSpan.setAttribute('test.key', 'test-value');
          await new Promise((r) => setTimeout(r, 50));
        }
      );
      results['Performance Spans'] = rootSpan ? 'PASS' : 'FAIL';
      console.log(`Performance Spans: ${results['Performance Spans']}`);
    }
  );

  // Check 6: Breadcrumbs
  Sentry.addBreadcrumb({
    category: 'test',
    message: 'Upgrade verification breadcrumb',
    level: 'info',
    data: { step: 'verification' },
  });
  results['Breadcrumbs'] = 'PASS';
  console.log(`Breadcrumbs: ${results['Breadcrumbs']}`);

  // Check 7: Flush (verify events delivered)
  const flushed = await Sentry.flush(5000);
  results['Event Flush'] = flushed ? 'PASS' : 'FAIL';
  console.log(`Event Flush: ${results['Event Flush']}`);

  // Summary
  const failures = Object.entries(results).filter(([, v]) => v === 'FAIL');
  if (failures.length === 0) {
    console.log('\nAll checks passed. Upgrade verified.');
  } else {
    console.log(`\n${failures.length} check(s) failed:`);
    failures.forEach(([k]) => console.log(`  - ${k}`));
  }
}

runVerification();
```

### 3. Python Verification Script (v2)

```python
# test_upgrade.py
import sentry_sdk

def run_verification():
    results = {}

    # Check 1: SDK version
    print(f"SDK Version: {sentry_sdk.VERSION}")
    results['SDK Version'] = sentry_sdk.VERSION

    # Check 2: Error capture
    try:
        raise ValueError("Upgrade verification error")
    except Exception as e:
        event_id = sentry_sdk.capture_exception(e)
        results['Error Capture'] = 'PASS' if event_id else 'FAIL'
        print(f"Error Capture: {results['Error Capture']}")

    # Check 3: Scope API (v2)
    scope = sentry_sdk.get_current_scope()
    scope.set_tag("test", "upgrade-verify")
    scope.set_user({"id": "test-user"})
    results['Scope API'] = 'PASS'
    print(f"Scope API: {results['Scope API']}")

    # Check 4: New scope context manager (v2)
    with sentry_sdk.new_scope() as scope:
        scope.set_extra("verification", True)
        sentry_sdk.capture_message("Scoped verification test")
    results['New Scope'] = 'PASS'
    print(f"New Scope: {results['New Scope']}")

    # Check 5: Breadcrumbs
    sentry_sdk.add_breadcrumb(
        category="test",
        message="Upgrade verification",
        level="info",
    )
    results['Breadcrumbs'] = 'PASS'
    print(f"Breadcrumbs: {results['Breadcrumbs']}")

    # Check 6: Flush
    sentry_sdk.flush(timeout=5)
    results['Flush'] = 'PASS'
    print(f"Flush: {results['Flush']}")

    failures = [k for k, v in results.items() if v == 'FAIL']
    if not failures:
        print("\nAll checks passed. Upgrade verified.")
    else:
        print(f"\n{len(failures)} check(s) failed: {', '.join(failures)}")

if __name__ == "__main__":
    run_verification()
```

### 4. Dashboard Verification

After running verification scripts, check in Sentry dashboard:

1. **Issues page** — "Upgrade verification error" should appear
2. **Performance page** — "upgrade-verification" trace should appear with child span
3. **Release page** — new release associated with upgraded SDK version
4. **Source maps** — click into an error, verify stack traces resolve to source code
5. **Breadcrumbs** — expand an event, verify breadcrumb trail includes "Upgrade verification"

### 5. Integration-Specific Checks

| Integration | What to Verify |
|-------------|---------------|
| Express/Fastify | Routes auto-instrumented, error handler catches thrown errors |
| React | Error boundary captures component errors, React Router spans appear |
| Database (Prisma/Knex) | DB query spans appear in traces with query descriptions |
| HTTP client (Axios/fetch) | Outgoing HTTP spans appear, `sentry-trace` header propagated |
| Cron/Queue | Scheduled job spans appear, queue consumer spans tracked |

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
