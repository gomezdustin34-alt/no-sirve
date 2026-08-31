# Dígalo con Flores — Backend

API en Node.js + Express + TypeScript + Prisma para el flujo real de compra: catálogo, carrito, pedidos, transferencia bancaria con comprobante, panel admin y notificaciones.

## Poner en marcha (desarrollo)

```bash
cd backend
npm install
cp .env.example .env      # completa al menos AUTH_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
npx prisma migrate dev --name init
npm run seed               # crea el admin, categorías, productos y datos bancarios de ejemplo
npm run dev                 # http://localhost:4000
```

## Qué debe configurar el propietario para que todo funcione de verdad

Sin estas credenciales, el sitio funciona igual (los pedidos se guardan, el admin puede operar), pero las notificaciones automáticas quedarán registradas como `FAILED` en la tabla `Notification` — el pedido nunca se pierde por esto.

| Necesitas | Variable(s) en `.env` | Dónde conseguirlo |
|---|---|---|
| Notificar pedidos por WhatsApp | `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `OWNER_WHATSAPP_NUMBER` | Cuenta de WhatsApp Business API en [Meta for Developers](https://developers.facebook.com/docs/whatsapp/cloud-api) |
| Enviar correos (dueño + clientes) | `RESEND_API_KEY` **o** `SMTP_HOST/SMTP_USER/SMTP_PASSWORD` | [Resend](https://resend.com) (más simple) o cualquier proveedor SMTP |
| Base de datos en producción | `DATABASE_URL` | Postgres administrado (Railway, Supabase, RDS...). En desarrollo usa SQLite sin configurar nada |
| Clave de sesión | `AUTH_SECRET` | Generar con `node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"` |
| Datos bancarios reales para transferencias | — | Se cargan desde `/admin/configuracion` una vez logueado como admin, **no** se escriben en el código |

## Qué incluye esta primera entrega

- Catálogo, producto, carrito con precios recalculados 100% en el servidor.
- Checkout con transferencia bancaria: subida de comprobante validada por tipo real de archivo (no solo extensión), tamaño y almacenamiento con nombre aleatorio.
- Creación de pedido resiliente: se guarda primero, las notificaciones (WhatsApp/email) se intentan después y quedan auditadas.
- Panel admin: dashboard, productos (CRUD), pedidos (aprobar/rechazar pago, cambiar estado), configuración del negocio (incluye datos bancarios).
- Seguimiento público de pedido por id.
- Seguridad: JWT en cookie httpOnly, roles verificados en backend, rate limiting en endpoints sensibles, validación con Zod en cada request, Prisma parametriza toda consulta (sin SQL injection), CORS restringido al origen del frontend, Helmet, tabla de auditoría (`AuditLog`).

## Nota para producción: dominio del frontend y backend

Este servidor Express sirve la API y los archivos del frontend juntos (`express.static` sobre `../frontend`, ver `src/server.ts`), así que en desarrollo todo vive en `http://localhost:4000` — mismo origen, sin CORS real de por medio. La cookie de sesión se firma con `SameSite=Lax`, que sigue funcionando si en el futuro se separan detrás de un proxy en subdominios del mismo dominio (ej. `app.digaloconflores.com` y `api.digaloconflores.com`). Si se despliegan en dominios completamente distintos sin proxy, la cookie debe pasar a `SameSite=None; Secure` (ver `src/controllers/auth.controller.ts`).

## Qué queda fuera de esta entrega (a propósito)

Club de fidelización, recordatorios de fechas, reseñas de producto, cupones (el modelo ya existe y `pricing.service.ts` ya sabe aplicarlos, falta el CRUD de admin), cálculo de envío por zona/barrio (hoy es una tarifa plana en `pricing.service.ts`), página de historias tipo revista, SEO avanzado (sitemap/robots/Schema.org) y una auditoría de seguridad formal tipo pentest. La base de datos ya tiene los modelos (`Reminder`, `Review`, `Coupon`) listos para que estas features se agreguen sin rediseñar nada.
