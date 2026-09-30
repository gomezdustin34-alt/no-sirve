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
 *   beats  64–80  sube la tensión      → compañerismo y concentración
 *   beat   80     ¡DROP!              → Pensar. Resolver. Competir.
 *   beats  80–108 parte más fuerte     → momentos destacados
 *   beats 108–116 la canción se apaga  → pantalla final
 */
export const CLIPS: Clip[] = [
  // ── INTRO (beats 0–16): los mejores planos ──────────────────
  {
    nombre: "Pasacalle OMΦ entre los árboles",
    archivo: V16,
    desde: 0.5,
    beats: 8,
    velocidad: 0.6,
    movimiento: "zoom-in",
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
    //   (espacio que no se parte) mantiene "la OMI" junta.
    texto: "Así se vivió la OMI",
    transicion: "fundido",
  },

  // ── LLEGADA (beats 16–28) ───────────────────────────────────
  {
    nombre: "Letrero Olimpiadas Matemáticas en la entrada",
    archivo: V16,
    desde: 9,
    beats: 4,
    movimiento: "zoom-out",
    transicion: "corte",
  },
  {
    nombre: "BIENVENIDOS con globos",
    archivo: V16,
    desde: 23,
    beats: 4,
    movimiento: "ninguno",
    transicion: "deslizar",
    efecto: "whoosh",
  },
  {
    nombre: "Estudiantes moviéndose entre estaciones",
    archivo: V2,
    desde: 5,
    beats: 4,
    movimiento: "derecha",
    sonidoReal: 0.3,
    transicion: "barrido",
    efecto: "whoosh",
  },

  // ── LOS RETOS (beats 28–44): entra el bajo ──────────────────
  {
    nombre: "Mesa 'Pensamiento Variacional' con tarjetas",
    archivo: V1,
    desde: 33,
    beats: 4,
    movimiento: "zoom-in",
    texto: "Un día de retos",
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
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Poniendo los números en el tablero",
    archivo: V14,
    desde: 3.5,
    beats: 2,
    movimiento: "zoom-in",
    transicion: "corte",
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
    transicion: "matematica",
    efecto: "whoosh",
  },

  // ── MÁS QUE MATEMÁTICAS (beats 44–60): exposiciones ─────────
  {
    nombre: "Museo de las Matemáticas",
    archivo: V6,
    desde: 0,
    beats: 2,
    movimiento: "zoom-in",
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
    transicion: "corte",
  },
  {
    nombre: "Exposición de los carritos robot",
    archivo: V10,
    desde: 2,
    beats: 2,
    movimiento: "zoom-in",
    sonidoReal: 0.4,
    transicion: "corte",
  },
  {
    nombre: "Exposición 'Origen de los números'",
    archivo: V11,
    desde: 3,
    beats: 2,
    movimiento: "derecha",
    sonidoReal: 0.4,
    transicion: "corte",
  },
  {
    nombre: "Dos expositoras explicando",
    archivo: V7,
    desde: 2,
    beats: 2,
    movimiento: "zoom-out",
    sonidoReal: 0.5,
    transicion: "deslizar",
    efecto: "whoosh",
  },
  {
    nombre: "Exposición 'Geometría en nuestra cultura'",
    archivo: V9,
    desde: 3,
    beats: 2,
    movimiento: "izquierda",
    sonidoReal: 0.4,
    transicion: "corte",
  },
  {
    nombre: "Profesora en la estación de frecuencias",
    archivo: V13,
    desde: 5,
    beats: 2,
    movimiento: "zoom-in",
    transicion: "fundido",
  },

  // ── COMPAÑERISMO (beats 60–68) ──────────────────────────────
  {
    nombre: "Profesora sonriendo con un estudiante (120 fps)",
    archivo: V15,
    desde: 15,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Compañeros mirando cómo resuelve el tangram",
    archivo: V5,
    desde: 45,
    beats: 4,
    movimiento: "zoom-in",
    transicion: "corte",
  },

  // ── LA TENSIÓN SUBE (beats 68–80): concentración ────────────
  {
    nombre: "Speed ramp: primer plano concentrado con las tarjetas",
    archivo: V3,
    desde: 30,
    beats: 4,
    rampa: true,
    movimiento: "zoom-in",
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
    nombre: "Primer plano mirando su tarjeta",
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

  // ── MOMENTOS DESTACADOS (beats 86–102) ──────────────────────
  {
    nombre: "Mano en la cabeza pensando la respuesta (lento)",
    archivo: V3,
    desde: 18.5,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "corte",
  },
  {
    nombre: "Niño con carnet OMI levanta la mirada (lento)",
    archivo: V2,
    desde: 36,
    beats: 4,
    velocidad: 0.5,
    movimiento: "zoom-out",
    transicion: "matematica",
    efecto: "whoosh",
  },
  {
    nombre: "Escultura de π y letras OMΦ (120 fps)",
    archivo: V17,
    desde: 0.5,
    beats: 4,
    velocidad: 0.4,
    movimiento: "zoom-in",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Medallas listas (120 fps)",
    archivo: V17,
    desde: 11,
    beats: 2,
    velocidad: 0.5,
    movimiento: "derecha",
    transicion: "corte",
    efecto: "click",
  },
  {
    nombre: "Diploma de mención de honor (120 fps)",
    archivo: V17,
    desde: 15.5,
    beats: 2,
    velocidad: 0.5,
    movimiento: "zoom-in",
    transicion: "fundido",
  },

  // ── CIERRE (beats 102–108) ──────────────────────────────────
  {
    nombre: "Auditorio: Olimpiadas Matemáticas INETFRADPAS",
    archivo: V16,
    desde: 49,
    beats: 6,
    velocidad: 0.6,
    movimiento: "zoom-out",
    transicion: "fundido",
  },
];
