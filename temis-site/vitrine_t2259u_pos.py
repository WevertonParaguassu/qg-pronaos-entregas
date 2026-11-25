#!/usr/bin/env python3
"""t2259u — vitrine pública /aplicativos/ (azul e dourado, selo App Têmis).
Sem palavras vetadas, sem urgência falsa, sem prova social inventada.
Os preços vêm do catálogo gerado (alacarte_publicos.json). Sem source map.
Rollback: apagar a linha deste script no build.sh e a pasta out/aplicativos/.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--vitrine-t2259u-->"
PROIB = ("assinatura", "gratuita", "grátis", "adapta")
DADOS = json.loads((ROOT / "alacarte_publicos.json").read_text(encoding="utf-8")) if (ROOT / "alacarte_publicos.json").exists() else {"cards": ""}

CSS = """
.t2259 vit, .vit-wrap{--az:#07142b;--az2:#0d2147;--ou:#d4af5a;--ou2:#f0d78c;--tx:#eef2fb;--mu:#a9b6d3}
.vit-wrap{background:radial-gradient(1200px 700px at 80% -10%,#1b3a78 0,#07142b 55%);color:#eef2fb;padding:48px 20px 72px}
.vit-wrap h1{font-family:Georgia,serif;color:#f0d78c;font-size:36px;margin:0 0 12px}
.vit-wrap .lede{max-width:720px;color:#a9b6d3;line-height:1.55;margin:0 0 28px}
.vit-filtros{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 22px}
.vit-filtros button{background:#0a1b3c;color:#f0d78c;border:1px solid #d4af5a55;border-radius:999px;padding:8px 16px;cursor:pointer;font:inherit}
.vit-filtros button.on{background:linear-gradient(180deg,#f0d78c,#d4af5a);color:#1a1405;font-weight:700;border-color:transparent}
.vit-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.vit-card{background:linear-gradient(165deg,#16325f 0%,#0d2147 55%,#0a1a38 100%);border:1px solid #d4af5a66;border-radius:18px;padding:20px;display:flex;flex-direction:column;min-height:240px}
.vit-card:hover{border-color:#d4af5a;box-shadow:0 8px 28px #d4af5a22}
.vit-card .bdg{display:inline-block;background:linear-gradient(180deg,#f0d78c,#d4af5a);color:#1a1405;font-size:11px;font-weight:800;letter-spacing:.4px;border-radius:999px;padding:3px 9px;text-transform:uppercase}
.vit-card h3{font-family:Georgia,serif;color:#f0d78c;font-size:20px;margin:10px 0 6px}
.vit-card .ent{color:#eef2fb;font-size:14px;line-height:1.45;flex:1}
.vit-card .pr{margin:12px 0 4px;font-family:Georgia,serif;color:#f0d78c;font-size:22px}
.vit-card .pr s{color:#a9b6d3;font-size:14px;margin-right:6px}
.vit-card .dep{color:#a9b6d3;font-size:12px}
.vit-card .btn{display:inline-block;margin-top:12px;background:linear-gradient(180deg,#f0d78c,#d4af5a);color:#1a1405;font-weight:700;border-radius:999px;padding:10px 18px;text-decoration:none}
@media(max-width:640px){.vit-wrap h1{font-size:26px}.vit-grid{grid-template-columns:1fr}}
"""

JS = "(function(){var bs=document.querySelectorAll('.vit-filtros button'),cs=document.querySelectorAll('.vit-card');bs.forEach(function(b){b.onclick=function(){bs.forEach(function(x){x.classList.remove('on')});b.classList.add('on');var f=b.getAttribute('data-f');cs.forEach(function(c){c.style.display=(f==='todos'||c.getAttribute('data-tipo')===f)?'':'none'})}})})();"

def minify_js(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s

def pagina():
    cards = DADOS.get("cards") or ""
    body = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aplicativos Têmis à la carte</title>
<meta name="description" content="Contrate cada aplicativo Têmis, skill ou ferramenta do seu jeito, item a item. Você recebe o resultado para revisar.">
<style>{CSS}</style></head><body>
{MARCA}
<main class="vit-wrap">
<h1>Cada aplicativo Têmis, no seu ritmo</h1>
<p class="lede">Escolha só o que o escritório precisa agora: um aplicativo Têmis, uma skill Têmis ou uma ferramenta, com a entrega à vista. O trabalho roda no servidor; você leva o resultado pronto para a advogada revisar. Se preferir o conjunto completo, compare os planos — sem pressa e sem relógio inventado.</p>
<div class="vit-filtros">
<button type="button" class="on" data-f="todos">Todos</button>
<button type="button" data-f="aplicativo">Aplicativos</button>
<button type="button" data-f="skill">Skills</button>
<button type="button" data-f="ferramenta">Ferramentas</button>
</div>
<div class="vit-grid">{cards}</div>
<p class="lede" style="margin-top:28px">A contratação mensal pode ser encerrada quando você quiser. A avulsa vale 30 dias. Direito de arrependimento de 7 dias (CDC, art. 49). Minutas e cálculos são para revisão da advogada.</p>
<p><a class="vit-card btn" href="/conta/vitrine" style="display:inline-block">Contratar na área do cliente</a>
<a class="vit-card btn" href="/planos/" style="display:inline-block;margin-left:8px">Ver os planos</a></p>
</main>
<script>{minify_js(JS)}</script>
</body></html>"""
    low = body.lower()
    for w in PROIB:
        if w in low:
            raise SystemExit("palavra vetada na vitrine pública: " + w)
    return body

def linkar_home(out: Path):
    # coloca um atalho discreto no /planos/ ou no rodapé da home, se existir, sem quebrar pos anteriores
    for nome in ("planos/index.html", "index.html"):
        p = out / nome
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        if MARCA in t:
            continue
        inj = f'{MARCA}<p><a href="/aplicativos/">Aplicativos Têmis à la carte — contrate item a item</a></p>'
        if "</footer>" in t:
            t = t.replace("</footer>", inj + "</footer>", 1)
            p.write_text(t, encoding="utf-8")
        elif "</main>" in t:
            t = t.replace("</main>", inj + "</main>", 1)
            p.write_text(t, encoding="utf-8")

def main():
    dest = OUT / "aplicativos"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(pagina(), encoding="utf-8")
    # sem .map, sem fonte js solta
    linkar_home(OUT)
    print("vitrine t2259u ok", dest)

if __name__ == "__main__":
    main()
