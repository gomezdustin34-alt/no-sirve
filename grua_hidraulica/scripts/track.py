"""Rastrea la grúa en v6 usando el color de la manguera rosa (marcador natural).

Guarda trabajo/track_v6.json con, para cada fotograma, el centro del lazo de
manguera sobre la mesa (x, y) y su tamaño aparente (para estimar el zoom de cámara).
Las etiquetas y lupas de render.py se anclan a esta posición."""
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
W, H = 576, 1024


def frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def main():
    out = []
    prev = np.array([250.0, 910.0])
    for i, f in enumerate(frames(ROOT / "trabajo" / "pre" / "v6.mp4")):
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
        # rosa / magenta saturado
        m = cv2.inRange(hsv, (140, 70, 120), (175, 255, 255))
        m[:700] = 0                          # solo la zona de la mesa
        ys, xs = np.nonzero(m)
        if len(xs) > 40:
            # robusto a manos/jeringa: se queda con los píxeles cerca de la mediana
            cx, cy = np.median(xs), np.median(ys)
            keep = (np.abs(xs - cx) < 90) & (np.abs(ys - cy) < 50)
            cx, cy = xs[keep].mean(), ys[keep].mean()
            spread = np.percentile(xs[keep], 95) - np.percentile(xs[keep], 5)
            prev = np.array([cx, cy])
            out.append([float(cx), float(cy), float(spread), int(len(xs))])
        else:
            out.append([float(prev[0]), float(prev[1]), None, 0])
    a = np.array([[o[0], o[1]] for o in out])
    # suavizado temporal (media móvil centrada de 9 fotogramas)
    k = 9
    pad = np.pad(a, ((k // 2, k // 2), (0, 0)), mode="edge")
    sm = np.stack([np.convolve(pad[:, j], np.ones(k) / k, mode="valid") for j in range(2)], 1)
    sp = np.array([o[2] if o[2] else np.nan for o in out])
    sp = np.where(np.isnan(sp), np.nanmedian(sp), sp)
    pad = np.pad(sp, (15, 15), mode="edge")
    sp_s = np.convolve(pad, np.ones(31) / 31, mode="valid")
    res = [{"x": round(float(x), 1), "y": round(float(y), 1), "s": round(float(s), 1)} for (x, y), s in zip(sm, sp_s)]
    (ROOT / "trabajo" / "track_v6.json").write_text(json.dumps(res))
    print(len(res), "fotogramas; ejemplo:", res[150], res[990], res[1160])


if __name__ == "__main__":
    main()
