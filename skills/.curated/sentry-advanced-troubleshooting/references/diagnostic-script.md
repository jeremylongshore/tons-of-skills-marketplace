# Diagnostic Script

## Diagnostic Script

```typescript
// diagnostic.ts - Run to check Sentry health
import * as Sentry from '@sentry/node';

async function runDiagnostics() {
  console.log('=== Sentry Diagnostics ===\n');

  // Check 1: Environment
  console.log('1. Environment');
  console.log('   DSN set:', !!process.env.SENTRY_DSN);
  console.log('   Environment:', process.env.NODE_ENV);

  // Check 2: Client
  const client = Sentry.getCurrentHub().getClient();
  console.log('\n2. Client');
  console.log('   Initialized:', !!client);
  console.log('   DSN:', client?.getDsn()?.toString() || 'N/A');

  // Check 3: Test capture
  console.log('\n3. Test Capture');
  const eventId = Sentry.captureMessage('Diagnostic test');
  console.log('   Event ID:', eventId);

  // Check 4: Flush
  console.log('\n4. Flushing...');
  const flushed = await Sentry.flush(5000);
  console.log('   Flushed:', flushed);

  console.log('\n=== Complete ===');
}

runDiagnostics();
```
