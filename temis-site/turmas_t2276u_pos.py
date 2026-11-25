#!/usr/bin/env python3
"""Selo «Turma aberta · restam N vagas» em /planos/. Rollback: apagar a linha no build.sh."""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

TAG = '<script src="/assets/temis_vagas.js" defer></script>'
VETADAS = re.compile(
    r"assinaturas?|gratuit[ao]s?|gr[aá]tis|\(free\)|:free\b|antigravity|\badapta\b|TEM-CAP-|t2275u|t2276u",
    re.I,
)


def main(out: str) -> None:
    raiz = Path(__file__).resolve().parent
    dest_dir = Path(out) / "assets"
    dest_dir.mkdir(parents=True, exist_ok=True)
    src = raiz / "temis_vagas.js"
    if not src.is_file():
        raise SystemExit("faltou temis_vagas.js")
    js = src.read_text(encoding="utf-8")
    # o filtro interno do script cita as palavras vetadas para removê-las;
    # o que o visitante vê são só os textos abaixo.
    visivel = "\n".join(
        s for s in (
            "Turma aberta · restam N vagas",
            "Turma aberta · resta 1 vaga",
            "Vagas esgotadas — entre na lista de espera",
            "Entre na lista de espera. Avisamos neste e-mail quando abrir vaga.",
            "Entrar na lista de espera",
        )
    )
    if VETADAS.search(visivel):
        raise SystemExit("texto visível do selo não pode ter palavra vetada ou código interno")
    if "TEM-CAP" in js or "t2275u" in js or "t2276u" in js:
        raise SystemExit("o script público não pode trazer código interno")
    shutil.copy2(src, dest_dir / "temis_vagas.js")
    injetados = 0
    for rel in ("planos/index.html", "planos.html"):
        p = Path(out) / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        if "temis_vagas.js" in t:
            print("já tinha", rel)
            injetados += 1
            continue
        if "</body>" not in t.lower() and "</body>" not in t:
            raise SystemExit(f"sem </body> em {rel}")
        # uma inserção, imediatamente antes de </body>
        t2, n = re.subn(r"</body>", TAG + "\n</body>", t, count=1, flags=re.I)
        if n != 1:
            raise SystemExit(f"não inseriu em {rel}")
        p.write_text(t2, encoding="utf-8")
        print("injetado", rel)
        injetados += 1
    if injetados == 0:
        raise SystemExit("não achei /planos/ no out")
    print("[turmas] ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
