#!/usr/bin/env node
// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

const HELP = `cross-reference: check and resolve cross-catalogue identifier references (ops:ABB-024).

Run from the workspace root. Paths come from [suite.cross-reference] in
.agents/skill-bindings.toml, relative to that file; a flag overrides its binding, relative
to the working directory.

  node xref.cjs validate             check the registers; exit 1 if any row is skipped
  node xref.cjs list                 the registered namespaces and identifiers
  node xref.cjs resolve <ref>...     print the URL each reference links to
  node xref.cjs check [--offline]    check every reference in the Markdown files

check reports a reference this catalogue does not publish, or that no URL can be built
for, as an error. Another catalogue's references are checked against its manifest
(base_url + manifest); an unreachable site is reported and skipped. --offline checks
only this catalogue's own references, and identifiers in the identifier register.
Fenced and inline code are ignored, so examples in documentation are never checked.

Flags: --root <dir>  --bindings <file>  --namespaces <csv>  --external <csv>
       --schemes <csv>  --local-manifest <json>  --local-map <module>  --json
Exit 0: clean. Exit 1: problems. Exit 2: usage or configuration error.`;

const fs = require('fs');
const path = require('path');
const {loadRegisters, referenceRegex} = require('./lib/registers.cjs');
const {readBindings, loadLocalMap, registerPaths, bindingPath, BINDINGS} = require('./lib/config.cjs');

const DEFAULT_SKIP = ['node_modules', 'build', 'dist', '.docusaurus'];

function parseArgs(argv) {
  const out = {_: [], flags: {}};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--offline' || a === '--json' || a === '-h' || a === '--help') out.flags[a.replace(/^-+/, '')] = true;
    else if (a.startsWith('--')) out.flags[a.slice(2)] = argv[++i];
    else out._.push(a);
  }
  return out;
}

function configure(flags) {
  const root = path.resolve(flags.root || process.cwd());
  const b = readBindings(root, flags.bindings || BINDINGS);
  // A flag is relative to the working directory, so make it absolute before it meets base.
  for (const [flag, key] of [['namespaces', 'namespaces'], ['external', 'external'], ['schemes', 'schemes'],
    ['local-manifest', 'localManifest'], ['local-map', 'localMap']]) {
    if (flags[flag]) b[key] = path.resolve(flags[flag]);
  }
  if (!b.namespaces) {
    const e = new Error(`no namespace register: bind namespaces in [suite.cross-reference] of ${flags.bindings || BINDINGS}, or pass --namespaces`);
    e.usage = true;
    throw e;
  }
  return {root, bindings: b, regs: loadRegisters(registerPaths(root, b))};
}

/** Markdown with fenced code blocks and inline code blanked out, keeping line breaks. */
function stripCode(text) {
  return text
    .replace(/^(\s*)(```|~~~)[^\n]*\n[\s\S]*?^\1\2[^\n]*$/gm, (m) => m.replace(/[^\n]/g, ' '))
    .replace(/(`+)[^`\n]+?\1/g, (m) => ' '.repeat(m.length));
}

function walk(dir, skip, out = []) {
  for (const e of fs.readdirSync(dir, {withFileTypes: true})) {
    if (e.name.startsWith('.') || skip.has(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, skip, out);
    else if (/\.mdx?$/.test(e.name)) out.push(p);
  }
  return out;
}

/** namespace -> id -> Set of files, for every reference in the scanned Markdown. */
function collectRefs(root, bindings, regs) {
  const re = referenceRegex(regs.namespaces.keys());
  const refs = new Map();
  if (!re) return refs;
  const skip = new Set([...DEFAULT_SKIP, ...(bindings.skip || [])]);
  const dirs = bindings.scan && bindings.scan.length ? bindings.scan.map((d) => bindingPath(root, bindings, d)) : [root];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const file of walk(dir, skip)) {
      let text;
      try { text = stripCode(fs.readFileSync(file, 'utf8')); } catch { continue; }
      const rel = path.relative(root, file).split(path.sep).join('/');
      for (const m of text.matchAll(re)) {
        if (!refs.has(m[1])) refs.set(m[1], new Map());
        const ids = refs.get(m[1]);
        if (!ids.has(m[2])) ids.set(m[2], new Set());
        ids.get(m[2]).add(rel);
      }
    }
  }
  return refs;
}

async function fetchManifest(ns) {
  const url = new URL(ns.manifest, ns.baseUrl).href;
  const res = await fetch(url, {signal: AbortSignal.timeout(15000)});
  if (!res.ok) throw new Error(`${res.status} from ${url}`);
  const json = await res.json();
  return new Set(Object.keys(json.ids || {}));
}

async function check({root, bindings, regs}, {offline, log = console.log}) {
  const refs = collectRefs(root, bindings, regs);
  let errors = 0;
  let total = 0;
  let localIds = null;
  const where = (files) => [...files].join(', ');
  for (const [name, allIds] of refs) {
    const ns = regs.namespaces.get(name);
    total += allIds.size;
    if (ns.self) {
      if (!localIds) localIds = loadLocalMap(root, bindings);
      for (const [id, files] of allIds) {
        if (localIds.has(id)) continue;
        errors += 1;
        log(`  ERROR ${name}:${id} is not an identifier this catalogue publishes; referenced in ${where(files)}`);
      }
      continue;
    }
    // Registered one by one in the identifier register: known without a manifest.
    const ids = new Map([...allIds].filter(([id]) => !regs.entry(name, id)));
    if (!ids.size) continue;
    if (!ns.baseUrl) {
      for (const [id, files] of ids) {
        errors += 1;
        log(`  ERROR ${name}:${id} has no URL: not in the identifier register and ${name} has no base_url; referenced in ${where(files)}`);
      }
      continue;
    }
    if (offline) { log(`  skip  ${name}: ${ids.size} identifiers not checked (--offline)`); continue; }
    if (!ns.manifest) { log(`  skip  ${name}: no manifest registered, ${ids.size} identifiers not checked`); continue; }
    let known;
    try {
      known = await fetchManifest(ns);
    } catch (e) {
      log(`  skip  ${name}: manifest unreachable (${e.message}), ${ids.size} identifiers not checked`);
      continue;
    }
    for (const [id, files] of ids) {
      if (known.has(id)) continue;
      errors += 1;
      log(`  ERROR ${name}:${id} is not published by ${ns.name}; referenced in ${where(files)}`);
    }
  }
  log(`\nreferences: ${total} identifiers across ${refs.size} namespaces\nerrors: ${errors}`);
  return errors;
}

async function main(argv) {
  const {_: [cmd, ...rest], flags} = parseArgs(argv);
  if (!cmd || flags.h || flags.help) { console.log(HELP); return cmd ? 0 : 2; }
  let cfg;
  try { cfg = configure(flags); } catch (e) { console.error(e.message); return 2; }
  const {regs} = cfg;
  if (cmd === 'validate') {
    regs.warnings.forEach((w) => console.log(`  ERROR ${w}`));
    console.log(`namespaces: ${regs.namespaces.size}, registered identifiers: ${regs.ids.size}, problems: ${regs.warnings.length}`);
    return regs.warnings.length ? 1 : 0;
  }
  regs.warnings.forEach((w) => console.warn(`  warn  ${w}`));
  if (cmd === 'list') {
    if (flags.json) {
      console.log(JSON.stringify({namespaces: [...regs.namespaces.values()], identifiers: [...regs.ids.values()]}, null, 2));
      return 0;
    }
    for (const ns of regs.namespaces.values()) {
      console.log(`${ns.namespace.padEnd(7)}${ns.self ? 'self ' : '     '}${ns.name}${ns.baseUrl ? `  ${ns.baseUrl}` : ''}`);
    }
    for (const e of regs.ids.values()) console.log(`  ${e.namespace}:${e.id}  ${e.name || ''}  ${e.url}`);
    return 0;
  }
  if (cmd === 'resolve') {
    if (!rest.length) { console.error('usage: xref.cjs resolve <namespace:ID>...'); return 2; }
    let localIds = null;
    const localUrlFor = (id) => {
      if (!localIds) localIds = loadLocalMap(cfg.root, cfg.bindings);
      return localIds.get(id) || null;
    };
    let bad = 0;
    for (const ref of rest) {
      const m = /^([a-z][a-z0-9]*):(.+)$/.exec(ref);
      const r = m ? regs.resolve(m[1], m[2], localUrlFor) : {problem: `${ref} is not of the form namespace:ID`};
      if (r.url) console.log(`${ref}\t${r.url}`);
      else { bad += 1; console.log(`${ref}\tunresolved: ${r.problem}`); }
    }
    return bad ? 1 : 0;
  }
  if (cmd === 'check') {
    try { return (await check(cfg, {offline: flags.offline})) ? 1 : 0; } catch (e) { console.error(e.message); return 2; }
  }
  console.error(`unknown command ${cmd}\n\n${HELP}`);
  return 2;
}

if (require.main === module) main(process.argv.slice(2)).then((code) => process.exit(code));

module.exports = {main, check, collectRefs, stripCode, configure};
