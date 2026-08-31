import { z } from "zod";

const customizationSchema = z.object({
  size: z.enum(["pequeno", "mediano", "grande"]).optional(),
  wrapping: z.enum(["clasica", "premium", "de-lujo"]).optional(),
  extras: z.array(z.string().max(50)).max(10).optional(),
}).optional();

export const cartLineSchema = z.object({
  productId: z.string().min(1),
  quantity: z.number().int().min(1).max(20),
  customization: customizationSchema,
});

export const priceCartSchema = z.object({
  items: z.array(cartLineSchema).min(1).max(30),
  city: z.string().trim().max(80).default("default"),
  couponCode: z.string().trim().max(40).optional(),
});

export const createOrderSchema = z.object({
  customerName: z.string().trim().min(2).max(100),
  customerEmail: z.string().trim().email(),
  customerPhone: z.string().trim().min(6).max(30),
  recipientName: z.string().trim().min(2).max(100),
  recipientPhone: z.string().trim().max(30).optional(),
  deliveryAddress: z.string().trim().min(5).max(300),
  deliveryCity: z.string().trim().min(2).max(80),
  deliveryDate: z.string().datetime().or(z.string().min(8)),
  deliveryWindow: z.string().trim().min(2).max(60),
  cardMessage: z.string().trim().max(500).optional(),
  couponCode: z.string().trim().max(40).optional(),
  items: z.array(cartLineSchema).min(1).max(30),
});

export const confirmTransferSchema = z.object({
  bankName: z.string().trim().min(2).max(80),
  amount: z.coerce.number().int().positive(),
  transferDate: z.string().min(8),
  referenceNumber: z.string().trim().min(2).max(80),
  holderName: z.string().trim().min(2).max(100),
});

export const updateOrderStatusSchema = z.object({
  status: z.enum(["RECEIVED", "PAYMENT_VERIFIED", "PREPARING", "ON_THE_WAY", "DELIVERED", "CANCELLED"]),
});

export const reviewPaymentSchema = z.object({
  decision: z.enum(["CONFIRMED", "REJECTED"]),
});

// El admin puede ajustar casi todos los datos operativos de un pedido después de creado
// (dirección/fecha mal escrita por el cliente, cambios de última hora, notas internas).
export const adminUpdateOrderDetailsSchema = z.object({
  recipientName: z.string().trim().min(2).max(100).optional(),
  recipientPhone: z.string().trim().max(30).optional(),
  deliveryAddress: z.string().trim().min(5).max(300).optional(),
  deliveryCity: z.string().trim().min(2).max(80).optional(),
  deliveryDate: z.string().min(8).optional(),
  deliveryWindow: z.string().trim().min(2).max(60).optional(),
  cardMessage: z.string().trim().max(500).optional(),
  adminNotes: z.string().trim().max(2000).optional(),
});
