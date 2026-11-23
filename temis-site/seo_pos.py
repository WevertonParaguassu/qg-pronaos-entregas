#!/usr/bin/env python3
"""Pós-processador SEO + Sugestões do site público da Têmis.

Roda no build do Render, depois do nav_pos.py, sobre a pasta out/.
Não altera o pacote site.tgz.b64, planos.json, nem o painel mestre.

Faz:
  - BreadcrumbList (JSON-LD + migalhas visíveis) onde faltava
  - robots.txt (disallow da área logada)
  - sitemap.xml com lastmod e páginas novas indexáveis
  - noindex em 404 e em redirecionamentos finos
  - correção de textos desatualizados (termos/privacidade)
  - página /sugestoes/ + formulário no rodapé (honeypot, aviso LGPD)
  - página /avaliacoes/ (fluxo honesto, sem AggregateRating)
  - CSS/JS do formulário, endpoint no window.TEMIS

Rollback: apagar a linha do build.sh que chama este script.
Sem AggregateRating, sem preços, sem CPF/CNPJ/telefone/endereço do Weverton.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
from datetime import date
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
SITE = "https://agentetemis.com"
TODAY = date.today().isoformat()
E = htmllib.escape
ENDPOINT = "https://n8n.e-pronaos.com/webhook/temis-sugestoes"

# Páginas de conteúdo que precisam de migalhas (caminho relativo com / final)
CRUMBS = {
    "para-quem-e/": [("Início", "/"), ("Para quem é", None)],
    "para-quem-e/advocacia-autonoma/": [
        ("Início", "/"),
        ("Para quem é", "/para-quem-e/"),
        ("Advocacia autônoma", None),
    ],
    "para-quem-e/escritorios/": [
        ("Início", "/"),
        ("Para quem é", "/para-quem-e/"),
        ("Escritórios", None),
    ],
    "para-quem-e/departamentos-juridicos/": [
        ("Início", "/"),
        ("Para quem é", "/para-quem-e/"),
        ("Departamentos jurídicos", None),
    ],
    "seguranca/": [("Início", "/"), ("Segurança e sigilo", None)],
    "afiliados/": [("Início", "/"), ("Afiliados", None)],
    "privacidade/": [("Início", "/"), ("Privacidade", None)],
    "termos/": [("Início", "/"), ("Termos de uso", None)],
    "sugestoes/": [("Início", "/"), ("Sugestões", None)],
    "avaliacoes/": [("Início", "/"), ("Avaliações", None)],
}

ROBOTS = """User-agent: *
Allow: /
Disallow: /conta
Disallow: /conta/
Disallow: /painel
Disallow: /api/
Disallow: /billing
Disallow: /billing/
Disallow: /login
Disallow: /sair
Disallow: /teste-gratis
Disallow: /teste-gratis/

Sitemap: https://agentetemis.com/sitemap.xml
"""

CSS_EXTRA = """
/* seo_pos: migalhas, formulário de sugestões e rodapé (azul e dourado) */
.crumbs{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;font-size:.86rem;margin:0 0 1rem;color:var(--ink-3)}
.crumbs a{color:var(--gold-l);text-decoration:none;padding:.35rem 0;min-height:32px;display:inline-flex;align-items:center}
.crumbs span[aria-hidden]{opacity:.6}
.form-sugestao,.foot-sugestao{display:grid;gap:.7rem;margin:0}
.foot-sugestao{margin-top:.4rem;max-width:22rem}
.form-sugestao textarea{min-height:7rem;resize:vertical}
.foot-sugestao textarea{min-height:4.4rem;resize:vertical}
.form-sugestao .linha{display:grid;gap:.6rem;grid-template-columns:1fr}
@media (min-width:640px){.form-sugestao .linha{grid-template-columns:1fr 1fr}}
.sug-ok{margin:0;padding:1rem 1.1rem;border-radius:12px;border:1px solid rgba(224,192,120,.45);background:rgba(6,16,34,.78);color:var(--head)}
.form-sugestao.sent .campos,.foot-sugestao.sent .campos{display:none}
.aviso-lgpd{font-size:.82rem;color:var(--ink-3);margin:0}
"""

JS_EXTRA = r"""
/* seo_pos: formulário de Sugestões */
(function(){
  var d=document, CFG=window.TEMIS||{};
  var $=function(s,c){return(c||d).querySelector(s)};
  d.querySelectorAll('form.form-sugestao, form.foot-sugestao').forEach(function(f){
    var st=$('.form-status',f), btn=$('button[type=submit]',f);
    if(!st||!btn) return;
    f.addEventListener('submit', function(ev){
      ev.preventDefault();
      st.className='form-status';
      var v=function(n){return (f.elements[n]&&f.elements[n].value||'').trim()};
      var data={
        nome:v('nome'), email:v('email'), sugestao:v('sugestao'),
        consentimento: !!(f.elements.consentimento && f.elements.consentimento.checked),
        origem: location.pathname, website:v('website')
      };
      var err='';
      if(data.sugestao.length<10 || data.sugestao.length>2000) err='Escreva a sugestão em 10 a 2.000 caracteres.';
      else if(data.email && !/^[^\s@]{1,64}@[^\s@]{2,190}\.[a-z]{2,}$/i.test(data.email)) err='Se informar e-mail, use um endereço válido.';
      else if(data.nome.length>90) err='O nome pode ter no máximo 90 caracteres.';
      else if(!data.consentimento) err='Para enviar, confirme que leu o aviso de privacidade.';
      if(err){ st.textContent=err; st.classList.add('err'); return; }
      btn.disabled=true; st.textContent='Enviando…';
      var done=function(){
        f.classList.add('sent');
        var ok=$('.sug-ok', f.parentNode) || $('.sug-ok', f);
        if(ok){ ok.hidden=false; try{ok.focus()}catch(e){} }
        st.textContent='';
      };
      var fallback=function(){
        var body='Sugestão:%0A'+data.sugestao+(data.nome?'%0ANome: '+data.nome:'')+(data.email?'%0AE-mail: '+data.email:'');
        st.innerHTML='Não conseguimos enviar agora. <a href="mailto:'+ (CFG.contato||'contato.pronaos@gmail.com') +'?subject='+encodeURIComponent('Sugestão para a Têmis')+'&body='+body+'">Envie por e-mail</a>.';
        st.classList.add('err'); btn.disabled=false;
      };
      var ep=CFG.endpointSugestoes||'';
      if(!ep){ fallback(); return; }
      var ctl=window.AbortController?new AbortController():null;
      var to=setTimeout(function(){ctl&&ctl.abort()},12000);
      var fd=new URLSearchParams();
      Object.keys(data).forEach(function(k){fd.append(k, data[k]==null?'':String(data[k]));});
      fetch(ep,{method:'POST',body:fd,signal:ctl&&ctl.signal,mode:'cors'})
        .then(function(r){clearTimeout(to);return r.json().catch(function(){return{}}).then(function(j){if(r.ok&&j.ok){done()}else{fallback()}})})
        .catch(function(){clearTimeout(to);fallback()});
    });
  });
})();
"""

FORM_FIELDS = """\
<div class="campos">
<label>Sua sugestão<textarea name="sugestao" rows="4" required maxlength="2000" placeholder="O que podemos melhorar na Têmis?"></textarea></label>
<div class="linha">
<label>Nome (opcional)<input name="nome" autocomplete="name" maxlength="90"></label>
<label>E-mail (opcional)<input name="email" type="email" autocomplete="email" maxlength="190"></label>
</div>
<label class="hp" aria-hidden="true">Deixe em branco<input name="website" tabindex="-1" autocomplete="off"></label>
<label class="check"><input type="checkbox" name="consentimento"> Li o aviso: se eu informar nome ou e-mail, eles serão usados só para entender e, se couber, responder esta sugestão, conforme a <a href="/privacidade/">política de privacidade</a>. Sem nome e e-mail, a sugestão é anônima.</label>
<button class="btn" type="submit">Enviar sugestão</button>
<p class="form-status" role="status" aria-live="polite"></p>
</div>
<p class="sug-ok" hidden tabindex="-1">Obrigado. Sua sugestão chegou até nós.</p>
"""

FOOT_FORM = f"""<form class="form foot-sugestao" novalidate>
{FORM_FIELDS}
</form>"""

PAGE_FORM = f"""<form id="form-sugestao" class="form form-sugestao" novalidate>
{FORM_FIELDS}
</form>"""


def rel_of(p: Path) -> str:
    rel = p.relative_to(OUT).as_posix()
    if rel == "index.html":
        return ""
    if rel.endswith("/index.html"):
        return rel[: -len("index.html")]
    return rel


def is_redirect(html: str) -> bool:
    return "http-equiv=\"refresh\"" in html.lower() or "location.replace(" in html


def is_404(html: str) -> bool:
    return "Página não encontrada · Têmis" in html or "Esta página não existe no site da Têmis." in html


def is_thin(html: str) -> bool:
    return is_redirect(html) or is_404(html) or "google-site-verification:" in html and len(html) < 200


def ensure_noindex(html: str) -> str:
    if re.search(r'<meta[^>]+name=["\']robots["\']', html, re.I):
        html = re.sub(
            r'<meta[^>]+name=["\']robots["\'][^>]*>',
            '<meta name="robots" content="noindex, nofollow">',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = re.sub(
            r"(<meta charset=\"utf-8\">)",
            r'\1<meta name="robots" content="noindex, nofollow">',
            html,
            count=1,
            flags=re.I,
        )
        if "name=\"robots\"" not in html:
            html = html.replace("<head>", '<head><meta name="robots" content="noindex, nofollow">', 1)
    return html


def crumb_nav(items: list[tuple[str, str | None]]) -> str:
    parts = ['<nav class="crumbs" aria-label="Você está em">']
    for i, (name, href) in enumerate(items):
        if i:
            parts.append('<span aria-hidden="true">›</span>')
        if href is None:
            parts.append(f'<span aria-current="page">{E(name)}</span>')
        else:
            parts.append(f'<a href="{E(href)}">{E(name)}</a>')
    parts.append("</nav>")
    return "".join(parts)


def crumb_ld(items: list[tuple[str, str | None]], current_url: str) -> dict:
    els = []
    for i, (name, href) in enumerate(items, 1):
        url = SITE + (href or "") if href else current_url
        if not href:
            url = current_url
        els.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": url,
            }
        )
    return {"@type": "BreadcrumbList", "@id": current_url.rstrip("/") + "#breadcrumb", "itemListElement": els}


def inject_ld(html: str, obj: dict) -> str:
    if '"@type":"BreadcrumbList"' in html or '"@type": "BreadcrumbList"' in html:
        return html

    def add_to_graph(m: re.Match) -> str:
        raw = m.group(1)
        try:
            data = json.loads(raw)
        except Exception:
            return m.group(0)
        if isinstance(data, dict) and "@graph" in data:
            types = {
                (x.get("@type") if isinstance(x, dict) else None)
                for x in data["@graph"]
            }
            if "BreadcrumbList" in types:
                return m.group(0)
            data["@graph"].append(obj)
            return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'
        return m.group(0)

    new, n = re.subn(
        r'<script type="application/ld\+json">(.*?)</script>',
        add_to_graph,
        html,
        count=1,
        flags=re.I | re.S,
    )
    if n:
        return new
    blob = json.dumps({"@context": "https://schema.org", "@graph": [obj]}, ensure_ascii=False, separators=(",", ":"))
    return html.replace("</head>", f'<script type="application/ld+json">{blob}</script></head>', 1)


def inject_visible_crumbs(html: str, items: list[tuple[str, str | None]]) -> str:
    if 'class="crumbs"' in html:
        return html
    nav = crumb_nav(items)
    if '<div class="hero-copy">' in html:
        return html.replace('<div class="hero-copy">', '<div class="hero-copy">' + nav, 1)
    if "<main" in html:
        return re.sub(r"(<main[^>]*>)", r"\1" + nav, html, count=1)
    return html


def patch_legal(html: str, rel: str) -> str:
    if rel == "termos/":
        old = (
            "O site é informativo. Não há login, pagamento nem preços aqui. "
            "Nada do que você lê neste site substitui a atuação de um profissional habilitado. "
            "A Têmis prepara minutas e organizações de trabalho para revisão humana: "
            "quem decide e protocola é sempre você, ou o profissional responsável pelo caso."
        )
        new = (
            "O site apresenta a Têmis e permite criar conta e entrar. "
            "Os preços só aparecem depois do login; não são publicados nas páginas abertas. "
            "Nada do que você lê neste site substitui a atuação de um profissional habilitado. "
            "A Têmis prepara minutas (rascunhos) para revisão do advogado: "
            "quem decide, assina e protocola é sempre o profissional responsável pelo caso."
        )
        html = html.replace(old, new)
    if rel == "privacidade/":
        html = html.replace(
            "Não há login, cobrança nem envio de documentos por aqui.",
            "A criação de conta, o login e o envio de documentos do caso acontecem na área do cliente. "
            "Os preços só aparecem depois do login. As páginas abertas deste site não cobram nem exibem valores.",
        )
        old_am = (
            "Coletamos nome, e-mail, área e uma breve descrição do que você quer testar. "
            "Esses dados servem só para avaliar o pedido e enviar a sua amostra. "
            "Não envie documentos de clientes nem dados sensíveis de terceiros pelo formulário."
        )
        new_am = (
            "O teste grátis é liberado ao criar a conta, com CPF ou CNPJ. "
            "Os dados da conta servem para identificar a amostra (uma por pessoa) e o escritório. "
            "Não envie documentos de clientes nem dados sensíveis de terceiros no teste."
        )
        html = html.replace(old_am, new_am)
        if "Sugestões" not in html:
            extra = (
                "<h3>Sugestões</h3><p>No formulário de sugestões, o texto é obrigatório. "
                "Nome e e-mail são opcionais e, se informados, servem só para entender e, se couber, "
                "responder a sugestão. Sem eles, a sugestão é anônima.</p>"
            )
            html = html.replace("<h3>Cadastro de afiliados</h3>", extra + "<h3>Cadastro de afiliados</h3>", 1)
    return html


def patch_temis_cfg(html: str) -> str:
    def add(m: re.Match) -> str:
        raw = m.group(1)
        try:
            data = json.loads(raw)
        except Exception:
            if "endpointSugestoes" in raw:
                return m.group(0)
            raw2 = raw.rstrip()
            if raw2.endswith("}"):
                raw2 = raw2[:-1] + f', "endpointSugestoes": "{ENDPOINT}"}}'
                return f"<script>window.TEMIS={raw2}</script>"
            return m.group(0)
        if "endpointSugestoes" not in data:
            data["endpointSugestoes"] = ENDPOINT
        return "<script>window.TEMIS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"

    html, n = re.subn(r"<script>window.TEMIS=(.*?)</script>", add, html, count=1, flags=re.S)
    if n:
        return html
    # páginas internas sem o bloco completo: injeta o essencial antes de </body>
    if "endpointSugestoes" in html:
        return html
    if "</body>" in html:
        cfg = json.dumps(
            {
                "contato": "contato.pronaos@gmail.com",
                "endpointSugestoes": ENDPOINT,
                "site": SITE,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return html.replace("</body>", f"<script>window.TEMIS=Object.assign(window.TEMIS||{cfg},window.TEMIS||{{}})</script></body>", 1)
    return html


def inject_footer(html: str, skip_form: bool = False) -> str:
    if "/sugestoes/" not in html.split("</nav>")[0] if "</nav>" in html else True:
        pass
    # link no menu do rodapé
    if 'href="/sugestoes/"' not in html:
        html = html.replace(
            '<a href="/termos/">Termos de uso</a>',
            '<a href="/sugestoes/">Sugestões</a><a href="/avaliacoes/">Avaliações</a><a href="/termos/">Termos de uso</a>',
            1,
        )
    # formulário compacto no bloco de contato
    if skip_form or 'class="foot-sugestao"' in html or 'class="form foot-sugestao"' in html:
        return html
    block = (
        '<div class="foot-sug">'
        '<p class="muted"><a href="/sugestoes/">Sugestões</a></p>'
        f"{FOOT_FORM}"
        "<p class=\"aviso-lgpd\">Uma mensagem por vez. Sem dados de clientes.</p>"
        "</div>"
    )
    html = html.replace(
        '<p><a href="mailto:contato.pronaos@gmail.com">contato.pronaos@gmail.com</a></p></div>',
        '<p><a href="mailto:contato.pronaos@gmail.com">contato.pronaos@gmail.com</a></p>' + block + "</div>",
        1,
    )
    return html


def append_asset(path: Path, marker: str, extra: str) -> None:
    if not path.exists():
        return
    txt = path.read_text(encoding="utf-8")
    if marker in txt:
        return
    # remove comentário residual da lista de espera, se ainda existir
    if path.suffix == ".css":
        txt = re.sub(r"/\*[^*]*lista de espera[^*]*\*/", "/* sticky CTA no mobile */", txt)
    path.write_text(txt.rstrip() + "\n" + extra.strip() + "\n", encoding="utf-8")


def write_static_page(rel: str, title: str, desc: str, h1: str, eyebrow: str, body_html: str, items: list) -> None:
    dest = OUT / rel / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    donor = OUT / "privacidade" / "index.html"
    if not donor.exists():
        donor = OUT / "termos" / "index.html"
    if not donor.exists():
        raise SystemExit(f"sem página-base para gerar {rel}")
    html = donor.read_text(encoding="utf-8")
    url = SITE + "/" + rel

    def set_meta(name: str, content: str, html: str) -> str:
        html = re.sub(
            rf"<title>.*?</title>",
            f"<title>{E(title)}</title>",
            html,
            count=1,
            flags=re.I | re.S,
        )
        html = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{E(desc)}">',
            html,
            count=1,
        )
        for prop, val in {
            "og:title": title,
            "og:description": desc,
            "og:url": url,
            "twitter:title": title,
            "twitter:description": desc,
        }.items():
            html = re.sub(
                rf'<meta (?:property|name)="{re.escape(prop)}" content="[^"]*">',
                lambda m, p=prop, v=val: m.group(0).split("content=")[0] + f'content="{E(v)}">',
                html,
                count=1,
            )
        html = re.sub(
            r'<link rel="canonical" href="[^"]*">',
            f'<link rel="canonical" href="{url}">',
            html,
            count=1,
        )
        return html

    html = set_meta(title, desc, html)
    # troca o conteúdo principal (hero + section prose)
    hero = (
        '<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">'
        + crumb_nav(items)
        + f'<p class="eyebrow">{E(eyebrow)}</p><h1>{h1}</h1>'
        + "</div>"
    )
    html = re.sub(
        r'<section class="hero hero-page"><div class="wrap hero-in"><div class="hero-copy">[\s\S]*?</div>',
        hero,
        html,
        count=1,
    )
    html = re.sub(
        r'(<section class="sec"><div class="wrap prose">)[\s\S]*?(</div></section>)',
        r"\1\n" + body_html + r"\n\2",
        html,
        count=1,
    )
    html = inject_ld(html, crumb_ld(items, url))
    dest.write_text(html, encoding="utf-8")


def collect_indexable() -> list[str]:
    urls = []
    for p in sorted(OUT.rglob("*.html")):
        if p.name in {"404.html", "google1d303b8551cc5763.html"}:
            continue
        rel = rel_of(p)
        if any(rel.startswith(x) for x in ("conta/", "painel", "api/", "billing/", "teste-gratis")):
            continue
        html = p.read_text(encoding="utf-8", errors="replace")
        if is_redirect(html) or is_404(html):
            continue
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', html, re.I):
            continue
        path = "/" if rel == "" else "/" + rel
        if not path.endswith("/") and not path.split("/")[-1].count("."):
            path += "/"
        urls.append(SITE + path)
    # unique preserve order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def write_sitemap(urls: list[str]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        lines.append(f"<url><loc>{E(u)}</loc><lastmod>{TODAY}</lastmod></url>")
    lines.append("</urlset>\n")
    (OUT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def process_html_file(p: Path) -> None:
    if p.name == "google1d303b8551cc5763.html":
        return
    html = p.read_text(encoding="utf-8")
    orig = html
    rel = rel_of(p)
    if p.name == "404.html" or is_404(html) or is_redirect(html):
        html = ensure_noindex(html)
        if html != orig:
            p.write_text(html, encoding="utf-8")
        return
    html = patch_legal(html, rel)
    items = CRUMBS.get(rel)
    if items:
        current = SITE + "/" + rel
        html = inject_visible_crumbs(html, items)
        html = inject_ld(html, crumb_ld(items, current))
    html = patch_temis_cfg(html)
    html = inject_footer(html, skip_form=(rel == "sugestoes/"))
    if html != orig:
        p.write_text(html, encoding="utf-8")


def main() -> None:
    if not (OUT / "index.html").exists():
        raise SystemExit(f"out inválido: {OUT}")

    sug_body = f"""
<p>Quer melhorar a Têmis? Escreva aqui. Nome e e-mail são opcionais. A sugestão chega à equipe no e-mail contato.pronaos@gmail.com.</p>
<p class="aviso-lgpd">Não envie documentos de clientes, dados sensíveis de terceiros, senhas ou números de processo sigilosos. Peças geradas pela Têmis continuam sendo rascunhos para revisão do advogado responsável.</p>
{PAGE_FORM}
<p><a href="/privacidade/">Como tratamos os dados</a> · <a href="/termos/">Termos de uso</a></p>
"""
    av_body = """
<p>As avaliações da Têmis são só de quem de fato usou o serviço. Não compramos, não inventamos e não publicamos estrelas falsas.</p>
<h2>Como pedimos a avaliação</h2>
<ul>
<li>Depois de um kit concluído com sucesso (por exemplo, a minuta e os anexos entregues para a sua revisão), a Têmis pode perguntar, na área do cliente, se a entrega ajudou.</li>
<li>O pedido é opcional. Recusar não muda o seu plano nem o atendimento.</li>
<li>Quando o perfil da Têmis no Google estiver publicado, o convite incluirá o link oficial para avaliar lá. Até lá, o comentário fica só conosco, para melhorar o produto.</li>
</ul>
<h2>O que não fazemos</h2>
<ul>
<li>Não exibimos nota média inventada neste site.</li>
<li>Não pedimos avaliação em troca de desconto, crédito ou vantagem.</li>
<li>Não publicamos depoimento sem que a pessoa tenha usado a Têmis de verdade.</li>
</ul>
<p>Se já é cliente e quer falar da experiência agora, use a página de <a href="/sugestoes/">Sugestões</a> ou o e-mail <a href="mailto:contato.pronaos@gmail.com">contato.pronaos@gmail.com</a>.</p>
"""
    write_static_page(
        "sugestoes/",
        "Sugestões · Têmis",
        "Envie uma sugestão para a Têmis. Nome e e-mail são opcionais. O aviso de privacidade aparece no formulário.",
        "Sugestões",
        "Fale com a Têmis",
        sug_body,
        CRUMBS["sugestoes/"],
    )
    write_static_page(
        "avaliacoes/",
        "Avaliações honestas · Têmis",
        "A Têmis só pede avaliação a quem de fato usou o serviço, depois de um kit concluído. Sem estrelas inventadas.",
        "Avaliações honestas",
        "Estrelas de verdade",
        av_body,
        CRUMBS["avaliacoes/"],
    )

    # 404: garantir arquivo noindex (Render usa 404.html)
    four = OUT / "404.html"
    if not four.exists():
        # tenta copiar de uma resposta já conhecida se existir no lote local
        pass
    if four.exists():
        html = ensure_noindex(four.read_text(encoding="utf-8"))
        four.write_text(html, encoding="utf-8")

    for p in OUT.rglob("*.html"):
        process_html_file(p)

    append_asset(OUT / "assets" / "site.css", "form.foot-sugestao, form.form-sugestao" if False else "seo_pos: migalhas", CSS_EXTRA)
    append_asset(OUT / "assets" / "site.js", "seo_pos: formulário de Sugestões", JS_EXTRA)

    (OUT / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    urls = collect_indexable()
    write_sitemap(urls)
    print(f"[seo_pos] ok: {len(urls)} urls no sitemap, pages html={sum(1 for _ in OUT.rglob('*.html'))}")


if __name__ == "__main__":
    main()
