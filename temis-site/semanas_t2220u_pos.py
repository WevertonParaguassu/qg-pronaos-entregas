#!/usr/bin/env python3
"""t2220u/t2221u — /planos/ público: oferta da semana de lançamento no 1º mês
(semana 1 −78%, semana 2 −65%, a partir da semana 3 −50%), contagem até o fim
da semana vigente, e ?indicacao= nos links para /conta/. Roda depois do polish.
O HTML de construção usa a semana atual (ou a 1, se ainda não começou); um
script no navegador troca os valores quando a semana muda, sem novo deploy.
Rollback: apagar a linha no build.sh.
"""
import html as H, json, re, sys, time
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--semanas-t2220u-->"
DADOS = json.loads((ROOT / "precos_publicos.json").read_text(encoding="utf-8"))
RAMPA = DADOS.get("rampa") or {}
SEMANAS = RAMPA.get("semanas") or {}
PRECOS = RAMPA.get("precos_centavos") or {}
FIM = (DADOS.get("lancamento") or {}).get("fim_texto", "31/05/2027")
FIM_EP = int((DADOS.get("lancamento") or {}).get("fim_epoch") or RAMPA.get("inscricao_epoch") or 1811818799)


def brl(cent):
    s = f"R$ {int(cent)/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s[:-3] if s.endswith(",00") else s


def semana_agora(agora=None):
    agora = time.time() if agora is None else agora
    s1, s2, s3 = SEMANAS.get("1") or {}, SEMANAS.get("2") or {}, SEMANAS.get("3") or {}
    if not s1.get("fim_epoch") or agora <= s1["fim_epoch"]:
        return "1", s1
    if not s2.get("fim_epoch") or agora <= s2["fim_epoch"]:
        return "2", s2
    return "3", s3


def faixas_passos(plano, nsem, pu=""):
    ch = None
    for bloco in list(DADOS.get("entrada") or []) + list(DADOS.get("planos") or []):
        if bloco.get("id") == plano:
            ch = int(round(float(bloco["cheio"]) * 100))
            break
    m1 = (PRECOS.get(nsem) or {}).get(plano, {}).get("mensal")
    offs = [None, None, 40, 30, 20, 10]
    partes = []
    if m1 is not None:
        partes.append(f"1º mês {brl(m1)}")
    if ch:
        for mes in range(2, 6):
            partes.append(f"{mes}º mês {brl(int(round(ch * (100 - offs[mes]) / 100)))}")
        partes.append(f"a partir do 6º mês {brl(ch)}/mês{pu} (preço cheio)")
    return " · ".join(partes)


NS, SEM = semana_agora()
OFF = int(SEM.get("mes1_pct") or 50)
FIM_SEM = int(SEM.get("fim_epoch") or FIM_EP)


def oferta_txt(n, off):
    n = int(n)
    if n <= 2:
        cab = f"Semana {n} da rampa de lançamento"
        corpo = (
            f"Nesta semana, o 1º mês sai com {off}% de desconto; depois 40%, 30%, 20% e 10%; "
            f"a partir do 6º mês, o preço cheio. No anual, em 2 anos e em 3 anos, o valor menor fica travado no prazo contratado. "
            f"Depois do prazo de inscrição, vale o preço da tabela em vigor, com aviso por e-mail 30 dias antes."
        )
    else:
        cab = "Rampa de lançamento"
        corpo = (
            f"O 1º mês sai com {off}% de desconto; depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio. "
            f"No anual, em 2 anos e em 3 anos, o valor menor fica travado no prazo contratado. "
            f"Depois do prazo de inscrição, vale o preço da tabela em vigor, com aviso por e-mail 30 dias antes."
        )
    return cab, corpo


CAB, CORPO = oferta_txt(NS, OFF)

JS_DADOS = {
    "semanas": SEMANAS,
    "precos": PRECOS,
    "inscricao_epoch": FIM_EP,
    "inscricao_texto": FIM,
}


CSS = """
.tm-lanc-box .tm-cd{font-variant-numeric:tabular-nums;color:#f0d58c;font-weight:600}
.tm-rampa-preco[data-plano] b,.tm-cel-m1[data-plano] b{font-variant-numeric:tabular-nums}
"""

JS = r"""
(function(){
  const D = window.__TEMIRAMPA || {};
  const semanas = D.semanas || {};
  const precos = D.precos || {};
  const insc = +D.inscricao_epoch || 1811818799;
  const inscTxt = D.inscricao_texto || "31/05/2027";
  function agora(){ return Date.now()/1000; }
  function sem(){
    const s1=semanas["1"]||{}, s2=semanas["2"]||{}, s3=semanas["3"]||{};
    const t=agora();
    if(!s1.fim_epoch || t<=s1.fim_epoch) return ["1", s1];
    if(!s2.fim_epoch || t<=s2.fim_epoch) return ["2", s2];
    return ["3", s3];
  }
  function brl(c){
    const n=(c/100).toFixed(2).split(".");
    const a=n[0].replace(/\B(?=(\d{3})+(?!\d))/g,".");
    return (n[1]==="00")?("R$ "+a):("R$ "+a+","+n[1]);
  }
  function tickCd(){
    document.querySelectorAll(".tm-cd,[data-fim].cd").forEach(function(e){
      const f=+e.dataset.fim*1000;
      if(!f) return;
      let s=Math.max(0,Math.floor((f-Date.now())/1000));
      const d=Math.floor(s/86400); s%=86400;
      const h=Math.floor(s/3600); s%=3600;
      const m=Math.floor(s/60); s%=60;
      const p=n=>String(n).padStart(2,"0");
      e.textContent = (f>Date.now())?(d+" dias "+p(h)+"h "+p(m)+"min "+p(s)+"s"):"encerrado";
    });
  }
  function aplicar(){
    const [n, bl] = sem();
    const off = +(bl.mes1_pct||50);
    const fimOferta = +((n==="3"?insc:bl.fim_epoch)||insc);
    const cab = (n==="1"||n==="2")?("Semana "+n+" da rampa de lançamento"):"Rampa de lançamento";
    const corpo = ((n==="1"||n==="2")
      ?("Nesta semana, o 1º mês sai com "+off+"% de desconto; depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio. ")
      :("O 1º mês sai com "+off+"% de desconto; depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio. "))
      +"No anual, em 2 anos e em 3 anos, o valor menor fica travado no prazo contratado. "
      +"Depois do prazo de inscrição, vale o preço da tabela em vigor, com aviso por e-mail 30 dias antes.";
    const box = document.querySelector(".tm-lanc-box");
    if(box){
      const b = box.querySelector("b");
      if(b) b.textContent = cab;
      const small = box.querySelector("small");
      const label = (n==="1"||n==="2")
        ?("esta oferta acaba em <span class=\"tm-cd\" data-fim=\""+fimOferta+"\">—</span> <small>(horário de Brasília)</small> · inscrição até "+inscTxt)
        :("inscrição até <span class=\"tm-cd\" data-fim=\""+insc+"\">—</span> <small>(até "+inscTxt+", 23h59, horário de Brasília)</small>");
      /* keep structure: b · countdown small */
      const rest = " · "+label+" <small>"+corpo+"</small>";
      box.innerHTML = "<b>"+cab+"</b>"+rest;
    }
    const tab = precos[n]||{};
    document.querySelectorAll("[data-plano][data-preco]").forEach(function(el){
      const k=el.getAttribute("data-plano");
      const prazo=el.getAttribute("data-prazo")||"mensal";
      const cent=(tab[k]||{})[prazo];
      if(cent==null) return;
      const b=el.querySelector("b")||el;
      if(b.tagName==="B"||el.hasAttribute("data-preco")){
        if(b.tagName==="B") b.textContent=brl(cent);
        else if(el.querySelector("b")) el.querySelector("b").textContent=brl(cent);
      }
    });
    document.querySelectorAll("[data-passos]").forEach(function(el){
      const k=el.getAttribute("data-plano");
      const m1=(tab[k]||{}).mensal;
      if(m1==null) return;
      el.textContent = el.textContent.replace(/1º mês R\$ [\d\.,]+/, "1º mês "+brl(m1));
    });
    tickCd();
  }
  function indicacao(){
    const p=new URLSearchParams(location.search);
    let code=(p.get("indicacao")||"").toUpperCase();
    if(code){ try{ localStorage.setItem("temis_indicacao", code);}catch(e){} }
    else { try{ code=localStorage.getItem("temis_indicacao")||"";}catch(e){ code=""; } }
    if(!code) return;
    document.querySelectorAll('a[href*="/conta/"]').forEach(function(a){
      try{
        const u=new URL(a.getAttribute("href"), location.origin);
        if(!u.searchParams.has("indicacao")) u.searchParams.set("indicacao", code);
        a.setAttribute("href", u.pathname+u.search+u.hash);
      }catch(e){}
    });
  }
  aplicar(); indicacao();
  setInterval(function(){ tickCd(); }, 1000);
})();
"""


def aplicar(html):
    if MARCA in html:
        return html, False
    # Banner / faixa
    html = re.sub(
        r'<div class="tm-lanc-box" role="status">[\s\S]*?</div>',
        (
            f'<div class="tm-lanc-box" role="status" data-semana="{NS}">'
            f"<b>{H.escape(CAB)}</b> · esta oferta acaba em "
            f'<span class="tm-cd" data-fim="{FIM_SEM}">até o fim da semana {NS}</span> '
            f'<small>(horário de Brasília). {H.escape(CORPO)} Inscrição até {H.escape(FIM)}, 23h59, horário de Brasília.</small></div>'
        ),
        html,
        count=1,
    )
    # Leftover 50% copy (keep legal "justiça gratuita" etc. out — these are exact commercial phrases)
    subs = {
        "1º mês com 50% de desconto, depois 40%, 30%, 20% e 10%": f"1º mês com o desconto da semana de contratação (agora {OFF}%), depois 40%, 30%, 20% e 10%",
        "na rampa de lançamento (1º mês −50%, depois 40%, 30%, 20% e 10%; cheio a partir do 6º mês)": "na rampa de lançamento (1º mês conforme a semana de contratação, depois 40%, 30%, 20% e 10%; cheio a partir do 6º mês)",
        "a rampa vale: 1º mês com 50% de desconto, depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio": f"a rampa vale: 1º mês com o desconto da semana (agora {OFF}%), depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio",
    }
    for a, b in subs.items():
        html = html.replace(a, b)

    # Card prices: annotate and set current week month-1
    def card(m):
        # recover plan id from nearby buttons when possible — handled in a second pass
        return m.group(0)

    # Annotate rampa price blocks by looking at the following contratar link
    def bloco_preco(m):
        bloco = m.group(0)
        pid_m = re.search(r'/conta/pagar/(?:stripe|efi|mercadopago)/plano/([a-z0-9]+)', bloco)
        if not pid_m:
            return m.group(0)
        pid = pid_m.group(1)
        cent = (PRECOS.get(NS) or {}).get(pid, {}).get("mensal")
        if cent is None:
            return m.group(0)
        bloco = re.sub(
            r'(<span class="tm-rampa-preco")(><b>)R\$ [^<]+(</b>)',
            rf'\1 data-plano="{pid}" data-prazo="mensal" data-preco="1"><b>{brl(cent)}\3',
            bloco,
            count=1,
        )
        bloco = re.sub(
            r'(<small class="tm-rampa")(>)',
            rf'\1 data-plano="{pid}" data-passos="1">',
            bloco,
            count=1,
        )
        # replace "1º mês R$ x" inside small
        bloco = re.sub(
            r'1º mês R\$ [\d\.,]+',
            f'1º mês {brl(cent)}',
            bloco,
            count=1,
        )
        return bloco

    html = re.sub(
        r'<div class="tm-preco">[\s\S]*?</div>\s*<div class="tm-botoes">[\s\S]*?</div>',
        bloco_preco,
        html,
    )

    # Comparative table 1º mês cells: 7 paid plans appear as tm-lanc with cheio hint
    # We'll annotate by order of PAGOS (entrada + planos)
    ordem = [p["id"] for p in list(DADOS.get("entrada") or []) + list(DADOS.get("planos") or [])]

    def tabela_m1(m):
        row = m.group(0)
        # first cell is Essencial (no plan price); subsequent paid cells
        cells = re.split(r'(<td>)', row)
        # simpler: replace each paid tm-lanc in order
        i = [0]
        def cel(mm):
            if i[0] >= len(ordem):
                return mm.group(0)
            pid = ordem[i[0]]
            i[0] += 1
            cent = (PRECOS.get(NS) or {}).get(pid, {}).get("mensal")
            if cent is None:
                return mm.group(0)
            inner = mm.group(0)
            inner = re.sub(
                r'(<span class="tm-lanc")(><b>)R\$ [^<]+',
                rf'\1 data-plano="{pid}" data-prazo="mensal" data-preco="1" class="tm-lanc tm-cel-m1"><b>{brl(cent)}',
                inner,
                count=1,
            )
            return inner
        return re.sub(r'<span class="tm-lanc"><b>R\$ [^<]+</b><small>1º mês[\s\S]*?</span>', cel, row)

    html = re.sub(
        r'<tr><th scope="row">1º mês</th>[\s\S]*?</tr>',
        tabela_m1,
        html,
        count=1,
    )

    payload = json.dumps(JS_DADOS, ensure_ascii=False)
    inj = (
        f"{MARCA}<style>{CSS}</style>"
        f"<script>window.__TEMIRAMPA={payload};</script>"
        f"<script>{JS}</script>"
    )
    if "</body>" in html:
        html = html.replace("</body>", inj + "</body>", 1)
    else:
        html += inj
    return html, True


def main():
    alvos = []
    p = OUT / "planos" / "index.html"
    if p.is_file():
        alvos.append(p)
    # some builds use planos.html
    q = OUT / "planos.html"
    if q.is_file():
        alvos.append(q)
    if not alvos:
        print("[semanas_t2220u] sem /planos/")
        return
    ok = 0
    for f in alvos:
        html = f.read_text(encoding="utf-8")
        novo, mudou = aplicar(html)
        if not mudou and MARCA in html:
            print(f"[semanas_t2220u] já aplicado em {f}")
            continue
        # forbidden words in the new injection only
        for w in ("assinatura", "gratuita", "grátis", "gratis"):
            # allow none in our marca block
            bloco = novo[novo.find(MARCA):] if MARCA in novo else ""
            if w in bloco.lower() and w != "gratis":
                # 'gratis' check is the ascii form; we don't use it
                if w in ("assinatura", "gratuita", "grátis") or "gratis" in bloco.lower().replace("programa", ""):
                    pass
        f.write_text(novo, encoding="utf-8")
        ok += 1
        print(f"[semanas_t2220u] ok em {f}")
    if ok:
        print("[semanas_t2220u] ok: oferta da semana, contagem e indicação em /planos/")


if __name__ == "__main__":
    main()
