# Fixing kernel shadow field diagnostics

The kernel shadow lane compares skill frontmatter against the pinned kernel's `authoring/v1` and `authoring/v2` profiles.
It remains advisory: these findings do not change the authoritative Python validator or activate a new blocking gate.
This guide is preparation for the separately governed migration, not a deprecation announcement; no activation date or notice window is established here.

## Read the finding

Each `fieldDiagnostics` entry in the shadow `report.json` retains the file, profile, installed kernel version, JSON Pointer, AJV keyword, schema path, message and parameters.
Required-field findings point to the missing property itself, such as `/license`, rather than the parent `/`.
Nested required properties include their parent path; JSON Pointer uses `~1` for `/` and `~0` for `~` in property names.
The report includes every kernel finding, including files both validators reject; console and GitHub summaries show the first 40 with a total and report pointer.
A parse failure points to `/` and must be fixed before field validation can run.

## Repair the frontmatter

Use the [current required set](../000-docs/SCHEMA_CHANGELOG.md#non-negotiables--read-before-touching-this-file) and [skills standard](../000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md) to check the named field.
Missing fields need truthful values appropriate to the skill; do not copy placeholder ownership, licensing or compatibility claims merely to pass a check.
Type, pattern and enum failures require inspecting the reported profile and schema path, rather than deleting the field.
For `allowed-tools`, use only needed tools and scoped Bash permissions; both string and YAML-list forms are supported by the current standard.

The diagnostic's 6767-h § 3.1 link is historical and explicitly marked superseded.
Its old checklist omits `compatibility` and `tags`, and its CSV-only tool rule is obsolete.
The [section-level disposition](../000-docs/727-AT-ARCH-master-modernization-blueprint.md#section-level-disposition-of-6767-h) identifies the replacement authority.
Do not treat that historical section as a new requirement or rewrite its frozen anchors.
Optional or unknown fields have no invented 6767-h field citation; use their precise schema path and the current standards.

Run the authoritative validator against your plugin after editing:

```bash
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/<category>/<name>/
```

Retain the full diagnostic and a sanitized reproducer if the current rules and the pinned profile disagree.
Follow the [exception-request process](../.github/CONTRIBUTING.md#marketplace-acceptance-and-exceptions) for a reviewed disposition.
A submitted request alone does not waive a gate.

## Required-field repair references

These links locate the failed field for repair; the linked current standards and installed schema profile remain authoritative for its constraints.

### name

Check the skill identifier against the reported name constraint and its directory naming convention.
Preserve the skill's actual identity; do not substitute an unrelated example identifier.

### description

Describe the skill's actual capability and when it should be invoked.
Inspect the specific length, pattern or content finding instead of filling the field with generic text.

### allowed-tools

Declare only the tools the skill needs, using the current string or YAML-list representation.
For a scoped-Bash finding, replace bare Bash access with the required command scopes; do not disable the check.

### version

Use the skill's actual version and the format required by the reported profile.
Changing diagnostic output alone does not justify changing a skill's version.

### author

Supply accurate authorship and preserve upstream attribution.
A required author field does not authorize publishing private contact details.

### license

Declare the license actually granted for this skill.
If rights are uncertain, resolve them before assigning a license value.

### compatibility

Describe the supported host or environment accurately.
Follow the current compatibility guidance in the schema changelog; the historical 6767-h checklist omits this field.

### tags

Use relevant tags in the shape required by the current profile and inspect any item-level pointer.
The historical 6767-h checklist omits this field; its absence there is not a waiver of the current required set.

## Activation boundary

DR-049 still requires the complete public migration pack, direct notice to affected authors, VP DevRel co-sign, an elapsed fourteen-day public window and all other ratified flip prerequisites.
The lab tracks notice evidence separately; this guide and synthetic tests prove neither publication of that pack nor delivery to any author.
Tracking: `bd_000-projects-3kye.9`, [SAK coordination](https://github.com/jeremylongshore/intent-eval-core/issues/13).
