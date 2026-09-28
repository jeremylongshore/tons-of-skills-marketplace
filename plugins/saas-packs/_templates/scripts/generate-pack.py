#!/usr/bin/env python3
"""
Generate a complete SaaS vendor pack from templates and vendor configuration.

Usage:
    python3 generate-pack.py supabase
    python3 generate-pack.py vercel --dry-run
    python3 generate-pack.py --all
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
    import yaml
except ImportError:
    print("Error: Missing dependencies. Run: pip install jinja2 pyyaml")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).parent
TEMPLATES_DIR = SCRIPT_DIR.parent
SLOTS_DIR = TEMPLATES_DIR / "slots"
REPO_ROOT = TEMPLATES_DIR.parent.parent.parent
SAAS_PACKS_DIR = REPO_ROOT / "plugins" / "saas-packs"
VENDORS_DIR = SAAS_PACKS_DIR / "vendors"
TRACKER_CSV = SAAS_PACKS_DIR / "TRACKER.csv"

# Slot definitions by tier
TIER_SLOTS = {
    "standard": [
        "S01-install-auth",
        "S02-hello-world",
        "S03-local-dev-loop",
        "S04-sdk-patterns",
        "S05-core-workflow-a",
        "S06-core-workflow-b",
        "S07-common-errors",
        "S08-debug-bundle",
        "S09-rate-limits",
        "S10-security-basics",
        "S11-prod-checklist",
        "S12-upgrade-migration",
    ],
    "pro": [
        "P13-ci-integration",
        "P14-deploy-integration",
        "P15-webhooks-events",
        "P16-performance-tuning",
        "P17-cost-tuning",
        "P18-reference-architecture",
    ],
    "flagship": [
        "F19-multi-env-setup",
        "F20-observability",
        "F21-incident-runbook",
        "F22-data-handling",
        "F23-enterprise-rbac",
        "F24-migration-deep-dive",
    ],
    "flagship+": [
        "X25-advanced-troubleshooting",
        "X26-load-scale",
        "X27-reliability-patterns",
        "X28-policy-guardrails",
        "X29-architecture-variants",
        "X30-known-pitfalls",
    ],
}


def get_slots_for_tier(tier: str) -> list:
    """Get all slots for a given tier."""
    slots = list(TIER_SLOTS["standard"])
    if tier in ("flagship+", "flagship", "pro"):
        slots.extend(TIER_SLOTS["pro"])
    if tier in ("flagship+", "flagship"):
        slots.extend(TIER_SLOTS["flagship"])
    if tier == "flagship+":
        slots.extend(TIER_SLOTS["flagship+"])
    return slots


def load_vendor_config(company: str) -> dict:
    """Load vendor configuration from YAML file."""
    config_path = VENDORS_DIR / f"{company}.yaml"
    if not config_path.exists():
        # Return default config if no YAML exists
        return get_default_config(company)

    with open(config_path) as f:
        return yaml.safe_load(f)


def get_default_config(company: str) -> dict:
    """Generate default configuration for a vendor."""
    # Load from TRACKER.csv to get tier info
    tier = "standard"
    display_name = company.title()

    if TRACKER_CSV.exists():
        with open(TRACKER_CSV) as f:
            for line in f:
                if line.startswith(f"{company},"):
                    parts = line.strip().split(",")
                    display_name = parts[1]
                    tier = parts[2]
                    break

    return {
        "company": company,
        "display_name": display_name,
        "tier": tier,
        "primary_language": "typescript",
        "npm_package": f"@{company}/sdk",
        "pip_package": company,
        "client_class": f"{display_name.replace(' ', '')}Client",
        "api_url": f"https://api.{company}.com",
        "docs_url": f"https://docs.{company}.com",
        "status_url": f"https://status.{company}.com",
    }


def generate_plugin_json(company: str, display_name: str, tier: str, skill_count: int, config: dict) -> dict:
    """Generate plugin.json manifest."""
    return {
        "name": f"{company}-pack",
        "version": "1.0.0",
        "description": f"Claude Code skill pack for {display_name} ({skill_count} skills)",
        "author": {"name": "Jeremy Longshore", "email": "jeremy@intentsolutions.io"},
        "license": "MIT",
        "keywords": [company, display_name.lower(), "saas", "sdk", "integration"],
    }


def get_skill_slug(slot: str, config: dict) -> str:
    """Get the skill slug for a slot, using vendor-specific slugs when available."""
    slot_slug = slot.split("-", 1)[1]
    if slot == "S05-core-workflow-a":
        slot_slug = config.get("workflow_a_slug", slot_slug)
    elif slot == "S06-core-workflow-b":
        slot_slug = config.get("workflow_b_slug", slot_slug)
    return slot_slug


def generate_readme(config: dict, slots: list) -> str:
    """Generate README.md for the pack."""
    company = config["company"]
    display_name = config["display_name"]
    tier = config["tier"]

    readme = f"""# {display_name} Skill Pack

> Claude Code skill pack for {display_name} integration ({len(slots)} skills)

## Installation

```bash
/plugin install {company}-pack@claude-code-plugins-plus
```

## Skills Included

### Standard Skills (S01-S12)
| Skill | Description |
|-------|-------------|
"""

    # Add standard skills
    for slot in TIER_SLOTS["standard"]:
        skill_slug = get_skill_slug(slot, config)
        skill_name = f"{company}-{skill_slug}"
        readme += f"| `{skill_name}` | {skill_slug.replace('-', ' ').title()} |\n"

    # Add pro skills if applicable
    if tier in ("pro", "flagship", "flagship+"):
        readme += "\n### Pro Skills (P13-P18)\n| Skill | Description |\n|-------|-------------|\n"
        for slot in TIER_SLOTS["pro"]:
            skill_slug = get_skill_slug(slot, config)
            skill_name = f"{company}-{skill_slug}"
            readme += f"| `{skill_name}` | {skill_slug.replace('-', ' ').title()} |\n"

    # Add flagship skills if applicable
    if tier in ("flagship", "flagship+"):
        readme += "\n### Flagship Skills (F19-F24)\n| Skill | Description |\n|-------|-------------|\n"
        for slot in TIER_SLOTS["flagship"]:
            skill_slug = get_skill_slug(slot, config)
            skill_name = f"{company}-{skill_slug}"
            readme += f"| `{skill_name}` | {skill_slug.replace('-', ' ').title()} |\n"

    # Add flagship+ skills if applicable
    if tier == "flagship+":
        readme += "\n### Flagship+ Skills (X25-X30)\n| Skill | Description |\n|-------|-------------|\n"
        for slot in TIER_SLOTS["flagship+"]:
            skill_slug = get_skill_slug(slot, config)
            skill_name = f"{company}-{skill_slug}"
            readme += f"| `{skill_name}` | {skill_slug.replace('-', ' ').title()} |\n"

    readme += f"""
## Usage

Skills trigger automatically when you discuss {display_name} topics. For example:

- "Help me set up {display_name}" → triggers `{company}-install-auth`
- "Debug this {display_name} error" → triggers `{company}-common-errors`
- "Deploy my {display_name} integration" → triggers `{company}-deploy-integration`

## License

MIT
"""
    return readme


def generate_pack(company: str, dry_run: bool = False) -> bool:
    """Generate a complete pack for a vendor."""
    print(f"Generating pack for: {company}")

    # Load configuration
    config = load_vendor_config(company)
    tier = config.get("tier", "standard")
    display_name = config.get("display_name", company.title())
    slots = get_slots_for_tier(tier)

    print(f"  Tier: {tier} ({len(slots)} skills)")

    # Create pack directory
    pack_dir = SAAS_PACKS_DIR / f"{company}-pack"
    skills_dir = pack_dir / "skills"
    plugin_dir = pack_dir / ".claude-plugin"

    # Skip existing packs unless --force
    if pack_dir.exists() and (skills_dir / f"{company}-install-auth" / "SKILL.md").exists():
        print(f"  SKIP: {pack_dir} already exists (use --force to overwrite)")
        return True

    if dry_run:
        print(f"  [DRY RUN] Would create: {pack_dir}")
        print(f"  [DRY RUN] Would create {len(slots)} skills")
        return True

    # Create directories
    pack_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # Setup Jinja2 environment.
    # autoescape is intentionally left off (CodeQL py/jinja2/autoescape-false):
    # every template under SLOTS_DIR renders a SKILL.md (Markdown), never
    # HTML, and the rendered output is written straight to a Markdown file,
    # not served or interpreted as a web page. HTML-escaping would corrupt
    # Markdown syntax and vendor config values (e.g. quotes/ampersands in
    # display names) with spurious `&quot;`/`&amp;` entities.
    env = Environment(loader=FileSystemLoader(str(SLOTS_DIR)), autoescape=False)

    # Generate each skill from template
    for slot in slots:
        skill_slug = get_skill_slug(slot, config)
        skill_name = f"{company}-{skill_slug}"
        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        # Create references/ directory for progressive disclosure
        (skill_dir / "references").mkdir(exist_ok=True)

        template_file = f"{slot}.md.j2"
        try:
            template = env.get_template(template_file)
            content = template.render(**config)

            skill_file = skill_dir / "SKILL.md"
            with open(skill_file, "w") as f:
                f.write(content)

            print(f"  Created: {skill_name}")
        except Exception as e:
            print(f"  ERROR creating {skill_name}: {e}")
            return False

    # Generate plugin.json
    plugin_json = generate_plugin_json(company, display_name, tier, len(slots), config)
    with open(plugin_dir / "plugin.json", "w") as f:
        json.dump(plugin_json, f, indent=2)
    print("  Created: .claude-plugin/plugin.json")

    # Generate README.md
    readme = generate_readme(config, slots)
    with open(pack_dir / "README.md", "w") as f:
        f.write(readme)
    print("  Created: README.md")

    # Create license file
    license_dir = pack_dir / "000-docs"
    license_dir.mkdir(parents=True, exist_ok=True)
    with open(license_dir / "001-BL-LICN-license.txt", "w") as f:
        f.write("MIT License\n\nCopyright (c) 2025 Jeremy Longshore\n")
    print("  Created: 000-docs/001-BL-LICN-license.txt")

    print(f"✓ Pack generated: {pack_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate SaaS vendor skill packs")
    parser.add_argument("company", nargs="?", help="Company name (e.g., supabase)")
    parser.add_argument("--all", action="store_true", help="Generate all packs from TRACKER.csv")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--force", action="store_true", help="Overwrite existing packs")
    args = parser.parse_args()

    if args.all:
        if not TRACKER_CSV.exists():
            print(f"ERROR: TRACKER.csv not found at {TRACKER_CSV}")
            sys.exit(1)

        companies = []
        with open(TRACKER_CSV) as f:
            next(f)  # Skip header
            for line in f:
                if line.strip():
                    companies.append(line.split(",")[0])

        print(f"Generating {len(companies)} packs...")
        for company in companies:
            if not generate_pack(company, args.dry_run):
                print(f"Failed to generate {company}")
                sys.exit(1)

        print(f"\n✓ All {len(companies)} packs generated successfully")
    elif args.company:
        if not generate_pack(args.company, args.dry_run):
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
