import { prisma } from "../config/db";
import { OrderStatus } from "../lib/status";
import { sendOwnerWhatsappNotification } from "./whatsapp.service";
import {
  customerOrderEmailHtml,
  ownerOrderEmailHtml,
  sendEmail,
  statusUpdateEmailHtml,
} from "./email.service";
import { env } from "../config/env";

export const STATUS_LABELS: Record<OrderStatus, string> = {
  RECEIVED: "Pedido recibido",
  PAYMENT_VERIFIED: "Pago verificado",
  PREPARING: "Preparando tus flores",
  ON_THE_WAY: "En camino",
  DELIVERED: "Entregado",
  CANCELLED: "Cancelado",
};

export async function generateOrderCode(): Promise<string> {
  const count = await prisma.order.count();
  return `DF-${1000 + count + 1}`;
}

/**
 * Dispara las notificaciones de un pedido nuevo SIN bloquear ni hacer fallar
 * la creación del pedido si WhatsApp o email fallan (punto 50 del brief).
 * El pedido ya está guardado en base de datos antes de llamar a esta función;
 * cada intento queda registrado en la tabla Notification como sent/failed.
 */
export async function notifyNewOrder(orderId: string): Promise<void> {
  const order = await prisma.order.findUniqueOrThrow({
    where: { id: orderId },
    include: { items: true, payment: true },
  });

  const adminUrl = `${env.FRONTEND_ORIGIN}/admin/pedidos.html?order=${order.id}`;
  const trackingUrl = `${env.FRONTEND_ORIGIN}/seguimiento.html?id=${order.id}`;
  const totalFormatted = (order.total / 100).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });

  // --- WhatsApp al dueño ---
  await attemptNotification(orderId, "WHATSAPP", async () => {
    await sendOwnerWhatsappNotification({
      code: order.code,
      customerName: order.customerName,
      customerPhone: order.customerPhone,
      recipientName: order.recipientName,
      total: order.total,
      deliveryDate: order.deliveryDate.toLocaleDateString("es-CO"),
      deliveryWindow: order.deliveryWindow,
      cardMessage: order.cardMessage,
      items: order.items.map((i) => ({ productName: i.productName, quantity: i.quantity })),
      adminUrl,
    });
  });

  // --- Email al dueño ---
  await attemptNotification(orderId, "EMAIL", async () => {
    if (!env.OWNER_EMAIL) throw new Error("OWNER_EMAIL no configurado");
    await sendEmail({
      to: env.OWNER_EMAIL,
      subject: `🌷 Nuevo pedido #${order.code} — Dígalo con Flores`,
      html: ownerOrderEmailHtml({
        code: order.code,
        customerName: order.customerName,
        recipientName: order.recipientName,
        total: totalFormatted,
        paymentMethod: "Transferencia bancaria",
        status: "Pendiente de verificación",
        deliveryDate: order.deliveryDate.toLocaleDateString("es-CO"),
        deliveryWindow: order.deliveryWindow,
        adminUrl,
      }),
    });
  });

  // --- Email de confirmación al cliente ---
  await attemptNotification(orderId, "EMAIL", async () => {
    await sendEmail({
      to: order.customerEmail,
      subject: "Tu pedido de Dígalo con Flores 🌷",
      html: customerOrderEmailHtml({
        code: order.code,
        total: totalFormatted,
        deliveryDate: order.deliveryDate.toLocaleDateString("es-CO"),
        trackingUrl,
      }),
    });
  });
}

export async function notifyStatusUpdate(orderId: string): Promise<void> {
  const order = await prisma.order.findUniqueOrThrow({ where: { id: orderId } });
  const trackingUrl = `${env.FRONTEND_ORIGIN}/seguimiento.html?id=${order.id}`;

  await attemptNotification(orderId, "EMAIL", async () => {
    await sendEmail({
      to: order.customerEmail,
      subject: `Actualización de tu pedido #${order.code} — Dígalo con Flores`,
      html: statusUpdateEmailHtml({ code: order.code, statusLabel: STATUS_LABELS[order.status as OrderStatus], trackingUrl }),
    });
  });
}

async function attemptNotification(orderId: string, channel: "WHATSAPP" | "EMAIL", send: () => Promise<void>): Promise<void> {
  const notification = await prisma.notification.create({ data: { orderId, channel, status: "PENDING" } });
  try {
    await send();
    await prisma.notification.update({ where: { id: notification.id }, data: { status: "SENT", sentAt: new Date() } });
  } catch (err) {
    await prisma.notification.update({
      where: { id: notification.id },
      data: { status: "FAILED", error: err instanceof Error ? err.message : String(err) },
    });
  }
}
