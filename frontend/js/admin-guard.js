// Protege las páginas de /admin: si no hay sesión de administrador, redirige al login.
// La autorización real ocurre siempre en el backend (adminOnly middleware);
// esto es solo una conveniencia de UX para no mostrar la pantalla vacía.
(async function guardAdmin() {
  try {
    const me = await api.get("/api/auth/me");
    if (me.role !== "ADMIN") throw new Error("No autorizado");
    document.dispatchEvent(new CustomEvent("admin-ready", { detail: me }));
  } catch {
    location.href = "/admin/login.html";
  }
})();

function adminLogout() {
  api.post("/api/auth/logout").finally(() => (location.href = "/admin/login.html"));
}
