#!/usr/bin/env python3
"""t2226u — seção pública «Veja uma triagem real» na home e em /planos/.

Copia os MP4 auto-hospedados e os cartazes para out/triagem/, injeta o bloco
(vídeo de mesa nas telas largas, vídeo de celular nas estreitas; preload=none,
poster). O PWA deve continuar por último no build.sh.

Rollback: apagar a linha deste arquivo no build.sh (os arquivos em
temis-site/triagem_t2226u_*.tgz.b64 podem ficar; não entram no site se o pos não rodar).
"""
from __future__ import annotations

import base64
import io
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath

VETADAS = re.compile(r"assinatura|gratuita|grátis", re.I)
PACOTES = ("triagem_t2226u_desktop.tgz.b64", "triagem_t2226u_mobile.tgz.b64")
BASE = Path(__file__).resolve().parent
ARQS = (
    "triagem-desktop.mp4",
    "triagem-mobile.mp4",
    "poster-desktop.jpg",
    "poster-mobile.jpg",
)

CSS = """<style id="tm-triagem-css">
.tm-triagem-demo{position:relative;z-index:4;scroll-margin-top:5.5rem}
.tm-triagem-demo .tm-triagem-lead{max-width:46rem}
.tm-triagem-frame{margin:1.2rem 0 0.6rem;border:1px solid rgba(201,166,70,.45);border-radius:16px;background:#081224;overflow:hidden;box-shadow:0 12px 40px rgba(7,20,43,.45)}
.tm-triagem-vid{width:100%;height:auto;display:block;background:#081224;vertical-align:middle}
.tm-triagem-mob{display:none}
.tm-triagem-nota{font-size:.92rem;color:#a9b6d3;margin:.7rem 0 0}
@media (max-width:760px){
  .tm-triagem-desk{display:none}
  .tm-triagem-mob{display:block;max-height:80vh;width:auto;max-width:100%;margin:0 auto}
  .tm-triagem-frame{background:#081224;display:flex;justify-content:center}
}
</style>
"""

SECAO = """<section class="sec tm-triagem-demo" id="veja-uma-triagem"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Como funciona</p><h2>Veja uma triagem real</h2></div>
<p class="tm-triagem-lead">Uma triagem de ponta a ponta na Têmis, com documento fictício e dados mascarados. O Conselho das 4 identifica a área, o que se pede, os pontos fortes, os riscos e o próximo passo. Não é um caso real.</p>
<div class="tm-triagem-frame">
<video class="tm-triagem-vid tm-triagem-desk" controls preload="none" playsinline poster="/triagem/poster-desktop.jpg" width="1920" height="1080" aria-label="Triagem na Têmis, em tela grande">
<source src="/triagem/triagem-desktop.mp4" type="video/mp4">
</video>
<video class="tm-triagem-vid tm-triagem-mob" controls preload="none" playsinline poster="/triagem/poster-mobile.jpg" width="390" height="844" aria-label="Triagem na Têmis, no celular">
<source src="/triagem/triagem-mobile.mp4" type="video/mp4">
</video>
</div>
<p class="tm-triagem-nota">Amostra didática. Documento e pessoas são fictícios; CPF e CNPJ aparecem mascarados. <a href="/conta/comecar">Comece por aqui</a> · <a href="/conta/cadastro">Criar conta</a></p>
</div></section>
"""

HOME_ALVO = '<section class="sec" id="teste">'
PLANOS_ALVO = '<section class="sec" id="o-que-e">'


def _checa(txt: str, onde: str) -> None:
    m = VETADAS.search(txt)
    if m:
        raise SystemExit(f"[triagem_t2226u] palavra vetada «{m.group(0)}» em {onde}")


def copia_assets(out: Path) -> None:
    dest = out / "triagem"
    dest.mkdir(parents=True, exist_ok=True)
    for nome in PACOTES:
        inteiro = BASE / nome
        partes = sorted(BASE.glob(nome + ".p[0-9][0-9]"))
        if partes:
            texto = "".join(p.read_text() for p in partes)
        elif inteiro.is_file():
            texto = inteiro.read_text()
        else:
            raise SystemExit(f"[triagem_t2226u] pacote ausente: {nome} (nem partes .pXX)")
        raw = base64.b64decode("".join(texto.split()).encode("ascii"))
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
            for m in tf.getmembers():
                if not m.isfile():
                    continue
                name = PurePosixPath(m.name).name
                if name not in ARQS or ".." in Path(m.name).parts:
                    continue
                f = tf.extractfile(m)
                if f is None:
                    continue
                alvo = dest / name
                alvo.write_bytes(f.read())
                print(f"[triagem_t2226u] copiou {name} ({alvo.stat().st_size} bytes)")
    faltando = [n for n in ARQS if not (dest / n).is_file()]
    if faltando:
        raise SystemExit(f"[triagem_t2226u] faltam no pacote: {', '.join(faltando)}")


def injeta(html: str, alvo: str, onde: str) -> str:
    if "tm-triagem-css" not in html:
        if "</head>" not in html:
            raise SystemExit(f"[triagem_t2226u] </head> ausente em {onde}")
        html = html.replace("</head>", CSS + "</head>", 1)
    if 'id="veja-uma-triagem"' in html:
        # regrava o bloco (idempotente, pega atualizações)
        html = re.sub(
            r'<section class="sec tm-triagem-demo" id="veja-uma-triagem">.*?</section>\s*',
            SECAO,
            html,
            count=1,
            flags=re.S,
        )
        _checa(CSS + SECAO, onde)
        return html
    if alvo not in html:
        raise SystemExit(f"[triagem_t2226u] âncora não encontrada em {onde}: {alvo}")
    html = html.replace(alvo, SECAO + alvo, 1)
    _checa(CSS + SECAO, onde)
    return html


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("uso: triagem_t2226u_pos.py OUT")
    out = Path(sys.argv[1]).resolve()
    if not (out / "index.html").is_file():
        raise SystemExit(f"[triagem_t2226u] {out}/index.html ausente")
    copia_assets(out)
    home = out / "index.html"
    s = home.read_text(encoding="utf-8")
    s2 = injeta(s, HOME_ALVO, "home")
    if s2 != s:
        home.write_text(s2, encoding="utf-8")
        print("[triagem_t2226u] home: seção Veja uma triagem real")
    else:
        print("[triagem_t2226u] home: já estava")
    planos = out / "planos" / "index.html"
    if not planos.is_file():
        raise SystemExit("[triagem_t2226u] out/planos/index.html ausente")
    s = planos.read_text(encoding="utf-8")
    s2 = injeta(s, PLANOS_ALVO, "/planos/")
    if s2 != s:
        planos.write_text(s2, encoding="utf-8")
        print("[triagem_t2226u] /planos/: seção Veja uma triagem real")
    else:
        print("[triagem_t2226u] /planos/: já estava")


if __name__ == "__main__":
    main()
