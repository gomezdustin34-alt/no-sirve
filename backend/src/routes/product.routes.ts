import { Router } from "express";
import {
  adminListProducts,
  createProduct,
  deleteProduct,
  getProductBySlug,
  listProducts,
  updateProduct,
  updateProductStock,
  uploadProductImagesHandler,
} from "../controllers/product.controller";
import { requireAuth } from "../middleware/auth";
import { adminOnly } from "../middleware/adminOnly";
import { validateBody } from "../middleware/validate";
import { updateStockSchema, upsertProductSchema } from "../schemas/product.schema";
import { writeRateLimiter } from "../middleware/rateLimit";
import { uploadProductImages } from "../middleware/uploadProductImage";

export const productRouter = Router();

productRouter.get("/", listProducts);
productRouter.post("/upload-images", requireAuth, adminOnly, writeRateLimiter, uploadProductImages, uploadProductImagesHandler);
productRouter.get("/admin/all", requireAuth, adminOnly, adminListProducts);
productRouter.post("/", requireAuth, adminOnly, writeRateLimiter, validateBody(upsertProductSchema), createProduct);
productRouter.put("/:id", requireAuth, adminOnly, writeRateLimiter, validateBody(upsertProductSchema), updateProduct);
productRouter.patch("/:id/stock", requireAuth, adminOnly, writeRateLimiter, validateBody(updateStockSchema), updateProductStock);
productRouter.delete("/:id", requireAuth, adminOnly, deleteProduct);

productRouter.get("/:slug", getProductBySlug);
