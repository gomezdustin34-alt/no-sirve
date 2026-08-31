import { Router } from "express";
import {
  adminGetOrder,
  adminListOrders,
  adminReviewPayment,
  adminUpdateOrderDetails,
  adminUpdateOrderStatus,
  confirmTransfer,
  createOrder,
  getOrderTracking,
  priceCartHandler,
} from "../controllers/order.controller";
import { requireAuth, attachAuth } from "../middleware/auth";
import { adminOnly } from "../middleware/adminOnly";
import { validateBody } from "../middleware/validate";
import {
  adminUpdateOrderDetailsSchema,
  confirmTransferSchema,
  createOrderSchema,
  priceCartSchema,
  reviewPaymentSchema,
  updateOrderStatusSchema,
} from "../schemas/order.schema";
import { writeRateLimiter } from "../middleware/rateLimit";
import { uploadReceipt } from "../middleware/upload";

export const orderRouter = Router();

orderRouter.post("/price", writeRateLimiter, validateBody(priceCartSchema), priceCartHandler);
orderRouter.post("/", attachAuth, writeRateLimiter, validateBody(createOrderSchema), createOrder);
orderRouter.get("/:id/tracking", getOrderTracking);

orderRouter.post(
  "/:id/transfer",
  attachAuth,
  writeRateLimiter,
  uploadReceipt,
  validateBody(confirmTransferSchema),
  confirmTransfer
);

orderRouter.get("/admin/all", requireAuth, adminOnly, adminListOrders);
orderRouter.get("/admin/:id", requireAuth, adminOnly, adminGetOrder);
orderRouter.patch("/admin/:id/details", requireAuth, adminOnly, validateBody(adminUpdateOrderDetailsSchema), adminUpdateOrderDetails);
orderRouter.patch("/admin/:id/status", requireAuth, adminOnly, validateBody(updateOrderStatusSchema), adminUpdateOrderStatus);
orderRouter.patch("/admin/:id/payment", requireAuth, adminOnly, validateBody(reviewPaymentSchema), adminReviewPayment);
