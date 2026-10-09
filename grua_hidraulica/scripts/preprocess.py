"""Paso 1 · Preprocesado de los clips originales.

Para cada clip de fuentes/:
  * Vídeo: rotación automática, estabilización en dos pasadas (vidstab),
    reducción de ruido de imagen ligera, corrección de exposición/contraste/color.
    Se conserva la resolución nativa (el escalado final lo hace render.py).
  * Audio: filtro paso alto, reducción de ruido (RNNoise + FFT), ecualización
    de presencia para la voz y compresión suave. Salida WAV 48 kHz mono.

Uso:  python scripts/preprocess.py            (procesa todo)
      python scripts/preprocess.py v6 v7      (solo esos clips)
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "fuentes"
OUT = ROOT / "trabajo" / "pre"
RNN = ROOT / "assets" / "bd.rnnn"

# Ajuste de color por clip (todos grabados al aire libre con sol fuerte).
# eq: contraste / brillo / saturación / gamma.  Valores moderados: aspecto natural.
GRADE = {
    "default": "eq=contrast=1.07:brightness=-0.015:saturation=1.10:gamma=0.97",
    "v4": "eq=contrast=1.10:brightness=-0.03:saturation=1.05:gamma=0.95",   # papel muy claro
    "v5": "eq=contrast=1.10:brightness=-0.03:saturation=1.05:gamma=0.95",
    "v6": "eq=contrast=1.08:brightness=0.0:saturation=1.10:gamma=1.03",     # a la sombra
}
# Clips grabados a pulso que se benefician de la estabilización.
STABILIZE = {"v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9"}
# v6 lleva etiquetas ancladas a la grúa: zoom de estabilización fijo (sin "respiración").
OPTZOOM = {"v6": 1}

# Tono frío y ligera curva en S compartidos (estética "documental técnico").
LOOK = ("colorbalance=rs=-0.02:bs=0.03:rm=-0.01:bm=0.02:rh=0.0:bh=0.01,"
        "curves=master='0/0 0.25/0.23 0.75/0.78 1/1'")


def run(cmd):
    print("  $", " ".join(str(c) for c in cmd)[:160], "…")
    subprocess.run(cmd, check=True)


def process(name):
    src = SRC / f"{name}.mp4"
    OUT.mkdir(parents=True, exist_ok=True)
    trf = OUT / f"{name}.trf"
    vf = ["hqdn3d=1.2:1.2:3:3"]
    if name in STABILIZE:
        # vidstab escribe la ruta en el filtro: se usa ruta relativa para evitar ':' de Windows.
        os.chdir(OUT)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf",
             f"vidstabdetect=shakiness=5:accuracy=12:result={trf.name}", "-f", "null", "-"])
        vf.append(f"vidstabtransform=input={trf.name}:smoothing=18:optzoom={OPTZOOM.get(name, 2)}:zoomspeed=0.2:interpol=bicubic")
    vf += [GRADE.get(name, GRADE["default"]), LOOK, "fps=30", "format=yuv420p"]
    af = ",".join([
        "highpass=f=85:poles=2",
        f"arnndn=m='{RNN.as_posix()}':mix=0.75" if RNN.exists() else "anull",
        "afftdn=nr=10:nf=-42:tn=1",
        "equalizer=f=220:t=q:w=1.2:g=-2",      # menos "caja" / retumbe
        "equalizer=f=3200:t=q:w=1.5:g=3",      # presencia e inteligibilidad
        "equalizer=f=7500:t=q:w=2:g=-2",       # sibilancias / viento agudo
        "acompressor=threshold=-26dB:ratio=3:attack=8:release=180:makeup=4",
        "aresample=48000",
    ])
    os.chdir(OUT)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", ",".join(vf),
         "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-an", str(OUT / f"{name}.mp4")])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", af, "-ac", "1",
         "-c:a", "pcm_s16le", str(OUT / f"{name}.wav")])


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(p.stem for p in SRC.glob("v*.mp4"))
    for n in names:
        print("▶", n)
        process(n)
    print("Preprocesado listo en", OUT)
