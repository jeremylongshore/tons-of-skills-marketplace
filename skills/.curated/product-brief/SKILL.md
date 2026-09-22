---
name: product-brief
description: Structured product brief and PRD creation assistant. Use when the user
  needs to create a product brief, PRD, or feature spec that defines what to build
  and why. Trigger with "product brief", "PRD", "spec", "feature doc", "write a
  brief", or "define this feature".
version: 1.10.0
author: Ahmed Khaled Mohamed <ahmd.khaled.a.mohamed@gmail.com>
license: MIT
allowed-tools: Read, Glob, Grep
argument-hint: "feature name"
tags:
- productivity
- product-brief
compatibility: Designed for Claude Code
model: inherit
effort: medium
user-invocable: true
---
# Product Brief Skill

## Overview

Create a decision-ready brief that ties a verified user problem to scope, measurable outcomes,
risks, and open decisions. Run the
[evidence and review checklist](references/evidence-and-review.md) before treating a draft as
ready for engineering.

Use `Glob` to locate research, `Grep` to trace prior decisions, and `Read` to verify the evidence.

## Instructions

Guide the creation of clear, actionable product briefs that engineering can use to scope and build.

### Behavior

1. **Gather context first** — Problem, users, constraints
2. **Use a consistent structure** — Same format every time
3. **Focus on "what" and "why"** — Leave "how" to engineering
4. **Include success metrics** — How will we know it worked?
5. **Surface open questions** — Don't hide uncertainty

### Tone

- Clear and decisive
- Specific over vague
- Honest about what's unknown
- Respectful of engineering's expertise

## Brief Structure

Every product brief should include the decision-relevant sections below. Replace bracketed prompts
with verified project context and remove any section that truly does not apply.

```markdown
# [Feature Name]

## Problem Statement
What problem are we solving? Who has this problem? Why does it matter now?

## Proposed Solution
What are we building? (High-level, not implementation details)

## User Value
Why will users care? What's the benefit?

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Primary metric | X | Y |
| Secondary metric | A | B |

## Scope
### In Scope
- What's included in v1

### Out of Scope
- What we're explicitly NOT doing (and why)

## Open Questions
- Things we need to figure out before/during implementation

## Dependencies
- Other teams, systems, or work this depends on

## Timeline
- Target dates when known, or "set after engineering scoping"
```

### Advanced Patterns

1. **Scope negotiation** — The In Scope / Out of Scope section is the most-debated part of any brief. Write Out of Scope as a decision, not a deferral: "We're not building desktop support because mobile accounts for 92% of this use case's sessions. Revisit threshold: if desktop sessions exceed 20%." This turns "why not?" conversations into data conversations
2. **Metric selection** — Pick metrics you can actually measure within the project timeline. "Increase retention" is meaningless in a brief for a feature shipping in 4 weeks — you won't have retention data for months. Instead, pick a leading indicator: "Increase Day-1 feature activation from X% to Y%." Every metric in the brief should have a known data source and a realistic measurement window
3. **Dependency surfacing** — The Dependencies section should scare you a little. If it doesn't, you haven't thought hard enough. For each dependency, document: who owns it, have you talked to them, what's their timeline, and what happens to your project if they slip. Briefs with a clean "no dependencies" section are usually briefs where the PM hasn't discovered the dependencies yet
4. **The "jobs to be done" problem statement** — Don't describe the problem as a feature gap ("we don't have voice messages"). Describe it as a user struggle: "Users in messaging-heavy markets abandon threads when typing becomes slower than speaking — they switch to WhatsApp mid-conversation." The first framing invites solution debates; the second invites empathy and creative solutions
5. **Progressive disclosure of detail** — A brief should be readable at three speeds: skim (problem + solution + metrics in 30 seconds), read (full brief in 5 minutes), reference (open questions + dependencies when scoping). Structure the document so each speed gives a complete picture at its level of detail

## Process

1. **Ask clarifying questions** about the feature
2. **Propose the brief structure** with initial content
3. **Draft each section** based on user input
4. **Review and refine** together
5. **Highlight gaps** that need stakeholder input

## Examples

### Example 1: New Feature Brief

**User:** Help me write a product brief for adding voice messages to our chat feature.

**Good Response:**

Let me gather some context first:

1. **Problem**: What's driving this? User requests? Competitive pressure? Usage data?
2. **Users**: All users, or specific segments (power users, specific markets)?
3. **Constraints**: Any technical limitations? Timeline pressure?
4. **Success**: How will we measure if this worked?

Based on what you share, I'll draft the brief. Here's a starting structure:

---

# Voice Messages in Chat

## Problem Statement

[To be filled based on your context]

**Initial draft based on common patterns:**
Users in messaging-heavy markets (Brazil, India, SEA) prefer voice over text — it's faster and more personal. Our chat feature only supports text, creating friction for these users and putting us behind competitors who offer voice.

## Proposed Solution

Add the ability to record and send voice messages within existing chat threads.

Core functionality:

- Record button in chat input
- Playback controls for received messages
- Visual waveform for recorded/played audio

## User Value

- Faster communication (speaking vs. typing)
- More expressive (tone, emotion)
- Accessibility (users who struggle with typing)

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Voice messages sent/DAU | 0 | 5% |
| Chat engagement (messages/user) | X | +15% |
| Market-specific DAU (Brazil) | Y | +10% |

## Scope

### In Scope (v1)

- Record up to 60 seconds
- Send in 1:1 and group chats
- Playback with speed control (1x, 1.5x, 2x)
- iOS and Android

### Out of Scope

- Transcription (v2)
- Voice-to-text conversion (v2)
- Desktop support (v2)

## Open Questions

- Max recording length? (60s proposed, but needs validation)
- Storage: How long do we retain voice messages?
- Moderation: How do we handle reported voice content?

## Dependencies

- Audio infrastructure team (encoding, storage)
- Trust & Safety (moderation tooling)
- Client teams (iOS, Android)

## Timeline

- Scoping: 1 week
- Implementation: set after engineering scoping
- Target: confirmed launch window

---

What context can you fill in? I'll refine based on your input.

### Example 2: Quick Brief

**User:** I need a brief for adding a "remind me" button to push notifications.

**Good Response:**

Quick brief mode — I'll draft based on common patterns, you refine:

---

# Push Notification Reminders

## Problem Statement

Users who see a push notification but aren't ready to act have no way to come back to it. The notification disappears into the notification tray graveyard, and the opportunity is lost.

## Proposed Solution

Add a "Remind me" quick action to push notifications that reschedules the notification for a later time.

Options presented to user:

- "In 1 hour"
- "Tonight" (8pm local)
- "Tomorrow morning" (9am local)

## User Value

- Control over notification timing
- Reduced notification anxiety ("I can deal with this later")
- Better completion rate on notification CTAs

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Reminder usage rate | n/a | 5% of notifications |
| Reminded notification action rate | n/a | 40% (vs 12% overall) |
| Notification dismissal rate | 35% | 25% |

## Scope

### In Scope

- iOS and Android quick action
- Three time options (1hr, tonight, tomorrow)
- Works with all notification types

### Out of Scope

- Custom time picker
- Recurring reminders
- Smart timing suggestions

## Open Questions

- Should reminders count against frequency caps?
- What happens if user has DND enabled at reminder time?

---

Anything to adjust or add?

## Prerequisites

- Claude Code with read access to project files
- Feature context: problem, target users, and business motivation
- Any existing research, user feedback, or competitive analysis

## Output

Complete product briefs including problem statement, proposed solution, user value proposition, measurable success metrics with baselines and targets, scoped in/out decisions with rationale, open questions, dependencies, and timeline estimates.

## Error Handling

When the user cannot articulate the problem clearly, use jobs-to-be-done framing to help them discover it. If success metrics lack baselines, flag this as a gap and suggest how to establish them before launch. When dependencies are unclear, list known unknowns explicitly rather than omitting the section.

## Resources

- [Jobs to be Done framework](https://hbr.org/2016/09/know-your-customers-jobs-to-be-done) -- problem statement framing
- [RICE prioritization](https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/) -- scope and impact evaluation
- [Shape Up](https://basecamp.com/shapeup) -- appetite-based scoping methodology
