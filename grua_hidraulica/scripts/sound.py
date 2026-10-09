"""Música original y efectos de sonido sintetizados por código (sin samples externos).

Todo se genera con numpy a 48 kHz, así que no hay problemas de licencia:
la pista es una composición original de este proyecto.

La música es "por secciones": render.py le pasa la línea de tiempo con la
intensidad deseada en cada tramo y los instantes de los cortes importantes,
y aquí se construye una pista a 120 BPM cuyos acentos caen en esos cortes.
"""
import numpy as np

SR = 48000
BPM = 120.0
BEAT = 60.0 / BPM
rng = np.random.default_rng(7)


# ───────────────────────── utilidades ─────────────────────────
def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s_len = max(0, n - a - d - r)
    e = np.concatenate([np.linspace(0, 1, max(a, 1)), np.linspace(1, s, max(d, 1)),
                        np.full(s_len, s), np.linspace(s, 0, max(r, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def lowpass_fast(x, fc):
    """Paso bajo por FFT con frecuencia de corte fija (rápido para señales largas)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def highpass_fast(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X, len(x))


def smooth(x, seconds):
    """Media móvil doble (≈ ventana triangular) mediante sumas acumuladas: O(n)."""
    k = max(1, int(seconds * SR / 2))
    for _ in range(2):
        c = np.cumsum(np.pad(x, (k, k), mode="edge"))
        x = (c[2 * k:] - c[:-2 * k]) / (2 * k)
    return x


def saw(freq, t):
    ph = (freq * t) % 1.0
    return 2 * ph - 1


def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    j0 = max(0, -i)
    i = max(i, 0)
    n = min(len(sig) - j0, len(buf) - i)
    buf[i:i + n] += sig[j0:j0 + n] * gain


def reverb(x, wet=0.25, decay=1.6):
    """Reverb sencilla por convolución con ruido de caída exponencial."""
    n = int(decay * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lowpass_fast(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return x * (1 - wet) + y * wet


# ───────────────────────── efectos de sonido ─────────────────────────
def sfx_impact(dur=2.2):
    """Golpe grave cinematográfico: barrido de seno 70→28 Hz + transitorio de ruido."""
    t = t_axis(dur)
    f = 28 + 42 * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 2.2)
    click = rng.standard_normal(len(t)) * np.exp(-t * 60)
    click = lowpass_fast(click, 2500)
    sub = np.tanh(2.2 * body) * 0.9
    out = sub + 0.35 * click
    return reverb(out, wet=0.2, decay=1.8) * 0.95


def sfx_whoosh(dur=0.7, up=True):
    t = t_axis(dur)
    n = rng.standard_normal(len(t))
    shape = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    # banda que barre en frecuencia: mezcla de dos pasos bajos ponderada en el tiempo
    lo, hi = lowpass_fast(n, 900), lowpass_fast(n, 5500)
    k = t / dur if up else 1 - t / dur
    s = (lo * (1 - k) + hi * k) * shape
    return highpass_fast(s, 150) * 0.55


def sfx_riser(dur=2.0):
    t = t_axis(dur)
    k = t / dur
    n = highpass_fast(lowpass_fast(rng.standard_normal(len(t)), 7000), 400) * k ** 2
    f = 220 * 2 ** (2.2 * k)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * k ** 2.5 * 0.25
    return (n * 0.35 + tone) * np.minimum(1, (1 - k) * 40)


def sfx_tick(freq=2400, dur=0.06):
    t = t_axis(dur)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 90) * 0.35


def sfx_blip():
    return np.concatenate([sfx_tick(1800, 0.05), sfx_tick(2700, 0.07)]) * 0.8


def sfx_transition():
    """Transición tecnológica: whoosh corto + 'blip' digital."""
    w = sfx_whoosh(0.55, up=True)
    out = np.zeros(int(0.8 * SR))
    place(out, w, 0)
    place(out, sfx_blip(), 0.42, 0.6)
    return out


def sfx_shutter():
    t = t_axis(0.18)
    n = rng.standard_normal(len(t)) * (np.exp(-t * 70) + 0.6 * np.exp(-((t - 0.07) * 80) ** 2))
    return highpass_fast(n, 1200) * 0.3


# ───────────────────────── música ─────────────────────────
# Progresión en Re menor: Dm – B♭ – F – C  (i – VI – III – VII), un acorde por compás.
CHORDS = [[50, 53, 57, 62], [46, 50, 53, 58], [53, 57, 60, 65], [48, 52, 55, 60]]
ROOTS = [38, 34, 41, 36]


def pad_layer(dur):
    t = t_axis(dur)
    out = np.zeros(len(t))
    bar = 4 * BEAT
    nb = int(np.ceil(dur / bar))
    for b in range(nb):
        ch = CHORDS[(b // 2) % 4]          # cada acorde dura 2 compases: más calma
        seg_t = t_axis(bar + 0.6)
        s = np.zeros(len(seg_t))
        for m in ch:
            for det in (-0.08, 0.08):
                s += saw(note_hz(m + det), seg_t)
        s *= env_adsr(len(seg_t), a=0.35, d=0.2, s=0.85, r=0.6)
        place(out, s, b * bar)
    return lowpass_fast(out, 1500) * 0.045


def bass_layer(dur):
    t = t_axis(dur)
    out = np.zeros(len(t))
    nbeats = int(dur / (BEAT / 2)) + 1
    for k in range(nbeats):
        bar = int(k * BEAT / 2 // (4 * BEAT))
        root = ROOTS[(bar // 2) % 4]
        nt = t_axis(BEAT / 2)
        s = np.sin(2 * np.pi * note_hz(root) * nt) + 0.3 * np.sin(2 * np.pi * note_hz(root + 12) * nt)
        s *= env_adsr(len(nt), a=0.004, d=0.12, s=0.35, r=0.05)
        place(out, s, k * BEAT / 2, 1.0 if k % 2 == 0 else 0.6)
    return np.tanh(out * 1.3) * 0.16


def arp_layer(dur):
    out = np.zeros(int(dur * SR))
    step = BEAT / 4
    pattern = [0, 2, 1, 3, 2, 1, 3, 2]
    n = int(dur / step) + 1
    for k in range(n):
        bar = int(k * step // (4 * BEAT))
        ch = CHORDS[(bar // 2) % 4]
        m = ch[pattern[k % 8]] + 12
        nt = t_axis(step * 1.6)
        s = (np.sin(2 * np.pi * note_hz(m) * nt) + 0.4 * np.sin(2 * np.pi * note_hz(m) * 2 * nt))
        s *= np.exp(-nt * 14)
        place(out, s, k * step, 0.9 if k % 4 == 0 else 0.55)
    return reverb(out * 0.05, wet=0.3, decay=1.2)


def drums_layer(dur):
    out = np.zeros(int(dur * SR))
    nt = t_axis(0.35)
    f = 45 + 90 * np.exp(-nt * 28)
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-nt * 9)
    nt = t_axis(0.25)
    snare = highpass_fast(rng.standard_normal(len(nt)), 1500) * np.exp(-nt * 22)
    nt = t_axis(0.05)
    hat = highpass_fast(rng.standard_normal(len(nt)), 7000) * np.exp(-nt * 80)
    n = int(dur / BEAT) + 1
    for k in range(n):
        tb = k * BEAT
        # bombo en 1 y 3, caja suave en 2 y 4, hi-hat en corcheas
        if k % 2 == 0:
            place(out, kick, tb, 0.55)
        else:
            place(out, snare, tb, 0.12)
        place(out, hat, tb, 0.05)
        place(out, hat, tb + 0.5 * BEAT, 0.07)
    return out


def build_music(total, sections, hits):
    """sections: lista de (inicio, fin, nivel) con nivel 0..3
         0 = pad suave (bajo voces), 1 = pad + arpegio, 2 = + bajo, 3 = + batería (máxima energía)
       hits: lista de instantes donde colocar un golpe de acento (cortes importantes).
    """
    n = int(total * SR) + SR
    layers = {
        "pad": pad_layer(total + 1),
        "arp": arp_layer(total + 1),
        "bass": bass_layer(total + 1),
        "drums": drums_layer(total + 1),
    }
    gains = {k: np.zeros(n) for k in layers}
    want = {0: ("pad",), 1: ("pad", "arp"), 2: ("pad", "arp", "bass"), 3: ("pad", "arp", "bass", "drums")}
    for s, e, lvl in sections:
        i0, i1 = int(s * SR), min(n, int(e * SR))
        for k in want[lvl]:
            gains[k][i0:i1] = 1.0
    out = np.zeros(n)
    for k, sig in layers.items():
        g = smooth(gains[k], 0.4)   # cambios de capa suaves (≈0,4 s)
        out[:len(sig)] += sig[:n] * g[:len(sig)]
    for h in hits:
        place(out, sfx_impact(1.6) * 0.5, h)
    return out[:int(total * SR)]
