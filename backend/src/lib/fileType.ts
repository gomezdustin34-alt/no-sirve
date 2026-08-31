/**
 * Verifica los "magic bytes" reales de un archivo ya guardado en disco para
 * confirmar que el contenido coincide con el MIME declarado (evita que un
 * .exe renombrado como .jpg pase el filtro de multer, que solo mira el nombre/mimetype declarado).
 */
export async function detectRealMime(filePath: string): Promise<string | null> {
  const { fileTypeFromFile } = await import("file-type");
  const detected = await fileTypeFromFile(filePath);
  return detected?.mime ?? null;
}
