import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { Movimiento } from "./config";
import { COLORES, FUENTE } from "./estilo";
import { TituloAnimado } from "./TituloAnimado";
import { ClipEnTimeline, FPS } from "./timeline";

const SEGMENTOS_RAMPA = 8;

/** Movimiento de cámara virtual: zoom o paneo suave a lo largo del plano. */
const transformacion = (movimiento: Movimiento, progreso: number) => {
  const p = Easing.inOut(Easing.cubic)(progreso);
  switch (movimiento) {
    case "zoom-in":
      return `scale(${interpolate(p, [0, 1], [1.04, 1.16])})`;
    case "zoom-out":
      return `scale(${interpolate(p, [0, 1], [1.16, 1.04])})`;
    case "izquierda":
      return `scale(1.12) translateX(${interpolate(p, [0, 1], [3, -3])}%)`;
    case "derecha":
      return `scale(1.12) translateX(${interpolate(p, [0, 1], [-3, 3])}%)`;
    default:
      return "scale(1.02)";
  }
};

/** Speed ramp: rápido al inicio, frena a cámara lenta. */
const velocidadRampa = (t: number) =>
  interpolate(t, [0, 0.35, 0.6, 1], [2, 2, 0.35, 0.35]);

const Video: React.FC<{ clip: ClipEnTimeline }> = ({ clip }) => {
  const src = staticFile(clip.archivo!);
  const inicio = Math.round(clip.desde * FPS);
  const velocidad = clip.velocidad ?? 1;
  // El sonido real solo se usa a velocidad normal (en cámara lenta suena raro).
  const volumen = !clip.rampa && velocidad === 1 ? (clip.sonidoReal ?? 0) : 0;
  const estilo: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  };

  if (!clip.rampa) {
    return (
      <OffthreadVideo
        src={src}
        trimBefore={inicio}
        playbackRate={velocidad}
        volume={volumen}
        muted={volumen === 0}
        style={estilo}
      />
    );
  }

  const largo = Math.ceil(clip.duracion / SEGMENTOS_RAMPA);
  let fuente = inicio;
  return (
    <>
      {Array.from({ length: SEGMENTOS_RAMPA }, (_, k) => {
        const rate = velocidadRampa(k / (SEGMENTOS_RAMPA - 1));
        const trim = Math.round(fuente);
        fuente += rate * largo;
        return (
          <Sequence
            key={k}
            from={k * largo}
            durationInFrames={largo}
            layout="none"
          >
            <AbsoluteFill>
              <OffthreadVideo
                src={src}
                trimBefore={trim}
                playbackRate={rate}
                muted
                style={estilo}
              />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </>
  );
};

/** Tarjeta de ejemplo cuando todavía no hay clip. */
const Ejemplo: React.FC<{ clip: ClipEnTimeline }> = ({ clip }) => {
  const extras = [
    clip.velocidad && clip.velocidad !== 1
      ? `velocidad ${clip.velocidad}x`
      : null,
    clip.rampa ? "speed ramp" : null,
    clip.sonidoReal
      ? `sonido real ${Math.round(clip.sonidoReal * 100)}%`
      : null,
  ].filter(Boolean);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 30% 30%, ${COLORES.azul}, ${COLORES.fondo} 75%)`,
        // Si el plano lleva texto, la etiqueta baja para no taparlo.
        justifyContent: clip.texto ? "flex-end" : "center",
        paddingBottom: clip.texto ? 130 : 0,
        alignItems: "center",
        fontFamily: FUENTE,
        color: "rgba(255,255,255,0.8)",
      }}
    >
      <AbsoluteFill
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
      />
      <div style={{ textAlign: "center", maxWidth: 1300 }}>
        <div style={{ fontSize: 34, letterSpacing: 8, color: COLORES.acento }}>
          PLANO {clip.indice + 1} · {clip.beats} BEATS
        </div>
        <div
          style={{
            fontSize: clip.texto ? 40 : 58,
            fontWeight: 700,
            marginTop: 16,
          }}
        >
          {clip.nombre}
        </div>
        {extras.length > 0 && (
          <div style={{ fontSize: 30, marginTop: 16, opacity: 0.6 }}>
            {extras.join(" · ")}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const PlanoClip: React.FC<{ clip: ClipEnTimeline }> = ({ clip }) => {
  const frame = useCurrentFrame();
  const progreso = Math.min(1, Math.max(0, frame / clip.duracion));

  // El texto aparece cuando termina la transición de entrada y se va antes de la salida.
  const inicioTexto = clip.transicionEntrada / 2 + 3;
  const finTexto = clip.duracion - clip.transicionSalida / 2;

  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORES.fondo, overflow: "hidden" }}
    >
      <AbsoluteFill
        style={{
          transform: transformacion(clip.movimiento ?? "ninguno", progreso),
          filter: "contrast(1.06) saturate(1.1)",
        }}
      >
        {clip.archivo ? <Video clip={clip} /> : <Ejemplo clip={clip} />}
      </AbsoluteFill>
      {clip.texto && (
        <Sequence from={inicioTexto} durationInFrames={finTexto - inicioTexto}>
          <TituloAnimado texto={clip.texto} subtexto={clip.subtexto} />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
