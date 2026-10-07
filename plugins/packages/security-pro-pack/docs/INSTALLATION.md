# Installation Guide - Security Pro Pack

**Version:** 1.0.0
**Last Updated:** October 10, 2025
**Installation Time:** 3-5 minutes

---

## Overview

The **Security Pro Pack** is a comprehensive collection of 10 security-focused plugins for Claude Code, providing automated security scanning, compliance checking, cryptography review, and infrastructure security analysis.

**What's Included:**

- **3 Core Security plugins** - OWASP Top 10 vulnerability detection, penetration testing, quick security scans
- **2 Compliance plugins** - HIPAA/PCI DSS/GDPR/SOC 2 compliance checking and documentation generation
- **2 Cryptography plugins** - Cryptographic implementation review and automated crypto auditing
- **3 Infrastructure Security plugins** - Threat modeling, Docker security scanning, API security auditing

---

## Prerequisites

### Required

- **Claude Code** (latest version recommended)
  - Download from: https://claude.com/code
  - Minimum version: 0.1.0

- **Operating System:**
  - macOS 12.0 or later
  - Linux (Ubuntu 20.04+, Debian 11+, or equivalent)
  - Windows 10/11 (via WSL2 recommended)

### Optional (For Full Functionality)

- **Docker** (for docker-security-scan command)
  - Install from: https://docs.docker.com/get-docker/
  - Minimum version: 20.10+

- **Python 3.8+** (for crypto-audit advanced features)
  - Recommended: Python 3.10 or later

- **Node.js 16+** (for API security testing)
  - Recommended: Node.js 18 LTS or later

---

## Installation Methods

### Method 1: Direct Installation (Recommended)

**Step 1: Download the Security Pro Pack**

Option A - From GitHub Releases:

```bash
# Download the latest release
curl -L https://github.com/jeremylongshore/claude-code-plugins/releases/download/security-pro-pack-v1.0.0/security-pro-pack.zip -o security-pro-pack.zip

# Extract the archive
unzip security-pro-pack.zip
```

Option B - From Gumroad (if purchased):

```bash
# Download from Gumroad dashboard
# Extract the ZIP file
unzip security-pro-pack.zip
```

**Step 2: Install via Claude Code**

```bash
# Install the entire pack
claude plugin install ./security-pro-pack

# Verify installation
claude plugin list | grep "security-pro-pack"
```

**Step 3: Verification**

Test that all plugins are installed correctly:

```bash
# Test a command plugin
/security-scan-quick --version

# Test an agent plugin (in Claude Code session)
# Ask: "Can you perform a security audit using the Security Auditor Expert?"
```

---

### Method 2: Manual Installation

**Step 1: Locate Claude Plugins Directory**

```bash
# macOS
PLUGIN_DIR="$HOME/.claude/plugins"

# Linux
PLUGIN_DIR="$HOME/.config/claude/plugins"

# Windows (WSL2)
PLUGIN_DIR="/mnt/c/Users/$USER/.claude/plugins"
```

**Step 2: Copy Plugin Files**

```bash
# Extract Security Pro Pack
unzip security-pro-pack.zip -d /tmp/security-pro-pack

# Copy to Claude plugins directory
cp -r /tmp/security-pro-pack "$PLUGIN_DIR/security-pro-pack"
```

**Step 3: Reload Claude Code**

```bash
# Restart Claude Code or run:
claude plugin reload
```

---

### Method 3: Git Clone (For Developers)

```bash
# Clone the repository
git clone https://github.com/jeremylongshore/claude-code-plugins.git

# Navigate to Security Pro Pack
cd claude-code-plugins/products/security-pro-pack

# Install from local directory
claude plugin install .
```

---

## Post-Installation Configuration

### Environment Variables (Optional)

Some plugins support additional configuration via environment variables:

```bash
# ~/.bashrc or ~/.zshrc

# API security audit authentication tokens
export CLAUDE_API_AUTH_TOKEN="your-test-api-token"

# Docker security scan custom registry
export DOCKER_REGISTRY="registry.example.com"

# Compliance docs organization name
export COMPLIANCE_ORG_NAME="YourCompany Inc"
```

### Docker Configuration (For docker-security-scan)

If using the Docker security scanning features:

```bash
# Verify Docker is running
docker ps

# Pull required images for testing (optional)
docker pull alpine:latest

# Test Docker socket access
docker info
```

### API Security Testing Setup (For api-security-audit)

For API security auditing features:

```bash
# Install optional dependencies for advanced testing
npm install -g newman  # For Postman collection testing

# Or install Python dependencies
pip install requests pytest
```

---

## Verification & Testing

### Quick Verification

Test each plugin category to ensure proper installation:

**1. Core Security:**

```bash
# Quick security scan
/ss

# Expected: Scan runs and completes without errors
```

**2. Compliance:**

```bash
# Generate HIPAA documentation
/compliance-docs-generate --framework hipaa

# Expected: Documentation files generated successfully
```

**3. Cryptography:**

```bash
# Crypto audit
/ca

# Expected: Cryptographic review completes
```

**4. Infrastructure Security:**

```bash
# Docker security scan
/dss nginx:latest

# Expected: Container security scan runs
```

### Full Plugin List Verification

```bash
# List all installed Security Pro Pack plugins
claude plugin list | grep -E "(security-auditor|penetration-tester|security-scan-quick|compliance-checker|compliance-docs-generate|crypto-expert|crypto-audit|threat-modeler|docker-security-scan|api-security-audit)"
```

Expected output:

```
 security-auditor-expert (agent)
 penetration-tester (agent)
 security-scan-quick (command, shortcut: ss)
 compliance-checker (agent)
 compliance-docs-generate (command, shortcut: cdg)
 crypto-expert (agent)
 crypto-audit (command, shortcut: ca)
 threat-modeler (agent)
 docker-security-scan (command, shortcut: dss)
 api-security-audit (command, shortcut: asa)
```

---

## Troubleshooting Installation Issues

### Issue: "Plugin not found"

**Solution:**

```bash
# Check plugin directory path
echo $HOME/.claude/plugins

# Verify Security Pro Pack directory exists
ls -la $HOME/.claude/plugins/security-pro-pack

# If missing, reinstall using Method 1
```

### Issue: "Permission denied"

**Solution:**

```bash
# Fix permissions
chmod -R 755 $HOME/.claude/plugins/security-pro-pack

# Ensure ownership
chown -R $USER:$USER $HOME/.claude/plugins/security-pro-pack
```

### Issue: Docker commands fail

**Solution:**

```bash
# Verify Docker is running
sudo systemctl status docker  # Linux
# or
open -a Docker  # macOS

# Check Docker socket permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "Command not found" for shortcuts

**Solution:**

```bash
# Reload Claude Code configuration
claude plugin reload

# Restart Claude Code application
# On macOS: Cmd+Q and relaunch
# On Linux: pkill claude && claude
```

### Issue: Validation errors during install

**Solution:**

```bash
# Verify package integrity (if downloaded from GitHub)
sha256sum security-pro-pack.zip
# Compare with SHA256 hash in release notes

# Re-download if checksums don't match
```

---

## Updating Security Pro Pack

### Check for Updates

```bash
# Check current version
claude plugin info security-pro-pack

# Check for latest version
curl -s https://api.github.com/repos/jeremylongshore/claude-code-plugins/releases/latest | grep tag_name
```

### Update Process

```bash
# Method 1: Update via CLI
claude plugin update security-pro-pack

# Method 2: Manual update
# 1. Download new version
# 2. Backup existing installation
mv $HOME/.claude/plugins/security-pro-pack $HOME/.claude/plugins/security-pro-pack.backup

# 3. Install new version
claude plugin install ./security-pro-pack-v1.1.0
```

---

## Uninstalling Security Pro Pack

### Complete Removal

```bash
# Uninstall via CLI
claude plugin uninstall security-pro-pack

# Verify removal
claude plugin list | grep security-pro-pack
# (Should return no results)
```

### Manual Removal

```bash
# Remove plugin directory
rm -rf $HOME/.claude/plugins/security-pro-pack

# Remove configuration (optional)
rm -f $HOME/.claude/config/security-pro-pack.json

# Reload Claude Code
claude plugin reload
```

---

## Next Steps

After successful installation:

1. **Quick Start Guide** - See `QUICK_START.md` for first-time usage
2. **Use Cases** - See `USE_CASES.md` for real-world scenarios
3. **Troubleshooting** - See `TROUBLESHOOTING.md` for common issues

---

## Support & Help

**Installation Issues:**

- GitHub Issues: https://github.com/jeremylongshore/claude-code-plugins/issues
- Email Support: [email protected]

**Documentation:**

- Full Documentation:
- Video Tutorials:

**Community:**

- GitHub Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions
- Slack:

---

**Installation Complete!**

You now have access to 10 powerful security plugins. Proceed to `QUICK_START.md` to begin using the Security Pro Pack.

**Security Pro Pack Team**
