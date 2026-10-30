# Remediation Playbook

Legacy reference context: approve scope and local inputs before the examples.
Missing/failed selected analyses remain incomplete, not clean. The retained web
scanner emits a numeric risk score only for completed checks, and its method
check observes advertisement only. Python auditing requires pinned requirements
or an explicit approved interpreter; legacy and canonical Finding schemas differ.

Copy-paste fix templates for common security vulnerabilities. Each entry includes
the vulnerable pattern, the fix, and a verification command.

---

## SQL Injection

**Vulnerable pattern (Python):**

```python
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
```

**Fix (Python - parameterized query):**

```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

**Fix (Python - SQLAlchemy):**

```python
from sqlalchemy import text
result = session.execute(text("SELECT * FROM users WHERE username = :name"),
                         {"name": username})
```

**Vulnerable pattern (Node.js):**

```javascript
const query = `SELECT * FROM users WHERE username = '${username}'`;
db.query(query);
```

**Fix (Node.js - parameterized):**

```javascript
db.query("SELECT * FROM users WHERE username = $1", [username]);
```

**Fix (Node.js - Knex.js):**

```javascript
knex("users").where("username", username).first();
```

**Verification:**

```bash
python3 code_security_scanner.py /path/to/code --tools regex
# Check that no SQL string concatenation findings remain
```

---

## Cross-Site Scripting (XSS)

**Vulnerable pattern (Python/Jinja2):**

```python
# Marking user input as safe bypasses auto-escaping
return Markup(f"<p>Hello {user_input}</p>")
```

**Fix (Python/Jinja2):**

```python
# Let the template engine auto-escape (default in Jinja2)
return render_template("greeting.html", name=user_input)
```

```html
<!-- greeting.html - auto-escaped by default -->
<p>Hello {{ name }}</p>
```

**Vulnerable pattern (Node.js/Express):**

```javascript
res.send(`<p>Search results for: ${req.query.q}</p>`);
```

**Fix (Node.js - use template engine with auto-escaping):**

```javascript
// With EJS (auto-escapes by default with <%= %>)
res.render("search", { query: req.query.q });
```

```html
<!-- search.ejs -->
<p>Search results for: <%= query %></p>
```

**Fix (React - auto-escapes by default):**

```jsx
// React auto-escapes variables in JSX
return <p>Search results for: {query}</p>;
// NEVER use dangerouslySetInnerHTML with user input
```

**Additional protection - CSP header:**

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

**Verification:**

```bash
python3 security_scanner.py https://your-site.com --checks headers
# Verify CSP header is present and configured
```

---

## Hardcoded Secrets

**Vulnerable pattern:**

```python
API_KEY = "sk-abc123def456ghi789"
DATABASE_URL = "postgresql://admin:password123@db.example.com/prod"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

**Fix (Python - environment variables):**

```python
import os

API_KEY = os.environ["API_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
```

**Fix (Python - dotenv for development):**

```python
from dotenv import load_dotenv
import os

load_dotenv()  # loads from .env file (NEVER commit .env)
API_KEY = os.environ["API_KEY"]
```

**Fix (Node.js):**

```javascript
// npm install dotenv
require("dotenv").config();

const apiKey = process.env.API_KEY;
const dbUrl = process.env.DATABASE_URL;
```

**Prevention - .gitignore:**

```gitignore
.env
.env.local
.env.production
*.pem
*.key
credentials.json
```

**Verification:**

```bash
python3 code_security_scanner.py /path/to/code --tools regex
# Check for hardcoded-secret findings
# Also verify .env is in .gitignore:
grep -q '.env' .gitignore && echo "OK" || echo "MISSING"
```

---

## Missing Security Headers

**Vulnerable:** No security headers configured (defaults to none).

**Fix (Express.js - Helmet):**

```javascript
const helmet = require("helmet");
app.use(helmet());
```

**Fix (Django):**

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # ... other middleware
]

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
```

**Fix (Flask):**

```python
from flask_talisman import Talisman

Talisman(app, content_security_policy={
    "default-src": "'self'",
    "script-src": "'self'",
    "frame-ancestors": "'none'",
})
```

**Verification:**

```bash
python3 security_scanner.py https://your-site.com --checks headers
# All headers should show as present
```

---

## Weak TLS Configuration

**Vulnerable:** TLS 1.0/1.1 enabled, weak cipher suites, expired certificates.

**Fix (Nginx):**

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
```

**Fix (Apache):**

```apache
SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
SSLHonorCipherOrder off
```

**Certificate renewal (Let's Encrypt):**

```bash
# Install certbot
sudo certbot renew --dry-run

# Auto-renewal cron
0 12 * * * /usr/bin/certbot renew --quiet
```

**Verification:**

```bash
python3 security_scanner.py https://your-site.com --checks ssl
# Check certificate expiry and protocol version
```

---

## Vulnerable Dependencies

**Vulnerable:** Outdated packages with known CVEs.

**Fix (npm):**

```bash
# View vulnerabilities
npm audit

# Auto-fix compatible updates
npm audit fix

# Force major version updates (review changes!)
npm audit fix --force

# Update specific package
npm install package-name@latest
```

**Fix (Python/pip):**

```bash
# Audit installed packages
pip-audit

# Update specific package
pip install --upgrade package-name

# Update all packages (use with caution)
pip list --outdated --format=json | python3 -c "
import json, sys
for pkg in json.load(sys.stdin):
    print(pkg['name'])
" | xargs -n1 pip install --upgrade
```

**Fix (Lock file hygiene):**

```bash
# npm - regenerate lock file
rm package-lock.json && npm install

# pip - regenerate requirements
pip freeze > requirements.txt
```

**Verification:**

```bash
python3 dependency_auditor.py /path/to/project
# Should show no critical/high vulnerabilities
```

---

## Command Injection

**Vulnerable pattern (Python):**

```python
import os
os.system("ping " + user_host)

import subprocess
subprocess.run(f"grep {pattern} {filename}", shell=True)
```

**Fix (Python):**

```python
import subprocess
import shlex

# Use list arguments (no shell interpretation)
subprocess.run(["ping", "-c", "1", validated_host], shell=False, timeout=10)

# If shell is truly needed, use shlex.quote
subprocess.run(f"grep {shlex.quote(pattern)} {shlex.quote(filename)}",
               shell=True, timeout=10)
```

**Vulnerable pattern (Node.js):**

```javascript
const { exec } = require("child_process");
exec(`ls ${userInput}`);
```

**Fix (Node.js):**

```javascript
const { execFile } = require("child_process");
// execFile does not invoke a shell
execFile("ls", [validatedPath], (error, stdout) => {
    // ...
});
```

**Verification:**

```bash
python3 code_security_scanner.py /path/to/code --tools bandit,regex
# Check for command-injection category findings
```

---

## Insecure Deserialization

**Vulnerable pattern (Python):**

```python
import pickle
data = pickle.loads(request.data)    # Arbitrary code execution

import yaml
config = yaml.load(user_input)       # Arbitrary code execution
```

**Fix (Python):**

```python
# Use safe data formats
import json
data = json.loads(request.data)

# Use SafeLoader for YAML
import yaml
config = yaml.safe_load(user_input)

# If pickle is required (trusted data only), use hmac verification
import hmac
import hashlib

def verify_and_load(data, signature, secret_key):
    expected = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid signature")
    return pickle.loads(data)  # Only after verification
```

**Verification:**

```bash
python3 code_security_scanner.py /path/to/code --tools bandit,regex
# Check for insecure-deserialization category findings
```

---

## CORS Misconfiguration

**Vulnerable:**

```javascript
app.use(cors({ origin: "*", credentials: true }));
// Or reflecting any origin:
res.setHeader("Access-Control-Allow-Origin", req.headers.origin);
```

**Fix (Express.js):**

```javascript
const allowedOrigins = ["https://app.example.com", "https://admin.example.com"];

app.use(cors({
    origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error("Not allowed by CORS"));
        }
    },
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
}));
```

**Fix (Django):**

```python
# pip install django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]
CORS_ALLOW_CREDENTIALS = True
```

**Verification:**

```bash
python3 security_scanner.py https://your-api.com --checks cors
# Should not show wildcard or reflected origin with credentials
```

---

## Checklist: Post-Remediation

After applying fixes, run the full scan suite to verify:

```bash
# 1. Check security headers
python3 security_scanner.py https://your-site.com --checks headers,ssl,cors

# 2. Check dependencies
python3 dependency_auditor.py /path/to/project --min-severity high

# 3. Check code
python3 code_security_scanner.py /path/to/code --severity high

# 4. Verify no regressions
# Run your application's test suite
npm test   # or pytest, etc.
```

---

## Further Reading

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
