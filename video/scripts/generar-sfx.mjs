// Genera efectos de sonido sutiles (whoosh, impact, riser, click) en public/sfx/.
// Uso: node scripts/generar-sfx.mjs
// Puedes reemplazar cualquiera de estos .wav por uno tuyo con el mismo nombre.
import { mkdirSync, writeFileSync } from "node:fs";

const SR = 44100;
const out = new URL("../public/sfx/", import.meta.url);
mkdirSync(out, { recursive: true });

// Ruido determinista para que el resultado sea siempre igual.
let semilla = 12345;
const ruido = () => {
  semilla = (semilla * 1103515245 + 12345) & 0x7fffffff;
  return (semilla / 0x7fffffff) * 2 - 1;
};

const guardar = (nombre, muestras) => {
  const pico = Math.max(...muestras.map(Math.abs)) || 1;
  const datos = Buffer.alloc(44 + muestras.length * 2);
  datos.write("RIFF", 0);
  datos.writeUInt32LE(36 + muestras.length * 2, 4);
  datos.write("WAVEfmt ", 8);
  datos.writeUInt32LE(16, 16);
  datos.writeUInt16LE(1, 20);
  datos.writeUInt16LE(1, 22);
  datos.writeUInt32LE(SR, 24);
  datos.writeUInt32LE(SR * 2, 28);
  datos.writeUInt16LE(2, 32);
  datos.writeUInt16LE(16, 34);
  datos.write("data", 36);
  datos.writeUInt32LE(muestras.length * 2, 40);
  muestras.forEach((m, i) =>
    datos.writeInt16LE(Math.round((m / pico) * 0.8 * 32767), 44 + i * 2),
  );
  writeFileSync(new URL(`${nombre}.wav`, out), datos);
  console.log(`public/sfx/${nombre}.wav`);
};

const generar = (segundos, fn) =>
  Array.from({ length: Math.round(segundos * SR) }, (_, i) => fn(i / SR, i));

// Whoosh: ruido filtrado cuyo brillo y volumen suben y bajan (0,8 s).
{
  let lp = 0;
  guardar(
    "whoosh",
    generar(0.8, (t) => {
      const p = t / 0.8;
      const env = Math.sin(Math.PI * Math.pow(p, 0.8)) ** 2;
      const corte = 0.02 + 0.25 * Math.sin(Math.PI * p);
      lp += corte * (ruido() - lp);
      return lp * env;
    }),
  );
}

// Impact: golpe grave que cae de tono + ataque corto (1 s).
{
  let fase = 0;
  let lp = 0;
  guardar(
    "impact",
    generar(1, (t) => {
      fase += (2 * Math.PI * (40 + 60 * Math.exp(-t * 18))) / SR;
      lp += 0.08 * (ruido() - lp);
      return Math.sin(fase) * Math.exp(-t * 4.5) + lp * 1.5 * Math.exp(-t * 30);
    }),
  );
}

// Riser: tono y ruido que suben durante 2,5 s y terminan en el corte.
{
  let fase = 0;
  let lp = 0;
  guardar(
    "riser",
    generar(2.5, (t) => {
      const p = t / 2.5;
      fase += (2 * Math.PI * (180 + 900 * p * p)) / SR;
      lp += (0.02 + 0.3 * p) * (ruido() - lp);
      const env = Math.pow(p, 2.2) * (p > 0.98 ? (1 - p) / 0.02 : 1);
      return (Math.sin(fase) * 0.35 + lp) * env;
    }),
  );
}

// Click: tic corto y seco (0,06 s).
guardar(
  "click",
  generar(0.06, (t) => Math.sin(2 * Math.PI * 2200 * t) * Math.exp(-t * 120)),
);

// Subdrop: caída grave y larga para el drop de la canción (1,8 s).
{
  let fase = 0;
  guardar(
    "subdrop",
    generar(1.8, (t) => {
      fase += (2 * Math.PI * (70 * Math.exp(-t * 1.2) + 28)) / SR;
      const env = Math.min(1, t / 0.005) * Math.exp(-t * 1.6);
      return Math.tanh(2.2 * Math.sin(fase)) * env;
    }),
  );
}

// Glitch: ráfagas digitales entrecortadas (0,35 s).
{
  let retenido = 0;
  guardar(
    "glitch",
    generar(0.35, (t, i) => {
      // "bitcrush": mantiene la muestra varias veces y corta a pedazos
      if (i % 24 === 0) retenido = ruido();
      const puerta = Math.sin(t * 2 * Math.PI * 38) > -0.2 ? 1 : 0;
      const tono = Math.sign(Math.sin(2 * Math.PI * (900 + 1400 * t) * t));
      return (retenido * 0.7 + tono * 0.25) * puerta * Math.exp(-t * 6);
    }),
  );
}

// Tick: golpecito seco para cada corte de la ráfaga (0,04 s).
guardar(
  "tick",
  generar(0.04, (t) => {
    const n = ruido();
    return (Math.sin(2 * Math.PI * 3200 * t) * 0.6 + n * 0.4) * Math.exp(-t * 160);
  }),
);

// Obturador: dos clics de cámara de fotos con un poco de mecanismo (0,18 s).
guardar(
  "obturador",
  generar(0.18, (t) => {
    const clic = (t0) =>
      t >= t0 ? (ruido() * 0.7 + Math.sin(2 * Math.PI * 1800 * t) * 0.3) * Math.exp(-(t - t0) * 120) : 0;
    return clic(0) + 0.7 * clic(0.075);
  }),
);
