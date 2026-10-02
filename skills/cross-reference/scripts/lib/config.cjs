// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * The workspace's answer to inputs.toml: [suite.cross-reference] in
 * .agents/skill-bindings.toml, plus the catalogue's own identifier map.
 *
 * Reads only the subset of TOML a bindings table needs (key = "string", key = true,
 * key = ["a", "b"]), so the skill needs no TOML parser.
 *
 * A path in a bindings file is relative to the bindings file, as for every other skill, so
 * a path to the repository root's registers folder is "../registers/...". A path given on
 * the command line is relative to the working directory instead.
 */

const fs = require('fs');
const path = require('path');

const SUITE = 'cross-reference';
const BINDINGS = '.agents/skill-bindings.toml';

function parseValue(raw) {
  const v = raw.trim();
  if (v.startsWith('[')) {
    return [...v.matchAll(/"((?:[^"\\]|\\.)*)"|'([^']*)'/g)].map((m) => (m[1] !== undefined ? m[1] : m[2]));
  }
  if (v.startsWith('"')) return v.slice(1, v.lastIndexOf('"'));
  if (v.startsWith("'")) return v.slice(1, v.lastIndexOf("'"));
  if (v === 'true' || v === 'false') return v === 'true';
  return v.replace(/\s+#.*$/, '');
}

/**
 * The [suite.cross-reference] table of a bindings file, or {} when absent. The returned
 * object's non-enumerable `base` is the directory its paths are relative to.
 */
function readBindings(root, file = BINDINGS) {
  const p = path.resolve(root, file);
  const out = {};
  Object.defineProperty(out, 'base', {value: path.dirname(p), writable: true});
  if (!fs.existsSync(p)) return out;
  let inTable = false;
  for (const line of fs.readFileSync(p, 'utf-8').split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const header = /^\[([^\]]+)\]$/.exec(t);
    if (header) { inTable = header[1].trim() === `suite.${SUITE}`; continue; }
    if (!inTable) continue;
    const kv = /^([A-Za-z0-9_-]+)\s*=\s*(.+)$/.exec(t);
    if (kv) out[kv[1]] = parseValue(kv[2]);
  }
  return out;
}

/** Turn a Map, a plain object or a manifest ({ids: {...}}) into a Map of identifier -> page. */
function toMap(value) {
  if (value instanceof Map) return value;
  if (value && typeof value === 'object') return new Map(Object.entries(value.ids || value));
  return new Map();
}

/**
 * The catalogue's own identifiers and their pages, from whichever binding is set:
 *
 *   localManifest  a JSON file: {"ids": {"ABB-024": "abbs/abb-024/"}} or a flat object
 *   localMap       a CommonJS module exporting a function (or `localMapExport` naming one)
 *                  that returns a Map, an object or a manifest
 *
 * Named exports win over the module itself, since a remark plugin module is often a
 * function with the map builder attached. An empty Map when neither is bound.
 */
function loadLocalMap(root, bindings) {
  const base = bindings.base || root;
  if (bindings.localManifest) {
    const p = path.resolve(base, bindings.localManifest);
    return toMap(JSON.parse(fs.readFileSync(p, 'utf-8')));
  }
  if (bindings.localMap) {
    const mod = require(path.resolve(base, bindings.localMap));
    const name = bindings.localMapExport;
    const fn = name ? mod[name] : (mod.buildLinkMap || mod.localMap || mod.default || (typeof mod === 'function' ? mod : null));
    if (typeof fn !== 'function') throw new Error(`${bindings.localMap} exports no function${name ? ` named ${name}` : ''}`);
    return toMap(fn());
  }
  return new Map();
}

/** Register paths from bindings, resolved against the bindings file's directory. */
function registerPaths(root, bindings) {
  const abs = (p) => (p ? path.resolve(bindings.base || root, p) : undefined);
  return {namespaces: abs(bindings.namespaces), external: abs(bindings.external), schemes: abs(bindings.schemes)};
}

/** A path from bindings, resolved against the bindings file's directory. */
function bindingPath(root, bindings, p) {
  return path.resolve(bindings.base || root, p);
}

module.exports = {readBindings, loadLocalMap, registerPaths, bindingPath, toMap, SUITE, BINDINGS};
