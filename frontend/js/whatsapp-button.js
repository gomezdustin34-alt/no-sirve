// Botón flotante de WhatsApp: toma el número configurado por el admin en
// /admin/configuracion.html y abre una conversación directa (wa.me), sin
// depender de ninguna API — funciona apenas el admin guarde su número.
(function initWhatsappButton() {
  document.addEventListener("DOMContentLoaded", async () => {
    try {
      const info = await api.get("/api/settings/public");
      const digits = (info.whatsappNumber || "").replace(/\D/g, "");
      if (!digits) return;

      const btn = document.createElement("a");
      btn.className = "whatsapp-float";
      btn.href = `https://wa.me/${digits}?text=${encodeURIComponent("Hola, tengo una pregunta sobre Dígalo con Flores 🌷")}`;
      btn.target = "_blank";
      btn.rel = "noopener";
      btn.title = "Escríbenos por WhatsApp";
      btn.setAttribute("aria-label", "Escríbenos por WhatsApp");
      btn.innerHTML = `
        <svg width="28" height="28" viewBox="0 0 32 32" fill="currentColor" aria-hidden="true">
          <path d="M16.001 3C9.096 3 3.5 8.596 3.5 15.5c0 2.362.656 4.57 1.795 6.455L3 29l7.223-2.257A12.44 12.44 0 0 0 16.001 28C22.905 28 28.5 22.404 28.5 15.5S22.905 3 16.001 3Zm7.29 17.61c-.31.87-1.532 1.63-2.514 1.83-.68.14-1.567.25-4.55-.977-3.816-1.58-6.27-5.45-6.46-5.7-.19-.25-1.545-2.06-1.545-3.93 0-1.87.98-2.79 1.328-3.17.31-.34.68-.42.907-.42.227 0 .454.003.652.012.21.01.492-.08.77.587.31.75 1.052 2.6 1.144 2.79.09.19.15.41.03.66-.12.25-.18.41-.36.62-.19.22-.39.49-.56.66-.19.19-.38.39-.163.77.216.38.96 1.585 2.061 2.567 1.417 1.264 2.612 1.656 2.99 1.845.38.19.6.16.822-.096.22-.25.94-1.09 1.19-1.47.25-.38.5-.31.84-.19.34.13 2.19 1.03 2.566 1.218.38.19.63.28.72.44.09.16.09.9-.22 1.78Z"/>
        </svg>
      `;
      document.body.appendChild(btn);
      requestAnimationFrame(() => btn.classList.add("is-visible"));
    } catch {
      // Sin datos de contacto configurados aún: no se muestra el botón.
    }
  });
})();
