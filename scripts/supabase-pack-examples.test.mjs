/** Offline regressions execute actual documented functions, not copied implementations.
 * VM capability injection is a test fixture, not OS isolation or an SDK/SQL proof.
 */
import assert from 'node:assert/strict';
import { createHmac, webcrypto } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { test as nodeTest } from 'node:test';
import { TextDecoder, TextEncoder } from 'node:util';
import vm from 'node:vm';
import ts from 'typescript';

const { Request, Response } = globalThis;
const test = (name, fn) => nodeTest(name, { timeout: 5000 }, fn);
const skills = new URL('../plugins/saas-packs/supabase-pack/skills/', import.meta.url);
function example(relativePath, marker) {
  const markdown = readFileSync(new URL(relativePath, skills), 'utf8');
  return selectExample(markdown, marker);
}
function selectExample(markdown, marker) {
  const matches = [...markdown.matchAll(/^```typescript\n([\s\S]*?)^```/gm)]
    .map((match) => match[1])
    .filter((block) => block.includes(marker));
  assert.equal(matches.length, 1, `Expected one example containing ${marker}`);
  const ast = ts.createSourceFile('selected.ts', matches[0], ts.ScriptTarget.Latest, true);
  const name = marker.split(' ').at(-1);
  assert.equal(
    ast.statements.filter((statement) => statement.name?.text === name).length,
    1,
    `Expected one named declaration for ${name}`,
  );
  return matches[0];
}
function load(source, imports = {}, deployment = false) {
  const ast = ts.createSourceFile('example.ts', source, ts.ScriptTarget.Latest, true);
  const declarations = ast.statements.filter((statement) => {
    if (ts.isImportDeclaration(statement)) {
      assert(Object.hasOwn(imports, statement.moduleSpecifier.text), 'Unexpected example import');
      return true;
    }
    if (ts.isExpressionStatement(statement)) {
      const call = statement.expression;
      assert(
        deployment &&
          ts.isCallExpression(call) &&
          ts.isPropertyAccessExpression(call.expression) &&
          call.expression.expression.getText(ast) === 'Deno' &&
          call.expression.name.text === 'serve',
        'Unexpected top-level activation',
      );
      // The deployment binding is not executed; tests call the actual handler directly.
      return false;
    }
    assert(
      ts.isFunctionDeclaration(statement) ||
        ts.isClassDeclaration(statement) ||
        ts.isTypeAliasDeclaration(statement) ||
        ts.isInterfaceDeclaration(statement) ||
        (ts.isVariableStatement(statement) &&
          statement.declarationList.declarations.every((declaration) =>
            ['TRANSIENT_READ_CODES', 'encoder', 'UUID'].includes(declaration.name.getText(ast)),
          )),
      'Unexpected top-level declaration',
    );
    return true;
  });
  const selected = ts
    .createPrinter()
    .printList(ts.ListFormat.MultiLine, ts.factory.createNodeArray(declarations), ast);
  const compiled = ts.transpileModule(selected, {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
    reportDiagnostics: true,
  });
  assert.deepEqual(compiled.diagnostics, []);
  const context = {
    exports: {},
    Uint8Array,
    TextEncoder,
    TextDecoder,
    Request,
    Response,
    crypto: webcrypto,
    require(name) {
      assert(Object.hasOwn(imports, name), 'Unexpected runtime import');
      return imports[name];
    },
  };
  vm.runInNewContext(compiled.outputText, context, { timeout: 1000 });
  return context.exports;
}
const reliabilityPath = 'supabase-reliability-patterns/SKILL.md';
const reliability = load(
  example(reliabilityPath, 'export async function withReadRetry') +
    example(reliabilityPath, 'export class ReadCircuit'),
);
const protocol = load(
  example(
    'supabase-webhooks-events/references/signature-verification.md',
    'export async function verifyOwnedWebhook',
  ),
);
const receiver = load(
  example(
    'supabase-webhooks-events/references/edge-function-receivers.md',
    'export async function handleOwnedWebhook',
  ),
  {
    './custom-protocol.ts': protocol,
    'npm:@supabase/supabase-js@2': {
      createClient() {
        throw new Error('Real SDK forbidden');
      },
    },
  },
  true,
);
const secret = 'synthetic-local-fixture-secret';
const timestamp = '1700000000';
const now = 1700000000000;
const bytes = Uint8Array.from([0, 255, 254, 128, 65]);
const event = {
  eventId: '00000000-0000-4000-8000-000000000001',
  type: 'order.created',
  orderId: '00000000-0000-4000-8000-000000000002',
};
async function request(body = new TextEncoder().encode(JSON.stringify(event))) {
  return new Request('https://receiver.invalid/hook', {
    method: 'POST',
    body,
    headers: {
      'x-app-timestamp': timestamp,
      'x-app-signature': await protocol.signOwnedWebhook(body, timestamp, secret),
    },
  });
}

test('extractor rejects missing, ambiguous blocks and duplicate named declarations', () => {
  const block = '```typescript\nexport class ReadCircuit {}\n```';
  assert.throws(() => selectExample('', 'export class ReadCircuit'));
  assert.throws(() => selectExample(block + '\n' + block, 'export class ReadCircuit'));
  assert.throws(() =>
    selectExample(
      '```typescript\nexport class ReadCircuit {}\n' + 'export class ReadCircuit {}\n```',
      'export class ReadCircuit',
    ),
  );
});

test('extractor rejects unknown imports and top-level server activation', () => {
  assert.throws(() => load("import x from 'node:child_process';"));
  assert.throws(() => load('Deno.serve(() => {});'));
});

test('read retries stop immediately for auth and exactly at the transient budget', async () => {
  for (const [code, expected] of [
    ['PGRST301', 1],
    ['42501', 1],
    ['08006', 4],
  ]) {
    let calls = 0;
    let sleeps = 0;
    await reliability.withReadRetry(
      async () => {
        calls++;
        return { data: null, error: { code } };
      },
      { maxRetries: 3, baseDelayMs: 0, maxDelayMs: 0 },
      async () => {
        sleeps++;
      },
      () => 0,
    );
    assert.equal(calls, expected);
    assert.equal(sleeps, expected - 1);
  }
});

for (const outcome of ['success', 'nonretryable failure']) {
  test(`stale closed ${outcome} cannot release or reset a newer half-open probe`, async () => {
    let clock = 0;
    const circuit = new reliability.ReadCircuit(1, 100, () => clock);
    let resolveOld;
    let resolveProbe;
    const old = circuit.call(
      () =>
        new Promise((resolve) => {
          resolveOld = resolve;
        }),
    );
    const observedOld = old.then(
      (value) => ({ value }),
      (error) => ({ error }),
    );
    await assert.rejects(() =>
      circuit.call(async () => ({ data: null, error: { code: '08006' } })),
    );
    clock = 100;
    const probe = circuit.call(
      () =>
        new Promise((resolve) => {
          resolveProbe = resolve;
        }),
    );
    resolveOld(
      outcome === 'success'
        ? { data: 'old', error: null }
        : { data: null, error: { code: '42501' } },
    );
    await observedOld;
    let extraProbe = false;
    await assert.rejects(() =>
      circuit.call(async () => {
        extraProbe = true;
        return { data: 'unexpected', error: null };
      }),
    );
    assert.equal(extraProbe, false);
    resolveProbe({ data: 'fresh', error: null });
    assert.equal(await probe, 'fresh');
  });
}

test('raw binary HMAC matches an independent Node vector and rejects reencoding/tamper', async () => {
  const signature = await protocol.signOwnedWebhook(bytes, timestamp, secret);
  assert.equal(
    signature,
    createHmac('sha256', secret).update(`${timestamp}.`).update(bytes).digest('hex'),
  );
  assert.equal(await protocol.verifyOwnedWebhook(bytes, signature, timestamp, secret, now), true);
  const reencoded = new TextEncoder().encode(new TextDecoder().decode(bytes));
  const tampered = bytes.slice();
  tampered[1] ^= 1;
  for (const body of [reencoded, tampered]) {
    assert.equal(await protocol.verifyOwnedWebhook(body, signature, timestamp, secret, now), false);
  }
});

test('HMAC rejects missing configuration, malformed signatures and stale/future timestamps', async () => {
  const signature = await protocol.signOwnedWebhook(bytes, timestamp, secret);
  for (const [sig, time, key, clock] of [
    [signature, timestamp, undefined, now],
    ['short', timestamp, secret, now],
    [signature, 'NaN', secret, now],
    [signature, timestamp, secret, NaN],
    [signature, timestamp, secret, now - 300001],
    [signature, timestamp, secret, now + 300001],
  ])
    assert.equal(await protocol.verifyOwnedWebhook(bytes, sig, time, key, clock), false);
});

test('receiver missing secret fails before reading/inserting', async () => {
  let inserts = 0;
  let readerCalls = 0;
  const unread = await request();
  Object.defineProperty(unread.body, 'getReader', {
    value() {
      readerCalls++;
      throw new Error('Body reader must not be acquired');
    },
  });
  const result = await receiver.handleOwnedWebhook(
    unread,
    undefined,
    {
      insert: async () => {
        inserts++;
        return { error: null };
      },
    },
    now,
  );
  assert.equal(result.status, 503);
  assert.equal(inserts, 0);
  assert.equal(readerCalls, 0);
  assert.equal(unread.bodyUsed, false);
});

test('receiver invalid authentication never inserts', async () => {
  let inserts = 0;
  const unsigned = new Request('https://receiver.invalid', { method: 'POST', body: '{}' });
  const result = await receiver.handleOwnedWebhook(
    unsigned,
    secret,
    {
      insert: async () => {
        inserts++;
        return { error: null };
      },
    },
    now,
  );
  assert.equal(result.status, 401);
  assert.equal(inserts, 0);
});

test('receiver returned/thrown insert errors and duplicate ID do not claim acceptance', async () => {
  for (const [insert, expected] of [
    [async () => ({ error: { code: '42501' } }), 503],
    [
      async () => {
        throw new Error('synthetic');
      },
      503,
    ],
    [async () => ({ error: { code: '23505' } }), 409],
  ])
    assert.equal(
      (await receiver.handleOwnedWebhook(await request(), secret, { insert }, now)).status,
      expected,
    );
});

test('receiver 202 waits for checked inbox success and never claims processing complete', async () => {
  let finish;
  let inserted;
  let completed = false;
  let entered;
  const insertEntered = new Promise((resolve) => {
    entered = resolve;
  });
  const response = receiver
    .handleOwnedWebhook(
      await request(),
      secret,
      {
        insert: (row) => {
          inserted = row;
          return new Promise((resolve) => {
            finish = resolve;
            entered();
          });
        },
      },
      now,
    )
    .then((value) => {
      completed = true;
      return value;
    });
  // Explicit entry handshake; premature response/rejection fails instead of polling CPU turns.
  await Promise.race([
    insertEntered,
    response.then(() => {
      throw new Error('Receiver settled before checked insertion');
    }),
  ]);
  assert.equal(typeof finish, 'function');
  assert.equal(completed, false);
  assert.deepEqual(
    { ...inserted },
    {
      event_id: event.eventId,
      event_type: event.type,
      order_id: event.orderId,
    },
  );
  finish({ error: null });
  const result = await response;
  assert.equal(result.status, 202);
  assert.deepEqual(await result.json(), {
    accepted: true,
    eventId: event.eventId,
    processingComplete: false,
  });
});
