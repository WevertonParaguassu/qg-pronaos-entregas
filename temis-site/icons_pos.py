#!/usr/bin/env python3
"""Ícones de linha dourados, um por cada uma das 28 aplicações, ligados no catálogo e nas páginas (t1946u).
Roda depois do confianca_pos (as grades já existem). Rollback: apagar a linha no build.sh.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
MARCA = "<!--icons-t1951u-->"

# viewBox 0 0 24 24, stroke only, gold applied by CSS
P = {
    "central": "M4 19V5h16v14H4zm2-2h12M8 7h8",
    "memoria-do-escritorio": "M6 4h9l5 5v11H6V4zm9 0v5h5",
    "hub-juridico": "M12 3v18M5 8h14M5 16h14M8 8v8m8-8v8",
    "reflexa": "M4 12h16M12 4l8 8-8 8",
    "radar-processual": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM12 6a6 6 0 1 0 0 12 6 6 0 0 0 0-12zM12 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4z",
    "probatoria": "M8 3h8v4H8V3zm-2 4h12v14H6V7zm4 5h8m-8 4h6",
    "evolutiva": "M4 17l5-5 3 3 8-8M16 7h4v4",
    "jurisprudencia-viva": "M6 4h12v16H6V4zm3 4h6M9 12h6M9 16h4",
    "estrategia-recursal": "M5 19c6-2 6-12 14-14M15 3h4v4",
    "destrancamento-processual": "M7 11V8a5 5 0 0 1 10 0v3M6 11h12v10H6V11z",
    "organon-juridico": "M4 6h16M4 12h16M4 18h10M8 6v12",
    "auditoria-juridica": "M9 11l2 2 4-4M5 4h14v16H5V4z",
    "documental-diagramacao": "M5 4h10l4 4v12H5V4zm10 0v4h4M8 13h8M8 17h5",
    "cartografia-humana-processual": "M4 6l6-2 6 2 4-1v15l-4 1-6-2-6 2V6z",
    "fontes-do-direito-legado": "M5 4h6c2 0 3 1 3 3v13H8c-2 0-3-1-3-3V4zm8 0h6v16h-6",
    "cupula-v2": "M4 18h16M6 18V10l6-6 6 6v8",
    "ingestao-processual": "M12 3v12m-5-5 5 5 5-5M5 21h14",
    "pericial": "M9 3h6l1 3h3v4h-2l-3 11H10L7 10H5V6h3l1-3z",
    "especialistas-juridicos": "M8 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm8 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM3 20a5 5 0 0 1 10 0M13 20a5 5 0 0 1 8 0",
    "fontes-do-direito-v3": "M6 4h8c3 0 4 2 4 5s-1 5-4 5H10v6H6V4zm4 6h3",
    "calculos-juridicos": "M6 3h12v18H6V3zm3 4h6M8 11h2m3 0h3M8 15h2m3 0h3",
    "outcome-loop": "M4 12a8 8 0 1 0 2.3-5.6M4 4v6h6",
    "audaciosa": "M12 3l2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3z",
    "advogado-do-diabo": "M8 9a4 4 0 1 1 8 0c0 3-4 5-4 8M12 20h.01",
    "protetora-leal": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z",
    "agon": "M5 19l7-14 7 14M8 13h8",
    "nous": "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
    "politeia": "M3 20h18M5 20V9l7-5 7 5v11M10 20v-6h4v6",
}

CSS = """
/* icons_pos t1951u */
.icon-app{width:28px;height:28px;flex:none;display:block;stroke:#E0C078;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.apps-grid a{flex-direction:row;flex-wrap:wrap;align-items:flex-start;gap:.7rem .8rem}
.apps-grid a .icon-app{margin-top:.15rem}
.apps-grid a h3,.apps-grid a p,.apps-grid a .disp,.apps-grid a .abrir{flex:1 1 calc(100% - 40px)}
.apps-grid a p,.apps-grid a .disp,.apps-grid a .abrir{flex-basis:100%;margin-left:36px}
.app-hero-icon{display:inline-block;vertical-align:-.35rem;margin-right:.45rem}
"""


def svg(slug: str, cls="icon-app") -> str:
    d = P.get(slug, "M5 5h14v14H5z")
    # "m" circles in radar/nous used as path approx — keep path
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
        f'<path d="{d}"/></svg>'
    )


def main() -> None:
    n = 0
    for p in OUT.rglob("*.html"):
        s = p.read_text(encoding="utf-8")
        if MARCA in s:
            continue
        orig = s
        if "icons_pos t1951u" not in s and "</style>" in s:
            s = s.replace("</style>", CSS + "</style>", 1)
        # catalog cards: <a href="/temis/slug/"> maybe with leftover
        def card(m):
            slug = m.group(1)
            inner = m.group(2)
            if "icon-app" in inner:
                return m.group(0)
            return f'<a href="/temis/{slug}/">{svg(slug)}{inner}</a>'
        s = re.sub(
            r'<a href="/temis/([a-z0-9-]+)/">(.*?)</a>',
            card,
            s,
            flags=re.S,
        )
        # app page title
        rel = str(p.relative_to(OUT)).replace("\\", "/")
        m = re.fullmatch(r"temis/([a-z0-9-]+)/index\.html", rel)
        if m:
            slug = m.group(1)
            if f"icon-app app-hero-icon" not in s:
                s = re.sub(
                    r"(<h1>)",
                    r"\1" + svg(slug, "icon-app app-hero-icon"),
                    s,
                    count=1,
                )
        if s != orig:
            if MARCA not in s:
                s = s.replace("</body>", MARCA + "</body>", 1) if "</body>" in s else s + MARCA
            p.write_text(s, encoding="utf-8")
            n += 1
    print(f"[icons_pos] ok: {n} html com ícones de linha dourados")


if __name__ == "__main__":
    main()
