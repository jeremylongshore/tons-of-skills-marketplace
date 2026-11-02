# DVERA — CT Verification Skills for C/C++ Coding Agents

> 한국어: [README.ko.md](README.ko.md)

DVERA (Dynamic Verification Agent) brings CT C/C++ verification work into coding agents such as Claude Code, Codex CLI, Cursor, and GitHub Copilot. It uses the working context of source code, requirements, build information, source changes, and existing test assets to prepare and request CT verification work.

CT (Controller Tester) is a test automation solution for unit, integration, and code-based testing of mission-critical C/C++ software. It brings together test-environment setup, test design and generation, execution, code-coverage analysis, reporting, and traceability management.

DVERA does not replace CT's verification results. The coding agent helps prepare and coordinate verification work; CT performs the analysis, build, test execution, and result aggregation. Generated tests must be reviewed for test intent, data, and expected results, then confirmed with actual execution results and measured coverage.

## What the CT and DVERA workflow adds

| Verification need | CT and DVERA workflow |
|---|---|
| Complex C/C++ environments | Capture compiler, macro, include-path, toolchain, build, and target conditions before analysis. |
| Unit and integration verification | Design and execute tests at function, module, and interface levels, including existing GoogleTest assets where applicable. |
| Reviewable evidence | Connect test intent, execution results, statement/branch/MC/DC coverage, reports, and requirement links for review. |
| Repeated change verification | Re-run affected tests after code changes and review new failures and coverage deltas for regression follow-up. |
| AI-assisted test work | Use code, requirements, and change context to prepare test work, then improve it with CT analysis and measured results. |

## Workflow at a glance

1. Prepare the compiler, macro, include-path, toolchain, and target context for a CT project.
2. Analyze the project and resolve environment or configuration issues through a controlled feedback loop.
3. Generate, execute, and improve unit or integration tests using build, execution, and coverage feedback.
4. Review coverage and results, produce reports, and re-run affected verification after source changes.

The Skills in this repository document that product-connected workflow. They are not standalone replacements for a CT installation.

## Install

In Claude Code:

```text
/plugin marketplace add SuresoftTechnologies/dvera-plugin
/plugin install dvera@suresofttech
```

Or from a terminal:

```text
claude plugin marketplace add SuresoftTechnologies/dvera-plugin
claude plugin install dvera@suresofttech
```

Skills then load as `/dvera:ct-init-project`, `/dvera:ct-test-loop`, and so on. The plugin adds about 620 tokens to every session; each Skill body is read only when that Skill runs.

Product-backed actions need a deployed CT environment. Without one, a Skill stops at its installation check and shows how to reach product support.

## Example requests

Trigger examples from the CT user guide. Responses can vary with the AI model and conversation context; if the result differs from what you expect, rephrase the request with more detail and retry.

| Request | Skill |
|---|---|
| `Create a CT project and start verification.` | `ct-init-project` |
| `Run tests in CT.` | `ct-init-project` |
| `Generate tests for the calculate_checksum function.` | `ct-test-loop` |
| `Find functions without tests and generate tests for them.` | `ct-test-loop` |
| `Run regression tests.` | `ct-regression` |
| `Open CT.` | `ct-open` |

## Skills

All Skills require a deployed CT environment for their product-backed actions and stop with an installation notice when none is found.

| Skill | CT workflow stage |
|---|---|
| `ct-init-project` | Start or prepare a CT verification project. |
| `ct-extract-macro` | Capture target compiler macros and build-environment facts. |
| `ct-make-conf` | Prepare the analysis configuration for the selected toolchain. |
| `ct-setup-project` | Create the CT project and apply build inputs. |
| `ct-analysis-loop` | Analyze the project and resolve configuration or toolchain issues. |
| `ct-test-loop` | Generate, run, and improve tests. |
| `ct-kb-update` | Record verified workflow observations after a completed CT run. |
| `ct-regression` | Re-run existing tests after a code change and review deltas. |
| `ct-self-healing` | Run regression evidence collection and identify CT Self-Healing review candidates. |
| `ct-run-gtest` | Re-run GoogleTest assets registered in CT and review results and coverage. |
| `ct-req-to-test` | Generate and execute a CT AI test from approved requirements. |
| `ct-report` | Export execution and coverage evidence. |
| `ct-open` | Open the CT project for visual inspection. |
| `ct-orchestrator` | Resume the appropriate stage of an in-progress verification workflow. |

## Product-backed workflow

DVERA works with a deployed CT and DVERA environment. This repository documents the verification workflow and ships an MCP server that forwards tool calls to a local CT installation, but does not include the CT runtime or product installation.

Without the deployed environment, users can inspect this repository's documented workflow, but a Skill that needs CT actions stops at its installation check. It must not claim that CT analysis, execution, coverage measurement, or reporting has occurred.

## MCP tools

Give the agent CT's verification tools directly. With the MCP server
(`scripts/dvera-mcp.py`) connected, it can create the project, run analysis, generate and
execute tests, and read coverage back without leaving the conversation - the same tools CT
exposes to its own agent. Calls go to CT's `ct_tool.py` entry point, and the server keeps no
process of its own between them.

Connect it in one of two ways.

**Point an MCP client at the interpreter CT already ships** - no extra install:

```json
{
  "mcpServers": {
    "dvera": {
      "command": "C:/Program Files/Suresoft/CT 2026/python/python.exe",
      "args": ["/path/to/dvera-plugin/scripts/dvera-mcp.py"]
    }
  }
}
```

On Linux the interpreter is at `<CT install>/python/python3`. Any Python 3.8 or later works
if you would rather use your own. Replace the script path with wherever this repository
sits: clone it, or use the copy the plugin manager installed (`claude plugin list` shows
where plugins live). The server takes the source directory from the client's working
directory, so run the client from the project you want to verify.

**Or install the bundle** from this repository's releases: download `dvera-mcp.mcpb` and
open it with a client that installs MCP bundles. It resolves its own Python, so nothing has
to be installed first.

Set `CT_HOME` if CT is installed outside the default location. The server is safe to leave
configured on any machine: it starts either way, and without CT it offers a single tool,
`dvera_check_environment`, which reports what is missing and what to do about it. That tool
is also there when CT is - run it first whenever the verification tools do not appear.

## Requirements for product-backed verification

- CT 2026.06 or later
- A valid CT license
- A supported C/C++ build and target environment
- DVERA integration supplied as part of the deployed CT environment

For a product demo, purchase, or deployment consultation, contact [bizcenter@suresofttech.com](mailto:bizcenter@suresofttech.com).

## Privacy Policy

The MCP server in this repository runs entirely on your machine.

- It sends nothing to Suresoft Technologies or to any third party. There is no telemetry,
  no analytics, and no network call of its own.
- Tool arguments are passed to the CT installation on the same machine, and CT's response is
  returned to your MCP client. Nothing is written outside CT's own workspace.
- It stores no credentials and reads no files beyond the CT installation directory and the
  paths a tool call names.
- Anything CT itself records - workspaces, analysis output, reports - is governed by CT's own
  handling of that data, not by this repository.

The Skills are documentation: they carry no code that runs on your machine.

The full policy is in [PRIVACY.md](PRIVACY.md). Questions about data handling in the CT
product itself go to
[bizcenter@suresofttech.com](mailto:bizcenter@suresofttech.com).

## License and trademarks

This repository is licensed under the [MIT License](LICENSE). The license covers everything in this repository - the documentation, the Skill files, and the MCP server source. It does not cover CT itself: CT and DVERA are Suresoft Technologies products, and no product functionality or product licence is granted by this repository.

GoogleTest is a trademark of Google LLC. This repository is not affiliated with, sponsored by, or endorsed by Google. Other product names may be trademarks of their respective owners.
