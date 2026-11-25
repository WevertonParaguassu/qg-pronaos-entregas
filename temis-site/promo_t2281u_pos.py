#!/usr/bin/env python3
"""t2281u — vitrine /planos/ e regras da promoção mostram «de R$ X por R$ Y · −Z%».
Preços iniciais da semana vigente no deploy; o JS atualiza por /conta/promo.json.
Rollback: apagar a linha no build.sh e os arquivos promo_t2281u_pos.py, temis_promo.js.
"""
from __future__ import annotations
import re, shutil, sys
from pathlib import Path

MARCA = "<!--promo-t2281u-->"
TAG = '<script src="/assets/temis_promo.js" defer></script>\n' + MARCA
VETADAS = re.compile(r"assinatura|gratuita|gr[aá]tis|\(free\)|:free|Adapta|Weverton", re.I)

PRECOS = {
    "base": (2900, 990, 65),
    "pratica": (4900, 2500, 48),
    "solo": (12900, 6900, 46),
    "profissional": (24900, 13900, 44),
    "escritorio": (19900, 10900, 45),
    "max": (79700, 44900, 43),
    "ultra": (149700, 94900, 36),
}

CSS = """<style>
.tm-promo-passo{color:#f0d58c;margin:.6rem 0 .3rem}
.tm-promo-lista{display:grid;gap:.2rem;margin:.3rem 0 1.2rem;padding-left:1.2rem;list-style:disc;line-height:1.45}
.tm-promo-lista li{display:list-item}
.tm-preco[data-tm-plano]{line-height:1.4}
</style>
"""


def brl(c):
    s = f"{c/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if s.endswith(",00"):
        s = s[:-3]
    return "R$ " + s


def frase(k):
    ch, fn, pct = PRECOS[k]
    extra = " por usuário" if k == "escritorio" else ""
    return f"de {brl(ch)} por {brl(fn)}{extra} · −{pct}%"


def _injeta_js(t: str) -> str:
    if "temis_promo.js" in t:
        return t
    if "</body>" not in t and "</body>" not in t.lower():
        raise SystemExit("sem </body>")
    t2, n = re.subn(r"</body>", TAG + "\n</body>", t, count=1, flags=re.I)
    if n != 1:
        raise SystemExit("não inseriu script")
    return t2


def _atualiza_regras(t: str) -> str:
    t = t.replace("somente no fechamento do plano", "na página de planos, nos cartões e no fechamento")
    t = t.replace(
        "o valor exato aparece no fechamento do plano",
        "o preço final e o percentual aparecem na página de planos, nos cartões e no fechamento",
    )
    t = t.replace(
        "O valor exato de cada plano e prazo aparece <b>somente no fechamento do plano</b>, na área do cliente, antes de pagar.",
        "O preço final e o percentual de cada plano aparecem <b>na página de planos, nos cartões e no fechamento</b>.",
    )
    t = t.replace(
        "Por isso a vitrine não anuncia um único percentual sobre o preço cheio: o desconto efetivo varia conforme o plano, e o valor em reais é o que vale.",
        "O percentual anunciado é o desconto efetivo sobre o preço cheio daquele plano, no formato de R$ X por R$ Y · −Z%.",
    )
    t = t.replace(
        "o valor exato de cada plano e prazo aparece no fechamento do plano, na área do cliente",
        "o preço final e o percentual aparecem na página de planos, nos cartões e no fechamento",
    )
    t = t.replace(
        "O valor exato, em reais, aparece no fechamento do plano — depois de entrar na sua conta e escolher o prazo.",
        "O preço final e o percentual aparecem na página de planos, nos cartões e no fechamento.",
    )
    t = t.replace(
        "O valor exato aparece no fechamento do plano.",
        "O preço final e o percentual aparecem na página de planos, nos cartões e no fechamento.",
    )
    t = t.replace(
        "o valor exato aparece no fechamento do plano",
        "o preço final e o percentual aparecem na página de planos, nos cartões e no fechamento",
    )
    return t



def _marca_tabela_mes(t: str) -> str:
    """Preenche a linha '1º mês' da tabela comparativa. Só troca o span fechado, sem regex gulosa."""
    n = 0
    for cheio, slug in (
        ("29", "base"),
        ("49", "pratica"),
        ("129", "solo"),
        ("249", "profissional"),
        ("199", "escritorio"),
        ("797", "max"),
        ("1.497", "ultra"),
    ):
        alvo = (
            f'<span class="tm-cel-fechamento"><b>no fechamento</b>'
            f'<small>valor exato no fechamento do plano · cheio R$ {cheio}</small></span>'
        )
        novo = (
            f'<span class="tm-cel-fechamento" data-tm-plano="{slug}" data-tm-prazo="mensal">'
            f'{frase(slug)}</span>'
        )
        if alvo in t:
            t = t.replace(alvo, novo, 1)
            n += 1
    print("tabela_1o_mes", n)
    return t


def _marca_preco(t: str, heading: str, slug: str) -> str:
    """Troca só o primeiro <div class="tm-preco"> depois do heading, janela curta. Não toca a lista do topo."""
    fr = frase(slug)
    pat = re.compile(
        rf"(<h[12][^>]*>[\s\S]{{0,80}}?{re.escape(heading)}[\s\S]{{0,80}}?</h[12]>)"
        rf"([\s\S]{{0,800}}?)"
        rf"(<div class=\"tm-preco\")([^>]*)>"
        rf"([\s\S]*?)</div>",
        re.I,
    )

    def repl(m):
        return (
            f"{m.group(1)}{m.group(2)}{m.group(3)} data-tm-plano=\"{slug}\">"
            f"<span class=\"tm-lanc\"><b>{fr}</b>"
            f"<small>1ª semana de adesão · depois o preço sobe até o cheio, em 31/05/2027</small></span></div>"
        )

    t2, n = pat.subn(repl, t, count=1)
    print("preco", heading, slug, n)
    return t2


def main(out: str) -> None:
    raiz = Path(__file__).resolve().parent
    dest = Path(out) / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    js = raiz / "temis_promo.js"
    if not js.is_file():
        alt = Path("/workspace/temis_t2280u/static/temis_promo.js")
        if alt.is_file():
            js = alt
        else:
            raise SystemExit("faltou temis_promo.js")
    js_txt = js.read_text(encoding="utf-8")
    if VETADAS.search(js_txt):
        raise SystemExit("JS público não pode ter palavra vetada")
    if "t2280u" in js_txt or "t2281u" in js_txt:
        raise SystemExit("JS público não pode trazer código interno")
    shutil.copy2(js, dest / "temis_promo.js")

    injetados = 0
    for rel in ("planos/index.html", "planos.html", "regras-da-promocao/index.html", "regras-da-promocao.html"):
        p = Path(out) / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        t = _injeta_js(t)
        t = _atualiza_regras(t)
        if "planos" in rel:
            if "tm-promo-lista{" not in t and "</head>" in t:
                t = t.replace("</head>", CSS + "</head>", 1)
            if "data-tm-promo-passo" not in t:
                itens = "".join(
                    f'<li data-tm-plano="{k}">{frase(k)}</li>'
                    for k in ("base", "pratica", "solo", "profissional", "escritorio", "max", "ultra")
                )
                faixa = (
                    '<p class="tm-promo-passo" data-tm-promo-passo>1ª semana de adesão · até 02/12/2026 05:59, horário de Brasília</p>'
                    f'<ul class="tm-promo-lista">{itens}</ul>'
                )
                t2, n = re.subn(r"(<h1[^>]*>[\s\S]*?</h1>)", r"\1\n" + faixa, t, count=1, flags=re.I)
                if n == 1:
                    t = t2
            for heading, slug in (
                ("Têmis Base", "base"),
                ("Têmis Prática", "pratica"),
                (">Solo<", "solo"),
                (">Profissional<", "profissional"),
                (">Escritório<", "escritorio"),
                ("Têmis Max", "max"),
                ("Têmis Ultra", "ultra"),
            ):
                # heading puro, sem os sinais de tag
                h = heading.replace(">", "").replace("<", "")
                t = _marca_preco(t, h, slug)
            t = _marca_tabela_mes(t)
        p.write_text(t, encoding="utf-8")
        print("atualizado", rel)
        injetados += 1

    if injetados == 0:
        raise SystemExit("não achei /planos/ no out")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
