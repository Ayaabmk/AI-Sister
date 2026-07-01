(function () {
  document.title = "AI Sisters — Boulangerie Madeleine 🥐";

  function applyBranding() {
    // Titre onglet
    if (!document.title.includes("AI Sisters")) {
      document.title = "AI Sisters — Boulangerie Madeleine 🥐";
    }

    // Remplacer le logo Chainlit par le logo AI Sisters
    document.querySelectorAll("img.logo").forEach((img) => {
      img.src = "/public/logo_dark.svg";
      img.style.width = "280px";
      img.style.marginBottom = "20px";
    });

    // Masquer les liens vers chainlit
    document.querySelectorAll("a").forEach((a) => {
      if (a.href && (a.href.includes("chainlit.io") || a.href.includes("github.com/Chainlit"))) {
        const parent = a.closest("div, p, footer, span");
        if (parent) parent.style.display = "none";
        else a.style.display = "none";
      }
    });
  }

  // Appliquer immédiatement puis observer les changements DOM
  const observer = new MutationObserver(applyBranding);
  const start = () => {
    applyBranding();
    observer.observe(document.body, { childList: true, subtree: true });
  };

  if (document.body) start();
  else document.addEventListener("DOMContentLoaded", start);
})();
