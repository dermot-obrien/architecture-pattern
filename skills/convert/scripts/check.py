#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Post-install check for the convert skill (DD-11 of AI-Assisted Work).

Run from the workspace root:

    python scripts/check.py

Checks that the skills this one drives are installed where an agent would find them,
`model`, `pattern` and `use-case`, that the pattern skill ships the template of each of
the four types, and that git is on PATH for archiving. Prints where conversion folders
and archived originals go, from [suite.convert] or the defaults.

Exit 0: correct (warnings may be printed). Exit 1: problems, one line each.
Exit 2: usage or environment error. Offline and read-only.
"""
from __future__ import annotations

import os
import shutil
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: convert needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)
if sys.argv[1:] in (["-h"], ["--help"]):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    print("usage: check.py   (run from the workspace root; takes no arguments)", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from convertlib import draft, skills  # noqa: E402
import convert  # noqa: E402

problems, warnings = [], []
for name, entry in (("model", "bin/model.py"), ("pattern", "scripts/register.py"),
                    ("use-case", "assets/template.md")):
    path = skills.find(name, entry)
    if path:
        print(f"  {name:<9}: {os.path.dirname(os.path.dirname(path))}")
    else:
        problems.append(f"the {name} skill is not installed beside this one, on AGENT_SKILLS_PATH "
                        "or in any agent skills directory")
for type_name, profile in draft.PROFILES.items():
    if not skills.find(profile["skill"], profile["template"]):
        problems.append(f"no template for {type_name}: {profile['skill']}/{profile['template']} "
                        "is missing; the pattern skill is older than 0.13.0")
if not shutil.which("git"):
    warnings.append("git is not on PATH, so originals can be copied but not archived")

try:
    binding_file, table = convert.convert_table(os.getcwd())
except convert.UsageError as ex:
    print(f"error: {ex}", file=sys.stderr)
    sys.exit(2)
work = convert.bound(binding_file, table.get("workDir")) if binding_file else ""
archive = convert.bound(binding_file, table.get("archiveDir")) if binding_file else ""
print(f"  workDir   : {work or 'conversions/ at the repository root (the default)'}")
print(f"  archiveDir: {archive or 'archive/ at the root of each source repository (the default)'}")

for w in warnings:
    print(f"warning: {w}")
for p in problems:
    print(p)
print(f"convert: {'ok' if not problems else 'failed'}")
sys.exit(1 if problems else 0)
