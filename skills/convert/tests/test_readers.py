# SPDX-License-Identifier: Apache-2.0
"""The diagram readers: draw.io drawn by hand, draw.io with identifiers, SVG and PNG."""
from __future__ import annotations

import os

import pytest

from conftest import SKILL, needs_model, source
from convertlib import drawio, image, svg
from convertlib.unit import box, split_label


def labels(u):
    return [b["label"] for b in u["boxes"]]


def link_names(u):
    return {(box(u, lk["source"])["label"], box(u, lk["target"])["label"]): lk["label"]
            for lk in u["links"]}


def read_file(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class TestLabels:
    def test_name_and_description_from_markup(self):
        assert split_label("<b>Order Service</b><br>validates the order") == \
            ("", "Order Service", "validates the order")

    def test_catalogue_identifier_leads(self):
        assert split_label("ABB-012 Identity Provider") == ("ABB-012", "Identity Provider", "")

    def test_identifier_on_its_own_line(self):
        assert split_label("SBB-101<br>Gateway<br>edge") == ("SBB-101", "Gateway", "edge")

    def test_local_identifier_is_two_digits(self):
        assert split_label("3 Gateway") == ("03", "Gateway", "")

    def test_number_inside_a_name_is_not_an_identifier(self):
        assert split_label("Office Suite 365") == ("", "Office Suite 365", "")

    def test_entities_and_spaces(self):
        assert split_label("Q&amp;A&nbsp;agent") == ("", "Q&A agent", "")


@pytest.fixture(scope="module")
def unit():
    units = drawio.read(source("order-intake", "order-intake.drawio"), "Order intake")
    assert len(units) == 1
    return units[0]


class TestDrawnDrawio:
    def test_read_from_shapes(self, unit):
        assert unit["extraction"] == "heuristic"

    def test_every_box_and_no_more(self, unit):
        assert sorted(labels(unit)) == sorted([
            "Sales Channel", "Order API", "Order Service", "Order Store", "Payment Gateway",
            "Event Broker", "Notification Service"])

    def test_key_and_title_left_out(self, unit):
        assert not any("Blue" in x or "Key" == x or "Order Intake" == x for x in labels(unit))
        assert any("key or legend" in n for n in unit["notes"])
        assert unit["signals"]["title"] == "Order Intake"

    def test_container_is_the_group(self, unit):
        by = {b["label"]: b for b in unit["boxes"]}
        assert by["Order Service"]["container"] == "Order domain"
        assert by["Payment Gateway"]["container"] == ""

    def test_second_line_is_the_description(self, unit):
        by = {b["label"]: b for b in unit["boxes"]}
        assert by["Order Service"]["description"] == "validates and prices the order"

    def test_links_with_numbers_taken_off(self, unit):
        names = link_names(unit)
        assert names[("Sales Channel", "Order API")] == "submit order"
        assert names[("Event Broker", "Notification Service")] == "deliver event"   # a child label
        assert len(unit["links"]) == 6

    def test_numbered_connectors_are_a_scenario(self, unit):
        assert len(unit["scenarios"]) == 1
        steps = unit["scenarios"][0]["steps"]
        assert [s["step"] for s in steps] == [1, 2, 3, 4, 5, 6]
        assert box(unit, steps[2]["target"])["label"] == "Payment Gateway"
        assert all(s["link"] for s in steps)


class TestCompressedPages:
    def test_one_unit_per_page(self):
        units = drawio.read(source("event-pipeline", "event-pipeline.drawio"), "Event pipeline")
        assert [u["name"] for u in units] == ["Event pipeline Ingest", "Event pipeline Serve"]
        assert len(units[0]["boxes"]) == 5 and len(units[1]["boxes"]) == 3
        assert [u["page"] for u in units] == [0, 1]

    def test_uncompressed_writes_every_page_as_xml(self):
        text = drawio.uncompressed(read_file(source("event-pipeline", "event-pipeline.drawio")))
        assert text.count("<mxGraphModel") == 2 and 'compressed="false"' in text


def mxfile(cells):
    return ('<mxfile><diagram name="P"><mxGraphModel><root><mxCell id="0"/>'
            '<mxCell id="1" parent="0"/>' + cells + "</root></mxGraphModel></diagram></mxfile>")


def vertex(cid, label, x, y, w=120, h=60, style="rounded=1;", parent="1"):
    return (f'<mxCell id="{cid}" value="{label}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(cid, s, t, label="", style="", points=""):
    ends = (f' source="{s}"' if s else "") + (f' target="{t}"' if t else "")
    return (f'<mxCell id="{cid}" value="{label}" style="{style}" edge="1" parent="1"{ends}>'
            f'<mxGeometry relative="1" as="geometry">{points}</mxGeometry></mxCell>')


class TestDrawnEdgeCases:
    def test_arrow_drawn_backwards_is_reversed(self):
        u = drawio.read_text(mxfile(vertex("a", "Client", 0, 0) + vertex("b", "Server", 300, 0)
                                    + edge("e", "a", "b", "reply", "startArrow=classic;endArrow=none;")),
                             "x.drawio", "X")[0]
        assert link_names(u) == {("Server", "Client"): "reply"}

    def test_line_without_arrowhead_is_undirected_and_uncertain(self):
        u = drawio.read_text(mxfile(vertex("a", "A", 0, 0) + vertex("b", "B", 300, 0)
                                    + edge("e", "a", "b", "", "endArrow=none;")), "x.drawio", "X")[0]
        assert u["links"][0]["directed"] is False
        assert "no arrowhead" in u["links"][0]["uncertain"]

    def test_free_end_joins_the_nearest_box(self):
        pts = '<mxPoint x="305" y="30" as="targetPoint"/>'
        u = drawio.read_text(mxfile(vertex("a", "A", 0, 0) + vertex("b", "B", 300, 0)
                                    + edge("e", "a", None, "call", points=pts)), "x.drawio", "X")[0]
        assert link_names(u) == {("A", "B"): "call"}
        assert "not attached" in u["links"][0]["uncertain"]

    def test_icon_takes_the_text_beside_it(self):
        u = drawio.read_text(mxfile(
            vertex("a", "", 0, 0, 60, 60, "shape=mxgraph.cloud_platform.database;")
            + vertex("t", "Ledger", 0, 70, 60, 20, "text;strokeColor=none;fillColor=none;")
            + vertex("b", "Writer", 300, 0) + edge("e", "b", "a", "post")), "x.drawio", "X")[0]
        assert "Ledger" in labels(u)
        assert any("text beside" in b["uncertain"] for b in u["boxes"])

    def test_endpoint_inside_a_box_climbs_to_it(self):
        u = drawio.read_text(mxfile(
            vertex("a", "Outer", 0, 0, 200, 100) + vertex("b", "Other", 400, 0)
            + edge("e", "b", "a", "use")), "x.drawio", "X")[0]
        assert link_names(u) == {("Other", "Outer"): "use"}

    def test_scenario_layer(self):
        cells = (vertex("a", "A", 0, 0) + vertex("b", "B", 300, 0) + edge("e", "a", "b", "calls")
                 + '<mxCell id="L2" value="S1 Happy path" parent="0"/>'
                 + '<mxCell id="f" value="1: asks" style="" edge="1" parent="L2" source="a" target="b">'
                 '<mxGeometry relative="1" as="geometry"/></mxCell>')
        u = drawio.read_text(mxfile(cells), "x.drawio", "X")[0]
        assert len(u["links"]) == 1
        assert u["scenarios"][0]["name"] == "Happy path"
        assert u["scenarios"][0]["steps"][0]["action"] == "asks"
        assert u["scenarios"][0]["steps"][0]["link"] == u["links"][0]["key"]

    def test_badges_are_not_boxes(self):
        u = drawio.read_text(mxfile(vertex("a", "A", 0, 0) + vertex("b", "B", 300, 0)
                                    + vertex("n", "1", 10, 10, 24, 24, "ellipse;")
                                    + edge("e", "a", "b", "x")), "x.drawio", "X")[0]
        assert labels(u) == ["A", "B"]

    def test_gaps_in_numbering_are_renumbered_with_a_note(self):
        u = drawio.read_text(mxfile(vertex("a", "A", 0, 0) + vertex("b", "B", 300, 0)
                                    + vertex("c", "C", 600, 0) + edge("e1", "a", "b", "1. go")
                                    + edge("e2", "b", "c", "3. on")), "x.drawio", "X")[0]
        assert [s["step"] for s in u["scenarios"][0]["steps"]] == [1, 2]
        assert any("renumbered" in n for n in u["notes"])

    def test_not_a_drawio_file(self):
        with pytest.raises(drawio.DrawioError):
            drawio.read_text("<svg/>", "x.drawio", "X")


@needs_model
class TestIdentifiedDrawio:
    def test_read_exactly_by_model(self):
        path = os.path.join(SKILL, "..", "pattern", "examples", "knowledge-retrieval",
                            "components.drawio")
        units = drawio.read(os.path.normpath(path), "Knowledge retrieval")
        u = units[0]
        assert u["extraction"] == "exact"
        assert {b["id"] for b in u["boxes"]} >= {"ABB-901", "ABB-905"}
        assert all(lk["id"].startswith("IF-") for lk in u["links"])
        assert u["scenarios"] and all(s["actor"] for sc in u["scenarios"] for s in sc["steps"])


class TestSvg:
    def test_drawio_export_is_read_as_drawio(self):
        units = svg.read(source("edge-gateway", "edge-gateway.drawio.svg"), "Edge gateway")
        u = units[0]
        assert u["sources"]["format"] == "svg-drawio"
        assert "API gateway 3.4" in labels(u) and len(u["links"]) == 5
        assert {b["container"] for b in u["boxes"]} == {"Container cluster 1.29", ""}

    def test_plain_svg_boxes_lines_and_labels(self):
        u = svg.read(source("claims-portal", "claims-portal.svg"), "Claims")[0]
        assert u["extraction"] == "heuristic"
        assert sorted(labels(u)) == sorted(["Claimant", "Claims Portal", "Claims Service",
                                            "Policy Register", "Document Store", "Claims Handler"])
        assert link_names(u)[("Claims Service", "Policy Register")] == "check cover"
        assert u["signals"]["title"] == "Submit a claim"
        assert all(len(b["geom"]) == 4 for b in u["boxes"])

    def test_plain_svg_description_from_a_second_line(self):
        u = svg.read(source("claims-portal", "claims-portal.svg"), "Claims")[0]
        by = {b["label"]: b for b in u["boxes"]}
        assert by["Claims Portal"]["description"] == "where claims are made"

    def test_transforms_are_followed(self):
        text = ('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="300">'
                '<g transform="translate(100,50)"><rect x="0" y="0" width="120" height="50"/>'
                '<text x="60" y="30">Left</text></g>'
                '<g transform="translate(500,50)"><rect x="0" y="0" width="120" height="50"/>'
                '<text x="60" y="30">Right</text></g>'
                '<line x1="220" y1="75" x2="500" y2="75" marker-end="url(#m)"/></svg>')
        u = svg.read_text(text, "x.svg", "X")[0]
        assert link_names(u) == {("Left", "Right"): ""}

    def test_not_an_svg(self):
        with pytest.raises(svg.SvgError):
            svg.read_text("<mxfile/>", "x.svg", "X")


class TestImages:
    def test_png_with_drawio_inside(self):
        with open(source("appointment-booking", "appointment-booking.drawio.png"), "rb") as fh:
            info = image.png_info(fh.read())
        assert info["width"] == 980 and info["mxfile"].startswith("<mxfile")
        units = drawio.read_text(info["mxfile"], "x.png", "Booking", fmt="png-drawio")
        assert len(units[0]["boxes"]) == 5 and len(units[0]["scenarios"][0]["steps"]) == 5

    def test_picture_is_left_for_the_agent(self):
        path = source("incident-handover", "incident-handover.png")
        with open(path, "rb") as fh:
            data = fh.read()
        assert image.png_info(data)["mxfile"] == ""
        u = image.for_agent(path, "Incident handover", data)
        assert u["status"] == "needs-agent" and u["extraction"] == "agent"
        assert u["image"] == {"width": 860, "height": 420}
