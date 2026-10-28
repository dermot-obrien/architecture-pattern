# SPDX-License-Identifier: Apache-2.0
"""Choose the pattern type a unit converts to, and say why.

    architecture-pattern     the boxes are capabilities, services or logical containers:
                             ABB identifiers, words such as service, capability,
                             component, layer, store, gateway, engine
    reference-architecture   the boxes name products and technologies: SBB identifiers,
                             version numbers, icons from a technology shape library, and
                             words such as database, cluster, queue, bucket, server, runtime
    use-case                 actors and their goals: actor shapes, words such as actor,
                             user, customer, goal, wants to, so that, use case
    collaboration            participants working together, otherwise: people, teams,
                             roles and boards, handovers, meetings and reviews

Each type scores the evidence for it; the highest score wins when it is clear of the
rest, and collaboration wins otherwise. A type the source declares, in front matter
pattern_type or document_type, or that the caller passes with --type, is taken as given.
The reasons are kept for the conversion report.
"""
from __future__ import annotations

import re

TYPES = ("architecture-pattern", "reference-architecture", "use-case", "collaboration")
ALIASES = {"ap": "architecture-pattern", "pattern": "architecture-pattern",
           "architecture-pattern": "architecture-pattern",
           "ra": "reference-architecture", "reference-architecture": "reference-architecture",
           "uc": "use-case", "use-case": "use-case", "usecase": "use-case",
           "co": "collaboration", "cl": "collaboration", "collaboration": "collaboration"}

LOGICAL = r"\b(service|services|capability|capabilities|component|components|layer|logical|store|registry|gateway|engine|manager|broker|adapter|orchestrator|repository|catalogue|catalog|pipeline|module|function|building block|abb|pattern|interface|boundary|cache|application|client|relay|breaker|proxy|scheduler|processor|worker|consumer|producer|publisher|subscriber|index|portal|channel|api|queue|log)\b"
PHYSICAL = (r"\b(database|db|cluster|queue|topic|bucket|server|servers|vm|virtual machine|runtime|"
            r"container image|container platform|object storage|block storage|relational|nosql|sql|"
            r"in-memory|cache cluster|load balancer|firewall|subnet|network|cdn|ingress|appliance|"
            r"saas|paas|iaas|hosted|managed service|serverless function|sbb|product|version|edition|"
            r"operating system|host|hosts|node pool|replica|replicas)\b")
ACTOR = r"\b(actor|user|users|customer|customers|end user|citizen|patient|member|claimant|applicant|persona|visitor|student|employee)\b"
GOAL = r"\b(as an? \w+,? i want|i want to|wants to|so that|goal|goals|use case|user journey|observable result)\b"
PEOPLE = (r"\b(team|teams|lead|leads|manager|managers|owner|owners|board|committee|office|department|"
          r"group|forum|council|reviewer|reviewers|approver|steward|analyst|architect|engineer|"
          r"handover|hand over|meeting|review|reviews|workshop|agree|agrees|collaborat\w*|coordinat\w*|"
          r"escalat\w*|sign off|sign-off|raci|stakeholder|stakeholders|partner|partners|supplier|suppliers)\b")
VERSION = re.compile(r"\b[vV]?[0-9]+\.[0-9]+(\.[0-9]+)?\b")
# draw.io's own generic libraries; a shape from any other library is a technology icon.
GENERIC_LIBRARIES = ("basic", "flowchart", "general", "arrows", "arrows2", "bpmn", "archimate",
                     "archimate3", "uml", "er", "mockup", "lean_mapping", "sysml", "c4")
VENDOR_SHAPE = re.compile(r"shape=mxgraph\.(?!(" + "|".join(GENERIC_LIBRARIES) + r")\b)[a-z0-9_]+", re.I)


def normalise(t: str) -> str:
    return ALIASES.get((t or "").strip().lower().replace(" ", "-").replace("_", "-"), "")


def _count(pattern, texts) -> int:
    rx = re.compile(pattern, re.I)
    return sum(len(rx.findall(t or "")) for t in texts)


def classify(u, forced="") -> dict:
    """{type, reasons, scores, how} for the unit."""
    if forced:
        t = normalise(forced)
        return {"type": t, "how": "given", "scores": {},
                "reasons": [f"--type {forced} was given"]}
    declared = normalise(u.get("signals", {}).get("declared_type", ""))
    if declared:
        return {"type": declared, "how": "declared", "scores": {},
                "reasons": [f"the source declares {u['signals']['declared_type']!r}"]}

    labels = [b["label"] for b in u["boxes"]] + [b.get("description", "") for b in u["boxes"]]
    texts = list(u.get("signals", {}).get("words", [])) + [u.get("summary", "")]
    styles = u.get("signals", {}).get("styles", [])
    ids = [b.get("id", "") for b in u["boxes"]]
    kinds = [b.get("kind", "") for b in u["boxes"]]
    n = max(len(u["boxes"]), 1)

    score = {t: 0.0 for t in TYPES}
    why = {t: [] for t in TYPES}

    def add(t, pts, reason):
        if pts:
            score[t] += pts
            why[t].append(reason)

    def share(pattern, texts_by_box):
        """How many boxes have a word matching the pattern in their label or description."""
        rx = re.compile(pattern, re.I)
        return sum(1 for t in texts_by_box if rx.search(t or ""))

    names = [b["label"] for b in u["boxes"]]

    abb = sum(1 for i in ids if i.startswith("ABB-"))
    sbb = sum(1 for i in ids if i.startswith("SBB-"))
    add("architecture-pattern", 4 * abb / n, f"{abb} box(es) carry ABB identifiers")
    add("reference-architecture", 4 * sbb / n, f"{sbb} box(es) carry SBB identifiers")

    # A box named for a technology is physical, whatever else its name says.
    is_physical = [bool(re.search(PHYSICAL, t or "", re.I) or VERSION.search(t or "")) for t in names]
    physical = sum(is_physical)
    logical = share(LOGICAL, [t for t, p in zip(names, is_physical) if not p])
    add("architecture-pattern", 4 * logical / n,
        f"{logical} of {n} box names are logical building blocks (service, store, gateway...)")
    add("reference-architecture", 4.5 * physical / n,
        f"{physical} of {n} box names are technologies or carry a version number")
    vendor = sum(1 for s in styles if VENDOR_SHAPE.search(s or ""))
    add("reference-architecture", 3 * min(vendor / n, 1),
        f"{vendor} box(es) drawn with an icon from a technology shape library")

    actor_shapes = sum(1 for s in styles if "umlActor" in (s or "")) + kinds.count("actor")
    goals = _count(GOAL, texts + labels)
    actor_names = share(ACTOR, names)
    add("use-case", 1.5 * min(actor_shapes, 2), f"{actor_shapes} actor shape(s) or actor kind(s)")
    add("use-case", 1.0 * min(goals, 4), f"{goals} statement(s) of a goal (as a, I want, so that, goal...)")
    add("use-case", 0.5 * min(actor_names, 3), f"{actor_names} box(es) named for a user")

    people = share(PEOPLE, names)
    people_text = _count(PEOPLE, texts)
    add("collaboration", 4 * people / n,
        f"{people} of {n} box names are people, teams, boards or offices")
    add("collaboration", 0.3 * min(people_text, 8),
        f"{people_text} collaboration word(s) in the text (handover, review, agree...)")

    # The text's own words, beyond the labels.
    add("architecture-pattern", 0.5 * min(_count(r"\b(architecture pattern|pattern|logical|technology[- ]agnostic|building blocks?)\b", texts), 4),
        "the text speaks of a pattern, logical design or building blocks")
    add("reference-architecture", 0.5 * min(_count(r"\b(reference architecture|technology[- ]specific|deploy\w*|hosted|platform|products?|versions?)\b", texts), 4),
        "the text speaks of a reference architecture, deployment or products")

    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    best, top = ranked[0]
    runner = ranked[1][1]
    reasons = [f"{t}: {s:.1f} ({'; '.join(why[t]) or 'no evidence'})" for t, s in ranked]
    if top < 2 or top - runner < 0.75:
        chosen = "collaboration"
        if best != "collaboration":
            reasons.insert(0, f"no type was clearly ahead ({best} {top:.1f}, next {runner:.1f}), "
                              "so collaboration, the type with the lightest rules")
        else:
            reasons.insert(0, "collaboration scored highest, or nothing else was clear")
    else:
        chosen = best
        reasons.insert(0, f"{best} scored {top:.1f}, clear of {ranked[1][0]} at {runner:.1f}")
    return {"type": chosen, "how": "chosen", "scores": {t: round(s, 2) for t, s in score.items()},
            "reasons": reasons}
