# DevOps Automation Pack - Installation Guide

**Time Required:** 5 minutes
**Difficulty:** Beginner
**Last Updated:** October 2025

---

## Prerequisites

Before you start, make sure you have:

- Claude Code version 1.5 or higher installed
- Command line access (Terminal on Mac/Linux, PowerShell on Windows)
- 10 MB free disk space
- Internet connection for download

**Check your Claude Code version:**

```bash
claude --version
```

You should see version 1.5.0 or higher.

---

## Quick Installation

Follow these three steps to get the DevOps Automation Pack running:

### Step 1: Download the Pack

After purchasing, you'll receive a download link via email.

1. Click the **"Download Pack"** button in your purchase email
2. Save `DevOps_Automation_Pack.zip` to your Downloads folder
3. The file is 8.2 MB and downloads in seconds

### Step 2: Extract the Files

**On Mac or Linux:**

```bash
cd ~/Downloads
unzip DevOps_Automation_Pack.zip
cd DevOps_Automation_Pack
```

**On Windows:**

1. Open your Downloads folder
2. Right-click `DevOps_Automation_Pack.zip`
3. Select **"Extract All..."**
4. Click **"Extract"**
5. Open the extracted folder

### Step 3: Install to Claude Code

From inside the pack directory, run:

```bash
claude plugin install .
```

Expected output:

```
 Installing devops-automation-pack...
 Loaded 25 commands
 Loaded 6 agents
 Installation complete!

Try: /commit-smart to get started
```

**Installation complete!**

---

## Verification

Let's confirm everything installed correctly.

### Check Available Commands

Run this command:

```bash
claude plugin list
```

You should see `devops-automation-pack` in the list.

### Test a Command

Try the smart commit command:

```bash
/commit-smart
```

If you see the command prompt for Git status, it's working!

### View All Commands

See everything you installed:

```bash
/help | grep devops
```

You'll see all 25 commands with their shortcuts.

---

## What You Installed

Congratulations! You now have access to **25 professional DevOps plugins**:

### Git Workflow (5 plugins)

- `/commit-smart` (gc) - Generate conventional commits with AI
- `/pr-create` (gpr) - Create pull requests with templates
- `/branch-create` (bc) - Create feature branches with naming conventions
- `/merge-safe` (ms) - Safe merge with conflict detection
- `/rebase-interactive` (ri) - Interactive rebase workflow

### CI/CD Automation (6 plugins)

- `/github-actions-create` (gha) - Generate GitHub Actions workflows
- `/gitlab-ci-create` (glci) - Generate GitLab CI pipelines
- `/circleci-config` (cci) - Generate CircleCI configuration
- `/pipeline-optimize` (po) - Analyze and optimize slow pipelines
- `/deployment-strategy` (ds) - Recommend deployment approach
- **CI/CD Expert Agent** - Pipeline design specialist

### Docker (4 plugins)

- `/dockerfile-generate` (dg) - Create optimized Dockerfiles
- `/docker-compose-create` (dcc) - Generate docker-compose.yml files
- `/docker-optimize` (do) - Reduce image size and build time
- **Docker Specialist Agent** - Container optimization expert

### Kubernetes (4 plugins)

- `/k8s-manifest-generate` (km) - Generate Kubernetes manifests
- `/k8s-helm-chart` (kh) - Create Helm charts
- `/k8s-troubleshoot` (kt) - Debug pod failures and issues
- **Kubernetes Expert Agent** - K8s orchestration specialist

### Terraform (4 plugins)

- `/terraform-module-create` (tm) - Generate reusable modules
- `/terraform-plan-analyze` (tpa) - Analyze plans for risks
- `/cloudformation-generate` (cfn) - Create CloudFormation templates
- **Terraform Architect Agent** - Infrastructure as code expert

### Deployment (2 plugins)

- `/monitoring-setup` (ms) - Set up Prometheus + Grafana
- **Deployment Specialist Agent** - Release management expert

**Total:** 19 commands + 6 specialized agents = 25 powerful plugins

---

## First Test

Let's run your first command to see the pack in action.

### Create a Smart Git Commit

If you're in a Git repository with changes:

```bash
/commit-smart
```

The command will:

1. Analyze your Git changes
2. Review recent commit messages for style
3. Generate a conventional commit message
4. Show you the commit before creating it

**Example output:**

```
 Analyzing changes...
 Found 3 modified files
 Reviewed commit history

Suggested commit:
feat(auth): add password reset functionality

- Implement password reset email flow
- Add reset token validation
- Update user model with reset fields

Create this commit? (y/n):
```

Type `y` and press Enter. Your commit is created!

> **Tip:** You can use the shortcut `/gc` instead of typing the full command name.

---

## Troubleshooting

### Error: "Command not found"

**Symptoms:**

- Running `/commit-smart` shows "unknown command"
- Plugins don't appear in `/help`

**Solution:**

1. Restart Claude Code completely
2. Reopen Claude Code
3. Run `/help` again to verify commands appear

If still not working:

```bash
claude plugin install ~/Downloads/DevOps_Automation_Pack
```

---

### Error: "Permission denied"

**Symptoms:**

- Installation fails with permission error
- Cannot execute installation script

**Solution:**

**On Mac/Linux:**

```bash
chmod +x install.sh
./install.sh
```

**On Windows:**

1. Right-click PowerShell
2. Select "Run as Administrator"
3. Run installation command again

---

### Error: "Plugin already installed"

**Symptoms:**

- Installation says pack already exists
- Want to reinstall or upgrade

**Solution:**

Uninstall the old version first:

```bash
claude plugin uninstall devops-automation-pack
claude plugin install ~/Downloads/DevOps_Automation_Pack
```

This removes the old version and installs the new one.

---

### Commands work but give errors

**Symptoms:**

- Commands run but produce unexpected errors
- Features don't work as described

**Possible causes and solutions:**

**1. Git not configured:**

```bash
git config --global user.name "Your Name"
git config --global user.email "[email protected]"
```

**2. Not in a Git repository:**

```bash
cd /path/to/your/project
git init  # if needed
```

**3. Missing dependencies:**

Some commands require:

- Git (for Git workflow commands)
- Docker (for Docker commands)
- kubectl (for Kubernetes commands)
- terraform (for Terraform commands)

Install only what you need for the commands you'll use.

---

## Getting Help

### Documentation

- **Quick Start Guide:** `docs/QUICK_START.md` - Your first 5 minutes with the pack
- **Use Cases:** `docs/USE_CASES.md` - Real-world examples
- **Troubleshooting:** `docs/000-docs/157-DR-FAQS-troubleshooting.md` - Detailed problem solutions

### Support

**Email:** mandy@intentsolutions.io

When contacting support, include:

1. **Error message** (exact text - copy and paste it)
2. **Command you ran** (what you typed)
3. **Your setup:**
   - Operating system (Mac, Linux, Windows)
   - Claude Code version (run `claude --version`)
   - Which plugin caused the error

**We respond within 24 hours.**

### Community

- **GitHub Issues:** Report bugs and request features
- **GitHub Discussions:** Ask questions and share tips at https://github.com/jeremylongshore/claude-code-plugins/discussions
- **Documentation Updates:** Check back for new guides

---

## What's Next?

Now that you've installed the pack, here's what to do:

### 1. Try the Quick Start (5 minutes)

See `docs/QUICK_START.md` for a guided first task.

You'll learn to:

- Create a feature branch
- Make changes
- Generate a smart commit
- Create a pull request

All in 5 minutes!

### 2. Explore Use Cases

See `docs/USE_CASES.md` for real-world examples:

- Setting up a new project with CI/CD
- Optimizing Docker images
- Deploying to Kubernetes
- Creating infrastructure with Terraform
- And more...

### 3. Learn the Commands

Run `/help` and look for commands that match your workflow.

Each command has:

- A full name (e.g., `/commit-smart`)
- A shortcut (e.g., `/gc`)
- Built-in help (e.g., `/commit-smart --help`)

### 4. Use the Agents

The 6 specialized agents activate automatically when you:

- Ask about CI/CD pipelines
- Work with Docker files
- Debug Kubernetes issues
- Write Terraform code
- Plan deployments

Just ask Claude naturally, and the right expert will help!

---

**Installation Complete!**

You're all set. Start using the DevOps Automation Pack to save hours every week.

Need help? See `docs/000-docs/157-DR-FAQS-troubleshooting.md` or email mandy@intentsolutions.io

---

**Document Version:** 1.0.0
**Pack Version:** 1.0.0
**Last Updated:** October 10, 2025
