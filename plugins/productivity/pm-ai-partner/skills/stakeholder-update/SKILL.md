---
name: stakeholder-update
description: Create and review stakeholder status updates, progress reports, and executive
  summaries. Use when the user needs to write concise upward communication.
  Trigger with "stakeholder update", "status update", "progress report", "update
  leadership", "weekly update", or "executive summary".
version: 1.10.0
author: Ahmed Khaled Mohamed <ahmd.khaled.a.mohamed@gmail.com>
license: MIT
allowed-tools: Read, Glob, Grep
argument-hint: "project or team"
tags:
- productivity
- stakeholder-update
compatibility: Designed for Claude Code
model: inherit
effort: medium
user-invocable: true
---
# Stakeholder Update Skill

## Overview

Turn current evidence into a concise update that leads with status, names risks plainly, and
makes decisions or help requests explicit. Use the
[evidence and review checklist](references/evidence-and-review.md) before sending it.

Use `Glob` to locate status artifacts, `Grep` to trace commitments, and `Read` to verify the data.

## Instructions

Help create clear, concise stakeholder updates that communicate progress, risks, and asks effectively.

### Authentication

Use only existing authenticated access when source systems are involved. Never request or expose
credentials, tokens, or API keys; if access is unavailable, report the last verified timestamp.

### Behavior

1. **Lead with the headline** — Don't bury the lead
2. **Use consistent structure** — Same format builds trust
3. **Be honest about risks** — Surface problems early
4. **Include clear asks** — What do you need from them?
5. **Keep it scannable** — Executives skim

### Tone

- Confident but not arrogant
- Transparent about challenges
- Action-oriented
- Respectful of reader's time

### Advanced Patterns

1. **The bad news sandwich is dead** — Don't bury risks between good news. Executives see through it and lose trust. Instead, lead with the headline (good or bad), then immediately follow with what you're doing about it. "Android delivery dropped to 88%. Root cause identified, fix deploying Monday, ETA to recover: 2 weeks." Confidence comes from having a plan, not from hiding problems
2. **Metric trend > metric snapshot** — A single number is noise. Three data points are a trend. Always show the direction: "Delivery rate: 94% (up from 89% last month, target 95%)." The reader can instantly assess: are we improving, stable, or declining? Without trend, they'll ask — and you'll look unprepared
3. **The "asks" section is the point** — Most PMs treat the asks section as an afterthought. But the entire update exists to get your asks answered. If you have no asks, you're sending a status report — send it as an email. If you have asks, lead with them in the TL;DR: "On track for March launch. Need: decision on scope cut by Friday."
4. **Audience-calibrated detail** — Your skip-level wants 3 bullets. Your manager wants a page. Your team wants the full picture. Don't write one update for three audiences. Write the full version, then create progressively shorter summaries. The TL;DR section should stand alone as a complete Slack message
5. **Consistency builds trust** — Send updates on the same day, in the same format, at the same cadence. When stakeholders know what to expect, they read it. When the format varies, they skim or ignore. The best update format is the one you actually send every week, not the perfect template you use once

## Update Structure

```markdown
## [Project/Team] Update — [Date]

### TL;DR
One sentence summary. What's the single most important thing to know?

### Status: On Track / At Risk / Off Track

### Progress This Period
- [Completed item 1]
- [Completed item 2]
- [In progress item]

### Key Metrics
| Metric | Target | Actual | Trend |
|--------|--------|--------|-------|
| [Metric 1] | X | Y | up/down/flat |

### Risks & Blockers
| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| [Risk 1] | [High/Med/Low] | [What we're doing] | [Who] |

### Asks
- [ ] [What you need from leadership]

### Next Period
- [ ] [What's coming next]
```

## Principles

### Headline First

Bad: "We had several meetings this week and discussed various topics..."
Good: "We're on track to launch March 1st. Key risk: Android testing capacity."

### Specific Over Vague

Bad: "Good progress on performance"
Good: "Reduced P99 latency from 450ms to 180ms (-60%)"

### Honest About Problems

Bad: "Minor delays expected"
Good: "Timeline at risk: 2-week slip likely due to API dependency. We need [specific help]."

### Clear Asks

Bad: "Would be helpful to have more resources"
Good: "Requesting: 1 additional Android engineer for 3 weeks, or we slip by 2 weeks"

## Examples

### Example 1: Weekly Update

**User:** Help me write a weekly update for my team's work on push notification improvements.

**Good Response:**

---

## Push Notifications Update — Week of Feb 10, 2026

### TL;DR

Delivery rate hit 94% (target: 95%). Android token refresh fix deployed, monitoring results.

### Status: At Risk

On track for delivery rate target, but Android reachability work is behind schedule.

### Progress This Week

- **Android token refresh fix deployed** — Live for 10% of users, expanding Monday
- **iOS delivery optimization** — P99 latency down from 2.1s to 1.4s
- **Rich media support** — Design complete, engineering started (40% done)
- **Quick reply buttons** — Blocked on iOS 17 API approval

### Key Metrics

| Metric | Target | This Week | Last Week | Trend |
|--------|--------|-----------|-----------|-------|
| Delivery rate (iOS) | 95% | 96.2% | 95.8% | up |
| Delivery rate (Android) | 95% | 91.4% | 89.2% | up |
| P99 latency | <2s | 1.4s | 2.1s | up |

### Risks & Blockers

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Quick reply blocked on Apple | High | Escalated to partner team, ETA next week | Ahmed |
| Android engineer out sick | Med | Redistributing work, 3-day slip possible | Michelle |

### Asks

1. **Decision needed:** Should we launch rich media without quick reply, or wait?
2. **Escalation help:** Apple approval taking 2+ weeks — can leadership contact reach out?

### Next Week

- [ ] Android token refresh: expand to 100%
- [ ] Rich media: complete implementation
- [ ] Quick reply: resolve Apple blocker

---

Adjust anything?

### Example 2: Executive Summary

**User:** Write an executive summary of our Q1 progress for leadership.

**Good Response:**

---

## Client Messaging — Executive Summary

### Bottom Line

**Strong Q1.** Delivered 3 of 4 planned initiatives. Push delivery rate at 94% (target: 95%), with clear path to close the gap in Q2. Team velocity improved 20% after process changes.

### What We Shipped

| Initiative | Status | Impact |
|------------|--------|--------|
| Android token refresh | Shipped | +5% delivery rate, +2M reachable users |
| Push performance optimization | Shipped | -60% latency (2.1s to 0.8s) |
| Inbox redesign | Shipped | +15% inbox open rate |
| Rich media push | 70% | Slipped to Q2 (Apple approval delay) |

### Key Metrics

| Metric | Previous period | Current period | Target | Status |
|--------|---------|---------|--------|--------|
| Push delivery rate | 89% | 94% | 95% | At Risk |
| Message success rate | 10% | 14% | 15% | At Risk |
| Team velocity (points/sprint) | 45 | 54 | 50 | On Track |

### What Worked

1. **Focus on Android** — Concentrated effort closed the iOS/Android delivery gap
2. **Process improvements** — Async standups + clearer ownership = faster shipping
3. **Partner alignment** — Early stakeholder involvement reduced late-stage churn

### What Didn't

1. **Apple dependency** — Underestimated approval timeline for new notification APIs
2. **Scope creep** — Rich media grew 40% from original spec
3. **On-call burden** — Team spent 15% of time on unplanned support

### Q2 Priorities

1. **Close the delivery gap** — 94% to 99% (Android token + FCM reliability)
2. **Ship rich media** — Unblock Apple, launch by April
3. **Reduce support burden** — Self-service tools for partners

### Asks

1. **Headcount:** Request 1 additional engineer for Q2 to maintain velocity
2. **Executive support:** Apple escalation for notification APIs
3. **Decision:** Invest in self-service tooling vs. dedicated support engineer?

---

Want me to adjust the framing or add more detail anywhere?

### Example 3: Quick Status

**User:** I need a quick Slack update about a feature delay.

**Good Response:**

---

**Quick update on [Feature]:**

**Status:** 1-week delay (new target: Feb 22)

**Why:** Discovered edge case in Android 12+ that breaks the happy path. Fix is straightforward but needs testing.

**Impact:** No user-facing impact (feature not launched). Marketing aware and adjusting.

**What we're doing:**

- Fix ready for review today
- Full QA this week
- Still on track for Feb launch window

No action needed — will update if anything changes.

---

Good for Slack?

## Prerequisites

- Claude Code with read access to project files
- Project status information: progress, metrics, risks, and blockers
- Awareness of the target audience (manager, VP, cross-functional peers)

## Output

Structured stakeholder updates including TL;DR headline, traffic-light status, progress summaries, metric trends with context, risks with mitigations and owners, clear asks, and next-period plans calibrated to audience seniority.

## Error Handling

When project metrics are unavailable, use qualitative progress indicators and flag the measurement gap as a risk. If the user cannot identify specific asks, help them determine whether the update is informational (send as email) or decisional (needs a meeting). When bad news must be communicated, structure it with the plan-forward pattern rather than burying it.

## Resources

- [BLUF (Bottom Line Up Front)](https://en.wikipedia.org/wiki/BLUF_(communication)) -- lead-with-the-headline communication
- [Pyramid Principle](https://www.amazon.com/Pyramid-Principle-Logic-Writing-Thinking/dp/0273710516) -- structured top-down communication
- [RAG status reporting](https://en.wikipedia.org/wiki/Traffic_light_rating_system) -- Red/Amber/Green project health
