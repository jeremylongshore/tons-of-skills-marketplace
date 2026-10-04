# Examples

**Example 1: Full-stack request tracing with log correlation**

Request: "Every error in our Express API should appear in both our log aggregator and Sentry with cross-links."

Result: Express middleware assigns a request ID, sets it as a Sentry tag, creates a pino child logger with the same ID, and on errors captures the exception in Sentry while stamping the event ID into the log entry. Both log aggregator and Sentry show the same `request_id` for filtering.

**Example 2: Grafana dashboard with Sentry error annotations**

Request: "Show Sentry errors as annotations on our Grafana latency dashboard."

Result: Sentry internal integration sends webhook on issue creation. A receiver endpoint transforms the payload into a Grafana annotation API call. Error events appear as vertical markers on the latency graph, with clickable links back to Sentry.

**Example 3: Datadog + Sentry dual visibility**

Request: "Correlate Sentry errors with Datadog APM traces so we can click between them."

Result: `beforeSend` hook reads the active Datadog span, injects `dd.trace_id` and `dd.span_id` as tags, and adds a `datadog` context with a clickable trace URL. Engineers can jump from Sentry error to Datadog distributed trace in one click.

**Example 4: Business metrics alongside error rates**

Request: "Track checkout success/failure rates in Sentry alongside our error data."

Result: `Sentry.metrics.increment('checkout.attempted')` and `Sentry.metrics.increment('checkout.failed')` with tags for payment provider and plan tier. Sentry Discover queries show error spikes correlated with checkout failure rate changes.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
