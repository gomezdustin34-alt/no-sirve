import { CIERRE, CLIPS, Clip, MUSICA, Transicion } from "./config";

export const FPS = 30;

/** Duración (en frames) de cada tipo de transición. Pares, para centrarlas en el golpe. */
export const DURACION_TRANSICION: Record<Transicion, number> = {
  corte: 0,
  destello: 0,
  fundido: 16,
  deslizar: 12,
  barrido: 12,
  matematica: 16,
};

export type ClipEnTimeline = Clip & {
  indice: number;
  /** Frame (en el video final) donde se ve el corte de entrada, alineado al golpe. */
  corteEntrada: number;
  /** Frame donde se ve el corte de salida. */
  corteSalida: number;
  /** Frames que dura la secuencia (incluye la mitad de cada transición). */
  duracion: number;
  transicionEntrada: number;
  transicionSalida: number;
};

const framesPorBeat = (FPS * 60) / MUSICA.bpm;

export const construirTimeline = () => {
  const clips: ClipEnTimeline[] = [];
  let beats = 0;
  let transicionEntrada = 0;

  CLIPS.forEach((clip, indice) => {
    const corteEntrada = Math.round(beats * framesPorBeat);
    beats += clip.beats;
    const corteSalida = Math.round(beats * framesPorBeat);
    const transicionSalida = DURACION_TRANSICION[clip.transicion ?? "corte"];
    clips.push({
      ...clip,
      indice,
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
