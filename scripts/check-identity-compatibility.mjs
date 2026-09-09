#!/usr/bin/env node
/**
 * Protect the model-neutral rename's deliberately frozen compatibility surface.
 *
 * The required CI lane runs the local contract only. `--live` additionally
 * follows the public redirects as an operator receipt; it is intentionally not
 * part of required CI because GitHub and skills.sh availability are external.
 */

import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import ts from 'typescript';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const DEFAULT_ROOT = join(SCRIPT_DIR, '..');

export const IDENTITY = Object.freeze({
  canonicalRepository: 'jeremylongshore/tons-of-skills-marketplace',
  rootRepositoryUrl: 'git+https://github.com/jeremylongshore/tons-of-skills-marketplace.git',
  cliRepositoryUrl: 'https://github.com/jeremylongshore/tons-of-skills-marketplace.git',
  catalogUrl:
    'https://raw.githubusercontent.com/jeremylongshore/tons-of-skills-marketplace/main/.claude-plugin/marketplace.json',
  marketplaceSlug: 'claude-code-plugins-plus',
  packageName: '@intentsolutionsio/ccpi',
  cliEntry: './dist/index.js',
  installCommand: '/plugin marketplace add jeremylongshore/claude-code-plugins',
  skillsRoute: 'https://skills.sh/jeremylongshore/tons-of-skills-marketplace',
});

export const LIVE_REDIRECTS = Object.freeze([
  {
    label: 'legacy GitHub install repository',
    source: 'https://github.com/jeremylongshore/claude-code-plugins',
    destination: 'https://github.com/jeremylongshore/tons-of-skills-marketplace',
  },
  {
    label: 'legacy GitHub repository',
    source: 'https://github.com/jeremylongshore/claude-code-plugins-plus-skills',
    destination: 'https://github.com/jeremylongshore/tons-of-skills-marketplace',
  },
  {
    label: 'legacy GitHub clone endpoint',
    source: 'https://github.com/jeremylongshore/claude-code-plugins-plus-skills.git',
    destination: 'https://github.com/jeremylongshore/tons-of-skills-marketplace',
  },
  {
    label: 'legacy skills.sh discovery route',
    source: 'https://skills.sh/jeremylongshore/claude-code-plugins-plus-skills',
    destination: IDENTITY.skillsRoute,
  },
]);

const PROGRAM_IMPORTS = Object.freeze([
  { source: 'commander', named: ['Command'] },
  { source: './utils/paths.js', named: ['detectClaudePaths'] },
  { source: './commands/install.js', named: ['installPlugin'] },
  { source: './commands/upgrade.js', named: ['upgradeCommand'] },
  { source: './commands/list.js', named: ['listPlugins'] },
  { source: './commands/doctor.js', named: ['doctorCheck'] },
  {
    source: './commands/marketplace.js',
    named: ['marketplaceCommand', 'addMarketplace', 'removeMarketplace'],
  },
  { source: './commands/validate.js', named: ['validateCommand'] },
  {
    source: './commands/skills.js',
    named: ['doctorSkills', 'installPortableSkill', 'listHarnesses'],
  },
  { source: './utils/version.js', named: ['getVersion'] },
  { source: 'chalk', default: 'chalk' },
  { source: 'ora', default: 'ora' },
]);

const ACTION_DIRECT_CALLS = new Set([
  'String',
  'addMarketplace',
  'detectClaudePaths',
  'doctorCheck',
  'doctorSkills',
  'installPlugin',
  'installPortableSkill',
  'listHarnesses',
  'listPlugins',
  'marketplaceCommand',
  'ora',
  'removeMarketplace',
  'upgradeCommand',
  'validateCommand',
]);

const ACTION_MEMBER_CALLS = Object.freeze({
  chalk: new Set(['blue', 'gray', 'red', 'yellow']),
  console: new Set(['error', 'log']),
  process: new Set(['exit']),
  spinner: new Set(['fail', 'succeed']),
});

const ACTION_PROTECTED_BINDINGS = new Set([
  ...ACTION_DIRECT_CALLS,
  ...Object.keys(ACTION_MEMBER_CALLS),
]);

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

export function loadIdentitySnapshot(root = DEFAULT_ROOT) {
  return {
    rootPackage: readJson(join(root, 'package.json')),
    cliPackage: readJson(join(root, 'packages/cli/package.json')),
    extendedCatalog: readJson(join(root, '.claude-plugin/marketplace.extended.json')),
    generatedCatalog: readJson(join(root, '.claude-plugin/marketplace.json')),
    readme: readFileSync(join(root, 'README.md'), 'utf8'),
    cliConstantsSource: readFileSync(join(root, 'packages/cli/src/utils/constants.ts'), 'utf8'),
    cliProgramSource: readFileSync(join(root, 'packages/cli/src/program.ts'), 'utf8'),
  };
}

export function hasExportedString(source, name, value) {
  const sourceFile = ts.createSourceFile(
    'identity-constants.ts',
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  );
  if (sourceFile.parseDiagnostics.length > 0) return false;

  const values = [];
  for (const statement of sourceFile.statements) {
    if (!ts.isVariableStatement(statement)) continue;
    const exported = statement.modifiers?.some(
      (modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword,
    );
    const constant = (statement.declarationList.flags & ts.NodeFlags.Const) !== 0;
    if (!exported || !constant) continue;
    for (const declaration of statement.declarationList.declarations) {
      if (!ts.isIdentifier(declaration.name) || declaration.name.text !== name) continue;
      if (declaration.initializer && ts.isStringLiteralLike(declaration.initializer)) {
        values.push(declaration.initializer.text);
      } else {
        values.push(null);
      }
    }
  }
  return values.length === 1 && values[0] === value;
}

function buildProgramFunction(source) {
  const sourceFile = ts.createSourceFile(
    'program.ts',
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  );
  if (sourceFile.parseDiagnostics.length > 0) return null;
  const importStatements = sourceFile.statements.filter(ts.isImportDeclaration);
  const exactImports =
    importStatements.length === PROGRAM_IMPORTS.length &&
    importStatements.every((statement, index) => {
      const expected = PROGRAM_IMPORTS[index];
      const clause = statement.importClause;
      if (
        !clause ||
        clause.isTypeOnly ||
        !ts.isStringLiteral(statement.moduleSpecifier) ||
        statement.moduleSpecifier.text !== expected.source ||
        statement.attributes
      ) {
        return false;
      }
      if ((clause.name?.text ?? null) !== (expected.default ?? null)) return false;
      const bindings = clause.namedBindings;
      if (!expected.named) return !bindings;
      if (!bindings || !ts.isNamedImports(bindings)) return false;
      return (
        bindings.elements.length === expected.named.length &&
        bindings.elements.every(
          (element, elementIndex) =>
            !element.isTypeOnly &&
            !element.propertyName &&
            element.name.text === expected.named[elementIndex],
        )
      );
    });
  if (!exactImports) return null;

  const matches = sourceFile.statements.filter(
    (statement) =>
      ts.isFunctionDeclaration(statement) &&
      statement.name?.text === 'buildProgram' &&
      statement.body &&
      statement.parameters.length === 0 &&
      !statement.asteriskToken &&
      statement.modifiers?.some((modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword) &&
      !statement.modifiers?.some((modifier) => modifier.kind === ts.SyntaxKind.AsyncKeyword) &&
      !statement.modifiers?.some((modifier) => modifier.kind === ts.SyntaxKind.DefaultKeyword),
  );
  if (matches.length !== 1) return null;
  const buildProgram = matches[0];
  const constrainedModule = sourceFile.statements.every(
    (statement) =>
      (ts.isImportDeclaration(statement) && Boolean(statement.importClause)) ||
      statement === buildProgram,
  );
  return constrainedModule ? buildProgram : null;
}

function fluentCalls(expression, receiver) {
  if (ts.isIdentifier(expression) && expression.text === receiver) return [];
  if (!ts.isCallExpression(expression) || !ts.isPropertyAccessExpression(expression.expression)) {
    return null;
  }
  const preceding = fluentCalls(expression.expression.expression, receiver);
  if (!preceding) return null;
  return [...preceding, { method: expression.expression.name.text, call: expression }];
}

function referencesRegistrationBinding(node) {
  let found = false;
  const forbiddenIdentifiers = new Set([
    'Command',
    'Function',
    'arguments',
    'eval',
    'global',
    'globalThis',
    'module',
    'process',
    'program',
    'require',
    'skills',
  ]);
  const forbiddenProperties = new Set(['constructor', 'getBuiltinModule', 'mainModule']);
  const isAllowedProcessExit = (current) => {
    if (!ts.isIdentifier(current) || current.text !== 'process') return false;
    const access = current.parent;
    if (
      !ts.isPropertyAccessExpression(access) ||
      access.expression !== current ||
      access.name.text !== 'exit'
    ) {
      return false;
    }
    const call = access.parent;
    return (
      ts.isCallExpression(call) &&
      call.expression === access &&
      call.arguments.length === 1 &&
      ts.isNumericLiteral(call.arguments[0]) &&
      call.arguments[0].text === '1'
    );
  };
  const visit = (current) => {
    if (
      (ts.isIdentifier(current) &&
        forbiddenIdentifiers.has(current.text) &&
        !isAllowedProcessExit(current)) ||
      (ts.isPropertyAccessExpression(current) && forbiddenProperties.has(current.name.text)) ||
      ts.isElementAccessExpression(current) ||
      current.kind === ts.SyntaxKind.ThisKeyword ||
      (ts.isCallExpression(current) && current.expression.kind === ts.SyntaxKind.ImportKeyword)
    ) {
      found = true;
      return;
    }
    ts.forEachChild(current, visit);
  };
  visit(node);
  return found;
}

function isAllowedActionCall(call) {
  if (call.questionDotToken || call.typeArguments?.length) return false;
  const callee = call.expression;
  if (ts.isIdentifier(callee)) return ACTION_DIRECT_CALLS.has(callee.text);
  if (!ts.isPropertyAccessExpression(callee) || callee.questionDotToken) return false;
  if (ts.isIdentifier(callee.expression)) {
    return ACTION_MEMBER_CALLS[callee.expression.text]?.has(callee.name.text) ?? false;
  }
  return (
    callee.name.text === 'start' &&
    ts.isCallExpression(callee.expression) &&
    ts.isIdentifier(callee.expression.expression) &&
    callee.expression.expression.text === 'ora'
  );
}

function isAllowedSpinnerDeclaration(declaration) {
  if (!ts.isIdentifier(declaration.name) || declaration.name.text !== 'spinner') return false;
  const initializer = declaration.initializer;
  if (!initializer || !ts.isCallExpression(initializer) || initializer.arguments.length !== 0) {
    return false;
  }
  const start = initializer.expression;
  if (!ts.isPropertyAccessExpression(start) || start.name.text !== 'start') return false;
  const oraCall = start.expression;
  return (
    ts.isCallExpression(oraCall) &&
    ts.isIdentifier(oraCall.expression) &&
    oraCall.expression.text === 'ora' &&
    oraCall.arguments.length === 1 &&
    ts.isStringLiteralLike(oraCall.arguments[0])
  );
}

function hasSafeActionBody(node) {
  let safe = true;
  let spinnerDeclarations = 0;
  const visit = (current) => {
    if (
      ts.isNewExpression(current) ||
      ts.isTaggedTemplateExpression(current) ||
      ts.isComputedPropertyName(current) ||
      ts.isFunctionDeclaration(current) ||
      ts.isFunctionExpression(current) ||
      ts.isArrowFunction(current) ||
      ts.isClassDeclaration(current) ||
      ts.isClassExpression(current) ||
      ts.isMethodDeclaration(current) ||
      ts.isGetAccessorDeclaration(current) ||
      ts.isSetAccessorDeclaration(current) ||
      ts.isForStatement(current) ||
      ts.isForInStatement(current) ||
      ts.isForOfStatement(current) ||
      (ts.isBinaryExpression(current) &&
        current.operatorToken.kind >= ts.SyntaxKind.FirstAssignment &&
        current.operatorToken.kind <= ts.SyntaxKind.LastAssignment) ||
      (ts.isPrefixUnaryExpression(current) &&
        (current.operator === ts.SyntaxKind.PlusPlusToken ||
          current.operator === ts.SyntaxKind.MinusMinusToken)) ||
      ts.isPostfixUnaryExpression(current) ||
      (ts.isCallExpression(current) && !isAllowedActionCall(current))
    ) {
      safe = false;
      return;
    }
    if (ts.isVariableStatement(current)) {
      const declarations = current.declarationList.declarations;
      if (
        (current.declarationList.flags & ts.NodeFlags.Const) === 0 ||
        declarations.some((declaration) => !ts.isIdentifier(declaration.name))
      ) {
        safe = false;
        return;
      }
      for (const declaration of declarations) {
        if (!ACTION_PROTECTED_BINDINGS.has(declaration.name.text)) continue;
        if (!isAllowedSpinnerDeclaration(declaration) || spinnerDeclarations > 0) {
          safe = false;
          return;
        }
        spinnerDeclarations += 1;
      }
    }
    if (
      ts.isCatchClause(current) &&
      current.variableDeclaration &&
      (!ts.isIdentifier(current.variableDeclaration.name) ||
        ACTION_PROTECTED_BINDINGS.has(current.variableDeclaration.name.text))
    ) {
      safe = false;
      return;
    }
    ts.forEachChild(current, visit);
  };
  visit(node);
  return safe;
}

function isStringArgument(argument) {
  return ts.isStringLiteralLike(argument);
}

function positionalArgumentCount(command) {
  return command.match(/<[^>]+>|\[[^\]]+\]/g)?.length ?? 0;
}

function hasSafeActionCallback(callback, calls) {
  if (!ts.isArrowFunction(callback)) return false;
  const commandCall = calls.find((entry) => entry.method === 'command')?.call;
  const command = commandCall ? stringArgument(commandCall) : null;
  if (command === null) return false;
  if (callback.parameters.length > positionalArgumentCount(command) + 1) return false;
  return (
    callback.parameters.every(
      (parameter) =>
        ts.isIdentifier(parameter.name) &&
        !ACTION_PROTECTED_BINDINGS.has(parameter.name.text) &&
        !parameter.dotDotDotToken &&
        !parameter.initializer,
    ) &&
    !referencesRegistrationBinding(callback.body) &&
    hasSafeActionBody(callback.body)
  );
}

function hasSafeRegistrationArguments(entry, calls) {
  const args = [...entry.call.arguments];
  switch (entry.method) {
    case 'name':
    case 'command':
    case 'description':
      return args.length === 1 && args.every(isStringArgument);
    case 'option':
    case 'requiredOption':
      return args.length >= 2 && args.length <= 3 && args.every(isStringArgument);
    case 'version':
      return (
        args.length === 1 &&
        ts.isCallExpression(args[0]) &&
        ts.isIdentifier(args[0].expression) &&
        args[0].expression.text === 'getVersion' &&
        args[0].arguments.length === 0
      );
    case 'action':
      return args.length === 1 && hasSafeActionCallback(args[0], calls);
    default:
      return false;
  }
}

function safeFluentCalls(expression, receiver) {
  const calls = fluentCalls(expression, receiver);
  if (!calls) return null;
  return calls.some(
    (entry) =>
      entry.call.arguments.some(referencesRegistrationBinding) ||
      !hasSafeRegistrationArguments(entry, calls),
  )
    ? null
    : calls;
}

function hasProgramExpressionShape(calls) {
  const commandCount = calls.filter((entry) => entry.method === 'command').length;
  const actionCount = calls.filter((entry) => entry.method === 'action').length;
  if (commandCount === 0) {
    return (
      calls.length === 3 &&
      calls[0].method === 'name' &&
      calls[1].method === 'description' &&
      calls[2].method === 'version' &&
      actionCount === 0
    );
  }
  return (
    commandCount === 1 &&
    actionCount === 1 &&
    calls[0].method === 'command' &&
    calls.at(-1).method === 'action'
  );
}

function hasSkillsBindingShape(calls) {
  return calls.length === 2 && calls[0].method === 'command' && calls[1].method === 'description';
}

function hasPortableCommandShape(calls) {
  return (
    calls.filter((entry) => entry.method === 'command').length === 1 &&
    calls.filter((entry) => entry.method === 'action').length === 1 &&
    calls[0].method === 'command' &&
    calls.at(-1).method === 'action' &&
    !calls.some((entry) => entry.method === 'name')
  );
}

function hasConstrainedBuildFlow(body) {
  const statements = body.statements;
  const finalStatement = statements.at(-1);
  if (
    !finalStatement ||
    !ts.isReturnStatement(finalStatement) ||
    !finalStatement.expression ||
    !ts.isIdentifier(finalStatement.expression) ||
    finalStatement.expression.text !== 'program'
  ) {
    return false;
  }

  let programDeclared = false;
  let skillsDeclared = false;
  const valid = statements.slice(0, -1).every((statement, index) => {
    if (ts.isVariableStatement(statement)) {
      if (
        (statement.declarationList.flags & ts.NodeFlags.Const) === 0 ||
        statement.declarationList.declarations.length !== 1
      ) {
        return false;
      }
      const declaration = statement.declarationList.declarations[0];
      if (!ts.isIdentifier(declaration.name)) return false;
      if (declaration.name.text === 'program') {
        if (index !== 0 || programDeclared || !declaration.initializer) return false;
        programDeclared = true;
        return (
          ts.isNewExpression(declaration.initializer) &&
          ts.isIdentifier(declaration.initializer.expression) &&
          declaration.initializer.expression.text === 'Command' &&
          declaration.initializer.arguments?.length === 0
        );
      }
      if (declaration.name.text === 'skills') {
        if (!programDeclared || skillsDeclared || !declaration.initializer) return false;
        skillsDeclared = true;
        const calls = safeFluentCalls(declaration.initializer, 'program');
        return calls !== null && hasSkillsBindingShape(calls);
      }
      return false;
    }
    if (!ts.isExpressionStatement(statement)) return false;
    if (!programDeclared) return false;
    const programCalls = safeFluentCalls(statement.expression, 'program');
    if (programCalls !== null) return hasProgramExpressionShape(programCalls);
    if (!skillsDeclared) return false;
    const skillsCalls = safeFluentCalls(statement.expression, 'skills');
    return skillsCalls !== null && hasPortableCommandShape(skillsCalls);
  });
  return valid && programDeclared && skillsDeclared;
}

function stringArgument(call) {
  const argument = call?.arguments[0];
  return argument && ts.isStringLiteralLike(argument) ? argument.text : null;
}

function hasProgramIdentity(source, expectedName, expectedCommand) {
  const buildProgram = buildProgramFunction(source);
  if (!buildProgram) return { name: false, command: false };
  if (!hasConstrainedBuildFlow(buildProgram.body)) return { name: false, command: false };
  const programDeclarations = buildProgram.body.statements.flatMap((statement) => {
    if (
      !ts.isVariableStatement(statement) ||
      (statement.declarationList.flags & ts.NodeFlags.Const) === 0
    ) {
      return [];
    }
    return statement.declarationList.declarations.filter(
      (declaration) =>
        ts.isIdentifier(declaration.name) &&
        declaration.name.text === 'program' &&
        declaration.initializer &&
        ts.isNewExpression(declaration.initializer) &&
        ts.isIdentifier(declaration.initializer.expression) &&
        declaration.initializer.expression.text === 'Command',
    );
  });
  if (programDeclarations.length !== 1) return { name: false, command: false };

  const programCalls = buildProgram.body.statements.flatMap((statement) => {
    if (ts.isExpressionStatement(statement)) {
      return safeFluentCalls(statement.expression, 'program') ?? [];
    }
    if (!ts.isVariableStatement(statement)) return [];
    const declaration = statement.declarationList.declarations[0];
    if (
      !declaration ||
      !ts.isIdentifier(declaration.name) ||
      declaration.name.text !== 'skills' ||
      !declaration.initializer
    ) {
      return [];
    }
    return safeFluentCalls(declaration.initializer, 'program') ?? [];
  });
  const nameCalls = programCalls
    .filter((entry) => entry.method === 'name')
    .map((entry) => entry.call);
  const name = nameCalls.length === 1 && stringArgument(nameCalls[0]) === expectedName;

  const skillBindings = buildProgram.body.statements.flatMap((statement) => {
    if (
      !ts.isVariableStatement(statement) ||
      (statement.declarationList.flags & ts.NodeFlags.Const) === 0
    ) {
      return [];
    }
    return statement.declarationList.declarations.filter(
      (declaration) => ts.isIdentifier(declaration.name) && declaration.name.text === 'skills',
    );
  });
  const skillCalls =
    skillBindings.length === 1 && skillBindings[0].initializer
      ? safeFluentCalls(skillBindings[0].initializer, 'program')
      : null;
  const commandCalls =
    skillCalls?.filter((entry) => entry.method === 'command').map((entry) => entry.call) ?? [];
  const allExpectedCommandCalls = programCalls.filter(
    (entry) => entry.method === 'command' && stringArgument(entry.call) === expectedCommand,
  );
  const command =
    commandCalls.length === 1 &&
    stringArgument(commandCalls[0]) === expectedCommand &&
    allExpectedCommandCalls.length === 1;
  return { name, command };
}

export function checkIdentityCompatibility(snapshot) {
  const violations = [];
  const {
    rootPackage,
    cliPackage,
    extendedCatalog,
    generatedCatalog,
    readme,
    cliConstantsSource,
    cliProgramSource,
  } = snapshot;

  if (rootPackage.repository?.url !== IDENTITY.rootRepositoryUrl) {
    violations.push('root package repository URL is not canonical');
  }
  if (
    cliPackage.repository?.url !== IDENTITY.cliRepositoryUrl ||
    cliPackage.repository?.directory !== 'packages/cli'
  ) {
    violations.push('CLI package repository metadata is not canonical');
  }
  if (cliPackage.name !== IDENTITY.packageName) {
    violations.push(`published CLI package identity must remain ${IDENTITY.packageName}`);
  }
  if (cliPackage.bin?.ccpi !== IDENTITY.cliEntry || cliPackage.bin?.tons !== IDENTITY.cliEntry) {
    violations.push('ccpi and tons binary aliases must both resolve to the same CLI entry point');
  }
  if (
    extendedCatalog.name !== IDENTITY.marketplaceSlug ||
    generatedCatalog.name !== IDENTITY.marketplaceSlug
  ) {
    violations.push(`marketplace install identity must remain ${IDENTITY.marketplaceSlug}`);
  }
  if (!readme.includes(IDENTITY.installCommand)) {
    violations.push(`frozen install command is missing: ${IDENTITY.installCommand}`);
  }
  if (!readme.includes(IDENTITY.skillsRoute)) {
    violations.push(`canonical skills.sh route is missing: ${IDENTITY.skillsRoute}`);
  }
  if (!hasExportedString(cliConstantsSource, 'MARKETPLACE_REPO', IDENTITY.canonicalRepository)) {
    violations.push('CLI marketplace repository constant is not canonical');
  }
  if (!hasExportedString(cliConstantsSource, 'MARKETPLACE_SLUG', IDENTITY.marketplaceSlug)) {
    violations.push('CLI marketplace slug no longer preserves the install identity');
  }
  if (!hasExportedString(cliConstantsSource, 'CATALOG_URL', IDENTITY.catalogUrl)) {
    violations.push('CLI catalog URL is not canonical');
  }
  const programIdentity = hasProgramIdentity(cliProgramSource, 'ccpi', 'skills');
  if (!programIdentity.name) {
    violations.push('existing ccpi program identity is missing');
  }
  if (!programIdentity.command) {
    violations.push('portable capability is not exposed through the tons skills command family');
  }

  return violations;
}

function normalizedDestination(value) {
  const url = new URL(value);
  url.hostname = url.hostname.replace(/^www\./, '');
  url.hash = '';
  url.search = '';
  url.pathname = url.pathname.replace(/\.git\/?$/, '').replace(/\/$/, '');
  return url.toString().replace(/\/$/, '');
}

export function checkRedirectResult(contract, response) {
  const violations = [];
  if (response.status < 200 || response.status >= 300) {
    violations.push(`${contract.label} returned HTTP ${response.status}`);
  }
  if (normalizedDestination(response.url) !== normalizedDestination(contract.destination)) {
    violations.push(
      `${contract.label} resolved to ${response.url}, expected ${contract.destination}`,
    );
  }
  return violations;
}

export async function checkLiveRedirects(fetchImpl = globalThis.fetch) {
  if (typeof fetchImpl !== 'function') {
    throw new TypeError('a fetch implementation is required for live redirect checks');
  }

  const results = [];
  for (const contract of LIVE_REDIRECTS) {
    const response = await fetchImpl(contract.source, {
      redirect: 'follow',
      headers: { 'user-agent': 'tons-of-skills-identity-check/1.0' },
    });
    const violations = checkRedirectResult(contract, response);
    results.push({
      ...contract,
      status: response.status,
      resolved: response.url,
      violations,
    });
    if (response.body && typeof response.body.cancel === 'function') await response.body.cancel();
  }
  return results;
}

async function main() {
  const args = process.argv.slice(2);
  const unknown = args.filter((arg) => arg !== '--live');
  if (unknown.length > 0) {
    console.error(`identity-compatibility: unknown argument(s): ${unknown.join(', ')}`);
    process.exitCode = 2;
    return;
  }

  const violations = checkIdentityCompatibility(loadIdentitySnapshot());
  for (const violation of violations) {
    console.error(`identity-compatibility: VIOLATION — ${violation}`);
  }
  if (violations.length > 0) {
    console.error(`identity-compatibility: FAIL — ${violations.length} local violation(s)`);
    process.exitCode = 1;
    return;
  }
  console.log(
    'identity-compatibility: OK (canonical repository + frozen install/package/CLI identities)',
  );

  if (args.includes('--live')) {
    const results = await checkLiveRedirects();
    const liveViolations = results.flatMap((result) => result.violations);
    for (const result of results) {
      console.log(
        `identity-compatibility: ${result.label}: HTTP ${result.status} -> ${result.resolved}`,
      );
    }
    for (const violation of liveViolations) {
      console.error(`identity-compatibility: LIVE VIOLATION — ${violation}`);
    }
    if (liveViolations.length > 0) {
      console.error(
        `identity-compatibility: LIVE FAIL — ${liveViolations.length} redirect violation(s)`,
      );
      process.exitCode = 1;
      return;
    }
    console.log('identity-compatibility: LIVE OK');
  }
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (isMain) await main();
