# 🎬 Cómo montar el aftermovie de la OMI

Este proyecto usa **Remotion**: el video se arma con código, pero tú solo necesitas
editar **un archivo**: `src/Omi/config.ts`. Ahí dices qué clip va en cada lugar,
cuánto dura, si va en cámara lenta, qué texto lleva y cómo pasa al siguiente.

El video es **vertical (1080×1920)**, listo para Reels, TikTok, Shorts o Estados.

Lo demás ya está hecho:

- cortes sincronizados con los golpes de la música
- zooms y paneos suaves
- cámara lenta y speed ramps
- transiciones limpias
- ráfagas de π √ ∑ y figuras geométricas
- textos animados, efectos de sonido, barras de cine opcionales y pantalla final

---

## 1. Preparar el proyecto (una sola vez)

Necesitas [Node.js](https://nodejs.org) 18 o superior.

```bash
cd video
npm install
```

## 2. Poner el material en su lugar

```
video/public/omi/clips/    ← aquí van TODOS tus videos
video/public/omi/musica/   ← aquí va la canción
```

**Renombra los archivos** con nombres cortos, sin espacios ni tildes, que digan qué
son. Te ahorrará mucho tiempo:

```
llegada-1.mp4   llegada-2.mp4   salon-general.mp4   concentracion-1.mp4
risas-1.mp4     aplausos.mp4    foto-grupal.mp4     ...
```

Consejos sobre los archivos:

- **Formato:** `.mp4` es lo ideal. Los `.mov` de iPhone (HEVC) a veces no se ven en la
  vista previa; conviértelos a MP4 H.264 con [HandBrake](https://handbrake.fr)
  (preset "Fast 1080p30") o con ffmpeg:
  `ffmpeg -i IMG_1234.MOV -c:v libx264 -crf 18 -c:a aac IMG_1234.mp4`
- **Vertical:** graba y usa tomas verticales. Si tienes alguna horizontal, se
  recorta al centro automáticamente: revisa en la vista previa que no se corte
  la persona importante.
- **Cámara lenta:** si alguien grabó a 60 fps, usa esas tomas para los momentos lentos.
  Se verán mucho más suaves.
- **Fotos:** si tienes fotos buenas también sirven, pero esta plantilla está pensada
  para video. Pídemelo y agrego soporte para fotos con movimiento.

## 3. Elegir la música

1. Copia tu pista a `public/omi/musica/`, por ejemplo `pista.mp3`.
   Busca una instrumental *cinematic / inspirational* libre de derechos: YouTube Audio
   Library, Pixabay Music, Uppbeat…
2. En `src/Omi/config.ts`, en `MUSICA`:
   ```ts
   archivo: "omi/musica/pista.mp3",
   bpm: 120,       // el tempo de la canción
   empiezaEn: 0,   // segundo donde arranca (para saltar una intro larga)
   ```
3. **El BPM es clave**: todos los cortes se calculan con él. Búscalo con
   "nombre de la canción + BPM" en internet, o tocando el ritmo en
   una web de "BPM tapper". Si está mal, los cortes no caen en el golpe.

> 💡 Elige una canción que empiece tranquila y vaya creciendo. La plantilla ya
> usa planos largos al inicio y cortes cada vez más rápidos hacia el clímax.

## 4. Abrir el editor visual (Remotion Studio)

```bash
npm run dev
```

Se abre `http://localhost:3000`. A la izquierda verás dos composiciones:

| Composición | Para qué sirve |
|---|---|
| **OMI** | El aftermovie. Mientras un clip no tenga archivo, verás una tarjeta azul con su nombre ("PLANO 5 · 4 BEATS…") para ver el ritmo. |
| **Revisar** | Para mirar un clip crudo y encontrar el segundo exacto de su mejor momento. |

Cada vez que guardas `config.ts`, la vista previa se actualiza sola.

## 5. Encontrar los mejores momentos (con "Revisar")

1. Abre la composición **Revisar**.
2. En el panel derecho (Props), escribe en `archivo` la ruta del clip,
   por ejemplo `omi/clips/risas-1.mp4`.
3. Dale play o arrastra la línea de tiempo. Arriba a la izquierda verás
   **`desde: 12,4`**: es el número que vas a copiar.
4. Anota los momentos buenos de cada clip. Busca risas reales, caras de
   concentración, manos escribiendo, abrazos, aplausos y reacciones.

## 6. Montar: llenar la lista de planos

En `src/Omi/config.ts`, la lista `CLIPS` ya trae **24 planos** organizados así:

**intro → llegada → preparación → estudiantes → competencia → espontáneos →
interacción → destacados → cierre**

Cada plano tiene un `nombre` que sugiere qué tipo de toma poner ahí. Para montar
uno, cambia `archivo` y `desde`:

```ts
{
  nombre: "Espontáneo: risas (con sonido real)",
  archivo: "omi/clips/risas-1.mp4",   // ← tu clip
  desde: 12.4,                         // ← el segundo que anotaste (con PUNTO, no coma)
  beats: 4,
  movimiento: "zoom-in",
  sonidoReal: 0.9,
  texto: "Más que matemáticas…",
  transicion: "corte",
},
```

### Qué hace cada campo

| Campo | Qué hace | Valores |
|---|---|---|
| `archivo` | El clip. `null` = tarjeta de ejemplo | `"omi/clips/xxx.mp4"` |
| `desde` | Segundo del clip original donde empieza | `12.4` |
| `beats` | Cuánto dura, en golpes de música (a 120 BPM, 4 beats = 2 s) | `2`, `4`, `8` |
| `velocidad` | Cámara lenta o rápida | `0.5` lenta, `0.35` muy lenta, `1` normal |
| `rampa` | Speed ramp: rápido → frena en cámara lenta | `true` |
| `movimiento` | Movimiento de cámara | `"zoom-in"`, `"zoom-out"`, `"izquierda"`, `"derecha"`, `"ninguno"` |
| `sonidoReal` | Volumen del audio del clip (risas, aplausos). Solo suena a velocidad normal, y la música baja sola cuando es fuerte (≥ 0.5) | `0` a `1` |
| `texto` / `subtexto` | Texto animado sobre el plano | `"Un día de retos"` |
| `transicion` | Cómo pasa **al siguiente** plano | `"corte"`, `"fundido"`, `"deslizar"`, `"barrido"`, `"matematica"`, `"destello"` |
| `efecto` | Sonido sutil en ese corte | `"whoosh"`, `"impact"`, `"riser"`, `"click"` |

**Puedes borrar, duplicar y reordenar planos libremente.** La duración total del
video se recalcula sola. Si tienes pocas tomas buenas, es mejor borrar planos que
rellenar con tomas flojas o repetidas.

### Reglas de oro para que quede "brutal"

- **Empieza con lo mejor.** Los 2 primeros planos son tu gancho: el plano más
  bonito y la mejor toma de los estudiantes, en cámara lenta.
- **El ritmo crece.** Usa planos largos (8 beats) al inicio y cortos (2 beats)
  en la competencia y el clímax.
- **Alterna tamaños de plano:** general → primer plano → detalle → general.
  Así el video respira.
- **Cámara lenta solo en momentos con emoción:** una sonrisa, un abrazo,
  alguien celebrando. Si todo va lento, nada destaca.
- **`"destello"` + `"impact"`** para los golpes más fuertes. **`"matematica"`**
  para cambiar de sección (no la uses en todos los cortes).
- **`"riser"`** en el corte *antes* de un momento importante: genera expectativa.
- **Pocos textos.** La plantilla trae 6, y está bien así.
- **No inventes.** Si no hubo premiación, borra ese plano. Si en la `firma` del cierre
  pones colegio o fecha, que sean datos reales.

## 7. Pantalla final

En `CIERRE`:

```ts
texto: "Una experiencia para recordar.",
firma: "OMI 2026 · Nombre del colegio",  // opcional, o null
segundos: 4,
```

## 8. Exportar el video final

```bash
npx remotion render OMI out/omi-aftermovie.mp4
```

El archivo queda en `video/out/omi-aftermovie.mp4` (vertical 1080×1920, 30 fps).

- Máxima calidad: agrega `--crf=16`
- Borrador rápido para revisar: agrega `--scale=0.5`
- También puedes exportar desde el Studio con el botón **Render**

## 9. Ajustes opcionales

- **Versión horizontal** (para YouTube o proyector): en `config.ts`, `VERTICAL = false`.
- **Barras de cine:** `BARRAS_CINE = true` (vienen apagadas porque en vertical quitan espacio).
- **Efectos más fuertes o más suaves:** cambia `VOLUMEN_EFECTOS` (0.35 por defecto).
- **Tus propios efectos:** reemplaza los `.wav` en `public/sfx/` manteniendo el
  nombre. Si quieres regenerar los originales: `node scripts/generar-sfx.mjs`.
- **Colores y tipografía:** están en `src/Omi/estilo.ts`.
- **Símbolos de las ráfagas:** también en `src/Omi/estilo.ts` (lista `SIMBOLOS`).

## 10. Problemas comunes

| Problema | Solución |
|---|---|
| Error "file not found" o pantalla en rojo | Revisa que la ruta en `archivo` coincida exactamente (mayúsculas incluidas) y que **no** empiece con `public/` |
| El clip se ve negro en la vista previa | Probablemente es HEVC: conviértelo a MP4 H.264 (paso 2) |
| Los cortes no caen en el golpe | El `bpm` está mal, o `empiezaEn` no coincide con un golpe |
| El clip se congela o se pone negro al final del plano | El clip es más corto que `desde` + la duración del plano. Baja `desde`, baja `beats` o sube `velocidad` |
| La cámara lenta se ve a saltos | El clip es de 30 fps. Usa `velocidad: 0.6` en vez de `0.35`, o tomas de 60 fps |

> ⚠️ Los videos crudos **no se suben a git** (pesan demasiado). Ya están excluidos
> en `.gitignore`. Guarda una copia del material en Drive o en un disco.
