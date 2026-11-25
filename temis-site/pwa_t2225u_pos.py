#!/usr/bin/env python3
"""t2225u · PWA instalável da Têmis (último passo do build.sh).

Gera manifesto, ícones (any + maskable, azul e dourado), service worker com
cascão offline seguro (NUNCA guarda respostas autenticadas, /api, /conta,
/painel, /estacao, nem documentos de cliente — LGPD), página offline,
assetlinks.json do TWA Android, botão «Instalar o app Têmis» e dica no iOS
«Adicionar à Tela de Início».

Idempotente (marca t2225u-pwa). Rollback: apagar a linha deste script no build.sh.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import tarfile
import io
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
HERE = Path(__file__).parent
MARCA = "t2225u-pwa"
PKG = "com.agentetemis.app"
# Impressões públicas dos certificados (TWA). Não são segredo.
# 1) chave de upload (keystore local)
# 2) certificado com que a Play assina o app (App Signing)
SHA256_UPLOAD = "5F:AA:F3:E8:29:B0:53:04:55:1E:41:96:B9:4F:D7:C7:DA:83:CF:BA:3D:73:BB:77:41:33:E5:F2:3E:29:C5:D6"
SHA256_PLAY = "51:04:E5:A8:0B:59:D0:B4:63:53:25:CF:93:F4:47:72:39:A7:02:0D:FD:AC:E0:B1:A4:A1:65:1C:5A:CD:C9:07"
SHA256S = [SHA256_UPLOAD, SHA256_PLAY]
ORIGEM = "https://agentetemis.com"

MANIFEST = {
    "id": ORIGEM + "/",
    "name": "Têmis",
    "short_name": "Têmis",
    "description": "Aplicativos Têmis para o trabalho jurídico: análise de documentos, pesquisa e minutas para revisão profissional.",
    "lang": "pt-BR",
    "dir": "ltr",
    "start_url": "/conta/entrar?fonte=pwa",
    "scope": "/",
    "display": "standalone",
    "display_override": ["standalone", "minimal-ui", "browser"],
    "orientation": "any",
    "background_color": "#060D1B",
    "theme_color": "#060D1B",
    "categories": ["business", "productivity"],
    "prefer_related_applications": False,
    "icons": [
        {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-192-maskable.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        {"src": "/apple-touch-icon.png?v=t2225u", "sizes": "180x180", "type": "image/png", "purpose": "any"},
    ],
    "shortcuts": [
        {"name": "Entrar", "short_name": "Entrar", "url": "/conta/entrar?fonte=pwa", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192"}]},
        {"name": "Planos", "short_name": "Planos", "url": "/planos/", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192"}]},
        {"name": "Estação", "short_name": "Estação", "url": "/api/estacao/pagina", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192"}]},
    ],
}

ASSETLINKS = [
    {
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": PKG,
            "sha256_cert_fingerprints": SHA256S,
        },
    }
]

SW_JS = r"""/* t2225u-pwa · service worker da Têmis
   Cascão offline do site público. NUNCA guarda:
   - /conta, /api, /painel, /login, /sair, /estacao
   - documentos de cliente (pdf, docx, zip, p7s…)
   - respostas com Content-Disposition, Cache-Control: private/no-store
   - POST/PUT/PATCH/DELETE
   LGPD: documentos não ficam neste aparelho.
*/
const VER = "temis-pwa-t2225u-v1";
const SHELL = [
  "/offline.html",
  "/manifest.webmanifest",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/icon-192-maskable.png",
  "/icons/icon-512-maskable.png",
  "/favicon.svg",
];
const PRIV = /^\/(?:conta|api|painel|login|sair|estacao)(?:\/|$)/i;
const DOC = /\.(pdf|docx?|odt|rtf|xlsx?|csv|zip|p7s|p7m|eml)(?:\?|$)/i;
const DOC_PATH = /\/(?:download|uploads?|docs?|documentos?|anexo|arquivos?)(?:\/|$)/i;
const ASSET = /^\/(?:assets|img|icons)\//i;

function sameOrigin(url) {
  try { return new URL(url, self.location.href).origin === self.location.origin; }
  catch (e) { return false; }
}
function isPrivate(url) {
  const u = new URL(url, self.location.href);
  if (u.origin !== self.location.origin) return true;
  return PRIV.test(u.pathname) || DOC.test(u.pathname) || DOC_PATH.test(u.pathname);
}
function isAsset(url) {
  const u = new URL(url, self.location.href);
  return u.origin === self.location.origin && (ASSET.test(u.pathname) || /^\/favicon/.test(u.pathname) || /^\/apple-touch-icon/.test(u.pathname) || /^\/manifest\./.test(u.pathname) || u.pathname === "/offline.html");
}
function podeCachear(res) {
  if (!res || !res.ok || res.type !== "basic") return false;
  const ct = (res.headers.get("content-type") || "").toLowerCase();
  if (/pdf|zip|msword|officedocument|octet-stream|spreadsheet|csv/.test(ct)) return false;
  if (res.headers.get("content-disposition")) return false;
  const cc = res.headers.get("cache-control") || "";
  if (/no-store|private/i.test(cc)) return false;
  const len = parseInt(res.headers.get("content-length") || "0", 10);
  if (len > 5 * 1024 * 1024) return false;
  return true;
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(VER).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== VER).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET" && req.method !== "HEAD") return;
  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.protocol !== "http:" && url.protocol !== "https:") return;
  if (!sameOrigin(req.url)) return;

  if (isPrivate(req.url)) {
    if (req.mode === "navigate") {
      event.respondWith(fetch(req).catch(() => caches.match("/offline.html")));
    }
    return;
  }

  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (podeCachear(res)) {
            const copia = res.clone();
            caches.open(VER).then((c) => c.put(req, copia));
          }
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match("/offline.html")))
    );
    return;
  }

  if (isAsset(req.url)) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const rede = fetch(req)
          .then((res) => {
            if (podeCachear(res)) {
              const copia = res.clone();
              caches.open(VER).then((c) => c.put(req, copia));
            }
            return res;
          })
          .catch(() => cached);
        return cached || rede;
      })
    );
    return;
  }
});
"""

OFFLINE_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#060D1B">
<meta name="robots" content="noindex">
<title>Sem conexão · Têmis</title>
<link rel="manifest" href="/manifest.json">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root{--bg:#060D1B;--gold:#BF9B4E;--gold-l:#D9BC7A;--gold-s:#FFE3A0;--ink:#C7CEDD;--head:#EDE4CC}
  html,body{margin:0;min-height:100%;background:linear-gradient(180deg,#0A1630 0%,#060D1B 60%) no-repeat,var(--bg);color:var(--ink);font:350 1rem/1.65 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
  main{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem 1.4rem;text-align:center}
  svg{width:96px;height:96px;margin-bottom:1.2rem}
  h1{font-family:Georgia,serif;font-weight:400;font-size:1.8rem;color:var(--head);margin:0 0 .6rem}
  h1 em{font-style:italic;color:var(--gold-l)}
  p{max-width:32rem;margin:0 0 1.4rem}
  a,button{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:.8rem 1.5rem;border-radius:999px;background:var(--gold);color:var(--bg);font:600 .95rem/1 system-ui,sans-serif;text-decoration:none;border:0;cursor:pointer}
  a:hover,button:hover{background:var(--gold-l)}
</style>
</head>
<body>
<main>
  <svg viewBox="0 0 64 64" aria-hidden="true">
    <rect width="64" height="64" rx="32" fill="#0B1A33"/>
    <circle cx="32" cy="32" r="30.2" fill="none" stroke="#E0C078" stroke-width="2.2"/>
    <g fill="none" stroke="#E0C078" stroke-width="2.35" stroke-linecap="round" stroke-linejoin="round">
      <path d="M32 11v34"/><path d="M18 49h28"/><path d="M14 20h36"/>
      <path d="M14 20 7 36h14z"/><path d="M50 20l-7 16h14z"/>
    </g>
  </svg>
  <h1>Sem conexão. <em>A Têmis espera você.</em></h1>
  <p>O app Têmis não guarda documentos neste aparelho. Quando a rede voltar, entre de novo para seguir o trabalho.</p>
  <button type="button" onclick="location.reload()">Tentar de novo</button>
</main>
</body>
</html>
"""

PWA_CSS = """/* t2225u-pwa · botão Instalar o app Têmis e dica no iOS */
#temis-pwa-bar{position:fixed;z-index:240;right:16px;bottom:16px;max-width:min(26rem,calc(100vw - 32px));
  background:rgba(6,13,27,.92);border:1px solid rgba(191,155,78,.45);border-radius:16px;
  box-shadow:0 12px 40px rgba(0,0,0,.35);padding:12px 14px;color:#C7CEDD;
  font:350 14px/1.45 "InterV",system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased;
  display:flex;flex-direction:column;gap:10px;backdrop-filter:blur(10px)}
#temis-pwa-bar[hidden]{display:none!important}
#temis-pwa-bar p{margin:0;color:#EDE4CC}
#temis-pwa-bar p strong{font-weight:600;color:#FFE3A0}
#temis-pwa-acoes{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:flex-end}
#temis-pwa-bar button,#temis-pwa-bar .temis-pwa-instalar{
  display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:.55rem 1.05rem;
  border-radius:999px;border:1px solid #BF9B4E;background:#BF9B4E;color:#060D1B;
  font:600 .9rem/1 "InterV",system-ui,sans-serif;cursor:pointer;text-decoration:none}
#temis-pwa-bar button.temis-pwa-depois{background:transparent;color:#D9BC7A}
#temis-pwa-bar button.temis-pwa-depois:hover{background:rgba(191,155,78,.12)}
#temis-pwa-bar button:hover,#temis-pwa-bar .temis-pwa-instalar:hover{background:#D9BC7A}
@media (display-mode: standalone),(display-mode: minimal-ui){#temis-pwa-bar{display:none!important}}
@media (prefers-reduced-motion:reduce){#temis-pwa-bar{transition:none}}
"""

PWA_JS = r"""/* t2225u-pwa · registra o service worker, botão Instalar o app Têmis e dica no iOS */
(function(){
  if (window.__temisPwa) return; window.__temisPwa = 1;
  var K = "temis-pwa-dismiss-t2225u";
  try {
    if (window.matchMedia && (window.matchMedia("(display-mode: standalone)").matches || window.matchMedia("(display-mode: minimal-ui)").matches)) return;
  } catch (e) {}
  if (window.navigator && window.navigator.standalone) return;

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function(){
      navigator.serviceWorker.register("/sw.js", {scope: "/"}).catch(function(){});
    });
  }

  var dismissed = false;
  try { dismissed = localStorage.getItem(K) === "1"; } catch (e) {}

  var ua = navigator.userAgent || "";
  var ios = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  var iosSafari = ios && !/CriOS|FxiOS|EdgiOS|OPiOS|DuckDuckGo/.test(ua);

  var deferred = null;
  window.addEventListener("beforeinstallprompt", function(ev){
    ev.preventDefault();
    deferred = ev;
    if (!dismissed) show("chrome");
  });

  function show(kind){
    if (document.getElementById("temis-pwa-bar")) return;
    var bar = document.createElement("div");
    bar.id = "temis-pwa-bar";
    bar.setAttribute("role", "dialog");
    bar.setAttribute("aria-label", "Instalar o app Têmis");
    var texto = kind === "ios"
      ? "<p>Para ter o <strong>app Têmis</strong> neste iPhone ou iPad: toque em <strong>Compartilhar</strong> e depois em <strong>Adicionar à Tela de Início</strong>.</p>"
      : "<p>Instale o <strong>app Têmis</strong> e abra o trabalho jurídico direto da tela inicial.</p>";
    bar.innerHTML = texto + '<div id="temis-pwa-acoes"></div>';
    var acoes = bar.querySelector("#temis-pwa-acoes");
    if (kind !== "ios") {
      var inst = document.createElement("button");
      inst.type = "button";
      inst.className = "temis-pwa-instalar";
      inst.textContent = "Instalar o app Têmis";
      inst.addEventListener("click", function(){
        if (!deferred) return;
        deferred.prompt();
        deferred.userChoice.finally(function(){ deferred = null; hide(true); });
      });
      acoes.appendChild(inst);
    }
    var depois = document.createElement("button");
    depois.type = "button";
    depois.className = "temis-pwa-depois";
    depois.textContent = "Agora não";
    depois.addEventListener("click", function(){ hide(true); });
    acoes.appendChild(depois);
    document.body.appendChild(bar);
  }
  function hide(lembrar){
    var bar = document.getElementById("temis-pwa-bar");
    if (bar) bar.remove();
    if (lembrar) { try { localStorage.setItem(K, "1"); } catch (e) {} }
  }

  if (!dismissed && iosSafari) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function(){ show("ios"); });
    else show("ios");
  }
})();
"""

HEAD = f"""<!-- {MARCA} -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#060D1B">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Têmis">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=t2225u" sizes="180x180">
<link rel="stylesheet" href="/assets/temis-pwa.css?v=1">
"""

SCRIPT = f'<script defer src="/assets/temis-pwa.js?v=1" data-m="{MARCA}"></script>'


def extrai_icones(dest: Path) -> int:
    b64 = HERE / "pwa_icons_t2225u.tgz.b64"
    if not b64.is_file():
        raise SystemExit(f"faltou {b64}")
    raw = base64.b64decode(b64.read_text().encode("ascii"))
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            nome = Path(m.name).name
            if nome not in {
                "icon-192.png", "icon-512.png",
                "icon-192-maskable.png", "icon-512-maskable.png",
                "apple-touch-icon.png", "icon-96.png", "icon-32.png",
            }:
                continue
            f = tf.extractfile(m)
            if not f:
                continue
            data = f.read()
            if nome == "apple-touch-icon.png":
                (dest.parent / "apple-touch-icon.png").write_bytes(data)
            (dest / nome).write_bytes(data)
            n += 1
    return n


def injeta(html: str) -> str:
    if MARCA in html:
        return html
    s = html
    # evita theme-color duplicado: se já houver, o nosso ainda entra (mesmo valor)
    if "</head>" in s:
        s = s.replace("</head>", HEAD + "</head>", 1)
    if "</body>" in s:
        s = s.replace("</body>", SCRIPT + "\n</body>", 1)
    elif s.rstrip().endswith("</html>"):
        s = s.rstrip()[:-7] + SCRIPT + "</html>"
    return s


def main() -> None:
    if not OUT.is_dir():
        raise SystemExit(f"pasta de saída inexistente: {OUT}")
    icons = OUT / "icons"
    n_ic = extrai_icones(icons)
    (OUT / "manifest.webmanifest").write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "manifest.json").write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "sw.js").write_text(SW_JS, encoding="utf-8")
    (OUT / "offline.html").write_text(OFFLINE_HTML, encoding="utf-8")
    assets = OUT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "temis-pwa.css").write_text(PWA_CSS, encoding="utf-8")
    (assets / "temis-pwa.js").write_text(PWA_JS, encoding="utf-8")
    well = OUT / ".well-known"
    well.mkdir(exist_ok=True)
    (well / "assetlinks.json").write_text(
        json.dumps(ASSETLINKS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    n_html = 0
    for p in OUT.rglob("*.html"):
        if p.name == "offline.html":
            continue
        s0 = p.read_text(encoding="utf-8")
        s1 = injeta(s0)
        if s1 != s0:
            p.write_text(s1, encoding="utf-8")
            n_html += 1
    print(f"[t2225u-pwa] icones={n_ic} html={n_html} ok")


if __name__ == "__main__":
    main()
