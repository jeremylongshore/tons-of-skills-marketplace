# YouTube Strategy Plugin

Research and pre-production planning for YouTube: compare sourced channel coverage, develop filmable ideas, write briefs, choose title/thumbnail concepts and prepare filming outlines.

## Skills

| Skill          | What It Does                                                         |
| -------------- | -------------------------------------------------------------------- |
| `yt-research`  | Research competitor channels, niches, and trending topics            |
| `yt-ideation`  | Generate and validate video ideas aligned with content pillars       |
| `yt-brief`     | Refine a video idea into a structured production brief               |
| `yt-packaging` | Create title and thumbnail concept pairs for maximum CTR             |
| `yt-outline`   | Build step-by-step video outlines with demo prep and visual planning |

## Commands

| Command             | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| `/youtube-strategy` | See all available skills and choose what to work on                     |
| `/yt-pipeline`      | Run the complete Research > Ideate > Brief > Package > Outline workflow |
| `/yt-research`      | Research competitor channels and trending topics                        |
| `/yt-ideate`        | Generate and validate video ideas                                       |
| `/yt-brief`         | Create a structured production brief                                    |
| `/yt-package`       | Create title and thumbnail concept pairs                                |
| `/yt-outline`       | Build a detailed video outline with demo prep                           |

## Agents

| Agent              | Purpose                                                    |
| ------------------ | ---------------------------------------------------------- |
| `yt-scraper`       | Orchestrate YouTube data scraping via Apify                |
| `channel-analyzer` | Competitive intelligence analysis per channel batch        |
| `idea-validator`   | Validate video ideas against search demand and competition |

## Workflow

The recommended workflow follows these stages:

1. **Research** (`/yt-research`) - Analyze competitors, identify content gaps
2. **Ideation** (`/yt-ideate`) - Generate 15-20 ideas, validate against demand
3. **Brief** (`/yt-brief`) - Refine selected ideas into production briefs
4. **Packaging** (`/yt-package`) - Create title options and thumbnail concepts
5. **Outline** (`/yt-outline`) - Build detailed outlines with demo prep checklists

Use `/yt-pipeline` to run all stages in sequence with human checkpoints.

## Installation

```bash
/plugin install youtube-strategy@claude-code-plugins-plus
```

## Inputs and handoffs

Web research and supplied exports are supported inputs. Optional bulk collection
requires an already configured, permitted integration and approved scope.
Availability depends on the host's connector and agent tools.

| Stage     | Saved artifact                                                                |
| --------- | ----------------------------------------------------------------------------- |
| Research  | `niche-analysis.json` and `niche-report.md`, with sources and coverage limits |
| Ideation  | `validated_ideas.json`, with evidence status and actual selections            |
| Brief     | `video-brief-{slug}.md`                                                       |
| Packaging | `packaging-{slug}.md`, with selected title and thumbnail direction            |
| Outline   | `video-outline-{slug}.md` and `demo-prep-checklist-{slug}.md`                 |

Use the same selected video ID across the last three stages. Read explicit
legacy paths when supplied and preserve unrelated projects. Unknown metrics stay
unknown; proposed ideas and packaging are not forecasts of views or CTR. Outputs
are planning documents and concepts, with their approval/rehearsal status visible.
