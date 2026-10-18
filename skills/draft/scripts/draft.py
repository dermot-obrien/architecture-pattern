#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Draft a placeholder pattern from research, citing every source, for a person to review.

    python scripts/draft.py plan PLACEHOLDER [--out research.json] [--recorded FILE]
    python scripts/draft.py add-source research.json --url URL --title TITLE --excerpt TEXT
                                       [--publisher NAME] [--accessed DATE]
    python scripts/draft.py write PLACEHOLDER --research research.json --sections sections.md
                                  [--set KEY=VALUE ...] [--dry-run] [--author NAME]
    python scripts/draft.py check DRAFT [--research research.json]

Run from the workspace root. The agent does the judgement; this script does the parts that
must be exact.

plan        reads the placeholder (a document with portfolio.state placeholder), lists the
            template's sections to fill, suggests queries for online research, and gathers the
            repository's research: related signed documents and passages that use the
            placeholder's terms, each numbered R1, R2 and so on. It writes research.json
            (default: research.json beside the placeholder). --recorded merges web sources from a
            recorded research file instead of the agent searching: the offline mode.
add-source  records one web source the agent read, numbered W1, W2 and so on.
write       puts the agent's sections (a Markdown file of `## Heading` blocks, citing sources as
            [R1] or [W2]) into the placeholder's template, in place of those sections' guidance,
            and adds the Sources section and a link definition for every source. The draft is
            marked: status draft, portfolio.state draft, provenance ai-generated and ai-raw, a
            review banner, and a review notice under the title. Refuses a citation that names no
            source, a heading the template does not have, a document that is not a placeholder
            or a draft, and a draft missing a field its type requires once it is no longer a
            placeholder (pattern_scope; implements on a reference architecture; primary_actor,
            supports_outcome and success_criteria on a use case), which --set supplies.
check       confirms a draft carries every marking and that every citation resolves.

Exit 0: ok. Exit 1: problems, one line each. Exit 2: usage.
Standard library only; Python 3.11 or newer. Needs the portfolio skill installed beside it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: draft.py needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.environ.get("SKILL_DIR") or os.path.dirname(HERE))
SKILL_DIRS = (".agents/skills", ".claude/skills", ".github/skills", ".cursor/skills")


def _find_portfolio():
    cands = [os.path.join(os.path.dirname(SKILL_DIR), "portfolio")]
    cands += [os.path.join(p, "portfolio") for p in os.environ.get("AGENT_SKILLS_PATH", "").split(os.pathsep) if p]
    for base in (os.getcwd(), os.path.expanduser("~")):
        cands += [os.path.join(base, d, "portfolio") for d in SKILL_DIRS]
    for c in cands:
        if os.path.isfile(os.path.join(c, "scripts", "portfolio_lib", "docs.py")):
            return os.path.join(c, "scripts")
    return ""


_PF = _find_portfolio()
if not _PF:
    print("error: the portfolio skill is not installed beside draft, nor on AGENT_SKILLS_PATH; install it from "
          "https://github.com/dermot-obrien/architecture-pattern", file=sys.stderr)
    sys.exit(2)
sys.path.insert(0, _PF)
from portfolio_lib import backlog as B  # noqa: E402
from portfolio_lib import docs as D  # noqa: E402
from portfolio_lib.bindings import Bindings, UsageError  # noqa: E402

CITE_RE = re.compile(r"\[((?:R|W)\d+)\](?!\(|:)")
DECK_RE = re.compile(r"^\s*<!--\s*/?deck:(?!skip)[^>]*-->\s*$")
BANNER = "AI-generated draft for review. Check every claim against its source before relying on it."
NOTICE = ("> AI-generated draft, written from the research cited under Sources. It is for review, "
          "not for use: check each claim against its source, then clear `portfolio.state`.")
# What the continuum's schemas require of a document once it is more than a placeholder.
REQUIRED = {
    "architecture-pattern": ["pattern_scope"],
    "reference-architecture": ["pattern_scope", "implements"],
    "collaboration": ["pattern_scope"],
    "use-case": ["primary_actor", "supports_outcome", "success_criteria"],
}
SCOPES = ("problem", "domain", "capability-area", "platform", "hosting-profile", "epic")
STOP = B.STOP | {"using", "based", "model", "service", "system", "systems"}


class Problem(Exception):
    pass


def today():
    return D.today()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_doc(path, b):
    d = D.load(os.path.abspath(path), b.root, b.archive_dir)
    if d is None:
        raise UsageError(f"{path} carries no portfolio signature in its front matter")
    return d


def name_of(d):
    return re.sub(r"^\s*[A-Z][A-Z0-9]*-\d{3,}\s+", "", d.title)


def terms(text):
    words = re.findall(r"[a-z][a-z0-9-]{3,}", text.lower())
    out = []
    for w in words:
        for part in [w] + w.split("-"):
            if len(part) >= 4 and part not in STOP and part not in out:
                out.append(part)
    return out


# ------------------------------------------------------------------ plan

def template_sections(body):
    """The H2 headings of the placeholder, in order, except the ones a draft never writes."""
    out = []
    for line in body.splitlines():
        m = D.H2_RE.match(line)
        if m and m.group(1).strip().lower() not in ("sources", "candidate notes"):
            out.append(m.group(1).strip())
    return out


def repository_sources(doc, b, limit=12):
    """Related signed documents, then passages elsewhere that use the placeholder's terms."""
    name = name_of(doc)
    keys = terms(name)
    sources = []
    docs = D.discover(b.roots + ([b.archive_dir] if os.path.isdir(b.archive_dir) else []), b.root, b.archive_dir, b.exclude)
    related = []
    for d in docs:
        if os.path.abspath(d.path) == os.path.abspath(doc.path) or d.state == "placeholder":
            continue
        s = B.score(B.norm_name(name), B.norm_name(d.title))
        in_title = [k for k in keys if k in d.title.lower()]
        shared = [k for k in keys if k in (d.title + " " + d.summary).lower()]
        if s >= 0.5 or (in_title and len(keys) <= 2) or len(shared) >= 2:
            related.append((s + 0.1 * len(shared), d))
    for _s, d in sorted(related, key=lambda x: (-x[0], x[1].rel))[: limit // 2]:
        sources.append({"kind": "repository", "path": d.rel, "title": d.title,
                        "excerpt": d.summary, "why": "a related document" + (" (archived)" if d.archived else "")})
    # The placeholder's own candidate notes, when it was promoted from a candidate.
    notes = D.sections(doc.body).get("candidate notes")
    if notes and notes.strip():
        sources.append({"kind": "repository", "path": doc.rel + "#candidate-notes", "title": "Candidate notes",
                        "excerpt": re.sub(r"\s+", " ", notes).strip()[:400], "why": "the notes the candidate carried"})
    taken = {s["path"] for s in sources}
    if keys:
        for p in D.walk(b.roots, b.exclude):
            rel = os.path.relpath(p, b.root).replace(os.sep, "/")
            if rel in taken or os.path.abspath(p) == os.path.abspath(doc.path) or len(sources) >= limit:
                continue
            try:
                text = D.COMMENT_RE.sub("", D.split(read(p))[1])
            except (OSError, UnicodeDecodeError):
                continue
            for para in re.split(r"\n\s*\n", text):
                flat = re.sub(r"\s+", " ", para).strip()
                if flat.startswith(("#", "|", "```")) or len(flat) < 40:
                    continue
                low = flat.lower()
                hits = [k for k in keys if k in low]
                if len(hits) >= min(2, len(keys)):
                    sources.append({"kind": "repository", "path": rel, "title": D.first_h1(text) or rel,
                                    "excerpt": flat[:400], "why": "uses " + ", ".join(hits)})
                    taken.add(rel)
                    break
    for i, s in enumerate(sources, 1):
        s["id"] = f"R{i}"
    return sources


def cmd_plan(a, b):
    doc = load_doc(a.placeholder, b)
    if doc.state not in ("placeholder", "draft"):
        raise UsageError(f"{doc.rel} is not a placeholder (portfolio.state is {doc.state or 'unset'})")
    name = name_of(doc)
    type_word = {"architecture-pattern": "architecture pattern", "reference-architecture": "reference architecture",
                 "collaboration": "collaboration", "use-case": "use case"}.get(doc.type, "pattern")
    research = {
        "placeholder": doc.rel, "id": doc.id, "title": doc.title, "type": doc.type, "planned": today(),
        "sections": template_sections(doc.body),
        "queries": [f"{name} {type_word}", f"{name} architecture building blocks",
                    f"{name} trade-offs", f"{name} reference implementation" if doc.type == "reference-architecture"
                    else f"{name} scenarios"],
        "sources": repository_sources(doc, b),
    }
    if a.recorded:
        rec = json.loads(read(a.recorded))
        for s in rec.get("sources", []):
            if s.get("kind") == "web":
                _add_web(research, s)
    out = a.out or os.path.join(os.path.dirname(doc.path), "research.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(research, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"research: {os.path.relpath(out, b.root)}")
    print(f"sections to write: {', '.join(research['sections'])}")
    print("search online for:")
    for q in research["queries"]:
        print(f"  {q}")
    for s in research["sources"]:
        print(f"  [{s['id']}] {s['title']} ({s.get('path') or s.get('url')})")
    return 0


def _add_web(research, s):
    n = 1 + sum(1 for x in research["sources"] if x["id"].startswith("W"))
    if any(x.get("url") == s["url"] for x in research["sources"]):
        return next(x["id"] for x in research["sources"] if x.get("url") == s["url"])
    entry = {"id": f"W{n}", "kind": "web", "url": s["url"], "title": s["title"], "excerpt": s.get("excerpt", ""),
             "publisher": s.get("publisher", ""), "accessed": s.get("accessed") or today()}
    research["sources"].append(entry)
    return entry["id"]


def cmd_add_source(a, b):
    research = json.loads(read(a.research))
    if not re.match(r"^https?://", a.url):
        raise UsageError("--url is an http or https address")
    sid = _add_web(research, {"url": a.url, "title": a.title, "excerpt": a.excerpt, "publisher": a.publisher,
                              "accessed": a.accessed})
    with open(a.research, "w", encoding="utf-8") as f:
        json.dump(research, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(sid)
    return 0


# ------------------------------------------------------------------ write

def parse_sections(text):
    """{heading: content} from the agent's file, in order."""
    out, current, buf = {}, None, []
    fenced = False
    for line in text.splitlines():
        if D.FENCE_RE.match(line):
            fenced = not fenced
        m = None if fenced else D.H2_RE.match(line)
        if m:
            if current is not None:
                out[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf).strip()
    return out


def citations(text):
    clean = re.sub(r"```.*?```", "", text, flags=re.S)
    return CITE_RE.findall(clean)


def source_line(s, doc_dir, root):
    if s["kind"] == "web":
        bits = [s["title"]] + ([s["publisher"]] if s.get("publisher") else []) + [s["url"], f"accessed {s['accessed']}"]
        return f"- [{s['id']}] " + ", ".join(bits), f"[{s['id']}]: {s['url']}"
    path, frag = (s["path"].split("#", 1) + [""])[:2]
    rel = os.path.relpath(os.path.join(root, path), doc_dir).replace(os.sep, "/") + (f"#{frag}" if frag else "")
    return f"- [{s['id']}] {s['title']}, in this repository: `{s['path']}`", f"[{s['id']}]: {rel}"


def replace_sections(body, drafted):
    """The body with each drafted section's content in place of the template's, deck tags kept."""
    lines = body.splitlines()
    out, i = [], 0
    norm = {D._norm_heading(k): v for k, v in drafted.items()}
    fenced = False
    while i < len(lines):
        line = lines[i]
        if D.FENCE_RE.match(line):
            fenced = not fenced
        m = None if fenced else D.H2_RE.match(line)
        if m and D._norm_heading(m.group(1)) in norm:
            out.append(line)
            j = i + 1
            section = []
            f2 = False
            while j < len(lines):
                if D.FENCE_RE.match(lines[j]):
                    f2 = not f2
                if not f2 and (D.H2_RE.match(lines[j]) or D.H1_RE.match(lines[j])):
                    break
                section.append(lines[j])
                j += 1
            lead, trail = deck_tags(section)
            out.append("")
            out.extend(lead + ([""] if lead else []))
            out.append(norm[D._norm_heading(m.group(1))])
            out.append("")
            out.extend(trail + ([""] if trail else []))
            i = j
            continue
        out.append(line)
        i += 1
    return "\n".join(out).rstrip() + "\n"


def deck_tags(section):
    """(leading, trailing) one-line deck tags of a section, leaving out any inside a guidance comment.

    A tag after the section's last other line marks the next heading, so it stays at the end."""
    tags, depth = [], 0
    for i, ln in enumerate(section):
        st = ln.strip()
        if depth == 0 and DECK_RE.match(ln):
            tags.append(i)
        elif st.startswith("<!--") and "-->" not in st:
            depth += 1
        elif depth and "-->" in st:
            depth -= 1
    content = [i for i, ln in enumerate(section) if ln.strip() and i not in tags]
    last = max(content, default=-1)
    lead = [section[i] for i in tags if i < last]
    trail = [section[i] for i in tags if i > last]
    return lead, trail


def strip_old_sources(body):
    return re.split(r"^## Sources\s*$", body, maxsplit=1, flags=re.M)[0].rstrip() + "\n"


def cmd_write(a, b):
    doc = load_doc(a.placeholder, b)
    if doc.state not in ("placeholder", "draft"):
        raise UsageError(f"{doc.rel} is not a placeholder or a draft (portfolio.state is {doc.state or 'unset'}); "
                         "the draft skill never overwrites a reviewed document")
    research = json.loads(read(a.research))
    drafted = parse_sections(read(a.sections))
    sources = {s["id"]: s for s in research.get("sources", [])}
    problems, warnings = [], []
    if not drafted:
        problems.append(f"{a.sections} has no ## sections")
    known = {D._norm_heading(h) for h in template_sections(doc.body)}
    for h, text in drafted.items():
        if D._norm_heading(h) not in known:
            problems.append(f"## {h} is not a section of the template ({', '.join(template_sections(doc.body))})")
        cited = citations(text)
        for c in cited:
            if c not in sources:
                problems.append(f"## {h} cites [{c}], which is not in {a.research}")
        if not cited and len(re.sub(r"\s+", " ", text)) > 200:
            warnings.append(f"## {h} cites no source")
    used = {c for t in drafted.values() for c in citations(t)}
    for sid in sources:
        if sid not in used:
            warnings.append(f"[{sid}] {sources[sid]['title']} is not cited, so it is left out of Sources")
    if not used:
        problems.append("the draft cites no source: a draft from research cites what it drew on")
    sets = {}
    for kv in a.set or []:
        if "=" not in kv:
            problems.append(f"--set {kv}: expected KEY=VALUE")
            continue
        k, v = kv.split("=", 1)
        sets[k.strip()] = v.strip()
    fm_now = dict(doc.fm)
    fm_now.update(sets)
    missing = [k for k in REQUIRED.get(doc.type, []) if not fm_now.get(k) or fm_now.get(k) in ([], "[]")]
    if missing:
        problems.append("a draft is no longer a placeholder, so it needs " + ", ".join(missing)
                        + ": pass " + " ".join(f"--set {k}=..." for k in missing)
                        + (f" (pattern_scope is one of {', '.join(SCOPES)})" if "pattern_scope" in missing else ""))
    if fm_now.get("pattern_scope") and doc.kind == "pattern" and str(fm_now["pattern_scope"]) not in SCOPES:
        problems.append(f"pattern_scope {fm_now['pattern_scope']} is not one of {', '.join(SCOPES)}")
    for w in warnings:
        print(f"warn: {w}")
    if problems:
        for p in problems:
            print(f"error: {p}")
        return 1

    fm_text, body = D.split(read(doc.path))
    body = strip_old_sources(body)
    body = replace_sections(body, drafted)
    body = re.sub(r"<!-- portfolio: a placeholder.*?-->\n*", "", body, count=1, flags=re.S)
    if NOTICE not in body:
        body = re.sub(r"^(#\s+.+)$", lambda m: m.group(1) + "\n\n" + NOTICE, body, count=1, flags=re.M)
    cited = [sources[s] for s in sorted(used, key=lambda x: (x[0], int(x[1:])))]
    doc_dir = os.path.dirname(doc.path)
    entries = [source_line(s, doc_dir, b.root) for s in cited]
    body = body.rstrip() + "\n\n## Sources\n\n" + "\n".join(e[0] for e in entries) + "\n\n" + "\n".join(e[1] for e in entries) + "\n"
    text = f"---\n{fm_text}---\n{body}"
    refs = [{"type": "doc", "url": s["url"]} if s["kind"] == "web" else {"type": "source", "path": s["path"].split("#")[0]}
            for s in cited if s["kind"] == "web" or s["path"].split("#")[0] != doc.rel]
    for k, v in sets.items():
        text = _set_block(text, k, [f"{k}: {v if v[:1] in '[{' else D._yaml_scalar(v)}"])
    text = D.edit(text, top={"status": "draft", "last_modified": today()},
                  portfolio={"state": "draft", "since": today(),
                             "reason": "AI-generated draft from research; awaiting review"})
    text = _set_block(text, "provenance", [
        "provenance:", "  origin: ai-generated", "  review_state: ai-raw",
        f"  authored_by: {D._yaml_scalar(a.author or 'draft skill')}", f"  authored_at: {D._yaml_scalar(today() + 'T00:00:00Z')}"]
        + ([f"  task_ref: {D._yaml_scalar(doc.portfolio['backlog_ref'])}"] if doc.portfolio.get("backlog_ref") else []))
    text = _set_block(text, "banner", ["banner:", "  tone: warning", f"  text: {D._yaml_scalar(BANNER)}"])
    text = _set_block(text, "references", ["references:"] + [
        "  - { " + ", ".join(f"{k}: {D._yaml_scalar(v)}" for k, v in r.items()) + " }" for r in refs])
    if a.dry_run:
        sys.stdout.write(text)
        return 0
    with open(doc.path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"drafted {doc.rel}: {len(drafted)} sections, {len(cited)} sources cited")
    return 0


def _set_block(text, key, block_lines):
    fm_text, body = D.split(text)
    lines = fm_text.splitlines()
    span = D._top_key_span(lines, key)
    if span:
        lines[span[0]:span[1]] = block_lines
    else:
        lines.extend(block_lines)
    return "---\n" + "\n".join(lines) + "\n---\n" + body


# ------------------------------------------------------------------ check

def check_draft(path, b, research=None):
    doc = load_doc(path, b)
    p = []
    if doc.status.lower() != "draft":
        p.append(f"status is {doc.status or 'unset'}, not draft")
    if doc.state != "draft":
        p.append(f"portfolio.state is {doc.state or 'unset'}, not draft")
    prov = doc.fm.get("provenance") if isinstance(doc.fm.get("provenance"), dict) else {}
    if prov.get("origin") != "ai-generated":
        p.append("provenance.origin is not ai-generated")
    if prov.get("review_state") not in ("ai-raw", "ai-verified"):
        p.append("provenance.review_state is not ai-raw or ai-verified")
    if not isinstance(doc.fm.get("banner"), dict):
        p.append("no review banner")
    if NOTICE not in doc.body:
        p.append("no review notice under the title")
    secs = D.sections(doc.body)
    if "sources" not in secs:
        p.append("no ## Sources section")
    defined = set(re.findall(r"^\[((?:R|W)\d+)\]:\s+\S+", doc.body, re.M))
    listed = set(re.findall(r"^- \[((?:R|W)\d+)\]", secs.get("sources", ""), re.M))
    body_wo_sources = re.split(r"^## Sources\s*$", doc.body, maxsplit=1, flags=re.M)[0]
    used = set(citations(body_wo_sources))
    if not used:
        p.append("cites no source")
    for c in sorted(used - defined):
        p.append(f"[{c}] is cited but has no link definition")
    for c in sorted(used - listed):
        p.append(f"[{c}] is cited but not listed under Sources")
    if research:
        known = {s["id"] for s in json.loads(read(research)).get("sources", [])}
        for c in sorted(used - known):
            p.append(f"[{c}] is not in {research}")
    return doc, p


def cmd_check(a, b):
    doc, problems = check_draft(a.draft, b, a.research)
    for x in problems:
        print(f"error: {doc.rel}: {x}")
    if not problems:
        print(f"{doc.rel}: a marked draft; every citation resolves")
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="draft.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 1)[1])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("plan")
    s.add_argument("placeholder")
    s.add_argument("--out")
    s.add_argument("--recorded", help="a recorded research file whose web sources stand in for searching online")
    s = sub.add_parser("add-source")
    s.add_argument("research")
    s.add_argument("--url", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--excerpt", required=True)
    s.add_argument("--publisher", default="")
    s.add_argument("--accessed")
    s = sub.add_parser("write")
    s.add_argument("placeholder")
    s.add_argument("--research", required=True)
    s.add_argument("--sections", required=True)
    s.add_argument("--author")
    s.add_argument("--set", action="append", metavar="KEY=VALUE",
                   help="a front matter field the draft needs, such as pattern_scope=domain or implements=[AP-001]")
    s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("check")
    s.add_argument("draft")
    s.add_argument("--research")
    a = ap.parse_args(argv)
    try:
        b = Bindings(os.getcwd())
        return {"plan": cmd_plan, "add-source": cmd_add_source, "write": cmd_write, "check": cmd_check}[a.cmd](a, b)
    except (UsageError, OSError, json.JSONDecodeError) as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
