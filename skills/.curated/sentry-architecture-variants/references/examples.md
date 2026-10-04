# Examples

**Example 1 — Monolith with 5 teams:**
Request: "Set up Sentry for a Rails-style monolith with auth, billing, inventory, shipping, and analytics modules."
Result: Single Sentry project with `module` and `team` tags. Each team filters their issues with `tags.module:billing`. Ownership rules route alerts to the correct Slack channel. Breadcrumbs tagged by module show cross-module request flow.

**Example 2 — Microservices with Kafka:**
Request: "Configure Sentry for 12 microservices communicating via REST and Kafka."
Result: 12 Sentry projects with shared `initServiceSentry()` config. HTTP traces propagate automatically. Kafka producers inject `sentry-trace`/`baggage` into message headers. Consumers call `continueTrace()` to connect the chain. Trace view shows: `api-gateway → order-service → [kafka] → fulfillment-worker`.

**Example 3 — Serverless API on Lambda:**
Request: "Add Sentry to 8 AWS Lambda functions behind API Gateway."
Result: One Sentry project for the function group. Each handler wrapped with `Sentry.wrapHandler()`. Cold starts tagged explicitly. No manual `flush()` calls. Source maps uploaded via `sentry-cli` in CI.

**Example 4 — React SPA + Node API:**
Request: "Full-stack Sentry for a React frontend calling a Node.js Express API."
Result: Two Sentry projects (frontend + backend). React app uses `@sentry/react` with `browserTracingIntegration()` and `replayIntegration()`. `tracePropagationTargets` set to the API domain. Express API auto-continues browser traces. Trace view shows: `button.click → fetch /api/orders → db.query`.

**Example 5 — React Native mobile app:**
Request: "Set up Sentry for a React Native app with navigation tracking."
Result: `@sentry/react-native` with `reactNativeTracingIntegration()` and React Navigation instrumentation. Native crash handling enabled. Screenshots and view hierarchy attached on crash. Source maps and dSYMs uploaded in CI for readable stack traces.

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
