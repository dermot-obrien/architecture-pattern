# SPDX-License-Identifier: Apache-2.0
"""Find the sources, pair each diagram with its text, gather them into one conversion
folder, and archive the originals.

A source is a diagram (.drawio, .dio, .svg, .png, .jpg) or a text (.md, .markdown,
.txt). A folder is searched to any depth. Each diagram is one unit, with the texts that
go with it, in this order of confidence:

    1. a text that links to the diagram, as an image or a link
    2. a text with the same stem, so order-intake.md with order-intake.drawio
    3. the texts in a folder that holds only one diagram

Exports of one diagram side by side, order-intake.drawio beside order-intake.svg and
order-intake.png, are one unit, read from the most structured of them: draw.io, then an
SVG or PNG carrying the draw.io diagram, then a plain SVG, then a picture. The others are
gathered and archived with it.

Archiving never deletes. A source tracked by git is moved with `git mv` into the archive
folder, at the same path below it as below the repository root, so its history follows
it. A source outside git, or not tracked, is copied into the conversion folder and left
where it is.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.parse

from .unit import humanise, slug

DIAGRAM_EXT = (".drawio", ".dio", ".svg", ".png", ".jpg", ".jpeg")
TEXT_EXT = (".md", ".markdown", ".txt")
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv"}
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def stem(path) -> str:
    name = os.path.basename(path)
    low = name.lower()
    for ext in (".drawio.svg", ".drawio.png", ".drawio.xml") + DIAGRAM_EXT + TEXT_EXT:
        if low.endswith(ext):
            return name[:-len(ext)]
    return os.path.splitext(name)[0]


def kind(path) -> str:
    low = path.lower()
    if low.endswith(TEXT_EXT):
        return "text"
    if low.endswith((".drawio", ".dio", ".drawio.xml")):
        return "drawio"
    if low.endswith(".svg"):
        return "svg"
    if low.endswith((".png", ".jpg", ".jpeg")):
        return "image"
    if low.endswith(".xml"):
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                head = fh.read(512)
            if "<mxfile" in head or "<mxGraphModel" in head:
                return "drawio"
        except OSError:
            pass
    return ""


def discover(paths, skip=()) -> list:
    """Every source file under the paths, as absolute paths, in a stable order."""
    skip = {os.path.abspath(s) for s in skip if s}
    found = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            if kind(p):
                found.append(p)
            continue
        if not os.path.isdir(p):
            raise FileNotFoundError(p)
        for d, dirs, files in os.walk(p):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith(".")
                             and os.path.abspath(os.path.join(d, x)) not in skip)
            for f in sorted(files):
                fp = os.path.join(d, f)
                if kind(fp):
                    found.append(fp)
    out, seen = [], set()
    for f in found:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


RANK = {"drawio": 0, "svg": 2, "image": 4}


def _rank(path) -> int:
    k = kind(path)
    low = path.lower()
    if k == "svg" and ".drawio." in low:
        return 1
    if k == "image" and ".drawio." in low:
        return 3
    return RANK.get(k, 9)


def _links_in(text_path) -> set:
    try:
        with open(text_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return set()
    out = set()
    base = os.path.dirname(text_path)
    for m in LINK.finditer(text):
        target = m.group(1).split("#", 1)[0]
        if target and "://" not in target:
            out.add(os.path.normpath(os.path.join(base, urllib.parse.unquote(target))))
    return out


def pair(files) -> tuple:
    """(units, unpaired texts). A unit is {name, diagram, alternates, texts}."""
    diagrams = [f for f in files if kind(f) != "text"]
    texts = [f for f in files if kind(f) == "text"]
    # Exports of one diagram side by side are one unit.
    groups = {}
    for d in diagrams:
        groups.setdefault((os.path.dirname(d), stem(d).lower()), []).append(d)
    units = []
    for (folder, _s), members in sorted(groups.items()):
        members.sort(key=lambda p: (_rank(p), p))
        units.append({"name": humanise(stem(members[0])), "diagram": members[0],
                      "alternates": members[1:], "texts": [], "folder": folder})
    by_member = {m: u for u in units for m in [u["diagram"]] + u["alternates"]}
    unpaired = []
    for t in texts:
        linked = [by_member[x] for x in _links_in(t) if x in by_member]
        same = [u for u in units if u["folder"] == os.path.dirname(t)
                and stem(u["diagram"]).lower() == stem(t).lower()]
        alone = [u for u in units if u["folder"] == os.path.dirname(t)]
        if linked:
            targets = linked
        elif same:
            targets = same
        elif len(alone) == 1:
            targets = alone
        else:
            unpaired.append(t)
            continue
        seen = []
        for u in targets:
            if u not in seen:
                seen.append(u)
                u["texts"].append(t)
    return units, unpaired


# ------------------------------------------------------------------ git

def git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def repo_of(path) -> str:
    d = path if os.path.isdir(path) else os.path.dirname(path)
    r = git(["rev-parse", "--show-toplevel"], d)
    return os.path.abspath(r.stdout.strip()) if r.returncode == 0 else ""


def tracked(path, repo) -> bool:
    return git(["ls-files", "--error-unmatch", "--", path], repo).returncode == 0


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ the conversion folder

def work_root(start, bound="") -> str:
    """Where conversion folders go: the bound workDir, else conversions/ at the
    repository root, else beside the working directory."""
    if bound:
        return bound
    repo = repo_of(start)
    return os.path.join(repo or os.path.abspath(start), "conversions")


def new_run_dir(root, label, today=None) -> str:
    today = today or datetime.date.today().isoformat()
    base = os.path.join(root, f"{today}-{slug(label, 32)}")
    d, n = base, 2
    while os.path.exists(d):
        d = f"{base}-{n}"
        n += 1
    return d


def archive_target(path, repo, archive_dir) -> str:
    rel = os.path.relpath(path, repo)
    return os.path.join(archive_dir, rel)


def plan_sources(units, unpaired, archive_dir_for, archive=True) -> list:
    """One entry per source file: where it is, whether git tracks it, where it goes."""
    entries, seen = [], set()
    for u in units:
        for role, paths in (("diagram", [u["diagram"]]), ("alternate", u["alternates"]),
                            ("text", u["texts"])):
            for p in paths:
                if p in seen:
                    continue
                seen.add(p)
                entries.append(_entry(p, role, u, archive_dir_for, archive))
    for p in unpaired:
        if p not in seen:
            seen.add(p)
            e = _entry(p, "unpaired", None, archive_dir_for, False)
            e["note"] = "a text that goes with no diagram; not converted, left where it is"
            entries.append(e)
    return entries


def _entry(p, role, u, archive_dir_for, archive):
    repo = repo_of(p)
    is_tracked = bool(repo) and tracked(p, repo)
    e = {"original": p, "role": role, "unit": slug(u["name"]) if u else "",
         "repository": repo, "tracked": is_tracked, "archive": ""}
    if archive and is_tracked:
        adir = archive_dir_for(repo)
        if os.path.commonpath([os.path.abspath(p), adir]) == adir:
            e["note"] = "already in the archive folder; left where it is"
        else:
            e["archive"] = archive_target(p, repo, adir)
    elif archive and repo and not is_tracked:
        e["note"] = "in a git repository but not tracked; copied, and left where it is"
    elif archive:
        e["note"] = "not in a git repository; copied, and left where it is"
    return e


def gather(entries, run_dir) -> None:
    """Copy every source into the conversion folder, recording its fingerprint."""
    for e in entries:
        folder = os.path.join(run_dir, "sources", e["unit"] or "_unpaired")
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, os.path.basename(e["original"]))
        n = 2
        while os.path.exists(dest):
            root, ext = os.path.splitext(os.path.basename(e["original"]))
            dest = os.path.join(folder, f"{root}-{n}{ext}")
            n += 1
        shutil.copy2(e["original"], dest)
        e["gathered"] = os.path.relpath(dest, run_dir).replace(os.sep, "/")
        e["sha256"] = sha256(dest)


def archive(entries) -> list:
    """`git mv` every tracked source to its archive path. Returns the problems."""
    problems = []
    for e in entries:
        target = e.get("archive")
        if not target or e.get("archived"):
            continue
        if os.path.exists(target):
            problems.append(f"{target} already exists; {e['original']} was left where it is")
            e["archive"] = ""
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        r = git(["mv", "--", e["original"], target], e["repository"])
        if r.returncode != 0:
            problems.append(f"git mv {e['original']} failed: {r.stderr.strip()}; left where it is")
            e["archive"] = ""
        else:
            e["archived"] = True
    return problems


def write_manifest(run_dir, data) -> str:
    path = os.path.join(run_dir, "manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    return path


def read_manifest(run_dir) -> dict:
    with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as fh:
        return json.load(fh)
