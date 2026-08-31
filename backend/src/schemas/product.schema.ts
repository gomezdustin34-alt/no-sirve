import { z } from "zod";

export const upsertProductSchema = z.object({
  slug: z.string().trim().min(2).max(120).regex(/^[a-z0-9-]+$/, "Solo minúsculas, números y guiones"),
  name: z.string().trim().min(2).max(150),
  description: z.string().trim().min(10).max(2000),
  meaning: z.string().trim().max(1000).optional(),
  flowersUsed: z.string().trim().max(300).optional(),
  basePrice: z.number().int().positive(),
  images: z.array(z.string().url().or(z.string().startsWith("/"))).min(1).max(10),
  occasion: z.string().trim().max(60).optional(),
  stock: z.number().int().min(0).max(100000),
  isFeatured: z.boolean().optional(),
  isAvailable: z.boolean().optional(),
  categoryId: z.string().optional(),
});

export const updateStockSchema = z.object({
  stock: z.number().int().min(0).max(100000),
});

export const createCategorySchema = z.object({
  name: z.string().trim().min(2).max(80),
  slug: z.string().trim().min(2).max(80).regex(/^[a-z0-9-]+$/, "Solo minúsculas, números y guiones"),
  imagePath: z.string().trim().optional(),
});
