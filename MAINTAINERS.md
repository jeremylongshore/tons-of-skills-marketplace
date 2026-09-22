# Maintainers — Tons of Skills

The live roster for the maintainer ladder. **How the ladder works** (tiers,
rights, vetting, delegation) is in [`GOVERNANCE.md`](GOVERNANCE.md). This file is
just _who_ — handles, tiers, and areas. No personal information beyond a public
GitHub handle; security contact is in [`SECURITY.md`](.github/SECURITY.md).

Tiers: **Contributor · Reviewer · Approver · Maintainer · Lead** (see GOVERNANCE).
Areas: `ci-infra`, `validator-schema`, `marketplace-site`, `external-sync`,
`docs-governance`, `freshie`, `deps`, `plugins-<category>`.

An Approver's review satisfies the code-owner merge gate for their area(s) (wired
in [`.github/CODEOWNERS`](.github/CODEOWNERS)). A Reviewer's ✅ is the `/lgtm`
quality signal but does not yet satisfy that gate.

---

## Roster

| Handle                                                           | Tier           | Area(s)                        | Backup           | Notes                                                                                                                                  |
| ---------------------------------------------------------------- | -------------- | ------------------------------ | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| [@jeremylongshore](https://github.com/jeremylongshore)           | **Lead**       | all                            | —                | Owns the repo, releases, and all high-trust paths (validators, schema, CI, deps, root policy).                                         |
| [@blueandyellow44](https://github.com/blueandyellow44)           | **Maintainer** | all                            | @jeremylongshore | Co-maintainer at the top tier — code-owner on every area (paired with the Lead), sets direction, can sponsor others up.                |
| [@rfisch](https://github.com/rfisch)                             | **Maintainer** | all                            | @jeremylongshore | Co-maintainer at the top tier — code-owner on every area, sets direction, and can sponsor others up the ladder.                        |
| [@opeyemiariyo-netizen](https://github.com/opeyemiariyo-netizen) | **Approver**   | `ci-infra`, `marketplace-site` | @jeremylongshore | Code-owner on CI/deploy + the marketplace site. Promoted by the Lead 2026-07-16 (pipeline quiz waived for learn-on-the-job mentoring). |

### Invitation pending

Seats the Lead intends to fill by invite as the bench proves out. Added to the
roster above (with area + sponsor) when they accept and are wired into CODEOWNERS.
No handles are listed until invited, to avoid implying rights that do not yet
exist.

- Additional cohort contributors — onboarded via the lightweight
  **outside-contributor → Reviewer** on-ramp described in
  [GOVERNANCE](GOVERNANCE.md) and the
  [org-migration record](000-docs/707-AT-DECR-org-migration-to-intent-solutions-io.md).

### Emeritus

_(none yet)_ — inactive maintainers move here; recognition kept, active rights
paused. See GOVERNANCE § Off-ramp.

---

## Skill-of-the-Week rotation

Editorial pick, rotated so it is not always the Lead. The picker for the week runs
`node scripts/promote-spotlight.mjs` (see GOVERNANCE § Skill of the Week).

| Rotation slot      | Picker           |
| ------------------ | ---------------- |
| Default / fallback | @jeremylongshore |
| Rotation           | @blueandyellow44 |
| Rotation           | @rfisch          |

_(Rotation expands as Reviewers/Approvers are added — add a row per picker.)_

---

## How to join

You do not apply for a tier; you earn it. Ship good work in an area, and — under
the current invite-only model — the Lead invites you up. As the bench grows we move
to the two-sponsor model in [GOVERNANCE § Vetting](GOVERNANCE.md#vetting--how-you-move-up).
A promotion is a one-line PR editing this file, with the sponsoring maintainer(s)
named in the PR.
