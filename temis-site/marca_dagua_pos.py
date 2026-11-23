#!/usr/bin/env python3
"""Pós-processador t1977u: a parte coberta da estátua fica em marca d'água.

Os cartões vivem dentro de main/.sec com z-index, então a estátua (z-index 0)
ficava inteira atrás deles. Este script, no fim do build, só com CSS:

- tira o z-index de main e .sec para o empilhamento poder intercalá-los;
- o fundo de vidro vai num ::before (z-index -1), atrás da estátua;
- o texto dos cartões sobe (z-index 3), na frente da estátua;
- o recorte da figura cheia (já feito pelo JS) permanece: fora do cartão
  a estátua é nítida; por baixo do cartão só resta a camada marca d'água;
- fallback mais opaco para navegadores sem backdrop-filter;
- não mexe no fluxo do hero nem na tipografia móvel (t1955u).

Rollback: apagar a linha do build.sh que chama este script.
"""
from __future__ import annotations

import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")

MARKER = "marca_dagua_pos t1977u"

ITEMS = [
    ".mini",
    ".card",
    ".band",
    ".demo",
    ".dash",
    ".ok",
    ".apps-grid a",
    ".doc-paper",
    ".check-lab li",
    ".ficha>div",
    ".sug-ok",
    ".relatar-ok",
    ".cta-relatar",
    ".selo-ficcao",
]

def sel(suffix: str = "") -> str:
    return ",".join(i + suffix for i in ITEMS)

CSS = f"""
/* marca_dagua_pos t1977u: parte coberta da estátua em marca d'água; o resto visível */
main,.sec{{z-index:auto}}
footer,.foot{{z-index:4}}
header.top,.mcta,.cta-sticky{{z-index:50}}
#temis-estatua{{z-index:1;pointer-events:none}}
#temis-estatua a.statue-acquire{{
  clip-path:none!important;
  -webkit-clip-path:none!important;
  pointer-events:none;
}}
#temis-estatua .figura{{pointer-events:auto}}
#temis-estatua .figura-wm{{
  opacity:.4;
  mix-blend-mode:normal;
  filter:saturate(1.08);
  clip-path:none!important;
  -webkit-clip-path:none!important;
  pointer-events:none;
}}
@media(max-width:900px){{
  #temis-estatua .figura-wm{{opacity:.34}}
}}
{sel()}{{
  position:relative;
  background-color:transparent;
  background-image:none;
  isolation:auto;
  -webkit-backdrop-filter:none;
  backdrop-filter:none;
}}
{sel("::before")}{{
  content:"";
  position:absolute;
  inset:0;
  z-index:-1;
  border-radius:inherit;
  pointer-events:none;
  background-color:rgba(11,28,56,.58);
  background-image:var(--filigree),var(--filigree-e),var(--filigree-sw),var(--filigree-se);
  background-repeat:no-repeat;
  background-size:38px 38px;
  background-position:6px 6px,calc(100% - 6px) 6px,6px calc(100% - 6px),calc(100% - 6px) calc(100% - 6px);
  -webkit-backdrop-filter:blur(12px) saturate(1.25);
  backdrop-filter:blur(12px) saturate(1.25);
  box-shadow:0 16px 36px rgba(4,12,28,.28);
}}
.apps-grid a::before{{
  background-image:linear-gradient(135deg,rgba(14,30,60,.58),rgba(6,16,34,.52));
}}
.selo-ficcao::before,.cta-relatar::before,.sug-ok::before,.relatar-ok::before,
.doc-paper::before,.check-lab li::before,.ficha>div::before{{
  background-image:none;
}}
{sel(" > *")}{{
  position:relative;
  z-index:3;
}}
.hero-shot,.shot,figure.shot,.plat-shots figure.shot,
.shot figcaption,.lab-doc figcaption,
main a.btn,main a.btn-ghost,.cta-duo,.pill{{
  position:relative;
  z-index:3;
}}
.mini h3,.card h3,.mini p,.card p,
.apps-grid a h3,.apps-grid a p,
.doc-paper,.ficha>div{{
  text-shadow:0 1px 2px rgba(4,12,28,.9),0 0 14px rgba(6,13,27,.55);
}}
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){{
  {sel("::before")}{{
    background-color:rgba(11,28,56,.86);
    -webkit-backdrop-filter:none;
    backdrop-filter:none;
  }}
  .apps-grid a::before{{
    background-image:linear-gradient(135deg,rgba(14,30,60,.9),rgba(6,16,34,.86));
  }}
}}
"""

STYLE = f"<style>\n{CSS}\n</style>"


def inject(html: str) -> str:
    if MARKER in html:
        return html
    if "</head>" in html:
        return html.replace("</head>", STYLE + "</head>", 1)
    return html


def append_css_file(css_path: Path) -> None:
    if not css_path.exists():
        return
    text = css_path.read_text(encoding="utf-8")
    if MARKER in text:
        return
    css_path.write_text(text.rstrip() + "\n" + CSS + "\n", encoding="utf-8")


def main() -> None:
    if not OUT.exists():
        sys.exit(f"saída inexistente: {OUT}")
    n = 0
    for p in OUT.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        s2 = inject(s)
        if s2 != s:
            p.write_text(s2, encoding="utf-8")
            n += 1
    append_css_file(OUT / "assets" / "site.css")
    print(f"[marca_dagua_pos] ok: vidro atrás e texto na frente da estátua em {n} html")


if __name__ == "__main__":
    main()
