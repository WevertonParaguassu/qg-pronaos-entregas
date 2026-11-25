#!/usr/bin/env python3
"""t2198u (aprovado pelo Weverton em 24/11/2026, t2200s9327) — /planos/ público: preços já aprovados (tabela de 23/11/2026, sem
mudar valores), contagem do lançamento até 31/01/2027 23h59 (Brasília), comparativo por recurso (incluindo os novos) e o
«Têmis Essencial — 7 dias para testar». Dados: temis-site/precos_publicos.json. Rollback: apagar a linha no build.sh."""
import json, re, sys, html
from pathlib import Path
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
DADOS = json.loads((Path(__file__).parent / "precos_publicos.json").read_text(encoding="utf-8"))
MARCA = "<!--precos-t2198u-->"
E = html.escape
L = DADOS["lancamento"]; FIM = L["fim_texto"]; EP = int(L["fim_epoch"])
def r(v): return f"R$ {v:,.0f}".replace(",", ".")

def preco_html(p):
    pu = " por usuário" if p["por_usuario"] else ""
    return (f'<div class="tm-preco"><span class="tm-lanc"><s aria-label="preço cheio">{r(p["cheio"])}</s> <b>{r(p["lancamento"])}</b>/mês{pu}'
            f'<small>até {FIM} · depois {r(p["cheio"])}/mês (preço cheio)</small></span>'
            f'<span class="tm-cheio" hidden><b>{r(p["cheio"])}</b>/mês{pu}</span></div>'
            f'<p><a class="btn" href="/conta/planos">Contratar o {E(p["nome"])} ›</a></p>')

def sim(v): return '<span class="tm-s" aria-label="incluído">✓</span>' if v else '<span class="tm-n" aria-label="não incluído">—</span>'
def n(v, suf=""): return (f"{v:,}".replace(",", ".") + suf) if v else '<span class="tm-n">—</span>'

def tabela():
    ps = DADOS["planos"]; es = DADOS["essencial"]["recursos"]
    cols = [("Essencial<br><small>7 dias para testar</small>", es, None)] + [(E(p["nome"]), p["recursos"], p) for p in ps]
    solo = ps[0]
    def lin(rot, f, nota=""):
        return f'<tr><th scope="row">{rot}{f"<small>{nota}</small>" if nota else ""}</th>' + "".join(f"<td>{f(rc, p)}</td>" for _, rc, p in cols) + "</tr>"
    def lim(campo, suf=""):
        return lambda rc, p: n((p or solo)[campo], suf)
    calc_tipos = lambda rc, p: ("todos" if len(rc["calculos"]) >= 5 else "atualização e prescrição") + f'<small>{n(rc["calculos_mes"])}/mês</small>'
    linhas = [
        '<tr class="tm-g"><th colspan="7">Preço</th></tr>',
        f'<tr><th scope="row">Por mês</th><td><b>sem custo no teste</b><small>depois, preço do Solo</small></td>' + "".join(
            f'<td><span class="tm-lanc"><b>{r(p["lancamento"])}</b><small>até {FIM} · cheio {r(p["cheio"])}</small></span><span class="tm-cheio" hidden><b>{r(p["cheio"])}</b></span>{"<small>por usuário</small>" if p["por_usuario"] else ""}</td>' for p in ps) + "</tr>",
        '<tr class="tm-g"><th colspan="7">Volume</th></tr>',
        lin("Usuários", lambda rc, p: "1" if not p else ("a partir de 2" if p["por_usuario"] else n(p["usuarios"]))),
        lin("Casos ativos", lim("casos")), lin("Minutas por mês", lim("minutas")), lin("Mensagens por mês", lim("mensagens")),
        lin("Armazenamento", lambda rc, p: n((p or solo)["armazenamento_gb"], " GB")),
        '<tr class="tm-g"><th colspan="7">No dia a dia</th></tr>',
        lin("Chat jurídico com fontes, leitura dos autos e minutas .docx", lambda rc, p: sim(True)),
        lin("Conferência das citações", lambda rc, p: sim(rc["citacoes"]), "selo verificado / não encontrado e link oficial; citação sem fonte sai antes da entrega"),
        lin("Plano de teses antes da minuta", lambda rc, p: sim(rc["teses"]), "você aprova as teses; a peça segue o plano"),
        lin("Monitor de processos por número CNJ", lambda rc, p: n(rc["monitor_cnj"]), "DataJud e Diário de Justiça Eletrônico"),
        lin("Monitor por OAB", lambda rc, p: n(rc["monitor_oab"])),
        lin("Prazos em dias úteis, agenda, tarefas e atendimentos", lambda rc, p: sim(rc["escritorio"])),
        lin("Cálculos com índices oficiais do Banco Central", calc_tipos, "memória de cálculo em PDF"),
        lin("Transcrição de áudio no servidor da Têmis", lambda rc, p: n(rc["transcricao_min_mes"], " min/mês")),
        lin("Modelos .docx próprios (papel timbrado)", lambda rc, p: n(rc["modelos"])),
        lin("Firma digital com o seu certificado ICP-Brasil", lambda rc, p: sim(rc["firmar"])),
        lin("Consulta de CNPJ em dados públicos", lambda rc, p: sim(rc["cnpj"])),
        '<tr class="tm-g"><th colspan="7">Equipe e agente</th></tr>',
        lin("Revisão adversarial, Protetora Leal e Auditoria", lambda rc, p: sim(p and p["id"] != "solo")),
        lin("Memória do Escritório, Radar Processual e convites de equipe", lambda rc, p: sim(p and p["id"] in ("escritorio", "max", "ultra"))),
        lin("Agente Têmis pessoal (memória e estilo do seu escritório)", lambda rc, p: sim(p and p["id"] in ("max", "ultra"))),
        lin("100% das Têmis, fila prioritária e Conselho das 4 (opcional)", lambda rc, p: sim(p and p["id"] == "ultra")),
    ]
    head = "<tr><th></th>" + "".join(f'<th scope="col">{c}</th>' for c, _, _ in cols) + "</tr>"
    return (f'<section class="sec" id="comparativo"><div class="wrap"><div class="sec-head"><p class="eyebrow">Comparativo</p><h2>O que cada plano entrega</h2></div>'
            f'<div class="tm-tab-w"><table class="tm-tab"><thead>{head}</thead><tbody>{"".join(linhas)}</tbody></table></div>'
            f'<p class="fine">Limites por mês. Minutas são rascunhos para revisão de advogado(a). Preços em reais, por mês, no plano mensal; anual com 15% de desconto. '
            f'Direito de arrependimento de 7 dias (CDC art. 49).</p></div></section>')

def faixa():
    return (f'<section class="sec tm-faixa"><div class="wrap"><div class="tm-lanc-box" role="status"><b>Preço de lançamento</b> · termina em '
            f'<span class="tm-cd" data-fim="{EP}">até {FIM}</span> <small>(até {FIM}, 23h59, horário de Brasília). Contratando até lá, o preço de lançamento vale por até 12 meses; '
            f'depois, a tabela em vigor, com aviso por e-mail 30 dias antes.</small></div>'
            f'<div class="tm-ess"><div><p class="eyebrow">Para começar</p><h2>Têmis Essencial — 7 dias para testar</h2>'
            f'<p>Sem custo no teste. 7 dias com o plano Solo e os recursos novos em versão de entrada (conferência das citações, 3 processos monitorados, '
            f'15 cálculos, plano de teses, 15 minutos de transcrição e 1 modelo .docx). O cartão só é pedido no fim do teste: sem cartão, o teste termina sozinho e nada é cobrado. '
            f'Um teste por CPF/CNPJ e por e-mail.</p></div><p><a class="btn" href="/conta/essencial">7 dias para testar ›</a></p></div></div></section>')

CSS = """<style>
.tm-preco{margin:.4rem 0 .6rem;font-size:1.05rem}.tm-preco b{font-size:1.6rem;color:#f0d58c}.tm-preco s{opacity:.6;margin-right:.3rem}
.tm-preco small,.tm-tab small{display:block;opacity:.75;font-size:.78rem;font-weight:400}
.tm-faixa .wrap{position:relative;z-index:5}.tm-lanc-box{backdrop-filter:blur(6px);border:1px solid #d4af5a;border-radius:14px;padding:14px 18px;background:#0b1a3acc;margin-bottom:18px}.tm-cd{color:#f0d58c;font-weight:700}
.tm-ess{display:flex;gap:18px;align-items:center;justify-content:space-between;flex-wrap:wrap;border:1.5px solid #e9c46a;border-radius:16px;padding:18px 22px;
 background:linear-gradient(135deg,#0b1a3a,#132b5c);box-shadow:0 0 0 1px #e9c46a33,0 10px 40px #d4af5a22}.tm-ess h2{margin:.2rem 0 .4rem}
.tm-tab-w{overflow-x:auto;border:1px solid #d4af5a55;border-radius:14px}.tm-tab{width:100%;border-collapse:collapse;min-width:860px;font-size:.92rem}
.tm-tab th,.tm-tab td{padding:9px 10px;border-bottom:1px solid #d4af5a22;text-align:center;vertical-align:top}.tm-tab th[scope=row]{text-align:left;font-weight:500}
.tm-tab thead th{position:sticky;top:0;background:#0b1a3a;color:#f0d58c}.tm-tab thead th:last-child{color:#0b1a3a;background:linear-gradient(135deg,#f6df9a,#d4af5a)}
.tm-tab .tm-g th{text-align:left;color:#f0d58c;background:#d4af5a14;font-size:.8rem;letter-spacing:.06em;text-transform:uppercase}
.tm-s{color:#f0d58c;font-weight:700}.tm-n{opacity:.45}
</style>"""
JS = ("<script>(()=>{const f=%d*1000;const p=n=>String(n).padStart(2,'0');const z=document.querySelectorAll('.tm-cd');"
      "const t=()=>{let s=Math.floor((f-Date.now())/1000);if(s<=0){document.querySelectorAll('.tm-lanc,.tm-faixa .tm-lanc-box').forEach(e=>e.hidden=true);"
      "document.querySelectorAll('.tm-cheio').forEach(e=>e.hidden=false);z.forEach(e=>e.textContent='encerrado');return false}"
      "const d=Math.floor(s/86400);s%%=86400;const h=Math.floor(s/3600);s%%=3600;const m=Math.floor(s/60);s%%=60;"
      "z.forEach(e=>e.textContent=`${d} dias ${p(h)}h ${p(m)}min ${p(s)}s`);return true};if(t())setInterval(t,1000)})()</script>") % EP

def main():
    f = OUT / "planos" / "index.html"
    if not f.exists(): print("[precos_pos] sem /planos/"); return
    s = f.read_text(encoding="utf-8")
    if MARCA in s: print("[precos_pos] já aplicado"); return
    s = s.replace("Os preços aparecem depois do login.", f"Preços de lançamento até {FIM}; o comparativo completo está logo abaixo.")
    s = re.sub(r'<a class="btn" href="/conta/cadastro">[^<]*</a><a class="btn btn-ghost" href="/conta/entrar\?volta=/conta/planos">[^<]*</a>',
               '<a class="btn" href="/conta/essencial">7 dias para testar</a><a class="btn btn-ghost" href="#comparativo">Comparar os planos ›</a>', s, count=1)
    n = 0
    for p in DADOS["planos"]:
        rx = re.compile(r'(<div id="(?:[^"]+"\s+id=")?' + re.escape("agente" if p["id"] == "max" else p["id"]) + r'"[^>]*>.*?<h2>[^<]*</h2>)', re.S)
        s, k = rx.subn(lambda m: m.group(1) + preco_html(p), s, 1); n += k
    if n != 5: raise SystemExit(f"[precos_pos] esperava 5 planos, achei {n}")
    i = s.find('</section>', s.find('class="hero hero-page"'))
    if i < 0: raise SystemExit("[precos_pos] sem hero")
    s = s[:i + 10] + faixa() + s[i + 10:]
    j = s.find('<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Além dos planos</p>')
    s = (s[:j] + tabela() + s[j:]) if j > 0 else s.replace("</main>", tabela() + "</main>", 1)
    s = s.replace("</head>", MARCA + CSS + "</head>", 1).replace("</body>", JS + "</body>", 1)
    f.write_text(s, encoding="utf-8"); print(f"[precos_pos] ok: {n} preços, faixa do lançamento, Essencial e comparativo em /planos/")

if __name__ == "__main__":
    main()
