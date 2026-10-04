# sdk-major-upgrade

**Owner:** `sentry-event-forensics` → `sdk-migrator`
Off the default fan-out. Only when the user asked to upgrade.

Do not claim the upgrade succeeded without a test capture a human can see in Sentry.

## JavaScript v7 → v8

Command:

```bash
npx @sentry/migr8@latest
```

Docs: https://docs.sentry.io/platforms/javascript/migration/v7-to-v8/

The codemod does not finish the job. Call these out as manual breaks when the repo still has them:

- Class integrations (`new BrowserTracing()`, `new Replay()`, `new Integrations.*`) → functional integrations (`browserTracingIntegration()`, `replayIntegration()`, `rewriteFramesIntegration()`).
- `startTransaction` / `span.startChild` → `startSpan` / `startInactiveSpan`.
- Hub APIs: `getCurrentHub`, `configureScope`, `hub.getScope` removed or replaced by the scope/isolation APIs the migration page names.
- `tracingOrigins` → `tracePropagationTargets`.
- `@sentry/hub` as a direct dependency.
- Bundler plugin major aligned with the SDK (`@sentry/webpack-plugin`, `@sentry/vite-plugin`, `@sentry/esbuild-plugin` ≥ 2 for Debug ID inject). An old plugin that only uploads is the release-medic grep's problem, not a reason to skip the codemod.

After the codemod: one service, a test event, the event id quoted back. No event id, no "upgrade succeeded."

## Python 1.x → 2.x

Docs: https://docs.sentry.io/platforms/python/migration/1.x-to-2.x/

There is no single `npx` equivalent to promise. Read that page against the repo. Hub is removed; `configure_scope` / `push_scope` usage has to be checked, not assumed. Integrations that were classes changed. Same exit rule: a test capture, or you did not finish.

## Do not

- Run this during a 2am "events vanished" call.
- Edit every package in one breath unless the user listed them.
- Print auth tokens. `sendDefaultPii` changes belong to PII, not this checklist, unless the diff shows the upgrade flipped it to true — then name it and hand off.
