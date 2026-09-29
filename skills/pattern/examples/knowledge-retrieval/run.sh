#!/usr/bin/env sh
# SPDX-License-Identifier: Apache-2.0
# Reproduce every output in this folder from index.md. Run from this directory.
set -e
# model and markdown-deck are their own repositories; point MODEL and MARKDOWN_DECK at
# their CLIs if they are not installed beside this skill.
MODEL=${MODEL:-../../../model/bin/model.py}
DECK=${MARKDOWN_DECK:-../../../markdown-deck/bin/markdown-deck.mjs}

echo "1. the document is the model"
python "$MODEL" extract index.md --format json --out model.json

echo "2. generate the diagram (first time only; use sync afterwards)"
[ -f components.drawio ] || python "$MODEL" emit index.md --to drawio --out components.drawio

echo "3. reconcile, keeping whatever layout the author has given it"
python "$MODEL" sync index.md components.drawio

echo "4. check the document and the diagram agree"
python "$MODEL" validate index.md --against components.drawio

echo "5. render the structure view and animate the scenarios over it"
python "$MODEL" render components.drawio --out components.svg --layer Structure
python "$MODEL" animate index.md

echo "6. publish the deck"
node "$DECK" build index.md --out dist --theme default --eyebrow "PAT-900 Knowledge Retrieval"
node "$DECK" pdf dist/deck.html --out dist/deck.pdf
