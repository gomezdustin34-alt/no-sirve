import { NextFunction, Request, Response } from "express";

/**
 * Autorización de solo-admin. Debe usarse después de requireAuth.
 * El rol siempre se lee del JWT firmado por el servidor, nunca de un
 * campo enviado por el cliente — así un cliente no puede "convertirse" en admin.
 */
export function adminOnly(req: Request, res: Response, next: NextFunction): void {
  if (!req.auth || req.auth.role !== "ADMIN") {
    res.status(403).json({ error: "Acceso restringido a administradores" });
    return;
  }
  next();
}
