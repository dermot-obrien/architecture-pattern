# SPDX-License-Identifier: Apache-2.0
"""Images: a PNG draw.io exported with the diagram inside it, or a picture to read by eye.

draw.io's PNG export can include a copy of the diagram, in a text chunk keyed `mxfile`.
When it is there, the image is read as that draw.io diagram. Otherwise there is no
structure to parse: the unit is left for the agent, who reads the image, writes the
boxes, links and scenarios into the unit file, and drafts from it.
"""
from __future__ import annotations

import struct
import urllib.parse
import zlib

from .unit import new_unit

PNG = b"\x89PNG\r\n\x1a\n"


def png_info(data: bytes) -> dict:
    """{width, height, mxfile} of a PNG; mxfile is the embedded draw.io text, or ""."""
    if data[:8] != PNG:
        return {}
    w, h = struct.unpack(">II", data[16:24])
    i, embedded = 8, ""
    while i + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[i:i + 8])
        body = data[i + 8:i + 8 + length]
        i += 12 + length
        try:
            if kind == b"tEXt":
                key, _, value = body.partition(b"\x00")
                if key == b"mxfile":
                    embedded = urllib.parse.unquote(value.decode("latin-1"))
            elif kind == b"zTXt":
                key, _, rest = body.partition(b"\x00")
                if key == b"mxfile":
                    embedded = urllib.parse.unquote(zlib.decompress(rest[1:]).decode("utf-8"))
            elif kind == b"iTXt":
                key, _, rest = body.partition(b"\x00")
                if key == b"mxfile":
                    flag = rest[0]
                    rest = rest[2:]
                    _lang, _, rest = rest.partition(b"\x00")
                    _tkey, _, text = rest.partition(b"\x00")
                    raw = zlib.decompress(text) if flag else text
                    embedded = urllib.parse.unquote(raw.decode("utf-8"))
        except (zlib.error, UnicodeDecodeError, IndexError):
            pass
        if kind == b"IEND":
            break
    return {"width": w, "height": h, "mxfile": embedded}


def image_size(data: bytes) -> tuple:
    if data[:8] == PNG:
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":                       # JPEG: find the frame header
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + length
    return 0, 0


def for_agent(path, name, data) -> dict:
    """An empty unit that says what the agent is to read from the picture."""
    u = new_unit(name=name, diagram=path, fmt="png" if data[:8] == PNG else "image")
    u["extraction"] = "agent"
    w, h = image_size(data)
    u["image"] = {"width": w, "height": h}
    u["status"] = "needs-agent"
    u["notes"].append("an image with no diagram inside it: read it, then write the boxes, "
                      "links and scenarios here")
    return u
