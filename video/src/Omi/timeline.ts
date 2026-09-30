import { CIERRE, CLIPS, Clip, ENERGIA, MUSICA, Transicion } from "./config";

export const FPS = 30;

/** Duración (en frames) de cada tipo de transición. Pares, para centrarlas en el golpe. */
export const DURACION_TRANSICION: Record<Transicion, number> = {
  corte: 0,
  destello: 0,
  fundido: 16,
  deslizar: 12,
  barrido: 12,
  matematica: 16,
  zoom: 10,
  latigazo: 8,
  glitch: 0,
};

export type ClipEnTimeline = Clip & {
  indice: number;
  /** Beat de la canción donde empieza el plano. */
  beatEntrada: number;
  /** Frame (en el video final) donde se ve el corte de entrada, alineado al golpe. */
  corteEntrada: number;
  /** Frame donde se ve el corte de salida. */
  corteSalida: number;
  /** Frames que dura la secuencia (incluye la mitad de cada transición). */
  duracion: number;
  transicionEntrada: number;
  transicionSalida: number;
};

export const framesPorBeat = (FPS * 60) / MUSICA.bpm;

/** Nivel de energía (0 a 1) en un beat dado, según ENERGIA en config.ts. */
export const energiaEn = (beat: number) => {
  let nivel = 0;
  for (const [desde, n] of ENERGIA) if (beat >= desde) nivel = n;
  return nivel;
};

export const construirTimeline = () => {
  const clips: ClipEnTimeline[] = [];
  let beats = 0;
  let transicionEntrada = 0;

  CLIPS.forEach((clip, indice) => {
    const corteEntrada = Math.round(beats * framesPorBeat);
    const beatEntrada = beats;
    beats += clip.beats;
    const corteSalida = Math.round(beats * framesPorBeat);
    const transicionSalida = DURACION_TRANSICION[clip.transicion ?? "corte"];
    clips.push({
      ...clip,
      indice,
      beatEntrada,
      corteEntrada,
      corteSalida,
      transicionEntrada,
      transicionSalida,
      duracion:
        corteSalida -
        corteEntrada +
        transicionEntrada / 2 +
        transicionSalida / 2,
    });
    transicionEntrada = transicionSalida;
  });

  const inicioCierre = clips.length ? clips[clips.length - 1].corteSalida : 0;
  const framesCierre = Math.round(CIERRE.segundos * FPS);
  const cierre = {
    corteEntrada: inicioCierre,
    transicionEntrada,
    duracion: framesCierre + transicionEntrada / 2,
  };

  return { clips, cierre, total: inicioCierre + framesCierre };
};

export const TIMELINE = construirTimeline();
