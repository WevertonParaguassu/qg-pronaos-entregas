#!/usr/bin/env bash
# Render (static site temis-previews): desempacota prévias de teste. NÃO é o site oficial temis-os.
set -euo pipefail
rm -rf out && mkdir -p out
cat temis-previews/site.tgz.b64.part1 temis-previews/site.tgz.b64.part2 | base64 -d | tar xz -C out
test -f out/index.html && test -f out/v1/planos/index.html && test -f out/v5/planos/index.html
echo "[temis-previews] ok: $(find out -type f | wc -l) arquivos"
