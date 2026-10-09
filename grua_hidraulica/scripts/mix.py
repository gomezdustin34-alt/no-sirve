"""Mezcla de audio: diálogos limpios + música (sintetizada o externa) + efectos.

  * Cada fragmento de diálogo se nivela a la misma sonoridad de voz.
  * Puerta/expansor suave: entre palabras baja el ruido de fondo ~8 dB sin cortar
    las pausas naturales (no se eliminan, solo se limpian).
  * Fundidos de 25 ms en cada corte para evitar "clics".
  * Ducking: la música baja automáticamente cuando hay voz.
  * Master: −14 LUFS integrados, pico ≤ −1 dBFS.
"""
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm as pyln

import sound

SR = sound.SR


def read_wav(path):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.float32).astype(np.float64)


def write_wav(path, x, stereo=True):
    x = np.asarray(x, np.float32)
    data = np.stack([x, x], 1) if stereo and x.ndim == 1 else x
    ch = 2 if data.ndim == 2 else 1
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", "-",
                    "-c:a", "pcm_s24le", str(path)], input=data.tobytes(), check=True)


def env_db(x, win=0.02):
    n = int(win * SR)
    m = len(x) // n
    fr = x[:m * n].reshape(m, n)
    return 10 * np.log10(np.mean(fr ** 2, axis=1) + 1e-12), n


def smooth_gain(g_frames, n, attack=0.01, release=0.15):
    """Suaviza una curva de ganancia por tramos (dB) con ataque/relajación."""
    out = np.empty_like(g_frames)
    a_c = np.exp(-n / (attack * SR))
    r_c = np.exp(-n / (release * SR))
    cur = g_frames[0]
    for i, g in enumerate(g_frames):
        c = a_c if g > cur else r_c
        cur = c * cur + (1 - c) * g
        out[i] = cur
    return out


def gate(x, depth_db=8.0):
    """Expansor descendente: atenúa lo que está cerca del suelo de ruido."""
    e, n = env_db(x, 0.01)
    if len(e) < 10:
        return x
    floor = np.percentile(e, 15)
    speech = np.percentile(e, 85)
    thr = floor + 0.35 * (speech - floor)
    # 0 dB por encima del umbral, rampa hasta -depth por debajo
    g = -depth_db * np.clip((thr - e) / 6.0, 0, 1)
    g = smooth_gain(g, n, attack=0.005, release=0.12)
    gs = np.repeat(10 ** (g / 20), n)
    gs = np.pad(gs, (0, len(x) - len(gs)), mode="edge")
    return x * gs


def speech_rms_db(x):
    e, _ = env_db(x, 0.02)
    if len(e) == 0:
        return -60
    loud = e[e > np.percentile(e, 60)]
    return 10 * np.log10(np.mean(10 ** (loud / 10)) + 1e-12)


def fade(x, fi=0.025, fo=0.025):
    x = x.copy()
    a, b = int(fi * SR), int(fo * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a) ** 2
    if b:
        x[-b:] *= np.linspace(1, 0, b) ** 2
    return x


def limiter(x, ceiling_db=-1.0, look=0.005, release=0.08):
    c = 10 ** (ceiling_db / 20)
    n = int(look * SR)
    peak = np.abs(x)
    # máximo en ventana de anticipación
    from numpy.lib.stride_tricks import sliding_window_view
    padded = np.pad(peak, (0, n))
    pk = sliding_window_view(padded, n + 1).max(axis=1)[:len(x)]
    g = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    # relajación suave
    r = np.exp(-1 / (release * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(0, len(g), 64):
        blk = g[i:i + 64].min()
        cur = blk if blk < cur else r ** 64 * cur + (1 - r ** 64) * blk
        out[i:i + 64] = cur
    return x * out


def build(total, dialogs, sfx_events, music_sections, music_hits, music_file=None, outdir=None,
          duck_db=-16.0):
    """dialogs: [(wav_path, tin, tout, t_start, gain_db)]
       sfx_events: [(sig ndarray, t, gain)]"""
    n = int(total * SR) + 1
    dia = np.zeros(n)
    cache = {}
    target = -21.0
    for path, tin, tout, t0, gdb in dialogs:
        if path not in cache:
            cache[path] = gate(read_wav(path))
        src = cache[path]
        seg = src[int(tin * SR):int(tout * SR)]
        if len(seg) == 0:
            continue
        lvl = speech_rms_db(seg)
        seg = fade(seg) * 10 ** ((target - lvl + gdb) / 20)
        sound.place(dia, seg, t0)

    sfx = np.zeros(n)
    for sig, t, g in sfx_events:
        sound.place(sfx, sig, t, g)

    if music_file:
        mus = read_wav(music_file)
        mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
        # nivel por secciones también para música externa
        lvl = np.zeros(n)
        table = {0: -10.0, 1: -6.0, 2: -3.0, 3: 0.0}
        for s, e, L in music_sections:
            lvl[int(s * SR):int(e * SR)] = table[L]
        mus = mus * 10 ** (sound.smooth(lvl, 0.5)[:n] / 20)
        mus /= (np.max(np.abs(mus)) + 1e-9) / 0.5
    else:
        mus = sound.build_music(total, music_sections, music_hits)
        mus = np.pad(mus, (0, n - len(mus)))[:n]

    # fundido final de la música (3 s)
    k3 = int(3.0 * SR)
    mus[-k3:] *= np.linspace(1, 0, k3) ** 1.5
    # ducking: envolvente de la voz → reducción de la música
    e, k = env_db(dia, 0.05)
    active = (e > -45).astype(float)
    g = smooth_gain(active * duck_db, k, attack=0.12, release=1.0)
    gs = np.pad(np.repeat(10 ** (g / 20), k), (0, n), mode="edge")[:n]
    mus_d = mus * gs

    mix = dia + mus_d * 0.8 + sfx * 0.8
    # La salida es estéreo con L = R: BS.1770 suma la potencia de ambos canales (+3 dB),
    # así que se mide en estéreo para que el archivo final quede en −14 LUFS reales.
    meter = pyln.Meter(SR)
    loud = meter.integrated_loudness(np.stack([mix, mix], 1))
    mix *= 10 ** ((-14.0 - loud) / 20)
    mix = limiter(mix, -1.0)
    if outdir:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        gain = 10 ** ((-14.0 - loud) / 20)
        write_wav(outdir / "stem_dialogos.wav", dia * gain)
        write_wav(outdir / "stem_musica.wav", mus_d * 0.8 * gain)
        write_wav(outdir / "stem_efectos.wav", sfx * 0.8 * gain)
        write_wav(outdir / "stem_mezcla_sin_musica.wav", limiter((dia + sfx * 0.8) * gain, -1.0))
    return mix
