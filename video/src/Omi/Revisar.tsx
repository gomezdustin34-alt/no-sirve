import React from "react";
import { z } from "zod";
import {
  AbsoluteFill,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FUENTE } from "./estilo";

export const esquemaRevisar = z.object({
  archivo: z.string(),
});

/**
 * Herramienta para mirar un clip crudo y anotar en qué segundo empieza
 * el mejor momento (el valor que va en `desde` dentro de config.ts).
 */
export const Revisar: React.FC<z.infer<typeof esquemaRevisar>> = ({
  archivo,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const segundos = (frame / fps).toFixed(1).replace(".", ",");
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {archivo ? (
        <OffthreadVideo
          src={staticFile(archivo)}
          style={{ width: "100%", height: "100%", objectFit: "contain" }}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          top: 30,
          left: 30,
          padding: "12px 24px",
          borderRadius: 12,
          backgroundColor: "rgba(0,0,0,0.7)",
          color: "white",
          fontFamily: FUENTE,
          fontSize: 56,
          fontWeight: 700,
        }}
      >
        desde: {segundos}
        <div style={{ fontSize: 24, fontWeight: 400, opacity: 0.7 }}>
          {archivo}
        </div>
      </div>
    </AbsoluteFill>
  );
};
