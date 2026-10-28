# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""[suite.portfolio] and the parts of [suite.pattern] and [suite.use-case] the portfolio reads.

Paths in the binding file are relative to the file's own folder, as in every suite. The
binding file is found by searching upward from the working directory, as register.py does.
"""
from __future__ import annotations

import os
import tomllib

from .docs import PATTERN_TYPES, SERIES

BINDING_NAMES = (".agents/skill-bindings.toml", "skill-bindings.toml", "model.toml", ".model.toml")
DEFAULT_OUTPUT = {"pattern": "patterns", "use-case": "use-cases"}


class UsageError(Exception):
    pass


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


def repo_root(binding_file, start) -> str:
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


class Bindings:
    def __init__(self, start=None, binding_file=None):
        start = os.path.abspath(start or os.getcwd())
        self.file = binding_file or find_bindings(start)
        raw = {}
        if self.file:
            try:
                with open(self.file, "rb") as fh:
                    raw = tomllib.load(fh)
            except (OSError, tomllib.TOMLDecodeError) as ex:
                raise UsageError(f"{self.file}: {ex}")
        suite = raw.get("suite") or {}
        self.portfolio = suite.get("portfolio") or {}
        self.pattern = suite.get("pattern") or {}
        self.use_case = suite.get("use-case") or {}
        self.root = repo_root(self.file, start)

    def path(self, value, default=None) -> str:
        """A bound path, or the default relative to the repository root."""
        if value:
            return os.path.normpath(os.path.join(os.path.dirname(self.file), str(value)))
        return os.path.normpath(os.path.join(self.root, default)) if default else ""

    # --- where to look
    @property
    def roots(self) -> list:
        v = self.portfolio.get("roots")
        if not v:
            return [self.root]
        return [self.path(p) for p in ([v] if isinstance(v, str) else v)]

    @property
    def exclude(self) -> list:
        v = self.portfolio.get("exclude") or []
        return [self.path(p) for p in ([v] if isinstance(v, str) else v)]

    @property
    def archive_dir(self) -> str:
        return self.path(self.portfolio.get("archiveDir"), "archive")

    @property
    def candidates_dir(self) -> str:
        return self.path(self.portfolio.get("candidatesDir"), "candidates")

    @property
    def inventory(self) -> str:
        return self.path(self.portfolio.get("inventory"))

    @property
    def link_base(self) -> str:
        return str(self.portfolio.get("linkBase") or "")

    @property
    def stubs(self) -> bool:
        return bool(self.portfolio.get("stubs", False))

    @property
    def stale_after_days(self):
        v = self.portfolio.get("staleAfterDays")
        return int(v) if v not in (None, "") else None

    @property
    def default_owner(self) -> str:
        return str(self.portfolio.get("defaultOwner") or "unassigned")

    @property
    def form(self) -> dict:
        """{type: {part: [headings]}} from [suite.portfolio.form.<type>]."""
        out = {}
        for t, spec in (self.portfolio.get("form") or {}).items():
            if isinstance(spec, dict):
                out[t] = {k: ([v] if isinstance(v, str) else list(v)) for k, v in spec.items()}
        return out

    # --- where new documents go, and their series
    def output_dir(self, dtype) -> str:
        if dtype == "use-case":
            return self.path(self.use_case.get("outputDir"), DEFAULT_OUTPUT["use-case"])
        return self.path(self.pattern.get("outputDir"), DEFAULT_OUTPUT["pattern"])

    def series(self, dtype) -> str:
        if dtype == "use-case":
            return str(self.use_case.get("idSeries") or SERIES["use-case"])
        types = self.pattern.get("types") or {}
        t = types.get(dtype) if isinstance(types, dict) else None
        if isinstance(t, dict) and t.get("idSeries"):
            return str(t["idSeries"])
        return SERIES.get(dtype, "AP")

    def register(self, dtype) -> str:
        table = self.use_case if dtype == "use-case" else self.pattern
        return self.path(table.get("register")) if table.get("register") else ""

    def template(self, dtype) -> str:
        """The repository's own template for a type, as template.py resolves it, else ""."""
        if dtype == "use-case":
            return self.path(self.use_case.get("template")) if self.use_case.get("template") else ""
        types = self.pattern.get("types") or {}
        t = types.get(dtype) if isinstance(types, dict) else None
        own = str((t or {}).get("template") or "") if isinstance(t, dict) else ""
        if own and not own.startswith("builtin:"):
            return self.path(own)
        if own.startswith("builtin:"):
            return "builtin:" + own[len("builtin:"):]
        return self.path(self.pattern.get("template")) if self.pattern.get("template") else ""

    @property
    def pattern_types(self):
        types = self.pattern.get("types") or {}
        bound = [k for k, v in types.items() if isinstance(v, dict)] if isinstance(types, dict) else []
        return bound or list(PATTERN_TYPES)
