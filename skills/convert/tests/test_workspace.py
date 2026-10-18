# SPDX-License-Identifier: Apache-2.0
"""Finding and pairing sources, the conversion folder, and archiving."""
from __future__ import annotations

import os

from conftest import git
from convertlib import workspace as ws


def touch(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return str(path)


def names(units):
    return {os.path.basename(u["diagram"]): sorted(os.path.basename(t) for t in u["texts"])
            for u in units}


def test_kinds_and_stems():
    assert ws.kind("a.drawio") == "drawio" and ws.kind("a.dio") == "drawio"
    assert ws.kind("a.drawio.svg") == "svg" and ws.kind("a.drawio.png") == "image"
    assert ws.kind("a.md") == "text" and ws.kind("a.pdf") == ""
    assert ws.stem("x/order-intake.drawio.svg") == "order-intake"


def test_pairing_by_link_then_stem_then_folder(tmp_path):
    d = tmp_path
    touch(d / "one" / "flow.drawio", "<mxfile/>")
    touch(d / "one" / "README.md", "# One")
    touch(d / "two" / "a.svg", "<svg/>")
    touch(d / "two" / "b.svg", "<svg/>")
    touch(d / "two" / "a.md", "# A")
    touch(d / "two" / "about-b.md", "See ![the picture](./b.svg)")
    touch(d / "two" / "stray.md", "# Nothing")
    units, unpaired = ws.pair(ws.discover([str(d)]))
    assert names(units) == {"flow.drawio": ["README.md"], "a.svg": ["a.md"], "b.svg": ["about-b.md"]}
    assert [os.path.basename(p) for p in unpaired] == ["stray.md"]


def test_exports_of_one_diagram_are_one_unit(tmp_path):
    for f in ("x.drawio", "x.drawio.svg", "x.png"):
        touch(tmp_path / f, "<mxfile/>")
    units, _ = ws.pair(ws.discover([str(tmp_path)]))
    assert len(units) == 1
    assert os.path.basename(units[0]["diagram"]) == "x.drawio"
    assert [os.path.basename(p) for p in units[0]["alternates"]] == ["x.drawio.svg", "x.png"]


def test_discover_skips_hidden_and_given_folders(tmp_path):
    touch(tmp_path / "a.drawio")
    touch(tmp_path / ".git" / "b.drawio")
    touch(tmp_path / "conversions" / "c.drawio")
    found = ws.discover([str(tmp_path)], skip=[str(tmp_path / "conversions")])
    assert [os.path.basename(p) for p in found] == ["a.drawio"]


def test_run_folder_never_reused(tmp_path):
    first = ws.new_run_dir(str(tmp_path), "Order Intake", "2026-01-02")
    os.makedirs(first)
    assert os.path.basename(first) == "2026-01-02-order-intake"
    assert os.path.basename(ws.new_run_dir(str(tmp_path), "Order Intake", "2026-01-02")) == \
        "2026-01-02-order-intake-2"


def plan(paths, archive_dir_for, archive=True):
    units, unpaired = ws.pair(ws.discover(paths))
    for u in units:
        u["slug"] = ws.slug(u["name"])
    return ws.plan_sources(units, unpaired, archive_dir_for, archive)


def test_outside_git_copies_and_leaves(tmp_path):
    src = touch(tmp_path / "m" / "x.drawio", "<mxfile/>")
    entries = plan([str(tmp_path / "m")], lambda repo: os.path.join(repo, "archive"))
    assert entries[0]["archive"] == "" and "not in a git repository" in entries[0]["note"]
    run = tmp_path / "run"
    ws.gather(entries, str(run))
    assert ws.archive(entries) == []
    assert os.path.exists(src) and (run / entries[0]["gathered"]).exists()
    assert len(entries[0]["sha256"]) == 64


def test_in_git_moves_tracked_and_leaves_untracked(git_repo):
    tracked = touch(git_repo / "docs" / "x.drawio", "<mxfile/>")
    touch(git_repo / "docs" / "x.md", "# X")
    git("add", "docs/x.drawio", cwd=git_repo)
    git("commit", "-qm", "x", cwd=git_repo)
    entries = plan([str(git_repo / "docs")], lambda repo: os.path.join(repo, "archive"))
    by = {os.path.basename(e["original"]): e for e in entries}
    assert by["x.drawio"]["tracked"] and by["x.drawio"]["archive"].endswith(os.path.join("archive", "docs", "x.drawio"))
    assert not by["x.md"]["tracked"] and by["x.md"]["archive"] == ""
    ws.gather(entries, str(git_repo / "conversions" / "run"))
    assert ws.archive(entries) == []
    assert not os.path.exists(tracked) and os.path.exists(git_repo / "archive" / "docs" / "x.drawio")
    assert os.path.exists(git_repo / "docs" / "x.md")
    status = git("status", "--short", cwd=git_repo).stdout
    assert "R  docs/x.drawio -> archive/docs/x.drawio" in status


def test_an_occupied_archive_path_is_never_overwritten(git_repo):
    touch(git_repo / "docs" / "x.drawio", "<mxfile/>")
    touch(git_repo / "archive" / "docs" / "x.drawio", "older")
    git("add", "-A", cwd=git_repo)
    git("commit", "-qm", "x", cwd=git_repo)
    entries = plan([str(git_repo / "docs")], lambda repo: os.path.join(repo, "archive"))
    problems = ws.archive(entries)
    assert problems and "already exists" in problems[0]
    assert os.path.exists(git_repo / "docs" / "x.drawio")
    with open(git_repo / "archive" / "docs" / "x.drawio", encoding="utf-8") as fh:
        assert fh.read() == "older"


def test_no_archive_plans_no_moves(git_repo):
    touch(git_repo / "x.drawio", "<mxfile/>")
    git("add", "-A", cwd=git_repo)
    git("commit", "-qm", "x", cwd=git_repo)
    entries = plan([str(git_repo)], lambda repo: os.path.join(repo, "archive"), archive=False)
    assert entries[0]["archive"] == ""
