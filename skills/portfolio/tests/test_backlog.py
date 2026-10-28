# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Parsing a backlog in each of its forms, and matching it: exact, fuzzy, ambiguous and new."""
from __future__ import annotations

import os
import unittest

import helpers  # noqa: F401
from helpers import FIXTURES, read
from portfolio_lib import backlog as B
from portfolio_lib import docs as D
from portfolio_lib.bindings import Bindings

REPO = os.path.join(FIXTURES, "mixed-repo")


class Parse(unittest.TestCase):
    def test_table(self):
        rows, problems = B.parse(read(os.path.join(FIXTURES, "backlog.md")))
        self.assertEqual(len(rows), 12)
        first = rows[0]
        self.assertEqual((first["name"], first["type"], first["committed"], first["priority"], first["target_quarter"], first["ref"]),
                         ("Order intake", "architecture-pattern", True, "high", "2026-Q4", "BL-1"))
        self.assertEqual(rows[1]["target_quarter"], "2027-Q1")  # written as Q1 2027
        self.assertEqual(rows[5]["type"], "reference-architecture")  # written as RA
        self.assertEqual(problems, ["line 15: type 'widget' is not one of architecture-pattern, reference-architecture, collaboration, use-case"])

    def test_bullets(self):
        rows, problems = B.parse(read(os.path.join(FIXTURES, "backlog-bullets.md")))
        self.assertEqual(problems, [])
        got = [(r["name"], r["type"], r["committed"], r["priority"], r["target_quarter"]) for r in rows]
        self.assertEqual(got, [
            ("Order intake", "architecture-pattern", True, "high", ""),
            ("Event-driven ingest", "", True, "", ""),
            ("Zero-trust ingress", "reference-architecture", True, "", "2027-Q2"),
            ("Data mesh", "", False, "low", ""),
            ("Release coordination", "collaboration", False, "", ""),
        ])

    def test_csv(self):
        rows, problems = B.parse(read(os.path.join(FIXTURES, "backlog.csv")), "csv")
        self.assertEqual(problems, [])
        self.assertEqual([(r["name"], r["type"], r["committed"]) for r in rows],
                         [("Order intake", "architecture-pattern", True), ("Zero-trust ingress", "reference-architecture", True),
                          ("Data mesh", "", False)])

    def test_brackets_that_are_not_a_type_stay_in_the_name(self):
        rows, _ = B.parse("- Payments (cards and wallets)\n")
        self.assertEqual((rows[0]["name"], rows[0]["type"]), ("Payments (cards and wallets)", ""))

    def test_table_without_name_column(self):
        rows, problems = B.parse("| Foo | Bar |\n|---|---|\n| a | b |\n")
        self.assertEqual(rows, [])
        self.assertIn("no name column", problems[0])


class Match(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = Bindings(REPO)
        cls.docs = D.discover(b.roots, b.root, b.archive_dir)
        rows, _ = B.parse(read(os.path.join(FIXTURES, "backlog.md")))
        cls.results = {r["row"]["line"]: r for r in B.match(rows, cls.docs)}

    def result(self, line):
        r = self.results[line]
        return r["result"], (r["doc"].id or r["doc"].title) if r["doc"] else None

    def test_exact_by_name(self):
        self.assertEqual(self.result(5), ("exact", "AP-001"))
        self.assertEqual(self.result(14), ("exact", "UC-001"))

    def test_exact_by_id(self):
        self.assertEqual(self.result(16), ("exact", "AP-003"))
        self.assertEqual(self.results[16]["how"], "id")

    def test_fuzzy(self):
        self.assertEqual(self.result(6), ("fuzzy", "AP-002"))
        self.assertGreaterEqual(self.results[6]["score"], B.MATCH)

    def test_candidate_matched(self):
        self.assertEqual(self.result(9), ("exact", "Event-sourced ledger"))
        self.assertTrue(self.results[9]["doc"].is_candidate)

    def test_ambiguous(self):
        self.assertEqual(self.results[7]["result"], "ambiguous")   # "Intake": only somewhat close to one
        r = self.results[8]                                        # two candidates near "Tenant isolation model"
        self.assertEqual(r["result"], "ambiguous")
        self.assertEqual({o.title for o in r["options"]}, {"Tenant isolation", "Tenant isolation at rest"})

    def test_new_and_duplicate(self):
        for line in (10, 11, 12):
            self.assertEqual(self.results[line]["result"], "new", line)
        self.assertEqual(self.results[13]["result"], "duplicate")

    def test_archived_pages_are_not_matched(self):
        docs = [d for d in self.docs if d.id != "AP-001"]
        for d in docs:
            if d.id == "AP-004":
                d.archived = True
        rows, _ = B.parse("- Old gateway; committed\n")
        self.assertEqual(B.match(rows, docs)[0]["result"], "new")

    def test_type_breaks_a_tie(self):
        a = D.Doc("a", "a", {}, "", "pattern", "architecture-pattern", "AP-001", "AP-001 Payments")
        r = D.Doc("r", "r", {}, "", "pattern", "reference-architecture", "RA-001", "RA-001 Payments")
        rows, _ = B.parse("- Payments (reference architecture)\n- Payments\n")
        res = B.match(rows, [a, r])
        self.assertEqual((res[0]["result"], res[0]["doc"].id), ("exact", "RA-001"))
        self.assertEqual(res[1]["result"], "ambiguous")


class Ids(unittest.TestCase):
    def test_next_id(self):
        self.assertEqual(B.next_id("AP", {"AP-001", "AP-007", "RA-009"}), "AP-008")
        self.assertEqual(B.next_id("CL", set()), "CL-001")
        self.assertEqual(B.next_id("AP", {"AP-0042"}), "AP-0043")

    def test_slug(self):
        self.assertEqual(B.slug("Zero-trust ingress: v2!"), "zero-trust-ingress-v2")

    def test_names_normalise(self):
        self.assertEqual(B.norm_name("AP-002 Event-driven ingestion pattern"), "event driven ingestion")


if __name__ == "__main__":
    unittest.main()
