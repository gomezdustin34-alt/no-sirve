"""Opcional · Transcripción con marcas de tiempo por palabra (cómo se obtuvieron los subtítulos de edl.py).

Usa sherpa-onnx con el modelo multilingüe NVIDIA Parakeet-TDT 0.6B v3 (incluye español), descargable de:
  https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2
Descomprímelo en modelos/ y ejecuta:
  pip install sherpa-onnx
  python scripts/transcribe.py   → trabajo/palabras.json  (+ texto por pantalla)

Para comparar, también se usó Whisper large-v3-turbo (sherpa-onnx-whisper-turbo) por fragmentos.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import sherpa_onnx as so

ROOT = Path(__file__).resolve().parent.parent
M = ROOT / "modelos" / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"


def load(path):
    # mismo prefiltrado que se usó: limpia viento y ruido antes del reconocimiento
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af",
                        "highpass=f=90,lowpass=f=7500,afftdn=nr=12:nf=-35,dynaudnorm=f=200:g=15",
                        "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32)


def main():
    rec = so.OfflineRecognizer.from_transducer(
        encoder=str(M / "encoder.int8.onnx"), decoder=str(M / "decoder.int8.onnx"),
        joiner=str(M / "joiner.int8.onnx"), tokens=str(M / "tokens.txt"), num_threads=4,
        model_type="nemo_transducer")
    out = {}
    for f in sorted((ROOT / "fuentes").glob("v*.mp4")):
        s = rec.create_stream()
        s.accept_waveform(16000, load(f))
        rec.decode_stream(s)
        words = []
        for tk, t in zip(s.result.tokens, s.result.timestamps):
            if tk.startswith("▁") or not words:
                words.append([tk.replace("▁", "").strip(), round(t, 2)])
            else:
                words[-1][0] += tk
        out[f.stem] = words
        print(f"{f.stem}: {s.result.text}\n   " + " ".join(f"{w}@{t:.2f}" for w, t in words))
    (ROOT / "trabajo").mkdir(exist_ok=True)
    (ROOT / "trabajo" / "palabras.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
