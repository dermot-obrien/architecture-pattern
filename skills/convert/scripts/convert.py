#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Convert existing architecture material, a diagram and its text, into a pattern document.

    python scripts/convert.py run   <file-or-folder>... [--type TYPE] [--out DIR] [--work DIR]
                                    [--name NAME] [--id ID] [--no-archive] [--dry-run] [--json]
    python scripts/convert.py draft <conversion folder> [--unit SLUG] [--force] [--json]
    python scripts/convert.py read  <diagram> [--text FILE ...]
    python scripts/convert.py verify <document> [--source UNIT.json] [--json]
    python scripts/convert.py archive <conversion folder> [--dry-run]

run      finds the diagrams (.drawio, .svg, .png, .jpg) and texts (.md, .txt) under the
         paths, pairs each diagram with its text, gathers copies into one conversion
         folder with a manifest, archives the originals that git tracks with `git mv`,
         reads each diagram, chooses its type, drafts the document beside its diagram,
         checks it, and writes report.md. --dry-run prints the plan and writes nothing.
draft    drafts again from each unit's unit.json in a conversion folder: after the agent
         has written one from an image, or corrected one. A document already drafted is
         never overwritten unless --force.
read     prints the unit model read from one diagram and its texts, as JSON.
verify   validates a document with model, regenerates its diagram from its tables, and
         compares that with the source unit.
archive  archives the originals of a run made with --no-archive.

TYPE is architecture-pattern, reference-architecture, use-case or collaboration (or AP,
RA, UC, CL). Unset, each unit's type is chosen from its content, and report.md says why.

Bindings, all optional, in [suite.convert] of .agents/skill-bindings.toml, relative to
that file: workDir (default conversions/ at the repository root), archiveDir (default
archive/ at the root of the repository holding the source). Documents go where the
pattern and use-case skills put them, their outputDir, unless --out names a folder.

Exit 0: every unit drafted and valid. 1: a unit needs the agent (an image), or failed to
draft or validate. 2: usage. 3: the model skill or the pattern skill is not installed.
"""
from __future__ import annotations

import argparse
import copy
import datetime
import json
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    print(f"Python {sys.version.split()[0]} is too old: convert.py needs 3.11 or newer.",
          file=sys.stderr)
    sys.exit(2)

import tomllib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from convertlib import classify, draft, drawio, image, preview, sketch, skills, svg, text, verify  # noqa: E402
from convertlib import unit as unit_mod  # noqa: E402
from convertlib import workspace as ws  # noqa: E402
from convertlib.unit import humanise, slug  # noqa: E402

BINDING_NAMES = (os.path.join(".agents", "skill-bindings.toml"), "skill-bindings.toml")


class UsageError(Exception):
    pass


# ------------------------------------------------------------------ bindings

def find_bindings(start) -> str:
    d = os.path.abspath(start)
    while True:
        for name in BINDING_NAMES:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
        up = os.path.dirname(d)
        if up == d:
            return ""
        d = up


def load_bindings(start) -> tuple:
    path = find_bindings(start)
    if not path:
        return "", {}
    try:
        with open(path, "rb") as fh:
            return path, tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as ex:
        raise UsageError(f"{path}: {ex}")


def bound(binding_file, value) -> str:
    if not value:
        return ""
    return os.path.normpath(os.path.join(os.path.dirname(binding_file), str(value)))


def convert_table(start) -> tuple:
    """[suite.convert], with archiveDir falling back to [suite.portfolio] archiveDir, so a
    repository that binds a portfolio has one archive folder."""
    path, raw = load_bindings(start)
    suite = raw.get("suite") or {}
    table = dict(suite.get("convert") or {})
    if not table.get("archiveDir") and (suite.get("portfolio") or {}).get("archiveDir"):
        table["archiveDir"] = suite["portfolio"]["archiveDir"]
    return path, table


def node_series(raw, profile):
    """The identifier prefixes a workspace's binding reads in a type's boxes table, such as
    {"ABB", "SBB"}, or None when its pattern says nothing plainer than a regular expression."""
    import re
    for t in ((raw.get("markdown") or {}).get("tables") or []):
        if str(t.get("section", "")).lower() == profile["nodes"].lower():
            found = set(re.findall(r"[A-Z][A-Z0-9]{1,6}(?=[|)\-])", str(t.get("id_pattern", ""))))
            return found or None
    return None


def binding_reads(binding_file, raw, section) -> bool:
    """Whether a binding file maps a table section, so a document there needs no model.toml."""
    tables = ((raw.get("markdown") or {}).get("tables") or [])
    return any(str(t.get("section", "")).lower() == section.lower() for t in tables)


# ------------------------------------------------------------------ reading

def read_unit_files(spec, scratch=None) -> list:
    """Units from one diagram and its texts. `scratch` is where a decoded draw.io goes."""
    path, name = spec["diagram"], spec["name"]
    k = ws.kind(path)
    embedded = ""
    if k == "drawio":
        with open(path, encoding="utf-8") as fh:
            embedded = fh.read()
        units = drawio.read_text(embedded, path, name)
    elif k == "svg":
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        embedded = svg.embedded_drawio(raw)
        units = svg.read_text(raw, path, name)
    else:
        with open(path, "rb") as fh:
            data = fh.read()
        info = image.png_info(data)
        if info.get("mxfile"):
            embedded = info["mxfile"]
            units = drawio.read_text(embedded, path, name, fmt="png-drawio")
        else:
            units = [image.for_agent(path, name, data)]
    if not units:
        u = image.for_agent(path, name, b"")
        u["extraction"] = "agent"
        u["notes"] = ["no boxes could be read from the diagram: read it, then write the "
                      "boxes, links and scenarios here"]
        units = [u]
    for u in units:
        u["sources"]["text"] = list(spec.get("texts", []))
        u["sources"]["alternates"] = list(spec.get("alternates", []))
        if embedded and u["extraction"] != "agent":
            u["drawio"] = embedded
        for t in spec.get("texts", []):
            with open(t, encoding="utf-8", errors="replace") as fh:
                found = text.apply(u, fh.read(), t)
            if found.get("title") and len(units) == 1:
                u["name"] = found["title"]
        if len(units) == 1 and not spec.get("texts") and u["signals"].get("title"):
            u["name"] = u["signals"]["title"]
        finish(u)
    return units


def merged(units) -> dict:
    """One unit holding every page's boxes and words, for choosing their type together."""
    m = copy.deepcopy(units[0])
    for u in units[1:]:
        m["boxes"] += copy.deepcopy(u["boxes"])
        m["signals"]["styles"] = m["signals"].get("styles", []) + u["signals"].get("styles", [])
        m["signals"]["words"] = m["signals"].get("words", []) + u["signals"].get("words", [])
    return m


def finish(u) -> None:
    """Tidy a unit after every reader has had its say."""
    # A step that names no actor cannot be drawn; keep it in the notes instead.
    for sc in u["scenarios"]:
        kept = []
        for st in sc["steps"]:
            if not st.get("actor"):
                u["notes"].append(f"a step of {sc.get('name') or 'a scenario'!r}, "
                                  f"{st.get('action')!r}, names no box on the diagram; left out")
                continue
            kept.append(st)
        for i, st in enumerate(kept, 1):
            st["step"] = i
        sc["steps"] = kept
    u["scenarios"] = [sc for sc in u["scenarios"] if sc["steps"]]
    # One flow drawn on the diagram and written in the text is one scenario.
    out = []
    for sc in u["scenarios"]:
        pairs = [(s["actor"], s["target"]) for s in sc["steps"]]
        twin = next((o for o in out if [(s["actor"], s["target"]) for s in o["steps"]] == pairs), None)
        if twin:
            if twin["from"] == "diagram" and sc["from"] != "diagram":
                for a, b in zip(twin["steps"], sc["steps"]):
                    if b.get("action") and (not a.get("action") or a["action"] == "TBD"
                                            or len(b["action"]) > len(a["action"])):
                        a["action"] = b["action"]
                if sc.get("name"):
                    twin["name"] = sc["name"]
            u["notes"].append(f"the flow {sc.get('name')!r} is drawn on the diagram and written "
                              "in the text; it is one scenario")
            continue
        out.append(sc)
    u["scenarios"] = out
    for b in u["boxes"]:
        b.pop("_cell", None)


# ------------------------------------------------------------------ identifiers and places

class Places:
    """Where each type's documents go, and the next identifier in each series."""

    def __init__(self, out=None, cwd=None):
        self.cwd = cwd or os.getcwd()
        self.out = os.path.abspath(out) if out else ""
        self.reg = skills.load_pattern_module("register")
        self.used = {}

    def series(self, type_name):
        profile = draft.PROFILES[type_name]
        if self.reg is None:
            return None, profile["series"]
        binding_file, tables = self.reg.load_bindings(self.cwd)
        suite = profile["suite"]
        table = tables.get(suite, {})
        s = self.reg.Series(suite, table, binding_file, self.cwd)
        types = s.types
        if suite == "pattern" and type_name in types and types[type_name].get("idSeries"):
            s = s.of_type(type_name)
        elif suite == "pattern" and type_name == "architecture-pattern" and table.get("idSeries") and not types:
            s.set_prefix(str(table["idSeries"]), type_name)
        elif suite == "pattern":
            s.set_prefix(profile["series"], type_name)
        if self.out:
            s.roots = list(s.roots) + [self.out]
        return s, s.prefix

    def folder(self, type_name) -> str:
        if self.out:
            return self.out
        s, _ = self.series(type_name)
        if s is None:
            return os.path.join(self.cwd, "patterns" if draft.PROFILES[type_name]["suite"] == "pattern" else "use-cases")
        return s.output

    def register_file(self, type_name) -> str:
        s, _ = self.series(type_name)
        return s.register if s is not None and s.register and os.path.isfile(s.register) else ""

    def next_id(self, type_name) -> str:
        s, prefix = self.series(type_name)
        n, width = 0, 3
        if s is not None:
            reg = self.reg.Register(s.register) if s.register and os.path.isfile(s.register) else None
            ident = self.reg.next_id(s, reg)
            num = ident.rsplit("-", 1)[1]
            n, width = int(num), len(num)
        else:
            n = 1
        n = max(n, self.used.get(prefix, 0) + 1)
        self.used[prefix] = n
        return f"{prefix}-{n:0{width}d}"


def template_for(type_name, cwd) -> tuple:
    """(template path, where it came from) for a type."""
    profile = draft.PROFILES[type_name]
    if profile["suite"] == "pattern":
        tmod = skills.load_pattern_module("template")
        if tmod is not None:
            binding_file, tables = tmod.register.load_bindings(cwd)
            table = tables.get("pattern", {})
            types = table.get("types") or {}
            if type_name in types:
                path, source, _own = tmod.resolve(table, binding_file, type_name)
                if os.path.isfile(path):
                    return path, source
        p = skills.find("pattern", profile["template"])
        if p:
            return p, f"shipped by pattern for {type_name}"
    else:
        path, raw = load_bindings(cwd)
        t = (((raw.get("suite") or {}).get("use-case") or {}).get("template"))
        if t:
            p = bound(path, t)
            if os.path.isfile(p):
                return p, "[suite.use-case] template"
        p = skills.find("use-case", profile["template"])
        if p:
            return p, "shipped by use-case"
    raise UsageError(f"no template for {type_name}: install the "
                     f"{profile['skill']} skill beside this one")


# ------------------------------------------------------------------ drafting one unit

def page_only(drawio_text, page):
    """The draw.io text holding only one page, written out uncompressed."""
    import xml.etree.ElementTree as ET
    full = drawio.uncompressed(drawio_text)
    root = ET.fromstring(full)
    pages = root.findall("diagram")
    for i, d in enumerate(pages):
        if i != page:
            root.remove(d)
    # The first layer is the structure; name it so, as model emit does, when the source
    # left it unnamed, so a view of it can be recorded by name.
    for d in root.findall("diagram"):
        cells = d.find("mxGraphModel/root")
        if cells is None:
            continue
        for c in cells:
            if c.get("parent") == "0":
                if not (c.get("value") or c.get("label")):
                    c.set("value", "Structure")
                break
    return ET.tostring(root, encoding="unicode")


def make_diagram(doc, u, notes) -> None:
    """components.drawio beside the document: the source's own drawing with identifiers
    adopted onto its shapes, so its layout is kept, else one generated from the tables;
    then a current view of its structure layer."""
    folder = os.path.dirname(doc)
    target = os.path.join(folder, "components.drawio")
    adopted = False
    drawing = ""
    if u.get("drawio"):
        drawing = page_only(u["drawio"], u.get("page", 0))
        what = "the source drawing"
    elif sketch.has_geometry(u):
        drawing = sketch.build(u)
        what = "a redrawing of the source, each box where it was drawn"
    if drawing:
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(drawing)
        r = skills.run_model("sync", doc, target, "--adopt")
        if r is not None and r.returncode == 0:
            adopted = True
            notes.append(f"components.drawio is {what}, its shapes given the "
                         "document's identifiers (model sync --adopt), so its layout is kept")
        else:
            notes.append(f"{what} could not be adopted "
                         f"({((r.stderr or r.stdout).strip()[:200]) if r else 'no model'}); "
                         "the diagram was generated from the tables instead")
            os.unlink(target)
    if not adopted:
        r = skills.run_model("emit", doc, "--to", "drawio", "--out", target)
        if r is None or r.returncode != 0:
            raise RuntimeError(f"model emit failed: {(r.stderr or r.stdout).strip() if r else 'no model'}")
        notes.append("components.drawio was generated from the tables: arrange it in draw.io, "
                     "then use model sync, never emit")
    view = os.path.join(folder, "components.svg")
    if skills.run_model("drawio").returncode == 0:
        r = skills.run_model("render", target, "--out", view, "--layer", layer_name(target))
        if r.returncode == 0:
            notes.append("components.svg was rendered by draw.io desktop")
            return
    with open(target, encoding="utf-8") as fh:
        svg_text, layer = preview.build(fh.read())
    with open(view, "w", encoding="utf-8") as fh:
        fh.write(svg_text)
    r = skills.run_model("stamp", view, "--diagram", target, "--layer", layer)
    if r is None or r.returncode != 0:
        notes.append(f"the preview view could not be stamped: {(r.stderr or r.stdout).strip()[:200] if r else ''}")
    notes.append("components.svg is a plain preview drawn without draw.io; after arranging "
                 "the diagram, render or export the Structure layer and stamp it")


def layer_name(diagram) -> str:
    r = skills.run_model("layers", diagram, "--json")
    try:
        layers = json.loads(r.stdout)
        return layers[0].get("name") or "Structure"
    except (ValueError, IndexError, AttributeError, KeyError):
        return "Structure"


def draft_unit(u, places, cwd, force=False, ident=None, dry_run=False) -> dict:
    """Draft one unit. Returns its result for the report."""
    t = u["type"]
    profile = draft.PROFILES[t]
    res = {"type": t, "notes": []}
    template, source = template_for(t, cwd)
    res["template"] = f"{template} ({source})"
    folder_root = places.folder(t)
    s_, _prefix = places.series(t) if not places.out else (None, "")
    if s_ is not None and s_.output_default:
        res["notes"].append(f"no outputDir is bound under [suite.{profile['suite']}], so the "
                            f"document went in the default, {folder_root}; bind outputDir to "
                            "put documents elsewhere")
    ident = ident or u.get("id") or places.next_id(t)
    u["id"] = ident
    folder = os.path.join(folder_root, draft.folder_name(ident, u["name"]))
    doc = os.path.join(folder, "index.md")
    res.update({"id": ident, "document": doc})
    if dry_run:
        return res
    if os.path.exists(doc) and not force:
        res["status"] = "exists"
        res["notes"].append("a document is already there; it was not overwritten (pass --force)")
        return res
    binding_file, raw = load_bindings(folder_root if os.path.isdir(folder_root) else cwd)
    reads = bool(binding_file) and binding_reads(binding_file, raw, profile["nodes"])
    drafted = draft.assign_ids(copy.deepcopy(u), node_series(raw, profile) if reads else None)
    # Local ids (01 Gateway) read only where the binding says what one looks like.
    has_local = any(draft.LOCAL.match(b["id"]) for b in drafted["boxes"])
    model_table = raw.get("model") or {}
    if reads and has_local and not (model_table.get("local_pattern") or model_table.get("local_prefix")):
        reads = False
        res["notes"].append(f"{binding_file} maps the tables but sets no [model] local_pattern, "
                            "so local ids would not read there")
    with open(template, encoding="utf-8") as fh:
        body = draft.render(fh.read(), drafted, ident, t,
                            [os.path.relpath(p, folder).replace(os.sep, "/")
                             for p in u["sources"].get("kept") or
                             [u["sources"]["diagram"]] + u["sources"].get("text", [])])
    os.makedirs(folder, exist_ok=True)
    with open(doc, "w", encoding="utf-8") as fh:
        fh.write(body)
    if not reads:
        with open(os.path.join(folder, "model.toml"), "w", encoding="utf-8") as fh:
            fh.write(draft.model_toml(drafted, profile))
        res["notes"].append("model.toml was written beside the document, because no binding "
                            f"file above it maps a {profile['nodes']} table")
    make_diagram(doc, drafted, res["notes"])
    reg = places.register_file(t)
    if reg:
        args = [sys.executable, skills.pattern_script("register.py")]
        if profile["suite"] == "use-case":
            args += ["--suite", "use-case"]
        r = subprocess.run(args + ["add", ident, "--name", u["name"], "--status", "Draft",
                                   "--path", folder], cwd=cwd, capture_output=True, text=True)
        res["notes"].append("register row added" if r.returncode == 0 else
                            f"register row not added: {(r.stderr or r.stdout).strip()}")
    res["status"] = "drafted"
    res["drafted"] = {"boxes": len(drafted["boxes"]), "links": len(drafted["links"]),
                      "scenarios": len(drafted["scenarios"]),
                      "steps": sum(len(s["steps"]) for s in drafted["scenarios"])}
    return res


# ------------------------------------------------------------------ the report

def write_report(run_dir, manifest) -> str:
    L = ["# Conversion report", "",
         f"Run {os.path.basename(run_dir)}, {manifest.get('date', '')}. Sources: "
         + ", ".join(f"`{p}`" for p in manifest.get("inputs", [])) + ".", ""]
    units = manifest.get("units", [])
    L += ["| Unit | Source | Read | Type | Document | Status |", "|---|---|---|---|---|---|"]
    for un in units:
        r = un.get("result", {})
        L.append(f"| {un['slug']} | {os.path.basename(un['diagram'])} | {un.get('extraction', '')} | "
                 f"{un.get('type', '')} | {r.get('id', '')} | {r.get('status', un.get('status', ''))} |")
    L.append("")
    for un in units:
        r = un.get("result", {})
        L += [f"## {un['slug']}", ""]
        L.append(f"Diagram `{un['diagram']}` ({un.get('format', '')}, read {un.get('extraction', '')})"
                 + (", with text " + ", ".join(f"`{t}`" for t in un.get("texts", [])) if un.get("texts")
                    else ", with no text") + ".")
        L.append("")
        if un.get("status") == "needs-agent":
            L += ["This is a picture with no diagram inside it. Read the image "
                  f"`{un.get('gathered', '')}`, write its boxes, links and scenarios into "
                  f"`units/{un['slug']}/unit.json` as `references/unit-model.md` describes, "
                  "set `status` to `ready`, then run `convert.py draft` on this folder.", ""]
            continue
        c = un.get("classification", {})
        L += [f"Type: {un.get('type', '')} ({c.get('how', '')}).", ""]
        for reason in c.get("reasons", []):
            L.append(f"- {reason}")
        L.append("")
        if r.get("document"):
            L += [f"Document: `{r['document']}`, from the template {r.get('template', '')}.", ""]
        d = r.get("drafted")
        if d:
            L += [f"Drafted {d['boxes']} boxes, {d['links']} links and {d['scenarios']} "
                  f"scenario(s) of {d['steps']} steps.", ""]
        for n in r.get("notes", []):
            L.append(f"- {n}")
        if r.get("notes"):
            L.append("")
        v = r.get("verify")
        if v:
            val = v.get("validate", {})
            L.append(f"Validation: {val.get('result', '')}"
                     + (f", {val.get('summary')}" if val.get("summary") else "") + ".")
            for f in val.get("findings", [])[:30]:
                L.append(f"- {f.get('severity')} {f.get('where', '')}: {f.get('message')} [{f.get('rule')}]")
            L.append("")
            cmp_ = v.get("comparison", {})
            if cmp_.get("skipped"):
                L += [f"Comparison with the source: skipped, {cmp_['skipped']}.", ""]
            elif cmp_:
                b, lk, st = cmp_["boxes"], cmp_["links"], cmp_["steps"]
                L.append(f"Comparison with the source: {'agrees' if cmp_['agrees'] else 'differs'}. "
                         f"Boxes {b['source']} in the source, {b['document']} regenerated; links "
                         f"{lk['source']} and {lk['document']}; steps {st['source']} and {st['document']}.")
                for label, items in (("box only in the source", b["missing"]),
                                     ("box only in the document", b["extra"]),
                                     ("link only in the source", lk["missing"]),
                                     ("link only in the document", lk["extra"]),
                                     ("link reversed", lk["reversed"])):
                    for it in items:
                        L.append(f"- {label}: {it}")
                L.append("")
        unc = un.get("uncertain", [])
        if unc:
            L += ["To review, also listed in the document's conversion notes:", ""]
            L += [f"- {x}" for x in unc] + [""]
    sources = manifest.get("sources", [])
    if sources:
        L += ["## Sources", "", "| Original | Gathered | Archived to |", "|---|---|---|"]
        for e in sources:
            L.append(f"| `{e['original']}` | `{e.get('gathered', '')}` | "
                     f"{('`' + e['archive'] + '`') if e.get('archived') else (e.get('note') or 'not archived')} |")
        L.append("")
    for p in manifest.get("problems", []):
        L.append(f"- {p}")
    path = os.path.join(run_dir, "report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L).rstrip() + "\n")
    return path


def uncertain_list(u) -> list:
    out = []
    for b in u["boxes"]:
        if b.get("uncertain"):
            out.append(f"box {b['label']}: {b['uncertain']}")
    for lk in u["links"]:
        if lk.get("uncertain"):
            out.append(f"link {lk.get('label') or lk['key']}: {lk['uncertain']}")
    for sc in u["scenarios"]:
        for st in sc["steps"]:
            if st.get("uncertain"):
                out.append(f"{sc.get('name') or sc['key']} step {st['step']}: {st['uncertain']}")
    return out + list(u.get("notes", []))


# ------------------------------------------------------------------ commands

def plan(a, cwd):
    binding_file, table = convert_table(cwd)
    work = os.path.abspath(a.work) if a.work else ws.work_root(
        cwd, bound(binding_file, table.get("workDir")) if binding_file else "")
    archive_dir_bound = bound(binding_file, table.get("archiveDir")) if binding_file else ""

    def archive_dir_for(repo):
        return archive_dir_bound or os.path.join(repo, "archive")

    out = os.path.abspath(a.out) if a.out else ""
    files = ws.discover(a.paths, skip=[work, out, archive_dir_bound])
    units, unpaired = ws.pair(files)
    if not units:
        raise UsageError("no diagram (.drawio, .svg, .png, .jpg) found under "
                         + ", ".join(a.paths))
    if a.name and len(units) == 1:
        units[0]["name"] = a.name
    names = set()
    for u in units:
        base = slug(u["name"])
        s, n = base, 2
        while s in names:
            s = f"{base}-{n}"
            n += 1
        names.add(s)
        u["slug"] = s
    label = a.name or (os.path.basename(os.path.abspath(a.paths[0])) if len(a.paths) == 1 else "sources")
    run_dir = ws.new_run_dir(work, ws.stem(label))
    entries = ws.plan_sources(units, unpaired, archive_dir_for, archive=not a.no_archive)
    for e in entries:
        e["unit"] = next((u["slug"] for u in units if e["original"] in
                          [u["diagram"]] + u["alternates"] + u["texts"]), "")
    return run_dir, units, unpaired, entries


def cmd_run(a, cwd):
    run_dir, specs, unpaired, entries = plan(a, cwd)
    places = Places(a.out, cwd)
    manifest = {"date": datetime.date.today().isoformat(), "inputs": [os.path.abspath(p) for p in a.paths],
                "run": run_dir, "type": a.type or "", "out": os.path.abspath(a.out) if a.out else "",
                "sources": entries, "units": [], "problems": []}

    if a.dry_run:
        plan_out = {"run": run_dir, "units": [], "sources": entries,
                    "unpaired": unpaired}
        for spec in specs:
            units = read_unit_files(spec)
            whole = classify.classify(merged(units), a.type) if len(units) > 1 else None
            for u in units:
                c = (whole or classify.classify(u, a.type)) if u["extraction"] != "agent" else {
                    "type": classify.normalise(a.type) or "", "reasons": ["an image: the agent reads it"]}
                t = c["type"]
                entry = {"slug": spec["slug"], "diagram": spec["diagram"], "texts": spec["texts"],
                         "alternates": spec["alternates"], "extraction": u["extraction"],
                         "boxes": len(u["boxes"]), "links": len(u["links"]),
                         "scenarios": len(u["scenarios"]), "type": t, "reasons": c["reasons"][:1]}
                if t:
                    u["type"] = t
                    r = draft_unit(u, places, cwd, ident=a.id if len(specs) == 1 else None, dry_run=True)
                    entry["document"] = r["document"]
                plan_out["units"].append(entry)
        if a.json:
            print(json.dumps(plan_out, indent=2))
        else:
            print(f"  conversion folder  {run_dir}  (dry run: nothing written)")
            for un in plan_out["units"]:
                print(f"  unit {un['slug']}: {os.path.relpath(un['diagram'], cwd)}"
                      + (f" + {len(un['texts'])} text(s)" if un["texts"] else ", no text")
                      + f"; read {un['extraction']}, {un['boxes']} boxes, {un['links']} links, "
                      f"{un['scenarios']} scenario(s)")
                print(f"       type {un['type'] or '(the agent decides after reading the image)'}: "
                      f"{un['reasons'][0] if un['reasons'] else ''}")
                if un.get("document"):
                    print(f"       would write {os.path.relpath(un['document'], cwd)}")
            for e in entries:
                where = (f"git mv to {os.path.relpath(e['archive'], cwd)}" if e.get("archive")
                         else e.get("note") or "copied only (--no-archive)")
                print(f"  source {os.path.relpath(e['original'], cwd)}: {where}")
        return 0

    os.makedirs(run_dir)
    ws.gather(entries, run_dir)
    worst = 0
    for spec in specs:
        units = read_unit_files(spec)
        # The pages of one file are one body of material: their type is chosen together.
        whole = classify.classify(merged(units), a.type) if len(units) > 1 else None
        for i, u in enumerate(units):
            s = spec["slug"] if len(units) == 1 else f"{spec['slug']}-{slug(u.get('signals', {}).get('page') or str(i + 1))}"
            udir = os.path.join(run_dir, "units", s)
            os.makedirs(udir, exist_ok=True)
            gathered = next((e.get("gathered", "") for e in entries if e["original"] == spec["diagram"]), "")
            un = {"slug": s, "diagram": spec["diagram"], "texts": spec["texts"],
                  "alternates": spec["alternates"], "format": u["sources"]["format"],
                  "extraction": u["extraction"], "gathered": gathered}
            if u.get("drawio") and u["sources"]["format"] != "drawio":
                with open(os.path.join(udir, "source.drawio"), "w", encoding="utf-8") as fh:
                    fh.write(drawio.uncompressed(u["drawio"]))
            if u["extraction"] == "agent":
                if a.type:
                    u["type"] = classify.normalise(a.type)
                save_unit(udir, u)
                un["status"] = "needs-agent"
                un["candidate"] = write_candidate(u, spec, s, places, entries)
                manifest["units"].append(un)
                worst = 1
                continue
            save_json(os.path.join(udir, "source.json"), strip_private(u))
            c = whole or classify.classify(u, a.type)
            u["type"] = c["type"]
            u["classification"] = c
            u["status"] = "ready"
            un.update({"type": c["type"], "classification": c, "uncertain": uncertain_list(u)})
            # Where each source will be kept: its archive path, when it is archived.
            kept = {e["original"]: e.get("archive") or e["original"] for e in entries}
            u["sources"]["kept"] = [kept.get(p, p) for p in [spec["diagram"]] + spec["texts"]]
            res = run_draft(u, places, cwd, ident=a.id if len(specs) == 1 and len(units) == 1 else None)
            un["result"] = res
            if res.get("status") == "drafted":
                u["id"] = res["id"]
            save_unit(udir, u)
            un["status"] = res.get("status", "")
            if res.get("status") != "drafted" or res.get("verify", {}).get("validate", {}).get("result") == "error":
                worst = 1
            manifest["units"].append(un)
    if not a.no_archive:
        manifest["problems"] += ws.archive(entries)
    ws.write_manifest(run_dir, manifest)
    report = write_report(run_dir, manifest)
    summarise(manifest, report, a.json)
    return worst


def write_candidate(u, spec, unit_slug, places, entries) -> dict:
    """A placeholder document for a source that needs the agent, marked needs-conversion so
    the portfolio's tagging finds it. Removed by draft once the real document is written,
    if no one has changed it."""
    type_name = u.get("type", "")
    folder = os.path.join(places.folder(type_name or "architecture-pattern"), unit_slug)
    doc = os.path.join(folder, "index.md")
    if os.path.exists(doc):
        return {"path": doc, "written": False}
    kept = {e["original"]: e.get("archive") or e["original"] for e in entries}
    sources = [os.path.relpath(kept.get(p, p), folder).replace(os.sep, "/")
               for p in [spec["diagram"]] + spec["texts"]]
    text = draft.candidate(u, type_name, sources, "a picture with no diagram inside it, waiting "
                           "for the agent to read it and run convert.py draft",
                           datetime.date.today().isoformat())
    os.makedirs(folder, exist_ok=True)
    with open(doc, "w", encoding="utf-8") as fh:
        fh.write(text)
    return {"path": doc, "written": True, "sha256": ws.sha256(doc)}


def remove_candidate(un, res) -> None:
    """Remove the placeholder a run wrote, once the real document exists, unless edited."""
    c = un.get("candidate") or {}
    path = c.get("path")
    if not (c.get("written") and path and os.path.isfile(path)):
        return
    if ws.sha256(path) != c.get("sha256"):
        res["notes"].append(f"the placeholder {path} was edited, so it was left; remove it by hand")
        return
    os.unlink(path)
    try:
        os.rmdir(os.path.dirname(path))
    except OSError:
        pass
    res["notes"].append(f"the needs-conversion placeholder {path} was removed")
    c["written"] = False


def run_draft(u, places, cwd, ident=None, force=False) -> dict:
    try:
        res = draft_unit(u, places, cwd, force=force, ident=ident)
    except (ValueError, RuntimeError, UsageError) as ex:
        return {"status": "failed", "notes": [str(ex)], "type": u.get("type", "")}
    if res.get("status") == "drafted":
        res["verify"] = verify.check(res["document"], u)
    return res


def strip_private(u):
    v = copy.deepcopy(u)
    v.pop("drawio", None)
    return v


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def save_unit(udir, u):
    save_json(os.path.join(udir, "unit.json"), strip_private(u))


def summarise(manifest, report, as_json):
    if as_json:
        print(json.dumps({"run": manifest["run"], "report": report,
                          "units": [{k: un.get(k) for k in ("slug", "type", "status", "extraction")}
                                    | {"document": un.get("result", {}).get("document", ""),
                                       "valid": un.get("result", {}).get("verify", {}).get("validate", {}).get("result", ""),
                                       "agrees": un.get("result", {}).get("verify", {}).get("comparison", {}).get("agrees")}
                                    for un in manifest["units"]]}, indent=2))
        return
    print(f"  conversion folder  {manifest['run']}")
    for un in manifest["units"]:
        r = un.get("result", {})
        v = r.get("verify", {})
        cmp_ = v.get("comparison", {})
        agrees = "" if not cmp_ or cmp_.get("skipped") else (
            "; agrees with the source" if cmp_.get("agrees") else "; differs from the source")
        print(f"  {un.get('status', ''):<12} {un['slug']}: {un.get('type') or '?'}"
              + (f" {r.get('id', '')} -> {r.get('document', '')}" if r.get("document") else "")
              + (f"; validate {v['validate']['result']}" if v.get("validate") else "") + agrees)
    for e in manifest["sources"]:
        if e.get("archived"):
            print(f"  archived     {e['original']} -> {e['archive']}")
    for p in manifest.get("problems", []):
        print(f"  ! {p}")
    print(f"  report       {report}")


def cmd_draft(a, cwd):
    run_dir = os.path.abspath(a.folder)
    manifest = ws.read_manifest(run_dir)
    places = Places(manifest.get("out") or None, cwd)
    worst = 0
    for un in manifest["units"]:
        if a.unit and un["slug"] != a.unit:
            continue
        udir = os.path.join(run_dir, "units", un["slug"])
        with open(os.path.join(udir, "unit.json"), encoding="utf-8") as fh:
            u = json.load(fh)
        # A unit written from scratch by the agent says nothing of where it came from.
        src = u.setdefault("sources", {})
        if not src.get("diagram"):
            src.update({"diagram": un["diagram"], "text": list(un.get("texts", [])),
                        "format": un.get("format", "")})
        u.setdefault("extraction", un.get("extraction", ""))
        for problem in unit_mod.normalise(u):
            u.setdefault("notes", []).append(problem)
        if u.get("status") == "needs-agent":
            un["status"] = "needs-agent"
            worst = 1
            continue
        if not u.get("boxes"):
            un["status"] = "failed"
            un["result"] = {"status": "failed", "notes": ["unit.json has no boxes"]}
            worst = 1
            continue
        # The source drawing, when there is one, is adopted again.
        src = os.path.join(udir, "source.drawio")
        if os.path.isfile(src):
            with open(src, encoding="utf-8") as fh:
                u["drawio"] = fh.read()
        elif un.get("format") == "drawio" and os.path.isfile(un["diagram"]):
            with open(un["diagram"], encoding="utf-8") as fh:
                u["drawio"] = fh.read()
        elif un.get("format") == "drawio" and un.get("gathered"):
            with open(os.path.join(run_dir, un["gathered"]), encoding="utf-8") as fh:
                u["drawio"] = fh.read()
        if not u.get("type"):
            c = classify.classify(u, manifest.get("type", ""))
            u["type"], u["classification"] = c["type"], c
        else:
            u["type"] = classify.normalise(u["type"]) or u["type"]
            u.setdefault("classification", {"type": u["type"], "how": "set in unit.json",
                                            "reasons": ["the type is set in unit.json"]})
        if u["type"] not in draft.PROFILES:
            un["status"] = "failed"
            un["result"] = {"status": "failed", "notes": [f"unknown type {u['type']!r}"]}
            worst = 1
            continue
        source_path = os.path.join(udir, "source.json")
        if os.path.isfile(source_path):
            with open(source_path, encoding="utf-8") as fh:
                source_unit = json.load(fh)
        else:
            source_unit = None
        kept = {e["original"]: e["archive"] if e.get("archived") else e["original"]
                for e in manifest["sources"]}
        u["sources"]["kept"] = [kept.get(p, p) for p in [un["diagram"]] + un.get("texts", [])]
        try:
            res = draft_unit(u, places, cwd, force=a.force, ident=u.get("id") or None)
        except (ValueError, RuntimeError, UsageError) as ex:
            res = {"status": "failed", "notes": [str(ex)], "type": u["type"]}
        if res.get("status") == "drafted":
            res["verify"] = verify.check(res["document"], source_unit or u)
            remove_candidate(un, res)
        un.update({"type": u["type"], "classification": u["classification"], "result": res,
                   "status": res.get("status", ""), "extraction": u.get("extraction", ""),
                   "uncertain": uncertain_list(u)})
        u["id"] = res.get("id", u.get("id", ""))
        save_unit(udir, u)
        if res.get("status") != "drafted" or res.get("verify", {}).get("validate", {}).get("result") == "error":
            worst = 1
    ws.write_manifest(run_dir, manifest)
    report = write_report(run_dir, manifest)
    summarise(manifest, report, a.json)
    return worst


def cmd_read(a, cwd):
    spec = {"diagram": os.path.abspath(a.diagram), "texts": [os.path.abspath(t) for t in a.text or []],
            "alternates": [], "name": humanise(ws.stem(a.diagram))}
    units = read_unit_files(spec)
    for u in units:
        if u["extraction"] != "agent":
            u["classification"] = classify.classify(u)
    print(json.dumps([strip_private(u) for u in units], indent=2))
    return 0


def cmd_verify(a, cwd):
    source = None
    if a.source:
        with open(a.source, encoding="utf-8") as fh:
            source = json.load(fh)
    out = verify.check(a.document, source)
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        v = out["validate"]
        print(f"  validate {v.get('result')}: {v.get('summary', '')}")
        for f in v.get("findings", []):
            print(f"    {f.get('severity')} {f.get('where', '')}: {f.get('message')}")
        c = out.get("comparison", {})
        if c.get("skipped"):
            print(f"  comparison skipped: {c['skipped']}")
        elif c:
            print(f"  comparison: {'agrees' if c['agrees'] else 'differs'}")
            for k in ("missing", "extra"):
                for x in c["boxes"][k]:
                    print(f"    box {k}: {x}")
            for k in ("missing", "extra", "reversed"):
                for x in c["links"][k]:
                    print(f"    link {k}: {x}")
    bad = out["validate"].get("result") == "error" or out.get("comparison", {}).get("agrees") is False
    return 1 if bad else 0


def cmd_archive(a, cwd):
    run_dir = os.path.abspath(a.folder)
    manifest = ws.read_manifest(run_dir)
    binding_file, table = convert_table(cwd)
    archive_dir_bound = bound(binding_file, table.get("archiveDir")) if binding_file else ""
    for e in manifest["sources"]:
        if e.get("archived") or e["role"] == "unpaired" or not e.get("tracked"):
            continue
        if not os.path.exists(e["original"]):
            e["note"] = "no longer where it was; not archived"
            continue
        adir = archive_dir_bound or os.path.join(e["repository"], "archive")
        e["archive"] = ws.archive_target(e["original"], e["repository"], adir)
        if a.dry_run:
            print(f"  would git mv {e['original']} -> {e['archive']}")
    if a.dry_run:
        return 0
    manifest["problems"] = manifest.get("problems", []) + ws.archive(manifest["sources"])
    ws.write_manifest(run_dir, manifest)
    write_report(run_dir, manifest)
    for e in manifest["sources"]:
        if e.get("archived"):
            print(f"  archived {e['original']} -> {e['archive']}")
    for p in manifest["problems"]:
        print(f"  ! {p}")
    return 1 if manifest["problems"] else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="convert.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="gather, archive, read, classify, draft and check")
    r.add_argument("paths", nargs="+", help="files and folders holding the sources")
    r.add_argument("--type", help="the type of every unit, instead of choosing one")
    r.add_argument("--out", help="the folder the documents go in, instead of each type's outputDir")
    r.add_argument("--work", help="where the conversion folder is made, instead of workDir")
    r.add_argument("--name", help="the document's name, for a single unit")
    r.add_argument("--id", help="the document's identifier, for a single unit")
    r.add_argument("--no-archive", action="store_true", help="copy the sources, leave the originals")
    r.add_argument("--dry-run", action="store_true", help="print the plan; write and move nothing")
    r.add_argument("--json", action="store_true", help="print JSON instead of the summary")
    d = sub.add_parser("draft", help="draft again from each unit.json in a conversion folder")
    d.add_argument("folder")
    d.add_argument("--unit", help="only this unit")
    d.add_argument("--force", action="store_true", help="overwrite a document already drafted")
    d.add_argument("--json", action="store_true")
    rd = sub.add_parser("read", help="print the unit model read from one diagram")
    rd.add_argument("diagram")
    rd.add_argument("--text", action="append", help="a text that goes with it; repeatable")
    v = sub.add_parser("verify", help="validate a document and compare it with its source")
    v.add_argument("document")
    v.add_argument("--source", help="the unit's source.json, to compare against")
    v.add_argument("--json", action="store_true")
    ar = sub.add_parser("archive", help="archive the originals of a run made with --no-archive")
    ar.add_argument("folder")
    ar.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    cwd = os.getcwd()
    if a.cmd in ("run", "draft", "verify") and not skills.model_cli():
        print("  ! the model skill is not installed beside this one, on AGENT_SKILLS_PATH or "
              "in any agent skills directory: install it from "
              "https://github.com/dermot-obrien/diagram-model", file=sys.stderr)
        return 3
    if a.cmd in ("run", "draft") and not skills.pattern_script("register.py"):
        print("  ! the pattern skill is not installed beside this one or on AGENT_SKILLS_PATH: "
              "install it from https://github.com/dermot-obrien/architecture-pattern",
              file=sys.stderr)
        return 3
    try:
        return {"run": cmd_run, "draft": cmd_draft, "read": cmd_read, "verify": cmd_verify,
                "archive": cmd_archive}[a.cmd](a, cwd)
    except (UsageError, FileNotFoundError, drawio.DrawioError, svg.SvgError) as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
