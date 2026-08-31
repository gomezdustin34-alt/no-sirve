import { Request, Response } from "express";
import bcrypt from "bcryptjs";
import { prisma } from "../config/db";
import { env } from "../config/env";
import { signSession } from "../middleware/auth";
import { recordAudit } from "../lib/audit";
import { Role } from "../lib/status";

const cookieOptions = {
  httpOnly: true,
  secure: env.isProduction,
  sameSite: "lax" as const,
  maxAge: 7 * 24 * 60 * 60 * 1000,
  path: "/",
};

export async function register(req: Request, res: Response): Promise<void> {
  const { name, email, password, phone } = req.body;

  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    res.status(409).json({ error: "Ya existe una cuenta con ese correo" });
    return;
  }

  const passwordHash = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({ data: { name, email, phone, passwordHash, role: "CUSTOMER" } });

  const token = signSession({ userId: user.id, role: user.role as Role });
  res.cookie(env.AUTH_COOKIE_NAME, token, cookieOptions);
  res.status(201).json({ id: user.id, name: user.name, email: user.email, role: user.role });
}

export async function login(req: Request, res: Response): Promise<void> {
  const { email, password } = req.body;

  const user = await prisma.user.findUnique({ where: { email } });
  const genericError = () => res.status(401).json({ error: "Correo o contraseña incorrectos" });

  if (!user) {
    genericError();
    return;
  }

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) {
    genericError();
    return;
  }

  const token = signSession({ userId: user.id, role: user.role as Role });
  res.cookie(env.AUTH_COOKIE_NAME, token, cookieOptions);
  await recordAudit({ actorId: user.id, actorRole: user.role, action: "LOGIN", entity: "User", entityId: user.id });
  res.json({ id: user.id, name: user.name, email: user.email, role: user.role });
}

export async function logout(_req: Request, res: Response): Promise<void> {
  res.clearCookie(env.AUTH_COOKIE_NAME, { path: "/" });
  res.status(204).send();
}

export async function me(req: Request, res: Response): Promise<void> {
  if (!req.auth) {
    res.status(401).json({ error: "No autenticado" });
    return;
  }
  const user = await prisma.user.findUnique({ where: { id: req.auth.userId } });
  if (!user) {
    res.status(401).json({ error: "No autenticado" });
    return;
  }
  res.json({ id: user.id, name: user.name, email: user.email, role: user.role });
}
