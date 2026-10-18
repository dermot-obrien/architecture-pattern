#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Post-install check for the draft skill.

Run from the workspace root:

    python scripts/check.py

Confirms the portfolio skill is installed where draft.py finds it, and lists the placeholders
waiting for a draft and the drafts waiting for review. Read-only.

Exit 0: correct. Exit 1: problems. Exit 2: usage or environment.
"""
from __future__ import annotations

import importlib.util
import os
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: draft needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)
if sys.argv[1:] in (["-h"], ["--help"]):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    print("usage: check.py   (run from the workspace root; takes no arguments)", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("draft", os.path.join(HERE, "draft.py"))
draft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(draft)  # exits 2 with the install hint when portfolio is missing

print(f"portfolio skill: {os.path.dirname(draft._PF)}")
try:
    b = draft.Bindings(os.getcwd())
except draft.UsageError as ex:
    print(f"error: {ex}")
    sys.exit(1)
docs = draft.D.discover(b.roots, b.root, b.archive_dir, b.exclude)
for state, what in (("placeholder", "waiting for a draft"), ("draft", "waiting for review")):
    found = [d for d in docs if d.state == state]
    print(f"{len(found)} {what}")
    for d in found:
        print(f"  {d.id or '-'} {d.rel}")
sys.exit(0)
