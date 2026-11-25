#!/usr/bin/env python3
"""t2306u: blog educativo + páginas /para-quem-e/ para estudantes, Defensoria,
servidores, peritos e cartórios. Sem preço da semana cravado (CTA aponta a /planos/).
Rollback: apagar a linha deste script no build.sh (o restante do site não muda).
Uso: python3 blog_juridico_t2306u_pos.py out
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

HOJE = date(2026, 11, 25).isoformat()  # data editorial deste lote; lastmod do sitemap
BASE = "https://agentetemis.com"
CTA = "/planos/?utm_source={src}&utm_medium=organic&utm_campaign=inauguracao_s1&utm_content={c}"


def _chrome(out: Path) -> tuple[str, str, str]:
    """Reaproveita head de CSS + header/footer de uma página já gerada."""
    cand = [
        out / "para-quem-e" / "advocacia-autonoma" / "index.html",
        out / "para-quem-e" / "index.html",
        out / "tarefas" / "peticao-inicial" / "index.html",
        out / "index.html",
    ]
    html = ""
    for p in cand:
        if p.is_file():
            html = p.read_text(encoding="utf-8", errors="ignore")
            break
    if not html:
        raise SystemExit("blog_juridico_t2306u_pos: não achei página-base em out/")
    # header: do <header até o fim do primeiro header; fallback: de <body até <main or section
    hm = re.search(r"(<header\b.*?</header>)", html, re.I | re.S)
    header = hm.group(1) if hm else ""
    fm = re.search(r"(<footer\b.*?</footer>)", html, re.I | re.S)
    footer = fm.group(1) if fm else ""
    # folhas de estilo e ícones do <head> original (sem title/canonical/description)
    links = "\n".join(re.findall(r'<link rel="(?:icon|apple-touch-icon|manifest|stylesheet)[^>]*>', html, re.I))
    extras = "\n".join(re.findall(r'<link rel="preconnect"[^>]*>', html, re.I))
    css = extras + "\n" + links
    if 'href="/assets/site.css"' not in css:
        css += '\n<link rel="stylesheet" href="/assets/site.css">'
    if "polish-t2217u.css" not in css:
        css += '\n<link rel="stylesheet" href="/assets/polish-t2217u.css?v=4">'
    return header, footer, css


def _pagina(title, desc, canonical, header, footer, css, body_inner, og_type="article"):
    can = BASE + canonical
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#060D1B">
<link rel="canonical" href="{can}">
<link rel="alternate" hreflang="pt-BR" href="{can}">
<link rel="alternate" hreflang="x-default" href="{can}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Têmis">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{BASE}/img/og-1200x630.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
{css}
</head><body>
{header}
<main>
{body_inner}
</main>
{footer}
</body></html>
"""


def _artigo(h1, lead, blocos, src, content, header, footer, css, kicker="Blog da Têmis"):
    cta = CTA.format(src=src, c=content)
    partes = [f'<section class="sec"><div class="wrap"><p class="kicker">{kicker}</p><h1>{h1}</h1><p class="lead">{lead}</p>']
    for b in blocos:
        if b[0] == "h2":
            partes.append(f"<h2>{b[1]}</h2>")
        else:
            partes.append(f"<p>{b[1]}</p>")
    partes.append(
        f'<p class="cta-box">A oferta vigente de lançamento, com os valores da semana em vigor, está em '
        f'<a href="{cta}">agentetemis.com/planos</a>. Turma aberta · vagas limitadas por plano. '
        f"Quem assina a peça continua responsável por ela.</p></div></section>"
    )
    return "\n".join(partes)


def _publico(h1, lead, blocos, src, content, header, footer, css):
    return _artigo(h1, lead, blocos, src, content, header, footer, css, kicker="Para quem é a Têmis")


PAGINAS = []  # filled in main with chrome


def definir_conteudo():
    artigos = []
    artigos.append((
        "blog/index.html",
        "Blog da Têmis — prática jurídica e IA",
        "Textos práticos sobre petição com IA, revisão de quem assina e o uso da Têmis por advogados, estudantes, defensores, servidores, peritos e cartórios.",
        "/blog/",
        "website",
        lambda header, footer, css: f'''<section class="sec"><div class="wrap">
<p class="kicker">Blog da Têmis</p>
<h1>Prática jurídica e IA, com a revisão no centro</h1>
<p class="lead">Artigos curtos para quem redige, revisa ou organiza peças. Sem atalho que tire a responsabilidade de quem assina.</p>
<div class="grid3">
<a class="mini link-card" href="/blog/peticao-com-ia/"><h3>Petição com IA</h3><p>O que dá para automatizar na petição inicial e o que continua na mão de quem assina.</p><span class="more">Ler →</span></a>
<a class="mini link-card" href="/blog/ia-para-advogados/"><h3>IA para advogados</h3><p>Como usar um agente jurídico no escritório ou na advocacia autônoma, sem abrir mão da revisão.</p><span class="more">Ler →</span></a>
<a class="mini link-card" href="/blog/ia-para-estudantes-de-direito/"><h3>IA para estudantes de Direito</h3><p>Laboratório de peças na faculdade: aprender com a minuta, não entregar sem ler.</p><span class="more">Ler →</span></a>
</div>
<p>Também há páginas para <a href="/para-quem-e/">cada perfil</a>, inclusive Defensoria, servidores do Judiciário, peritos e cartórios, e o catálogo de <a href="/tarefas/">tarefas</a>.</p>
</div></section>'''
    ))
    artigos.append((
        "blog/peticao-com-ia/index.html",
        "Petição com IA: o que automatizar e o que continua com quem assina · Têmis",
        "Como usar IA na petição inicial: organizar fatos, estruturar pedidos e revisar. A responsabilidade permanece de quem assina a peça.",
        "/blog/peticao-com-ia/",
        "article",
        lambda header, footer, css: _artigo(
            "Petição com IA: o que dá para automatizar e o que continua com quem assina",
            "O gargalo de uma petição inicial quase nunca é «abrir o editor». É ler o caso, não perder um pedido e revisar o que vai assinado.",
            [
                ("h2", "O que a IA faz bem nesta tarefa"),
                ("p", "A partir dos documentos do caso, um agente jurídico pode sugerir uma estrutura de fatos, apontar inconsistências, listar pedidos e devolver uma minuta para revisão. Isso vale para quem já advoga e também para o estudante que está montando a primeira peça no laboratório da faculdade."),
                ("h2", "O que não se transfere para a máquina"),
                ("p", "A tese, o tom, o que entra ou sai do pedido e a decisão de protocolar continuam com quem assina. A Têmis não é um substituto do advogado, do defensor ou do parecerista: é um posto de trabalho que devolve texto e alertas para a revisão humana — inclusive com o Conselho das 4, quando o plano comporta mais de um olhar sobre a mesma peça."),
                ("h2", "Como começar com critério"),
                ("p", "Escolha um caso real ou uma peça de estudo, reúna os documentos, peça a minuta e compare com o que você assinou ou entregaria. O critério é o mesmo na advocacia autônoma, no escritório, na Defensoria e na sala de aula: nada vai ao protocolo sem leitura."),
            ],
            "blog", "artigo_peticao-com-ia", header, footer, css,
        )
    ))
    artigos.append((
        "blog/ia-para-advogados/index.html",
        "IA para advogados: revisão humana no centro · Têmis",
        "Como advogados autônomos, escritórios e departamentos jurídicos usam a Têmis para redigir e revisar peças, com a responsabilidade de quem assina.",
        "/blog/ia-para-advogados/",
        "article",
        lambda header, footer, css: _artigo(
            "IA para advogados: a revisão humana no centro",
            "Ferramenta nenhuma assume o risco da procuração. O valor está em render mais na triagem, na minuta e na conferência — e ainda assim ler o que se assina.",
            [
                ("h2", "Sozinho, em sociedade ou em departamento"),
                ("p", "Na advocacia autônoma, o ganho é tempo de qualidade: a Têmis organiza o acervo e devolve minuta, e o advogado revisa como revisaria a peça de um estagiário experiente. No escritório, o ganho é padrão: a mesma qualidade de partida, com o conhecimento da casa preservado. No departamento jurídico, o ganho é trilha e rastreio das versões que o time efetivamente aprovou."),
                ("h2", "Ética prática, não slogan"),
                ("p", "Dado de cliente, segredo de justiça e peça de menor de idade não se tratam como material genérico. A Têmis foi desenhada para a revisão permanecer no centro e para o titular da conta decidir o que entra no contexto. Se uma tarefa pede parecer, laudo ou cálculo, o caminho é o mesmo: minuta + conferência de quem assina ou certifica."),
                ("h2", "Oferta de lançamento"),
                ("p", "Os valores da semana em vigor não ficam cravados neste artigo, porque a condição muda. A tabela viva está na página de planos, no endereço do final deste texto."),
            ],
            "blog", "artigo_ia-para-advogados", header, footer, css,
        )
    ))
    artigos.append((
        "blog/ia-para-estudantes-de-direito/index.html",
        "IA para estudantes de Direito: laboratório de peças, não atalho · Têmis",
        "Como o estudante de Direito pode usar a Têmis para aprender a redigir e revisar petições, sem entregar peça sem ler.",
        "/blog/ia-para-estudantes-de-direito/",
        "article",
        lambda header, footer, css: _artigo(
            "IA para estudantes de Direito: laboratório, não atalho",
            "Na faculdade, o uso honesto de um agente jurídico é comparar a minuta com o que a disciplina pede — e reescrever o que não estiver no padrão de quem um dia vai assinar.",
            [
                ("h2", "O que muda no estudo da prática"),
                ("p", "Em vez de começar do branco, o estudante parte de uma minuta e treina o olhar de revisão: faltou causa de pedir? O pedido é genérico? O documento citado está nos autos de estudo? Esse é o mesmo músculo que o advogado usa no dia a dia."),
                ("h2", "O que a faculdade (e a OAB) ainda exigem de você"),
                ("p", "A autoria e a compreensão da peça continuam suas. Entregar texto sem ler, em trabalho, em núcleo de prática ou em exame, é o contrário do que se deve aprender aqui. A Têmis serve como bancada: você traz o caso, lê o resultado, anota o que mudaria e só então considera a peça pronta."),
                ("h2", "Pesquisa e iniciação científica"),
                ("p", "Para monografia e pesquisa, a IA pode ajudar a organizar doutrina e a testar estrutura de raciocínio. Não substitui citação conferida, nem a revisão do orientador. Artigo em revista científica ou na SciELO segue o rito de cada veículo — este blog não é publicação acadêmica avaliada por pares."),
            ],
            "blog", "artigo_estudantes", header, footer, css,
        )
    ))
    publicos = []
    publicos.append((
        "para-quem-e/estudantes-de-direito/index.html",
        "Têmis para estudantes de Direito",
        "Para quem está na faculdade, no núcleo de prática ou na pesquisa e quer treinar peças com IA, sem abrir mão de ler e revisar.",
        "/para-quem-e/estudantes-de-direito/",
        "website",
        lambda h, f, c: _publico(
            "Estudantes de Direito",
            "Para quem está na graduação, no núcleo de prática, na iniciação científica ou se preparando para a OAB e quer uma bancada de peças — não um atalho.",
            [
                ("h2", "Como a Têmis entra no estudo"),
                ("p", "Você traz o caso de aula ou o processo-modelo, pede a minuta e treina a revisão: pedidos, fatos, documentos e linguagem. O aprendizado está no que você muda, não no que a máquina devolve pronto."),
                ("h2", "O que permanece com você"),
                ("p", "A compreensão da matéria, a ética acadêmica e, no futuro, a responsabilidade de quem assina. Há um artigo inteiro sobre esse uso em <a href=\"/blog/ia-para-estudantes-de-direito/\">IA para estudantes de Direito</a>."),
            ],
            "site", "para-quem_estudantes", h, f, c,
        )
    ))
    publicos.append((
        "para-quem-e/defensoria/index.html",
        "Têmis para a Defensoria Pública",
        "Para defensores e equipes da Defensoria que precisam triar, redigir e revisar volume alto de peças, com a responsabilidade de quem assina.",
        "/para-quem-e/defensoria/",
        "website",
        lambda h, f, c: _publico(
            "Defensoria Pública",
            "Para defensores e equipes que convivem com volume alto, prazo curto e o dever de não perder o assistido no meio da fila.",
            [
                ("h2", "Triagem e minuta, com revisão no fim"),
                ("p", "A Têmis ajuda a organizar documentos, devolver uma primeira versão da peça e apontar lacunas. A decisão, o tom e o ato de assinar a peça continuam com o defensor ou com quem a casa designar."),
                ("h2", "Cuidado com o que é sigiloso"),
                ("p", "Dado de assistido e peça coberta por sigilo pedem o mesmo rigor de sempre. A ferramenta entra como posto de trabalho, não como publicação."),
            ],
            "site", "para-quem_defensoria", h, f, c,
        )
    ))
    publicos.append((
        "para-quem-e/servidores-do-judiciario/index.html",
        "Têmis para servidores do Judiciário e áreas jurídicas",
        "Para servidores do Judiciário, do MP e de áreas jurídicas da Administração que redigem minutas, despachos de apoio ou pareceres, com revisão de quem assina.",
        "/para-quem-e/servidores-do-judiciario/",
        "website",
        lambda h, f, c: _publico(
            "Servidores do Judiciário e áreas jurídicas",
            "Para quem redige minuta, apoio a despacho, parecer interno ou organiza acervo — sempre sob a revisão de quem tem atribuição para assinar.",
            [
                ("h2", "Apoio à minuta, não substituto da atribuição"),
                ("p", "A Têmis pode devolver uma estrutura, cruzar documentos e apontar inconsistências. Não ocupa o lugar da atribuição legal de quem despacha, relata ou assina."),
                ("h2", "Normas da casa em primeiro lugar"),
                ("p", "Uso de ferramenta de IA no órgão depende do que a corregedoria, o tribunal ou a chefia autorizarem. Este texto não é convite a burlar norma interna: é uma apresentação da ferramenta, para quem puder adotá-la no regime da própria instituição."),
            ],
            "site", "para-quem_servidores", h, f, c,
        )
    ))
    publicos.append((
        "para-quem-e/peritos/index.html",
        "Têmis para peritos e assistentes técnicos",
        "Para peritos e assistentes técnicos que organizam quesitos, laudos e documentos, com a responsabilidade de quem assina o trabalho técnico.",
        "/para-quem-e/peritos/",
        "website",
        lambda h, f, c: _publico(
            "Peritos e assistentes técnicos",
            "Para quem vive de quesitos, laudos e acervo técnico e quer apoio para organizar o material e redigir a primeira versão, sem abrir mão da conferência profissional.",
            [
                ("h2", "Do quesito à minuta do laudo"),
                ("p", "A Têmis ajuda a reunir documentos, estruturar respostas a quesitos e devolver uma minuta. A conclusão técnica e o ato de assinar o laudo continuam com o perito ou o assistente."),
                ("h2", "Peça e laudo não se misturam"),
                ("p", "Quando o trabalho toca a análise de um laudo já existente, há uma tarefa específica no catálogo: <a href=\"/tarefas/analise-laudo/\">análise de laudo</a>."),
            ],
            "site", "para-quem_peritos", h, f, c,
        )
    ))
    publicos.append((
        "para-quem-e/cartorios/index.html",
        "Têmis para cartórios e serventias",
        "Para cartórios e serventias que organizam documentos, minutas e comunicações, com a responsabilidade de quem certifica e assina.",
        "/para-quem-e/cartorios/",
        "website",
        lambda h, f, c: _publico(
            "Cartórios e serventias",
            "Para equipes de serventia que lidam com volume de documentos, minutas e comunicações e precisam de ordem, sem abrir mão da fé pública de quem certifica.",
            [
                ("h2", "Organizar, redigir, conferir"),
                ("p", "A Têmis pode ajudar a classificar documentos, devolver uma minuta de comunicação e apontar lacunas. O ato cartorário, a certidão e o dever de quem certifica não se terceirizam."),
                ("h2", "Uso conforme a norma da serventia"),
                ("p", "Como em qualquer ferramenta, o uso no cartório depende do que a correiçao, o tribunal e a própria serventia autorizarem. A apresentação aqui é informativa."),
            ],
            "site", "para-quem_cartorios", h, f, c,
        )
    ))
    return artigos + publicos


def _escreve(out: Path, rel: str, html: str):
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def _sitemap(out: Path, caminhos: list[str]):
    sm = out / "sitemap.xml"
    if not sm.is_file():
        return
    txt = sm.read_text(encoding="utf-8")
    added = []
    for path in caminhos:
        loc = BASE + path
        if loc in txt:
            continue
        block = f"<url><loc>{loc}</loc><lastmod>{HOJE}</lastmod></url>\n"
        if "</urlset>" in txt:
            txt = txt.replace("</urlset>", block + "</urlset>", 1)
            added.append(loc)
    sm.write_text(txt, encoding="utf-8")
    return added


def _indice_para_quem(out: Path):
    idx = out / "para-quem-e" / "index.html"
    if not idx.is_file():
        return
    html = idx.read_text(encoding="utf-8")
    cards = '''<a class="mini link-card" href="/para-quem-e/estudantes-de-direito/"><h3>Estudantes de Direito</h3><p>Para a faculdade, o núcleo de prática e a pesquisa: bancada de peças, não atalho.</p><span class="more">Ver como ajuda →</span></a>
<a class="mini link-card" href="/para-quem-e/defensoria/"><h3>Defensoria Pública</h3><p>Para defensores e equipes com volume alto e a responsabilidade de quem assina.</p><span class="more">Ver como ajuda →</span></a>
<a class="mini link-card" href="/para-quem-e/servidores-do-judiciario/"><h3>Servidores do Judiciário</h3><p>Para minutas e pareceres de apoio, sob a atribuição de quem assina no órgão.</p><span class="more">Ver como ajuda →</span></a>
<a class="mini link-card" href="/para-quem-e/peritos/"><h3>Peritos e assistentes</h3><p>Para quesitos, laudos e acervo técnico, com conferência de quem assina o trabalho.</p><span class="more">Ver como ajuda →</span></a>
<a class="mini link-card" href="/para-quem-e/cartorios/"><h3>Cartórios e serventias</h3><p>Para organizar documentos e minutas, sem abrir mão de quem certifica.</p><span class="more">Ver como ajuda →</span></a>'''
    if "/para-quem-e/estudantes-de-direito/" in html:
        return
    def _inj(m):
        return m.group(1) + m.group(2) + cards + m.group(3)
    html2, n = re.subn(r'(<div class="grid3">)(.*?)(</div>)', _inj, html, count=1, flags=re.S)
    if n == 0:
        html2 = html.replace("</main>", "<section class=\"sec\"><div class=\"wrap\"><div class=\"grid3\">" + cards + "</div></div></section></main>", 1)
    idx.write_text(html2, encoding="utf-8")


def _nav_blog(out: Path):
    """Se o rodapé ou o menu tiverem um bloco de links institucionais, acrescenta Blog uma vez."""
    for p in out.rglob("index.html"):
        html = p.read_text(encoding="utf-8", errors="ignore")
        if 'href="/blog/"' in html:
            continue
        if 'href="/para-quem-e/"' in html and "<footer" in html:
            html2 = html.replace('href="/para-quem-e/"', 'href="/blog/" data-t2306u="1"', 1)
            # that's dangerous (replaces first para-quem which may be in header nav as the item itself)
            # skip automatic nav injection to avoid breaking menus; blog is linked from new pages and sitemap
            pass


def main():
    if len(sys.argv) < 2:
        raise SystemExit("uso: blog_juridico_t2306u_pos.py out")
    out = Path(sys.argv[1]).resolve()
    header, footer, css = _chrome(out)
    caminhos = []
    for rel, title, desc, canonical, og, bodyfn in definir_conteudo():
        inner = bodyfn(header, footer, css)
        html = _pagina(title, desc, canonical, header, footer, css, inner, og)
        # recusa palavras de marketing proibidas no visível (não atinge «justiça gratuita», que não usamos aqui)
        vis = re.sub(r"<[^>]+>", " ", html).lower()
        for proibida in (" assinar o plano", "assinatura", "gratuita", "grátis", "gratis"):
            if proibida in vis and proibida != "assinatura":
                # «assinatura» como substantivo comercial
                pass
        for proibida in ("gratuita", "grátis", "gratis"):
            if proibida in vis:
                raise SystemExit(f"palavra evitada na página {rel}: {proibida}")
        if re.search(r"\bassinatura\b", vis):
            raise SystemExit(f"palavra evitada na página {rel}: assinatura")
        _escreve(out, rel, html)
        caminhos.append(canonical if canonical.endswith("/") else canonical + "/")
    _indice_para_quem(out)
    added = _sitemap(out, caminhos)
    print("[blog_juridico_t2306u] paginas=%s sitemap_novas=%s" % (len(caminhos), len(added or [])))


if __name__ == "__main__":
    main()
