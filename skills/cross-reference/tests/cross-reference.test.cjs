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
const {writeIdRoutes, pagePath} = require('../scripts/docusaurus/id-routes.cjs');
const {check, configure, stripCode} = require('../scripts/xref.cjs');

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
