import { env } from "../config/env";

interface OrderNotificationData {
  code: string;
  customerName: string;
  customerPhone: string;
  recipientName: string;
  total: number;
  deliveryDate: string;
  deliveryWindow: string;
  cardMessage?: string | null;
  items: { productName: string; quantity: number }[];
  adminUrl: string;
}

function formatCurrency(cents: number): string {
  return (cents / 100).toLocaleString("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });
}

export function buildOrderWhatsappMessage(data: OrderNotificationData): string {
  const itemsText = data.items.map((i) => `🌹 ${i.quantity} × ${i.productName}`).join("\n");
  return [
    "🌷 NUEVO PEDIDO",
    "DÍGALO CON FLORES",
    "",
    `Pedido: #${data.code}`,
    "",
    `Cliente:\n${data.customerName}`,
    "",
    `Teléfono:\n${data.customerPhone}`,
    "",
    `Destinatario:\n${data.recipientName}`,
    "",
    `Total:\n${formatCurrency(data.total)}`,
    "",
    "Pago:\nTransferencia bancaria",
    "",
    "Estado:\nPendiente de verificación",
    "",
    `Entrega:\n${data.deliveryDate}`,
    "",
    `Horario:\n${data.deliveryWindow}`,
    "",
    `Productos:\n${itemsText}`,
    ...(data.cardMessage ? ["", `Mensaje:\n"${data.cardMessage}"`] : []),
    "",
    `Ver pedido:\n${data.adminUrl}`,
  ].join("\n");
}

/**
 * Envía la notificación de nuevo pedido al WhatsApp del propietario usando
 * la API oficial de WhatsApp Cloud (Meta). Si faltan credenciales en .env,
 * falla de forma controlada y se registra en la tabla Notification —
 * el pedido NUNCA se pierde por esto (punto 50 del brief).
 */
export async function sendOwnerWhatsappNotification(data: OrderNotificationData): Promise<void> {
  if (!env.WHATSAPP_ACCESS_TOKEN || !env.WHATSAPP_PHONE_NUMBER_ID || !env.OWNER_WHATSAPP_NUMBER) {
    throw new Error("Credenciales de WhatsApp no configuradas (WHATSAPP_ACCESS_TOKEN / WHATSAPP_PHONE_NUMBER_ID / OWNER_WHATSAPP_NUMBER)");
  }

  const message = buildOrderWhatsappMessage(data);
  const url = `https://graph.facebook.com/v20.0/${env.WHATSAPP_PHONE_NUMBER_ID}/messages`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.WHATSAPP_ACCESS_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messaging_product: "whatsapp",
      to: env.OWNER_WHATSAPP_NUMBER,
      type: "text",
      text: { body: message },
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`WhatsApp API respondió ${response.status}: ${errorBody}`);
  }
}
