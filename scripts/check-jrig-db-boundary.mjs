#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { resolvePluginProvenance } from './plugin-provenance.mjs';
import { safeReadFile } from './safe-fs.mjs';

const ROOT_FILES = new Set(['AGENTS.md', 'CLAUDE.md', 'README.md', 'STANDARDS.md']);
const ACTIVE_ROOTS = ['.github/', 'plugins/', 'scripts/'];
const ACTIVE_EXTENSIONS = new Set(['.md', '.sh', '.yaml', '.yml']);
const DIRECT_REASON = 'DIRECT_JRIG_FRESHIE_DB';
const DIRECTIVE_REASON = 'JRIG_FRESHIE_DB_DIRECTIVE';
const AMBIGUOUS_STATE = '__JRIG_AMBIGUOUS_SHELL_STATE__';
const LITERAL_DOLLAR = '__JRIG_LITERAL_DOLLAR_7F8C2A__';
const JRIG_EVAL_RE = /\b(?:(?:pnpm\s+(?:exec|dlx)|npx)\s+)?j-rig\s+eval\b/;

function shellLiteralView(text) {
  return text
    .replace(/\\\s*\n\s*/g, '')
    .replace(/\$(['"])/g, '$1')
    .replace(/[`'"]/g, '')
    .replace(/\\([^\n])/g, '$1');
}

function staticShellWords(text) {
  const words = [];
  let word = '';
  let quote = null;
  let active = false;
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quote) {
      if (character === quote) quote = null;
      else if (character === '\\' && quote === '"' && index + 1 < text.length)
        word += text[(index += 1)];
      else word += character;
      active = true;
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      active = true;
      continue;
    }
    if (character === '\\' && index + 1 < text.length) {
      word += text[(index += 1)];
      active = true;
      continue;
    }
    if (/\s/.test(character)) {
      if (active) words.push(word);
      word = '';
      active = false;
      continue;
    }
    if (/[`$;&|<>]/.test(character)) return null;
    word += character;
    active = true;
  }
  if (quote) return null;
  if (active) words.push(word);
  return words;
}

function evaluateStaticPrintf(body) {
  const words = staticShellWords(body);
  if (!words || words.shift() !== 'printf') return null;
  if (words[0] === '--') words.shift();
  const format = words.shift();
  if (format === undefined) return null;
  let argument = 0;
  let output = '';
  for (let index = 0; index < format.length; index += 1) {
    if (format[index] !== '%') {
      output += format[index];
      continue;
    }
    const directive = format[(index += 1)];
    if (directive === '%') output += '%';
    else if (directive === 's') output += words[argument++] ?? '';
    else return null;
  }
  return argument === words.length ? output : null;
}

function hasActiveShellExpansion(value) {
  let quote = null;
  for (let index = 0; index < value.length; index += 1) {
    const character = value[index];
    if (character === '\\' && quote !== "'") {
      index += 1;
      continue;
    }
    if (quote) {
      if (character === quote) quote = null;
      else if (quote !== "'" && character === '$' && /[({A-Za-z_]/.test(value[index + 1] ?? ''))
        return true;
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      continue;
    }
    if (character === '$' && /[({A-Za-z_]/.test(value[index + 1] ?? '')) return true;
  }
  return false;
}

function resolveStaticCommandSubstitutions(value) {
  return value.replace(/\$\(([^()]*)\)/g, (token, body) => evaluateStaticPrintf(body) ?? token);
}

function maskLiteralShellDollars(value) {
  let output = '';
  let quote = null;
  for (let index = 0; index < value.length; index += 1) {
    const character = value[index];
    if (character === '\\' && quote !== "'" && index + 1 < value.length) {
      const next = value[(index += 1)];
      output += next === '$' ? LITERAL_DOLLAR : `\\${next}`;
      continue;
    }
    if (quote) {
      if (character === quote) quote = null;
      output += quote === "'" && character === '$' ? LITERAL_DOLLAR : character;
      continue;
    }
    if (character === "'" || character === '"') quote = character;
    output += character;
  }
  return output;
}

function functionAliases(text) {
  const aliases = new Set();
  const functions =
    /(?:^|[;\n])\s*(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\s*\))?\s*\{([\s\S]*?)\}/g;
  for (const match of text.matchAll(functions)) {
    if (/\bj-rig\b/.test(shellLiteralView(match[2]))) aliases.add(match[1]);
  }
  const shellAliases = /(?:^|[;\n])\s*alias\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\n;]+)/g;
  for (const match of text.matchAll(shellAliases)) {
    if (/\bj-rig\b/.test(shellLiteralView(match[2]))) aliases.add(match[1]);
  }
  return aliases;
}

function containsJrigEval(text, aliases = new Set()) {
  const literal = shellLiteralView(text);
  if (JRIG_EVAL_RE.test(literal)) return true;
  if (/\bj-rig\b[\s)]*eval\b/.test(literal)) return true;
  if (/\bj-rig\b/.test(literal) && /\$\([^)]*\beval\b[^)]*\)/.test(literal)) return true;
  for (const alias of aliases) {
    const escaped = alias.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&');
    if (new RegExp(`\\b${escaped}\\s+eval\\b`).test(literal)) return true;
  }
  return false;
}

function isFlowIdentifierStart(character) {
  return (
    (character >= 'A' && character <= 'Z') ||
    (character >= 'a' && character <= 'z') ||
    character === '_'
  );
}

function isFlowIdentifierPart(character) {
  return isFlowIdentifierStart(character) || (character >= '0' && character <= '9');
}

function isFlowQuote(character) {
  return character === '`' || character === "'" || character === '"';
}

function skipFlowWhitespace(value, cursor) {
  while (cursor < value.length && /\s/.test(value[cursor])) cursor += 1;
  return cursor;
}

function scanFlowEnvEntries(value, offset) {
  const entries = [];
  let cursor = 0;
  let malformed = false;

  // Every branch advances cursor; even an unterminated quoted value is scanned once.
  while (cursor < value.length) {
    cursor = skipFlowWhitespace(value, cursor);
    if (value[cursor] === ',') {
      cursor += 1;
      continue;
    }
    if (cursor >= value.length || value[cursor] === '}') break;

    const entryStart = cursor;
    const keyQuote = isFlowQuote(value[cursor]) ? value[cursor++] : null;
    const nameStart = cursor;
    if (!isFlowIdentifierStart(value[cursor])) {
      malformed = true;
      while (cursor < value.length && value[cursor] !== ',') cursor += 1;
      continue;
    }
    cursor += 1;
    while (cursor < value.length && isFlowIdentifierPart(value[cursor])) cursor += 1;
    const name = value.slice(nameStart, cursor);
    if (keyQuote) {
      if (value[cursor] !== keyQuote) {
        malformed = true;
        while (cursor < value.length && value[cursor] !== ',') cursor += 1;
        continue;
      }
      cursor += 1;
    } else if (isFlowQuote(value[cursor])) {
      malformed = true;
      while (cursor < value.length && value[cursor] !== ',') cursor += 1;
      continue;
    }

    cursor = skipFlowWhitespace(value, cursor);
    if (value[cursor] !== ':') {
      malformed = true;
      while (cursor < value.length && value[cursor] !== ',') cursor += 1;
      continue;
    }
    cursor = skipFlowWhitespace(value, cursor + 1);
    const valueStart = cursor;
    let valueEnd;

    if (value[cursor] === '"' || value[cursor] === "'") {
      const quote = value[cursor];
      let fallbackEnd = null;
      let closed = false;
      cursor += 1;
      while (cursor < value.length) {
        const character = value[cursor];
        if (fallbackEnd === null && (character === ',' || character === '}')) {
          fallbackEnd = cursor;
        }
        if (character === '\\') {
          cursor += Math.min(2, value.length - cursor);
          continue;
        }
        cursor += 1;
        if (character === quote) {
          closed = true;
          break;
        }
      }
      valueEnd = closed ? cursor : (fallbackEnd ?? cursor);
      if (!closed) malformed = true;
    } else {
      while (cursor < value.length && value[cursor] !== ',' && value[cursor] !== '}') cursor += 1;
      valueEnd = cursor;
    }

    entries.push({
      index: offset + entryStart,
      name,
      value: value.slice(valueStart, valueEnd).trim(),
    });

    cursor = skipFlowWhitespace(value, cursor);
    if (cursor < value.length && value[cursor] !== ',' && value[cursor] !== '}') {
      malformed = true;
      while (cursor < value.length && value[cursor] !== ',') cursor += 1;
    }
  }

  return { entries, malformed };
}

function flowEnvMappings(text) {
  const mappings = [];
  const prefix = /^[ \t]*env[ \t]*:[ \t]*\{/gm;
  let match;

  while ((match = prefix.exec(text)) !== null) {
    const openBrace = match.index + match[0].lastIndexOf('{');
    let cursor = openBrace + 1;
    let depth = 1;
    let quote = null;

    while (cursor < text.length && depth > 0) {
      const character = text[cursor];
      if (quote) {
        if (character === '\\' && quote !== "'") {
          cursor += Math.min(2, text.length - cursor);
          continue;
        }
        if (character === quote) {
          if (quote === "'" && text[cursor + 1] === "'") {
            cursor += 2;
            continue;
          }
          quote = null;
        }
        cursor += 1;
        continue;
      }
      if (isFlowQuote(character)) quote = character;
      else if (character === '{') depth += 1;
      else if (character === '}') depth -= 1;
      cursor += 1;
    }

    const closed = depth === 0;
    const contentEnd = closed ? cursor - 1 : cursor;
    mappings.push({
      content: text.slice(openBrace + 1, contentEnd),
      contentOffset: openBrace + 1,
      index: match.index,
      closed,
    });
    if (!closed) break;
    prefix.lastIndex = cursor;
  }

  return mappings;
}

function malformedFlowEnvOffset(text) {
  for (const flow of flowEnvMappings(text)) {
    if (!flow.closed || scanFlowEnvEntries(flow.content, flow.contentOffset).malformed) {
      return flow.index;
    }
  }
  return -1;
}

function collectAssignments(text) {
  const events = [];
  const record = (index, name, rawValue) => {
    events.push({ index, name, value: rawValue.trim() });
  };

  // Match every assignment token, not only the first token in declarations
  // such as `local -r SAFE=x DB=...`.
  const assignment = /(?:^|[;\n]|\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\$\([^)]*\)|[^\s;\n]*)/g;
  for (const match of text.matchAll(assignment)) {
    record(match.index, match[1], match[2]);
  }
  const unset = /(?:^|[;\n])\s*unset\s+([A-Za-z_][A-Za-z0-9_]*)\b/g;
  for (const match of text.matchAll(unset)) {
    events.push({ index: match.index, name: match[1], unset: true });
  }

  const anchors = new Map();
  const yamlAnchor = /^\s*[^#\n:]+:\s*&([A-Za-z_][A-Za-z0-9_]*)\s+([^#\n]+?)\s*$/gm;
  for (const match of text.matchAll(yamlAnchor)) {
    anchors.set(match[1], shellLiteralView(match[2].trim()));
  }

  const yamlScalar = /^\s+[`'"]?([A-Za-z_][A-Za-z0-9_]*)[`'"]?\s*:\s*([`'"]?[^#\n]+?[`'"]?)\s*$/gm;
  for (const match of text.matchAll(yamlScalar)) {
    const rawValue = match[2].trim();
    const alias = /^\*([A-Za-z_][A-Za-z0-9_]*)$/.exec(rawValue);
    record(
      match.index,
      match[1],
      alias && anchors.has(alias[1]) ? anchors.get(alias[1]) : rawValue,
    );
  }
  for (const flow of flowEnvMappings(text)) {
    for (const entry of scanFlowEnvEntries(flow.content, flow.contentOffset).entries) {
      record(entry.index, entry.name, entry.value);
    }
  }

  const assignments = new Map();
  for (const event of events.sort((left, right) => left.index - right.index)) {
    if (event.unset) assignments.delete(event.name);
    else assignments.set(event.name, event.value);
  }
  return assignments;
}

function expandKnownVariables(value, assignments, stack = new Set()) {
  const resolve = (name, nextStack = stack) => {
    if (nextStack.has(name) || !assignments.has(name)) return null;
    const nestedStack = new Set(nextStack).add(name);
    return expandKnownVariables(assignments.get(name), assignments, nestedStack);
  };

  const staticCommands = resolveStaticCommandSubstitutions(maskLiteralShellDollars(value));
  const githubEnv = staticCommands.replace(
    /\$\{\{\s*env\.([A-Za-z_][A-Za-z0-9_]*)\s*\}\}/g,
    (token, name) => resolve(name) ?? token,
  );
  const variable =
    /\$\{!([A-Za-z_][A-Za-z0-9_]*)\}|\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:-|:=|:\+|:|-|=|\+)([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)/g;
  return githubEnv.replace(
    variable,
    (token, indirectName, bracedName, operator, operand, bareName) => {
      if (indirectName) {
        const pointer = resolve(indirectName);
        return pointer === null ? token : (resolve(shellLiteralView(pointer)) ?? token);
      }

      const name = bracedName ?? bareName;
      const resolved = resolve(name);
      if (operator === ':-' || operator === ':=') {
        return resolved ? resolved : expandKnownVariables(operand, assignments, stack);
      }
      if (operator === '-' || operator === '=') {
        return resolved !== null ? resolved : expandKnownVariables(operand, assignments, stack);
      }
      if (operator === ':+') {
        return resolved ? expandKnownVariables(operand, assignments, stack) : '';
      }
      if (operator === '+') {
        return resolved !== null ? expandKnownVariables(operand, assignments, stack) : '';
      }
      if (operator === ':') {
        if (resolved === null || !/^-?\d+$/.test(operand)) return token;
        return resolved.slice(Number.parseInt(operand, 10));
      }
      return resolved ?? token;
    },
  );
}

function applyParameterSideEffects(assignments, text) {
  const next = new Map(assignments);
  const sideEffect = /\$\{([A-Za-z_][A-Za-z0-9_]*)(:=|=)([^}]*)\}/g;
  for (const match of text.matchAll(sideEffect)) {
    const current = next.has(match[1])
      ? shellLiteralView(expandKnownVariables(next.get(match[1]), next))
      : '';
    const unset = !next.has(match[1]);
    if (unset || (match[2] === ':=' && !current)) next.set(match[1], match[3]);
  }
  return next;
}

function shellWordPattern(value) {
  let literal = '';
  let regex = '^';
  let quote = null;
  let activeGlob = false;
  const appendLiteral = (character) => {
    literal += character;
    regex += character.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&');
  };

  for (let index = 0; index < value.length; index += 1) {
    const character = value[index];
    if (character === '\\' && quote !== "'") {
      if (index + 1 < value.length) appendLiteral(value[(index += 1)]);
      continue;
    }
    if (quote) {
      if (character === quote) quote = null;
      else appendLiteral(character);
      continue;
    }
    if (character === '$' && (value[index + 1] === "'" || value[index + 1] === '"')) {
      quote = value[(index += 1)];
      continue;
    }
    if (character === "'" || character === '"') {
      quote = character;
      continue;
    }
    if (character === '*' || character === '?') {
      activeGlob = true;
      literal += character;
      regex += character === '*' ? '.*' : '.';
      continue;
    }
    if (character === '[') {
      const closing = value.indexOf(']', index + 1);
      if (closing > index + 1) {
        const body = value.slice(index + 1, closing).replace(/\\/g, '\\\\');
        activeGlob = true;
        literal += value.slice(index, closing + 1);
        regex += `[${body}]`;
        index = closing;
        continue;
      }
    }
    appendLiteral(character);
  }
  return { literal, regex: `${regex}$`, activeGlob };
}

function isFreshieInventoryPath(value) {
  const cleaned = value.replace(/[),.;`]+$/, '');
  const candidates = [cleaned];
  for (let round = 0; round < 4; round += 1) {
    const next = [];
    for (const candidate of candidates) {
      const brace = /\{([^{}]+)\}/.exec(candidate);
      if (!brace) continue;
      for (const option of brace[1].split(',')) {
        next.push(
          `${candidate.slice(0, brace.index)}${option}${candidate.slice(brace.index + brace[0].length)}`,
        );
      }
    }
    if (next.length === 0 || candidates.length + next.length > 64) break;
    candidates.push(...next);
  }
  for (const candidate of candidates) {
    const fullPattern = shellWordPattern(candidate);
    const fullNormalized = path.posix.normalize(fullPattern.literal);
    if (
      fullNormalized === 'freshie/inventory.sqlite' ||
      fullNormalized.endsWith('/freshie/inventory.sqlite')
    ) {
      return true;
    }
    const suffix = candidate.split('/').slice(-2).join('/');
    const pattern = shellWordPattern(suffix);
    if (pattern.activeGlob && new RegExp(pattern.regex).test('freshie/inventory.sqlite'))
      return true;
  }
  return false;
}

function commandTargetsFreshie(command, assignments, aliases = new Set()) {
  const dbArgument = /(?:^|\s)--db(?:\s*=\s*|\s+)([^\s;&|]+)/g;
  const expanded = expandKnownVariables(command, assignments)
    .replace(/\\\s*\n\s*/g, '')
    .replace(/\\([A-Za-z-])/g, '$1')
    .replace(/(["'])--db\1/g, '--db')
    .replace(/(["'])--db/g, '--db');
  const literal = shellLiteralView(expanded);
  const executable = literal
    .trim()
    .replace(/^(?:[A-Za-z_][A-Za-z0-9_]*=[^\s]+\s+)*/, '')
    .replace(/^command\s+/, '');
  if (/^(?:echo|printf)\b/.test(executable)) return false;
  const invokesJrig =
    /\bj-rig\b/.test(literal) ||
    [...aliases].some((alias) => new RegExp(`\\b${alias}\\b`).test(literal));
  if (!invokesJrig) return false;
  if (assignments.has(AMBIGUOUS_STATE) && /--db\b/.test(literal)) return true;
  for (const match of expanded.matchAll(dbArgument)) {
    // A non-static variable or command substitution can resolve to the tracked
    // database at runtime. Direct JRig guidance must prove the DB argument is
    // scratch-safe; literal single-quoted or escaped dollar text is harmless.
    if (hasActiveShellExpansion(match[1])) return true;
    if (isFreshieInventoryPath(match[1])) return true;
  }
  if (invokesJrig && /\beval\b/.test(literal) && /--db\b/.test(literal)) {
    if (/\$\([^)]*\bfreshie\/[^)]*\binventory\.sqlite\b[^)]*\)/.test(expanded)) return true;
    const candidates = expanded.match(/[^\s;&|]+/g) ?? [];
    if (
      candidates.some(
        (candidate) =>
          isFreshieInventoryPath(candidate) ||
          (/\$\(/.test(expanded) && isFreshieInventoryPath(candidate.replace(/[)"']+$/, ''))),
      )
    )
      return true;
  }
  return false;
}

function lineNumber(text, offset) {
  return text.slice(0, offset).split('\n').length;
}

function splitShellStatements(text) {
  const statements = [];
  let start = 0;
  let quote = null;
  let depth = 0;
  let pendingOperator = null;
  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (!quote && text.startsWith('```', index)) {
      index += 2;
      continue;
    }
    if (character === '\\' && quote !== "'") {
      index += 1;
      continue;
    }
    if (quote) {
      if (character === quote) quote = null;
      continue;
    }
    // A possessive apostrophe in Markdown prose (for example, "platform's")
    // is not a shell quote and must not absorb later, unrelated lines.
    if (
      character === '"' ||
      character === '`' ||
      (character === "'" && (index === 0 || !/[A-Za-z0-9_]/.test(text[index - 1])))
    ) {
      quote = character;
      continue;
    }
    if (character === '(') {
      depth += 1;
      continue;
    }
    if (character === ')' && depth > 0) {
      depth -= 1;
      continue;
    }
    if (depth > 0) continue;
    const operatorLength =
      character === ';' || character === '\n'
        ? 1
        : (character === '&' && text[index + 1] === '&') ||
            (character === '|' && text[index + 1] === '|')
          ? 2
          : character === '&' || character === '|'
            ? 1
            : 0;
    if (operatorLength > 0) {
      const statement = text.slice(start, index).trim();
      const operator = text.slice(index, index + operatorLength);
      if (statement)
        statements.push({
          text: statement,
          offset: start,
          operatorBefore: pendingOperator,
          operatorAfter: operator,
        });
      pendingOperator = operator;
      index += operatorLength - 1;
      start = index + 1;
      continue;
    }
    if (character === '#' && (index === 0 || /\s/.test(text[index - 1]))) {
      const statement = text.slice(start, index).trim();
      if (statement) {
        statements.push({
          text: statement,
          offset: start,
          operatorBefore: pendingOperator,
          operatorAfter: '\n',
        });
      }
      const newline = text.indexOf('\n', index);
      if (newline < 0) return statements;
      pendingOperator = '\n';
      start = newline + 1;
      index = newline;
      continue;
    }
  }
  const statement = text.slice(start).trim();
  if (statement)
    statements.push({
      text: statement,
      offset: start,
      operatorBefore: pendingOperator,
      operatorAfter: null,
    });
  return statements;
}

function assignmentOnly(text) {
  const stripped = text
    .replace(/^\s*(?:(?:export|readonly|local|declare|typeset)\s+(?:-[A-Za-z]+\s+)*)?/, '')
    .replace(/(?:^|\s)[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\$\([^)]*\)|[^\s;]*)/g, '')
    .trim();
  return stripped === '';
}

function mapKey(value) {
  return JSON.stringify([...value.entries()].sort(([left], [right]) => left.localeCompare(right)));
}

function uniqueStates(states) {
  const unique = new Map();
  for (const state of states) unique.set(mapKey(state), state);
  if (unique.size <= 64) return [...unique.values()];
  const refused = new Map(unique.values().next().value);
  refused.set(AMBIGUOUS_STATE, 'true');
  return [refused];
}

function staticStatus(text) {
  const literal = shellLiteralView(text).trim();
  if (literal === 'true' || literal === ':') return true;
  if (literal === 'false') return false;
  if (assignmentOnly(text)) return true;
  return null;
}

function commandBlocks(text, initialAssignments = new Map(), baseOffset = 0) {
  const blocks = [];
  const aliases = functionAliases(text);
  let states = [new Map(initialAssignments)];
  let priorStatus = null;
  for (const statement of splitShellStatements(text)) {
    const trimmed = statement.text
      .replace(/^\s*\{\s*/, '')
      .replace(/(^|[;\s])\}\s*$/, '$1')
      .trim();
    if (!trimmed) continue;
    const subshell = /^\(([\s\S]*)\)$/.exec(trimmed);
    if (subshell) {
      for (const state of states) {
        blocks.push(
          ...commandBlocks(
            subshell[1],
            state,
            baseOffset + statement.offset + trimmed.indexOf('(') + 1,
          ),
        );
      }
      priorStatus = null;
      continue;
    }

    const condition = statement.operatorBefore;
    const executes =
      condition === '&&' ? priorStatus !== false : condition === '||' ? priorStatus !== true : true;
    const optional = (condition === '&&' || condition === '||') && priorStatus === null;
    const statementAssignments = collectAssignments(trimmed);
    const appliedStates = states.map((state) =>
      applyParameterSideEffects(mergeAssignments(state, statementAssignments), trimmed),
    );
    const expandedCommands = appliedStates.map((state) => expandKnownVariables(trimmed, state));
    if (
      executes &&
      (expandedCommands.some((expanded) => containsJrigEval(expanded, aliases)) ||
        (containsJrigEval(trimmed, aliases) && appliedStates.length > 0))
    ) {
      for (const assignments of appliedStates) {
        blocks.push({
          text: trimmed,
          offset: baseOffset + statement.offset,
          assignments,
          aliases,
        });
      }
    }

    const isolated =
      statement.operatorBefore === '|' ||
      statement.operatorAfter === '|' ||
      statement.operatorAfter === '&';
    const hasParameterSideEffect = /\$\{[A-Za-z_][A-Za-z0-9_]*:?=/.test(trimmed);
    const controlFlowAssignment =
      statementAssignments.size > 0 &&
      /^\s*(?:if|then|elif|else|while|until|for|case|select|do)\b/.test(trimmed);
    if (
      executes &&
      (assignmentOnly(trimmed) || hasParameterSideEffect || controlFlowAssignment) &&
      !isolated
    ) {
      states =
        optional || controlFlowAssignment
          ? uniqueStates([...states, ...appliedStates])
          : uniqueStates(appliedStates);
    }
    if (executes) priorStatus = optional ? null : staticStatus(trimmed);
  }
  return blocks;
}

function mergeAssignments(...maps) {
  const merged = new Map();
  for (const assignments of maps) {
    for (const [name, value] of assignments) merged.set(name, value);
  }
  return merged;
}

function structuredYamlBlocks(text, filePath) {
  const blocks = [];
  const sources = [];
  const yamlLike =
    /\.ya?ml$/i.test(filePath) ||
    /^\s*(?:[`'"]?(?:run|r\\u0075n)[`'"]?|env|jobs|steps)\s*:/im.test(text);
  if (yamlLike) sources.push({ text, offset: 0, wholeDocument: true });
  for (const fence of text.matchAll(/```ya?ml\s*\n([\s\S]*?)```/gi)) {
    sources.push({ text: fence[1], offset: fence.index, wholeDocument: false });
  }

  let wholeDocument = false;
  for (const source of sources) {
    try {
      yaml.loadAll(source.text, (document) => {
        if (!document || typeof document !== 'object') return;
        if (source.wholeDocument) wholeDocument = true;
        const visited = new WeakSet();
        const visit = (value, inheritedEnv = new Map()) => {
          if (!value || typeof value !== 'object' || visited.has(value)) return;
          visited.add(value);
          const localEnv = new Map(inheritedEnv);
          if (!Array.isArray(value) && value.env && typeof value.env === 'object') {
            for (const [name, envValue] of Object.entries(value.env)) {
              if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && typeof envValue === 'string') {
                localEnv.set(name, envValue);
              }
            }
          }

          for (const [key, child] of Object.entries(value)) {
            if (key === 'run' && typeof child === 'string') {
              for (const command of commandBlocks(child, localEnv)) {
                const needle = /j-rig|\$[A-Za-z_]/.exec(command.text)?.[0];
                const relative = needle ? source.text.indexOf(needle) : 0;
                blocks.push({
                  ...command,
                  offset: source.offset + Math.max(relative, 0),
                });
              }
            } else if (key !== 'env') {
              visit(child, localEnv);
            }
          }
        };
        visit(document);
      });
    } catch {
      if (source.wholeDocument) wholeDocument = false;
      const malformedFlowOffset = malformedFlowEnvOffset(source.text);
      if (
        malformedFlowOffset >= 0 &&
        containsJrigEval(source.text) &&
        /--db\b/.test(shellLiteralView(source.text))
      ) {
        blocks.push({
          text: source.text,
          offset: source.offset + malformedFlowOffset,
          assignments: new Map([[AMBIGUOUS_STATE, 'true']]),
        });
      }
    }
  }
  return { blocks, wholeDocument };
}

// YAML folds `run: >` lines into one shell command. A line-oriented scan would
// otherwise miss a forbidden --db flag placed on the next indented line.
function foldedRunBlocks(text) {
  const lines = text.split('\n');
  const blocks = [];
  let offset = 0;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const match =
      /^(\s*)(?:-\s*)?[`'"]?run[`'"]?\s*:\s*(?:&[A-Za-z_][A-Za-z0-9_]*\s+)?>(?:[1-9][+-]?|[+-][1-9]?)?\s*(?:#.*)?$/.exec(
        line,
      );
    if (!match) {
      offset += line.length + 1;
      continue;
    }

    const parentIndent = match[1].length;
    const content = [];
    let firstOffset = null;
    let cursor = index + 1;
    let cursorOffset = offset + line.length + 1;
    while (cursor < lines.length) {
      const candidate = lines[cursor];
      if (candidate.trim() === '') {
        content.push('');
      } else {
        const indent = candidate.match(/^\s*/)[0].length;
        if (indent <= parentIndent) break;
        if (firstOffset === null) firstOffset = cursorOffset;
        content.push(candidate.trim());
      }
      cursorOffset += candidate.length + 1;
      cursor += 1;
    }
    for (const paragraph of content.join('\n').split(/\n\s*\n/)) {
      const folded = paragraph.replace(/\n/g, ' ').trim();
      if (!folded || firstOffset === null) continue;
      const assignments = collectAssignments(`${text.slice(0, firstOffset)}\n${folded}`);
      if (containsJrigEval(expandKnownVariables(folded, assignments))) {
        blocks.push({ text: folded, offset: firstOffset, assignments });
      }
    }
    offset += line.length + 1;
  }
  return blocks;
}

export function inspectJrigDbBoundary(text, filePath) {
  const findings = [];
  const seen = new Set();
  const structured = structuredYamlBlocks(text, filePath);
  const commands = structured.wholeDocument
    ? structured.blocks
    : [...commandBlocks(text), ...foldedRunBlocks(text), ...structured.blocks];
  const commandLines = new Set(commands.map((command) => lineNumber(text, command.offset)));
  for (const command of commands) {
    if (commandTargetsFreshie(command.text, command.assignments, command.aliases)) {
      const finding = {
        path: filePath,
        line: lineNumber(text, command.offset),
        reasonCode: DIRECT_REASON,
      };
      const key = `${finding.line}:${finding.reasonCode}`;
      if (!seen.has(key)) findings.push(finding);
      seen.add(key);
    }
  }

  const directLines = new Set(findings.map((finding) => finding.line));
  const prose = text
    .replace(/[`"]+/g, '')
    .replace(/\\([^\n])/g, '$1')
    .replace(/\/{2,}/g, '/')
    .replace(/\/\.\//g, '/');
  const directive =
    /^(?=[^\n]*--db\b)(?=[^\n]*\bfreshie(?:'s)?\b[^\n]{0,80}?inventory\.sqlite\b)[^\n]+$/gim;
  for (const match of prose.matchAll(directive)) {
    const directiveLine = lineNumber(prose, match.index);
    if (commandLines.has(directiveLine)) continue;
    if (directLines.has(directiveLine)) continue;
    const residue = match[0]
      .replace(/--db\b/gi, '')
      .replace(/\S*\bfreshie(?:'s)?\b[^\n]{0,80}?inventory\.sqlite\b\S*/gi, '');
    if (!/[A-Za-z]{3}/.test(residue)) continue;
    if (/^\s*(?:echo|printf)\b/i.test(match[0])) continue;
    // Shell-shaped lines are governed by the execution-aware command scan.
    // Do not reclassify a statically unreachable command as prose.
    if (containsJrigEval(match[0])) continue;
    const directiveVerb =
      /(?:^|[,;:]\s*|\b(?:should|must|can)\s+)(?:to\s+)?(?:choose|configure|direct|feed|pass|persist|point|provide|route|select|send|set|supply|target|use|write)\b/i;
    if (!directiveVerb.test(match[0])) continue;
    const finding = {
      path: filePath,
      line: directiveLine,
      reasonCode: DIRECTIVE_REASON,
    };
    const key = `${finding.line}:${finding.reasonCode}`;
    if (!seen.has(key)) findings.push(finding);
    seen.add(key);
  }
  return findings;
}

function isActiveSurface(filePath) {
  if (ROOT_FILES.has(filePath)) return true;
  if (!ACTIVE_ROOTS.some((root) => filePath.startsWith(root))) return false;
  return ACTIVE_EXTENSIONS.has(path.extname(filePath));
}

export function auditJrigDbBoundary({
  root = process.cwd(),
  paths,
  // Default read is the verified safe-fs read (no follow, regular file, same
  // inode before and after open), so the lstat below is no longer a
  // check-then-read gap. Tests inject both functions for fault cases.
  readFile = (absolute) =>
    safeReadFile(path.resolve(root), path.relative(root, absolute)).content.toString('utf8'),
  lstat = fs.lstatSync,
  provenance = resolvePluginProvenance,
} = {}) {
  const findings = [];
  let scanned = 0;
  let mirrorsSkipped = 0;

  for (const filePath of [...paths].filter(isActiveSurface).sort()) {
    const absolute = path.join(root, filePath);
    let metadata;
    try {
      metadata = lstat(absolute);
    } catch (error) {
      findings.push({
        path: filePath,
        line: 0,
        reasonCode: 'UNREADABLE_ACTIVE_SURFACE',
        detail: error instanceof Error ? error.message : String(error),
      });
      continue;
    }
    if (!metadata.isFile() || metadata.isSymbolicLink()) {
      findings.push({ path: filePath, line: 0, reasonCode: 'NON_REGULAR_ACTIVE_SURFACE' });
      continue;
    }

    if (filePath.startsWith('plugins/')) {
      const result = provenance(path.dirname(filePath), { root });
      if (result.status === 'mirror') {
        mirrorsSkipped += 1;
        continue;
      }
      if (result.status !== 'first-party') {
        findings.push({
          path: filePath,
          line: 0,
          reasonCode: result.reasonCode ?? 'UNRESOLVED_PROVENANCE',
        });
        continue;
      }
    }

    let text;
    try {
      text = readFile(absolute, 'utf8');
    } catch (error) {
      findings.push({
        path: filePath,
        line: 0,
        reasonCode: 'UNREADABLE_ACTIVE_SURFACE',
        detail: error instanceof Error ? error.message : String(error),
      });
      continue;
    }
    scanned += 1;
    findings.push(...inspectJrigDbBoundary(text, filePath));
  }

  return { findings, scanned, mirrorsSkipped };
}

function trackedPaths(root) {
  const output = execFileSync(
    'git',
    [
      'ls-files',
      '-z',
      '--',
      'AGENTS.md',
      'CLAUDE.md',
      'README.md',
      'STANDARDS.md',
      '.github',
      'plugins',
      'scripts',
    ],
    { cwd: root, maxBuffer: 32 * 1024 * 1024 },
  );
  return output.toString('utf8').split('\0').filter(Boolean);
}

export function main(root = process.cwd()) {
  let paths;
  try {
    paths = trackedPaths(root);
  } catch (error) {
    console.error(`jrig-db-boundary: REFUSED (Git inventory unavailable: ${error.message})`);
    return 1;
  }
  const report = auditJrigDbBoundary({ root, paths });
  if (report.findings.length > 0) {
    for (const finding of report.findings.slice(0, 50)) {
      const location = finding.line > 0 ? `${finding.path}:${finding.line}` : finding.path;
      console.error(
        `${location}: ${finding.reasonCode}${finding.detail ? ` (${finding.detail})` : ''}`,
      );
    }
    console.error(
      `jrig-db-boundary: REFUSED (${report.findings.length} finding(s); use scripts/run-jrig-eval.sh so j-rig receives only a scratch DB)`,
    );
    return 1;
  }
  console.log(
    `jrig-db-boundary: OK (${report.scanned} active first-party surfaces; ${report.mirrorsSkipped} mirror surfaces skipped by provenance)`,
  );
  return 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = main();
}
