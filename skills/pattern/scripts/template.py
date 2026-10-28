#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Which template a new pattern is written from, and whether every template in use fits.

    python scripts/template.py which [--type TYPE]
    python scripts/template.py check

Run from the workspace root. The template for a pattern type is the first of:

    1. [suite.pattern.types.<TYPE>] template   the repository's own for that type
                                               ("builtin:<name>" names a shipped one)
    2. [suite.pattern] template                the repository's own for every pattern
    3. assets/templates/<TYPE>.md              shipped with this skill for that type:
                                               architecture-pattern, reference-architecture,
                                               solution-design
    4. assets/template.md                      shipped with this skill, for any pattern

Without --type, or with no types bound, it is 2 else 4. A repository's template may say
anything, so long as it keeps the construct the binding reads.

which  prints the template's path, and on stderr where it came from.
check  runs `model contract` on the template of every bound type (or the one template when
       no types are bound): every section, table and column the binding reads, a scenario
       heading and its steps table. A repository's own template for a type is also held
       to that type's series. Exit 1 if any template has an error.

Exit 2: usage or bindings. Standard library only; Python 3.11 or newer.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.environ.get("SKILL_DIR") or os.path.dirname(HERE))
ASSETS = os.path.join(SKILL_DIR, "assets")


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


register = _load("pattern_register", "register.py")


def builtin(name) -> str:
    return os.path.join(ASSETS, "templates", f"{name}.md")


def resolve(table, binding_file, type_name="") -> tuple:
    """(path, where it came from, whether the repository supplied it)."""
    types = {str(k): v for k, v in (table.get("types") or {}).items() if isinstance(v, dict)}
    if type_name:
        if type_name not in types:
            raise register.UsageError(
                f"'{type_name}' is not a type bound under [suite.pattern.types]; expected one "
                f"of {', '.join(sorted(types)) or '(none bound)'}")
        own = str(types[type_name].get("template") or "")
        if own.startswith("builtin:"):
            return builtin(own[len("builtin:"):]), f"[suite.pattern.types.{type_name}] template", False
        if own:
            return (register.bound(binding_file, own),
                    f"[suite.pattern.types.{type_name}] template", True)
    if table.get("template"):
        return register.bound(binding_file, table["template"]), "[suite.pattern] template", True
    if type_name and os.path.isfile(builtin(type_name)):
        return builtin(type_name), f"shipped for {type_name}", False
    return os.path.join(ASSETS, "template.md"), "shipped", False


def cmd_which(a, table, binding_file):
    path, source, _own = resolve(table, binding_file, a.type or "")
    if not os.path.isfile(path):
        raise register.UsageError(f"the template {path}, from {source}, does not exist")
    print(f"template from {source}", file=sys.stderr)
    print(path)
    return 0


def cmd_check(table, binding_file, root):
    publish = _load("pattern_publish", "publish.py")
    model = publish.find_skill("model", "bin/model.py")
    if not os.path.exists(model):
        raise register.UsageError("the model skill is not installed, so templates cannot be checked")
    types = sorted(k for k, v in (table.get("types") or {}).items() if isinstance(v, dict))
    worst = 0
    for type_name in types or [""]:
        path, source, own = resolve(table, binding_file, type_name)
        label = type_name or "every pattern"
        if not os.path.isfile(path):
            print(f"error: the template for {label}, {path} from {source}, does not exist")
            worst = 1
            continue
        cmd = [sys.executable, model, "contract", path, "--near", root]
        # A shipped template carries the example series in its H1; only the repository's
        # own is held to the repository's series.
        if type_name and own:
            cmd += ["--type", type_name]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"template for {label}: {source}")
        for line in (r.stdout + r.stderr).splitlines():
            if line.strip():
                print(f"  {line.strip()}")
        worst = max(worst, 1 if r.returncode else 0)
    return worst


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="template.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("which", help="print the template a new pattern is written from")
    w.add_argument("--type", help="a pattern type bound under [suite.pattern.types]")
    sub.add_parser("check", help="check every template in use has the construct the binding reads")
    a = ap.parse_args(argv)
    try:
        binding_file, tables = register.load_bindings(os.getcwd())
        table = tables.get("pattern", {})
        if a.cmd == "which":
            return cmd_which(a, table, binding_file)
        return cmd_check(table, binding_file, register.repo_root(binding_file, os.getcwd()))
    except register.UsageError as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
