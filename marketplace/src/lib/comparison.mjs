// Comparison references are local UI identifiers, never install names.
export function comparisonKey(item) {
  if (!item || !['plugin', 'skill'].includes(item.type)) return null;
  const id = item.id || item.name;
  return typeof id === 'string' && id ? `${item.type}:${encodeURIComponent(id)}` : null;
}

export function buildComparisonLookup(rows) {
  const items = Object.create(null);
  const legacy = new Map();
  for (const item of rows) {
    const key = comparisonKey(item);
    if (!key) continue;
    if (Object.hasOwn(items, key)) throw new Error(`Duplicate comparison reference: ${key}`);
    items[key] = item;
    const id = item.id || item.name;
    legacy.set(id, [...(legacy.get(id) || []), key]);
  }
  const ambiguous = [];
  for (const [id, keys] of legacy) {
    // Legacy aliases point to the typed key, avoiding a second copy of each body.
    if (keys.length === 1 && !Object.hasOwn(items, id)) items[id] = keys[0];
    else ambiguous.push(id);
  }
  return { items, ambiguous };
}

export function savedComparisonReferences(saved) {
  if (!Array.isArray(saved)) return [];
  return saved.map(comparisonKey).filter(Boolean).slice(0, 4);
}

export function resolveComparison(references, lookup) {
  const items = [];
  const rejected = [];
  const seen = new Set();
  for (const reference of references.slice(0, 4)) {
    const value = Object.hasOwn(lookup.items, reference) ? lookup.items[reference] : null;
    const item =
      typeof value === 'string' && Object.hasOwn(lookup.items, value) ? lookup.items[value] : value;
    if (!item) {
      rejected.push({
        reference,
        reason: lookup.ambiguous.includes(reference) ? 'ambiguous' : 'unknown',
      });
      continue;
    }
    const key = comparisonKey(item);
    if (!seen.has(key)) items.push(item);
    seen.add(key);
  }
  return { items, rejected };
}
