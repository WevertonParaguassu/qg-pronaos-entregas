#!/usr/bin/env python3
"""t2248u — chamada pública generalista + regras alinhadas à cobrança com piso.

A vitrine não anuncia percentual de campanha nem o valor exato da rampa.
O valor exato aparece no fechamento do plano (área do cliente / checkout).
Lê as datas em precos_publicos.json (mesmo calendário do checkout).
Não altera preços nem cupons (isso é da temis-vendas).

Rollback: apagar a linha deste script no build.sh.
"""
from __future__ import annotations

import json, re, sys, time
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--chamada-t2248u-->"
PROIBIDAS = ("assinatura", "gratuita", "grátis", "adapta")
DADOS = json.loads((ROOT / "precos_publicos.json").read_text(encoding="utf-8"))
SEMANAS = (DADOS.get("rampa") or {}).get("semanas") or {}
FIM_EP = int((DADOS.get("lancamento") or {}).get("fim_epoch") or 1811818799)
REGRAS = "/regras-da-promocao/"

def semana_agora(agora=None):
    agora = time.time() if agora is None else agora
    s1, s2, s3 = SEMANAS.get("1") or {}, SEMANAS.get("2") or {}, SEMANAS.get("3") or {}
    if s3.get("fim_epoch") and agora > int(s3["fim_epoch"]):
        return "0", {}
    if not s1.get("fim_epoch") or agora <= int(s1["fim_epoch"]):
        return "1", s1
    if not s2.get("fim_epoch") or agora <= int(s2["fim_epoch"]):
        return "2", s2
    return "3", s3

def textos(n, sem):
    f1 = (SEMANAS.get("1") or {}).get("fim_texto") or "02/12/2026 05:59, horário de Brasília"
    f2 = (SEMANAS.get("2") or {}).get("fim_texto") or "09/12/2026 05:59, horário de Brasília"
    f3 = (SEMANAS.get("3") or {}).get("fim_texto") or "31/05/2027 23:59, horário de Brasília"
    comum = (
        "<p>As condições de lançamento variam conforme a semana em que você adere. "
        "O valor exato, em reais, aparece no fechamento do plano — depois de entrar na sua conta e escolher o prazo. "
        "Nenhum plano é fechado abaixo do valor mínimo daquele plano.</p>"
        "<p>No prazo mensal, a rampa de lançamento vale nos primeiros meses e, a partir do 6º, segue o preço cheio. "
        "No anual, a rampa vale dentro desse ano. Nos planos de 2 anos e de 3 anos, a rampa vale <b>somente no 1º ano</b>; "
        "os anos seguintes seguem a tabela daquele prazo, sem a rampa. Não há preço travado para sempre.</p>"
    )
    if n == "1":
        faixa = (
            f"1ª semana de adesão, até {f1}. Condições de lançamento por semana de adesão; "
            f"o valor exato aparece no fechamento do plano. A rampa vai até {f3}."
        )
        titulo = "Chegou a Têmis · 1ª semana de adesão"
        janela = comum + (
            f"<p>Esta semana de adesão vai até <b>{f1}</b>. Depois, abre a 2ª semana (até {f2}). "
            f"A rampa de lançamento termina em {f3}. A data de encerramento não reinicia.</p>"
        )
    elif n == "2":
        faixa = (
            f"2ª semana de adesão, até {f2}. Condições de lançamento por semana de adesão; "
            f"o valor exato aparece no fechamento do plano. A rampa vai até {f3}."
        )
        titulo = "Chegou a Têmis · 2ª semana de adesão"
        janela = comum + (
            f"<p>Esta semana de adesão vai até <b>{f2}</b>. Depois, as condições seguem até {f3}, "
            f"quando a rampa de lançamento termina. A data de encerramento não reinicia.</p>"
        )
    else:
        faixa = f"Condições de lançamento até {f3}. O valor exato aparece no fechamento do plano."
        titulo = "Chegou a Têmis · condições de lançamento"
        janela = comum + (
            f"<p>A adesão com as condições de lançamento vai até <b>{f3}</b>. "
            f"Depois dessa data, novas adesões seguem a tabela em vigor, sem a rampa. A data não reinicia.</p>"
        )
    return faixa, titulo, janela

NS, SEM = semana_agora()
if NS == "0":
    FAIXA, TITULO, JANELA = "", "", ""
else:
    FAIXA, TITULO, JANELA = textos(NS, SEM)

JS_DADOS = {
    "semanas": {k: {"fim_epoch": v.get("fim_epoch"), "fim_texto": v.get("fim_texto"), "inicio_texto": v.get("inicio_texto")} for k, v in SEMANAS.items()},
    "inscricao_epoch": FIM_EP,
    "textos": {n: {"faixa": textos(n, SEMANAS.get(n) or {})[0], "titulo": textos(n, SEMANAS.get(n) or {})[1], "janela": textos(n, SEMANAS.get(n) or {})[2]} for n in ("1", "2", "3") if SEMANAS.get(n)},
}

REGRAS_MAIN = '<main id="main" class="wrap" style="position:relative;z-index:2;padding:2.5rem 0 3rem">\n<nav class="crumbs" aria-label="Você está aqui"><a href="/">Início</a> › <span>Regras da promoção</span></nav>\n<p class="kicker">Rampa de lançamento</p>\n<h1>Regras da promoção</h1>\n<p class="lead">Estas são as regras da rampa de lançamento da Têmis. Os valores cobrados são os exibidos no fechamento do plano no momento da adesão. Esta página descreve a regra que o sistema aplica; não altera preços.</p>\n<p>Horários em horário de Brasília. Preços em reais (R$). Atualizado em 25/11/2026.</p>\n<h2>1. Como funciona</h2>\n<p>Na inauguração, as condições dependem da <b>semana em que você adere</b> a um plano. O valor exato de cada plano e prazo aparece <b>somente no fechamento do plano</b>, na área do cliente, antes de pagar.</p>\n<p>O percentual da rampa incide somente sobre a faixa acima do <b>valor mínimo do plano</b> (o piso necessário para a Têmis atender com qualidade). Nenhum mês é cobrado abaixo desse piso. Por isso a vitrine não anuncia um único percentual sobre o preço cheio: o desconto efetivo varia conforme o plano, e o valor em reais é o que vale.</p>\n<h2>2. Calendário (datas fixas, que não reiniciam)</h2>\n<table class="tm-tab" style="min-width:0;width:100%">\n<thead><tr><th scope="col">Período de adesão</th><th scope="col">Vigência</th></tr></thead>\n<tbody>\n<tr><th scope="row">1ª semana de adesão</th><td>25/11/2026, 06:00 até 02/12/2026, 05:59</td></tr>\n<tr><th scope="row">2ª semana de adesão</th><td>02/12/2026, 06:00 até 09/12/2026, 05:59</td></tr>\n<tr><th scope="row">Rampa em diante</th><td>09/12/2026, 06:00 até 31/05/2027, 23:59</td></tr>\n</tbody>\n</table>\n<p>A rampa de lançamento termina em <b>31/05/2027, 23:59 (horário de Brasília)</b>. Depois dessa data, novas adesões seguem a tabela em vigor, sem a rampa. A data é fixa e não reinicia.</p>\n<h2>3. Prazo mensal</h2>\n<p>No mensal, a rampa vale nos primeiros meses (o 1º mês conforme a semana de adesão, depois a sequência da rampa), sempre respeitando o piso do plano. A partir do 6º mês, vale o preço cheio mensal. Os valores de cada mês aparecem no fechamento.</p>\n<h2>4. Prazo anual</h2>\n<p>No anual, a rampa vale dentro desse ano (12 meses), com o desconto de prazo anual vigente no checkout, respeitando o piso do plano no total do ano. Ao fim do ano, a renovação segue a tabela então em vigor, com aviso por e-mail 30 dias antes. Não há preço travado para sempre.</p>\n<h2>5. Planos de 2 anos e de 3 anos</h2>\n<p>A rampa de lançamento vale <b>somente no 1º ano</b>. Os anos seguintes seguem a tabela daquele prazo (sem a rampa), também respeitando o piso. O total antecipado aparece no fechamento. Ao fim do prazo contratado, a renovação segue a tabela então em vigor, com aviso por e-mail 30 dias antes. Não há preço travado para sempre.</p>\n<h2>6. Quem pode aderir</h2>\n<p>A rampa vale para quem contratar um dos planos listados em <a href="/planos/">Planos</a> (incluindo Base e Prática), nos prazos mensal, anual, de 2 anos ou de 3 anos, até 31/05/2027, 23:59 (horário de Brasília).</p>\n<p>O teste Têmis Essencial é um por CPF ou CNPJ e por e-mail, nas condições da página Planos e dos <a href="/termos/">Termos de uso</a>. A rampa incide sobre a adesão ao plano, não sobre o teste. As condições de lançamento valem uma única vez por CPF ou CNPJ (veja o item 12).</p>\n<h2>7. Sobre quais cobranças incide</h2>\n<p>A rampa incide sobre as cobranças dos planos e prazos citados acima. Tarefas avulsas, aplicativos Têmis avulsos e combos seguem o preço exibido no checkout de cada item.</p>\n<h2>8. Não cumulatividade</h2>\n<p>O desconto da rampa é aplicado automaticamente no fechamento do plano e não se acumula com outros cupons ou códigos promocionais. Uma indicação, quando houver, não soma um desconto extra em cima da rampa.</p>\n<h2>9. Direito de arrependimento</h2>\n<p>Na primeira contratação, você pode desistir em até 7 dias (art. 49 do Código de Defesa do Consumidor) e receber de volta o valor pago, pelo e-mail <a href="mailto:temis@e-pronaos.com">temis@e-pronaos.com</a>.</p>\n<h2>10. Encerramento antecipado</h2>\n<p>A Têmis pode encerrar a rampa de lançamento antes de 31/05/2027 somente sem prejuízo de quem já tiver aderido nas condições então vigentes. Quem já contratou mantém o valor e o prazo que contratou. A data publicada de encerramento não reinicia.</p>\n<h2>12. Uma vez por CPF ou CNPJ</h2>\n<p>As condições de lançamento da rampa valem <b>uma única vez por CPF ou CNPJ</b>. Quem já tiver aderido com aquele documento (nesta ou em outra conta) paga, no fechamento, o preço da tabela então em vigor, ainda respeitando o piso do plano quando a rampa não se aplicar. O documento é guardado somente como código protegido, irreversível; a Têmis não armazena o CPF ou o CNPJ em claro.</p>\n<h2>11. Outras condições</h2>\n<ul>\n<li>Preços em reais (R$), no Brasil.</li>\n<li>Minutas e peças geradas pela Têmis são rascunhos para revisão do advogado responsável.</li>\n<li>O detalhamento dos aplicativos Têmis de cada plano está em <a href="/planos/">Planos</a>.</li>\n<li>Termos gerais: <a href="/termos/">Termos de uso</a> e <a href="/privacidade/">Política de privacidade</a>.</li>\n</ul>\n<p><a class="btn" href="/planos/">Ver os planos</a></p>\n</main>'

def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def garante_palavras(texto, onde):
    low = (texto or "").lower()
    for w in PROIBIDAS:
        if w in low:
            raise SystemExit(f"[chamada_t2248u] palavra proibida «{w}» em {onde}")
    if re.search(r"\bgratis\b", low):
        raise SystemExit(f"[chamada_t2248u] palavra proibida «gratis» em {onde}")

def atualiza_faixa(html):
    if NS == "0":
        return html
    dados = json.dumps(JS_DADOS, ensure_ascii=False)
    html = re.sub(r'(<span class="tm-chegou-t" id="tm-chegou-t">)[\s\S]*?(</span>)', lambda m: m.group(1)+_esc(FAIXA)+m.group(2), html, count=1)
    html = re.sub(r'(<h2 id="tm-pop-t">)[\s\S]*?(</h2>)', lambda m: m.group(1)+_esc(TITULO)+m.group(2), html, count=1)
    html = re.sub(r'(<div id="tm-pop-d">)[\s\S]*?(</div>)', lambda m: m.group(1)+JANELA+m.group(2), html, count=1)
    html = re.sub(r"<script>window\.__TEMICHEGOU=[\s\S]*?</script>", "<script>window.__TEMICHEGOU=" + dados + ";</script>", html, count=1)
    if MARCA not in html:
        html = html.replace("</body>", MARCA + "</body>", 1)
    return html

def atualiza_planos(html):
    week_end = int((SEM or {}).get("fim_epoch") or FIM_EP)
    if NS == "3":
        week_end = FIM_EP
    cd = f'<span class="tm-cd" data-fim="{week_end}">—</span>'
    geral = (
        '<div class="tm-lanc-box" role="status">'
        "<b>Condições de lançamento por semana de adesão</b> · "
        "o valor exato de cada plano e prazo aparece no fechamento do plano, na área do cliente. "
        f"Esta semana de adesão acaba em {cd} "
        '<small>(horário de Brasília). A rampa respeita o piso mínimo do plano. Nos prazos de 2 anos e de 3 anos, '
        "a rampa vale só no 1º ano; depois, a tabela do prazo. Inscrição até 31/05/2027, 23h59, horário de Brasília. "
        '<a href="/regras-da-promocao/">Regras da promoção</a>.</small></div>'
    )
    html = re.sub(r'<div class="tm-lanc-box"[^>]*>[\s\S]*?</div>', geral, html, count=1)
    nota = (
        "Condições de lançamento por semana de adesão: o valor exato aparece no fechamento do plano. "
        "A rampa respeita o piso mínimo do plano. Nos prazos de 2 anos e de 3 anos, a rampa vale só no 1º ano. "
        "Vale para quem contrata até 31/05/2027."
    )
    def bloco_preco(m):
        bloco = m.group(0)
        cm = re.search(r'<span class="tm-cheio"[^>]*>([\s\S]*?)</span>', bloco)
        if not cm:
            return bloco
        cheio = cm.group(1)
        def rpreco(mm):
            return mm.group(1) + cheio + mm.group(2)
        bloco = re.sub(
            r'(<span class="tm-rampa-preco"[^>]*>)[\s\S]*?(</span>)',
            rpreco,
            bloco,
            count=1,
        )
        def rnota(mm):
            return mm.group(1) + nota + mm.group(2)
        bloco = re.sub(
            r'(<small class="tm-rampa"[^>]*>)[\s\S]*?(</small>)',
            rnota,
            bloco,
            count=1,
        )
        return bloco
    html = re.sub(r'<div class="tm-preco">[\s\S]*?</div>', bloco_preco, html)
    def tabela(m):
        row = m.group(0)
        def cel(mm):
            inner = mm.group(0)
            ch = re.search(r"cheio (R\$ [^<]+)", inner)
            hint = (" · cheio " + ch.group(1)) if ch else ""
            return (
                '<span class="tm-cel-fechamento"><b>no fechamento</b>'
                "<small>valor exato no fechamento do plano" + hint + "</small></span>"
            )
        row = re.sub(r'<span class="tm-lanc"[^>]*>[\s\S]*?</span>', cel, row)
        return row
    html = re.sub(r'<tr><th scope="row">1º mês</th>[\s\S]*?</tr>', tabela, html, count=1)
    html = html.replace(
        "anual com 15% de desconto sobre o ano da rampa.",
        "anual com o desconto de prazo vigente no fechamento do plano.",
    )
    js = (
        "<script>(function(){"
        "function tickCd(){"
        "document.querySelectorAll('.tm-cd,[data-fim].cd').forEach(function(e){"
        "var f=+e.dataset.fim*1000; if(!f) return;"
        "var s=Math.max(0,Math.floor((f-Date.now())/1000));"
        "var d=Math.floor(s/86400); s%=86400;"
        "var h=Math.floor(s/3600); s%=3600;"
        "var m=Math.floor(s/60); s%=60;"
        "var p=function(n){return String(n).padStart(2,'0');};"
        "e.textContent=(f>Date.now())?(d+' dias '+p(h)+'h '+p(m)+'min '+p(s)+'s'):'encerrado';"
        "});}"
        "function indicacao(){"
        "var p=new URLSearchParams(location.search);"
        "var code=(p.get('indicacao')||'').toUpperCase();"
        "if(code){try{localStorage.setItem('temis_indicacao',code);}catch(e){}}"
        "else{try{code=localStorage.getItem('temis_indicacao')||'';}catch(e){code='';}}"
        "if(!code) return;"
        "document.querySelectorAll('a[href*=\"/conta/\"]').forEach(function(a){"
        "try{var u=new URL(a.getAttribute('href'),location.origin);"
        "if(!u.searchParams.has('indicacao')) u.searchParams.set('indicacao',code);"
        "a.setAttribute('href',u.pathname+u.search+u.hash);}catch(e){}"
        "});}"
        "tickCd(); indicacao(); setInterval(tickCd,1000);"
        "})();</script>"
    )
    html = re.sub(
        r"<script>window\.__TEMIRAMPA=[\s\S]*?</script>\s*<script>[\s\S]*?</script>",
        "<!--temirampa-desligado-t2248u-->" + js,
        html,
        count=1,
    )
    return html

def pagina_regras(molde):
    s = molde
    s = re.sub(r"(<title>)[^<]+(</title>)", r"\g<1>Regras da promoção · Têmis\g<2>", s, count=1)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>Regras da rampa de lançamento da Têmis: condições por semana de adesão, valor exato no fechamento do plano, piso mínimo, anual e prazos de 2 e 3 anos.\g<2>", s, count=1)
    s = re.sub(r"<main\b.*?</main>", REGRAS_MAIN, s, count=1, flags=re.S)
    s = atualiza_faixa(s)
    garante_palavras(REGRAS_MAIN, "/regras-da-promocao/")
    return s

def main():
    if not OUT.exists():
        print("[chamada_t2248u] sem pasta out/")
        return
    garante_palavras(FAIXA + TITULO + JANELA, "faixa/janela")
    feitos = {"paginas": 0, "regras": False, "planos": False}
    molde = None
    for cand in (OUT / "regras-da-promocao" / "index.html", OUT / "suporte" / "index.html", OUT / "sugestoes" / "index.html"):
        if cand.exists():
            molde = cand.read_text(encoding="utf-8")
            break
    if molde:
        d = OUT / "regras-da-promocao"
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina_regras(molde), encoding="utf-8")
        feitos["regras"] = True
    for f in OUT.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        if "tm-chegou" not in s and not str(f).endswith("/planos/index.html"):
            continue
        novo = atualiza_faixa(s) if "tm-chegou" in s else s
        if str(f).endswith("/planos/index.html"):
            n2 = atualiza_planos(novo)
            if n2 != novo:
                feitos["planos"] = True
            novo = n2
        if novo != s:
            f.write_text(novo, encoding="utf-8")
            feitos["paginas"] += 1
    print("[chamada_t2248u]", "semana=" + NS, feitos)

if __name__ == "__main__":
    main()
