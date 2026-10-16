# PRD: intent-skills-diagnostic

**Author:** Max Sheahan
**Date:** 2026-10-15
**Status:** Active

## Problem

People who use Claude or Codex for work rarely know which of the 400+ Tons of Skills plugins fit their own work, and browsing the catalog does not tell them. They keep re-explaining the same thing to the AI (a commit format, a grading rubric, a brand voice) when a skill could hold it. A recommender that guesses or pads its list is worse than none, so every pick has to come from a reviewed list with a source and a check date.

## Target users

| User | Context | Primary need |
| --- | --- | --- |
| Developer on Claude Code or Codex | Setup feels thin; repeats project conventions | One or two plugins that remove a repeated explanation |
| Non-developer on claude.ai, Desktop or Cowork | Teaching, writing, ops or marketing work | A fit without a technical stack question |
| Heavy plugin user | Already has many skills installed | No duplicate of what is installed; an honest "no new tool needed" |

## Success criteria

1. Every pick comes from the reviewed list, at most two, each with source URL, check date and the install route for the person's tool.
2. Missing answers return the question to ask; the stack question appears only for software work with no scanned stack.
3. When nothing fits, the result is "no verified match" or "no new tool needed", never a padded pick.
4. The card never types into the chat; all tools are read-only.

## Functional requirements

- **FR-1:** `ask_questions` shows only the open intake questions on a card.
- **FR-2:** `scan_setup` tells the assistant which names to list on Claude Code or Codex, never config contents.
- **FR-3:** `recommend_skills` returns one of four outcomes with at most two reviewed picks and per-surface install routes.
- **FR-4:** `talk_to_intent` shows a contact link only when asked; nothing is submitted or booked.
- **FR-5:** `start_here` greets with three example requests.

## Out of scope

- Installing anything for the person.
- Reading configuration contents or secrets.
- Live fetching from tonsofskills.com (the reviewed list is checked and dated).
- Memory between chats, accounts, booking.
- ChatGPT and other hosts.
