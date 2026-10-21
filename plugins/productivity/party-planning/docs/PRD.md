# PRD: party-planning

**Author:** Tarun Batta
**Date:** 2026-10-20
**Status:** Draft

## Problem

Hosts planning a party have to answer the same concrete questions every time:
how much pizza, beer, wine, and ice to buy, and which games will actually work
for their group. Most people guess. Guessing wrong means running out of food
mid-party or overspending on supplies that go to waste, and games picked from
generic listicles come with no player counts, times, or supplies, so they flop
in the room. The tested formulas and the game library behind HostPartyPlay's
calculators already exist on the website, but not inside the assistant people
actually ask these questions to.

## Target users

| User | Context | Primary need |
| --- | --- | --- |
| Home hosts | Birthdays, holidays, game nights at home | Exact food and drink quantities, and games that fit their crowd |
| Parents | Kids' birthday parties | Age-appropriate games with counts, times, and supplies |
| Office and event organizers | Team parties, school events, receptions | Quantities for larger groups and a workable run-of-show |
| Anyone mid-shopping | In a store or ordering online | One number, fast, in buyable units |

## Success criteria

- Quantity answers match the tested formulas exactly (for example, 25 adults
  plus 10 kids returns 12 large pizzas) and are stated in buyable units.
- Game recommendations return 3–5 games matched to the occasion, group size,
  and age mix, each with a player count, time, supplies, and a rules link.
- Every answer includes exactly one link to the source page behind it, so the
  user can adjust inputs or read the full detail.
- The plugin ships as a single SKILL.md with no scripts and no network calls
  of its own; every link is HTTPS.

## Functional requirements

- FR-1: Answer food and drink quantity questions with the tested per-person
  formulas (pizza, drinks, ice, taco bar, and 35+ other foods), rounded up to
  buyable units.
- FR-2: Recommend 3–5 party games matched to occasion, group size, age mix,
  and time available, each with a player count, duration, supplies, and a
  short rules summary.
- FR-3: Point trivia and printable requests to the current packs on the data
  source, linking the specific page used rather than reproducing long content.
- FR-4: Provide hosting timelines and pacing guidance: an icebreaker in the
  first 30 minutes, and structured games capped at 45–60 minutes.
- FR-5: Lead with the practical answer, quantities first in buyable units,
  and say so when a crowd or occasion does not fit a formula instead of
  forcing one.

## Out of scope

- Booking, ordering, or purchasing anything on the user's behalf.
- Invitations, RSVPs, or guest-list management.
- Content beyond what the data source publishes; nothing paywalled or behind
  a sign-up.
