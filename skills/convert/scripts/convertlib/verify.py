# SPDX-License-Identifier: Apache-2.0
"""Check a drafted document against itself and against the source it came from.

1. `model validate` on the document and the diagram it declares.
2. The diagram regenerated from the document's own tables, with `model emit`, read back,
   and compared with what was read from the source diagram: every box by its name and
   every line by the names at its two ends. A box or a line on one side only, and a line
   whose direction changed, are reported, never hidden.

An image source has no structure to compare, so only the first check applies; the
report says so.
"""
from __future__ import annotations

import json
import os
import tempfile

from . import skills
from .unit import box, norm


def model_json(path, config=None):
    args = ["extract", path, "--format", "json"]
    if config:
        args += ["--config", config]
    r = skills.run_model(*args)
    if r is None:
        return None, "the model skill is not installed"
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()
    try:
        return json.loads(r.stdout), ""
    except ValueError:
        return None, "model extract printed no JSON"


def validate(doc):
    r = skills.run_model("validate", doc, "--json", "--fail-on", "error")
    if r is None:
        return {"result": "skipped", "why": "the model skill is not installed", "findings": []}
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return {"result": "error", "why": (r.stderr or r.stdout).strip()[:400], "findings": []}
    findings = data.get("findings", data if isinstance(data, list) else [])
    errors = [f for f in findings if f.get("severity") == "error"]
    return {"result": "error" if errors or r.returncode else "ok",
            "summary": data.get("summary", ""), "abstraction": data.get("abstraction", ""),
            "findings": findings}


def regenerate(doc):
    """The document's model as model emit draws it, read back from the drawn diagram."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "regenerated.drawio")
        r = skills.run_model("emit", doc, "--to", "drawio", "--out", out)
        if r is None:
            return None, "the model skill is not installed"
        if r.returncode != 0:
            return None, (r.stderr or r.stdout).strip()
        doc_cfg = config_near(doc)
        args = ["extract", out, "--format", "json"]
        if doc_cfg:
            args += ["--config", doc_cfg]
        r = skills.run_model(*args)
        try:
            return json.loads(r.stdout), ""
        except (ValueError, AttributeError):
            return None, "the regenerated diagram did not read back"


def config_near(doc):
    d = os.path.dirname(os.path.abspath(doc))
    while True:
        for name in (os.path.join(".agents", "skill-bindings.toml"), "skill-bindings.toml",
                     "model.toml", ".model.toml"):
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
        up = os.path.dirname(d)
        if up == d:
            return ""
        d = up


def compare(source_unit, regenerated) -> dict:
    """Differences between the source's boxes and lines and the regenerated diagram's."""
    src_boxes = {norm(b["label"]): b for b in source_unit["boxes"]}
    gen_nodes = {n["id"]: n for n in regenerated.get("nodes", [])}
    gen_boxes = {norm(n.get("label") or n["id"]): n for n in gen_nodes.values()}

    def label_of(node_id):
        n = gen_nodes.get(node_id)
        return norm(n.get("label") or node_id) if n else norm(node_id)

    src_links = []
    for lk in source_unit["links"]:
        a, b = box(source_unit, lk["source"]), box(source_unit, lk["target"])
        if a and b:
            src_links.append((norm(a["label"]), norm(b["label"]), lk.get("label", "")))
    gen_links = [(label_of(e["source"]), label_of(e["target"]), e.get("label", ""))
                 for e in regenerated.get("edges", [])]

    missing_boxes = sorted(src_boxes[k]["label"] for k in src_boxes if k not in gen_boxes)
    extra_boxes = sorted((gen_boxes[k].get("label") or gen_boxes[k]["id"])
                         for k in gen_boxes if k not in src_boxes)
    remaining = list(gen_links)
    missing_links, reversed_links = [], []
    for s, t, label in src_links:
        hit = next((g for g in remaining if g[0] == s and g[1] == t), None)
        if hit:
            remaining.remove(hit)
            continue
        rev = next((g for g in remaining if g[0] == t and g[1] == s), None)
        if rev:
            remaining.remove(rev)
            reversed_links.append(f"{s} to {t}")
            continue
        missing_links.append(f"{s} to {t}" + (f" ({label})" if label else ""))
    extra_links = [f"{s} to {t}" + (f" ({lb})" if lb else "") for s, t, lb in remaining]
    src_steps = sum(len(sc["steps"]) for sc in source_unit["scenarios"])
    gen_steps = sum(len(sc.get("steps", [])) for sc in regenerated.get("scenarios", []))
    same = not (missing_boxes or extra_boxes or missing_links or extra_links or reversed_links)
    return {"agrees": same,
            "boxes": {"source": len(src_boxes), "document": len(gen_boxes),
                      "missing": missing_boxes, "extra": extra_boxes},
            "links": {"source": len(src_links), "document": len(gen_links),
                      "missing": missing_links, "extra": extra_links,
                      "reversed": reversed_links},
            "steps": {"source": src_steps, "document": gen_steps}}


def check(doc, source_unit=None) -> dict:
    out = {"validate": validate(doc)}
    if source_unit is None or source_unit.get("extraction") == "agent":
        out["comparison"] = {"skipped": "the source is an image, so there is no structure to "
                                        "compare; check the diagram against the picture by eye"}
        return out
    regenerated, why = regenerate(doc)
    if regenerated is None:
        out["comparison"] = {"skipped": f"the diagram could not be regenerated: {why}"}
    else:
        out["comparison"] = compare(source_unit, regenerated)
    return out
