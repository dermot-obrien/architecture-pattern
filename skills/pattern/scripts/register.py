#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The register: one CSV of every identifier the repository has minted, and where each lives.

    python scripts/register.py next [PREFIX | --type TYPE]
    python scripts/register.py add ID --name NAME --path FOLDER [--type T] [--status S]
                                      [--summary S] [--url URL] [--set COLUMN=VALUE ...]
    python scripts/register.py check [--fix]
    python scripts/register.py outdir

    common options: --suite pattern|use-case   whose bindings to read (default pattern)
                    --register FILE            the register, instead of the bound one

Run from the workspace root. The register is `register` under [suite.pattern] or
[suite.use-case] of .agents/skill-bindings.toml, found by searching upward from the
working directory, and both may name the same file. Its identifier column is `id`, or
its first column when none is named `id`. Every other column is optional:

    id,type,name,status,path,url,summary
    PAT-001,pattern,Order intake,Approved,../patterns/integration/PAT-001-order-intake,,...
    UC-004,use-case,Track an order,Draft,../use-cases/UC-004-track-an-order,,...

`type` is a pattern type's name, such as architecture-pattern or reference-architecture,
when the repository binds types, else the suite. `path` is the folder (or the document)
relative to the register file, so a pattern can
sit in any category folder. `url` is its page on a published site, when that cannot be
built from the id. Columns the register does not have are never added.

next   prints the next free identifier in PREFIX, or in the idSeries of a pattern type
       bound under [suite.pattern.types.<TYPE>] (default the suite's idSeries; when types
       are bound, --type is required so the id is in the right series): the
       highest number in the register, or in a folder name under patternsRoot and
       outputDir at any depth, plus one, with as many digits as the widest. With none of
       the three bound, every folder in the repository is scanned, with a warning.
outdir prints the folder new documents go in: outputDir, else the default, patterns/ or
       use-cases/ at the repository root, with a note on stderr saying it is the default.
add    appends one row and refuses an identifier already there. A row is appended,
       never inserted, so two branches that each take the next number both change the
       end of the file and git reports a conflict instead of merging a duplicate.
       --path is relative to the working directory; it is stored relative to the register.
check  reports duplicate identifiers and paths that name no document (errors), and rows whose
       name or status differ from their document, and documents under the bound folders
       with no row (warnings). --fix rewrites path, name and status from the documents,
       finding a moved folder by its `<ID>-` name, and adds a row for each unregistered
       document. It never removes a row.

Exit 0: ok, warnings may be printed. Exit 1: errors remain. Exit 2: usage or bindings.
Standard library only; Python 3.11 or newer.
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import os
import re
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: register.py needs 3.11 or newer.",
          file=sys.stderr)
    sys.exit(2)

import tomllib  # noqa: E402

BINDING_NAMES = (".agents/skill-bindings.toml", "skill-bindings.toml", "model.toml", ".model.toml")
SUITES = {"pattern": "AP", "use-case": "UC"}
# Where new documents go when a suite binds no outputDir, relative to the repository root.
DEFAULT_OUTPUT = {"pattern": "patterns", "use-case": "use-cases"}
SKIP_DIRS = {"node_modules", "dist", "build"}
H1_RE = re.compile(r"^#\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


class UsageError(Exception):
    pass


# ---------------------------------------------------------------------- bindings

def find_bindings(start) -> str:
    d = os.path.abspath(start)
    while True:
        for name in BINDING_NAMES:
            p = os.path.join(d, *name.split("/"))
            if os.path.isfile(p):
                return p
        up = os.path.dirname(d)
        if up == d:
            return ""
        d = up


def load_bindings(start) -> tuple:
    """(binding file, {suite name: its table}) for the suites this script reads."""
    path = find_bindings(start)
    if not path:
        return "", {}
    try:
        with open(path, "rb") as fh:
            raw = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as ex:
        raise UsageError(f"{path}: {ex}")
    suite = raw.get("suite") or {}
    return path, {k: v for k, v in suite.items() if k in SUITES and isinstance(v, dict)}


def repo_root(binding_file, start) -> str:
    """The folder a binding file binds: the one holding `.agents/`, or the file's own. With no
    binding file, the nearest folder above `start` holding `.git`, else `start`."""
    if binding_file:
        d = os.path.dirname(os.path.abspath(binding_file))
        return os.path.dirname(d) if os.path.basename(d) == ".agents" else d
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        up = os.path.dirname(d)
        if up == d:
            return os.path.abspath(start)
        d = up


def bound(binding_file, value) -> str:
    """A path from the binding file, which is relative to the file's folder."""
    if not value:
        return ""
    return os.path.normpath(os.path.join(os.path.dirname(binding_file), str(value)))


class Series:
    """One suite's identifier series: its prefix, its row type, and where its documents live."""

    def __init__(self, suite, table, binding_file, start=None):
        self.suite = suite
        self.type = suite
        self.prefix = str(table.get("idSeries") or SUITES[suite])
        self.output = bound(binding_file, table.get("outputDir"))
        self.output_default = not self.output
        if self.output_default:
            self.output = os.path.join(repo_root(binding_file, start or os.getcwd()),
                                       DEFAULT_OUTPUT[suite])
        roots = [table.get("patternsRoot"), table.get("outputDir")]
        self.roots = [bound(binding_file, r) for r in roots if r]
        self.register = bound(binding_file, table.get("register"))
        # Nothing bound to number from: the whole repository is the only place left to look.
        self.whole_repo = not self.roots and not self.register
        if self.whole_repo:
            self.roots = [repo_root(binding_file, start or os.getcwd())]
        self.set_prefix(self.prefix)
        # [suite.pattern.types.<name>]: the repository's kinds of pattern, each with its own
        # idSeries, such as AP for architecture patterns and RA for reference architectures.
        self.types = {str(k): v for k, v in (table.get("types") or {}).items()
                      if isinstance(v, dict)}

    def set_prefix(self, prefix, type_name=None):
        self.prefix = prefix
        if type_name:
            self.type = type_name
        self.id_re = re.compile(rf"^{re.escape(prefix)}-([0-9]+)$")
        self.folder_re = re.compile(rf"^({re.escape(prefix)}-[0-9]+)(?:-|$)")
        return self

    def of_type(self, name):
        """This series narrowed to one pattern type's idSeries."""
        t = self.types.get(name)
        if t is None:
            raise UsageError(f"'{name}' is not a type bound under [suite.{self.suite}.types]; "
                             f"expected one of {', '.join(sorted(self.types)) or '(none bound)'}")
        if not t.get("idSeries"):
            raise UsageError(f"[suite.{self.suite}.types.{name}] has no idSeries to number from")
        s = copy.copy(self)
        return s.set_prefix(str(t["idSeries"]), name)

    def type_for(self, pid) -> str:
        """The bound type whose idSeries an identifier carries, else this series' type."""
        for name, t in self.types.items():
            if t.get("idSeries") and pid.startswith(f"{t['idSeries']}-"):
                return name
        return self.type

    def every_series(self) -> list:
        """This series, and one per bound type with an idSeries."""
        out = [self]
        for name, t in self.types.items():
            if t.get("idSeries") and t["idSeries"] != self.prefix:
                out.append(self.of_type(name))
        return out


# ---------------------------------------------------------------------- the CSV

class Register:
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.base = os.path.dirname(self.path)
        try:
            with open(self.path, encoding="utf-8-sig", newline="") as fh:
                text = fh.read()
        except FileNotFoundError:
            raise UsageError(f"the register {self.path} does not exist")
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.text = text
        rows = list(csv.reader(io.StringIO(text)))
        rows = [r for r in rows if any(c.strip() for c in r)]
        if not rows:
            raise UsageError(f"the register {self.path} has no header row")
        self.header = [h.strip() for h in rows[0]]
        lower = [h.lower() for h in self.header]
        self.col = {name: lower.index(name) for name in lower if name}
        self.id_col = self.col.get("id", 0)
        self.rows = [r + [""] * (len(self.header) - len(r)) for r in rows[1:]]

    def has(self, column) -> bool:
        return column in self.col

    def get(self, row, column) -> str:
        i = self.col.get(column)
        return row[i].strip() if i is not None and i < len(row) else ""

    def set(self, row, column, value):
        row[self.col[column]] = value

    def ids(self) -> list:
        return [r[self.id_col].strip() for r in self.rows]

    def resolve(self, rel) -> str:
        """A path cell as a document path, or "" when it names nothing."""
        if not rel:
            return ""
        p = os.path.normpath(os.path.join(self.base, rel))
        if os.path.isdir(p):
            p = os.path.join(p, "index.md")
        return p if os.path.isfile(p) else ""

    def relative(self, path) -> str:
        return os.path.relpath(os.path.abspath(path), self.base).replace(os.sep, "/")

    def encode(self, row) -> str:
        out = io.StringIO()
        csv.writer(out, lineterminator=self.newline).writerow(row)
        return out.getvalue()

    def append(self, row):
        with open(self.path, "a", encoding="utf-8", newline="") as fh:
            if self.text and not self.text.endswith(("\n", "\r")):
                fh.write(self.newline)
            fh.write(self.encode(row))

    def save(self):
        with open(self.path, "w", encoding="utf-8", newline="") as fh:
            fh.write(self.encode(self.header))
            for r in self.rows:
                fh.write(self.encode(r))


# ---------------------------------------------------------------------- documents

def read_doc(path) -> dict:
    """Front matter `title` and `status`, and the first H1 outside code fences."""
    try:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.read(65536).splitlines()
    except (OSError, UnicodeDecodeError):
        return {}
    meta, body = {}, lines
    if lines and lines[0].strip() == "---":
        for i, ln in enumerate(lines[1:], 1):
            if ln.strip() in ("---", "..."):
                body = lines[i + 1:]
                break
            m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
            if m:
                meta[m.group(1)] = m.group(2).strip().strip("'\"")
    h1, fenced = "", False
    for ln in body:
        if FENCE_RE.match(ln):
            fenced = not fenced
        elif not fenced and (m := H1_RE.match(ln)):
            h1 = m.group(1).strip()
            break
    return {"h1": h1, "title": meta.get("title", ""), "status": meta.get("status", "")}


def doc_name(info, pid) -> str:
    for text in (info.get("h1", ""), info.get("title", "")):
        if text.startswith(pid):
            return text[len(pid):].strip(" :-–—")
        if text:
            return text
    return ""


def scan(series) -> dict:
    """{id: [document paths]} for folders named `<ID>-...` holding index.md under the roots."""
    found = {}
    for root in series.roots:
        if not os.path.isdir(root):
            continue
        for d, dirs, files in os.walk(root):
            dirs[:] = sorted(x for x in dirs if not x.startswith(".") and x not in SKIP_DIRS)
            m = series.folder_re.match(os.path.basename(d))
            if m and "index.md" in files:
                p = os.path.abspath(os.path.join(d, "index.md"))
                lst = found.setdefault(m.group(1), [])
                if p not in lst:
                    lst.append(p)
    return found


# ---------------------------------------------------------------------- commands

def next_id(series, reg) -> str:
    nums, width = [], 3
    # The folders count too, so a document written before its row was added is never
    # given a second number.
    ids = (reg.ids() if reg else []) + list(scan(series))
    for pid in ids:
        m = series.id_re.match(pid)
        if m:
            nums.append(int(m.group(1)))
            width = max(width, len(m.group(1)))
    return f"{series.prefix}-{(max(nums) + 1 if nums else 1):0{width}d}"


def whole_repo_warning(series) -> str:
    return (f"warning: no register, patternsRoot or outputDir is bound under [suite.{series.suite}], "
            f"so the whole repository under {series.roots[0]} was scanned for {series.prefix}- "
            "folders. Bind register, or patternsRoot, to number without a full scan.")


def cmd_next(a, series, reg):
    if a.type:
        series = series.of_type(a.type)
    elif a.prefix:
        series.set_prefix(a.prefix)
    elif series.types:
        raise UsageError(f"this repository binds pattern types; name one with --type "
                         f"({', '.join(sorted(series.types))}), so the id is in its series")
    if not reg and not any(os.path.isdir(r) for r in series.roots):
        raise UsageError(f"no register is bound under [suite.{series.suite}] and none of its "
                         "folders exist, so there is nothing to number from")
    if series.whole_repo and not a.register:
        print(whole_repo_warning(series), file=sys.stderr)
    print(next_id(series, reg))
    return 0


def cmd_outdir(a, series):
    print(series.output)
    if series.output_default:
        exists = "" if os.path.isdir(series.output) else "; it does not exist yet, so create it"
        print(f"note: no outputDir is bound under [suite.{series.suite}], so new documents go in "
              f"the default, {series.output}{exists}. Bind [suite.{series.suite}] outputDir, "
              f"relative to the binding file, to put them elsewhere.", file=sys.stderr)
    return 0


def cmd_add(a, series, reg):
    if not reg:
        raise UsageError(f"no register is bound under [suite.{series.suite}]; bind register "
                         "or pass --register")
    pid = a.id.strip()
    if pid in reg.ids():
        print(f"error: {pid} is already in {reg.path}; take `register.py next` instead",
              file=sys.stderr)
        return 1
    values = {"type": a.type or series.type_for(pid), "name": a.name, "status": a.status,
              "summary": a.summary, "url": a.url}
    if a.path:
        values["path"] = reg.relative(a.path)
    for kv in a.set or []:
        if "=" not in kv:
            raise UsageError(f"--set {kv}: expected COLUMN=VALUE")
        k, v = kv.split("=", 1)
        values[k.strip().lower()] = v
    row = [""] * len(reg.header)
    row[reg.id_col] = pid
    skipped = []
    for k, v in values.items():
        if v in (None, ""):
            continue
        if reg.has(k):
            reg.set(row, k, v)
        else:
            skipped.append(k)
    reg.append(row)
    print(f"added {pid} to {reg.path}")
    if skipped:
        print(f"warning: the register has no {', '.join(skipped)} column; not recorded")
    return 0


def cmd_check(a, series_by_prefix, reg):
    errors, warnings, fixed = [], [], []
    ids = reg.ids()

    seen = {}
    for i, pid in enumerate(ids):
        if not pid:
            errors.append(f"row {i + 2} has no identifier")
        elif pid in seen:
            errors.append(f"{pid} is in the register twice, rows {seen[pid] + 2} and {i + 2}: "
                          "renumber one, and its document, before either is referenced")
        else:
            seen[pid] = i

    found = {}
    for s in series_by_prefix.values():
        for pid, paths in scan(s).items():
            found.setdefault(pid, []).extend(paths)

    for i, row in enumerate(reg.rows):
        pid = row[reg.id_col].strip()
        if not pid or seen.get(pid) != i:
            continue
        rel = reg.get(row, "path")
        doc = reg.resolve(rel)
        if reg.has("path") and not doc:
            candidates = found.get(pid, [])
            if a.fix and len(candidates) == 1:
                reg.set(row, "path", reg.relative(os.path.dirname(candidates[0])))
                fixed.append(f"{pid}: path {rel or '(empty)'} -> {reg.get(row, 'path')}")
                doc = candidates[0]
            elif rel or candidates:
                hint = ""
                if candidates:
                    hint = f"; found at {', '.join(reg.relative(os.path.dirname(c)) for c in candidates)}"
                    if len(candidates) == 1:
                        hint += "; `check --fix` corrects it"
                if rel:
                    errors.append(f"{pid}: path {rel} names no document{hint}")
                else:
                    warnings.append(f"{pid}: has no path{hint}")
        if not doc:
            continue
        info = read_doc(doc)
        for column, value in (("name", doc_name(info, pid)), ("status", info.get("status", ""))):
            if not reg.has(column) or not value or reg.get(row, column) == value:
                continue
            if a.fix:
                fixed.append(f"{pid}: {column} {reg.get(row, column)!r} -> {value!r}")
                reg.set(row, column, value)
            else:
                warnings.append(f"{pid}: {column} is {reg.get(row, column)!r} in the register "
                                f"but {value!r} in {reg.relative(doc)}")

    added = []
    for pid in sorted(found):
        if pid in seen:
            continue
        paths = found[pid]
        if len(paths) > 1:
            errors.append(f"{pid} has {len(paths)} folders: {', '.join(reg.relative(p) for p in paths)}")
            continue
        s = next(s for s in series_by_prefix.values() if s.folder_re.match(pid))
        if a.fix:
            info = read_doc(paths[0])
            row = [""] * len(reg.header)
            row[reg.id_col] = pid
            for column, value in (("type", s.type), ("name", doc_name(info, pid)),
                                  ("status", info.get("status", "")),
                                  ("path", reg.relative(os.path.dirname(paths[0])))):
                if reg.has(column):
                    reg.set(row, column, value)
            added.append(row)
            fixed.append(f"{pid}: added from {reg.relative(paths[0])}")
        else:
            warnings.append(f"{pid} at {reg.relative(paths[0])} is not in the register; "
                            "`check --fix` adds it")

    if fixed:
        # Changed rows are rewritten where they are and new ones go at the end, so a fix
        # changes as few lines as it can.
        reg.rows.extend(added)
        reg.save()
    for f in fixed:
        print(f"fixed: {f}")
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"register: {len(reg.rows)} rows, {len(errors)} errors, {len(warnings)} warnings"
          + (f", {len(fixed)} fixed" if fixed else ""))
    return 1 if errors else 0


# ---------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="register.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--suite", choices=sorted(SUITES), default="pattern",
                    help="whose [suite.*] bindings to read (default pattern)")
    ap.add_argument("--register", help="the register CSV, instead of the bound one")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("outdir", help="print the folder new documents go in: outputDir, else the default")
    n = sub.add_parser("next", help="print the next free identifier")
    n.add_argument("prefix", nargs="?", help="the series, default the suite's idSeries")
    n.add_argument("--type", help="a pattern type bound under [suite.pattern.types]; its idSeries")
    ad = sub.add_parser("add", help="append a row")
    ad.add_argument("id")
    ad.add_argument("--name")
    ad.add_argument("--path", help="the folder or document, relative to the working directory")
    ad.add_argument("--type", help="default: the bound pattern type whose idSeries the id carries, "
                                   "else the suite, pattern or use-case")
    ad.add_argument("--status")
    ad.add_argument("--summary")
    ad.add_argument("--url")
    ad.add_argument("--set", action="append", metavar="COLUMN=VALUE",
                    help="any other column the register has; repeatable")
    ch = sub.add_parser("check", help="check the register against the documents")
    ch.add_argument("--fix", action="store_true", help="rewrite path, name and status, add missing rows")
    a = ap.parse_args(argv)

    try:
        binding_file, tables = load_bindings(os.getcwd())
        series = Series(a.suite, tables.get(a.suite, {}), binding_file, os.getcwd())
        reg_path = os.path.abspath(a.register) if a.register else series.register
        reg = Register(reg_path) if reg_path else None
        if a.cmd == "outdir":
            return cmd_outdir(a, series)
        if a.cmd == "next":
            return cmd_next(a, series, reg)
        if a.cmd == "add":
            return cmd_add(a, series, reg)
        if not reg:
            raise UsageError(f"no register is bound under [suite.{a.suite}]; bind register or "
                             "pass --register")
        # Every suite whose register is this file contributes its series and folders.
        by_prefix = {s.prefix: s for s in series.every_series()}
        for name, table in tables.items():
            s = Series(name, table, binding_file, os.getcwd())
            if name != a.suite and s.register and os.path.isfile(s.register) \
                    and os.path.samefile(s.register, reg.path):
                for each in s.every_series():
                    by_prefix.setdefault(each.prefix, each)
        return cmd_check(a, by_prefix, reg)
    except UsageError as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
