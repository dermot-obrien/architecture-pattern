# SPDX-License-Identifier: Apache-2.0
"""Drafting a unit into the template of its type."""
from __future__ import annotations

import os
import re
import tomllib

import pytest

from conftest import SKILL
from convertlib import draft
from convertlib.unit import add_box, add_link, new_unit

TEMPLATES = {
    "architecture-pattern": os.path.join(SKILL, "..", "pattern", "assets", "templates", "architecture-pattern.md"),
    "reference-architecture": os.path.join(SKILL, "..", "pattern", "assets", "templates", "reference-architecture.md"),
    "collaboration": os.path.join(SKILL, "..", "pattern", "assets", "templates", "collaboration.md"),
    "use-case": os.path.join(SKILL, "..", "use-case", "assets", "template.md"),
}


def sample(scenario=True):
    u = new_unit(name="Order intake")
    u["summary"] = "Orders are taken once and priced once."
    a = add_box(u, "Order API", description="Takes orders", container="Order domain")
    b = add_box(u, "Order Store", id="ABB-012", kind="store")
    c = add_box(u, "Payment Gateway", uncertain="the label was faint")
    l1 = add_link(u, a["key"], b["key"], label="persist | order")
    add_link(u, a["key"], c["key"], label="")
    if scenario:
        u["scenarios"].append({"key": "", "name": "Take an order", "from": "text: numbered list",
                               "steps": [{"step": 1, "actor": a["key"], "target": b["key"],
                                          "action": "stores it", "link": l1["key"], "uncertain": ""}]})
    u["sections"].append({"heading": "Constraints", "text": "Never store card numbers."})
    u["notes"].append("a key on the diagram was left out")
    return u


def template(t):
    with open(TEMPLATES[t], encoding="utf-8") as fh:
        return fh.read()


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


class TestIds:
    def test_local_ids_fill_around_kept_ones(self):
        u = new_unit()
        add_box(u, "A", id="02")
        add_box(u, "B")
        add_box(u, "C", id="ABB-001")
        add_box(u, "D")
        draft.assign_ids(u)
        assert [b["id"] for b in u["boxes"]] == ["02", "01", "ABB-001", "03"]

    def test_a_series_the_binding_does_not_read_becomes_local(self):
        u = new_unit()
        add_box(u, "A", id="CAP-001")
        draft.assign_ids(u, {"ABB", "SBB"})
        assert u["boxes"][0]["id"] == "01" and u["boxes"][0]["note_id"] == "CAP-001"

    def test_duplicate_identifier_becomes_local(self):
        u = new_unit()
        add_box(u, "A", id="ABB-001")
        add_box(u, "B", id="ABB-001")
        draft.assign_ids(u)
        assert [b["id"] for b in u["boxes"]] == ["ABB-001", "01"]

    def test_links_and_scenarios(self):
        u = sample()
        u["links"][1]["id"] = "IF-01"
        draft.assign_ids(u)
        assert [lk["id"] for lk in u["links"]] == ["IF-02", "IF-01"]
        assert u["scenarios"][0]["key"] == "S1"


@pytest.mark.parametrize("type_name", list(TEMPLATES))
def test_every_template_takes_the_tables(type_name):
    u = draft.assign_ids(sample())
    out = draft.render(template(type_name), u, "XX-001", type_name, ["../src/a.drawio"], "2026-01-02")
    profile = draft.PROFILES[type_name]
    assert re.search(r"^# XX-001 Order intake$", out, re.M)
    nodes = section(out, profile["nodes"])
    assert "| 01 Order API | Takes orders |" in nodes
    assert "| ABB-012 Order Store | TBD |" in nodes
    edges = section(out, profile["edges"])
    assert "| IF-01 | 01 Order API | ABB-012 Order Store | persist \\| order |" in edges
    assert "| IF-02 | 01 Order API | 02 Payment Gateway | TBD |" in edges
    scen = section(out, "Scenarios")
    assert "### S1 Take an order" in scen
    assert "| 1 | 01 Order API | ABB-012 Order Store | stores it | IF-01 |" in scen
    assert "Scenario name" not in scen
    assert "Orders are taken once and priced once." in out
    assert "![XX-001 Order intake](./components.svg)" in section(out, "Diagram")
    mapping = section(out, "Catalogue Mapping")
    assert "| 01 |  | gap |" in mapping and "| 02 |  | gap |" in mapping and "ABB-012" not in mapping
    assert "### From the source: Constraints" in out and "Never store card numbers." in out
    assert "Box 02 Payment Gateway: the label was faint." in out
    assert "A key on the diagram was left out." in out
    fm = out.split("---", 2)[1]
    assert "status: Draft" in fm and "last_modified: 2026-01-02" in fm
    assert "diagram: components.drawio" in fm and "origin: ai-generated" in fm
    assert '- "../src/a.drawio"' in fm
    assert "id: XX-001" in fm and 'title: "Order intake"' in fm and "portfolio:" not in fm
    if profile["suite"] == "pattern":
        assert fm.lstrip().startswith("kind: pattern")
        assert f"pattern_type: {type_name}" in fm and "pattern_scope: problem" in fm
        assert "pattern_scope is problem" in out
    else:
        assert fm.lstrip().startswith("kind: use-case")
        assert "document_type: use-case" in fm and "<ID>" not in out
    # Each signature key once, whatever the template carried.
    for key in ("kind", "pattern_type", "status", "provenance"):
        assert len(re.findall(rf"^{key}:", fm, re.M)) <= 1


def test_the_reference_architecture_realises_column():
    u = draft.assign_ids(sample())
    out = draft.render(template("reference-architecture"), u, "RA-001", "reference-architecture", [], "2026-01-02")
    assert "| 01 Order API | Takes orders | TBD | Order domain |" in out
    assert "implements: []" in out and "<path to the cost model>" not in out


def test_no_scenario_removes_the_examples_and_asks_for_one():
    u = draft.assign_ids(sample(scenario=False))
    for t in TEMPLATES:
        out = draft.render(template(t), u, "XX-001", t, [], "2026-01-02")
        scen = section(out, "Scenarios")
        assert "### S" not in scen and "Write at least one scenario" in scen


def test_the_kind_column_of_a_collaboration():
    u = draft.assign_ids(sample())
    out = draft.render(template("collaboration"), u, "CL-001", "collaboration", [], "2026-01-02")
    assert "| ABB-012 Order Store | TBD | store |" in out
    assert "| 01 Order API | Takes orders | participant |" in out


def test_model_toml_reads_and_covers_the_prefixes():
    u = draft.assign_ids(sample())
    for t in TEMPLATES:
        cfg = tomllib.loads(draft.model_toml(u, draft.PROFILES[t]))
        assert cfg["model"]["local_pattern"] == "[0-9]{2}"
        assert {x["section"] for x in cfg["markdown"]["tables"]} == {
            draft.PROFILES[t]["nodes"], draft.PROFILES[t]["edges"]}
        assert re.fullmatch(cfg["markdown"]["tables"][0]["id_pattern"], "ABB-012")


def test_folder_name():
    assert draft.folder_name("AP-001", "Order Intake: v2!") == "AP-001-order-intake-v2"


def test_a_scope_the_unit_sets_is_kept():
    u = draft.assign_ids(sample())
    u["scope"] = "platform"
    out = draft.render(template("collaboration"), u, "CL-001", "collaboration", [], "2026-01-02")
    assert "pattern_scope: platform" in out and "pattern_scope is" not in out


def test_a_candidate_is_marked_needs_conversion():
    u = sample()
    text = draft.candidate(u, "collaboration", ["../src/a.png"], "a picture to read", "2026-01-02")
    fm = text.split("---", 2)[1]
    assert fm.lstrip().startswith("kind: candidate")
    assert "candidate_type: collaboration" in fm and "id:" not in fm
    assert "portfolio:\n  state: needs-conversion\n" in fm and "since: 2026-01-02" in fm
    assert "# Order intake" in text
