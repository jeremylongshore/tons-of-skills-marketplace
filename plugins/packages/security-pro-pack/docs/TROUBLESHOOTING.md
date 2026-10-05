# Troubleshooting Guide - Security Pro Pack

**Common issues and solutions for Security Pro Pack plugins**

---

## Installation Issues

### Issue: "Plugin not found" after installation

**Symptoms:**

```bash
$ /security-scan-quick
Error: Command not found: security-scan-quick
```

**Cause:** Plugin not properly installed or Claude Code hasn't reloaded plugins

**Solution:**

```bash
# Step 1: Verify plugin directory exists
ls -la $HOME/.claude/plugins/security-pro-pack

# Step 2: If missing, reinstall
claude plugin install ./security-pro-pack

# Step 3: Reload Claude Code
claude plugin reload

# Step 4: Verify installation
claude plugin list | grep security-pro-pack
```

---

### Issue: Permission denied errors

**Symptoms:**

```bash
$ /docker-security-scan
Error: Permission denied: /home/user/.claude/plugins/security-pro-pack
```

**Cause:** Incorrect file permissions on plugin directory

**Solution:**

```bash
# Fix permissions
chmod -R 755 $HOME/.claude/plugins/security-pro-pack

# Fix ownership
chown -R $USER:$USER $HOME/.claude/plugins/security-pro-pack

# Reload plugins
claude plugin reload
```

---

### Issue: Validation errors during install

**Symptoms:**

```
Error: Invalid plugin structure
Missing required file: .claude-plugin/plugin.json
```

**Cause:** Corrupted or incomplete plugin package

**Solution:**

```bash
# Step 1: Verify package integrity
sha256sum security-pro-pack.zip
# Compare with SHA256 in release notes

# Step 2: If mismatch, re-download
rm security-pro-pack.zip
curl -L [download URL] -o security-pro-pack.zip

# Step 3: Extract and reinstall
unzip security-pro-pack.zip
claude plugin install ./security-pro-pack
```

---

## Command Plugin Issues

### Issue: /ss command produces no output

**Symptoms:**

```bash
$ /ss
# Command runs but no report generated
```

**Cause 1:** No files to scan in current directory

**Solution:**

```bash
# Verify you're in project directory
pwd

# Check for files
ls -la

# Explicitly specify directory
/ss /path/to/project
```

**Cause 2:** All issues filtered out (e.g., .gitignore excludes everything)

**Solution:**

```bash
# Run with verbose flag
/ss --verbose

# Check what's being scanned
/ss --dry-run
```

---

### Issue: /dss fails with "Docker daemon not running"

**Symptoms:**

```bash
$ /dss nginx:latest
Error: Cannot connect to Docker daemon
```

**Cause:** Docker not running or permissions issue

**Solution:**

**macOS:**

```bash
# Start Docker Desktop
open -a Docker

# Wait for Docker to start (30 seconds)
docker ps
```

**Linux:**

```bash
# Start Docker service
sudo systemctl start docker

# Verify it's running
sudo systemctl status docker

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Test without sudo
docker ps
```

---

### Issue: /asa returns "Connection refused"

**Symptoms:**

```bash
$ /asa https://api.example.com
Error: Connection refused
```

**Cause:** API not accessible or network issue

**Solution:**

```bash
# Step 1: Verify API is accessible
curl https://api.example.com/health
# Should return 200 OK

# Step 2: Check network connectivity
ping api.example.com

# Step 3: Verify firewall not blocking
# If behind corporate firewall, use --proxy flag
/asa https://api.example.com --proxy http://proxy.corp.com:8080

# Step 4: For local development
/asa http://localhost:3000  # Use http://, not https://
```

---

## Agent Plugin Issues

### Issue: Security Auditor Expert not activating

**Symptoms:**
> "Can you perform a security audit?"

Claude responds without using Security Auditor Expert agent

**Cause:** Activation triggers not recognized

**Solution:**

```
# Use explicit trigger words
> "Please use the Security Auditor Expert to perform an OWASP Top 10 audit"

# Or mention specific capabilities
> "Review this code for SQL injection and XSS vulnerabilities using the security expert"

# Or ask directly
> "Can you activate the Security Auditor Expert agent?"
```

---

### Issue: Compliance Checker provides generic advice

**Symptoms:**
Agent gives general security advice instead of specific HIPAA/PCI DSS/GDPR guidance

**Cause:** Unclear which framework to assess against

**Solution:**

```
# Be specific about framework
> "Use Compliance Checker to review this application for HIPAA compliance"

# Mention specific controls
> "Check this authentication system against PCI DSS Requirement 8"

# Provide context
> "We're a healthcare app. Review our database encryption for HIPAA Technical Safeguards."
```

---

### Issue: Crypto Expert recommends outdated algorithms

**Symptoms:**
Agent suggests algorithms that are no longer recommended

**Cause:** This should NOT happen - if it does, report as bug

**Solution:**

```
# Verify plugin version
claude plugin info security-pro-pack
# Should be v1.0.0 or later

# Update to latest version
claude plugin update security-pro-pack

# Report the issue
# Include: What was recommended, what should have been recommended
```

---

## Docker Security Scan Issues

### Issue: "Image not found" error

**Symptoms:**

```bash
$ /dss myapp:latest
Error: Image not found: myapp:latest
```

**Cause:** Image doesn't exist locally or typo in image name

**Solution:**

```bash
# Step 1: List all images
docker images

# Step 2: Verify exact image name (case-sensitive)
docker images | grep myapp

# Step 3: If not found, pull it
docker pull myapp:latest

# Step 4: For local builds
docker build -t myapp:latest .
```

---

### Issue: Scan reports "0 vulnerabilities" suspiciously

**Symptoms:**
All scans show zero vulnerabilities (unlikely for real images)

**Cause:** Scanner not accessing vulnerability database

**Solution:**

```bash
# Update vulnerability database
docker pull aquasec/trivy:latest

# Re-run scan
/dss myapp:latest --force-update

# Verify scanner is working
/dss nginx:latest  # Known to have some CVEs
```

---

## API Security Audit Issues

### Issue: Rate limiting errors during audit

**Symptoms:**

```bash
$ /asa https://api.example.com
Error: 429 Too Many Requests
```

**Cause:** API has aggressive rate limiting

**Solution:**

```bash
# Use slower scan mode
/asa https://api.example.com --slow

# Scan specific endpoints only
/asa https://api.example.com --endpoints /users,/orders

# Add authentication (may have higher limits)
/asa https://api.example.com --auth "Bearer YOUR_TOKEN"
```

---

### Issue: "SSL certificate verification failed"

**Symptoms:**

```
Error: SSL certificate verification failed
```

**Cause:** Self-signed certificate or invalid SSL

**Solution:**

```bash
# For development/staging with self-signed certs
/asa https://staging-api.example.com --insecure

# ️ WARNING: Never use --insecure for production audits!

# Better solution: Add certificate to system trust store
# macOS:
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cert.pem

# Linux:
sudo cp cert.pem /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

---

## Compliance Documentation Issues

### Issue: Generated docs missing organization details

**Symptoms:**
Documentation says "[Company Name]" instead of your company

**Cause:** Organization name not specified

**Solution:**

```bash
# Specify organization during generation
/compliance-docs-generate --framework hipaa --org "HealthCare Inc"

# Or set environment variable
export COMPLIANCE_ORG_NAME="HealthCare Inc"
/cdg --framework hipaa
```

---

### Issue: Documentation doesn't match our architecture

**Symptoms:**
Generated policies reference "cloud provider" but we're on-premises

**Cause:** Templates are generic, need customization

**Solution:**

```
# Step 1: Generate base documentation
/cdg --framework hipaa

# Step 2: Customize generated files
# Files are in markdown, edit as needed:
vim compliance-docs/hipaa/Security-Management-Process-Policy.md

# Step 3: Save customized version
cp compliance-docs/hipaa/*.md /your-repo/compliance/

# Step 4: Track in version control
git add compliance/
git commit -m "Add customized HIPAA documentation"
```

---

## Cryptography Audit Issues

### Issue: False positives on test code

**Symptoms:**

```
 CRITICAL: MD5 hashing detected
File: tests/fixtures/test-data.js:12
```

**Cause:** Scanner can't distinguish test code from production

**Solution:**

**Option 1: Add ignore comments**

```javascript
// tests/fixtures/test-data.js
// CRYPTO_AUDIT_IGNORE: Test fixture, not used in production
const TEST_HASH = md5("test-data")
```

**Option 2: Exclude test directories**

```bash
/ca src/crypto/ --exclude tests/,fixtures/
```

**Option 3: Configure in .cryptoauditignore file**

```
# .cryptoauditignore
tests/**/*
fixtures/**/*
*.test.js
*.spec.js
```

---

### Issue: "No cryptographic code found"

**Symptoms:**
Audit completes but reports 0 findings (you know you have crypto)

**Cause:** Scanner looking in wrong directory or file types not recognized

**Solution:**

```bash
# Specify exact files
/ca src/crypto/encryption.js src/auth/password.js

# Include specific file extensions
/ca --include "*.js,*.ts,*.py"

# Verbose mode to see what's scanned
/ca --verbose
```

---

## Threat Modeling Issues

### Issue: Agent produces generic threats

**Symptoms:**
Threat model lists obvious issues without system-specific analysis

**Cause:** Insufficient context provided about your system

**Solution:**

```
# Provide detailed context
> "I need a STRIDE threat model for our payment processing system.
>
> Architecture:
> - User browser → HTTPS → Nginx load balancer
> - Nginx → HTTP → Node.js API server (port 3000)
> - API → PostgreSQL database (port 5432)
> - API → Stripe API (external, HTTPS)
>
> Trust boundaries:
> 1. Internet to DMZ (Nginx)
> 2. DMZ to internal network (API server)
> 3. Internal to database
>
> Sensitive data:
> - Credit card tokens (encrypted)
> - User PII (name, email, address)
> - Payment history
>
> Please threat model this with STRIDE and prioritize by risk."
```

---

## Performance Issues

### Issue: Security scans taking too long

**Symptoms:**

```bash
$ /ss
# Runs for 10+ minutes on large codebase
```

**Cause:** Scanning too many files (including node_modules, vendor, etc.)

**Solution:**

```bash
# Exclude large directories
/ss --exclude node_modules/,vendor/,dist/,build/

# Scan specific directories only
/ss src/ --output src-security-scan.md

# Use .securityscanignore file
# .securityscanignore
node_modules/
vendor/
dist/
build/
*.min.js
```

---

### Issue: Docker scans very slow

**Symptoms:**
Each Docker image scan takes 5+ minutes

**Cause:** Downloading vulnerability database on each scan

**Solution:**

```bash
# Pre-download vulnerability DB (run once)
docker pull aquasec/trivy:latest

# Use local cache
/dss myapp:latest --cache

# Scan offline (use cached DB)
/dss myapp:latest --offline
```

---

## Output/Reporting Issues

### Issue: Reports not being saved

**Symptoms:**

```bash
$ /ss --output report.md
# Scan completes but report.md not created
```

**Cause:** Permission issue or invalid path

**Solution:**

```bash
# Check current directory permissions
ls -la

# Use absolute path
/ss --output /home/user/reports/security-scan.md

# Verify directory exists
mkdir -p reports/
/ss --output reports/security-scan.md
```

---

### Issue: Report formatting broken

**Symptoms:**
Markdown report doesn't render correctly in viewer

**Cause:** Special characters or encoding issue

**Solution:**

```bash
# Specify UTF-8 encoding
/ss --output report.md --encoding utf-8

# Convert to PDF (if markdown rendering issues persist)
pandoc report.md -o report.pdf

# Or view in different tool
cat report.md | less
```

---

## Integration Issues

### Issue: CI/CD pipeline fails with plugin

**Symptoms:**

```yaml
# GitHub Actions
- name: Security Scan
  run: /ss
  # Error: claude command not found
```

**Cause:** Claude Code not installed in CI environment

**Solution:**

**Option 1: Use standalone scripts**

```bash
# Extract scanner logic to standalone script
# security-scan.sh (generated by plugin)
./scripts/security-scan.sh src/
```

**Option 2: Install Claude Code in CI**

```yaml
- name: Install Claude Code
  run: |
    curl -L https://claude.com/download/cli -o claude
    chmod +x claude
    sudo mv claude /usr/local/bin/

- name: Install Security Pro Pack
  run: |
    claude plugin install security-pro-pack.zip

- name: Run Security Scan
  run: claude exec /ss
```

---

## Environment-Specific Issues

### Issue: Different results locally vs CI

**Symptoms:**
Local scan finds 5 issues, CI finds 15 issues

**Cause:** Different file sets scanned (CI has no .gitignore exclusions)

**Solution:**

```bash
# Use consistent exclusions
# Create .securityscanignore (committed to git)
echo "node_modules/" >> .securityscanignore
echo "dist/" >> .securityscanignore

# CI respects .securityscanignore
/ss --respect-gitignore=false
```

---

## Getting Help

### Before Asking for Help

1. **Check plugin version:**

   ```bash
   claude plugin info security-pro-pack
   # Should be v1.0.0 or later
   ```

2. **Run in verbose mode:**

   ```bash
   /ss --verbose 2>&1 | tee debug.log
   ```

3. **Check logs:**

   ```bash
   tail -f ~/.claude/logs/plugins.log
   ```

### How to Report Issues

**Good Bug Report:**

```markdown
**Plugin:** security-scan-quick
**Version:** 1.0.0
**OS:** macOS 14.0 / Ubuntu 22.04 / Windows 11

**Issue:**
Running /ss produces "Permission denied" error

**Steps to Reproduce:**
1. cd ~/my-project
2. /ss
3. Error appears

**Expected Behavior:**
Security scan should run and produce report

**Actual Behavior:**
Error: Permission denied: /tmp/security-scan-12345

**Logs:**
[Attach verbose output]

**Additional Context:**
- Docker is running
- Has worked previously (last week)
- Changed: Upgraded to macOS 14.0
```

### Support Channels

- **Email:** [email protected]
- **GitHub Issues:** https://github.com/jeremylongshore/claude-code-plugins/issues
- **Discussions:** https://github.com/jeremylongshore/claude-code-plugins/discussions
- **Documentation:**

---

## Common Error Messages

### "Command not found"

→ See "Installation Issues" section above

### "Permission denied"

→ See "Permission denied errors" section above

### "Connection refused"

→ See "/asa returns 'Connection refused'" section above

### "Rate limit exceeded"

→ See "Rate limiting errors during audit" section above

### "SSL certificate verification failed"

→ See "SSL certificate verification failed" section above

### "Docker daemon not running"

→ See "/dss fails with Docker daemon" section above

### "Image not found"

→ See "Docker Security Scan Issues" section above

---

**Still stuck?** Email [email protected] with:

1. Plugin version
1. Operating system
1. Error message (full text)
1. Steps to reproduce
1. Verbose output

We typically respond within 24 hours.
