#!/usr/bin/env python3
"""Laboratório interativo (t1950u/t1951u).
- Checklist com âncoras que saltam e destacam o trecho correspondente da amostra.
- Minuta completa (saída real do kit certificado em 22/11/2026) em visor com barra de rolagem visível, arraste e tela cheia.
- Citações [DOC n] abrem o documento sintético citado.
- laudos.pdf para baixar (o PDF gerado no mesmo teste).
- Capturas de interface enganosas (processando preso, kit do agente rotulado como Profissional, rastro cru no chat) são removidas.
- Peças mantidas (1ª página da minuta e do laudos.pdf) ganham rótulo honesto e lupa (o lightbox global vem do aquisicao_pos).
- Capturas honestas da plataforma (Profissional e Ultra, sessão sintética 23/11/2026), com lupa e rótulo de plano (t1957u).
Roda depois de aquisicao_pos e privacidade_pos. Rollback: apagar a linha no build.sh.
"""
from __future__ import annotations
import base64, html, io, re, sys, tarfile
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
HERE = Path(__file__).resolve().parent
E = html.escape
MARCA = "<!--lab-t1951u-->"
V = "t1951u"

DOCS = [
    (1, "Documento de identidade (RG/CNH)", "IMG_0001.jpg"),
    (2, "Comprovante de residência", "IMG_0002.jpg"),
    (3, "CNIS (extrato previdenciário)", "IMG_0003.jpg"),
    (4, "Comunicação de decisão do INSS", "IMG_0004.jpg"),
    (5, "Laudo / atestado / relatório médico", "IMG_0005.jpg"),
    (6, "Laudo / atestado / relatório médico", "IMG_0006.jpg"),
    (7, "Laudo / atestado / relatório médico", "IMG_0007.jpg"),
    (8, "Exame (imagem/laboratório)", "IMG_0008.jpg"),
]

ARTIGOS = [
    ("art. 99, § 3º, do CPC", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"),
    ("art. 98, do CPC", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"),
    ("art. 109, I, da CF", "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"),
    ("art. 3, da Lei 10.259/2001", "https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10259.htm"),
    ("art. 201, I, da CF", "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"),
    ("art. 59, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 60, § 1º, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 15, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 25, I, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 26, II, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 151, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 42, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 62, da Lei 8.213/1991", "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm"),
    ("art. 300, do CPC", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"),
    ("art. 12, da Lei 10.259/2001", "https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10259.htm"),
    ("art. 3, da EC 113/2021", "https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc113.htm"),
    ("art. 292, § 1º, do CPC", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm"),
]

CHECK_OK = [
    ("minuta-aviso", "Aviso de minuta para revisão na 1ª linha"),
    ("docs-lista", "Documentos: identidade, comprovante de residência, CNIS, decisão do INSS, laudos"),
    ("campos-minuta", "Campos: nome, CPF, endereço, cidade/UF, DER, NB, CIDs, data do laudo"),
    ("artigos-17", "Artigos conferidos no texto oficial (17/17)"),
    ("citas-doc", "Toda citação [DOC n] aponta para documento existente"),
    ("laudos-pdf", "laudos.pdf montado"),
]
CHECK_GAP = [
    ("alerta-cpf", "Divergência de CPF entre documentos (123.456.789-09 × 123.456.739-09) — o revisor pediu confirmação; é um número fictício"),
    ("alerta-uf", "Divergência de cidade/UF (Contagem-MG × Belo Horizonte-MG)"),
    ("alerta-laudo", "Divergência de data do laudo mais recente e de CRM entre laudos"),
    ("alerta-protetora", "Protetora Leal: conferir linguagem antes do protocolo"),
    ("pendentes", "Perguntas à advogada: estado civil, profissão, valor da causa (ainda não calculado automaticamente)"),
]

CSS = f"""
/* laboratorio_pos {V} */
.minuta-box{{position:relative;border:1px solid rgba(224,192,120,.45);border-radius:16px;background:rgba(6,16,34,.88);overflow:hidden}}
.minuta-toolbar{{display:flex;flex-wrap:wrap;gap:.6rem;align-items:center;justify-content:space-between;padding:.65rem .9rem;border-bottom:1px solid rgba(224,192,120,.28);background:rgba(11,26,51,.95)}}
.minuta-toolbar strong{{color:var(--gold-s);font:600 .82rem/1.3 var(--sans);letter-spacing:.04em;text-transform:uppercase}}
.minuta-toolbar .btns{{display:flex;flex-wrap:wrap;gap:.45rem}}
.minuta-toolbar a,.minuta-toolbar button{{appearance:none;background:transparent;color:var(--gold-l);border:1px solid rgba(224,192,120,.55);border-radius:999px;padding:.35rem .8rem;font:600 .78rem/1.3 var(--sans);cursor:pointer;text-decoration:none}}
.minuta-toolbar a:hover,.minuta-toolbar button:hover,.minuta-toolbar a:focus-visible,.minuta-toolbar button:focus-visible{{border-color:#E0C078;outline:none}}
.minuta-viewer{{max-height:min(70vh,44rem);overflow-y:scroll;scrollbar-gutter:stable;scrollbar-width:auto;scrollbar-color:#E0C078 #0B1A33;padding:1.1rem 1.2rem 1.4rem;color:var(--head);font:400 .95rem/1.65 var(--serif);white-space:pre-wrap}}
.minuta-viewer::-webkit-scrollbar{{width:14px}}
.minuta-viewer::-webkit-scrollbar-track{{background:#0B1A33}}
.minuta-viewer::-webkit-scrollbar-thumb{{background:#E0C078;border-radius:8px;border:2px solid #0B1A33}}
.minuta-box.is-full{{position:fixed;inset:.6rem;z-index:80;max-width:none;border-radius:12px;box-shadow:0 20px 80px #000a}}
.minuta-box.is-full .minuta-viewer{{max-height:calc(100vh - 5.2rem)}}
body.lab-full{{overflow:hidden}}
a.cit-doc{{color:var(--gold-l);font-weight:600;text-decoration:underline;text-underline-offset:2px}}
#minuta-aviso,#campos-minuta,#citas-doc,#pendentes,.is-hl{{scroll-margin-top:5.5rem}}
.is-hl{{outline:2px solid #E0C078;background:rgba(224,192,120,.18);border-radius:6px;animation:lab-hl 2.2s ease}}
@keyframes lab-hl{{from{{background:rgba(224,192,120,.4)}}to{{background:rgba(224,192,120,.18)}}}}
@media (prefers-reduced-motion:reduce){{@keyframes lab-hl{{from{{background:rgba(224,192,120,.18)}}to{{background:rgba(224,192,120,.18)}}}}}}
.check-lab a{{color:inherit;text-decoration:none;flex:1}}
.check-lab a:hover,.check-lab a:focus-visible{{color:var(--gold-l);text-decoration:underline}}
.docs-lista{{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:.7rem;margin:0 0 1rem}}
.docs-lista a{{display:block;border:1px solid rgba(224,192,120,.35);border-radius:12px;overflow:hidden;background:rgba(6,16,34,.8);color:inherit;text-decoration:none;font:500 .75rem/1.3 var(--sans)}}
.docs-lista a:hover,.docs-lista a:focus-visible{{border-color:#E0C078}}
.docs-lista img{{display:block;width:100%;height:110px;object-fit:cover;object-position:top;background:#0B1A33}}
.docs-lista span{{display:block;padding:.45rem .5rem .55rem;color:var(--ink-2)}}
.art-list{{display:grid;gap:.35rem;margin:.4rem 0 1rem;padding:0;list-style:none}}
.art-list li{{padding:.35rem .6rem;border-left:2px solid rgba(224,192,120,.5)}}
.art-list a{{color:var(--gold-l)}}
.rotulo-print{{display:block;margin:0;padding:.45rem .8rem 0;color:var(--gold-s);font:600 .72rem/1.3 var(--sans);letter-spacing:.04em;text-transform:uppercase}}
.alerta-box{{margin:1rem 0;padding:.8rem 1rem;border-left:3px solid #E8C4A0;background:rgba(42,21,16,.45);border-radius:0 12px 12px 0}}
.alerta-box p{{margin:.2rem 0}}
.cta-visor{{margin:1.1rem 0 0}}
"""

JS = r"""
(function(){
  function $(s,c){return (c||document).querySelector(s)}
  function $$(s,c){return [].slice.call((c||document).querySelectorAll(s))}
  function hl(el){
    if(!el) return;
    $$('.is-hl').forEach(function(n){n.classList.remove('is-hl')});
    el.classList.add('is-hl');
    var box=$('.minuta-viewer');
    if(box && box.contains(el)){
      var top=el.offsetTop - 24;
      box.scrollTo({top:Math.max(0,top), behavior: (window.matchMedia('(prefers-reduced-motion: reduce)').matches)?'auto':'smooth'});
    }
    el.scrollIntoView({block:'center', behavior: (window.matchMedia('(prefers-reduced-motion: reduce)').matches)?'auto':'smooth'});
  }
  $$('a[data-lab-jump]').forEach(function(a){
    a.addEventListener('click', function(ev){
      var id=a.getAttribute('href')||'';
      if(id.charAt(0)!=='#') return;
      var el=document.getElementById(id.slice(1));
      if(!el) return;
      ev.preventDefault();
      hl(el);
      try{history.replaceState(null,'',id)}catch(e){}
    });
  });
  var box=$('#minuta-box'), btn=$('#minuta-cheia'), viewer=$('.minuta-viewer');
  function cheia(on){
    if(!box) return;
    box.classList.toggle('is-full', !!on);
    document.body.classList.toggle('lab-full', !!on);
    if(btn) btn.textContent=on?'Sair da tela cheia':'Tela cheia';
    if(on && viewer) viewer.focus();
  }
  if(btn) btn.addEventListener('click', function(){ cheia(!box.classList.contains('is-full')); });
  document.addEventListener('keydown', function(ev){
    if(ev.key==='Escape' && box && box.classList.contains('is-full')) cheia(false);
  });
  if(location.hash){
    var t=document.getElementById(location.hash.slice(1));
    if(t) setTimeout(function(){hl(t)}, 200);
  }
})();
"""


def unpack_docs() -> None:
    dest = OUT / "laboratorio"
    dest.mkdir(parents=True, exist_ok=True)
    packed = HERE / "laboratorio_docs.tgz.b64"
    if not packed.is_file():
        print("[laboratorio_pos] aviso: laboratorio_docs.tgz.b64 ausente")
        return
    raw = base64.b64decode("".join(packed.read_text().split()))
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        tf.extractall(dest)
    img = OUT / "img" / "laboratorio"
    img.mkdir(parents=True, exist_ok=True)
    docs = dest / "docs"
    if docs.is_dir():
        for sp in docs.glob("doc-*.webp"):
            (img / sp.name).write_bytes(sp.read_bytes())


def minuta_html() -> str:
    p = OUT / "laboratorio" / "minuta.txt"
    raw = p.read_text(encoding="utf-8") if p.exists() else ""
    raw = raw.replace("\x0c", "\n").strip()
    text = E(raw)
    # first line aviso
    text, n = re.subn(
        r"MINUTA PARA REVISÃO DA ADVOGADA[^\n]*\n(?:\s*HUMANA)?",
        lambda m: f'<span id="minuta-aviso">{m.group(0)}</span>',
        text,
        count=1,
    )
    # [DOC n] and [DOC 5, 6, 7]
    def cit(m):
        inner = m.group(1)
        nums = re.findall(r"\d+", inner)
        parts = []
        for i, num in enumerate(nums):
            parts.append(f'<a class="cit-doc" href="/laboratorio/docs/doc-{num}.webp" data-lightbox data-caption="DOC {num}" data-doc="{num}">DOC {num}</a>')
        return "[" + ", ".join(parts) + "]"
    text = re.sub(r"\[DOC ([0-9, ]+)\]", cit, text)
    # campos block (preamble with name/cpf/address) — wrap first occurrence of the long name+cpf line
    text = text.replace(
        "Maria Aparecida Ficticia dos Santos",
        '<span id="campos-minuta">Maria Aparecida Ficticia dos Santos</span>',
        1,
    )
    # first [DOC after campos already linked; add citas-doc near first citation
    text = text.replace(
        '<a class="cit-doc" href="/laboratorio/docs/doc-1.webp"',
        '<span id="citas-doc"></span><a class="cit-doc" href="/laboratorio/docs/doc-1.webp"',
        1,
    )
    text = text.replace("[PENDENTE:", '<span id="pendentes" class="pendente">[PENDENTE:', 1)
    text = text.replace("123.456.789-09", '<mark id="cpf-minuta" class="cpf-a">123.456.789-09</mark>', 1)
    return text


def pecas_html() -> str:
    docs = "".join(
        f'<a id="doc-{n}" href="/laboratorio/docs/doc-{n}.webp" data-lightbox '
        f'data-caption="DOC {n} · {E(nome)} (arquivo sintético {arq})">'
        f'<img src="/img/laboratorio/doc-{n}.webp?v={V}" alt="DOC {n}: {E(nome)}, documento sintético do teste" width="280" height="200" loading="lazy" decoding="async">'
        f"<span>DOC {n} · {E(nome)}</span></a>"
        for n, nome, arq in DOCS
    )
    arts = "".join(
        f'<li><a href="{E(url)}" rel="noopener" target="_blank">{E(cit)}</a></li>'
        for cit, url in ARTIGOS
    )
    oks = "".join(
        f'<li><span class="ok" aria-hidden="true">✓</span>'
        f'<a href="#{anc}" data-lab-jump>{E(txt)}</a></li>'
        for anc, txt in CHECK_OK
    )
    gaps = "".join(
        f'<li><span class="falta" aria-hidden="true">!</span>'
        f'<a href="#{anc}" data-lab-jump>{E(txt)}</a></li>'
        for anc, txt in CHECK_GAP
    )
    minuta = minuta_html()
    return f'''
<section class="sec" id="pecas">{MARCA}
<div class="wrap">
<div class="sec-head"><h2>As peças que o kit entregou</h2>
<p class="lead">Minuta completa, laudos.pdf e o checklist do mesmo teste certificado de 22/11/2026, com dados 100% sintéticos. Cada item do checklist salta para o trecho correspondente. As citações [DOC n] abrem o documento citado. Isto não é um processo real e não é um acesso aberto à plataforma.</p>
<p class="selo-ficcao">Exemplo com dados fictícios · kit de petição inicial</p>
</div>

<p class="eyebrow" id="docs-lista">Documentos do caso (sintéticos)</p>
<div class="docs-lista">{docs}</div>

<div class="minuta-box" id="minuta-box">
  <div class="minuta-toolbar">
    <strong>Minuta da petição inicial · texto integral gerado no teste</strong>
    <div class="btns">
      <a href="/laboratorio/minuta-peticao-inicial.pdf">Baixar o PDF da minuta</a>
      <button type="button" id="minuta-cheia">Tela cheia</button>
    </div>
  </div>
  <div class="minuta-viewer" tabindex="0" role="region" aria-label="Minuta completa, role para ler o texto">{minuta}</div>
</div>
<div class="cta-duo cta-visor">
  <a class="btn" href="/conta/cadastro">Começar o teste grátis</a>
  <a class="btn btn-ghost" href="/tarefas/peticao-inicial/">Quero um kit assim no meu caso</a>
</div>
<p class="fine">Toda peça é minuta para revisão. A Têmis não protocola, não assina e não se apresenta perante o juízo. Os preços aparecem depois do login.</p>

<div class="lab-docs" style="margin-top:1.4rem">
<div>
<p class="eyebrow">Primeira página da minuta (PDF gerado)</p>
<figure class="shot"><span class="rotulo-print">Kit de petição inicial · teste certificado 22/11/2026 · dados fictícios</span>
<img src="/img/laboratorio/peticao-1.webp?v={V}" alt="Primeira página da minuta da petição inicial gerada no kit certificado de 22/11/2026, com dados fictícios" loading="lazy" decoding="async" data-lightbox>
<figcaption>Primeira página do PDF da minuta. O visor acima tem o texto integral; clique na imagem para ampliar.</figcaption></figure>
</div>
<div>
<p class="eyebrow" id="laudos-pdf">laudos.pdf montado</p>
<figure class="shot"><span class="rotulo-print">Kit de petição inicial · laudos.pdf · teste 22/11/2026 · dados fictícios</span>
<img src="/img/laboratorio/laudos-1.webp?v={V}" alt="Primeira página do laudos.pdf montado no kit certificado, com laudo sintético" loading="lazy" decoding="async" data-lightbox>
<figcaption>Primeira página do laudos.pdf gerado a partir das imagens sintéticas. <a href="/laboratorio/laudos.pdf">Baixar o laudos.pdf completo</a>.</figcaption></figure>
</div>
</div>

<div id="artigos-17">
<p class="eyebrow">Artigos conferidos no texto oficial (17/17)</p>
<p class="fine">No mesmo teste, a Têmis conferiu estas 17 citações no texto oficial do Planalto. Os links abaixo são os mesmos endereços usados na conferência.</p>
<ul class="art-list">{arts}</ul>
</div>

<h3>Checklist do kit</h3>
<ul class="check-lab">{oks}{gaps}</ul>
<p class="fine">Toque um item para ir ao trecho correspondente. O revisor local apontou divergências e deixou a confirmação para a advogada — foi assim no teste, com números fictícios.</p>

<div class="alerta-box">
<p id="alerta-cpf"><strong>CPF.</strong> A minuta usa 123.456.789-09; outro documento do lote trouxe 123.456.739-09. O revisor pediu confirmação. São números fictícios.</p>
<p id="alerta-uf"><strong>Cidade/UF.</strong> A minuta está em Contagem-MG; um documento trouxe Belo Horizonte-MG.</p>
<p id="alerta-laudo"><strong>Laudos.</strong> A minuta tomou o laudo de 05/09/2026 (Dr. Carlos Exemplo Ficticio, CRM-MG 99999). Há também laudos de 20/03/2026 e 10/06/2026, com CRM-MG 88888, 77777 e 66666. O revisor pediu para confirmar a data e o médico.</p>
<p id="alerta-protetora"><strong>Protetora Leal.</strong> Conferir a linguagem antes do protocolo (sem promessa de resultado).</p>
<p id="pendente-nota">As lacunas <a href="#pendentes" data-lab-jump>[PENDENTE]</a> na minuta (estado civil, profissão, nome e OAB da advogada, valor da causa, DCB) ficam para a advogada preencher.</p>
</div>

<p class="fine" style="margin-top:1.2rem">Fonte: certificação de 22/11/2026 com dados 100% sintéticos. O valor da causa ainda não é calculado automaticamente. O modelo local às vezes erra interpretação; por isso a peça é montada com regras e sai sempre como minuta.</p>
<div class="cta-duo">
<a class="btn" href="/conta/cadastro">Começar o teste grátis</a>
<a class="btn btn-ghost" href="/tarefas/peticao-inicial/">Tarefa: petição inicial</a>
</div>
</div></section>
'''


def rewrite_lab() -> None:
    p = OUT / "laboratorio" / "index.html"
    if not p.exists():
        print("[laboratorio_pos] aviso: laboratorio/index.html ausente")
        return
    s = p.read_text(encoding="utf-8")
    if MARCA in s:
        return
    # drop misleading UI shots (upload stuck, kit labeled profissional + agent, raw chat)
    s = re.sub(
        r'<section class="sec">\s*<div class="wrap">\s*<div class="sec-head"><h2>O caso</h2>.*?</section>',
        '''<section class="sec"><div class="wrap">
<div class="sec-head"><h2>O caso</h2>
<p class="lead">Pedido de benefício por incapacidade contra o INSS, em nome de Maria Aparecida Ficticia dos Santos, com carta de indeferimento, CNIS e laudos fictícios. Tempo até o estado «aguardando a advogada»: cerca de 104 segundos no teste certificado. 17 artigos conferidos no texto oficial do Planalto.</p>
<p class="fine">As capturas antigas da interface (envio com arquivos «processando», o kit aberto com o botão do agente num escritório rotulado como Profissional, e o chat com o rastro interno das ferramentas) foram retiradas: não representavam com honestidade o que a pessoa vê hoje, no plano certo, com o trabalho concluído. Abaixo está a saída real do kit — minuta, documentos, checklist e o laudos.pdf.</p>
</div></div></section>''',
        s,
        count=1,
        flags=re.S,
    )
    pecas = pecas_html()
    s2, n = re.subn(
        r'<section class="sec">\s*<div class="wrap">\s*<div class="sec-head"><h2>As peças que o kit entregou</h2>.*?</section>',
        pecas,
        s,
        count=1,
        flags=re.S,
    )
    if n == 0:
        print("[laboratorio_pos] aviso: bloco das peças não encontrado")
        s2 = s
    # CSS
    if f"laboratorio_pos {V}" not in s2:
        if "</style>" in s2:
            s2 = s2.replace("</style>", CSS + "</style>", 1)
        else:
            s2 = s2.replace("</head>", f"<style>{CSS}</style></head>", 1)
    if "minuta-cheia" in s2 and "data-lab-jump" in s2 and JS.strip()[:20] not in s2:
        s2 = s2.replace("</body>", "<script>" + JS + "</script></body>", 1)
    # home: if it still features ui_upload/ui_mente as product shots, leave to a later pass — handled below
    p.write_text(s2, encoding="utf-8")


def patch_home_shots() -> None:
    """Home also shows ui_kit and ui_mente — drop misleading ones, keep a link to the lab."""
    p = OUT / "index.html"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    if "lab-shots-t1951u" in s:
        return
    # replace the two lab product images block if present
    if 'src="/img/laboratorio/ui_upload.webp"' in s or 'src="/img/laboratorio/ui_kit.webp"' in s or 'src="/img/laboratorio/ui_mente.webp"' in s:
        s = re.sub(r'src="/img/laboratorio/ui_upload\.webp"[^>]*>', f'src="/img/laboratorio/peticao-1.webp?v={V}" alt="Primeira página da minuta da petição inicial gerada no kit certificado, dados fictícios" loading="lazy" decoding="async" data-lightbox>', s, count=1)
        s = re.sub(r'src="/img/laboratorio/ui_kit\.webp"[^>]*>', f'src="/img/laboratorio/laudos-1.webp?v={V}" alt="Primeira página do laudos.pdf montado no kit certificado, dados fictícios" loading="lazy" decoding="async" data-lightbox>', s, count=1)
        s = re.sub(
            r'<figure class="shot">\s*<img src="/img/laboratorio/ui_mente\.webp".*?</figure>',
            "",
            s,
            count=1,
            flags=re.S,
        )
        # captions that still describe upload/chat/kit UI
        s = s.replace(
            "Painel do kit da inicial com oito documentos sintéticos classificados e o agente aguardando a advogada",
            "Primeira página da minuta gerada no kit certificado de 22/11/2026, com dados fictícios",
        )
        s = s.replace(
            "Chat da Têmis listando laudos sintéticos, CIDs e a conferência do art. 42 da Lei 8.213/91 no Planalto",
            "Primeira página do laudos.pdf montado no mesmo teste, com dados fictícios",
        )
        s = s.replace("<!--lab-shots-t1951u-->", "")
        # mark once
        s = s.replace("<main", "<!--lab-shots-t1951u--><main", 1)
        p.write_text(s, encoding="utf-8")


PLAT_V = "t1957u"
PLAT_MARCA = "<!--plat-shots-t1957u-->"
PLAT_SHOTS = [
    ("profissional_painel_desktop.webp", "Plano Profissional · painel",
     "Painel no Têmis Profissional, sessão sintética de 23/11/2026. O Kit da inicial com o agente e o Pedir à Têmis aparecem como convite para o Max e o Ultra."),
    ("profissional_caso_desktop.webp", "Plano Profissional · caso",
     "Caso sintético no Têmis Profissional, 23/11/2026: documentos e minutas do teste, com Conversa rápida e Gerar minuta. O agente permanece no Max e no Ultra."),
    ("profissional_facetas_desktop.webp", "Plano Profissional · Facetas da Têmis",
     "Lista das facetas no Têmis Profissional, sessão sintética de 23/11/2026."),
    ("ultra_painel_desktop.webp", "Plano Ultra · painel",
     "Painel no Têmis Ultra, sessão sintética de 23/11/2026, com o Kit da inicial (agente), Pedir à Têmis e o Conselho das 4."),
    ("ultra_kit_desktop.webp", "Plano Ultra · Kit da inicial (agente)",
     "Kit da inicial no Têmis Ultra, sessão sintética de 23/11/2026, ainda sem o agente ter rodado. O Conselho das 4 neste caso é opt-in."),
    ("ultra_facetas_desktop.webp", "Plano Ultra · Facetas da Têmis",
     "Lista das facetas no Têmis Ultra, sessão sintética de 23/11/2026."),
]
PLAT_CSS = """
/* laboratorio_pos plataforma t1957u */
.plat-shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.1rem;margin-top:1.2rem}
.plat-shots figure.shot{margin:0;background:rgba(6,16,34,.88);border:1px solid rgba(224,192,120,.35);border-radius:16px;overflow:hidden}
.plat-shots img{width:100%;height:auto;display:block;background:#0B1A33}
.plat-shots figcaption{padding:.65rem .85rem 0.9rem;color:var(--head,#e8e3d3);font:400 .86rem/1.45 var(--sans,system-ui,sans-serif)}
.hero-shot .rotulo-print{position:relative;z-index:1}
"""

def unpack_plataforma_shots() -> None:
    dest = OUT / "img" / "plataforma"
    dest.mkdir(parents=True, exist_ok=True)
    packed = HERE / "plataforma_shots.tgz.b64"
    src_dir = HERE / "img_plataforma"
    if packed.is_file():
        raw = base64.b64decode("".join(packed.read_text().split()))
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            tf.extractall(dest)
    elif src_dir.is_dir():
        for sp in src_dir.glob("*.webp"):
            (dest / sp.name).write_bytes(sp.read_bytes())
    else:
        print("[laboratorio_pos] aviso: plataforma_shots.tgz.b64 ausente")
        return
    n = len(list(dest.glob("*.webp")))
    print(f"[laboratorio_pos] capturas da plataforma: {n} webp em /img/plataforma/")


def _fig(src, rotulo, caption) -> str:
    return (
        f'<figure class="shot">{PLAT_MARCA}'
        f'<span class="rotulo-print">{E(rotulo)}</span>'
        f'<img src="/img/plataforma/{src}?v={PLAT_V}" alt="{E(rotulo)}. {E(caption)}" '
        f'width="1440" height="900" loading="lazy" decoding="async" data-lightbox '
        f'data-caption="{E(rotulo)}">'
        f'<figcaption>{E(caption)}</figcaption></figure>'
    )


def plataforma_section() -> str:
    figs = [_fig(n, r, c) for n, r, c in PLAT_SHOTS]
    return (
        f'<section class="sec" id="plataforma-planos">{PLAT_MARCA}\n'
        f'<div class="wrap">\n'
        f'<div class="sec-head">\n'
        f'<p class="eyebrow">A plataforma</p>\n'
        f'<h2>Profissional e Ultra, como aparecem de verdade</h2>\n'
        f'<p class="lead">Capturas de 23/11/2026 em sessões sintéticas (nenhum processo real). Clique para ampliar. O Kit da inicial com o agente Têmis entra no Têmis Max e no Têmis Ultra; no Profissional ele aparece travado, com convite para subir de degrau.</p>\n'
        f'<p class="selo-ficcao">Sessão sintética · rótulo de plano em cada captura</p>\n'
        f'</div>\n<div class="plat-shots">\n{"".join(figs)}\n</div>\n</div></section>\n'
    )


def _inject_plat_css(s: str) -> str:
    if "laboratorio_pos plataforma t1957u" in s:
        return s
    css = "<style>" + PLAT_CSS + "</style>"
    if "</head>" in s:
        return s.replace("</head>", css + "</head>", 1)
    return s


def patch_plataforma_shots() -> None:
    unpack_plataforma_shots()
    lab = OUT / "laboratorio" / "index.html"
    if lab.is_file():
        s = lab.read_text(encoding="utf-8")
        if PLAT_MARCA not in s:
            bloco = plataforma_section()
            if 'id="pecas"' in s:
                s = s.replace('<section class="sec" id="pecas">', bloco + '\n<section class="sec" id="pecas">', 1)
            elif "</main>" in s:
                s = s.replace("</main>", bloco + "</main>", 1)
            s = _inject_plat_css(s)
            lab.write_text(s, encoding="utf-8")
            print("[laboratorio_pos] laboratório: bloco da plataforma por plano")
    patch_home_plataforma()


def patch_home_plataforma() -> None:
    p = OUT / "index.html"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    if "plat-shots-t1957u" in s:
        return
    s = _inject_plat_css(s)
    hero_img = (
        f'<figure class="hero-shot">{PLAT_MARCA}'
        f'<span class="rotulo-print">Plano Profissional · painel · sessão sintética 23/11/2026</span>'
        f'<img src="/img/plataforma/profissional_painel_desktop.webp?v={PLAT_V}" width="1440" height="900" '
        f'alt="Painel da Têmis no plano Profissional, sessão sintética de 23/11/2026. O Kit da inicial com o agente aparece como convite para o Max e o Ultra." '
        f'decoding="async" fetchpriority="high" data-lightbox data-caption="Plano Profissional · painel">'
        f'</figure>'
    )
    s2, nhero = re.subn(
        r'<figure class="hero-shot">.*?</figure>',
        hero_img,
        s,
        count=1,
        flags=re.S,
    )
    if nhero:
        s = s2
    figs_home = "".join([
        _fig("profissional_painel_desktop.webp", "Plano Profissional · painel",
             "No Profissional, o Kit da inicial com o agente e o Pedir à Têmis aparecem como convite para o Max e o Ultra. Conversa rápida e Gerar minuta seguem disponíveis."),
        _fig("profissional_caso_desktop.webp", "Plano Profissional · caso",
             "Caso sintético com documentos e minutas do teste, no plano Profissional, em 23/11/2026."),
        _fig("ultra_painel_desktop.webp", "Plano Ultra · painel",
             "No Ultra entram o Kit da inicial (agente), Pedir à Têmis e o Conselho das 4."),
        _fig("ultra_kit_desktop.webp", "Plano Ultra · Kit da inicial (agente)",
             "O kit no Ultra, sessão sintética de 23/11/2026, ainda sem o agente ter rodado. O Conselho das 4 neste caso é opt-in."),
    ])
    demo = (
        f'<section class="sec" id="demonstracao">{PLAT_MARCA}<div class="wrap">\n'
        f'<div class="sec-head">\n'
        f'<p class="eyebrow">Demonstração</p>\n'
        f'<h2>Veja a plataforma, não só a promessa</h2>\n'
        f'<p class="lead">Capturas de 23/11/2026 em sessões sintéticas nos planos Profissional e Ultra. Clique para ampliar. Não é um processo real e não está aberto um acesso público à plataforma.</p>\n'
        f'<p class="selo-ficcao">Sessão sintética · rótulo de plano em cada captura</p>\n'
        f'</div>\n<div class="plat-shots">\n{figs_home}\n</div>\n'
        f'<p><a class="more" href="/laboratorio/#plataforma-planos">Ver também as Facetas da Têmis, a minuta e o laudos.pdf no laboratório ›</a></p>\n'
        f'</div></section>'
    )
    s3, nd = re.subn(
        r'<section class="sec" id="demonstracao">.*?</section>',
        demo,
        s,
        count=1,
        flags=re.S,
    )
    if nd:
        s = s3
    else:
        print("[laboratorio_pos] aviso: #demonstracao não encontrado na home")
    if nhero == 0:
        print("[laboratorio_pos] aviso: hero-shot não encontrado na home")
    p.write_text(s, encoding="utf-8")
    print(f"[laboratorio_pos] home: hero={nhero} demonstracao={nd}")


def main() -> None:
    if not OUT.exists():
        sys.exit(f"saída inexistente: {OUT}")
    unpack_docs()
    rewrite_lab()
    patch_home_shots()
    patch_plataforma_shots()
    print("[laboratorio_pos] ok: laboratório interativo, peças reais, capturas honestas por plano")


if __name__ == "__main__":
    main()
