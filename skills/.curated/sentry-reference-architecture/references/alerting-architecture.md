# Alerting Architecture

## Alerting Architecture

### Alert Hierarchy

```
Critical (Page immediately)
├── Error rate > 10% (5 min)
├── P0 issue detected
└── Service down

Warning (Slack notification)
├── Error rate > 5%
├── New error type
└── Performance degradation

Info (Daily digest)
├── Resolved issues
├── Release health
└── Trend reports
```

### Issue Routing

```yaml
# Alert rules by team
backend-team:
  - path:match("/api/*")
  - tag:service IN [user-service, payment-service]

frontend-team:
  - platform:javascript
  - tag:service = web-frontend

devops-team:
  - tag:category = infrastructure
  - level:fatal
```
