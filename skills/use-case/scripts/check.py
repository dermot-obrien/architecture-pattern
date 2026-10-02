#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Post-install check for the use-case skill (DD-11 of AI-Assisted Work).

Run from the workspace root. SKILL_DIR, the installed skill's directory, defaults to the
folder above this script; an installer sets it:

    python scripts/check.py

Checks that the three skills this one needs are installed where an agent would find them,
`pattern`, `model` and `markdown-deck`, then runs `model doctor --skill use-case`, which
checks the workspace's [suite.use-case] bindings against inputs.toml. draw.io desktop is
optional: without it, views are exported by hand and stamped, so its absence is a warning.

Exit 0: correct (warnings may be printed). Exit 1: problems, one line each.
Exit 2: usage or environment error. Offline and read-only.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: use-case needs 3.11 or newer.", file=sys.stderr)
    sys.exit(2)
if sys.argv[1:] in (["-h"], ["--help"]):
    print(__doc__.strip())
    sys.exit(0)
if len(sys.argv) > 1:
    print("usage: check.py   (run from the workspace root; takes no arguments)", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.environ.get("SKILL_DIR") or os.path.dirname(HERE))
SKILL_DIRS = (".agents/skills", ".github/skills", ".cursor/skills", ".claude/skills")


def pattern_publish():
    """The pattern skill's publish.py, which knows every other place a skill is installed."""
    roots = [os.path.dirname(SKILL_DIR)]
    roots += [p for p in os.environ.get("AGENT_SKILLS_PATH", "").split(os.pathsep) if p]
    d = os.getcwd()
    while True:
        roots += [os.path.join(d, *r.split("/")) for r in SKILL_DIRS]
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    home = os.path.expanduser("~")
    roots += [os.path.join(home, *r.split("/")) for r in SKILL_DIRS + (".copilot/skills",)]
    for root in roots:
        p = os.path.join(root, "pattern", "scripts", "publish.py")
        if os.path.exists(p):
            return p
    return None


problems, warnings = [], []
publish_py = pattern_publish()
if not publish_py:
    print("the pattern skill is not installed beside this one, in any skills directory an agent "
          "reads, nor on AGENT_SKILLS_PATH. Install it from "
          "https://github.com/dermot-obrien/architecture-pattern.")
    sys.exit(1)
spec = importlib.util.spec_from_file_location("pattern_publish", publish_py)
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)

found = {"pattern": publish_py}
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
    # doctor finds use-case among model's siblings; make sure it looks where use-case is.
    env["AGENT_SKILLS_PATH"] = os.pathsep.join(
        p for p in (os.path.dirname(SKILL_DIR), env.get("AGENT_SKILLS_PATH", "")) if p)
    r = subprocess.run([sys.executable, found["model"], "doctor", "--skill", "use-case"],
                       capture_output=True, text=True, env=env, timeout=60)
    for line in (r.stdout + r.stderr).splitlines():
        if line.strip():
            print(line)
    if r.returncode != 0:
        problems.append("model doctor --skill use-case reported the errors above. Fix [suite.use-case] "
                        "in .agents/skill-bindings.toml.")
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
    print("use-case: ok")
sys.exit(1 if problems else 0)
