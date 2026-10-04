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
  | "destello" // corte con un destello blanco breve (momentos fuertes)
  | "zoom" // zoom a través del plano, con desenfoque
  | "latigazo" // paneo rápido tipo latigazo, con desenfoque de movimiento
  | "glitch"; // corte con separación de colores y temblor digital

export type Efecto =
  | "whoosh"
  | "impact"
  | "riser"
  | "click"
  | "glitch"
  | "tick"
  | "subdrop"
  | "obturador";

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
  /**
   * Etiqueta pequeña abajo, tipo rótulo de TV. Úsala para nombres REALES
   * que aparecen en el material (estaciones, carteles…).
   */
  etiqueta?: string;
  /**
   * Marca el plano que cae en el drop de la canción: antes sale una
   * cuenta regresiva 3·2·1 y en el corte suena un golpe grave.
   */
  drop?: boolean;
  /** Plano de la ráfaga rápida: destello y glitch pequeños en cada corte. */
  rafaga?: boolean;
  /**
   * Fotos (en vez de video): caen como polaroids, una por beat, y se
   * apilan. Con `fotos`, `archivo` va en null y `desde` no se usa.
   */
  fotos?: string[];
  /** Pie escrito en cada polaroid (mismo orden que `fotos`). */
  pies?: string[];
};

/** Tus fotos (en public/omi/fotos/). */
export const F01 = "omi/fotos/f01-tiendita-dona-mati.jpg";
export const F02 = "omi/fotos/f02-profes-math-superpower.jpg";
export const F03 = "omi/fotos/f03-mesa-omi-circuito-juegos.jpg";
export const F04 = "omi/fotos/f04-museo-matematico.jpg";
export const F05 = "omi/fotos/f05-profes-grados-4-5.jpg";
export const F06 = "omi/fotos/f06-escenario-dia-creatividad.jpg";
export const F07 = "omi/fotos/f07-estacion-bingo.jpg";
export const F08 = "omi/fotos/f08-tiendita-explicando.jpg";
export const F09 = "omi/fotos/f09-premiados-con-medallas.jpg";
export const F10 = "omi/fotos/f10-entrega-diplomas.jpg";

/** Fotos tomadas en vertical (para darles la forma correcta de polaroid). */
export const FOTOS_VERTICALES = [F05, F06];

/**
 * Energía visual por tramo de la canción (en beats): controla el pulso de
 * cámara al ritmo y las chispas matemáticas. 0 = quieto, 1 = a tope.
 */
export const ENERGIA: [desdeBeat: number, nivel: number][] = [
  [0, 0],
  [28, 0.3],
  [64, 0.55],
  [80, 1],
  [100, 0.35],
  [108, 0],
];

/** Música de fondo. Pon tu pista en public/omi/musica/ */
export const MUSICA = {
  /**
   * Ejemplo: "omi/musica/pista.mp3". null = sin música.
   * "musica/omi-provisional.wav" es una pista provisional generada por
   * scripts/generar-musica.mjs (120 BPM), por si no tienes canción.
   */
  archivo: "omi/musica/cancion.wav" as string | null,
  /** Tempo de la pista. Búscalo con cualquier "BPM tapper" en internet. */
  bpm: 118,
  /** Segundo de la canción donde empieza el video (para saltar intros largas). */
  empiezaEn: 0,
  /** Volumen general de la música (0 a 1). */
  volumen: 0.85,
  /** Baja la música automáticamente cuando un clip tiene sonido real fuerte. */
  bajarConSonidoReal: true,
};

/** Volumen de los efectos (whoosh, impact…). Bajo para que no opaquen. */
export const VOLUMEN_EFECTOS = 0.35;

/**
 * Formato del video. Vertical = 1080×1920 (Reels, TikTok, Shorts, Estados).
 * Pon `false` para horizontal 1920×1080 (YouTube, proyector).
 */
export const VERTICAL = true;

/**
 * Barras negras de cine arriba y abajo. En vertical quedan raras y tapan
 * espacio de la pantalla, por eso vienen apagadas.
 */
export const BARRAS_CINE = false;

/** Pantalla final. `firma` es opcional: colegio, ciudad o fecha REAL del evento. */
export const CIERRE = {
  texto: "Una experiencia para recordar.",
  // Datos tomados de los letreros del evento (videos 16 y 17).
  firma: "OLIMPIADAS MATEMÁTICAS · INETFRADPAS 2026" as string | null,
  // 8 beats a 118 BPM: termina justo cuando se apaga la canción.
  segundos: 4.07,
};

/** Tus 17 videos (en public/omi/clips/). */
const V1 = "omi/clips/v1-cuchara-ruleta-palitos.mp4";
const V2 = "omi/clips/v2-cancha-tarjetas-pensando.mp4";
const V3 = "omi/clips/v3-profesor-mesa-tarjetas.mp4";
const V4 = "omi/clips/v4-mesa-tarjetas.mp4";
const V5 = "omi/clips/v5-conos-tangram.mp4";
const V6 = "omi/clips/v6-museo-corto.mp4";
const V7 = "omi/clips/v7-expo-naturaleza.mp4";
const V8 = "omi/clips/v8-expo-piano.mp4";
const V9 = "omi/clips/v9-expo-geometria.mp4";
const V10 = "omi/clips/v10-expo-robots.mp4";
const V11 = "omi/clips/v11-expo-origen-numeros.mp4";
const V12 = "omi/clips/v12-mesa-diagramas.mp4";
const V13 = "omi/clips/v13-expo-frecuencia.mp4";
const V14 = "omi/clips/v14-tablero-numeros.mp4";
const V15 = "omi/clips/v15-caza-de-datos-120fps.mp4";
const V16 = "omi/clips/v16-llegada-bienvenidos-auditorio.mp4";
const V17 = "omi/clips/v17-mesa-premios-120fps.mp4";

/**
 * LISTA DE PLANOS, en orden.
 * Montaje con las mejores tomas de tus 17 videos (todos aparecen),
 * armado sobre la estructura de la canción (118 BPM):
 *   beats   0–28  intro tranquila      → llegada
 *   beats  28–64  entra el bajo        → retos y exposiciones
 *   beats  64–80  sube la tensión      → compañerismo, concentración, 3·2·1
 *   beat   80     ¡DROP!              → Pensar. Resolver. Competir.
 *   beats  86–94  parte más fuerte     → RÁFAGA con los 17 videos
 *   beats  94–108                      → reconocimientos y cierre
 * Las etiquetas usan nombres REALES que aparecen en los carteles.
 */
const r = (
  archivo: string,
  desde: number,
  beats: number,
  movimiento: Movimiento,
  nombre: string,
): Clip => ({ nombre, archivo, desde, beats, movimiento, rafaga: true });

export const CLIPS: Clip[] = [
  // ── INTRO (beats 0–16) ──────────────────────────────────────
  {
    nombre: "Pasacalle OMΦ entre los árboles",
    archivo: V16,
    desde: 0.5,
    beats: 8,
    velocidad: 0.6,
    movimiento: "zoom-in",
    etiqueta: "Olimpiadas Matemáticas · 2026",
    transicion: "matematica",
    efecto: "whoosh",
  },
  {
    nombre: "Niño pensando, mano en la barbilla, carnet OMI",
    archivo: V2,
    desde: 31,
    beats: 8,
    velocidad: 0.5,
    movimiento: "zoom-out",
    // \u00a0 (espacio que no se parte) mantiene "la OMI" junta.
    texto: "Así se vivió la\u00a0OMI",
    transicion: "zoom",
    efecto: "whoosh",
  },

  // ── LLEGADA (beats 16–28) ───────────────────────────────────
  {
    nombre: "Letrero Olimpiadas Matemáticas en la entrada",
    archivo: V16,
    desde: 9,
    beats: 4,
    movimiento: "zoom-out",
    texto: "Llegó el día",
    transicion: "latigazo",
    efecto: "whoosh",
  },
  {
    nombre: "BIENVENIDOS con globos",
    archivo: V16,
    desde: 23,
    beats: 4,
    movimiento: "ninguno",
    transicion: "latigazo",
    efecto: "whoosh",
  },
  {
    nombre: "Foto: profes de la OMI, grados 4° y 5°",
    archivo: null,
    desde: 0,
    beats: 4,
    fotos: [F05],
    pies: ["Grados 4° y 5°"],
    transicion: "glitch",
  },

  // ── LOS RETOS (beats 28–44): entra el bajo ──────────────────
  {
    nombre: "Mesa 'Pensamiento Variacional' con tarjetas",
    archivo: V1,
    desde: 33,
    beats: 4,
    movimiento: "zoom-in",
    texto: "Un día de retos",
    etiqueta: "Pensamiento Variacional",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Detalle: la ruleta de colores",
    archivo: V1,
    desde: 17,
    beats: 2,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Manos armando el reto de los palitos",
    archivo: V1,
    desde: 44,
    beats: 2,
    movimiento: "zoom-in",
    etiqueta: "Reto de los palitos",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Poniendo los números en el tablero",
    archivo: V14,
    desde: 3.5,
    beats: 2,
    movimiento: "zoom-in",
    transicion: "latigazo",
    efecto: "whoosh",
  },
  {
    nombre: "Estudiantes en la mesa de diagramas",
    archivo: V12,
    desde: 3,
    beats: 2,
    movimiento: "izquierda",
    sonidoReal: 0.3,
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Frente a la ruleta, rascándose la cabeza",
    archivo: V5,
    desde: 16.5,
    beats: 4,
    movimiento: "izquierda",
    sonidoReal: 0.3,
    texto: "¿Y ahora?",
    transicion: "matematica",
    efecto: "whoosh",
  },

  // ── MÁS QUE MATEMÁTICAS (beats 44–60): exposiciones ─────────
  {
    nombre: "Foto: Museo Matemático",
    archivo: null,
    desde: 0,
    beats: 2,
    fotos: [F04],
    pies: ["Museo Matemático"],
    transicion: "corte",
  },
  {
    nombre: "Exposición con teclado (explicando)",
    archivo: V8,
    desde: 0.5,
    beats: 4,
    movimiento: "zoom-in",
    sonidoReal: 0.5,
    texto: "Más que matemáticas…",
    etiqueta: "¿Por qué la naturaleza usa las matemáticas?",
    transicion: "corte",
  },
  {
    nombre: "Exposición de los carritos robot",
    archivo: V10,
    desde: 2,
    beats: 2,
    movimiento: "zoom-in",
    sonidoReal: 0.4,
    etiqueta: "Galería de Genios",
    transicion: "corte",
  },
  {
    nombre: "Exposición 'Origen de los números'",
    archivo: V11,
    desde: 3,
    beats: 2,
    movimiento: "derecha",
    sonidoReal: 0.4,
    etiqueta: "Origen de los números",
    transicion: "latigazo",
    efecto: "whoosh",
  },
  {
    nombre: "Dos expositoras explicando",
    archivo: V7,
    desde: 2,
    beats: 2,
    movimiento: "zoom-out",
    sonidoReal: 0.5,
    texto: "Creatividad",
    transicion: "corte",
  },
  {
    nombre: "Exposición 'Geometría en nuestra cultura'",
    archivo: V9,
    desde: 3,
    beats: 2,
    movimiento: "izquierda",
    sonidoReal: 0.4,
    etiqueta: "Geometría en nuestra cultura",
    transicion: "corte",
  },
  {
    nombre: "Profesora en la estación de frecuencias",
    archivo: V13,
    desde: 5,
    beats: 2,
    movimiento: "zoom-in",
    transicion: "zoom",
    efecto: "whoosh",
  },

  // ── COMPAÑERISMO Y TENSIÓN (beats 60–80) ────────────────────
  {
    nombre: "Profesora sonriendo con un estudiante (120 fps)",
    archivo: V15,
    desde: 15,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-in",
    texto: "Trabajo en equipo",
    etiqueta: "La caza de los datos",
    transicion: "corte",
  },
  {
    nombre: "Compañeros mirando cómo resuelve el tangram",
    archivo: V5,
    desde: 45,
    beats: 4,
    movimiento: "zoom-in",
    transicion: "glitch",
  },
  {
    nombre: "Speed ramp: primer plano concentrado con las tarjetas",
    archivo: V3,
    desde: 30,
    beats: 4,
    rampa: true,
    movimiento: "zoom-in",
    texto: "Concentración total",
    transicion: "corte",
  },
  {
    nombre: "Manos en el juego 'La caza de los datos' (120 fps)",
    archivo: V15,
    desde: 22,
    beats: 2,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Niño leyendo su tarjeta",
    archivo: V4,
    desde: 10,
    beats: 2,
    movimiento: "zoom-out",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Primer plano mirando su tarjeta (empieza el 3·2·1)",
    archivo: V1,
    desde: 38,
    beats: 2,
    velocidad: 0.6,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Tangram casi listo (lento) → sube al drop",
    archivo: V5,
    desde: 64,
    beats: 2,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "destello",
    efecto: "riser",
  },

  // ── ¡DROP! (beat 80): una palabra por golpe ─────────────────
  {
    nombre: "Chica concentrada leyendo la tarjeta",
    archivo: V2,
    desde: 22,
    beats: 2,
    movimiento: "zoom-in",
    texto: "Pensar.",
    drop: true,
    transicion: "corte",
    efecto: "impact",
  },
  {
    nombre: "Manos resolviendo el tangram",
    archivo: V5,
    desde: 56,
    beats: 2,
    movimiento: "zoom-in",
    texto: "Resolver.",
    transicion: "corte",
    efecto: "impact",
  },
  {
    nombre: "Carrera con la cuchara en la boca, hacia la cámara",
    archivo: V1,
    desde: 12.5,
    beats: 2,
    movimiento: "zoom-in",
    texto: "Competir.",
    transicion: "destello",
    efecto: "impact",
  },

  // ── RÁFAGA (beats 86–94): un pedacito de cada uno de los 17 videos,
  //    cada vez más rápido (medio beat y al final un cuarto de beat) ──
  r(V16, 25, 0.5, "zoom-in", "Ráfaga: BIENVENIDOS"),
  r(V1, 11, 0.5, "zoom-out", "Ráfaga: cuchara"),
  r(V5, 5, 0.5, "zoom-in", "Ráfaga: carrera entre conos"),
  r(V2, 3.8, 0.5, "zoom-out", "Ráfaga: tiro al blanco"),
  r(V13, 5.5, 0.5, "zoom-in", "Ráfaga: estación de frecuencias"),
  r(V14, 5, 0.5, "zoom-out", "Ráfaga: tablero de números"),
  r(V12, 4, 0.5, "zoom-in", "Ráfaga: diagramas"),
  r(V3, 13.5, 0.5, "zoom-out", "Ráfaga: profesor mira a cámara"),
  r(V4, 12, 0.5, "zoom-in", "Ráfaga: leyendo tarjeta"),
  r(V15, 16.5, 0.5, "zoom-out", "Ráfaga: profesora sonriendo"),
  r(V6, 2, 0.5, "zoom-in", "Ráfaga: museo"),
  r(V7, 3, 0.5, "zoom-out", "Ráfaga: expositoras"),
  r(V8, 12, 0.5, "zoom-in", "Ráfaga: explicando en el teclado"),
  r(V9, 5, 0.5, "zoom-out", "Ráfaga: geometría"),
  r(V10, 3, 0.5, "zoom-in", "Ráfaga: robots"),
  r(V11, 8.5, 0.25, "zoom-out", "Ráfaga: origen de los números"),
  {
    ...r(V17, 22, 0.25, "zoom-in", "Ráfaga: letras OMΦ"),
    transicion: "destello",
    efecto: "whoosh",
  },

  // ── ÁLBUM DE FOTOS (beats 94–100): una polaroid por beat ───
  {
    nombre: "Álbum: fotos que caen y se apilan",
    archivo: null,
    desde: 0,
    beats: 6,
    fotos: [F01, F08, F03, F07, F06],
    pies: [
      "La tiendita de Doña Mati",
      "¡Pienso, calculo y compro!",
      "Circuito de juegos",
      "Estación Bingo Matemático",
      "Día de la Creatividad 2026",
    ],
    transicion: "corte",
  },

  // ── RECONOCIMIENTOS Y CIERRE (beats 100–108) ────────────────
  {
    nombre: "Foto: entrega de diplomas y medallas",
    archivo: null,
    desde: 0,
    beats: 2,
    fotos: [F10],
    pies: ["Reconocimientos"],
    transicion: "zoom",
    efecto: "whoosh",
  },
  {
    nombre: "Foto: premiados con medallas y diplomas",
    archivo: null,
    desde: 0,
    beats: 3,
    fotos: [F09],
    texto: "Así fue ese día…",
    transicion: "glitch",
  },
  {
    nombre: "Foto: profes 'Math is my superpower'",
    archivo: null,
    desde: 0,
    beats: 3,
    fotos: [F02],
    pies: ["Math is my superpower"],
    texto: "…y estuvo brutal.",
    transicion: "fundido",
  },
];
