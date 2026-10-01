"""Pista musical sintetizada para el montaje rápido "Todo lo que se vivió".

150 BPM -> una semicorchea dura exactamente 0.1 s (3 fotogramas a 30 fps),
así cada corte del montaje cae sobre un golpe de la música.

Estructura (1 compás = 1.6 s):
  c1-c2  bombo + hats suaves + bajo + pad        (arranque)
  c3-c4  + palmas, hats en semicorcheas, arpegio  (sube la energía)
  c5     + hats abiertos, empieza el riser
  c6     redoble de caja 8vos -> 16vos, riser     (build)
  c7     DROP: crash, sub, todo a tope            (ráfaga final)
  11.2s  corte en seco a silencio
  11.6s  piano suave con mucha reverb bajo el texto final
"""
import wave

import numpy as np

SR = 44100
BPM = 150
BEAT = 60 / BPM          # 0.4 s
SIXTEENTH = BEAT / 4     # 0.1 s
BAR = BEAT * 4           # 1.6 s

rng = np.random.default_rng(7)


def note_hz(n):
    """MIDI -> Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def env_exp(n, decay):
    t = np.arange(n) / SR
    return np.exp(-t / decay)


def onepole_lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def hp(x):
    return np.diff(x, prepend=0.0)


def add(buf, sig, t0):
    i = int(round(t0 * SR))
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig


def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    ph = (t * freq * (1 + detune)) % 1.0
    return 2 * ph - 1


# ---------- instrumentos ----------
def kick(gain=1.0):
    n = int(0.38 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = rng.standard_normal(n) * np.exp(-t * 400) * 0.25
    return gain * (body + click)


def clap(gain=1.0, decay=0.13):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    noise = hp(rng.standard_normal(n))
    env = np.exp(-t / decay)
    # tres micro-golpes al inicio, típico de palmas
    for d in (0.0, 0.011, 0.022):
        env += np.where((t >= d) & (t < d + 0.01), np.exp(-(t - d) * 300), 0)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return gain * (noise * env * 0.5 + tone)


def hat(gain=1.0, decay=0.025):
    n = int(max(0.06, decay * 6) * SR)
    x = hp(hp(rng.standard_normal(n)))
    return gain * x * env_exp(n, decay) * 0.35


def crash(gain=1.0):
    n = int(2.2 * SR)
    x = hp(hp(rng.standard_normal(n)))
    return gain * x * env_exp(n, 0.55) * 0.35


def sub_drop(gain=1.0):
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    f = 40 + 60 * np.exp(-t * 6)
    return gain * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)


def whoosh(length, gain=1.0):
    """Ruido que crece hasta el corte (para los whip transitions)."""
    n = int(length * SR)
    x = hp(rng.standard_normal(n))
    env = np.linspace(0, 1, n) ** 2
    return gain * x * env * 0.25


def pluck(freq, gain=1.0, decay=0.18):
    n = int(decay * 5 * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)
         + 0.15 * np.sin(6 * np.pi * freq * t))
    return gain * s * np.exp(-t / decay) * np.minimum(1, t * 800)


def piano(freq, gain=1.0, length=4.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in enumerate((1.0, 0.45, 0.22, 0.12, 0.06), start=1):
        s += a * np.sin(2 * np.pi * freq * k * t * (1 + 0.0004 * k)) * np.exp(-t * (0.9 + 0.6 * k))
    return gain * s * np.minimum(1, t * 300)


def pad_chord(notes, length, gain=1.0):
    n = int(length * SR)
    s = np.zeros(n)
    for m in notes:
        f = note_hz(m)
        for d in (-0.004, 0.0, 0.005):
            s += saw(f, n, d)
    s = onepole_lp(s / (3 * len(notes)), 1400)
    att = np.minimum(1, np.arange(n) / (0.15 * SR))
    rel = np.minimum(1, (n - np.arange(n)) / (0.05 * SR))
    return gain * s * att * rel


def bass_note(m, length, gain=1.0):
    n = int(length * SR)
    s = saw(note_hz(m), n) * 0.6 + np.sin(2 * np.pi * note_hz(m) * np.arange(n) / SR)
    s = onepole_lp(s, 420)
    t = np.arange(n) / SR
    return gain * s * np.exp(-t * 4) * np.minimum(1, t * 500)


def reverb(x, seconds=1.8, mix=0.3, seed=1):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * (6.9 / seconds))
    ir = onepole_lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    size = len(x) + n
    nfft = 1 << (size - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return x * (1 - mix) + wet * mix


# ---------- composición ----------
CHORDS = {  # (raíz del bajo, notas del pad)
    "Am": (45, [57, 60, 64, 67]),
    "F": (41, [53, 57, 60, 64]),
    "C": (48, [55, 60, 64, 67]),
    "G": (43, [55, 59, 62, 67]),
}
PROGRESSION = ["Am", "F", "C", "G", "Am", "F", "Am"]  # c6 cambia a G a mitad


def render(cuts, whip_cuts, drop_time, end_music, total, slowmo_spans=()):
    """cuts: tiempos (s) de cada corte. whip_cuts: cortes con whoosh.
    drop_time: inicio de la ráfaga final. end_music: corte a silencio."""
    n = int(total * SR) + SR
    drums = np.zeros(n)
    music = np.zeros(n)
    fx = np.zeros(n)

    bars = int(round(end_music / BAR))
    for b in range(bars):
        t0 = b * BAR
        name = PROGRESSION[b] if b < len(PROGRESSION) else "Am"
        root, pad = CHORDS[name]
        is_build = b == bars - 2
        is_drop = b == bars - 1
        energy = min(1.0, 0.45 + 0.1 * b)

        # bombo: negras; en el build se duplica en la última negra
        for beat in range(4):
            drums_gain = 1.0 if not is_build else 0.9
            add(drums, kick(drums_gain), t0 + beat * BEAT)
        if is_build:
            add(drums, kick(0.8), t0 + 3.5 * BEAT)

        # palmas en 2 y 4 desde c3
        if b >= 2 and not is_build:
            for beat in (1, 3):
                add(drums, clap(0.55 + 0.1 * is_drop), t0 + beat * BEAT)

        # hats
        step = 2 if b < 2 else 1
        for s in range(0, 16, step):
            acc = 1.0 if s % 4 == 2 else 0.6
            add(drums, hat(acc * (0.35 + 0.08 * b)), t0 + s * SIXTEENTH)
        if b >= 4:
            for beat in range(4):
                add(drums, hat(0.45, decay=0.12), t0 + beat * BEAT + BEAT / 2)

        # redoble del build: 8vos la 1a mitad, 16vos la 2a, crescendo
        if is_build:
            for s in range(16):
                if s < 8 and s % 2:
                    continue
                g = 0.2 + 0.6 * s / 15
                add(drums, clap(g, decay=0.06), t0 + s * SIXTEENTH)

        # bajo en corcheas (en el build sube a G a mitad de compás)
        for e in range(8):
            r = root if not (is_build and e >= 4) else CHORDS["G"][0]
            add(music, bass_note(r, BEAT / 2, 0.55), t0 + e * BEAT / 2)

        # pad (sidechain manual: se agacha en cada negra)
        chord_len = BAR if not is_build else BAR / 2
        add(music, pad_chord(pad, chord_len, 0.32 * energy), t0)
        if is_build:
            add(music, pad_chord(CHORDS["G"][1], BAR / 2, 0.4), t0 + BAR / 2)

        # arpegio en semicorcheas desde c3
        if b >= 2:
            seq = pad + [p + 12 for p in pad]
            for s in range(16):
                m = seq[(s * 3) % len(seq)] + 12
                add(music, pluck(note_hz(m), 0.10 + 0.05 * (b >= 4) + 0.05 * is_drop), t0 + s * SIXTEENTH)

    # riser desde c5 hasta el drop
    riser_start = drop_time - 2 * BAR
    rn = int((drop_time - riser_start) * SR)
    t = np.arange(rn) / SR
    prog = t / t[-1]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * prog ** 2) / SR) * 0.08 * prog ** 2
    noise = hp(rng.standard_normal(rn)) * 0.18 * prog ** 3
    add(fx, sweep + noise, riser_start)

    # drop: crash + sub + palmas fuertes
    add(drums, crash(1.0), drop_time)
    add(drums, sub_drop(0.9), drop_time)

    # acento en cada corte -> el corte se "siente" en el golpe
    for c in cuts:
        if c >= end_music - 1e-6:
            continue
        g = 0.35 if c < drop_time else 0.6
        add(drums, kick(g) * 0.6, c)
        add(drums, hat(g * 0.8, decay=0.015), c)
    for c in whip_cuts:
        add(fx, whoosh(0.18, 0.9), c - 0.18)
    # en la cámara lenta: barrido de reverse-cymbal hacia el siguiente corte
    for (a, b_) in slowmo_spans:
        add(fx, whoosh(b_ - a, 0.7) * 0.8, a)

    # sidechain sencillo en la música
    side = np.ones(n)
    for k in np.arange(0, end_music, BEAT):
        i = int(k * SR)
        m = int(0.18 * SR)
        side[i:i + m] *= 1 - 0.55 * np.exp(-np.arange(min(m, n - i)) / SR / 0.06)
    music *= side

    left = reverb(music, 1.6, 0.22, 1) + drums + reverb(fx, 1.2, 0.3, 3)
    right = reverb(music, 1.6, 0.22, 2) + drums + reverb(fx, 1.2, 0.3, 4)

    # CORTE EN SECO a silencio (incluida la cola de reverb)
    cut_i = int(end_music * SR)
    left[cut_i:] = 0
    right[cut_i:] = 0

    # final: piano suave con reverb larga, 0.4 s después del silencio
    tail = np.zeros(n)
    t_piano = end_music + 0.4
    for k, m in enumerate([45, 52, 57, 60, 64, 71]):  # Am9
        add(tail, piano(note_hz(m), 0.16, length=total - t_piano - 0.05), t_piano + k * 0.07)
    tl = reverb(tail, 3.0, 0.45, 5)
    tr = reverb(tail, 3.0, 0.45, 6)
    fade_n = int(1.2 * SR)
    end_i = int(total * SR)
    for ch in (tl, tr):
        ch[end_i - fade_n:end_i] *= np.linspace(1, 0, fade_n)
        ch[end_i:] = 0
    tail_i = int(t_piano * SR)
    left[tail_i:] += tl[tail_i:]
    right[tail_i:] += tr[tail_i:]

    st = np.stack([left, right], axis=1)[: int(total * SR)]
    st = np.tanh(st * 1.2)
    st /= np.max(np.abs(st)) / 0.89
    return st


def write_wav(path, stereo):
    data = (stereo * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
