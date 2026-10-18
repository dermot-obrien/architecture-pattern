# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""A backlog of pattern names, matched against the portfolio.

The backlog is a Markdown table, a Markdown bullet list or a CSV. Each row names a pattern,
and may give its type, whether it is committed, its priority, target quarter, owner and a
reference such as a ticket.

    | Name | Type | Committed | Priority | Quarter | Ref |
    - Event-driven ingestion (architecture pattern); committed; priority: high; quarter: 2027-Q1
    - [x] Tenant isolation            (a checked box is committed)

Each row is matched against the documents found by signature, never by file name:

    exact      its normalised name is a document's title, or it names a document's id
    fuzzy      one document is close enough, and no other is near it
    ambiguous  more than one document is close, or one is only somewhat close: never acted on
    new        nothing is close

A committed new row becomes a placeholder: the type's template under the type's outputDir,
with the next identifier in its series. A committed row that matches a candidate promotes
the candidate: the page moves, with its history, to where the placeholder goes, and its
notes are kept at the end.
"""
from __future__ import annotations

import csv
import difflib
import io
import os
import re

from . import docs as D

TYPE_WORDS = {
    "architecture-pattern": ["architecture pattern", "architecture-pattern", "ap", "pattern", "abb pattern"],
    "reference-architecture": ["reference architecture", "reference-architecture", "ra", "reference"],
    "collaboration": ["collaboration", "collab", "cl"],
    "use-case": ["use case", "use-case", "usecase", "uc"],
}
WORD_TYPE = {w: t for t, ws in TYPE_WORDS.items() for w in ws}
COLUMNS = {
    "name": ["name", "pattern", "title", "pattern name"],
    "type": ["type", "kind", "pattern type"],
    "committed": ["committed", "commit", "commitment"],
    "priority": ["priority", "prio"],
    "target_quarter": ["target quarter", "quarter", "target_quarter", "target"],
    "owner": ["owner"],
    "ref": ["ref", "reference", "ticket", "backlog ref", "key", "issue"],
}
STOP = {"the", "a", "an", "of", "for", "and", "pattern", "architecture", "reference", "with", "to", "in", "on"}
MATCH, NEAR = 0.85, 0.65
PRIORITY_WORDS = {"p1": "high", "p2": "medium", "p3": "low", "p4": "none", "critical": "high"}


def norm_type(s):
    s = re.sub(r"[_\s]+", " ", str(s or "").strip().lower())
    if not s:
        return ""
    return WORD_TYPE.get(s) or WORD_TYPE.get(s.replace("-", " ")) or ("?" + s)


def norm_priority(s):
    s = str(s or "").strip().lower()
    return PRIORITY_WORDS.get(s, s)


def norm_quarter(s):
    s = str(s or "").strip().upper().replace(" ", "")
    m = re.match(r"^Q([1-4])[-/]?(\d{4})$", s)
    if m:
        return f"{m.group(2)}-Q{m.group(1)}"
    m = re.match(r"^(\d{4})[-/]?Q([1-4])$", s)
    return f"{m.group(1)}-Q{m.group(2)}" if m else s


def _row(n, **kw):
    r = {"line": n, "name": "", "type": "", "committed": False, "priority": "", "target_quarter": "",
         "owner": "", "ref": ""}
    r.update({k: v for k, v in kw.items() if v not in (None,)})
    r["name"] = re.sub(r"\s+", " ", str(r["name"])).strip()
    r["type"] = norm_type(r["type"])
    r["priority"] = norm_priority(r["priority"])
    r["target_quarter"] = norm_quarter(r["target_quarter"])
    if not isinstance(r["committed"], bool):
        r["committed"] = D.truthy(r["committed"])
    return r


def _map_header(cells):
    idx = {}
    for i, c in enumerate(cells):
        c = re.sub(r"[*_`]", "", c).strip().lower()
        for key, names in COLUMNS.items():
            if c in names and key not in idx:
                idx[key] = i
    return idx


def _cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def parse(text, fmt=None):
    """[row] from a backlog, and [problem]."""
    rows, problems = [], []
    if fmt == "csv":
        reader = csv.reader(io.StringIO(text))
        header = next(reader, [])
        idx = _map_header(header)
        if "name" not in idx:
            return [], ["the CSV has no name column (name, pattern or title)"]
        for n, cells in enumerate(reader, 2):
            if not any(c.strip() for c in cells):
                continue
            get = lambda k: cells[idx[k]] if k in idx and idx[k] < len(cells) else ""  # noqa: E731
            rows.append(_row(n, **{k: get(k) for k in COLUMNS}))
        return rows, problems
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            idx = _map_header(_cells(s))
            if "name" not in idx:
                problems.append(f"line {i + 1}: a table with no name column (name, pattern or title); skipped")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = _cells(lines[i])
                if "name" in idx:
                    get = lambda k: cells[idx[k]] if k in idx and idx[k] < len(cells) else ""  # noqa: E731
                    if get("name"):
                        rows.append(_row(i + 1, **{k: get(k) for k in COLUMNS}))
                i += 1
            continue
        m = re.match(r"^\s*[-*+]\s+(\[( |x|X)\]\s+)?(.+)$", line)
        if m:
            box, content = m.group(2), m.group(3)
            pieces = [p.strip() for p in content.split(";")]
            name, kw = pieces[0], {}
            t = re.match(r"^(.*?)\s*\(([^()]+)\)\s*$", name)
            if t and norm_type(t.group(2))[:1] != "?":
                name, kw["type"] = t.group(1), t.group(2)
            committed = box in ("x", "X")
            for p in pieces[1:]:
                if not p:
                    continue
                kv = re.match(r"^([A-Za-z _]+?)\s*:\s*(.+)$", p)
                if kv:
                    key = kv.group(1).strip().lower()
                    for col, names in COLUMNS.items():
                        if key in names:
                            kw[col] = kv.group(2).strip()
                elif p.lower() in ("committed", "commit"):
                    committed = True
                elif p.lower() in ("uncommitted", "not committed"):
                    committed = False
                elif norm_type(p)[:1] != "?":
                    kw["type"] = p
                elif norm_priority(p) in D.PRIORITIES:
                    kw["priority"] = p
                elif D.QUARTER_RE.match(norm_quarter(p)):
                    kw["target_quarter"] = p
            if "committed" in kw:
                committed = D.truthy(kw.pop("committed"))
            rows.append(_row(i + 1, name=name, committed=committed, **kw))
        i += 1
    for r in rows:
        if r["type"].startswith("?"):
            problems.append(f"line {r['line']}: type '{r['type'][1:]}' is not one of {', '.join(D.TYPES)}")
        if r["priority"] and r["priority"] not in D.PRIORITIES:
            problems.append(f"line {r['line']}: priority '{r['priority']}' is not one of {', '.join(D.PRIORITIES)}")
            r["priority"] = ""
        if r["target_quarter"] and not D.QUARTER_RE.match(r["target_quarter"]):
            problems.append(f"line {r['line']}: quarter '{r['target_quarter']}' is not YYYY-Qn")
            r["target_quarter"] = ""
    return rows, problems


# ------------------------------------------------------------------ matching

def norm_name(s):
    s = re.sub(r"^\s*[A-Z][A-Z0-9]*-\d{3,}\b[\s:.-]*", "", str(s))
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return " ".join(w for w in s.split() if w not in STOP)


def _tokens(s):
    return s.split()


def _soft_f1(ta, tb):
    """Token overlap, where two words count as one when they differ only a little (ingest, ingestion)."""
    if not ta or not tb:
        return 0.0
    left, hits = list(tb), 0
    for t in ta:
        best = max(left, key=lambda u: difflib.SequenceMatcher(None, t, u).ratio(), default=None)
        if best is not None and difflib.SequenceMatcher(None, t, best).ratio() >= 0.8:
            hits += 1
            left.remove(best)
    return 2 * hits / (len(ta) + len(tb))


def score(a, b):
    """Half the characters' similarity and half the words': either alone over-rewards a shared word."""
    if not a or not b:
        return 0.0
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    return 0.5 * ratio + 0.5 * _soft_f1(_tokens(a), _tokens(b))


def _doc_type(d):
    return str(d.fm.get("candidate_type") or "") if d.is_candidate else d.type


def match(rows, docs):
    """[{row, result: exact|fuzzy|ambiguous|new|duplicate, doc, options, how, score}]."""
    pool = [d for d in docs if not d.archived and d.state not in ("archive", "archived") and d.kind]
    names = {id(d): norm_name(d.title) for d in pool}
    seen, out = {}, []
    for r in rows:
        key = (norm_name(r["name"]), r["type"])
        if key in seen:
            out.append({"row": r, "result": "duplicate", "doc": None, "options": [], "how": f"same as line {seen[key]}", "score": 1.0})
            continue
        seen[key] = r["line"]
        rtype = r["type"] if not r["type"].startswith("?") else ""
        idm = re.search(r"\b([A-Z][A-Z0-9]*-\d{3,})\b", r["name"]) or re.search(r"\b([A-Z][A-Z0-9]*-\d{3,})\b", r["ref"])
        if idm:
            hit = [d for d in pool if d.id == idm.group(1)]
            if len(hit) == 1:
                out.append({"row": r, "result": "exact", "doc": hit[0], "options": [], "how": "id", "score": 1.0})
                continue
        n = norm_name(r["name"])
        exact = [d for d in pool if names[id(d)] == n and n]
        if rtype and len(exact) > 1:
            exact = [d for d in exact if _doc_type(d) == rtype] or exact
        if len(exact) == 1:
            out.append({"row": r, "result": "exact", "doc": exact[0], "options": [], "how": "name", "score": 1.0})
            continue
        if len(exact) > 1:
            out.append({"row": r, "result": "ambiguous", "doc": None, "options": exact, "how": "same name", "score": 1.0})
            continue
        scored = []
        for d in pool:
            s = score(n, names[id(d)])
            dt = _doc_type(d)
            if rtype and dt and dt != rtype:
                s -= 0.15
            if s >= NEAR:
                scored.append((s, d))
        scored.sort(key=lambda x: (-x[0], x[1].rel))
        if not scored:
            out.append({"row": r, "result": "new", "doc": None, "options": [], "how": "", "score": 0.0})
            continue
        top = scored[0][0]
        rivals = [d for s, d in scored[1:] if s >= top - 0.05]
        if top >= MATCH and not rivals:
            out.append({"row": r, "result": "fuzzy", "doc": scored[0][1], "options": [], "how": "close name", "score": round(top, 2)})
        else:
            out.append({"row": r, "result": "ambiguous", "doc": None, "options": [d for _s, d in scored[:3]],
                        "how": "several close names" if rivals else "only somewhat close", "score": round(top, 2)})
    return out


# ------------------------------------------------------------------ placeholders

def slug(s, limit=60):
    s = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return (s[:limit].rsplit("-", 1)[0] if len(s) > limit else s) or "untitled"


def used_ids(docs, bindings, dtype):
    series = bindings.series(dtype)
    ids = {d.id for d in docs if d.id}
    reg = bindings.register(dtype)
    if reg and os.path.isfile(reg):
        with open(reg, encoding="utf-8", newline="") as f:
            rd = csv.reader(f)
            header = next(rd, [])
            col = header.index("id") if "id" in header else 0
            ids |= {r[col].strip() for r in rd if len(r) > col}
    return series, {i for i in ids if i.startswith(series + "-")}


def next_id(series, used):
    nums = [int(m.group(2)) for m in (D.ID_RE.match(i) for i in used) if m and m.group(1) == series]
    width = max([3] + [len(m.group(2)) for m in (D.ID_RE.match(i) for i in used) if m])
    return f"{series}-{(max(nums) + 1 if nums else 1):0{width}d}"


def placeholder_front_matter(row, dtype, pid, bindings, extra=None):
    title = f"{pid} {row['name']}"
    lines = []
    if dtype == "use-case":
        lines += ["kind: use-case", f"id: {pid}"]
    else:
        lines += ["kind: pattern", f"id: {pid}"]
    lines += [f"title: {D._yaml_scalar(title)}"]
    if dtype != "use-case":
        lines += [f"pattern_type: {dtype}"]
    if extra and extra.get("description"):
        lines += [f"description: {D._yaml_scalar(extra['description'])}"]
    lines += ["version: 0.1.0", "status: draft", f"created: {D.today()}", f"last_modified: {D.today()}",
              f"owner: {D._yaml_scalar(row.get('owner') or bindings.default_owner)}", "portfolio:",
              "  state: placeholder"]
    if row.get("priority"):
        lines.append(f"  priority: {row['priority']}")
    if row.get("target_quarter"):
        lines.append(f"  target_quarter: \"{row['target_quarter']}\"")
    lines.append(f"  committed: {'true' if row.get('committed') else 'false'}")
    lines.append(f"  since: {D.today()}")
    ref = row.get("ref") or f"backlog line {row['line']}"
    lines.append(f"  backlog_ref: {D._yaml_scalar(ref)}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def placeholder_body(template_text, pid, name):
    _fm, body = D.split(template_text)
    body = body.lstrip("\n")
    body = re.sub(r"^#\s+.*$", f"# {pid} {name}", body, count=1, flags=re.M)
    body = body.replace("<ID>", pid)
    note = (f"<!-- portfolio: a placeholder, made from the backlog on {D.today()}. The draft skill "
            f"writes a first draft from research; until then every section below is the template's. -->\n\n")
    first, _, rest = body.partition("\n")
    return f"{first}\n\n{note}{rest.lstrip(chr(10))}"


def append_register(bindings, dtype, pid, name, path):
    reg = bindings.register(dtype)
    if not reg or not os.path.isfile(reg):
        return ""
    with open(reg, encoding="utf-8", newline="") as f:
        header = next(csv.reader(f), [])
    values = {"id": pid, "type": dtype, "name": name, "status": "draft",
              "path": os.path.relpath(path, os.path.dirname(reg)).replace(os.sep, "/")}
    row = [values.get(h, "") for h in header]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerow(row)
    with open(reg, "rb") as f:
        data = f.read()
    with open(reg, "a", encoding="utf-8", newline="") as f:
        if data and not data.endswith(b"\n"):
            f.write("\n")
        f.write(buf.getvalue())
    return reg


def candidate_text(row):
    lines = ["---", "kind: candidate", f"title: {D._yaml_scalar(row['name'])}"]
    if row.get("type") and not row["type"].startswith("?"):
        lines.append(f"candidate_type: {row['type']}")
    lines += [f"created: {D.today()}"]
    p = []
    if row.get("priority"):
        p.append(f"  priority: {row['priority']}")
    if row.get("target_quarter"):
        p.append(f"  target_quarter: \"{row['target_quarter']}\"")
    p.append("  committed: false")
    if row.get("ref"):
        p.append(f"  backlog_ref: {D._yaml_scalar(row['ref'])}")
    lines += ["portfolio:"] + p + ["---", "", f"# {row['name']}", "",
                                   "A possible pattern, noted from the backlog. Say what problem it answers, and why it might be worth a pattern.", ""]
    return "\n".join(lines)
