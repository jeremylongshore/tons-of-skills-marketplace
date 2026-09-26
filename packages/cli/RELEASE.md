# CLI Release Process

This document describes how to release new versions of `@intentsolutionsio/ccpi` to npm.

## Prerequisites

1. **npm account** with publish access to the `@intentsolutionsio` npm scope
2. **npm token** stored in GitHub secrets as `NPM_TOKEN`
3. **Write access** to the repository
4. **All tests passing** on main branch

## Release Checklist

### 1. Prepare Release

- [ ] Update version in `packages/cli/package.json`
- [ ] Add a dated entry to the root `CHANGELOG.md` (the GitHub Release notes link to it); flag breaking changes
- [ ] Test locally: `npm run build && node dist/index.js doctor`
- [ ] Commit changes: `git commit -am "chore(cli): bump version to X.Y.Z"`
- [ ] Push to main: `git push origin main`

### 2. Create Git Tag

```bash
# For version X.Y.Z
git tag cli-vX.Y.Z
git push origin cli-vX.Y.Z
```

**Example**:

```bash
git tag cli-v1.0.1
git push origin cli-v1.0.1
```

### 3. Automated Workflow Triggers

The publish job runs in the `npm-production` environment, so it waits for a maintainer to approve the deployment in GitHub Actions before anything reaches npm.

Once you push the tag, GitHub Actions will:

1. **Quality Gate** (`.github/workflows/cli-publish.yml`)
   - Run TypeScript type checking
   - Build the CLI
   - Verify package.json version matches tag
   - Run smoke tests (--version, --help, doctor)

2. **Publish to npm**
   - Install dependencies
   - Build for production
   - Publish with provenance to npm
   - Create GitHub Release with notes

3. **Verification**
   - Wait for npm registry propagation
   - Test installation from npm
   - Verify package works

### 4. Monitor Release

Watch the GitHub Actions workflow:

```
https://github.com/jeremylongshore/tons-of-skills-marketplace/actions
```

**Expected timeline**:

- Quality Gate: ~2 minutes
- npm Publish: ~1 minute
- Verification: ~2 minutes
- **Total**: ~5 minutes

### 5. Verify Release

After workflow completes:

```bash
# Test installation
npx @intentsolutionsio/ccpi@latest --version

# Should show new version
npx @intentsolutionsio/ccpi@X.Y.Z doctor
```

Check npm package page:

```
https://www.npmjs.com/package/@intentsolutionsio/ccpi
```

## Version Scheme (Semantic Versioning)

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes

**Examples**:

- `1.0.0` → `1.0.1`: Bug fix (patch)
- `1.0.1` → `1.1.0`: New feature (minor)
- `1.1.0` → `2.0.0`: Breaking change (major)

## Rollback Procedure

If a release has critical bugs:

### Option 1: Deprecate on npm

```bash
npm deprecate @intentsolutionsio/ccpi@X.Y.Z "Critical bug, use X.Y.Z-1"
```

### Option 2: Publish Hotfix

```bash
# Fix the bug
# Bump to X.Y.Z+1
git tag cli-vX.Y.Z+1
git push origin cli-vX.Y.Z+1
```

## Pre-release Versions

For testing before official release:

```bash
# Update package.json to X.Y.Z-beta.1
git tag cli-vX.Y.Z-beta.1
git push origin cli-vX.Y.Z-beta.1
```

Install pre-release:

```bash
npx @intentsolutionsio/ccpi@X.Y.Z-beta.1 doctor
```

## CI/CD Matrix

The test workflow runs on:

**Operating Systems**:

- ubuntu-latest
- macos-latest
- windows-latest

**Package Managers**:

- npm
- bun
- pnpm

**Node Versions**:

- 22.x
- 24.x

**Total Combinations**: 18, minus exclusions (Windows runs Node 22 only and skips bun) = 14 test runs.

**Deno**: a separate job runs a `--version` smoke test with Deno v1.x on ubuntu-latest and macos-latest (2 runs), for 16 runs in all. Source of truth: `.github/workflows/cli-test.yml`.

## Troubleshooting

### "Version mismatch" error

**Problem**: Git tag doesn't match package.json version

**Solution**:

```bash
# Delete local tag
git tag -d cli-vX.Y.Z

# Delete remote tag
git push origin :refs/tags/cli-vX.Y.Z

# Fix package.json version
# Create correct tag
git tag cli-vX.Y.Z
git push origin cli-vX.Y.Z
```

### "npm publish failed"

**Problem**: Package already exists at this version

**Solution**:

- Bump version to next patch (X.Y.Z+1)
- Never reuse version numbers

### "Quality gate failed"

**Problem**: Tests failing

**Solution**:

1. Check GitHub Actions logs
2. Fix failing tests locally
3. Commit fixes
4. Create new tag with patch version

## Emergency Hotfix

For critical production bugs:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Fix the bug
# Edit files...

# 3. Test thoroughly
npm run build
node dist/index.js doctor

# 4. Bump patch version
# Edit package.json: 1.0.0 → 1.0.1

# 5. Commit and tag
git commit -am "fix(cli): critical bug in doctor command"
git tag cli-v1.0.1
git push origin hotfix/critical-fix
git push origin cli-v1.0.1

# 6. Create PR to main
# 7. Merge after release is verified
```

## Release Notes Template

When creating manual release notes:

```markdown
## @intentsolutionsio/ccpi vX.Y.Z

### ✨ New Features

- Feature description

### 🐛 Bug Fixes

- Bug fix description

### 📚 Documentation

- Doc updates

### 🔧 Internal

- Internal changes

### 📦 Installation

\`\`\`bash
npx @intentsolutionsio/ccpi@X.Y.Z doctor
\`\`\`
```

## Post-Release

After successful release:

1. **Update website** (if CLI changes affect docs)
2. **Notify users** (Discussion post, if major release)
3. **Monitor npm stats** (downloads, issues)
4. **Track errors** (GitHub Issues)

## Release Schedule

**Patch releases**: As needed (bug fixes)
**Minor releases**: Monthly (new features)
**Major releases**: Quarterly (breaking changes)

## Links

- **npm Package**: https://www.npmjs.com/package/@intentsolutionsio/ccpi
- **GitHub Actions**: https://github.com/jeremylongshore/tons-of-skills-marketplace/actions
- **Issues**: https://github.com/jeremylongshore/claude-code-plugins/issues
