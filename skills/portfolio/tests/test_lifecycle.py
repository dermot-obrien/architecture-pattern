# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Tagging rules, the portfolio check, and the links an archive would break."""
from __future__ import annotations

import os
import shutil
import unittest

import helpers  # noqa: F401
from helpers import FIXTURES, copy_fixture, write
from portfolio_lib import docs as D
from portfolio_lib import lifecycle as L
from portfolio_lib.bindings import Bindings

REPO = os.path.join(FIXTURES, "mixed-repo")


def doc(fm, body="", dtype="architecture-pattern", kind="pattern"):
    return D.Doc("x.md", "x.md", fm, body, kind, dtype, fm.get("id", "AP-001"), "x")


class Tags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = Bindings(REPO)
        cls.docs = D.discover(b.roots, b.root, b.archive_dir)

    def test_fixture_plan(self):
        plan = {d.id: ch["state"] for d, ch, _ in L.plan_tags(self.docs)}
        self.assertEqual(plan, {"AP-003": "proposed-deprecation", "AP-005": "needs-conversion"})

    def test_deprecation_reasons(self):
        self.assertEqual(L.deprecation_reason(doc({"status": "Superseded"})), "status is superseded")
        self.assertEqual(L.deprecation_reason(doc({"superseded_by": ["AP-002"]})), "superseded by AP-002")
        self.assertEqual(L.deprecation_reason(doc({"valid_until": "2026-01-01"})), "valid_until 2026-01-01 has passed")
        self.assertEqual(L.deprecation_reason(doc({"valid_until": "2099-01-01"})), "")
        self.assertIn("not modified for", L.deprecation_reason(doc({"last_modified": "2024-01-01"}), 365))

    def test_a_person_set_state_is_not_overridden(self):
        for state in ("archive", "draft", "placeholder", "proposed-deprecation"):
            d = doc({"status": "deprecated", "portfolio": {"state": state}})
            self.assertEqual(L.plan_tags([d]), [], state)

    def test_deprecation_wins_over_conversion(self):
        d = doc({"status": "retired", "portfolio": {"state": "needs-conversion"}})
        self.assertEqual(L.plan_tags([d])[0][1]["state"], "proposed-deprecation")

    def test_conversion_cleared_when_in_form(self):
        in_form = next(d for d in self.docs if d.id == "AP-001")
        d = doc({"portfolio": {"state": "needs-conversion"}}, in_form.body)
        d, ch, why = L.plan_tags([d])[0]
        self.assertEqual(ch["state"], None)
        self.assertIn("now in form", why)

    def test_candidates_and_archive_untouched(self):
        cand = doc({}, "", "candidate", "candidate")
        arch = doc({"status": "deprecated"})
        arch.archived = True
        self.assertEqual(L.plan_tags([cand, arch]), [])


class Check(unittest.TestCase):
    def test_fixture_clean_but_legacy(self):
        b = Bindings(REPO)
        errors, warnings = L.check(D.discover(b.roots, b.root, b.archive_dir), b)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("legacy signature", warnings[0])

    def test_errors(self):
        b = Bindings(REPO)
        bad = [
            doc({"id": "RA-005"}),                                                   # AP type, RA id
            doc({"id": "AP-001", "portfolio": {"state": "maybe", "priority": "urgent",
                                               "target_quarter": "Q1", "committed": "perhaps"}}),
            doc({"id": "AP-001"}),                                                   # duplicate of the above
            D.Doc("c.md", "c.md", {"portfolio": {"state": "draft"}, "candidate_type": "widget"}, "", "candidate", "candidate"),
            D.Doc("p.md", "p.md", {}, "", "pattern", "", "", "untyped"),
        ]
        errors, _ = L.check(bad, b)
        text = "\n".join(errors)
        for needle in ("not in the architecture-pattern series AP-NNN", "portfolio.state maybe", "portfolio.priority urgent",
                       "target_quarter Q1", "committed is true or false", "is also the id of", "candidate carries no portfolio.state",
                       "candidate_type widget", "kind pattern with no pattern_type"):
            self.assertIn(needle, text)

    def test_bound_series(self):
        tmp, repo = copy_fixture(with_git=False)
        self.addCleanup(shutil.rmtree, tmp)
        p = os.path.join(repo, ".agents", "skill-bindings.toml")
        with open(p) as f:
            text = f.read()
        write(p, text.replace('idSeries = "CL"', 'idSeries = "COL"'))
        b = Bindings(repo)
        errors, _ = L.check(D.discover(b.roots, b.root, b.archive_dir), b)
        self.assertEqual(errors, ["patterns/CL-001-incident-response/index.md: id CL-001 is not in the collaboration series COL-NNN"])


class Links(unittest.TestCase):
    def test_affected_links(self):
        b = Bindings(REPO)
        docs = D.discover(b.roots, b.root, b.archive_dir)
        moves, problems = L.plan_archive(docs, b)
        self.assertEqual(problems, [])
        self.assertEqual([(os.path.relpath(m["src"], REPO), m["folder"]) for m in moves],
                         [("patterns/AP-004-old-gateway", True)])
        links = {(os.path.relpath(lk["file"], REPO), lk["target"], lk["new_target"], lk["inbound"])
                 for lk in L.links_affected(moves, b)}
        self.assertEqual(links, {
            ("docs/README.md", "../patterns/AP-004-old-gateway/index.md", "../archive/patterns/AP-004-old-gateway/index.md", True),
            ("patterns/AP-002-event-driven-ingestion/index.md", "../AP-004-old-gateway/index.md",
             "../../archive/patterns/AP-004-old-gateway/index.md", True),
            ("patterns/AP-002-event-driven-ingestion/index.md", "../AP-004-old-gateway/components.svg",
             "../../archive/patterns/AP-004-old-gateway/components.svg", True),
            ("patterns/AP-004-old-gateway/index.md", "../AP-001-order-intake/index.md",
             "../../../patterns/AP-001-order-intake/index.md", False),
        })

    def test_fenced_and_external_links_ignored(self):
        text = "[a](https://example.org/x.md) [b](#here)\n```\n[c](../x.md)\n```\n[d]: ../y.md\n"
        self.assertEqual([t for _n, _s, _e, t in L.iter_links(text)], ["https://example.org/x.md", "#here", "../y.md"])


if __name__ == "__main__":
    unittest.main()
