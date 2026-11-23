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
troca("index.html", "com OCR e modelo locais. Detalhes em Segurança e sigilo.",
      "com OCR e modelos locais por padrão. " + FRASE + " Detalhes em Segurança e sigilo.")
troca("privacidade/index.html", "OCR e modelo locais.", "OCR e modelos locais por padrão. " + FRASE)
s_rel = "seguranca/index.html"; p = OUT / s_rel
if p.exists():
    s = p.read_text(encoding="utf-8")
    if MARCA not in s:
        i = s.find("<li><strong>Cadeado de privacidade.</strong>")
        j = s.find("</li>", i) if i >= 0 else -1
        if j >= 0:
            s = s[:j + 5] + LI + s[j + 5:]
            s = s.replace("e um cadeado que impede dado de cliente em ferramenta externa.",
                          "e um cadeado que impede dado de cliente em ferramenta externa. No Ultra, com opt-in por caso, só uma pergunta anonimizada vai ao conselho de IAs externas.")
            p.write_text(s, encoding="utf-8"); n += 1
        else: print("[privacidade_pos] aviso: item do cadeado não achado em seguranca")
print(f"[privacidade_pos] ok: {n} página(s) atualizada(s) (Conselho das 4 com opt-in e anonimização)")
