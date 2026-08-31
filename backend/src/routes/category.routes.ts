import { Router } from "express";
import { createCategory, listCategories } from "../controllers/category.controller";
import { requireAuth } from "../middleware/auth";
import { adminOnly } from "../middleware/adminOnly";
import { validateBody } from "../middleware/validate";
import { createCategorySchema } from "../schemas/product.schema";
import { writeRateLimiter } from "../middleware/rateLimit";

export const categoryRouter = Router();

categoryRouter.get("/", listCategories);
categoryRouter.post("/", requireAuth, adminOnly, writeRateLimiter, validateBody(createCategorySchema), createCategory);
