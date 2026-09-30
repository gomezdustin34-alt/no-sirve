import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  random,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORES, FUENTE, SIMBOLOS } from "./estilo";

/**
 * Ráfaga breve de símbolos matemáticos y figuras geométricas,
 * centrada en un corte. Dura lo que dure su <Sequence>.
 */
export const RafagaMatematica: React.FC<{ semilla: number }> = ({
  semilla,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const t = frame / durationInFrames;
  const vida = Math.sin(Math.PI * t); // 0 → 1 → 0

  const simbolos = Array.from({ length: 9 }, (_, i) => {
    const r = (k: string) => random(`${semilla}-${i}-${k}`);
    return {
      texto: SIMBOLOS[Math.floor(r("s") * SIMBOLOS.length)],
      x: 8 + r("x") * 84,
      y: 12 + r("y") * 76,
      tam: 40 + r("t") * 70,
      giro: (r("g") - 0.5) * 30,
      retraso: r("d") * 0.3,
      deriva: (r("v") - 0.5) * 60,
    };
  });

  const barrido = Easing.inOut(Easing.cubic)(t);
  const radio = 120 + random(`${semilla}-r`) * 120;
  const cx = width * (0.3 + random(`${semilla}-cx`) * 0.4);
  const cy = height * (0.35 + random(`${semilla}-cy`) * 0.3);

  return (
    <AbsoluteFill style={{ pointerEvents: "none", fontFamily: FUENTE }}>
      <svg width={width} height={height} style={{ position: "absolute" }}>
        {/* línea que cruza la pantalla */}
        <line
          x1={interpolate(barrido, [0, 1], [-200, width])}
          y1={height * 0.62}
          x2={interpolate(barrido, [0, 1], [0, width + 200])}
          y2={height * 0.38}
          stroke={COLORES.acento2}
          strokeWidth={3}
          opacity={vida * 0.8}
        />
        {/* círculo con triángulo inscrito que se dibujan */}
        <g opacity={vida * 0.7} fill="none" strokeWidth={2.5}>
          <circle
            cx={cx}
            cy={cy}
            r={radio}
            stroke={COLORES.texto}
            pathLength={1}
            strokeDasharray="1"
            strokeDashoffset={1 - Math.min(1, t * 1.6)}
            transform={`rotate(${t * 90 - 90} ${cx} ${cy})`}
          />
          <polygon
            points={[0, 1, 2]
              .map((k) => {
                const a = (k * 2 * Math.PI) / 3 - Math.PI / 2 + t * 0.8;
                return `${cx + radio * Math.cos(a)},${cy + radio * Math.sin(a)}`;
              })
              .join(" ")}
            stroke={COLORES.acento}
            pathLength={1}
            strokeDasharray="1"
            strokeDashoffset={1 - Math.min(1, Math.max(0, t * 1.6 - 0.2))}
          />
        </g>
      </svg>
      {simbolos.map((s, i) => {
        const local = Math.min(1, Math.max(0, (t - s.retraso) / 0.7));
        const o = Math.sin(Math.PI * local);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${s.x}%`,
              top: `${s.y}%`,
              fontSize: s.tam,
              fontWeight: 600,
              color: i % 3 === 0 ? COLORES.acento : COLORES.texto,
              opacity: o * 0.85,
              transform: `translate(-50%, ${-local * s.deriva}px) rotate(${s.giro}deg) scale(${0.7 + local * 0.4})`,
              filter: `blur(${(1 - o) * 6}px)`,
              whiteSpace: "nowrap",
              textShadow: "0 0 24px rgba(92,225,230,0.5)",
            }}
          >
            {s.texto}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Destello blanco breve para cortes fuertes. */
export const Destello: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const opacidad = interpolate(frame, [0, 1, durationInFrames], [0, 0.85, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "white", opacity: opacidad }} />
  );
};

/** Fondo de cuadrícula y figuras en movimiento lento (para la pantalla final). */
export const FondoGeometrico: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const cx = width / 2;
  const cy = height / 2;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 45%, ${COLORES.azul} 0%, ${COLORES.fondo} 70%)`,
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          transform: `translateY(${(frame * 0.4) % 60}px)`,
        }}
      />
      <svg width={width} height={height} style={{ position: "absolute" }}>
        <g fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={2}>
          <circle cx={cx} cy={cy} r={330} />
          <circle
            cx={cx}
            cy={cy}
            r={420}
            strokeDasharray="4 14"
            transform={`rotate(${frame * 0.3} ${cx} ${cy})`}
          />
          <polygon
            transform={`rotate(${frame * -0.25} ${cx} ${cy})`}
            points={[0, 1, 2, 3, 4, 5]
              .map((k) => {
                const a = (k * Math.PI) / 3;
                return `${cx + 380 * Math.cos(a)},${cy + 380 * Math.sin(a)}`;
              })
              .join(" ")}
          />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
