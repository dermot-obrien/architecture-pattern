# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""Discovery by signature, the form check, summaries and front matter edits.

    python -m unittest discover -s skills/portfolio/tests
"""
from __future__ import annotations

import os
import shutil
import unittest

import helpers  # noqa: F401  (puts the library on the path)
from helpers import FIXTURES, copy_fixture
from portfolio_lib import docs as D
from portfolio_lib.bindings import Bindings

REPO = os.path.join(FIXTURES, "mixed-repo")


class Signature(unittest.TestCase):
    def test_each_kind(self):
        self.assertEqual(D.signature({"kind": "pattern", "pattern_type": "architecture-pattern"}),
                         ("pattern", "architecture-pattern", False))
        self.assertEqual(D.signature({"kind": "pattern", "pattern_type": "collaboration"}),
                         ("pattern", "collaboration", False))
        self.assertEqual(D.signature({"kind": "use-case"}), ("use-case", "use-case", False))
        self.assertEqual(D.signature({"kind": "candidate"}), ("candidate", "candidate", False))

    def test_legacy(self):
        self.assertEqual(D.signature({"pattern_type": "reference-architecture"}),
                         ("pattern", "reference-architecture", True))
        self.assertEqual(D.signature({"document_type": "use-case"}), ("use-case", "use-case", True))
        self.assertEqual(D.signature({"document_type": "pattern"}), ("pattern", "", True))

    def test_legacy_document_type_takes_the_series(self):
        import tempfile
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        p = os.path.join(tmp, "index.md")
        with open(p, "w") as f:
            f.write("---\ndocument_type: pattern\n---\n# RA-004 Something on queues\n")
        d = D.load(p, tmp)
        self.assertEqual((d.kind, d.type, d.id, d.legacy), ("pattern", "reference-architecture", "RA-004", True))

    def test_not_signed(self):
        for fm in ({}, {"title": "Pattern", "tags": ["pattern"]}, {"pattern": "true"},
                   {"kind": "abb", "pattern_type": "architecture-pattern"}, {"pattern_type": "pattern"}):
            self.assertIsNone(D.signature(fm), fm)


class Discovery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = Bindings(REPO)
        cls.docs = D.discover(b.roots, b.root, b.archive_dir)
        cls.by = {d.rel: d for d in cls.docs}

    def test_every_type_found(self):
        types = {d.type for d in self.docs}
        self.assertEqual(types, {"architecture-pattern", "reference-architecture", "collaboration", "use-case", "candidate"})
        self.assertEqual(len(self.docs), 12)

    def test_name_collisions_not_found(self):
        for rel in ("patterns/AP-090-not-a-pattern/index.md", "docs/pattern.md", "docs/architecture-pattern/index.md",
                    "notes/ABB-001-identity/index.md", "reference-architecture.md", "docs/README.md"):
            self.assertNotIn(rel, self.by)

    def test_id_from_front_matter_not_folder(self):
        d = self.by["patterns/AP-001-order-intake/index.md"]
        self.assertEqual((d.id, d.title, d.type), ("AP-001", "AP-001 Order intake", "architecture-pattern"))

    def test_legacy_id_from_heading(self):
        d = self.by["patterns/legacy/AP-006-file-transfer/index.md"]
        self.assertTrue(d.legacy)
        self.assertEqual(d.id, "AP-006")
        self.assertEqual(d.title, "AP-006 Managed file transfer")

    def test_summary(self):
        self.assertEqual(self.by["patterns/AP-002-event-driven-ingestion/index.md"].summary,
                         "Ingests events from producers through a durable log, so consumers can replay them.")
        self.assertEqual(self.by["patterns/AP-001-order-intake/index.md"].summary,
                         "Takes an order from any channel and records it exactly once.")

    def test_portfolio_block(self):
        d = self.by["patterns/AP-004-old-gateway/index.md"]
        self.assertEqual(d.state, "archive")
        self.assertEqual(self.by["patterns/AP-001-order-intake/index.md"].portfolio["target_quarter"], "2026-Q4")

    def test_unparseable_signed_front_matter_reported(self):
        tmp, repo = copy_fixture(with_git=False)
        self.addCleanup(shutil.rmtree, tmp)
        p = os.path.join(repo, "patterns", "broken.md")
        with open(p, "w") as f:
            f.write("---\nkind: pattern\ntitle: [unclosed\n---\n# Broken\n")
        d = D.load(p, repo)
        self.assertTrue(d.problems)


class Form(unittest.TestCase):
    def doc(self, body, dtype="architecture-pattern"):
        return D.Doc("x.md", "x.md", {}, body, "pattern", dtype)

    def test_in_form(self):
        b = Bindings(REPO)
        for d in D.discover(b.roots, b.root):
            if d.rel.startswith("patterns/AP-005") or d.is_candidate:
                continue
            self.assertEqual(D.form_problems(d), [], d.rel)

    def test_missing_parts(self):
        p = D.form_problems(self.doc("## Diagram\n\n![x](x.png)\n\n## Notes\n\ntext\n"))
        self.assertEqual(p, ["no ## Building Blocks section", "no ## Interfaces section", "no ## Scenarios section"])

    def test_section_without_table(self):
        body = "## Diagram\n\n## 3. Building Blocks\n\nTo do.\n\n## Interfaces\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n## Scenarios\n\n### S1 x\n"
        self.assertEqual(D.form_problems(self.doc(body)), ["## Building Blocks has no table"])

    def test_table_in_comment_does_not_count(self):
        body = "## Diagram\n\n## Building Blocks\n\n<!--\n| a | b |\n|---|---|\n| 1 | 2 |\n-->\n\n## Interfaces\n\n| a |\n|---|\n| 1 |\n\n## Scenarios\n\n### S1\n"
        self.assertEqual(D.form_problems(self.doc(body)), ["## Building Blocks has no table"])

    def test_bound_headings(self):
        body = "## Picture\n\n## Boxes\n\n| a |\n|---|\n| 1 |\n\n## Lines\n\n| a |\n|---|\n| 1 |\n\n## Stories\n\n### S1\n"
        form = {"architecture-pattern": {"diagram": ["Picture"], "boxes": ["Boxes"], "links": ["Lines"], "scenarios": ["Stories"]}}
        self.assertEqual(D.form_problems(self.doc(body), form), [])


class Edit(unittest.TestCase):
    TEXT = "---\nkind: pattern\nid: AP-001  # keep this comment\ntags:\n- a\n- b\nportfolio:\n  priority: high\n  committed: true\nowner: Team\n---\n\n# Body\n"

    def test_set_state_keeps_other_lines(self):
        out = D.edit(self.TEXT, portfolio={"state": "needs-conversion", "reason": "no tables: yet"})
        self.assertIn("id: AP-001  # keep this comment\n", out)
        self.assertIn("tags:\n- a\n- b\n", out)
        self.assertIn('portfolio:\n  state: needs-conversion\n  priority: high\n  committed: true\n  reason: "no tables: yet"\n', out)
        self.assertTrue(out.endswith("---\n\n# Body\n"))
        fm, _ = D.parse(D.split(out)[0])
        self.assertEqual(fm["owner"], "Team")

    def test_remove_and_drop_empty_block(self):
        out = D.edit(self.TEXT, portfolio={"priority": None, "committed": None})
        self.assertNotIn("portfolio", out)
        self.assertIn("owner: Team", out)

    def test_add_block_and_top_key(self):
        out = D.edit("---\nkind: pattern\n---\nbody\n", top={"unlisted": True}, portfolio={"target_quarter": "2027-Q1"})
        self.assertEqual(out, '---\nkind: pattern\nunlisted: true\nportfolio:\n  target_quarter: "2027-Q1"\n---\nbody\n')

    def test_inline_portfolio_rewritten(self):
        out = D.edit("---\nportfolio: { priority: low }\nkind: pattern\n---\n", portfolio={"state": "draft"})
        self.assertIn("portfolio:\n  state: draft\n  priority: low\nkind: pattern\n", out)

    def test_round_trip_parses(self):
        out = D.edit(self.TEXT, portfolio={"reason": 'says "no" # really', "since": "2026-10-18"})
        fm, err = D.parse(D.split(out)[0])
        self.assertIsNone(err)
        self.assertEqual(fm["portfolio"]["reason"], 'says "no" # really')


if __name__ == "__main__":
    unittest.main()
