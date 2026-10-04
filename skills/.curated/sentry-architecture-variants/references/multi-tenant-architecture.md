# Multi-Tenant Architecture — Sentry Deep Dive

## Single Project with Tenant Tags

For most SaaS apps, one Sentry project with per-tenant tagging is sufficient.

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 0.1,

  beforeSend(event) {
    // Strip tenant-specific PII from all events
    if (event.request?.data) {
      event.request.data = '[Filtered]';
    }
    return event;
  },
});

// Middleware: set tenant context per request using withScope
app.use((req, res, next) => {
  const tenantId = req.headers['x-tenant-id'] || 'unknown';

  Sentry.withScope((scope) => {
    scope.setTag('tenant_id', tenantId);
    scope.setTag('tenant_plan', getTenantPlan(tenantId));  // 'free', 'pro', 'enterprise'
    scope.setUser({ id: `tenant:${tenantId}` });           // tenant, not individual user
    next();
  });
});

// Filter by tenant in Sentry dashboard:
// Issues → Search: tags.tenant_id:acme-corp
// Performance → Search: tags.tenant_plan:enterprise
```

## Per-Tenant Projects (Enterprise Scale)

For regulated industries or large enterprise clients requiring data isolation:

```
Organization: mycompany
├── Project: platform-shared      # Platform-level errors
├── Project: tenant-acme          # ACME Corp errors
├── Project: tenant-globex        # Globex errors
└── Project: tenant-initech       # Initech errors
```

```typescript
// Dynamic DSN routing per tenant
const tenantDSNs: Record<string, string> = {
  'acme': 'https://abc@sentry.io/1',
  'globex': 'https://def@sentry.io/2',
  'default': process.env.SENTRY_DSN!,
};

// Initialize with default DSN, route events per tenant
Sentry.init({
  dsn: tenantDSNs.default,
  beforeSend(event) {
    const tenantId = event.tags?.tenant_id;
    if (tenantId && tenantDSNs[tenantId]) {
      // Route to tenant-specific project
      event.dsn = tenantDSNs[tenantId];
    }
    return event;
  },
});
```

## Scope Isolation Warning

**Never use `Sentry.setTag()` at the global level for tenant data.** Global tags persist across requests in Node.js (shared process), causing tenant data to leak between requests.

```typescript
// WRONG — leaks between requests
app.use((req, res, next) => {
  Sentry.setTag('tenant_id', req.tenantId);  // global scope!
  next();
});

// CORRECT — isolated per request
app.use((req, res, next) => {
  Sentry.withScope((scope) => {
    scope.setTag('tenant_id', req.tenantId);  // scoped to this request
    next();
  });
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
