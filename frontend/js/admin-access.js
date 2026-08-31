// Inyecta, al fondo de cada página del cliente, un enlace discreto "Admin" que abre
// un modal de inicio de sesión ahí mismo — sin tener que navegar a /admin/login.html
// para autenticarse. Solo después de iniciar sesión correctamente se redirige al dashboard.
(function initAdminAccess() {
  document.addEventListener("DOMContentLoaded", () => {
    const footerBottom = document.querySelector(".footer-bottom");
    if (!footerBottom) return;

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "footer-admin-trigger";
    trigger.textContent = "Admin";
    footerBottom.appendChild(trigger);

    const overlay = document.createElement("div");
    overlay.className = "admin-login-modal-overlay";
    overlay.innerHTML = `
      <div class="admin-login-modal" role="dialog" aria-modal="true" aria-labelledby="admin-modal-title" style="position:relative;">
        <button type="button" class="admin-login-modal-close" aria-label="Cerrar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
        <img src="/assets/img/logo.png" class="brand-mark" alt="Dígalo con Flores" style="width:52px;height:52px;display:block;margin:0 auto 0.9rem;" />
        <p id="admin-modal-title" class="eyebrow" style="text-align:center;margin-bottom:1rem;">Acceso administrador</p>
        <div id="admin-modal-error" class="form-message error" style="display:none;"></div>
        <form id="admin-modal-form">
          <div class="field" style="text-align:left;"><label for="admin-modal-email">Correo</label><input id="admin-modal-email" type="email" required /></div>
          <div class="field" style="text-align:left;"><label for="admin-modal-password">Contraseña</label><input id="admin-modal-password" type="password" required /></div>
          <button type="submit" class="btn btn-primary btn-full">Entrar</button>
        </form>
      </div>
    `;
    document.body.appendChild(overlay);

    function open() {
      overlay.classList.add("is-open");
      document.getElementById("admin-modal-email").focus();
    }
    function close() {
      overlay.classList.remove("is-open");
      document.getElementById("admin-modal-error").style.display = "none";
    }

    trigger.addEventListener("click", open);
    overlay.querySelector(".admin-login-modal-close").addEventListener("click", close);
    overlay.addEventListener("click", (e) => { if (e.target === overlay) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });

    overlay.querySelector("#admin-modal-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const errorBox = document.getElementById("admin-modal-error");
      errorBox.style.display = "none";
      try {
        const user = await api.post("/api/auth/login", {
          email: document.getElementById("admin-modal-email").value,
          password: document.getElementById("admin-modal-password").value,
        });
        if (user.role !== "ADMIN") throw new Error("Esta cuenta no tiene permisos de administrador");
        location.href = "/admin/dashboard.html";
      } catch (err) {
        errorBox.textContent = err.message || "No se pudo iniciar sesión";
        errorBox.style.display = "block";
      }
    });
  });
})();
