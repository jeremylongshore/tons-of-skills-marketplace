---
title: "git replace Refs Can Swap Bytes Under a Pinned Commit"
description: "A local git replace ref makes git archive return replacement bytes under a pinned commit SHA. Release builds need --no-replace-objects on the command line."
date: "2026-11-12"
tags: ["git", "release-engineering", "supply-chain-security", "python", "ci-cd"]
featured: false
canonical: "https://startaitools.com/posts/git-replace-refs-swap-bytes-under-pinned-commit/"
---
A release builder that names its output with a pinned Git commit makes one claim: the files inside belong to that commit. A local Git replace ref can break that claim without changing the commit ID the builder writes down. By the end, you will know which Git flag closes the gap, why it has to sit on the command line, and which test proves it stays closed.

Replace refs are a normal Git feature, and most people never see them. A replace ref is a local pointer from one object to a substitute. You create one with `git replace <object> <replacement>`, and Git stores it under `refs/replace/<object>`. Most commands then read the replacement wherever the original object is requested. The original name does not change, but the bytes come from the substitute.

By default, a clone or fetch does not bring those refs along. That makes them local. A replace ref lives in the checkout that created it, so two checkouts of the same commit can return different file contents.

The failure has a specific shape. Release metadata can name the commit that was requested while the installer and the source archive contain the replacement bytes. Nothing in the label changes. The payload is what changed.

The package is audit-harness (the in-repo package of deterministic test-quality checks), and its source lives in the intent-audit-harness repository. Its release builder takes a tag and an expected full commit SHA, refuses to run if the tag resolves to any other commit, and writes four files: an installer script, a source archive, a `release.json` metadata file and a SHA256SUMS file covering the other three. The `release.json` file records the SHA. If the SHA is right and the bytes are wrong, the label is misleading. A checksum computed over those bytes matches them exactly, so the checksum cannot catch it.

## How the regression test sets the trap

The regression test is the part worth copying. It commits a second version of `install.sh`, points the original commit at that version with `git replace`, and then checks that `git show` returns the substitute. Only after that does it run the builder.

The order matters. A test that never confirms the substitution is live can pass for the wrong reason. Here the redirect is proven first, so a green result means the builder ignored a substitution that really existed.

After the build, three assertions must hold. The metadata still names the original commit. The installer on disk holds the original bytes. The `install.sh` inside the archive also holds the original bytes.

## The fix is a flag, not an environment variable

The fix goes on every Git read the builder makes. The original bytes come back only if Git skips replacement objects.

```python
def git(repo, *args):
    return subprocess.check_output(
        ["git", "--no-replace-objects", "-C", str(repo), *args], env=git_env(),
    )
```

The flag goes on the command line for a specific reason. The builder's `git_env()` helper strips every inherited `GIT_*` variable before it runs Git. That is deliberate, because a parent shell or a hook can point Git at a different repository. The cost is that `GIT_NO_REPLACE_OBJECTS`, the environment form of the same switch, gets stripped too. An environment variable would be silently dropped. A flag in the argument list survives.

The archive call builds its own argument list, so it needs the flag added directly. If only the helper were fixed, the archive would still be built from the substitute while every other read stayed clean.

The shebang check is another read of the same kind. The builder requires `install.sh`, read with `git show COMMIT:install.sh`, to start with `#!/usr/bin/env bash`. Before the flag, that check would have read whatever the replace ref pointed to.

## The rest of the builder's guards

The replacement fix is not the only guard on the provenance path. The builder accepts a tag only if it matches a `v`-prefixed SemVer pattern and resolves to the expected commit, which must be given as a full 40-hex SHA. The `package.json` version must equal the tag without its leading `v`.

Output goes into a directory created with mode `0o700`, and the builder refuses to write into an existing output directory. The gzip header uses `mtime=0`, so the archive header does not change between runs. `SHA256SUMS` covers the three payloads.

These guards do not defend against a replace ref on their own. The tag and version checks confirm names. The flag confirms bytes.

## What the evidence does not show

Three things are still soft. Weigh them before you copy the approach.

First, I did not rerun a separate local reproduction for this note. The evidence is the regression test and the pull request.

Second, the validation numbers live in the pull request body. It reports 13 release-asset tests passing, and a full `npm run check` passing in 131.50 seconds with all 306 source hashes unchanged. An automated adversarial review comment on the pull request noted those numbers are not linked to a CI run. Treat them as a claim until someone links the run.

Third, nothing here is a signed release. The release-assets spec calls the builder an implementation candidate, not a published or signed release, and no release or signing was performed. The spec also says checksums alone do not authenticate an installer. The release workflow is written to sign the checksum manifest with Cosign, but it has not yet run against a real release, and a mocked Cosign success in the unit suite is not signature qualification. No real signed release exists yet.

The parent packaging and signing work is still open. Rollback is a revert through the normal pull request process. The change is the merged pull request at https://github.com/jeremylongshore/intent-audit-harness/pull/242, merged 2026-11-12.

## Use this

- Put `--no-replace-objects` on the command line of every Git read in the builder, including `git archive`. Do not rely on an environment variable if the builder strips `GIT_*` variables.
- As a supplementary check, run `git replace -l` in every checkout your release builder reads from. Any output means a substitution is live in that checkout.
- Add a regression test that creates a real replacement ref, confirms ordinary `git show` returns the substitute, then asserts the builder still emits the original bytes.

## Related posts

[The first audit-harness release moved test gates into each repo](https://startaitools.com/posts/audit-harness-v010-enforcement-travels-with-code/)

[A marketplace install copied files but never ran the installer](https://startaitools.com/posts/copying-files-is-not-installing/)
