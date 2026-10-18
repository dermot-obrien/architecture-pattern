# SPDX-License-Identifier: Apache-2.0
"""Convert the examples, then check and publish the results with the pattern skill.

Every test here drives the model skill and the pattern skill's publish.py, as an agent
would, and is skipped when model is not installed.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

from conftest import (EXAMPLES, SKILL, git, needs_model, publish, run_convert, run_json,
                      source)

pytestmark = needs_model

EXPECTED = {
    "order-intake": "architecture-pattern",
    "document-search": "architecture-pattern",
    "cache-aside": "architecture-pattern",
    "circuit-breaker": "architecture-pattern",
    "outbox": "architecture-pattern",
    "edge-gateway": "reference-architecture",
    "event-pipeline-ingest": "reference-architecture",
    "event-pipeline-serve": "reference-architecture",
    "claims-portal": "use-case",
    "appointment-booking": "use-case",
    "supplier-onboarding": "collaboration",
}
PICTURES = {"incident-handover", "release-approval"}


def manifest(run):
    with open(os.path.join(run, "manifest.json"), encoding="utf-8") as fh:
        return json.load(fh)


def published_ok(folder):
    data, r = publish(folder)
    results = data["results"]
    assert results, r.stderr
    bad = [x for x in results if x["status"] != "ok"]
    assert not bad, bad
    return results


@pytest.fixture(scope="module")
def whole_set(tmp_path_factory):
    """Every example, converted in one run from a folder outside git."""
    root = tmp_path_factory.mktemp("set")
    shutil.copytree(os.path.join(EXAMPLES, "sources"), root / "material")
    data, r = run_json("run", root / "material", "--out", root / "out", "--work", root / "work",
                       cwd=root)
    return root, data, r


class TestWholeSet:
    def test_every_unit_is_found(self, whole_set):
        _root, data, _r = whole_set
        assert {u["slug"] for u in data["units"]} == set(EXPECTED) | PICTURES

    def test_each_type_as_expected(self, whole_set):
        _root, data, _r = whole_set
        got = {u["slug"]: u["type"] for u in data["units"] if u["slug"] not in PICTURES}
        assert got == EXPECTED

    def test_drafted_valid_and_agreeing(self, whole_set):
        _root, data, _r = whole_set
        for u in data["units"]:
            if u["slug"] in PICTURES:
                assert u["status"] == "needs-agent"
                continue
            assert (u["status"], u["valid"], u["agrees"]) == ("drafted", "ok", True), u

    def test_pictures_make_the_run_exit_one(self, whole_set):
        assert whole_set[2].returncode == 1

    def test_publish_renders_and_animates(self, whole_set):
        root, _data, _r = whole_set
        results = published_ok(root / "out")
        assert len(results) == len(EXPECTED)
        animated = [x for x in results if any("animated" in n for n in x["notes"])]
        assert len(animated) >= 6

    def test_report_and_manifest(self, whole_set):
        root, data, _r = whole_set
        run = data["run"]
        with open(os.path.join(run, "report.md"), encoding="utf-8") as fh:
            report = fh.read()
        assert "Read the image" in report and "Comparison with the source: agrees" in report
        m = manifest(run)
        assert all(e.get("gathered") and len(e.get("sha256", "")) == 64 for e in m["sources"])
        assert all(not e.get("archived") for e in m["sources"])
        for name in ("source.json", "unit.json"):
            assert os.path.isfile(os.path.join(run, "units", "order-intake", name))

    def test_originals_left_in_place(self, whole_set):
        root, _data, _r = whole_set
        assert (root / "material" / "order-intake" / "order-intake.drawio").exists()

    def test_layout_kept_from_a_drawio(self, whole_set):
        root, _data, _r = whole_set
        doc = next((root / "out").glob("AP-*-order-intake"))
        text = (doc / "components.drawio").read_text(encoding="utf-8")
        assert 'Order domain' in text and 'local_id="01"' in text
        assert (doc / "components.svg.render.json").exists()

    def test_no_document_is_overwritten(self, whole_set):
        root, data, _r = whole_set
        again, _ = run_json("draft", data["run"], "--unit", "order-intake", cwd=root)
        u = next(x for x in again["units"] if x["slug"] == "order-intake")
        assert u["status"] == "exists"


@pytest.mark.parametrize("src", [
    "order-intake/order-intake.drawio",
    "edge-gateway/edge-gateway.drawio.svg",
    "claims-portal/claims-portal.svg",
    "appointment-booking/appointment-booking.drawio.png",
])
@pytest.mark.parametrize("type_name", ["AP", "RA", "UC", "CO"])
def test_every_format_to_every_type(tmp_path, src, type_name):
    data, r = run_json("run", source(*src.split("/")), "--type", type_name, "--out", tmp_path / "out",
                       "--work", tmp_path / "work", "--no-archive", cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    u = data["units"][0]
    assert (u["status"], u["valid"], u["agrees"]) == ("drafted", "ok", True)
    published_ok(tmp_path / "out")


@pytest.mark.parametrize("name,expected", [("incident-handover", "collaboration"),
                                           ("release-approval", "collaboration")])
def test_a_picture_read_by_the_agent(tmp_path, copy_sources, name, expected):
    material = copy_sources(name)
    data, r = run_json("run", material, "--out", tmp_path / "out", "--work", tmp_path / "work",
                       cwd=tmp_path)
    assert r.returncode == 1 and data["units"][0]["status"] == "needs-agent"
    unit = os.path.join(data["run"], "units", name, "unit.json")
    shutil.copy(os.path.join(EXAMPLES, "agent", f"{name}.unit.json"), unit)
    data, r = run_json("draft", data["run"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    u = data["units"][0]
    assert (u["status"], u["type"], u["valid"]) == ("drafted", expected, "ok")
    assert u["agrees"] is None                      # an image has no structure to compare
    results = published_ok(tmp_path / "out")
    assert any("animated" in n for n in results[0]["notes"])
    doc = next((tmp_path / "out").glob("CO-*")) / "index.md"
    text = doc.read_text(encoding="utf-8")
    assert "Drafted from an image" in text
    assert "incident-handover.png" in text or "release-approval.png" in text


def test_dry_run_writes_and_moves_nothing(git_repo, copy_sources):
    copy_sources("order-intake", into=git_repo)
    git("add", "-A", cwd=git_repo)
    git("commit", "-qm", "material", cwd=git_repo)
    before = sorted(str(p) for p in git_repo.rglob("*") if ".git" not in p.parts)
    r = run_convert("run", "order-intake", "--dry-run", cwd=git_repo)
    assert r.returncode == 0
    assert "git mv to archive" in r.stdout and "would write patterns/AP-001-order-intake/index.md" in r.stdout
    after = sorted(str(p) for p in git_repo.rglob("*") if ".git" not in p.parts)
    assert before == after


def test_a_repository_archives_its_originals(git_repo, copy_sources):
    copy_sources("platform", into=git_repo / "docs")
    (git_repo / "docs" / "platform" / "draft-notes.md").write_text("# Not yet\n", encoding="utf-8")
    git("add", "docs/platform/cache-aside.drawio", "docs/platform/cache-aside.md",
        "docs/platform/outbox.drawio", "docs/platform/outbox.md",
        "docs/platform/circuit-breaker.svg", cwd=git_repo)
    git("commit", "-qm", "material", cwd=git_repo)
    data, r = run_json("run", "docs/platform", cwd=git_repo)
    assert r.returncode == 0, r.stdout + r.stderr
    assert {u["slug"] for u in data["units"]} == {"cache-aside", "outbox", "circuit-breaker"}
    archived = git_repo / "archive" / "docs" / "platform"
    assert sorted(p.name for p in archived.iterdir()) == [
        "cache-aside.drawio", "cache-aside.md", "circuit-breaker.svg", "outbox.drawio", "outbox.md"]
    assert (git_repo / "docs" / "platform" / "draft-notes.md").exists()
    status = git("status", "--short", cwd=git_repo).stdout
    assert "R  docs/platform/outbox.drawio -> archive/docs/platform/outbox.drawio" in status
    doc = next((git_repo / "patterns").glob("AP-*-cache-aside")) / "index.md"
    assert '"../../archive/docs/platform/cache-aside.drawio"' in doc.read_text(encoding="utf-8")
    published_ok(git_repo / "patterns")


BINDINGS = '''bindingsVersion = "1.0"

[model]
node_id_attrs = ["abb_id", "sbb_id"]
edge_id_attr  = "iface_id"
group_attr    = "group"
local_pattern = '[0-9]{2}'
local_attr    = "local_id"

[[markdown.tables]]
section    = "Building Blocks"
entity     = "node"
id_pattern = "(ABB|SBB)-[0-9]{3}"
columns    = { id = "Building Block", label = "Building Block", group = "Source" }

[[markdown.tables]]
section    = "Participants"
entity     = "node"
id_pattern = "(ABB|SBB)-[0-9]{3}"
columns    = { id = "Participant", label = "Participant", group = "Kind" }

[[markdown.tables]]
section    = "Interfaces"
entity     = "edge"
id_pattern = "IF-[0-9]{2,3}"
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }

[[markdown.tables]]
section    = "Interactions"
entity     = "edge"
id_pattern = "IF-[0-9]{2,3}"
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }

[markdown.scenarios]
section         = "Scenarios"
heading_pattern = '^(S[0-9]+)\\b[\\s:.-]*(.*)$'
columns         = { step = "Step", actor = "Actor", action = "Action", edge = "Interface", target = "Target" }

[suite.pattern]
outputDir = "../patterns"
register  = "../register.csv"

[suite.pattern.types.architecture-pattern]
idSeries = "AP"
physical = "none"

[suite.pattern.types.reference-architecture]
idSeries = "RA"
physical = "most"

[suite.pattern.types.collaboration]
label    = "Collaboration"
idSeries = "CO"

[suite.use-case]
outputDir = "../use-cases"
register  = "../register.csv"

[suite.convert]
workDir    = "../work/conversions"
archiveDir = "../work/archive"
'''


def test_a_bound_workspace(git_repo, copy_sources):
    (git_repo / ".agents").mkdir()
    (git_repo / ".agents" / "skill-bindings.toml").write_text(BINDINGS, encoding="utf-8")
    (git_repo / "register.csv").write_text("id,type,name,status,path,url,summary\n"
                                           "AP-007,architecture-pattern,Older,Approved,,,\n",
                                           encoding="utf-8")
    copy_sources("order-intake", "supplier-onboarding", "edge-gateway", "claims-portal", into=git_repo)
    git("add", "-A", cwd=git_repo)
    git("commit", "-qm", "material", cwd=git_repo)
    data, r = run_json("run", "order-intake", "supplier-onboarding", "edge-gateway",
                       "claims-portal", cwd=git_repo)
    assert r.returncode == 0, r.stdout + r.stderr
    docs = {u["slug"]: os.path.relpath(u["document"], git_repo) for u in data["units"]}
    assert docs == {
        "order-intake": os.path.join("patterns", "AP-008-order-intake", "index.md"),
        "supplier-onboarding": os.path.join("patterns", "CO-001-supplier-onboarding", "index.md"),
        "edge-gateway": os.path.join("patterns", "RA-001-edge-gateway", "index.md"),
        "claims-portal": os.path.join("use-cases", "UC-001-submit-a-claim", "index.md"),
    }
    # The workspace's binding reads the tables, so no model.toml is written.
    assert not list(git_repo.glob("patterns/*/model.toml"))
    register = (git_repo / "register.csv").read_text(encoding="utf-8")
    assert "CO-001,collaboration,Supplier onboarding,Draft,patterns/CO-001-supplier-onboarding" in register
    assert data["run"].startswith(str(git_repo / "work" / "conversions"))
    assert (git_repo / "work" / "archive" / "order-intake" / "order-intake.drawio").exists()
    pattern_check = os.path.join(SKILL, "..", "pattern", "scripts", "check.py")
    r = subprocess.run([sys.executable, pattern_check], cwd=git_repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    convert_check = os.path.join(SKILL, "scripts", "check.py")
    r = subprocess.run([sys.executable, convert_check], cwd=git_repo, capture_output=True, text=True)
    assert r.returncode == 0 and "work/conversions" in r.stdout, r.stdout + r.stderr
    published_ok(git_repo / "patterns")
    published_ok(git_repo / "use-cases")


def test_verify_reports_a_difference(tmp_path, copy_sources):
    material = copy_sources("order-intake")
    data, _ = run_json("run", material, "--out", tmp_path / "out", "--work", tmp_path / "work",
                       "--no-archive", cwd=tmp_path)
    run = data["run"]
    doc = data["units"][0]["document"]
    text = open(doc, encoding="utf-8").read()
    # Drop the Notification Service's row and its interface: the source still has both.
    text = "\n".join(ln for ln in text.splitlines()
                     if "07 Notification Service" not in ln or ln.startswith("| 6 |"))
    text = "\n".join(ln for ln in text.splitlines() if not ln.startswith("| 6 |"))
    open(doc, "w", encoding="utf-8").write(text + "\n")
    r = run_convert("verify", doc, "--source", os.path.join(run, "units", "order-intake", "source.json"),
                    "--json")
    out = json.loads(r.stdout)
    assert r.returncode == 1
    assert out["comparison"]["agrees"] is False
    assert out["comparison"]["boxes"]["missing"] == ["Notification Service"]
    assert out["comparison"]["links"]["missing"] == ["event broker to notification service (deliver event)"]


def test_read_prints_the_unit(tmp_path):
    r = run_convert("read", source("platform", "outbox.drawio"), "--text", source("platform", "outbox.md"))
    units = json.loads(r.stdout)
    assert units[0]["name"] == "Transactional outbox"
    assert units[0]["classification"]["type"] == "architecture-pattern"
    assert "drawio" not in units[0]
