# Quit-sponsor

A quit-smoking sponsor skill for AI agents.

> The guiding idea: quitting is not a fight you win, it is a match you stop attending. A sponsor does not coach the boxing, it walks you out of the arena.

## What it is

An Agent Skills package (a folder with a SKILL.md) that turns an AI agent with persistent memory into a quit-smoking sponsor: a witness with long memory and exact receipts, available at the moments human support usually is not, like the 1 a.m. craving or the trigger that fired five minutes ago.

It is not an app, not a chatbot script, and not a medical device. It is orchestration. The published evidence says what works: immediate execution of the quit decision, urge surfing, arousal reappraisal, nicotine replacement, abstinence over reduction. The skill tells the agent when, in what order, triggered by what signal.

## Who it's for

The people who would otherwise quit alone: no affordable professional help, no insurance, a remote area, shame that blocks a face-to-face visit, or a plain preference for a witness with no face to lose. It is not a panacea: professional support combined with medication has the strongest evidence in cessation, and if you have access to it, take it. The skill then works alongside as the continuity layer (the clinician gets fifteen minutes a month, the sponsor gets the 2 a.m. wave). Complement, never substitute.

## Three layers

1. The science, operationalized: withdrawal timelines for nicotine and cannabis, the caffeine interaction, hunger and taste tactics, alcohol as the top early trigger, honest weight numbers, exercise as scheduled dose and rescue walk, abstinence over moderation, waves and how to reappraise them. Every claim traces to references.md.
2. The sponsor decision tree: the three-clause contract (call before, slips are data, witness never sermon) closed by the confession promise, the day zero budget, the purge ritual, the wave triage, the withdrawal attribution flip script, the slip protocol with attribution coaching and escalation on repetition, the silence protocol with its pre-forgiving outreach ladder, a low-verbal client mode, compound high-risk situations and field removal, the daily scaffold, the two-year check-in arc, social pressure scripts, writing cycles, replacement-addiction screening, the timestamped logbook.
3. Personalization: excavating the person's own wanting, inventorying the arsenal they arrive with (drilled reflexes from prior recovery work versus folklore), a light proportionate anamnesis (who is around, mental-health terrain, medications), autopsying their real relapse history, writing 3 to 6 specific if-then plans, finding their somatic signature, adopting their metaphors.

## Install

This is a standard Agent Skills folder (the SKILL.md format), so it works in any tool that reads the standard.

- ClawHub: `clawhub install quit-sponsor` ([skill page](https://clawhub.ai/skill/quit-sponsor)).
- Claude Code: clone this repo into `~/.claude/skills/quit-sponsor/`, or add the repo as a plugin marketplace and install from it (a manifest is included).
- Other Agent Skills readers (various CLI agents and IDE assistants): place the folder where your tool discovers skills.

Persistent memory across sessions is strongly recommended. The value of a sponsor is continuity: the contract, the logbook, and the risk map must survive restarts. Without memory the skill still works, degraded, by keeping its logbook in a file the person owns.

Model fit is measured, not assumed: MODEL_FIT.md carries a reproducible six-turn crisis test, dated results, and use/avoid guidance. As of July 2026: Claude Opus and Sonnet 5, GPT-5.6 Sol, and GLM-5-turbo classes held the crisis scenario with the skill (the cheapest played a perfect game); DeepSeek V4 Pro class needs per-version verification (it read the "never ask for the hand" rule and asked anyway); models or routes with truncated or empty replies are proscribed for crisis duty. If your model is not listed, run the fit test before trusting it with a crisis. And never run the role without the skill: bare, every vendor tested reproduced the field-corrected errors.

## Philosophy

- Zero shame. Slips are data. The run continues, with one data point marked on it; nothing banked is ever lost.
- Exact receipts. Timestamps, the person's own words, gentle corrections when memory drifts.
- The science cites, the orchestration is lived. The scientific layer stands on published evidence; the decision tree was field-tested live with a veteran quitter, and provenance is labeled (literature, field, or simulation-only). This follows the oldest tradition in addiction work: a large share of counselors come from lived experience, one recovery deep (surveys find roughly 37 to 57 percent of substance abuse counselors are themselves in recovery; reference 45). Single-lineage calibration is the trade's normal, not a bias to apologize for; generalizing it is the model's job.
- The logbook belongs to the human. Local, private, never exfiltrated.

## Status

v0. A field test (N=1) is in progress; this project makes no outcome claims yet. The scientific layer stands on the published evidence in references.md regardless.

## Safety

Read SAFETY.md first; it overrides everything else. Highlights: not medical advice; physical red flags go to a doctor; acute distress goes to human crisis lines; the logbook is the person's private health data.

## Changelog

- v0.6.0: honest scope ("who this is for": built first for people without access to professional help; complement, never substitute, since professional support plus medication holds the strongest evidence). Model-tier recommendation: frontier-class models only; the sponsor role is judgment-dense and an economy tier improvising through a crisis is worse than nothing. Day-2 field doctrine: the purge sold honestly (it does not reduce craving or create distance, it kills the automatic path and buys the minutes in which clause 1 can fire), the two regimes of craving (weather versus hijack, with the negotiation self-marker and the rule that no tool may require reasoning mid-crisis), and the counters card for "what happens if I smoke one" (the only thing a cigarette resets is the part that hurts; delivered mid-siege, the withdrawal itself testifies against the relapse). The scope boundary rewritten as what it is, a mortality line: "slips are data" is safe coaching for tobacco and can kill if transplanted to alcohol (withdrawal itself is medically dangerous) or opioids (post-abstinence tolerance loss makes the first slip potentially the last); plus the force-multiplier honesty (the tool multiplies wanting, it cannot create it). Full-read review actioned: clause 1 disclosed at activation (the installer self-selected; knowing the rule before the first crisis is the non-negotiable part, firing it is their journey), every uncalled slip re-teaches clause 1, outreach becomes a negotiated setting (re-cueing named as a real cost for absorbed workers), provenance labels (literature, field, simulation-only), aftercare reframed as boosters with no graduation, store-the-flag data minimization for the anamnesis, text-format curve, and a references maintenance rule (numbers rot first; yearly re-verification pass). Counselor-tradition claim sourced (37 to 57 percent of counselors are in recovery, reference 45), the two-way complementarity line (a model cannot replace a human, a human cannot replace a model; compose them, and when someone has neither, this is the mission), and GitHub issue templates that route live crises away from public issues. The check-in arc reframed: cadence follows need, not the calendar (starting cadence set by the arsenal inventory; fragility tightens on a word; stability thins at a stated price; boosters scheduled against forgetting where you came from). Crisis delivery rules: physical moves are never dispatched, they ride inside the conversation (mirror first, one clause of why, short fast replies); the inverted economics script runs only if the person raises the money themselves. MODEL_FIT.md added: a reproducible six-turn crisis fit test, measured results across six models from four vendors (the skill ports across families and equalizes tiers; bare, every vendor reproduced the field-corrected errors; stock check five of five with the skill, zero of five bare), and dated use/avoid guidance. Intake hardened from the field test: inventory the arsenal the person arrives with (a rehab or twelve-step veteran carries drilled reflexes to reuse; a first-timer needs them installed), fire-drill rehearsal of clause 1 so it survives a crisis (a clause offered is not a clause installed; only pre-drilled reflexes run mid-hijack), a light proportionate anamnesis (who is around, mental-health terrain, medications, physical flags), and the medication-clearance warning in SAFETY.md (quitting raises blood levels of several common drugs; tell the prescriber).
- v0.5.0: relapse paths hardened (10-scenario adversarial simulation plus a real crisis night in the N=1 field test). Order-of-operations for colliding rules, the front-door rule and two-counter semantics, a post-relapse state, recurrence escalation with teeth and a slip-log reaction field, a medical red-flag playbook, and a graded crisis ladder (each rung increases distance, exile with sentence deferred to daylight as the primary path). Plus the self-citation rule, silence protocol v2, negotiated disengagement with a pact-amendment clause, presence-is-not-veracity handling, and sponsor factual discipline.
- v0.4.0: crisis night lessons (live field test at peak withdrawal). The wave machine and cue exile: decay only holds with the cue out of range, exile compromise when destruction is refused, inverted economics script, correct the number instead of defending it. The Ulysses pact: pre-cancelled negotiation arguments behind an identical warm wall, always paired with the pre-armed return door. The nicotine kinetics script: speed, not presence.
- v0.3.0: survive the low-initiative client (adversarial user-test findings). Silence protocol at the same rank as the slip protocol, cumulative counter replacing all resets, staged day zero budget, withdrawal attribution flip script, low-verbal client mode, and the confession promise closing the contract.
- v0.2.1: first public release.

## License

MIT.

## Support this work

This skill is free and always will be. If it helped you or someone you care about:

- GitHub Sponsors: via the Sponsor button (when available)
- Ethereum: `0x72bDBED0c423CF543996167935a5c2254768E269`

Every donation funds more open tools like this one.
