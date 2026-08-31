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
  "application/pdf": ".pdf",
};

// En producción apunta a un volumen persistente (UPLOADS_DIR), en local al
// directorio del repo. Los comprobantes son privados: solo servidos a admins
// autenticados (ver admin.controller.ts), nunca vía express.static.
const uploadDir = env.UPLOADS_DIR || path.join(__dirname, "..", "..", "uploads");
fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename: (_req, file, cb) => {
    const ext = ALLOWED_EXTENSIONS[file.mimetype] ?? "";
    const safeName = `${crypto.randomUUID()}${ext}`;
    cb(null, safeName);
  },
});

function fileFilter(_req: Request, file: Express.Multer.File, cb: multer.FileFilterCallback) {
  if (!ALLOWED_EXTENSIONS[file.mimetype]) {
    cb(new Error("Tipo de archivo no permitido. Solo JPG, PNG, WEBP o PDF."));
    return;
  }
  cb(null, true);
}

/** Middleware de subida de comprobantes de transferencia: valida tipo declarado y tamaño. */
export const uploadReceipt = multer({
  storage,
  fileFilter,
  limits: { fileSize: env.UPLOAD_MAX_SIZE_MB * 1024 * 1024, files: 1 },
}).single("receipt");

export { detectRealMime } from "../lib/fileType";
export const RECEIPT_ALLOWED_MIMES = Object.keys(ALLOWED_EXTENSIONS);
export const RECEIPTS_DIR = uploadDir;
