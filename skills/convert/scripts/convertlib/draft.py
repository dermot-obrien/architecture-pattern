# SPDX-License-Identifier: Apache-2.0
"""Write a unit as a document of its type, from the template that type uses.

The template is the one the repository binds for the type, else the one the pattern or
use-case skill ships. Only the parts the unit knows are written: the front matter, the
H1, the opening section's summary, the image under Diagram, the boxes, links and
scenario tables, and the Catalogue Mapping. Every other section keeps the template's
guidance for the agent to complete. Source text that placed nowhere is kept at the end,
under headings that begin "From the source", and everything a reader was unsure of is
listed in a comment under the H1.
"""
from __future__ import annotations

import datetime
import json
import re

from .unit import box, slug

PROFILES = {
    "architecture-pattern": {
        "suite": "pattern", "series": "AP", "nodes": "Building Blocks", "edges": "Interfaces",
        "lead": ("Intent", "Context"), "skill": "pattern",
        "template": "assets/templates/architecture-pattern.md", "group": "Source",
        "label": "architecture pattern"},
    "reference-architecture": {
        "suite": "pattern", "series": "RA", "nodes": "Building Blocks", "edges": "Interfaces",
        "lead": ("Intent", "Context"), "skill": "pattern",
        "template": "assets/templates/reference-architecture.md", "group": "Source",
        "label": "reference architecture"},
    "use-case": {
        "suite": "use-case", "series": "UC", "nodes": "Participants", "edges": "Interactions",
        "lead": ("The solution in one sentence",), "skill": "use-case",
        "template": "assets/template.md", "group": "Kind", "label": "use case"},
    "collaboration": {
        "suite": "pattern", "series": "CL", "nodes": "Participants", "edges": "Interactions",
        "lead": ("Purpose",), "skill": "pattern",
        "template": "assets/templates/collaboration.md", "group": "Kind",
        "label": "collaboration"},
}

LOCAL = re.compile(r"^[0-9]{2}$")
EDGE_ID = re.compile(r"^IF-[0-9]{2,3}$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def cell(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).replace("|", "\\|").strip()


# ------------------------------------------------------------------ identifiers

def assign_ids(u, node_series=None):
    """Give every box, link and scenario the identifier the document will carry.

    A box keeps a catalogue identifier it was drawn with when it is in one of
    `node_series` (all series, when None), and a two-digit local id it was drawn with;
    every other box takes the next free local id. A link keeps an IF- identifier; every
    other link takes the next free one. Scenarios are S1, S2 and so on, in order."""
    used = set()
    for b in u["boxes"]:
        ident = b.get("id", "")
        if ident and not LOCAL.match(ident):
            prefix = ident.split("-", 1)[0]
            if node_series is not None and prefix not in node_series:
                b["note_id"] = ident
                b["id"] = ""
                continue
        if ident and ident not in used:
            used.add(ident)
        elif ident:
            b["note_id"] = ident
            b["id"] = ""
    n = 0
    for b in u["boxes"]:
        if not b.get("id"):
            n += 1
            while f"{n:02d}" in used:
                n += 1
            b["id"] = f"{n:02d}"
            used.add(b["id"])
    if len([b for b in u["boxes"] if LOCAL.match(b["id"])]) > 99:
        raise ValueError("more than 99 boxes need a local id")
    used_e = {lk["id"] for lk in u["links"] if EDGE_ID.match(lk.get("id") or "")}
    n = 0
    for lk in u["links"]:
        if not EDGE_ID.match(lk.get("id") or ""):
            n += 1
            while f"IF-{n:02d}" in used_e:
                n += 1
            lk["id"] = f"IF-{n:02d}"
            used_e.add(lk["id"])
    for i, sc in enumerate(u["scenarios"], 1):
        sc["key"] = f"S{i}"
    return u


def named(u, key) -> str:
    b = box(u, key)
    return f"{b['id']} {b['label']}" if b else ""


def link_id(u, key) -> str:
    return next((lk["id"] for lk in u["links"] if lk["key"] == key), "")


# ------------------------------------------------------------------ the template

def sections(lines) -> list:
    """[(level, heading, start, end)] of every heading outside code fences; end is the
    line of the next heading at the same level or above."""
    heads, fenced, comment = [], False, False
    for i, ln in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", ln):
            fenced = not fenced
        if "<!--" in ln and "-->" not in ln.split("<!--", 1)[1]:
            comment = True
        elif comment and "-->" in ln:
            comment = False
            continue
        if fenced or comment:
            continue
        m = HEADING.match(ln)
        if m:
            heads.append((len(m.group(1)), m.group(2).strip(), i))
    out = []
    for j, (lv, h, i) in enumerate(heads):
        end = len(lines)
        for lv2, _h2, i2 in heads[j + 1:]:
            if lv2 <= lv:
                end = i2
                break
        out.append((lv, h, i, end))
    return out


def uncommented(lines) -> list:
    """The lines outside HTML comments."""
    out, inside = [], False
    for ln in lines:
        rest, kept = ln, ""
        while rest:
            if inside:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    inside, rest = False, rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start < 0:
                    kept += rest
                    rest = ""
                else:
                    kept += rest[:start]
                    inside, rest = True, rest[start + 4:]
        if kept.strip():
            out.append(kept)
    return out


def find_section(lines, *names):
    want = [n.lower() for n in names]
    for lv, h, i, end in sections(lines):
        if h.lower() in want and lv >= 2:
            return lv, h, i, end
    return None


def table_span(lines, start, end):
    """(first, last + 1, header cells) of the first pipe table in lines[start:end]."""
    i = start
    while i < end:
        if lines[i].strip().startswith("|") and i + 1 < end and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            j = i + 2
            while j < end and lines[j].strip().startswith("|"):
                j += 1
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            return i, j, header, lines[i + 1]
        i += 1
    return None


def table_text(header, rule, rows) -> list:
    out = ["| " + " | ".join(header) + " |", rule]
    for r in rows:
        out.append("| " + " | ".join(cell(x) for x in r) + " |")
    return out


def _col(header, *names):
    for i, h in enumerate(header):
        if any(h.lower().startswith(n) for n in names):
            return i
    return None


def node_rows(u, header, profile) -> list:
    rows = []
    gi = _col(header, profile["group"].lower())
    ri = _col(header, "role", "description", "what")
    re_i = _col(header, "realises")
    for b in u["boxes"]:
        r = [""] * len(header)
        r[0] = f"{b['id']} {b['label']}"
        desc = b.get("description") or "TBD"
        if ri is not None:
            r[ri] = desc
        elif len(header) > 1:
            r[1] = desc
        if gi is not None:
            if profile["group"] == "Kind":
                r[gi] = b.get("kind") or default_kind(b, profile)
            else:
                r[gi] = b.get("container") or "loose"
        if re_i is not None:
            r[re_i] = "TBD"
        rows.append(r)
    return rows


def default_kind(b, profile) -> str:
    if profile["label"] == "use case":
        return "actor" if b.get("kind") == "actor" else "solution"
    return "participant"


def edge_rows(u, header) -> list:
    rows = []
    pi, ci = _col(header, "provider"), _col(header, "consumer")
    ui = _col(header, "purpose", "label")
    for lk in u["links"]:
        r = [""] * len(header)
        r[0] = lk["id"]
        if pi is not None:
            r[pi] = named(u, lk["source"])
        if ci is not None:
            r[ci] = named(u, lk["target"])
        if ui is not None:
            purpose = lk.get("label") or "TBD"
            if lk.get("description"):
                purpose = f"{purpose} ({lk['description']})"
            r[ui] = purpose
        rows.append(r)
    return rows


def step_rows(u, sc, header) -> list:
    rows = []
    si, ai, ti = _col(header, "step"), _col(header, "actor"), _col(header, "target")
    xi, ii = _col(header, "action"), _col(header, "interface")
    for st in sc["steps"]:
        r = [""] * len(header)
        if si is not None:
            r[si] = str(st["step"])
        if ai is not None:
            r[ai] = named(u, st["actor"]) or "TBD"
        if ti is not None:
            r[ti] = named(u, st["target"])
        if xi is not None:
            r[xi] = st.get("action") or "TBD"
        if ii is not None:
            r[ii] = link_id(u, st.get("link", ""))
        rows.append(r)
    return rows


# ------------------------------------------------------------------ front matter

def set_key(fm_lines, key, value_lines):
    """Replace a top-level key's block in front matter lines, or append it."""
    out, i, done = [], 0, False
    while i < len(fm_lines):
        ln = fm_lines[i]
        if re.match(rf"^{re.escape(key)}\s*:", ln):
            j = i + 1
            while j < len(fm_lines) and (fm_lines[j].startswith((" ", "\t")) or not fm_lines[j].strip()):
                j += 1
            if not done:
                out += value_lines
                done = True
            i = j
            continue
        out.append(ln)
        i += 1
    if not done:
        out += value_lines
    return out


# The portfolio discovers a document by its front matter alone, never by its file or
# folder name, so every document convert writes carries this signature, and it is
# written here and nowhere else.
SIGNATURE_KEYS = ("kind", "id", "title", "pattern_type", "pattern_scope", "candidate_type",
                  "status", "document_type")


def scope_of(u) -> str:
    """The pattern_scope to write: the unit's own, else problem for a small design and
    domain for a larger one, which the conversion notes ask the author to confirm."""
    return u.get("scope") or ("problem" if len(u["boxes"]) <= 8 else "domain")


def signature(kind, ident, title, type_name="", scope="", portfolio=None) -> list:
    """The front matter lines that say what a document is.

    kind is pattern, use-case or candidate. A pattern names its pattern_type and
    pattern_scope; a candidate may name the type it is expected to become. `portfolio`
    is the optional portfolio block, such as {"state": "needs-conversion", ...}, left
    out when the document is live with nothing pending."""
    out = [f"kind: {kind}"]
    if ident:
        out.append(f"id: {ident}")
    out.append(f'title: "{title}"')
    if kind == "pattern":
        out += [f"pattern_type: {type_name}", f"pattern_scope: {scope}"]
    elif kind == "candidate" and type_name:
        out.append(f"candidate_type: {type_name}")
    # Lowercase, as the continuum envelope's status enum is.
    out.append("status: draft")
    if kind == "use-case":
        out.append("document_type: use-case")
    if portfolio:
        out.append("portfolio:")
        out += [f"  {k}: {v}" for k, v in portfolio.items()]
    return out


def provenance(sources) -> list:
    return (["provenance:", "  origin: ai-generated", "  review_state: ai-raw",
             "converted_from:"] + [f'  - "{s}"' for s in sources])


def front_matter(lines, u, ident, type_name, profile, sources, today):
    if not lines or lines[0].strip() != "---":
        lines = ["---", "---"] + lines
    end = next(i for i, ln in enumerate(lines[1:], 1) if ln.strip() == "---")
    fm, body = lines[1:end], lines[end + 1:]
    fm = [ln for ln in fm if not ln.lstrip().startswith("#")]
    for key in SIGNATURE_KEYS + ("portfolio", "provenance", "converted_from"):
        fm = drop_key(fm, key)
    fm = set_key(fm, "last_modified", [f"last_modified: {today}"])
    for key in ("realises", "implements", "realised_by", "former_ids"):
        if any(re.match(rf"^{key}\s*:", ln) for ln in fm):
            fm = set_key(fm, key, [f"{key}: []"])
    if any(re.match(r"^flows\s*:", ln) for ln in fm):
        fm = set_key(fm, "flows", ["flows: []"])
    if any(re.match(r"^references\s*:", ln) for ln in fm):
        fm = set_key(fm, "references", ["references: []"])
    if any(re.match(r"^sidebar_label\s*:", ln) for ln in fm):
        fm = set_key(fm, "sidebar_label", [f"sidebar_label: \"{u['name']}\""])
    fm = set_key(fm, "model", ["model:", "  diagram: components.drawio"])
    kind = "pattern" if profile["suite"] == "pattern" else "use-case"
    head = signature(kind, ident, u["name"], type_name, scope_of(u))
    return ["---"] + head + fm + provenance(sources) + ["---"] + body


def drop_key(fm_lines, key):
    """Front matter lines without a top-level key's block."""
    out, skipping = [], False
    for ln in fm_lines:
        if re.match(rf"^{re.escape(key)}\s*:", ln):
            skipping = True
            continue
        if skipping and (ln.startswith((" ", "\t")) or not ln.strip()):
            continue
        skipping = False
        out.append(ln)
    return out


def candidate(u, type_name, sources, reason, today) -> str:
    """A placeholder for a source that could not be converted yet, marked so the
    portfolio's tagging finds it: kind candidate, portfolio state needs-conversion."""
    fm = signature("candidate", "", u["name"], type_name, portfolio={
        "state": "needs-conversion", "reason": f'"{reason}"', "since": today})
    body = [f"# {u['name']}", "",
            "Not converted yet. " + reason[:1].upper() + reason[1:] + ".", ""]
    if u.get("summary"):
        body += [u["summary"], ""]
    return "\n".join(["---"] + fm + provenance(sources) + ["---", ""] + body)


# ------------------------------------------------------------------ the document

def review_comment(u) -> list:
    items = []
    if u.get("extraction") == "agent":
        items.append("Drafted from an image: every box, line and step is a reading of the picture.")
    for b in u["boxes"]:
        if b.get("uncertain"):
            items.append(f"Box {b['id']} {b['label']}: {b['uncertain']}.")
        if b.get("note_id"):
            items.append(f"Box {b['id']} {b['label']} was drawn as {b['note_id']}, which this "
                         "repository's binding does not read; it has a local id until mapped.")
    for lk in u["links"]:
        if lk.get("uncertain"):
            items.append(f"Interface {lk['id']} ({named(u, lk['source'])} to "
                         f"{named(u, lk['target'])}): {lk['uncertain']}.")
    for sc in u["scenarios"]:
        for st in sc["steps"]:
            if st.get("uncertain"):
                items.append(f"{sc['key']} step {st['step']}: {st['uncertain']}.")
    if u.get("_scope_note"):
        items.append(u["_scope_note"])
    items.append("Provider and Consumer follow each arrow's direction on the source "
                 "diagram; swap any where the arrow showed a call rather than what is provided.")
    items += [n[:1].upper() + n[1:] + ("" if n.endswith(".") else ".") for n in u.get("notes", [])]
    out = ["<!--", "CONVERSION NOTES. Review each, then delete this comment.", ""]
    out += [f"- {x}" for x in items]
    out += ["-->"]
    return out


def render(template_text, u, ident, type_name, sources, today=None) -> str:
    profile = PROFILES[type_name]
    today = today or datetime.date.today().isoformat()
    if profile["suite"] == "pattern" and not u.get("scope"):
        u["_scope_note"] = (f"pattern_scope is {scope_of(u)}, from the number of boxes; set it to "
                            "problem, domain, capability-area, platform, hosting-profile or epic.")
    lines = template_text.splitlines()
    lines = front_matter(lines, u, ident, type_name, profile, sources, today)

    # The H1, and the template's placeholder identifier wherever it appears.
    for i, ln in enumerate(lines):
        if re.match(r"^#\s+", ln):
            lines[i] = f"# {ident} {u['name']}"
            lines[i + 1:i + 1] = [""] + review_comment(u)
            break
    text = "\n".join(lines)
    text = text.replace("<ID>", ident)
    lines = text.splitlines()

    def replace_table(names, rows_fn):
        sec = find_section(lines, *names)
        if not sec:
            return False
        span = table_span(lines, sec[2] + 1, sec[3])
        if not span:
            lines[sec[3]:sec[3]] = []
            return False
        a, b, header, rule = span
        lines[a:b] = table_text(header, rule, rows_fn(header))
        return True

    if not replace_table((profile["nodes"],), lambda h: node_rows(u, h, profile)):
        raise ValueError(f"the template has no {profile['nodes']} table")
    if not replace_table((profile["edges"],), lambda h: edge_rows(u, h)):
        raise ValueError(f"the template has no {profile['edges']} table")

    # Scenarios: everything from the first ### under the section is replaced.
    sec = find_section(lines, "Scenarios")
    if sec and u["scenarios"]:
        sub = [s for s in sections(lines) if sec[2] < s[2] < sec[3] and s[0] > sec[0]]
        start = sub[0][2] if sub else sec[3]
        span = table_span(lines, start, sec[3])
        header, rule = (span[2], span[3]) if span else (
            ["Step", "Actor", "Target", "Action", "Interface"], "|---:|---|---|---|---|")
        block = []
        for sc in u["scenarios"]:
            block += [f"### {sc['key']} {sc.get('name') or 'Scenario'}", ""]
            if sc.get("from") and sc["from"] != "diagram":
                block += [f"<!-- convert: read from the {sc['from'].replace('text: ', 'text, a ')} -->", ""]
            block += table_text(header, rule, step_rows(u, sc, header)) + [""]
        lines[start:sec[3]] = block
    elif sec:
        # The template's example scenarios would be read as real ones; the source shows
        # no sequence, so they go, and the agent writes one.
        sub = [s for s in sections(lines) if sec[2] < s[2] < sec[3] and s[0] > sec[0]]
        if sub:
            lines[sub[0][2]:sec[3]] = []
        lines[sec[2] + 1:sec[2] + 1] = ["", "<!-- convert: the source shows no sequence. Write "
                                        "at least one scenario, S1, from what the source says "
                                        "happens. -->"]

    # The opening section: the source's own summary under its heading.
    if u.get("summary"):
        sec = find_section(lines, *profile["lead"])
        if sec:
            lines[sec[2] + 1:sec[2] + 1] = [""] + u["summary"].split("\n")

    # The structure view under Diagram.
    sec = find_section(lines, "Diagram")
    if sec and not any("components.svg)" in ln and ln.lstrip().startswith("![")
                       for ln in uncommented(lines[sec[2]:sec[3]])):
        at = sec[3]
        while at > sec[2] + 1 and not lines[at - 1].strip():
            at -= 1
        lines[at:at] = ["", f"![{ident} {u['name']}](./components.svg)"]

    # Catalogue Mapping: a gap row for every local box, until someone maps it.
    local = [b for b in u["boxes"] if LOCAL.match(b["id"])]
    rows = [[b["id"], "", "gap"] for b in local]
    sec = find_section(lines, "Catalogue Mapping")
    if sec:
        span = table_span(lines, sec[2] + 1, sec[3])
        if span:
            if rows:
                lines[span[0]:span[1]] = table_text(span[2], span[3], rows)
            else:
                lines[span[0]:span[1]] = []
    elif rows:
        while lines and not lines[-1].strip():
            lines.pop()
        lines += ["", "## Catalogue Mapping", "",
                  "<!-- What each local id realises in the building block catalogue: "
                  "realises, partial or gap. -->", ""]
        lines += table_text(["Local ID", "Maps To", "Relationship"], "|---|---|---|", rows)

    # Text from the source that placed nowhere, kept for the agent to fold in.
    if u.get("sections"):
        while lines and not lines[-1].strip():
            lines.pop()
        lines += ["", "## Notes from the source", "",
                  "<!-- convert: text from the source that was not placed above. Fold it "
                  "into the sections it belongs in, then delete this section. -->"]
        for s in u["sections"]:
            lines += ["", f"### From the source: {s['heading']}", "", s["text"].strip()]
    return "\n".join(lines).rstrip() + "\n"


def folder_name(ident, name) -> str:
    return f"{ident}-{slug(name)}"


def model_toml(u, profile) -> str:
    """A binding beside the document, for a workspace whose own does not read its tables."""
    prefixes = sorted({b["id"].split("-", 1)[0] for b in u["boxes"] if "-" in b["id"]}
                      | {"ABB", "SBB"})
    attrs = [f"{p.lower()}_id" for p in prefixes]
    node_pattern = "(" + "|".join(prefixes) + r")-[0-9]{2,4}(\.[0-9]+)?"
    node_col = "Building Block" if profile["nodes"] == "Building Blocks" else "Participant"
    group_attr = "pattern" if profile["group"] == "Source" else "kind"
    return f'''bindingsVersion = "1.0"

# Written by the convert skill, so this document's tables read without a workspace
# binding. A workspace whose .agents/skill-bindings.toml maps these sections can delete it.

[model]
node_id_attrs = {json.dumps(attrs)}
edge_id_attr  = "iface_id"
group_attr    = "{group_attr}"
local_pattern = '[0-9]{{2}}'
local_attr    = "local_id"

[[markdown.tables]]
section    = "{profile['nodes']}"
entity     = "node"
id_pattern = '{node_pattern}'
columns    = {{ id = "{node_col}", label = "{node_col}", group = "{profile['group']}" }}

[[markdown.tables]]
section    = "{profile['edges']}"
entity     = "edge"
id_pattern = 'IF-[0-9]{{2,3}}'
columns    = {{ id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }}

[markdown.scenarios]
section         = "Scenarios"
heading_pattern = '^(S[0-9]+)\\b[\\s:.-]*(.*)$'
columns         = {{ step = "Step", actor = "Actor", action = "Action", edge = "Interface", target = "Target" }}

[rules]
node_id_mismatch = "warn"
edge_missing_id  = "warn"
'''
