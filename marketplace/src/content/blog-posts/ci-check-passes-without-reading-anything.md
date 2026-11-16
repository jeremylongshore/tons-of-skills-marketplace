---
title: "CI Check Passes Without Reading What It Claims to Check"
description: "A check has to name what it looked at, and that has to be the real thing. Three checks got it wrong on one day, and the rule that fixes them is the same."
date: "2026-11-15"
tags: ["ci-cd", "testing", "debugging", "devops"]
featured: false
canonical: "https://startaitools.com/posts/ci-check-passes-without-reading-anything/"
---
Three of our checks gave the wrong answer on the same day, and one rule fixes all three: a check has to say what it looked at, and what it looked at has to be the real thing. A check on how much input each helper script reads answered PASS while the nine Perl helper scripts it was supposed to check went unread. A screenshot scanner reported green while its plugin did nothing. One test environment rejected a correct plugin, because the machine it ran on was not set up like a normal install.

If you trust a passing check to have looked at the thing it claims to check, the three failures below are worth your time. Each one is a different kind of check: one that reads files, one that reads a folder, and one that reads the environment it runs in.

## How does a CI check pass without reading what it claims to check?

A CI (continuous integration) check can pass without reading what it claims to check because nothing required the verdict to name the files it opened. One check matched only shell scripts, so it printed PASS over a corpus (the set of files the check covered) of one git hook, and a coverage reporter that checks whether each gate ran had to call that gate UNPROVEN.

| Check | What it set out to do | What it actually did |
|---|---|---|
| Gate C42 | Make sure each shipped runtime script limits how much input it reads before it stores or sorts it | Matched shell only, so it never opened the Perl helpers and printed PASS over a corpus of one git hook |
| Screenshot scanner | Read the screenshots the plugin wrote into the folder it resolved | Resolved `~/Pictures`, one level above the folder Omasnap writes into, so the inbox was always empty |
| Rig first-run hook | Make a first run look like a new plugin user | Wiped `~/.local/state/omarchy` and took the current-theme state with it, so the render's QML warnings came from first-party code |

## Three checks that gave the wrong answer

Our desktop plugins are built for Omarchy, an opinionated Arch Linux desktop setup. Their helper scripts run on a timer and read the user's home directory, so a CI gate in our shared contributor tooling makes sure each helper limits how much input it reads before it stores or sorts it. That gate is numbered C42. Its verdicts are PASS, WARN, and SKIP for nothing to check.

### The gate that scanned one file and answered PASS

Its file selector matched shell only: the `.sh` and `.bash` extensions, and any file whose first line was a shell shebang (the `#!` line that names the interpreter). It missed the `.pl` and `.pm` extensions and any Perl shebang. A sibling gate in the same lane (the shared contributor tooling that ships inside each plugin) had already been widened to match a Perl shebang, [and this one was not](https://startaitools.com/posts/a-path-is-not-proof-of-identity/). The screenshot scanner the rule was written for, `bin/capture-conveyor-scan`, had been rewritten in Perl, so the selector never opened it. The gate's own header comment cites that file as the reason the rule exists.

The verdict was a PASS over a corpus of one git hook. The plugin fleet's [coverage reporter called the gate UNPROVEN](https://startaitools.com/posts/the-lane-that-reviewed-nothing/), and that call is the only reason the fiction broke.

```bash
# Before: shell only. A Perl helper never matched the selector, so the gate
# answered PASS over a corpus of one git hook.
gate_tree_files '\.(sh|bash)$'
gate_tree_files '(^|/)[^./]+$' | while IFS= read -r rel; do
  first=$(/usr/bin/head -n1 "$GATE_TREE_DIR/$rel" 2>/dev/null || true)
  case "$first" in \#\!*sh*) printf '%s\n' "$rel" ;; esac
done

# After: shell or Perl, matched by extension or by shebang.
gate_tree_files '\.(sh|bash|pl|pm)$'
gate_tree_files '(^|/)[^./]+$' | while IFS= read -r rel; do
  first=$(/usr/bin/head -n1 "$GATE_TREE_DIR/$rel" 2>/dev/null || true)
  case "$first" in \#\!*sh*|\#\!*perl*) printf '%s\n' "$rel" ;; esac
done
```

The runtime helpers are extensionless, so the selector cannot be an extension list alone. A file is in scope when its name ends in `.sh`, `.bash`, `.pl` or `.pm`, or when its first line is a shell or Perl shebang. Dev tooling stays out. `scripts/`, `tests/`, `e2e/` and `.github/` never run on a user's machine.

### The scanner whose fixture agreed with the code

The second failure sat in a proof rig (an isolated container that renders a plugin and records what it saw). Omarchy takes screenshots with Omasnap, which writes into `~/Pictures/Screenshots`. The scanner resolved the folder from `OMARCHY_SCREENSHOT_DIR`, then `XDG_PICTURES_DIR`, then `user-dirs.dirs`, then `~/Pictures`. On a stock install that last fallback lands one level above the folder screenshots actually go into, so the inbox was always empty.

The rig fixture seeded `~/Pictures` and asserted that the resolved directory ended in `/Pictures`. Both halves were true, the plugin did nothing, and the receipt (a machine-written record proving a step really ran) said green.

```perl
# After: the folder is resolved in Omasnap's own order.
sub screenshot_directory {
    for my $name (qw(OMASNAP_SCREENSHOT_DIR OMARCHY_SCREENSHOT_DIR)) {
        my $value = $ENV{$name} // '';
        return $value if length($value);
    }
    return '' unless $home_usable;

    my $conf = read_pinned_config("$config_home/omasnap", 'omasnap.conf');
    if (defined $conf) {
        my $configured = omasnap_output_directory($conf);
        return $configured if defined $configured;
    }
    my $user_dirs = read_pinned_config($config_home, 'user-dirs.dirs');
    if (defined $user_dirs) {
        my $pictures = user_dirs_pictures($user_dirs);
        return "$pictures/Screenshots" if defined $pictures;
    }
    return "$home/Pictures/Screenshots";
}
```

The folder is now resolved in Omasnap's own order, and two details in that order matter. The `XDG_PICTURES_DIR` environment variable is gone, because neither Omasnap nor Qt reads it. The `omasnap.conf` step was added on purpose: Omasnap reads its own config between the environment and its default, so skipping it would reproduce the empty inbox for anyone who set a directory there. `user-dirs.dirs` is read the way Qt reads it, so an unquoted absolute path works.

### The rig that deleted the state it was measuring

The third failure is the one that looks most like a defect in the plugin under test, and it is not one. The live first-run hook, the script that wipes the machine to fake a new plugin user, deletes `~/.local/state/omarchy` and its cache directory. That wipe also removed the current-theme state every Omarchy install carries. On the rig upgraded to current Omarchy (74de104, Qt 6.12), the first-party image-picker and lock plugins log QML warnings, and the render refuses every live run.

The warnings came from first-party code, not from the plugin under test. The render was right to refuse.

```bash
rm -rf "$HOME/.local/state/omarchy" "$HOME/.cache/omarchy"
mkdir -p "$HOME/.local/state/omarchy" "$HOME/.config/omarchy/plugins"
# A first-run plugin user still has an Omarchy theme. Restore the three
# entries omarchy-theme-set writes.
current="$HOME/.local/state/omarchy/current"
mkdir -p "$current"
ln -nsf /root/omarchy/themes/tokyo-night "$current/theme"
printf 'tokyo-night\n' > "$current/theme.name"
ln -nsf "$current/theme/backgrounds/0-liftoff.webp" "$current/background"
```

That fix had a fork in it, and Claude Opus 5 5 took the branch we agreed with. The render refused every run because the test rig's isolated home had none of the theme state a normal install carries. The options were to seed that state, or to narrow the QML warning filter to the plugin's own paths. The change seeded the state, and wrote down why: a plugin can also cause a warning inside a first-party component it calls, so a filter scoped to your own paths would hide a real defect.

## The rule: say what you looked at, and look at the real thing

**Name the corpus.** A PASS names every file it read, by language. The gate ends its verdict with that list, and it refuses to count a file it could not open.

**An empty corpus is a skip.** If the selector matched nothing, the gate reports SKIP and says why. Before the fix, an empty corpus and a clean corpus printed the same word, and no reader could tell them apart. [The lane runner used to fold SKIP into the pass column, and that gap was closed first](https://startaitools.com/posts/the-skip-that-counted-as-a-pass/).

**A fixture must not agree with the code.** The scanner's rig seeded `~/Pictures` and asserted that the resolved directory ended in `/Pictures`. The code and the fixture agreed, and the application never writes there. The fix went into the resolution order, so the scanner follows whatever the user configured.

**The environment has to be the real one.** The rig's first-run hook deleted the state every install carries, and a correct render refused a correct plugin. The fix was to seed the state a normal install has. Narrowing the warning filter to the plugin's own paths would have hidden a real defect, because a plugin can also cause a warning inside a first-party component it calls.

**A zero exit code is not a success.** A zero exit status says the tool ran. It does not say the tool did the thing you asked.

```bash
# The analyzer's first output line names the language it analyzed. A file it
# could not open prints nothing at all, and an unopened file is never counted
# as scanned.
case "${RESULT%%$'\n'*}" in
  "LANG perl")  SCANNED_PERL+=("$REL") ;;
  "LANG shell") SCANNED_SHELL+=("$REL") ;;
  *) continue ;;
esac

SCANNED=$(( ${#SCANNED_SHELL[@]} + ${#SCANNED_PERL[@]} ))

if (( SCANNED == 0 )); then
  gate_skip "no shipped shell or Perl runtime file to scan (scripts/, tests/, e2e/ and .github/ are excluded as dev tooling)"
fi

CORPUS=""
if (( ${#SCANNED_SHELL[@]} > 0 )); then
  CORPUS="shell: $(corpus_names "${SCANNED_SHELL[@]}")"
fi
if (( ${#SCANNED_PERL[@]} > 0 )); then
  CORPUS+="${CORPUS:+; }Perl: $(corpus_names "${SCANNED_PERL[@]}")"
fi

gate_pass "scanned $SCANNED shipped runtime file(s) ($CORPUS); each budgets local input before buffering or sorting"
```

The last clause has its own shape, and it is the one most likely to bite a team. Desk Transition, the display-layout plugin, drives Hyprland through a helper script. Hyprland 0.57 reads a Lua config, so `hyprctl dispatch focusmonitor X` is a Lua syntax error there, which is why the helper sends the Lua form of a dispatch first and the classic form second. On that release the `keyword` command no longer exists, the server answers "unknown request", and hyprctl still exits 0. The old helper read that as a successful display change that never happened.

```bash
# The shipped helper runs under `set -euo pipefail`, so the status of the
# pipeline below is hyprctl's status and not head's.
set -euo pipefail

# Run hyprctl once. Succeeds only on the exact reply "ok" with exit status 0,
# and remembers the first line of whatever it printed for the failure note.
hypr_ok() {
  local out rc=0
  out="$(timeout 6s hyprctl "$@" 2>&1 | head -c 2048)" || rc=$?
  LAST_REPLY="${out%%$'\n'*}"
  [[ "$rc" -eq 0 && "$out" == "ok" ]]
}
```

The helper turns that into its own exit codes, so a caller can tell the failures apart: exit 1 when Hyprland refused the change, exit 2 when the named output is not an active output, and exit 3 when there was nothing to arrange.

Success needs a positive answer, not just a quiet status. Quiet Queue, the notification plugin, had the same shape. Its Do Not Disturb read now trusts only exit status 0 with output matching exactly on or off. Anything else, a shell that is not ready, a timeout, odd text, is unknown, and unknown is never off. While the state is unknown the helper keeps the session record, refuses to start or end a session, and a start it cannot verify restores the off it read.

## Why not the obvious approach

The obvious fix for the gate is to shell out to Perl. Run `perl -c` on every candidate helper and let the interpreter judge the file. That is a better gate, and the wrong one here, because the vendored lane ships inside the plugin and cannot take a runtime dependency on Perl being installed. The shipped helpers already run Perl on the user's machine, where the interpreter arrives with the base git package. The lane runs on contributor and CI machines instead, and it cannot assume what is installed there. The Perl rules went into the analyzer we already run, as pattern rules over the source text, and the gate stayed a WARN rather than a block, because a maintainer can confirm a bounded producer the regex cannot see.

The second obvious fix is to scan more: drop the exclusions and check the whole tree, scripts and tests included. The gate's own scope comment records that holding dev tooling to the runtime's threat model produced false positives on every plugin, since dev tooling never runs on a user's machine. The scope stayed shipped runtime files.

The third obvious fix for the screenshot scanner was to change the fixture: seed `~/Pictures/Screenshots` in the test, point the scanner at that folder and assert it finds the files. The old resolution order honoured `OMARCHY_SCREENSHOT_DIR` and `XDG_PICTURES_DIR`, so that would have made the test green and left the bug in place, because the bug is that the code and the fixture agreed on a path the application never uses.

## How it was verified, and what it cost

Verification is where a receipt earns the name. The gate suite ran 328 of 328, the reporters 18 of 18, integration 10 of 10, and the bash lint and pre-commit hooks were clean.

The cases for this one gate say more than the totals do. Of the 12 cases that exercise it, 10 fail against the gate on master. They cover a vacuous PASS on a Perl file, a PASS on an empty corpus, and a PASS with no corpus named. The other 2 are shell severity cases, and they pass on both versions, which is how we know the shell rules did not change under us. Six deliberate mutations of the gate are each caught by a specific mutation test case, so they are not passing by accident.

Two results matter most. The new gate passes all nine shipped Perl helper scripts across the plugin fleet and names each one, so a reader can see what was opened. And deleting one line, the readdir budget from a copy of the real scanner, flips that file to a WARN at the sort, citing the loop line. The gate can still fail.

Only the gate's change is verified in detail here. The scanner's fix shipped with 63 of 63 tests, Model.js at 100 percent coverage under c8, mutation at 97.79 percent, three clean race runs and no osv-scanner advisories. The rig fix shipped with the pit-wall and bazaar live runs passing on the upgraded rig, every fetch returning rc=0 with a body and no QML warnings, the unit suite at 16 of 16 and the contracts clean.

The cost was coverage having to notice. Until a coverage reporter called the gate UNPROVEN, nine shipped Perl helper scripts went unread by the gate that exists to read them, and every run printed PASS.

## Also shipped

- Desk Transition's helper sends the Lua form of a dispatch first and the classic form second, so one helper serves both releases of Hyprland. On 0.57 the classic form is parsed as Lua and errors, which is why the new form goes first.
- Quiet Queue's panel shows DND STATE UNKNOWN and dims every row while the state is unknown.
- The Foundry panel builds its start command from the helper's own resolved location, because the plugin installer puts nothing on PATH and the panel had been printing a command that could not run.

## How the work went

This post's main thread was carried by Claude Opus 5 5: six sessions, 1175 minutes, in intent-os, the internal operations and documentation repository, with 114 failure-to-fix moments and no course corrections from the human. MiniMax M3 and Claude Sonnet 5 ran the rest of the day's work.

## Use this

- Make every check print the corpus it opened, file by file, and report a skip when it opened nothing. The reference implementation is the C42 gate: https://github.com/jeremylongshore/contributing-clanker/blob/master/skills/contribute/scripts/gates/c42-omarchy-local-resource-budget.sh
- Point the fixture at the path the application really uses, and run the check where the application really runs, so neither the code and its fixture nor the check and the application can agree on something false.
- Require a positive answer before recording success. An exit code of zero says the tool ran; a reply of "ok" says the tool did what you asked.

## Frequently asked questions

### How do I make a CI check report the files it actually scanned?

The gate ends its verdict with the list of files it covered, by language. A file it could not open prints nothing at all, and an unopened file is never counted as scanned.

### Should a check that found nothing report a pass or a skip?

A skip, and the gate has to say why. Before the fix, an empty corpus and a clean corpus printed the same word, and no reader could tell them apart.

### How do I stop a test fixture from agreeing with the code?

Seed the path the application really uses, and assert against that, not against the path the code happens to read. The scanner's rig seeded `~/Pictures` and asserted the resolved directory ended in `/Pictures`, so both halves were true while the plugin did nothing.

### Is exit code 0 enough to record a success?

No. A zero exit status says the tool ran. It does not say the tool did the thing you asked. On Hyprland 0.57 the `keyword` command no longer exists, the server answers "unknown request", and hyprctl still exits 0, so success needs a positive answer rather than a quiet status.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do I make a CI check report the files it actually scanned?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The gate ends its verdict with the list of files it covered, by language. A file it could not open prints nothing at all, and an unopened file is never counted as scanned."
      }
    },
    {
      "@type": "Question",
      "name": "Should a check that found nothing report a pass or a skip?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A skip, and the gate has to say why. Before the fix, an empty corpus and a clean corpus printed the same word, and no reader could tell them apart."
      }
    },
    {
      "@type": "Question",
      "name": "How do I stop a test fixture from agreeing with the code?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Seed the path the application really uses, and assert against that, not against the path the code happens to read. The scanner's rig seeded ~/Pictures and asserted the resolved directory ended in /Pictures, so both halves were true while the plugin did nothing."
      }
    },
    {
      "@type": "Question",
      "name": "Is exit code 0 enough to record a success?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. A zero exit status says the tool ran. It does not say the tool did the thing you asked. On Hyprland 0.57 the keyword command no longer exists, the server answers \"unknown request\", and hyprctl still exits 0, so success needs a positive answer rather than a quiet status."
      }
    }
  ]
}
</script>

## Related Posts

- [What a Skipped Check Is Worth in CI](https://startaitools.com/posts/the-skip-that-counted-as-a-pass/)
- [Every Check Should Report What It Did Not Look At](https://startaitools.com/posts/the-lane-that-reviewed-nothing/)
- [A Path Is Not Proof of Identity](https://startaitools.com/posts/a-path-is-not-proof-of-identity/)
