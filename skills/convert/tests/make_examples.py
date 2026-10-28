#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Write the convert skill's example sources, every one generic.

    python tests/make_examples.py

Each example is the kind of material people already have: a diagram drawn by hand in
draw.io, exported as SVG or PNG, or drawn in another tool, with rich, sparse or no
Markdown beside it. The draw.io files are written as a person would leave them: shapes
with no identifiers, labels with markup, containers, a key, and arrows numbered for a
flow. Pictures are drawn with Pillow, which only this script needs; the tests read the
committed files.
"""
from __future__ import annotations

import base64
import html
import os
import shutil
import struct
import urllib.parse
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "examples", "sources")


# ------------------------------------------------------------------ draw.io by hand

BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
STORE = "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=12;fillColor=#fff2cc;strokeColor=#d6b656;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;"
LANE = "swimlane;whiteSpace=wrap;html=1;startSize=24;fillColor=none;dashed=1;"
TEXT = "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;"
TITLE = "text;html=1;strokeColor=none;fillColor=none;align=left;fontSize=20;fontStyle=1;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
ICON = "shape=mxgraph.cloud_platform.database;html=1;labelPosition=center;verticalLabelPosition=bottom;verticalAlign=top;"


class Drawing:
    def __init__(self, name="Page-1"):
        self.pages = []
        self.page(name)

    def page(self, name):
        self.cells = [('<mxCell id="0" />', None), ('<mxCell id="1" parent="0" />', None)]
        self.n = 0
        self.layer = "1"
        self.pages.append((name, self.cells))
        return self

    def add_layer(self, name):
        self.n += 1
        lid = f"L{self.n}"
        self.cells.append((f'<mxCell id="{lid}" value="{html.escape(name, quote=True)}" parent="0" />', None))
        self.layer = lid
        return lid

    def v(self, label, x, y, w=160, h=60, style=BOX, parent=None):
        self.n += 1
        cid = f"c{self.n}"
        self.cells.append((f'<mxCell id="{cid}" value="{html.escape(label, quote=True)}" style="{style}" '
                           f'vertex="1" parent="{parent or self.layer}"><mxGeometry x="{x}" y="{y}" '
                           f'width="{w}" height="{h}" as="geometry" /></mxCell>', None))
        return cid

    def e(self, src, tgt, label="", style=EDGE, parent=None, child_label=False, free_end=None):
        self.n += 1
        cid = f"e{self.n}"
        value = "" if child_label else html.escape(label, quote=True)
        ends = f' source="{src}"' + (f' target="{tgt}"' if tgt else "")
        geom = '<mxGeometry relative="1" as="geometry" />'
        if free_end:
            geom = (f'<mxGeometry relative="1" as="geometry"><mxPoint x="{free_end[0]}" '
                    f'y="{free_end[1]}" as="targetPoint" /></mxGeometry>')
        self.cells.append((f'<mxCell id="{cid}" value="{value}" style="{style}" edge="1" '
                           f'parent="{parent or self.layer}"{ends}>{geom}</mxCell>', None))
        if child_label:
            self.n += 1
            self.cells.append((f'<mxCell id="lbl{self.n}" value="{html.escape(label, quote=True)}" '
                               'style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;'
                               f'points=[];" vertex="1" connectable="0" parent="{cid}">'
                               '<mxGeometry x="-0.1" relative="1" as="geometry"><mxPoint as="offset" />'
                               '</mxGeometry></mxCell>', None))
        return cid

    def xml(self, compressed=False):
        out = ['<mxfile host="Electron" type="device" version="24.0.0">']
        for i, (name, cells) in enumerate(self.pages):
            model = ('<mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" '
                     'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" '
                     'pageHeight="827" math="0" shadow="0"><root>'
                     + "".join(c for c, _ in cells) + "</root></mxGraphModel>")
            if compressed:
                raw = urllib.parse.quote(model, safe="~()*!.'")
                comp = zlib.compressobj(9, zlib.DEFLATED, -15)
                data = comp.compress(raw.encode("utf-8")) + comp.flush()
                body = base64.b64encode(data).decode("ascii")
            else:
                body = model
            out.append(f'<diagram id="page{i + 1}" name="{html.escape(name, quote=True)}">{body}</diagram>')
        out.append("</mxfile>")
        return "\n".join(out) + "\n"


def write(rel, text, mode="w"):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({"encoding": "utf-8"} if mode == "w" else {})) as fh:
        fh.write(text)
    return path


# ------------------------------------------------------------------ plain SVG by hand

class Svg:
    def __init__(self, w, h):
        self.w, self.h, self.parts = w, h, []

    def rect(self, x, y, w, h, label, sub="", fill="#eef3fb", rx=8):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="#334"/>')
        cy = y + h / 2 + (0 if not sub else -6)
        self.parts.append(f'<text x="{x + w / 2}" y="{cy + 5}" text-anchor="middle" font-size="14" font-weight="bold">{html.escape(label)}</text>')
        if sub:
            self.parts.append(f'<text x="{x + w / 2}" y="{cy + 23}" text-anchor="middle" font-size="11">{html.escape(sub)}</text>')
        return (x, y, w, h)

    def person(self, x, y, label):
        self.parts.append(f'<g transform="translate({x},{y})"><circle cx="20" cy="12" r="10" fill="#fff" stroke="#334"/>'
                          '<path d="M20 22 L20 50 M4 32 L36 32 M20 50 L8 70 M20 50 L32 70" stroke="#334" fill="none"/>'
                          f'<rect x="-30" y="72" width="100" height="24" fill="#ffffff" stroke="none"/>'
                          f'<text x="20" y="88" text-anchor="middle" font-size="13">{html.escape(label)}</text></g>')
        return (x - 30, y + 72, 100, 24)

    def group(self, x, y, w, h, label):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#889" stroke-dasharray="6 4"/>'
                          f'<text x="{x + 10}" y="{y + 20}" font-size="13" font-weight="bold">{html.escape(label)}</text>')

    def arrow(self, a, b, label="", both=False, none=False):
        ax, ay = a[0] + a[2] / 2, a[1] + a[3] / 2
        bx, by = b[0] + b[2] / 2, b[1] + b[3] / 2

        def edge(box, tx, ty):
            x, y, w, h = box
            cx, cy = x + w / 2, y + h / 2
            dx, dy = tx - cx, ty - cy
            sx = (w / 2) / abs(dx) if dx else 1e9
            sy = (h / 2) / abs(dy) if dy else 1e9
            s = min(sx, sy)
            return cx + dx * s, cy + dy * s
        p, q = edge(a, bx, by), edge(b, ax, ay)
        marks = "" if none else ' marker-end="url(#a)"' + (' marker-start="url(#a)"' if both else "")
        self.parts.append(f'<path d="M{p[0]:.1f},{p[1]:.1f} L{q[0]:.1f},{q[1]:.1f}" stroke="#334" fill="none"{marks}/>')
        if label:
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            self.parts.append(f'<text x="{mx:.1f}" y="{my - 6:.1f}" text-anchor="middle" font-size="11">{html.escape(label)}</text>')

    def title(self, text):
        self.parts.append(f'<text x="20" y="34" font-size="22" font-weight="bold">{html.escape(text)}</text>')

    def text(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="Arial">'
                '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
                'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="#334"/></marker></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>' + "".join(self.parts) + "</svg>\n")


def drawio_svg(drawing, preview_svg):
    """An SVG as draw.io exports it with "include a copy of my diagram": the diagram in
    the root's content attribute, and the picture beside it."""
    content = html.escape(drawing.xml(compressed=True), quote=True)
    return preview_svg.replace("<svg ", f'<svg content="{content}" ', 1)


# ------------------------------------------------------------------ pictures

def picture(boxes, arrows, size, title="", people=()):
    """A PNG of boxes and arrows, drawn with Pillow."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", size, "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
        bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except OSError:
        font = bold = big = ImageFont.load_default()
    if title:
        d.text((20, 14), title, fill="black", font=big)
    centre = {}
    for name, (x, y, w, h) in boxes.items():
        if name in people:
            cx = x + w / 2
            d.ellipse([cx - 12, y, cx + 12, y + 24], outline="black", width=2)
            d.line([cx, y + 24, cx, y + 56], fill="black", width=2)
            d.line([cx - 18, y + 36, cx + 18, y + 36], fill="black", width=2)
            d.line([cx, y + 56, cx - 14, y + 78], fill="black", width=2)
            d.line([cx, y + 56, cx + 14, y + 78], fill="black", width=2)
            tw = d.textlength(name, font=bold)
            d.text((cx - tw / 2, y + 82), name, fill="black", font=bold)
        else:
            d.rounded_rectangle([x, y, x + w, y + h], radius=10, outline="#334455", width=2, fill="#eef3fb")
            tw = d.textlength(name, font=bold)
            d.text((x + (w - tw) / 2, y + h / 2 - 9), name, fill="black", font=bold)
        centre[name] = (x, y, w, h)
    import math
    for a, b, label in arrows:
        ax, ay, aw, ah = centre[a]
        bx, by, bw, bh = centre[b]
        p = (ax + aw / 2, ay + ah / 2)
        q = (bx + bw / 2, by + bh / 2)

        def clip(box, toward):
            x, y, w, h = box
            cx, cy = x + w / 2, y + h / 2
            dx, dy = toward[0] - cx, toward[1] - cy
            s = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
            return cx + dx * s, cy + dy * s
        p2, q2 = clip(centre[a], q), clip(centre[b], p)
        d.line([p2, q2], fill="#334455", width=2)
        ang = math.atan2(q2[1] - p2[1], q2[0] - p2[0])
        for da in (2.6, -2.6):
            d.line([q2, (q2[0] + 12 * math.cos(ang + da), q2[1] + 12 * math.sin(ang + da))], fill="#334455", width=2)
        if label:
            mx, my = (p2[0] + q2[0]) / 2, (p2[1] + q2[1]) / 2
            tw = d.textlength(label, font=font)
            d.rectangle([mx - tw / 2 - 3, my - 20, mx + tw / 2 + 3, my - 2], fill="white")
            d.text((mx - tw / 2, my - 19), label, fill="black", font=font)
    import io
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def png_with_drawio(png, drawing):
    """A PNG with the diagram in a tEXt chunk keyed mxfile, as draw.io's export writes it."""
    payload = urllib.parse.quote(drawing.xml(compressed=True), safe="")
    body = b"mxfile\x00" + payload.encode("latin-1")
    chunk = struct.pack(">I", len(body)) + b"tEXt" + body
    chunk += struct.pack(">I", zlib.crc32(b"tEXt" + body) & 0xFFFFFFFF)
    return png[:33] + chunk + png[33:]


# ------------------------------------------------------------------ the examples

def order_intake():
    """Architecture pattern: a hand-drawn draw.io, logical services, rich text."""
    g = Drawing("Order intake")
    g.v("Order Intake", 40, 10, 400, 30, TITLE)
    ch = g.v("<b>Sales Channel</b><br>web and mobile front ends", 40, 80, 170, 70)
    lane = g.v("Order domain", 280, 60, 460, 300, LANE)
    api = g.v("<b>Order API</b>", 30, 40, 160, 60, BOX, parent=lane)
    svc = g.v("<b>Order Service</b><br>validates and prices the order", 250, 40, 180, 70, BOX, parent=lane)
    store = g.v("Order Store", 270, 190, 140, 80, STORE, parent=lane)
    pay = g.v("<b>Payment Gateway</b>", 820, 90, 170, 60)
    broker = g.v("Event Broker", 820, 260, 170, 60)
    notify = g.v("Notification Service", 820, 400, 170, 60)
    g.e(ch, api, "1. submit order")
    g.e(api, svc, "2. create order")
    g.e(svc, pay, "3. authorise payment")
    g.e(svc, store, "4. persist order")
    g.e(svc, broker, "5. publish order placed")
    g.e(broker, notify, "6. deliver event", child_label=True)
    key = g.v("Key", 40, 420, 220, 120, LANE)
    g.v("Blue: service", 10, 30, 180, 30, TEXT, parent=key)
    g.v("Yellow: data store", 10, 60, 180, 30, TEXT, parent=key)
    write("order-intake/order-intake.drawio", g.xml())
    write("order-intake/order-intake.md", """# Order intake

A customer's order is taken from any sales channel, checked and priced once, paid for, recorded and announced to the rest of the business. The pattern keeps pricing and validation in one place so that every channel gives the same answer.

## Building blocks

| Component | Responsibility |
|---|---|
| Sales Channel | Collects the order from the customer, on the web or on a phone |
| Order API | The single entry point for orders from every channel |
| Order Service | Validates, prices and owns the order through its life |
| Payment Gateway | Authorises the payment with the payment provider |
| Order Store | Holds every order and its state |
| Event Broker | Carries business events to whoever subscribes |
| Notification Service | Tells the customer what happened |

## Flow

1. The Sales Channel submits the order to the Order API.
2. The Order API asks the Order Service to create the order.
3. The Order Service asks the Payment Gateway to authorise the payment.
4. The Order Service writes the order to the Order Store.
5. The Order Service publishes an order placed event to the Event Broker.
6. The Event Broker delivers the event to the Notification Service.

## Constraints

Payment details never reach the Order Store. Orders are idempotent on the channel's own reference.
""")


def edge_gateway():
    """Reference architecture: a draw.io-exported SVG, products with versions, sparse text."""
    g = Drawing("Edge gateway")
    cl = g.v("Container cluster 1.29", 260, 40, 520, 340, LANE)
    ing = g.v("Ingress controller 1.9", 30, 50, 180, 60, BOX, parent=cl)
    gw = g.v("API gateway 3.4", 300, 50, 180, 60, BOX, parent=cl)
    idp = g.v("Identity server 24", 30, 220, 180, 60, BOX, parent=cl)
    cache = g.v("In-memory cache 7.2", 300, 220, 180, 60, BOX, parent=cl)
    lb = g.v("Load balancer", 40, 90, 160, 60)
    db = g.v("Relational database 16", 860, 260, 170, 80, ICON)
    g.e(lb, ing, "HTTPS")
    g.e(ing, gw, "route request")
    g.e(gw, idp, "validate token")
    g.e(gw, cache, "read rate limits")
    g.e(gw, db, "query configuration")
    svg = Svg(1080, 420)
    a = svg.rect(40, 90, 160, 60, "Load balancer")
    svg.group(260, 40, 520, 340, "Container cluster 1.29")
    b = svg.rect(290, 90, 180, 60, "Ingress controller 1.9")
    c = svg.rect(560, 90, 180, 60, "API gateway 3.4")
    d = svg.rect(290, 260, 180, 60, "Identity server 24")
    e = svg.rect(560, 260, 180, 60, "In-memory cache 7.2")
    f = svg.rect(860, 260, 170, 80, "Relational database 16")
    for s, t, lb_ in ((a, b, "HTTPS"), (b, c, "route request"), (c, d, "validate token"),
                      (c, e, "read rate limits"), (c, f, "query configuration")):
        svg.arrow(s, t, lb_)
    write("edge-gateway/edge-gateway.drawio.svg", drawio_svg(g, svg.text()))
    write("edge-gateway/notes.md", """# Edge gateway

How requests from outside reach the services, as deployed on the shared container cluster.
""")


def claims_portal():
    """Use case: a plain SVG from another drawing tool, actors and goals, rich text."""
    s = Svg(1100, 520)
    s.title("Submit a claim")
    claimant = s.person(70, 120, "Claimant")
    portal = s.rect(260, 140, 200, 70, "Claims Portal", "where claims are made")
    intake = s.rect(560, 140, 200, 70, "Claims Service", "checks and records")
    policy = s.rect(860, 60, 200, 70, "Policy Register")
    docs = s.rect(860, 240, 200, 70, "Document Store")
    handler = s.person(620, 360, "Claims Handler")
    s.arrow(claimant, portal, "submit claim")
    s.arrow(portal, intake, "create claim")
    s.arrow(intake, policy, "check cover")
    s.arrow(intake, docs, "store evidence")
    s.arrow(intake, handler, "assign for review")
    write("claims-portal/claims-portal.svg", s.text())
    write("claims-portal/README.md", """# Submit a claim

As a claimant I want to submit a claim online, with my evidence, so that I am paid quickly and know where my claim stands. The goal is a decision within five working days.

## Actors

- Claimant: the policy holder making the claim
- Claims Handler: reviews the claim and decides it

## Main flow

1. The Claimant submits the claim and evidence through the Claims Portal.
2. The Claims Portal sends the claim to the Claims Service.
3. The Claims Service checks the cover with the Policy Register.
4. The Claims Service stores the evidence in the Document Store.
5. The Claims Service assigns the claim to a Claims Handler for review.

## Out of scope

Payment of an approved claim, which is another use case.
""")


def incident_handover():
    """Collaboration: a picture with no diagram inside it, sparse text."""
    boxes = {"Night Operations": (40, 120, 200, 70), "Day Operations": (600, 120, 200, 70),
             "Shift Log": (320, 300, 200, 70), "Duty Manager": (320, 20, 200, 70)}
    arrows = [("Night Operations", "Shift Log", "record open incidents"),
              ("Night Operations", "Day Operations", "brief at handover"),
              ("Day Operations", "Shift Log", "accept incidents"),
              ("Day Operations", "Duty Manager", "escalate breaches")]
    png = picture(boxes, arrows, (860, 420), "Incident handover")
    write("incident-handover/incident-handover.png", png, "wb")
    write("incident-handover/incident-handover.md", """# Incident handover

The handover between the night and day operations teams, so no open incident is dropped.
""")


def document_search():
    """Architecture pattern: a plain SVG with no text beside it."""
    s = Svg(980, 360)
    q = s.rect(40, 140, 170, 60, "Search Interface")
    r = s.rect(300, 140, 170, 60, "Query Service")
    i = s.rect(560, 60, 170, 60, "Index Store")
    p = s.rect(560, 230, 170, 60, "Permission Service")
    c = s.rect(800, 60, 150, 60, "Content Crawler")
    s.arrow(q, r, "search")
    s.arrow(r, i, "match terms")
    s.arrow(r, p, "filter by access")
    s.arrow(c, i, "add documents")
    write("document-search/document-search.svg", s.text())


def event_pipeline():
    """Reference architecture: a compressed draw.io with two pages and no text."""
    g = Drawing("Ingest")
    src = g.v("Device fleet", 40, 120, 150, 60)
    q = g.v("Message queue cluster 3.7", 260, 120, 190, 60)
    proc = g.v("Stream processing runtime 1.18", 520, 120, 210, 60)
    lake = g.v("Object storage bucket", 800, 40, 180, 60)
    wh = g.v("Analytical database 24", 800, 200, 180, 60)
    g.e(src, q, "publish telemetry")
    g.e(q, proc, "consume")
    g.e(proc, lake, "archive raw events")
    g.e(proc, wh, "load aggregates")
    g.page("Serve")
    wh2 = g.v("Analytical database 24", 40, 100, 180, 60)
    api = g.v("Query API server", 320, 100, 180, 60)
    dash = g.v("Dashboard application", 600, 100, 190, 60)
    g.e(api, wh2, "run query")
    g.e(dash, api, "request figures")
    write("event-pipeline/event-pipeline.drawio", g.xml(compressed=True))


def supplier_onboarding():
    """Collaboration: draw.io with swimlanes per party and a mermaid sequence in the text."""
    g = Drawing("Supplier onboarding")
    buyer = g.v("Buying team", 40, 60, 170, 70)
    risk = g.v("Risk review board", 320, 60, 180, 70)
    finance = g.v("Finance office", 620, 60, 170, 70)
    supplier = g.v("Supplier", 40, 260, 170, 70, ACTOR.replace("verticalLabelPosition=bottom;", "verticalLabelPosition=bottom;") )
    portal = g.v("Supplier portal", 320, 260, 180, 70)
    g.e(supplier, portal, "submit company details")
    g.e(portal, buyer, "notify of new supplier")
    g.e(buyer, risk, "request due diligence")
    g.e(risk, buyer, "approve or reject")
    g.e(buyer, finance, "set up payment terms")
    g.e(finance, supplier, "confirm account", free_end=None)
    write("supplier-onboarding/supplier-onboarding.drawio", g.xml())
    write("supplier-onboarding/supplier-onboarding.md", """# Supplier onboarding

How the buying team, the risk review board and the finance office work together to bring on a new supplier, with the supplier taking part through the portal. Each party owns one decision and hands the case on.

## Who takes part

| Participant | What they do | Kind |
|---|---|---|
| Supplier | Provides company, bank and insurance details | external |
| Supplier portal | Collects the details and tracks the case | system |
| Buying team | Sponsors the supplier and owns the case | team |
| Risk review board | Decides whether the supplier passes due diligence | board |
| Finance office | Sets up payment terms and the supplier account | team |

## Sequence

```mermaid
sequenceDiagram
    participant S as Supplier
    participant P as Supplier portal
    participant B as Buying team
    participant R as Risk review board
    participant F as Finance office
    S->>P: submit company details
    P->>B: notify of new supplier
    B->>R: request due diligence
    R->>B: approve the supplier
    B->>F: set up payment terms
    F->>S: confirm the account is open
```

## Agreements

The risk review board answers within ten working days. The buying team tells the supplier of a rejection.
""")


def appointment_booking():
    """Use case: a PNG draw.io exported with the diagram inside it, sparse text."""
    g = Drawing("Book an appointment")
    patient = g.v("Patient", 40, 120, 40, 80, ACTOR)
    app = g.v("Booking app", 200, 120, 170, 60)
    sched = g.v("Scheduling Service", 470, 120, 180, 60)
    cal = g.v("Clinic calendar", 760, 40, 170, 60)
    rem = g.v("Reminder Service", 760, 220, 170, 60)
    g.e(patient, app, "1. choose a time")
    g.e(app, sched, "2. request the slot")
    g.e(sched, cal, "3. hold the slot")
    g.e(sched, rem, "4. schedule a reminder")
    g.e(rem, patient, "5. send the reminder")
    boxes = {"Patient": (40, 120, 90, 100), "Booking app": (200, 120, 170, 60),
             "Scheduling Service": (470, 120, 180, 60), "Clinic calendar": (760, 40, 170, 60),
             "Reminder Service": (760, 220, 170, 60)}
    arrows = [("Patient", "Booking app", "1. choose a time"),
              ("Booking app", "Scheduling Service", "2. request the slot"),
              ("Scheduling Service", "Clinic calendar", "3. hold the slot"),
              ("Scheduling Service", "Reminder Service", "4. schedule a reminder"),
              ("Reminder Service", "Patient", "5. send the reminder")]
    png = picture(boxes, arrows, (980, 320), people=("Patient",))
    write("appointment-booking/appointment-booking.drawio.png", png_with_drawio(png, g), "wb")
    write("appointment-booking/appointment-booking.md", """# Book an appointment

A patient wants to book a visit at a time that suits them, so that they are seen without phoning the clinic.
""")


def release_approval():
    """Collaboration: a picture alone, with no text at all."""
    boxes = {"Product owner": (40, 60, 190, 70), "Change board": (360, 60, 190, 70),
             "Release team": (680, 60, 190, 70), "Service desk": (360, 260, 190, 70)}
    arrows = [("Product owner", "Change board", "request release"),
              ("Change board", "Release team", "approve window"),
              ("Release team", "Service desk", "announce change")]
    write("release-approval/release-approval.png",
          picture(boxes, arrows, (920, 380), "Release approval"), "wb")


def platform_folder():
    """A folder of several patterns: three diagrams, each with its own text by stem."""
    g = Drawing("Cache aside")
    app = g.v("Application", 40, 100, 160, 60)
    cache = g.v("Cache", 320, 30, 160, 60)
    store = g.v("Primary Store", 320, 180, 160, 60)
    g.e(app, cache, "1. read item")
    g.e(app, store, "2. read on a miss")
    g.e(app, cache, "3. write item back")
    write("platform/cache-aside.drawio", g.xml())
    write("platform/cache-aside.md", """# Cache aside

The application reads through a cache it manages itself, so the primary store is read only on a miss.

- Application: owns the read path and fills the cache
- Cache: holds recently read items for a short time
- Primary Store: the system of record
""")
    g = Drawing("Outbox")
    svc = g.v("Business Service", 40, 100, 170, 60)
    db = g.v("Service Database", 320, 30, 170, 60)
    relay = g.v("Outbox Relay", 320, 180, 170, 60)
    broker = g.v("Event Broker", 600, 180, 170, 60)
    g.e(svc, db, "write state and event in one transaction")
    g.e(relay, db, "poll outbox")
    g.e(relay, broker, "publish event")
    write("platform/outbox.drawio", g.xml())
    write("platform/outbox.md", """# Transactional outbox

Publish an event exactly when the state change that caused it commits.

## Steps

1. The Business Service writes its state and the event to the Service Database.
2. The Outbox Relay polls the Service Database for new events.
3. The Outbox Relay publishes each event to the Event Broker.
""")
    s = Svg(820, 300)
    a = s.rect(40, 110, 170, 60, "Client")
    b = s.rect(320, 110, 170, 60, "Circuit Breaker")
    c = s.rect(600, 110, 170, 60, "Remote Service")
    s.arrow(a, b, "call")
    s.arrow(b, c, "forward when closed")
    write("platform/circuit-breaker.svg", s.text())


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for f in (order_intake, edge_gateway, claims_portal, incident_handover, document_search,
              event_pipeline, supplier_onboarding, appointment_booking, release_approval,
              platform_folder):
        f()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
