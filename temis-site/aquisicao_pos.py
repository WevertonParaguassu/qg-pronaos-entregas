#!/usr/bin/env python3
"""Pós-processador t1936u/t1940u: restaura a estátua que vira marca d'água,
troca o selo-rosto pela balança (símbolo grego), favicons, CTAs de aquisição
(Max/Ultra, apps, laboratório, sticky no mobile, empurrão nos planos).
Preços só depois do login. Só azul e dourado. Sem caixas brancas, sem lista de espera.
Roda DEPOIS de confianca_pos.py. Rollback: apagar a linha no build.sh.
"""
from __future__ import annotations
import base64, io, re, sys, tarfile
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
HERE = Path(__file__).resolve().parent
BADGE = HERE / "badge"
SITE = "https://agentetemis.com"

STATUE = (
    '<div class="statue-slot">'
    '<a class="statue-acquire" href="/planos/#agente" title="Conheça o agente Têmis (Max e Ultra). Os preços aparecem depois do login.">'
    '<div class="statue-live"><picture>'
    '<source media="(min-width:901px)" srcset="/img/temis-720.webp">'
    '<img src="/img/temis-420.webp" width="420" height="804" '
    'alt="Estátua dourada de Têmis, deusa da justiça, com os olhos vendados, a espada e a balança. Toque para conhecer o agente Têmis." '
    'decoding="async" fetchpriority="high">'
    '</picture></div></a></div>'
)

SELO = (
    '<img class="brand-rosto" src="/img/temis-balanca-96.webp" '
    'srcset="/img/temis-balanca-96.webp 2x, /img/temis-balanca-192.webp 4x" '
    'width="40" height="40" alt="" aria-hidden="true" decoding="async">'
)

CSS = """
/* aquisicao_pos t1940u: estátua clicável, selo-balança, CTAs */
a.statue-acquire{display:block;width:100%;height:100%;color:inherit;text-decoration:none}
.statue-slot,.statue-slot a.statue-acquire{pointer-events:auto}
.statue-live{pointer-events:auto}
.statue-acquire:focus-visible{outline:2px solid #E0C078;outline-offset:4px}
.brand img.brand-rosto{width:40px;height:40px;border-radius:50%;display:block;flex:none;box-shadow:0 0 0 1px #E0C078aa,0 0 0 3px #0B1A33}
.cta-sticky{display:none}
@media(max-width:900px){
  .cta-sticky{display:flex;position:fixed;z-index:40;left:0;right:0;bottom:0;gap:.6rem;padding:.7rem .9rem calc(.7rem + env(safe-area-inset-bottom));
    background:rgba(6,13,27,.94);border-top:1px solid rgba(224,192,120,.45);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
  .cta-sticky a{flex:1;text-align:center;text-decoration:none}
  .cta-sticky .btn,.cta-sticky .btn-ghost{display:block;width:100%}
  body.has-hero{padding-bottom:5.2rem}
  body.hero-visible .cta-sticky{transform:translateY(110%);pointer-events:none}
  .cta-sticky{transition:transform .25s ease}
}
.cta-nudge{margin-top:1.1rem}
.cta-nudge p{margin:.3rem 0 0;color:var(--gold-s,#E0C078);font-size:.92rem}
a.mini.link-card .cta-app, article.mini .cta-app{display:inline-block;margin-top:.7rem;color:#E0C078;font:600 .86rem/1.3 var(--sans,inherit)}
.hero-os .hero-in{align-items:end}
@media(min-width:901px){
  .hero-os .hero-in{grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr)}
  .hero-os .statue-slot{width:min(100%,440px);margin:0 0 0 auto}
}
"""

JS_STICKY = """
(function(){
  var bar=document.querySelector('.cta-sticky');
  if(!bar) return;
  var hero=document.querySelector('.hero');
  function tick(){
    var on=false;
    if(hero){var r=hero.getBoundingClientRect(); on=r.bottom>80}
    document.body.classList.toggle('hero-visible', on);
  }
  tick();
  window.addEventListener('scroll', tick, {passive:true});
  window.addEventListener('resize', tick, {passive:true});
})();
"""

STICKY = (
    '<div class="cta-sticky" role="navigation" aria-label="Começar">'
    '<a class="btn" href="/conta/cadastro">Teste grátis</a>'
    '<a class="btn btn-ghost" href="/planos/#agente">Quero o agente</a>'
    '</div>'
)


def inject_css(head: str) -> str:
    if "aquisicao_pos t1940u" in head:
        return head
    if "</style>" in head:
        return head.replace("</style>", CSS + "</style>", 1)
    return head.replace("</head>", "<style>" + CSS + "</style></head>", 1)


def copy_badge() -> None:
    if not BADGE.exists():
        return
    img = OUT / "img"
    img.mkdir(parents=True, exist_ok=True)
    mapping = {
        "temis-balanca-96.webp": img / "temis-balanca-96.webp",
        "temis-balanca-192.webp": img / "temis-balanca-192.webp",
        "temis-balanca-96.png": img / "temis-balanca-96.png",
        "temis-balanca-192.png": img / "temis-balanca-192.png",
        "favicon.svg": OUT / "favicon.svg",
        "favicon.ico": OUT / "favicon.ico",
        "favicon-32.png": OUT / "favicon-32.png",
        "favicon-48.png": OUT / "favicon-48.png",
        "apple-touch-icon.png": OUT / "apple-touch-icon.png",
        "icon-192.png": OUT / "icon-192.png",
        "icon-512.png": OUT / "icon-512.png",
        "temis-balanca.svg": img / "temis-balanca.svg",
    }
    for src_name, dst in mapping.items():
        src = BADGE / src_name
        if src.exists():
            dst.write_bytes(src.read_bytes())


def restore_statue_home() -> None:
    p = OUT / "index.html"
    if not p.exists():
        return
    h = p.read_text()
    if "statue-acquire" in h and "statue-slot" in h:
        p.write_text(h)
        return
    h2, n = re.subn(
        r'<figure class="hero-shot">.*?</figure>',
        STATUE,
        h,
        count=1,
        flags=re.S,
    )
    if n:
        h = h2
    elif "statue-slot" not in h:
        h = re.sub(r'(</div>\s*</section>)', STATUE + r"\n\1", h, count=1)
    p.write_text(h)


def replace_badge() -> None:
    for p in OUT.rglob("*.html"):
        h = p.read_text()
        h2 = re.sub(
            r'(<a class="brand"[^>]*>)(?:<img class="brand-rosto"[^>]*>|<svg viewBox="0 0 64 64".*?</svg>)',
            lambda m: m.group(1) + SELO,
            h,
            count=1,
            flags=re.S,
        )
        # favicons: keep ico + svg, point to new files (already overwritten)
        if 'href="/favicon.ico"' not in h2 and 'href="/favicon.svg"' in h2:
            h2 = h2.replace(
                '<link rel="icon" href="/favicon.svg"',
                '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg"',
                1,
            )
        if h2 != h:
            p.write_text(h2)


def add_app_ctas() -> None:
    # páginas /temis/<slug>/ — convite ao conjunto / agente, sem preço
    cta = (
        '<p class="cta-nudge"><a class="btn" href="/conta/cadastro">Testar esta aplicação</a> '
        '<a class="btn btn-ghost" href="/montar/">Montar o meu conjunto</a></p>'
        '<p class="fine">Os preços de cada aplicação e dos planos aparecem depois do login. '
        'O agente Têmis pessoal está no Max e no Ultra.</p>'
    )
    for p in (OUT / "temis").rglob("index.html"):
        if p.parent.name in ("", "temis") and p.parent == OUT / "temis":
            # catálogo: já tem botão montar; acrescenta nudge do agente
            s = p.read_text()
            if "planos/#agente" not in s:
                s = s.replace(
                    "</main>",
                    '<section class="sec" id="adquirir"><div class="wrap">'
                    '<div class="sec-head"><p class="eyebrow">Agente Têmis</p>'
                    "<h2>Quer a Têmis como agente pessoal?</h2></div>"
                    "<p>O Max é o agente do seu escritório. O Ultra é o agente com 100% das aplicações. "
                    "Os valores aparecem depois do login.</p>"
                    '<div class="cta-duo"><a class="btn" href="/planos/#agente">Ver Max e Ultra</a>'
                    '<a class="btn btn-ghost" href="/conta/entrar?volta=/conta/planos">Entrar para ver os preços</a></div>'
                    "</div></section></main>",
                    1,
                )
                p.write_text(s)
            continue
        s = p.read_text()
        if "cta-nudge" in s:
            continue
        s2, n = re.subn(
            r'(<div class="actions">.*?</div>)',
            r"\1" + cta,
            s,
            count=1,
            flags=re.S,
        )
        if n == 0:
            s2 = s.replace("</main>", "<div class=\"wrap\">" + cta + "</div></main>", 1)
        p.write_text(s2)


def lab_and_planos_ctas() -> None:
    lab = OUT / "laboratorio" / "index.html"
    if lab.exists():
        s = lab.read_text()
        if "depois-do-lab" not in s:
            bloco = (
                '<section class="sec" id="depois-do-lab"><div class="wrap">'
                '<div class="sec-head"><p class="eyebrow">E agora</p>'
                "<h2>Gostou do que a Têmis fez neste caso fictício?</h2></div>"
                "<p>Comece pelo teste grátis (um por CPF ou CNPJ, sem cartão) ou conheça o agente Têmis "
                "nos planos Max e Ultra. Os preços aparecem depois do login.</p>"
                '<div class="cta-duo"><a class="btn" href="/conta/cadastro">Começar o teste grátis</a>'
                '<a class="btn btn-ghost" href="/planos/#agente">Quero o agente Têmis</a></div>'
                "</div></section>"
            )
            s = s.replace("</main>", bloco + "</main>", 1)
            lab.write_text(s)
    pl = OUT / "planos" / "index.html"
    if pl.exists():
        s = pl.read_text()
        # âncora do agente no Max/Ultra, sem preços
        s = s.replace('id="max"', 'id="max"', 1)
        if 'id="agente"' not in s:
            s = re.sub(
                r'(id="max")',
                r'id="agente" \1',
                s,
                count=1,
            )
        if "nudge-agente" not in s:
            nudge = (
                '<section class="sec" id="nudge-agente"><div class="wrap">'
                "<p>Max é o agente pessoal do escritório. Ultra é o agente com 100% das 28 aplicações. "
                "Para ver os valores e assinar, entre na sua conta. Sem lista de espera.</p>"
                '<div class="cta-duo"><a class="btn" href="/conta/entrar?volta=/conta/planos">Entrar para ver os preços</a>'
                '<a class="btn btn-ghost" href="/conta/cadastro">Criar conta e testar</a></div>'
                "</div></section>"
            )
            s = s.replace("</main>", nudge + "</main>", 1)
        pl.write_text(s)


def sticky_cta() -> None:
    for p in OUT.rglob("*.html"):
        s = p.read_text()
        if "cta-sticky" in s:
            continue
        if "</body>" not in s:
            continue
        s = s.replace("</body>", STICKY + "<script>" + JS_STICKY + "</script></body>", 1)
        p.write_text(s)


def inject_css_all() -> None:
    for p in OUT.rglob("*.html"):
        s = p.read_text()
        if "<head" not in s:
            continue
        # inject into first style or head
        if "aquisicao_pos t1940u" in s:
            continue
        s2, n = re.subn(r"</style>", CSS + "</style>", s, count=1)
        if n == 0:
            s2 = s.replace("</head>", "<style>" + CSS + "</style></head>", 1)
        p.write_text(s2)


def main() -> None:
    if not OUT.exists():
        sys.exit(f"saída inexistente: {OUT}")
    copy_badge()
    restore_statue_home()
    replace_badge()
    add_app_ctas()
    lab_and_planos_ctas()
    sticky_cta()
    inject_css_all()
    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"[aquisicao_pos] ok: {n} html; selo-balança; estátua no hero; CTAs")


if __name__ == "__main__":
    main()
