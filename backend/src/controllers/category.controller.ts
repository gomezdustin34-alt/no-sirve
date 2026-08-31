import { Request, Response } from "express";
import { prisma } from "../config/db";
import { recordAudit } from "../lib/audit";
import { HttpError } from "../middleware/errorHandler";

export async function listCategories(_req: Request, res: Response): Promise<void> {
  const categories = await prisma.category.findMany({ orderBy: { sortOrder: "asc" } });
  res.json(categories);
}

export async function createCategory(req: Request, res: Response): Promise<void> {
  const existing = await prisma.category.findUnique({ where: { slug: req.body.slug } });
  if (existing) throw new HttpError(409, "Ya existe una categoría con ese slug");

  const category = await prisma.category.create({ data: req.body });
  await recordAudit({ actorId: req.auth?.userId, actorRole: "ADMIN", action: "CREATE", entity: "Category", entityId: category.id });
  res.status(201).json(category);
}
