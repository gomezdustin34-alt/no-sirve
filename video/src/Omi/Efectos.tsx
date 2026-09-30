import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  random,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORES, FUENTE, SIMBOLOS } from "./estilo";
import { energiaEn, framesPorBeat } from "./timeline";

/**
 * Filtro SVG de separación de colores (rojo a un lado, azul al otro).
 * Se aplica con `filter: url(#rgb-split)` cuando `cantidad` > 0.
 */
export const FiltroRGB: React.FC<{ cantidad: number }> = ({ cantidad }) => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter
      id="rgb-split"
      x="0"
      y="0"
      width="100%"
      height="100%"
      colorInterpolationFilters="sRGB"
    >
      <feColorMatrix
        in="SourceGraphic"
        type="matrix"
        values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"
        result="r"
      />
      <feOffset in="r" dx={cantidad} dy={0} result="r2" />
      <feColorMatrix
        in="SourceGraphic"
        type="matrix"
        values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0"
        result="g"
      />
      <feColorMatrix
        in="SourceGraphic"
        type="matrix"
        values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0"
        result="b"
      />
      <feOffset in="b" dx={-cantidad} dy={cantidad * 0.3} result="b2" />
      <feBlend in="r2" in2="g" mode="screen" result="rg" />
      <feBlend in="rg" in2="b2" mode="screen" />
    </filter>
  </svg>
);

/** Grano de película animado, muy sutil. */
export const Grano: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{ mixBlendMode: "overlay", opacity: 0.12, pointerEvents: "none" }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 360 640"
        preserveAspectRatio="none"
      >
        <filter id="grano">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.9"
            numOctaves={1}
            seed={frame % 12}
          />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="360" height="640" filter="url(#grano)" />
      </svg>
    </AbsoluteFill>
  );
};

/** Destello de luz cálida (light leak) que cruza la imagen. Dura lo que su <Sequence>. */
export const LuzCalida: React.FC<{ semilla: number; fuerza?: number }> = ({
  semilla,
  fuerza = 0.75,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = frame / durationInFrames;
  const vida = Math.sin(Math.PI * t);
  const r = (k: string) => random(`${semilla}-${k}`);
  const x = interpolate(t, [0, 1], [r("x0") * 40 - 20, 60 + r("x1") * 50]);
  const y = 20 + r("y") * 60;
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: "screen",
        opacity: vida * fuerza,
        pointerEvents: "none",
        background: [
          `radial-gradient(ellipse 60% 45% at ${x}% ${y}%, rgba(255,170,60,0.85), rgba(255,120,40,0) 70%)`,
          `radial-gradient(ellipse 40% 60% at ${x + 25}% ${y - 15}%, rgba(255,60,140,0.55), rgba(255,60,140,0) 70%)`,
          `radial-gradient(ellipse 30% 30% at ${x - 10}% ${y + 20}%, rgba(255,230,150,0.6), rgba(255,230,150,0) 70%)`,
        ].join(", "),
      }}
    />
  );
};

/** Marco de cámara: esquinas que se dibujan al inicio y quedan todo el video. */
export const MarcoCamara: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();
  const entrada = Easing.out(Easing.cubic)(
    Math.min(1, Math.max(0, (frame - 10) / 20)),
  );
  const salida = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const m = 48; // margen
  const l = 70 * entrada; // largo de cada esquina
  const c = "rgba(255,255,255,0.75)";
  const esquinas = [
    [m, m, 1, 1],
    [width - m, m, -1, 1],
    [m, height - m, 1, -1],
    [width - m, height - m, -1, -1],
  ];
  return (
    <AbsoluteFill style={{ opacity: salida, pointerEvents: "none" }}>
      <svg width={width} height={height}>
        {esquinas.map(([x, y, dx, dy], i) => (
          <path
            key={i}
            d={`M ${x} ${y + dy * l} L ${x} ${y} L ${x + dx * l} ${y}`}
            stroke={c}
            strokeWidth={4}
            fill="none"
            strokeLinecap="round"
          />
        ))}
        {/* cruz central muy sutil */}
        <g opacity={0.35 * entrada} stroke={c} strokeWidth={2}>
          <line
            x1={width / 2 - 14}
            y1={height / 2}
            x2={width / 2 + 14}
            y2={height / 2}
          />
          <line
            x1={width / 2}
            y1={height / 2 - 14}
            x2={width / 2}
            y2={height / 2 + 14}
          />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

/**
 * Chispas matemáticas: con cada golpe (según la energía de la canción)
 * aparece un símbolo que salta cerca de los bordes, sin tapar el centro.
 */
export const ChispasMatematicas: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const beat = frame / framesPorBeat;
  const chispas: React.ReactNode[] = [];
  for (let b = Math.floor(beat) - 1; b <= Math.floor(beat); b++) {
    if (b < 0) continue;
    const nivel = energiaEn(b);
    // Poca energía: una chispa cada 2 beats. Mucha: una por beat, a veces dos.
    if (nivel < 0.25) continue;
    if (nivel < 0.5 && b % 2 === 1) continue;
    const cuantas = nivel >= 0.9 ? 2 : 1;
    for (let k = 0; k < cuantas; k++) {
      const r = (s: string) => random(`chispa-${b}-${k}-${s}`);
      const local = frame - Math.round(b * framesPorBeat);
      if (local < 0 || local > 16) continue;
      const pop = spring({
        frame: local,
        fps,
        config: { damping: 9, stiffness: 200 },
      });
      const fuera = interpolate(local, [8, 16], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const izquierda = r("lado") < 0.5;
      const x = izquierda ? 14 + r("x") * 12 : 74 + r("x") * 12;
      const y = 14 + r("y") * 66;
      const simbolo = SIMBOLOS[Math.floor(r("s") * SIMBOLOS.length)];
      chispas.push(
        <div
          key={`${b}-${k}`}
          style={{
            position: "absolute",
            left: `${x}%`,
            top: `${y}%`,
            transform: `translate(-50%, -50%) scale(${pop}) rotate(${(r("g") - 0.5) * 40}deg)`,
            opacity: fuera * (0.55 + nivel * 0.4),
            fontFamily: FUENTE,
            fontWeight: 800,
            fontSize: 70 + r("t") * 60,
            color: r("c") < 0.5 ? COLORES.acento : COLORES.acento2,
            textShadow: "0 0 18px rgba(92,225,230,0.7)",
            whiteSpace: "nowrap",
          }}
        >
          {simbolo}
        </div>,
      );
    }
  }
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>{chispas}</AbsoluteFill>
  );
};

/** Número gigante de la cuenta regresiva (3, 2, 1) antes del drop. */
export const NumeroCuenta: React.FC<{ numero: number }> = ({ numero }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 10, stiffness: 240 } });
  const fuera = interpolate(
    frame,
    [durationInFrames - 4, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );
  const sep = Math.max(0, 10 - frame * 1.5);
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        pointerEvents: "none",
      }}
    >
      <svg
        width={560}
        height={560}
        style={{ position: "absolute", opacity: fuera }}
      >
        <circle
          cx={280}
          cy={280}
          r={230}
          fill="none"
          stroke={COLORES.acento}
          strokeWidth={8}
          pathLength={1}
          strokeDasharray="1"
          strokeDashoffset={1 - Math.min(1, frame / durationInFrames)}
          transform="rotate(-90 280 280)"
        />
      </svg>
      <div
        style={{
          fontFamily: FUENTE,
          fontWeight: 900,
          fontSize: 360,
          color: COLORES.texto,
          opacity: fuera,
          transform: `scale(${1.6 - pop * 0.6})`,
          textShadow: `${sep}px 0 rgba(255,0,80,0.85), ${-sep}px 0 rgba(0,220,255,0.85), 0 10px 40px rgba(0,0,0,0.6)`,
        }}
      >
        {numero}
      </div>
    </AbsoluteFill>
  );
};

/** Destello corto y suave (para cada corte de la ráfaga o golpes de beat). */
export const Flash: React.FC<{ fuerza?: number }> = ({ fuerza = 0.4 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const o = interpolate(frame, [0, durationInFrames], [fuerza, 0], {
    extrapolateRight: "clamp",
  });
  return <AbsoluteFill style={{ backgroundColor: "white", opacity: o }} />;
};
