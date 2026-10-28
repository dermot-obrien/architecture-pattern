# SPDX-License-Identifier: Apache-2.0
"""Redraw a unit as a plain draw.io diagram, where its boxes were drawn.

A source with geometry but no draw.io of its own, a plain SVG, or an image whose boxes
the agent placed, is redrawn here: each box where it was, each line between its boxes,
with no identifiers. The draft then adopts it with `model sync --adopt`, exactly as it
adopts a draw.io source, so the document's diagram keeps the source's layout rather
than a generated grid.
"""
from __future__ import annotations

import html

BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#25303F;fontColor=#25303F;"
GROUP = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;dashed=1;strokeColor=#8A94A3;verticalAlign=top;align=left;spacingLeft=8;"
EDGE = "edgeStyle=none;rounded=0;html=1;endArrow=classic;"


def has_geometry(u) -> bool:
    return bool(u["boxes"]) and all(len(b.get("geom") or []) == 4 for b in u["boxes"])


def build(u) -> str:
    def esc(s):
        return html.escape(str(s or ""), quote=True)

    cells = ['<mxCell id="0" />', '<mxCell id="1" value="Structure" parent="0" />']
    groups = {}
    for b in u["boxes"]:
        c = b.get("container")
        if c:
            x, y, w, h = b["geom"]
            g = groups.setdefault(c, [x, y, x + w, y + h])
            g[0], g[1] = min(g[0], x), min(g[1], y)
            g[2], g[3] = max(g[2], x + w), max(g[3], y + h)
    for i, (name, (x0, y0, x1, y1)) in enumerate(sorted(groups.items()), 1):
        cells.append(f'<mxCell id="g{i}" value="{esc(name)}" style="{GROUP}" vertex="1" parent="1">'
                     f'<mxGeometry x="{x0 - 20:g}" y="{y0 - 36:g}" width="{x1 - x0 + 40:g}" '
                     f'height="{y1 - y0 + 56:g}" as="geometry" /></mxCell>')
    for b in u["boxes"]:
        x, y, w, h = b["geom"]
        w, h = max(w, 120), max(h, 50)
        cells.append(f'<mxCell id="v-{esc(b["key"])}" value="{esc(b["label"])}" style="{BOX}" '
                     f'vertex="1" parent="1"><mxGeometry x="{x:g}" y="{y:g}" width="{w:g}" '
                     f'height="{h:g}" as="geometry" /></mxCell>')
    for lk in u["links"]:
        style = EDGE if lk.get("directed", True) else EDGE.replace("endArrow=classic", "endArrow=none")
        cells.append(f'<mxCell id="e-{esc(lk["key"])}" value="{esc(lk.get("label"))}" style="{style}" '
                     f'edge="1" parent="1" source="v-{esc(lk["source"])}" target="v-{esc(lk["target"])}">'
                     '<mxGeometry relative="1" as="geometry" /></mxCell>')
    return ('<mxfile host="convert" compressed="false"><diagram id="page-1" name="Page-1">'
            '<mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" '
            'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1920" '
            'pageHeight="1080" math="0" shadow="0"><root>' + "".join(cells)
            + "</root></mxGraphModel></diagram></mxfile>\n")
