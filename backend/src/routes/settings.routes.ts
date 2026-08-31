import { Router } from "express";
import { publicBusinessInfo } from "../controllers/admin.controller";

export const settingsRouter = Router();

settingsRouter.get("/public", publicBusinessInfo);
