#!/usr/bin/env python3
"""t2231u: robôs de IA fora do site (robots.txt + ai.txt + tdmrep.json). Buscadores comuns (Google, Bing) seguem indexando.
Rollback: apagar a linha do antirobo_t2231u_pos.py no build.sh."""
import pathlib, sys, json
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
BOTS = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-Web", "Claude-User", "Claude-SearchBot", "anthropic-ai",
        "CCBot", "PerplexityBot", "Perplexity-User", "Google-Extended", "GoogleOther", "Applebot-Extended", "Bytespider", "Amazonbot",
        "meta-externalagent", "meta-externalfetcher", "FacebookBot", "Diffbot", "cohere-ai", "cohere-training-data-crawler", "YouBot",
        "ImagesiftBot", "Omgilibot", "omgili", "Timpibot", "PetalBot", "DuckAssistBot", "MistralAI-User", "AI2Bot", "Ai2Bot-Dolma",
        "PanguBot", "Scrapy", "img2dataset", "webzio-extended", "FirecrawlAgent", "Crawl4AI", "ChatGLM-Spider", "iaskspider",
        "Kangaroo Bot", "Brightbot", "SemrushBot-OCOB", "VelenPublicWebCrawler", "Novellum", "Andibot", "bedrockbot", "TikTokSpider",
        "QualifiedBot", "LinerBot", "Quora-Bot", "magpie-crawler", "Sidetrade indexer bot", "Factset_spyderbot", "Cotoyogi", "anthropic"]
rb = out / "robots.txt"
atual = rb.read_text() if rb.exists() else "User-agent: *\nAllow: /\n"
if "t2231u" not in atual:
    bloco = "# t2231u: robôs de IA (treino, busca de IA e agentes) não entram na Têmis.\n" + "".join(f"User-agent: {b}\n" for b in BOTS) + "Disallow: /\n\n"
    rb.write_text(bloco + atual)
(out / "ai.txt").write_text("# Têmis · ai.txt (t2231u)\n# Conteúdo protegido: proibido usar para treino, ajuste, avaliação ou geração de IA sem autorização escrita.\nUser-Agent: *\nDisallow: /\nDisallow: *\n")
wk = out / ".well-known"; wk.mkdir(exist_ok=True)
(wk / "tdmrep.json").write_text(json.dumps([{"location": "/", "tdm-reservation": 1, "tdm-policy": "mailto:temis@e-pronaos.com"}]))
print(f"[antirobo_t2231u] robots.txt com {len(BOTS)} robôs de IA bloqueados; ai.txt e tdmrep.json gravados")
