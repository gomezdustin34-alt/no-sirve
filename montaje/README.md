# AURA FEST — Montaje "Todo lo que se vivió"

Video vertical 1080x1920, 30 fps, ~59.8 s: `salida/montaje_rapido.mp4`.

## Cómo está armado

La música es la canción `clips/cancion.mp4` (versión en español de
*Can't Help Falling in Love*, ~70 BPM), cortada en 55.0 s para quitar el jingle de
TikTok. Sus golpes (`BEATS` en `montaje.py`, detectados con librosa) definen
**todos los cortes**, y la edición se acelera por tramos:

| Tramo | Tiempo | Planos | Duración por plano |
|---|---|---|---|
| Intro ("Los sabios dicen…") | 0–2.7 s | 1 | 2.7 s, cámara lenta |
| Estrofa | 2.7–28.4 s | 15 | 2 golpes (~1.7 s), cámara lenta + destellos suaves |
| Sube | 28.4–43.9 s | 18 | 1 golpe (~0.86 s), whips |
| Build | 43.9–48.2 s | 10 | 1/2 golpe (~0.43 s) |
| **Ráfaga** | 48.2–50.8 s | **12 flashes** | 1/4 de golpe (~0.21 s) |
| Toma final | 50.8–56.3 s | 1 (cámara lenta 0.35x) | "Y esto… fue solo una parte de lo que vivimos." + **AURA FEST** |
| Créditos | 56.3–59.8 s | placa en negro | Presentado por: Dustin Gomez, Jairo Maldonado y Edgar Rivero |

Regla de edición: **ningún momento se repite**; se priorizan momentos felices,
reacciones y los lugares más bonitos.

Look de "época filosófica": brillo suave tipo ensueño, tonos cálidos con un 25 %
de sepia, viñeta, grano de película y tipografía con serifa.

## Volver a generarlo

```bash
# ffmpeg con zscale; clips en montaje/clips/ (ver SOURCES en montaje.py) + cancion.mp4
python3 montaje/montaje.py
```

Para cambiar planos edita `TIMELINE` (cada `S(...)`: clip, segundo de inicio,
centro del encuadre, zoom inicial/final, velocidad y efectos). Los cortes salen
de `cut_points()`; los planos sin cambios se reutilizan desde `build/`.
