import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';

const moduleURL = new URL('../dist/storage.js', import.meta.url).href;
const prelude = `
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {syncBuiltinESMExports} from 'node:module';
import {join} from 'node:path';
const folder=join(process.env.HOME,'.ai-experiment-logger');
const file=join(folder,'experiments.json');
const input={aiTool:'fixture',prompt:'synthetic',result:'synthetic',rating:5};
const load=async()=> (await import(${JSON.stringify(moduleURL)})).ExperimentStorage;
`;
async function scenario(name, program) {
  const home = await mkdtemp(join(tmpdir(), 'logger-storage-'));
  try {
    const result = spawnSync(process.execPath, ['--input-type=module', '-e', prelude + program], {
      cwd: home,
      env: { PATH: process.env.PATH, HOME: home, USERPROFILE: home },
      encoding: 'utf8',
      timeout: 15000,
    });
    assert.equal(result.error, undefined, name);
    assert.equal(result.status, 0, `${name}: ${result.stderr}`);
    assert.equal(result.stdout, '', 'storage must not write protocol-unrelated stdout');
  } finally {
    await rm(home, { recursive: true, force: true });
  }
}

test('invalid JSON fails closed without overwriting or disclosing its contents', () => scenario('invalid JSON', `
await fs.mkdir(folder,{mode:0o700});
const bytes='{ "synthetic-private-marker":';
await fs.writeFile(file,bytes);
const Store=await load(), store=new Store();
await assert.rejects(store.initialize(),error=>!error.message.includes('synthetic-private-marker'));
assert.equal(await fs.readFile(file,'utf8'),bytes);
`));

test('unsupported stored shape and version remain untouched', () => scenario('invalid shape', `
await fs.mkdir(folder,{mode:0o700});
const Store=await load();
for(const data of [{version:'1.0.0',experiments:'bad'},{version:'future',experiments:[]}]){
 const bytes=JSON.stringify(data);await fs.writeFile(file,bytes);
 await assert.rejects(new Store().initialize());assert.equal(await fs.readFile(file,'utf8'),bytes);
}
`));

test('two initialized stores retain each other\'s committed changes', () => scenario('multiple stores', `
const Store=await load(), first=new Store(), second=new Store();
await first.initialize();await second.initialize();
const a=await first.createExperiment({...input,prompt:'first'});
const b=await second.createExperiment({...input,prompt:'second'});
assert.deepEqual(new Set((await first.listExperiments()).map(r=>r.id)),new Set([a.id,b.id]));
await first.updateExperiment(a.id,{result:'updated'});
await second.deleteExperiment(b.id);
const rows=await first.listExperiments();assert.equal(rows.length,1);assert.equal(rows[0].result,'updated');
`));

test('concurrent writes within one instance persist all accepted records', () => scenario('queued writes', `
const Store=await load(), store=new Store();await store.initialize();
await Promise.all(Array.from({length:12},(_,i)=>store.createExperiment({...input,prompt:String(i)})));
const data=JSON.parse(await fs.readFile(file,'utf8'));assert.equal(data.experiments.length,12);
assert.equal(new Set(data.experiments.map(r=>r.prompt)).size,12);
`));

test('a preexisting writer lock is not stolen or removed', () => scenario('busy lock', `
const Store=await load(), store=new Store();await store.initialize();
const before=await fs.readFile(file,'utf8'), lock=join(folder,'.experiments.lock');
await fs.writeFile(lock,'synthetic-owner',{mode:0o600});
await assert.rejects(store.createExperiment(input));
assert.equal(await fs.readFile(file,'utf8'),before);assert.equal(await fs.readFile(lock,'utf8'),'synthetic-owner');
`));

test('failure before atomic rename preserves disk, memory and future write ability', () => scenario('atomic failure', `
const Store=await load(), store=new Store();await store.initialize();
await store.createExperiment(input);const before=await fs.readFile(file,'utf8');
const original=fs.rename;let calls=0;
fs.rename=async(from,to)=>{
 calls++;assert.equal(to,file);assert.equal(await fs.readFile(file,'utf8'),before);
 assert.equal(JSON.parse(await fs.readFile(from,'utf8')).experiments.length,2);
 assert.equal((await fs.stat(from)).mode&0o777,0o600);
 throw Object.assign(new Error('synthetic failure'),{code:'EIO'});
};syncBuiltinESMExports();
await assert.rejects(store.createExperiment({...input,prompt:'not committed'}));
fs.rename=original;syncBuiltinESMExports();assert.equal(calls,1);
assert.equal(await fs.readFile(file,'utf8'),before);assert.equal((await store.listExperiments()).length,1);
assert.deepEqual((await fs.readdir(folder)).sort(),['experiments.json']);
await store.createExperiment({...input,prompt:'recovered'});assert.equal((await store.listExperiments()).length,2);
`));

test('new files and directory have private permissions on POSIX', {skip: process.platform === 'win32'}, () => scenario('private modes', `
const Store=await load(), store=new Store();await store.initialize();
assert.equal((await fs.stat(folder)).mode&0o777,0o700);assert.equal((await fs.stat(file)).mode&0o777,0o600);
await store.createExperiment(input);assert.equal((await fs.stat(file)).mode&0o777,0o600);
`));

test('a symlinked data file cannot redirect storage writes', {skip: process.platform === 'win32'}, () => scenario('file symlink', `
await fs.mkdir(folder,{mode:0o700});const target=join(process.env.HOME,'target');
await fs.writeFile(target,JSON.stringify({version:'1.0.0',experiments:[]}));const before=await fs.readFile(target,'utf8');
await fs.symlink(target,file);const Store=await load();await assert.rejects(new Store().initialize());
assert.equal(await fs.readFile(target,'utf8'),before);assert.equal((await fs.lstat(file)).isSymbolicLink(),true);
`));

test('a symlinked data directory is rejected', {skip: process.platform === 'win32'}, () => scenario('directory symlink', `
const target=join(process.env.HOME,'target');await fs.mkdir(target);await fs.symlink(target,folder);
const Store=await load();await assert.rejects(new Store().initialize());assert.deepEqual(await fs.readdir(target),[]);
`));

test('external deletion never silently recreates an initialized store', () => scenario('missing file', `
const Store=await load(), store=new Store();await store.initialize();await fs.unlink(file);
await assert.rejects(store.createExperiment(input));await assert.rejects(store.listExperiments());
await assert.rejects(fs.stat(file),{code:'ENOENT'});
`));

test('CSV quotes dates and tags and neutralizes formula-leading text', () => scenario('CSV data', `
const Store=await load(), store=new Store();await store.initialize();
await store.createExperiment({...input,aiTool:'=1+1',prompt:'  @SUM(1)',result:'a"b',date:'date,with,commas',tags:['tag"quoted','=other']});
const csv=await store.exportToCSV();
const quote=String.fromCharCode(34), apostrophe=String.fromCharCode(39);
assert.ok(csv.includes(quote+apostrophe+'=1+1'+quote));
assert.ok(csv.includes(quote+apostrophe+'  @SUM(1)'+quote));
assert.ok(csv.includes('"a""b"'));assert.ok(csv.includes('"date,with,commas"'));
assert.ok(csv.includes('"tag""quoted, =other"'));
`));


test('replacement after descriptor open fails closed before reading bytes', () => scenario('descriptor replacement', `
await fs.mkdir(folder,{mode:0o700});
await fs.writeFile(file,JSON.stringify({version:'1.0.0',experiments:[]}));
const original=fs.open;let intercepted=false, read=false;
fs.open=async(path,...args)=>{
 const handle=await original(path,...args);
 if(path===file&&!intercepted){
  intercepted=true;
  const readFile=handle.readFile.bind(handle);
  handle.readFile=async(...values)=>{read=true;return readFile(...values);};
  await fs.rename(file,file+'.previous');
  await fs.writeFile(file,'synthetic replacement');
 }
 return handle;
};syncBuiltinESMExports();
const Store=await load();await assert.rejects(new Store().initialize());
fs.open=original;syncBuiltinESMExports();
assert.equal(intercepted,true);assert.equal(read,false);
assert.equal(await fs.readFile(file,'utf8'),'synthetic replacement');
assert.equal(JSON.parse(await fs.readFile(file+'.previous','utf8')).version,'1.0.0');
`));
