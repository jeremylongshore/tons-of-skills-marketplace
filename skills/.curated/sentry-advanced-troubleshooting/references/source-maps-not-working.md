# Source Maps Not Working

## Source Maps Not Working

### Verify Upload

```bash
# Check if source maps are uploaded
sentry-cli releases files $VERSION list

# Expected output:
# ~/static/js/main.js
# ~/static/js/main.js.map
```

### Check URL Prefix

```typescript
// Browser URL: https://example.com/static/js/main.js
// Source map should be: ~/static/js/main.js.map

// Upload with correct prefix
sentry-cli releases files $VERSION upload-sourcemaps ./dist \
  --url-prefix "~/static/js"
```

### Debug Source Map Resolution

```bash
# Validate source map
sentry-cli sourcemaps explain $EVENT_ID

# This shows:
# - What URL Sentry is looking for
# - What files are uploaded
# - Why mapping failed
```

### Common Source Map Issues

```yaml
Issue: Minified stack traces
Fix: Verify source maps uploaded with correct release

Issue: "Could not find source map"
Fix: Check url-prefix matches actual URLs

Issue: Wrong line numbers
Fix: Ensure source maps are from same build

Issue: "Source code not found"
Fix: Upload source files along with maps
```
