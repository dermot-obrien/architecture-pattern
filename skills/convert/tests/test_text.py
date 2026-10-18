# SPDX-License-Identifier: Apache-2.0
"""The Markdown that goes with a diagram: titles, descriptions, link labels, scenarios."""
from __future__ import annotations

from convertlib import text
from convertlib.unit import add_box, add_link, box, new_unit


def unit_of(*names, links=()):
    u = new_unit(name="X")
    keys = {}
    for n in names:
        keys[n] = add_box(u, n)["key"]
    for a, b, label in links:
        add_link(u, keys[a], keys[b], label=label)
    return u


def by_label(u):
    return {b["label"]: b for b in u["boxes"]}


def steps(u, i=0):
    return [(box(u, s["actor"])["label"] if s["actor"] else "",
             box(u, s["target"])["label"] if s["target"] else "", s["action"])
            for s in u["scenarios"][i]["steps"]]


def test_title_summary_and_declared_type():
    u = unit_of("A")
    found = text.apply(u, "---\npattern_type: reference-architecture\n---\n# The title\n\n"
                          "First paragraph.\n\nSecond one.\n\n## More\n\nOther text.\n")
    assert found["title"] == "The title"
    assert u["summary"] == "First paragraph.\n\nSecond one."
    assert u["signals"]["declared_type"] == "reference-architecture"
    assert u["sections"] == [{"heading": "More", "text": "Other text.", "source": ""}]


def test_descriptions_from_a_table_with_kind():
    u = unit_of("Order API", "Order Store")
    text.apply(u, "| Component | Kind | Responsibility |\n|---|---|---|\n"
                  "| **Order API** | service | Takes orders |\n| Order Store | store | Keeps them |\n")
    b = by_label(u)
    assert b["Order API"]["description"] == "Takes orders"
    assert b["Order API"]["kind"] == "service"


def test_descriptions_from_bullets_and_headings():
    u = unit_of("Cache", "Primary Store", "Application")
    text.apply(u, "- Cache: holds recent items\n- **Primary Store** – the record\n\n"
                  "## Application\n\nOwns the read path.\n")
    b = by_label(u)
    assert b["Cache"]["description"] == "holds recent items"
    assert b["Primary Store"]["description"] == "the record"
    assert b["Application"]["description"] == "Owns the read path."


def test_the_texts_description_wins_over_a_line_on_the_diagram():
    u = unit_of("Gateway")
    u["boxes"][0].update(description="routes", described_by="diagram")
    text.apply(u, "- Gateway: routes every request to the right service\n")
    assert u["boxes"][0]["description"] == "routes every request to the right service"


def test_link_labels_from_a_table_and_arrows():
    u = unit_of("A", "B", "C", links=[("A", "B", ""), ("B", "C", "calls")])
    text.apply(u, "| From | To | Purpose |\n|---|---|---|\n| A | B | sends orders |\n\n"
                  "- B -> C: asks for prices\n")
    assert u["links"][0]["label"] == "sends orders"
    assert u["links"][1]["label"] == "calls" and u["links"][1]["description"] == "asks for prices"


def test_mermaid_sequence_with_aliases():
    u = unit_of("Supplier", "Supplier portal", "Buying team",
                links=[("Supplier", "Supplier portal", "submit")])
    text.apply(u, "## Sequence\n\n```mermaid\nsequenceDiagram\n  participant S as Supplier\n"
                  "  participant P as Supplier portal\n  S->>P: submit details\n"
                  "  P-->>Buying team: notify\n  P->>Nobody: lost\n```\n")
    assert u["scenarios"][0]["name"] == "Sequence"
    assert steps(u) == [("Supplier", "Supplier portal", "submit details"),
                        ("Supplier portal", "Buying team", "notify"),
                        ("Supplier portal", "", "lost")]
    s = u["scenarios"][0]["steps"]
    assert s[0]["link"] and not s[0]["uncertain"]
    assert "no line on the diagram" in s[1]["uncertain"]
    assert "not a box" in s[2]["uncertain"]


def test_numbered_list_under_a_flow_heading():
    u = unit_of("Order API", "Order Service", "Order Store")
    text.apply(u, "## Main flow\n\n1. The Order API asks the Order Service to create it.\n"
                  "2. The Order Service writes to the Order Store.\n3. Done.\n")
    assert steps(u)[0][:2] == ("Order API", "Order Service")
    assert steps(u)[1][:2] == ("Order Service", "Order Store")
    assert u["scenarios"][0]["steps"][2]["uncertain"] == "names no box on the diagram"


def test_longer_names_win():
    u = unit_of("Order", "Order Store", "Writer")
    text.apply(u, "## Steps\n\n1. The Writer puts it in the Order Store.\n")
    assert steps(u)[0][:2] == ("Writer", "Order Store")


def test_unheaded_list_naming_two_boxes_each_is_a_scenario_marked_uncertain():
    u = unit_of("Alpha", "Beta", "Gamma")
    text.apply(u, "## Notes\n\n1. Alpha calls Beta.\n2. Beta calls Gamma.\n3. Gamma answers Alpha.\n")
    assert len(u["scenarios"]) == 1
    assert all("not headed" in s["uncertain"] for s in u["scenarios"][0]["steps"])


def test_a_list_that_is_not_a_flow_is_left_as_text():
    u = unit_of("A", "B")
    text.apply(u, "## Constraints\n\n1. Keep it simple.\n2. Log everything.\n")
    assert u["scenarios"] == []
    assert u["sections"][0]["heading"] == "Constraints"


def test_steps_table():
    u = unit_of("A", "B", links=[("A", "B", "x")])
    text.apply(u, "## Flow\n\n| Step | From | To | Action |\n|---|---|---|---|\n| 1 | A | B | sends |\n")
    assert steps(u) == [("A", "B", "sends")]
