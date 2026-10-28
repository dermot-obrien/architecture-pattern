#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Post-install check for the portfolio skill.

Run from the workspace root:

    python scripts/check.py

Reads [suite.portfolio], says which folders it scans and where it archives, finds the pattern
and use-case skills whose templates placeholders are written from, and runs `portfolio.py check`
on what it finds. A missing pattern or use-case skill is a warning: everything but placeholders
of that type still works.

Exit 0: correct (warnings may be printed). Exit 1: problems. Exit 2: usage or bindings.
"""
from __future__ import annotations

import os
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: portfolio needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)
if sys.argv[1:] in (["-h"], ["--help"]):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    print("usage: check.py   (run from the workspace root; takes no arguments)", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import portfolio  # noqa: E402
from portfolio_lib import lifecycle as L  # noqa: E402
from portfolio_lib.bindings import Bindings, UsageError  # noqa: E402

try:
    b = Bindings(os.getcwd())
except UsageError as ex:
    print(f"error: {ex}")
    sys.exit(2)
rel = lambda p: os.path.relpath(p, b.root)  # noqa: E731
print(f"bindings: {b.file or '(none: defaults apply)'}")
print(f"scans: {', '.join(rel(r) for r in b.roots)}")
print(f"archives to: {rel(b.archive_dir)}")
print(f"inventory: {rel(b.inventory) if b.inventory else '(printed; bind [suite.portfolio] inventory to write a page)'}")
warnings = 0
for name in ("pattern", "use-case"):
    where = portfolio.find_skill(name, b.root)
    if where:
        print(f"{name} skill: {where}")
    else:
        warnings += 1
        print(f"warn: the {name} skill is not installed, so placeholders of its types need a bound template")
docs = portfolio.load_docs(b)
errors, warns = L.check(docs, b)
for w in warns:
    print(f"warn: {w}")
for e in errors:
    print(f"error: {e}")
print(f"{len(docs)} signed documents, {len(errors)} errors, {len(warns) + warnings} warnings")
sys.exit(1 if errors else 0)
