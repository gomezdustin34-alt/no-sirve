import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  linearTiming,
  TransitionPresentation,
  TransitionSeries,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import {
  BARRAS_CINE,
  CIERRE,
  Efecto,
  MUSICA,
  Transicion,
  VOLUMEN_EFECTOS,
} from "./config";
import { COLORES, FUENTE } from "./estilo";
import { Destello, FondoGeometrico, RafagaMatematica } from "./Matematicas";
import { PlanoClip } from "./PlanoClip";
import { FPS, TIMELINE } from "./timeline";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const presentacion = (tipo: Transicion): TransitionPresentation<any> => {
  switch (tipo) {
    case "deslizar":
      return slide({ direction: "from-right" });
    case "barrido":
      return wipe({ direction: "from-left" });
    default:
      return fade();
  }
};

/** Duración de cada efecto y cuántos frames antes del corte empieza. */
const EFECTOS: Record<Efecto, { antes: number; duracion: number }> = {
  whoosh: { antes: 9, duracion: 24 },
  impact: { antes: 0, duracion: 30 },
  riser: { antes: 72, duracion: 75 },
  click: { antes: 0, duracion: 6 },
};

const Cierre: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const entrada = spring({ frame: frame - 6, fps, config: { damping: 20 } });
  const firma = spring({ frame: frame - 30, fps, config: { damping: 20 } });
  const salida = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );
  return (
    <AbsoluteFill style={{ opacity: salida }}>
      <FondoGeometrico />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          fontFamily: FUENTE,
          color: COLORES.texto,
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: 92,
            fontWeight: 800,
            opacity: entrada,
            filter: `blur(${(1 - entrada) * 10}px)`,
            transform: `scale(${0.94 + entrada * 0.06})`,
          }}
        >
          {CIERRE.texto}
        </div>
        {CIERRE.firma && (
          <div
            style={{
              marginTop: 30,
              fontSize: 34,
              letterSpacing: 8,
              color: COLORES.acento,
              opacity: firma,
            }}
          >
            {CIERRE.firma}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Volumen de la música: sube poco a poco, baja con el sonido real y se desvanece al final. */
const volumenMusica = (frame: number) => {
  const { clips, total } = TIMELINE;
  const subida = interpolate(frame, [0, 45, total * 0.35], [0, 0.7, 1], {
    extrapolateRight: "clamp",
  });
  const final = interpolate(frame, [total - 45, total], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  let agache = 1;
  if (MUSICA.bajarConSonidoReal) {
    for (const c of clips) {
      if ((c.sonidoReal ?? 0) >= 0.5 && !c.rampa && (c.velocidad ?? 1) === 1) {
        const v = interpolate(
          frame,
          [
            c.corteEntrada - 8,
            c.corteEntrada + 4,
            c.corteSalida - 4,
            c.corteSalida + 8,
          ],
          [1, 0.4, 0.4, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );
        agache = Math.min(agache, v);
      }
    }
  }
  return MUSICA.volumen * subida * final * agache;
};

export const Aftermovie: React.FC = () => {
  const { clips, cierre } = TIMELINE;

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* ── Imagen ─────────────────────────────────────────── */}
      <TransitionSeries>
        {clips.map((clip) => (
          <React.Fragment key={clip.indice}>
            <TransitionSeries.Sequence
              durationInFrames={clip.duracion}
              premountFor={30}
            >
              <PlanoClip clip={clip} />
            </TransitionSeries.Sequence>
            {clip.transicionSalida > 0 && (
              <TransitionSeries.Transition
                presentation={presentacion(clip.transicion ?? "corte")}
                timing={linearTiming({
                  durationInFrames: clip.transicionSalida,
                })}
              />
            )}
          </React.Fragment>
        ))}
        <TransitionSeries.Sequence durationInFrames={cierre.duracion}>
          <Cierre />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {/* ── Gráficos sobre los cortes ─────────────────────── */}
      {clips.map((clip) => {
        if (clip.transicion === "matematica") {
          return (
            <Sequence
              key={`m${clip.indice}`}
              from={clip.corteSalida - 18}
              durationInFrames={36}
            >
              <RafagaMatematica semilla={clip.indice} />
            </Sequence>
          );
        }
        if (clip.transicion === "destello") {
          return (
            <Sequence
              key={`d${clip.indice}`}
              from={clip.corteSalida}
              durationInFrames={10}
            >
              <Destello />
            </Sequence>
          );
        }
        return null;
      })}

      {/* Viñeta cinematográfica */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      {BARRAS_CINE && (
        <AbsoluteFill style={{ justifyContent: "space-between" }}>
          <div style={{ height: 100, backgroundColor: "black" }} />
          <div style={{ height: 100, backgroundColor: "black" }} />
        </AbsoluteFill>
      )}

      {/* ── Sonido ─────────────────────────────────────────── */}
      {MUSICA.archivo && (
        <Audio
          src={staticFile(MUSICA.archivo)}
          trimBefore={Math.round(MUSICA.empiezaEn * FPS)}
          volume={volumenMusica}
        />
      )}
      {clips.map((clip) => {
        if (!clip.efecto) return null;
        const e = EFECTOS[clip.efecto];
        const desde = Math.max(0, clip.corteSalida - e.antes);
        return (
          <Sequence
            key={`s${clip.indice}`}
            from={desde}
            durationInFrames={e.duracion}
          >
            <Audio
              src={staticFile(`sfx/${clip.efecto}.wav`)}
              volume={VOLUMEN_EFECTOS}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
