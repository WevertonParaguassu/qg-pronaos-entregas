#!/usr/bin/env python3
"""Pós-processador t1932u/t1933u: confiança, nova home, laboratório, catálogo das 28 apps,
contratação avulsa/combos (sem preços) e limpeza de cadastro por OAB.

Roda no build do Render, depois de nav_pos.py e seo_pos.py, sobre out/.
Não altera site.tgz.b64, planos.json, vendas_config.json nem a plataforma.
Rollback: apagar a linha do build.sh que chama este script.

Sem preços, sem AggregateRating, sem dados pessoais do Weverton,
sem 'Em preparação' e sem 'disponível em breve' no site público.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
HERE = Path(__file__).resolve().parent
SITE = "https://agentetemis.com"
TODAY = date.today().isoformat()
E = htmllib.escape

def _find_nav():
    for p in (
        HERE / "navegacao.json",
        HERE.parent / "navegacao.json",
        Path("/workspace/temis_vendas/site/navegacao.json"),
    ):
        if p.is_file():
            return p
    raise SystemExit("[confianca_pos] navegacao.json não encontrado")

NAV = json.loads(_find_nav().read_text(encoding="utf-8"))
FRENTES = {f["slug"]: f for f in NAV["frentes"]}
TEMIS = list(NAV["temis"])
TAREFAS = list(NAV.get("tarefas") or [])
def eh_contratavel(t):
    if not isinstance(t, dict):
        return bool(t)
    return bool(t.get("testado") or t.get("contratavel"))

def eh_incluido(t):
    if not isinstance(t, dict):
        return False
    return bool(t.get("incluido")) and not eh_contratavel(t)

AVAIL = [t for t in TEMIS if eh_contratavel(t)]
SOON = [t for t in TEMIS if not eh_contratavel(t) and not eh_incluido(t)]
INCLUIDOS = [t for t in TEMIS if eh_incluido(t)]

# Textos honestos para as 10 apps ainda não contratáveis avulsas (facetas.json + TEMIS_AGENTE.md)
SOON_COPY = {
    "hub-juridico": {
        "faz": "Pensa o roteamento e a revisão jurídica entre várias capacidades da Têmis.",
        "exemplo": "Um pedido complexo seria distribuído entre análise, fontes e revisão — quando esta aplicação estiver disponível para contratação avulsa.",
        "recebe": ["Roteamento entre capacidades", "Revisão jurídica multi-capacidade"],
    },
    "especialistas-juridicos": {
        "faz": "Encaminha o pedido ao recorte especializado mais adequado da Têmis.",
        "exemplo": "Um caso tributário e um previdenciário não receberiam o mesmo recorte de análise.",
        "recebe": ["Encaminhamento por especialidade"],
    },
    "nous": {
        "faz": "Oferece um conselho interdisciplinar de análise, como lente de raciocínio da Têmis.",
        "exemplo": "Um problema que mistura fato, norma e contexto poderia ser olhado por vários ângulos antes da minuta.",
        "recebe": ["Notas de análise interdisciplinar"],
    },
    "pericial": {
        "faz": "Organiza rotas de análise pericial (quesitos, pontos de impugnação, consistência do laudo).",
        "exemplo": "A partir de um laudo sintético, apontar o que conferir ou impugnar — quando estiver disponível avulsa.",
        "recebe": ["Pontos do laudo", "Sugestão de quesitos"],
    },
    "fontes-do-direito-legado": {
        "faz": "Adaptador legado de acesso a fontes jurídicas. A aplicação vigente é Fontes do Direito.",
        "exemplo": "A consulta oficial de legislação no teste de 22/11/2026 usou a base local do Planalto (Fontes do Direito).",
        "recebe": ["Acesso a fontes"],
    },
    "politeia": {
        "faz": "Lente de inteligência constitucional contemporânea.",
        "exemplo": "Um tema constitucional seria lido à luz da hierarquia de fontes — quando estiver disponível avulsa.",
        "recebe": ["Notas de leitura constitucional"],
    },
    "cupula-v2": {
        "faz": "Perfis e cuidados para atuação em tribunais superiores.",
        "exemplo": "Um recurso excepcional pediria um recorte próprio de admissibilidade e tese — quando estiver disponível avulsa.",
        "recebe": ["Recorte para tribunais superiores"],
    },
    "outcome-loop": {
        "faz": "Pretende vincular estratégia, execução e resultado do caso, para aprendizado do próprio escritório.",
        "exemplo": "Depois de uma sentença, registrar o que a estratégia previu e o que o resultado mostrou.",
        "recebe": ["Registro de desfecho", "Aprendizado do escritório"],
    },
    "ingestao-processual": {
        "faz": "Cuida da cobertura e da proveniência na entrada dos autos (o que entrou, o que falta, de onde veio).",
        "exemplo": "Um volume digitalizado entraria com a conta de páginas e a origem de cada peça — quando estiver disponível avulsa.",
        "recebe": ["Mapa de cobertura dos autos", "Proveniência dos arquivos"],
    },
    "calculos-juridicos": {
        "faz": "Cálculos jurídicos determinísticos, com premissas explícitas para conferência do advogado.",
        "exemplo": "Atualização de parcelas com as premissas à vista — quando estiver disponível avulsa. O valor da causa ainda não é calculado automaticamente.",
        "recebe": ["Memória de cálculo com premissas"],
    },
}

CSS = """
/* confianca_pos: home, laboratório, catálogo das 28, disponibilidade */
.selo-ficcao{display:inline-flex;align-items:center;gap:.45rem;margin:0 0 1rem;padding:.4rem .85rem;border-radius:999px;border:1px solid rgba(224,192,120,.55);background:rgba(11,26,51,.9);color:var(--gold-s);font:600 .78rem/1.3 var(--sans);letter-spacing:.04em;text-transform:uppercase}
.hero-os .hero-in{display:grid;gap:1.6rem;align-items:center}
@media (min-width:900px){.hero-os .hero-in{grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr)}}
.hero-os .hero-copy h1{font-size:clamp(1.8rem,4vw,3rem);max-width:18ch}
.cta-duo{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.3rem 0 .4rem}
.hero-shot,.shot{display:block;border-radius:16px;border:1px solid rgba(224,192,120,.4);background:rgba(6,16,34,.85);overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.35)}
.hero-shot img,.shot img,.lab-doc img{display:block;width:100%;height:auto}
.shot figcaption,.lab-doc figcaption{margin:0;padding:.65rem .9rem .8rem;color:var(--ink-3);font-size:.82rem;background:rgba(6,16,34,.95)}
.shots{display:grid;gap:1rem;grid-template-columns:1fr}
@media (min-width:800px){.shots{grid-template-columns:1fr 1fr}}
.disp{display:inline-flex;align-items:center;margin:.15rem 0 .6rem;padding:.3rem .75rem;border-radius:999px;border:1px solid rgba(224,192,120,.4);font:600 .78rem/1.3 var(--sans);color:var(--gold-s);background:rgba(15,42,82,.45)}
.disp-nao{color:var(--ink-2);border-color:rgba(122,134,160,.45);background:rgba(6,16,34,.6);font-weight:500}
.apps-grid{display:grid;gap:.8rem;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.apps-grid a{display:flex;flex-direction:column;gap:.35rem;min-height:7.5rem;padding:1rem 1.1rem;border-radius:14px;border:1px solid rgba(224,192,120,.4);background:linear-gradient(135deg,rgba(14,30,60,.92),rgba(6,16,34,.92));color:inherit;text-decoration:none}
.apps-grid a:hover,.apps-grid a:focus-visible{border-color:#E0C078}
.apps-grid h3{margin:0;font-size:1.05rem}
.apps-grid p{margin:0;font-size:.9rem;color:var(--ink-2)}
.apps-grid .abrir{margin-top:auto;font-size:.85rem;font-weight:600;color:var(--gold-l)}
.doc-paper{margin:0;padding:1.2rem 1.3rem;border-radius:14px;border:1px solid rgba(224,192,120,.45);background:rgba(6,16,34,.88);color:var(--head);font:400 .95rem/1.65 var(--serif);white-space:pre-wrap}
.doc-paper .aviso-minuta{color:var(--gold-s);font-family:var(--sans);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;margin:0 0 .8rem}
.check-lab{list-style:none;margin:0;padding:0;display:grid;gap:.4rem}
.check-lab li{display:flex;gap:.6rem;padding:.55rem .7rem;border-radius:10px;border:1px solid rgba(224,192,120,.28);background:rgba(6,16,34,.75)}
.check-lab .ok{color:var(--gold-s)}
.check-lab .falta{color:#E8C4A0}
.lab-docs{display:grid;gap:1rem;grid-template-columns:1fr}
@media (min-width:800px){.lab-docs{grid-template-columns:1.1fr .9fr}}
.frentes-bloco{margin:1.6rem 0 0}
.frentes-bloco h3{margin:0 0 .7rem;font-size:1.15rem}
"""

# Trecho da minuta gerada em 22/11/2026 a partir de documentos 100% sintéticos (saida_teste1).
EXCERPT = """MINUTA PARA REVISÃO DA ADVOGADA — NÃO PROTOCOLAR SEM REVISÃO HUMANA

AO JUÍZO DO JUIZADO ESPECIAL FEDERAL CÍVEL DA SUBSEÇÃO JUDICIÁRIA DE CONTAGEM - MG

Maria Aparecida Ficticia dos Santos [DOC 1], [PENDENTE: Estado civil], [PENDENTE: Profissão], inscrita no CPF sob o nº 123.456.789-09 [DOC 1] (número fictício), residente em Rua das Acácias Fictícias, 123, Bairro Jardim Teste, Contagem - MG, CEP 32000-000 [DOC 2], vem propor a presente

AÇÃO DE CONCESSÃO/RESTABELECIMENTO DE BENEFÍCIO POR INCAPACIDADE COM PEDIDO DE TUTELA DE URGÊNCIA
em face do INSTITUTO NACIONAL DO SEGURO SOCIAL – INSS.

III – DOS FATOS
A parte autora solicitou a concessão do auxílio por incapacidade temporária [DOC 2]. A solicitação foi indeferida por não constatação de incapacidade laborativa pela perícia médica [DOC 4]. O laudo médico, emitido em 05/09/2026, registrou os CID F32.2, M51.1 e M54.5, com início da incapacidade em 15/03/2026, pelo médico Dr. Carlos Exemplo Ficticio, CRM-MG 99999 [DOC 5, 6, 7].

IV – DO DIREITO
O auxílio por incapacidade temporária é devido ao segurado que, cumprida a carência quando exigida, ficar incapacitado para o seu trabalho por mais de 15 dias consecutivos (art. 59 da Lei 8.213/1991; texto conferido no Planalto)."""

# Checklist do mesmo kit (o revisor apontou divergência de OCR no CPF — dado fictício).
CHECK_OK = [
    "Aviso de minuta para revisão na 1ª linha",
    "Documentos: identidade, comprovante de residência, CNIS, decisão do INSS, laudos",
    "Campos: nome, CPF, endereço, cidade/UF, DER, NB, CIDs, data do laudo",
    "Artigos conferidos no texto oficial (17/17)",
    "Toda citação [DOC n] aponta para documento existente",
    "laudos.pdf montado",
]
CHECK_GAP = [
    "Divergência de CPF entre documentos (123.456.789-09 × 123.456.739-09) — o revisor pediu confirmação; é um número fictício",
    "Divergência de cidade/UF (Contagem-MG × Belo Horizonte-MG)",
    "Divergência de data do laudo mais recente e de CRM entre laudos",
    "Protetora Leal: conferir linguagem antes do protocolo",
    "Perguntas à advogada: estado civil, profissão, valor da causa (ainda não calculado automaticamente)",
]

OAB_SIGNUP = [
    (re.compile(r"Crie a conta com o seu número da OAB", re.I),
     "Crie a conta com o seu CPF ou o CNPJ do escritório"),
    (re.compile(r"Crie a conta com (o )?seu número da OAB", re.I),
     "Crie a conta com o seu CPF ou o CNPJ do escritório"),
    (re.compile(r"cadastre-se com (o )?seu número da OAB", re.I),
     "cadastre-se com o seu CPF ou o CNPJ do escritório"),
    (re.compile(r"criar a conta com (o )?(seu |sua )?(número da )?OAB", re.I),
     "criar a conta com o seu CPF ou o CNPJ do escritório"),
    (re.compile(r"informe (o |seu )?número da OAB", re.I),
     "informe o CPF ou o CNPJ"),
    (re.compile(r"número da OAB para (criar|abrir|fazer) (a )?conta", re.I),
     "CPF ou CNPJ para criar a conta"),
    (re.compile(r"com a sua inscrição da OAB", re.I),
     "com o seu CPF ou o CNPJ do escritório"),
    (re.compile(r"use (o |seu )?número da OAB", re.I),
     "use o CPF ou o CNPJ"),
]


def copy_assets() -> None:
    dest = OUT / "img" / "laboratorio"
    dest.mkdir(parents=True, exist_ok=True)
    packed = HERE / "assets_t1932u.tgz.b64"
    if packed.is_file():
        import base64, io, tarfile
        raw = base64.b64decode("".join(packed.read_text().split()))
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            tf.extractall(dest)
        return
    src = None
    for c in (HERE / "assets_t1932u", HERE / "assets"):
        if c.is_dir():
            src = c
            break
    if not src:
        print("[confianca_pos] aviso: pasta de imagens nao encontrada")
        return
    for sp in src.iterdir():
        if sp.suffix.lower() == ".webp":
            shutil.copy2(sp, dest / sp.name)



def donor():
    base = (OUT / "index.html").read_text(encoding="utf-8")
    head, rest = base.split("<main", 1)
    foot = rest.split("</main>", 1)[1]
    body_at = head.find("<body")
    header = head[body_at:]
    head = head[:body_at]
    return head, header, foot


def set_meta(head: str, title: str, desc: str, canonical: str) -> str:
    head = re.sub(r"<title>[^<]*</title>", f"<title>{E(title)}</title>", head, count=1)
    if re.search(r'<meta name="description"', head):
        head = re.sub(
            r'<meta name="description" content="[^"]*"',
            f'<meta name="description" content="{E(desc)}"',
            head, count=1,
        )
    else:
        head = head.replace("</title>", f'</title>\n<meta name="description" content="{E(desc)}">', 1)
    if re.search(r'property="og:title"', head):
        head = re.sub(r'<meta property="og:title" content="[^"]*"', f'<meta property="og:title" content="{E(title)}"', head)
    if re.search(r'property="og:description"', head):
        head = re.sub(r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{E(desc)}"', head)
    if re.search(r'rel="canonical"', head):
        head = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{E(canonical)}"', head)
    else:
        head = head.replace("</title>", f'</title>\n<link rel="canonical" href="{E(canonical)}">', 1)
    return head


def strip_ld(head: str) -> str:
    return re.sub(r'\s*<script type="application/ld\+json">[\s\S]*?</script>', '', head)

def patch_nav(header: str, current: str) -> str:
    # Ensure Laboratório and Combos; keep As Têmis as the 28-app catalog.
    if 'href="/laboratorio/"' not in header:
        header = header.replace(
            '<a href="/seguranca/">Segurança</a>',
            '<a href="/laboratorio/">Laboratório</a><a href="/seguranca/">Segurança</a>',
        )
    def curr(href, label, slug):
        ac = ' aria-current=page' if current.rstrip("/") == slug.rstrip("/") or (slug != "/" and current.startswith(slug)) else ""
        if href == "/" and current not in {"/", ""}:
            ac = ""
        return f'<a href="{href}"{ac}>{label}</a>'
    # rebuild aria-current lightly
    return header


def inject_css(head: str) -> str:
    if "confianca_pos:" in head:
        return head
    tag = f"<style>\n{CSS}\n</style>\n"
    if "</head>" in head:
        return head.replace("</head>", tag + "</head>", 1)
    return head + tag


def pagina(rel: str, title: str, desc: str, main: str, canonical: str | None = None, current: str | None = None) -> None:
    head, header, foot = donor()
    canon = canonical or f"{SITE}/{rel}"
    if not canon.endswith("/") and not canon.endswith(".html") and rel.endswith("/"):
        canon = canon + "/"
    head = inject_css(set_meta(head, title, desc, canon))
    if rel not in ("", "/"):
        head = strip_ld(head)
    header = patch_nav(header, current or ("/" + rel))
    # drop statue from new page headers if present in main we control
    html = head + header + main + foot
    if rel in ("", "/"):
        dest = OUT / "index.html"
    elif rel.endswith("/"):
        dest = (OUT / rel) / "index.html"
    else:
        dest = OUT / rel
        if dest.suffix.lower() not in {".html", ".htm"}:
            dest = dest / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def crumbs(*pairs):
    parts = ['<nav class="crumbs" aria-label="Você está em">']
    for i, (label, href) in enumerate(pairs):
        if i:
            parts.append('<span aria-hidden="true">›</span>')
        if href:
            parts.append(f'<a href="{E(href)}">{E(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{E(label)}</span>')
    parts.append("</nav>")
    return "".join(parts)


def selo_ficcao():
    return '<p class="selo-ficcao">Exemplo com dados fictícios</p>'


def rewrite_home() -> None:
    shots = f'''
<figure class="hero-shot">
<img src="/img/laboratorio/ui_kit.webp" width="1280" height="800" alt="Tela da plataforma Têmis no kit da petição inicial, com documentos sintéticos classificados" decoding="async" fetchpriority="high">
</figure>'''
    main = f'''<main id="main">
<section class="hero hero-os" id="topo"><div class="wrap hero-in">
<div class="hero-copy">
<p class="eyebrow">Têmis OS · Plataforma de inteligência jurídica</p>
<h1>Seu trabalho jurídico. Uma rede de inteligências especializadas.</h1>
<p class="lead">Escolha uma tarefa, conheça as aplicações da Têmis e veja como análise documental, pesquisa e revisão podem atuar em conjunto, com supervisão profissional. Os preços aparecem depois do login.</p>
<div class="cta-duo">
<a class="btn" href="#por-tarefa">Por tarefa</a>
<a class="btn btn-ghost" href="/temis/">Conheça a Têmis</a>
</div>
<p class="fine">Petições, recursos, laudos, provas e análises · 28 aplicações no catálogo, contratação avulsa ou por combo · um teste grátis por CPF ou CNPJ.</p>
</div>
{shots}
</div></section>

<section class="sec" id="demonstracao"><div class="wrap">
<div class="sec-head">
<p class="eyebrow">Demonstração</p>
<h2>Veja a plataforma, não só a promessa</h2>
<p class="lead">Capturas e peças geradas pela própria Têmis em 22/11/2026, a partir de um caso 100% sintético (auxílio por incapacidade contra o INSS). Não é um processo real e não está aberto um acesso público à plataforma.</p>
{selo_ficcao()}
</div>
<div class="shots">
<figure class="shot"><img src="/img/laboratorio/ui_kit.webp" alt="Painel do kit da inicial com oito documentos sintéticos classificados e o agente aguardando a advogada" loading="lazy" decoding="async"><figcaption>Kit da petição inicial na área logada. Documentos fictícios, OCR local, minuta para revisão.</figcaption></figure>
<figure class="shot"><img src="/img/laboratorio/ui_mente.webp" alt="Chat da Têmis listando laudos sintéticos, CIDs e a conferência do art. 42 da Lei 8.213/91 no Planalto" loading="lazy" decoding="async"><figcaption>Chat da Têmis: listou os laudos do caso fictício e conferiu o art. 42 da Lei 8.213/1991 no texto oficial do Planalto.</figcaption></figure>
</div>
<p><a class="more" href="/laboratorio/">Abrir o laboratório com a minuta, o laudos.pdf e o checklist ›</a></p>
</div></section>

<section class="sec" id="por-tarefa"><div class="wrap">
<div class="sec-head">
<p class="eyebrow">Por tarefa</p>
<h2>O que você precisa fazer</h2>
<p class="lead">Os pacotes por tarefa não revelam quais aplicações da Têmis atuam por trás. Você pede o trabalho; a Têmis organiza a execução. Preços após o login.</p>
</div>
<div class="apps-grid">
<a href="/tarefas/peticao-inicial/"><h3>Petição inicial</h3><p>Você envia os documentos do caso e recebe a minuta com fatos, fundamentos, pedidos e anexos organizados.</p><span class="disp">Disponível para contratação</span><span class="abrir">Abrir ›</span></a>
<a href="/tarefas/analise-processo/"><h3>Análise dos autos</h3><p>Pergunte no chat sobre o caso. A resposta cita o documento e o trecho, e a conferência de lei usa o texto oficial.</p><span class="disp">Disponível para contratação</span><span class="abrir">Abrir ›</span></a>
<a href="/tarefas/"><h3>Outras tarefas</h3><p>Contestação, recurso, parecer e análise de laudo entram no catálogo; a contratação avulsa delas ainda não está aberta.</p><span class="disp disp-nao">Catálogo completo</span><span class="abrir">Ver tarefas ›</span></a>
</div>
</div></section>

<section class="sec" id="aplicativos"><div class="wrap">
<div class="sec-head">
<p class="eyebrow">Conheça a Têmis</p>
<h2>28 aplicações. Contrate as que quiser.</h2>
<p class="lead">Monte o seu conjunto à la carte, escolha um combo pronto ou suba de plano. Cada aplicação tem a sua página e o seu preço — este último só depois do login. Quem fala é sempre a Têmis; as aplicações são especialidades dela, não bots separados.</p>
</div>
<div class="cta-duo">
<a class="btn" href="/temis/">Ver as 28 aplicações</a>
<a class="btn btn-ghost" href="/montar/">Montar o meu conjunto</a>
<a class="btn btn-ghost" href="/combos/">Combos prontos</a>
</div>
<p class="fine">As aplicações ainda não abertas para contratação avulsa permanecem no catálogo, sem convite para experimentá-las.</p>
</div></section>

<section class="sec" id="compromissos"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Compromissos</p><h2>Revisão humana, fontes e sigilo</h2></div>
<div class="minis">
<article class="mini"><h3>Revisão humana obrigatória</h3><p>Toda peça sai como minuta para revisão. A Têmis não protocola, não envia e não acessa tribunal. Quem decide e assina é o profissional habilitado.</p></article>
<article class="mini"><h3>Fontes à vista</h3><p>A afirmação relevante aponta para o documento, a lei (texto oficial do Planalto, quando conferida) ou o precedente. O que não tem lastro aparece para conferência.</p></article>
<article class="mini"><h3>Sem promessa de resultado</h3><p>Sem probabilidade de vitória e sem captação. Respeito ao Provimento 205/2021 da OAB e às regras equivalentes de cada jurisdição.</p></article>
<article class="mini"><h3>Documentos na nossa plataforma</h3><p>O site aberto não recebe autos. Depois do login, os documentos vão para a plataforma própria, na VPS4, com OCR e modelo locais. Detalhes em Segurança e sigilo.</p></article>
<article class="mini"><h3>Isolamento por escritório</h3><p>Cada escritório tem o seu espaço. Em teste com dois escritórios sintéticos (22/11/2026), um não enxergou caso, documento, memória nem tarefa do outro.</p></article>
<article class="mini"><h3>Estado honesto</h3><p>O catálogo lista as 28 aplicações. 25 aplicações podem ser contratadas avulsas depois do login (16 com conector MCP testado e 9 pela página do agente). Fontes do Direito (legado) entra em todos os planos e não é vendida à parte.</p></article>
</div>
<p><a class="more" href="/seguranca/">Como os documentos e a IA local funcionam ›</a></p>
</div></section>

<section class="sec" id="para-quem"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Para quem é</p><h2>Feita para quem responde pelo resultado</h2></div>
<div class="minis">
<article class="mini"><h3>Advocacia autônoma</h3><p>Para quem advoga sozinho e precisa render como uma equipe, sem abrir mão da revisão pessoal de cada peça.</p><p><a class="more" href="/para-quem-e/advocacia-autonoma/">Ver como ajuda ›</a></p></article>
<article class="mini"><h3>Escritórios</h3><p>Para sociedades que querem padronizar a qualidade, distribuir o trabalho e preservar o conhecimento da casa.</p><p><a class="more" href="/para-quem-e/escritorios/">Ver como ajuda ›</a></p></article>
<article class="mini"><h3>Departamentos jurídicos</h3><p>Para jurídicos internos que precisam responder ao negócio com rapidez, controle de risco e rastreabilidade.</p><p><a class="more" href="/para-quem-e/departamentos-juridicos/">Ver como ajuda ›</a></p></article>
</div>
</div></section>

<section class="sec" id="teste"><div class="wrap split">
<div class="sec-head"><p class="eyebrow">Teste grátis</p><h2>Um teste por CPF ou CNPJ, sem cartão</h2></div>
<div class="prose">
<p>Crie a conta com e-mail, CPF ou CNPJ e uma senha, e use na hora. O nome é bem-vindo, mas não precisa ser o primeiro passo. Não há lista de espera. Os preços dos planos, das aplicações e dos combos aparecem depois do login.</p>
<div class="cta-duo"><a class="btn" href="/conta/cadastro">Começar o teste grátis</a><a class="btn btn-ghost" href="/conta/entrar">Já tenho conta: entrar</a></div>
</div></div></section>
</main>'''
    pagina(
        "",
        "TÊMIS OS · Plataforma de inteligência jurídica",
        "Plataforma de inteligência jurídica: contrate por tarefa, por aplicativo ou em combos. Veja um caso fictício gerado pela Têmis. Preços após o login. Teste grátis por CPF ou CNPJ.",
        main,
        canonical=f"{SITE}/",
        current="/",
    )
    # donor() used index.html — we just overwrote it, fine.


def rewrite_seguranca() -> None:
    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Segurança e sigilo",None))}
<p class="eyebrow">Segurança e sigilo</p>
<h1>O sigilo do seu cliente <em>vem antes de tudo.</em></h1>
<p class="lead">A Têmis foi desenhada para o trabalho jurídico, em que a confidencialidade é dever profissional. Aqui está o caminho real dos documentos — sem atalho de marketing.</p>
</div></div></section>
<section class="sec"><div class="wrap prose">
<h2>O site aberto e a plataforma</h2>
<p>O site público (estas páginas em agentetemis.com) não recebe autos nem arquivos de clientes. Formulários abertos (sugestões, afiliados) servem para mensagem e cadastro comercial: não envie documentos de processo nem dados sensíveis de terceiros por eles.</p>
<p>Depois que você cria a conta e entra, os documentos do caso vão para a <strong>plataforma própria da Têmis, na VPS4</strong>. Não transitam por este site estático. A plataforma não é um produto público na internet aberta: o acesso à área logada passa pelo domínio, e o serviço roda na infraestrutura da casa, isolado por escritório.</p>
<h2>O que acontece com o arquivo</h2>
<ul>
<li><strong>Isolamento por escritório.</strong> Cada organização tem o seu espaço (casos, documentos, memória, estilo, tarefas e arquivos). Em 22/11/2026, um teste com dois escritórios sintéticos passou em 27 de 27 checagens: um não abriu caso, documento, kit, tarefa, busca nem memória do outro.</li>
<li><strong>OCR local.</strong> A leitura de páginas digitalizadas roda na própria plataforma (Tesseract), página a página, sem enviar a imagem a um serviço externo. Esse caminho foi exercitado no teste do kit com documentos sintéticos.</li>
<li><strong>Modelo local.</strong> A análise usa o modelo local no notebook Nitro (<code>qwen3:8b</code>). Se o Nitro estiver fora, a plataforma cai para o mesmo modelo na VPS4. Esse caminho foi testado com o Nitro no mesmo dia. Não usamos o documento do cliente para treinar modelos.</li>
<li><strong>Cadeado de privacidade.</strong> Ferramentas externas só podem receber texto genérico. Uma guarda bloqueia CPF, número de benefício, CID, datas, fatos extraídos e qualquer trecho relevante dos documentos do caso. A guarda foi testada. Pontes com outros agentes e o cérebro externo (CEUCI) estão desligados ou ainda não verificados nesta rodada: não entram no caminho dos autos.</li>
<li><strong>Trilha de conferência.</strong> A plataforma registra os passos de cada tarefa (ferramenta usada, motivo, status e resumo), para o escritório conferir o que foi feito. Não afirmamos que essa trilha seja imutável no sentido de um arquivo de auditoria certificado.</li>
</ul>
<h2>O que a Têmis não faz</h2>
<p>Não protocola, não assina e não acessa tribunal. Toda peça sai como minuta para revisão do profissional habilitado. Não prometemos resultado. Não vendemos nem compartilhamos documento de cliente para treinar modelo de terceiros. A base compartilhada entre escritórios, quando existe, guarda só contagens anônimas de um vocabulário fechado — sem texto, nome, número, data ou identificador.</p>
<h2>LGPD e os seus direitos</h2>
<p>Coleta mínima, finalidade declarada e canal direto: peça acesso, correção ou exclusão pelo e-mail <a href="mailto:contato.pronaos@gmail.com">contato.pronaos@gmail.com</a>. O teste grátis é um por CPF ou CNPJ. Os preços só aparecem depois do login.</p>
</div></section></main>'''
    pagina(
        "seguranca/",
        "Segurança e sigilo · Têmis OS",
        "Documentos do caso vão para a plataforma própria na VPS4, com isolamento por escritório, OCR e modelo locais e um cadeado que impede dado de cliente em ferramenta externa.",
        main,
    )


def rewrite_privacidade() -> None:
    path = OUT / "privacidade" / "index.html"
    if not path.is_file():
        return
    s = path.read_text(encoding="utf-8")
    old = '''<h3>Pedido de amostra</h3><p>O teste grátis é liberado ao criar a conta, com CPF ou CNPJ. Os dados da conta servem para identificar a amostra (uma por pessoa) e o escritório. Não envie documentos de clientes nem dados sensíveis de terceiros no teste.</p>'''
    new = '''<h3>Teste grátis e documentos do caso</h3><p>O teste grátis é liberado ao criar a conta, com e-mail, CPF ou CNPJ e senha (um por CPF ou CNPJ). Os dados da conta identificam a pessoa ou o escritório e o direito ao teste. O site aberto não recebe autos. Depois do login, os documentos que você enviar na plataforma seguem o caminho descrito em <a href="/seguranca/">Segurança e sigilo</a>: infraestrutura própria, isolamento por escritório, OCR e modelo locais. No formulário de sugestões e em mensagens abertas, não envie documentos de processo nem dados sensíveis de terceiros.</p>'''
    if old in s:
        s = s.replace(old, new)
    else:
        s = s.replace(
            "Não envie documentos de clientes nem dados sensíveis de terceiros no teste.",
            "O site aberto não recebe autos; depois do login, os documentos do caso seguem o caminho de Segurança e sigilo. Não envie autos pelo formulário de sugestões.",
        )
    # less statue on this legal page? keep for now or strip large statue
    s = re.sub(
        r'<div class="statue-slot">[\s\S]*?</div></div></div></section>',
        '</div></div></section>',
        s,
        count=1,
    )
    path.write_text(s, encoding="utf-8")


def disp(t) -> str:
    if not isinstance(t, dict):
        if t:
            return '<span class="disp">Disponível para contratação avulsa · preço após o login</span>'
        return '<span class="disp disp-nao">Ainda não disponível para contratação avulsa</span>'
    if eh_incluido(t):
        return '<span class="disp">Incluída em todos os planos · a partir do teste grátis</span>'
    if eh_contratavel(t):
        extra = " · página do agente Têmis" if t.get("superficie") == "agente" or (t.get("contratavel") and not t.get("testado")) else ""
        return f'<span class="disp">Disponível para contratação avulsa{extra} · preço após o login</span>'
    return '<span class="disp disp-nao">Ainda não disponível para contratação avulsa</span>'


def app_copy(t: dict) -> dict:
    if t.get("testado"):
        return t
    extra = SOON_COPY.get(t["slug"], {})
    out = dict(t)
    out.setdefault("faz", extra.get("faz") or "Especialidade prevista no mapa da Têmis.")
    out.setdefault("exemplo", extra.get("exemplo") or "Quando a contratação avulsa desta aplicação estiver aberta, o preço aparecerá depois do login.")
    out.setdefault("recebe", extra.get("recebe") or ["Descrição da especialidade"])
    return out


def rewrite_catalog() -> None:
    by = {}
    for t in TEMIS:
        by.setdefault(t["frente"], []).append(t)
    blocos = []
    for fr in NAV["frentes"]:
        items = by.get(fr["slug"]) or []
        if not items:
            continue
        cards = []
        for t in items:
            tt = app_copy(t)
            cards.append(
                f'<a href="/temis/{E(t["slug"])}/"><h3>{E(t["nome"])}</h3>'
                f'<p>{E(tt["faz"][:180])}</p>{disp(t)}<span class="abrir">Abrir ›</span></a>'
            )
        blocos.append(
            f'<div class="frentes-bloco" id="{E(fr["slug"])}">'
            f'<h3>{E(fr["nome"])}</h3><div class="apps-grid">{"".join(cards)}</div></div>'
        )
    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("As Têmis",None))}
<p class="eyebrow">Conheça a Têmis</p>
<h1>28 aplicações, <em>uma só Têmis.</em></h1>
<p class="lead">Contrate à la carte as aplicações que quiser, escolha um combo pronto ou suba de plano. Cada uma tem a sua página e a sua explicação. O preço aparece depois do login. Pacotes por tarefa não dizem quais aplicações atuam por trás.</p>
<div class="cta-duo">
<a class="btn" href="/montar/">Montar o meu conjunto</a>
<a class="btn btn-ghost" href="/combos/">Combos prontos</a>
<a class="btn btn-ghost" href="/tarefas/">Por tarefa</a>
</div>
</div></div></section>
<section class="sec"><div class="wrap">{"".join(blocos)}</div></section>
</main>'''
    pagina(
        "temis/",
        "As 28 aplicações da Têmis · Têmis OS",
        "Catálogo das 28 aplicações da Têmis para contratação avulsa, combos ou planos. Explicação em cada página; preços após o login.",
        main,
    )
    # individual pages
    n = len(TEMIS)
    for i, t in enumerate(TEMIS):
        tt = app_copy(t)
        ok = eh_contratavel(t)
        fr = FRENTES.get(t["frente"], {"nome": t["frente"], "slug": t["frente"]})
        prev = TEMIS[i - 1] if i else None
        nxt = TEMIS[i + 1] if i + 1 < n else None
        viz = '<nav class="vizinhos" aria-label="Navegar entre as aplicações">'
        viz += f'<a href="/temis/">‹ Catálogo</a>'
        if nxt:
            viz += f'<a class="prox" href="/temis/{E(nxt["slug"])}/">{E(nxt["nome"])} ›</a>'
        viz += "</nav>"
        recebe = "".join(f"<li>{E(x)}</li>" for x in (tt.get("recebe") or []))
        if ok:
            cta = (
                '<div class="cta-duo"><a class="btn" href="/conta/entrar?volta=/conta/planos">Entrar para ver o preço</a>'
                '<a class="btn btn-ghost" href="/conta/cadastro">Começar o teste grátis</a>'
                '<a class="btn btn-ghost" href="/montar/">Montar o conjunto</a></div>'
            )
            honesto = (
                '<p class="fine">Esta aplicação é entregue pela página do agente Têmis. '
                "O conector MCP dedicado ainda não está no ar.</p>"
                if (t.get("superficie") == "agente" or (t.get("contratavel") and not t.get("testado")))
                else '<p class="fine">Tudo sai como rascunho para revisão do advogado responsável. Quem fala é sempre a Têmis.</p>'
            )
            como = (
                "<div><h2>Como contratar</h2><p>Depois do login você vê o preço mensal desta aplicação, "
                "pode somá-la a outras (monte o seu conjunto) ou escolher um combo pronto. "
                "Nos pacotes por tarefa, a Têmis não revela quais aplicações atuaram.</p>"
                + honesto + "</div>"
            )
        elif eh_incluido(t):
            cta = (
                '<p class="fine">Esta aplicação (adaptador legado) entra em todos os planos, a partir do teste grátis. '
                "A aplicação vigente de consulta a fontes é Fontes do Direito. Não é vendida à parte.</p>"
                '<div class="cta-duo"><a class="btn" href="/conta/cadastro">Começar o teste grátis</a>'
                '<a class="btn btn-ghost" href="/temis/fontes-do-direito-v3/">Ver Fontes do Direito</a></div>'
            )
            como = (
                "<div><h2>Como entra no seu plano</h2><p>Não há preço avulso. Ela acompanha o teste grátis e os planos pagos, "
                "como adaptador legado. A consulta oficial de fontes usa Fontes do Direito.</p>"
                '<p class="fine">Tudo sai como rascunho para revisão do advogado responsável.</p></div>'
            )
        else:
            cta = (
                '<p class="fine">Esta aplicação ainda não está aberta para contratação avulsa. '
                "Ela permanece no catálogo para você conhecer o mapa da Têmis. "
                "Quando a contratação for liberada, o preço aparecerá depois do login.</p>"
                '<div class="cta-duo"><a class="btn btn-ghost" href="/temis/">Voltar ao catálogo</a>'
                '<a class="btn btn-ghost" href="/conta/cadastro">Teste grátis das aplicações já disponíveis</a></div>'
            )
            como = (
                "<div><h2>Quando estiver disponível</h2><p>Esta especialidade faz parte do mapa da Têmis "
                "e ainda não pode ser contratada avulsa. Não há prazo anunciado nesta página.</p>"
                '<p class="fine">Tudo o que a Têmis já entrega sai como rascunho para revisão do advogado responsável.</p></div>'
            )
        main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("As Têmis","/temis/"),(fr["nome"], f"/temis/#{fr['slug']}"),(t["nome"], None))}
<p class="eyebrow">{E(fr["nome"])}</p>
<h1>{E(t["nome"])}</h1>
<p class="lead">{E(tt["faz"])}</p>
{disp(t)}
{cta}
</div></div></section>
<section class="sec"><div class="wrap"><div class="ficha">
<div><h2>Exemplo</h2><p>{E(tt["exemplo"])}</p><p class="fine">Exemplo ilustrativo, com dados fictícios quando houver caso.</p></div>
<div><h2>O que você recebe</h2><ul>{recebe}</ul></div>
{como}
</div>{viz}</div></section></main>'''
        pagina(
            f"temis/{t['slug']}/",
            f"{t['nome']} · aplicação da Têmis",
            f"{t['nome']}: {tt['faz']} Preço após o login. Teste grátis por CPF ou CNPJ nas aplicações já disponíveis.",
            main,
        )


def rewrite_laboratorio() -> None:
    checks = "".join(f'<li><span class="ok" aria-hidden="true">✓</span><span>{E(x)}</span></li>' for x in CHECK_OK)
    gaps = "".join(f'<li><span class="falta" aria-hidden="true">!</span><span>{E(x)}</span></li>' for x in CHECK_GAP)
    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Laboratório",None))}
<p class="eyebrow">Laboratório</p>
<h1>Um caso fictício, <em>peças de verdade.</em></h1>
<p class="lead">Em 22/11/2026 a Têmis rodou, sem intervenção, um kit de petição inicial com oito documentos sintéticos. Abaixo estão capturas da plataforma e recortes das peças que ela mesma montou. Isto não é um acesso aberto à plataforma e não é um processo real.</p>
{selo_ficcao()}
</div></div></section>
<section class="sec"><div class="wrap">
<div class="sec-head"><h2>O caso</h2>
<p class="lead">Pedido de benefício por incapacidade contra o INSS, em nome de Maria Aparecida Ficticia dos Santos, com carta de indeferimento, CNIS e laudos fictícios. Tempo até o estado «aguardando a advogada»: cerca de 104 segundos no teste certificado. 17 artigos conferidos no texto oficial do Planalto.</p>
</div>
<div class="shots">
<figure class="shot"><img src="/img/laboratorio/ui_upload.webp" alt="Tela de envio de documentos na plataforma, com OCR local e arquivos sintéticos recebidos" loading="lazy" decoding="async"><figcaption>Envio na plataforma: fotos e PDFs entram em partes, com OCR local. Nenhum arquivo deste exemplo é de cliente real.</figcaption></figure>
<figure class="shot"><img src="/img/laboratorio/ui_kit.webp" alt="Documentos sintéticos classificados no kit da inicial" loading="lazy" decoding="async"><figcaption>O kit classificou os oito arquivos e aguardou a revisão da advogada. Toda peça é minuta — a Têmis não protocola.</figcaption></figure>
<figure class="shot"><img src="/img/laboratorio/ui_mente.webp" alt="Chat da Têmis conferindo laudos sintéticos e o art. 42 da Lei 8.213/91" loading="lazy" decoding="async"><figcaption>No chat, a Têmis listou os laudos (datas, CID, médicos fictícios) e conferiu o art. 42 da Lei 8.213/1991 no Planalto.</figcaption></figure>
</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head"><h2>As peças que o kit entregou</h2>
<p class="lead">Recortes da minuta e do laudos.pdf gerados no mesmo teste, com o checklist que a própria Têmis preencheu — inclusive as divergências que ela pediu para a advogada confirmar.</p>
{selo_ficcao()}
</div>
<div class="lab-docs">
<div>
<p class="eyebrow">Minuta da petição (trecho)</p>
<div class="doc-paper"><p class="aviso-minuta">Minuta para revisão · dados fictícios</p>{E(EXCERPT)}</div>
<figure class="shot" style="margin-top:1rem"><img src="/img/laboratorio/peticao-1.webp" alt="Primeira página da minuta da petição inicial gerada no caso fictício" loading="lazy" decoding="async"><figcaption>Primeira página da minuta em PDF, gerada pela plataforma.</figcaption></figure>
</div>
<div>
<p class="eyebrow">laudos.pdf e checklist</p>
<figure class="shot"><img src="/img/laboratorio/laudos-1.webp" alt="Primeira página do laudos.pdf montado no caso fictício" loading="lazy" decoding="async"><figcaption>laudos.pdf montado pela Têmis a partir das imagens sintéticas do teste.</figcaption></figure>
<h3 style="margin-top:1.2rem">Checklist do kit</h3>
<ul class="check-lab">{checks}{gaps}</ul>
<p class="fine">O revisor local apontou, entre outras coisas, a divergência de CPF causada pelo OCR — e deixou a confirmação para a advogada. Foi assim no teste, com números fictícios.</p>
</div>
</div>
<p class="fine" style="margin-top:1.2rem">Fonte: certificação de 22/11/2026 com dados 100% sintéticos, descrita em TEMIS_AGENTE.md. O valor da causa ainda não é calculado automaticamente. O modelo local às vezes erra interpretação; por isso a peça é montada com regras e sai sempre como minuta.</p>
<div class="cta-duo">
<a class="btn" href="/conta/cadastro">Começar o teste grátis</a>
<a class="btn btn-ghost" href="/tarefas/peticao-inicial/">Tarefa: petição inicial</a>
</div>
</div></section></main>'''
    pagina(
        "laboratorio/",
        "Laboratório · caso fictício gerado pela Têmis",
        "Laboratório público da Têmis: minuta, laudos.pdf e checklist gerados pela plataforma a partir de um caso 100% sintético. Exemplo com dados fictícios.",
        main,
    )


def rewrite_montar_combos_tarefas() -> None:
    # montar
    apps = "".join(
        f'<li><a href="/temis/{E(t["slug"])}/">{E(t["nome"])}</a> — '
        + ("incluída em todos os planos; não é vendida à parte." if eh_incluido(t)
           else "disponível para contratação avulsa; preço após o login." if eh_contratavel(t)
           else "ainda não disponível para contratação avulsa.")
        + "</li>"
        for t in TEMIS
    )
    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Montar o conjunto",None))}
<p class="eyebrow">Contratação avulsa</p>
<h1>Monte o seu conjunto de aplicações.</h1>
<p class="lead">Escolha, à la carte, quais das 28 aplicações da Têmis você quer. Depois do login você vê o preço mensal de cada uma e fecha o conjunto — ou prefere um combo pronto. Os pacotes por tarefa continuam disponíveis à parte e não revelam quais aplicações atuaram.</p>
<div class="cta-duo">
<a class="btn" href="/conta/entrar?volta=/conta/planos">Entrar para ver os preços</a>
<a class="btn btn-ghost" href="/combos/">Ver combos prontos</a>
<a class="btn btn-ghost" href="/temis/">Catálogo das 28</a>
</div>
</div></div></section>
<section class="sec"><div class="wrap prose">
<h2>As 28 aplicações</h2>
<ul>{apps}</ul>
<p>A soma, o desconto de combo e a cobrança são feitos na área logada. Nada disso é publicado nesta página.</p>
</div></section></main>'''
    pagina("montar/", "Monte o seu conjunto de aplicações · Têmis OS",
           "Contratação à la carte das aplicações da Têmis: escolha quais quer usar. Preços mensais após o login. Combos prontos também disponíveis.", main)

    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Combos",None))}
<p class="eyebrow">Combos prontos</p>
<h1>Pacotes prontos, <em>quando você não quer montar peça por peça.</em></h1>
<p class="lead">Além da contratação avulsa de cada aplicação e dos planos, você pode comprar um combo de tarefas. Os valores e o desconto em relação à compra avulsa aparecem depois do login.</p>
</div></div></section>
<section class="sec"><div class="wrap"><div class="ficha">
<div><h2>Combo Postulatória</h2><p>Para quem vai ajuizar no mês. Reúne petições iniciais e análises dos autos.</p><p class="fine">Exemplo de uso: iniciais previdenciárias com análise de cada caso. Preço após o login.</p></div>
<div><h2>Combo Defesa</h2><p>Para quem defende réus. Quando a contestação e a análise de laudo estiverem abertas para contratação, este combo as agrupa.</p><p class="fine">A contestação e a análise de laudo ainda não estão abertas avulsas; o combo acompanha essa disponibilidade.</p></div>
<div><h2>Combo Recursal</h2><p>Para quem recorre de sentenças. Agrupa recursos e análises dos autos.</p><p class="fine">O recurso ainda não está aberto para contratação avulsa; a análise dos autos sim. Preço do combo após o login, quando disponível.</p></div>
</div>
<div class="cta-duo" style="margin-top:1.2rem">
<a class="btn" href="/conta/entrar?volta=/conta/planos">Entrar para ver os preços</a>
<a class="btn btn-ghost" href="/montar/">Prefiro montar o conjunto</a>
</div>
</div></section></main>'''
    pagina("combos/", "Combos prontos da Têmis · Têmis OS",
           "Combos prontos da Têmis (postulatória, defesa, recursal). Valores após o login. Também é possível montar o conjunto à la carte.", main)

    cards = []
    for t in TAREFAS:
        ok = bool(t.get("testado"))
        faz = t.get("faz") or "Tarefa prevista no catálogo da Têmis."
        if t["slug"] == "analise-processo":
            faz = "Envie os documentos do caso e pergunte no chat. A Têmis cita o documento e o trecho de cada afirmação, e confere a lei no texto oficial quando essa conferência é pedida. O tempo depende do volume e do modelo local — não prometemos resposta em segundos."
        href = f'/tarefas/{t["slug"]}/'
        cards.append(
            f'<a href="{href}"><h3>{E(t["nome"])}</h3><p>{E(faz[:220])}</p>{disp(ok)}<span class="abrir">Abrir ›</span></a>'
        )
    main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Por tarefa",None))}
<p class="eyebrow">Por tarefa</p>
<h1>Peça o trabalho, <em>não o organograma.</em></h1>
<p class="lead">Os pacotes por tarefa não revelam quais aplicações da Têmis atuam por trás. Você descreve o que precisa; a execução fica com a plataforma. Preços após o login.</p>
</div></div></section>
<section class="sec"><div class="wrap"><div class="apps-grid">{"".join(cards)}</div></div></section></main>'''
    pagina("tarefas/", "Tarefas da Têmis · petição, análise e outras",
           "Contrate a Têmis por tarefa: petição inicial, análise dos autos e demais trabalhos do catálogo. Preços após o login.", main)

    # untested task pages (replace stubs)
    for t in TAREFAS:
        if t.get("testado"):
            # soften "em segundos" on existing page
            continue
        faz = t.get("faz") or "Esta tarefa faz parte do mapa da Têmis, mas a contratação avulsa ainda não está aberta."
        main = f'''<main id="main"><section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">
{crumbs(("Início","/"),("Por tarefa","/tarefas/"),(t["nome"], None))}
<p class="eyebrow">Por tarefa</p>
<h1>{E(t["nome"])}</h1>
<p class="lead">{E(faz)}</p>
{disp(False)}
<p class="fine">Quando a contratação desta tarefa for liberada, o preço aparecerá depois do login. Enquanto isso, a petição inicial e a análise dos autos já podem ser contratadas.</p>
<div class="cta-duo"><a class="btn btn-ghost" href="/tarefas/">Outras tarefas</a><a class="btn btn-ghost" href="/conta/cadastro">Teste grátis</a></div>
</div></div></section></main>'''
        pagina(f"tarefas/{t['slug']}/", f"{t['nome']} · tarefa da Têmis",
               f"{t['nome']}: tarefa do catálogo da Têmis. A contratação avulsa ainda não está aberta. Preços, quando houver, após o login.", main)


def patch_existing_claims() -> None:
    """Soften leftover overclaims; never invent 'em preparação' / 'disponível em breve'."""
    repls = [
        (r"18 Têmis em funcionamento", "28 aplicações no catálogo"),
        (r"\d+ Têmis em funcionamento nesta frente", "aplicações desta frente"),
        (r"\d+ Têmis em funcionamento, organizadas em \d+ frentes", "28 aplicações, organizadas em 7 frentes"),
        (r"\d+ Têmis em funcionamento em \d+ frentes", "28 aplicações em 7 frentes"),
        (r"Em funcionamento · testada", "Disponível para contratação avulsa"),
        (r"Em funcionamento · testada", "Disponível para contratação avulsa"),
        (r"trilha imutável", "trilha de auditoria"),
        (r"Documentos de clientes em infraestrutura própria, lidos só por IA local, nunca usados para treinar modelos\.",
         "Depois do login, documentos do caso vão para a plataforma própria (VPS4), com OCR e modelo locais; não são usados para treinar modelos."),
        (r"lidos só por IA local, nunca usados para treinar modelos",
         "lidos na plataforma própria com modelo local; não usados para treinar modelos"),
        (r"O site não recebe documentos de clientes\. Envie apenas o que for necessário para a amostra, sem dados sensíveis de terceiros\.",
         "O site aberto não recebe autos. Depois do login, os documentos do caso vão para a plataforma própria, como está em Segurança e sigilo."),
        (r"Não envie documentos de clientes nem dados sensíveis de terceiros\.",
         "Não envie autos nem dados de processo pelos formulários abertos deste site."),
        (r"A Têmis responde em segundos,",
         "A Têmis responde no chat,"),
        (r"responde em segundos", "responde no chat"),
        (r"Só aparece no site o que passou em teste de funcionamento\. Nada é apresentado como conectado sem estar\.",
         "O catálogo lista as 28 aplicações. Só convidamos a contratar o que já está aberto; o restante permanece visível, ainda não disponível avulso."),
        (r"Incluída a partir do plano <b>[^<]+</b>\. <a href=\"/planos/\">Ver o que cada plano inclui ›</a>",
         'Também entra em alguns planos; você pode contratar só esta aplicação. <a href="/montar/">Montar o conjunto</a> ou <a href="/planos/">ver os planos</a> — preços após o login.'),
    ]
    for p in OUT.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        orig = s
        for a, b in repls:
            s = re.sub(a, b, s)
        for rx, b in OAB_SIGNUP:
            s = rx.sub(b, s)
        # forbidden public wording
        s = re.sub(r"Em preparação", "", s, flags=re.I)
        s = re.sub(r"disponível em breve", "ainda não disponível para contratação avulsa", s, flags=re.I)
        if s != orig:
            p.write_text(s, encoding="utf-8")


def patch_planos() -> None:
    path = OUT / "planos" / "index.html"
    if not path.is_file():
        return
    s = path.read_text(encoding="utf-8")
    extra = '''<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Além dos planos</p><h2>Por aplicativo, por tarefa ou por combo</h2></div>
<div class="ficha">
<div><h2>À la carte</h2><p>Escolha quais das 28 aplicações quer contratar. Cada uma tem a sua página. O preço mensal aparece depois do login.</p><p><a class="more" href="/montar/">Montar o conjunto ›</a></p></div>
<div><h2>Por tarefa</h2><p>Peça o trabalho (petição inicial, análise dos autos e as que forem sendo abertas). O pacote não revela quais aplicações atuaram.</p><p><a class="more" href="/tarefas/">Ver tarefas ›</a></p></div>
<div><h2>Combos prontos</h2><p>Pacotes prontos de tarefas, quando você não quer montar item a item. Valores depois do login.</p><p><a class="more" href="/combos/">Ver combos ›</a></p></div>
</div></div></section>'''
    if "Montar o conjunto" not in s:
        s = s.replace("</main>", extra + "</main>")
    # drop large statue on planos if present
    s = re.sub(r'<div class="statue-slot">[\s\S]*?</div></div></div></section>', '</div></div></section>', s, count=1)
    path.write_text(s, encoding="utf-8")


def patch_tarefas_testadas() -> None:
    for slug, lead in {
        "analise-processo": "Envie os documentos do caso e pergunte no chat. A Têmis cita o documento e o trecho de cada afirmação, e confere a lei no texto oficial quando essa conferência é pedida. O tempo depende do volume e do modelo local — não prometemos resposta em segundos.",
        "peticao-inicial": "Você descreve o caso e envia os documentos na área logada. A Têmis lê, pesquisa as fontes e entrega a minuta da petição inicial com os anexos organizados, sempre como rascunho para a sua revisão.",
    }.items():
        p = OUT / "tarefas" / slug / "index.html"
        if not p.is_file():
            continue
        s = p.read_text(encoding="utf-8")
        s = re.sub(r'<p class="lead">[\s\S]*?</p>', f'<p class="lead">{E(lead)}</p>', s, count=1)
        s = s.replace("Em funcionamento · testada", "Disponível para contratação")
        s = re.sub(r'<div class="statue-slot">[\s\S]*?</div></div></div></section>', '</div></div></section>', s, count=1)
        p.write_text(s, encoding="utf-8")


def redirect(rel: str, alvo: str) -> None:
    dest = OUT / rel / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex, nofollow">'
        f'<meta http-equiv="refresh" content="0;url={E(alvo)}">'
        f'<link rel="canonical" href="{SITE}{E(alvo)}">'
        "<title>Têmis</title>"
        f"<script>location.replace({alvo!r})</script></head><body>"
        f'<p><a href="{E(alvo)}">Continuar</a></p></body></html>\n',
        encoding="utf-8",
    )


def inject_css_all() -> None:
    for p in OUT.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        if "confianca_pos:" in s or "<head" not in s.lower():
            continue
        # skip tiny redirect stubs
        if 'http-equiv="refresh"' in s and len(s) < 800:
            continue
        p.write_text(inject_css(s) if False else s.replace("</head>", f"<style>\n{CSS}\n</style>\n</head>", 1), encoding="utf-8")


def update_sitemap() -> None:
    extra = [
        f"{SITE}/",
        f"{SITE}/temis/",
        f"{SITE}/laboratorio/",
        f"{SITE}/montar/",
        f"{SITE}/combos/",
        f"{SITE}/tarefas/",
        f"{SITE}/seguranca/",
        f"{SITE}/planos/",
    ]
    extra += [f"{SITE}/temis/{t['slug']}/" for t in TEMIS]
    extra += [f"{SITE}/tarefas/{t['slug']}/" for t in TAREFAS]
    # keep other indexable URLs already in sitemap (para-quem-e, etc.)
    have = set()
    sm = OUT / "sitemap.xml"
    if sm.is_file():
        have.update(re.findall(r"<loc>([^<]+)</loc>", sm.read_text(encoding="utf-8")))
    have.update(extra)
    # drop redirects / logged-in / amostra
    drop = {"/amostra/", "/amostra", "/teste-gratis/", "/teste-gratis", "/conta", "/catalogo/"}
    urls = []
    for u in sorted(have):
        path = "/" + u.split("://", 1)[-1].split("/", 1)[-1]
        if not path.startswith("/"):
            path = "/" + path
        if any(path.rstrip("/") == d.rstrip("/") or path.startswith("/conta") for d in drop):
            continue
        if path.startswith("/catalogo"):
            continue
        urls.append(u if u.endswith("/") or u.endswith(".xml") or "." in path.rsplit("/", 1)[-1] else u)
    # normalize
    norm = []
    for u in urls:
        if u.startswith(SITE) and not u.endswith("/") and "." not in u.rsplit("/", 1)[-1]:
            u += "/"
        norm.append(u)
    urls = sorted(set(norm))
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append(f"<url><loc>{E(u)}</loc><lastmod>{TODAY}</lastmod></url>")
    body.append("</urlset>\n")
    sm.write_text("\n".join(body), encoding="utf-8")


def add_jsonld_home() -> None:
    path = OUT / "index.html"
    s = path.read_text(encoding="utf-8")
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": SITE + "/#org", "name": "Têmis",
             "alternateName": ["Têmis OS", "Agente Têmis", "agentetemis"],
             "url": SITE + "/", "email": "contato.pronaos@gmail.com",
             "logo": SITE + "/icon-192.png"},
            {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
             "name": "Têmis OS", "inLanguage": "pt-BR",
             "publisher": {"@id": SITE + "/#org"}},
            {"@type": "SoftwareApplication", "@id": SITE + "/#app",
             "name": "Têmis OS", "applicationCategory": "BusinessApplication",
             "operatingSystem": "Web", "inLanguage": "pt-BR", "url": SITE + "/",
             "description": "Plataforma de inteligência jurídica para minutas e análise de autos, com revisão humana obrigatória. Contratação por tarefa, por aplicativo ou em combos; preços após o login.",
             "publisher": {"@id": SITE + "/#org"}},
        ],
    }
    tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"
    s = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>\n?', "", s)
    s = s.replace("</head>", tag + "</head>", 1)
    path.write_text(s, encoding="utf-8")


def guardrails() -> None:
    ruins = []
    for p in OUT.rglob("*.html"):
        t = p.read_text(encoding="utf-8")
        if re.search(r"em prepara", t, re.I):
            ruins.append(str(p.relative_to(OUT)) + " : em preparação")
        if re.search(r"disponível em breve", t, re.I):
            ruins.append(str(p.relative_to(OUT)) + " : disponível em breve")
        if re.search(r"número da OAB", t, re.I) and "205/2021" not in t[max(0, t.lower().find("número da oab")-80):t.lower().find("número da oab")+80]:
            # catch signup leftovers
            if re.search(r"(crie|criar|cadastre|conta|cadastro|informe).{0,40}número da OAB|número da OAB.{0,40}(conta|cadastro)", t, re.I):
                ruins.append(str(p.relative_to(OUT)) + " : OAB signup")
    if ruins:
        sys.exit("[confianca_pos] recusa: " + "; ".join(ruins[:8]))


def main() -> None:
    if not (OUT / "index.html").is_file():
        raise SystemExit(f"[confianca_pos] não achei {OUT}/index.html")
    copy_assets()
    rewrite_home()
    rewrite_seguranca()
    rewrite_privacidade()
    rewrite_catalog()
    rewrite_laboratorio()
    rewrite_montar_combos_tarefas()
    patch_planos()
    patch_tarefas_testadas()
    redirect("amostra", "/teste-gratis")
    patch_existing_claims()
    inject_css_all()
    add_jsonld_home()
    update_sitemap()
    # ensure nav has laboratorio on pages we didn't fully rewrite
    for p in OUT.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        if 'id="nav"' in s and 'href="/laboratorio/"' not in s and 'http-equiv="refresh"' not in s:
            s = s.replace(
                '<a href="/seguranca/">Segurança</a>',
                '<a href="/laboratorio/">Laboratório</a><a href="/seguranca/">Segurança</a>',
            )
            p.write_text(s, encoding="utf-8")
    guardrails()
    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"[confianca_pos] ok: {n} arquivos; 28 apps; laboratório e redirecionamento de /amostra/")


if __name__ == "__main__":
    main()
