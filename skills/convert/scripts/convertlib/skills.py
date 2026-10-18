# SPDX-License-Identifier: Apache-2.0
"""Find the skills this one drives, wherever they are installed: model, pattern, use-case.

The same places the pattern skill's publish.py searches: beside this skill, each
directory on AGENT_SKILLS_PATH, the project and user skills directories agents read, and
Claude Code plugins, newest first.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(os.path.dirname(HERE))
SKILLS = os.path.dirname(SKILL_DIR)

PROJECT_SKILL_DIRS = (".agents/skills", ".github/skills", ".cursor/skills", ".claude/skills",
                      ".codex/skills")
USER_SKILL_DIRS = (".agents/skills", ".copilot/skills", ".cursor/skills", ".claude/skills",
                   ".gemini/skills", ".codex/skills")


def roots() -> list:
    out = [SKILLS]
    out += [p for p in os.environ.get("AGENT_SKILLS_PATH", "").split(os.pathsep) if p]
    for start in (SKILL_DIR, os.getcwd()):
        d = os.path.abspath(start)
        while True:
            out += [os.path.join(d, *r.split("/")) for r in PROJECT_SKILL_DIRS]
            if os.path.dirname(d) == d:
                break
            d = os.path.dirname(d)
    home = os.path.expanduser("~")
    out += [os.path.join(home, *r.split("/")) for r in USER_SKILL_DIRS]
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(home, ".claude")
    cache = os.path.join(config, "plugins", "cache")
    if os.path.isdir(cache):
        for market in sorted(os.listdir(cache)):
            mdir = os.path.join(cache, market)
            if not os.path.isdir(mdir):
                continue
            for plugin in sorted(os.listdir(mdir)):
                pdir = os.path.join(mdir, plugin)
                if not os.path.isdir(pdir):
                    continue
                versions = sorted(os.listdir(pdir), reverse=True, key=lambda v: tuple(
                    int(x) if x.isdigit() else -1 for x in v.split("-")[0].split(".")))
                out += [os.path.join(pdir, v, "skills") for v in versions]
    return out


def find(name, entry) -> str:
    """The path to `entry` inside the named skill, first found, else ""."""
    for root in roots():
        p = os.path.join(root, name, *entry.split("/"))
        if os.path.exists(p):
            return p
    return ""


def model_cli() -> str:
    return find("model", "bin/model.py")


def pattern_script(name) -> str:
    return find("pattern", f"scripts/{name}")


def load_pattern_module(name):
    """Import one of the pattern skill's scripts, such as register.py, as a module."""
    path = pattern_script(f"{name}.py")
    if not path:
        return None
    spec = importlib.util.spec_from_file_location(f"pattern_{name.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_model(*args, timeout=300):
    """Run the model CLI. Returns the CompletedProcess, or None when model is not installed."""
    cli = model_cli()
    if not cli:
        return None
    return subprocess.run([sys.executable, cli, *map(str, args)], capture_output=True,
                          text=True, timeout=timeout)
