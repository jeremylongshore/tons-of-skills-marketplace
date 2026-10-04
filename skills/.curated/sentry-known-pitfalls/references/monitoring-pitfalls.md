# Monitoring Pitfalls

## Pitfall 10: Not Setting Up Alerts

Sentry collects errors but does not notify anyone by default. Without alert rules, critical production bugs go unnoticed for hours or days.

**Three-tier alert structure:**

```yaml
# Tier 1 — Immediate (PagerDuty)
# Trigger: New fatal/error issue in production
# Action: PagerDuty page

# Tier 2 — Urgent (Slack)
# Trigger: Error rate > 100 events in 5 minutes
# Action: Post to #sentry-alerts

# Tier 3 — Awareness (Email)
# Trigger: Issue unresolved > 7 days
# Action: Weekly digest email
```

**API-based alert creation:**

```bash
curl -X POST "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/rules/" \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Error Spike",
    "conditions": [{
      "id": "sentry.rules.conditions.event_frequency.EventFrequencyCondition",
      "value": 100, "interval": "5m"
    }],
    "actions": [{
      "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
      "channel": "#sentry-alerts"
    }],
    "environment": "production"
  }'
```

**Verify alerts work:**

```typescript
Sentry.captureException(new Error('[TEST] Alert verification'));
await Sentry.flush(5000);
// Check Slack/PagerDuty within 5 minutes, then resolve in Sentry UI
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
