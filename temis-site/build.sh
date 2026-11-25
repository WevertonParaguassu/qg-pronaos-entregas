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
# Polimento final (t2217u): tipografia, cartões acima da estátua, home sem painel sintético, menu com a página atual, textos coerentes; folhas temis-conta.css/temis-app.css para /conta e o painel. Rollback: apagar só esta linha.
python3 temis-site/polish_t2217u_pos.py out
# Oferta da semana no 1º mês (78/65/50), contagem até o fim da semana e ?indicacao= (t2220u/t2221u). Rollback: apagar só esta linha.
python3 temis-site/semanas_t2220u_pos.py out
# Programa Cobrimos a oferta (t2230u): regulamento em /termos/#cobrimos e resumo em /planos/ (junto ao comparativo). Rollback: apagar só esta linha.
python3 temis-site/cobrimos_t2230u_pos.py out
# Vídeos da triagem (t2226u): seção «Veja uma triagem real» na home e em /planos/; MP4s auto-hospedados, lazy (preload=none), com cartaz; mesa nas telas largas, celular nas estreitas. Rollback: apagar só esta linha.
python3 temis-site/triagem_t2226u_pos.py out
# Robôs de IA fora (t2231u): robots.txt com os robôs de IA, ai.txt e .well-known/tdmrep.json. Rollback: apagar só esta linha.
python3 temis-site/antirobo_t2231u_pos.py out
# Suporte e inauguração (t2235u): página /suporte/ com suportetemis@e-pronaos.com, linha de suporte no rodapé, aviso em /sugestoes/, faixa «Chegou a Têmis» na home (troca sozinha por semana: 78/65/50) e sitemap. Rollback: apagar só esta linha.
python3 temis-site/suporte_t2235u_pos.py out
# Busca da marca Têmis/Temis (t2239u): título/OG, JSON-LD com alternateName, linha «também escrito Temis», hreflang pt-BR e sitemap completo. Não mexe no robots.txt. Rollback: apagar só esta linha.
python3 temis-site/busca_t2239u_pos.py out
# Chamada da rampa (t2240u): faixa e janela com desconto por semana de adesão (não «1º mês» como título), página /regras-da-promocao/, troca sozinha por semana. Não altera preços nem cupons. Rollback: apagar só esta linha.
python3 temis-site/chamada_t2240u_pos.py out
# Chamada generalista + regras com piso (t2248u): valor exato só no fechamento; rampa só no 1º ano em 2/3 anos. Rollback: apagar só esta linha.
python3 temis-site/chamada_t2248u_pos.py out
# Vitrine pública /aplicativos/ (t2259u): aplicativos, skills e ferramentas à la carte. Roda antes do PWA.
# Rollback: apagar só esta linha e os arquivos vitrine_t2259u_pos.py e alacarte_publicos.json.
python3 temis-site/vitrine_t2259u_pos.py out
# Política de cancelamento (t2260u): /politica-de-cancelamento/, links em /planos/, /termos/, /regras-da-promocao/, rodapé e sitemap. Rollback: apagar só esta linha.
python3 temis-site/cancelamento_t2260u_pos.py out
# Abatimento do uso na política de cancelamento (t2262u): atualiza /politica-de-cancelamento/ e as notas.
# Roda depois do t2260u e antes do PWA. Rollback: apagar só estas duas linhas.
python3 temis-site/cancelamento_t2262u_pos.py out
# Turmas publicadas na vitrine /planos/ (t2276u): selo «Turma aberta · restam N vagas», azul e ouro. Lê /conta/vagas.json no mesmo domínio. Rollback: apagar só esta linha.
python3 temis-site/turmas_t2276u_pos.py out
# Preço final e percentual na vitrine (t2281u): «de R$ X por R$ Y · −Z%», atualizado por /conta/promo.json. Rollback: apagar só esta linha.
python3 temis-site/promo_t2281u_pos.py out
# PWA instalável (t2225u): manifesto, service worker (cascão offline, sem cache de API/documentos), ícones maskable, botão Instalar o app Têmis e dica no iOS. Roda por último, depois das semanas. Rollback: apagar só esta linha.
python3 temis-site/pwa_t2225u_pos.py out
test -f out/index.html && echo "[temis-site] ok: $(find out -type f | wc -l) arquivos"
