#!/usr/bin/env python3
"""Generate skill database (CSV + MD files) for a vendor."""

import os
import sys
import csv


# These vendors have replaced or retired the legacy fixed-taxonomy database.
# Refuse regeneration so deleted filler cannot silently reappear through an old
# release command.
RETIRED_SKILL_DATABASES = {
    "framer": "The unsupported Framer tutorial pack is retired (claude-juoz.3.11.57)",
    "apple-notes": "The unsupported Apple Notes tutorial pack is retired (claude-juoz.3.11.56)",
    "gamma": "The unsupported Gamma tutorial pack is retired (claude-juoz.3.11.55)",
    "glean": "The unsafe Glean tutorial pack is retired (claude-juoz.3.11.54)",
    "clay": "The unsupported Clay tutorial pack is retired (claude-juoz.3.11.53)",
    "appfolio": "The unsupported AppFolio tutorial pack is retired (claude-juoz.3.11.52)",
    "snowflake": "Snowflake v2 uses the curated snowflake-pack operator skills",
    "langfuse": "Langfuse v2 uses the five evidence-driven langfuse-pack operator skills",
}

# Skill templates for flagship tier (24 skills)
FLAGSHIP_SKILLS = [
    # Onboarding (6)
    ("install-auth", "onboarding", "Install and configure {display} SDK/CLI authentication"),
    ("hello-world", "onboarding", "Create a minimal working {display} example"),
    ("local-dev-loop", "onboarding", "Configure {display} local development workflow"),
    ("sdk-patterns", "onboarding", "Apply production-ready {display} SDK patterns"),
    ("primary-workflow", "onboarding", "Execute {display} primary workflow"),
    ("core-feature", "onboarding", "Implement {display} core feature integration"),
    # Operations (6)
    ("common-errors", "operations", "Diagnose and fix {display} common errors"),
    ("debug-bundle", "operations", "Collect {display} debug evidence for support"),
    ("rate-limits", "operations", "Implement {display} rate limiting and backoff"),
    ("security-basics", "operations", "Apply {display} security best practices"),
    ("prod-checklist", "operations", "Execute {display} production deployment checklist"),
    ("upgrade-migration", "operations", "Plan and execute {display} SDK upgrades"),
    # CI/CD (6)
    ("ci-integration", "cicd", "Configure {display} CI/CD integration"),
    ("deploy-pipeline", "cicd", "Deploy {display} integrations to production"),
    ("webhooks-events", "cicd", "Implement {display} webhook handling"),
    ("performance-tuning", "cicd", "Optimize {display} API performance"),
    ("cost-tuning", "cicd", "Optimize {display} costs and usage"),
    ("reference-architecture", "cicd", "Implement {display} reference architecture"),
    # Enterprise (6)
    ("multi-env-setup", "enterprise", "Configure {display} multi-environment setup"),
    ("observability", "enterprise", "Set up {display} monitoring and observability"),
    ("advanced-troubleshooting", "enterprise", "Apply {display} advanced debugging"),
    ("load-scale", "enterprise", "Implement {display} load testing and scaling"),
    ("reliability-patterns", "enterprise", "Implement {display} reliability patterns"),
    ("known-pitfalls", "enterprise", "Identify and avoid {display} anti-patterns"),
]

# Pro tier (18 skills) - subset
PRO_SKILLS = FLAGSHIP_SKILLS[:18]

# Standard tier (12 skills) - subset
STANDARD_SKILLS = FLAGSHIP_SKILLS[:12]


def generate_csv(vendor: str, display: str, skills: list, output_dir: str):
    """Generate skills CSV file."""
    csv_path = os.path.join(output_dir, f"{vendor}-skills.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Name",
                "Who",
                "What",
                "When",
                "Where",
                "Definition_of_Success_Technical",
                "Definition_of_Success_Business",
                "Target_Goal",
                "Production",
                "Category",
                "Path",
                "Allowed_Tools",
                "Version",
                "License",
                "Author",
            ]
        )

        for skill_name, category, what_template in skills:
            full_name = f"{vendor}-{skill_name}"
            what = what_template.format(display=display)

            # Generate trigger phrases
            triggers = f"{vendor} {skill_name.replace('-', ' ')}, {what.lower()}"

            # Determine allowed tools based on category
            if category == "onboarding":
                tools = "Read, Write, Edit, Bash(npm:*), Bash(pip:*), Grep"
            elif category == "operations":
                tools = "Read, Grep"
            elif category == "cicd":
                tools = "Read, Write, Edit, Bash(gh:*)"
            else:  # enterprise
                tools = "Read, Write, Edit, Bash(kubectl:*)"

            writer.writerow(
                [
                    full_name,
                    "Backend developers, DevOps engineers, Full-stack developers",
                    what,
                    triggers,
                    f"Claude Code skill; {display} SDK; local/cloud development",
                    f"Working {display} integration; Tests passing; Documentation updated",
                    f"Faster {display} integration; Reduced errors; Team productivity",
                    f"Complete {display} {skill_name.replace('-', ' ')} in under 15 minutes",
                    "true",
                    category,
                    f"plugins/saas-packs/{vendor}-pack/skills/{full_name}/",
                    tools,
                    "1.0.0",
                    "MIT",
                    "Jeremy Longshore <jeremy@intentsolutions.io>",
                ]
            )

    return csv_path


def generate_md(vendor: str, display: str, skill_name: str, category: str, what: str, output_dir: str):
    """Generate skill MD file."""
    full_name = f"{vendor}-{skill_name}"
    md_path = os.path.join(output_dir, f"{full_name}.md")

    content = f"""# {full_name}

## File Scaffold

```
{full_name}/
-- SKILL.md
```

## File Descriptions

### 1. SKILL.md
**Purpose:** {what}
**Workflow:** Part of the {category} skill category for {display} integration.
**Relates to:** Other {vendor} skills in this pack.

## Summary

This skill helps developers {what.lower()}. It provides step-by-step guidance for {display} integration following best practices and production-ready patterns. Use this skill to accelerate your {display} development workflow.
"""

    with open(md_path, "w") as f:
        f.write(content)

    return md_path


def generate_skill_database(vendor: str, display: str, tier: str):
    """Generate complete skill database for a vendor."""
    normalized_vendor = vendor.strip().casefold()
    if normalized_vendor in RETIRED_SKILL_DATABASES:
        reason = RETIRED_SKILL_DATABASES[normalized_vendor]
        raise ValueError(f"skill database generation is retired for {vendor!r}: {reason}")

    output_dir = f"plugins/saas-packs/skill-databases/{vendor}"
    os.makedirs(output_dir, exist_ok=True)

    # Select skills based on tier
    if tier == "flagship+":
        skills = FLAGSHIP_SKILLS + [
            ("architecture-variants", "advanced", f"Choose {display} architecture blueprints"),
            ("policy-guardrails", "advanced", f"Implement {display} policy enforcement"),
            ("migration-deep-dive", "advanced", f"Execute {display} major migrations"),
            ("data-handling", "advanced", f"Implement {display} data compliance"),
            ("incident-runbook", "advanced", f"Execute {display} incident response"),
            ("enterprise-rbac", "advanced", f"Configure {display} enterprise access control"),
        ]
    elif tier == "flagship":
        skills = FLAGSHIP_SKILLS
    elif tier == "pro":
        skills = PRO_SKILLS
    else:  # standard
        skills = STANDARD_SKILLS

    # Generate CSV
    csv_path = generate_csv(vendor, display, skills, output_dir)
    print(f"Created: {csv_path}")

    # Generate MD files
    for skill_name, category, what_template in skills:
        what = what_template.format(display=display)
        md_path = generate_md(vendor, display, skill_name, category, what, output_dir)
        print(f"Created: {md_path}")

    return len(skills)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: generate-skill-db.py <vendor> <display_name> <tier>")
        print("Tiers: flagship+, flagship, pro, standard")
        sys.exit(1)

    vendor = sys.argv[1]
    display = sys.argv[2]
    tier = sys.argv[3]

    try:
        count = generate_skill_database(vendor, display, tier)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)
    print(f"\nGenerated {count} skills for {display}")
