# Error Handling Architecture

## Error Handling Architecture

### Global Error Handler

```typescript
// middleware/errorHandler.ts
import { Sentry } from '@mycompany/shared/sentry';

export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  // Capture in Sentry
  Sentry.withScope((scope) => {
    scope.setTag('endpoint', req.path);
    scope.setTag('method', req.method);
    scope.setUser({ ip_address: req.ip });
    scope.setExtra('query', req.query);
    Sentry.captureException(error);
  });

  // Respond to client
  res.status(500).json({
    error: 'Internal server error',
    requestId: res.sentry, // Sentry event ID
  });
}
```

### Domain-Specific Handlers

```typescript
// errors/PaymentError.ts
export class PaymentError extends Error {
  constructor(
    message: string,
    public code: string,
    public provider: string,
    public transactionId?: string
  ) {
    super(message);
    this.name = 'PaymentError';
  }
}

// When caught
if (error instanceof PaymentError) {
  Sentry.withScope((scope) => {
    scope.setTag('error_type', 'payment');
    scope.setTag('payment_provider', error.provider);
    scope.setExtra('transaction_id', error.transactionId);
    Sentry.captureException(error);
  });
}
```
