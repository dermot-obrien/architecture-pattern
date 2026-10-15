// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

// Run: node --test skills/cross-reference/tests/*.test.cjs

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {loadRegisters} = require('../scripts/lib/registers.cjs');
const {readBindings, loadLocalMap} = require('../scripts/lib/config.cjs');
const remarkXref = require('../scripts/docusaurus/remark-xref.cjs');
const idRoutesPlugin = require('../scripts/docusaurus/id-routes.cjs');
const {writeIdRoutes, pagePath, docRoutes} = idRoutesPlugin;
const {check, configure, stripCode} = require('../scripts/xref.cjs');
const {registerToMap, fromRegister} = require('../scripts/lib/local-register.cjs');

const EXAMPLE = path.join(__dirname, '..', 'examples', 'catalogue');
const reg = (f) => path.join(EXAMPLE, 'registers', f);

function tmpRegisters(nsRows, idRows = []) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'xref-'));
  fs.writeFileSync(path.join(dir, 'ns.csv'), ['namespace,name,self,base_url,url_template,manifest,owner,notes', ...nsRows].join('\n'));
  fs.writeFileSync(path.join(dir, 'ids.csv'), ['namespace,id,name,repository,url,notes', ...idRows].join('\n'));
  fs.writeFileSync(path.join(dir, 'schemes.csv'), 'prefix\nBB\nPAT\n');
  return {namespaces: path.join(dir, 'ns.csv'), external: path.join(dir, 'ids.csv'), schemes: path.join(dir, 'schemes.csv')};
}

test('namespace codes follow the rules', () => {
  const regs = loadRegisters(tmpRegisters([
    'ex,Example,yes,https://e.org/,,,,',
    'ops,Ops,no,https://o.org,,,,',
    'bb,Clash,no,,,,,',
    'toolong,Long,no,,,,,',
    'Up,Upper,no,,,,,',
    'a-b,Hyphen,no,,,,,',
    'ops,Duplicate,no,,,,,',
  ]));
  assert.deepEqual([...regs.namespaces.keys()], ['ex', 'ops']);
  assert.equal(regs.namespaces.get('ops').baseUrl, 'https://o.org/');
  assert.equal(regs.self.namespace, 'ex');
  assert.equal(regs.warnings.length, 5);
  assert.match(regs.warnings.join('\n'), /"bb": it is an identifier prefix/);
  assert.match(regs.warnings.join('\n'), /"ops": duplicate/);
});

test('identifier register rows are validated', () => {
  const regs = loadRegisters(tmpRegisters(
    ['ex,Example,yes,,,,,', 'lab,Lab,no,,,,,'],
    [
      'lab,BB-007,Broker,lab-notes,https://l.org/broker,',
      'zzz,BB-001,x,y,https://z.org,',
      'ex,BB-001,x,y,https://e.org,',
      'lab,bad,x,y,https://l.org,',
      'lab,BB-008,x,y,/relative,',
      'lab,BB-007,again,y,https://l.org/again,',
    ],
  ));
  assert.deepEqual([...regs.ids.keys()], ['lab:BB-007']);
  assert.equal(regs.warnings.length, 5);
});

test('resolution order', () => {
  const regs = loadRegisters({namespaces: reg('identifier-namespaces.csv'), external: reg('external-identifiers.csv'), schemes: reg('identifier-schemes.csv')});
  assert.deepEqual(regs.warnings, []);
  const local = (id) => (id === 'BB-001' ? '/blocks/bb-001' : null);
  assert.equal(regs.resolve('ex', 'BB-001', local).url, '/blocks/bb-001');
  assert.match(regs.resolve('ex', 'BB-404', local).problem, /not an identifier this catalogue publishes/);
  assert.equal(regs.resolve('ops', 'BB-024').url, 'https://ops.example.org/architecture/id/BB-024/');
  assert.equal(regs.resolve('ops', 'BB-024').title, 'BB-024 in Operations Platform');
  const lab = regs.resolve('lab', 'BB-007');
  assert.equal(lab.url, 'https://lab.example.org/notes/message-broker');
  assert.equal(lab.title, 'Message broker (lab-notes)');
  assert.match(regs.resolve('lab', 'BB-099').problem, /has no URL/);
  assert.match(regs.resolve('nope', 'BB-001').problem, /not a registered namespace/);
});

test('bindings and the local map load from the workspace', () => {
  const b = readBindings(EXAMPLE);
  assert.equal(b.namespaces, '../registers/identifier-namespaces.csv');
  assert.equal(b.base, path.join(EXAMPLE, '.agents'));
  assert.deepEqual(b.scan, ['../docs']);
  assert.equal(loadLocalMap(EXAMPLE, b).get('PAT-001'), 'patterns/pat-001/');
});

function para(...children) {
  return {type: 'root', children: [{type: 'paragraph', children}]};
}

test('remark plugin links text and link targets, and leaves the rest alone', () => {
  const warnings = [];
  const plugin = remarkXref({
    root: EXAMPLE,
    namespaces: 'registers/identifier-namespaces.csv',
    external: 'registers/external-identifiers.csv',
    localMap: () => new Map([['BB-001', '/blocks/bb-001']]),
    onWarn: (m) => warnings.push(m),
  });
  const tree = para(
    {type: 'text', value: 'See ops:BB-024, ex:BB-001, BB-001 bare, lab:BB-099, note:BB-1 and '},
    {type: 'link', url: 'lab:BB-007', children: [{type: 'text', value: 'the broker'}]},
    {type: 'text', value: ' and '},
    {type: 'link', url: 'lab:BB-404', children: [{type: 'text', value: 'a missing one'}]},
    {type: 'inlineCode', value: 'ops:BB-024'},
  );
  plugin(tree, {path: 'page.md'});
  const kids = tree.children[0].children;
  const links = kids.filter((k) => k.type === 'link');
  assert.deepEqual(links.map((l) => l.url), [
    'https://ops.example.org/architecture/id/BB-024/',
    '/blocks/bb-001',
    'https://lab.example.org/notes/message-broker',
  ]);
  assert.equal(links[2].title, 'Message broker (lab-notes)');
  assert.ok(kids.some((k) => k.type === 'text' && k.value.includes('BB-001 bare, lab:BB-099, note:BB-1')));
  assert.ok(kids.some((k) => k.type === 'text' && k.value === 'a missing one'), 'an unresolved link keeps its text');
  assert.equal(kids.at(-1).type, 'inlineCode');
  assert.equal(warnings.length, 2);
});

test('remark plugin rejoins a reference split into a text directive', () => {
  const plugin = remarkXref({root: EXAMPLE, namespaces: 'registers/identifier-namespaces.csv', onWarn: () => {}});
  const tree = para(
    {type: 'text', value: 'Uses ops'},
    {type: 'textDirective', name: 'BB-024', attributes: {}, children: []},
    {type: 'text', value: ' for sign-in.'},
  );
  plugin(tree, {});
  const kids = tree.children[0].children;
  assert.equal(kids[1].type, 'link');
  assert.equal(kids[1].children[0].value, 'ops:BB-024');
  assert.equal(kids[2].value, ' for sign-in.');
});

test('id routes write redirects and the manifest', () => {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'xref-out-'));
  const regs = loadRegisters({namespaces: reg('identifier-namespaces.csv')});
  const {manifest, pages} = writeIdRoutes({
    outDir, baseUrl: '/catalogue/', map: new Map([['BB-001', '/blocks/bb-001'], ['PAT-001', '/patterns/pat-001#scenarios'], ['bad id', '/x']]),
    self: regs.self, siteName: 'x', siteUrl: 'x',
  });
  assert.equal(pages, 4);
  assert.deepEqual(manifest.ids, {'BB-001': 'blocks/bb-001/', 'PAT-001': 'patterns/pat-001/#scenarios'});
  assert.equal(manifest.namespace, 'ex');
  assert.match(fs.readFileSync(path.join(outDir, 'id', 'bb-001', 'index.html'), 'utf8'), /url=\/catalogue\/blocks\/bb-001\//);
  assert.equal(pagePath('/'), '');
});

test('a file-aware local resolver gets the page and may set the tooltip', () => {
  const seen = [];
  const plugin = remarkXref({
    root: EXAMPLE,
    namespaces: 'registers/identifier-namespaces.csv',
    localUrlFor: (id, file) => { seen.push(file.path); return {url: `../blocks/${id}.md`, title: 'Intake gateway'}; },
    onWarn: () => {},
  });
  const tree = para({type: 'text', value: 'See ex:BB-001.'});
  plugin(tree, {path: 'docs/page.md'});
  const link = tree.children[0].children[1];
  assert.equal(link.url, '../blocks/BB-001.md');
  assert.equal(link.title, 'Intake gateway');
  assert.deepEqual(seen, ['docs/page.md']);
});

test('id routes follow the docs plugin routes when localMap asks for them', async () => {
  const allContent = {'docusaurus-plugin-content-docs': {default: {loadedVersions: [{docs: [
    {source: '@site/blocks/bb-001.md', permalink: '/catalogue/blocks/intake/'},
  ]}]}}};
  assert.equal(docRoutes(allContent).get('blocks/bb-001.md'), '/catalogue/blocks/intake/');
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'xref-routes-'));
  const plugin = idRoutesPlugin(
    {siteConfig: {baseUrl: '/catalogue/', url: 'https://example.org', title: 'x'}, siteDir: EXAMPLE},
    {localMap: ({routes}) => new Map([['BB-001', routes.get('blocks/bb-001.md')]])},
  );
  const log = console.log;
  console.log = () => {};
  try {
    await plugin.allContentLoaded({allContent});
    await plugin.postBuild({outDir});
  } finally {
    console.log = log;
  }
  const manifest = JSON.parse(fs.readFileSync(path.join(outDir, 'id', 'index.json'), 'utf8'));
  assert.deepEqual(manifest.ids, {'BB-001': 'blocks/intake/'});
  assert.match(fs.readFileSync(path.join(outDir, 'id', 'BB-001', 'index.html'), 'utf8'), /url=\/catalogue\/blocks\/intake\//);
});

test('check ignores code and reports what cannot resolve', async () => {
  assert.equal(stripCode('a `lab:BB-1` b\n```\nlab:BB-2\n```\nc').includes('lab:'), false);
  const cfg = configure({root: EXAMPLE});
  const lines = [];
  assert.equal(await check(cfg, {offline: true, log: (l) => lines.push(l)}), 0);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'xref-docs-'));
  fs.writeFileSync(path.join(dir, 'p.md'), 'ex:BB-404 and lab:BB-099 and lab:BB-007\n');
  const bad = configure({root: EXAMPLE});
  bad.bindings.scan = [dir];
  const out = [];
  assert.equal(await check(bad, {offline: true, log: (l) => out.push(l)}), 2);
  assert.match(out.join('\n'), /ex:BB-404 is not an identifier this catalogue publishes/);
  assert.match(out.join('\n'), /lab:BB-099 has no URL/);
});

// ------------------------------------------------------------------ the local register

function tmpRegister() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'xref-register-'));
  const write = (rel, text) => {
    fs.mkdirSync(path.dirname(path.join(dir, rel)), {recursive: true});
    fs.writeFileSync(path.join(dir, rel), text);
  };
  write('docs/patterns/integration/PAT-001-order-intake/index.md', '# PAT-001 Order intake\n');
  write('docs/patterns/platform/PAT-002-event-backbone/index.md', '# PAT-002 Event backbone\n');
  write('docs/guide.md', 'See PAT-001.\n');
  write('registers/catalogue.csv', [
    'id,type,name,status,path,url,summary',
    'PAT-001,pattern,Order intake,Approved,../docs/patterns/integration/PAT-001-order-intake,,"Accepts orders, all channels"',
    'PAT-002,pattern,Event backbone,Draft,../docs/patterns/platform/PAT-002-event-backbone/index.md,,',
    'PAT-003,pattern,Moved away,Draft,../docs/patterns/gone/PAT-003-x,,',
    'UC-001,use-case,Track an order,Draft,,https://wiki.example.org/uc-001,',
  ].join('\n') + '\n');
  return dir;
}

test('the register is a local map, for the CLI', () => {
  const dir = tmpRegister();
  const map = registerToMap(path.join(dir, 'registers', 'catalogue.csv'));
  assert.deepEqual([...map.keys()], ['PAT-001', 'PAT-002', 'PAT-003', 'UC-001']);
  assert.equal(map.get('UC-001'), 'https://wiki.example.org/uc-001');
  fs.mkdirSync(path.join(dir, '.agents'));
  fs.writeFileSync(path.join(dir, '.agents', 'skill-bindings.toml'),
    '[suite.cross-reference]\nnamespaces = "../ns.csv"\nlocalRegister = "../registers/catalogue.csv"\n');
  assert.equal(loadLocalMap(dir, readBindings(dir)).size, 4);
});

test('fromRegister links a page to the file relative to it, and url wins', () => {
  const dir = tmpRegister();
  const local = fromRegister('registers/catalogue.csv', {root: dir});
  assert.deepEqual(local.localUrlFor('PAT-001', {path: path.join(dir, 'docs', 'guide.md')}),
    {url: './patterns/integration/PAT-001-order-intake/index.md', title: 'PAT-001 Order intake'});
  assert.equal(local.localUrlFor('PAT-002', {path: path.join(dir, 'docs', 'patterns', 'integration', 'PAT-001-order-intake', 'index.md')}).url,
    '../../platform/PAT-002-event-backbone/index.md');
  assert.equal(local.localUrlFor('PAT-003', {path: path.join(dir, 'docs', 'guide.md')}), null, 'a path that names nothing');
  assert.equal(local.localUrlFor('UC-001', {}).url, 'https://wiki.example.org/uc-001');
  assert.equal(local.localUrlFor('PAT-001', {path: path.join(dir, 'docs/patterns/integration/PAT-001-order-intake/index.md')}), null, 'never the page itself');
  const routes = new Map([['docs/patterns/integration/PAT-001-order-intake/index.md', '/patterns/order-intake/']]);
  assert.deepEqual([...local.localMap({routes})], [
    ['PAT-001', '/patterns/order-intake/'],
    ['UC-001', 'https://wiki.example.org/uc-001'],
  ]);
});

test('bare identifiers link when asked, only when known, and never in a heading', () => {
  const dir = tmpRegister();
  const local = fromRegister('registers/catalogue.csv', {root: dir});
  const warnings = [];
  const plugin = remarkXref({
    root: EXAMPLE,
    namespaces: 'registers/identifier-namespaces.csv',
    localUrlFor: local.localUrlFor,
    bare: true,
    onWarn: (m) => warnings.push(m),
  });
  const tree = {type: 'root', children: [
    {type: 'heading', depth: 1, children: [{type: 'text', value: 'PAT-001 in a heading'}]},
    {type: 'paragraph', children: [{type: 'text', value: 'PAT-001, ISO-9001, x-PAT-002, ex:PAT-002 and ops:BB-024.'}]},
  ]};
  plugin(tree, {path: path.join(dir, 'docs', 'guide.md')});
  assert.equal(tree.children[0].children.length, 1, 'the heading is untouched');
  const links = tree.children[1].children.filter((k) => k.type === 'link');
  assert.deepEqual(links.map((l) => l.children[0].value), ['PAT-001', 'ex:PAT-002', 'ops:BB-024']);
  assert.equal(links[0].title, 'PAT-001 Order intake');
  assert.deepEqual(warnings, []);
  // Without the option a bare identifier stays text, as before.
  const off = remarkXref({root: EXAMPLE, namespaces: 'registers/identifier-namespaces.csv', localUrlFor: local.localUrlFor, onWarn: () => {}});
  const t2 = para({type: 'text', value: 'PAT-001 here'});
  off(t2, {path: path.join(dir, 'docs', 'guide.md')});
  assert.equal(t2.children[0].children.length, 1);
});
