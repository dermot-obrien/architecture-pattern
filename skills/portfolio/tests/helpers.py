# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Shared set-up: the library on the path, a copy of a fixture repository, and the CLI."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL, "scripts")
FIXTURES = os.path.join(HERE, "fixtures")
CLI = os.path.join(SCRIPTS, "portfolio.py")
TODAY = "2026-10-18"
sys.path.insert(0, SCRIPTS)
os.environ["PORTFOLIO_TODAY"] = TODAY


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=False)


def copy_fixture(name="mixed-repo", with_git=True):
    """A fresh copy of a fixture repository in a temporary folder, committed when with_git."""
    tmp = tempfile.mkdtemp(prefix="portfolio-")
    dest = os.path.join(tmp, "repo")
    shutil.copytree(os.path.join(FIXTURES, name), dest)
    if with_git:
        git(dest, "init", "-q")
        git(dest, "add", "-A")
        git(dest, "-c", "user.email=test@example.org", "-c", "user.name=Test", "commit", "-qm", "fixture")
    return tmp, dest


def run(repo, *args):
    env = dict(os.environ, PORTFOLIO_TODAY=TODAY)
    return subprocess.run([sys.executable, CLI, *args], cwd=repo, capture_output=True, text=True, env=env)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
