import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORES, FUENTE } from "./estilo";

/**
 * Texto corto que entra letra por letra (desenfoque → nítido),
 * con una línea matemática que se dibuja debajo y un símbolo de acento.
 */
export const TituloAnimado: React.FC<{
  texto: string;
  subtexto?: string;
  tamano?: number;
}> = ({ texto, subtexto, tamano = 110 }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const letras = Array.from(texto);
  // Más rápido si el texto es largo o el plano es corto.
  const escalon = Math.max(
    0.6,
    Math.min(1.6, (durationInFrames * 0.3) / letras.length),
  );

  const salida = interpolate(
    frame,
    [durationInFrames - 8, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const linea = interpolate(
    frame,
    [4, 4 + letras.length * escalon + 8],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );
  const acento = spring({ frame: frame - 6, fps, config: { damping: 14 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        opacity: salida,
        transform: `translateY(${(1 - salida) * -20}px)`,
        background:
          "radial-gradient(ellipse at center, rgba(0,0,0,0.45) 0%, rgba(0,0,0,0) 60%)",
      }}
    >
      <div
        style={{
          position: "relative",
          textAlign: "center",
          fontFamily: FUENTE,
        }}
      >
        <span
          style={{
            position: "absolute",
            left: -70,
            top: -60,
            fontSize: 70,
            color: COLORES.acento,
            opacity: acento * 0.9,
            transform: `rotate(${(1 - acento) * -40}deg) scale(${acento})`,
          }}
        >
          π
        </span>
        <div
          style={{
            fontSize: tamano,
            fontWeight: 800,
            color: COLORES.texto,
            letterSpacing: -1,
            textShadow: "0 6px 30px rgba(0,0,0,0.5)",
            whiteSpace: "pre",
          }}
        >
          {letras.map((letra, i) => {
            const p = spring({
              frame: frame - i * escalon,
              fps,
              config: { damping: 18, stiffness: 160 },
            });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  opacity: p,
                  filter: `blur(${(1 - p) * 12}px)`,
                  transform: `translateY(${(1 - p) * 40}px)`,
                }}
              >
                {letra}
              </span>
            );
          })}
        </div>
        <svg
          width="100%"
          height="24"
          style={{ display: "block", marginTop: 8 }}
        >
          <line
            x1="0"
            y1="12"
            x2="100%"
            y2="12"
            stroke={COLORES.acento}
            strokeWidth="4"
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray="1"
            strokeDashoffset={1 - linea}
          />
          <circle
            cx={`${linea * 100}%`}
            cy="12"
            r="7"
            fill={COLORES.acento}
            opacity={linea < 1 ? 1 : 0}
          />
        </svg>
        {subtexto && (
          <div
            style={{
              fontSize: tamano * 0.32,
              color: "rgba(255,255,255,0.85)",
              marginTop: 18,
              letterSpacing: 6,
              opacity: linea,
            }}
          >
            {subtexto}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
