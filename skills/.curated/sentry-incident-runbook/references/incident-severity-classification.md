# Incident Severity Classification

## Incident Severity Classification

### P0 - Critical

- **Definition:** Complete service outage, data loss risk
- **Sentry Indicators:**
  - Error rate > 50%
  - Fatal errors affecting all users
  - Database connection failures
- **Response Time:** Immediate (< 5 minutes)

### P1 - High

- **Definition:** Major feature broken, significant user impact
- **Sentry Indicators:**
  - Error rate 10-50%
  - Authentication failures
  - Payment processing errors
- **Response Time:** < 30 minutes

### P2 - Medium

- **Definition:** Feature degraded, workaround exists
- **Sentry Indicators:**
  - Error rate 1-10%
  - Non-critical API failures
  - Performance degradation
- **Response Time:** < 4 hours

### P3 - Low

- **Definition:** Minor issue, minimal user impact
- **Sentry Indicators:**
  - Error rate < 1%
  - Edge case errors
  - Non-blocking failures
- **Response Time:** Next business day
