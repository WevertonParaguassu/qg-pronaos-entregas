#!/usr/bin/env bash
# Render (static site temis-previews): desempacota prévias de teste. NÃO é o site oficial temis-os.
set -euo pipefail
rm -rf out && mkdir -p out
cat temis-previews/site.tgz.b64.b1 temis-previews/site.tgz.b64.b2 temis-previews/site.tgz.b64.b3 temis-previews/site.tgz.b64.b4 | base64 -d | tar xz -C out
# v8 (22/11): pacote c1 por cima (index.html atualizado + /v8/)
base64 -d temis-previews/site.tgz.b64.c1 | tar xz -C out
# v8.1 (22/11, t1807u): quadros translúcidos + /v8_1/ e índice atualizado
base64 -d temis-previews/site.tgz.b64.d1 | tar xz -C out
# v9a/v9b (22/11, t1824u/t1825u): dois layouts sóbrios + programa de afiliados; índice atualizado
base64 -d temis-previews/site.tgz.b64.e1 | tar xz -C out
test -f out/index.html && test -f out/v1/planos/index.html && test -f out/v7/planos/index.html && test -f out/v8/planos/index.html && test -f out/v8/img/temis-wm-v8.webp && test -f out/v8_1/planos/index.html && test -f out/v8_1/img/temis-wm-v8.webp && test -f out/v8_1/assets/temis.css
test -f out/v9a/afiliados/index.html && test -f out/v9b/afiliados/index.html && test -f out/v9a/assets/site.css && test -f out/v9b/img/temis-720.webp
echo "[temis-previews] ok: $(find out -type f | wc -l) arquivos"
