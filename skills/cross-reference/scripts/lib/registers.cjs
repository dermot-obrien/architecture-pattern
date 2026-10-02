// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * Namespace and identifier registers: which catalogue owns an identifier, and its URL.
 *
 * A reference to another catalogue's identifier is a compact URI (W3C CURIE Syntax 1.0):
 *
 *   ops:ABB-024     namespace ops, local identifier ABB-024
 *
 * A bare ABB-024 always means the catalogue the page is in. The namespace register maps
 * each short code to its catalogue's site; the identifier register maps one identifier to
 * its exact page when the site's addresses can't be built from the identifier.
 *
 * Zero dependencies. Every function takes paths and returns data: nothing is read from a
 * fixed location, so the same code serves a Docusaurus plugin, a CLI and a test.
 */

const fs = require('fs');

const DEFAULT_TEMPLATE = '{base_url}id/{id}/';
const NAMESPACE_RE = /^[a-z][a-z0-9]{1,5}$/;
const ID_SOURCE = '[A-Z][A-Z0-9]*-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*';
const ID_RE = new RegExp(`^${ID_SOURCE}$`);

function parseCsvRow(line) {
  const fields = [];
  let i = 0;
  while (i <= line.length) {
    if (i === line.length) { fields.push(''); break; }
    if (line[i] === '"') {
      let val = '';
      i++;
      while (i < line.length) {
        if (line[i] === '"' && line[i + 1] === '"') { val += '"'; i += 2; }
        else if (line[i] === '"') { i++; break; }
        else { val += line[i]; i++; }
      }
      fields.push(val);
      if (line[i] === ',') i++;
    } else {
      const next = line.indexOf(',', i);
      if (next === -1) { fields.push(line.slice(i)); break; }
      fields.push(line.slice(i, next));
      i = next + 1;
    }
  }
  return fields;
}

/** Rows of a CSV file as objects keyed by the trimmed header. A missing file is no rows. */
function readCsv(file) {
  if (!file || !fs.existsSync(file)) return [];
  const lines = fs.readFileSync(file, 'utf-8').replace(/^﻿/, '').split(/\r?\n/).filter((l) => l.trim());
  if (!lines.length) return [];
  const header = parseCsvRow(lines[0]).map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const cells = parseCsvRow(line);
    return Object.fromEntries(header.map((h, i) => [h, (cells[i] || '').trim()]));
  });
}

/**
 * Load and validate the registers.
 *
 *   namespaces  path of the namespace register (namespace,name,self,base_url,url_template,manifest,owner,notes)
 *   external    optional path of the identifier register (namespace,id,name,repository,url,notes)
 *   schemes     optional path of a CSV with a `prefix` column: the catalogue's identifier
 *               prefixes, which a namespace code may not equal
 *   prefixes    optional extra prefixes, as an array
 *
 * Rows that break a rule are skipped, with a warning saying why. Returns an object with
 * the namespaces, the registered identifiers, the warnings and the lookups below.
 */
function loadRegisters({namespaces, external, schemes, prefixes = []} = {}) {
  const warnings = [];
  const reserved = new Set(prefixes.map((p) => String(p).toLowerCase()));
  for (const r of readCsv(schemes)) if (r.prefix) reserved.add(r.prefix.toLowerCase());

  const nsMap = new Map();
  for (const row of readCsv(namespaces)) {
    const code = row.namespace;
    const skip = (why) => warnings.push(`namespace register: skipped "${code}": ${why}`);
    if (!NAMESPACE_RE.test(code)) { skip('a code is 2 to 6 lower case letters or digits, starting with a letter'); continue; }
    if (reserved.has(code)) { skip('it is an identifier prefix, so it would read as a type'); continue; }
    if (nsMap.has(code)) { skip('duplicate'); continue; }
    const baseUrl = row.base_url && !row.base_url.endsWith('/') ? `${row.base_url}/` : (row.base_url || '');
    nsMap.set(code, {
      namespace: code,
      name: row.name || code,
      self: (row.self || '').toLowerCase() === 'yes',
      baseUrl,
      template: row.url_template || DEFAULT_TEMPLATE,
      manifest: row.manifest || '',
      owner: row.owner || '',
    });
  }
  const selves = [...nsMap.values()].filter((n) => n.self);
  if (selves.length > 1) warnings.push(`namespace register: ${selves.length} rows say self = yes; only ${selves[0].namespace} is used`);

  const ids = new Map();
  for (const row of readCsv(external)) {
    const key = `${row.namespace}:${row.id}`;
    const skip = (why) => warnings.push(`identifier register: skipped ${key}: ${why}`);
    const ns = nsMap.get(row.namespace);
    if (!ns) { skip(`${row.namespace} is not in the namespace register`); continue; }
    if (ns.self) { skip(`${row.namespace} is this catalogue, whose identifiers live in its own registers`); continue; }
    if (!ID_RE.test(row.id)) { skip('not an identifier of the form ABB-024'); continue; }
    if (!/^https?:\/\//.test(row.url)) { skip('url must be absolute (http or https)'); continue; }
    if (ids.has(key)) { skip('duplicate'); continue; }
    ids.set(key, {namespace: row.namespace, id: row.id, name: row.name, repository: row.repository, url: row.url});
  }

  const self = selves[0] || null;

  /** The registered row for an identifier in another catalogue, or null. */
  function entry(namespace, id) {
    return ids.get(`${namespace}:${id}`) || null;
  }

  /** URL of an identifier in another catalogue: its row, else the namespace template. Null when neither gives one. */
  function externalUrl(namespace, id) {
    const e = entry(namespace, id);
    if (e) return e.url;
    const ns = nsMap.get(namespace);
    if (!ns || ns.self || !ns.baseUrl) return null;
    return ns.template.replace('{base_url}', ns.baseUrl).replace('{id}', encodeURIComponent(id));
  }

  /** Tooltip for a link into another catalogue. */
  function titleFor(namespace, id) {
    const e = entry(namespace, id);
    if (e && e.name) return `${e.name} (${e.repository || namespace})`;
    const ns = nsMap.get(namespace);
    return ns && !ns.self ? `${id} in ${ns.name}` : null;
  }

  /**
   * Resolve a reference. localUrlFor(id) gives this catalogue's own page for an identifier:
   * a URL, or {url, title}, or null. Returns {url, title, problem}: url null and problem set
   * when it can't resolve.
   */
  function resolve(namespace, id, localUrlFor) {
    const ns = nsMap.get(namespace);
    if (!ns) return {url: null, title: null, problem: `${namespace} is not a registered namespace`};
    if (ns.self) {
      const found = localUrlFor ? localUrlFor(id) : null;
      const url = found && typeof found === 'object' ? found.url : found;
      return url ? {url, title: (found && found.title) || null, problem: null}
        : {url: null, title: null, problem: `${namespace}:${id} is not an identifier this catalogue publishes`};
    }
    const url = externalUrl(namespace, id);
    return url ? {url, title: titleFor(namespace, id), problem: null}
      : {url: null, title: null, problem: `${namespace}:${id} has no URL: register it in the identifier register or give ${namespace} a base_url`};
  }

  return {namespaces: nsMap, ids, warnings, self, entry, externalUrl, titleFor, resolve};
}

/** A regular expression matching a bare-text reference in any of the given codes, or null. */
function referenceRegex(codes) {
  const names = [...codes].sort((a, b) => b.length - a.length);
  return names.length ? new RegExp(`(?<![\\w/:.-])(${names.join('|')}):(${ID_SOURCE})`, 'g') : null;
}

module.exports = {
  loadRegisters, readCsv, parseCsvRow, referenceRegex,
  DEFAULT_TEMPLATE, NAMESPACE_RE, ID_RE, ID_SOURCE,
};
