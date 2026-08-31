import path from "path";
import express from "express";
import "express-async-errors"; // Express 4 no reenvía rechazos de promesas a next() por sí solo — este parche sí lo hace.
import helmet from "helmet";
import cors from "cors";
import cookieParser from "cookie-parser";
import { env } from "./config/env";
import { attachAuth } from "./middleware/auth";
import { errorHandler, notFoundHandler } from "./middleware/errorHandler";
import { publicApiLimiter } from "./middleware/rateLimit";
import { authRouter } from "./routes/auth.routes";
import { productRouter } from "./routes/product.routes";
import { categoryRouter } from "./routes/category.routes";
import { orderRouter } from "./routes/order.routes";
import { adminRouter } from "./routes/admin.routes";
import { settingsRouter } from "./routes/settings.routes";
import { PRODUCT_IMAGES_DIR, PRODUCT_IMAGES_PUBLIC_PATH } from "./middleware/uploadProductImage";
import { runBootstrap } from "./lib/bootstrap";

const app = express();
const FRONTEND_DIR = path.join(__dirname, "..", "..", "frontend");

// El frontend es HTML estático con <script> y style="" inline por diseño (sin build
// step ni nonces por request), así que se desactiva solo la CSP de Helmet; el resto
// de sus protecciones (X-Frame-Options, X-Content-Type-Options, HSTS...) siguen activas.
app.use(helmet({ contentSecurityPolicy: false }));
app.use(
  cors({
    origin: env.FRONTEND_ORIGIN,
    credentials: true,
  })
);
app.use(express.json({ limit: "1mb" }));
app.use(cookieParser());
app.use(attachAuth);
app.use(publicApiLimiter);

app.get("/health", (_req, res) => res.json({ status: "ok" }));

app.use("/api/auth", authRouter);
app.use("/api/products", productRouter);
app.use("/api/categories", categoryRouter);
app.use("/api/orders", orderRouter);
app.use("/api/admin", adminRouter);
app.use("/api/settings", settingsRouter);

// Ruta explícita para las fotos de producto: funciona igual sin importar si
// PRODUCT_IMAGES_DIR vive dentro del frontend (local) o en un volumen aparte (producción).
app.use(PRODUCT_IMAGES_PUBLIC_PATH, express.static(PRODUCT_IMAGES_DIR));
app.use(express.static(FRONTEND_DIR));

app.use(notFoundHandler);
app.use(errorHandler);

runBootstrap()
  .catch((err) => {
    console.error("Error en el arranque inicial (bootstrap):", err);
  })
  .finally(() => {
    app.listen(env.PORT, () => {
      console.log(`🌷 Dígalo con Flores escuchando en http://localhost:${env.PORT}`);
    });
  });
