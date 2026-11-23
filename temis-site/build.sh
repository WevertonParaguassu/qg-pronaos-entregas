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
# Ícones de linha dourados das 28 aplicações no catálogo e nas páginas. Rollback: apagar só esta linha.
python3 temis-site/icons_pos.py out
# Estátua fixa (marca d'água), selo-balança, CTAs, lightbox (t1940u/t1947u/t1951u). Rollback: apagar só esta linha.
python3 temis-site/aquisicao_pos.py out
# Privacidade honesta com o Conselho das 4 (Ultra, opt-in, pergunta anonimizada) — t1942u/t1944u. Rollback: apagar só esta linha.
python3 temis-site/privacidade_pos.py out
# Laboratório interativo (checklist com âncoras, minuta completa, [DOC n], laudos.pdf) e prints honestos (t1950u/t1951u). Rollback: apagar só esta linha.
python3 temis-site/laboratorio_pos.py out
# Contato público temis@e-pronaos.com (t1956u). Rollback: apagar só esta linha.
python3 temis-site/contato_pos.py out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
