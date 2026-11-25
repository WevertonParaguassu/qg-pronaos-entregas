#!/usr/bin/env python3
"""t2230u — Programa Cobrimos a oferta: regulamento nos termos e resumo em /planos/
(e no comparativo). Rollback: apagar a linha deste arquivo no build.sh."""
from __future__ import annotations

import re
import sys
from pathlib import Path

VETADAS = re.compile(r"assinatura|gratuita|grátis", re.I)

RESUMO = """<section class="sec" id="cobrimos-oferta"><div class="wrap"><div class="sec-head"><p class="eyebrow">Cobrimos a oferta</p><h2>Se achar um plano equivalente em outra plataforma</h2></div>
<p>A Têmis cobre a oferta de outra plataforma jurídica com inteligência artificial, no plano de mesmo nível. O pedido vale só quando o plano ou pacote concorrente <b>não estiver em promoção nem com desconto</b> no momento, a plataforma estiver <b>no ar há mais de 2 anos</b> (como comprovação de plataforma séria) e você comprovar que ela de fato presta o serviço e que você é cliente real — com <b>fatura ou comprovante de pagamento</b> e um <b>print da conta ativa</b>.</p>
<p>Se ficar comprovada fraude, a Têmis se reserva o direito de recusar o pedido, cancelar o benefício, cobrar a diferença e adotar as medidas administrativas ou judiciais cabíveis.</p>
<p class="actions"><a class="btn" href="/conta/cobrimos">Pedir a cobertura ›</a><a class="btn btn-ghost" href="/termos/#cobrimos">Ler as regras ›</a></p>
</div></section>"""

STYLE = """<style id="tm-cobrimos-css">
.tm-cobrimos-reg{position:relative;z-index:4;background:rgba(8,18,36,.92);border:1px solid rgba(201,166,70,.4);border-radius:14px;padding:1.25rem 1.35rem 1.45rem;margin:1.6rem 0 1.2rem;scroll-margin-top:5.5rem}
.tm-cobrimos-reg h3{margin-top:0}
</style>
"""

REGULAMENTO = """<div class="tm-cobrimos-reg" id="cobrimos"><h3>Programa Cobrimos a oferta</h3>
<p>O programa Cobrimos a oferta permite pedir que a Têmis cubra o preço de um plano ou pacote equivalente de outra plataforma jurídica, com o plano da Têmis de mesmo nível. O pedido é feito na <a href="/conta/cobrimos">área do cliente</a>. A equipe responde em até 2 dias úteis. Cobrimos com o plano de capacidade equivalente. Há um valor mínimo por plano. Uma cobertura por CPF ou CNPJ; o valor coberto vale por 12 meses e, depois, segue a tabela em vigor, com aviso de 30 dias.</p>
<p>Condições para o pedido ser analisado:</p>
<ol>
<li>Só vale para plano ou pacote de outras plataformas que, no momento do pedido, <b>não estejam em promoção nem com desconto</b>.</li>
<li>A plataforma concorrente precisa estar <b>no ar há mais de 2 anos</b>, como comprovação de que é uma plataforma séria.</li>
<li>Quem pede precisa comprovar que a outra plataforma de fato presta o serviço e que é cliente real dela, com <b>fatura ou comprovante de pagamento</b> e um <b>print da conta ativa</b>, para evitar fraudes.</li>
<li>A Têmis se reserva o direito de recusar o pedido, de cancelar o benefício e de cobrar a diferença, bem como de adotar as medidas administrativas ou judiciais cabíveis, se ficar comprovada fraude.</li>
</ol>
<p>Também não valem preço de primeiro mês, cupom pessoal, plano «sob consulta» sem proposta escrita ou produto que saiu de linha. A oferta precisa ser pública, atual e conferível (link ou print com data).</p>
</div>
"""

# âncora no comparativo, logo abaixo do título da seção
NOTA_COMPARATIVO = (
    '<p class="fine" id="cobrimos-comparativo">Cobrimos oferta equivalente de outra plataforma, '
    'só se o plano não estiver em promoção, a plataforma estiver no ar há mais de 2 anos e houver '
    'comprovação de cliente real. <a href="#cobrimos-oferta">Como funciona</a> · '
    '<a href="/termos/#cobrimos">Regras</a>.</p>'
)


def _checa(txt: str, onde: str) -> None:
    m = VETADAS.search(txt)
    if m:
        raise SystemExit(f"[cobrimos_t2230u] palavra vetada «{m.group(0)}» em {onde}")


def patch_planos(html: str) -> str:
    if 'id="cobrimos-oferta"' not in html:
        alvo = '<section class="sec" id="comparativo">'
        if alvo not in html:
            raise SystemExit("[cobrimos_t2230u] âncora do comparativo não encontrada em /planos/")
        html = html.replace(alvo, RESUMO + alvo, 1)
    if 'id="cobrimos-comparativo"' not in html:
        # logo após o h2 do comparativo
        h2 = "<h2>O que cada plano entrega</h2>"
        if h2 not in html:
            raise SystemExit("[cobrimos_t2230u] título do comparativo não encontrado em /planos/")
        html = html.replace(h2, h2 + NOTA_COMPARATIVO, 1)
    _checa(RESUMO + NOTA_COMPARATIVO, "/planos/")
    return html


def patch_termos(html: str) -> str:
    if "tm-cobrimos-css" not in html:
        html = html.replace("</head>", STYLE + "</head>", 1) if "</head>" in html else STYLE + html
    if 'class="tm-cobrimos-reg"' in html:
        _checa(REGULAMENTO, "/termos/")
        return html
    alvo = "<h3>Alterações e contato</h3>"
    if alvo not in html:
        raise SystemExit("[cobrimos_t2230u] seção «Alterações e contato» não encontrada em /termos/")
    if 'id="cobrimos"' in html:
        html = re.sub(r'<h3 id="cobrimos">[\s\S]*?(?=<h3>Alterações e contato</h3>)', REGULAMENTO, html, count=1)
    else:
        html = html.replace(alvo, REGULAMENTO + alvo, 1)
    _checa(REGULAMENTO, "/termos/")
    return html


def main(out: Path) -> None:
    planos = out / "planos" / "index.html"
    termos = out / "termos" / "index.html"
    if not planos.exists() or not termos.exists():
        raise SystemExit("[cobrimos_t2230u] faltam /planos/ ou /termos/ no out/")
    p = patch_planos(planos.read_text(encoding="utf-8"))
    t = patch_termos(termos.read_text(encoding="utf-8"))
    planos.write_text(p, encoding="utf-8")
    termos.write_text(t, encoding="utf-8")
    # idempotência numa segunda passagem
    assert patch_planos(p) == p
    assert patch_termos(t) == t
    print("[cobrimos_t2230u] ok: regulamento em /termos/#cobrimos e resumo em /planos/ (antes do comparativo)")


if __name__ == "__main__":
    dest = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    main(dest)
