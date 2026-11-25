#!/usr/bin/env python3
"""t2235u — Suporte e inauguração no site público da Têmis.
1) Página /suporte/ com suportetemis@e-pronaos.com, o que mandar, o que nunca mandar e atalhos (Sugestões, Relatar um problema).
2) Rodapé de todas as páginas: linha «Suporte: suportetemis@e-pronaos.com · Central de suporte».
3) /sugestoes/: aviso do e-mail de suporte.
4) Home: faixa «Chegou a Têmis · semana de inauguração», que troca sozinha conforme a semana (78/65/50) lendo precos_publicos.json.
5) sitemap.xml com /suporte/.
Roda antes do PWA (que continua por último). Rollback: apagar a linha deste script no build.sh.
"""
import json, re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
ROOT = Path(__file__).resolve().parent
# Interruptor: enquanto a regra suportetemis@ não existir no Email Routing da Cloudflare, o site mostra temis@ (que já entrega).
# Para ligar: gravar "sim" em temis-site/suporte_ativo.txt (só depois do e-mail de teste chegar na caixa contato.pronaos).
_ATIVO = (ROOT / "suporte_ativo.txt").read_text(encoding="utf-8").strip().lower() == "sim" if (ROOT / "suporte_ativo.txt").exists() else False
SUP = "suportetemis@e-pronaos.com" if _ATIVO else "temis@e-pronaos.com"
MARCA = "<!--suporte-t2235u-->"
DADOS = json.loads((ROOT / "precos_publicos.json").read_text(encoding="utf-8"))
SEM = (DADOS.get("rampa") or {}).get("semanas") or {}

CSS = """<style>/* t2235u */
.foot-suporte{margin-top:.35rem}
.sup-grid{display:grid;gap:1rem;margin:1.4rem 0}
@media(min-width:800px){.sup-grid{grid-template-columns:repeat(3,1fr)}}
.sup-card{position:relative;z-index:2;padding:1.2rem 1.3rem;border:1px solid rgba(224,192,120,.45);border-radius:16px;background:rgba(11,26,51,.92)}
.sup-card h2{font-size:1.25rem;margin:0 0 .5rem}
.sup-card p,.sup-card li{color:#c9d3ee;line-height:1.55}
.sup-mail{display:inline-block;margin:.6rem 0 0;padding:.75rem 1.2rem;border-radius:12px;background:linear-gradient(180deg,#f6dd9a,#d9b25c);color:#1a1204!important;font-weight:700;text-decoration:none}
.tm-chegou{position:relative;z-index:60;display:flex;flex-wrap:wrap;gap:.35rem .8rem;align-items:center;justify-content:center;padding:.55rem 1rem;
 background:linear-gradient(90deg,#0b1a33,#13284f 50%,#0b1a33);border-bottom:1px solid rgba(224,192,120,.55);color:#eef2ff;font:500 .92rem/1.35 Inter,system-ui,sans-serif;text-align:center}
.tm-chegou b{color:#f6dd9a;letter-spacing:.06em;text-transform:uppercase}
.tm-chegou a{color:#1a1204;background:#e0c078;padding:.25rem .7rem;border-radius:999px;font-weight:700;text-decoration:none;white-space:nowrap}
</style>"""

MAIN = f"""<main id="main" class="wrap" style="position:relative;z-index:2;padding:2.5rem 0 3rem">
<nav class="crumbs" aria-label="Você está aqui"><a href="/">Início</a> › <span>Suporte</span></nav>
<p class="kicker">Fale com a Têmis</p>
<h1>Suporte</h1>
<p class="lead">Precisa de ajuda com a sua conta, um pagamento ou um aplicativo Têmis? Escreva para o nosso suporte. Uma pessoa da equipe lê, organiza e responde.</p>
<p><a class="sup-mail" href="mailto:{SUP}?subject=Suporte%20T%C3%AAmis">{SUP}</a></p>
<div class="sup-grid">
 <div class="sup-card"><h2>O que mandar</h2><ul><li>O e-mail da sua conta na Têmis.</li><li>Em qual tela ou aplicativo Têmis aconteceu.</li><li>O que você esperava e o que apareceu (um print ajuda).</li><li>Data e hora aproximadas.</li></ul></div>
 <div class="sup-card"><h2>Nunca mande</h2><ul><li>Senhas ou códigos de verificação.</li><li>Documentos de clientes ou dados sensíveis de terceiros.</li><li>Número de processo sob sigilo.</li></ul><p>A equipe nunca pede a sua senha.</p></div>
 <div class="sup-card"><h2>Outros caminhos</h2><ul><li><a href="/relatar/">Relatar um problema</a> numa página do site.</li><li><a href="/sugestoes/">Enviar uma sugestão</a> para melhorar a plataforma.</li><li><a href="/conta/comecar">Faça o tour</a> e veja como a triagem funciona.</li><li><a href="/planos/">Planos e preços</a>.</li></ul></div>
</div>
<p class="muted">Pagamentos e reembolsos seguem os <a href="/termos/">Termos de uso</a> e o direito de arrependimento de 7 dias (CDC, art. 49). Dados pessoais são tratados conforme a <a href="/privacidade/">Política de privacidade</a>. Minutas da Têmis são rascunhos para revisão do advogado responsável.</p>
</main>"""

def faixa():
    s1, s2, s3 = SEM.get("1", {}), SEM.get("2", {}), SEM.get("3", {})
    dados = json.dumps({"s": [[s1.get("fim_epoch"), s1.get("mes1_pct", 78), "02/12, 05:59"],
                              [s2.get("fim_epoch"), s2.get("mes1_pct", 65), "09/12, 05:59"],
                              [s3.get("fim_epoch"), s3.get("mes1_pct", 50), "31/05/2027, 23:59"]]})
    return (f'{MARCA}<div class="tm-chegou" role="status" id="tm-chegou"><b>Chegou a Têmis</b>'
            f'<span id="tm-chegou-t">Semana de inauguração: 1º mês com {s1.get("mes1_pct", 78)}% de desconto até 02/12, 05:59 (horário de Brasília).</span>'
            f'<a href="/planos/?utm_source=site&amp;utm_medium=faixa&amp;utm_campaign=inauguracao_t2235u">Ver a oferta</a></div>'
            '<script>(function(){var D=' + dados + ';var n=Date.now()/1000,el=document.getElementById("tm-chegou-t");if(!el)return;'
            'var r=["Semana de inauguração","2ª semana de inauguração","Rampa de lançamento"];'
            'for(var i=0;i<3;i++){var s=D.s[i];if(s[0]&&n<=s[0]){el.textContent=r[i]+": 1º mês com "+s[1]+"% de desconto"+(i<2?" até "+s[2]:"; inscrição até "+s[2])+" (horário de Brasília).";return}}'
            'var b=document.getElementById("tm-chegou");if(b)b.remove()})();</script>')

def main():
    feitos = {"rodape": 0, "suporte": False, "sugestoes": False, "home": False, "sitemap": False}
    # 1) /suporte/ a partir do molde de /sugestoes/
    molde = OUT / "sugestoes" / "index.html"
    if molde.exists():
        s = molde.read_text(encoding="utf-8")
        s = s.replace("Sugestões · Têmis", "Suporte · Têmis").replace("https://agentetemis.com/sugestoes", "https://agentetemis.com/suporte")
        s = s.replace("Envie uma sugestão para a Têmis. Nome e e-mail são opcionais. O aviso de privacidade aparece no formulário.",
                      f"Suporte da Têmis: escreva para {SUP}. Conta, pagamentos e aplicativos Têmis.")
        s = s.replace('"name":"Sugestões"', '"name":"Suporte"')
        s = re.sub(r"<main\b.*?</main>", lambda m: MAIN, s, count=1, flags=re.S)
        d = OUT / "suporte"; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(s, encoding="utf-8"); feitos["suporte"] = True
    # 2) rodapé, 3) sugestões, 4) home
    for f in OUT.rglob("*.html"):
        s = f.read_text(encoding="utf-8")
        if MARCA in s:
            continue
        o = s
        alvo = '<a href="mailto:temis@e-pronaos.com">temis@e-pronaos.com</a>'
        if _ATIVO and '<footer' in s and alvo in s:
            ini = s.rfind('<footer')
            pos = s.find(alvo, ini)
            if pos > 0:
                ins = f'<p class="foot-suporte muted">Suporte: <a href="mailto:{SUP}">{SUP}</a> · <a href="/suporte/">Central de suporte</a></p>'
                s = s[:pos + len(alvo)] + ins + s[pos + len(alvo):]
                feitos["rodape"] += 1
        if f == OUT / "sugestoes" / "index.html":
            fr = "A sugestão chega à equipe no e-mail temis@e-pronaos.com."
            if _ATIVO and fr in s:
                s = s.replace(fr, fr + f' Para suporte da sua conta, escreva para <a href="mailto:{SUP}">{SUP}</a>.', 1); feitos["sugestoes"] = True
        if f == OUT / "index.html":
            s = re.sub(r'(<body\b[^>]*>)', lambda m: m.group(1) + faixa(), s, count=1); feitos["home"] = True
        if s != o:
            s = s.replace("</head>", CSS + "</head>", 1)
            if MARCA not in s:
                s = s.replace("</body>", MARCA + "</body>", 1)
            f.write_text(s, encoding="utf-8")
    sm = OUT / "sitemap.xml"
    if sm.exists():
        x = sm.read_text(encoding="utf-8")
        if "/suporte/" not in x and "</urlset>" in x:
            x = x.replace("</urlset>", "<url><loc>https://agentetemis.com/suporte/</loc><changefreq>monthly</changefreq><priority>0.5</priority></url></urlset>")
            sm.write_text(x, encoding="utf-8"); feitos["sitemap"] = True
    print("[suporte_t2235u]", SUP, feitos)

if __name__ == "__main__":
    main()
