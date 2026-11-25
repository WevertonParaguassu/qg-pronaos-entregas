#!/usr/bin/env python3
"""t2217u — /planos/ público: glossário (aplicativo Têmis, skill Têmis, API), rampa de lançamento
(−50/40/30/20/10, preço cheio a partir do 6º mês, inscrição até 31/05/2027 23h59 BRT),
escada de 8 degraus (Essencial → Base → Prática → Solo → Profissional → Escritório → Max → Ultra)
e botões Contratar com cartão / Pagar com Pix (QR na tela) / Pagar com Mercado Pago.
Roda depois de precos_pos, palavras_pos, entrada e medalhas; não reescreve precos_pos.py.
Rollback: apagar a linha no build.sh.
"""
import html as H, json, re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--rampa-glossario-t2217u-->"
DADOS = json.loads((ROOT / "precos_publicos.json").read_text(encoding="utf-8"))
E = H.escape
L = DADOS["lancamento"]
FIM = L["fim_texto"]
EP = int(L["fim_epoch"])
RAMPA = DADOS.get("rampa") or {"descontos_pct": [50, 40, 30, 20, 10], "cheia_a_partir": 6}
OFFS = list(RAMPA.get("descontos_pct") or [50, 40, 30, 20, 10])
LISTAS = DADOS.get("listas") or {}
ENTRADA = list(DADOS.get("entrada") or [])
PAGOS = ENTRADA + list(DADOS["planos"])  # Base, Prática, Solo, Profissional, Escritório, Max, Ultra
DEGRAUS = ["essencial"] + [p["id"] for p in PAGOS]  # 8 degraus
ESCADA = "Base → Prática → Solo → Profissional → Escritório → Max → Ultra"


def brl(reais):
    cent = int(round(float(reais) * 100))
    s = f"R$ {cent/100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s[:-3] if s.endswith(",00") else s


def mes_rampa(cheio, mes):
    off = OFFS[mes - 1] if 1 <= mes <= len(OFFS) else 0
    return round(float(cheio) * (100 - off) / 100, 2)


def rotulo(p):
    pu = " por usuário" if p.get("por_usuario") else ""
    ch = p["cheio"]
    passos = " · ".join(f"{n}º mês {brl(mes_rampa(ch, n))}" for n in range(1, 6))
    txt = f"{passos} · a partir do 6º mês {brl(ch)}/mês{pu} (preço cheio). Vale para quem contrata até {FIM}."
    return (
        f'<div class="tm-preco"><span class="tm-lanc">'
        f'<span class="tm-rampa-preco"><b>{brl(mes_rampa(ch, 1))}</b>/mês{pu} no 1º mês</span>'
        f'<small class="tm-rampa">{E(txt)}</small></span>'
        f'<span class="tm-cheio" hidden><b>{brl(ch)}</b>/mês{pu}</span></div>'
    )


def botoes(pid, nome):
    # Checkout de verdade fica atrás do login em /conta/; os três nomes apontam para a rota certa.
    return (
        f'<div class="tm-botoes">'
        f'<a class="btn" href="/conta/pagar/stripe/plano/{E(pid)}?prazo=mensal">Contratar com cartão</a>'
        f'<div class="tm-alt">'
        f'<a class="btn btn-ghost" href="/conta/pagar/efi/plano/{E(pid)}?prazo=mensal">Pagar com Pix (QR na tela)</a>'
        f'<a class="btn btn-ghost" href="/conta/pagar/mercadopago/plano/{E(pid)}?prazo=mensal">Pagar com Mercado Pago</a>'
        f"</div></div>"
    )


def listas_html(pid):
    L0 = LISTAS.get(pid) or {}
    apps = L0.get("apps") or []
    skills = L0.get("skills") or []
    def item(tag, n):
        return f'<li class="tm-app"><span class="tm-tag">{E(tag)}</span> {E(n)}</li>'
    ul_apps = "<ul class=\"tm-lista\">" + "".join(item("App Têmis", n) for n in apps) + "</ul>" if apps else "<p>Nenhum aplicativo Têmis listado neste plano.</p>"
    if skills:
        ul_sk = "<ul class=\"tm-lista\">" + "".join(item("Skill Têmis", n) for n in skills) + "</ul>"
    else:
        ul_sk = "<p>Nenhuma skill Têmis neste plano.</p>"
    api = ("<p>A ligação (API) dos aplicativos inclusos, quando ela existir, acompanha este plano. "
           "Uma API feita sob medida para o seu escritório não entra em nenhum plano; é contratada à parte.</p>")
    return (f'<div class="tm-listas"><p><b>Aplicativos Têmis inclusos</b></p>{ul_apps}'
            f"<p><b>Skills Têmis inclusas</b></p>{ul_sk}<p><b>API</b></p>{api}</div>")


def glossario():
    return (
        '<section class="sec" id="o-que-e"><div class="wrap">'
        '<div class="sec-head"><p class="eyebrow">Glossário</p><h2>O que você está contratando</h2></div>'
        "<p>Três palavras aparecem nos planos. Elas não são a mesma coisa:</p>"
        "<p><b>Aplicativo Têmis (app).</b> É um programa dentro da Têmis, com nome próprio — por exemplo, Chat jurídico com fontes ou Leitura dos autos. Você abre o aplicativo e trabalha nele. Cada plano diz quais aplicativos Têmis vêm inclusos; o que não vem, você vê em “Não inclui”.</p>"
        "<p><b>Skill Têmis.</b> É um modo de trabalho especializado que a Têmis aplica sobre o caso (por exemplo, auditar a peça, montar teses ou traçar a estratégia recursal). Não é um extra solto: as skills Têmis começam no Têmis Profissional e sobem na escada. Base, Prática e Solo não incluem skills Têmis.</p>"
        "<p><b>API.</b> É a porta para outro sistema se conectar à Têmis (o software do escritório falando com os aplicativos do seu plano, quando essa ligação existe). Uma API dedicada, feita sob medida, não entra em nenhum plano e é contratada à parte.</p>"
        f'<p class="fine">Suba de degrau quando quiser: {ESCADA}.</p>'
        "</div></section>"
    )


def faixa():
    return (
        f'<section class="sec tm-faixa"><div class="wrap">'
        f'<div class="tm-lanc-box" role="status"><b>Rampa de lançamento</b> · inscrição até '
        f'<span class="tm-cd" data-fim="{EP}">até {FIM}</span> '
        f'<small>(até {FIM}, 23h59, horário de Brasília). Contratando até lá, a rampa vale: 1º mês com 50% de desconto, depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio. Depois do prazo de inscrição, vale o preço da tabela em vigor, com aviso por e-mail 30 dias antes. Planos de 2 e 3 anos antecipam esse período com o desconto do prazo.</small></div>'
        f'<div class="tm-ess"><div class="tm-ess-topo"><div>'
        f'<p class="eyebrow">o primeiro passo · degrau 1 de 8</p>'
        f"<h2>Têmis Essencial — 7 dias para testar</h2>"
        f"<p>Sem custo no teste. 7 dias para testar: chat jurídico com fontes, conferência das citações, 1 processo monitorado e 5 cálculos de atualização. O cartão só é pedido no fim do teste: sem cartão, o teste termina sozinho e nada é cobrado. Um teste por CPF/CNPJ e por e-mail.</p>"
        f'</div></div><p><a class="btn" href="/conta/essencial">7 dias para testar ›</a></p></div></div></section>'
    )


def sim(v):
    return '<span class="tm-s" aria-label="incluído">✓</span>' if v else '<span class="tm-n" aria-label="não incluído">—</span>'


def n(v, suf=""):
    if not v:
        return '<span class="tm-n">—</span>'
    if isinstance(v, float) and not v.is_integer():
        s = f"{v:.1f}".replace(".", ",")
    else:
        s = f"{int(v):,}".replace(",", ".")
    return s + suf


def tabela():
    es = DADOS["essencial"]["recursos"]
    cols = [("Essencial<br><small>7 dias para testar</small>", es, None, "essencial")] + [
        (E(p["nome"].replace("Têmis ", "")), p["recursos"], p, p["id"]) for p in PAGOS
    ]
    ncol = len(cols)

    def lin(rot, f, nota=""):
        nota_h = f"<small>{nota}</small>" if nota else ""
        return f'<tr><th scope="row">{rot}{nota_h}</th>' + "".join(f"<td>{f(rc, p, kid)}</td>" for _, rc, p, kid in cols) + "</tr>"

    calc_tipos = lambda rc, p, kid: (
        ("todos" if len(rc["calculos"]) >= 5 else ("atualização e prescrição" if len(rc["calculos"]) > 1 else "atualização"))
        + f'<small>{n(rc["calculos_mes"])}/mês</small>'
    )

    def preco_cel(rc, p, kid):
        if not p:
            return "<b>sem custo no teste</b><small>depois, preço do Solo na rampa</small>"
        pu = "<small>por usuário</small>" if p.get("por_usuario") else ""
        return (f'<span class="tm-lanc"><b>{brl(mes_rampa(p["cheio"], 1))}</b>'
                f"<small>1º mês · rampa até {FIM} · cheio {brl(p['cheio'])}</small></span>"
                f'<span class="tm-cheio" hidden><b>{brl(p["cheio"])}</b></span>{pu}')

    linhas = [
        f'<tr class="tm-g"><th colspan="{ncol}">Preço (rampa de lançamento)</th></tr>',
        f'<tr><th scope="row">1º mês</th>' + "".join(f"<td>{preco_cel(rc, p, kid)}</td>" for _, rc, p, kid in cols) + "</tr>",
        f'<tr class="tm-g"><th colspan="{ncol}">Volume</th></tr>',
        lin("Usuários", lambda rc, p, kid: "1" if not p else ("a partir de 2" if p["por_usuario"] else n(p.get("usuarios_incluidos") or p["usuarios"]))),
        lin("Casos ativos", lambda rc, p, kid: n((p or {"casos": None}).get("casos") if p else None) if p else n(DADOS["planos"][0]["casos"])),
        lin("Minutas por mês", lambda rc, p, kid: n(p["minutas"] if p else DADOS["planos"][0]["minutas"])),
        lin("Mensagens por mês", lambda rc, p, kid: n(p["mensagens"] if p else DADOS["planos"][0]["mensagens"])),
        lin("Armazenamento", lambda rc, p, kid: n((p["armazenamento_gb"] if p else DADOS["planos"][0]["armazenamento_gb"]), " GB")),
        f'<tr class="tm-g"><th colspan="{ncol}">No dia a dia</th></tr>',
        lin("Chat jurídico com fontes, leitura dos autos e minutas .docx", lambda rc, p, kid: sim(True)),
        lin("Conferência das citações", lambda rc, p, kid: sim(rc["citacoes"]), "selo verificado / não encontrado e link oficial; citação sem fonte sai antes da entrega"),
        lin("Plano de teses antes da minuta", lambda rc, p, kid: sim(rc["teses"]), "você aprova as teses; a peça segue o plano"),
        lin("Monitor de processos por número CNJ", lambda rc, p, kid: n(rc["monitor_cnj"]), "DataJud e Diário de Justiça Eletrônico"),
        lin("Monitor por OAB", lambda rc, p, kid: n(rc["monitor_oab"])),
        lin("Prazos em dias úteis, agenda, tarefas e atendimentos", lambda rc, p, kid: sim(rc["escritorio"])),
        lin("Cálculos com índices oficiais do Banco Central", calc_tipos, "memória de cálculo em PDF"),
        lin("Transcrição de áudio no servidor da Têmis", lambda rc, p, kid: n(rc["transcricao_min_mes"], " min/mês") if rc.get("transcricao_min_mes") else '<span class="tm-n">—</span>'),
        lin("Modelos .docx próprios (papel timbrado)", lambda rc, p, kid: n(rc["modelos"]) if rc.get("modelos") else '<span class="tm-n">—</span>'),
        lin("Firma digital com o seu certificado ICP-Brasil", lambda rc, p, kid: sim(rc["firmar"])),
        lin("Consulta de CNPJ em dados públicos", lambda rc, p, kid: sim(rc["cnpj"])),
        lin("Skills Têmis", lambda rc, p, kid: sim(bool((p or {}).get("recursos", {}).get("skills_temis") if p else False) or (rc or {}).get("skills_temis"))),
        f'<tr class="tm-g"><th colspan="{ncol}">Equipe e agente</th></tr>',
        lin("Revisão adversarial, Protetora Leal e Auditoria", lambda rc, p, kid: sim(kid in ("profissional", "escritorio", "max", "ultra"))),
        lin("Memória do Escritório, Radar Processual e convites de equipe", lambda rc, p, kid: sim(kid in ("escritorio", "max", "ultra"))),
        lin("Agente Têmis pessoal (memória e estilo do seu escritório)", lambda rc, p, kid: sim(kid in ("max", "ultra"))),
        lin("Conselho das 4 (opcional)", lambda rc, p, kid: sim(kid in ("max", "ultra")), "no Max, com teto mensal interno; no Ultra, com modelos de topo"),
        lin("100% das Têmis, fila prioritária e Rodada completa", lambda rc, p, kid: sim(kid == "ultra")),
    ]
    # Essencial casos/minutas: tabela de t2198u usava Solo numbers for essencial via lim(). Be honest: essencial is a 7-day Solo test with reduced recursos, volume follows Solo in the original. Keep Solo volume for essencial to avoid inventing lower volume numbers not in JSON. The essencial object has no casos/minutas. Original used solo. OK.

    head = "<tr><th></th>" + "".join(f'<th scope="col">{c}</th>' for c, _, _, _ in cols) + "</tr>"
    return (
        f'<section class="sec" id="comparativo"><div class="wrap"><div class="sec-head"><p class="eyebrow">Comparativo</p>'
        f"<h2>O que cada plano entrega</h2></div>"
        f'<div class="tm-tab-w"><table class="tm-tab"><thead>{head}</thead><tbody>{"".join(linhas)}</tbody></table></div>'
        f'<p class="fine">Limites por mês. Minutas são rascunhos para revisão de advogado(a). Preços em reais, no plano mensal, com a rampa de lançamento para quem contrata até {FIM} (23h59, Brasília); anual com 15% de desconto sobre o ano da rampa. '
        f"Direito de arrependimento de 7 dias (CDC art. 49).</p></div></section>"
    )


CSS = """<style>
.tm-rampa-preco b{font-size:1.6rem;color:#f0d58c}
.tm-rampa,.tm-preco small.tm-rampa{display:block;opacity:.85;font-size:.78rem;font-weight:400;white-space:normal;line-height:1.35;margin-top:.25rem}
.tm-botoes{margin:.7rem 0 .5rem;display:flex;flex-direction:column;gap:8px;align-items:flex-start}
.tm-alt{display:flex;flex-wrap:wrap;gap:8px}
.tm-listas{margin:10px 0;font-size:.92rem}
.tm-listas p{margin:8px 0 4px}
.tm-lista{list-style:none;padding:0;margin:6px 0 12px}
.tm-app{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:.86rem;margin:4px 0}
.tm-tag{display:inline-block;font-size:10px;letter-spacing:.04em;text-transform:uppercase;border:1px solid #d4af5a;color:#0b1a3a;background:linear-gradient(180deg,#f6df9a,#d4af5a);border-radius:999px;padding:2px 7px;font-weight:700;white-space:nowrap}
#o-que-e p{max-width:70ch}
.tm-tab{min-width:1100px}
.tm-entrada-grid{margin:0 0 18px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.tm-card.tm-entrada{border:1.5px solid #d4af5a55;border-radius:16px;padding:18px 20px;background:rgba(11,28,56,.58)}
.tm-entrada .tm-botoes{margin-top:.4rem}
</style>"""


def troca_preco_e_cta(s, p):
    """Substitui o bloco de preço injetado pelo precos_pos ou pelo entrada, e o CTA único, pelo rótulo da rampa + 3 botões + listas."""
    pid, nome = p["id"], p["nome"]
    bloco = rotulo(p) + listas_html(pid) + botoes(pid, nome)
    # 1) cartões dos 5 planos (precos_pos): <div class="tm-preco">...</div><p><a class="btn" href="/conta/planos">Contratar o NOME ›</a></p>
    rx1 = re.compile(
        r'<div class="tm-preco">[\s\S]*?</div>\s*<p><a class="btn" href="/conta/planos">Contratar o [^<]*</a></p>',
        re.S,
    )
    # We'll apply per-card by finding the card heading first.
    return bloco, rx1


def main():
    f = OUT / "planos" / "index.html"
    if not f.exists():
        print("[rampa_glossario_t2217u] sem /planos/")
        return
    s = f.read_text(encoding="utf-8")
    if MARCA in s:
        print("[rampa_glossario_t2217u] já aplicado")
        return

    # Hero: escada de 8 degraus, sem "do Solo ao Ultra" / 5 planos / 12 meses / 31/01
    substituicoes = {
        "do Solo ao Ultra": "do Essencial ao Ultra (Base, Prática, Solo, Profissional, Escritório, Max e Ultra)",
        "Do Solo ao Ultra": "Do Essencial ao Ultra",
        "Solo → Ultra": ESCADA,
        "Solo ao Ultra": "Essencial ao Ultra",
        "os 5 planos": "os 8 degraus",
        "5 planos": "8 degraus",
        "até 12 meses": "na rampa de lançamento (1º mês −50%, depois 40%, 30%, 20% e 10%; cheio a partir do 6º mês)",
        "por até 12 meses": "na rampa de lançamento",
        "31/01/2027": FIM,
        "Preços de lançamento até": "Rampa de lançamento até",
        "Preço de lançamento": "Rampa de lançamento",
        "Solo → Profissional → Escritório → Max → Ultra": "Essencial → Base → Prática → Solo → Profissional → Escritório → Max → Ultra",
        "Entrar para ver os preços": "Entrar para contratar",
        "preço de lançamento vale por até 12 meses": "a rampa vale: 1º mês com 50% de desconto, depois 40%, 30%, 20% e 10%; a partir do 6º mês, o preço cheio",
    }
    for a, b in substituicoes.items():
        s = s.replace(a, b)

    # Reescreve a faixa do lançamento (a gerada pelo precos_pos, possivelmente já mexida pelo medalhas)
    s = re.sub(r'<section class="sec tm-faixa">[\s\S]*?</section>', faixa(), s, count=1)

    # Glossário logo após a faixa
    if 'id="o-que-e"' not in s:
        s = s.replace("</section>", "</section>" + glossario(), 1) if '<section class="sec tm-faixa">' in s else s
        # The first </section> after replace of faixa might be the faixa itself — we inserted via replace of the whole section.
        # Safer: insert after tm-faixa section
        if s.count('id="o-que-e"') == 0:
            s = s.replace('</section>', '</section>' + glossario(), 1)

    # Preços + botões + listas em cada cartão pago
    for p in PAGOS:
        pid, nome = p["id"], p["nome"]
        bloco = rotulo(p) + listas_html(pid) + botoes(pid, nome)
        # a) precos_pos injection after <h2>Têmis Nome</h2> or <h2>Nome</h2>
        for h in (nome, nome.replace("Têmis ", ""), "Têmis " + nome if not nome.startswith("Têmis") else nome):
            rx = re.compile(
                r'(<h2>' + re.escape(h) + r'</h2>)(?:\s*<div class="tm-preco">[\s\S]*?</div>)?(?:\s*<p><a class="btn"[^>]*>Contratar o [^<]*</a></p>)?',
                re.S,
            )
            s2, nsub = rx.subn(lambda m, b=bloco: m.group(1) + b, s, count=1)
            if nsub:
                s = s2
                break
        # b) cartões de entrada: <p class="tm-preco">... até 31/05 ...</p>
        rx_e = re.compile(
            r'(<article class="tm-card tm-entrada" id="plano-' + re.escape(pid) + r'"[\s\S]*?<h2>' + re.escape(nome) + r'</h2>)\s*<p class="tm-preco">[\s\S]*?</p>',
            re.S,
        )
        s, _ = rx_e.subn(lambda m, b=bloco: m.group(1) + b, s, count=1)

    # Remapeia “Degrau X de 5” (escada_pos nos 5 planos) para a escada de 8
    mapa = {"solo": 4, "profissional": 5, "escritorio": 6, "max": 7, "ultra": 8}
    def remap_degrau(m):
        bloco = m.group(0)
        kid = None
        ids = re.findall(r'id="([^"]+)"', m.group(1) if m.lastindex else bloco)
        # look back: the regex includes preceding id
        return bloco
    s = re.sub(r'Degrau ([1-5]) de 5', lambda m: f"Degrau {[0,4,5,6,7,8][int(m.group(1))]} de 8", s)
    # The second pass is dangerous if already remapped (4 would become?). Skip second if first already mapped 1->4 etc.
    # entrada cards: add degrau label if missing
    for p, d in (("base", 2), ("pratica", 3)):
        tag = next((x.get("tag", "") for x in ENTRADA if x["id"] == p), "")
        s = s.replace(
            f'<article class="tm-card tm-entrada" id="plano-{p}">',
            f'<article class="tm-card tm-entrada" id="plano-{p}" data-degrau="{d}">',
            1,
        )
        s = re.sub(
            r'(id="plano-' + p + r'"[^>]*>[\s\S]*?<p class="eyebrow">)([^<]*)(</p>)',
            lambda m, d=d, tag=tag: m.group(1) + f"Degrau {d} de 8 · {tag or m.group(2)}" + m.group(3),
            s,
            count=1,
        )

    # Comparativo: troca a tabela toda (agora com 8 planos + Essencial)
    s = re.sub(r'<section class="sec" id="comparativo">[\s\S]*?</section>', tabela(), s, count=1)

    # Preço flat que tenha restado nos cartões de entrada
    s = re.sub(r'<p class="tm-preco"><strong>R\$ [^<]+</strong>\s*<span>até 31/05/2027 · depois R\$ [^<]+</span></p>\s*', '', s)
    # Se o grid de entrada caiu no fim da página, move para imediatamente antes da ficha dos 5 planos
    mgrid = re.search(r'<!--entrada-t2204u-->\s*<div class="tm-entrada-grid">[\s\S]*?</div>(?=\s*</main>|\s*<section)', s)
    mficha = re.search(r'<div class="ficha">', s)
    if mgrid and mficha and mgrid.start() > mficha.start():
        grid = mgrid.group(0)
        s = s[:mgrid.start()] + s[mgrid.end():]
        mficha = re.search(r'<div class="ficha">', s)
        s = s[:mficha.start()] + grid + s[mficha.start():]

    # CTAs soltos “Contratar o X” que tenham restado
    s = re.sub(
        r'<a class="btn" href="/conta/planos">Contratar o ([^<]+) ›</a>',
        lambda m: (
            '<div class="tm-botoes"><a class="btn" href="/conta/planos">Contratar com cartão</a>'
            '<div class="tm-alt"><a class="btn btn-ghost" href="/conta/planos">Pagar com Pix (QR na tela)</a>'
            '<a class="btn btn-ghost" href="/conta/planos">Pagar com Mercado Pago</a></div></div>'
        ),
        s,
    )

    s = s.replace("</head>", MARCA + CSS + "</head>", 1)
    f.write_text(s, encoding="utf-8")
    print("[rampa_glossario_t2217u] ok: glossário, rampa, 8 degraus e 3 botões em /planos/")


if __name__ == "__main__":
    main()
