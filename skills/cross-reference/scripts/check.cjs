#!/usr/bin/env node
// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * Post-install check for the cross-reference skill (DD-11 of AI-Assisted Work).
 *
 * Run from the workspace root; takes no arguments:
 *
 *   node scripts/check.cjs
 *
 * Checks [suite.cross-reference] in .agents/skill-bindings.toml against inputs.toml: the
 * namespace register is bound and exists, every register row passes the rules, one row is
 * this catalogue's own, and the catalogue's identifier map loads. Offline and read-only.
 *
 * Exit 0: correct (warnings may be printed). Exit 1: problems, one line each.
 * Exit 2: usage or environment error.
 */

const fs = require('fs');
const path = require('path');
const {loadRegisters} = require('./lib/registers.cjs');
const {readBindings, loadLocalMap, registerPaths, BINDINGS} = require('./lib/config.cjs');

const [major] = process.versions.node.split('.').map(Number);
if (major < 18) { console.error(`Node ${process.versions.node} is too old: cross-reference needs 18 or newer.`); process.exit(2); }
if (process.argv.length > 2) { console.error('usage: check.cjs   (run from the workspace root; takes no arguments)'); process.exit(2); }

const root = process.cwd();
const problems = [];
const warnings = [];
const b = readBindings(root);

if (!fs.existsSync(path.join(root, BINDINGS))) {
  problems.push(`${BINDINGS} not found: add a [suite.cross-reference] table with at least namespaces = "<path to the namespace register>"`);
} else if (!b.namespaces) {
  problems.push(`[suite.cross-reference] in ${BINDINGS} does not bind namespaces: set it to the path of the namespace register`);
}

if (b.namespaces) {
  const paths = registerPaths(root, b);
  for (const [key, p] of Object.entries(paths)) {
    if (p && !fs.existsSync(p)) problems.push(`${key} = "${b[key]}" does not exist`);
  }
  if (fs.existsSync(paths.namespaces)) {
    const regs = loadRegisters(paths);
    problems.push(...regs.warnings);
    if (!regs.self) warnings.push('no row in the namespace register has self = yes, so references in this catalogue\'s own code are not checked');
  }
  if (!b.localManifest && !b.localMap) {
    warnings.push('neither localManifest nor localMap is bound, so this catalogue\'s own references cannot be checked');
  } else {
    try {
      const n = loadLocalMap(root, b).size;
      if (!n) warnings.push('the catalogue\'s identifier map is empty');
    } catch (e) {
      problems.push(`the catalogue's identifier map did not load: ${e.message}`);
    }
  }
}

warnings.forEach((w) => console.log(`warning: ${w}`));
problems.forEach((p) => console.log(`problem: ${p}`));
console.log(problems.length ? `cross-reference: ${problems.length} problems` : 'cross-reference: ok');
process.exit(problems.length ? 1 : 0);
