import nodemailer from "nodemailer";
import { env } from "../config/env";

interface SendEmailInput {
  to: string;
  subject: string;
  html: string;
}

let transporter: nodemailer.Transporter | null = null;

function getSmtpTransporter(): nodemailer.Transporter {
  if (!transporter) {
    transporter = nodemailer.createTransport({
      host: env.SMTP_HOST,
      port: Number(env.SMTP_PORT),
      secure: Number(env.SMTP_PORT) === 465,
      auth: env.SMTP_USER ? { user: env.SMTP_USER, pass: env.SMTP_PASSWORD } : undefined,
    });
  }
  return transporter;
}

/**
 * Envía un correo usando Resend si RESEND_API_KEY está configurado,
 * o SMTP genérico en caso contrario. Si no hay ninguna credencial,
 * lanza un error controlado (el llamador lo registra como notificación fallida
 * sin perder el pedido — punto 50 del brief).
 */
export async function sendEmail({ to, subject, html }: SendEmailInput): Promise<void> {
  if (env.RESEND_API_KEY) {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from: env.SMTP_FROM, to, subject, html }),
    });
    if (!response.ok) {
      throw new Error(`Resend respondió ${response.status}: ${await response.text()}`);
    }
    return;
  }

  if (!env.SMTP_HOST || !env.SMTP_USER) {
    throw new Error("No hay proveedor de email configurado (RESEND_API_KEY o SMTP_HOST/SMTP_USER)");
  }

  await getSmtpTransporter().sendMail({ from: env.SMTP_FROM, to, subject, html });
}

const EMOTION_BAND = "background:#F8DCDC;color:#365B4A;padding:4px 12px;border-radius:999px;font-size:12px;letter-spacing:.04em;display:inline-block;";

export function ownerOrderEmailHtml(params: {
  code: string; customerName: string; recipientName: string; total: string;
  paymentMethod: string; status: string; deliveryDate: string; deliveryWindow: string; adminUrl: string;
}): string {
  return `
  <div style="font-family:Georgia,serif;background:#FFF8F2;padding:32px;color:#2E302F;">
    <div style="max-width:520px;margin:0 auto;background:#FFFDF9;border:1px solid #EDE3DB;border-radius:4px;padding:32px;">
      <p style="${EMOTION_BAND}">NUEVO PEDIDO</p>
      <h1 style="font-size:24px;margin:16px 0 4px;color:#365B4A;">Dígalo con Flores</h1>
      <p style="color:#74716D;margin:0 0 24px;">Pedido #${params.code}</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr><td style="padding:6px 0;color:#74716D;">Cliente</td><td style="text-align:right;">${params.customerName}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Destinatario</td><td style="text-align:right;">${params.recipientName}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Total</td><td style="text-align:right;font-weight:bold;">${params.total}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Pago</td><td style="text-align:right;">${params.paymentMethod}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Estado</td><td style="text-align:right;">${params.status}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Entrega</td><td style="text-align:right;">${params.deliveryDate}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Horario</td><td style="text-align:right;">${params.deliveryWindow}</td></tr>
      </table>
      <a href="${params.adminUrl}" style="display:inline-block;margin-top:24px;background:#365B4A;color:#FFFDF9;padding:12px 24px;border-radius:2px;text-decoration:none;font-size:14px;">Ver pedido</a>
    </div>
  </div>`;
}

export function customerOrderEmailHtml(params: { code: string; total: string; deliveryDate: string; trackingUrl: string }): string {
  return `
  <div style="font-family:Georgia,serif;background:#FFF8F2;padding:32px;color:#2E302F;">
    <div style="max-width:520px;margin:0 auto;background:#FFFDF9;border:1px solid #EDE3DB;border-radius:4px;padding:32px;">
      <h1 style="font-size:24px;margin:0 0 8px;color:#365B4A;">Tu pedido de Dígalo con Flores 🌷</h1>
      <p style="color:#74716D;">Hemos recibido tu pedido #${params.code} y lo estamos revisando.</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:16px;">
        <tr><td style="padding:6px 0;color:#74716D;">Total</td><td style="text-align:right;">${params.total}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Entrega estimada</td><td style="text-align:right;">${params.deliveryDate}</td></tr>
        <tr><td style="padding:6px 0;color:#74716D;">Estado del pago</td><td style="text-align:right;">Pendiente de verificación</td></tr>
      </table>
      <a href="${params.trackingUrl}" style="display:inline-block;margin-top:24px;background:#365B4A;color:#FFFDF9;padding:12px 24px;border-radius:2px;text-decoration:none;font-size:14px;">Seguir mi pedido</a>
      <p style="margin-top:24px;font-style:italic;color:#74716D;">"Hay cosas que el corazón sabe decir mejor con flores."</p>
    </div>
  </div>`;
}

export function statusUpdateEmailHtml(params: { code: string; statusLabel: string; trackingUrl: string }): string {
  return `
  <div style="font-family:Georgia,serif;background:#FFF8F2;padding:32px;color:#2E302F;">
    <div style="max-width:520px;margin:0 auto;background:#FFFDF9;border:1px solid #EDE3DB;border-radius:4px;padding:32px;">
      <h1 style="font-size:22px;margin:0 0 8px;color:#365B4A;">Actualización de tu pedido #${params.code}</h1>
      <p style="font-size:16px;">Nuevo estado: <strong>${params.statusLabel}</strong></p>
      <a href="${params.trackingUrl}" style="display:inline-block;margin-top:16px;background:#365B4A;color:#FFFDF9;padding:12px 24px;border-radius:2px;text-decoration:none;font-size:14px;">Ver seguimiento</a>
    </div>
  </div>`;
}
