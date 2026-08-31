import fs from "fs/promises";
import { Request, Response } from "express";
import { prisma } from "../config/db";
import { applyCoupon, calculateShipping, priceCart } from "../services/pricing.service";
import { generateOrderCode, notifyNewOrder, notifyStatusUpdate, STATUS_LABELS } from "../services/order.service";
import { RECEIPT_ALLOWED_MIMES } from "../middleware/upload";
import { detectRealMime } from "../lib/fileType";
import { recordAudit } from "../lib/audit";
import { HttpError } from "../middleware/errorHandler";
import { OrderStatus } from "../lib/status";

export async function priceCartHandler(req: Request, res: Response): Promise<void> {
  const { items, city, couponCode } = req.body;
  const { items: pricedItems, subtotal } = await priceCart(items);
  const shippingCost = calculateShipping(city);
  const discount = await applyCoupon(couponCode, subtotal);
  const total = Math.max(subtotal + shippingCost - discount, 0);

  res.json({ items: pricedItems, subtotal, shippingCost, discount, total });
}

/**
 * Crea el pedido. El precio se recalcula por completo en el servidor
 * (nunca se confía en montos enviados por el cliente) y el pedido se
 * guarda ANTES de intentar cualquier notificación externa.
 */
export async function createOrder(req: Request, res: Response): Promise<void> {
  const body = req.body;

  const { items: pricedItems, subtotal } = await priceCart(body.items);
  const shippingCost = calculateShipping(body.deliveryCity);
  const discount = await applyCoupon(body.couponCode, subtotal);
  const total = Math.max(subtotal + shippingCost - discount, 0);

  const code = await generateOrderCode();

  // Reserva de stock y creación del pedido en una sola transacción: si algún
  // producto se agotó entre el cálculo del precio y este punto (dos clientes
  // comprando al mismo tiempo), todo se revierte y no se crea el pedido.
  const order = await prisma.$transaction(async (tx) => {
    for (const item of pricedItems) {
      const result = await tx.product.updateMany({
        where: { id: item.productId, stock: { gte: item.quantity } },
        data: { stock: { decrement: item.quantity } },
      });
      if (result.count === 0) {
        throw new HttpError(409, `"${item.productName}" ya no tiene suficiente stock disponible. Revisa tu carrito.`);
      }
    }

    return tx.order.create({
      data: {
        code,
        userId: req.auth?.userId,
        customerName: body.customerName,
        customerEmail: body.customerEmail,
        customerPhone: body.customerPhone,
        recipientName: body.recipientName,
        recipientPhone: body.recipientPhone,
        deliveryAddress: body.deliveryAddress,
        deliveryCity: body.deliveryCity,
        deliveryDate: new Date(body.deliveryDate),
        deliveryWindow: body.deliveryWindow,
        cardMessage: body.cardMessage,
        subtotal,
        shippingCost,
        discount,
        total,
        items: {
          create: pricedItems.map((item) => ({
            productId: item.productId,
            productName: item.productName,
            unitPrice: item.unitPrice,
            quantity: item.quantity,
            customization: item.customization ? JSON.stringify(item.customization) : null,
          })),
        },
      },
    });
  });

  await recordAudit({ actorId: req.auth?.userId, actorRole: req.auth?.role ?? "CUSTOMER", action: "CREATE", entity: "Order", entityId: order.id });

  res.status(201).json({ id: order.id, code: order.code, total: order.total });

  // Las notificaciones se disparan después de responder al cliente: si fallan,
  // el pedido ya quedó guardado y la respuesta ya fue enviada.
  notifyNewOrder(order.id).catch((err) => console.error("notifyNewOrder falló:", err));
}

export async function getOrderTracking(req: Request, res: Response): Promise<void> {
  const order = await prisma.order.findUnique({
    where: { id: req.params.id },
    include: { items: true, payment: true },
  });
  if (!order) {
    res.status(404).json({ error: "Pedido no encontrado" });
    return;
  }

  res.json({
    code: order.code,
    status: order.status,
    statusLabel: STATUS_LABELS[order.status as OrderStatus],
    deliveryDate: order.deliveryDate,
    deliveryWindow: order.deliveryWindow,
    total: order.total,
    paymentStatus: order.payment?.status ?? null,
    items: order.items.map((i) => ({ productName: i.productName, quantity: i.quantity })),
  });
}

/** Sube y registra el comprobante de transferencia (punto 24-25 del brief). */
export async function confirmTransfer(req: Request, res: Response): Promise<void> {
  const orderId = req.params.id;
  const file = req.file;

  if (!file) throw new HttpError(400, "Debes adjuntar el comprobante de transferencia");

  const realMime = await detectRealMime(file.path);
  if (!realMime || !RECEIPT_ALLOWED_MIMES.includes(realMime)) {
    await fs.unlink(file.path).catch(() => undefined);
    throw new HttpError(400, "El archivo no coincide con un tipo permitido (JPG, PNG, WEBP o PDF)");
  }

  const order = await prisma.order.findUnique({ where: { id: orderId } });
  if (!order) {
    await fs.unlink(file.path).catch(() => undefined);
    throw new HttpError(404, "Pedido no encontrado");
  }

  const { bankName, amount, transferDate, referenceNumber, holderName } = req.body;

  const payment = await prisma.payment.upsert({
    where: { orderId },
    create: {
      orderId,
      bankName,
      amount: Number(amount),
      transferDate: new Date(transferDate),
      referenceNumber,
      holderName,
      receiptFilename: file.filename,
      status: "PENDING_VERIFICATION",
    },
    update: {
      bankName,
      amount: Number(amount),
      transferDate: new Date(transferDate),
      referenceNumber,
      holderName,
      receiptFilename: file.filename,
      status: "PENDING_VERIFICATION",
    },
  });

  await recordAudit({ actorId: req.auth?.userId, action: "SUBMIT_TRANSFER", entity: "Payment", entityId: payment.id });
  res.status(201).json({ status: payment.status });
}

// ---------- Admin ----------

export async function adminListOrders(req: Request, res: Response): Promise<void> {
  const { status } = req.query;
  const orders = await prisma.order.findMany({
    where: { status: typeof status === "string" ? (status as OrderStatus) : undefined },
    include: { items: true, payment: true },
    orderBy: { createdAt: "desc" },
  });
  res.json(orders);
}

export async function adminGetOrder(req: Request, res: Response): Promise<void> {
  const order = await prisma.order.findUnique({
    where: { id: req.params.id },
    include: { items: true, payment: true, notifications: true },
  });
  if (!order) {
    res.status(404).json({ error: "Pedido no encontrado" });
    return;
  }
  res.json(order);
}

export async function adminUpdateOrderDetails(req: Request, res: Response): Promise<void> {
  const { deliveryDate, ...rest } = req.body;
  const order = await prisma.order.update({
    where: { id: req.params.id },
    data: { ...rest, deliveryDate: deliveryDate ? new Date(deliveryDate) : undefined },
  });
  await recordAudit({ actorId: req.auth?.userId, actorRole: "ADMIN", action: "UPDATE_DETAILS", entity: "Order", entityId: order.id });
  res.json(order);
}

export async function adminUpdateOrderStatus(req: Request, res: Response): Promise<void> {
  const order = await prisma.order.update({
    where: { id: req.params.id },
    data: { status: req.body.status },
  });
  await recordAudit({
    actorId: req.auth?.userId,
    actorRole: "ADMIN",
    action: "UPDATE_STATUS",
    entity: "Order",
    entityId: order.id,
    metadata: { status: order.status },
  });
  res.json(order);
  notifyStatusUpdate(order.id).catch((err) => console.error("notifyStatusUpdate falló:", err));
}

export async function adminReviewPayment(req: Request, res: Response): Promise<void> {
  const { decision } = req.body;
  const payment = await prisma.payment.update({
    where: { orderId: req.params.id },
    data: { status: decision, reviewedByAdminId: req.auth?.userId, reviewedAt: new Date() },
  });

  if (decision === "CONFIRMED") {
    const order = await prisma.order.update({ where: { id: req.params.id }, data: { status: "PAYMENT_VERIFIED" } });
    notifyStatusUpdate(order.id).catch((err) => console.error("notifyStatusUpdate falló:", err));
  }

  await recordAudit({
    actorId: req.auth?.userId,
    actorRole: "ADMIN",
    action: "REVIEW_PAYMENT",
    entity: "Payment",
    entityId: payment.id,
    metadata: { decision },
  });

  res.json(payment);
}
