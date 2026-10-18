# SPDX-License-Identifier: Apache-2.0
"""Read the Markdown that goes with a diagram, and place what it says on the unit.

What is read, in order of how sure the reading is:

    a title           front matter title, else the first H1
    a summary         the paragraphs before the first subheading
    box descriptions  a table whose first column names a box; a bullet "Name: what it
                      does"; a heading that is a box's name, and the paragraph under it
    link labels       a table with From and To (or Source and Target, Provider and
                      Consumer) columns; a line "A -> B: what flows"
    scenarios         a mermaid sequenceDiagram; a table with a Step column; a numbered
                      list under a heading that says scenario, flow, sequence, steps,
                      journey or process; any other numbered list whose items each name
                      two boxes

A numbered step in prose names its actor first and its target second; a step naming
fewer than two boxes, or more, is marked uncertain. Text that places nowhere is kept in
`sections`, so the draft carries it for the agent to fold in.
"""
from __future__ import annotations

import re

from .unit import box, boxes_named, link_between, norm

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)\s*([\w-]*)")
ORDERED = re.compile(r"^\s{0,3}([0-9]{1,2})[.)]\s+(.*)$")
BULLET = re.compile(r"^\s{0,3}[-*+]\s+(.*)$")
ARROW = re.compile(r"^(.+?)\s*(?:->|-->|→|=>)\s*(.+?)\s*[:–—-]\s+(.+)$")
DEFINE = re.compile(r"^\*{0,2}([^*:–—]+?)\*{0,2}\s*(?::|\s[–—-]\s)\s*(.+)$")
SCENARIO_HEAD = re.compile(r"scenario|flow|sequence|steps|journey|process|walkthrough|how it works", re.I)
MERMAID_MSG = re.compile(r"^\s*([\w .()&/'-]+?)\s*(-{1,2}>>|-{1,2}>|-{1,2}x|-{1,2}\))\s*[+-]?\s*([\w .()&/'-]+?)\s*:\s*(.*)$")
MERMAID_PART = re.compile(r"^\s*(participant|actor)\s+(\S+)(?:\s+as\s+(.+))?\s*$", re.I)


def front_matter(text) -> tuple:
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for ln in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
        if mm:
            meta[mm.group(1)] = mm.group(2).strip().strip("'\"")
    return meta, text[m.end():]


def blocks(text) -> list:
    """The document as a list of sections: {level, heading, lines}, and fenced code kept
    whole as ("fence", lang, lines) items inside lines."""
    out = [{"level": 0, "heading": "", "lines": []}]
    fence = None
    for ln in text.splitlines():
        if fence is not None:
            if FENCE.match(ln):
                out[-1]["lines"].append(("fence", fence[0], fence[1]))
                fence = None
            else:
                fence[1].append(ln)
            continue
        m = FENCE.match(ln)
        if m:
            fence = (m.group(2).lower(), [])
            continue
        h = HEADING.match(ln)
        if h:
            out.append({"level": len(h.group(1)), "heading": h.group(2).strip(), "lines": []})
            continue
        out[-1]["lines"].append(ln)
    if fence is not None:
        out[-1]["lines"].append(("fence", fence[0], fence[1]))
    return out


def tables(lines) -> list:
    """[(header, rows)] of the pipe tables among the lines."""
    out, cur = [], None
    for ln in lines + [""]:
        if isinstance(ln, tuple):
            ln = ""
        s = ln.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cur is None:
                cur = [cells, []]
            elif all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            else:
                cur[1].append(cells)
        elif cur is not None:
            out.append((cur[0], cur[1]))
            cur = None
    return out


def _col(header, *names):
    for i, h in enumerate(header):
        hn = norm(h)
        if any(re.search(rf"\b{n}", hn) for n in names):
            return i
    return None


def _clean(s) -> str:
    s = re.sub(r"\*\*|__|`", "", s or "").strip()
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)


def paragraphs(lines) -> list:
    out, cur = [], []
    for ln in lines:
        if isinstance(ln, tuple) or not ln.strip() or ln.strip().startswith(("|", "<!--")):
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        if ORDERED.match(ln) or BULLET.match(ln):
            if cur:
                out.append(" ".join(cur))
                cur = []
            continue
        cur.append(ln.strip())
    if cur:
        out.append(" ".join(cur))
    return out


def _describe(b, desc) -> bool:
    """Give a box the text's description. The text's wins over a line under the box's
    name on the diagram, which is usually a shorter version of it."""
    if not desc or (b.get("description") and b.get("described_by") != "diagram"):
        return False
    b["description"] = desc
    b["described_by"] = "text"
    return True


def _exact_box(u, name):
    n = norm(_clean(name))
    if not n:
        return None
    for b in u["boxes"]:
        if n in (norm(b["label"]), norm(f"{b['id']} {b['label']}"), norm(b["id"])):
            return b
    return None


# ------------------------------------------------------------------ scenarios

def _step_from_text(u, text):
    names = boxes_named(u, text)
    why = ""
    if len(names) < 2:
        why = ("names one box, so its target is a guess" if names
               else "names no box on the diagram")
    elif len(names) > 2:
        why = f"names {len(names)} boxes; the first two were taken as actor and target"
    actor = names[0] if names else ""
    target = names[1] if len(names) > 1 else ""
    return actor, target, why


def _finish_steps(u, raw):
    steps = []
    for i, (actor, target, action, why) in enumerate(raw, 1):
        lk = link_between(u, actor, target) if actor and target else None
        if actor and target and not lk:
            why = (why + "; " if why else "") + "no line on the diagram joins these two boxes"
        steps.append({"step": i, "actor": actor, "target": target, "action": action,
                      "link": lk["key"] if lk else "", "uncertain": why})
    return steps


def mermaid_scenario(u, lines, name):
    alias = {}
    raw = []
    for ln in lines:
        m = MERMAID_PART.match(ln)
        if m:
            alias[m.group(2)] = (m.group(3) or m.group(2)).strip()
            continue
        m = MERMAID_MSG.match(ln)
        if not m:
            continue
        a, b = alias.get(m.group(1).strip(), m.group(1).strip()), alias.get(m.group(3).strip(), m.group(3).strip())
        ba, bb = _exact_box(u, a), _exact_box(u, b)
        if ba is None:
            found = boxes_named(u, a)
            ba = box(u, found[0]) if found else None
        if bb is None:
            found = boxes_named(u, b)
            bb = box(u, found[0]) if found else None
        why = ""
        if ba is None or bb is None:
            missing = [x for x, y in ((a, ba), (b, bb)) if y is None]
            why = f"{' and '.join(repr(x) for x in missing)} is not a box on the diagram"
        raw.append((ba["key"] if ba else "", bb["key"] if bb else "", _clean(m.group(4)), why))
    if not raw:
        return None
    return {"key": "", "name": name, "from": "text: sequence diagram", "steps": _finish_steps(u, raw)}


def list_scenario(u, items, name, source):
    raw = []
    for text in items:
        actor, target, why = _step_from_text(u, text)
        raw.append((actor, target, _clean(text), why))
    return {"key": "", "name": name, "from": source, "steps": _finish_steps(u, raw)}


def table_scenario(u, header, rows, name):
    si = _col(header, "step", "#", "no")
    ai = _col(header, "actor", "from", "who", "source")
    ti = _col(header, "target", "to", "receiver", "destination")
    di = _col(header, "action", "what", "description", "message", "happens")
    if si is None or di is None:
        return None
    raw = []
    for r in rows:
        r = r + [""] * (len(header) - len(r))
        action = _clean(r[di])
        if ai is not None and ti is not None:
            ba, bb = _exact_box(u, r[ai]), _exact_box(u, r[ti])
            why = "" if ba and bb else "an actor or target is not a box on the diagram"
            raw.append((ba["key"] if ba else "", bb["key"] if bb else "", action, why))
        else:
            actor, target, why = _step_from_text(u, action)
            raw.append((actor, target, action, why))
    return {"key": "", "name": name, "from": "text: steps table", "steps": _finish_steps(u, raw)}


# ------------------------------------------------------------------ applying

def apply(u, text, source="") -> dict:
    """Place the Markdown's content on the unit. Returns what was found, for the report."""
    meta, body = front_matter(text)
    secs = blocks(body)
    found = {"descriptions": 0, "links": 0, "scenarios": 0, "title": ""}
    title = meta.get("title", "")
    for s in secs:
        if s["level"] == 1 and not title:
            title = s["heading"]
    if title:
        found["title"] = title
        u.setdefault("signals", {}).setdefault("titles", []).append(title)
    for k in ("pattern_type", "document_type", "type"):
        if meta.get(k):
            u["signals"]["declared_type"] = meta[k]
    words = u["signals"].setdefault("words", [])

    # The summary: the paragraphs before the first subheading below the title.
    lead = []
    for s in secs:
        if s["level"] <= 1:
            lead += paragraphs(s["lines"])
        else:
            break
    if lead and not u.get("summary"):
        u["summary"] = "\n\n".join(_clean(p) for p in lead)
    words += lead

    placed_sections = set()
    for idx, s in enumerate(secs):
        lines = s["lines"]
        heading = s["heading"]
        words.append(heading)
        used = False
        # Tables: boxes, links, or steps.
        for header, rows in tables(lines):
            if _col(header, "step") is not None:
                sc = table_scenario(u, header, rows, heading or "Flow from the text")
                if sc:
                    u["scenarios"].append(sc)
                    found["scenarios"] += 1
                    used = True
                    continue
            fi = _col(header, "from", "source", "provider", "caller")
            ti = _col(header, "to", "target", "consumer", "callee")
            if fi is not None and ti is not None and fi != ti:
                li = _col(header, "purpose", "label", "what", "flows", "description", "data", "message")
                for r in rows:
                    r = r + [""] * (len(header) - len(r))
                    ba, bb = _exact_box(u, r[fi]), _exact_box(u, r[ti])
                    if not ba or not bb:
                        continue
                    lk = link_between(u, ba["key"], bb["key"])
                    if lk and li is not None and r[li]:
                        if lk["label"]:
                            lk["description"] = _clean(r[li])
                        else:
                            lk["label"] = _clean(r[li])
                        found["links"] += 1
                        used = True
                continue
            di = _col(header, "role", "description", "purpose", "responsib", "what", "does")
            ki = _col(header, "kind", "type", "category")
            for r in rows:
                if not r:
                    continue
                b = _exact_box(u, r[0])
                if not b:
                    continue
                r = r + [""] * (len(header) - len(r))
                desc = _clean(r[di]) if di is not None and di != 0 else _clean(r[1]) if len(r) > 1 else ""
                if _describe(b, desc):
                    found["descriptions"] += 1
                    used = True
                if ki is not None and ki != 0 and r[ki] and not b["kind"]:
                    b["kind"] = _clean(r[ki]).lower()
        # Fenced mermaid sequence diagrams.
        for ln in lines:
            if isinstance(ln, tuple) and ln[1] == "mermaid" and any(
                    "sequencediagram" in x.lower().replace(" ", "") for x in ln[2][:3]):
                sc = mermaid_scenario(u, ln[2], heading or "Sequence from the text")
                if sc:
                    u["scenarios"].append(sc)
                    found["scenarios"] += 1
                    used = True
        # Bullets and arrows.
        for ln in lines:
            if isinstance(ln, tuple):
                continue
            m = BULLET.match(ln)
            item = m.group(1) if m else ln.strip()
            a = ARROW.match(_clean(item))
            if a:
                ba, bb = _exact_box(u, a.group(1)), _exact_box(u, a.group(2))
                if ba and bb:
                    lk = link_between(u, ba["key"], bb["key"], either=False) or \
                        link_between(u, ba["key"], bb["key"])
                    if lk:
                        if lk["label"] and norm(lk["label"]) != norm(a.group(3)):
                            lk["description"] = _clean(a.group(3))
                        elif not lk["label"]:
                            lk["label"] = _clean(a.group(3))
                        found["links"] += 1
                        used = True
                continue
            if m:
                d = DEFINE.match(item)
                if d:
                    b = _exact_box(u, d.group(1))
                    if b and _describe(b, _clean(d.group(2))):
                        found["descriptions"] += 1
                        used = True
        # A heading that is a box's name describes it.
        b = _exact_box(u, heading) if heading else None
        if b:
            paras = paragraphs(lines)
            if paras and _describe(b, _clean(paras[0])):
                found["descriptions"] += 1
            used = True
        # Numbered lists.
        items = [ORDERED.match(ln).group(2) for ln in lines
                 if not isinstance(ln, tuple) and ORDERED.match(ln)]
        if items and not any(isinstance(ln, tuple) and ln[1] == "mermaid" for ln in lines):
            if SCENARIO_HEAD.search(heading or ""):
                u["scenarios"].append(list_scenario(u, items, heading, "text: numbered list"))
                found["scenarios"] += 1
                used = True
            elif len(items) >= 3 and sum(len(boxes_named(u, i)) >= 2 for i in items) * 2 > len(items):
                sc = list_scenario(u, items, heading or "Flow from the text",
                                   "text: numbered list, read as a scenario")
                for st in sc["steps"]:
                    st["uncertain"] = (st["uncertain"] + "; " if st["uncertain"] else "") + \
                        "a numbered list not headed as a scenario"
                u["scenarios"].append(sc)
                found["scenarios"] += 1
                used = True
        if used:
            placed_sections.add(idx)
        words += paragraphs(lines)

    for idx, s in enumerate(secs):
        if idx in placed_sections or s["level"] <= 1:
            continue
        body_text = "\n".join(ln for ln in s["lines"] if not isinstance(ln, tuple)).strip()
        if body_text:
            u["sections"].append({"heading": s["heading"], "text": body_text, "source": source})
    return found
