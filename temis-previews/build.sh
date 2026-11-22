#!/usr/bin/env bash
# Render (static site temis-previews): desempacota prévias de teste. NÃO é o site oficial temis-os.
set -euo pipefail
rm -rf out && mkdir -p out
base64 -d temis-previews/site.tgz.b64 | tar xz -C out
test -f out/index.html && test -f out/v1/planos/index.html && test -f out/v4/planos/index.html
echo "[temis-previews] ok: $(find out -type f | wc -l) arquivos"
