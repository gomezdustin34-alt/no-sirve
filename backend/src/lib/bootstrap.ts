import bcrypt from "bcryptjs";
import { prisma } from "../config/db";
import { env } from "../config/env";

const DEMO_CATEGORIES = [
  { name: "Rosas Clásicas", slug: "rosas-clasicas", sortOrder: 1 },
  { name: "Cumpleaños", slug: "cumpleanos", sortOrder: 2 },
  { name: "Aniversario", slug: "aniversario", sortOrder: 3 },
  { name: "Agradecimiento", slug: "agradecimiento", sortOrder: 4 },
  { name: "Colección Silvestre", slug: "silvestre", sortOrder: 5 },
  { name: "Reconciliación", slug: "reconciliacion", sortOrder: 6 },
];

const DEMO_PRODUCTS = [
  { slug: "suspiro-de-primavera", name: "Suspiro de Primavera", description: "Un arreglo delicado de rosas rosadas y flores de temporada, envuelto en papel kraft y lino natural.", meaning: "Para decir lo que las palabras no alcanzan a explicar.", flowersUsed: "Rosas rosadas, astromelias, eucalipto", basePrice: 98000, images: ["/assets/img/placeholder-arreglo-1.svg"], categorySlug: "rosas-clasicas", occasion: "romantico", stock: 12, isFeatured: true },
  { slug: "carta-de-amor", name: "Carta de Amor", description: "Docena de rosas rojas de tallo largo con una tarjeta artesanal escrita a mano.", meaning: "El clásico que nunca falla, para un amor que se dice fuerte.", flowersUsed: "12 rosas rojas", basePrice: 145000, images: ["/assets/img/placeholder-arreglo-2.svg"], categorySlug: "aniversario", occasion: "romantico", stock: 8, isFeatured: true },
  { slug: "jardin-de-abril", name: "Jardín de Abril", description: "Mezcla vibrante de flores de campo en tonos durazno y lavanda, como si trajeras un jardín entero.", meaning: "Alegría espontánea, sin motivo especial.", flowersUsed: "Ranúnculos, lisianthus, lavanda", basePrice: 112000, images: ["/assets/img/placeholder-arreglo-3.svg"], categorySlug: "silvestre", occasion: "cualquier-dia", stock: 5 },
  { slug: "siempre-tu", name: "Siempre Tú", description: "Peonías y rosas blancas en una caja de sombrero, elegante y atemporal.", meaning: "Para admirar a alguien profundamente.", flowersUsed: "Peonías, rosas blancas", basePrice: 168000, images: ["/assets/img/placeholder-arreglo-4.svg"], categorySlug: "aniversario", occasion: "especial", stock: 6, isFeatured: true },
  { slug: "dulce-recuerdo", name: "Dulce Recuerdo", description: "Girasoles y flores amarillas cálidas, envueltas en papel de arroz.", meaning: "Cuando alguien te hace mucha falta.", flowersUsed: "Girasoles, crisantemos amarillos", basePrice: 89000, images: ["/assets/img/placeholder-arreglo-5.svg"], categorySlug: "silvestre", occasion: "cualquier-dia", stock: 15 },
  { slug: "para-ti", name: "Para Ti", description: "Orquídeas delicadas en tonos lavanda, para un gracias sincero.", meaning: "Gratitud pura, sin necesidad de más palabras.", flowersUsed: "Orquídeas, alstroemeria lila", basePrice: 124000, images: ["/assets/img/placeholder-arreglo-6.svg"], categorySlug: "agradecimiento", occasion: "agradecimiento", stock: 6 },
  { slug: "porque-si", name: "Porque Sí", description: "Ramo silvestre de flores mixtas, pequeño y espontáneo.", meaning: "No necesitas una razón para regalar flores.", flowersUsed: "Mix de flores de temporada", basePrice: 65000, images: ["/assets/img/placeholder-arreglo-7.svg"], categorySlug: "silvestre", occasion: "cualquier-dia", stock: 20 },
  { slug: "eterno", name: "Eterno", description: "Arreglo de perdón: flores blancas y rosas suaves, tarjeta incluida para tus propias palabras.", meaning: "Un gesto sincero para reparar y volver a empezar.", flowersUsed: "Rosas blancas, hortensias", basePrice: 132000, images: ["/assets/img/placeholder-arreglo-8.svg"], categorySlug: "reconciliacion", occasion: "reconciliacion", stock: 3 },
];

/**
 * Se ejecuta en cada arranque del servidor. Es completamente idempotente:
 * - El usuario admin y la configuración del negocio solo se crean si no existen.
 * - El catálogo de ejemplo SOLO se siembra si la base de datos está vacía
 *   (0 productos), para no pisar nunca los datos reales que cargue el admin
 *   después de la primera vez que arranca en producción.
 */
export async function runBootstrap(): Promise<void> {
  const existingAdmin = await prisma.user.findUnique({ where: { email: env.ADMIN_EMAIL } }).catch(() => null);
  if (!existingAdmin && env.ADMIN_EMAIL && env.ADMIN_PASSWORD) {
    await prisma.user.create({
      data: {
        name: "Propietario",
        email: env.ADMIN_EMAIL,
        passwordHash: await bcrypt.hash(env.ADMIN_PASSWORD, 12),
        role: "ADMIN",
      },
    });
    console.log(`✔ Usuario admin creado: ${env.ADMIN_EMAIL}`);
  }

  await prisma.businessSettings.upsert({
    where: { id: "singleton" },
    create: { id: "singleton" },
    update: {},
  });

  const productCount = await prisma.product.count();
  if (productCount === 0) {
    console.log("Base de datos vacía: sembrando catálogo de ejemplo...");
    const categoryMap = new Map<string, string>();
    for (const cat of DEMO_CATEGORIES) {
      const created = await prisma.category.upsert({ where: { slug: cat.slug }, create: cat, update: cat });
      categoryMap.set(cat.slug, created.id);
    }
    for (const { categorySlug, ...product } of DEMO_PRODUCTS) {
      await prisma.product.upsert({
        where: { slug: product.slug },
        create: { ...product, images: JSON.stringify(product.images), categoryId: categoryMap.get(categorySlug) ?? null },
        update: { ...product, images: JSON.stringify(product.images), categoryId: categoryMap.get(categorySlug) ?? null },
      });
    }
    console.log("✔ Catálogo de ejemplo sembrado.");
  }
}
