import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  random,
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
import {
  ChispasMatematicas,
  FiltroRGB,
  Flash,
  Grano,
  LuzCalida,
  MarcoCamara,
  NumeroCuenta,
} from "./Efectos";
import { PlanoClip } from "./PlanoClip";
import {
  energiaEn,
  entradasFoto,
  FPS,
  framesPorBeat,
  TIMELINE,
} from "./timeline";
import { latigazo, zoomTraves } from "./Transiciones";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const presentacion = (tipo: Transicion): TransitionPresentation<any> => {
  switch (tipo) {
    case "deslizar":
      return slide({ direction: "from-right" });
    case "barrido":
      return wipe({ direction: "from-left" });
    case "zoom":
      return zoomTraves();
    case "latigazo":
      return latigazo();
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
  glitch: { antes: 0, duracion: 12 },
  tick: { antes: 0, duracion: 4 },
  subdrop: { antes: 0, duracion: 60 },
  obturador: { antes: 0, duracion: 10 },
};

/** Frames donde cae cada foto (todas las polaroids del video). */
const CAIDAS_FOTO: number[] = TIMELINE.clips.flatMap((c) => entradasFoto(c));

type Golpe = { frame: number; fuerza: number; duracion: number };

/** Momentos donde la cámara tiembla y los colores se separan. */
const GOLPES: Golpe[] = (() => {
  const g: Golpe[] = [];
  for (const c of TIMELINE.clips) {
    if (c.drop) g.push({ frame: c.corteEntrada, fuerza: 1.3, duracion: 14 });
    if (c.efecto === "impact")
      g.push({ frame: c.corteSalida, fuerza: 1, duracion: 10 });
    if (c.transicion === "glitch")
      g.push({ frame: c.corteSalida, fuerza: 0.9, duracion: 8 });
    if (c.rafaga) g.push({ frame: c.corteEntrada, fuerza: 0.45, duracion: 4 });
  }
  for (const f of CAIDAS_FOTO)
    g.push({ frame: f + 4, fuerza: 0.35, duracion: 6 });
  return g;
})();

/** Sonidos automáticos: golpe grave en el drop, glitch y tics de la ráfaga. */
const SONIDOS_AUTO: { frame: number; efecto: Efecto; volumen: number }[] =
  (() => {
    const s: { frame: number; efecto: Efecto; volumen: number }[] = [];
    for (const c of TIMELINE.clips) {
      if (c.drop)
        s.push({ frame: c.corteEntrada, efecto: "subdrop", volumen: 0.6 });
      if (c.transicion === "glitch")
        s.push({ frame: c.corteSalida, efecto: "glitch", volumen: 0.3 });
      if (c.rafaga)
        s.push({ frame: c.corteEntrada, efecto: "tick", volumen: 0.25 });
    }
    for (const f of CAIDAS_FOTO)
      s.push({ frame: f, efecto: "obturador", volumen: 0.45 });
    return s;
  })();

/** Frames donde entra cada número de la cuenta regresiva (3, 2, 1). */
const CUENTA: { frame: number; numero: number }[] = (() => {
  const drop = TIMELINE.clips.find((c) => c.drop);
  if (!drop) return [];
  return [3, 2, 1].map((n) => ({
    numero: n,
    frame: Math.round((drop.beatEntrada - n) * framesPorBeat),
  }));
})();

/**
 * Cámara viva: pulso al ritmo (según la energía de la canción),
 * temblor y separación de colores en los golpes.
 */
const CamaraViva: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const beat = frame / framesPorBeat;
  const fase = beat - Math.floor(beat);
  const pulso = 1 + 0.045 * energiaEn(beat) * Math.exp(-fase * 7);

  let temblor = 0;
  for (const g of GOLPES) {
    const t = frame - g.frame;
    if (t >= 0 && t < g.duracion)
      temblor = Math.max(temblor, g.fuerza * (1 - t / g.duracion));
  }
  const dx = (random(`tx${frame}`) - 0.5) * 36 * temblor;
  const dy = (random(`ty${frame}`) - 0.5) * 36 * temblor;
  const giro = (random(`tr${frame}`) - 0.5) * 1.6 * temblor;
  const rgb = Math.round(temblor * 16);

  return (
    <AbsoluteFill>
      <FiltroRGB cantidad={rgb} />
      <AbsoluteFill
        style={{
          transform: `translate(${dx}px, ${dy}px) rotate(${giro}deg) scale(${pulso + temblor * 0.04})`,
          filter: rgb > 0 ? "url(#rgb-split)" : undefined,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
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
          padding: "0 80px",
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

/** Volumen de la música: entra suave, baja con el sonido real y se desvanece al final. */
const volumenMusica = (frame: number) => {
  const { clips, total } = TIMELINE;
  // La canción ya crece sola: solo evitamos que arranque de golpe.
  const subida = interpolate(frame, [0, 8], [0, 1], {
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
      <CamaraViva>
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
      </CamaraViva>

      {/* ── Luz cálida: al inicio, en transiciones suaves y al final ── */}
      <Sequence durationInFrames={60}>
        <LuzCalida semilla={0} fuerza={0.9} />
      </Sequence>
      {clips.map((clip) =>
        ["fundido", "zoom", "matematica"].includes(clip.transicion ?? "") ? (
          <Sequence
            key={`l${clip.indice}`}
            from={clip.corteSalida - 20}
            durationInFrames={40}
          >
            <LuzCalida semilla={clip.indice + 1} />
          </Sequence>
        ) : null,
      )}
      <Sequence from={cierre.corteEntrada - 10} durationInFrames={80}>
        <LuzCalida semilla={99} fuerza={0.6} />
      </Sequence>

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
        if (clip.fotos) {
          return entradasFoto(clip).map((f) => (
            <Sequence
              key={`fo${clip.indice}-${f}`}
              from={f}
              durationInFrames={3}
            >
              <Flash fuerza={0.5} />
            </Sequence>
          ));
        }
        if (clip.rafaga) {
          return (
            <Sequence
              key={`f${clip.indice}`}
              from={clip.corteEntrada}
              durationInFrames={3}
            >
              <Flash fuerza={0.35} />
            </Sequence>
          );
        }
        return null;
      })}

      {/* Chispas matemáticas al ritmo */}
      <Sequence durationInFrames={cierre.corteEntrada}>
        <ChispasMatematicas />
      </Sequence>

      {/* Cuenta regresiva antes del drop */}
      {CUENTA.map((c, i) => (
        <Sequence
          key={`c${c.numero}`}
          from={c.frame}
          durationInFrames={
            (CUENTA[i + 1]?.frame ?? c.frame + framesPorBeat) - c.frame
          }
        >
          <NumeroCuenta numero={c.numero} />
        </Sequence>
      ))}

      {/* Viñeta, grano y marco de cámara */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      <Grano />
      <Sequence durationInFrames={cierre.corteEntrada + 10}>
        <MarcoCamara />
      </Sequence>
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
      {SONIDOS_AUTO.map((s, i) => (
        <Sequence
          key={`a${i}`}
          from={s.frame}
          durationInFrames={EFECTOS[s.efecto].duracion}
        >
          <Audio src={staticFile(`sfx/${s.efecto}.wav`)} volume={s.volumen} />
        </Sequence>
      ))}
      {CUENTA.map((c) => (
        <Sequence key={`cs${c.numero}`} from={c.frame} durationInFrames={6}>
          <Audio src={staticFile("sfx/click.wav")} volume={0.5} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
