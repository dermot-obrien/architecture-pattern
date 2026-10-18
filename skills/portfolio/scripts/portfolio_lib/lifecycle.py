# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Tagging, signing, checking and archiving.

Every command plans first and changes nothing until the plan is complete, so a dry run
prints exactly what a real run does. Nothing is ever deleted: archiving moves a page with
`git mv` where git tracks it, so its history follows it.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
import shutil
import subprocess

from . import docs as D

DEPRECATED_STATUSES = {"deprecated", "superseded", "retired", "withdrawn", "obsolete"}
NO_AUTO = {"placeholder", "draft", "archive", "archived", "proposed-deprecation"}


def _write(doc, text):
    with open(doc.path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


# ------------------------------------------------------------------ tag

def deprecation_reason(doc, stale_after_days=None):
    fm = doc.fm
    status = doc.status.lower()
    if status in DEPRECATED_STATUSES:
        return f"status is {status}"
    sb = fm.get("superseded_by")
    if sb and (sb if isinstance(sb, list) else [sb]) != [""]:
        return f"superseded by {', '.join(sb) if isinstance(sb, list) else sb}"
    if str(fm.get("lifecycle_state") or "").lower() == "retired":
        return "lifecycle_state is retired"
    vu = str(fm.get("valid_until") or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", vu) and vu < D.today():
        return f"valid_until {vu} has passed"
    if stale_after_days:
        lm = str(fm.get("last_modified") or "").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", lm):
            age = (_dt.date.fromisoformat(D.today()) - _dt.date.fromisoformat(lm)).days
            if age > stale_after_days:
                return f"not modified for {age} days (staleAfterDays is {stale_after_days})"
    return ""


def plan_tags(docs, form=None, stale_after_days=None):
    """[(doc, {portfolio changes}, why)] for every document whose tag should change."""
    plan = []
    for d in docs:
        if d.archived or d.is_candidate or not d.kind:
            continue
        state = d.state
        why_dep = deprecation_reason(d, stale_after_days)
        if why_dep and state in ("", "needs-conversion"):
            plan.append((d, {"state": "proposed-deprecation", "reason": why_dep, "since": D.today()}, why_dep))
            continue
        if state in NO_AUTO and state != "needs-conversion":
            continue
        problems = D.form_problems(d, form)
        if problems and state == "":
            why = "not in the form its type expects: " + "; ".join(problems)
            plan.append((d, {"state": "needs-conversion", "reason": why, "since": D.today()}, why))
        elif not problems and state == "needs-conversion":
            plan.append((d, {"state": None, "reason": None, "since": None}, "now in form: tag cleared"))
    return plan


def apply_portfolio(doc, changes):
    text = D.edit(_read(doc.path), portfolio=changes)
    _write(doc, text)


# ------------------------------------------------------------------ sign

def plan_sign(docs):
    out = []
    for d in docs:
        if d.legacy:
            top = {"kind": "pattern" if d.kind == "pattern" else "use-case"}
            if d.kind == "pattern" and d.type and not d.fm.get("pattern_type"):
                top["pattern_type"] = d.type
            if d.id and not d.fm.get("id"):
                top["id"] = d.id
            out.append((d, top))
    return out


def apply_sign(doc, top):
    text = _read(doc.path)
    fm_text, body = D.split(text)
    # kind goes first, where the standard puts it.
    lines = (fm_text or "").splitlines()
    head = [f"{k}: {D._yaml_scalar(v)}" for k, v in top.items()]
    nl = "\r\n" if "\r\n" in text else "\n"
    _write(doc, f"---{nl}{nl.join(head + lines)}{nl}---{nl}{body}")


# ------------------------------------------------------------------ check

def check(docs, bindings):
    """(errors, warnings), each a list of 'path: message'."""
    errors, warnings = [], []
    by_id = {}
    for d in docs:
        where = d.rel
        for p in d.problems:
            errors.append(f"{where}: {p}")
        if not d.kind:
            continue
        if d.legacy:
            warnings.append(f"{where}: legacy signature (no kind); portfolio.py sign adds it")
        if d.kind == "pattern" and not d.type:
            errors.append(f"{where}: kind pattern with no pattern_type ({', '.join(D.PATTERN_TYPES)})")
        if not d.is_candidate:
            if not d.id:
                (warnings if d.legacy else errors).append(f"{where}: no id")
            elif d.type:
                series = bindings.series(d.type)
                m = D.ID_RE.match(d.id)
                if not m or m.group(1) != series:
                    errors.append(f"{where}: id {d.id} is not in the {d.type} series {series}-NNN")
            if d.id:
                if d.id in by_id and not (d.archived or by_id[d.id].archived):
                    errors.append(f"{where}: {d.id} is also the id of {by_id[d.id].rel}")
                by_id.setdefault(d.id, d)
        elif d.fm.get("id") and not D.SLUG_RE.match(str(d.fm["id"])):
            errors.append(f"{where}: a candidate's id, when it has one, is a kebab-case slug")
        if d.is_candidate:
            ct = str(d.fm.get("candidate_type") or "")
            if ct and ct not in D.TYPES:
                errors.append(f"{where}: candidate_type {ct} is not one of {', '.join(D.TYPES)}")
        p = d.fm.get("portfolio")
        if p is None:
            continue
        if not isinstance(p, dict):
            errors.append(f"{where}: portfolio is not a mapping")
            continue
        for k in p:
            if k not in D.PORTFOLIO_KEYS:
                errors.append(f"{where}: portfolio.{k} is not a field of the standard ({', '.join(D.PORTFOLIO_KEYS)})")
        st = str(p.get("state") or "")
        if st and st not in D.STATES:
            errors.append(f"{where}: portfolio.state {st} is not one of {', '.join(D.STATES)}")
        if st and d.is_candidate:
            errors.append(f"{where}: a candidate carries no portfolio.state; promote it to a placeholder instead")
        pr = str(p.get("priority") or "")
        if pr and pr not in D.PRIORITIES:
            errors.append(f"{where}: portfolio.priority {pr} is not one of {', '.join(D.PRIORITIES)}")
        q = str(p.get("target_quarter") or "")
        if q and not D.QUARTER_RE.match(q):
            errors.append(f"{where}: portfolio.target_quarter {q} is not YYYY-Qn")
        c = p.get("committed")
        if c not in (None, "") and str(c).lower() not in ("true", "false"):
            errors.append(f"{where}: portfolio.committed is true or false, not {c}")
        if st == "archived" and not d.archived:
            warnings.append(f"{where}: portfolio.state archived, but the page is outside the archive folder")
        if st == "archive" and d.archived:
            warnings.append(f"{where}: in the archive folder but still marked archive; portfolio.py archive finishes it")
    return errors, warnings


# ------------------------------------------------------------------ archive

LINK_RE = re.compile(r"(\]\()(<[^>]+>|[^)\s]+)((?:\s+\"[^\"]*\")?\))")
REF_RE = re.compile(r"^(\s*\[[^\]]+\]:\s*)(\S+)(.*)$")


def _is_local(target):
    return not (re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith(("#", "/")))


def _split_target(t):
    t = t[1:-1] if t.startswith("<") and t.endswith(">") else t
    m = re.match(r"^([^#?]*)(.*)$", t)
    return m.group(1), m.group(2)


def iter_links(text):
    """(line number, start, end, target) for each inline or reference-style link outside code."""
    fenced = False
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        if D.FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for m in LINK_RE.finditer(line):
            yield n, m.start(2), m.end(2), m.group(2)
        m = REF_RE.match(line)
        if m:
            yield n, m.start(2), m.end(2), m.group(2)


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def in_git(repo):
    return _git(repo, "rev-parse", "--is-inside-work-tree").stdout.strip() == "true"


def tracked(repo, path):
    return _git(repo, "ls-files", "--error-unmatch", "--", os.path.relpath(path, repo)).returncode == 0


def plan_archive(docs, bindings):
    """[{doc, src, dest, folder}] and problems. The whole folder moves when the page is its
    folder's index and no other signed document shares the folder."""
    root, adir = bindings.root, bindings.archive_dir
    signed_dirs = {}
    for d in docs:
        signed_dirs.setdefault(os.path.dirname(d.path), []).append(d)
    moves, problems = [], []
    for d in docs:
        if d.state != "archive" or d.archived:
            continue
        here = os.path.dirname(d.path)
        folder = (os.path.splitext(os.path.basename(d.path))[0] == "index"
                  and len(signed_dirs[here]) == 1
                  and os.path.abspath(here) not in [os.path.abspath(r) for r in bindings.roots + [root]])
        src = here if folder else d.path
        rel = os.path.relpath(src, root)
        if rel.startswith(".."):
            problems.append(f"{d.rel}: outside the repository, so it is not archived")
            continue
        dest = os.path.join(adir, rel)
        if os.path.exists(dest):
            problems.append(f"{d.rel}: {os.path.relpath(dest, root)} already exists in the archive; not moved")
            continue
        moves.append({"doc": d, "src": src, "dest": dest, "folder": folder})
    return moves, problems


def _moved(path, moves):
    """Where a path ends up after the moves, or None if it does not move."""
    ap = os.path.abspath(path)
    for mv in moves:
        s = os.path.abspath(mv["src"])
        if ap == s or (mv["folder"] and ap.startswith(s + os.sep)):
            return os.path.join(mv["dest"], os.path.relpath(ap, s)) if ap != s else mv["dest"]
    return None


def links_affected(moves, bindings):
    """Links that a move would break: [{file, line, target, new_target, inbound}]."""
    root = bindings.root
    out = []
    moved_files = set()
    for mv in moves:
        if mv["folder"]:
            for p in D.walk([mv["src"]], skip_names=set()):
                moved_files.add(os.path.abspath(p))
        else:
            moved_files.add(os.path.abspath(mv["src"]))
    scan = [p for p in D.walk([root], exclude=[bindings.archive_dir])]
    for f in scan:
        try:
            text = _read(f)
        except (OSError, UnicodeDecodeError):
            continue
        f_new = _moved(f, moves) if os.path.abspath(f) in moved_files else None
        for n, s, e, target in iter_links(text):
            if not _is_local(target):
                continue
            path_part, frag = _split_target(target)
            if not path_part:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(f), path_part))
            t_new = _moved(resolved, moves)
            if f_new is None and t_new is None:
                continue
            here = os.path.dirname(f_new or f)
            there = t_new or resolved
            new_target = os.path.relpath(there, here).replace(os.sep, "/")
            if path_part.endswith("/") and not new_target.endswith("/"):
                new_target += "/"
            if os.path.normpath(new_target) == os.path.normpath(path_part):
                continue
            out.append({"file": f, "line": n, "start": s, "end": e, "target": target,
                        "new_target": new_target + frag, "inbound": f_new is None})
    return out


def _rewrite(links):
    by_file = {}
    for lk in links:
        by_file.setdefault(lk["file"], []).append(lk)
    for f, lks in by_file.items():
        lines = _read(f).splitlines(keepends=True)
        for lk in sorted(lks, key=lambda x: (x["line"], -x["start"])):
            ln = lines[lk["line"] - 1]
            lines[lk["line"] - 1] = ln[:lk["start"]] + lk["new_target"] + ln[lk["end"]:]
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write("".join(lines))


def _move(repo, src, dest, use_git):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if use_git and tracked(repo, src):
        r = _git(repo, "mv", "--", os.path.relpath(src, repo), os.path.relpath(dest, repo))
        if r.returncode != 0:
            raise RuntimeError(f"git mv {src}: {r.stderr.strip()}")
        # Untracked files left behind in a folder git moved still belong with it.
        if os.path.isdir(src):
            for name in os.listdir(src):
                shutil.move(os.path.join(src, name), os.path.join(dest, name))
            try:
                os.rmdir(src)
            except OSError:
                pass
        return "git mv"
    shutil.move(src, dest)
    return "move"


def stub_text(title, new_rel):
    return (f"---\ntitle: {D._yaml_scalar(title + ' (archived)')}\nmoved_to: {D._yaml_scalar(new_rel)}\n"
            f"unlisted: true\n---\n\n# {title}\n\nThis page was archived. It is now at [{new_rel}]({new_rel}).\n")


def apply_archive(moves, links, bindings, rewrite=False, stubs=False, log=print):
    root = bindings.root
    use_git = in_git(root)
    # Rewrite links before moving, while every file is where the plan found it.
    if rewrite and links:
        _rewrite(links)
    for mv in moves:
        how = _move(root, mv["src"], mv["dest"], use_git)
        d = mv["doc"]
        new_path = os.path.join(mv["dest"], os.path.relpath(d.path, mv["src"])) if mv["folder"] else mv["dest"]
        text = D.edit(_read(new_path), top={"unlisted": True},
                      portfolio={"state": "archived", "since": D.today(),
                                 "archived_from": os.path.relpath(mv["src"], root).replace(os.sep, "/")})
        with open(new_path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        if use_git and how == "git mv":
            _git(root, "add", "--", os.path.relpath(new_path, root))
        log(f"archived {d.rel} -> {os.path.relpath(new_path, root).replace(os.sep, '/')} ({how})")
        if stubs:
            stub = d.path
            os.makedirs(os.path.dirname(stub), exist_ok=True)
            rel = os.path.relpath(new_path, os.path.dirname(stub)).replace(os.sep, "/")
            with open(stub, "w", encoding="utf-8") as f:
                f.write(stub_text(d.title, rel))
            if use_git:
                _git(root, "add", "--", os.path.relpath(stub, root))
            log(f"  stub left at {d.rel}")
