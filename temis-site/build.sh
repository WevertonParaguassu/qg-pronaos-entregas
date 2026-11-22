#!/usr/bin/env bash
# Render (static site temis-os): desempacota o snapshot estático do site público da Têmis em ./out
set -euo pipefail
rm -rf out && mkdir -p out
base64 -d temis-site/site.tgz.b64 | tar xz -C out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
