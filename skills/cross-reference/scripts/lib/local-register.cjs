// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * This catalogue's own identifiers from its register: the CSV the pattern skill numbers
 * patterns and use cases from, `id,type,name,status,path,url,summary`.
 *
 *   id     the identifier; else the first column
 *   url    its page, when the site's address cannot be found from its file; wins
 *   path   its folder or document, relative to the register
 *   name   the tooltip, after the identifier
 *
 * Every other column is ignored. A row with neither url nor path is still an identifier
 * this catalogue publishes, for `xref check`, but has nowhere to link.
 *
 * In docusaurus.config.js, one register serves both plugins:
 *
 *   const {fromRegister} = require('<skills>/cross-reference/scripts/lib/local-register.cjs');
 *   const local = fromRegister('registers/catalogue.csv');   // relative to the site directory
 *   remark-xref:  {..., localUrlFor: local.localUrlFor}
 *   id-routes:    {..., localMap: local.localMap}
 *
 * localUrlFor links to the identifier's Markdown file relative to the page being built,
 * which Docusaurus resolves and checks; localMap follows the docs plugin's routes to the
 * same file. A file outside the docs, or a row whose path names nothing, has no page.
 */

const fs = require('fs');
const path = require('path');
const {readCsv} = require('./registers.cjs');

const INDEX = ['index.md', 'index.mdx', 'README.md'];

/** The register's rows as [{id, name, url, file}], file absolute or ''. */
function readLocalRegister(file) {
  const abs = path.resolve(file);
  if (!fs.existsSync(abs)) throw new Error(`the register ${abs} does not exist`);
  const base = path.dirname(abs);
  const rows = readCsv(abs);
  const header = rows.length ? Object.keys(rows[0]) : [];
  const idKey = header.find((h) => h.toLowerCase() === 'id') || header[0];
  const col = (row, name) => {
    const k = Object.keys(row).find((h) => h.toLowerCase() === name);
    return k ? row[k] : '';
  };
  const out = [];
  for (const row of rows) {
    const id = (row[idKey] || '').trim();
    if (!id) continue;
    let target = '';
    const rel = col(row, 'path');
    if (rel) {
      const p = path.resolve(base, rel);
      if (fs.existsSync(p) && fs.statSync(p).isDirectory()) {
        const hit = INDEX.map((n) => path.join(p, n)).find((f) => fs.existsSync(f));
        target = hit || '';
      } else if (fs.existsSync(p)) {
        target = p;
      }
    }
    out.push({id, name: col(row, 'name'), url: col(row, 'url'), path: rel, file: target});
  }
  return out;
}

/** Identifier -> url, else the path as written, else ''. For the CLI, which needs only membership. */
function registerToMap(file) {
  return new Map(readLocalRegister(file).map((r) => [r.id, r.url || r.path || '']));
}

function toPosix(p) {
  return p.split(path.sep).join('/');
}

/**
 * The two options the Docusaurus plugins take, from one register. `file` is relative to
 * `root`, by default the working directory, which is the site directory in a build.
 */
function fromRegister(file, {root = process.cwd()} = {}) {
  let rows = null;
  const load = () => {
    if (!rows) rows = new Map(readLocalRegister(path.resolve(root, file)).map((r) => [r.id, r]));
    return rows;
  };
  const title = (r) => (r.name ? `${r.id} ${r.name}` : r.id);

  function localUrlFor(id, vfile) {
    const r = load().get(id);
    if (!r) return null;
    if (r.url) return {url: r.url, title: title(r)};
    if (!r.file || !vfile || !vfile.path) return null;
    if (path.resolve(root, vfile.path) === r.file) return null;   // the page itself
    let rel = toPosix(path.relative(path.dirname(vfile.path), r.file));
    if (!rel.startsWith('.')) rel = `./${rel}`;
    return {url: rel, title: title(r)};
  }

  function localMap({routes} = {}) {
    const out = new Map();
    for (const r of load().values()) {
      if (r.url) { out.set(r.id, r.url); continue; }
      if (!r.file || !routes) continue;
      const permalink = routes.get(toPosix(path.relative(root, r.file)));
      if (permalink) out.set(r.id, permalink);
    }
    return out;
  }

  return {localUrlFor, localMap};
}

module.exports = {readLocalRegister, registerToMap, fromRegister};
