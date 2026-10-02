// SPDX-FileCopyrightText: 2026 Dermot O'Brien
// SPDX-License-Identifier: Apache-2.0
'use strict';

/**
 * Docusaurus plugin: a stable URL for every identifier the catalogue publishes.
 *
 *   <baseUrl>id/ABB-024/     redirects to the identifier's page, wherever it lives
 *   <baseUrl>id/abb-024/     the same, for a reader typing it in lower case
 *   <baseUrl>id/index.json   the identifier manifest: every identifier and its page
 *
 * Pages move; an identifier does not. Other catalogues link to {base_url}id/{id}/, so they
 * never need a page's path, and read id/index.json to check their references. Redirects
 * are static HTML written in postBuild, so they work on any static host.
 *
 * Options, in docusaurus.config.js:
 *
 *   plugins: [[require.resolve('<skills>/cross-reference/scripts/docusaurus/id-routes.cjs'), {
 *     localMap: () => new Map([['ABB-024', '/abbs/abb-024']]),   // required: id -> site path
 *     namespaces: 'registers/identifier-namespaces.csv',          // optional: names the manifest
 *   }]]
 *
 * localMap is called after every plugin has loaded its content, with {routes}: a Map of
 * each doc's source file, relative to the site directory, to its permalink. A catalogue that
 * knows which file holds each identifier can return routes.get(file), so the redirects
 * follow the docs plugin's own routes, slugs included. A permalink that starts with the
 * site's baseUrl is fine.
 */

const fs = require('fs');
const path = require('path');
const {loadRegisters, DEFAULT_TEMPLATE} = require('../lib/registers.cjs');
const {toMap} = require('../lib/config.cjs');

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function redirectHtml(target, id) {
  const t = escapeHtml(target);
  return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>${escapeHtml(id)}</title>
    <meta http-equiv="refresh" content="0; url=${t}" />
    <link rel="canonical" href="${t}" />
    <meta name="robots" content="noindex" />
    <script>window.location.replace(${JSON.stringify(target)} + window.location.hash);</script>
  </head>
  <body>
    <p>${escapeHtml(id)} is at <a href="${t}">${t}</a>.</p>
  </body>
</html>
`;
}

/** A site path from the map, as a path under baseUrl with a trailing slash before any anchor. */
function pagePath(p) {
  const [route, anchor] = String(p).replace(/^\//, '').split('#');
  const withSlash = route === '' || route.endsWith('/') ? route : `${route}/`;
  return anchor ? `${withSlash}#${anchor}` : withSlash;
}

/** Write the redirects and the manifest into outDir. Returns the manifest. Exported for tests. */
function writeIdRoutes({outDir, baseUrl, map, self, siteName, siteUrl}) {
  const ids = {};
  let pages = 0;
  for (const [id, p] of [...map.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    // Identifiers become folder names: keep to the characters an identifier uses.
    if (!p || !/^[A-Za-z0-9][A-Za-z0-9.-]*$/.test(id)) continue;
    const route = baseUrl !== '/' && String(p).startsWith(baseUrl) ? String(p).slice(baseUrl.length) : p;
    const rel = pagePath(route);
    ids[id] = rel;
    for (const slug of new Set([id, id.toLowerCase()])) {
      const dir = path.join(outDir, 'id', slug);
      fs.mkdirSync(dir, {recursive: true});
      fs.writeFileSync(path.join(dir, 'index.html'), redirectHtml(`${baseUrl}${rel}`, id));
      pages += 1;
    }
  }
  const manifest = {
    $comment: 'Identifiers this site publishes. A page is at base_url + the path given; {base_url}id/{id}/ always redirects to it.',
    namespace: self ? self.namespace : null,
    name: self ? self.name : siteName,
    base_url: self && self.baseUrl ? self.baseUrl : siteUrl,
    url_template: DEFAULT_TEMPLATE,
    count: Object.keys(ids).length,
    ids,
  };
  fs.mkdirSync(path.join(outDir, 'id'), {recursive: true});
  fs.writeFileSync(path.join(outDir, 'id', 'index.json'), `${JSON.stringify(manifest, null, 2)}\n`);
  return {manifest, pages};
}

/** Each doc's source file, relative to the site directory, to its permalink. */
function docRoutes(allContent) {
  const routes = new Map();
  const docs = (allContent && allContent['docusaurus-plugin-content-docs']) || {};
  for (const instance of Object.values(docs)) {
    for (const version of (instance && instance.loadedVersions) || []) {
      for (const doc of version.docs || []) routes.set(doc.source.replace(/^@site\//, ''), doc.permalink);
    }
  }
  return routes;
}

module.exports = function idRoutesPlugin(context, options = {}) {
  const {siteConfig} = context;
  let routes = new Map();
  return {
    name: 'cross-reference-id-routes',
    async allContentLoaded({allContent}) {
      routes = docRoutes(allContent);
    },
    async postBuild({outDir}) {
      if (typeof options.localMap === 'undefined') throw new Error('[cross-reference] id-routes needs a localMap option');
      const map = toMap(typeof options.localMap === 'function' ? options.localMap({routes}) : options.localMap);
      const root = options.root || context.siteDir;
      const regs = options.namespaces ? loadRegisters({namespaces: path.resolve(root, options.namespaces)}) : null;
      const {manifest, pages} = writeIdRoutes({
        outDir,
        baseUrl: siteConfig.baseUrl,
        map,
        self: regs ? regs.self : null,
        siteName: siteConfig.title,
        siteUrl: `${siteConfig.url}${siteConfig.baseUrl}`,
      });
      console.log(`[cross-reference] wrote ${pages} identifier redirects and id/index.json (${manifest.count} identifiers)`);
    },
  };
};
module.exports.writeIdRoutes = writeIdRoutes;
module.exports.pagePath = pagePath;
module.exports.docRoutes = docRoutes;
