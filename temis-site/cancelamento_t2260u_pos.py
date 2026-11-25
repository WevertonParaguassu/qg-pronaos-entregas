#!/usr/bin/env python3
"""t2260u — página pública /politica-de-cancelamento/ e links em /planos/, /termos/,
/regras-da-promocao/, rodapé e sitemap.

Rollback: apagar a linha deste script no build.sh e a pasta out/politica-de-cancelamento/.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--cancelamento-t2260u-->"
PROIBIDAS = ("assinatura", "gratuita", "grátis", "adapta")
URL = "/politica-de-cancelamento/"
TITULO = "Política de cancelamento · Têmis"
DESC = (
    "Como cancelar um plano da Têmis: desistência em 7 dias com devolução integral (CDC art. 49) "
    "e, nos planos longos, multa de 20% só sobre o saldo não usufruído."
)

# Texto canônico (igual ao da Área do cliente). Autocontido para o build no Render.
CORPO = '<h1>Política de cancelamento da Têmis</h1><div class="card"><p>Esta página explica, em linguagem clara, como encerrar um plano da Têmis. Os números exatos da sua contratação aparecem na Área do cliente, na tela de cancelamento, antes de qualquer confirmação.</p><h2>1. Direito de desistência em 7 dias</h2><p>Na contratação a distância (pelo site), você pode desistir em até 7 dias, contados do início desta contratação, nos termos do art. 49 do Código de Defesa do Consumidor. Nesse prazo, o valor pago volta integralmente, sem multa e sem que você precise justificar. O acesso é encerrado quando a devolução é confirmada.</p><h2>2. Plano mensal, depois dos 7 dias</h2><p>Você pode cancelar a qualquer momento, sem multa sobre os meses futuros ainda não cobrados. O acesso segue até o fim do período já pago. Depois dos 7 dias, o mês em curso não é devolvido, porque o serviço correspondente permanece à sua disposição até o término desse período.</p><h2>3. Planos anuais, de 2 anos e de 3 anos, depois dos 7 dias</h2><p>O cancelamento antecipado é permitido. Como o período foi pago adiantado, devolvemos o saldo não usufruído, calculado dia a dia, menos uma multa de 20% incidente <b>somente sobre esse saldo</b> (nunca sobre o valor total do plano nem sobre o tempo já usado).</p><p>Fórmula: <b>saldo não usufruído</b> = valor pago × (dias não usufruídos ÷ dias totais do período). <b>Multa</b> = 20% × saldo não usufruído. <b>Valor devolvido</b> = saldo não usufruído − multa.</p><p>Essa multa proporcional está limitada a 20% do que ainda não foi usufruído, para não colocar quem contrata em desvantagem excessiva (art. 51, IV, do CDC). Ela apenas recompõe, em parte, o desconto de prazo e o custo administrativo do encerramento antecipado. O acesso encerra quando a devolução é confirmada.</p><h2>4. Como cancelar</h2><p>Na <a href="/conta/">Área do cliente</a>, abra Cancelar o plano. A tela mostra o demonstrativo completo (dias, saldo, multa e valor a devolver) e só executa depois da sua confirmação. Em caso de dúvida, escreva para temis@e-pronaos.com.</p><h2>5. Promoção de lançamento</h2><p>O desconto de lançamento vale uma única vez por CPF ou CNPJ, conforme as <a href="/regras-da-promocao/">regras da promoção</a>. Cancelar e contratar de novo com o mesmo documento não reabre o desconto.</p><h2>6. Pagamento e prazos da devolução</h2><p>A devolução segue o mesmo caminho do pagamento (cartão, Pix ou boleto), pelos prazos do arranjador (Stripe, Efí ou Mercado Pago). Valores e datas do seu caso aparecem no demonstrativo antes da confirmação.</p></div>'

def garante(texto, onde):
    low = (texto or "").lower()
    for w in PROIBIDAS:
        if w in low:
            raise SystemExit(f"[cancelamento_t2260u] palavra vetada «{w}» em {onde}")

MAIN = (
    '<main id="main" class="wrap" style="position:relative;z-index:2;padding:2.5rem 0 3rem">\n'
    '<nav class="crumbs" aria-label="Você está aqui"><a href="/">Início</a> › '
    '<span>Política de cancelamento</span></nav>\n'
    '<p class="kicker">Contratação</p>\n'
    + CORPO +
    '<p class="mu">Atualizado em 25/11/2026. Horário de Brasília. '
    'Veja também as <a href="/regras-da-promocao/">regras da promoção</a> e os '
    '<a href="/termos/">termos de uso</a>.</p>\n'
    "</main>"
)

LINK_RODAPE = '<a href="/politica-de-cancelamento/">Política de cancelamento</a>'
LINK_TERMOS = '<a href="/termos/">Termos de uso</a>'

NOTA_PLANOS = (
    '<p class="mu" data-m="t2260u-pag">Cancelamento: 7 dias para desistir com devolução integral (CDC art. 49). '
    'No mensal, depois disso, cancele quando quiser, sem multa sobre meses futuros; o acesso segue até o fim do período pago. '
    'Nos planos de 1, 2 ou 3 anos, depois dos 7 dias, a multa é de 20% só do saldo não usufruído, e o restante volta. '
    '<a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)

NOTA_TERMOS = (
    '<p data-m="t2260u-pag">O cancelamento dos planos (desistência em 7 dias, planos mensais e multa proporcional '
    'dos prazos longos) está detalhado na <a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)

NOTA_REGRAS = (
    '<p data-m="t2260u-pag">O desconto de lançamento vale uma única vez por CPF ou CNPJ. Cancelar e contratar de novo '
    'com o mesmo documento não reabre o desconto. O encerramento do plano segue a '
    '<a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)

def meta(s, path, title, desc):
    s = re.sub(r"(<title>)[^<]*(</title>)", rf"\g<1>{title}\g<2>", s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', rf"\g<1>{desc}\g<2>", s, count=1)
    s = re.sub(r'(rel="canonical" href=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    s = re.sub(r'(property="og:url" content=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    s = re.sub(r'(property="og:title" content=")[^"]*(")', rf"\g<1>{title}\g<2>", s)
    s = re.sub(r'(property="og:description" content=")[^"]*(")', rf"\g<1>{desc}\g<2>", s)
    s = re.sub(r'(name="twitter:title" content=")[^"]*(")', rf"\g<1>{title}\g<2>", s)
    s = re.sub(r'(hreflang="pt-BR" href=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    s = re.sub(r'(hreflang="x-default" href=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    return s

def pagina(molde):
    s = meta(molde, URL, TITULO, DESC)
    if re.search(r"<main\b", s):
        s = re.sub(r"<main\b.*?</main>", MAIN, s, count=1, flags=re.S)
    else:
        s = s.replace("</body>", MAIN + "</body>")
    if MARCA not in s:
        s = s.replace("</body>", MARCA + "</body>")
    return s

def injeta_rodape(s):
    if LINK_RODAPE in s:
        return s
    if LINK_TERMOS in s:
        return s.replace(LINK_TERMOS, LINK_TERMOS + LINK_RODAPE, 1)
    return s

def injeta_bloco(s, nota, ancora_depois=None):
    if 'data-m="t2260u-pag"' in s and URL in s and nota[:40] in s:
        return s
    if nota in s:
        return s
    # tenta inserir antes do </main>
    if "</main>" in s:
        return s.replace("</main>", nota + "\n</main>", 1)
    return s

def sitemap(p):
    if not p.exists():
        return False
    t = p.read_text(encoding="utf-8")
    loc = "https://agentetemis.com/politica-de-cancelamento/"
    if loc in t:
        return False
    item = (
        f"  <url><loc>{loc}</loc>"
        f"<lastmod>2026-11-25</lastmod>"
        f"<changefreq>monthly</changefreq><priority>0.6</priority></url>\n"
    )
    if "</urlset>" in t:
        t = t.replace("</urlset>", item + "</urlset>", 1)
        p.write_text(t, encoding="utf-8")
        return True
    return False

def main():
    if not OUT.exists():
        print("[cancelamento_t2260u] sem pasta out/")
        return
    garante(MAIN + NOTA_PLANOS + NOTA_TERMOS + NOTA_REGRAS + TITULO + DESC, "textos")
    feitos = {"pagina": False, "rodape": 0, "planos": False, "termos": False, "regras": False, "sitemap": False}
    molde = None
    for cand in (OUT / "regras-da-promocao" / "index.html", OUT / "termos" / "index.html", OUT / "suporte" / "index.html"):
        if cand.exists():
            molde = cand.read_text(encoding="utf-8")
            break
    if molde:
        d = OUT / "politica-de-cancelamento"
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina(molde), encoding="utf-8")
        feitos["pagina"] = True
    for f in OUT.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        novo = injeta_rodape(s)
        caminho = str(f).replace("\\", "/")
        if caminho.endswith("/planos/index.html"):
            n2 = injeta_bloco(novo, NOTA_PLANOS)
            if n2 != novo:
                feitos["planos"] = True
            novo = n2
        if caminho.endswith("/termos/index.html"):
            n2 = injeta_bloco(novo, NOTA_TERMOS)
            if n2 != novo:
                feitos["termos"] = True
            novo = n2
        if caminho.endswith("/regras-da-promocao/index.html"):
            n2 = injeta_bloco(novo, NOTA_REGRAS)
            if n2 != novo:
                feitos["regras"] = True
            novo = n2
        if novo != s:
            f.write_text(novo, encoding="utf-8")
            feitos["rodape"] += 1
    sm = OUT / "sitemap.xml"
    feitos["sitemap"] = sitemap(sm)
    print("[cancelamento_t2260u]", feitos)

if __name__ == "__main__":
    main()
