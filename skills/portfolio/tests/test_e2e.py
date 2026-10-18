# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""End to end, through the command line, on a copy of the mixed repository:
inventory, then tag, then archive, then regenerate the inventory; and the backlog."""
from __future__ import annotations

import json
import os
import shutil
import unittest

from helpers import FIXTURES, copy_fixture, git, read, run, write

BACKLOG = os.path.join(FIXTURES, "backlog.md")


def fm_of(path):
    from portfolio_lib import docs as D
    fm, _ = D.parse(D.split(read(path))[0])
    return fm


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp, self.repo = copy_fixture()
        self.addCleanup(shutil.rmtree, self.tmp)

    def p(self, *parts):
        return os.path.join(self.repo, *parts)

    def test_inventory_tag_archive_regenerate(self):
        # 1. inventory
        r = run(self.repo, "inventory")
        self.assertEqual(r.returncode, 0, r.stderr)
        inv = read(self.p("docs", "portfolio.md"))
        self.assertIn("[AP-004 Old gateway](../patterns/AP-004-old-gateway/index.md)", inv)
        self.assertIn("| archive | AP-004 |", inv)
        self.assertNotIn("AP-090", inv)
        self.assertIn("[Event-sourced ledger](../candidates/event-sourced-ledger.md)", inv)
        # regenerating changes nothing
        r = run(self.repo, "inventory")
        self.assertIn("unchanged", r.stderr)

        # 2. tag
        r = run(self.repo, "tag", "--dry-run")
        self.assertIn("2 changes planned", r.stdout)
        self.assertEqual(git(self.repo, "status", "--porcelain").stdout.strip(), "?? docs/portfolio.md")
        r = run(self.repo, "tag")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(fm_of(self.p("patterns", "AP-003-nightly-batch-export", "index.md"))["portfolio"]["state"], "proposed-deprecation")
        self.assertEqual(fm_of(self.p("patterns", "AP-005-whiteboard-sketch", "index.md"))["portfolio"]["state"], "needs-conversion")
        self.assertIn("0 changes", run(self.repo, "tag").stdout)  # idempotent

        # deprecation agreed for AP-003: a person marks it for archive
        r = run(self.repo, "tag", "patterns/AP-003-nightly-batch-export", "--state", "archive", "--reason", "Agreed")
        self.assertEqual(r.returncode, 0, r.stderr)

        # 3. archive
        r = run(self.repo, "archive", "--dry-run")
        self.assertIn("would archive patterns/AP-003-nightly-batch-export/", r.stdout)
        self.assertIn("would archive patterns/AP-004-old-gateway/", r.stdout)
        self.assertTrue(os.path.isdir(self.p("patterns", "AP-004-old-gateway")))
        r = run(self.repo, "archive", "--rewrite-links")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(self.p("patterns", "AP-004-old-gateway")))
        moved = self.p("archive", "patterns", "AP-004-old-gateway", "index.md")
        self.assertTrue(os.path.isfile(self.p("archive", "patterns", "AP-004-old-gateway", "components.svg")))
        fm = fm_of(moved)
        self.assertEqual((fm["portfolio"]["state"], fm["portfolio"]["archived_from"], fm["unlisted"]),
                         ("archived", "patterns/AP-004-old-gateway", "true"))
        status = git(self.repo, "status", "--porcelain").stdout
        self.assertIn("R  patterns/AP-004-old-gateway/index.md -> archive/patterns/AP-004-old-gateway/index.md", status)
        self.assertIn("../archive/patterns/AP-004-old-gateway/index.md", read(self.p("docs", "README.md")))
        self.assertIn("../../../patterns/AP-001-order-intake/index.md", read(moved))
        # nothing deleted: every file of the fixture is still somewhere
        self.assertEqual(run(self.repo, "archive").stdout.strip(), "nothing to archive")

        # 4. regenerate
        run(self.repo, "inventory")
        inv = read(self.p("docs", "portfolio.md"))
        self.assertNotIn("AP-004", inv)
        self.assertNotIn("AP-003", inv)
        r = run(self.repo, "inventory", "--include-archived", "--format", "json", "--out", "-")
        data = json.loads(r.stdout)
        self.assertEqual({a["id"] for a in data["archived"]}, {"AP-003", "AP-004"})
        self.assertEqual(data["counts"]["needs-conversion"], 1)
        self.assertEqual(run(self.repo, "check").returncode, 0)

    def test_archive_reports_links_without_rewriting(self):
        r = run(self.repo, "archive")
        self.assertIn("link breaks: docs/README.md:3", r.stdout)
        self.assertIn("warn: 4 links", r.stdout)
        self.assertIn("../patterns/AP-004-old-gateway/index.md", read(self.p("docs", "README.md")))

    def test_archive_with_stub(self):
        run(self.repo, "archive", "--stub")
        stub = self.p("patterns", "AP-004-old-gateway", "index.md")
        fm = fm_of(stub)
        self.assertEqual(fm["moved_to"], "../../archive/patterns/AP-004-old-gateway/index.md")
        self.assertNotIn("kind", fm)  # a stub is never discovered
        ids = [d["id"] for d in json.loads(run(self.repo, "discover", "--json").stdout)]
        self.assertEqual(ids.count("AP-004"), 1)

    def test_archive_outside_git_moves_and_never_deletes(self):
        tmp, repo = copy_fixture(with_git=False)
        self.addCleanup(shutil.rmtree, tmp)
        before = sorted(os.path.relpath(os.path.join(d, f), repo).replace("patterns/AP-004", "X")
                        for d, _, fs in os.walk(repo) for f in fs)
        r = run(repo, "archive")
        self.assertIn("(move)", r.stdout)
        after = sorted(os.path.relpath(os.path.join(d, f), repo).replace("archive/patterns/AP-004", "X")
                       for d, _, fs in os.walk(repo) for f in fs)
        self.assertEqual(before, after)

    def test_archive_refuses_an_occupied_destination(self):
        write(self.p("archive", "patterns", "AP-004-old-gateway", "index.md"), "# already here\n")
        r = run(self.repo, "archive")
        self.assertEqual(r.returncode, 1)
        self.assertIn("already exists in the archive", r.stdout)
        self.assertTrue(os.path.isdir(self.p("patterns", "AP-004-old-gateway")))

    def test_archive_dir_is_a_binding(self):
        p = self.p(".agents", "skill-bindings.toml")
        write(p, read(p).replace('archiveDir = "../archive"', 'archiveDir = "../retired/patterns"'))
        run(self.repo, "archive")
        self.assertTrue(os.path.isfile(self.p("retired", "patterns", "patterns", "AP-004-old-gateway", "index.md")))

    def test_sign_then_check_clean(self):
        self.assertIn("would sign", run(self.repo, "sign", "--dry-run").stdout)
        run(self.repo, "sign")
        fm = fm_of(self.p("patterns", "legacy", "AP-006-file-transfer", "index.md"))
        self.assertEqual((fm["kind"], fm["id"]), ("pattern", "AP-006"))
        r = run(self.repo, "check")
        self.assertIn("0 errors, 0 warnings", r.stdout)

    def test_html_inventory(self):
        out = os.path.join(self.tmp, "site", "portfolio.html")
        run(self.repo, "inventory", "--out", out)
        page = read(out)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("prefers-color-scheme: dark", page)
        self.assertIn('href="../repo/patterns/AP-001-order-intake/index.md"', page)

    def test_site_links_use_stable_addresses(self):
        p = self.p(".agents", "skill-bindings.toml")
        write(p, read(p) + 'linkBase = "/architecture/"\n')
        inv = run(self.repo, "inventory", "--out", self.p("docs", "x.md")) and read(self.p("docs", "x.md"))
        self.assertIn("[AP-001 Order intake](/architecture/id/AP-001/)", inv)
        self.assertIn("[Event-sourced ledger](../candidates/event-sourced-ledger.md)", inv)


class Backlog(unittest.TestCase):
    def setUp(self):
        self.tmp, self.repo = copy_fixture()
        self.addCleanup(shutil.rmtree, self.tmp)

    def p(self, *parts):
        return os.path.join(self.repo, *parts)

    def test_dry_run_changes_nothing(self):
        r = run(self.repo, "backlog", BACKLOG, "--dry-run")
        self.assertIn("Dry run", r.stdout)
        self.assertEqual(git(self.repo, "status", "--porcelain").stdout, "")

    def test_placeholders_promotion_and_report(self):
        report = os.path.join(self.tmp, "report.json")
        r = run(self.repo, "backlog", BACKLOG, "--report", report)
        self.assertEqual(r.returncode, 1)  # the widget row is a problem
        data = json.loads(read(report))
        self.assertEqual(data["counts"], {"exact": 4, "fuzzy": 1, "ambiguous": 2, "new": 4, "duplicate": 1})
        ra = self.p("patterns", "RA-002-zero-trust-ingress", "index.md")
        cl = self.p("patterns", "CL-002-release-coordination", "index.md")
        fm = fm_of(ra)
        self.assertEqual((fm["kind"], fm["id"], fm["pattern_type"], fm["status"]), ("pattern", "RA-002", "reference-architecture", "draft"))
        self.assertEqual(fm["portfolio"], {"state": "placeholder", "priority": "medium", "target_quarter": "2027-Q2",
                                           "committed": "true", "since": "2026-10-18", "backlog_ref": "BL-6"})
        self.assertIn("# RA-002 Zero-trust ingress", read(ra))
        self.assertIn("## Building Blocks", read(ra))         # the reference architecture template
        self.assertIn("## Participants", read(cl))             # a collaboration template
        self.assertEqual(fm_of(cl)["pattern_type"], "collaboration")
        # the committed candidate was promoted, its history moved with git mv and its notes kept
        ap = self.p("patterns", "AP-007-event-sourced-ledger", "index.md")
        self.assertFalse(os.path.exists(self.p("candidates", "event-sourced-ledger.md")))
        self.assertIn("## Candidate notes\n\nRaised by the finance platform team.", read(ap))
        self.assertEqual(fm_of(ap)["portfolio"]["target_quarter"], "2027-Q2")
        # nothing for the ambiguous, uncommitted or unknown rows
        self.assertFalse(os.path.exists(self.p("candidates", "data-mesh.md")))
        self.assertFalse(any("widget" in f for f in os.listdir(self.p("patterns"))))
        # the new documents are discovered by their signature and pass the check
        self.assertEqual(run(self.repo, "check").returncode, 0)
        # a second run creates nothing more
        before = sorted(os.listdir(self.p("patterns")))
        data2 = json.loads(run(self.repo, "backlog", BACKLOG, "--json").stdout)
        self.assertEqual(sorted(os.listdir(self.p("patterns"))), before)
        # only Data mesh, which is not committed, and the widget row, whose type is unknown
        self.assertEqual({r["name"] for r in data2["results"] if r["result"] == "new"}, {"Data mesh", "Widget factory"})
        placeholders = json.loads(run(self.repo, "inventory", "--format", "json", "--out", "-").stdout)["counts"]["placeholder"]
        self.assertEqual(placeholders, 3)

    def test_update_and_candidates(self):
        run(self.repo, "backlog", BACKLOG, "--update", "--candidates")
        p = fm_of(self.p("patterns", "AP-002-event-driven-ingestion", "index.md"))["portfolio"]
        self.assertEqual((p["priority"], p["committed"], p["target_quarter"]), ("high", "true", "2027-Q1"))
        cand = fm_of(self.p("candidates", "data-mesh.md"))
        self.assertEqual((cand["kind"], cand["portfolio"]["priority"]), ("candidate", "low"))

    def test_register_row_added(self):
        p = self.p(".agents", "skill-bindings.toml")
        write(p, read(p).replace('outputDir = "../patterns"\n', 'outputDir = "../patterns"\nregister = "../catalogue.csv"\n', 1))
        write(self.p("catalogue.csv"), "id,type,name,status,path,url,summary\nRA-007,reference-architecture,Minted elsewhere,,,,\n")
        run(self.repo, "backlog", os.path.join(FIXTURES, "backlog.csv"))
        rows = read(self.p("catalogue.csv")).splitlines()
        # the register's own RA-007 is respected, so the next is RA-008
        self.assertIn("RA-008,reference-architecture,Zero-trust ingress,draft,patterns/RA-008-zero-trust-ingress,,", rows)

    def test_use_case_placeholder(self):
        b = os.path.join(self.tmp, "uc.md")
        write(b, "- Cancel an order (use case); committed\n")
        run(self.repo, "backlog", b)
        uc = self.p("use-cases", "UC-002-cancel-an-order", "index.md")
        self.assertEqual(fm_of(uc)["kind"], "use-case")
        self.assertIn("# UC-002 Cancel an order", read(uc))
        self.assertIn("## Participants", read(uc))


if __name__ == "__main__":
    unittest.main()
