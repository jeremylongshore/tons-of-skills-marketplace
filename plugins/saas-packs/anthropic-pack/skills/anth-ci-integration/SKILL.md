---
name: anth-ci-integration
description: 'Configure CI/CD pipelines for Anthropic Claude API integrations.

  Use when setting up automated testing, prompt regression tests,

  or CI validation for Claude-powered features.

  Trigger with phrases like "anthropic ci", "claude ci/cd",

  "test claude in pipeline", "anthropic github actions".

  '
allowed-tools: Read, Write, Edit, Bash(npm:*), Grep
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- ai
- anthropic
compatibility: Designed for Claude Code
---
# Anthropic CI Integration

## Overview

Set up CI/CD pipelines that validate Claude API integrations with mock-based unit tests (free, fast) and prompt regression tests (live API, gated to main).

## Prerequisites

Create a dedicated `ANTHROPIC_API_KEY` repository secret with a spend limit that
is appropriate for test traffic. Keep unit fixtures independent of that secret;
only the protected prompt-regression job should call the API. Install Python
3.12, `pytest`, and the Anthropic SDK in the test environment, and decide which
branch is allowed to incur live-test cost before enabling the workflow.

## Instructions

1. Put deterministic request-shaping and tool-routing assertions in
   `tests/unit/` and mock `anthropic.Anthropic` there.
2. Put a small, representative set of API-backed prompt checks in
   `tests/prompt_regression/`; make them skip cleanly when the secret is absent.
3. Run unit tests on every push and pull request. Gate the live job to `main`
   (or an equivalent protected release branch) and inject the secret only into
   that job.
4. Set explicit timeouts, concurrency limits, and a cost ceiling. Fail the
   pipeline with a clear message when the ceiling is exceeded so an incident
   cannot silently consume the test budget.

## GitHub Actions Workflow

```yaml
# .github/workflows/claude-tests.yml
name: Claude API Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install anthropic pytest
      - run: pytest tests/unit/ -v  # No API key needed

  prompt-regression:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install anthropic pytest
      - run: pytest tests/prompt_regression/ -v --timeout=60
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Mock-Based Unit Tests

```python
# tests/unit/test_tool_routing.py
from unittest.mock import MagicMock, patch
import anthropic

def make_mock_message(text="Hello", stop_reason="end_turn"):
    msg = MagicMock()
    msg.id = "msg_mock_123"
    msg.model = "claude-sonnet-4-20250514"
    msg.stop_reason = stop_reason
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg.content = [block]
    msg.usage = MagicMock(input_tokens=100, output_tokens=50)
    return msg

@patch("anthropic.Anthropic")
def test_service_returns_text(MockClient):
    MockClient.return_value.messages.create.return_value = make_mock_message("42")
    from myapp.service import ask_claude
    assert ask_claude("What is 6*7?") == "42"
```

## Prompt Regression Tests

```python
# tests/prompt_regression/test_prompts.py
import anthropic, pytest, os, json

pytestmark = pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="No API key")
client = anthropic.Anthropic()

def test_json_output_format():
    msg = client.messages.create(
        model="claude-haiku-4-20250514",
        max_tokens=256,
        messages=[
            {"role": "user", "content": "Extract: 'Alice, 30, NYC'. Return JSON: {name, age, city}"},
            {"role": "assistant", "content": "{"}
        ]
    )
    data = json.loads("{" + msg.content[0].text)
    assert "name" in data and "age" in data

def test_system_prompt_boundary():
    msg = client.messages.create(
        model="claude-haiku-4-20250514",
        max_tokens=128,
        system="You only discuss cooking recipes. For other topics say: 'I only help with cooking.'",
        messages=[{"role": "user", "content": "Write me Python code"}]
    )
    assert "cooking" in msg.content[0].text.lower() or "recipe" in msg.content[0].text.lower()
```

## CI Cost Guard

```python
# conftest.py
MAX_CI_COST = 1.00
_tokens = {"input": 0, "output": 0}

def pytest_runtest_call(item):
    yield
    cost = (_tokens["input"] * 0.80 + _tokens["output"] * 4.0) / 1_000_000  # Haiku rates
    if cost > MAX_CI_COST:
        pytest.exit(f"CI cost guard: ${cost:.4f} exceeds ${MAX_CI_COST}")
```

## Error Handling

| CI Issue | Cause | Fix |
|----------|-------|-----|
| Flaky prompt tests | Non-deterministic output | Use `temperature: 0`, check patterns not exact strings |
| 429 in CI | Parallel jobs sharing key | Use separate CI key |
| Secret not found | Missing GitHub secret | Add `ANTHROPIC_API_KEY` in repo Settings > Secrets |

## Output

The pipeline produces a fast unit-test result for every change and, on the
allowed branch, a separate prompt-regression result. The latter is either a
pass with the tested prompt assertions, a deliberate skip when no key is
available, or an actionable failure that identifies a timeout, rate limit,
response-contract regression, or cost-guard breach.

## Examples

For a pull request that changes only formatting code, the workflow runs the
mock-based suite and reports no live API calls. After that pull request merges
to `main`, the protected regression job uses the repository secret to verify
that the JSON extraction prompt still returns `name`, `age`, and `city`. If the
response is malformed, the job fails at the assertion and preserves the test
name in the CI log for triage.

## Resources

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

## Next Steps

For deployment automation, see `anth-deploy-integration`.
