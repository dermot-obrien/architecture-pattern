# SPDX-License-Identifier: Apache-2.0
"""Choosing the type: from the content, given, or declared."""
from __future__ import annotations

import pytest

from conftest import source
from convertlib import classify
from convertlib.unit import add_box, new_unit

import convert


def read(diagram, *texts):
    spec = {"diagram": source(*diagram.split("/")), "texts": [source(*t.split("/")) for t in texts],
            "alternates": [], "name": "X"}
    return convert.read_unit_files(spec)


@pytest.mark.parametrize("diagram,texts,expected", [
    ("order-intake/order-intake.drawio", ["order-intake/order-intake.md"], "architecture-pattern"),
    ("document-search/document-search.svg", [], "architecture-pattern"),
    ("platform/outbox.drawio", ["platform/outbox.md"], "architecture-pattern"),
    ("platform/cache-aside.drawio", ["platform/cache-aside.md"], "architecture-pattern"),
    ("edge-gateway/edge-gateway.drawio.svg", ["edge-gateway/notes.md"], "reference-architecture"),
    ("claims-portal/claims-portal.svg", ["claims-portal/README.md"], "use-case"),
    ("appointment-booking/appointment-booking.drawio.png", ["appointment-booking/appointment-booking.md"], "use-case"),
    ("supplier-onboarding/supplier-onboarding.drawio", ["supplier-onboarding/supplier-onboarding.md"], "collaboration"),
])
def test_examples_classify_as_expected(diagram, texts, expected):
    u = read(diagram, *texts)[0]
    c = classify.classify(u)
    assert c["type"] == expected, c["reasons"]
    assert c["how"] == "chosen" and c["reasons"][0]


def test_pages_of_one_file_choose_together():
    units = read("event-pipeline/event-pipeline.drawio")
    assert classify.classify(convert.merged(units))["type"] == "reference-architecture"


def test_given_type_wins():
    u = read("order-intake/order-intake.drawio")[0]
    assert classify.classify(u, "CO") == {"type": "collaboration", "how": "given", "scores": {},
                                          "reasons": ["--type CO was given"]}


def test_declared_type_wins():
    u = new_unit()
    add_box(u, "Order Service")
    u["signals"]["declared_type"] = "use-case"
    assert classify.classify(u)["type"] == "use-case"


def test_nothing_clear_is_a_collaboration():
    u = new_unit()
    for n in ("Alpha", "Beta", "Gamma"):
        add_box(u, n)
    c = classify.classify(u)
    assert c["type"] == "collaboration" and "collaboration" in c["reasons"][0]


def test_technology_name_counts_as_physical_not_logical():
    u = new_unit()
    for n in ("Query API server", "Analytical database 24", "Dashboard application"):
        add_box(u, n)
    c = classify.classify(u)
    assert c["scores"]["reference-architecture"] > c["scores"]["architecture-pattern"]


def test_aliases():
    assert classify.normalise("AP") == "architecture-pattern"
    assert classify.normalise("reference architecture") == "reference-architecture"
    assert classify.normalise("use_case") == "use-case"
    assert classify.normalise("nonsense") == ""
