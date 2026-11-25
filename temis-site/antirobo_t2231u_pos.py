#!/usr/bin/env python3
"""t2231u (v2, 25/11/2026): robôs de TREINO de IA fora do site; robôs de BUSCA/RESPOSTA de IA podem ler só as páginas públicas
(para a Têmis ser citada), nunca a área logada. Buscadores comuns (Google, Bing) seguem indexando.
A área logada (/conta, /painel, /api, /login, /sair) também é barrada no Caddy da VPS1 para qualquer robô de IA.
Rollback: apagar a linha do antirobo_t2231u_pos.py no build.sh."""
import pathlib, sys, json, re
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
TREINO = ["GPTBot", "CCBot", "ClaudeBot", "Claude-Web", "anthropic-ai", "Google-Extended", "Applebot-Extended", "Bytespider",
          "Amazonbot", "meta-externalagent", "meta-externalfetcher", "FacebookBot", "Diffbot", "cohere-ai", "cohere-training-data-crawler",
          "ImagesiftBot", "Omgilibot", "omgili", "Timpibot", "PetalBot", "AI2Bot", "Ai2Bot-Dolma", "PanguBot", "Scrapy", "img2dataset",
          "webzio-extended", "FirecrawlAgent", "Crawl4AI", "ChatGLM-Spider", "iaskspider", "Kangaroo Bot", "Brightbot", "SemrushBot-OCOB",
          "VelenPublicWebCrawler", "Novellum", "Andibot", "bedrockbot", "TikTokSpider", "QualifiedBot", "LinerBot", "Quora-Bot",
          "magpie-crawler", "Sidetrade indexer bot", "Factset_spyderbot", "Cotoyogi", "YouBot", "MistralAI-User", "Claude-User",
          "Claude-SearchBot", "GoogleOther"]
BUSCA = ["OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "Applebot", "DuckAssistBot", "Bingbot"]
PRIVADO = ["/conta", "/conta/", "/painel", "/api/", "/billing", "/billing/", "/login", "/sair", "/teste-gratis", "/teste-gratis/",
           "/uploads/", "/estacao"]
rb = out / "robots.txt"
atual = rb.read_text() if rb.exists() else "User-agent: *\nAllow: /\n"
atual = re.sub(r"(?s)^# t2231u.*?\n\n(?=User-agent: \*)", "", atual)  # idempotente (tira bloco antigo)
dis_atuais = re.findall(r"(?m)^Disallow:\s*(\S+)", atual)
priv = list(dict.fromkeys(PRIVADO + dis_atuais))
bloco = ("# t2231u: robôs de TREINO de IA não entram na Têmis.\n" + "".join(f"User-agent: {b}\n" for b in TREINO) + "Disallow: /\n\n"
         "# t2231u: robôs de BUSCA/RESPOSTA de IA podem ler as páginas públicas (para citar a Têmis), nunca a área logada.\n"
         + "".join(f"User-agent: {b}\n" for b in BUSCA) + "".join(f"Disallow: {d}\n" for d in priv) + "Allow: /\n\n")
# no grupo *, Disallow antes do Allow: / (robôs que usam a 1ª regra que casa também respeitam a área logada)
m = re.search(r"(?s)(User-agent: \*\n)(.*?)(\n\n|\nSitemap:|$)", atual)
if m:
    linhas = m.group(2).splitlines(); allow = [l for l in linhas if l.strip() == "Allow: /"]
    outras = [l for l in linhas if l.strip() != "Allow: /"]
    atual = atual[:m.start(2)] + "\n".join(outras + allow) + atual[m.end(2):]
rb.write_text(bloco + atual)
(out / "ai.txt").write_text("# Têmis · ai.txt (t2231u v2)\n# Proibido usar o conteúdo para treino, ajuste ou avaliação de modelos de IA sem autorização escrita.\n"
                            "# Busca e resposta com citação e link para agentetemis.com: permitidas nas páginas públicas.\nUser-Agent: *\nDisallow: /\n")
wk = out / ".well-known"; wk.mkdir(exist_ok=True)
(wk / "tdmrep.json").write_text(json.dumps([{"location": "/", "tdm-reservation": 1, "tdm-policy": "mailto:temis@e-pronaos.com"}]))
print(f"[antirobo_t2231u v2] treino bloqueado: {len(TREINO)}; busca de IA liberada nas páginas públicas: {len(BUSCA)}")
