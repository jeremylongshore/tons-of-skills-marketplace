# When to Use (and Not Use) zero-tech-debt

The most expensive failure mode of this skill is misclassification: applying a structural refactor where a surgical patch was wanted, or applying a hotfix where rot needed to be removed at the root. Get this judgment right _before_ anything else.

## Strong signals — proceed with zero-tech-debt

- Operator explicitly names tech debt, legacy code, or accumulated complexity
- Operator says "do it right this time" / "the way it should have been built" / "rethink this" / "refactor properly" / "modernize"
- **Multiple parallel implementations exist** for the same logical operation (two routes that do the same thing, two state containers holding overlapping fields, two functions whose only difference is one was added later)
- **Naming no longer matches what the code actually does** — the function called `processOrder` now handles refunds, subscriptions, and gift cards because nobody renamed it
- **Onboarding requires explaining "why we have both X and Y"** — a near-perfect tech-debt detector
- **Feature work keeps routing around old scaffolding** instead of through it — every new ticket has a "but first, work around this" step

## Weak signals — clarify intent before invoking

- Generic "improve this code" with no scope — ask: _what specific shape do you want the end state to have?_
- Bug reports that merely touch legacy paths — usually a targeted patch is the right answer
- Performance work where structural cleanup is incidental — split the work; performance fix lands first, structural cleanup separately
- "Refactor" used loosely — could mean rename-only, could mean rebuild — disambiguate before committing scope

## Hard non-triggers — recommend a surgical patch instead

- **Production hotfixes** — minimize diff, preserve blast radius, ship the fix, log the rot for later
- **Security backports** — preserve audit clarity and reviewer focus; reviewers need to see exactly what changed and nothing else
- **Time-boxed patches before a release cut** — the cost of being wrong exceeds the cost of staying messy
- **Code owned by another team without prior coordination** — you can write the refactor; you can't make it land
- **Work where the requested outcome is a bounded patch** — sensitive domains can also need planned structural redesign, but do not turn a fix into one without that scope

## The escape valve

If any non-trigger condition applies, the right move is to **stop and recommend a targeted patch**. Document the rot you noticed in a follow-up ticket so it doesn't get lost — but don't expand the current change to fix it.

This is the discipline that keeps zero-tech-debt from becoming "every change is a giant refactor."
