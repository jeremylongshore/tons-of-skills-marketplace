# Release Checklist

Use this checklist for all future releases of the Claude Code Plugins Marketplace.

---

## Pre-Release Verification

- [ ] **All critical/high priority issues closed** for milestone
  ```bash
  gh issue list --milestone "vX.Y.Z" --label "priority:critical,priority:high" --state open
  ```

- [ ] **Tests pass** (validation scripts)
  ```bash
  ./scripts/validate-all.sh plugins
  ./scripts/test-installation.sh plugins/devops/git-commit-smart
  ```

- [ ] **No uncommitted changes**
  ```bash
  git status --porcelain
  ```

- [ ] **No broken links** in documentation
  ```bash
  # Check for dead links in markdown files
  find . -name "*.md" -exec grep -H "http" {} \;
  ```

---

## Version & Changelog

- [ ] **Determine bump type** based on changes
  - **major**: Breaking changes (BREAKING CHANGE in commits)
  - **minor**: New features (feat: commits)
  - **patch**: Bug fixes (fix: commits)

- [ ] **Update version** in relevant files
  ```bash
  # Update marketplace.json
  jq '.metadata.version = "X.Y.Z"' .claude-plugin/marketplace.json > tmp && mv tmp .claude-plugin/marketplace.json

  # Commit version bump
  git add .claude-plugin/marketplace.json
  git commit -m "chore: bump version to vX.Y.Z"
  ```

- [ ] **Update CHANGELOG.md** (newest entry on top)
  - Release date: `YYYY-MM-DD`
  - Version header: `## [X.Y.Z] - YYYY-MM-DD`
  - Categories: Added, Changed, Fixed, Removed, Security, Infrastructure
  - Metrics: plugins added, issues fixed, contributions
  - Migration notes (if breaking changes)

- [ ] **Commit changelog**
  ```bash
  git add CHANGELOG.md
  git commit -m "docs: update changelog for vX.Y.Z"
  ```

---

## Documentation Sync

- [ ] **Update README.md** version references
  - Check badge versions
  - Update "Last Updated" date
  - Verify installation instructions
  - Update statistics section

- [ ] **Update plugin READMEs** if needed
  - Check for outdated examples
  - Verify installation commands
  - Update version references

- [ ] **Verify docs/ consistency**
  - All guides reference correct version
  - Links are not broken
  - Examples are up-to-date

- [ ] **Commit documentation updates**
  ```bash
  git add README.md docs/ plugins/
  git commit -m "docs: sync version references to vX.Y.Z"
  ```

---

## Create Tag & Release

- [ ] **Create annotated Git tag**
  ```bash
  git tag -a vX.Y.Z -m "Release vX.Y.Z

  ## Highlights
  - [Key feature 1]
  - [Key feature 2]
  - [Key improvement 3]

  See CHANGELOG.md for complete details."
  ```

- [ ] **Push tag to repository**
  ```bash
  git push origin vX.Y.Z
  ```

- [ ] **Create GitHub release**
  ```bash
  gh release create vX.Y.Z \
    --title " Release vX.Y.Z" \
    --notes-file CHANGELOG.md \
    --latest
  ```

---

## Deployment

### For New Plugins

- [ ] **Validate plugin structure**
  ```bash
  ./scripts/validate-all.sh plugins/category/plugin-name
  ./scripts/test-installation.sh plugins/category/plugin-name
  python3 scripts/check-frontmatter.py plugins/category/plugin-name/commands/*.md
  ```

- [ ] **Add to marketplace catalog**
  ```bash
  # Manually edit .claude-plugin/marketplace.json
  # Or use jq to add programmatically
  ```

- [ ] **Update README.md** with new plugin

### For Documentation

- [ ] **Verify documentation site** (if applicable)
  ```bash
  cd docs
  # Build and test docs site
  cd ..
  ```

- [ ] **Check GitHub Pages** deployment (if enabled)

### For Scripts/Tools

- [ ] **Ensure all scripts executable**
  ```bash
  chmod +x scripts/*.sh scripts/*.py
  find plugins -name "*.sh" -exec chmod +x {} \;
  ```

---

## Announcement

- [ ] **Create release announcement issue**
  ```bash
  gh issue create \
    --title " Release vX.Y.Z Available" \
    --body "We're excited to announce vX.Y.Z!

  ##  Highlights
  - [Key feature 1]
  - [Key feature 2]
  - [Key improvement 3]

  ##  New Plugins
  - **plugin-name**: [Description]

  ##  Improvements
  - [Improvement 1]
  - [Improvement 2]

  ##  Full Changelog
  See the [complete changelog](https://github.com/jeremylongshore/claude-code-plugins/blob/main/000-docs/247-OD-CHNG-changelog.md#xyz---yyyy-mm-dd) for all details.

  ##  Upgrade
  \`\`\`bash
  /plugin marketplace add jeremylongshore/claude-code-plugins
  /plugin install plugin-name@claude-code-plugins
  \`\`\`

  ##  Feedback
  Let us know what you think in the [discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)!" \
    --label "announcement,release"
  ```

- [ ] **Pin the announcement issue**
  ```bash
  gh issue pin <issue-number>
  ```

- [ ] **Post in GitHub Discussions** (Announcements category)
  - Brief summary
  - Link to GitHub release
  - Call to action (try it out!)

- [ ] **Share on social media** (optional)
  - Twitter/X thread
  - LinkedIn post
  - Dev.to article

---

## Archive & Cleanup

- [ ] **Archive release artifacts**
  ```bash
  # Create archive directory
  mkdir -p .github/releases/vX.Y.Z/

  # Copy artifacts
  cp CHANGELOG.md .github/releases/vX.Y.Z/changelog.md
  gh issue list --milestone "vX.Y.Z" --json number,title,state > .github/releases/vX.Y.Z/issues.json
  gh pr list --search "milestone:vX.Y.Z" --json number,title,mergedAt > .github/releases/vX.Y.Z/prs.json

  # Commit archive
  git add .github/releases/vX.Y.Z/
  git commit -m "chore: archive vX.Y.Z release artifacts"
  git push
  ```

- [ ] **Close milestone**
  ```bash
  gh milestone close "vX.Y.Z"
  ```

- [ ] **Remove temporary files**
  ```bash
  rm -rf _PRESERVE_MIGRATION/  # If still exists
  ```

---

## Post-Release

- [ ] **Monitor for issues**
  - Watch GitHub issues
  - Check discussions
  - Respond to community feedback

- [ ] **Update project board** (if using)
  - Move completed items
  - Plan next milestone

- [ ] **Schedule next release** (optional)
  ```bash
  gh milestone create "vX.Y.Z+1" \
    --title "Next Release" \
    --description "Planned improvements for next release" \
    --due-date "YYYY-MM-DD"
  ```

- [ ] **Thank contributors**
  - Comment on their PRs
  - Update CONTRIBUTORS.md (if exists)
  - Mention in release announcement

---

## Quick Reference Commands

### Check Release Readiness
```bash
# Issues check
gh issue list --milestone "vX.Y.Z" --state open

# Tests
./scripts/validate-all.sh plugins

# Status
git status --porcelain
```

### Version Bump
```bash
# Update marketplace.json version
jq '.metadata.version = "X.Y.Z"' .claude-plugin/marketplace.json > tmp && mv tmp .claude-plugin/marketplace.json
git add .claude-plugin/marketplace.json
git commit -m "chore: bump version to vX.Y.Z"
```

### Changelog & Tag
```bash
# Edit CHANGELOG.md manually, then:
git add CHANGELOG.md
git commit -m "docs: update changelog for vX.Y.Z"

# Create tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### Release
```bash
gh release create vX.Y.Z --title "Release vX.Y.Z" --notes-file CHANGELOG.md --latest
```

### Announce
```bash
gh issue create --title " Release vX.Y.Z" --body "..." --label "announcement,release"
```

---

**This checklist is based on the master-github-repo-release system.**
**Last Updated**: 2025-10-10
