#!/usr/bin/env python3
"""t2240u — chamada da rampa de lançamento (faixa + janela + /regras-da-promocao/).

Lê a mesma tabela pública (precos_publicos.json) que espelha lancamento.rampa
do checkout (vendas_config). Não altera preços, cupons nem a lógica de cobrança.

A faixa e a janela trocam sozinhas por semana (1 / 2 / 3+ / fim) no navegador,
sem novo deploy. A janela aparece uma vez por visitante, é dispensável, não
entra em /conta nem em passos de checkout, e não trava a página.

Rollback: apagar as 2 linhas deste script no build.sh (comentário + python3).
O PWA continua por último.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--chamada-t2240u-->"
PROIBIDAS = ("assinatura", "gratuita", "grátis", "adapta")
SKIP_REL = (
    "/conta",
    "/login",
    "/sair",
    "/billing",
    "/painel",
    "/uploads",
    "/estacao",
    "/regras-da-promocao",
)
DADOS = json.loads((ROOT / "precos_publicos.json").read_text(encoding="utf-8"))
RAMPA = DADOS.get("rampa") or {}
SEMANAS = RAMPA.get("semanas") or {}
FIM_TXT = (DADOS.get("lancamento") or {}).get("fim_texto") or RAMPA.get("inscricao_ate") or "31/05/2027"
FIM_EP = int((DADOS.get("lancamento") or {}).get("fim_epoch") or RAMPA.get("inscricao_epoch") or 1811818799)
UTM_OFERTA = "/planos/?utm_source=site&amp;utm_medium=faixa&amp;utm_campaign=inauguracao_t2235u"
UTM_POP = "/planos/?utm_source=site&amp;utm_medium=janela&amp;utm_campaign=inauguracao_t2235u"
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


def fim_curto(bloco, fallback):
    t = (bloco or {}).get("fim_texto") or fallback
    # já vem como "02/12/2026 05:59, horário de Brasília"
    return t


def textos(n, sem):
    """Textos da faixa e da janela. n='1'|'2'|'3'."""
    off = int((sem or {}).get("mes1_pct") or { "1": 78, "2": 65, "3": 50 }.get(n, 50))
    s1, s2, s3 = SEMANAS.get("1") or {}, SEMANAS.get("2") or {}, SEMANAS.get("3") or {}
    f1 = fim_curto(s1, "02/12/2026 05:59, horário de Brasília")
    f2 = fim_curto(s2, "09/12/2026 05:59, horário de Brasília")
    f3 = fim_curto(s3, "31/05/2027 23:59, horário de Brasília")
    longos = (
        "Vale também nos planos anual, de 2 anos e de 3 anos: o valor menor "
        "fica travado no prazo contratado (não é o percentual do 1º mês sobre o período inteiro)."
    )
    if n == "1":
        faixa = (
            f"1ª semana de adesão: {off}% de desconto no 1º mês até {f1}. "
            f"Na semana 2 o desconto do 1º mês passa a {int(s2.get('mes1_pct') or 65)}%; "
            f"depois, a {int(s3.get('mes1_pct') or 50)}% até {f3}, quando a rampa de lançamento termina. "
            + longos
        )
        titulo = "Chegou a Têmis · 1ª semana de adesão"
        janela = (
            f"<p>Quem aderir a um plano até <b>{f1}</b> tem <b>{off}% de desconto no 1º mês</b> "
            f"do prazo mensal. Nos meses seguintes do mensal, o desconto é 40%, 30%, 20% e 10%; "
            f"a partir do 6º mês, vale o preço cheio.</p>"
            f"<p>O mesmo calendário vale para os planos <b>anual, de 2 anos e de 3 anos</b>: "
            f"o extra do 1º mês entra no total antecipado, junto com a rampa dos meses 2 a 5 e o "
            f"preço cheio do restante do prazo, menos o desconto de prazo exibido no checkout. "
            f"Esse total fica travado só no prazo contratado. A renovação segue a tabela então em vigor. "
            f"Não há travamento vitalício de preço.</p>"
            f"<p>Na semana 2 (a partir de 02/12/2026, 06:00, horário de Brasília), o desconto do 1º mês "
            f"passa a {int(s2.get('mes1_pct') or 65)}%. A partir de 09/12/2026, 06:00, passa a "
            f"{int(s3.get('mes1_pct') or 50)}% até {f3}, quando a rampa de lançamento termina. "
            f"Depois dessa data, novas adesões seguem a tabela em vigor, sem a rampa.</p>"
        )
    elif n == "2":
        faixa = (
            f"2ª semana de adesão: {off}% de desconto no 1º mês até {f2}. "
            f"A partir de 09/12/2026, 06:00, o desconto do 1º mês passa a {int(s3.get('mes1_pct') or 50)}% "
            f"até {f3}, quando a rampa de lançamento termina. "
            + longos
        )
        titulo = "Chegou a Têmis · 2ª semana de adesão"
        janela = (
            f"<p>Quem aderir a um plano até <b>{f2}</b> tem <b>{off}% de desconto no 1º mês</b> "
            f"do prazo mensal. Nos meses seguintes do mensal, o desconto é 40%, 30%, 20% e 10%; "
            f"a partir do 6º mês, vale o preço cheio.</p>"
            f"<p>O mesmo calendário vale para os planos <b>anual, de 2 anos e de 3 anos</b>: "
            f"o extra do 1º mês entra no total antecipado, junto com a rampa dos meses 2 a 5 e o "
            f"preço cheio do restante do prazo, menos o desconto de prazo exibido no checkout. "
            f"Esse total fica travado só no prazo contratado. A renovação segue a tabela então em vigor. "
            f"Não há travamento vitalício de preço.</p>"
            f"<p>A partir de 09/12/2026, 06:00 (horário de Brasília), o desconto do 1º mês passa a "
            f"{int(s3.get('mes1_pct') or 50)}% até {f3}, quando a rampa de lançamento termina. "
            f"Depois dessa data, novas adesões seguem a tabela em vigor, sem a rampa.</p>"
        )
    else:
        faixa = (
            f"Rampa de lançamento: {off}% de desconto no 1º mês. Adesão até {f3}. "
            f"Depois dessa data, novas adesões seguem a tabela em vigor, sem a rampa. "
            + longos
        )
        titulo = "Chegou a Têmis · rampa de lançamento"
        janela = (
            f"<p>Quem aderir a um plano até <b>{f3}</b> tem <b>{off}% de desconto no 1º mês</b> "
            f"do prazo mensal. Nos meses seguintes do mensal, o desconto é 40%, 30%, 20% e 10%; "
            f"a partir do 6º mês, vale o preço cheio.</p>"
            f"<p>O mesmo calendário vale para os planos <b>anual, de 2 anos e de 3 anos</b>: "
            f"o extra do 1º mês entra no total antecipado, junto com a rampa dos meses 2 a 5 e o "
            f"preço cheio do restante do prazo, menos o desconto de prazo exibido no checkout. "
            f"Esse total fica travado só no prazo contratado. A renovação segue a tabela então em vigor. "
            f"Não há travamento vitalício de preço.</p>"
            f"<p>Depois de {f3}, a rampa de lançamento termina e novas adesões seguem a tabela em vigor, "
            f"sem esses descontos da rampa. A data de encerramento não reinicia.</p>"
        )
    return off, faixa, titulo, janela


NS, SEM = semana_agora()
if NS == "0":
    OFF, FAIXA, TITULO, JANELA = 0, "", "", ""
else:
    OFF, FAIXA, TITULO, JANELA = textos(NS, SEM)

JS_DADOS = {
    "semanas": {
        k: {
            "fim_epoch": v.get("fim_epoch"),
            "mes1_pct": v.get("mes1_pct"),
            "fim_texto": v.get("fim_texto"),
            "inicio_texto": v.get("inicio_texto"),
        }
        for k, v in SEMANAS.items()
    },
    "inscricao_epoch": FIM_EP,
    "textos": {n: {
        "faixa": textos(n, SEMANAS.get(n) or {})[1],
        "titulo": textos(n, SEMANAS.get(n) or {})[2],
        "janela": textos(n, SEMANAS.get(n) or {})[3],
    } for n in ("1", "2", "3") if SEMANAS.get(n)},
}


CSS = r"""
/* t2240u — faixa e janela da rampa (azul e dourado) */
.tm-chegou{position:relative;z-index:60;display:flex;flex-wrap:wrap;gap:.45rem .85rem;align-items:center;justify-content:center;
 padding:.65rem 1.1rem;background:linear-gradient(90deg,#0b1a33,#13284f 50%,#0b1a33);
 border-bottom:1px solid rgba(224,192,120,.55);color:#eef2ff;font:500 .9rem/1.45 Inter,system-ui,sans-serif;text-align:center}
.tm-chegou b.tm-chegou-marca{color:#f6dd9a;letter-spacing:.06em;text-transform:uppercase;font-weight:700}
.tm-chegou .tm-chegou-t{max-width:62rem}
.tm-chegou-links{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;justify-content:center}
.tm-chegou a{color:#1a1204;background:#e0c078;padding:.28rem .75rem;border-radius:999px;font-weight:700;text-decoration:none;white-space:nowrap}
.tm-chegou a.tm-chegou-sec{background:transparent;color:#f6dd9a;border:1px solid rgba(224,192,120,.75)}
.tm-chegou a:focus-visible,.tm-pop-card a:focus-visible,.tm-pop-x:focus-visible{outline:2px solid #f6dd9a;outline-offset:2px}
.tm-regras-promo{margin:.4rem 0 1rem;font-size:.9rem}
.tm-regras-promo a{color:#f0d58c}
.tm-pop{position:fixed;inset:0;z-index:300;display:flex;align-items:center;justify-content:center;padding:1rem;pointer-events:none}
.tm-pop[hidden]{display:none!important}
.tm-pop.is-on{pointer-events:auto}
.tm-pop-backdrop{position:absolute;inset:0;background:rgba(6,13,27,.45)}
.tm-pop-card{position:relative;z-index:1;width:min(32rem,100%);max-height:min(88vh,40rem);overflow:hidden;padding:1.4rem 1.45rem 1.1rem;
 display:flex;flex-direction:column;border:1px solid rgba(224,192,120,.55);border-radius:18px;background:linear-gradient(165deg,#0d1c38,#13284f 55%,#0b1a33);
 color:#eef2ff;box-shadow:0 18px 50px rgba(0,0,0,.35);font:400 .95rem/1.5 Inter,system-ui,sans-serif}
.tm-pop-card #tm-pop-d{overflow:auto;flex:1 1 auto;min-height:0;padding-right:.15rem}
.tm-pop-kicker{margin:0 0 .25rem;color:#f6dd9a;letter-spacing:.08em;text-transform:uppercase;font-size:.72rem;font-weight:700}
.tm-pop-card h2{margin:0 0 .7rem;font-family:Georgia,serif;font-weight:400;color:#f6dd9a;font-size:1.45rem;letter-spacing:-.01em}
.tm-pop-card p{margin:0 0 .7rem;color:#c9d3ee}
.tm-pop-card p:last-of-type{margin-bottom:0}
.tm-pop-acoes{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem!important;flex:0 0 auto}
.tm-pop-cta{display:inline-block;padding:.55rem 1rem;border-radius:999px;background:linear-gradient(180deg,#f6dd9a,#d9b25c);
 color:#1a1204!important;font-weight:700;text-decoration:none}
.tm-pop-sec{display:inline-block;padding:.5rem .95rem;border-radius:999px;border:1px solid rgba(224,192,120,.7);
 color:#f6dd9a!important;text-decoration:none;font-weight:600}
.tm-pop-x{position:absolute;top:.55rem;right:.55rem;width:2.2rem;height:2.2rem;border:0;border-radius:999px;
 background:transparent;color:#f6dd9a;font-size:1.4rem;line-height:1;cursor:pointer}
@media (prefers-reduced-motion:reduce){.tm-pop-card,.tm-chegou{transition:none}}
@media (max-width:640px){.tm-chegou{font-size:.86rem;padding:.55rem .8rem}.tm-pop-card{padding:1.2rem 1.05rem 1.1rem}}
"""

JS = r"""
(function(){
  var D = window.__TEMICHEGOU || {};
  var semanas = D.semanas || {};
  var textos = D.textos || {};
  var insc = +D.inscricao_epoch || 1811818799;
  var KEY = "temis_promo_t2240u_visto";
  function agora(){ return Date.now()/1000; }
  function nsem(){
    var s1=semanas["1"]||{}, s2=semanas["2"]||{}, s3=semanas["3"]||{};
    var t=agora();
    if(s3.fim_epoch && t>s3.fim_epoch) return "0";
    if(!s1.fim_epoch || t<=s1.fim_epoch) return "1";
    if(!s2.fim_epoch || t<=s2.fim_epoch) return "2";
    return "3";
  }
  function skipPop(){
    var p = (location.pathname||"/").toLowerCase();
    var bloq = ["/conta","/login","/sair","/billing","/painel","/uploads","/estacao","/regras-da-promocao"];
    for(var i=0;i<bloq.length;i++){ if(p===bloq[i] || p.indexOf(bloq[i]+"/")===0) return true; }
    return false;
  }
  function aplicarFaixa(){
    var n = nsem();
    var bar = document.getElementById("tm-chegou");
    if(n==="0"){ if(bar) bar.remove(); return n; }
    var t = (textos[n]||{}).faixa;
    var el = document.getElementById("tm-chegou-t");
    if(el && t) el.textContent = t;
    if(bar) bar.removeAttribute("hidden");
    return n;
  }
  function fechar(pop, motivo){
    if(!pop) return;
    pop.classList.remove("is-on");
    pop.setAttribute("hidden","");
    pop.setAttribute("aria-hidden","true");
    try{ localStorage.setItem(KEY,"1"); }catch(e){}
    var x = pop.__tmPrevFocus;
    if(x && x.focus) try{ x.focus(); }catch(e){}
  }
  function abrir(pop, titulo){
    var card = pop.querySelector(".tm-pop-card");
    var tt = document.getElementById("tm-pop-t");
    var dd = document.getElementById("tm-pop-d");
    var pack = textos[titulo] || textos[nsem()] || {};
    if(tt && pack.titulo) tt.textContent = pack.titulo;
    if(dd && pack.janela) dd.innerHTML = pack.janela;
    pop.__tmPrevFocus = document.activeElement;
    pop.removeAttribute("hidden");
    pop.classList.add("is-on");
    pop.setAttribute("aria-hidden","false");
    var btn = pop.querySelector(".tm-pop-x");
    if(btn) btn.focus();
  }
  function ligarJanela(){
    var pop = document.getElementById("tm-promo-pop");
    if(!pop) return;
    var n = nsem();
    if(n==="0" || skipPop()){ fechar(pop); return; }
    var visto = false;
    try{ visto = localStorage.getItem(KEY)==="1"; }catch(e){}
    pop.addEventListener("click", function(ev){
      if(ev.target && ev.target.getAttribute && ev.target.hasAttribute("data-close")) fechar(pop);
    });
    var x = pop.querySelector(".tm-pop-x");
    if(x) x.addEventListener("click", function(){ fechar(pop); });
    document.addEventListener("keydown", function(ev){
      if(ev.key==="Escape" && pop.classList.contains("is-on")) fechar(pop);
    });
    if(!visto) abrir(pop, n);
  }
  var n = aplicarFaixa();
  if(n && n!=="0") ligarJanela();
})();
"""


def faixa_html():
    if NS == "0" or not FAIXA:
        return ""
    dados = json.dumps(JS_DADOS, ensure_ascii=False)
    # texto estático da semana do build; o script troca se a semana mudar
    return (
        f'{MARCA}<div class="tm-chegou" role="status" id="tm-chegou">'
        f'<b class="tm-chegou-marca">Chegou a Têmis</b>'
        f'<span class="tm-chegou-t" id="tm-chegou-t">{_esc(FAIXA)}</span>'
        f'<span class="tm-chegou-links">'
        f'<a href="{UTM_OFERTA}">Ver a oferta</a>'
        f'<a class="tm-chegou-sec" href="{REGRAS}">Regras da promoção</a>'
        f"</span></div>"
        f"{popup_html()}"
        f"<script>window.__TEMICHEGOU={dados};</script>"
        f"<script>{JS}</script>"
    )


def popup_html():
    return (
        f'<div id="tm-promo-pop" class="tm-pop" hidden aria-hidden="true">'
        f'<div class="tm-pop-backdrop" data-close tabindex="-1" aria-hidden="true"></div>'
        f'<div class="tm-pop-card" role="dialog" aria-modal="true" aria-labelledby="tm-pop-t" aria-describedby="tm-pop-d">'
        f'<button type="button" class="tm-pop-x" aria-label="Fechar a janela da promoção">×</button>'
        f'<p class="tm-pop-kicker">Inauguração</p>'
        f'<h2 id="tm-pop-t">{_esc(TITULO)}</h2>'
        f'<div id="tm-pop-d">{JANELA}</div>'
        f'<p class="tm-pop-acoes"><a class="tm-pop-cta" href="{UTM_POP}">Ver os planos</a>'
        f'<a class="tm-pop-sec" href="{REGRAS}">Regras da promoção</a></p>'
        f"</div></div>"
    )


def _esc(s):
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def rel_of(p: Path) -> str:
    rel = "/" + str(p.relative_to(OUT)).replace("\\", "/")
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel.endswith(".html") and not rel.endswith("/index.html"):
        rel = rel[: -len(".html")]
        if not rel.endswith("/"):
            # keep file pages as /x or /x.html? public pages use dirs
            rel = rel
    return rel


def deve_pular(rel: str, p: Path) -> bool:
    r = (rel or "/").lower()
    if p.name in ("404.html", "offline.html"):
        return True
    if re.fullmatch(r"google[0-9a-f]+\.html", p.name, re.I):
        return True
    for s in SKIP_REL:
        if r == s or r.startswith(s + "/"):
            return True
    return False


def limpa_faixa_antiga(html: str) -> str:
    """Troca a faixa curta do t2235u (só na home) pela nova, sem duplicar."""
    html = re.sub(
        r'<!--suporte-t2235u-->\s*<div class="tm-chegou"[^>]*>[\s\S]*?</div>\s*<script>[\s\S]*?</script>',
        "",
        html,
        count=1,
    )
    # se um build anterior deste script já injetou, remove para reaplicar
    html = re.sub(
        r'<!--chamada-t2240u-->[\s\S]*?<script>window\.__TEMICHEGOU=[\s\S]*?</script>\s*<script>[\s\S]*?</script>',
        "",
        html,
        count=1,
    )
    return html


def injeta_css(html: str) -> str:
    if "t2240u — faixa e janela" in html:
        return html
    return html.replace("</head>", f"<style>{CSS}</style></head>", 1)


def injeta_faixa(html: str) -> str:
    bloco = faixa_html()
    if not bloco:
        return html
    html = limpa_faixa_antiga(html)
    if MARCA in html:
        return html
    html = injeta_css(html)
    if re.search(r"<body\b[^>]*>", html):
        html = re.sub(r"(<body\b[^>]*>)", r"\1" + bloco, html, count=1)
    return html


def garante_palavras(texto: str, onde: str):
    low = texto.lower()
    for w in PROIBIDAS:
        if w in low:
            # 'gratis' ascii também
            raise SystemExit(f"[chamada_t2240u] palavra proibida «{w}» em {onde}")
    if re.search(r"\bgratis\b", low):
        raise SystemExit(f"[chamada_t2240u] palavra proibida «gratis» em {onde}")


REGRAS_MAIN = f"""<main id="main" class="wrap" style="position:relative;z-index:2;padding:2.5rem 0 3rem">
<nav class="crumbs" aria-label="Você está aqui"><a href="/">Início</a> › <span>Regras da promoção</span></nav>
<p class="kicker">Rampa de lançamento</p>
<h1>Regras da promoção</h1>
<p class="lead">Estas são as regras da rampa de lançamento da Têmis. Os valores cobrados são os do checkout no momento da adesão. Esta página descreve a regra que o sistema já aplica; não altera preços.</p>
<p>Horários em horário de Brasília. Preços em reais (R$). Atualizado em 25/11/2026.</p>

<h2>1. O que é a rampa</h2>
<p>Na inauguração, o desconto do <b>1º mês</b> depende da <b>semana em que você adere</b> a um plano. Esse percentual não incide sobre o período inteiro do plano. Depois do 1º mês, no prazo mensal, os descontos seguintes são fixos (40%, 30%, 20% e 10%). A partir do 6º mês do mensal, vale o preço cheio.</p>
<p>Os planos anual, de 2 anos e de 3 anos entram no mesmo calendário: o extra do 1º mês é diluído no total antecipado do prazo contratado, junto com a rampa dos meses 2 a 5 e o preço cheio do restante do prazo, menos o desconto de prazo que o checkout exibir. Esse total fica travado só nesse prazo. Não há travamento vitalício de preço.</p>

<h2>2. Calendário (datas fixas, que não reiniciam)</h2>
<table class="tm-tab" style="min-width:0;width:100%">
<thead><tr><th scope="col">Período de adesão</th><th scope="col">Desconto no 1º mês</th></tr></thead>
<tbody>
<tr><th scope="row">1ª semana: 25/11/2026, 06:00 até 02/12/2026, 05:59</th><td>78%</td></tr>
<tr><th scope="row">2ª semana: 02/12/2026, 06:00 até 09/12/2026, 05:59</th><td>65%</td></tr>
<tr><th scope="row">A partir de 09/12/2026, 06:00, até 31/05/2027, 23:59</th><td>50%</td></tr>
</tbody>
</table>
<p>A rampa de lançamento termina em <b>31/05/2027, 23:59 (horário de Brasília)</b>. Depois dessa data, novas adesões seguem a tabela em vigor, sem os descontos desta rampa. A data de encerramento é fixa e não reinicia.</p>

<h2>3. Como o mensal é cobrado</h2>
<ul>
<li>1º mês: percentual da semana de adesão (78%, 65% ou 50% sobre o preço cheio mensal).</li>
<li>2º mês: 40% de desconto sobre o preço cheio mensal.</li>
<li>3º mês: 30%.</li>
<li>4º mês: 20%.</li>
<li>5º mês: 10%.</li>
<li>A partir do 6º mês: preço cheio mensal.</li>
</ul>
<p>O valor exato de cada plano aparece em <a href="/planos/">Planos</a> e é confirmado no checkout.</p>

<h2>4. Planos anual, de 2 anos e de 3 anos</h2>
<p>Quem aderir a esses prazos dentro de uma das janelas acima antecipa o período contratado (12, 24 ou 36 meses) num único valor. Esse valor é a soma da rampa no período (1º mês da semana de adesão, meses 2 a 5 com 40%, 30%, 20% e 10%, e o restante no preço cheio), menos o desconto de prazo vigente no checkout no momento da adesão. Hoje esse desconto de prazo, que não se confunde com a rampa, é o exibido no checkout (na configuração atual: 15% no anual, 20% em 2 anos e 25% em 3 anos).</p>
<p>O valor menor assim calculado fica travado apenas no prazo contratado. Ao fim desse prazo, a renovação segue a tabela então em vigor, com aviso por e-mail 30 dias antes. Não há preço travado para sempre.</p>
<p>No cartão, o percentual aplicado pelo intermediador de pagamento pode ter no máximo duas casas decimais; quando isso ocorre, a diferença (de até alguns reais nos planos de maior valor) fica a favor de quem contrata. Pix e Mercado Pago usam o centavo exato. Vale o valor apresentado e confirmado no checkout.</p>

<h2>5. Quem pode aderir</h2>
<p>A rampa vale para quem contratar um dos planos listados em <a href="/planos/">Planos</a> (incluindo Base e Prática), nos prazos mensal, anual, de 2 anos ou de 3 anos, até 31/05/2027, 23:59 (horário de Brasília).</p>
<p>O teste Têmis Essencial é um por CPF ou CNPJ e por e-mail, nas condições da página Planos e dos <a href="/termos/">Termos de uso</a>. A rampa de lançamento incide sobre a adesão ao plano, não sobre o teste.</p>

<h2>6. Sobre quais cobranças incide</h2>
<p>A rampa incide sobre as cobranças dos planos e prazos citados acima. Tarefas avulsas, aplicativos Têmis avulsos e combos seguem o preço exibido no checkout de cada item, e não recebem automaticamente o percentual da semana.</p>

<h2>7. Não cumulatividade</h2>
<p>O desconto da rampa é aplicado automaticamente no checkout e não se acumula com outros cupons ou códigos promocionais. Uma indicação, quando houver, substitui o cupom da semana no prazo mensal; não soma um desconto extra em cima da rampa.</p>

<h2>8. Direito de arrependimento</h2>
<p>Na primeira contratação, você pode desistir em até 7 dias (art. 49 do Código de Defesa do Consumidor) e receber de volta o valor pago, pelo e-mail <a href="mailto:temis@e-pronaos.com">temis@e-pronaos.com</a>.</p>

<h2>9. Encerramento antecipado</h2>
<p>A Têmis pode encerrar a rampa de lançamento antes de 31/05/2027 somente sem prejuízo de quem já tiver aderido nas condições então vigentes. Quem já contratou mantém o valor e o prazo que contratou. A data publicada de encerramento não reinicia.</p>

<h2>10. Outras condições</h2>
<ul>
<li>Preços em reais (R$), no Brasil.</li>
<li>Minutas e peças geradas pela Têmis são rascunhos para revisão do advogado responsável.</li>
<li>O detalhamento dos aplicativos Têmis de cada plano está em <a href="/planos/">Planos</a>.</li>
<li>Termos gerais: <a href="/termos/">Termos de uso</a> e <a href="/privacidade/">Política de privacidade</a>.</li>
</ul>
<p><a class="btn" href="/planos/">Ver os planos</a></p>
</main>"""


def pagina_regras(molde: str) -> str:
    s = molde
    s = s.replace("Sugestões · Têmis", "Regras da promoção · Têmis")
    s = s.replace("Suporte · Têmis", "Regras da promoção · Têmis")
    s = s.replace("https://agentetemis.com/sugestoes", "https://agentetemis.com/regras-da-promocao")
    s = s.replace("https://agentetemis.com/suporte", "https://agentetemis.com/regras-da-promocao")
    s = s.replace("https://agentetemis.com/sugestoes/", "https://agentetemis.com/regras-da-promocao/")
    s = s.replace("https://agentetemis.com/suporte/", "https://agentetemis.com/regras-da-promocao/")
    # meta description (várias formas)
    s = re.sub(
        r'(<meta name="description" content=")[^"]*(")',
        r"\1Regras da rampa de lançamento da Têmis: desconto do 1º mês por semana de adesão (78%, 65% ou 50%), calendário até 31/05/2027, 23:59 (horário de Brasília), planos mensal, anual, de 2 anos e de 3 anos.\2",
        s,
        count=1,
    )
    s = re.sub(
        r'(property="og:title" content=")[^"]*(")',
        r"\1Regras da promoção · Têmis\2",
        s,
        count=1,
    )
    s = re.sub(
        r'(property="og:description" content=")[^"]*(")',
        r"\1Rampa de lançamento da Têmis: percentual do 1º mês conforme a semana de adesão, até 31/05/2027, 23:59 (horário de Brasília).\2",
        s,
        count=1,
    )
    s = re.sub(
        r'(property="og:url" content=")[^"]*(")',
        r"\1https://agentetemis.com/regras-da-promocao/\2",
        s,
        count=1,
    )
    s = re.sub(
        r'(rel="canonical" href=")[^"]*(")',
        r"\1https://agentetemis.com/regras-da-promocao/\2",
        s,
        count=1,
    )
    s = re.sub(
        r'(hreflang="pt-BR" href=")[^"]*(")',
        r"\1https://agentetemis.com/regras-da-promocao/\2",
        s,
    )
    s = re.sub(
        r'(hreflang="x-default" href=")[^"]*(")',
        r"\1https://agentetemis.com/regras-da-promocao/\2",
        s,
    )
    s = re.sub(r"<main\b.*?</main>", REGRAS_MAIN, s, count=1, flags=re.S)
    # não indexar como suporte; garantir indexação
    if "noindex" in s.lower() and 'name="robots"' in s.lower():
        s = re.sub(
            r'<meta[^>]*name="robots"[^>]*>',
            '<meta name="robots" content="index,follow">',
            s,
            count=1,
            flags=re.I,
        )
    if 'rel="canonical"' not in s:
        s = s.replace(
            "</head>",
            '<link rel="canonical" href="https://agentetemis.com/regras-da-promocao/">'
            '<link rel="alternate" hreflang="pt-BR" href="https://agentetemis.com/regras-da-promocao/">'
            '<link rel="alternate" hreflang="x-default" href="https://agentetemis.com/regras-da-promocao/"></head>',
            1,
        )
    s = injeta_css(s)
    # nesta página: faixa sim, janela não (o JS respeita o path)
    s = injeta_faixa(s)
    garante_palavras(REGRAS_MAIN, "/regras-da-promocao/")
    garante_palavras(s[s.find("<main"):s.find("</main>") + 8] if "<main" in s else REGRAS_MAIN, "main regras")
    return s


def atualiza_sitemap():
    sm = OUT / "sitemap.xml"
    if not sm.exists():
        return False
    x = sm.read_text(encoding="utf-8")
    if "agentetemis.com/regras-da-promocao" in x:
        return False
    if "</urlset>" in x:
        entry = '<url><loc>https://agentetemis.com/regras-da-promocao/</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>'
        sm.write_text(x.replace("</urlset>", entry + "</urlset>"), encoding="utf-8")
        return True
    return False


def link_planos(html: str) -> str:
    if 'class="tm-regras-promo"' in html:
        return html
    if 'class="tm-lanc-box"' not in html:
        return html
    return re.sub(
        r'(<div class="tm-lanc-box"[^>]*>[\s\S]*?</div>)',
        r'\1<p class="tm-regras-promo"><a href="/regras-da-promocao/">Regras da promoção</a></p>',
        html,
        count=1,
    )


def selftest():
    # datas: durante semana 1, 2, 3 e depois do fim
    cases = [
        (1795597200 + 3600, "1", 78),  # 25/11 07:00
        (1796201999, "1", 78),          # último segundo s1
        (1796202000, "2", 65),
        (1796806799, "2", 65),
        (1796806800, "3", 50),
        (1811818799, "3", 50),
        (1811818800, "0", 0),
    ]
    for ep, esper, off in cases:
        n, sem = semana_agora(ep)
        assert n == esper, (ep, n, esper)
        if n != "0":
            o, faixa, titulo, janela = textos(n, sem)
            assert o == off, (n, o, off)
            assert f"{off}% de desconto no 1º mês" in faixa
            assert "horário de Brasília" in faixa
            assert "anual" in faixa and "2 anos" in faixa and "3 anos" in faixa
            assert "1º mês" in janela
            for w in PROIBIDAS + ("gratis",):
                blob = (faixa + titulo + janela).lower()
                assert w not in blob, w
            # não afirmar 78% sobre o período inteiro
            assert "78% de desconto no plano" not in faixa
            assert "percentual do 1º mês sobre o período inteiro" in faixa
    # regras
    for w in PROIBIDAS + ("gratis",):
        assert w not in REGRAS_MAIN.lower(), w
    print("[chamada_t2240u] selftest ok")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    if not OUT.exists():
        print("[chamada_t2240u] sem pasta out/")
        return
    garante_palavras(FAIXA + TITULO + JANELA, "faixa/janela")
    feitos = {"paginas": 0, "regras": False, "sitemap": False, "planos": False}

    # 1) página de regras a partir do molde
    molde = None
    for cand in (OUT / "suporte" / "index.html", OUT / "sugestoes" / "index.html"):
        if cand.exists():
            molde = cand.read_text(encoding="utf-8")
            break
    if molde:
        d = OUT / "regras-da-promocao"
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(pagina_regras(molde), encoding="utf-8")
        feitos["regras"] = True

    # 2) faixa + janela nas páginas públicas
    for f in OUT.rglob("*.html"):
        rel = rel_of(f)
        if deve_pular(rel, f) and f != OUT / "regras-da-promocao" / "index.html":
            continue
        s = f.read_text(encoding="utf-8")
        if "<body" not in s:
            continue
        novo = injeta_faixa(s)
        if "planos" in rel or f.name == "planos.html" or 'class="tm-lanc-box"' in s:
            novo2 = link_planos(novo)
            if novo2 != novo:
                feitos["planos"] = True
            novo = novo2
        if novo != s:
            f.write_text(novo, encoding="utf-8")
            feitos["paginas"] += 1

    feitos["sitemap"] = atualiza_sitemap()
    print("[chamada_t2240u]", "semana=" + NS, "off=" + str(OFF), feitos)


if __name__ == "__main__":
    main()
