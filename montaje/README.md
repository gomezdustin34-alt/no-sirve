# Montaje rápido — "Todo lo que se vivió"

Video vertical 1080x1920, 30 fps, 16.2 s: `salida/montaje_rapido.mp4`.

## Cómo está armado

La música (sintetizada en `musica.py`) va a **150 BPM**, así que una semicorchea
dura exactamente 0.1 s (3 fotogramas). Toda la línea de tiempo de `montaje.py`
está en semicorcheas, por eso **cada corte cae sobre un golpe** (además cada corte
lleva su propio acento de bombo/hat, y los whips llevan un "whoosh").

| Tramo | Tiempo | Planos | Duración por plano | Música |
|---|---|---|---|---|
| Arranque | 0.0–3.2 s | 5 | 0.8 → 0.4 s | bombo, bajo, pad |
| Sube | 3.2–6.4 s | 7 | 0.4 s + 1 cámara lenta de 0.8 s | + palmas, arpegio |
| Acelera | 6.4–8.0 s | 5 | 0.4–0.3 s | + hats abiertos, riser |
| Build | 8.0–9.6 s | 7 | 0.3–0.2 s | redoble de caja |
| **Ráfaga** | 9.6–11.2 s | **12 flashes** | 0.2–0.1 s | drop: crash + sub |
| Corte a silencio | 11.2 s | — | — | silencio total |
| Toma final | 11.2–16.2 s | 1 (cámara lenta 0.35x) | 5 s | piano suave |

Efectos: speed ramps (planos 3, 7), zooms animados con easing en todos los planos,
whip transitions con desenfoque direccional (siguiendo la dirección del paneo),
motion blur (`tmix`) en los planos acelerados, temblor de cámara y flashes de
exposición en la ráfaga, cámara lenta con interpolación de movimiento
(`minterpolate`), grado de color, viñeta y texto final:
*"Y esto… fue solo una parte de lo que vivimos."*

## Volver a generarlo

```bash
pip install numpy          # ffmpeg con zscale también es necesario
# poner los clips en montaje/clips/ (IMG_3854.mov, IMG_3855.mov, IMG_3856.mov)
python3 montaje/montaje.py
```

Para cambiar el orden, encuadres o duraciones, edita `TIMELINE` en `montaje.py`
(cada `S(...)` es un plano: clip, segundo de inicio, centro del encuadre, zoom,
duración en semicorcheas y efectos). Para agregar más clips, súmalos a `SOURCES`.
