# SPDX-License-Identifier: Apache-2.0
"""Shared fixtures for the convert skill's tests.

The unit tests need only Python. The end-to-end tests drive the model skill and the
pattern skill's publish.py, so they need `model` installed beside this skill or on
AGENT_SKILLS_PATH, and are skipped, saying so, when it is not.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(TESTS)
SCRIPTS = os.path.join(SKILL, "scripts")
EXAMPLES = os.path.join(SKILL, "examples")
SOURCES = os.path.join(EXAMPLES, "sources")
CONVERT = os.path.join(SCRIPTS, "convert.py")
PUBLISH = os.path.join(os.path.dirname(SKILL), "pattern", "scripts", "publish.py")

sys.path.insert(0, SCRIPTS)

from convertlib import skills  # noqa: E402

HAS_MODEL = bool(skills.model_cli())
needs_model = pytest.mark.skipif(not HAS_MODEL, reason="the model skill is not installed "
                                 "beside this one or on AGENT_SKILLS_PATH")


def source(*parts) -> str:
    return os.path.join(SOURCES, *parts)


def run_convert(*args, cwd=None, check=True):
    r = subprocess.run([sys.executable, CONVERT, *map(str, args)], cwd=cwd,
                       capture_output=True, text=True, timeout=600)
    if check and r.returncode not in (0, 1):
        raise AssertionError(f"convert.py {' '.join(map(str, args))} exited {r.returncode}:\n"
                             f"{r.stdout}\n{r.stderr}")
    return r


def run_json(*args, cwd=None):
    r = run_convert(*args, "--json", cwd=cwd)
    try:
        return json.loads(r.stdout), r
    except ValueError:
        raise AssertionError(f"no JSON from convert.py:\n{r.stdout}\n{r.stderr}")


def publish(folder):
    r = subprocess.run([sys.executable, PUBLISH, str(folder), "--recursive", "--no-deck",
                        "--render", "never", "--json"], capture_output=True, text=True,
                       timeout=600)
    return json.loads(r.stdout), r


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def copy_sources(tmp_path):
    """Copy named example folders into a fresh folder, outside any git repository."""
    def _copy(*names, into=None):
        dest = into or (tmp_path / "material")
        dest.mkdir(parents=True, exist_ok=True)
        for n in names:
            shutil.copytree(source(n), dest / n)
        return dest
    return _copy


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    git("config", "user.email", "test@example.org", cwd=repo)
    git("config", "user.name", "Test", cwd=repo)
    return repo
