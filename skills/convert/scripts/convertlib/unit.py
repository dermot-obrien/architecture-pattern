# SPDX-License-Identifier: Apache-2.0
"""The unit model: the boxes, links and scenarios read from one diagram and its text.

    {
      "name": "Order intake",                  the document's name, without an identifier
      "summary": "...",                         the source's opening text, if any
      "type": "",                               chosen later: architecture-pattern,
                                                reference-architecture, use-case, collaboration
      "sources": {"diagram": "...", "format": "drawio", "text": ["..."]},
      "extraction": "exact",                    exact (an identified draw.io), heuristic
                                                (drawn shapes and text), agent (from an image)
      "boxes": [{"key": "b1", "id": "", "label": "Gateway", "description": "",
                 "kind": "", "container": "", "uncertain": ""}],
      "links": [{"key": "l1", "id": "", "source": "b1", "target": "b2", "label": "",
                 "description": "", "directed": true, "uncertain": ""}],
      "scenarios": [{"key": "S1", "name": "", "from": "diagram", "steps": [
                 {"step": 1, "actor": "b1", "target": "b2", "action": "", "link": "l1",
                  "uncertain": ""}]}],
      "signals": {...},                         what the classifier reads: styles, words
      "notes": ["..."],                         anything not placed, for the report
      "sections": [{"heading": "...", "text": "..."}]   source text not otherwise placed
    }

Boxes and links are referred to by `key`, which is stable within the unit. `id` is the
identifier the source carried, if any; the draft gives every box and link one. A non-empty
`uncertain` says why a reader was not sure, and the draft lists each for review.
"""
from __future__ import annotations

import html
import re

CATALOGUE_ID = re.compile(r"^\s*([A-Z][A-Z0-9]{1,6}-[0-9]{2,4}(?:\.[0-9]+)?)\b[\s:.\-]*")
LOCAL_ID = re.compile(r"^\s*([0-9]{1,3})\s+(?=\S)")
BREAKS = re.compile(r"<\s*(br|/div|/p|/li|/h[1-6]|hr)\b[^>]*>", re.I)
TAGS = re.compile(r"<[^>]+>")


def new_unit(name="", diagram="", fmt="", text=None) -> dict:
    return {"name": name, "summary": "", "type": "",
            "sources": {"diagram": diagram, "format": fmt, "text": list(text or [])},
            "extraction": "", "boxes": [], "links": [], "scenarios": [],
            "signals": {"styles": [], "words": []}, "notes": [], "sections": []}


def html_lines(value) -> list:
    """The visible lines of a draw.io label, which may hold HTML."""
    s = str(value or "")
    if "<" in s:
        s = BREAKS.sub("\n", s)
        s = TAGS.sub("", s)
    s = html.unescape(s).replace(" ", " ")
    return [re.sub(r"\s+", " ", ln).strip() for ln in s.splitlines() if ln.strip()]


def split_label(value) -> tuple:
    """(identifier, name, description) from a box label. The first line is the name,
    any further lines the description; a catalogue or local identifier leading the name
    is taken off it."""
    lines = html_lines(value)
    if not lines:
        return "", "", ""
    first, rest = lines[0], " ".join(lines[1:])
    ident = ""
    m = CATALOGUE_ID.match(first)
    if m and first[m.end():].strip():
        ident, first = m.group(1), first[m.end():].strip()
    elif m and rest:
        ident, first, rest = m.group(1), lines[1], " ".join(lines[2:])
    else:
        m = LOCAL_ID.match(first)
        if m:
            ident, first = m.group(1).zfill(2), first[m.end():].strip()
    return ident, first, rest


def norm(s) -> str:
    """A label for comparison: lower case, markup and punctuation gone, spaces single."""
    s = " ".join(html_lines(s)).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slug(s, limit=48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", norm(s)).strip("-")
    return s[:limit].rstrip("-") or "untitled"


def humanise(stem) -> str:
    s = re.sub(r"[-_]+", " ", stem).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:1].upper() + s[1:] if s else "Untitled"


def add_box(u, label, **kw) -> dict:
    b = {"key": f"b{len(u['boxes']) + 1}", "id": "", "label": label, "description": "",
         "kind": "", "container": "", "uncertain": ""}
    b.update({k: v for k, v in kw.items() if v is not None})
    u["boxes"].append(b)
    return b


def add_link(u, source, target, **kw) -> dict:
    lk = {"key": f"l{len(u['links']) + 1}", "id": "", "source": source, "target": target,
          "label": "", "description": "", "directed": True, "uncertain": ""}
    lk.update({k: v for k, v in kw.items() if v is not None})
    u["links"].append(lk)
    return lk


def box(u, key):
    return next((b for b in u["boxes"] if b["key"] == key), None)


def link_between(u, a, b, either=True):
    """The first link from a to b, or from b to a when `either`."""
    for lk in u["links"]:
        if lk["source"] == a and lk["target"] == b:
            return lk
    if either:
        for lk in u["links"]:
            if lk["source"] == b and lk["target"] == a:
                return lk
    return None


def label_index(u) -> list:
    """[(normalised label, box key)], longest first, for finding boxes named in text."""
    out = []
    for b in u["boxes"]:
        for name in {b["label"], f"{b['id']} {b['label']}".strip(), b["id"]}:
            n = norm(name)
            if n and len(n) > 1:
                out.append((n, b["key"]))
    return sorted(set(out), key=lambda x: -len(x[0]))


def boxes_named(u, text) -> list:
    """Box keys named in text, in the order they first appear. Longer names win, so
    'Order store' is found before 'Order'."""
    t = f" {norm(text)} "
    taken = [False] * len(t)
    found = []
    for name, key in label_index(u):
        for m in re.finditer(rf"(?<=\s){re.escape(name)}(?=\s)", t):
            if any(taken[m.start():m.end()]):
                continue
            for i in range(m.start(), m.end()):
                taken[i] = True
            found.append((m.start(), key))
    seen, out = set(), []
    for _, key in sorted(found):
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def normalise(u) -> dict:
    """Make a unit written or corrected by hand complete: every field present, every box
    and link with a key, and every link end and step actor or target that names a box by
    its label or identifier turned into that box's key. Returns the problems found."""
    base = new_unit()
    for k, v in base.items():
        u.setdefault(k, v)
    for k, v in base["sources"].items():
        u["sources"].setdefault(k, v)
    keys = set()
    for i, b in enumerate(u["boxes"], 1):
        b.setdefault("key", f"b{i}")
        if not b["key"] or b["key"] in keys:
            b["key"] = f"b{i}"
            while b["key"] in keys:
                b["key"] += "x"
        keys.add(b["key"])
        for k, v in (("id", ""), ("label", ""), ("description", ""), ("kind", ""),
                     ("container", ""), ("uncertain", "")):
            b.setdefault(k, v)
        if not b["label"]:
            b["label"] = b["id"] or b["key"]
    problems = []

    def resolve(ref, what):
        if not ref or ref in keys:
            return ref or ""
        n = norm(ref)
        for b in u["boxes"]:
            if n in (norm(b["label"]), norm(b["id"]), norm(f"{b['id']} {b['label']}")):
                return b["key"]
        problems.append(f"{what} names {ref!r}, which is no box")
        return ""

    lkeys = set()
    for i, lk in enumerate(u["links"], 1):
        lk.setdefault("key", f"l{i}")
        if not lk["key"] or lk["key"] in lkeys:
            lk["key"] = f"l{i}"
        lkeys.add(lk["key"])
        for k, v in (("id", ""), ("label", ""), ("description", ""), ("directed", True),
                     ("uncertain", "")):
            lk.setdefault(k, v)
        lk["source"] = resolve(lk.get("source"), f"link {lk['key']}")
        lk["target"] = resolve(lk.get("target"), f"link {lk['key']}")
    u["links"] = [lk for lk in u["links"] if lk["source"] and lk["target"]]
    lkeys = {lk["key"] for lk in u["links"]}
    for j, sc in enumerate(u["scenarios"], 1):
        sc.setdefault("key", f"S{j}")
        sc.setdefault("name", "")
        sc.setdefault("from", "agent" if u.get("extraction") == "agent" else "")
        for i, st in enumerate(sc.get("steps", []), 1):
            st.setdefault("step", i)
            st.setdefault("action", "")
            st.setdefault("uncertain", "")
            st["actor"] = resolve(st.get("actor"), f"{sc['key']} step {i}")
            st["target"] = resolve(st.get("target"), f"{sc['key']} step {i}")
            ref = st.get("link", "")
            if ref and ref not in lkeys:
                hit = next((lk["key"] for lk in u["links"] if lk["id"] == ref), "")
                st["link"] = hit
            elif not ref and st["actor"] and st["target"]:
                hit = link_between(u, st["actor"], st["target"])
                st["link"] = hit["key"] if hit else ""
            st.setdefault("link", "")
    return problems
