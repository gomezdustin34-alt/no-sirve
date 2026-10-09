# Grúa hidráulica: edición automatizada

Este sistema monta el vídeo educativo de la grúa hidráulica a partir de los 9 clips originales.
Todo se hace con Python y FFmpeg: no hace falta ningún editor de vídeo.

## Resultado (`salida/`)

| Archivo | Contenido |
|---|---|
| `grua_hidraulica_final.mp4` | Vídeo final, 1920×1080, H.264, 30 fps, AAC 48 kHz, −14 LUFS |
| `subtitulos_es.srt` / `.ass` | Subtítulos en español, sincronizados (el `.ass` resalta los conceptos clave) |
| `capitulos.txt` | Marcas de capítulo, listas para pegar en la descripción de YouTube |
| `audio/stem_*.wav` | Pistas separadas: diálogos, música, efectos y mezcla sin música |
| `audio/mezcla_final.wav` | Mezcla final del audio |

## Estructura del vídeo (≈ 3 min 45 s)

| Tiempo | Sección | Material |
|---|---|---|
| 0:00 | **Gancho**: el brazo levanta la carga (cámara lenta), seguido de la pregunta *«¿Cómo puede una simple jeringa levantar una carga?»* | v6 |
| 0:07 | **Título**: «GRÚA HIDRÁULICA · Aplicación del principio de Pascal» | v6 |
| 0:11 | **01 Presentación**: el equipo, la coordinadora y el reto | v1, v3, v7 |
| 1:08 | **02 Investigación y método**: los 4 pasos y la fuente consultada | v8, v2 |
| 1:41 | **03 Diseño y materiales**: medidas del boceto y lista de materiales | v4, v5, v6 |
| 2:47 | **04 ¿Cómo funciona?**: animación del principio de Pascal, P = F / A | gráfico |
| 3:08 | **05 Demostración**: prueba real, lupa de detalle y repetición a 0,35× | v6 |
| 3:28 | **06 Conclusión** y créditos sobre un plano de la grúa | v9, v6 |

## Cómo ejecutarlo en tu ordenador

1. Instala **Python 3.10 o superior** y **FFmpeg**. FFmpeg tiene que incluir `libvidstab` y `arnndn`
   (las versiones "full" de gyan.dev en Windows, y `brew install ffmpeg` en macOS, ya los traen).
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Copia los clips originales en `fuentes/` con los nombres `v1.mp4` … `v9.mp4` (más abajo está la correspondencia).
4. Ejecuta, desde esta carpeta:
   ```
   python scripts/preprocess.py      # estabilización, color y limpieza de audio (≈ 15 min)
   python scripts/track.py           # rastreo de la grúa en v6 (≈ 1 min)
   python scripts/render.py --jobs 4 # montaje final (≈ 10-20 min según el equipo)
   ```

Opciones de `render.py`:
- `--musica mi_pista.mp3`: sustituye la música sintetizada por una pista con licencia.
  Se nivela y se atenúa automáticamente bajo las voces.
- `--sin-subtitulos`: genera el vídeo sin subtítulos quemados en la imagen (se pueden cargar
  aparte con el `.srt`).
- `--stills 12.5 80`: solo exporta fotogramas PNG de esos segundos, para revisar el diseño.

## Cómo hacer cambios

Todo el contenido está en **`scripts/edl.py`**:
- `CUES`: el texto de los subtítulos. Puedes corregir cualquier palabra y volver a ejecutar `render.py`.
- `NOMBRES`: los nombres de los créditos finales. Rellena los que faltan.
- `SEGMENTS`: el orden de los planos, los puntos de entrada y salida, los zooms, los paneles y las etiquetas.

## Correspondencia de archivos

| Clip | Archivo original | Contenido |
|---|---|---|
| v1 | b3e5c434-….mp4 | Presentación del equipo (6 integrantes) |
| v2 | 1faccc6d-….mp4 | Líder de la investigación |
| v3 | f09e99e2-….mp4 | Coordinadora de planeación |
| v4 | 38def276-….mp4 | Diseñadora estructural: boceto (base y laterales) |
| v5 | 15998647-….mp4 | Boceto: soportes (22 cm y 3 cm) |
| v6 | cb6d92b3-….mp4 | Encargado de la construcción: materiales y **demostración** |
| v7 | d4051575-….mp4 | Relatora: actividad y reto |
| v8 | 3c95abf2-….mp4 | Relatora: proceso (investigación, planeación, construcción, evaluación) |
| v9 | d2ae17c6-….mp4 | Relatora: conclusión |

## Qué hace cada paso

- **Audio:** filtro paso alto, reducción de ruido con red neuronal (RNNoise) y por FFT, ecualización de
  presencia y compresión suave. Una puerta suave baja el ruido de fondo entre frases sin eliminar las
  pausas naturales. Las voces se nivelan entre sí, la música baja sola cuando alguien habla y el
  máster queda a −14 LUFS con pico de −1 dBFS.
- **Imagen:** estabilización `vidstab` en dos pasadas, reducción de ruido ligera, corrección de contraste
  y saturación, y un tono frío suave.
- **Montaje:** los cortes van entre frases (con marcas de tiempo por palabra) y se eliminan los tiempos
  muertos (por ejemplo, 8 s en v4 mientras se ordenan los papeles). Los saltos dentro de un mismo plano
  se disimulan con un cambio de zoom.
- **Cámara lenta:** interpolación de movimiento (`minterpolate`) en la elevación del brazo.
- **Gráficos:** panel lateral para los clips verticales, lista de materiales que se marca a medida que
  se nombran, tarjetas con las medidas dichas en el vídeo, lupa ×2,1 sobre la grúa con etiquetas que
  siguen a la cámara (la manguera rosa se usa como marcador de rastreo) y arco de trayectoria del brazo.
- **Música:** composición original sintetizada por código a 120 BPM (Re menor). Por eso no hay
  problemas de licencia. Las capas suben y bajan según la sección y los acentos caen en los cortes
  del gancho y en los cambios de capítulo.
