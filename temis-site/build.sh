#!/usr/bin/env bash
# Render (static site temis-os): desempacota o snapshot estático do site público da Têmis em ./out
set -euo pipefail
rm -rf out && mkdir -p out
base64 -d temis-site/site.tgz.b64 | tar xz -C out
# navegação em camadas (frentes → Têmis → detalhe). Rollback: apagar a linha abaixo.
python3 temis-site/nav_pos.py out
# SEO, termos, sugestões e avaliações honestas. Rollback: apagar a linha abaixo (o pacote e o nav_pos ficam iguais).
python3 temis-site/seo_pos.py out
# Confiança, nova home, laboratório e catálogo das 28 (t1932u/t1933u). Rollback: apagar só esta linha.
python3 temis-site/confianca_pos.py out
# Estátua que vira marca d'água, selo-balança, CTAs de aquisição (t1940u). Rollback: apagar só esta linha.
python3 temis-site/aquisicao_pos.py out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
