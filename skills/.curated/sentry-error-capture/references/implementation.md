## Implementation Guide

### Step 1: Basic Error Capture

```typescript
import * as Sentry from '@sentry/node';

try {
  await riskyOperation();
} catch (error) {
  const eventId = Sentry.captureException(error);
  console.log(`Error tracked: ${eventId}`);
}
```

### Step 2: Add User Context

```typescript
// Set user for all subsequent errors
Sentry.setUser({
  id: user.id,
  email: user.email,
  username: user.username,
  ip_address: request.ip,
});

// Clear user on logout
Sentry.setUser(null);
```

### Step 3: Add Tags and Extra Data

```typescript
// Tags for filtering
Sentry.setTag('feature', 'checkout');
Sentry.setTag('tenant', tenantId);

// Extra context data
Sentry.setExtra('cart_items', cart.items.length);
Sentry.setExtra('total_amount', cart.total);
```

### Step 4: Contextual Capture

```typescript
Sentry.captureException(error, {
  level: 'error',
  tags: {
    operation: 'payment',
    provider: 'stripe',
  },
  extra: {
    orderId: order.id,
    amount: order.total,
    currency: order.currency,
  },
  user: {
    id: customer.id,
    email: customer.email,
  },
});
```

### Step 5: Custom Fingerprinting

```typescript
Sentry.captureException(error, {
  fingerprint: [
    '{{ default }}',
    String(error.code),
    endpoint,
  ],
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
