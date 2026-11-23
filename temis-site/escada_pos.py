#!/usr/bin/env python3
"""Medalhas douradas da escada de planos (Solo → Ultra) na página pública /planos/ (t1974u).
Mesmo traço dos ícones das 28 aplicações (viewBox 24, só linha, dourado). Escala: o brilho cresce a cada degrau; o Ultra
ganha medalha dourada cheia, coroa e borda. Sem preços (preço só depois do login). Rollback: apagar a linha no build.sh.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
MARCA = "<!--escada-t1974u-->"
P = {'solo': 'M19.5 3.5c-6.5 1-10.8 5.3-12.6 11.6L5 20.5M7.2 14.8c3.4-.2 6.9-1.6 9.1-5.6M9.6 10.9c2-.1 3.9-.8 5.4-2.2', 'profissional': 'M12 4v15M8 19.5h8M5 7h14M7 7l-3 6a3 2.2 0 0 0 6 0L7 7zM17 7l-3 6a3 2.2 0 0 0 6 0l-3-6z', 'escritorio': 'M3 20.5h18M4.5 17.5h15M12 3l8.5 5h-17L12 3zM6.5 8v9.5M10 8v9.5M14 8v9.5M17.5 8v9.5', 'max': 'M12 2.8l8 3v6.1c0 5-3.4 8.3-8 9.4-4.6-1.1-8-4.4-8-9.4V5.8l8-3zM12 8l1.25 2.55 2.8.4-2.03 1.98.48 2.8L12 14.4l-2.5 1.33.48-2.8-2.03-1.98 2.8-.4L12 8z', 'ultra': 'M4 19h16M5 19 3.4 9.2l4.7 3.6L12 6.3l3.9 6.5 4.7-3.6L19 19M12 2.2l.55 1.25 1.25.55-1.25.55L12 5.8l-.55-1.25L10.2 4l1.25-.55L12 2.2zM3.4 4.6l.4.9.9.4-.9.4-.4.9-.4-.9-.9-.4.9-.4.4-.9zM20.6 4.6l.4.9.9.4-.9.4-.4.9-.4-.9-.9-.4.9-.4.4-.9zM9.5 16h5'}
TAG = {"solo": "o começo", "profissional": "mais volume e revisão", "escritorio": "a equipe toda", "max": "seu agente pessoal", "ultra": "o topo da escada"}
CSS = """<style>
.tm-topo{display:flex;align-items:center;gap:14px;margin:0 0 6px}.tm-topo .eyebrow{margin:0}
.tm-med{flex:none;width:54px;height:54px;border-radius:50%;display:grid;place-items:center;border:1.5px solid #d4af5a;
 background:radial-gradient(circle at 32% 26%,#1d3d7c,#081633 70%)}
.tm-med svg{width:28px;height:28px;stroke:#f0d58c;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.tm-m1{box-shadow:0 0 0 3px #d4af5a10}.tm-m2{box-shadow:0 0 0 3px #d4af5a1c,0 0 10px #d4af5a22}
.tm-m3{box-shadow:0 0 0 3px #d4af5a26,0 0 14px #d4af5a33}.tm-m4{border-width:2px;box-shadow:0 0 0 4px #d4af5a30,0 0 18px #d4af5a44}
.tm-m5{width:60px;height:60px;border:2px solid #f6df9a;background:radial-gradient(circle at 35% 28%,#fff1c2,#e2bd62 45%,#a87c26 100%);
 box-shadow:0 0 0 4px #d4af5a40,0 0 26px #e9c46a88}.tm-m5 svg{stroke:#0b1a3a;width:31px;height:31px}
.ficha>#ultra{border-color:#e9c46a!important;box-shadow:0 0 0 1px #e9c46a55,0 10px 40px #d4af5a22}
@media (prefers-reduced-motion:no-preference){.tm-m5{animation:tmPulso 3.2s ease-in-out infinite}
@keyframes tmPulso{0%,100%{box-shadow:0 0 0 4px #d4af5a40,0 0 22px #e9c46a66}50%{box-shadow:0 0 0 6px #d4af5a55,0 0 34px #f0d58caa}}}
@media (max-width:480px){.tm-med{width:46px;height:46px}.tm-med svg{width:24px;height:24px}.tm-m5{width:52px;height:52px}.tm-m5 svg{width:28px;height:28px}}
</style>"""

def medalha(k: str, n: int) -> str:
    return (f'<span class="tm-med tm-m{n}" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="{P[k]}"/></svg></span>')

def main() -> None:
    f = OUT / "planos" / "index.html"
    if not f.exists(): print("[escada_pos] sem /planos/"); return
    s = f.read_text(encoding="utf-8")
    if MARCA in s: print("[escada_pos] já aplicado"); return
    n = 0
    def troca(m):
        nonlocal n
        ids = re.findall(r'id="([^"]+)"', m.group(1)); k = next((i for i in ids if i in P), None)
        if not k: return m.group(0)
        n += 1; d = int(m.group(2))
        return (f'{m.group(1)}<div class="tm-topo">{medalha(k, d)}<p class="eyebrow">Degrau {d} de 5 · {TAG[k]}</p></div>')
    s = re.sub(r'(<div id="[^"]+"(?: id="[^"]+")?>)<p class="eyebrow">Degrau (\d) de 5</p>', troca, s)
    if n != 5: raise SystemExit(f"[escada_pos] esperava 5 degraus, achei {n}")
    s = s.replace("</head>", MARCA + CSS + "</head>", 1)
    f.write_text(s, encoding="utf-8"); print(f"[escada_pos] ok: {n} medalhas em /planos/")

if __name__ == "__main__":
    main()
