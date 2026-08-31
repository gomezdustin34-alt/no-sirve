import path from "path";
import { Request, Response } from "express";
import { prisma } from "../config/db";
import { recordAudit } from "../lib/audit";
import { HttpError } from "../middleware/errorHandler";
import { RECEIPTS_DIR } from "../middleware/upload";

export async function dashboardStats(_req: Request, res: Response): Promise<void> {
  const startOfDay = new Date();
  startOfDay.setHours(0, 0, 0, 0);
  const sevenDaysAgo = new Date(startOfDay);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 6);
  const startOfMonth = new Date(startOfDay.getFullYear(), startOfDay.getMonth(), 1);

  const [
    totalOrders,
    ordersToday,
    pendingPayments,
    confirmedOrders,
    monthOrders,
    activeProducts,
    outOfStock,
    totalInventoryUnits,
    last7DaysOrders,
    topItems,
    unitsSoldAgg,
    recentOrdersList,
  ] = await Promise.all([
    prisma.order.count(),
    prisma.order.count({ where: { createdAt: { gte: startOfDay } } }),
    prisma.payment.count({ where: { status: "PENDING_VERIFICATION" } }),
    prisma.order.findMany({ where: { status: { not: "CANCELLED" } }, select: { total: true } }),
    prisma.order.findMany({ where: { status: { not: "CANCELLED" }, createdAt: { gte: startOfMonth } }, select: { total: true } }),
    prisma.product.count({ where: { isAvailable: true } }),
    prisma.product.count({ where: { isAvailable: true, stock: { lte: 0 } } }),
    prisma.product.aggregate({ where: { isAvailable: true }, _sum: { stock: true } }),
    prisma.order.findMany({
      where: { createdAt: { gte: sevenDaysAgo }, status: { not: "CANCELLED" } },
      select: { createdAt: true, total: true },
    }),
    prisma.orderItem.groupBy({
      by: ["productName"],
      _sum: { quantity: true },
      orderBy: { _sum: { quantity: "desc" } },
      take: 5,
    }),
    prisma.orderItem.aggregate({
      where: { order: { status: { not: "CANCELLED" } } },
      _sum: { quantity: true },
    }),
    prisma.order.findMany({
      orderBy: { createdAt: "desc" },
      take: 6,
      select: { id: true, code: true, customerName: true, total: true, status: true, createdAt: true },
    }),
  ]);

  const totalSales = confirmedOrders.reduce((sum, o) => sum + o.total, 0);
  const monthlyRevenue = monthOrders.reduce((sum, o) => sum + o.total, 0);

  // Ventas de los últimos 7 días, agrupadas por fecha (SQLite no agrupa por fecha
  // truncada en Prisma directamente, así que se agrega en memoria — el volumen
  // de una floristería no lo justifica a nivel de base de datos).
  const salesByDay: { date: string; total: number }[] = [];
  for (let i = 6; i >= 0; i--) {
    const day = new Date(startOfDay);
    day.setDate(day.getDate() - i);
    const dayKey = day.toISOString().slice(0, 10);
    const total = last7DaysOrders
      .filter((o) => o.createdAt.toISOString().slice(0, 10) === dayKey)
      .reduce((sum, o) => sum + o.total, 0);
    salesByDay.push({ date: dayKey, total });
  }

  const topProducts = topItems.map((t) => ({ name: t.productName, quantity: t._sum.quantity ?? 0 }));

  res.json({
    totalOrders,
    ordersToday,
    pendingPayments,
    totalSales,
    monthlyRevenue,
    unitsSold: unitsSoldAgg._sum.quantity ?? 0,
    activeProducts,
    outOfStock,
    totalInventoryUnits: totalInventoryUnits._sum.stock ?? 0,
    salesByDay,
    topProducts,
    recentOrders: recentOrdersList,
  });
}

/** Datos bancarios y de contacto visibles públicamente en el checkout (sin secretos). */
export async function publicBusinessInfo(_req: Request, res: Response): Promise<void> {
  const settings = await prisma.businessSettings.upsert({
    where: { id: "singleton" },
    create: { id: "singleton" },
    update: {},
  });
  res.json({
    businessName: settings.businessName,
    bankName: settings.bankName,
    bankAccountType: settings.bankAccountType,
    bankAccountNumber: settings.bankAccountNumber,
    bankAccountHolder: settings.bankAccountHolder,
    bankHolderDocument: settings.bankHolderDocument,
    whatsappNumber: settings.whatsappNumber,
    contactEmail: settings.contactEmail,
    openingHours: settings.openingHours,
  });
}

export async function getSettings(_req: Request, res: Response): Promise<void> {
  const settings = await prisma.businessSettings.upsert({
    where: { id: "singleton" },
    create: { id: "singleton" },
    update: {},
  });
  res.json(settings);
}

export async function updateSettings(req: Request, res: Response): Promise<void> {
  const settings = await prisma.businessSettings.upsert({
    where: { id: "singleton" },
    create: { id: "singleton", ...req.body },
    update: req.body,
  });
  await recordAudit({ actorId: req.auth?.userId, actorRole: "ADMIN", action: "UPDATE", entity: "BusinessSettings" });
  res.json(settings);
}

/** Sirve el comprobante de transferencia SOLO a administradores autenticados. */
export async function getReceiptFile(req: Request, res: Response): Promise<void> {
  const payment = await prisma.payment.findUnique({ where: { orderId: req.params.orderId } });
  if (!payment) throw new HttpError(404, "Comprobante no encontrado");

  const filePath = path.join(RECEIPTS_DIR, payment.receiptFilename);
  res.sendFile(filePath);
}
