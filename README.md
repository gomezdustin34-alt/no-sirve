# Dígalo con Flores 🌷

Floristería digital: frontend estático (HTML/CSS/JS) + backend en Node.js/Express/Prisma. El mismo servidor Express sirve la API y los archivos del frontend, así que todo el sitio vive en **una sola URL**. Ver el detalle de arquitectura y decisiones en `backend/README.md`.

## Levantar el proyecto en desarrollo

```bash
cd backend
npm install
cp .env.example .env
# abre .env y al menos define AUTH_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
npx prisma migrate dev --name init
npm run seed
npm run dev
```

Abre **`http://localhost:4000`** — ahí está todo: la tienda, el checkout y el panel admin (`/admin/login.html`). No hace falta levantar el frontend por separado.

## Cuenta de administrador

El `npm run seed` crea un usuario admin con el correo/clave definidos en `ADMIN_EMAIL` / `ADMIN_PASSWORD` de tu `.env`. Entra en `http://localhost:4000/admin/login.html`.

## Flujo de compra para probar

1. `http://localhost:4000` → elige una emoción (ej. "Te amo").
2. Entra a un producto, personaliza y agrégalo al carrito.
3. Ve al carrito → checkout → completa los 6 pasos, sube cualquier imagen como comprobante.
4. Copia el número de pedido y revísalo en `/admin/pedidos.html` (login admin requerido).
5. Aprueba el pago y cambia el estado — el cliente vería la actualización en `/seguimiento.html?id=...`.

Sin credenciales reales de WhatsApp/Email en `.env`, los pasos 3-4 seguirán funcionando: el pedido se crea igual, solo las notificaciones automáticas quedan registradas como fallidas (ver `backend/README.md`).
