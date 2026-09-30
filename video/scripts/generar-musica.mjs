// Genera una pista instrumental PROVISIONAL de 120 BPM para el aftermovie:
// empieza tranquila (pad + arpegio), entra el ritmo y crece hasta un clímax.
// Uso: node scripts/generar-musica.mjs
// Sale en public/musica/omi-provisional.wav. Cámbiala por una canción real
// cuando la tengas (ver GUIA-OMI.md, paso 3).
import { mkdirSync, writeFileSync } from "node:fs";

const SR = 44100;
const BPM = 120;
const BEAT = 60 / BPM;
const BEATS = 116; // 108 del montaje + 8 de la pantalla final (4 s)
const TOTAL = BEATS * BEAT + 3; // + cola final
const N = Math.round(TOTAL * SR);
const out = new Float32Array(N);

let semilla = 7;
const ruido = () => {
  semilla = (semilla * 1103515245 + 12345) & 0x7fffffff;
  return (semilla / 0x7fffffff) * 2 - 1;
};
const hz = (midi) => 440 * Math.pow(2, (midi - 69) / 12);

// Progresión inspiradora: Am – F – C – G (un acorde por compás de 4 beats).
const ACORDES = [
  [57, 60, 64], // Am
  [53, 57, 60], // F
  [48, 52, 55], // C
  [55, 59, 62], // G
];
const acorde = (beat) => ACORDES[Math.floor(beat / 4) % 4];

/** Energía de cada sección, según el montaje. */
const seccion = (beat) => {
  if (beat < 16) return "intro"; // planos largos, título
  if (beat < 44) return "retos"; // estaciones y retos
  if (beat < 60) return "competencia"; // Pensar. Resolver. Competir.
  if (beat < 76) return "exposiciones"; // Más que matemáticas…
  if (beat < 100) return "climax"; // compañerismo y destacados
  return "cierre";
};

const agregar = (t0, dur, fn) => {
  const i0 = Math.round(t0 * SR);
  const n = Math.round(dur * SR);
  for (let i = 0; i < n && i0 + i < N; i++) out[i0 + i] += fn(i / SR);
};

// ── Pad (cuerdas suaves) ──────────────────────────────────────
for (let b = 0; b < BEATS; b += 4) {
  const notas = [...acorde(b), acorde(b)[0] - 12];
  const s = seccion(b);
  const vol = s === "intro" ? 0.16 : s === "cierre" ? 0.2 : 0.13;
  const dur = 4 * BEAT + 1.2;
  for (const m of notas) {
    const f = hz(m);
    agregar(b * BEAT, dur, (t) => {
      const env = Math.min(1, t / 0.6) * Math.min(1, (dur - t) / 1.2);
      const v =
        Math.sin(2 * Math.PI * f * t) +
        0.4 * Math.sin(2 * Math.PI * f * 1.003 * 2 * t) +
        0.2 * Math.sin(2 * Math.PI * f * 0.997 * 3 * t);
      return v * env * vol * 0.35;
    });
  }
}

// ── Arpegio (tipo piano/pluck) ────────────────────────────────
for (let b = 4; b < 112; b += 0.5) {
  const s = seccion(b);
  const notas = acorde(b);
  const paso = Math.round(b * 2) % 4;
  const alto = s === "climax" ? 24 : 12;
  const m = [notas[0], notas[1], notas[2], notas[1]][paso] + alto;
  const f = hz(m);
  const vol = s === "intro" ? 0.1 : s === "exposiciones" ? 0.1 : 0.13;
  agregar(b * BEAT, 0.9, (t) => {
    const env = Math.exp(-t * 5) * Math.min(1, t / 0.004);
    return (Math.sin(2 * Math.PI * f * t) + 0.3 * Math.sin(4 * Math.PI * f * t)) * env * vol;
  });
}

// ── Bajo ──────────────────────────────────────────────────────
for (let b = 16; b < 100; b++) {
  const s = seccion(b);
  if (s === "exposiciones" && b % 2) continue;
  const f = hz(acorde(b)[0] - 24);
  agregar(b * BEAT, BEAT * 0.95, (t) => {
    const env = Math.exp(-t * 3) * Math.min(1, t / 0.01);
    return Math.tanh(1.5 * Math.sin(2 * Math.PI * f * t)) * env * 0.22;
  });
}

// ── Batería ───────────────────────────────────────────────────
const kick = (t0, vol) => {
  let fase = 0;
  agregar(t0, 0.35, (t) => {
    fase += (2 * Math.PI * (45 + 90 * Math.exp(-t * 30))) / SR;
    return Math.sin(fase) * Math.exp(-t * 9) * vol;
  });
};
const clap = (t0, vol) => {
  let prev = 0;
  agregar(t0, 0.18, (t) => {
    const n = ruido();
    const hp = n - prev;
    prev = n;
    return hp * Math.exp(-t * 22) * vol;
  });
};
const hat = (t0, vol) => {
  let prev = 0;
  agregar(t0, 0.05, (t) => {
    const n = ruido();
    const hp = n - prev;
    prev = n;
    return hp * Math.exp(-t * 90) * vol;
  });
};

for (let b = 16; b < 100; b++) {
  const s = seccion(b);
  const t = b * BEAT;
  if (s === "retos") {
    if (b % 2 === 0) kick(t, 0.5);
    hat(t + BEAT / 2, 0.08);
  } else if (s === "competencia") {
    kick(t, 0.6);
    if (b % 2 === 1) clap(t, 0.22);
    hat(t + BEAT / 2, 0.1);
  } else if (s === "exposiciones") {
    if (b % 4 === 0) kick(t, 0.45);
    hat(t + BEAT / 2, 0.06);
  } else if (s === "climax") {
    kick(t, 0.65);
    if (b % 2 === 1) clap(t, 0.26);
    hat(t, 0.07);
    hat(t + BEAT / 2, 0.11);
  }
}
// Golpe final al entrar al cierre.
kick(100 * BEAT, 0.8);

// ── Eco suave para dar espacio ────────────────────────────────
const eco = Math.round(BEAT * 0.75 * SR);
for (let i = eco; i < N; i++) out[i] += out[i - eco] * 0.25;

// ── Master: fade in/out, saturación suave y normalización ─────
const fin = BEATS * BEAT;
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const fade = Math.min(1, t / 1.5) * Math.min(1, Math.max(0, (TOTAL - t) / (TOTAL - fin + 1)));
  out[i] = Math.tanh(out[i] * 1.2) * fade;
}
let pico = 0;
for (const v of out) pico = Math.max(pico, Math.abs(v));

const datos = Buffer.alloc(44 + N * 2);
datos.write("RIFF", 0);
datos.writeUInt32LE(36 + N * 2, 4);
datos.write("WAVEfmt ", 8);
datos.writeUInt32LE(16, 16);
datos.writeUInt16LE(1, 20);
datos.writeUInt16LE(1, 22);
datos.writeUInt32LE(SR, 24);
datos.writeUInt32LE(SR * 2, 28);
datos.writeUInt16LE(2, 32);
datos.writeUInt16LE(16, 34);
datos.write("data", 36);
datos.writeUInt32LE(N * 2, 40);
for (let i = 0; i < N; i++) {
  datos.writeInt16LE(Math.round((out[i] / pico) * 0.89 * 32767), 44 + i * 2);
}
const dir = new URL("../public/musica/", import.meta.url);
mkdirSync(dir, { recursive: true });
writeFileSync(new URL("omi-provisional.wav", dir), datos);
console.log(`public/musica/omi-provisional.wav (${TOTAL.toFixed(1)} s, ${BPM} BPM)`);
