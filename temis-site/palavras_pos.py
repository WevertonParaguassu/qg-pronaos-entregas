#!/usr/bin/env python3
"""t2198u — sem «assinatura», «gratuita» ou «grátis» no texto visível do site (diretriz do Weverton). Troca só texto e
atributos de leitura (title/alt/aria-label/content de description); URLs ficam iguais. Chamada aprovada: «7 dias para testar»
ou «sem custo no teste». Também tira o «preço após o login» dos planos (a tabela agora é pública). Rollback: apagar a linha no build.sh."""
import re, sys
from pathlib import Path
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
T = [
    ("Teste grátis, um por CPF ou CNPJ · planos e preços após o login", "Sem custo no teste, um por CPF ou CNPJ · planos e preços na página Planos"),
    ("Começar o teste grátis", "Começar sem custo no teste"),
    ("Experimentar no teste grátis", "Experimentar sem custo no teste"),
    ("Um teste grátis por CPF ou CNPJ, sem cartão.", "Sem custo no teste, um por CPF ou CNPJ, sem cartão."),
    ("Comece pelo teste grátis", "Comece sem custo no teste"),
    ("Teste grátis por CPF ou CNPJ", "Sem custo no teste, um por CPF ou CNPJ,"),
    ("a partir do teste grátis", "a partir do teste sem custo"),
    ("acompanha o teste grátis", "acompanha o teste sem custo"),
    ("peça a sua amostra grátis", "comece sem custo no teste"),
    ("amostra gratuita", "teste sem custo"),
    ("Teste grátis", "Sem custo no teste"),
    ("teste grátis", "teste sem custo"),
    ("Para ver os valores e assinar, entre na sua conta.", "Para contratar, entre na sua conta."),
    ("sem assinar o plano inteiro", "sem contratar o plano inteiro"),
    ("Os preços de cada aplicação e dos planos aparecem depois do login.", "Os preços dos planos estão na página Planos; os de cada aplicação aparecem depois do login."),
]
GEN = [(re.compile(r"\bgrátis\b"), "sem custo"), (re.compile(r"\bGrátis\b"), "Sem custo"), (re.compile(r"\bgratuita\b"), "sem custo"),
       (re.compile(r"\bGratuita\b"), "Sem custo"), (re.compile(r"\bassinatura\b"), "contratação"), (re.compile(r"\bAssinatura\b"), "Contratação")]
def troca(x):
    for a, b in T: x = x.replace(a, b)
    for rx, b in GEN: x = rx.sub(b, x)
    return x
def limpa(doc):
    partes = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", doc, flags=re.S | re.I)
    for i, s in enumerate(partes):
        if i % 2 == 0: partes[i] = troca(s)
        elif not re.match(r"<(script|style)\b", s, re.I):
            partes[i] = re.sub(r'(\b(?:title|alt|aria-label|content|placeholder)=")([^"]*)(")', lambda m: m.group(1) + troca(m.group(2)) + m.group(3), s)
    return "".join(partes)
def main():
    n = 0
    for f in OUT.rglob("*.html"):
        s = f.read_text(encoding="utf-8"); t = limpa(s)
        if t != s: f.write_text(t, encoding="utf-8"); n += 1
    print(f"[palavras_pos] ok: {n} páginas sem as palavras vetadas")
if __name__ == "__main__":
    main()
