import { Router } from "express";
import { dashboardStats, getReceiptFile, getSettings, updateSettings } from "../controllers/admin.controller";
import { requireAuth } from "../middleware/auth";
import { adminOnly } from "../middleware/adminOnly";

export const adminRouter = Router();

adminRouter.use(requireAuth, adminOnly);

adminRouter.get("/dashboard", dashboardStats);
adminRouter.get("/settings", getSettings);
adminRouter.put("/settings", updateSettings);
adminRouter.get("/receipts/:orderId", getReceiptFile);
