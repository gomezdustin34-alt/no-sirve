import "dotenv/config";
import { z } from "zod";

const envSchema = z.object({
  PORT: z.string().default("4000"),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  FRONTEND_ORIGIN: z.string().default("http://localhost:5173"),
  DATABASE_URL: z.string().min(1, "DATABASE_URL es obligatorio"),

  AUTH_SECRET: z.string().min(16, "AUTH_SECRET debe tener al menos 16 caracteres"),
  AUTH_COOKIE_NAME: z.string().default("dcf_session"),
  AUTH_TOKEN_EXPIRES_IN: z.string().default("7d"),

  ADMIN_EMAIL: z.string().optional().default(""),
  ADMIN_PASSWORD: z.string().optional().default(""),

  WHATSAPP_ACCESS_TOKEN: z.string().optional().default(""),
  WHATSAPP_PHONE_NUMBER_ID: z.string().optional().default(""),
  OWNER_WHATSAPP_NUMBER: z.string().optional().default(""),

  OWNER_EMAIL: z.string().optional().default(""),
  SMTP_HOST: z.string().optional().default(""),
  SMTP_PORT: z.string().optional().default("587"),
  SMTP_USER: z.string().optional().default(""),
  SMTP_PASSWORD: z.string().optional().default(""),
  SMTP_FROM: z.string().optional().default("Dígalo con Flores <no-reply@digaloconflores.com>"),
  RESEND_API_KEY: z.string().optional().default(""),

  UPLOAD_MAX_SIZE_MB: z.string().default("5"),

  // Rutas de almacenamiento persistente. En local apuntan dentro del repo;
  // en producción (Railway) deben apuntar a un volumen montado, ej. /data/uploads/...,
  // para que los comprobantes y fotos de producto sobrevivan a los redeploys.
  UPLOADS_DIR: z.string().optional().default(""),
  PRODUCT_IMAGES_DIR: z.string().optional().default(""),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("Variables de entorno inválidas:", parsed.error.flatten().fieldErrors);
  throw new Error("Configuración de entorno inválida. Revisa tu archivo .env contra .env.example");
}

export const env = {
  ...parsed.data,
  PORT: Number(parsed.data.PORT),
  UPLOAD_MAX_SIZE_MB: Number(parsed.data.UPLOAD_MAX_SIZE_MB),
  isProduction: parsed.data.NODE_ENV === "production",
};
