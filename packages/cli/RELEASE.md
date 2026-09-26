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
- [ ] Test locally: `pnpm -C packages/cli build && node packages/cli/dist/index.js doctor`
- [ ] Open a pull request with the bump (put `[skip auto-bump]` in the title so the bot does not add a patch bump) and merge it once the required checks pass
- [ ] Wait for the merge commit's own required checks on `main` (Validate Plugins, Secret Scan, Skill Conform) to finish green; the publish preflight requires them

### 2. Create Git Tag

Tag the commit on `main` that contains the bump. The publish preflight rejects any
commit that is not on `main` or lacks successful push-to-`main` runs of all three
required checks (`ci-required`, `gitleaks`, `skill-conform`); see
`scripts/npm-publication-preflight.mjs`.

```bash
# For version X.Y.Z, on an up-to-date main
git checkout main && git pull
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
   - Install (`--ignore-scripts`; the CLI needs no dependency install scripts)
   - Run TypeScript type checking and the CLI test suite
   - Build the CLI
   - Verify package.json version matches tag
   - Run smoke tests (--version, --help, doctor)

2. **Preflight**
   - Re-query the tagged commit's required checks on `main`; publish only if all three succeeded

3. **Publish to npm** (waits for `npm-production` approval)
   - Build for production
   - Publish with provenance: stable versions to the `latest` dist-tag, pre-release versions (containing `-`) to `next`
   - Create the GitHub Release, marked as a pre-release for pre-release versions

4. **Verification and evidence**
   - Wait for npm registry propagation, then install the exact published version
   - Emit signed publication evidence

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

Fix the bug and bump to X.Y.Z+1 in a pull request, merge it, wait for the merge
commit's required checks on `main`, then tag that commit:

```bash
git checkout main && git pull
git tag cli-vX.Y.Z+1
git push origin cli-vX.Y.Z+1
```

## Pre-release Versions

For testing before official release. A version containing a hyphen publishes to
the `next` dist-tag, so `latest` is untouched. It follows the same path as a
stable release: bump in a pull request, merge, then tag the commit on `main`.

```bash
# After X.Y.Z-beta.1 is merged to main
git tag cli-vX.Y.Z-beta.1
git push origin cli-vX.Y.Z-beta.1
```

Install pre-release:

```bash
npx @intentsolutionsio/ccpi@next doctor
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

A hotfix cannot be tagged on its branch: the publish preflight only accepts a
commit on `main` whose required checks passed there. Merge first, then tag.

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-fix main

# 2. Fix the bug, then test
pnpm -C packages/cli build && pnpm -C packages/cli test
node packages/cli/dist/index.js doctor

# 3. Bump the patch version in packages/cli/package.json (e.g. 3.0.0 -> 3.0.1)

# 4. Commit, push, and open a pull request ([skip auto-bump] in the title)
git commit -am "fix(cli): critical bug in doctor command"
git push origin hotfix/critical-fix

# 5. Merge once required checks pass; wait for the merge commit's checks on main

# 6. Tag the merge commit
git checkout main && git pull
git tag cli-v3.0.1
git push origin cli-v3.0.1
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

Releases are cut as needed; there is no fixed cadence. Only 1.0.0, 2.0.0, and
2.0.3 were published before 3.0.0.

## Links

- **npm Package**: https://www.npmjs.com/package/@intentsolutionsio/ccpi
- **GitHub Actions**: https://github.com/jeremylongshore/tons-of-skills-marketplace/actions
- **Issues**: https://github.com/jeremylongshore/tons-of-skills-marketplace/issues
