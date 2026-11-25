(() => {
  const URL = "/conta/promo.json";
  const fmt = (cents) => {
    const n = Number(cents) / 100;
    const s = n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    return s;
  };
  const texto = (p, prazo) => {
    const b = (prazo && p.prazos && p.prazos[prazo]) || p;
    if (b && b.texto) return b.texto + (p.por_usuario ? " por usuário" : "");
    const ch = b.preco_cheio_centavos, fn = b.preco_final_centavos;
    if (!ch || fn == null) return "";
    const pct = b.percentual != null ? b.percentual : Math.floor((1 - fn / ch) * 100);
    return "de " + fmt(ch) + " por " + fmt(fn) + " · −" + pct + "%" + (p.por_usuario ? " por usuário" : "");
  };
  const aplica = (d) => {
    if (!d || !d.ok || !d.planos) return;
    document.querySelectorAll("[data-tm-plano]").forEach((el) => {
      const k = el.getAttribute("data-tm-plano");
      const pz = el.getAttribute("data-tm-prazo") || "mensal";
      const p = d.planos[k];
      if (!p) return;
      const t = texto(p, pz);
      if (!t) return;
      el.textContent = t;
    });
    document.querySelectorAll("[data-tm-promo-passo]").forEach((el) => {
      const rot = (d.passo && d.passo.rotulo) || "";
      const fim = (d.passo && d.passo.fim_texto) || d.fim_texto || "";
      el.textContent = [rot, fim ? "até " + fim : ""].filter(Boolean).join(" · ");
    });
  };
  try {
    fetch(URL, { credentials: "same-origin" })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => { if (d) aplica(d); })
      .catch(() => {});
  } catch (e) {}
})();
