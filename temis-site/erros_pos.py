#!/usr/bin/env python3
"""Pós-processador t1965u: Relatar um problema + 404 amigável no site público.

Roda no fim do build do Render, depois dos outros pós-processadores.
- Link «Relatar um problema» no rodapé de todas as páginas
- Página /relatar/ com mensagem pronta (página, hora, código, navegador)
  enviada por formulário a /conta/publico/relatar e, se falhar, por
  mailto:temis@e-pronaos.com. Sem CPF/CNPJ.
- 404.html ganha o mesmo convite e um código de referência curto no cliente
  (só para o relato; o detalhe técnico nunca aparece).

Rollback: apagar a linha do build.sh que chama este script.
"""
from __future__ import annotations

import html as htmllib
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
SITE = "https://agentetemis.com"
E = htmllib.escape
ENDPOINT = "/conta/publico/relatar"
CONTATO = "temis@e-pronaos.com"

CSS = """
/* erros_pos t1965u: relatar um problema */
.foot-relatar{margin-top:.6rem}
a.relatar-link{color:var(--gold-l, #e3c26b)}
.form-relatar{display:grid;gap:.7rem;margin:1rem 0;max-width:36rem}
.form-relatar textarea{min-height:9rem;resize:vertical}
.form-relatar .linha{display:grid;gap:.6rem;grid-template-columns:1fr}
@media (min-width:640px){.form-relatar .linha{grid-template-columns:1fr 1fr}}
.relatar-ok{margin:0;padding:1rem 1.1rem;border-radius:12px;border:1px solid rgba(224,192,120,.45);background:rgba(6,16,34,.78);color:var(--head,#f3e7c4)}
.form-relatar.sent .campos{display:none}
.cta-relatar{margin:1.2rem 0;padding:1rem 1.1rem;border:1px solid rgba(224,192,120,.35);border-radius:14px;background:rgba(6,16,34,.55)}
.cta-relatar .ref{display:inline-block;margin:.3rem 0;padding:.15rem .7rem;border:1px solid rgba(224,192,120,.45);border-radius:999px;color:var(--gold-l,#e3c26b);font-size:.9rem}
"""

JS = r"""
/* erros_pos t1965u: relatar um problema, mensagem pronta */
(function(){
  var d=document, CFG=window.TEMIS||{};
  var contato=CFG.contato||'temis@e-pronaos.com';
  function qs(s,c){return (c||d).querySelector(s)}
  function param(n){try{return new URLSearchParams(location.search).get(n)||''}catch(e){return ''}}
  function agora(){
    try{
      return new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short',timeStyle:'short'})+' (horário de Brasília)';
    }catch(e){return new Date().toISOString()}
  }
  function nav(){return (navigator.userAgent||'').slice(0,180)}
  function refCliente(){
    var a='ABCDEFGHJKLMNPQRSTUVWXYZ23456789', s='T-';
    for(var i=0;i<6;i++) s+=a.charAt(Math.floor(Math.random()*a.length));
    return s;
  }
  function corpo(ref, pagina, quando, texto){
    return 'Olá, Equipe Têmis,\n\nGostaria de relatar um problema.\n\n'
      +'Pedido: '+(ref||'(sem código)')+'\n'
      +'Página: '+(pagina||location.href)+'\n'
      +'Quando: '+(quando||agora())+'\n'
      +'Navegador: '+nav()+'\n\n'
      +'O que aconteceu:\n'+(texto||'')+'\n\n'
      +'Não envio documentos de clientes, CPF, CNPJ nem senhas.\n';
  }
  function mailto(ref, pagina, quando, texto){
    var ass='Problema na Têmis'+(ref?(' · '+ref):'');
    return 'mailto:'+contato+'?subject='+encodeURIComponent(ass)+'&body='+encodeURIComponent(corpo(ref,pagina,quando,texto));
  }
  d.querySelectorAll('form.form-relatar').forEach(function(f){
    var st=qs('.form-status',f), btn=qs('button[type=submit]',f);
    if(!st||!btn) return;
    var paginaEl=f.elements['pagina'], quandoEl=f.elements['quando'], refEl=f.elements['ref_erro'], navEl=f.elements['navegador'], msgEl=f.elements['mensagem'];
    var ref=param('ref')||(refEl&&refEl.value)||'';
    var pagina=param('pagina')||(paginaEl&&paginaEl.value)||location.pathname;
    var quando=agora();
    if(refEl&&!refEl.value) refEl.value=ref;
    if(paginaEl) paginaEl.value=pagina;
    if(quandoEl) quandoEl.value=quando;
    if(navEl) navEl.value=nav();
    if(msgEl && !msgEl.value){
      msgEl.value='Gostaria de relatar um problema.\n\nPedido: '+(ref||'(ainda será gerado)')+'\nPágina: '+pagina+'\nQuando: '+quando+'\nNavegador: '+nav()+'\n\nO que aconteceu:\n';
    }
    var mail=qs('a.relatar-mail', f.parentNode)||qs('a.relatar-mail');
    if(mail) mail.href=mailto(ref,pagina,quando,msgEl&&msgEl.value||'');
    if(msgEl) msgEl.addEventListener('input', function(){
      if(mail) mail.href=mailto(refEl&&refEl.value||ref, pagina, quando, msgEl.value);
    });
    f.addEventListener('submit', function(ev){
      ev.preventDefault();
      st.className='form-status';
      var v=function(n){return (f.elements[n]&&f.elements[n].value||'').trim()};
      var data={
        nome:v('nome'), email:v('email'), mensagem:v('mensagem'),
        pagina:v('pagina'), quando:v('quando'), ref_erro:v('ref_erro'), navegador:v('navegador'),
        consentimento: !!(f.elements.consentimento && f.elements.consentimento.checked),
        website:v('website')
      };
      var err='';
      if(data.mensagem.length<10 || data.mensagem.length>4000) err='Escreva o que aconteceu em 10 a 4.000 caracteres.';
      else if(data.email && !/^[^\s@]{1,64}@[^\s@]{2,190}\.[a-z]{2,}$/i.test(data.email)) err='Se informar e-mail, use um endereço válido.';
      else if(!data.consentimento) err='Para enviar, confirme que leu o aviso de privacidade.';
      if(err){ st.textContent=err; st.classList.add('err'); return; }
      btn.disabled=true; st.textContent='Enviando…';
      var done=function(ticket){
        f.classList.add('sent');
        var ok=qs('.relatar-ok', f.parentNode)||qs('.relatar-ok', f);
        if(ok){
          ok.hidden=false;
          if(ticket) ok.textContent='Recebemos o seu relato. O número do pedido é '+ticket+'. Se você informou um e-mail, em breve enviamos uma confirmação.';
          try{ok.focus()}catch(e){}
        }
        st.textContent='';
      };
      var fallback=function(){
        st.innerHTML='Não conseguimos enviar agora. <a href="'+mailto(data.ref_erro,data.pagina,data.quando,data.mensagem)+'">Envie por e-mail, com a mensagem já pronta</a>.';
        st.classList.add('err'); btn.disabled=false;
      };
      var ep=CFG.endpointRelatar||'""" + ENDPOINT + r"""';
      var ctl=window.AbortController?new AbortController():null;
      var to=setTimeout(function(){ctl&&ctl.abort()},12000);
      var fd=new URLSearchParams();
      Object.keys(data).forEach(function(k){fd.append(k, data[k]==null?'':String(data[k]));});
      fetch(ep,{method:'POST',body:fd,signal:ctl&&ctl.signal,mode:'cors'})
        .then(function(r){clearTimeout(to);return r.json().catch(function(){return{}}).then(function(j){if(r.ok&&j.ok){done(j.ticket||'')}else{fallback()}})})
        .catch(function(){clearTimeout(to);fallback()});
    });
  });
  var box=qs('.cta-relatar[data-auto]');
  if(box){
    var ref=box.getAttribute('data-ref')||refCliente();
    var span=qs('.ref', box); if(span) span.textContent='Pedido '+ref;
    var a=qs('a.btn', box);
    if(a){
      var dest='/relatar/?ref='+encodeURIComponent(ref)+'&pagina='+encodeURIComponent(location.pathname);
      a.href=dest;
    }
  }
})();
"""

FORM = f"""<form class="form form-relatar" novalidate>
<div class="campos">
<label>O que aconteceu<textarea name="mensagem" rows="8" required maxlength="4000"></textarea></label>
<div class="linha">
<label>Nome (opcional)<input name="nome" autocomplete="name" maxlength="90"></label>
<label>E-mail (opcional, para recebermos e respondermos)<input name="email" type="email" autocomplete="email" maxlength="190"></label>
</div>
<input type="hidden" name="pagina"><input type="hidden" name="quando"><input type="hidden" name="ref_erro"><input type="hidden" name="navegador">
<label class="hp" aria-hidden="true">Deixe em branco<input name="website" tabindex="-1" autocomplete="off"></label>
<label class="check"><input type="checkbox" name="consentimento"> Li o aviso: se eu informar nome ou e-mail, eles serão usados só para entender e responder este relato, conforme a <a href="/privacidade/">política de privacidade</a>. Sem nome e e-mail, o relato é anônimo. Não envie CPF, CNPJ, senhas nem documentos de clientes.</label>
<button class="btn" type="submit">Enviar relato</button>
<p class="form-status" role="status" aria-live="polite"></p>
</div>
<p class="relatar-ok" hidden tabindex="-1">Recebemos o seu relato. Obrigado.</p>
<p class="aviso-lgpd">Prefere o seu programa de e-mail? <a class="relatar-mail" href="mailto:{CONTATO}">Enviar mensagem pronta para {CONTATO}</a>.</p>
</form>"""


def append_asset(path: Path, marca: str, trecho: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(trecho, encoding="utf-8")
        return
    t = path.read_text(encoding="utf-8")
    if marca in t:
        return
    path.write_text(t.rstrip() + "\n" + trecho, encoding="utf-8")


def inject_footer_link(html: str) -> str:
    if 'href="/relatar/"' in html:
        return html
    # menu do rodapé
    html = html.replace(
        '<a href="/sugestoes/">Sugestões</a>',
        '<a href="/sugestoes/">Sugestões</a><a href="/relatar/">Relatar um problema</a>',
        1,
    )
    if 'href="/relatar/"' not in html:
        html = html.replace(
            '<a href="/termos/">Termos de uso</a>',
            '<a href="/relatar/">Relatar um problema</a><a href="/termos/">Termos de uso</a>',
            1,
        )
    # bloco de contato
    if 'class="foot-relatar"' not in html:
        extra = (
            '<p class="foot-relatar muted"><a class="relatar-link" href="/relatar/">'
            "Relatar um problema</a></p>"
        )
        if 'class="foot-sug"' in html:
            html = html.replace('<div class="foot-sug">', extra + '<div class="foot-sug">', 1)
        elif f"mailto:{CONTATO}" in html:
            html = html.replace(
                f'<a href="mailto:{CONTATO}">{CONTATO}</a>',
                f'<a href="mailto:{CONTATO}">{CONTATO}</a>' + extra,
                1,
            )
    return html


def enhance_404(html: str) -> str:
    if "cta-relatar" in html:
        return html
    bloco = """<div class="cta-relatar" data-auto>
<p>Se chegou aqui por engano depois de um erro, você pode nos avisar com uma mensagem já pronta. Não é preciso informar CPF, CNPJ nem documentos de clientes.</p>
<p class="ref">Pedido</p>
<p><a class="btn" href="/relatar/">Relatar um problema</a>
<a class="btn btn-ghost" href="mailto:temis@e-pronaos.com">Escrever para temis@e-pronaos.com</a></p>
</div>"""
    if "</main>" in html:
        return html.replace("</main>", bloco + "</main>", 1)
    return html + bloco


def write_relatar_page() -> None:
    donor = OUT / "sugestoes" / "index.html"
    if not donor.exists():
        donor = OUT / "privacidade" / "index.html"
    if not donor.exists():
        raise SystemExit("erros_pos: sem página-base para /relatar/")
    html = donor.read_text(encoding="utf-8")
    url = SITE + "/relatar/"
    title = "Relatar um problema · Têmis"
    desc = "Envie um relato pronto sobre um problema na Têmis. Nome e e-mail são opcionais. Sem CPF, CNPJ ou documentos de clientes."
    html = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", html, count=1, flags=re.I | re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(desc)}">', html, count=1)
    for prop, val in {
        "og:title": title,
        "og:description": desc,
        "og:url": url,
        "twitter:title": title,
        "twitter:description": desc,
    }.items():
        html = re.sub(
            rf'<meta (?:property|name)="{re.escape(prop)}" content="[^"]*">',
            lambda m, v=val: m.group(0).split("content=")[0] + f'content="{E(v)}">',
            html,
            count=1,
        )
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', html, count=1)
    body = f"""
<p class="eyebrow">Fale com a Têmis</p>
<h1>Relatar um problema</h1>
<p>Use o formulário abaixo. A mensagem já vem pronta com a página, o horário e o código do pedido, se houver. Você pode editar antes de enviar. Nome e e-mail são opcionais; com o e-mail, respondemos por lá.</p>
<p class="aviso-lgpd">Não envie documentos de clientes, CPF, CNPJ, senhas ou números de processo sigilosos.</p>
{FORM}
<p><a href="/sugestoes/">Quer só sugerir uma melhoria?</a> · <a href="/privacidade/">Como tratamos os dados</a></p>
"""
    # troca o conteúdo principal: do <main> até </main>, preservando nav
    m = re.search(r"(<main\b[^>]*>)([\s\S]*?)(</main>)", html, re.I)
    if not m:
        raise SystemExit("erros_pos: página-base sem <main>")
    html = html[: m.start()] + m.group(1) + body + m.group(3) + html[m.end() :]
    dest = OUT / "relatar" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def patch_temis_cfg(html: str) -> str:
    if "endpointRelatar" in html:
        return html
    html = html.replace(
        '"endpointSugestoes":"/conta/publico/sugestoes"',
        '"endpointSugestoes":"/conta/publico/sugestoes","endpointRelatar":"/conta/publico/relatar"',
    )
    html = html.replace(
        '"endpointSugestoes": "/conta/publico/sugestoes"',
        '"endpointSugestoes": "/conta/publico/sugestoes", "endpointRelatar": "/conta/publico/relatar"',
    )
    return html


def main() -> None:
    if not (OUT / "index.html").exists():
        raise SystemExit(f"out inválido: {OUT}")
    write_relatar_page()
    four = OUT / "404.html"
    if four.exists():
        html = enhance_404(four.read_text(encoding="utf-8"))
        html = inject_footer_link(html)
        html = patch_temis_cfg(html)
        four.write_text(html, encoding="utf-8")
    n = 0
    for p in OUT.rglob("*.html"):
        if p.name == "google1d303b8551cc5763.html":
            continue
        html = p.read_text(encoding="utf-8")
        orig = html
        html = inject_footer_link(html)
        html = patch_temis_cfg(html)
        if html != orig:
            p.write_text(html, encoding="utf-8")
            n += 1
    append_asset(OUT / "assets" / "site.css", "erros_pos t1965u", CSS)
    append_asset(OUT / "assets" / "site.js", "erros_pos t1965u", JS)
    print(f"[erros_pos] paginas={n} relatar=ok 404={'ok' if four.exists() else 'ausente'}")


if __name__ == "__main__":
    main()
