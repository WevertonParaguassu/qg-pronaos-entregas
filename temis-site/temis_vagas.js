/* Selo público «Turma aberta · restam N vagas» na vitrine de planos. */
(function () {
  var ENDPOINTS = ["/conta/vagas.json", "https://agentetemis.com/conta/vagas.json"];
  var ALIAS = { max: ["agente", "plano-max", "max"], essencial: ["essencial", "plano-essencial"] };
  function limpa(s) {
    return String(s || "").replace(/assinaturas?|gratuit[ao]s?|gr[aá]tis|\(free\)|:free\b|antigravity|\badapta\b/gi, "plano");
  }
  function textoTurma(n, fallback) {
    n = parseInt(n, 10);
    if (!isFinite(n) || n <= 0) return fallback || "Vagas esgotadas — entre na lista de espera";
    if (n === 1) return "Turma aberta · resta 1 vaga";
    return "Turma aberta · restam " + n + " vagas";
  }
  function achar(k) {
    var ids = ["plano-" + k, k].concat(ALIAS[k] || []);
    for (var i = 0; i < ids.length; i++) {
      var el = document.getElementById(ids[i]);
      if (el) return el;
    }
    var a = document.querySelector('a[href*="plano/' + k + '"]');
    if (a) return a.closest("article, .tm-card, .ficha, .card, div[id]") || a.parentNode;
    return null;
  }
  function selo(el, info) {
    if (!el || !info) return;
    var antigo = el.querySelector(".turma-aberta");
    if (antigo) antigo.parentNode.removeChild(antigo);
    var n = info.vagas_restantes;
    var txt = limpa(info.texto || textoTurma(n));
    var p = document.createElement("p");
    p.className = "turma-aberta";
    p.setAttribute("data-restam", String(n == null ? "" : n));
    p.style.color = "#f0d78c";
    p.style.fontFamily = "Georgia, serif";
    p.style.margin = "8px 0 4px";
    p.style.fontSize = "15px";
    p.textContent = txt;
    var box = el.querySelector(".tm-botoes, .botoes-plano, .cta, a.btn");
    if (box && box.parentNode) box.parentNode.insertBefore(p, box);
    else el.appendChild(p);
  }
  function espera(el) {
    var box = el.querySelector(".tm-botoes, .botoes-plano, .cta, a.btn, button");
    var html =
      '<div class="vagas-esgotadas">' +
      "<h3>Vagas esgotadas</h3>" +
      "<p>Entre na lista de espera. Avisamos neste e-mail quando abrir vaga.</p>" +
      '<p><a class="btn" href="/conta/planos">Entrar na lista de espera</a></p></div>';
    if (box && box.parentNode) {
      var wrap = document.createElement("div");
      wrap.innerHTML = limpa(html);
      box.parentNode.replaceChild(wrap, box);
    }
  }
  function card(el, info) {
    if (!info || !el) return;
    if (info.aberto) selo(el, info);
    else espera(el);
  }
  function aplica(d) {
    if (!d || !d.planos) return;
    Object.keys(d.planos).forEach(function (k) {
      card(achar(k), d.planos[k]);
    });
    Object.keys(d.apps || {}).forEach(function (k) {
      var el = document.getElementById("app-" + k) || document.querySelector('[data-app="' + k + '"]');
      if (el) card(el, d.apps[k]);
    });
  }
  function tenta(i) {
    if (i >= ENDPOINTS.length) return;
    fetch(ENDPOINTS[i], { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(aplica)
      .catch(function () { tenta(i + 1); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { tenta(0); });
  else tenta(0);
})();
