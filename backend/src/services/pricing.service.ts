import { prisma } from "../config/db";
import { HttpError } from "../middleware/errorHandler";

export interface CartLineInput {
  productId: string;
  quantity: number;
  customization?: {
    size?: "pequeno" | "mediano" | "grande";
    wrapping?: "clasica" | "premium" | "de-lujo";
    extras?: string[];
  };
}

export interface PricedLine extends CartLineInput {
  productName: string;
  unitPrice: number;
  lineTotal: number;
}

const SIZE_SURCHARGE: Record<string, number> = { pequeno: 0, mediano: 8000, grande: 18000 };
const WRAPPING_SURCHARGE: Record<string, number> = { clasica: 0, premium: 6000, "de-lujo": 15000 };
const EXTRA_PRICE = 5000; // por extra (chocolates, peluche, vela, etc.)

/**
 * Recalcula el precio real de cada línea consultando el producto en base de datos.
 * Nunca confía en un precio enviado desde el frontend — así se evita la
 * manipulación de precios (punto 48 del brief).
 */
export async function priceCart(lines: CartLineInput[]): Promise<{ items: PricedLine[]; subtotal: number }> {
  if (lines.length === 0) throw new HttpError(400, "El carrito está vacío");

  const items: PricedLine[] = [];
  let subtotal = 0;

  for (const line of lines) {
    if (line.quantity < 1 || line.quantity > 20) {
      throw new HttpError(400, "Cantidad inválida");
    }

    const product = await prisma.product.findUnique({ where: { id: line.productId } });
    if (!product || !product.isAvailable) {
      throw new HttpError(400, `Producto no disponible: ${line.productId}`);
    }
    if (product.stock <= 0) {
      throw new HttpError(409, `"${product.name}" está agotado.`);
    }
    if (product.stock < line.quantity) {
      throw new HttpError(409, `Solo quedan ${product.stock} unidades de "${product.name}".`);
    }

    let unitPrice = product.basePrice;
    if (line.customization?.size) unitPrice += SIZE_SURCHARGE[line.customization.size] ?? 0;
    if (line.customization?.wrapping) unitPrice += WRAPPING_SURCHARGE[line.customization.wrapping] ?? 0;
    if (line.customization?.extras) unitPrice += line.customization.extras.length * EXTRA_PRICE;

    const lineTotal = unitPrice * line.quantity;
    subtotal += lineTotal;

    items.push({ ...line, productName: product.name, unitPrice, lineTotal });
  }

  return { items, subtotal };
}

const SHIPPING_BY_CITY: Record<string, number> = {
  default: 12000,
};

export function calculateShipping(city: string): number {
  return SHIPPING_BY_CITY[city.toLowerCase()] ?? SHIPPING_BY_CITY.default;
}

export async function applyCoupon(code: string | undefined, subtotal: number): Promise<number> {
  if (!code) return 0;

  const coupon = await prisma.coupon.findUnique({ where: { code } });
  if (!coupon || !coupon.isActive) return 0;
  if (coupon.expiresAt && coupon.expiresAt < new Date()) return 0;
  if (coupon.maxUses && coupon.usedCount >= coupon.maxUses) return 0;
  if (subtotal < coupon.minPurchase) return 0;

  if (coupon.percentOff) return Math.round((subtotal * coupon.percentOff) / 100);
  if (coupon.amountOff) return Math.min(coupon.amountOff, subtotal);
  return 0;
}
