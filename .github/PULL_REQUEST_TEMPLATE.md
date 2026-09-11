# Pull Request

> 📘 **First time contributing?** Read both:
>
> 1. [CONTRIBUTING.md](CONTRIBUTING.md) § Before You Submit — the contract and the workflow
> 2. **Plugin & Skill Spec** (v3.6.0 baseline; enforced schema 3.15.2 — see `000-docs/SCHEMA_CHANGELOG.md`) — the authoritative spec the validator scores against (8-field frontmatter, 7 body sections, 100-point rubric, all source-cited)
>
> The PR Pre-screen workflow sets an advisory `prescreen-grade` status on every
> run and posts a structured comment with the exact validator findings only when
> changes are needed (silent on PASS) — reading both up front saves a round-trip.

## Type of Change

<!-- Select all that apply -->

- [ ] 🔌 New plugin submission
- [ ] ⬆️ Plugin update/enhancement
- [ ] 📚 Documentation improvement
- [ ] 🐛 Bug fix
- [ ] 🏗️ Infrastructure/CI improvement
- [ ] 🎨 Marketplace website update
- [ ] 🔧 Configuration change
- [ ] 🧪 Tests added/updated
- [ ] 🔐 Security fix
- [ ] 🚀 Performance improvement
- [ ] ♻️ Refactoring
- [ ] 🌐 Translation/i18n
- [ ] 🗑️ Deprecation/removal
- [ ] 📦 Dependency update
- [ ] 🎯 Other (please describe)

## Description

<!-- Provide a clear and concise description of your changes -->

**Summary:**

**Motivation:**

**Related Issues:**

<!-- Link to related issues: Closes #123, Fixes #456 -->

## Submission Standard (plugin & source submissions)

<!-- Required for new plugin/source submissions — see
     000-docs/700-DR-GUID-skill-submission-standard.md and templates/skill-docs/ -->

- [ ] This PR links its submission issue (`Closes #N` / `Refs #N`) — submissions start
      as an issue using the plugin-submission template; a PR without one will be asked
      to file it
- [ ] The required docs for my declared tier are included (`docs/PRD.md` at minimum —
      see the [tier→docs matrix](../templates/skill-docs/README.md))
- [ ] Validator run locally (`python3 scripts/validate-skills-schema.py --marketplace --verbose <plugin-dir>`)
- [ ] For `feat(sources)` PRs: source vetted per the
      [external-source vetting playbook](../000-docs/699-DR-GUID-external-source-vetting-playbook.md)
- [ ] `verified:` / `curated:` flags in `sources.yaml` are honest (no `verified: true`
      without maintainer vetting; no silently hardened mirrors without `curated: true`)

## Security

- Related alerts: GHSA-/CVE-
- Impact assessment: None / Low / Medium / High

## Plugin Details (for plugin submissions/updates)

**Plugin Name:**
**Category:**
**Version:**
**Keywords:**

**Components Included:**

- [ ] Commands (how many: )
- [ ] Agents (how many: )
- [ ] Hooks (how many: )
- [ ] Scripts (how many: )
- [ ] MCP servers

**Dependencies:**

<!-- List any external dependencies required -->

## Checklist

### For All PRs

- [ ] I have read the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines
- [ ] "Allow edits by maintainers" is enabled (fork PRs) — we push small regen/bump fixes to your branch instead of round-tripping
- [ ] My code follows the project's style and conventions
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] My changes generate no new warnings or errors
- [ ] Documentation has been updated (if applicable)
- [ ] CodeQL passes; no new code scanning alerts
- [ ] No high/critical Dependabot alerts introduced

### For Plugin Submissions/Updates

- [ ] Plugin has valid `.claude-plugin/plugin.json` with all required fields
- [ ] `plugin.json` validated with `jq empty plugin.json`
- [ ] README.md is comprehensive with installation, usage, and examples
- [ ] LICENSE file is included (MIT or Apache-2.0 recommended)
- [ ] All shell scripts are executable (`chmod +x scripts/*.sh`)
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Marketplace.json has been updated with plugin entry
- [ ] Plugin tested locally with `/plugin install`
- [ ] Commands include YAML frontmatter (name, description)
- [ ] Agents include YAML frontmatter (name, description, model)
- [ ] Hooks use `${CLAUDE_PLUGIN_ROOT}` for portable paths
- [ ] All JSON files are valid (`jq empty *.json`)

### For Marketplace Website Changes

- [ ] Website builds successfully (`cd marketplace && npm run build`)
- [ ] No broken links or missing assets
- [ ] Mobile-responsive design verified
- [ ] SEO metadata updated (if applicable)
- [ ] Accessibility standards followed (WCAG 2.1)

### For Documentation Changes

- [ ] Spelling and grammar checked
- [ ] Code examples tested and working
- [ ] Links verified and not broken
- [ ] Screenshots/diagrams updated (if applicable)
- [ ] Version references updated

## Testing Evidence

<!-- Describe how you tested your changes -->

**Test Environment:**

- OS:
- Claude Code Version:
- Python Version (if applicable):
- Node Version (if applicable):

**Test Commands Run:**

```bash
# Example:
/plugin install my-plugin@test
/my-command --option value
```

**Test Results:**

<!-- Paste relevant output, screenshots, or describe results -->

**Edge Cases Tested:**

- [ ] Works with minimal configuration
- [ ] Handles errors gracefully
- [ ] Works across different platforms (macOS, Linux, Windows)
- [ ] Performance is acceptable for large inputs
- [ ] Security considerations addressed

## Breaking Changes

<!-- Does this PR introduce any breaking changes? -->

- [ ] Yes (describe below)
- [ ] No

**If yes, describe:**

## Screenshots / Recordings (if applicable)

<!-- Add screenshots or recordings showing your changes in action -->

## Performance Impact

<!-- Does this change affect performance? -->

- [ ] No performance impact
- [ ] Minor performance impact (negligible)
- [ ] Moderate performance impact (describe below)
- [ ] Significant performance impact (describe and justify below)

## Security Considerations

<!-- REQUIRED for all plugin submissions - see SECURITY.md -->

### Automated Security Scans

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] No AWS keys, private keys, or credentials detected
- [ ] No destructive commands (`rm -rf /`, data deletion)
- [ ] No `eval()` or command injection risks
- [ ] No suspicious curl/wget to IP addresses
- [ ] No base64 obfuscation detected
- [ ] All URLs use HTTPS (except localhost)
- [ ] No URL shorteners (potential phishing)

### Manual Security Review

- [ ] **Prompt Injection Protection**: No hidden instructions that hijack Claude's behavior
- [ ] **Data Privacy**: No data exfiltration to external servers (all network calls documented in README)
- [ ] **Permission Audit**: Plugin requests minimal necessary permissions only
- [ ] **Clear Intent**: README clearly explains what the plugin does
- [ ] **Input Validation**: All user inputs validated before processing
- [ ] **Error Handling**: No sensitive data in error messages
- [ ] **Dependencies**: All npm dependencies reviewed (for MCP plugins)

### Testing

- [ ] Tested in isolated environment before submission
- [ ] No unexpected side effects observed
- [ ] Graceful error handling for edge cases
- [ ] Works as documented in README

## Rollback Plan

<!-- How can these changes be rolled back if needed? -->

## Additional Notes

<!-- Any other information reviewers should know -->

## Reviewer Checklist (for maintainers)

- [ ] Code quality meets standards
- [ ] Tests pass (CI/CD green)
- [ ] Security review completed
- [ ] Documentation is clear and complete
- [ ] Breaking changes documented
- [ ] Version bumped appropriately
- [ ] CHANGELOG.md updated
- [ ] Ready to merge

---

**By submitting this PR, I confirm:**

- [ ] I have the right to submit this code under the project's license
- [ ] I understand my contributions will be publicly available
- [ ] I agree to the project's [Code of Conduct](../CODE_OF_CONDUCT.md)
