import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FOTOS_VERTICALES } from "./config";
import { COLORES, FUENTE } from "./estilo";
import { framesPorBeat } from "./timeline";

/** Una polaroid que cae, se acomoda con un pequeño rebote y queda girada. */
const Polaroid: React.FC<{
  src: string;
  pie?: string;
  semilla: number;
  /** Frame (local) donde entra. */
  entrada: number;
  /** 0 = la foto de arriba; 1, 2… = fotos que ya quedaron debajo. */
  profundidad: number;
}> = ({ src, pie, semilla, entrada, profundidad }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const local = frame - entrada;
  if (local < 0) return null;

  const caida = spring({
    frame: local,
    fps,
    config: { damping: 13, stiffness: 170, mass: 0.8 },
  });
  const r = (k: string) => random(`foto-${semilla}-${k}`);
  const giroFinal = (r("g") - 0.5) * 9;
  const giro = giroFinal + (1 - caida) * (r("s") < 0.5 ? -14 : 14);
  const escala = 1.25 - caida * 0.25;
  // Las fotos de abajo se corren un poco y se oscurecen.
  const corrimientoX = profundidad * (r("dx") < 0.5 ? -26 : 26);
  const corrimientoY = profundidad * -18;
  const oscuro = 1 - Math.min(0.45, profundidad * 0.18);

  const vertical = FOTOS_VERTICALES.includes(src);
  const anchoFoto = vertical ? width * 0.66 : width * 0.84;
  const altoFoto = vertical ? (anchoFoto * 4) / 3 : (anchoFoto * 3) / 4;
  const borde = 22;
  const zoom = interpolate(local, [0, durationInFrames], [1.0, 1.1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        left: width / 2,
        top: height * 0.44,
        transform: `translate(-50%, -50%) translate(${corrimientoX}px, ${corrimientoY}px) rotate(${giro}deg) scale(${escala})`,
        opacity: Math.min(1, local / 3),
        filter: `brightness(${oscuro})`,
      }}
    >
      <div
        style={{
          backgroundColor: "#fbfaf6",
          padding: `${borde}px ${borde}px ${pie ? 120 : borde * 3}px`,
          borderRadius: 6,
          boxShadow:
            "0 30px 70px rgba(0,0,0,0.55), 0 6px 18px rgba(0,0,0,0.35)",
          position: "relative",
        }}
      >
        <div
          style={{
            width: anchoFoto,
            height: altoFoto,
            overflow: "hidden",
            backgroundColor: "#222",
          }}
        >
          <Img
            src={staticFile(src)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${zoom})`,
            }}
          />
        </div>
        {pie && (
          <div
            style={{
              position: "absolute",
              left: borde,
              right: borde,
              bottom: 26,
              textAlign: "center",
              fontFamily: FUENTE,
              fontWeight: 800,
              fontStyle: "italic",
              fontSize: 40,
              color: COLORES.azul,
              opacity: interpolate(local, [6, 14], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          >
            {pie}
          </div>
        )}
        {/* cinta adhesiva arriba */}
        <div
          style={{
            position: "absolute",
            top: -22,
            left: "50%",
            width: 170,
            height: 46,
            transform: `translateX(-50%) rotate(${(r("c") - 0.5) * 10}deg)`,
            backgroundColor: "rgba(255,201,60,0.75)",
            boxShadow: "0 2px 6px rgba(0,0,0,0.2)",
          }}
        />
      </div>
    </div>
  );
};

/**
 * Plano de fotos: una sola polaroid, o varias que van cayendo una por beat
 * y se apilan. Fondo: la última foto, desenfocada y oscurecida.
 */
export const PlanoFotos: React.FC<{
  fotos: string[];
  pies?: string[];
  semilla: number;
  /** Frame (local) donde cae la primera foto. */
  inicio: number;
}> = ({ fotos, pies, semilla, inicio }) => {
  const frame = useCurrentFrame();
  const entradas = fotos.map((_, k) => inicio + Math.round(k * framesPorBeat));
  let actual = 0;
  entradas.forEach((e, k) => {
    if (frame >= e) actual = k;
  });

  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORES.fondo, overflow: "hidden" }}
    >
      <Img
        src={staticFile(fotos[actual])}
        style={{
          position: "absolute",
          inset: -60,
          width: "calc(100% + 120px)",
          height: "calc(100% + 120px)",
          objectFit: "cover",
          filter: "blur(38px) brightness(0.45) saturate(1.3)",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "70px 70px",
        }}
      />
      {fotos.map((src, k) => (
        <Polaroid
          key={k}
          src={src}
          pie={pies?.[k]}
          semilla={semilla * 10 + k}
          entrada={entradas[k]}
          profundidad={Math.max(0, actual - k)}
        />
      ))}
    </AbsoluteFill>
  );
};
