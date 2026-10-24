#!/bin/bash
# Prepara cada sesión en la nube con las herramientas para crear videos animados
# (dibujo, audio, voz y montaje). Solo se ejecuta en sesiones remotas.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PAQUETES=(
  Pillow numpy opencv-python-headless librosa scipy soundfile imageio imageio-ffmpeg
  moviepy scikit-image scikit-learn matplotlib pydub audioread edge-tts
)

# Si todo ya está instalado (contenedor en caché), no reinstala nada.
if python3 -c "import PIL, numpy, cv2, librosa, scipy, soundfile, imageio, imageio_ffmpeg, moviepy, skimage, sklearn, matplotlib, pydub, audioread, edge_tts" 2>/dev/null; then
  echo "Bibliotecas de video ya instaladas."
else
  echo "Instalando bibliotecas de animación y audio..."
  # El pip del sistema lo gestiona Debian: no se actualiza pip, solo se instalan los paquetes.
  python3 -m pip install --quiet --disable-pip-version-check "${PAQUETES[@]}"
fi

command -v ffmpeg >/dev/null 2>&1 && ffmpeg -version | head -n 1 || echo "Aviso: FFmpeg no está disponible."
command -v git >/dev/null 2>&1 && git --version || echo "Aviso: Git no está disponible."

python3 -c "import PIL, numpy, cv2, librosa, scipy, soundfile, imageio, skimage, sklearn, matplotlib, pydub, edge_tts; print('Todas las bibliotecas principales están listas.')"
