'use strict';

const path = require('node:path');

function sourcePublicationDisposition(source, { readEvidence } = {}) {
  const label = source?.name ?? '<unnamed source>';
  const dispositions = [
    ['publication_disposition', source?.publication_disposition],
    ['copyleft_disposition', source?.copyleft_disposition],
  ].filter(([, value]) => value !== undefined);
  if (dispositions.length === 0) return null;
  if (dispositions.length > 1) throw new Error(`${label}: multiple publication dispositions`);
  const [field, value] = dispositions[0];
  if (
    !value ||
    typeof value !== 'object' ||
    Array.isArray(value) ||
    value.status !== 'quarantined' ||
    !Array.isArray(value.channels) ||
    value.channels.length !== 0
  ) {
    throw new Error(
      `${label}: ${field} must be ` + '`status: quarantined` with an empty `channels` list',
    );
  }
  if (typeof value.rationale !== 'string' || value.rationale.trim().length === 0) {
    throw new Error(`${label}: ${field} requires a nonempty rationale`);
  }
  if (
    (field === 'publication_disposition' &&
      (!Array.isArray(value.artifacts) || value.artifacts.length === 0)) ||
    (value.artifacts !== undefined && !Array.isArray(value.artifacts))
  ) {
    throw new Error(`${label}: publication_disposition has no governed artifacts`);
  }
  const artifacts = [];
  const seen = new Set();
  for (const artifact of value.artifacts ?? []) {
    const gate = artifact?.gate === undefined ? 'G0' : artifact.gate;
    if (gate !== 'G0' && gate !== 'G1') {
      throw new Error(`${label}: unknown publication artifact gate ${String(gate)}`);
    }
    const evidence = artifact?.path;
    const target = source?.target_path;
    if (
      typeof evidence !== 'string' ||
      typeof target !== 'string' ||
      !/^plugins\/[^/]+\/[^/]+$/.test(target) ||
      path.posix.normalize(target) !== target ||
      path.posix.normalize(evidence) !== evidence ||
      evidence.includes('\\') ||
      evidence.includes('\0') ||
      !evidence.startsWith(`${target}/`) ||
      evidence.split('/').includes('..')
    ) {
      throw new Error(`${label}: disposition artifact is outside its mirror or unsafe`);
    }
    if (seen.has(evidence)) throw new Error(`${label}: duplicate publication artifact ${evidence}`);
    seen.add(evidence);
    if (
      !Array.isArray(artifact.reason_codes) ||
      artifact.reason_codes.length === 0 ||
      !artifact.reason_codes.every((code) => typeof code === 'string' && code.trim().length > 0)
    ) {
      throw new Error(`${label}: disposition artifact has no reason_codes: ${evidence}`);
    }
    if (readEvidence) readEvidence(evidence);
    artifacts.push({
      path: evidence,
      gate,
      reason_codes: [...new Set(artifact.reason_codes)].sort(),
    });
  }
  const legalArtifacts = artifacts
    .filter((artifact) => artifact.gate === 'G1')
    .map(({ path: evidence, reason_codes }) => ({
      path: evidence,
      reason_codes,
    }));
  if (legalArtifacts.length > 0 && (typeof source.name !== 'string' || !source.name.trim())) {
    throw new Error('A G1 source hold requires a nonempty source name');
  }
  return {
    field,
    rationale: value.rationale,
    artifacts,
    legal_hold:
      legalArtifacts.length === 0
        ? null
        : {
            source: source.name,
            rationale: value.rationale,
            artifacts: legalArtifacts,
          },
  };
}

/**
 * Canonical catalog publication policy.
 *
 * marketplace.extended.json retains quarantined records for attribution and
 * provenance. Every installable/public projection must call this helper and
 * omit them. Unknown states fail closed.
 */
function isPublishedPlugin(plugin, label = 'catalog plugin') {
  if (!plugin || typeof plugin !== 'object' || Array.isArray(plugin)) {
    throw new Error(`${label} must be an object`);
  }
  if (plugin.publication === undefined) return true;
  if (plugin.publication === 'quarantined') return false;
  throw new Error(`${label} has unknown publication state: ${String(plugin.publication)}`);
}

function publishedPlugins(plugins, label = 'catalog') {
  if (!Array.isArray(plugins)) throw new Error(`${label} plugins must be an array`);
  return plugins.filter((plugin, index) => isPublishedPlugin(plugin, `${label} plugin ${index}`));
}

module.exports = {
  isPublishedPlugin,
  publishedPlugins,
  sourcePublicationDisposition,
};
