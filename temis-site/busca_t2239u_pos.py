#!/usr/bin/env python3
"""t2239u — busca da marca Têmis / Temis / Agente Têmis.

Roda no build do Render, depois do suporte e antes do PWA, sobre a pasta out/.
Não altera o pacote site.tgz.b64 nem o robots.txt (o antirobo já libera os
robôs de busca/resposta de IA nas páginas públicas e bloqueia treino + área logada).

Faz:
  - título, description e OG/Twitter da home com «Têmis (Temis)» e «Agente Têmis»
  - linha visível «Têmis — também escrito Temis» na home (azul e dourado)
  - hreflang pt-BR e x-default nas páginas indexáveis
  - JSON-LD Organization + WebSite + SoftwareApplication com alternateName
  - sitemap.xml completo das páginas indexáveis (inclui /suporte/ e /relatar/)

Rollback: apagar a linha deste script no build.sh.
Sem Adapta, sem rivais, sem nome/CPF/CNPJ do titular, sem «assinatura»,
«gratuita» ou «grátis».
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
MARCA = "<!--busca-t2239u-->"

HOME_TITLE = "Têmis (Temis) · Agente Têmis · IA para advogados"
HOME_DESC = (
    "Têmis (Temis) é o Agente Têmis: inteligência jurídica para a advocacia "
    "brasileira. Tarefas e aplicativos Têmis; preços em Planos. Sem custo no teste."
)
OG_ALT = "Têmis (Temis), Agente Têmis — inteligência jurídica para advogados"
ALTERNATE = [
    "Temis",
    "Agente Têmis",
    "Agente Temis",
    "Têmis IA",
    "Temis IA",
    "Têmis OS",
    "agentetemis",
]
LD_DESC = (
    "Têmis (Temis), o Agente Têmis, é a plataforma de inteligência jurídica "
    "para a advocacia brasileira. Contratação por tarefa, por aplicativo Têmis "
    "ou em combos, com revisão humana obrigatória."
)
DISALLOW_PREFIXES = (
    "/conta",
    "/painel",
    "/api/",
    "/billing",
    "/login",
    "/sair",
    "/teste-gratis",
    "/teste-gratuito",
    "/uploads/",
    "/estacao",
    "/amostra",
)
CSS = """
/* busca-t2239u: grafia Têmis / Temis (azul e dourado) */
.tm-grafia{margin:.85rem 0 0;font:500 .95rem/1.5 var(--sans);color:var(--gold-l);letter-spacing:.01em}
.tm-grafia b{font-weight:600;color:var(--gold-s)}
"""


def rel_of(p: Path) -> str:
    rel = p.relative_to(OUT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel.endswith(".html"):
        return "/" + rel
    return "/" + rel


def is_disallowed(rel: str) -> bool:
    r = rel if rel.startswith("/") else "/" + rel
    for d in DISALLOW_PREFIXES:
        if r == d or r.startswith(d.rstrip("/") + "/") or r.startswith(d):
            return True
    return False


def has_noindex(html: str) -> bool:
    for m in re.finditer(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', html, re.I):
        if re.search(r"\bnoindex\b", m.group(1), re.I):
            return True
    return False


def canonical_of(html: str, rel: str) -> str:
    m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html, re.I)
    if m:
        return m.group(1).strip()
    if rel == "/":
        return SITE + "/"
    return SITE + rel


def set_meta(html: str, *, title: str, desc: str, url: str) -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", html, count=1, flags=re.I | re.S)
    if re.search(r'<meta\s+name=["\']description["\']', html, re.I):
        html = re.sub(
            r'<meta\s+name=["\']description["\']\s+content="[^"]*"',
            f'<meta name="description" content="{E(desc)}"',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = html.replace("<head>", f'<head><meta name="description" content="{E(desc)}">', 1)
    pairs = {
        "og:title": title,
        "og:description": desc,
        "og:url": url,
        "og:site_name": "Têmis",
        "og:locale": "pt_BR",
        "twitter:title": title,
        "twitter:description": desc,
        "og:image:alt": OG_ALT,
    }
    for prop, val in pairs.items():
        attr = "property" if prop.startswith("og:") else "name"
        pat = rf'<meta\s+(?:property|name)="{re.escape(prop)}"\s+content="[^"]*"'
        if re.search(pat, html, re.I):
            html = re.sub(pat, f'<meta {attr}="{prop}" content="{E(val)}"', html, count=1, flags=re.I)
        else:
            html = html.replace("</head>", f'<meta {attr}="{prop}" content="{E(val)}">\n</head>', 1)
    return html


def ensure_hreflang(html: str, url: str) -> str:
    # idempotente: tira hreflang antigo e recoloca
    html = re.sub(r'\s*<link\s+rel=["\']alternate["\']\s+hreflang=["\'][^"\']+["\']\s+href=["\'][^"\']+["\']\s*/?>', "", html, flags=re.I)
    tags = (
        f'<link rel="alternate" hreflang="pt-BR" href="{E(url)}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{E(url)}">\n'
    )
    if re.search(r'rel=["\']canonical["\']', html, re.I):
        html = re.sub(
            r'(<link\s+rel=["\']canonical["\'][^>]*>)',
            r"\1\n" + tags,
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = html.replace("</head>", tags + "</head>", 1)
    return html


def ld_graph() -> dict:
    org_id = SITE + "/#org"
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": org_id,
                "name": "Têmis",
                "alternateName": ALTERNATE,
                "url": SITE + "/",
                "email": "temis@e-pronaos.com",
                "logo": SITE + "/icon-192.png",
            },
            {
                "@type": "WebSite",
                "@id": SITE + "/#website",
                "url": SITE + "/",
                "name": "Têmis",
                "alternateName": ALTERNATE,
                "inLanguage": "pt-BR",
                "publisher": {"@id": org_id},
            },
            {
                "@type": "SoftwareApplication",
                "@id": SITE + "/#app",
                "name": "Têmis",
                "alternateName": ALTERNATE,
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "inLanguage": "pt-BR",
                "url": SITE + "/",
                "description": LD_DESC,
                "publisher": {"@id": org_id},
            },
        ],
    }


def _keep_from_graph(data) -> list:
    keep = []
    if isinstance(data, dict) and isinstance(data.get("@graph"), list):
        items = data["@graph"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        return keep
    for x in items:
        if not isinstance(x, dict):
            continue
        t = x.get("@type")
        types = t if isinstance(t, list) else [t]
        if "BreadcrumbList" in types or "FAQPage" in types:
            keep.append(x)
    return keep


def upsert_jsonld(html: str) -> str:
    graph = ld_graph()
    scripts = list(re.finditer(r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>', html, re.I | re.S))
    keep: list = []
    if scripts:
        # preserva migalhas/FAQ; o bloco de Organization/WebSite/SoftwareApplication é o nosso
        for m in scripts:
            try:
                data = json.loads(m.group(1))
            except Exception:
                continue
            keep.extend(_keep_from_graph(data))
        html = re.sub(r'<script\s+type=["\']application/ld\+json["\']\s*>.*?</script>\s*', "", html, flags=re.I | re.S)
    seen = set()
    for item in keep:
        t = item.get("@type")
        key = (t if isinstance(t, str) else tuple(t or []), item.get("@id"))
        if key in seen:
            continue
        seen.add(key)
        graph["@graph"].append(item)
    tag = '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + "</script>\n"
    return html.replace("</head>", tag + "</head>", 1)


def inject_visible_line(html: str) -> str:
    if "tm-grafia" in html:
        # atualiza o texto se já existir
        html = re.sub(
            r'<p class="tm-grafia">.*?</p>',
            '<p class="tm-grafia"><b>Têmis</b> — também escrito Temis.</p>',
            html,
            count=1,
            flags=re.S,
        )
        return html
    line = '<p class="tm-grafia"><b>Têmis</b> — também escrito Temis.</p>'
    if '<p class="lead">' in html:
        html = re.sub(
            r'(<p class="lead">.*?</p>)',
            r"\1\n" + line,
            html,
            count=1,
            flags=re.S,
        )
    elif '<div class="hero-copy">' in html:
        html = html.replace('<div class="hero-copy">', '<div class="hero-copy">' + line, 1)
    else:
        html = re.sub(r"(<main[^>]*>)", r"\1" + line, html, count=1)
    return html


def inject_css(html: str) -> str:
    if "busca-t2239u: grafia" in html or "tm-grafia{" in html:
        return html
    return html.replace("</head>", f"<style>{CSS}</style>\n</head>", 1)


def patch_eyebrow(html: str) -> str:
    # só a home: deixa a grafia também no olho da hero
    html = html.replace(
        "Têmis OS · Plataforma de inteligência jurídica",
        "Têmis (Temis) · Agente Têmis",
        1,
    )
    return html


def write_sitemap(urls: list[str]) -> None:
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        body.append(f"<url><loc>{E(u)}</loc><lastmod>{TODAY}</lastmod></url>")
    body.append("</urlset>\n")
    (OUT / "sitemap.xml").write_text("\n".join(body), encoding="utf-8")


def collect_indexable() -> list[str]:
    urls = []
    for p in sorted(OUT.rglob("*.html")):
        if p.name == "404.html" or p.name == "offline.html":
            continue
        # arquivo de verificação do Search Console, não é página de conteúdo
        if re.fullmatch(r"google[0-9a-f]+\.html", p.name, re.I):
            continue
        rel = rel_of(p)
        if is_disallowed(rel):
            continue
        html = p.read_text(encoding="utf-8")
        if has_noindex(html):
            continue
        if re.search(r"<title>\s*Redirecionando", html, re.I):
            continue
        urls.append(canonical_of(html, rel).split("#")[0])
    # normaliza e ordena, home primeiro
    norm = []
    seen = set()
    for u in urls:
        if not u.startswith(SITE):
            continue
        if u != SITE + "/" and not u.endswith("/") and "." not in u.rsplit("/", 1)[-1]:
            u += "/"
        if u in seen:
            continue
        seen.add(u)
        norm.append(u)
    norm.sort(key=lambda u: (u != SITE + "/", u))
    return norm


def process_home(p: Path) -> None:
    html = p.read_text(encoding="utf-8")
    html = set_meta(html, title=HOME_TITLE, desc=HOME_DESC, url=SITE + "/")
    html = patch_eyebrow(html)
    html = inject_visible_line(html)
    html = inject_css(html)
    html = upsert_jsonld(html)
    html = ensure_hreflang(html, SITE + "/")
    if MARCA not in html:
        html = html.replace("</body>", MARCA + "</body>", 1)
    p.write_text(html, encoding="utf-8")


def process_other(p: Path, rel: str) -> None:
    html = p.read_text(encoding="utf-8")
    if has_noindex(html) or is_disallowed(rel):
        return
    url = canonical_of(html, rel)
    # só hreflang nas páginas canônicas próprias (não em redirecionamentos finos)
    if url.rstrip("/") != (SITE + rel).rstrip("/") and rel != "/":
        return
    new = ensure_hreflang(html, url)
    if new != html:
        if MARCA not in new:
            new = new.replace("</body>", MARCA + "</body>", 1) if "</body>" in new else new
        p.write_text(new, encoding="utf-8")


def append_css_asset() -> None:
    path = OUT / "assets" / "site.css"
    if not path.exists():
        return
    txt = path.read_text(encoding="utf-8")
    if "busca-t2239u: grafia" in txt:
        return
    path.write_text(txt.rstrip() + "\n" + CSS.strip() + "\n", encoding="utf-8")


def main() -> None:
    if not (OUT / "index.html").is_file():
        sys.exit("[busca_t2239u] sem out/index.html")
    process_home(OUT / "index.html")
    n = 1
    for p in OUT.rglob("*.html"):
        if p == OUT / "index.html" or p.name == "404.html":
            continue
        process_other(p, rel_of(p))
        n += 1
    append_css_asset()
    urls = collect_indexable()
    write_sitemap(urls)
    print(f"[busca_t2239u] ok: home + hreflang, {len(urls)} urls no sitemap, html={n}")


if __name__ == "__main__":
    main()
