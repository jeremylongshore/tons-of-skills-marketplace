# Logging Integration Reference

## Winston Transport Pattern

The recommended pattern wraps a custom Winston transport that both forwards errors to Sentry and stamps the Sentry event ID back into the log object:

```typescript
import winston from 'winston';
import * as Sentry from '@sentry/node';

class SentryTransport extends winston.Transport {
  log(info: any, callback: () => void) {
    setImmediate(callback);
    if (info.level === 'error' || info.level === 'fatal') {
      Sentry.withScope((scope) => {
        scope.setTag('logger', 'winston');
        scope.setContext('log_entry', {
          level: info.level,
          service: info.service,
        });
        const eventId = Sentry.captureException(
          info.error instanceof Error ? info.error : new Error(info.message)
        );
        info.sentry_event_id = eventId;
      });
    }
  }
}
```

## Pino Hook Pattern

Pino uses the `hooks.logMethod` callback for interception. The hook fires before serialization, so injected fields appear in the final JSON output:

```typescript
import pino from 'pino';
import * as Sentry from '@sentry/node';

const logger = pino({
  hooks: {
    logMethod(inputArgs, method, level) {
      if (level >= 50) { // 50 = error, 60 = fatal
        const [obj, msg] = typeof inputArgs[0] === 'object'
          ? [inputArgs[0], inputArgs[1]]
          : [{}, inputArgs[0]];

        Sentry.withScope((scope) => {
          scope.setTag('logger', 'pino');
          const eventId = Sentry.captureException(
            obj.err instanceof Error ? obj.err : new Error(String(msg))
          );
          if (typeof inputArgs[0] === 'object') {
            inputArgs[0].sentry_event_id = eventId;
          }
        });
      }
      return method.apply(this, inputArgs);
    },
  },
});
```

## structlog Processor (Python)

```python
import structlog
import sentry_sdk

def sentry_processor(logger, method_name, event_dict):
    if method_name in ('error', 'critical', 'fatal'):
        exc_info = event_dict.get('exc_info')
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('logger', 'structlog')
            scope.set_context('log_entry', {
                k: str(v) for k, v in event_dict.items()
                if k not in ('exc_info', 'event')
            })
            if exc_info and isinstance(exc_info, BaseException):
                event_id = sentry_sdk.capture_exception(exc_info)
            else:
                event_id = sentry_sdk.capture_message(
                    event_dict.get('event', ''), level=method_name
                )
            event_dict['sentry_event_id'] = event_id
    return event_dict
```

## Request ID Correlation

Every request should carry a request ID through logs, Sentry tags, and response headers:

```typescript
import { randomUUID } from 'crypto';
import * as Sentry from '@sentry/node';

app.use((req, res, next) => {
  const requestId = (req.headers['x-request-id'] as string) || randomUUID();
  res.setHeader('x-request-id', requestId);
  Sentry.setTag('request_id', requestId);
  req.log = logger.child({ requestId });
  next();
});
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
