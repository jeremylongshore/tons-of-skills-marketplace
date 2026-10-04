## Examples

### Express Middleware

```typescript
import * as Sentry from '@sentry/node';
import express from 'express';

const app = express();

// Sentry request handler (creates transaction)
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());

app.get('/api/users', async (req, res) => {
  const span = Sentry.getCurrentHub().getScope()?.getTransaction()?.startChild({
    op: 'db.query',
    description: 'fetch_users',
  });

  const users = await db.users.findMany();
  span?.finish();

  res.json(users);
});
```

### Python with FastAPI

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)

@app.get('/api/users')
async def get_users():
    with sentry_sdk.start_span(op='db.query', description='fetch_users'):
        users = await db.fetch_all('SELECT * FROM users')
    return users
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
