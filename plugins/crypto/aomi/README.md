# Aomi — Agent Skills bundle

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) ![Works with Claude Code · Cursor · Gemini · Codex · Copilot](https://img.shields.io/badge/Works%20with-Claude%20Code%20%C2%B7%20Cursor%20%C2%B7%20Gemini%20%C2%B7%20Codex%20%C2%B7%20Copilot-6E56CF)

> Aomi for AI agents — drive on-chain action and build new app integrations through natural-language prompts. Works with Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code Copilot, and any [Agent Skills](https://agentskills.io)–compatible AI tool.

## What's in this bundle

| Skill | Purpose | Risk tier | Audience |
|-------|---------|-----------|----------|
| [`aomi-transact`](skills/transact/SKILL.md) | Drive the Aomi CLI to chat, simulate, and sign on-chain transactions with account-abstraction-first execution. Wraps swaps, lending, bridges, staking, perps, and CEX read across integrated EVM apps, with Solana sign-only support where unsigned transactions are returned. | **L2** (signs/broadcasts) | End-user / power-user |
| [`aomi-build`](skills/build/SKILL.md) | Scaffold new Aomi apps and plugins from API docs, OpenAPI/Swagger specs, SDK docs, and product requirements. Generates Rust SDK crates with `lib.rs`, `client.rs`, `tool.rs`, plus tool schemas, preambles, and host-interop flows. | **L1** (scaffolds code) | Developer |

The two skills are different audiences and different risk profiles. Bundling means the agent loads only the skill whose description triggers match — there is no token bloat for installing both.

## Install

### Via Claude Code (after Anthropic listing lands)

```bash
/plugin marketplace add anthropics/claude-code
/plugin install aomi
```

### Via Self-hosted marketplace (canonical alternative)

```bash
/plugin marketplace add aomi-labs/skills
/plugin install aomi
```

### Via `gh` extension

```bash
gh extension install ai-ecoverse/gh-upskill
gh upskill aomi-labs/skills --skill aomi
```

### Via direct clone

```bash
git clone https://github.com/aomi-labs/skills
cp -r skills/plugins/aomi ~/.claude/skills/
```

## Prerequisites

```bash
# Required for aomi-transact (the on-chain CLI driver)
npm install -g @aomi-labs/client@latest      # v0.4.2 or newer
```

`aomi-build` has no runtime prerequisites — it generates Rust source code from specs.

## Usage

Once installed, ask your agent in natural language. The agent picks the right skill based on the prompt:

**Triggers `aomi-transact`:**
- *"What's the price of ETH?"*
- *"Swap 1 USDC for WETH on Uniswap V3, send to my wallet."*
- *"Stake 0.01 ETH with Lido."*
- *"Bridge 50 USDC from Ethereum to Base via CCTP."*

**Triggers `aomi-build`:**
- *"Use aomi-build to turn this OpenAPI spec into an Aomi app."*
- *"Build an Aomi plugin from these REST endpoints."*
- *"Convert this SDK README into an Aomi tool surface."*

## Bundle structure

```
aomi/
├── .claude-plugin/
│   └── plugin.json             # bundle manifest
├── README.md                   # this file
├── LICENSE                     # MIT
├── SECURITY.md                 # bundle-level OWASP AST01–AST10 walkthrough
└── skills/
    ├── transact/
    │   ├── SKILL.md            # main skill
    │   ├── agents/openai.yaml  # Codex/OpenAI host metadata
    │   ├── references/
    │   │   ├── account-abstraction.md
    │   │   ├── apps.md
    │   │   ├── drain-vectors.md
    │   │   ├── examples.md
    │   │   ├── session.md
    │   │   └── troubleshooting.md
    │   └── templates/
    │       └── aomi-workflow.sh
    └── build/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        │   ├── aomi-sdk-patterns.md
        │   ├── examples.md
        │   ├── host-routes.md
        │   ├── spec-to-tools.md
        │   └── troubleshooting.md
        └── templates/
            └── quick-scaffold.sh
```

## Security posture

`aomi-transact` ships with a complete [OWASP AST03 (Over-Privileged Skills)](https://owasp.org/www-project-agentic-skills-top-10/ast03) permission manifest in its frontmatter — `risk_tier: L2`, `permissions.{files,network,shell,tools}` declarations. `aomi-build` is `risk_tier: L1` (scaffolds code, no transaction side effects).

The bundle has been scanned by four independent tools: Cisco AI Defense skill-scanner, pors/skill-audit, NMitchem/SkillScan, and Snyk agent-scan. Captured reports live at [`.scanner-reports/`](https://github.com/aomi-labs/skills/tree/main/.scanner-reports) in the repo root. Per-skill OWASP AST01–AST10 walkthroughs are in [`SECURITY.md`](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).

## About Aomi

Aomi Labs builds native harness around blockchains functioning like Claude Code on-chain. We specialize in executions against arbitrary protocol with non-custodial workflow, account abstraction, and full security with simulations. Aomi also host agentic applications deployed and owned by developers, companies, and agents. Aomi provides E2E integration with UI, Skills and SDKs.

**Links:**
- 🌐 Website: [aomi.dev](https://aomi.dev)
- 🤖 Agents: [aomi.dev/agents](https://aomi.dev/agents)
- 𝕏 Twitter: [x.com/aomi_labs](https://x.com/aomi_labs)
- 💻 GitHub: [github.com/aomi-labs](https://github.com/aomi-labs)
- 📦 Packages:
  - [@aomi-labs/react](https://www.npmjs.com/package/@aomi-labs/react)
  - [aomi-sdk](https://crates.io/crates/aomi-sdk)
