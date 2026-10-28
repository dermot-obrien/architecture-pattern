# SPDX-License-Identifier: Apache-2.0
"""A plain SVG preview of a diagram's structure layer, for a machine without draw.io.

The pattern skill's publish step and model's animate need a current view of the
structure layer. Where draw.io desktop is installed, `model render` makes one; where it
is not, this draws one: every shape on the structure layer as a box with its label, and
every connector between two of them as a straight arrow with its label, framed exactly
by the shapes so the walkthrough's positions line up. It is then recorded with
`model stamp`. It is a preview, not a render: arrange the diagram in draw.io, then
render or export the view again.
"""
from __future__ import annotations

import html
import math

from . import drawio
from .unit import html_lines

STROKE, FILL, TEXT = "#25303F", "#FFFFFF", "#25303F"


def _wrap(text, width_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def _clip(box, toward):
    """The point where a line from the box's centre toward a point leaves the box."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    dx, dy = toward[0] - cx, toward[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else math.inf
    sy = (h / 2) / abs(dy) if dy else math.inf
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def build(drawio_text) -> tuple:
    """(svg text, structure layer name) for the first page of a diagram."""
    pages = drawio.parse_mxfile(drawio_text)
    if not pages:
        raise drawio.DrawioError("the diagram has no pages")
    cells = drawio.cells_of(pages[0][1])
    layers = [c for c in sorted(cells.values(), key=lambda c: c.order) if c.kind == "layer"]
    if not layers:
        raise drawio.DrawioError("the diagram has no layers")
    base = layers[0]
    memo = {}
    boxes, frame = {}, {}
    for c in sorted(cells.values(), key=lambda c: c.order):
        if c.kind != "vertex" or not c.geom:
            continue
        lay = drawio._layer_of(cells, c)
        if lay is None or lay.id != base.id:
            continue
        if c.attrs.get("scenario"):
            continue
        g = drawio._abs_geom(cells, c, memo)
        if g[2] <= 0 and g[3] <= 0:
            continue
        # The frame is every shape on the layer, as model animate measures it, an
        # edge's own label included; only shapes that are not labels are drawn.
        frame[c.id] = g
        parent = cells.get(c.parent)
        if parent is None or parent.kind != "edge":
            boxes[c.id] = g
    if not boxes:
        raise drawio.DrawioError("the structure layer has no shapes")
    x0 = min(b[0] for b in frame.values())
    y0 = min(b[1] for b in frame.values())
    x1 = max(b[0] + b[2] for b in frame.values())
    y1 = max(b[1] + b[3] for b in frame.values())
    W, H = x1 - x0, y1 - y0

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" '
           f'width="{W:g}" height="{H:g}" font-family="Helvetica, Arial, sans-serif">',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
           f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="{STROKE}"/>'
           '</marker></defs>',
           f'<rect x="0" y="0" width="{W:g}" height="{H:g}" fill="#FFFFFF"/>']
    # Containers first, so the boxes inside them draw on top.
    order = sorted(boxes, key=lambda cid: -(boxes[cid][2] * boxes[cid][3]))
    for cid in order:
        c = cells[cid]
        x, y, w, h = boxes[cid]
        x, y = x - x0, y - y0
        container = any(o != cid and boxes[o][0] >= boxes[cid][0] and boxes[o][1] >= boxes[cid][1]
                        and boxes[o][0] + boxes[o][2] <= boxes[cid][0] + boxes[cid][2]
                        and boxes[o][1] + boxes[o][3] <= boxes[cid][1] + boxes[cid][3]
                        for o in boxes)
        text_only = drawio._is_text(c) and not container
        lines = html_lines(c.value)
        if not text_only:
            fill = "none" if container else FILL
            if "ellipse" in c.words or c.pairs.get("shape") == "ellipse":
                out.append(f'<ellipse cx="{x + w / 2:g}" cy="{y + h / 2:g}" rx="{w / 2:g}" '
                           f'ry="{h / 2:g}" fill="{fill}" stroke="{STROKE}" stroke-width="1"/>')
            else:
                dash = ' stroke-dasharray="6 4"' if container else ""
                out.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="6" '
                           f'fill="{fill}" stroke="{STROKE}" stroke-width="1"{dash}/>')
        if not lines:
            continue
        wrapped = []
        for ln in lines:
            wrapped += _wrap(ln, max(int(w / 7.5), 6))
        size = 13 if not container else 12
        if container:
            ty = y + 16
            for ln in wrapped[:2]:
                out.append(f'<text x="{x + 8:g}" y="{ty:g}" font-size="{size}" fill="{TEXT}" '
                           f'font-weight="bold">{html.escape(ln)}</text>')
                ty += size + 3
            continue
        total = len(wrapped) * (size + 3)
        ty = y + h / 2 - total / 2 + size
        for i, ln in enumerate(wrapped):
            weight = ' font-weight="bold"' if i == 0 else ""
            out.append(f'<text x="{x + w / 2:g}" y="{ty:g}" font-size="{size}" fill="{TEXT}" '
                       f'text-anchor="middle"{weight}>{html.escape(ln)}</text>')
            ty += size + 3
    for c in sorted(cells.values(), key=lambda c: c.order):
        if c.kind != "edge":
            continue
        lay = drawio._layer_of(cells, c)
        if lay is None or lay.id != base.id or c.source not in boxes or c.target not in boxes:
            continue
        a, b = boxes[c.source], boxes[c.target]
        ca = (a[0] + a[2] / 2, a[1] + a[3] / 2)
        cb = (b[0] + b[2] / 2, b[1] + b[3] / 2)
        p, q = _clip(a, cb), _clip(b, ca)
        start, end = drawio._direction(c)
        marks = (' marker-end="url(#arrow)"' if end else "") + (' marker-start="url(#arrow)"' if start else "")
        out.append(f'<line x1="{p[0] - x0:g}" y1="{p[1] - y0:g}" x2="{q[0] - x0:g}" '
                   f'y2="{q[1] - y0:g}" stroke="{STROKE}" stroke-width="1.2"{marks}/>')
        # The connector's own value, else the labels drawn on it as child cells.
        label = " ".join(html_lines(c.value)) or " ".join(
            " ".join(html_lines(k.value)) for k in cells.values()
            if k.parent == c.id and k.kind == "vertex").strip()
        if label:
            mx, my = (p[0] + q[0]) / 2 - x0, (p[1] + q[1]) / 2 - y0
            short = label if len(label) <= 40 else label[:38] + "..."
            out.append(f'<text x="{mx:g}" y="{my - 4:g}" font-size="11" fill="{TEXT}" '
                       f'text-anchor="middle" stroke="#FFFFFF" stroke-width="3" '
                       f'paint-order="stroke">{html.escape(short)}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n", " ".join(html_lines(base.value)) or "Structure"
