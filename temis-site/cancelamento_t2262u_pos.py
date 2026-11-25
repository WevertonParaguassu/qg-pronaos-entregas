#!/usr/bin/env python3
"""t2262u — atualiza /politica-de-cancelamento/ (abatimento do uso nos 7 dias),
notas em /planos/, /termos/, /regras-da-promocao/ e a descrição. Roda DEPOIS do
cancelamento_t2260u_pos.py e ANTES do PWA.

Rollback: apagar a linha deste script no build.sh. A página volta ao texto do t2260u
no próximo build (o script t2260u continua no pipeline).
"""
from __future__ import annotations
import re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "out")
MARCA = "<!--cancelamento-t2262u-->"
PROIBIDAS = ("assinatura", "gratuita", "grátis", "adapta")
URL = "/politica-de-cancelamento/"
TITULO = "Política de cancelamento · Têmis"
DESC = (
    "Como cancelar um plano da Têmis: desistência em 7 dias (CDC art. 49), "
    "com abatimento do que já foi entregue e usado; nos planos longos, depois disso, "
    "multa de 20% só sobre o saldo não usufruído."
)

# Texto canônico (igual ao da Área do cliente, módulo t2262u). Autocontido para o build no Render.
CORPO = (
    '<h1>Política de cancelamento da Têmis</h1>'
    '<div class="card">'
    '<p>Esta página explica, em linguagem clara, como encerrar um plano da Têmis. '
    'Os números exatos da sua contratação aparecem na Área do cliente, na tela de cancelamento, '
    'antes de qualquer confirmação.</p>'

    '<h2>1. Direito de desistência em 7 dias</h2>'
    '<p>Na contratação a distância (pelo site), você pode desistir em até 7 dias, contados do início '
    'desta contratação, nos termos do art. 49 do Código de Defesa do Consumidor. Esse direito permanece. '
    'Não há multa neste prazo e você não precisa justificar.</p>'
    '<p>O valor correspondente ao que <b>ainda não foi usado</b> volta por inteiro. '
    'O valor correspondente ao que já foi <b>efetivamente entregue e usado</b> — peças geradas, '
    'análises, créditos de modelo, downloads e serviços prestados a seu pedido, com início imediato — '
    'é abatido, com medição real do uso. Isso vale para conteúdo digital já entregue, que não se '
    'restitui da mesma forma que um bem físico. O aceite expresso dessa regra aparece no fechamento '
    'da contratação e, de novo, quando você pede um entregável pesado na janela de 7 dias.</p>'
    '<p>Se não houver nenhum uso efetivo, o valor pago volta por inteiro, sem multa. '
    'O acesso é encerrado quando a devolução é confirmada.</p>'

    '<h2>2. Liberação gradual nos 7 primeiros dias</h2>'
    '<p>Para que a desistência continue possível de fato, os entregáveis de maior custo '
    '(pacote completo em ZIP, peças e chamadas pesadas de modelo acima do limite do plano, '
    'aplicativos avulsos) são liberados aos poucos nessa janela, ou de imediato se você der '
    'aceite expresso de início imediato, ciente de que o valor correspondente será abatido '
    'se desistir. O download da peça que você já gerou permanece disponível.</p>'

    '<h2>3. Aplicativos, skills e ferramentas avulsos</h2>'
    '<p>Itens avulsos já entregues ou já consumidos, com aceite no pedido, não são devolvidos '
    'depois da entrega. O valor do plano é apurado em separado.</p>'

    '<h2>4. Plano mensal, depois dos 7 dias</h2>'
    '<p>Você pode cancelar a qualquer momento, sem multa sobre os meses futuros ainda não cobrados. '
    'O acesso segue até o fim do período já pago. Depois dos 7 dias, o mês em curso não é devolvido, '
    'porque o serviço correspondente permanece à sua disposição até o término desse período. '
    'O que já foi usado não volta.</p>'

    '<h2>5. Planos anuais, de 2 anos e de 3 anos, depois dos 7 dias</h2>'
    '<p>O cancelamento antecipado é permitido. Como o período foi pago adiantado, devolvemos o saldo '
    'não usufruído, calculado dia a dia, menos uma multa de 20% incidente <b>somente sobre esse saldo</b> '
    '(nunca sobre o valor total do plano nem sobre o tempo já usado). O que já foi usufruído não volta.</p>'
    '<p>Fórmula: <b>saldo não usufruído</b> = valor pago × (dias não usufruídos ÷ dias totais do período). '
    '<b>Multa</b> = 20% × saldo não usufruído. <b>Valor devolvido</b> = saldo não usufruído − multa.</p>'
    '<p>Essa multa proporcional está limitada a 20% do que ainda não foi usufruído, para não colocar '
    'quem contrata em desvantagem excessiva (art. 51, IV, do CDC). Ela apenas recompõe, em parte, '
    'o desconto de prazo e o custo administrativo do encerramento antecipado. O acesso encerra quando '
    'a devolução é confirmada.</p>'

    '<h2>6. Como cancelar</h2>'
    '<p>Na <a href="/conta/">Área do cliente</a>, abra Cancelar o plano. A tela mostra o demonstrativo '
    'completo (dias, uso efetivo, saldo, multa e valor a devolver) e só registra o pedido depois da sua confirmação. '
    'Valores acima de um teto automático, ou casos que peçam conferência, passam pelo agente-guarda '
    'antes de qualquer devolução. Em caso de dúvida, escreva para temis@e-pronaos.com.</p>'

    '<h2>7. Promoção de lançamento e prevenção de abuso</h2>'
    '<p>O desconto de lançamento e o período de teste valem uma única vez por CPF ou CNPJ, conforme as '
    '<a href="/regras-da-promocao/">regras da promoção</a>. Cancelar e contratar de novo com o mesmo '
    'documento não reabre o desconto nem o período de teste. Para essa conferência guardamos só um '
    'código cifrado do documento e a data, nunca o número. Uso intenso na janela de desistência seguido '
    'de cancelamento, ou cancelamentos em série, vai a revisão.</p>'

    '<h2>8. Pagamento e prazos da devolução</h2>'
    '<p>A devolução segue o mesmo caminho do pagamento (cartão, Pix ou boleto), pelos prazos do '
    'arranjador (Stripe, Efí ou Mercado Pago). Valores e datas do seu caso aparecem no demonstrativo '
    'antes da confirmação.</p>'
    '</div>'
)

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

NOTA_PLANOS = (
    '<p class="mu" data-m="t2262u-can">Cancelamento: 7 dias para desistir (CDC art. 49). '
    'O que você não tiver usado volta por inteiro, sem multa; o que já tiver sido entregue e usado é abatido. '
    'No mensal, depois disso, cancele quando quiser, sem multa sobre meses futuros; o acesso segue até o fim do período pago. '
    'Nos planos de 1, 2 ou 3 anos, depois dos 7 dias, a multa é de 20% só do saldo não usufruído, e o restante volta. '
    'Aplicativos avulsos já entregues não são devolvidos. '
    '<a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)

NOTA_TERMOS = (
    '<p data-m="t2262u-can">O cancelamento dos planos (desistência em 7 dias com abatimento do que já foi usado, '
    'planos mensais e multa proporcional dos prazos longos) está detalhado na '
    '<a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)

NOTA_REGRAS = (
    '<p data-m="t2262u-can">O desconto de lançamento e o período de teste valem uma única vez por CPF ou CNPJ. '
    'Cancelar e contratar de novo com o mesmo documento não reabre o desconto nem o período de teste. '
    'O encerramento do plano segue a '
    '<a href="/politica-de-cancelamento/">Política de cancelamento</a>.</p>'
)


def garante(texto, onde):
    low = (texto or "").lower()
    for w in PROIBIDAS:
        if w in low:
            raise SystemExit(f"[cancelamento_t2262u] palavra vetada «{w}» em {onde}")


def meta(s, path, title, desc):
    s = re.sub(r"(<title>)[^<]*(</title>)", rf"\g<1>{title}\g<2>", s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', rf"\g<1>{desc}\g<2>", s, count=1)
    s = re.sub(r'(rel="canonical" href=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    s = re.sub(r'(property="og:url" content=")[^"]*(")', rf"\g<1>https://agentetemis.com{path}\g<2>", s)
    s = re.sub(r'(property="og:title" content=")[^"]*(")', rf"\g<1>{title}\g<2>", s)
    s = re.sub(r'(property="og:description" content=")[^"]*(")', rf"\g<1>{desc}\g<2>", s)
    s = re.sub(r'(name="twitter:title" content=")[^"]*(")', rf"\g<1>{title}\g<2>", s)
    s = re.sub(r'(name="twitter:description" content=")[^"]*(")', rf"\g<1>{desc}\g<2>", s)
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


def troca_nota(s, nova, marca_antiga='data-m="t2260u-pag"', marca_nova='data-m="t2262u-can"'):
    if marca_nova in s and nova[:40] in s:
        return s
    # substitui a nota do t2260u, se existir
    s2 = re.sub(
        rf'<p[^>]*{re.escape(marca_antiga)}[^>]*>.*?</p>',
        nova,
        s,
        count=1,
        flags=re.S,
    )
    if s2 != s:
        return s2
    if nova in s:
        return s
    if "</main>" in s:
        return s.replace("</main>", nova + "\n</main>", 1)
    return s


def main():
    if not OUT.exists():
        print("[cancelamento_t2262u] sem pasta out/")
        return
    garante(MAIN + NOTA_PLANOS + NOTA_TERMOS + NOTA_REGRAS + TITULO + DESC, "textos")
    feitos = {"pagina": False, "planos": False, "termos": False, "regras": False}
    alvo = OUT / "politica-de-cancelamento" / "index.html"
    if alvo.exists():
        molde = alvo.read_text(encoding="utf-8")
        alvo.write_text(pagina(molde), encoding="utf-8")
        feitos["pagina"] = True
    else:
        # se o t2260u ainda não rodou, cria a partir de outro molde
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
    for rel, nota, chave in (
        ("planos/index.html", NOTA_PLANOS, "planos"),
        ("termos/index.html", NOTA_TERMOS, "termos"),
        ("regras-da-promocao/index.html", NOTA_REGRAS, "regras"),
    ):
        f = OUT / rel
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8")
        n = troca_nota(s, nota)
        if n != s:
            f.write_text(n, encoding="utf-8")
            feitos[chave] = True
    print("[cancelamento_t2262u]", feitos)


if __name__ == "__main__":
    main()
