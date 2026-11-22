#!/usr/bin/env python3
"""Pós-processador do site público da Têmis (roda no build do Render, depois do untar em out/).
Navegação em camadas: Início → frente (/temis/<frente>/) → Têmis (/temis/<slug>/) e tarefas (/tarefas/<slug>/).
Só mostra o que passou teste funcional (navegacao.json, campo 'testado'). Não mexe no SEO de base,
no arquivo de verificação do Google nem na estátua. Rollback: tirar a linha do build.sh que chama este script."""
import json, re, sys, html, pathlib

OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
CFG = json.loads((pathlib.Path(__file__).parent / "navegacao.json").read_text())
SITE = "https://agentetemis.com"
E = html.escape
FR = {f["slug"]: f for f in CFG["frentes"]}
VIS = [t for t in CFG["temis"] if t.get("testado")]
OCULTOS = [t for t in CFG["temis"] if not t.get("testado")]
TAR = [t for t in CFG["tarefas"] if t.get("testado")]
TAR_OC = [t for t in CFG["tarefas"] if not t.get("testado")]
def da_frente(f): return [t for t in VIS if t["frente"] == f]
FRENTES = [f for f in CFG["frentes"] if da_frente(f["slug"])]

BASE = (OUT / "temis" / "index.html").read_text()
HEAD, RESTO = BASE.split("<main", 1)
FOOT = RESTO.split("</main>", 1)[1]
HEADER = HEAD[HEAD.find("<body"):]
HEAD = HEAD[:HEAD.find("<body")]
STATUE = re.search(r'<div class="statue-slot">.*?</picture></div></div>', BASE, re.S).group(0)

CSS = """
/* navegação em camadas (nav_pos.py) */
.crumbs{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;font-size:.86rem;margin:0 0 1rem;color:var(--ink-3)}
.crumbs a{color:var(--gold-l);text-decoration:none;padding:.35rem 0;min-height:32px;display:inline-flex;align-items:center}
.crumbs span[aria-hidden]{opacity:.6}
.voltar{display:inline-flex;align-items:center;gap:.4rem;min-height:44px;padding:.5rem 1rem .5rem .8rem;margin:0 0 1rem;border-radius:999px;border:1px solid rgba(224,192,120,.55);color:var(--gold-l);text-decoration:none;font-weight:500;background:rgba(6,16,34,.55)}
.voltar:hover,.voltar:focus-visible{border-color:#E0C078}
.lista-t{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.item-t{display:flex;align-items:center;gap:1rem;min-height:72px;padding:1rem 1.1rem;border-radius:14px;border:1px solid rgba(224,192,120,.45);background:linear-gradient(135deg,rgba(14,30,60,.92),rgba(6,16,34,.92));color:inherit;text-decoration:none;transition:border-color .2s,transform .2s}
.item-t:hover,.item-t:focus-visible{border-color:#E0C078;transform:translateY(-2px)}
.item-t h3{margin:0 0 .25rem;font-size:1.08rem}
.item-t p{margin:0;font-size:.92rem;color:var(--ink-2)}
.item-t .abrir{margin-left:auto;flex:none;display:inline-flex;align-items:center;gap:.25rem;font-size:.85rem;font-weight:600;color:var(--gold-l);white-space:nowrap}
.item-t .abrir::after{content:"›";font-size:1.5rem;line-height:1}
.catgal-t small::after{content:" · Abrir ›";color:var(--gold-l)}
.ficha{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.ficha>div{padding:1.2rem;border-radius:14px;border:1px solid rgba(224,192,120,.4);background:rgba(6,16,34,.78)}
.ficha h2{font-size:1.15rem;margin:0 0 .6rem}
.ficha ul{margin:.2rem 0 0;padding-left:1.1rem}
.ficha li{margin:.3rem 0}
.vizinhos{display:flex;justify-content:space-between;gap:.8rem;flex-wrap:wrap;margin-top:1.5rem}
.vizinhos a{flex:1 1 220px;min-height:52px;display:flex;align-items:center;padding:.7rem 1rem;border-radius:12px;border:1px solid rgba(224,192,120,.35);color:var(--gold-l);text-decoration:none}
.vizinhos a.prox{justify-content:flex-end;text-align:right}
.selo-ok{display:inline-flex;align-items:center;gap:.35rem;padding:.3rem .8rem;border-radius:999px;border:1px solid rgba(224,192,120,.6);color:var(--gold-l);font-size:.8rem;background:rgba(6,16,34,.6)}
.selo-ok::before{content:"✓"}
.cat-hero{border-radius:16px;overflow:hidden;border:1px solid rgba(224,192,120,.55);margin:0 0 1.2rem;max-width:640px}
.cat-hero img{display:block;width:100%;height:auto}
"""

def pagina(rel, titulo, desc, main, ld=None, nav_ativo="/temis/"):
    h = HEAD
    h = re.sub(r"<title>.*?</title>", f"<title>{E(titulo)}</title>", h, flags=re.S)
    for pat in (r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*', r'(<meta name="twitter:description" content=")[^"]*'):
        h = re.sub(pat, lambda m: m.group(1) + E(desc), h)
    for pat in (r'(<meta property="og:title" content=")[^"]*', r'(<meta name="twitter:title" content=")[^"]*'):
        h = re.sub(pat, lambda m: m.group(1) + E(titulo), h)
    url = f"{SITE}/{rel}" if rel else SITE + "/"
    h = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, h)
    if ld: h = h.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>')
    destino = OUT / rel / "index.html"; destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(h + HEADER + f'<main id="main">{main}</main>' + FOOT)

def crumbs(itens):
    partes = []
    for i, (nome, href) in enumerate(itens):
        if i: partes.append('<span aria-hidden="true">›</span>')
        partes.append(f'<a href="{href}">{E(nome)}</a>' if href else f'<span aria-current="page">{E(nome)}</span>')
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": SITE + h} if h else {})} for i, (n, h) in enumerate(itens)]}
    return f'<nav class="crumbs" aria-label="Você está em">{"".join(partes)}</nav>', ld

def pic(img, alt, eager=False):
    lz = '' if eager else ' loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="/img/cats/{img}-640.avif"><img src="/img/cats/{img}-640.webp" alt="{E(alt)}" '
            f'width="640" height="360"{lz} decoding="async"></picture>')

def galeria():
    return '<div class="catgal">' + "".join(
        f'<a class="catgal-i" href="/temis/{f["slug"]}/">{pic(f["img"], f["alt"])}<span class="catgal-t">{E(f["nome"])}'
        f'<small>{len(da_frente(f["slug"]))} Têmis</small></span></a>' for f in FRENTES) + "</div>"

def item(href, nome, resumo):
    return f'<a class="item-t" href="{href}"><div><h3>{E(nome)}</h3><p>{E(resumo)}</p></div><span class="abrir">Abrir</span></a>'

CTA = ('<div class="actions"><a class="btn" href="/conta/cadastro">{t}</a>'
       '<a class="btn btn-ghost" href="/conta/entrar">Já tenho conta: entrar</a></div>')

# 1) hub /temis/
main = (f'<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">'
        f'{crumbs([("Início", "/"), ("As Têmis", None)])[0]}<p class="eyebrow">As Têmis</p>'
        f'<h1>Escolha uma <em>frente de trabalho.</em></h1><p class="lead">{len(VIS)} Têmis em funcionamento, organizadas em {len(FRENTES)} frentes. '
        f'Toque numa frente para ver as Têmis dela; toque numa Têmis para ver o que ela faz e experimentar.</p>'
        f'{CTA.format(t="Começar o teste grátis")}</div>{STATUE}</div></section>'
        f'<section class="sec" id="frentes"><div class="wrap"><div class="sec-head"><p class="eyebrow">Frentes</p><h2>Por onde começar</h2></div>{galeria()}</div></section>'
        f'<section class="sec" id="tarefas"><div class="wrap"><div class="sec-head"><p class="eyebrow">Por tarefa</p><h2>O que você precisa fazer</h2>'
        f'<p class="lead">Você escolhe a tarefa; a Têmis combina as especialidades certas por trás.</p></div>'
        f'<div class="lista-t">{"".join(item("/tarefas/" + t["slug"] + "/", t["nome"], t["faz"].split(".")[0] + ".") for t in TAR)}</div></div></section>')
c, ld = crumbs([("Início", "/"), ("As Têmis", None)])
pagina("temis/", "As Têmis · frentes e especialidades do agente Têmis",
       f"{len(VIS)} Têmis em funcionamento em {len(FRENTES)} frentes: operação, pesquisa, provas, estratégia, qualidade e documentos. Teste grátis.", main, ld)

# 2) frentes
for f in FRENTES:
    ts = da_frente(f["slug"])
    c, ld = crumbs([("Início", "/"), ("As Têmis", "/temis/"), (f["nome"], None)])
    outras = [g for g in FRENTES if g["slug"] != f["slug"]]
    main = (f'<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">{c}<a class="voltar" href="/temis/">‹ Todas as frentes</a>'
            f'<div class="cat-hero">{pic(f["img"], f["alt"], True)}</div><p class="eyebrow">Frente</p><h1>{E(f["nome"])}</h1>'
            f'<p class="lead">{E(f["resumo"])}</p></div>{STATUE}</div></section>'
            f'<section class="sec"><div class="wrap"><div class="sec-head"><h2>{len(ts)} Têmis nesta frente</h2></div>'
            f'<div class="lista-t">{"".join(item("/temis/" + t["slug"] + "/", t["nome"], t["faz"].split(".")[0] + ".") for t in ts)}</div>'
            f'<div class="sec-head" style="margin-top:2.5rem"><h2>Outras frentes</h2></div>'
            f'<div class="lista-t">{"".join(item("/temis/" + g["slug"] + "/", g["nome"], g["resumo"]) for g in outras)}</div></div></section>')
    pagina(f"temis/{f['slug']}/", f"{f['nome']} · Têmis", f"{f['resumo']} {len(ts)} Têmis em funcionamento nesta frente.", main, ld)

# 3) cada Têmis
for f in FRENTES:
    ts = da_frente(f["slug"])
    for i, t in enumerate(ts):
        c, ld = crumbs([("Início", "/"), ("As Têmis", "/temis/"), (f["nome"], f"/temis/{f['slug']}/"), (t["nome"], None)])
        ant = ts[i - 1] if i > 0 else None; prox = ts[i + 1] if i + 1 < len(ts) else None
        viz = ((f'<a href="/temis/{ant["slug"]}/">‹ {E(ant["nome"])}</a>' if ant else f'<a href="/temis/{f["slug"]}/">‹ {E(f["nome"])}</a>')
               + (f'<a class="prox" href="/temis/{prox["slug"]}/">{E(prox["nome"])} ›</a>' if prox else '<a class="prox" href="/temis/">Todas as frentes ›</a>'))
        main = (f'<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">{c}'
                f'<a class="voltar" href="/temis/{f["slug"]}/">‹ Voltar para {E(f["nome"])}</a>'
                f'<p class="eyebrow">{E(f["nome"])}</p><h1>{E(t["nome"])}</h1><p class="lead">{E(t["faz"])}</p>'
                f'<p><span class="selo-ok">Em funcionamento · testada</span></p>{CTA.format(t="Experimentar no teste grátis")}</div>{STATUE}</div></section>'
                f'<section class="sec"><div class="wrap"><div class="ficha">'
                f'<div><h2>Exemplo</h2><p>{E(t["exemplo"])}</p><p class="fine">Caso fictício, para ilustrar.</p></div>'
                f'<div><h2>O que você recebe</h2><ul>{"".join("<li>" + E(x) + "</li>" for x in t["recebe"])}</ul></div>'
                f'<div><h2>Como usar</h2><p>Crie a conta, abra um caso, envie os documentos e peça no chat. A Têmis aciona esta especialidade quando o pedido precisa dela.</p>'
                f'<p class="fine">Tudo sai como rascunho para revisão do advogado responsável.</p></div>'
                f'</div><nav class="vizinhos" aria-label="Navegar entre as Têmis">{viz}</nav></div></section>')
        pagina(f"temis/{t['slug']}/", f"{t['nome']} · Têmis", t["faz"], main, ld)

# 4) tarefas
for i, t in enumerate(TAR):
    c, ld = crumbs([("Início", "/"), ("Tarefas", "/temis/#tarefas"), (t["nome"], None)])
    outras = "".join(item("/tarefas/" + o["slug"] + "/", o["nome"], o["faz"].split(".")[0] + ".") for o in TAR if o is not t)
    main = (f'<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">{c}'
            f'<a class="voltar" href="/temis/#tarefas">‹ Todas as tarefas</a><p class="eyebrow">Tarefa</p><h1>{E(t["nome"])}</h1>'
            f'<p class="lead">{E(t["faz"])}</p><p><span class="selo-ok">Em funcionamento · testada</span></p>{CTA.format(t="Experimentar no teste grátis")}</div>{STATUE}</div></section>'
            f'<section class="sec"><div class="wrap"><div class="ficha"><div><h2>Exemplo</h2><p>{E(t["exemplo"])}</p><p class="fine">Caso fictício, para ilustrar.</p></div>'
            f'<div><h2>O que você recebe</h2><ul>{"".join("<li>" + E(x) + "</li>" for x in t["recebe"])}</ul></div>'
            f'<div><h2>Revisão humana</h2><p>Petições e pareceres são rascunhos para revisão do advogado. Nada é protocolado pela Têmis.</p></div></div>'
            + (f'<div class="sec-head" style="margin-top:2.5rem"><h2>Outras tarefas</h2></div><div class="lista-t">{outras}</div>' if outras else "")
            + '</div></section>')
    pagina(f"tarefas/{t['slug']}/", f"{t['nome']} com IA jurídica · Têmis", t["faz"], main, ld)

# 5) ocultos: redirecionam para a frente (ou para /temis/), sem índice
def stub(rel, alvo):
    p = OUT / rel / "index.html"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                 f'<meta http-equiv="refresh" content="0;url={alvo}"><link rel="canonical" href="{SITE}{alvo}"><title>Têmis</title>'
                 f'<script>location.replace("{alvo}")</script></head><body><p><a href="{alvo}">Continuar</a></p></body></html>')
for t in OCULTOS: stub(f"temis/{t['slug']}", f"/temis/{t['frente']}/" if t["frente"] in [f["slug"] for f in FRENTES] else "/temis/")
for t in TAR_OC: stub(f"tarefas/{t['slug']}", "/temis/#tarefas")
for velho, alvo in (("protetora-leal", "/temis/protetora-leal/"), ("advogado-do-diabo", "/temis/advogado-do-diabo/")):
    if (OUT / velho).exists(): stub(velho, alvo)

# 6) início
idx = OUT / "index.html"; s = idx.read_text()
nucleo = ('<section class="sec" id="nucleo"><div class="wrap"><div class="sec-head"><p class="eyebrow">Em funcionamento</p>'
          '<h2>O que a Têmis já faz por você</h2><p class="lead">Toque para abrir. Cada item tem a sua página, com exemplo e teste grátis.</p></div>'
          '<div class="lista-t">' + "".join(item("/tarefas/" + t["slug"] + "/", t["nome"], t["faz"].split(".")[0] + ".") for t in TAR)
          + item("/temis/advogado-do-diabo/", "Revisão adversarial", "A peça atacada como a parte contrária faria, antes do protocolo.")
          + item("/temis/jurisprudencia-viva/", "Pesquisa de jurisprudência", "Precedentes e contraprecedentes, com referência verificável.")
          + '</div></div></section>')
s = re.sub(r'<section class="sec" id="nucleo">.*?</section>', lambda m: nucleo, s, flags=re.S)
tarefas = ('<section class="sec" id="tarefas"><div class="wrap"><div class="sec-head"><p class="eyebrow">Por tarefa</p><h2>O que você precisa fazer</h2></div>'
           '<div class="lista-t">' + "".join(item("/tarefas/" + t["slug"] + "/", t["nome"], t["exemplo"]) for t in TAR) + '</div></div></section>')
s = re.sub(r'<section class="sec" id="tarefas">.*?</section>', lambda m: tarefas, s, flags=re.S)
frentes = (f'<section class="sec" id="frentes"><div class="wrap"><div class="sec-head"><p class="eyebrow">{len(FRENTES)} frentes</p>'
           f'<h2>Escolha por onde começar</h2><p class="lead">{len(VIS)} Têmis em funcionamento. Toque numa frente para ver as Têmis dela.</p></div>'
           f'{galeria()}<p><a class="more" href="/temis/">Ver todas as frentes ›</a></p></div></section>')
s = re.sub(r'<section class="sec" id="frentes">.*?</section>', lambda m: frentes, s, flags=re.S)
idx.write_text(s)

# 7) global: CTA de conta, rodapé, nada de "em preparação"
for p in OUT.rglob("*.html"):
    s = p.read_text()
    if 'name="robots" content="noindex"' in s and len(s) < 1200: continue
    o = s
    s = s.replace("Sem cobrança no site · uma amostra gratuita por pessoa", "Teste grátis, um por pessoa · planos e preços após o login")
    s = s.replace('<a class="btn btn-sm" href="/amostra/">Amostra grátis</a>', '<a href="/conta/entrar">Entrar</a><a class="btn btn-sm" href="/conta/cadastro">Teste grátis</a>')
    s = s.replace('<a href="/amostra/">Amostra grátis</a>', '<a href="/conta/cadastro">Teste grátis</a><a href="/conta/entrar">Entrar</a>')
    s = re.sub(r'<a class="mcta" href="/amostra/">[^<]*</a>', '<a class="mcta" href="/conta/cadastro">Começar o teste grátis</a>', s)
    s = re.sub(r'href="/amostra/"', 'href="/conta/cadastro"', s)
    s = re.sub(r'(Todas|Todos) em preparação, no mesmo catálogo[^.<]*\.', 'Em funcionamento, com teste grátis.', s)
    s = re.sub(r'<span class="pill">Em preparação</span>', '', s)
    s = re.sub(r',? ?todas em preparação', '', s)
    s = s.replace("Cada módulo declara o que está pronto, em preparação ou bloqueado.", "Só aparece no site o que passou em teste de funcionamento.")
    if s != o: p.write_text(s)

# /amostra/: o pedido manual vira o cadastro com teste grátis automático
am = OUT / "amostra" / "index.html"
if am.exists():
    s = am.read_text()
    s = re.sub(r'<form id="form-amostra".*?</form>', '<div class="ficha"><div><h2>Teste grátis automático</h2><p>Crie a conta com o seu número da OAB e use na hora: '
               'uma minuta completa, até 20 mensagens ou 30 dias, o que vier primeiro.</p><a class="btn" href="/conta/cadastro">Criar conta e testar</a>'
               '<p class="fine">Já tem conta? <a href="/conta/entrar">Entrar</a>.</p></div></div>', s, flags=re.S)
    s = s.replace("Conte o que você quer testar e retornamos no e-mail informado.", "Crie a conta e use na hora, sem esperar retorno.")
    am.write_text(s)

# 8) CSS, sitemap, _redirects
css = OUT / "assets" / "site.css"
if "nav_pos.py" not in css.read_text(): css.write_text(css.read_text() + CSS)
sm = OUT / "sitemap.xml"; x = sm.read_text()
locs = re.findall(r"<loc>([^<]+)</loc>", x)
novos = [f"{SITE}/temis/{f['slug']}/" for f in FRENTES] + [f"{SITE}/temis/{t['slug']}/" for t in VIS] + [f"{SITE}/tarefas/{t['slug']}/" for t in TAR]
fora = {f"{SITE}/temis/{t['slug']}/" for t in OCULTOS} | {f"{SITE}/tarefas/{t['slug']}/" for t in TAR_OC} | {f"{SITE}/amostra/"}
todos = [l for l in locs if l not in fora] + [n for n in novos if n not in locs]
sm.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + "\n".join(f"<url><loc>{l}</loc></url>" for l in todos) + "\n</urlset>\n")
rd = OUT / "_redirects"
if rd.exists():
    rd.write_text("\n".join(l for l in rd.read_text().splitlines() if not re.match(r"^/(temis|tarefas|protetora-leal|advogado-do-diabo)\b", l)) + "\n")

# 9) conferência
ruins = [str(p.relative_to(OUT)) for p in OUT.rglob("*.html") if re.search(r"em prepara", p.read_text(), re.I)]
if ruins: sys.exit(f"[nav_pos] ainda há 'em preparação' em: {ruins}")
print(f"[nav_pos] ok: {len(FRENTES)} frentes, {len(VIS)} Têmis, {len(TAR)} tarefas; ocultos {len(OCULTOS)}+{len(TAR_OC)}; sitemap {len(todos)} URLs")
