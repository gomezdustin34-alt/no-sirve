import { Router } from "express";
import { login, logout, me, register } from "../controllers/auth.controller";
import { validateBody } from "../middleware/validate";
import { loginSchema, registerSchema } from "../schemas/auth.schema";
import { authRateLimiter } from "../middleware/rateLimit";
import { requireAuth } from "../middleware/auth";

export const authRouter = Router();

authRouter.post("/register", authRateLimiter, validateBody(registerSchema), register);
authRouter.post("/login", authRateLimiter, validateBody(loginSchema), login);
authRouter.post("/logout", logout);
authRouter.get("/me", requireAuth, me);
