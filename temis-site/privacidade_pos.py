#!/usr/bin/env python3
"""Privacidade honesta com o Conselho das 4 (t1942u/t1944u, 23/11/2026). Roda depois dos outros *_pos.py.
Texto do Weverton: documentos ficam nos servidores da PRONAOS e, por padrão, passam só por modelos locais; no Ultra, com o opt-in
do cliente por caso, uma versão anonimizada (sem nomes, CPF/CNPJ, número de processo ou fatos que identifiquem alguém) pode ser
consultada com um conselho de IAs externas. Idempotente: não repete se já aplicado. Rollback: apagar a linha dele no build.sh."""
import pathlib, sys
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
MARCA = "<!--conselho-privacidade-->"
FRASE = ("No plano Ultra, só com o opt-in do cliente em cada caso, uma versão anonimizada da pergunta (sem nomes, CPF/CNPJ, "
         "número de processo ou fatos que identifiquem alguém) pode ser consultada com um conselho de IAs externas; os documentos não saem.")
LI = ('<li><strong>Conselho das 4 (só no Ultra, só com opt-in).</strong> Por padrão, tudo fica nos servidores da PRONAOS e passa só por modelos locais. '
      'No plano Ultra, se o cliente ativar o Conselho das 4 naquele caso, a Têmis reescreve a pergunta aqui mesmo, sem nomes, CPF/CNPJ, número de processo, '
      'endereço ou fatos que identifiquem alguém, e só essa versão anonimizada é consultada com quatro IAs externas (ChatGPT, Gemini, Claude e Grok). '
      'Os documentos do caso nunca saem dos nossos servidores. A guarda do cadeado confere a pergunta antes de sair e bloqueia o envio se ainda houver dado do caso. '
      'A resposta volta mostrando onde as quatro concordam, onde divergem e quem disse o quê, e os artigos citados são conferidos no texto oficial da lei. '
      'O cliente desliga quando quiser.</li>' + MARCA)
n = 0
def troca(rel, velho, novo):
    global n
    p = OUT / rel
    if not p.exists(): print(f"[privacidade_pos] aviso: {rel} não existe"); return
    s = p.read_text(encoding="utf-8")
    if MARCA in s or novo in s: return
    if velho not in s: print(f"[privacidade_pos] aviso: trecho não achado em {rel}: {velho[:50]}…"); return
    p.write_text(s.replace(velho, novo), encoding="utf-8"); n += 1
troca("index.html", "os documentos vão para a plataforma própria, na VPS4, com OCR e modelo locais. Detalhes em Segurança e sigilo.",
      "os documentos ficam nos servidores da própria PRONAOS e, por padrão, são lidos só pelos modelos que rodam lá. " + FRASE + " Detalhes em Segurança e sigilo.")
troca("privacidade/index.html", "OCR e modelo locais.", "OCR e modelos locais por padrão. " + FRASE)

# Página Segurança reescrita para leigos (t1952u/t1953u): sem nomes de servidores, modelos ou mecanismos internos.
# O item "Conselho das 4 (só no Ultra, só com opt-in)" (LI) fica IGUAL, palavra por palavra.
DESC_SEG = "Os documentos do seu cliente ficam nos servidores da PRONAOS, num espaço só do seu escritório, e não são usados para treinar IA."
LEAD_SEG = "A Têmis foi feita para o trabalho jurídico, em que guardar segredo é dever. Veja, em poucas palavras, como cuidamos dos documentos do seu cliente."
CORPO_SEG = (
 '<section class="sec"><div class="wrap prose">'
 '<h2>Onde ficam os documentos</h2>'
 '<p>Os documentos que você envia ficam nos servidores da própria PRONAOS, num espaço só do seu escritório. Este site público não recebe arquivos de clientes. '
 'Os formulários abertos (sugestões e afiliados) servem só para mensagens: não envie documentos de processo por eles.</p>'
 '<h2>Cada escritório no seu espaço</h2>'
 '<p>Um escritório não vê os casos, os documentos nem a memória de outro. Testamos essa separação antes de abrir a plataforma.</p>'
 '<h2>Quem lê os documentos</h2>'
 '<p>Por padrão, a leitura e a análise acontecem só nos nossos servidores, com modelos de inteligência artificial que rodam lá dentro. '
 'Os documentos do cliente não são enviados a ferramentas de IA de fora.</p>'
 '<h2>Cadeado de privacidade</h2>'
 '<p>Quando a Têmis usa uma ferramenta externa, ela só pode mandar texto genérico. O cadeado barra dados pessoais, como CPF, números de documentos, '
 'dados de saúde e trechos do processo.</p>'
 '<h2>Conselho das 4</h2><ul>' + LI + '</ul>'
 '<h2>Seus documentos não treinam IA</h2>'
 '<p>Não usamos documentos de clientes para treinar modelos de IA. Também não vendemos nem compartilhamos esses documentos com ninguém.</p>'
 '<h2>Histórico para conferir</h2>'
 '<p>O escritório pode ver o que a Têmis fez em cada tarefa: o que ela consultou e por quê.</p>'
 '<h2>O que a Têmis não faz</h2>'
 '<p>Não protocola, não assina e não entra em sistema de tribunal. Toda peça é uma minuta para revisão do advogado ou da advogada. Não prometemos resultado.</p>'
 '<h2>Seus direitos (LGPD)</h2>'
 '<p>Coletamos só o necessário e para uma finalidade clara. Para pedir acesso, correção ou exclusão dos seus dados, escreva para '
 '<a href="mailto:contato.pronaos@gmail.com">contato.pronaos@gmail.com</a>.</p>'
 '</div></section>' + MARCA)
p = OUT / "seguranca/index.html"
if p.exists():
    s = p.read_text(encoding="utf-8")
    if MARCA not in s:
        import re
        a = s.find('<section class="sec"><div class="wrap prose">'); b = s.find("</main>", a)
        if a >= 0 and b >= 0:
            s = s[:a] + CORPO_SEG + s[b:]
            s = re.sub(r'(<p class="lead">)[^<]*(</p>)', lambda m: m.group(1) + LEAD_SEG + m.group(2), s, count=1)
            s = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*(")', lambda m: m.group(1) + DESC_SEG + m.group(2), s)
            p.write_text(s, encoding="utf-8"); n += 1
        else: print("[privacidade_pos] aviso: corpo da página Segurança não achado")
print(f"[privacidade_pos] ok: {n} página(s) atualizada(s) (Segurança para leigos + Conselho das 4 com opt-in e anonimização)")
