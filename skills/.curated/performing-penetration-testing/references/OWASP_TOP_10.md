# OWASP Top 10 (2021) Reference

Legacy reference context: approve scope and local inputs before the examples.
Missing/failed selected analyses remain incomplete, not clean. The retained web
scanner emits a numeric risk score only for completed checks, and its method
check observes advertisement only. Python auditing requires pinned requirements
or an explicit approved interpreter; legacy and canonical Finding schemas differ.

Quick reference for the OWASP Top 10 web application security risks, with scanner
mapping and remediation guidance.

---

## A01:2021 - Broken Access Control

**What it is:** Users can act outside their intended permissions. Includes IDOR,
missing function-level access control, CORS misconfiguration, and privilege
escalation.

**Scanner detection:**

- `security_scanner.py` -- checks CORS policy for wildcard origins, reflected
  origins, and credentials with wildcard
- `code_security_scanner.py` -- flags missing authorization decorators (regex)

**Remediation (Python/Flask):**

```python
# BAD: No authorization check
@app.route("/api/users/<user_id>")
def get_user(user_id):
    return db.get_user(user_id)

# GOOD: Verify the requesting user has access
@app.route("/api/users/<user_id>")
@login_required
def get_user(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    return db.get_user(user_id)
```

**Remediation (Node.js/Express):**

```javascript
// Middleware: verify resource ownership
function authorizeUser(req, res, next) {
    if (req.user.id !== req.params.userId && !req.user.isAdmin) {
        return res.status(403).json({ error: "Forbidden" });
    }
    next();
}
```

---

## A02:2021 - Cryptographic Failures

**What it is:** Sensitive data exposed due to weak or missing encryption. Includes
plaintext transmission, weak hashing algorithms, and improper key management.

**Scanner detection:**

- `security_scanner.py` -- checks SSL/TLS certificate validity, protocol version,
  HSTS header presence and max-age
- `code_security_scanner.py` -- flags MD5/SHA1 usage, insecure URLs (http://)

**Remediation:**

```python
# BAD: Weak hashing
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# GOOD: Use bcrypt or argon2
from argon2 import PasswordHasher
ph = PasswordHasher()
hashed = ph.hash(password)
```

---

## A03:2021 - Injection

**What it is:** Untrusted data sent to an interpreter as part of a command or query.
Includes SQL injection, NoSQL injection, OS command injection, and LDAP injection.

**Scanner detection:**

- `code_security_scanner.py` -- bandit flags (B608 SQL injection, B602 subprocess
  shell=True, B307 eval); regex patterns for string concatenation in queries,
  os.system calls, eval/exec usage

**Remediation (SQL - Python):**

```python
# BAD: String concatenation
cursor.execute("SELECT * FROM users WHERE name = '" + name + "'")

# GOOD: Parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

**Remediation (Command - Python):**

```python
# BAD: Shell injection
os.system("ping " + user_input)

# GOOD: Use subprocess with list args
subprocess.run(["ping", "-c", "1", validated_host], shell=False)
```

---

## A04:2021 - Insecure Design

**What it is:** Flaws in the design and architecture of the application rather than
implementation bugs. Missing threat modeling, insecure business logic.

**Scanner detection:**

- Not directly detectable by automated tools
- `code_security_scanner.py` can flag patterns that suggest design issues (e.g.,
  no rate limiting, missing input validation at boundaries)

**Mitigation:**

- Use threat modeling (STRIDE, DREAD) during design
- Implement defense in depth
- Apply principle of least privilege
- Use secure design patterns (input validation, output encoding)

---

## A05:2021 - Security Misconfiguration

**What it is:** Missing security hardening, default credentials, unnecessary
features enabled, verbose error messages, misconfigured permissions.

**Scanner detection:**

- `security_scanner.py` -- checks all security headers, server version disclosure,
  exposed admin endpoints, directory listing, dangerous HTTP methods enabled
- `dependency_auditor.py` -- flags outdated packages with known vulnerabilities

**Remediation:**

- Remove default accounts and passwords
- Disable directory listing
- Remove server version headers
- Configure security headers (see SECURITY_HEADERS.md)
- Disable unnecessary HTTP methods
- Review and minimize exposed endpoints

---

## A06:2021 - Vulnerable and Outdated Components

**What it is:** Using libraries, frameworks, or other software components with
known vulnerabilities.

**Scanner detection:**

- `dependency_auditor.py` -- runs npm audit and pip-audit to find CVEs in
  installed packages, reports severity and available fix versions

**Remediation:**

```bash
# Check npm vulnerabilities
npm audit

# Auto-fix where possible
npm audit fix

# Check Python dependencies
pip-audit

# Update specific package
pip install --upgrade package-name
```

---

## A07:2021 - Identification and Authentication Failures

**What it is:** Weak authentication mechanisms, credential stuffing, brute force,
session fixation, missing MFA.

**Scanner detection:**

- `security_scanner.py` -- checks for session cookie security attributes
  (Secure, HttpOnly, SameSite)
- `code_security_scanner.py` -- flags hardcoded passwords and tokens

**Remediation:**

- Implement MFA
- Never ship default credentials
- Implement account lockout / rate limiting
- Use strong password hashing (bcrypt, argon2)
- Rotate session IDs after authentication

---

## A08:2021 - Software and Data Integrity Failures

**What it is:** Code and infrastructure that does not protect against integrity
violations. Includes insecure deserialization, unsigned updates, untrusted CI/CD
pipelines.

**Scanner detection:**

- `code_security_scanner.py` -- bandit flags B301 (pickle), B506 (yaml.load
  without SafeLoader); regex patterns for marshal.loads, insecure deserialization

**Remediation (Python):**

```python
# BAD: Insecure deserialization
import pickle
data = pickle.loads(user_input)

# GOOD: Use safe formats
import json
data = json.loads(user_input)

# BAD: Unsafe YAML loading
import yaml
data = yaml.load(content)

# GOOD: Use SafeLoader
data = yaml.safe_load(content)
```

---

## A09:2021 - Security Logging and Monitoring Failures

**What it is:** Insufficient logging of security events, missing alerting, and
inability to detect active breaches.

**Scanner detection:**

- Not directly detectable by automated scanning
- Code review can identify missing logging in authentication and authorization
  paths

**Mitigation:**

- Log all authentication events (success and failure)
- Log access control failures
- Log input validation failures
- Ensure logs are tamper-proof
- Implement alerting for anomalous patterns
- Test that logging and alerting work

---

## A10:2021 - Server-Side Request Forgery (SSRF)

**What it is:** Application fetches remote resources based on user-supplied URLs
without validating the destination, allowing attackers to reach internal services.

**Scanner detection:**

- `code_security_scanner.py` -- regex patterns for URL fetching with user input
  (requests.get with unvalidated variables)

**Remediation (Python):**

```python
# BAD: Fetch user-supplied URL directly
response = requests.get(user_url)

# GOOD: Validate against allowlist
from urllib.parse import urlparse
ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}

parsed = urlparse(user_url)
if parsed.hostname not in ALLOWED_HOSTS:
    raise ValueError("URL not in allowlist")
if parsed.scheme not in ("http", "https"):
    raise ValueError("Invalid scheme")
response = requests.get(user_url, allow_redirects=False)
```

---

## Scanner Quick Reference

| OWASP Risk | security_scanner.py | dependency_auditor.py | code_security_scanner.py |
|------------|--------------------|-----------------------|--------------------------|
| A01 Access Control | CORS checks | -- | Auth pattern checks |
| A02 Crypto Failures | SSL/TLS, HSTS | -- | MD5/SHA1, http:// |
| A03 Injection | -- | -- | SQLi, CMDi, eval |
| A04 Insecure Design | -- | -- | -- (manual review) |
| A05 Misconfiguration | Headers, endpoints | Outdated packages | -- |
| A06 Vulnerable Components | -- | npm/pip audit | -- |
| A07 Auth Failures | Cookie attributes | -- | Hardcoded secrets |
| A08 Integrity Failures | -- | -- | pickle, yaml.load |
| A09 Logging Failures | -- | -- | -- (manual review) |
| A10 SSRF | -- | -- | URL fetch patterns |

---

## Further Reading

- [OWASP Top 10 Official](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)
