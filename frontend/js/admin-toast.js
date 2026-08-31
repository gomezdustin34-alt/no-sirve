// Notificaciones toast para el panel admin: confirma visualmente cada acción
// (guardar, aprobar, eliminar...) para que el admin sepa que sí se aplicó.
function ensureToastContainer() {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message, type = "success") {
  const container = ensureToastContainer();
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  const icon = type === "error"
    ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>'
    : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12.5l2.5 2.5L16 9"/></svg>';
  toast.innerHTML = `${icon}<span>${message}</span>`;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("is-visible"));
  setTimeout(() => {
    toast.classList.remove("is-visible");
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

/** Envuelve una acción async: si tiene éxito muestra el toast de éxito, si falla el de error. */
async function withToast(action, successMessage, errorPrefix = "No se pudo completar la acción") {
  try {
    const result = await action();
    showToast(successMessage, "success");
    return result;
  } catch (err) {
    showToast(`${errorPrefix}: ${err.message || "intenta de nuevo"}`, "error");
    throw err;
  }
}
