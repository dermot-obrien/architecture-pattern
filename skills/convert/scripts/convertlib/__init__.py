# SPDX-License-Identifier: Apache-2.0
"""The convert skill's library: read a diagram and its text, choose a pattern type, draft
the document, and check what was drafted against the source.

A unit is one diagram and the Markdown that goes with it. Every reader produces the same
unit model, a plain dict that is written to the conversion folder as JSON, so the agent
can read it, correct it, or write one by hand from an image and draft from that.
"""
