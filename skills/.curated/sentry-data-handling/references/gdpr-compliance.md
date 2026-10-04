# Gdpr Compliance

## GDPR Compliance

### Right to Erasure (Delete User Data)

```bash
# Delete all events for a user
curl -X DELETE \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$ORG/$PROJECT/users/$USER_ID/"
```

### Programmatic User Data Deletion

```typescript
async function deleteUserData(userId: string) {
  const response = await fetch(
    `https://sentry.io/api/0/projects/${ORG}/${PROJECT}/users/${userId}/`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${SENTRY_AUTH_TOKEN}`,
      },
    }
  );
  return response.ok;
}
```

### User Consent Handling

```typescript
function initSentryWithConsent(hasConsent: boolean) {
  Sentry.init({
    dsn: hasConsent ? process.env.SENTRY_DSN : undefined,

    // Don't send any PII
    sendDefaultPii: false,

    // Anonymize user
    beforeSend(event) {
      if (event.user) {
        event.user = {
          id: hashUserId(event.user.id), // Pseudonymized ID
          // Remove all other user fields
        };
      }
      return event;
    },
  });
}
```
