# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Documents found by their front matter signature, and edits to that front matter.

The signature is the continuum's front matter, and nothing else: a file or folder name is
never read to decide whether a document is a pattern.

    kind: pattern     with pattern_type architecture-pattern, reference-architecture or collaboration
    kind: use-case
    kind: candidate   a possible pattern, not formally one yet

A document written before `kind` was carried, with `pattern_type` and no `kind`, or with
`document_type: pattern` or `document_type: use-case`, is still a deliberate signature. It is found, marked legacy, and
`portfolio.py sign` adds the `kind`.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
from dataclasses import dataclass, field

from . import yamlish

PATTERN_TYPES = ("architecture-pattern", "reference-architecture", "collaboration")
TYPES = PATTERN_TYPES + ("use-case",)
SERIES = {"architecture-pattern": "AP", "reference-architecture": "RA", "collaboration": "CL", "use-case": "UC"}
LABELS = {
    "architecture-pattern": "Architecture patterns",
    "reference-architecture": "Reference architectures",
    "collaboration": "Collaborations",
    "use-case": "Use cases",
    "candidate": "Candidates",
}
STATES = ("placeholder", "draft", "needs-conversion", "proposed-deprecation", "archive", "archived")
PRIORITIES = ("high", "medium", "low", "none")
PORTFOLIO_KEYS = ("state", "priority", "target_quarter", "committed", "reason", "since",
                  "backlog_ref", "archived_from")
QUARTER_RE = re.compile(r"^\d{4}-Q[1-4]$")
ID_RE = re.compile(r"^([A-Z][A-Z0-9]*)-(\d{3,})$")
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$")
H2_RE = re.compile(r"^##\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
MARKDOWN = (".md", ".mdx")

# The four parts every type shares: a diagram, the boxes, the links between them, and the
# scenarios that walk across them. A heading may carry a number ("3. Building Blocks").
DEFAULT_FORM = {
    "architecture-pattern": {"diagram": ["Diagram"], "boxes": ["Building Blocks"],
                             "links": ["Interfaces"], "scenarios": ["Scenarios"]},
    "reference-architecture": {"diagram": ["Diagram"], "boxes": ["Building Blocks"],
                               "links": ["Interfaces"], "scenarios": ["Scenarios"]},
    "collaboration": {"diagram": ["Diagram"], "boxes": ["Participants"],
                      "links": ["Interactions"], "scenarios": ["Scenarios"]},
    "use-case": {"diagram": ["Diagram"], "boxes": ["Participants"],
                 "links": ["Interactions"], "scenarios": ["Scenarios"]},
}
TABLE_PARTS = ("boxes", "links")


def truthy(value) -> bool:
    return str(value).strip().lower() in ("true", "yes", "y", "1", "x", "committed")


def today() -> str:
    return os.environ.get("PORTFOLIO_TODAY") or _dt.date.today().isoformat()


# ------------------------------------------------------------------ front matter text

def split(text: str):
    """(front matter text or None, body). The front matter is the block between the first
    two `---` lines, which must open the file."""
    t = text[1:] if text.startswith("﻿") else text
    if not (t.startswith("---\n") or t.startswith("---\r\n")):
        return None, t
    lines = t.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return None, t


def parse(fm_text):
    try:
        data = yamlish.load(fm_text or "")
    except yamlish.YamlError as ex:
        return None, str(ex)
    if not isinstance(data, dict):
        return None, "front matter is not a mapping"
    return data, None


# ------------------------------------------------------------------ the document

@dataclass
class Doc:
    path: str                    # absolute
    rel: str                     # relative to the repository root, with /
    fm: dict
    body: str
    kind: str                    # pattern, use-case or candidate
    type: str                    # one of TYPES, or candidate, or "" when it cannot be told
    id: str = ""
    title: str = ""
    legacy: bool = False
    archived: bool = False       # it sits under the archive folder
    problems: list = field(default_factory=list)

    @property
    def portfolio(self) -> dict:
        p = self.fm.get("portfolio")
        return p if isinstance(p, dict) else {}

    @property
    def state(self) -> str:
        return str(self.portfolio.get("state") or "").strip().lower()

    @property
    def status(self) -> str:
        return str(self.fm.get("status") or "").strip()

    @property
    def summary(self) -> str:
        return summary(self.fm, self.body)

    @property
    def is_candidate(self) -> bool:
        return self.kind == "candidate"


def signature(fm: dict):
    """(kind, type, legacy) when the front matter carries the signature, else None."""
    kind = str(fm.get("kind") or "").strip().lower()
    ptype = str(fm.get("pattern_type") or "").strip().lower()
    if kind == "pattern":
        return "pattern", ptype if ptype in PATTERN_TYPES else "", False
    if kind == "use-case":
        return "use-case", "use-case", False
    if kind == "candidate":
        return "candidate", "candidate", False
    if kind:
        return None  # another kind of the continuum: an ABB, a capability and so on
    if ptype in PATTERN_TYPES:
        return "pattern", ptype, True
    dt = str(fm.get("document_type") or "").strip().lower()
    if dt == "use-case":
        return "use-case", "use-case", True
    if dt == "pattern":
        return "pattern", "", True  # the type follows from the identifier's series
    return None


def first_h1(body: str) -> str:
    fenced = False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            m = H1_RE.match(line)
            if m:
                return m.group(1).strip()
    return ""


def summary(fm: dict, body: str, limit: int = 220) -> str:
    """The description, else the first paragraph of prose after the title."""
    text = str(fm.get("description") or "").strip()
    if not text:
        clean = COMMENT_RE.sub("", body)
        para, fenced = [], False
        for line in clean.splitlines():
            s = line.strip()
            if FENCE_RE.match(line):
                fenced = not fenced
                continue
            if fenced:
                continue
            if not s:
                if para:
                    break
                continue
            if s.startswith(("#", "|", ">", "!", "<", "---", "- ", "* ", "```")) or re.match(r"^\d+\.\s", s):
                if para:
                    break
                continue
            para.append(s)
        text = " ".join(para)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0]
        text = cut.rstrip(",;:") + " ..."
    return text


def load(path: str, root: str, archive_dir: str | None = None):
    """The Doc at path, or None when it carries no signature."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    fm_text, body = split(text)
    if fm_text is None:
        return None
    fm, err = parse(fm_text)
    if fm is None:
        # A page whose front matter does not parse might be signed; say so rather than drop it.
        if re.search(r"^(kind|pattern_type|document_type)\s*:", fm_text, re.M):
            d = Doc(path, _rel(path, root), {}, body, "", "", problems=[f"front matter does not parse: {err}"])
            return d
        return None
    sig = signature(fm)
    if not sig:
        return None
    kind, dtype, legacy = sig
    title = str(fm.get("title") or "").strip() or first_h1(body) or os.path.splitext(os.path.basename(path))[0]
    did = str(fm.get("id") or "").strip()
    if not did and legacy:
        m = re.match(r"^([A-Z][A-Z0-9]*-\d{3,})\b", first_h1(body))
        did = m.group(1) if m else ""
    if kind == "pattern" and not dtype:
        m = ID_RE.match(did)
        dtype = {v: k for k, v in SERIES.items() if k in PATTERN_TYPES}.get(m.group(1), "") if m else ""
    d = Doc(path, _rel(path, root), fm, body, kind, dtype, did, title, legacy)
    if archive_dir:
        a = os.path.abspath(archive_dir)
        d.archived = os.path.abspath(path).startswith(a + os.sep)
    return d


def _rel(path, root) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


SKIP = {".git", "node_modules", ".docusaurus", "build", "dist", ".venv", "__pycache__", ".agents", ".claude"}


def walk(roots, exclude=(), skip_names=SKIP):
    excl = [os.path.abspath(e) for e in exclude]
    seen = set()
    for root in roots:
        if os.path.isfile(root):
            if root.endswith(MARKDOWN):
                seen.add(os.path.abspath(root))
                yield os.path.abspath(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in skip_names and os.path.abspath(os.path.join(dirpath, d)) not in excl)
            for name in sorted(filenames):
                if name.endswith(MARKDOWN):
                    p = os.path.abspath(os.path.join(dirpath, name))
                    if p not in seen:
                        seen.add(p)
                        yield p


def discover(roots, root, archive_dir=None, exclude=()):
    docs = []
    for p in walk(roots, exclude):
        d = load(p, root, archive_dir)
        if d is not None:
            docs.append(d)
    return docs


# ------------------------------------------------------------------ form

def _norm_heading(h: str) -> str:
    h = re.sub(r"^\s*(\d+(\.\d+)*\.?|[A-Z]\.)\s+", "", h)
    return re.sub(r"\s+", " ", h).strip().lower()


def sections(body: str) -> dict:
    """{normalised H2 heading: its content up to the next H2}."""
    out, current, buf, fenced = {}, None, [], False
    for line in body.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
        m = None if fenced else H2_RE.match(line)
        if m:
            if current is not None:
                out.setdefault(current, "\n".join(buf))
            current, buf = _norm_heading(m.group(1)), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out.setdefault(current, "\n".join(buf))
    return out


def has_table(content: str) -> bool:
    lines = [ln.strip() for ln in COMMENT_RE.sub("", content).splitlines()]
    for i in range(len(lines) - 2):
        if lines[i].startswith("|") and re.match(r"^\|?\s*:?-{3,}", lines[i + 1]) and lines[i + 2].startswith("|"):
            return True
    return False


def has_scenarios(content: str) -> bool:
    clean = COMMENT_RE.sub("", content)
    return bool(re.search(r"^###\s+\S", clean, re.M)) or has_table(clean)


def form_problems(doc: Doc, form: dict | None = None) -> list:
    """What keeps the document from the form its type expects: [] when it is in form."""
    if doc.is_candidate:
        return []
    if not doc.type:
        return ["the pattern type cannot be told: set pattern_type"]
    spec = (form or {}).get(doc.type) or DEFAULT_FORM[doc.type]
    secs = sections(doc.body)
    missing = []
    for part in ("diagram", "boxes", "links", "scenarios"):
        names = [_norm_heading(n) for n in spec.get(part, [])]
        found = next((secs[n] for n in names if n in secs), None)
        label = " or ".join(spec.get(part, [])) or part
        if found is None:
            missing.append(f"no ## {label} section")
        elif part in TABLE_PARTS and not has_table(found):
            missing.append(f"## {label} has no table")
        elif part == "scenarios" and not has_scenarios(found):
            missing.append(f"## {label} has no scenario")
    return missing


# ------------------------------------------------------------------ editing front matter

def _yaml_scalar(v) -> str:
    if v is True:
        return "true"
    if v is False:
        return "false"
    s = str(v)
    if s == "" or re.search(r"[:#\[\]{},&*!|>'\"%@`]|^\s|\s$|^(true|false|yes|no|null|~)$", s, re.I) \
            or QUARTER_RE.match(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _top_key_span(lines, key):
    """(start, end) of a top-level key and the lines that belong to it, or None."""
    pat = re.compile(rf"^{re.escape(key)}\s*:(\s|$)")
    for i, ln in enumerate(lines):
        if pat.match(ln):
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                # Indented lines, blank lines and a sequence at column 0 belong to the key.
                if nxt.strip() == "" or nxt.startswith((" ", "\t", "- ")) or nxt.strip() == "-":
                    j += 1
                    continue
                break
            # Do not swallow trailing blank lines.
            while j > i + 1 and lines[j - 1].strip() == "":
                j -= 1
            return i, j
    return None


def edit(text: str, top: dict | None = None, portfolio: dict | None = None) -> str:
    """Set top-level keys and portfolio keys, changing no other line.

    A value of None removes the key. The portfolio block is rewritten in block form, its
    keys in the standard's order, and dropped when it is left empty."""
    lead = "﻿" if text.startswith("﻿") else ""
    fm_text, body = split(text)
    if fm_text is None:
        fm_text, body = "", text[len(lead):]
    nl = "\r\n" if "\r\n" in fm_text else "\n"
    lines = fm_text.splitlines()
    for key, value in (top or {}).items():
        span = _top_key_span(lines, key)
        new = [] if value is None else [f"{key}: {_yaml_scalar(value)}"]
        if span:
            lines[span[0]:span[1]] = new
        elif new:
            lines.extend(new)
    if portfolio is not None:
        fm, _ = parse(nl.join(lines))
        current = dict((fm or {}).get("portfolio") or {}) if isinstance((fm or {}).get("portfolio"), dict) else {}
        for k, v in portfolio.items():
            if v is None:
                current.pop(k, None)
            else:
                current[k] = v
        order = [k for k in PORTFOLIO_KEYS if k in current] + [k for k in current if k not in PORTFOLIO_KEYS]
        block = ["portfolio:"] + [f"  {k}: {_yaml_scalar(_typed(k, current[k]))}" for k in order] if current else []
        span = _top_key_span(lines, "portfolio")
        if span:
            lines[span[0]:span[1]] = block
        else:
            lines.extend(block)
    return f"{lead}---{nl}{nl.join(lines)}{nl}---{nl}{body}"


def _typed(key, value):
    if key == "committed":
        return value if isinstance(value, bool) else truthy(value)
    return value
