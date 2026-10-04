# Error Capture Pitfalls

## Pitfall 4: `beforeSend` Accidentally Returning `null`

`beforeSend` must return `event` to send or `null` to drop. Missing return statements cause JavaScript to return `undefined`, which Sentry treats as "drop."

```typescript
// WRONG — non-error events silently vanish
Sentry.init({
  beforeSend(event) {
    if (event.level === 'error') {
      return event;
    }
    // No return — warnings, info, fatal all dropped
  },
});

// RIGHT — always return event as final statement
Sentry.init({
  beforeSend(event, hint) {
    const error = hint?.originalException;
    if (error instanceof Error && error.message.match(/^NetworkError/)) {
      return null;  // Explicit drop
    }
    return event;  // Always the last line
  },
});
```

## Pitfall 6: Capturing Errors Without Re-Throwing

Catching errors, sending to Sentry, but not re-throwing causes cascading `undefined` failures downstream.

```typescript
// WRONG — error swallowed, returns undefined
async function getUser(id: string) {
  try {
    return await fetch(`/api/users/${id}`).then(r => r.json());
  } catch (error) {
    Sentry.captureException(error);
    // Returns undefined — callers break silently
  }
}

// RIGHT — capture and re-throw
async function getUser(id: string) {
  try {
    return await fetch(`/api/users/${id}`).then(r => r.json());
  } catch (error) {
    Sentry.captureException(error);
    throw error;  // Let caller handle it
  }
}
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
