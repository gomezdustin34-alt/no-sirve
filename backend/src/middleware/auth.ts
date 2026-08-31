import { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { env } from "../config/env";

export interface AuthPayload {
  userId: string;
  role: "CUSTOMER" | "ADMIN";
}

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      auth?: AuthPayload;
    }
  }
}

export function signSession(payload: AuthPayload): string {
  return jwt.sign(payload, env.AUTH_SECRET, { expiresIn: env.AUTH_TOKEN_EXPIRES_IN as jwt.SignOptions["expiresIn"] });
}

/** Adjunta req.auth si hay una cookie de sesión válida; nunca rechaza la petición. */
export function attachAuth(req: Request, _res: Response, next: NextFunction): void {
  const token = req.cookies?.[env.AUTH_COOKIE_NAME];
  if (!token) return next();

  try {
    const payload = jwt.verify(token, env.AUTH_SECRET) as AuthPayload;
    req.auth = payload;
  } catch {
    // token inválido o expirado: se trata como no autenticado
  }
  next();
}

/** Exige que exista una sesión válida (cualquier rol). */
export function requireAuth(req: Request, res: Response, next: NextFunction): void {
  if (!req.auth) {
    res.status(401).json({ error: "No autenticado" });
    return;
  }
  next();
}
