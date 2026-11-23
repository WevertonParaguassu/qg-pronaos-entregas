#!/usr/bin/env python3
"""Troca o contato público do site para temis@e-pronaos.com no HTML gerado.

Roda no fim do build do Render, depois dos outros pós-processadores.
Não altera webhooks, SMTP interno nem o endereço de destino da caixa.
Rollback: apagar a linha do build.sh que chama este script.
"""
from __future__ import annotations

import sys
from pathlib import Path

OLD = "contato.pronaos@gmail.com"
NEW = "temis@e-pronaos.com"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
SUFIXOS = {".html", ".htm", ".txt", ".xml", ".json", ".js", ".css", ".md"}

def main() -> None:
    trocas = 0
    arquivos = 0
    for path in OUT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUFIXOS:
            continue
        try:
            texto = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        n = texto.count(OLD)
        if not n:
            continue
        path.write_text(texto.replace(OLD, NEW), encoding="utf-8")
        trocas += n
        arquivos += 1
    print(f"[contato_pos] arquivos={arquivos} trocas={trocas} contato={NEW}")

if __name__ == "__main__":
    main()
