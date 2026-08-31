import crypto from "crypto";
import fs from "fs";
import path from "path";
import multer from "multer";
import { Request } from "express";
import { env } from "../config/env";

const ALLOWED_EXTENSIONS: Record<string, string> = {
  "image/jpeg": ".jpg",
  "image/png": ".png",
  "image/webp": ".webp",
};

// Las imágenes de producto son públicas (a diferencia de los comprobantes de pago).
// En local viven dentro del frontend estático por conveniencia; en producción
// PRODUCT_IMAGES_DIR debe apuntar a un volumen persistente — se sirven igual
// gracias a la ruta estática explícita registrada en server.ts.
export const PRODUCT_IMAGES_DIR = env.PRODUCT_IMAGES_DIR || path.join(__dirname, "..", "..", "..", "frontend", "assets", "img", "products");
export const PRODUCT_IMAGES_PUBLIC_PATH = "/assets/img/products";
fs.mkdirSync(PRODUCT_IMAGES_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, PRODUCT_IMAGES_DIR),
  filename: (_req, file, cb) => {
    const ext = ALLOWED_EXTENSIONS[file.mimetype] ?? "";
    cb(null, `${crypto.randomUUID()}${ext}`);
  },
});

function fileFilter(_req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback) {
  if (!ALLOWED_EXTENSIONS[file.mimetype]) {
    cb(new Error("Tipo de imagen no permitido. Solo JPG, PNG o WEBP."));
    return;
  }
  cb(null, true);
}

export const PRODUCT_IMAGE_ALLOWED_MIMES = Object.keys(ALLOWED_EXTENSIONS);

export const uploadProductImages = multer({
  storage,
  fileFilter,
  limits: { fileSize: env.UPLOAD_MAX_SIZE_MB * 1024 * 1024, files: 6 },
}).array("images", 6);
