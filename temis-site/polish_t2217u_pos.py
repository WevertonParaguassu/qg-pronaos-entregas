#!/usr/bin/env python3
"""t2217u · polimento final do site público da Têmis (último passo do build.sh).
- Folha /assets/polish-t2217u.css ligada em todas as páginas (tipografia, espaçamento, cartões acima da estátua,
  etiquetas App Têmis alinhadas, grade dos planos 3+2, rodapé arrumado, foco visível, contraste).
- Copia /assets/temis-conta.css (mesma identidade para /conta/*, login e painel, servida pelo próprio site).
- Home sem o painel de demonstração sintético (hero-shot e a seção «Demonstração").
- Menu principal com o item da página atual marcado (aria-current) em vez de sempre «Início"/«As Têmis".
- Texto coerente: preços dos planos na página Planos; preço de aplicativo/combos dentro da conta; «aplicativos Têmis".
- /planos/: faixa de seção do comparativo cobrindo as 9 colunas.
Idempotente (marca t2217u-polish). Rollback: apagar a linha deste script no build.sh.
"""
import re, sys, pathlib, shutil
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
HERE = pathlib.Path(__file__).parent
MARCA = "t2217u-polish"
LINK = f'<link rel="stylesheet" href="/assets/polish-t2217u.css?v=3" data-m="{MARCA}">'

TROCAS = [
    # preços: planos são públicos; aplicativo avulso e combos, dentro da conta
    ("Os preços dos planos, das aplicações e dos combos aparecem depois do login",
     "Os preços dos planos estão na página Planos; os dos aplicativos Têmis avulsos e dos combos aparecem dentro da conta"),
    ("Os preços só aparecem depois do login; não são publicados nas páginas abertas",
     "Os preços dos planos estão na página Planos; os dos aplicativos Têmis avulsos e dos combos aparecem dentro da conta"),
    ("Os preços só aparecem depois do login", "Os preços dos planos estão na página Planos"),
    ("Os preços aparecem depois do login", "Os preços dos planos estão na página Planos"),
    ("Cada aplicação tem a sua página e o seu preço — este último só depois do login",
     "Cada aplicativo Têmis tem a sua página; o preço avulso aparece dentro da conta"),
    ("os de cada aplicação aparecem depois do login", "os de cada aplicativo Têmis aparecem dentro da conta"),
    ('href="/temis/#tarefas"', 'href="/tarefas/"'),
    ("Esta aplicação (adaptador legado)", "Este aplicativo Têmis (conector legado)"),
    ("Adaptador legado", "Conector legado"), ("adaptador legado", "conector legado"),
    ("Preços após o login.</p>", "Preços dos planos na página Planos.</p>"),
    # aplicativos Têmis (t2211u)
    ("conheça as aplicações da Têmis", "conheça os aplicativos Têmis"),
    ("28 aplicações no catálogo", "28 aplicativos Têmis no catálogo"),
    ("28 aplicações. Contrate as que quiser.", "28 aplicativos Têmis. Contrate os que quiser."),
    ("as aplicações são especialidades dela", "os aplicativos Têmis são especialidades dela"),
    ("Ver as 28 aplicações", "Ver os 28 aplicativos Têmis"),
    ("As aplicações ainda não abertas para contratação avulsa permanecem no catálogo, sem convite para experimentá-las.",
     "Os aplicativos Têmis ainda não abertos para contratação avulsa permanecem no catálogo, sem convite para experimentá-los."),
    ("quais aplicações da Têmis atuam", "quais aplicativos Têmis atuam"),
    ("quais aplicações atuaram", "quais aplicativos Têmis atuaram"),
    ("quais aplicações atuam", "quais aplicativos Têmis atuam"),
    ("nas aplicações já disponíveis", "nos aplicativos Têmis já disponíveis"),
    ("Testar esta aplicação", "Testar este aplicativo Têmis"),
    ("Navegar entre as aplicações", "Navegar entre os aplicativos Têmis"),
    ("o preço mensal desta aplicação, pode somá-la a outras", "o preço mensal deste aplicativo Têmis, pode somá-lo a outros"),
    ("o preço mensal de cada uma e fe", "o preço mensal de cada um e fe"),
    (" aplicações desta frente", " aplicativos Têmis desta frente"),
    ("Esta aplicação é entregue", "Este aplicativo Têmis é entregue"),
    (" · aplicação da Têmis", " · aplicativo Têmis"),
    ("O catálogo lista as 28 aplicações. 25 aplicações podem ser contratadas avulsas",
     "O catálogo lista os 28 aplicativos Têmis. 25 podem ser contratados avulsos"),
    ("entra em todos os planos e não é vendida à parte", "entra em todos os planos e não é vendido à parte"),
    ("Catálogo das 28 aplicações da Têmis", "Catálogo dos 28 aplicativos Têmis"),
    ("As 28 aplicações da Têmis", "Os 28 aplicativos Têmis"),
    ("As 28 aplicações", "Os 28 aplicativos Têmis"),
    ("Escolha, à la carte, quais das 28 aplicações da Têmis você quer", "Escolha, à la carte, quais dos 28 aplicativos Têmis você quer"),
    ("Monte o seu conjunto de aplicações", "Monte o seu conjunto de aplicativos Têmis"),
    ("à la carte das aplicações da Têmis", "à la carte dos aplicativos Têmis"),
    ("100% das 28 aplicações", "100% dos 28 aplicativos Têmis"),
    ("A aplicação vigente é Fontes do Direito", "O aplicativo Têmis vigente é Fontes do Direito"),
    ("Contrate à la carte as aplicações que quiser", "Contrate à la carte os aplicativos Têmis que quiser"),
    ("Pacotes por tarefa não dizem quais aplicações atuam", "Pacotes por tarefa não dizem quais aplicativos Têmis atuam"),
    ("libera todas as aplicações do combo", "libera todos os aplicativos Têmis do combo"),
    ("Além da contratação avulsa de cada aplicação", "Além da contratação avulsa de cada aplicativo Têmis"),
    ("bancada pronta de aplicações", "bancada pronta de aplicativos Têmis"),
    ("montadas só com aplicações já disponíveis", "montadas só com aplicativos Têmis já disponíveis"),
    ("bancadas de aplicações por especialidade", "bancadas de aplicativos Têmis por especialidade"),
    ("Combos de aplicações", "Combos de aplicativos Têmis"),
    ("As aplicações que cooperam", "Os aplicativos Têmis que cooperam"),
    # home: compromisso de documentos, curto e no mesmo tom das outras caixas
    ("O site aberto não recebe autos. Depois do login, os documentos ficam nos servidores da própria PRONAOS e, por padrão, são lidos só pelos modelos que rodam lá. No plano Ultra, só com o opt-in do cliente em cada caso, uma versão anonimizada da pergunta (sem nomes, CPF/CNPJ, número de processo ou fatos que identifiquem alguém) pode ser consultada com um conselho de IAs externas; os documentos não saem. Detalhes em Segurança e sigilo.",
     "O site aberto não recebe autos. Depois do login, os documentos ficam nos servidores da Têmis e são lidos pelos modelos que rodam lá. No Ultra, só com o seu opt-in em cada caso, uma versão anonimizada da pergunta pode ir a um conselho de IAs externas; os documentos não saem."),
    ("Cada escritório tem o seu espaço. Em teste com dois escritórios sintéticos (22/11/2026), um não enxergou caso, documento, memória nem tarefa do outro.",
     "Cada escritório tem o seu espaço: um não enxerga caso, documento, memória nem tarefa do outro."),
]

def marca_nav(h, rel):
    """aria-current no item do menu principal que corresponde à página."""
    m = re.search(r'(<nav id="nav"[^>]*>)(.*?)(</nav>)', h, re.S)
    if not m: return h
    itens = m.group(2).replace(" aria-current=page", "").replace(' aria-current="page"', "")
    caminho = "/" + rel
    melhor, tam = None, 0
    for href in re.findall(r'<a href="(/[^"]*)"', itens):
        if href.startswith("/conta"): continue
        ok = (caminho == href) if href == "/" else caminho.startswith(href)
        if ok and len(href) > tam: melhor, tam = href, len(href)
    if melhor:
        itens = itens.replace(f'<a href="{melhor}">', f'<a href="{melhor}" aria-current="page">', 1)
    return h[:m.start()] + m.group(1) + itens + m.group(3) + h[m.end():]

def home(h):
    h = re.sub(r'<figure class="hero-shot">.*?</figure>\s*', '', h, count=1, flags=re.S)
    h = re.sub(r'<section class="sec" id="demonstracao">.*?</section>\s*', '', h, count=1, flags=re.S)
    return h

CPF_RE = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
MASC = "***.***.***-**"
def laboratorio():
    """t2217u-lab: tira o CPF fictício (texto, imagens e PDF) e põe noindex no /laboratorio/."""
    import base64, tarfile, io
    b64 = HERE / "lab_red_t2217u.tgz.b64"
    if b64.exists():
        tf = tarfile.open(fileobj=io.BytesIO(base64.b64decode(b64.read_text())), mode="r:gz")
        for m in tf.getmembers():
            dado = tf.extractfile(m).read()
            if m.name.endswith(".pdf"): alvos = [OUT / "laboratorio" / m.name]
            else: alvos = [OUT / "img" / "laboratorio" / m.name] + ([OUT / "laboratorio" / "docs" / m.name] if m.name.startswith("doc-") else [])
            for a in alvos:
                if a.parent.exists(): a.write_bytes(dado)
    for t in (OUT / "laboratorio").glob("*.txt"):
        x = t.read_text(encoding="utf-8"); y = CPF_RE.sub(MASC, x)
        if y != x: t.write_text(y, encoding="utf-8")
    sm = OUT / "sitemap.xml"
    if sm.exists():
        x = sm.read_text(encoding="utf-8"); y = re.sub(r"<url><loc>[^<]*/laboratorio/</loc>.*?</url>\s*", "", x, flags=re.S)
        if y != x: sm.write_text(y, encoding="utf-8")

def lab_html(h):
    h = CPF_RE.sub(MASC, h)
    h = h.replace(f"({MASC} × {MASC}) — o revisor pediu confirmação; é um número fictício", f"({MASC} × {MASC}, dígitos ocultados) — o revisor pediu confirmação")
    for n in ("doc-1", "doc-3", "peticao-1"):
        h = h.replace(f"/img/laboratorio/{n}.webp?v=t1951u", f"/img/laboratorio/{n}.webp?v=t2217u")
    for n in ("doc-1", "doc-3"):
        h = h.replace(f'href="/laboratorio/docs/{n}.webp"', f'href="/laboratorio/docs/{n}.webp?v=t2217u"')
    h = h.replace('href="/laboratorio/minuta-peticao-inicial.pdf"', 'href="/laboratorio/minuta-peticao-inicial.pdf?v=t2217u"')
    if 'name="robots"' not in h: h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex, nofollow" data-m="t2217u-lab">', 1)
    else: h = re.sub(r'<meta name="robots" content="[^"]*"', '<meta name="robots" content="noindex, nofollow"', h, count=1)
    return h

def main():
    assets = OUT / "assets"; assets.mkdir(exist_ok=True)
    shutil.copy(HERE / "polish-t2217u.css", assets / "polish-t2217u.css")
    shutil.copy(HERE / "temis-conta.css", assets / "temis-conta.css"); shutil.copy(HERE / "temis-app.css", assets / "temis-app.css")
    n = 0
    for f in OUT.rglob("*.html"):
        rel = f.relative_to(OUT).as_posix()
        rel = "" if rel == "index.html" else (rel[:-10] if rel.endswith("/index.html") else rel)
        h = f.read_text(encoding="utf-8"); h0 = h
        for a, b in TROCAS: h = h.replace(a, b)
        if rel == "": h = home(h)
        if rel == "404.html":
            h = re.sub(r'<link rel="canonical" href="[^"]*/404-page/">', '', h)
            h = re.sub(r'<meta property="og:url" content="[^"]*/404-page/">', '', h)
        if rel == "planos/":
            h = h.replace('<tr class="tm-g"><th colspan="8">', '<tr class="tm-g"><th colspan="9">')
            h = h.replace('<div id="agente" id="max">', '<div id="agente" class="tm-max">')
        if rel == "laboratorio/": h = lab_html(h)
        h = marca_nav(h, rel)
        if MARCA not in h and "</head>" in h: h = h.replace("</head>", LINK + "</head>", 1)
        if h != h0: f.write_text(h, encoding="utf-8"); n += 1
    laboratorio()
    print(f"[polish_t2217u] ok: {n} páginas polidas")

if __name__ == "__main__": main()
