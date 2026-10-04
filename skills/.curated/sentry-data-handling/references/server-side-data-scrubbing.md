# Server-Side Data Scrubbing

## Server-Side Data Scrubbing

### Sentry Dashboard Settings

1. Project Settings → Security & Privacy
2. Enable "Data Scrubber"
3. Configure scrubbing rules:
   - Default fields (passwords, tokens, etc.)
   - Custom field patterns
   - IP address anonymization

### Advanced Data Scrubbing Rules

```json
{
  "applications": {
    "scrubData": true,
    "scrubDefaults": true,
    "sensitiveFields": [
      "password",
      "secret",
      "token",
      "apiKey",
      "ssn"
    ],
    "safeFields": [
      "username",
      "email_domain"
    ],
    "scrubIpAddresses": true
  }
}
```
