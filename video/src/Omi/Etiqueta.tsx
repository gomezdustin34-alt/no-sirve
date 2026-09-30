import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORES, FUENTE } from "./estilo";

const ICONOS = ["π", "√", "∑", "Φ", "Δ", "∞"];

/**
 * Rótulo tipo TV en la parte baja: un cuadro con un símbolo matemático
 * y el nombre (se escribe letra por letra). Queda por encima de la zona
 * donde TikTok/Instagram ponen sus botones.
 */
export const Etiqueta: React.FC<{ texto: string; semilla: number }> = ({
  texto,
  semilla,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, height } = useVideoConfig();
  const entrada = Easing.out(Easing.cubic)(Math.min(1, frame / 10));
  const icono = spring({ frame: frame - 2, fps, config: { damping: 11 } });
  const letras = Math.floor(Math.max(0, frame - 5) * 1.6);
  const salida = interpolate(
    frame,
    [durationInFrames - 7, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const visible = Array.from(texto).slice(0, letras).join("");
  const cursor = letras < texto.length && Math.floor(frame / 3) % 2 === 0;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: 56,
          right: 56,
          top: height * 0.7,
          display: "flex",
          alignItems: "center",
          gap: 20,
          opacity: salida,
          transform: `translateY(${(1 - salida) * 20}px)`,
          clipPath: `inset(0 ${(1 - entrada) * 100}% 0 0)`,
          fontFamily: FUENTE,
        }}
      >
        <div
          style={{
            flex: "0 0 auto",
            width: 92,
            height: 92,
            borderRadius: 12,
            backgroundColor: COLORES.acento,
            color: COLORES.fondo,
            fontSize: 58,
            fontWeight: 900,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `rotate(${(1 - icono) * -90}deg) scale(${icono})`,
          }}
        >
          {ICONOS[semilla % ICONOS.length]}
        </div>
        <div
          style={{
            padding: "14px 26px",
            borderRadius: 10,
            backgroundColor: "rgba(7,11,26,0.72)",
            borderLeft: `4px solid ${COLORES.acento2}`,
            color: COLORES.texto,
            fontSize: 50,
            fontWeight: 800,
            letterSpacing: 1,
            lineHeight: 1.2,
            maxWidth: "80%",
          }}
        >
          {visible}
          <span style={{ opacity: cursor ? 1 : 0, color: COLORES.acento }}>
            ▌
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
