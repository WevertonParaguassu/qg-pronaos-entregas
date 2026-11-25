#!/usr/bin/env python3
"""t2201u — medalhas (tags novas + lâmpada do Essencial) e ajustes da tabela pública
depois do precos_pos, sem editar o precos_pos.py. Rollback: apagar a linha no build.sh.
Nunca inclui cota de modelo nem as palavras vetadas.
"""
import re, sys
from pathlib import Path
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
MARCA = "<!--medalhas-t2201u-->"
LAMP = "M12 3.2c.15 1.3-.15 2.2-.7 3M12 3.2c-.15 1.3.15 2.2.7 3M10.4 6.4c-1.9.7-3.2 2.2-3.2 4 0 1.7 1.1 3 2.7 3.7l-.6 3.1h6.2l-.6-3.1c1.6-.7 2.7-2 2.7-3.7 0-1.8-1.3-3.3-3.2-4M9.2 17.5h5.6M8.2 19.4h7.6M10.2 21.2h3.6"
TAGS = {
    "o começo": "a pena",
    "mais volume e revisão": "a balança",
    "a equipe toda": "as colunas",
    "seu agente pessoal": "o escudo",
    "o topo da escada": "a coroa",
}
CSS = """<style>
.tm-ess .tm-med{width:56px;height:56px;margin-right:4px}
.tm-ess-topo{display:flex;align-items:center;gap:12px}
.tm-alem,section.sec:has(.eyebrow):has(h2) {}
section.tm-hide-avulso{display:none!important}
</style>"""

def main():
    f = OUT / "planos" / "index.html"
    if not f.exists():
        print("[medalhas_t2201u] sem /planos/"); return
    s = f.read_text(encoding="utf-8")
    if MARCA in s:
        print("[medalhas_t2201u] já aplicado"); return
    for a, b in TAGS.items():
        s = s.replace(a, b)
    # lâmpada no cartão Essencial
    lamp = (f'<div class="tm-ess-topo"><span class="tm-med tm-m1" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24"><path d="{LAMP}" fill="none" stroke="#f0d58c" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')
    s = s.replace(
        '<div class="tm-ess"><div><p class="eyebrow">Para começar</p>',
        '<div class="tm-ess"><div>' + lamp + '<div><p class="eyebrow">o primeiro passo</p>',
        1)
    if lamp.split("tm-ess-topo")[0] in s or "tm-ess-topo" in s:
        # close the extra div if we opened one
        s = s.replace(
            '<h2>Têmis Essencial — 7 dias para testar</h2>',
            '<h2>Têmis Essencial — 7 dias para testar</h2></div>',
            1)
    # faixa: alinha o texto aos recursos reais da entrada (sem teses; conferência e 1 processo / 5 cálculos)
    s = s.replace(
        "7 dias com o plano Solo e os recursos novos em versão de entrada (conferência das citações, 3 processos monitorados, 15 cálculos, plano de teses, 15 minutos de transcrição e 1 modelo .docx).",
        "7 dias para testar: chat jurídico com fontes, conferência das citações, 1 processo monitorado e 5 cálculos de atualização. O cartão só é pedido no fim do teste."
    )
    # Conselho: Max também entra (a linha gerada só marcava o Ultra)
    s = re.sub(
        r'(<th scope="row">100% das Têmis, fila prioritária e Conselho das 4 \(opcional\).*?</th>)(<td>—</td>){4}(<td>—</td>)(<td>✓</td>)',
        r'\1\2<td>✓</td><td>✓</td>',
        s,
        count=1,
        flags=re.S,
    )
    # Se o padrão acima não pegou (símbolos em span), tenta pelos tm-n/tm-s
    if "fila prioritária e Conselho" in s:
        def fix_row(m):
            row = m.group(0)
            # 6 cells after th: Essencial Solo Prof Esc Max Ultra — want — — — — ✓ ✓
            cells = re.findall(r"<td>.*?</td>", row, flags=re.S)
            if len(cells) == 6:
                def mark(on):
                    return '<td><span class="tm-s" aria-label="incluído">✓</span></td>' if on else '<td><span class="tm-n" aria-label="não incluído">—</span></td>'
                new = m.group(1) + "".join(mark(i >= 4) for i in range(6)) + "</tr>"
                return new
            return row
        s = re.sub(
            r'(<tr><th scope="row">100% das Têmis, fila prioritária e Conselho das 4 \(opcional\).*?</th>)(.*?</tr>)',
            fix_row, s, count=1, flags=re.S)
        # better heading: split meaning — don't promise 100%+fila on Max
        s = s.replace(
            "100% das Têmis, fila prioritária e Conselho das 4 (opcional)",
            "Conselho das 4",
        )
    # hide à la carte / avulso block
    s = re.sub(
        r'<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Além dos planos</p>.*?</section>',
        '<section class="sec tm-hide-avulso" hidden></section>',
        s, count=1, flags=re.S)
    s = s.replace("</head>", MARCA + CSS + "</head>", 1)
    f.write_text(s, encoding="utf-8")
    print("[medalhas_t2201u] ok")

if __name__ == "__main__":
    main()
