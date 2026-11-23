#!/usr/bin/env bash
# Render (static site temis-os): desempacota o snapshot estático do site público da Têmis em ./out
set -euo pipefail
rm -rf out && mkdir -p out
base64 -d temis-site/site.tgz.b64 | tar xz -C out
# navegação em camadas (frentes → Têmis → detalhe), só o que passou em teste. Rollback: apagar a linha abaixo.
python3 temis-site/nav_pos.py out
# SEO, termos, sugestões e avaliações honestas. Rollback: apagar a linha abaixo (o pacote e o nav_pos ficam iguais).
python3 temis-site/seo_pos.py out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
