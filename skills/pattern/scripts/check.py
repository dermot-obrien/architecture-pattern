#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Post-install check for the pattern skill (DD-11 of AI-Assisted Work).

Run from the workspace root, with SKILL_DIR set to the installed skill's directory:

    python scripts/check.py

Checks that the two skills this one needs are installed where an agent would find them,
`model` and `markdown-deck`, then runs `model doctor --skill pattern`, which checks the
workspace's [suite.pattern] bindings against inputs.toml, and reports the patterns root
composing searches (model 0.8.0 or later). draw.io desktop is optional:
without it, views are exported by hand and stamped, so its absence is a warning.

Exit 0: correct (warnings may be printed). Exit 1: problems, one line each.
Exit 2: usage or environment error. Offline and read-only.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: pattern needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)
if sys.argv[1:] in (["-h"], ["--help"]):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    print("usage: check.py   (run from the workspace root; takes no arguments)", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.environ.get("SKILL_DIR") or os.path.dirname(HERE))

# publish.py already knows every place an agent installs skills; use its search.
spec = importlib.util.spec_from_file_location("pattern_publish", os.path.join(HERE, "publish.py"))
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)

problems, warnings = [], []
found = {}
for name, entry, repo in (("model", "bin/model.py", "diagram-model"),
                          ("markdown-deck", "bin/markdown-deck.mjs", "markdown-deck")):
    path = publish.find_skill(name, entry)
    if os.path.exists(path):
        found[name] = path
    else:
        problems.append(f"the {name} skill is not installed in any skills directory an agent reads, "
                        f"nor on AGENT_SKILLS_PATH. Install it from "
                        f"https://github.com/dermot-obrien/{repo}.")

if "model" in found:
    env = dict(os.environ)
    # doctor finds pattern among model's siblings; make sure it looks where pattern is.
    env["AGENT_SKILLS_PATH"] = os.pathsep.join(
        p for p in (os.path.dirname(SKILL_DIR), env.get("AGENT_SKILLS_PATH", "")) if p)
    r = subprocess.run([sys.executable, found["model"], "doctor", "--skill", "pattern"],
                       capture_output=True, text=True, env=env, timeout=60)
    for line in (r.stdout + r.stderr).splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        problems.append("model doctor --skill pattern reported the errors above. Fix [suite.pattern] "
                        "in .agents/skill-bindings.toml.")
    # Composing: where a participation step's Uses finds the participating pattern. model
    # 0.8.0 reports it; an older model cannot resolve a composition at all.
    j = subprocess.run([sys.executable, found["model"], "doctor", "--skill", "pattern", "--json"],
                       capture_output=True, text=True, env=env, timeout=60)
    try:
        composition = json.loads(j.stdout).get("composition")
    except ValueError:
        composition = None
    if not composition:
        problems.append("the model skill installed is older than 0.8.0, so composite patterns (the "
                        "Uses column) cannot be checked. Update it from "
                        "https://github.com/dermot-obrien/diagram-model.")
    else:
        print(f"patterns root: {composition.get('patternsRoot') or '(unbound)'} "
              f"[{composition.get('from')}]; approved statuses: "
              f"{', '.join(composition.get('approvedStatuses') or [])}")
    d = subprocess.run([sys.executable, found["model"], "drawio"], capture_output=True, text=True,
                       timeout=60)
    if d.returncode != 0:
        warnings.append("draw.io desktop was not found, so views are exported by hand and stamped "
                        "with model stamp. Install draw.io desktop to render them.")

for w in warnings:
    print(f"warning: {w}")
for p in problems:
    print(p)
if not problems:
    print("pattern: ok")
sys.exit(1 if problems else 0)
