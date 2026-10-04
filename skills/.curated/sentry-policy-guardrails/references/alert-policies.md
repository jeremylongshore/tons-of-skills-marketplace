# Alert Policies

## Alert Policies

### Standard Alert Template

```yaml
# Organization-wide alert standards
alert_policies:
  critical:
    name: "Critical Error Rate"
    conditions:
      - event_frequency > 100 per hour
    actions:
      - pagerduty: critical-oncall
      - slack: "#incidents"
    required: true  # Teams cannot disable

  high_error_rate:
    name: "High Error Rate"
    conditions:
      - error_rate > 5%
    actions:
      - slack: team-channel  # Team configures channel
    required: true

  new_issue:
    name: "New Issue Notification"
    conditions:
      - is:unresolved is:new
    actions:
      - slack: team-channel
    required: false  # Optional
```

### Alert Configuration Validation

```typescript
// Validate team alert configurations
interface AlertConfig {
  name: string;
  conditions: string[];
  actions: string[];
}

function validateAlertConfig(config: AlertConfig): string[] {
  const errors: string[] = [];

  // Required alerts must exist
  const requiredAlerts = ['Critical Error Rate', 'High Error Rate'];
  for (const required of requiredAlerts) {
    if (config.name === required && config.actions.length === 0) {
      errors.push(`Required alert "${required}" must have actions configured`);
    }
  }

  // PagerDuty required for critical
  if (config.name.includes('Critical') && !config.actions.some(a => a.includes('pagerduty'))) {
    errors.push('Critical alerts must include PagerDuty action');
  }

  return errors;
}
```
