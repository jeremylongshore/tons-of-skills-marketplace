/**
 * Machine-readable ownership registry for generated projections and retained
 * point-in-time evidence. Consumers must use this registry instead of growing
 * private path lists.
 */

export const GENERATED_ARTIFACT_REGISTRY = [
  {
    id: 'epic-1-scorecard',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^000-docs\/742-RA-DATA-epic-1-scorecard\.json$/,
    canonical: 'scripts/measure-epic-1.mjs',
    regenerate: 'pnpm run measure:e1',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    why: 'governed Epic 1 measurement output',
  },
  {
    id: 'marketplace-catalog-projection',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/catalog\.json$/,
    canonical: '.claude-plugin/marketplace.extended.json and skills-catalog.json',
    regenerate: 'node marketplace/scripts/sync-catalog.mjs --check',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    contentCheck: true,
    why: 'deterministic website plugin projection rendered only from canonical catalog and full skill projection inputs; E1.8 removed output self-reference and runtime timestamps before activating the content gate',
  },
  {
    id: 'marketplace-skills-catalog-projection',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/skills-catalog\.json$/,
    canonical: '.claude-plugin/marketplace.extended.json and plugin SKILL.md sources',
    regenerate: 'node marketplace/scripts/discover-skills.mjs --level=full --check',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    contentCheck: true,
    why: 'deterministic L1 skill projection used by the website and Freshie consumers; E1.8 aligned its stale baseline with the marketplace-visible corpus before activating the content gate',
  },
  {
    id: 'marketplace-skills-index-projection',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/skills-index\.json$/,
    canonical: '.claude-plugin/marketplace.extended.json and plugin SKILL.md sources',
    regenerate: 'node marketplace/scripts/discover-skills.mjs --level=full --check',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    contentCheck: true,
    why: 'deterministic L0 skill projection used for catalog browsing and trigger matching',
  },
  {
    id: 'marketplace-search-projection',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/unified-search-index\.json$/,
    canonical: 'catalog.json, skills-catalog.json, plugin sources, and marketplace documentation',
    regenerate: 'node marketplace/scripts/generate-unified-search.mjs --check',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    contentCheck: true,
    why: 'deterministic search projection consumed by marketplace discovery surfaces; exact staged bytes are enforced by the shared E1.8 gate',
  },
  {
    id: 'marketplace-external-stats',
    kind: 'external_snapshot',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/(?:github|npm|skills)-stats\.json$/,
    canonical: 'point-in-time GitHub, npm, and skills.sh API observations',
    regenerate: null,
    freshnessOwner: '727:epic-1.10',
    why: 'network observations require freshness bounds and cannot participate in a deterministic every-PR regeneration gate',
  },
  {
    id: 'marketplace-spotlight-editorial-data',
    kind: 'canonical_data',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/data\/spotlights\.json$/,
    canonical: 'marketplace/src/data/spotlights.json',
    regenerate: null,
    why: 'editorial selection mutated intentionally by promote-spotlight.mjs and rendered by marketplace routes',
  },
  {
    id: 'marketplace-canonical-data',
    kind: 'canonical_data',
    tracking: 'tracked',
    pattern:
      /^marketplace\/src\/data\/(?:collections|cowork-packs|heat-check|jeremys-stash|partners|vendor-packs|verification-rubric)\.json$/,
    canonical: 'the tracked marketplace/src/data JSON file itself',
    regenerate: null,
    why: 'hand-authored marketplace collections, packs, partners, and policy data with no executable writer',
  },
  {
    id: 'marketplace-readme-sections-build-data',
    kind: 'generated_projection',
    tracking: 'untracked',
    pattern: /^marketplace\/src\/data\/readme-sections\.json$/,
    pathspec: ':(top)marketplace/src/data/readme-sections.json',
    glob: 'marketplace/src/data/readme-sections.json',
    canonical: 'plugin README.md files',
    regenerate: 'cd marketplace && node scripts/extract-readme-sections.mjs',
    why: 'Astro build-only plugin-page projection regenerated before build and development consumers run',
  },
  {
    id: 'marketplace-plugin-content',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^marketplace\/src\/content\/plugins\/.*\.json$/,
    canonical: '.claude-plugin/marketplace.extended.json and plugin source files',
    regenerate: 'cd marketplace && node generate-content.js',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    why: 'Astro plugin content generated from repository plugin metadata',
  },
  {
    id: 'plugin-package-manifests',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^plugins\/[^/]+\/[^/]+\/package\.json$/,
    canonical: 'plugin.json and repository package policy',
    regenerate: 'node scripts/generate-plugin-package-jsons.mjs',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    why: 'package tracking manifests generated from plugin metadata',
  },
  {
    id: 'curated-skill-mirror',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^skills\/\.curated\//,
    canonical: 'plugin skill sources selected by freshie/grades.csv',
    regenerate: 'python3 freshie/scripts/promote-to-curated.py',
    why: 'curated skills.sh projection',
  },
  {
    id: 'disposition-ledger',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern: /^freshie\/disposition-ledger\.json$/,
    canonical: 'freshie/grades.csv and scripts/validate-skills-schema.py',
    regenerate: 'pnpm run generate:disposition-ledger',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    why: 'Blueprint 727 §8 first-match-wins disposition for every Freshie-graded artifact',
  },
  {
    id: 'saas-tutorial-lattice',
    kind: 'generated_projection',
    tracking: 'tracked',
    pattern:
      /^(?:freshie\/saas-tutorial-lattice\.json|000-docs\/813-RA-AUDT-saas-tutorial-lattice\.md)$/,
    canonical: '.claude-plugin/marketplace.extended.json and tracked SaaS pack skill sources',
    regenerate: 'pnpm run generate:saas-lattice',
    postprocess: 'pnpm run normalize:dead-domain-projections',
    why: 'Bead claude-juoz.3.11 deterministic denominator and WIP-limited pack review queue',
  },
  {
    id: 'marketplace-public-data',
    kind: 'generated_projection',
    tracking: 'untracked',
    pattern: /^marketplace\/public\/data\/.*\.json$/,
    pathspec: ':(top)marketplace/public/data/*.json',
    glob: 'marketplace/public/data/*.json',
    canonical: 'marketplace/src/data/*.json',
    regenerate: 'cd marketplace && npm run build   (or: node scripts/copy-public-data.mjs)',
    why: 'runtime static-asset copy of the canonical build data; ~28.5MB when tracked',
  },
  {
    id: 'cowork-downloads',
    kind: 'generated_projection',
    tracking: 'untracked',
    pattern: /^marketplace\/public\/downloads\//,
    pathspec: ':(top)marketplace/public/downloads/**',
    glob: 'marketplace/public/downloads/**',
    canonical: '.claude-plugin/marketplace.extended.json',
    regenerate: 'cd marketplace && npm run build   (cowork:zips)',
    why: 'cowork zips are rebuilt from the catalog on every build',
  },
  {
    id: 'freshie-run-snapshots',
    kind: 'historical_snapshot',
    tracking: 'tracked',
    pattern: /^freshie\/exports\/run-[1-9]\d*\//,
    canonical: 'freshie/exports/run-N/csv-exports/INDEX.md and its recorded commit',
    regenerate: null,
    why: 'point-in-time discovery evidence; preserve observed values byte-for-byte',
  },
  {
    id: 'epic-9-boundary-evidence',
    kind: 'historical_snapshot',
    tracking: 'tracked',
    pattern: /^000-docs\/810-RA-DATA-epic-9-boundary-evidence\.json$/,
    canonical:
      'the exact-head npm registry, package graph, kernel-shadow, and DR-049 observations recorded for Epic 9 closure',
    regenerate: null,
    why: 'retained point-in-time evidence for the Epic 9 authority boundary and scorecard read-back',
  },
  {
    id: 'frozen-prose-anchor-manifest',
    kind: 'frozen_projection',
    tracking: 'tracked',
    pattern: /^tests\/fixtures\/prose-anchors\/expected-output\.json$/,
    canonical: '000-docs/6767-h-SPEC-DR-STND-claude-code-extensions-master.md',
    regenerate: null,
    why: 'exact expected heading manifest for the byte-frozen 6767-h document',
  },
];

export function artifactRegistration(candidate) {
  const path = String(candidate).replaceAll('\\', '/').replace(/^\.\//, '');
  const matches = GENERATED_ARTIFACT_REGISTRY.filter((entry) => entry.pattern.test(path));
  if (matches.length > 1) {
    throw new Error(
      `generated-artifact registry overlap for ${path}: ${matches.map((entry) => entry.id).join(', ')}`,
    );
  }
  return matches[0] ?? null;
}

export function artifactRegistrationsByTracking(tracking) {
  return GENERATED_ARTIFACT_REGISTRY.filter((entry) => entry.tracking === tracking);
}
