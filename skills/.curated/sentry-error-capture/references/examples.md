## Examples

### API Error Handler

```typescript
async function apiHandler(req, res, next) {
  try {
    const result = await processRequest(req);
    res.json(result);
  } catch (error) {
    Sentry.withScope((scope) => {
      scope.setTag('api_endpoint', req.path);
      scope.setTag('http_method', req.method);
      scope.setExtra('request_body', req.body);
      scope.setExtra('query_params', req.query);
      scope.setUser({ ip_address: req.ip });
      Sentry.captureException(error);
    });
    next(error);
  }
}
```

### Python Context Manager

```python
from contextlib import contextmanager
import sentry_sdk

@contextmanager
def capture_errors(operation: str, **context):
    try:
        yield
    except Exception as e:
        with sentry_sdk.push_scope() as scope:
            scope.set_tag('operation', operation)
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(e)
        raise

# Usage
with capture_errors('sync_users', batch_size=100):
    sync_all_users()
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
