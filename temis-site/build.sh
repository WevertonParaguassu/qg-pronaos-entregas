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
# Relatar um problema, 404 amigável e sem vazamento interno (t1965u). Rollback: apagar só esta linha.
python3 temis-site/erros_pos.py out
# Cartões em vidro: a estátua aparece em marca d'água por baixo (t1977u). Rollback: apagar só esta linha.
python3 temis-site/marca_dagua_pos.py out
# Medalhas douradas da escada de planos em /planos/ (Solo → Ultra, sem preços) — t1974u. Rollback: apagar só esta linha.
python3 temis-site/escada_pos.py out
# Tabela pública de preços (já aprovados), contagem do lançamento, comparativo por recurso e «Têmis Essencial — 7 dias para testar» em /planos/ (t2198u, aprovado em 24/11/2026). Rollback: apagar só esta linha.
python3 temis-site/precos_pos.py out
# Sem «assinatura», «gratuita» ou «grátis» no texto visível do site; chamada «sem custo no teste» (t2198u). Rollback: apagar só esta linha.
python3 temis-site/palavras_pos.py out
# Pacotinhos Base e Prática em /planos/, sem alterar precos_pos (t2204u). Rollback: apagar só esta linha.
python3 temis-site/entrada_t2204u_pos.py out
# Medalhas e tags da escada (t2201u). Rollback: apagar só esta linha.
python3 temis-site/medalhas_t2201u_pos.py out
# Glossário, rampa (−50/40/30/20/10, cheio no 6º mês, inscrição até 31/05/2027 23h59 BRT), escada de 8 degraus e nomes dos botões (t2217u). Rollback: apagar só esta linha.
python3 temis-site/rampa_glossario_t2217u_pos.py out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
