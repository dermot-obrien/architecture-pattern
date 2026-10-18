# SPDX-FileCopyrightText: 2026 Dermot O'Brien
# SPDX-License-Identifier: Apache-2.0
"""The drafting flow, offline: a recorded research file stands in for the online search.

    python -m unittest discover -s skills/draft/tests
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
FIX = os.path.join(HERE, "fixtures")
DRAFT = os.path.join(SKILLS, "draft", "scripts", "draft.py")
PORTFOLIO = os.path.join(SKILLS, "portfolio", "scripts", "portfolio.py")
REPO_FIXTURE = os.path.join(SKILLS, "portfolio", "tests", "fixtures", "mixed-repo")
ENV = dict(os.environ, PORTFOLIO_TODAY="2026-10-18")
PLACEHOLDER = "patterns/AP-007-event-sourced-ledger/index.md"
RESEARCH = "patterns/AP-007-event-sourced-ledger/research.json"


def run(repo, script, *args):
    return subprocess.run([sys.executable, script, *args], cwd=repo, capture_output=True, text=True, env=ENV)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class Draft(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="draft-")
        self.addCleanup(shutil.rmtree, self.tmp)
        self.repo = os.path.join(self.tmp, "repo")
        shutil.copytree(REPO_FIXTURE, self.repo)
        for args in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@example.org", "-c", "user.name=T", "commit", "-qm", "f"]):
            subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True)
        backlog = os.path.join(self.tmp, "backlog.md")
        with open(backlog, "w") as f:
            f.write("| Name | Type | Committed | Ref |\n|---|---|---|---|\n| Event-sourced ledger | | yes | BL-5 |\n"
                    "| Zero-trust ingress | RA | yes | BL-6 |\n| Order cancellation | AP | yes | BL-7 |\n")
        r = run(self.repo, PORTFOLIO, "backlog", backlog)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.doc = os.path.join(self.repo, PLACEHOLDER)

    def plan(self):
        r = run(self.repo, DRAFT, "plan", PLACEHOLDER, "--recorded", os.path.join(FIX, "recorded-research.json"))
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(read(os.path.join(self.repo, RESEARCH)))

    def write(self, sections=os.path.join(FIX, "sections.md"), *extra):
        return run(self.repo, DRAFT, "write", PLACEHOLDER, "--research", RESEARCH, "--sections", sections,
                   "--set", "pattern_scope=problem", *extra)

    def test_plan_gathers_repository_and_recorded_sources(self):
        research = self.plan()
        self.assertEqual(research["id"], "AP-007")
        self.assertIn("Building Blocks", research["sections"])
        self.assertNotIn("Candidate notes", research["sections"])
        ids = [s["id"] for s in research["sources"]]
        self.assertEqual(ids, ["R1", "W1", "W2", "W3"])
        self.assertEqual(research["sources"][0]["title"], "Candidate notes")
        self.assertTrue(all(s["url"].startswith("https://example.org/") for s in research["sources"] if s["kind"] == "web"))

    def test_plan_finds_related_documents(self):
        r = run(self.repo, DRAFT, "plan", "patterns/AP-008-order-cancellation/index.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        research = json.loads(read(os.path.join(self.repo, "patterns/AP-008-order-cancellation/research.json")))
        paths = [s.get("path") for s in research["sources"]]
        self.assertIn("patterns/AP-001-order-intake/index.md", paths)
        self.assertIn("patterns/RA-001-order-intake-on-queues/index.md", paths)
        self.assertNotIn("patterns/AP-090-not-a-pattern/index.md", paths)  # unsigned: passages only, never a related document
        r = run(self.repo, DRAFT, "plan", "patterns/RA-002-zero-trust-ingress/index.md")
        research = json.loads(read(os.path.join(self.repo, "patterns/RA-002-zero-trust-ingress/research.json")))
        self.assertIn("Zero-trust ingress reference implementation", research["queries"])

    def test_repository_passages(self):
        with open(os.path.join(self.repo, "docs", "ledger-notes.md"), "w") as f:
            f.write("# Ledger notes\n\nThe event log is the ledger: each sourced balance is replayed from it, never overwritten in place.\n")
        research = self.plan()
        self.assertIn("docs/ledger-notes.md", [s.get("path") for s in research["sources"]])

    def test_add_source_numbers_and_deduplicates(self):
        self.plan()
        r = run(self.repo, DRAFT, "add-source", RESEARCH, "--url", "https://example.org/a", "--title", "A", "--excerpt", "x")
        self.assertEqual(r.stdout.strip(), "W4")
        r = run(self.repo, DRAFT, "add-source", RESEARCH, "--url", "https://example.org/a", "--title", "A", "--excerpt", "x")
        self.assertEqual(r.stdout.strip(), "W4")
        r = run(self.repo, DRAFT, "add-source", RESEARCH, "--url", "file:///etc/x", "--title", "A", "--excerpt", "x")
        self.assertEqual(r.returncode, 2)

    def test_write_and_check(self):
        self.plan()
        r = self.write()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("warn: ## Scenarios cites no source", r.stdout)
        text = read(self.doc)
        # marked as an AI draft, for review
        for needle in ("status: draft", "  state: draft", "  origin: ai-generated", "  review_state: ai-raw",
                       "  task_ref: BL-5", "banner:\n  tone: warning", "> AI-generated draft"):
            self.assertIn(needle, text)
        # cited, with a Sources section and link definitions
        self.assertIn("derives the current state by replaying them [W1]", text)
        self.assertIn("- [W2] Projections over an append-only ledger, Example Engineering Notes, https://example.org/articles/ledger-projections, accessed 2026-10-18", text)
        self.assertIn("[W3]: https://example.org/articles/snapshots", text)
        self.assertIn('  - { type: doc, url: "https://example.org/articles/event-sourcing" }', text)
        # in the proper template: the drafted content replaced the guidance, the rest kept
        self.assertIn("| 03 | Projector | Derives balances from the ledger [W2] |", text)
        self.assertNotIn("COMP-NNN Official Name | 07 Local role name | What happens", text)
        self.assertIn("## Controls and Guardrails", text)
        # deck tags stay with the heading they mark
        self.assertRegex(text, r'<!-- deck:slide label="Interfaces" -->\s*\n## Interfaces')
        self.assertRegex(text, r'<!-- deck:slide label="Component View" -->\s*\n## Diagram')
        self.assertIn('<!-- deck:html src="./scenarios.html"', text)
        # the placeholder note is gone, the candidate's notes kept
        self.assertNotIn("portfolio: a placeholder", text)
        self.assertIn("## Candidate notes", text)
        r = run(self.repo, DRAFT, "check", PLACEHOLDER, "--research", RESEARCH)
        self.assertEqual(r.returncode, 0, r.stdout)
        # the portfolio sees a draft in form, and its check passes
        inv = json.loads(run(self.repo, PORTFOLIO, "inventory", "--format", "json", "--out", "-").stdout)
        self.assertEqual(inv["counts"]["draft"], 1)
        self.assertNotIn("AP-007", run(self.repo, PORTFOLIO, "tag", "--dry-run").stdout)
        self.assertEqual(run(self.repo, PORTFOLIO, "check").returncode, 0)

    def test_rewrite_is_idempotent(self):
        self.plan()
        self.write()
        first = read(self.doc)
        self.write()
        self.assertEqual(read(self.doc), first)

    def test_dry_run_writes_nothing(self):
        self.plan()
        before = read(self.doc)
        r = self.write(os.path.join(FIX, "sections.md"), "--dry-run")
        self.assertIn("## Sources", r.stdout)
        self.assertEqual(read(self.doc), before)

    def test_refuses_unresolved_citation_and_unknown_heading(self):
        self.plan()
        bad = os.path.join(self.tmp, "bad.md")
        with open(bad, "w") as f:
            f.write("## Context\n\nA claim [W9].\n\n## Market Size\n\nNot a template section [W1].\n")
        before = read(self.doc)
        r = self.write(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("cites [W9]", r.stdout)
        self.assertIn("## Market Size is not a section of the template", r.stdout)
        self.assertEqual(read(self.doc), before)

    def test_requires_the_fields_a_draft_needs(self):
        self.plan()
        before = read(self.doc)
        r = run(self.repo, DRAFT, "write", PLACEHOLDER, "--research", RESEARCH, "--sections", os.path.join(FIX, "sections.md"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("needs pattern_scope: pass --set pattern_scope=...", r.stdout)
        r = run(self.repo, DRAFT, "write", PLACEHOLDER, "--research", RESEARCH, "--sections", os.path.join(FIX, "sections.md"),
                "--set", "pattern_scope=galaxy")
        self.assertIn("pattern_scope galaxy is not one of", r.stdout)
        self.assertEqual(read(self.doc), before)
        self.assertEqual(self.write().returncode, 0)
        self.assertIn("\npattern_scope: problem\n", read(self.doc))

    def test_refuses_uncited_draft(self):
        self.plan()
        bad = os.path.join(self.tmp, "bad.md")
        with open(bad, "w") as f:
            f.write("## Context\n\nNo citations at all.\n")
        r = self.write(bad)
        self.assertEqual(r.returncode, 1)
        self.assertIn("cites no source", r.stdout)

    def test_refuses_a_reviewed_document(self):
        r = run(self.repo, DRAFT, "plan", "patterns/AP-001-order-intake/index.md")
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a placeholder", r.stderr)

    def test_check_catches_a_stripped_marking(self):
        self.plan()
        self.write()
        text = read(self.doc)
        with open(self.doc, "w") as f:
            f.write(re.sub(r"origin: ai-generated", "origin: human-authored", text).replace("[W3]: https://example.org/articles/snapshots\n", ""))
        r = run(self.repo, DRAFT, "check", PLACEHOLDER)
        self.assertEqual(r.returncode, 1)
        self.assertIn("provenance.origin is not ai-generated", r.stdout)
        self.assertIn("[W3] is cited but has no link definition", r.stdout)


if __name__ == "__main__":
    unittest.main()
