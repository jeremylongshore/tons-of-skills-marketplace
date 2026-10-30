# Security Headers Reference

Legacy reference context: approve scope and local inputs before the examples.
Missing/failed selected analyses remain incomplete, not clean. The retained web
scanner emits a numeric risk score only for completed checks, and its method
check observes advertisement only. Python auditing requires pinned requirements
or an explicit approved interpreter; legacy and canonical Finding schemas differ.

Comprehensive guide to HTTP security headers, what they protect against,
recommended values, and implementation across common frameworks.

---

## Content-Security-Policy (CSP)

**Purpose:** Prevents XSS, clickjacking, and code injection by controlling which
resources the browser is allowed to load.

**Recommended value:**

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

**What security_scanner.py checks:**

- Header is present
- `default-src` directive exists
- No `unsafe-eval` in `script-src`
- No wildcard `*` in `default-src` or `script-src`

**Implementation:**

Express.js:

```javascript
const helmet = require("helmet");
app.use(helmet.contentSecurityPolicy({
    directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        frameAncestors: ["'none'"],
    }
}));
```

Django:

```python
# settings.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FRAME_ANCESTORS = ("'none'",)
```

Nginx:

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none';" always;
```

Apache:

```apache
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none';"
```

---

## Strict-Transport-Security (HSTS)

**Purpose:** Forces browsers to use HTTPS for all future requests to the domain,
preventing protocol downgrade attacks and cookie hijacking.

**Recommended value:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**What security_scanner.py checks:**

- Header is present (critical if site supports HTTPS)
- `max-age` >= 31536000 (1 year)
- `includeSubDomains` directive present
- Notes `preload` status

**Implementation:**

Express.js:

```javascript
app.use(helmet.hsts({
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
}));
```

Django:

```python
# settings.py
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

Nginx:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

Apache:

```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

---

## X-Frame-Options

**Purpose:** Prevents clickjacking by controlling whether the page can be rendered
in a frame, iframe, embed, or object.

**Recommended value:**

```
X-Frame-Options: DENY
```

Or `SAMEORIGIN` if framing by same-origin pages is needed.

**What security_scanner.py checks:**

- Header is present
- Value is DENY or SAMEORIGIN (not ALLOW-FROM, which is deprecated)

**Implementation:**

Express.js:

```javascript
app.use(helmet.frameguard({ action: "deny" }));
```

Django:

```python
# settings.py (default in Django 3+)
X_FRAME_OPTIONS = "DENY"
```

Nginx:

```nginx
add_header X-Frame-Options "DENY" always;
```

---

## X-Content-Type-Options

**Purpose:** Prevents MIME-type sniffing, which can lead to XSS when browsers
interpret files as a different content type than declared.

**Recommended value:**

```
X-Content-Type-Options: nosniff
```

**What security_scanner.py checks:**

- Header is present
- Value is exactly `nosniff`

**Implementation:**

Express.js:

```javascript
app.use(helmet.noSniff());
```

Django:

```python
# Enabled by default via SecurityMiddleware
SECURE_CONTENT_TYPE_NOSNIFF = True
```

Nginx:

```nginx
add_header X-Content-Type-Options "nosniff" always;
```

---

## Referrer-Policy

**Purpose:** Controls how much referrer information is included with requests,
preventing leakage of sensitive URLs to third parties.

**Recommended values:**

```
Referrer-Policy: strict-origin-when-cross-origin
```

Or `no-referrer` for maximum privacy.

**What security_scanner.py checks:**

- Header is present
- Value is not `unsafe-url` (leaks full URL including path and query)
- Value is not empty

**Implementation:**

Express.js:

```javascript
app.use(helmet.referrerPolicy({ policy: "strict-origin-when-cross-origin" }));
```

Django:

```python
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
```

Nginx:

```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## Permissions-Policy

**Purpose:** Controls which browser features and APIs can be used by the page and
its iframes (camera, microphone, geolocation, etc.).

**Recommended value:**

```
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

**What security_scanner.py checks:**

- Header is present
- Notes which features are restricted

**Implementation:**

Express.js:

```javascript
app.use(helmet.permittedCrossDomainPolicies());
// Or manually:
app.use((req, res, next) => {
    res.setHeader("Permissions-Policy",
        "camera=(), microphone=(), geolocation=(), payment=()");
    next();
});
```

Nginx:

```nginx
add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
```

---

## X-XSS-Protection (Deprecated)

**Purpose:** Legacy header that enabled the browser's built-in XSS filter.
Deprecated in modern browsers in favor of CSP. Can cause issues if set to
`1; mode=block` on some older browsers.

**Recommended value:**

```
X-XSS-Protection: 0
```

Set to 0 (disabled) since the browser feature is deprecated and CSP is the
proper replacement.

**What security_scanner.py checks:**

- Notes if present
- Info-level finding (not a vulnerability)

---

## Cache-Control (Security-Relevant)

**Purpose:** Prevents sensitive responses from being cached and served to
unauthorized users.

**Recommended value for sensitive pages:**

```
Cache-Control: no-store, no-cache, must-revalidate, private
```

**Implementation:**

Express.js:

```javascript
app.use("/api/private", (req, res, next) => {
    res.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, private");
    next();
});
```

Django:

```python
from django.views.decorators.cache import never_cache

@never_cache
def sensitive_view(request):
    ...
```

---

## Complete Header Set

Recommended minimum security headers for a production web application:

```
Content-Security-Policy: default-src 'self'; script-src 'self'; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
X-XSS-Protection: 0
```

### Nginx complete block:

```nginx
# Security Headers
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; frame-ancestors 'none'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header X-XSS-Protection "0" always;

# Hide server version
server_tokens off;
```

### Apache complete block:

```apache
# Security Headers
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; frame-ancestors 'none'"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
Header always set X-XSS-Protection "0"

# Hide server version
ServerTokens Prod
ServerSignature Off
```

---

## Header Grading

The `security_scanner.py` grades headers on a 0-100 scale:

| Header | Weight | Scoring |
|--------|--------|---------|
| Content-Security-Policy | 25 | Present + default-src + no unsafe-eval |
| Strict-Transport-Security | 20 | Present + max-age >= 1yr + includeSubDomains |
| X-Content-Type-Options | 15 | Present + nosniff |
| X-Frame-Options | 15 | Present + DENY or SAMEORIGIN |
| Referrer-Policy | 10 | Present + not unsafe-url |
| Permissions-Policy | 10 | Present |
| Server header hidden | 5 | No version info in Server header |

---

## Further Reading

- [MDN HTTP Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [SecurityHeaders.com](https://securityheaders.com/) - Free header scanner
- [Helmet.js Documentation](https://helmetjs.github.io/)
