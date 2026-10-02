// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * Remark plugin: turn cross-catalogue references into links.
 *
 *   [Identity Provider](ops:ABB-024)    a link whose target is a reference
 *   see ops:ABB-024                      bare text, linked as written
 *
 * In the catalogue's own namespace a reference links to the page inside this build, so the
 * build's link check covers it. In another namespace it links to that identifier's row in
 * the identifier register, or to the namespace's url_template ({base_url}id/{id}/ by
 * default), with a tooltip. Nothing is fetched while building. A code that isn't
 * registered is left alone, so ordinary text with a colon is never touched. A reference
 * that can't resolve stays as plain text, with a warning.
 *
 * Options, in docusaurus.config.js:
 *
 *   remarkPlugins: [[require('<skills>/cross-reference/scripts/docusaurus/remark-xref.cjs'), {
 *     namespaces: 'registers/identifier-namespaces.csv',   // required
 *     external: 'registers/external-identifiers.csv',      // optional
 *     schemes: 'registers/identifier-schemes.csv',         // optional, CSV with a prefix column
 *     localUrlFor: (id) => '/abbs/abb-024',                // or localMap: () => Map of id -> path
 *   }]]
 *
 * Paths are relative to `root`, by default the working directory. Put it before any
 * plugin that links bare identifiers, which then leaves the new links alone.
 */

const path = require('path');
const {loadRegisters, referenceRegex, ID_SOURCE} = require('../lib/registers.cjs');
const {toMap} = require('../lib/config.cjs');

const LINK_RE = new RegExp(`^([a-z][a-z0-9]*):(${ID_SOURCE})$`);
const SKIP_TYPES = new Set(['link', 'linkReference', 'code', 'inlineCode', 'html']);

function remarkXref(options = {}) {
  const root = options.root || process.cwd();
  const abs = (p) => (p ? path.resolve(root, p) : undefined);
  const warn = options.onWarn || ((m) => console.warn(`[cross-reference] ${m}`));
  let regs = options.registers || null;
  let localUrlFor = options.localUrlFor || null;
  let textRe;

  function setup() {
    if (regs && textRe !== undefined) return;
    if (!regs) {
      regs = loadRegisters({namespaces: abs(options.namespaces), external: abs(options.external), schemes: abs(options.schemes)});
      regs.warnings.forEach(warn);
    }
    if (!localUrlFor && options.localMap) {
      let map = null;
      localUrlFor = (id) => {
        if (!map) map = toMap(typeof options.localMap === 'function' ? options.localMap() : options.localMap);
        return map.get(id) || null;
      };
    }
    textRe = referenceRegex(regs.namespaces.keys());
  }

  function resolve(ns, id, file) {
    const r = regs.resolve(ns, id, localUrlFor);
    if (r.problem) warn(`${r.problem}${file && file.path ? ` (in ${file.path})` : ''}; left unlinked`);
    return r;
  }

  // Docusaurus parses Markdown directives, so in "ops:ABB-024" the ":ABB-024" arrives as a
  // text directive after a text node ending "ops". Where the text before a plain directive
  // (no label, no attributes) ends in a registered code, put the directive back as text and
  // merge it with its neighbours. Other directives are untouched.
  function rejoinDirectives(parent) {
    const kids = parent.children;
    for (let i = 1; i < kids.length; i++) {
      const d = kids[i];
      const prev = kids[i - 1];
      if (d.type !== 'textDirective' || prev.type !== 'text') continue;
      if ((d.children && d.children.length) || (d.attributes && Object.keys(d.attributes).length)) continue;
      const m = /(?:^|[^\w/:.-])([a-z][a-z0-9]*)$/.exec(prev.value);
      if (!m || !regs.namespaces.has(m[1])) continue;
      let value = `${prev.value}:${d.name}`;
      let remove = 2;
      if (kids[i + 1] && kids[i + 1].type === 'text') {
        value += kids[i + 1].value;
        remove = 3;
      }
      kids.splice(i - 1, remove, {type: 'text', value});
      i -= 1;
    }
  }

  return (tree, file) => {
    setup();
    if (!regs.namespaces.size) return;
    const queue = [tree];
    while (queue.length) {
      const parent = queue.shift();
      if (!parent || !Array.isArray(parent.children)) continue;
      rejoinDirectives(parent);
      let i = 0;
      while (i < parent.children.length) {
        const child = parent.children[i];

        if (child.type === 'link' && typeof child.url === 'string') {
          const m = LINK_RE.exec(child.url);
          if (m && regs.namespaces.has(m[1])) {
            const r = resolve(m[1], m[2], file);
            if (r.url) {
              child.url = r.url;
              if (!child.title && r.title) child.title = r.title;
            } else {
              // Unresolvable: keep the text, drop the link, so the build has no broken link.
              parent.children.splice(i, 1, ...child.children);
              continue;
            }
          }
        }

        if (child.type === 'text' && textRe) {
          textRe.lastIndex = 0;
          const parts = [];
          let last = 0;
          let m;
          while ((m = textRe.exec(child.value)) !== null) {
            const r = resolve(m[1], m[2], file);
            if (!r.url) continue;
            if (m.index > last) parts.push({type: 'text', value: child.value.slice(last, m.index)});
            const link = {type: 'link', url: r.url, children: [{type: 'text', value: m[0]}]};
            if (r.title) link.title = r.title;
            parts.push(link);
            last = m.index + m[0].length;
          }
          if (parts.length) {
            if (last < child.value.length) parts.push({type: 'text', value: child.value.slice(last)});
            parent.children.splice(i, 1, ...parts);
            i += parts.length;
            continue;
          }
        }

        if (!SKIP_TYPES.has(child.type) && Array.isArray(child.children)) queue.push(child);
        i++;
      }
    }
  };
}

module.exports = remarkXref;
