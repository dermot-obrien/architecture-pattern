#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""The pattern portfolio: find every pattern by its front matter signature, list it, tag it,
archive it, and turn a backlog into placeholders.

    python scripts/portfolio.py discover   [--json]
    python scripts/portfolio.py inventory  [--format md|html|json] [--out FILE] [--include-archived]
    python scripts/portfolio.py check      [--json]
    python scripts/portfolio.py tag        [--dry-run] [--json]
    python scripts/portfolio.py tag PATH... --state STATE [--reason TEXT] [--dry-run]
    python scripts/portfolio.py tag PATH... --clear [--dry-run]
    python scripts/portfolio.py sign       [--dry-run]
    python scripts/portfolio.py archive    [--dry-run] [--rewrite-links] [--stub]
    python scripts/portfolio.py backlog FILE [--dry-run] [--default-type TYPE] [--update]
                                             [--candidates] [--report FILE] [--json]

Run from the workspace root. Bindings are [suite.portfolio] of .agents/skill-bindings.toml,
found by searching upward; [suite.pattern] and [suite.use-case] say where new documents go,
their series and their templates. With no binding file, the repository is the nearest
folder holding .git, and every default applies.

A document is in the portfolio only when its front matter says so: kind pattern (with
pattern_type architecture-pattern, reference-architecture or collaboration), kind use-case,
or kind candidate. File and folder names are never read.

discover   lists the signed documents.
inventory  writes the summary page to --out, else [suite.portfolio] inventory, else stdout
           (--out - is stdout). The format follows the file's extension, or --format.
check      validates signatures and portfolio blocks. Exit 1 on an error.
tag        with no path, tags what the documents show: needs-conversion when a document is
           not in the form its type expects, proposed-deprecation when its status, its
           superseded_by, its valid_until or its age says so. It clears needs-conversion from a
           document now in form, and never overrides a state a person set. With paths, sets or
           clears the state you give.
sign       adds kind to a legacy document that carries pattern_type, or document_type use-case,
           but no kind.
archive    moves every document marked portfolio.state archive into archiveDir, keeping its
           place in the tree, with git mv where git tracks it, then marks it archived. Links that
           the move would break are reported; --rewrite-links rewrites them, --stub (or
           [suite.portfolio] stubs) leaves a page saying where it went. Idempotent.
backlog    matches each row of a backlog against the portfolio and reports what matched, what is
           new and what is ambiguous. A committed new row becomes a placeholder; a committed row
           matching a candidate promotes it. --update copies a row's priority, quarter and
           commitment onto the document it matched; --candidates makes uncommitted new rows into
           candidate pages.

Exit 0: ok. Exit 1: errors found, or problems in the backlog. Exit 2: usage or bindings.
Standard library only; Python 3.11 or newer.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: portfolio.py needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SKILL_DIR = os.path.abspath(os.environ.get("SKILL_DIR") or os.path.dirname(HERE))

from portfolio_lib import backlog as B  # noqa: E402
from portfolio_lib import docs as D  # noqa: E402
from portfolio_lib import inventory as I  # noqa: E402
from portfolio_lib import lifecycle as L  # noqa: E402
from portfolio_lib.bindings import Bindings, UsageError  # noqa: E402

SKILL_DIRS = (".agents/skills", ".claude/skills", ".github/skills", ".cursor/skills")


def find_skill(name, root) -> str:
    """The installed folder of a sibling skill, or ""."""
    cands = [os.path.join(os.path.dirname(SKILL_DIR), name)]
    cands += [os.path.join(p, name) for p in os.environ.get("AGENT_SKILLS_PATH", "").split(os.pathsep) if p]
    for base in (root, os.path.expanduser("~")):
        cands += [os.path.join(base, d, name) for d in SKILL_DIRS]
    cands.append(os.path.join(os.path.expanduser("~"), ".copilot", "skills", name))
    return next((c for c in cands if os.path.isfile(os.path.join(c, "SKILL.md"))), "")


def template_for(b: Bindings, dtype) -> str:
    own = b.template(dtype)
    pattern = find_skill("pattern", b.root)
    if own.startswith("builtin:"):
        own = os.path.join(pattern, "assets", "templates", own[len("builtin:"):] + ".md") if pattern else ""
    if own:
        if not os.path.isfile(own):
            raise UsageError(f"the template {own}, bound for {dtype}, does not exist")
        return own
    if dtype == "use-case":
        uc = find_skill("use-case", b.root)
        if uc:
            return os.path.join(uc, "assets", "template.md")
        raise UsageError("no use case template: bind [suite.use-case] template, or install the use-case skill")
    if pattern and os.path.isfile(os.path.join(pattern, "assets", "templates", f"{dtype}.md")):
        return os.path.join(pattern, "assets", "templates", f"{dtype}.md")
    fallback = os.path.join(SKILL_DIR, "assets", f"{dtype}.md")
    if os.path.isfile(fallback):
        return fallback
    if pattern:
        return os.path.join(pattern, "assets", "template.md")
    raise UsageError(f"no template for {dtype}: bind one, or install the pattern skill")


def load_docs(b: Bindings):
    roots = list(b.roots)
    if os.path.isdir(b.archive_dir) and not any(os.path.abspath(b.archive_dir).startswith(os.path.abspath(r) + os.sep) for r in roots):
        roots.append(b.archive_dir)
    return D.discover(roots, b.root, b.archive_dir, b.exclude)


def emit(obj, as_json, text_lines):
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        for ln in text_lines:
            print(ln)


# ------------------------------------------------------------------ commands

def cmd_discover(a, b):
    docs = load_docs(b)
    rows = [{"path": d.rel, "kind": d.kind, "type": d.type, "id": d.id, "title": d.title, "status": d.status,
             "state": d.state, "legacy": d.legacy, "archived": d.archived, "problems": d.problems} for d in docs]
    lines = [f"{r['id'] or '-':8} {r['type'] or r['kind'] or '?':24} {r['state'] or '':22} {r['path']}"
             + ("  (legacy signature)" if r["legacy"] else "") for r in rows]
    lines.append(f"{len(rows)} signed documents")
    emit(rows, a.json, lines)
    return 0


def cmd_inventory(a, b):
    docs = load_docs(b)
    out = None if a.out == "-" else (a.out or b.inventory)
    ext = os.path.splitext(out)[1].lstrip(".").lower() if out else "md"
    fmt = a.format or {"htm": "html", "mdx": "md", "markdown": "md"}.get(ext, ext)
    if fmt not in ("md", "html", "json"):
        raise UsageError(f"unknown format {fmt}: md, html or json")
    inv = I.build(docs, out, b.link_base, a.include_archived)
    text = I.render(inv, fmt, a.title)
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
        old = open(out, encoding="utf-8").read() if os.path.isfile(out) else None
        if old != text:
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"inventory: {os.path.relpath(out, b.root)} ({sum(len(g['rows']) for g in inv['groups'])} documents, "
              f"{len(inv['candidates'])} candidates){'' if old != text else ', unchanged'}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


def cmd_check(a, b):
    errors, warnings = L.check(load_docs(b), b)
    emit({"errors": errors, "warnings": warnings}, a.json,
         [f"error: {e}" for e in errors] + [f"warn: {w}" for w in warnings]
         + [f"{len(errors)} errors, {len(warnings)} warnings"])
    return 1 if errors else 0


def cmd_tag(a, b):
    docs = load_docs(b)
    if a.paths:
        if not (a.state or a.clear):
            raise UsageError("tag with paths needs --state STATE or --clear")
        if a.state and a.state not in D.STATES:
            raise UsageError(f"--state is one of {', '.join(D.STATES)}")
        by_path = {os.path.abspath(d.path): d for d in docs}
        plan = []
        for p in a.paths:
            ap = os.path.abspath(p)
            if os.path.isdir(ap):
                ap = next((x for x in (os.path.join(ap, "index.md"), os.path.join(ap, "index.mdx")) if x in by_path), ap)
            d = by_path.get(ap)
            if d is None:
                raise UsageError(f"{p} carries no portfolio signature in its front matter, so it cannot be tagged")
            if d.is_candidate and not (a.clear or a.state == "needs-conversion"):
                raise UsageError(f"{p} is a candidate, whose only state is needs-conversion; promote it from the backlog")
            ch = {"state": None, "reason": None, "since": None} if a.clear else \
                {"state": a.state, "reason": a.reason or None, "since": D.today()}
            plan.append((d, ch, a.reason or ("cleared" if a.clear else "set by hand")))
    else:
        plan = L.plan_tags(docs, b.form, b.stale_after_days)
    rows = [{"path": d.rel, "id": d.id, "from": d.state, "to": ch.get("state") or "", "why": why} for d, ch, why in plan]
    if not a.dry_run:
        for d, ch, _ in plan:
            L.apply_portfolio(d, ch)
    verb = "would tag" if a.dry_run else "tagged"
    emit(rows, a.json, [f"{verb} {r['path']}: {r['from'] or '(none)'} -> {r['to'] or '(none)'}: {r['why']}" for r in rows]
         + [f"{len(rows)} changes{' planned' if a.dry_run else ''}"])
    return 0


def cmd_sign(a, b):
    plan = L.plan_sign(load_docs(b))
    for d, top in plan:
        if not a.dry_run:
            L.apply_sign(d, top)
        print(f"{'would sign' if a.dry_run else 'signed'} {d.rel}: " + ", ".join(f"{k}: {v}" for k, v in top.items()))
    print(f"{len(plan)} legacy documents{' to sign' if a.dry_run else ' signed'}")
    return 0


def cmd_archive(a, b):
    docs = load_docs(b)
    moves, problems = L.plan_archive(docs, b)
    links = L.links_affected(moves, b) if moves else []
    stubs = a.stub or b.stubs
    root = b.root
    rel = lambda p: os.path.relpath(p, root).replace(os.sep, "/")  # noqa: E731
    for mv in moves:
        print(f"{'would archive' if a.dry_run else 'archive'} {rel(mv['src'])}{'/' if mv['folder'] else ''} -> {rel(mv['dest'])}")
    for lk in links:
        what = "rewrite" if a.rewrite_links else "breaks"
        print(f"  link {what}: {rel(lk['file'])}:{lk['line']} {lk['target']} -> {lk['new_target']}"
              + ("" if lk["inbound"] else " (in the archived page)"))
    for p in problems:
        print(f"error: {p}")
    if not moves:
        print("nothing to archive")
    elif not a.dry_run:
        L.apply_archive(moves, links, b, rewrite=a.rewrite_links, stubs=stubs)
        if links and not a.rewrite_links and not stubs:
            print(f"warn: {len(links)} links now point at the old place; rerun with --rewrite-links on the next archive, or fix them by hand")
    return 1 if problems else 0


def cmd_backlog(a, b):
    if not os.path.isfile(a.file):
        raise UsageError(f"{a.file} does not exist")
    with open(a.file, encoding="utf-8") as f:
        text = f.read()
    rows, problems = B.parse(text, "csv" if a.file.lower().endswith(".csv") else None)
    docs = load_docs(b)
    results = B.match(rows, docs)
    default_type = B.norm_type(a.default_type)
    if default_type.startswith("?"):
        raise UsageError(f"--default-type is one of {', '.join(D.TYPES)}")
    minted = {}
    actions = []
    for res in results:
        r, doc = res["row"], res["doc"]
        rtype = r["type"] if r["type"] and not r["type"].startswith("?") else ""
        res["action"] = ""
        if r["type"].startswith("?"):
            res["action"] = "none: unknown type"
            continue
        if res["result"] in ("exact", "fuzzy"):
            if doc.is_candidate and r["committed"]:
                dtype = rtype or str(doc.fm.get("candidate_type") or "") or default_type
                pid = _mint(b, docs, dtype, minted)
                dest = os.path.join(b.output_dir(dtype), f"{pid}-{B.slug(r['name'])}", "index.md")
                res["action"] = f"promote to {pid} at {os.path.relpath(dest, b.root)}"
                actions.append(("promote", res, dtype, pid, dest))
            else:
                diffs = {}
                for k in ("priority", "target_quarter"):
                    if r[k] and str(doc.portfolio.get(k) or "") != r[k]:
                        diffs[k] = r[k]
                if r["committed"] != D.truthy(doc.portfolio.get("committed")) and (r["committed"] or "committed" in doc.portfolio):
                    diffs["committed"] = r["committed"]
                if diffs:
                    res["differences"] = diffs
                    if a.update:
                        res["action"] = "update " + ", ".join(f"{k} {_show(v)}" for k, v in diffs.items())
                        actions.append(("update", res, diffs))
                    else:
                        res["action"] = "differs: " + ", ".join(f"{k} {_show(v)}" for k, v in diffs.items())
        elif res["result"] == "new":
            if r["committed"]:
                dtype = rtype or default_type
                pid = _mint(b, docs, dtype, minted)
                dest = os.path.join(b.output_dir(dtype), f"{pid}-{B.slug(r['name'])}", "index.md")
                res["action"] = f"placeholder {pid} at {os.path.relpath(dest, b.root)}"
                actions.append(("placeholder", res, dtype, pid, dest))
            elif a.candidates:
                dest = os.path.join(b.candidates_dir, f"{B.slug(r['name'])}.md")
                if os.path.exists(dest):
                    res["action"] = f"none: {os.path.relpath(dest, b.root)} exists"
                else:
                    res["action"] = f"candidate at {os.path.relpath(dest, b.root)}"
                    actions.append(("candidate", res, dest))
            else:
                res["action"] = "none: not committed"
        else:
            res["action"] = "none: resolve by hand"
    report = _report(results, problems, b, a.dry_run)
    if not a.dry_run:
        for act in actions:
            _apply_backlog(act, b, minted)
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(json.dumps(_json(results, problems, b), indent=2) + "\n" if a.report.endswith(".json") else report)
    if a.json:
        print(json.dumps(_json(results, problems, b), indent=2, ensure_ascii=False))
    else:
        sys.stdout.write(report)
    return 1 if problems else 0


def _show(v):
    return ("yes" if v else "no") if isinstance(v, bool) else str(v)


def _mint(b, docs, dtype, minted):
    series, used = B.used_ids(docs, b, dtype)
    used |= set(minted)
    pid = B.next_id(series, used)
    minted[pid] = dtype
    return pid


def _apply_backlog(act, b, minted):
    kind = act[0]
    if kind == "update":
        _k, res, diffs = act
        L.apply_portfolio(res["doc"], diffs)
        return
    if kind == "candidate":
        _k, res, dest = act
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(B.candidate_text(res["row"]))
        return
    _k, res, dtype, pid, dest = act
    row = dict(res["row"])
    tpl = open(template_for(b, dtype), encoding="utf-8").read()
    extra = {}
    notes = ""
    if kind == "promote":
        cand = res["doc"]
        for k in ("priority", "target_quarter"):
            if not row.get(k) and cand.portfolio.get(k):
                row[k] = str(cand.portfolio[k])
        extra["description"] = cand.summary
        _fm, cbody = D.split(open(cand.path, encoding="utf-8").read())
        notes = "\n".join(ln for ln in cbody.strip().splitlines() if not D.H1_RE.match(ln)).strip()
        if os.path.exists(os.path.dirname(dest)):
            raise UsageError(f"{dest} exists")
        L._move(b.root, cand.path, dest, L.in_git(b.root))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    text = B.placeholder_front_matter(row, dtype, pid, b, extra) + "\n" + B.placeholder_body(tpl, pid, row["name"])
    if notes:
        text = text.rstrip("\n") + "\n\n## Candidate notes\n\n" + notes + "\n"
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)
    if kind == "promote" and L.in_git(b.root):
        L._git(b.root, "add", "--", os.path.relpath(dest, b.root))
    B.append_register(b, dtype, pid, row["name"], os.path.dirname(dest))


def _json(results, problems, b):
    def doc(d):
        return {"id": d.id, "title": d.title, "path": d.rel} if d else None
    return {"results": [{"line": r["row"]["line"], "name": r["row"]["name"], "type": r["row"]["type"],
                         "committed": r["row"]["committed"], "result": r["result"], "how": r["how"],
                         "score": r["score"], "match": doc(r["doc"]), "options": [doc(o) for o in r["options"]],
                         "action": r.get("action", "")} for r in results],
            "problems": problems,
            "counts": {k: sum(1 for r in results if r["result"] == k) for k in ("exact", "fuzzy", "ambiguous", "new", "duplicate")}}


def _report(results, problems, b, dry_run):
    c = _json(results, problems, b)["counts"]
    out = ["# Backlog match", "",
           f"{len(results)} rows: {c['exact']} exact, {c['fuzzy']} fuzzy, {c['ambiguous']} ambiguous, "
           f"{c['new']} new, {c['duplicate']} duplicates.{' Dry run: nothing was changed.' if dry_run else ''}", ""]

    def sect(title, items, fn):
        out.extend([f"## {title}", ""])
        if not items:
            out.extend(["None.", ""])
            return
        for r in items:
            out.append(fn(r))
        out.append("")

    label = lambda d: d.title if not d.id or d.title.startswith(d.id) else f"{d.id} {d.title}"  # noqa: E731
    name = lambda r: f"line {r['row']['line']} {r['row']['name']}" + (f" ({r['row']['type']})" if r["row"]["type"] else "")  # noqa: E731
    sect("Matched", [r for r in results if r["result"] in ("exact", "fuzzy")],
         lambda r: f"- {name(r)}: {r['result']} ({r['how']}{'' if r['result'] == 'exact' else ', ' + str(r['score'])}) "
                   f"{label(r['doc'])} `{r['doc'].rel}`" + (f". {r['action']}" if r["action"] else ""))
    sect("New", [r for r in results if r["result"] == "new"],
         lambda r: f"- {name(r)}{', committed' if r['row']['committed'] else ''}: {r['action']}")
    sect("Ambiguous", [r for r in results if r["result"] == "ambiguous"],
         lambda r: f"- {name(r)}: {r['how']} ({r['score']}); one of " + "; ".join(
             f"{label(o)} `{o.rel}`" for o in r["options"]))
    dups = [r for r in results if r["result"] == "duplicate"]
    if dups:
        sect("Duplicates", dups, lambda r: f"- {name(r)}: {r['how']}")
    if problems:
        sect("Problems", problems, lambda p: f"- {p}")
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="portfolio.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("--bindings", help="the binding file, instead of searching upward for one")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("discover", help="list the signed documents")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("inventory", help="write the summary page")
    s.add_argument("--format", choices=["md", "html", "json"])
    s.add_argument("--out")
    s.add_argument("--title", default="Pattern portfolio")
    s.add_argument("--include-archived", action="store_true")
    s = sub.add_parser("check", help="validate signatures and portfolio blocks")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("tag", help="tag what needs conversion or deprecation, or set a state by hand")
    s.add_argument("paths", nargs="*")
    s.add_argument("--state")
    s.add_argument("--reason")
    s.add_argument("--clear", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("sign", help="add kind to legacy documents")
    s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("archive", help="move documents marked archive into the archive folder")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--rewrite-links", action="store_true")
    s.add_argument("--stub", action="store_true")
    s = sub.add_parser("backlog", help="match a backlog and make placeholders")
    s.add_argument("file")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--default-type", default="architecture-pattern")
    s.add_argument("--update", action="store_true")
    s.add_argument("--candidates", action="store_true")
    s.add_argument("--report")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        b = Bindings(os.getcwd(), a.bindings)
        return {"discover": cmd_discover, "inventory": cmd_inventory, "check": cmd_check, "tag": cmd_tag,
                "sign": cmd_sign, "archive": cmd_archive, "backlog": cmd_backlog}[a.cmd](a, b)
    except UsageError as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
