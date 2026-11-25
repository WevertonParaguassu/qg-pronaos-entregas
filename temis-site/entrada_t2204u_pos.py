#!/usr/bin/env python3
"""t2204u — injeta os pacotinhos Base e Prática em /planos/ depois do precos_pos,
sem alterar precos_pos.py (que exige exatamente 5 planos no array principal).
Rollback: apagar a linha no build.sh.
"""
import json, re, sys
from pathlib import Path
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
ROOT = Path(__file__).resolve().parent
MARCA = "<!--entrada-t2204u-->"
PATHS = {
    "base": "M12 20V10M12 10c-2.2-3.2-4.2-4.6-6-5M12 10c2.2-3.2 4.2-4.6 6-5M8.5 8.2c.6-2.2 1.8-4 3.5-5.4 1.7 1.4 2.9 3.2 3.5 5.4",
    "pratica": "M7 3.5h10a1 1 0 0 1 1 1v15a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-15a1 1 0 0 1 1-1zM9 8h6M9 11h6M9 14h4",
}

def brl(n):
    return "R$ " + f"{int(n):,}".replace(",", ".")

def medal(k):
    d = PATHS[k]
    return (f'<span class="tm-med tm-m1" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24"><path d="{d}" fill="none" stroke="#f0d58c" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')

def card(p):
    return (
        f'<article class="tm-card tm-entrada" id="plano-{p["id"]}">'
        f'<div class="tm-ess-topo">{medal(p["id"])}<div>'
        f'<p class="eyebrow">{p.get("tag","")}</p>'
        f'<h2>{p["nome"]}</h2></div></div>'
        f'<p>{p["resumo"]}</p>'
        f'<ul class="tm-bullets">'
        f'<li>{p["casos"]} casos ativos · {p["minutas"]} minutas · {p["mensagens"]} mensagens/mês</li>'
        f'<li>Chat jurídico com fontes e conferência de citações</li>'
        f'<li>Sem skills Têmis neste degrau</li>'
        f'</ul></article>'
    )

def main():
    f = OUT / "planos" / "index.html"
    if not f.exists():
        print("[entrada_t2204u] sem /planos/"); return
    s = f.read_text(encoding="utf-8")
    if MARCA in s:
        print("[entrada_t2204u] já aplicado"); return
    data = json.loads((ROOT / "precos_publicos.json").read_text())
    cards = "".join(card(p) for p in data.get("entrada") or [])
    bloco = MARCA + '<div class="tm-entrada-grid">' + cards + "</div>"
    # encaixa os pacotinhos depois do Essencial e antes dos 5 planos
    inserted = False
    for pat in (
        r'(<div class="ficha">)',
        r'(<div id="solo")',
        r'(</div>\s*<div class="tm-planos">)',
        r'(<section[^>]*class="[^"]*tm-planos)',
        r'(<article[^>]*id="plano-solo")',
        r'(<h2>Têmis Solo</h2>)',
    ):
        m = re.search(pat, s)
        if m:
            s = s[:m.start()] + bloco + s[m.start():]
            inserted = True
            break
    if not inserted:
        s = s.replace("</main>", bloco + "</main>", 1) if "</main>" in s else s + bloco
    # linha da tabela: Skills Têmis a partir do Profissional
    # 6 colunas: Essencial Solo Prof Esc Max Ultra
    if "Skills Têmis" not in s:
        mark = lambda on: ('<td><span class="tm-s" aria-label="incluído">✓</span></td>' if on
                           else '<td><span class="tm-n" aria-label="não incluído">—</span></td>')
        row = '<tr><th scope="row">Skills Têmis</th>' + "".join(mark(i >= 2) for i in range(6)) + "</tr>"
        # após a primeira linha de recurso, ou antes do fechamento da tabela
        if re.search(r"<th scope=\"row\">", s):
            s = re.sub(r"(</tbody>|</table>)", row + r"\1", s, count=1)
        # também tente injetar após teses se existir
    s = s.replace("</head>", MARCA + "<style>.tm-entrada-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));margin:18px 0 8px}</style></head>", 1)
    f.write_text(s, encoding="utf-8")
    print("[entrada_t2204u] ok")

if __name__ == "__main__":
    main()
