/** Author-facing diagnostics; never changes a validator verdict or gate authority. */
const REPO = 'https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/';
const REQUIRED = new Set([
  'name',
  'description',
  'allowed-tools',
  'version',
  'author',
  'license',
  'compatibility',
  'tags',
]);
export const EXCEPTION_URL = `${REPO}.github/CONTRIBUTING.md#marketplace-acceptance-and-exceptions`;
export const FIX_IT_URL = `${REPO}docs/sak-field-diagnostics.md`;
const CURRENT_URL = `${REPO}000-docs/SCHEMA_CHANGELOG.md#non-negotiables--read-before-touching-this-file`;
const HISTORICAL_URL = `${REPO}000-docs/6767-h-SPEC-DR-STND-claude-code-extensions-master.md#31-yaml-frontmatter-required`;
const DISPOSITION_URL = `${REPO}000-docs/727-AT-ARCH-master-modernization-blueprint.md#section-level-disposition-of-6767-h`;
const escapePointer = (value) => String(value).replaceAll('~', '~0').replaceAll('/', '~1');

export function fieldDiagnostic(error, { lane, file, kernelVersion }) {
  let pointer = error.instancePath || '';
  if (error.keyword === 'required' && typeof error.params?.missingProperty === 'string') {
    pointer += `/${escapePointer(error.params.missingProperty)}`;
  } else if (
    error.keyword === 'additionalProperties' &&
    typeof error.params?.additionalProperty === 'string'
  ) {
    pointer += `/${escapePointer(error.params.additionalProperty)}`;
  }
  const field = pointer.split('/')[1]?.replaceAll('~1', '/').replaceAll('~0', '~') || null;
  const marketplaceRequired = REQUIRED.has(field);
  return {
    file,
    lane,
    kernelVersion,
    field,
    fieldPointer: pointer || '/',
    keyword: error.keyword ?? null,
    schemaPath: error.schemaPath ?? null,
    message: error.message ?? 'Frontmatter could not be validated',
    params: globalThis.structuredClone(error.params ?? {}),
    marketplaceRequired,
    fieldUrl: marketplaceRequired ? `${FIX_IT_URL}#${field}` : null,
    historicalSection: marketplaceRequired ? '6767-h § 3.1 (superseded)' : null,
    historicalUrl: marketplaceRequired ? HISTORICAL_URL : null,
    authorityDispositionUrl: DISPOSITION_URL,
    currentRequiredSetUrl: CURRENT_URL,
    exceptionUrl: EXCEPTION_URL,
    fixItUrl: FIX_IT_URL,
  };
}

// Escape untrusted artifact names/messages before putting them in GitHub Markdown.
const cell = (value) =>
  String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('|', '&#124;')
    .replaceAll('`', '&#96;')
    .replaceAll('[', '&#91;')
    .replaceAll(']', '&#93;')
    .replaceAll('\\', '&#92;')
    // Strip control characters from untrusted artifact text before rendering.
    // eslint-disable-next-line no-control-regex
    .replace(/[\r\n\u0000-\u001f\u007f]/g, ' ');

export function diagnosticSummary(rows, limit = 40) {
  const lines = [
    '### Kernel field diagnostics (advisory)',
    '',
    `Showing ${Math.min(limit, rows.length)} of ${rows.length} findings; all findings are retained in report.json under fieldDiagnostics.`,
    'The kernel remains advisory. Historical 6767-h field rules are superseded; use the linked current requirements and disposition.',
    '',
    '| file / profile | field pointer | finding | guidance |',
    '| --- | --- | --- | --- |',
  ];
  for (const row of rows.slice(0, limit)) {
    const historical = row.historicalUrl
      ? `[6767-h § 3.1 (superseded)](${row.historicalUrl}); `
      : '';
    const field = row.fieldUrl
      ? `[${cell(row.fieldPointer)}](${row.fieldUrl})`
      : cell(row.fieldPointer);
    lines.push(
      `| ${cell(row.file)} / ${cell(row.lane)} | ${field} | ${cell(row.message)} | ${historical}[current required set](${row.currentRequiredSetUrl}); [authority disposition](${row.authorityDispositionUrl}); [fix-it guide](${row.fixItUrl}); [exception request](${row.exceptionUrl}) |`,
    );
  }
  return lines;
}
