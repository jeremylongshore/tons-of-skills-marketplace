---
name: yt-pipeline
description: Run the full YouTube content production pipeline
argument-hint: [topic-or-channel-urls]
allowed-tools: Read, Write, Edit, Grep, Glob, Task, WebSearch, AskUserQuestion
model: sonnet
---

Run the complete YouTube content production pipeline. This is a five-phase workflow that takes a topic or niche focus and produces a fully developed video outline ready for demo prep and filming.

**Coordinate the five stages and their saved artifacts.** Use bounded delegation only when available and permitted by the user; direct work is a valid route. Preserve approvals already given for the selected ideas or actual artifacts instead of asking for the same decision again.

## Phase 0: Context

Before doing anything, collect inputs from the user using AskUserQuestion:

1. **Niche/Tool Focus**: What tool, feature, or topic area are we researching? (e.g., "AI writing tools for professionals", "new software features", "productivity automation")

2. **Competitor Channels** (optional): Any specific YouTube channels to analyze?

3. **Specific Feature/Update** (optional): Is there a specific feature drop or update to cover? If so, this is likely an Update Video with fast turnaround.

Do NOT proceed until the focus is confirmed.

## Phase 1: Research

### 1.1 Launch Research

Read `${CLAUDE_PLUGIN_ROOT}/skills/yt-research/SKILL.md` and follow its evidence and input-coverage contract. Use web research, supplied exports and permitted optional delegation:

- **`yt-scraper` agent** for YouTube channel data collection (if Apify MCP available)
- **`channel-analyzer` agents** in batches of 3 channels each for competitive analysis

### 1.2 Merge and Report

After all research completes, merge results into:

- `niche-analysis.json` - structured data
- `niche-report.md` - human-readable summary

Report to user:

```
Research complete.
- Channels analyzed: [N]
- Videos observed: [N] (state collection mode)
- Content gaps identified: [N]
- Coverage limits and unavailable sources: [summary]
```

Present the niche report and ask:
"Here's what I found. Ready to move to ideation, or want to research more channels?"

- Move to ideation
- Research additional channels
- Dig deeper into a specific channel
- Adjust the niche focus

**This is a mandatory human checkpoint. Do NOT proceed without approval.**

## Phase 2: Ideation

### 2.1 Generate Ideas

Read `${CLAUDE_PLUGIN_ROOT}/skills/yt-ideation/SKILL.md`. Using the selected research or explicit hypotheses, generate the requested shortlist. Each idea must include:

- **Title concept** (working title)
- **Content tier** (the creator's tier, if supplied)
- **Content type** (Full Tutorial, Feature Tutorial, Update Video, Use Case Video, etc.)
- **Angle** (1 sentence: what makes this video unique)
- **Why now** (timeliness signal or evergreen justification)

Prioritize the creator's goals and production constraints; do not impose a fixed growth-content mix.

### 2.2 Validate Ideas

Use permitted idea-validation delegation when available, or evaluate directly. Record the evidence, feasibility and open questions; numeric scores are optional labeled heuristics, not measured demand.

### 2.3 Present Validated Ideas

Save `validated_ideas.json` and present a prioritized shortlist. Update actual selections and their basis after the creator chooses, keeping each selected idea ID as the downstream video ID:

```
Here is the shortlist, prioritized by evidence and feasibility:

[Table: Priority | Title | Type | Evidence | Feasibility | Open questions]

Which ideas do you want to develop into briefs?
```

- Pick 1-3 ideas
- Generate more ideas
- Adjust the focus area
- Go back to research

**This is a mandatory human checkpoint.**

## Phase 3: Brief (per selected idea)

Choose one video ID (`{slug}`) per selected idea and reuse it across brief,
packaging, outline and checklist filenames. Read existing selected artifacts
before revising them; preserve explicitly supplied legacy paths. Each artifact
records its video ID, approval status and exact input/output paths. If a target
belongs to another video, choose another ID rather than replacing it.

For each idea the user selects:

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/yt-brief/SKILL.md` and the selected record in `validated_ideas.json`
2. Define: angle, key points, value proposition, CTA asset, audience segment, content tier
3. Output: `video-brief-{slug}.md`
4. Present to user for review

"Here's the brief for '{idea title}'. Review and approve?"

- Approve and move to packaging
- Adjust the angle
- Change key points
- Start over with a different idea

**This is a mandatory human checkpoint.**

## Phase 4: Packaging

For each approved brief:

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/yt-packaging/SKILL.md`
2. Read the approved `video-brief-{slug}.md`; generate title options and thumbnail concepts
3. Output: `packaging-{slug}.md`

"Here are the title and thumbnail options. Pick your favorites."

- Pick title + thumbnail direction
- Request more options
- Adjust the angle

**This is a mandatory human checkpoint.**

## Phase 5: Outline

For each packaged video:

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/yt-outline/SKILL.md`
2. Read the approved `video-brief-{slug}.md` and `packaging-{slug}.md`; build the outline and demo prep checklist
3. Output: `video-outline-{slug}.md` + `demo-prep-checklist-{slug}.md`

"Here's the outline and demo prep checklist. Ready for the team to prep and film."

---

## Final Report

```
Pipeline Complete.
- Ideas generated: [N]
- Ideas validated: [N]
- Briefs created: [N]
- Videos fully packaged and outlined: [N]
- Output files: [list]
```

---

## Agent Identifiers

| Agent            | subagent_type                       |
| ---------------- | ----------------------------------- |
| YouTube Scraper  | `youtube-strategy:yt-scraper`       |
| Channel Analyzer | `youtube-strategy:channel-analyzer` |
| Idea Validator   | `youtube-strategy:idea-validator`   |

## Parallelism Rules

When the user permits delegation and the required tools are available, use Task for bounded parallel work. Otherwise follow the same artifact contracts directly; do not require sub-agents or a paid connector to produce the planning documents.
