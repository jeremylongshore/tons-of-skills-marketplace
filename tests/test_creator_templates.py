"""Validate copied creator templates after consumer formatting and strict gates."""

import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/skill-enhancers/skill-creator"
SKILL = PLUGIN / "skills/skill-creator/templates/skill-template.md"
LEGACY_SKILL = PLUGIN / "templates/skill-template.md"
AGENT = PLUGIN / "skills/skill-creator/templates/agent-template.md"
PRETTIER = ROOT / "node_modules/prettier/bin/prettier.cjs"
VALUES = {
    "SKILL_NAME": "fixture-skill",
    "AGENT_NAME": "fixture-agent",
    "MODEL": "inherit",
    "AUTHOR_NAME": "Fixture Maintainer",
    "AUTHOR_EMAIL": "fixture@example.com",
    "TAG_1": "review",
    "TAG_2": "quality",
    "TOOLS_CSV": "Read, Glob, Grep",
    "ENVIRONMENT_REQUIREMENTS": "Requires the fixture runtime",
    "PURPOSE_STATEMENT": "Review supplied source for correctness",
    "WHEN_TO_USE": "reviewing a bounded source change",
    "NATURAL_TRIGGER": "review this change",
    "CONCISE_AGENT_SPECIALTY_20_1536_CHARS": "Review supplied source and report correctness evidence.",
}


def render(source):
    return re.sub(
        r"\{\{(.*?)\}\}",
        lambda match: VALUES.get(match.group(1).strip(), "Inspect supplied source and report evidence."),
        source,
        flags=re.S,
    )


def metadata(source):
    return yaml.safe_load(source.split("---", 2)[1])


def format_template(path):
    # Installed/copied templates live outside this repository's template ignores.
    with tempfile.TemporaryDirectory(prefix="creator-template-copy-") as folder:
        result = subprocess.run(
            ["node", str(PRETTIER), "--parser", "markdown", "--stdin-filepath", str(Path(folder) / "artifact.md")],
            input=path.read_text(),
            text=True,
            capture_output=True,
            cwd=folder,
            check=True,
            timeout=20,
        )
    return result.stdout


@pytest.fixture(scope="module")
def validator():
    spec = importlib.util.spec_from_file_location(
        "creator_canonical_validator", ROOT / "scripts/validate-skills-schema.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("template", [SKILL, LEGACY_SKILL, AGENT], ids=["skill", "legacy-skill", "agent"])
def test_formatting_preserves_rendered_template_inputs(template):
    before = metadata(render(template.read_text()))
    after = metadata(render(format_template(template)))
    assert after == before
    assert isinstance(after["name"], str)
    assert all(isinstance(tag, str) for tag in after["tags"])


@pytest.mark.parametrize("template", [SKILL, LEGACY_SKILL], ids=["skill", "legacy-skill"])
def test_formatted_skill_template_passes_marketplace_gate(template, tmp_path, validator):
    path = tmp_path / "fixture-skill/SKILL.md"
    path.parent.mkdir()
    path.write_text(render(format_template(template)))
    result = validator.validate_skill(path, tier=validator.TIER_MARKETPLACE)
    assert not result.get("fatal"), result
    assert not result["errors"], result


def write_agent(tmp_path, context, source):
    path = tmp_path / context / "agents/fixture-agent.md"
    path.parent.mkdir(parents=True)
    if context == "plugin":
        manifest = path.parent.parent / ".claude-plugin/plugin.json"
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({"name": "fixture", "version": "1.0.0"}))
    else:
        front, body = source.split("\n---\n", 1)
        front = re.sub(r"(?m)^#\s*(hooks|mcpServers|permissionMode):", r"\1:", front)
        source = front + "\n---\n" + body
    path.write_text(source)
    return path


@pytest.mark.parametrize("context", ["plugin", "standalone"])
def test_formatted_agent_template_passes_context_gate(context, tmp_path, validator):
    path = write_agent(tmp_path, context, render(format_template(AGENT)))
    assert validator.detect_component(path) == ("agent", context)
    result = validator.validate_agent(path)
    assert not result.get("fatal"), result
    assert not result["errors"], result


@pytest.mark.parametrize("model", ["inherit", "claude-fixture-model-1"])
@pytest.mark.parametrize("tools", [["Read", "Glob", "Grep"], "Read, Glob, Grep"], ids=["array", "csv"])
def test_agent_gate_accepts_model_and_tool_wire_forms(model, tools, tmp_path, validator):
    source = render(format_template(AGENT))
    fm, body = validator.parse_frontmatter(source)
    fm.update(model=model, tools=tools)
    path = write_agent(tmp_path, "plugin", "---\n" + yaml.safe_dump(fm) + "---\n" + body)
    assert validator.detect_component(path) == ("agent", "plugin")
    result = validator.validate_agent(path)
    assert not result.get("fatal"), result
    assert not result["errors"], result


@pytest.mark.parametrize("field", ["compatible-with", "when_to_use"])
def test_agent_rejects_skill_fields(field, tmp_path, validator):
    source = render(format_template(AGENT))
    fm, body = validator.parse_frontmatter(source)
    fm[field] = "fixture"
    path = write_agent(tmp_path, "plugin", "---\n" + yaml.safe_dump(fm) + "---\n" + body)
    result = validator.validate_agent(path)
    assert any(f"Invalid field '{field}'" in error for error in result["errors"]), result


def test_missing_author_is_rejected(tmp_path, validator):
    source = render(SKILL.read_text())
    fm, body = validator.parse_frontmatter(source)
    del fm["author"]
    path = tmp_path / "fixture-skill/SKILL.md"
    path.parent.mkdir()
    path.write_text("---\n" + yaml.safe_dump(fm) + "---\n" + body)
    result = validator.validate_skill(path, tier=validator.TIER_MARKETPLACE)
    assert any("Missing required field: 'author'" in error for error in result["errors"])


def test_template_does_not_bypass_mcp_allowlist(tmp_path, validator):
    path = write_agent(tmp_path, "plugin", render(AGENT.read_text()))
    assert not validator.validate_agent(path)["errors"]
    path.write_text(path.read_text() + "\nCall mcp__fixture__unlisted to inspect the source.\n")
    assert validator.validate_agent(path)["errors"]
