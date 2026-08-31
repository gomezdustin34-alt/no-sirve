// SQLite no soporta enums nativos en Prisma (ver prisma/schema.prisma), así
// que estos campos se guardan como String y se tipan aquí en la capa de aplicación.

export type Role = "CUSTOMER" | "ADMIN";

export type OrderStatus =
  | "RECEIVED"
  | "PAYMENT_VERIFIED"
  | "PREPARING"
  | "ON_THE_WAY"
  | "DELIVERED"
  | "CANCELLED";

export type PaymentStatus = "PENDING_VERIFICATION" | "CONFIRMED" | "REJECTED";

export type NotificationChannel = "WHATSAPP" | "EMAIL";

export type NotificationStatus = "PENDING" | "SENT" | "FAILED";
