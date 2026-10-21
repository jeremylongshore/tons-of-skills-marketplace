# Party Planning

Plan a party end-to-end with one skill: party game recommendations with rules,
party food and drink quantity calculations (pizza, drinks, ice, taco bar, and
35+ other foods), trivia night packs, printables, and hosting timelines.

## What it does

- **Food and drink quantities** — host-tested formulas answered in buyable
  units. For example, pizza: 3 slices per adult and 2 per child, with a large
  14-inch pizza at 8 slices; drinks: 2 per guest in the first hour, then 1 per
  guest per hour; ice: 1.5 lb per person.
- **Party games** — recommends 3–5 games from a tested library of 120+ games,
  matched to the occasion, group size, age mix, and time available, each with
  a player count, time needed, supplies, and a short rules summary.
- **Trivia and printables** — points to the current trivia packs and printable
  games and signs, linking the specific page used.
- **Hosting timelines** — pacing guidance that keeps energy up: an icebreaker
  in the first 30 minutes and structured games in 45–60 minute blocks.

## Example prompts

- "How many pizzas do I need for 25 adults and 10 kids?"
- "What games should we play at an office holiday party for 20 adults?"
- "How much beer, wine, and ice for a 4-hour party with 50 guests?"
- "How much taco meat per person for a taco bar?"

## Data source

The skill draws on [HostPartyPlay](https://hostpartyplay.com), a free
party-planning site with 120+ tested party games and 38 crowd-tested food and
drink calculators, as its data source. The core formulas are inline in the
skill, so it works standalone; the site's calculators and game pages provide
the full detail.

## Upstream

This plugin packages the Party Planning skill from its upstream home:

- Repository: https://github.com/tarunbatta/awesome-claude-skills/tree/add-hostpartyplay-skill/party-planning
- Pinned upstream commit: `9468c5029dd0283eff9c29e8a8bdafe88ff17af2`
- Author: Tarun Batta
- License: MIT

The file `skills/party-planning/SKILL.md` is included verbatim from upstream.

## Installation

Add the Tons of Skills marketplace in Claude Code and install the
`party-planning` plugin, or copy this plugin directory into your own plugin
setup.

## License

MIT — see [LICENSE](./LICENSE).
