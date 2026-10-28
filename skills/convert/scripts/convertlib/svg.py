# SPDX-License-Identifier: Apache-2.0
"""Read an SVG into units.

An SVG exported from draw.io usually carries the whole diagram in its root's `content`
attribute; that is decoded and read as draw.io, exactly when its shapes are identified.

Any other SVG is read best-effort from what it draws: a closed shape (rect, circle,
ellipse, polygon, or a closed path) holding text is a box named by that text; a line,
polyline or open path whose two ends lie on or near two boxes is a link, pointing the way
its arrowhead marker says; text near a link's middle is its label, and a number leading
that label makes it a scenario step. Only translate, scale and matrix transforms are
followed. Everything read this way is marked uncertain in the report.
"""
from __future__ import annotations

import html
import math
import re
import xml.etree.ElementTree as ET

from . import drawio
from .unit import add_box, add_link, html_lines, new_unit, split_label

NS = re.compile(r"^\{[^}]+\}")
NUM = re.compile(r"[-+]?(?:[0-9]*\.[0-9]+|[0-9]+\.?)(?:[eE][-+]?[0-9]+)?")
SHAPES = ("rect", "circle", "ellipse", "polygon")
LINES = ("line", "polyline", "path")


class SvgError(Exception):
    pass


def _tag(el) -> str:
    return NS.sub("", el.tag)


def embedded_drawio(text: str) -> str:
    """The draw.io file an SVG carries in its `content` attribute, or ""."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as ex:
        raise SvgError(f"not an SVG: {ex}")
    if _tag(root) != "svg":
        raise SvgError(f"not an SVG: the root element is <{_tag(root)}>")
    content = root.get("content") or ""
    content = html.unescape(content).strip()
    if content.startswith("<mxfile") or content.startswith("<mxGraphModel"):
        return content
    return ""


# ------------------------------------------------------------------ geometry

def _mul(a, b):
    return (a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1],
            a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5])


IDENTITY = (1, 0, 0, 1, 0, 0)


def transform_of(s: str):
    m = IDENTITY
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in NUM.findall(args)]
        if name == "translate" and v:
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale" and v:
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "matrix" and len(v) == 6:
            t = tuple(v)
        elif name == "rotate" and v:
            a = math.radians(v[0])
            t = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
            if len(v) == 3:
                t = _mul(_mul((1, 0, 0, 1, v[1], v[2]), t), (1, 0, 0, 1, -v[1], -v[2]))
        else:
            continue
        m = _mul(m, t)
    return m


def apply(m, pt):
    return (m[0] * pt[0] + m[2] * pt[1] + m[4], m[1] * pt[0] + m[3] * pt[1] + m[5])


def _f(el, name, default=0.0):
    try:
        return float(NUM.match(el.get(name, "")).group(0))
    except (AttributeError, ValueError):
        return default


def path_points(d: str) -> tuple:
    """(points, closed) of a path, enough for its ends and its bounding box."""
    pts, cur, start, closed = [], (0.0, 0.0), (0.0, 0.0), False
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|" + NUM.pattern, d or "")
    i, cmd = 0, ""
    counts = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "t": 2, "a": 7, "z": 0}
    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r"[A-Za-z]", tok):
            cmd = tok
            i += 1
            if cmd in "Zz":
                closed = True
                cur = start
                pts.append(cur)
            continue
        n = counts.get(cmd.lower(), 2)
        args = [float(x) for x in tokens[i:i + n]]
        if len(args) < n or n == 0:
            break
        i += n
        rel = cmd.islower()
        c = cmd.lower()
        if c == "h":
            cur = (cur[0] + args[0] if rel else args[0], cur[1])
        elif c == "v":
            cur = (cur[0], cur[1] + args[0] if rel else args[0])
        else:
            x, y = args[-2], args[-1]
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
        if c == "m":
            start = cur
            cmd = "l" if rel else "L"
        pts.append(cur)
    return pts, closed


def _bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def _dist(g, pt):
    x, y, w, h = g
    dx = max(x - pt[0], 0, pt[0] - (x + w))
    dy = max(y - pt[1], 0, pt[1] - (y + h))
    return (dx * dx + dy * dy) ** 0.5


def _inside(g, pt, pad=0):
    x, y, w, h = g
    return x - pad <= pt[0] <= x + w + pad and y - pad <= pt[1] <= y + h + pad


# ------------------------------------------------------------------ reading

def _texts(el):
    """Text lines of a <text> (its tspans) or of a foreignObject's HTML."""
    if _tag(el) == "text":
        parts = []
        for t in el.iter():
            if t.text and t.text.strip():
                parts.append(t.text.strip())
        return [" ".join(parts)] if parts else []
    raw = ET.tostring(el, encoding="unicode")
    raw = re.sub(r"<(/?)[\w:]+?:", r"<\1", raw)
    return html_lines(raw)


def collect(root):
    shapes, lines, texts = [], [], []
    markers_end = set()

    def walk(el, m, in_switch=False, defs=False):
        tag = _tag(el)
        if tag in ("defs", "marker", "clipPath", "mask", "pattern", "symbol"):
            if tag == "marker":
                markers_end.add(el.get("id", ""))
            return
        m = _mul(m, transform_of(el.get("transform", "")))
        if tag == "switch":
            for ch in el:
                if _tag(ch) in ("foreignObject", "text", "g"):
                    walk(ch, m, True)
                    return                      # the first child that renders is the one
            return
        if tag in SHAPES or (tag == "path" and path_points(el.get("d", ""))[1]):
            fill = (el.get("fill") or "").lower()
            if tag == "rect":
                x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
                pts = [(x, y), (x + w, y + h)]
            elif tag in ("circle", "ellipse"):
                cx, cy = _f(el, "cx"), _f(el, "cy")
                rx = _f(el, "r") if tag == "circle" else _f(el, "rx")
                ry = _f(el, "r") if tag == "circle" else _f(el, "ry")
                pts = [(cx - rx, cy - ry), (cx + rx, cy + ry)]
            elif tag == "polygon":
                v = [float(x) for x in NUM.findall(el.get("points", ""))]
                pts = list(zip(v[0::2], v[1::2])) or [(0, 0)]
            else:
                pts = path_points(el.get("d", ""))[0] or [(0, 0)]
            pts = [apply(m, p) for p in pts]
            g = _bbox(pts)
            if g[2] > 2 and g[3] > 2:
                shapes.append({"g": g, "tag": tag, "fill": fill, "texts": [], "el": el})
        elif tag in LINES:
            if tag == "line":
                pts = [(_f(el, "x1"), _f(el, "y1")), (_f(el, "x2"), _f(el, "y2"))]
            elif tag == "polyline":
                v = [float(x) for x in NUM.findall(el.get("points", ""))]
                pts = list(zip(v[0::2], v[1::2]))
            else:
                pts = path_points(el.get("d", ""))[0]
            if len(pts) >= 2:
                pts = [apply(m, p) for p in pts]
                style = el.get("style", "")
                end = el.get("marker-end") or ("marker-end" in style and "url(" in style)
                start = el.get("marker-start") or ("marker-start" in style and "url(" in style)
                lines.append({"pts": pts, "end": bool(end), "start": bool(start), "label": ""})
        elif tag in ("text", "foreignObject"):
            got = _texts(el)
            if got:
                if tag == "text":
                    x, y = _f(el, "x"), _f(el, "y")
                    if not el.get("x"):
                        ts = next((t for t in el.iter() if t.get("x")), None)
                        if ts is not None:
                            x, y = _f(ts, "x"), _f(ts, "y")
                    pt = apply(m, (x, y - 4))
                else:
                    x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
                    pt = apply(m, (x + w / 2, y + h / 2))
                size = _f(el, "font-size", 0) or 12
                texts.append({"pt": pt, "lines": got, "size": size})
            return
        for ch in el:
            walk(ch, m, in_switch)

    walk(root, IDENTITY)
    return shapes, lines, texts


def read_plain(text, path, name) -> dict:
    root = ET.fromstring(text)
    u = new_unit(name=name, diagram=path, fmt="svg")
    u["extraction"] = "heuristic"
    shapes, lines, texts = collect(root)

    # The page background, and any shape enclosing others, is a frame or a group.
    def encloses(a, b):
        return (a["g"][0] <= b["g"][0] + 0.5 and a["g"][1] <= b["g"][1] + 0.5
                and a["g"][0] + a["g"][2] >= b["g"][0] + b["g"][2] - 0.5
                and a["g"][1] + a["g"][3] >= b["g"][1] + b["g"][3] - 0.5 and a is not b)

    # A shape enclosing other shapes is a frame or a group, never a box; one covering
    # nearly the whole picture is its background.
    W = _f(root, "width") or 0
    H = _f(root, "height") or 0
    vb = [float(x) for x in NUM.findall(root.get("viewBox", ""))]
    if len(vb) == 4:
        W, H = vb[2], vb[3]
    groups, plain = [], []
    for s in shapes:
        background = W and H and s["g"][2] * s["g"][3] >= 0.85 * W * H
        if background:
            continue
        if any(encloses(s, o) for o in shapes):
            groups.append(s)
        else:
            plain.append(s)

    # Each text belongs to the smallest plain shape it falls inside; text inside a group
    # but in no shape names the group when it sits along its top, and is free otherwise.
    free = []
    for t in texts:
        holders = [s for s in plain if _inside(s["g"], t["pt"], 2)]
        if holders:
            min(holders, key=lambda s: s["g"][2] * s["g"][3])["texts"].append(t)
            continue
        tops = [g for g in groups if _inside(g["g"], t["pt"], 2) and t["pt"][1] - g["g"][1] <= 32]
        if tops:
            min(tops, key=lambda g: g["g"][2] * g["g"][3])["texts"].append(t)
        else:
            free.append(t)
    boxes = [s for s in plain if s["texts"]]

    # A shape that is only a small numbered circle is a step badge.
    def badge(s):
        lines_ = [ln for t in s["texts"] for ln in t["lines"]]
        return (s["tag"] in ("circle", "ellipse") and s["g"][2] <= 50
                and len(lines_) == 1 and re.fullmatch(r"[0-9]{1,2}[a-z]?", lines_[0]))

    keys = []
    for s in sorted(boxes, key=lambda s: (round(s["g"][1] / 20), s["g"][0])):
        if badge(s):
            continue
        tx = sorted(s["texts"], key=lambda t: (t["pt"][1], t["pt"][0]))
        lines_ = [ln for t in tx for ln in t["lines"]]
        ident, label, desc = split_label("<br>".join(html.escape(x) for x in lines_))
        container = ""
        holders = [g for g in groups if encloses(g, s)]
        if holders:
            gsm = min(holders, key=lambda g: g["g"][2] * g["g"][3])
            gtexts = [t for t in gsm["texts"]]
            if gtexts:
                container = gtexts[0]["lines"][0]
        b = add_box(u, label or "Unnamed shape", id=ident, description=desc,
                    container=container, uncertain="read from the SVG's shapes and text",
                    described_by="diagram" if desc else "",
                    geom=[round(v, 1) for v in s["g"]])
        if s["tag"] in ("circle", "ellipse") and not desc:
            u["signals"]["styles"].append("ellipse")
        keys.append((s, b["key"]))
    for g in groups:
        for t in g["texts"]:
            u["signals"]["words"] += t["lines"]

    def nearest(pt):
        best = None
        for s, key in keys:
            d = _dist(s["g"], pt)
            if d <= 25 and (best is None or d < best[0]):
                best = (d, key)
        return best[1] if best else ""

    # Labels: free text nearest each line's middle, within reach.
    def middle(ln):
        pts = ln["pts"]
        segs = list(zip(pts, pts[1:]))
        total = sum(math.dist(a, b) for a, b in segs) or 1
        half, run = total / 2, 0
        for a, b in segs:
            d = math.dist(a, b)
            if run + d >= half:
                f = (half - run) / (d or 1)
                return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            run += d
        return pts[-1]

    joined = []
    for ln in lines:
        s, t = nearest(ln["pts"][0]), nearest(ln["pts"][-1])
        if s and t and s != t:
            joined.append((ln, s, t))
    taken = set()
    for ln, s, t in joined:
        mid = middle(ln)
        best = None
        for i, tx in enumerate(free):
            if i in taken:
                continue
            d = math.dist(mid, tx["pt"])
            if d <= 60 and (best is None or d < best[0]):
                best = (d, i)
        if best:
            taken.add(best[1])
            ln["label"] = " ".join(free[best[1]]["lines"])

    numbered = []
    for ln, s, t in joined:
        if ln["start"] and not ln["end"]:
            s, t = t, s
        why = "read from the SVG's lines"
        if ln["start"] == ln["end"]:
            why += "; " + ("it has an arrowhead at both ends" if ln["start"] else "it has no arrowhead")
        text = ln["label"]
        m = drawio.STEP.match(text) if text else None
        step = None
        if m and m.group(3):
            step = (int(m.group(1)), m.group(2), m.group(3).strip())
            text = step[2]
        lk = add_link(u, s, t, label=text, directed=ln["start"] != ln["end"], uncertain=why)
        if step:
            numbered.append((step[0], step[1], s, t, step[2], lk["key"]))
    if numbered:
        u["scenarios"].append(drawio._scenario(u, "S1", "Flow numbered on the diagram", numbered))

    for i, tx in enumerate(free):
        if i not in taken:
            u["notes"].append("text on the diagram: " + " / ".join(tx["lines"]))
    big = [tx for i, tx in enumerate(free) if i not in taken and tx["size"] >= 16]
    if big:
        top = min(big, key=lambda tx: tx["pt"][1])
        u["signals"]["title"] = " ".join(top["lines"])
    u["signals"]["words"] += [b["label"] for b in u["boxes"]]
    dropped = len(lines) - len(joined)
    if dropped:
        u["notes"].append(f"{dropped} line(s) on the SVG did not join two boxes and were left out")
    return u


def read_text(text, path, name) -> list:
    embedded = embedded_drawio(text)
    if embedded:
        units = drawio.read_text(embedded, path, name, fmt="svg-drawio")
        return units
    u = read_plain(text, path, name)
    u["page"] = 0
    return [u] if u["boxes"] else []


def read(path, name) -> list:
    with open(path, encoding="utf-8") as fh:
        return read_text(fh.read(), path, name)
