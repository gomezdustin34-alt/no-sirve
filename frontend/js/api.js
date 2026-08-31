// Cliente de API — centraliza fetch() con credenciales (cookie de sesión httpOnly).
// El frontend se sirve desde el mismo servidor Express que expone /api, así que
// las rutas son siempre relativas al origen actual.
const API_BASE = "";

async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: options.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = text; }
  }

  if (!res.ok) {
    const message = (data && data.error) || `Error ${res.status}`;
    const err = new Error(message);
    err.status = res.status;
    err.details = data && data.details;
    throw err;
  }
  return data;
}

const api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
  postForm: (path, formData) => apiRequest(path, { method: "POST", body: formData }),
  put: (path, body) => apiRequest(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: (path, body) => apiRequest(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: (path) => apiRequest(path, { method: "DELETE" }),
};

function formatMoney(cents) {
  return (cents / 100).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
}
