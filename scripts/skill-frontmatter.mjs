import yaml from './vendor/js-yaml-4.1.1/js-yaml.mjs';

const MAX_FRONTMATTER_CHARACTERS = 256 * 1024;
const MAX_FRONTMATTER_DEPTH = 64;
const MAX_FRONTMATTER_NODES = 4096;
const UNSAFE_MAPPING_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

/**
 * Parse bounded, failsafe YAML frontmatter from a complete SKILL.md document.
 */
export function parseSkillFrontmatter(content) {
  if (typeof content !== 'string') {
    throw new TypeError('SKILL frontmatter source must be a string');
  }

  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---(?=\r?\n|$)/);
  if (!match) {
    if (/^---(?:\r?\n|$)/.test(content)) {
      throw new Error('unterminated SKILL YAML frontmatter');
    }
    return null;
  }
  if (match[1].length > MAX_FRONTMATTER_CHARACTERS) {
    throw new RangeError(
      `invalid SKILL YAML frontmatter: exceeds ${MAX_FRONTMATTER_CHARACTERS} characters`,
    );
  }

  let parsed;
  let depth = 0;
  let nodeCount = 0;
  try {
    parsed = yaml.load(match[1], {
      schema: yaml.FAILSAFE_SCHEMA,
      json: false,
      onWarning(warning) {
        throw warning;
      },
      listener(event, state) {
        if (event === 'open') {
          depth += 1;
          nodeCount += 1;
          if (depth > MAX_FRONTMATTER_DEPTH) {
            throw new RangeError(`YAML nesting exceeds ${MAX_FRONTMATTER_DEPTH} levels`);
          }
          if (nodeCount > MAX_FRONTMATTER_NODES) {
            throw new RangeError(`YAML document exceeds ${MAX_FRONTMATTER_NODES} nodes`);
          }
          return;
        }

        if (state.anchor !== null) {
          throw new TypeError('YAML anchors and aliases are not supported');
        }
        depth -= 1;
      },
    });
  } catch (error) {
    throw new Error(`invalid SKILL YAML frontmatter: ${error.message}`, { cause: error });
  }

  if (!isPlainMapping(parsed)) {
    throw new TypeError('invalid SKILL YAML frontmatter: root must be a mapping');
  }

  return copySafeYamlValue(parsed, '$frontmatter');
}

function isPlainMapping(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function copySafeYamlValue(value, path, ancestors = new Set()) {
  if (value === null || typeof value === 'string') return value;

  if (Array.isArray(value)) {
    if (ancestors.has(value)) {
      throw new TypeError(`invalid SKILL YAML frontmatter: cyclic alias at ${path}`);
    }
    ancestors.add(value);
    const result = value.map((item, index) =>
      copySafeYamlValue(item, `${path}[${index}]`, ancestors),
    );
    ancestors.delete(value);
    return result;
  }

  if (!isPlainMapping(value)) {
    throw new TypeError(`invalid SKILL YAML frontmatter: unsupported value at ${path}`);
  }
  if (ancestors.has(value)) {
    throw new TypeError(`invalid SKILL YAML frontmatter: cyclic alias at ${path}`);
  }

  ancestors.add(value);
  const result = {};
  for (const [key, child] of Object.entries(value)) {
    if (UNSAFE_MAPPING_KEYS.has(key)) {
      throw new TypeError(
        `invalid SKILL YAML frontmatter: unsafe mapping key ${JSON.stringify(key)}`,
      );
    }
    result[key] = copySafeYamlValue(child, `${path}.${key}`, ancestors);
  }
  ancestors.delete(value);
  return result;
}
