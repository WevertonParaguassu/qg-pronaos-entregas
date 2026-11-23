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

ASSET_V = "t1955u"

STATUE = (
    '<div id="temis-estatua">'
    '<a class="statue-acquire" href="/planos/#agente" title="Conheça o agente Têmis (Max e Ultra). Os preços aparecem depois do login.">'
    '<span class="figura-wm" aria-hidden="true"><picture>'
    '<source media="(min-width:901px)" srcset="/img/temis-720.webp?v=t1955u">'
    '<img src="/img/temis-420.webp?v=t1955u" width="420" height="804" alt="" decoding="async" aria-hidden="true">'
    '</picture></span>'
    '<span class="figura"><picture>'
    '<source media="(min-width:901px)" srcset="/img/temis-720.webp?v=t1955u">'
    '<img src="/img/temis-420.webp?v=t1955u" width="420" height="804" '
    'alt="Estátua dourada de Têmis, deusa da justiça, com os olhos vendados, a espada e a balança. Toque para conhecer o agente Têmis." '
    'decoding="async">'
    '</picture></span>'
    '</a></div>'
)

SELO = (
    '<img class="brand-rosto" src="/img/temis-balanca-96.webp" '
    'srcset="/img/temis-balanca-96.webp 2x, /img/temis-balanca-192.webp 4x" '
    'width="40" height="40" alt="" aria-hidden="true" decoding="async">'
)

CSS = """
/* aquisicao_pos t1955u: estátua fixa fora do fluxo, selo-balança, CTAs, lightbox */
#temis-estatua{position:fixed;z-index:0;right:0;bottom:0;top:auto;left:auto;width:min(42vw,28rem);height:min(92vh,58rem);margin:0;padding:0;pointer-events:none}
#temis-estatua a.statue-acquire{display:block;position:relative;width:100%;height:100%;color:inherit;text-decoration:none;pointer-events:auto}
#temis-estatua .figura,#temis-estatua .figura-wm{position:absolute;inset:0;display:block}
#temis-estatua img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;object-position:bottom right;display:block;border:0}
#temis-estatua .figura{z-index:1;filter:drop-shadow(0 30px 60px rgba(0,0,0,.45))}
#temis-estatua .figura-wm{z-index:0;opacity:.28;mix-blend-mode:soft-light;pointer-events:none}
.statue-acquire:focus-visible{outline:2px solid #E0C078;outline-offset:4px}
@media(max-width:900px){
  /* um pouco mais acima, marca d'água atrás do texto; não reserva coluna */
  #temis-estatua{width:min(62vw,16rem);height:min(62vh,28rem);bottom:8.2rem;right:-0.4rem}
  #temis-estatua .figura{opacity:.36;filter:drop-shadow(0 16px 32px rgba(0,0,0,.3))}
  #temis-estatua .figura-wm{opacity:.22}
}
@media(prefers-reduced-motion:reduce){
  #temis-estatua .figura{opacity:.55;clip-path:none!important;-webkit-clip-path:none!important}
  #temis-estatua .figura-wm{opacity:.2}
}
/* o texto do hero nunca é empurrado pela estátua (ela está fora do fluxo) */
.hero-os .hero-in,.hero-page .hero-in,.hero .hero-in{align-items:start!important;grid-template-columns:1fr!important}
.hero .hero-copy,.hero-page .hero-copy,.hero-os .hero-copy{position:relative;z-index:3}
@media(min-width:901px){
  .hero .hero-copy,.hero-page .hero-copy,.hero-os .hero-copy{max-width:calc(100% - min(42vw,28rem) - 1.25rem)}
}
@media(max-width:900px){
  /* texto em largura total, mesma tipografia das outras páginas; estátua por baixo */
  .hero .hero-copy,.hero-page .hero-copy,.hero-os .hero-copy{max-width:none}
  .hero .hero-copy h1,.hero-os .hero-copy h1,.hero-page .hero-copy h1,
  .hero .hero-copy .lead,.hero-os .hero-copy .lead,
  .hero .hero-copy p{text-shadow:0 1px 10px #0B1A33,0 0 18px #06101F}
  .hero .cta-duo,.hero .selo-ficcao,.cta-duo{position:relative;z-index:3}
  .hero a.btn,.hero a.btn-ghost,.cta-duo a.btn,.cta-duo a.btn-ghost{position:relative;z-index:4;isolation:isolate}
  a.btn-ghost,.btn-ghost{background-color:#0B1A33}
}
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
/* lightbox das capturas de produto */
#temis-lupa{display:none;position:fixed;inset:0;z-index:90;background:rgba(6,13,27,.92);align-items:center;justify-content:center;padding:1rem}
#temis-lupa.is-on{display:flex}
#temis-lupa img{max-width:100%;max-height:calc(100vh - 5rem);object-fit:contain;border:1px solid rgba(224,192,120,.45);border-radius:8px;background:#0B1A33}
#temis-lupa p{position:absolute;left:1rem;right:4rem;bottom:.7rem;margin:0;color:#E0C078;font:500 .85rem/1.35 var(--sans,inherit)}
#temis-lupa button{position:absolute;top:.7rem;right:.7rem;background:transparent;border:1px solid #E0C078;color:#E0C078;border-radius:999px;width:2.2rem;height:2.2rem;font-size:1.2rem;cursor:pointer}
.shot, figure.shot, a[data-lightbox], img[data-lightbox]{cursor:zoom-in}
"""


JS_STICKY = """
(function(){
  var bar=document.querySelector('.cta-sticky');
  if(bar){
    var hero=document.querySelector('.hero');
    function tick(){
      var on=false;
      if(hero){var r=hero.getBoundingClientRect(); on=r.bottom>80}
      document.body.classList.toggle('hero-visible', on);
    }
    tick();
    window.addEventListener('scroll', tick, {passive:true});
    window.addEventListener('resize', tick, {passive:true});
  }
})();
(function(){
  var root=document.getElementById('temis-estatua');
  if(!root) return;
  var fig=root.querySelector('.figura');
  if(!fig) return;
  var reduced=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function inter(a,b){
    var x=Math.max(a.left,b.left), y=Math.max(a.top,b.top);
    var r=Math.min(a.right,b.right), bot=Math.min(a.bottom,b.bottom);
    if(r-x<4||bot-y<4) return null;
    return {x:x,y:y,w:r-x,h:bot-y};
  }
  function tick(){
    if(reduced){ fig.style.clipPath=''; fig.style.webkitClipPath=''; fig.style.opacity='0.55'; return; }
    var st=fig.getBoundingClientRect();
    if(st.width<2||st.height<2) return;
    var holes=[], nodes=document.querySelectorAll('header.top, footer, .cta-sticky, .hero .cta-duo, .hero a.btn, .hero a.btn-ghost, .cta-duo, main a.btn, main a.btn-ghost, main .card, main article, main .mini, main .shot, main .apps-grid > *, main .grid > a, main .ficha, main .cta-nudge, main .lab, main table, main .bande, main .doc-paper, main .minuta-box, main .alerta-box, main .check-lab, main .docs-lista');
    for(var i=0;i<nodes.length;i++){
      var r=nodes[i].getBoundingClientRect();
      var h=inter(st,r);
      if(h) holes.push(h);
    }
    var p=['evenodd','0% 0%','100% 0%','100% 100%','0% 100%','0% 0%'];
    holes.forEach(function(h){
      var x1=((h.x-st.left)/st.width*100).toFixed(2);
      var y1=((h.y-st.top)/st.height*100).toFixed(2);
      var x2=(((h.x+h.w)-st.left)/st.width*100).toFixed(2);
      var y2=(((h.y+h.h)-st.top)/st.height*100).toFixed(2);
      p.push(x1+'% '+y1+'%', x2+'% '+y1+'%', x2+'% '+y2+'%', x1+'% '+y2+'%', x1+'% '+y1+'%');
    });
    var val='polygon('+p.join(',')+')';
    fig.style.clipPath=val; fig.style.webkitClipPath=val;
    var ac=root.querySelector('a.statue-acquire');
    if(ac){ ac.style.clipPath=val; ac.style.webkitClipPath=val; }
  }
  var to=false;
  function ask(){ if(to) return; to=true; requestAnimationFrame(function(){ tick(); to=false; }); }
  if(document.readyState==='complete') tick(); else window.addEventListener('load', tick);
  window.addEventListener('scroll', ask, {passive:true});
  window.addEventListener('resize', ask, {passive:true});
})();
(function(){
  var box=document.getElementById('temis-lupa');
  if(!box){
    box=document.createElement('div');
    box.id='temis-lupa';
    box.setAttribute('role','dialog');
    box.setAttribute('aria-modal','true');
    box.innerHTML='<button type="button" aria-label="Fechar">×</button><img alt=""><p></p>';
    document.body.appendChild(box);
  }
  var img=box.querySelector('img'), cap=box.querySelector('p'), btn=box.querySelector('button');
  function close(){ box.classList.remove('is-on'); img.removeAttribute('src'); }
  function open(src, text){
    img.src=src; img.alt=text||''; cap.textContent=text||'';
    box.classList.add('is-on'); btn.focus();
  }
  document.addEventListener('click', function(ev){
    var t=ev.target.closest('img[data-lightbox], a[data-lightbox], .shot img, figure.shot img');
    if(!t) return;
    if(t.closest('#temis-estatua')) return;
    ev.preventDefault();
    var el=t.tagName==='A'?t:t.closest('a[data-lightbox]')||t;
    var src=el.getAttribute('href')||el.getAttribute('src')||(el.querySelector&&el.querySelector('img')&&el.querySelector('img').src);
    if(el.tagName==='IMG') src=el.currentSrc||el.src;
    var text=el.getAttribute('data-caption')||el.getAttribute('alt')||(el.querySelector&&el.querySelector('figcaption')&&el.querySelector('figcaption').textContent)||'';
    if(src) open(src, text.trim());
  });
  btn.addEventListener('click', close);
  box.addEventListener('click', function(ev){ if(ev.target===box) close(); });
  document.addEventListener('keydown', function(ev){ if(ev.key==='Escape'&&box.classList.contains('is-on')) close(); });
})();
"""


STICKY = (
    '<div class="cta-sticky" role="navigation" aria-label="Começar">'
    '<a class="btn" href="/conta/cadastro">Teste grátis</a>'
    '<a class="btn btn-ghost" href="/planos/#agente">Quero o agente</a>'
    '</div>'
)


def inject_css(head: str) -> str:
    if "aquisicao_pos t1951u" in head:
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


def _strip_inflow_slots(h: str) -> str:
    """Remove estátua no fluxo (hero grid) para ela não empurrar o texto."""
    while True:
        i = h.find('<div class="statue-slot"')
        if i < 0:
            j = h.find('class="statue-slot"')
            if j < 0:
                break
            i = h.rfind("<", 0, j)
        # balanced div
        pos, depth = i, 0
        k = i
        while k < len(h):
            if h.startswith("<div", k):
                depth += 1
                k += 4
            elif h.startswith("</div>", k):
                depth -= 1
                k += 6
                if depth == 0:
                    h = h[:pos] + h[k:]
                    break
            else:
                k += 1
        else:
            break
    h = re.sub(r'<figure class="hero-shot">.*?</figure>', "", h, count=1, flags=re.S)
    return h


def restore_statue_home() -> None:
    """Estátua fixa à direita em TODAS as páginas, fora do fluxo."""
    for p in OUT.rglob("*.html"):
        h = p.read_text()
        h = _strip_inflow_slots(h)
        if 'id="temis-estatua"' not in h and "</body>" in h:
            h = h.replace("</body>", STATUE + "</body>", 1)
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
        h2 = h2.replace('href="/favicon.svg"', 'href="/favicon.svg?v=t1955u"')
        h2 = h2.replace('href="/favicon.ico"', 'href="/favicon.ico?v=t1955u"')
        h2 = h2.replace('href="/favicon-32.png"', 'href="/favicon-32.png?v=t1955u"')
        h2 = h2.replace('href="/apple-touch-icon.png"', 'href="/apple-touch-icon.png?v=t1955u"')
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
        if "aquisicao_pos t1951u" in s:
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
    print(f"[aquisicao_pos] ok: {n} html; selo-balança cache-bust; estátua fixa em todas; lightbox; CTAs")


if __name__ == "__main__":
    main()
