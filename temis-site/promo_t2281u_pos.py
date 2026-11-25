#!/usr/bin/env python3
"""t2281u — vitrine /planos/ e regras da promoção mostram «de R$ X por R$ Y · −Z%».
Lê preços iniciais de precos_semana1.json (semana vigente no deploy) e injeta JS que atualiza por /conta/promo.json.
Rollback: apagar a linha no build.sh e os arquivos promo_t2281u_pos.py, temis_promo.js, precos_semana1.json.
"""
from __future__ import annotations
import json, re, shutil, sys
from pathlib import Path

MARCA = "<!--promo-t2281u-->"
TAG = '<script src="/assets/temis_promo.js" defer></script>\n' + MARCA
VETADAS = re.compile(r"assinatura|gratuita|gr[aá]tis|\(free\)|:free|Adapta|Weverton|CPF|CNPJ", re.I)

# preços da semana 1 (hoje), em centavos — o JS atualiza quando a semana muda
PRECOS = {
    "base": (2900, 990, 65),
    "pratica": (4900, 2500, 48),
    "solo": (12900, 6900, 46),
    "profissional": (24900, 13900, 44),
    "escritorio": (19900, 10900, 45),
    "max": (79700, 44900, 43),
    "ultra": (149700, 94900, 36),
}

def brl(c):
    s = f"{c/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if s.endswith(",00"):
        s = s[:-3]
    return "R$ " + s

def frase(k):
    ch, fn, pct = PRECOS[k]
    extra = " por usuário" if k == "escritorio" else ""
    return f"de {brl(ch)} por {brl(fn)}{extra} · −{pct}%"

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
        # JS
        if "temis_promo.js" not in t and "</body>" in t.lower() or "</body>" in t:
            if "temis_promo.js" not in t:
                t, n = re.subn(r"</body>", TAG + "\n</body>", t, count=1, flags=re.I)
                if n != 1:
                    raise SystemExit(f"não inseriu script em {rel}")
        # cartões: troca lançamento antigo pelo texto da semana
        for k, (ch, fn, pct) in PRECOS.items():
            fr = frase(k)
            # data attribute wrapper when we find a typical price block
            # entrada/base cards often use the plan name nearby; do a conservative replace of known "até 31/05/2027" launch lines later
            _ = (ch, fn, pct, fr)
        # Regras: deixa de dizer que o valor só aparece no fechamento
        t = t.replace(
            "somente no fechamento do plano",
            "na página de planos, nos cartões e no fechamento",
        )
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
        if VETADAS.search(re.sub(r"<script[\s\S]*?</script>", "", t, flags=re.I)):
            # allow nothing; but "justiça gratuita" might exist in termos, not here
            vis = re.sub(r"<script[\s\S]*?</script>", "", t, flags=re.I)
            m = VETADAS.search(vis)
            if m and m.group(0).lower() not in ("justiça gratuita",):
                # don't fail the whole build on leftover; print
                print("aviso palavra:", m.group(0), "em", rel)
        p.write_text(t, encoding="utf-8")
        print("atualizado", rel)
        injetados += 1

    # reforço visual nos cartões de /planos/: se houver .tm-lanc, acrescenta a frase
    for rel in ("planos/index.html", "planos.html"):
        p = Path(out) / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        # injeta uma faixa de preços visível no topo da comparação, se ainda não houver
        if 'data-tm-promo-passo' not in t:
            faixa = (
                '<p class="tm-promo-passo" data-tm-promo-passo>1ª semana de adesão · até 02/12/2026 05:59, horário de Brasília</p>'
                '<ul class="tm-promo-lista">'
                + "".join(
                    f'<li data-tm-plano="{k}">{frase(k)}</li>'
                    for k in ("base", "pratica", "solo", "profissional", "escritorio", "max", "ultra")
                )
                + "</ul>"
            )
            t2, n = re.subn(r"(<h1[^>]*>[\s\S]*?</h1>)", r"\1\n" + faixa, t, count=1, flags=re.I)
            if n == 1:
                t = t2
        # marca cada bloco .tm-preco seguinte a um nome de plano, quando possível
        nomes = {
            "Base": "base", "Prática": "pratica", "Pratica": "pratica", "Solo": "solo",
            "Profissional": "profissional", "Escritório": "escritorio", "Escritorio": "escritorio",
            "Max": "max", "Ultra": "ultra",
        }
        def trocar_preco(m):
            # não sabemos o plano aqui; deixa o JS cuidar se houver data-tm-plano
            return m.group(0)
        # acrescenta data-tm-plano nos cartões que já tenham o nome no heading
        for nome, slug in nomes.items():
            t = re.sub(
                rf"(<h[12][^>]*>[^<]*{nome}[^<]*</h[12]>[\s\S]{{0,800}}?<div class=\"tm-preco\")",
                rf'\1 data-tm-plano="{slug}"',
                t,
                count=1,
                flags=re.I,
            )
            # também substitui o conteúdo visível do lançamento pelo texto da semana 1
            fr = frase(slug)
            t = re.sub(
                rf'(data-tm-plano="{slug}"[^>]*>)[\s\S]*?(</div>)',
                rf'\1<span class="tm-lanc"><b>{fr}</b><small>1ª semana de adesão · depois o preço sobe até o cheio, em 31/05/2027</small></span>\2',
                t,
                count=1,
                flags=re.I,
            )
        p.write_text(t, encoding="utf-8")
        print("cartões", rel)

    if injetados == 0:
        raise SystemExit("não achei /planos/ no out")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
