## Examples

### Next.js Configuration

```typescript
// sentry.client.config.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_VERCEL_ENV || 'development',
  enabled: process.env.NODE_ENV === 'production',
  debug: process.env.NODE_ENV === 'development',
});
```

### Python Flask Configuration

```python
import sentry_sdk
from flask import Flask

app = Flask(__name__)

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    environment=os.environ.get('FLASK_ENV', 'development'),
    debug=os.environ.get('FLASK_ENV') == 'development',
    traces_sample_rate=1.0 if os.environ.get('FLASK_ENV') == 'development' else 0.1,
)
```

---
*[Tons of Skills](https://tonsofskills.com) by [Intent Solutions](https://intentsolutions.io) | [jeremylongshore.com](https://jeremylongshore.com)*
