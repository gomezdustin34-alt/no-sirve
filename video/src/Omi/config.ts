/**
 * ============================================================
 *  AFTERMOVIE OMI — ARCHIVO DE MONTAJE
 * ============================================================
 *  Este es el ÚNICO archivo que necesitas editar para montar el video.
 *  Guía paso a paso: video/GUIA-OMI.md
 *
 *  Rutas: todos los archivos van dentro de la carpeta `video/public/`
 *  y aquí se escriben SIN "public/". Ejemplo:
 *    video/public/omi/clips/llegada-1.mp4  →  "omi/clips/llegada-1.mp4"
 *
 *  Si un clip tiene `archivo: null`, se muestra una tarjeta de ejemplo
 *  con su nombre para que veas el ritmo antes de tener el material.
 * ============================================================
 */

export type Movimiento =
  | "zoom-in" // se acerca suavemente
  | "zoom-out" // se aleja suavemente
  | "izquierda" // paneo lento hacia la izquierda
  | "derecha" // paneo lento hacia la derecha
  | "ninguno";

export type Transicion =
  | "corte" // corte seco, justo en el golpe de la música
  | "fundido" // fundido suave (ideal al inicio y al final)
  | "deslizar" // el siguiente plano entra deslizándose
  | "barrido" // barrido limpio de lado a lado
  | "matematica" // fundido + ráfaga de símbolos π √ ∑ y líneas geométricas
  | "destello"; // corte con un destello blanco breve (momentos fuertes)

export type Efecto = "whoosh" | "impact" | "riser" | "click";

export type Clip = {
  /** Descripción para ti. Solo se ve en las tarjetas de ejemplo. */
  nombre: string;
  /** Ruta dentro de public/, o null mientras no tengas el clip. */
  archivo: string | null;
  /** Segundo del video original donde empieza la parte que quieres usar. */
  desde: number;
  /** Duración en golpes (beats) de la música. A 120 BPM, 1 beat = 0,5 s. */
  beats: number;
  /** 1 = normal, 0.5 = cámara lenta, 0.35 = muy lenta, 1.5 = acelerado. */
  velocidad?: number;
  /** Speed ramp: arranca rápido y frena a cámara lenta dentro del mismo plano. */
  rampa?: boolean;
  movimiento?: Movimiento;
  /** Volumen del sonido real del clip (risas, aplausos…). 0 = silencio, 1 = completo. */
  sonidoReal?: number;
  /** Texto animado sobre este plano. Úsalo poco. */
  texto?: string;
  /** Texto pequeño bajo el principal (opcional). */
  subtexto?: string;
  /** Cómo se pasa de ESTE clip al siguiente. */
  transicion?: Transicion;
  /** Efecto de sonido sutil en el corte hacia el siguiente clip. */
  efecto?: Efecto;
};

/** Música de fondo. Pon tu pista en public/omi/musica/ */
export const MUSICA = {
  /** Ejemplo: "omi/musica/pista.mp3". null = sin música. */
  archivo: null as string | null,
  /** Tempo de la pista. Búscalo con cualquier "BPM tapper" en internet. */
  bpm: 120,
  /** Segundo de la canción donde empieza el video (para saltar intros largas). */
  empiezaEn: 0,
  /** Volumen general de la música (0 a 1). */
  volumen: 0.85,
  /** Baja la música automáticamente cuando un clip tiene sonido real fuerte. */
  bajarConSonidoReal: true,
};

/** Volumen de los efectos (whoosh, impact…). Bajo para que no opaquen. */
export const VOLUMEN_EFECTOS = 0.35;

/** Barras negras de cine arriba y abajo. */
export const BARRAS_CINE = true;

/** Pantalla final. `firma` es opcional: colegio, ciudad o fecha REAL del evento. */
export const CIERRE = {
  texto: "Una experiencia para recordar.",
  firma: null as string | null, // ej.: "OMI 2026 · Nombre del colegio"
  segundos: 4,
};

/**
 * LISTA DE PLANOS, en orden.
 * Los nombres son sugerencias de qué tipo de toma poner en cada lugar.
 * Cambia, borra o agrega clips libremente.
 */
export const CLIPS: Clip[] = [
  // ── INTRO: los mejores planos, música tranquila ─────────────
  {
    nombre: "Plano general del lugar (el más bonito)",
    archivo: null,
    desde: 0,
    beats: 8,
    velocidad: 0.6,
    movimiento: "zoom-in",
    transicion: "matematica",
    efecto: "whoosh",
  },
  {
    nombre: "Mejor toma de estudiantes (cámara lenta)",
    archivo: null,
    desde: 0,
    beats: 8,
    velocidad: 0.5,
    movimiento: "zoom-out",
    texto: "Así se vivió la OMI",
    transicion: "fundido",
  },

  // ── LLEGADA ─────────────────────────────────────────────────
  {
    nombre: "Llegada: estudiantes entrando",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "derecha",
    sonidoReal: 0.3,
    transicion: "deslizar",
    efecto: "whoosh",
  },
  {
    nombre: "Llegada: saludos / registro",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "zoom-in",
    sonidoReal: 0.3,
    transicion: "corte",
  },

  // ── PREPARACIÓN ─────────────────────────────────────────────
  {
    nombre: "Preparación: salón / mesas listas",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "izquierda",
    texto: "Un día de retos",
    transicion: "barrido",
    efecto: "whoosh",
  },
  {
    nombre: "Preparación: detalle (hojas, lápices, calculadora)",
    archivo: null,
    desde: 0,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "corte",
    efecto: "click",
  },

  // ── ESTUDIANTES ─────────────────────────────────────────────
  {
    nombre: "Estudiantes: grupo conversando",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "derecha",
    sonidoReal: 0.4,
    transicion: "corte",
  },
  {
    nombre: "Estudiantes: primer plano, sonrisa",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Estudiantes: otro ángulo",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-out",
    transicion: "matematica",
    efecto: "riser",
  },

  // ── COMPETENCIA: cortes al golpe, una palabra por plano ─────
  {
    nombre: "Competencia: concentración (primer plano)",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-in",
    texto: "Pensar.",
    transicion: "corte",
    efecto: "impact",
  },
  {
    nombre: "Competencia: mano escribiendo",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-in",
    texto: "Resolver.",
    transicion: "corte",
    efecto: "impact",
  },
  {
    nombre: "Competencia: plano general del salón",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-out",
    texto: "Competir.",
    transicion: "destello",
    efecto: "impact",
  },
  {
    nombre: "Competencia: speed ramp (alguien pensando)",
    archivo: null,
    desde: 0,
    beats: 4,
    rampa: true,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Competencia: detalle (reloj, hoja, borrador)",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "izquierda",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Competencia: otro rostro concentrado",
    archivo: null,
    desde: 0,
    beats: 2,
    velocidad: 0.6,
    movimiento: "zoom-in",
    transicion: "matematica",
    efecto: "whoosh",
  },

  // ── MOMENTOS ESPONTÁNEOS ────────────────────────────────────
  {
    nombre: "Espontáneo: risas (con sonido real)",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "zoom-in",
    sonidoReal: 0.9,
    texto: "Más que matemáticas…",
    transicion: "corte",
  },
  {
    nombre: "Espontáneo: bromas / gestos",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "derecha",
    sonidoReal: 0.7,
    transicion: "corte",
  },
  {
    nombre: "Espontáneo: saludo a cámara",
    archivo: null,
    desde: 0,
    beats: 2,
    movimiento: "zoom-out",
    sonidoReal: 0.6,
    transicion: "deslizar",
    efecto: "whoosh",
  },

  // ── INTERACCIÓN ─────────────────────────────────────────────
  {
    nombre: "Interacción: compañeros ayudándose / hablando",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "izquierda",
    sonidoReal: 0.4,
    transicion: "corte",
  },
  {
    nombre: "Interacción: profesores con estudiantes",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "zoom-in",
    transicion: "fundido",
    efecto: "riser",
  },

  // ── MOMENTOS DESTACADOS ─────────────────────────────────────
  {
    nombre: "Destacado: el momento más emocionante (cámara lenta)",
    archivo: null,
    desde: 0,
    beats: 4,
    velocidad: 0.4,
    movimiento: "zoom-in",
    transicion: "destello",
    efecto: "impact",
  },
  {
    nombre: "Destacado: aplausos (con sonido real)",
    archivo: null,
    desde: 0,
    beats: 4,
    movimiento: "zoom-out",
    sonidoReal: 1,
    transicion: "corte",
  },
  {
    nombre: "Destacado: celebración / foto grupal",
    archivo: null,
    desde: 0,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "fundido",
  },

  // ── CIERRE ──────────────────────────────────────────────────
  {
    nombre: "Cierre: último plano (grupo, salida, atardecer…)",
    archivo: null,
    desde: 0,
    beats: 8,
    velocidad: 0.6,
    movimiento: "zoom-out",
    transicion: "fundido",
  },
];
