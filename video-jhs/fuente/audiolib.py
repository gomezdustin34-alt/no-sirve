import numpy as np
from scipy import signal

SR = 44100
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.ones(n) * s
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a, endpoint=False)
    dd = min(d, n - a)
    e[a:a + dd] = np.linspace(1, s, dd, endpoint=False)
    if r > 0 and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def reverb(x, seconds=1.8, mix=0.25, seed=3):
    n = int(seconds * SR)
    g = np.random.default_rng(seed)
    t = np.arange(n) / SR
    irL = g.standard_normal(n) * np.exp(-t * 6.9 / seconds)
    irR = g.standard_normal(n) * np.exp(-t * 6.9 / seconds)
    # darken IR
    b, a = signal.butter(1, 5000 / (SR / 2))
    irL = signal.lfilter(b, a, irL); irR = signal.lfilter(b, a, irR)
    irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))
    mono = x if x.ndim == 1 else x.mean(axis=1)
    wl = signal.fftconvolve(mono, irL)[:len(mono)]
    wr = signal.fftconvolve(mono, irR)[:len(mono)]
    dry = x if x.ndim == 2 else np.stack([x, x], 1)
    return dry * (1 - mix) + np.stack([wl, wr], 1) * mix * 0.6


def kick(sr=SR):
    n = int(0.32 * sr); t = np.arange(n) / sr
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / sr
    return np.sin(ph) * np.exp(-t * 9) * 0.9


def hat(sr=SR, dec=40):
    n = int(0.08 * sr); t = np.arange(n) / sr
    x = rng.standard_normal(n)
    b, a = signal.butter(2, 7000 / (sr / 2), 'high')
    return signal.lfilter(b, a, x) * np.exp(-t * dec) * 0.25


def snap(sr=SR):
    n = int(0.18 * sr); t = np.arange(n) / sr
    x = rng.standard_normal(n)
    b, a = signal.butter(2, [1200 / (sr / 2), 5000 / (sr / 2)], 'band')
    return signal.lfilter(b, a, x) * np.exp(-t * 22) * 0.5


def bell(freq, dur=1.2, sr=SR, idx=2.2):
    n = int(dur * sr); t = np.arange(n) / sr
    mod = np.sin(2 * np.pi * freq * 3.5 * t) * idx * np.exp(-t * 6)
    return np.sin(2 * np.pi * freq * t + mod) * np.exp(-t * 3.2) * env_adsr(n, 0.003, 0, 1, 0.05)


def pad_note(freq, dur, sr=SR):
    n = int(dur * sr); t = np.arange(n) / sr
    x = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        f = freq * 2 ** (det / 12)
        for h, amp in ((1, 1), (2, 0.35), (3, 0.18), (4, 0.08)):
            x += amp * np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28))
    return x * env_adsr(n, 0.25, 0.4, 0.75, 0.4) / 3


def music(length, bpm=108):
    beat = 60 / bpm; bar = beat * 4
    n = int(length * SR) + SR * 3
    drums = np.zeros(n); pad = np.zeros(n); bass = np.zeros(n); bells = np.zeros(n)
    side = np.ones(n)
    prog = [  # root, chord tones (midi)
        (45, [57, 60, 64, 67, 71]),   # Am9
        (41, [57, 60, 64, 65, 69]),   # Fmaj7
        (48, [55, 60, 64, 67, 71]),   # Cmaj7
        (43, [55, 59, 62, 64, 67]),   # G6
    ]
    nbars = int(np.ceil(length / bar)) + 1
    K, H, Hs, Sn = kick(), hat(), hat(dec=70), snap()

    def add(buf, x, t0, g=1.0):
        i = int(t0 * SR)
        if i >= len(buf): return
        m = min(len(x), len(buf) - i)
        buf[i:i + m] += x[:m] * g

    last_full = length - bar * 1.0
    for b in range(nbars):
        t0 = b * bar
        root, tones = prog[b % 4]
        intro = t0 < bar * 2
        outro = t0 >= last_full
        # pad chord
        for nn in tones[:4]:
            add(pad, pad_note(midi(nn), bar + 0.4), t0, 0.16)
        # bass
        if not intro:
            for off, d in ((0, 0.9), (1.5, 0.4), (2, 0.9), (3.5, 0.4)):
                nb = int(d * beat * SR); tt = np.arange(nb) / SR
                f = midi(root)
                x = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * env_adsr(nb, 0.01, 0.1, 0.8, 0.05)
                add(bass, x, t0 + off * beat, 0.32 if not outro else 0.0)
        # drums
        for k in range(4):
            tb = t0 + k * beat
            if not intro and not outro:
                add(drums, K, tb, 0.85)
                i = int(tb * SR); m = min(int(0.35 * SR), n - i)
                if m > 0:
                    side[i:i + m] = np.minimum(side[i:i + m], 1 - 0.45 * np.exp(-np.arange(m) / SR * 9))
                add(drums, H, tb + beat / 2, 0.7)
                add(drums, Hs, tb + beat / 4, 0.25); add(drums, Hs, tb + 3 * beat / 4, 0.25)
                if k in (1, 3):
                    add(drums, Sn, tb, 0.45)
            elif intro and b == 1:
                add(drums, Hs, tb, 0.3); add(drums, Hs, tb + beat / 2, 0.3)
        # bell arpeggio (sparkle) - 8ths, pattern
        pat = [0, 2, 4, 2, 3, 2, 4, 1]
        for k, p in enumerate(pat):
            if outro and k > 0: break
            add(bells, bell(midi(tones[p] + 12), 0.9), t0 + k * beat / 2, 0.11 if k % 2 == 0 else 0.07)
    pad = pad * side
    # gentle lowpass on pad
    b_, a_ = signal.butter(2, 2600 / (SR / 2)); pad = signal.lfilter(b_, a_, pad)
    wet = reverb(pad * 0.9 + bells, 2.2, 0.35)
    mix = wet + np.stack([drums + bass * side, drums + bass * side], 1)
    # stereo width for hats (tiny delay)
    mix[:, 1] = np.roll(mix[:, 1], 30) * 0.98 + mix[:, 1] * 0.02
    mix = mix[:int(length * SR)]
    # fades
    fi = int(0.8 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(1.8 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix /= np.max(np.abs(mix)) + 1e-9
    return mix * 0.9


# ---------------- SFX ----------------
def whoosh(dur=0.55):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n)
    # sweep bandpass by chunks
    ch = 512
    for i in range(0, n, ch):
        fc = 400 + 3800 * np.sin(np.pi * i / n) ** 2
        b, a = signal.butter(2, [fc * 0.6 / (SR / 2), min(fc * 1.6, 20000) / (SR / 2)], 'band')
        seg = x[max(0, i - 2048):i + ch]
        y = signal.lfilter(b, a, seg)[-min(ch, n - i):]
        out[i:i + len(y)] = y
    e = np.sin(np.pi * t / dur) ** 2
    y = out * e
    return np.stack([y * (1 - t / dur * 0.6), y * (0.4 + t / dur * 0.6)], 1) * 0.9 / (np.max(np.abs(y)) + 1e-9)


def pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 220
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
    return np.stack([y, y], 1) * 0.8


def click():
    n = int(0.03 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 2400 * t) * 0.6 + rng.standard_normal(n) * 0.3) * np.exp(-t * 220)
    return np.stack([y, y], 1) * 0.7


def beep():
    out = []
    for f, d in ((1318.5, 0.09), (0, 0.04), (1975.5, 0.14)):
        n = int(d * SR); t = np.arange(n) / SR
        y = np.sin(2 * np.pi * f * t) * env_adsr(n, 0.005, 0.02, 0.8, 0.02) if f else np.zeros(n)
        out.append(y)
    y = np.concatenate(out) * 0.45
    return reverb(y, 0.6, 0.2)


def chime():
    notes = [72, 76, 79, 84, 88]
    n = int(2.6 * SR); y = np.zeros(n)
    for k, nn in enumerate(notes):
        b = bell(midi(nn), 2.0, idx=1.6); i = int(k * 0.085 * SR)
        y[i:i + len(b)] += b[:n - i] * 0.35
    return reverb(y, 2.0, 0.35)


def ding():
    y = bell(midi(84), 1.4, idx=1.4) * 0.45 + bell(midi(91), 1.4, idx=1.0) * 0.2
    return reverb(y, 1.2, 0.3)


def ticks():
    n = int(0.5 * SR); y = np.zeros(n)
    for k in range(3):
        c = click()[:, 0]; i = int(k * 0.12 * SR); y[i:i + len(c)] += c * 0.6
    return np.stack([y, y], 1)
