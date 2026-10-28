# SPDX-License-Identifier: Apache-2.0
"""Read a draw.io diagram into units: one per page that draws anything.

A diagram whose shapes carry identifiers, as one the model skill wrote does, is read by
`model extract`, exactly. Any other is read from its shapes: a labelled vertex is a box,
a connector between two of them a link, a container a group, a small numbered circle a
scenario badge, a numbered connector a scenario step, and a layer holding only
connectors a scenario of its own. Whatever is read by judgement carries a reason in
`uncertain`, and whatever is not placed goes to `notes`.
"""
from __future__ import annotations

import base64
import json
import os
import re
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
import zlib

from . import skills
from .unit import add_box, add_link, html_lines, link_between, new_unit, split_label

OBJECT_TAGS = ("object", "UserObject")
RESERVED = {"id", "label", "placeholders", "tooltip", "link", "linkTarget", "tags",
            "treeRoot"}
STEP = re.compile(r"^\s*\(?\s*([0-9]{1,2})([a-z]?)\s*[).:\-]?\s*(.*)$", re.S)
SCENARIO_LAYER = re.compile(r"^\s*(S[0-9]+\b|scenario|flow|sequence|steps?\b|overlay)", re.I)
LEGEND = re.compile(r"^\s*(key|legend)\b", re.I)


class DrawioError(Exception):
    pass


# ------------------------------------------------------------------ the file

def _inflate(text: str) -> str:
    data = base64.b64decode(text)
    try:
        raw = zlib.decompress(data, -15)
    except zlib.error:
        raw = zlib.decompress(data)
    return urllib.parse.unquote(raw.decode("utf-8"))


def parse_mxfile(text: str):
    """[(page name, mxGraphModel element)] from the text of a .drawio file, compressed
    or not, or of a bare mxGraphModel."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as ex:
        raise DrawioError(f"not a draw.io file: {ex}")
    if root.tag == "mxGraphModel":
        return [("Page-1", root)]
    if root.tag != "mxfile":
        raise DrawioError(f"not a draw.io file: the root element is <{root.tag}>")
    pages = []
    for i, d in enumerate(root.findall("diagram")):
        model = d.find("mxGraphModel")
        if model is None:
            payload = (d.text or "").strip()
            if not payload:
                continue
            try:
                model = ET.fromstring(_inflate(payload))
            except (ValueError, zlib.error, ET.ParseError) as ex:
                raise DrawioError(f"page {i + 1} is compressed and does not decode: {ex}")
        pages.append((d.get("name") or f"Page-{i + 1}", model))
    return pages


def uncompressed(text: str) -> str:
    """The same diagram with every page written out as XML, which model's writers need."""
    root = ET.fromstring(text)
    if root.tag == "mxGraphModel":
        out = ET.Element("mxfile", {"host": "convert", "compressed": "false"})
        d = ET.SubElement(out, "diagram", {"id": "page-1", "name": "Page-1"})
        d.append(root)
        return ET.tostring(out, encoding="unicode")
    root.set("compressed", "false")
    for i, d in enumerate(root.findall("diagram")):
        if d.find("mxGraphModel") is None and (d.text or "").strip():
            model = ET.fromstring(_inflate(d.text.strip()))
            d.text = None
            d.append(model)
        if not d.get("id"):
            d.set("id", f"page-{i + 1}")
    return ET.tostring(root, encoding="unicode")


def style_of(s: str) -> tuple:
    """(bare words, key=value pairs) of a draw.io style string."""
    words, pairs = set(), {}
    for part in (s or "").split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            pairs[k.strip()] = v.strip()
        else:
            words.add(part)
    return words, pairs


class Cell:
    __slots__ = ("id", "value", "style", "words", "pairs", "parent", "kind", "source",
                 "target", "attrs", "geom", "points", "order")


def cells_of(model) -> dict:
    cells = {}
    root = model.find("root")
    if root is None:
        return cells
    for order, child in enumerate(root):
        if child.tag in OBJECT_TAGS:
            mx = child.find("mxCell")
            if mx is None:
                continue
            cid, value = child.get("id"), child.get("label", "")
            attrs = {k: v for k, v in child.attrib.items() if k not in RESERVED}
        elif child.tag == "mxCell":
            mx, cid, value, attrs = child, child.get("id"), child.get("value", ""), {}
        else:
            continue
        c = Cell()
        c.id, c.value, c.attrs, c.order = cid, value or "", attrs, order
        c.style = mx.get("style", "")
        c.words, c.pairs = style_of(c.style)
        c.parent, c.source, c.target = mx.get("parent"), mx.get("source"), mx.get("target")
        if mx.get("edge") == "1":
            c.kind = "edge"
        elif mx.get("vertex") == "1":
            c.kind = "vertex"
        elif mx.get("parent") is None:
            c.kind = "root"
        elif mx.get("parent") == "0":
            c.kind = "layer"
        else:
            c.kind = "other"
        g = mx.find("mxGeometry")
        c.geom, c.points = None, {}
        if g is not None:
            c.geom = tuple(float(g.get(k, 0) or 0) for k in ("x", "y", "width", "height"))
            for p in g.findall("mxPoint"):
                c.points[p.get("as", "")] = (float(p.get("x", 0) or 0), float(p.get("y", 0) or 0))
        cells[cid] = c
    return cells


# ------------------------------------------------------------------ tagged diagrams

ID_ATTR = re.compile(r"^[a-z][a-z0-9]*_id$")


def id_attrs_used(cells) -> tuple:
    """(node identifier attributes, edge identifier attribute) the diagram carries."""
    node, edge = [], ""
    for c in cells.values():
        for k in c.attrs:
            if not ID_ATTR.match(k) or not c.attrs[k]:
                continue
            if c.kind == "vertex" and k not in node and k not in ("from_id", "to_id"):
                node.append(k)
            elif c.kind == "edge" and not edge and k not in ("from_id", "to_id"):
                edge = k
    return node, edge


def read_tagged(path, node_attrs, edge_attr):
    """The model skill's own reading of an identified diagram, as JSON, or None."""
    attrs = list(node_attrs) + (["local_id"] if "local_id" not in node_attrs else [])
    cfg = ("[model]\n"
           f"node_id_attrs = {json.dumps(attrs)}\n"
           f'edge_id_attr = "{edge_attr or "iface_id"}"\n'
           "local_pattern = '[0-9]{1,3}'\n"
           'local_attr = "local_id"\n')
    fd, cfg_path = tempfile.mkstemp(suffix=".toml")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(cfg)
    try:
        r = skills.run_model("extract", path, "--format", "json", "--config", cfg_path)
    finally:
        os.unlink(cfg_path)
    if r is None or r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def unit_from_model(m, name, path, fmt) -> dict:
    u = new_unit(name=name, diagram=path, fmt=fmt)
    u["extraction"] = "exact"
    keys = {}
    for n in m.get("nodes", []):
        attrs = n.get("attrs") or {}
        desc = next((v for k, v in attrs.items() if k.startswith("role") and v), "")
        b = add_box(u, n.get("label") or n["id"], id=n["id"], description=desc,
                    kind=n.get("kind", ""), container=n.get("group", ""))
        keys[n["id"]] = b["key"]
    edge_keys = {}
    for e in m.get("edges", []):
        s, t = keys.get(e.get("source")), keys.get(e.get("target"))
        if not s or not t:
            u["notes"].append(f"connector {e.get('id') or e.get('label') or '?'} joins "
                              f"{e.get('source')} to {e.get('target')}, not both boxes; left out")
            continue
        lk = add_link(u, s, t, id=e.get("id", ""), label=e.get("label", ""))
        if e.get("id"):
            edge_keys[e["id"]] = lk["key"]
    for sc in m.get("scenarios", []):
        steps = []
        for st in sc.get("steps", []):
            steps.append({"step": st.get("step") or len(steps) + 1,
                          "actor": keys.get(st.get("actor"), ""),
                          "target": keys.get(st.get("target"), ""),
                          "action": st.get("action", ""),
                          "link": edge_keys.get(st.get("edge"), ""), "uncertain": ""})
        u["scenarios"].append({"key": sc.get("key") or f"S{len(u['scenarios']) + 1}",
                               "name": sc.get("name", ""), "from": "diagram", "steps": steps})
    return u


# ------------------------------------------------------------------ drawn diagrams

def _layer_of(cells, c):
    seen, cur = set(), c
    while cur is not None and cur.kind not in ("layer", "root"):
        if cur.id in seen:
            return None
        seen.add(cur.id)
        cur = cells.get(cur.parent)
    return cur if cur is not None and cur.kind == "layer" else None


def _abs_geom(cells, c, memo):
    if c.id in memo:
        return memo[c.id]
    x, y, w, h = c.geom or (0, 0, 0, 0)
    p = cells.get(c.parent)
    if p is not None and p.kind == "vertex" and p.id != c.id:
        memo[c.id] = (x, y, w, h)                  # cycle guard
        px, py, _, _ = _abs_geom(cells, p, memo)
        x, y = x + px, y + py
    memo[c.id] = (x, y, w, h)
    return memo[c.id]


def _is_text(c) -> bool:
    if "text" in c.words or c.pairs.get("shape") == "text":
        return True
    no_stroke = c.pairs.get("strokeColor") == "none"
    no_fill = c.pairs.get("fillColor", "none") == "none"
    return no_stroke and no_fill and "ellipse" not in c.words


def _is_container(c, has_children) -> bool:
    return ("swimlane" in c.words or c.pairs.get("container") == "1" or "group" in c.words
            or c.pairs.get("shape") in ("swimlane", "table") or has_children)


def _is_badge(c, label) -> bool:
    w, h = (c.geom or (0, 0, 0, 0))[2:]
    return bool(re.fullmatch(r"[0-9]{1,2}[a-z]?", label)) and 0 < w <= 50 and 0 < h <= 50


def _direction(c) -> tuple:
    end = c.pairs.get("endArrow", "classic") != "none"
    start = c.pairs.get("startArrow", "none") != "none"
    return start, end


def _contains(g, pt, pad=0):
    x, y, w, h = g
    return x - pad <= pt[0] <= x + w + pad and y - pad <= pt[1] <= y + h + pad


def _dist(g, pt):
    x, y, w, h = g
    dx = max(x - pt[0], 0, pt[0] - (x + w))
    dy = max(y - pt[1], 0, pt[1] - (y + h))
    return (dx * dx + dy * dy) ** 0.5


def read_drawn(cells, name, path, fmt, page_name="") -> dict:
    u = new_unit(name=name, diagram=path, fmt=fmt)
    u["extraction"] = "heuristic"
    layers = [c for c in sorted(cells.values(), key=lambda c: c.order) if c.kind == "layer"]
    if not layers:
        return u
    children = {}
    for c in cells.values():
        children.setdefault(c.parent, []).append(c)
    memo = {}

    def descendants(cid):
        out, stack = [], [cid]
        while stack:
            for ch in children.get(stack.pop(), []):
                out.append(ch)
                stack.append(ch.id)
        return out

    # Layers: a scenario layer has connectors and no boxes of its own, or says it is one.
    layer_vertices = {lay.id: [c for c in descendants(lay.id) if c.kind == "vertex"
                               and not _is_badge(c, " ".join(html_lines(c.value)))]
                      for lay in layers}
    structure, scenario_layers = [], []
    for i, lay in enumerate(layers):
        lname = " ".join(html_lines(lay.value)) or f"Layer {i + 1}"
        named = bool(SCENARIO_LAYER.match(lname))
        has_edges = any(c.kind == "edge" for c in descendants(lay.id))
        if i > 0 and has_edges and (named or not layer_vertices[lay.id]):
            scenario_layers.append((lay, lname))
        else:
            structure.append(lay)
    structure_ids = {lay.id for lay in structure}

    endpoint_ids = {x for c in cells.values() if c.kind == "edge" for x in (c.source, c.target) if x}
    legend = set()
    for c in cells.values():
        if c.kind == "vertex" and LEGEND.match(" ".join(html_lines(c.value))):
            if children.get(c.id):
                legend.add(c.id)
                legend.update(d.id for d in descendants(c.id))
            elif c.id not in endpoint_ids:
                legend.add(c.id)

    vertex_box, groups, texts, badges = {}, {}, [], []
    for c in sorted(cells.values(), key=lambda c: c.order):
        if c.kind != "vertex" or c.id in legend:
            continue
        lay = _layer_of(cells, c)
        if lay is None or lay.id not in structure_ids:
            continue
        parent = cells.get(c.parent)
        if parent is not None and parent.kind == "edge" or "edgeLabel" in c.words:
            continue                              # an edge's label, read with the edge
        label = " ".join(html_lines(c.value))
        if _is_badge(c, label):
            badges.append(c)
            continue
        kids = [k for k in children.get(c.id, []) if k.kind == "vertex"]
        connected = c.id in endpoint_ids
        if _is_container(c, bool(kids)) and not connected:
            groups[c.id] = split_label(c.value)[1] or label
            continue
        if _is_text(c) and not connected:
            texts.append(c)
            continue
        vertex_box[c.id] = c

    # The group each box sits in: its nearest container ancestor.
    def container_of(c):
        cur, seen = cells.get(c.parent), set()
        while cur is not None and cur.kind == "vertex" and cur.id not in seen:
            seen.add(cur.id)
            if cur.id in groups:
                return groups[cur.id]
            cur = cells.get(cur.parent)
        return ""

    # An unlabelled shape, such as an icon, takes the text placed under or over it.
    used_text = set()
    keyed = {}
    unnamed = 0
    for cid, c in vertex_box.items():
        ident, label, desc = split_label(c.value)
        uncertain = ""
        if not label:
            g = _abs_geom(cells, c, memo)
            best = None
            for t in texts:
                if t.id in used_text:
                    continue
                tg = _abs_geom(cells, t, memo)
                centre = (tg[0] + tg[2] / 2, tg[1] + tg[3] / 2)
                d = _dist(g, centre)
                if d <= 40 and (best is None or d < best[0]):
                    best = (d, t)
            if best:
                used_text.add(best[1].id)
                ident, label, desc = split_label(best[1].value)
                uncertain = "named from the text beside the shape"
            else:
                unnamed += 1
                label = f"Unnamed shape {unnamed}"
                uncertain = "the shape has no label; name it from the source"
        kind = ""
        shape = c.pairs.get("shape", "")
        if shape == "umlActor" or "actor" in shape.lower():
            kind = "actor"
        b = add_box(u, label, id=ident, description=desc, kind=kind,
                    container=container_of(c), uncertain=uncertain,
                    described_by="diagram" if desc else "")
        b["_cell"] = cid
        keyed[cid] = b["key"]
        u["signals"]["styles"].append(c.style)

    def resolve(cid):
        cur, seen = cells.get(cid), set()
        while cur is not None and cur.id not in seen:
            seen.add(cur.id)
            if cur.id in keyed:
                return keyed[cur.id]
            cur = cells.get(cur.parent)
        return ""

    def nearest(pt):
        best = None
        for cid, key in keyed.items():
            d = _dist(_abs_geom(cells, cells[cid], memo), pt)
            if d <= 30 and (best is None or d < best[0]):
                best = (d, key)
        return best[1] if best else ""

    def edge_label(c):
        parts = html_lines(c.value)
        for k in children.get(c.id, []):
            if k.kind == "vertex":
                parts += html_lines(k.value)
        return " ".join(parts).strip()

    def ends(c):
        why = []
        s = resolve(c.source) if c.source else ""
        t = resolve(c.target) if c.target else ""
        parent = cells.get(c.parent)
        off = (0, 0)
        if parent is not None and parent.kind == "vertex":
            off = _abs_geom(cells, parent, memo)[:2]
        if not s and "sourcePoint" in c.points:
            p = c.points["sourcePoint"]
            s = nearest((p[0] + off[0], p[1] + off[1]))
            if s:
                why.append("its start was not attached; joined to the nearest box")
        if not t and "targetPoint" in c.points:
            p = c.points["targetPoint"]
            t = nearest((p[0] + off[0], p[1] + off[1]))
            if t:
                why.append("its end was not attached; joined to the nearest box")
        start, end = _direction(c)
        directed = True
        if start and not end:
            s, t = t, s
        elif start == end:
            directed = False
            why.append("it has an arrowhead at both ends" if start else "it has no arrowhead")
        return s, t, directed, "; ".join(why)

    numbered = []
    for c in sorted(cells.values(), key=lambda c: c.order):
        if c.kind != "edge" or c.id in legend:
            continue
        lay = _layer_of(cells, c)
        if lay is None or lay.id not in structure_ids:
            continue
        s, t, directed, why = ends(c)
        text = edge_label(c)
        if not s or not t:
            u["notes"].append(f"a connector{' labelled ' + repr(text) if text else ''} "
                              "does not join two boxes, so it was left out")
            continue
        m = STEP.match(text) if text else None
        step = None
        if m and (m.group(3) or not text.strip().isalpha()):
            step = (int(m.group(1)), m.group(2), m.group(3).strip())
            text = step[2]
        lk = add_link(u, s, t, label=text, directed=directed, uncertain=why)
        if step:
            numbered.append((step[0], step[1], s, t, step[2], lk["key"]))

    if len(numbered) >= 2 or (numbered and not scenario_layers):
        u["scenarios"].append(_scenario(u, "S1", "Flow numbered on the diagram", numbered))

    for lay, lname in scenario_layers:
        found = []
        for i, c in enumerate(e for e in sorted(descendants(lay.id), key=lambda c: c.order)
                              if e.kind == "edge"):
            s, t, _directed, why = ends(c)
            text = edge_label(c)
            m = STEP.match(text) if text else None
            n, suffix = (int(m.group(1)), m.group(2)) if m else (i + 1, "")
            action = m.group(3).strip() if m else text
            if not s or not t:
                u["notes"].append(f"scenario layer {lname!r}: a step arrow does not join two "
                                  "boxes, so it was left out")
                continue
            lk = link_between(u, s, t)
            found.append((n, suffix, s, t, action, lk["key"] if lk else ""))
        if found:
            key = f"S{len(u['scenarios']) + 1}"
            m = re.match(r"^\s*(S[0-9]+)\b[\s:.\-]*(.*)$", lname)
            u["scenarios"].append(_scenario(u, key, (m.group(2) if m else lname) or lname, found))

    for t in texts:
        if t.id in used_text:
            continue
        lines = html_lines(t.value)
        if lines:
            u["notes"].append("text on the diagram: " + " / ".join(lines))
    title = _title(cells, texts, used_text, memo)
    if title:
        u["signals"]["title"] = title
    for gid, gname in groups.items():
        if gname:
            u["signals"]["words"].append(gname)
    if legend:
        u["notes"].append("a key or legend on the diagram was left out of the model")
    if page_name:
        u["signals"]["page"] = page_name
    u["signals"]["words"] += [b["label"] for b in u["boxes"]]
    return u


def _title(cells, texts, used, memo):
    """The largest text above every box, which is usually the diagram's title."""
    best = None
    for t in texts:
        if t.id in used:
            continue
        size = float(t.pairs.get("fontSize", 12) or 12)
        y = _abs_geom(cells, t, memo)[1]
        if best is None or (size, -y) > best[0]:
            best = ((size, -y), " ".join(html_lines(t.value)))
    return best[1] if best and best[0][0] >= 16 else ""


def _scenario(u, key, name, found) -> dict:
    found = sorted(found, key=lambda x: (x[0], x[1]))
    nums = [(n, s) for n, s, *_ in found]
    steps = []
    for i, (n, suffix, s, t, action, lk) in enumerate(found, 1):
        steps.append({"step": i, "actor": s, "target": t, "action": action or "TBD",
                      "link": lk, "uncertain": "" if action else "the arrow carries no words"})
    if [n for n, _ in nums] != list(range(1, len(nums) + 1)) or any(s for _, s in nums):
        u["notes"].append(f"{key}: the diagram numbers its steps "
                          f"{', '.join(f'{n}{s}' for n, s in nums)}; renumbered 1 to {len(nums)}")
    return {"key": key, "name": name, "from": "diagram", "steps": steps}


# ------------------------------------------------------------------ entry point

def read_text(text, path, name, fmt="drawio") -> list:
    """Units from the text of a draw.io file: one per page that draws anything."""
    pages = parse_mxfile(text)
    units = []
    for i, (pname, model) in enumerate(pages):
        cells = cells_of(model)
        node_attrs, edge_attr = id_attrs_used(cells)
        page_label = name if len(pages) == 1 else f"{name} {pname}".strip()
        u = None
        if i == 0 and node_attrs:
            with tempfile.NamedTemporaryFile("w", suffix=".drawio", delete=False,
                                             encoding="utf-8") as fh:
                fh.write(uncompressed(text))
                tmp = fh.name
            try:
                m = read_tagged(tmp, node_attrs, edge_attr)
            finally:
                os.unlink(tmp)
            if m and m.get("nodes"):
                u = unit_from_model(m, page_label, path, fmt)
        if u is None:
            u = read_drawn(cells, page_label, path, fmt, pname if len(pages) > 1 else "")
            if i > 0 and node_attrs:
                u["notes"].append("only the first page is read exactly by model; this page "
                                  "was read from its shapes")
        u["page"] = i
        if u["boxes"]:
            units.append(u)
    return units


def read(path, name) -> list:
    with open(path, encoding="utf-8") as fh:
        return read_text(fh.read(), path, name)
