import { NextFunction, Request, Response } from "express";
import { ZodSchema } from "zod";

/** Valida y sanea req.body contra un schema de Zod antes de llegar al controller. */
export function validateBody(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      res.status(400).json({ error: "Datos inválidos", details: result.error.flatten().fieldErrors });
      return;
    }
    req.body = result.data;
    next();
  };
}
