import { Request, Response } from "express";
import { prisma } from "../config/db";
import { recordAudit } from "../lib/audit";
import { detectRealMime } from "../lib/fileType";
import { PRODUCT_IMAGES_PUBLIC_PATH, PRODUCT_IMAGE_ALLOWED_MIMES } from "../middleware/uploadProductImage";
import fs from "fs/promises";
import path from "path";

function serialize(product: { images: string; stock: number; [key: string]: unknown }) {
  return { ...product, images: JSON.parse(product.images) as string[], soldOut: product.stock <= 0 };
}

const categorySelect = { category: { select: { id: true, name: true, slug: true } } } as const;

export async function listProducts(req: Request, res: Response): Promise<void> {
  const { category, occasion, featured } = req.query;

  const products = await prisma.product.findMany({
    where: {
      isAvailable: true,
      category: typeof category === "string" ? { slug: category } : undefined,
      occasion: typeof occasion === "string" ? occasion : undefined,
      isFeatured: featured === "true" ? true : undefined,
    },
    include: categorySelect,
    orderBy: { createdAt: "desc" },
  });

  res.json(products.map(serialize));
}

export async function getProductBySlug(req: Request, res: Response): Promise<void> {
  const product = await prisma.product.findUnique({ where: { slug: req.params.slug }, include: categorySelect });
  if (!product || !product.isAvailable) {
    res.status(404).json({ error: "Producto no encontrado" });
    return;
  }
  res.json(serialize(product));
}

export async function createProduct(req: Request, res: Response): Promise<void> {
  const data = req.body;
  const product = await prisma.product.create({
    data: { ...data, images: JSON.stringify(data.images) },
  });
  await recordAudit({ actorId: req.auth?.userId, actorRole: req.auth?.role, action: "CREATE", entity: "Product", entityId: product.id });
  res.status(201).json(serialize(product));
}

export async function updateProduct(req: Request, res: Response): Promise<void> {
  const data = req.body;
  const product = await prisma.product.update({
    where: { id: req.params.id },
    data: { ...data, images: JSON.stringify(data.images) },
  });
  await recordAudit({ actorId: req.auth?.userId, actorRole: req.auth?.role, action: "UPDATE", entity: "Product", entityId: product.id });
  res.json(serialize(product));
}

export async function deleteProduct(req: Request, res: Response): Promise<void> {
  await prisma.product.update({ where: { id: req.params.id }, data: { isAvailable: false } });
  await recordAudit({ actorId: req.auth?.userId, actorRole: req.auth?.role, action: "DEACTIVATE", entity: "Product", entityId: req.params.id });
  res.status(204).send();
}

/** Ajuste rápido de inventario: solo el stock, sin reenviar todo el producto. */
export async function updateProductStock(req: Request, res: Response): Promise<void> {
  const product = await prisma.product.update({
    where: { id: req.params.id },
    data: { stock: req.body.stock },
    include: categorySelect,
  });
  await recordAudit({
    actorId: req.auth?.userId,
    actorRole: "ADMIN",
    action: "UPDATE_STOCK",
    entity: "Product",
    entityId: product.id,
    metadata: { stock: product.stock },
  });
  res.json(serialize(product));
}

export async function adminListProducts(_req: Request, res: Response): Promise<void> {
  const products = await prisma.product.findMany({ include: categorySelect, orderBy: { createdAt: "desc" } });
  res.json(products.map(serialize));
}

/**
 * Recibe hasta 6 imágenes (multipart), verifica su tipo real por magic bytes
 * y devuelve las rutas públicas para que el admin las asocie a un producto.
 */
export async function uploadProductImagesHandler(req: Request, res: Response): Promise<void> {
  const files = (req.files as Express.Multer.File[] | undefined) ?? [];
  if (!files.length) {
    res.status(400).json({ error: "No se recibió ninguna imagen" });
    return;
  }

  const urls: string[] = [];
  for (const file of files) {
    const realMime = await detectRealMime(file.path);
    if (!realMime || !PRODUCT_IMAGE_ALLOWED_MIMES.includes(realMime)) {
      await Promise.all(files.map((f) => fs.unlink(f.path).catch(() => undefined)));
      res.status(400).json({ error: `El archivo "${file.originalname}" no es una imagen válida (JPG, PNG o WEBP)` });
      return;
    }
    urls.push(path.posix.join(PRODUCT_IMAGES_PUBLIC_PATH, file.filename));
  }

  await recordAudit({ actorId: req.auth?.userId, actorRole: "ADMIN", action: "UPLOAD_IMAGES", entity: "Product", metadata: { count: urls.length } });
  res.status(201).json({ urls });
}
