// Transport the Python validator's advisory registry evidence without promoting
// it to validator authority or conflating it with per-file corpus verdicts.
const object = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const strings = (value) => Array.isArray(value) && value.every((item) => typeof item === 'string');
const result = (status, note = '') => ({ status, note });
const flag = (value) =>
  typeof value === 'boolean'
    ? result(value ? 'match' : 'mismatch')
    : result('invalid', 'comparison flag is missing or is not a boolean');

function setComparison(handFields, kernelFields, reportedMatch, missingFields, extraFields) {
  const arrays = [handFields, kernelFields, missingFields, extraFields];
  if (typeof reportedMatch !== 'boolean' || !arrays.every(strings)) {
    return result('invalid', 'field sets or comparison flag are malformed');
  }
  const [hand, kernel, missing, extra] = arrays.map((items) => new Set(items));
  const expectedMissing = [...kernel].filter((field) => !hand.has(field));
  const expectedExtra = [...hand].filter((field) => !kernel.has(field));
  const consistent = (expected, actual) =>
    expected.length === actual.size && expected.every((field) => actual.has(field));
  if (
    !consistent(expectedMissing, missing) ||
    !consistent(expectedExtra, extra) ||
    reportedMatch !== (expectedMissing.length === 0 && expectedExtra.length === 0)
  ) {
    return result('invalid', 'comparison flag or deltas disagree with its field sets');
  }
  return {
    ...flag(reportedMatch),
    missingFromHandAuthored: [...missing].sort(),
    onlyInHandAuthored: [...extra].sort(),
  };
}

function pluginComparison(plugin) {
  if (!object(plugin))
    return result('invalid', 'plugin_manifest comparison is missing or malformed');
  if (plugin.available === false) {
    return result(
      'unavailable',
      typeof plugin.note === 'string' ? plugin.note : 'schema unavailable',
    );
  }
  if (plugin.available !== true) return result('invalid', 'plugin availability is malformed');
  return setComparison(
    plugin.hand_authored_fields,
    plugin.kernel_fields,
    plugin.fields_match,
    plugin.stale_missing_from_hand_authored,
    plugin.only_in_hand_authored,
  );
}

function toolsComparison(tools) {
  if (
    !object(tools) ||
    ![tools.in_hand_authored_registry, tools.in_kernel_properties, tools.match].every(
      (value) => typeof value === 'boolean',
    )
  ) {
    return result('invalid', 'tool presence or comparison flag is malformed');
  }
  if (tools.match !== (tools.in_hand_authored_registry === tools.in_kernel_properties)) {
    return result('invalid', 'comparison flag disagrees with observed tool presence');
  }
  return flag(tools.match);
}

export function collectRegistryShadow(entries) {
  const blocks = entries
    .filter((entry) => object(entry) && Object.hasOwn(entry, 'kernel_shadow'))
    .map((entry) => entry.kernel_shadow);
  const envelope = { mode: 'shadow-advisory', blocking: false, raw: blocks[0] ?? null };
  if (blocks.length === 0) {
    return { ...envelope, status: 'missing', note: 'validator emitted no kernel_shadow block' };
  }
  if (blocks.length !== 1 || !object(blocks[0])) {
    return {
      ...envelope,
      status: 'invalid',
      note: 'expected exactly one object-valued kernel_shadow block',
      raw: blocks,
    };
  }
  const raw = blocks[0];
  if (raw.available === false) {
    return {
      ...envelope,
      status: 'unavailable',
      note: typeof raw.note === 'string' ? raw.note : 'kernel schemas unavailable',
    };
  }
  if (raw.available !== true || raw.mode !== 'shadow-advisory') {
    return { ...envelope, status: 'invalid', note: 'invalid availability or advisory mode' };
  }
  return {
    ...envelope,
    status: 'reported',
    comparisons: {
      skill_required: setComparison(
        raw.hand_authored_always_required,
        raw.kernel_effective_required,
        raw.required_match,
        raw.required_only_in_kernel,
        raw.required_only_in_hand_authored,
      ),
      disallowed_tools: toolsComparison(raw.disallowed_tools),
      plugin_manifest: pluginComparison(raw.plugin_manifest),
    },
  };
}

const cell = (value) =>
  String(value)
    .replace(/[&<>|`\\]/g, (character) => `&#${character.charCodeAt(0)};`)
    .replace(/[\r\n]/g, ' ');

export function registrySummaryLines(registry) {
  const lines = [
    '### Registry comparisons (advisory; installed kernel only)',
    '',
    'Separate from skill-corpus verdicts. A match does not establish upstream currency or complete registry coverage.',
    '',
    '| comparison | status | details |',
    '| --- | --- | --- |',
  ];
  if (!registry.comparisons) {
    lines.push(`| kernel_shadow | ${registry.status} | ${cell(registry.note)} |`);
  } else {
    for (const [name, comparison] of Object.entries(registry.comparisons)) {
      const details = [comparison.note];
      if (comparison.missingFromHandAuthored?.length) {
        details.push(
          `missing from hand-authored: ${comparison.missingFromHandAuthored.join(', ')}`,
        );
      }
      if (comparison.onlyInHandAuthored?.length) {
        details.push(`only in hand-authored: ${comparison.onlyInHandAuthored.join(', ')}`);
      }
      lines.push(
        `| ${name} | ${comparison.status} | ${cell(details.filter(Boolean).join('; '))} |`,
      );
    }
  }
  return [...lines, ''];
}
