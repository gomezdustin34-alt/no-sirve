import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from style import *

UP = "/root/.claude/uploads/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/"
SRC = {"A": UP + "7e1b8dc4-WhatsApp_Video_2026-10-12_at_7.15.57_PM.mp4",
       "B": UP + "4d314c7b-WhatsApp_Video_2026-10-12_at_7.16.07_PM.mp4",
       "C": UP + "ae8ec567-WhatsApp_Video_2026-10-12_at_7.24.37_PM.mp4",
       "D": UP + "66ceb3c5-WhatsApp_Video_2026-10-12_at_7.24.38_PM.mp4"}
OUT = sys.argv[1]
PREVIEW = len(sys.argv) > 2 and sys.argv[2] == "preview"

quad = lambda x: x * x - 6 * x + 8
cub = lambda x: x ** 3 - 3 * x ** 2 + 2 * x

# (kind, src, in, out, section, extra)
SHOTS = [
    ("intro", None, 0, 2.2, "q", {}),
    ("video", "A", 0.9, 6.0, "q", {"cards": [(3.5, "main", "Tercera función", "f(x) = x² − 6x + 8", None)], "lower": True}),
    ("video", "A", 13.7, 19.3, "q", {"cards": [(16.0, "step", "Clasificación", "Polinómica cuadrática", "Su gráfica es una parábola")]}),
    ("video", "A", 20.8, 28.6, "q", {"cards": [(26.3, "step", "Fórmula del vértice", "x = −b / 2a", "a = 1     b = −6     c = 8")]}),
    ("video", "A", 28.6, 35.0, "q", {"cards": [(31.7, "step", "Resultado", "x = −(−6) / 2(1) = 3", None)]}),
    ("video", "A", 37.5, 42.6, "q", {"cards": [(40.5, "step", "Vértice", "V(3, −1)", "f(3) = 9 − 18 + 8 = −1")]}),
    ("graph", "A", 49.8, 54.6, "q", {"scene": "qmin"}),
    ("video", "A", 55.4, 62.2, "q", {"cards": [(60.3, "step", "Factorización", "(x − 2)(x − 4)", "x² − 6x + 8 = 0")]}),
    ("graph", "A", 62.2, 67.4, "q", {"scene": "qroots"}),
    ("video", "C", 0.7, 6.36, "q", {"cards": [(5.0, "step", "Intercepto con Y", "(0, 8)", "f(0) = 0 − 0 + 8 = 8")]}),
    ("graph", "B", 1.1, 8.9, "q", {"scene": "qmono"}),
    ("video", "B", 10.5, 14.6, "c", {"cards": [(12.0, "main", "Cuarta función", "f(x) = x³ − 3x² + 2x", None)]}),
    ("video", "B", 15.8, 18.9, "c", {"cards": [(16.9, "step", "Clasificación", "Polinómica cúbica", None)]}),
    ("video", "B", 20.5, 24.5, "c", {"cards": [(22.4, "step", "Dominio y rango", "D = ℝ      R = ℝ", "Todos los números reales")]}),
    ("video", "B", 25.5, 29.9, "c", {"cards": [(28.1, "step", "Factorización", "x(x − 1)(x − 2)", None)]}),
    ("video", "B", 29.8, 37.2, "c", {"cards": [(34.4, "step", "Interceptos con X", "x = 0,   x = 1,   x = 2", None)]}),
    ("graph", "B", 39.3, 43.5, "c", {"scene": "cy"}),
    ("graph", "D", 0.4, 4.45, "c", {"scene": "cend"}),
    ("thanks", "D", 4.45, 6.25, "c", {}),
]

def _p(img, im, pos): img.paste(im, pos, im)

# ---- timeline ----
starts = []; T = 0
for s in SHOTS:
    starts.append(T); T += round((s[3] - s[2]) * FPS) / FPS
TOTAL = T
# global card events
CARDS = {"q": [], "c": []}
for s, st in zip(SHOTS, starts):
    for (ts, kind, lab, txt, sub) in s[5].get("cards", []):
        g = st + (ts - s[2])
        im, pad = make_card(lab, txt, sub=sub, accent=(AMBER if kind == "main" else VIOLET2), big=(50 if kind == "main" else 44))
        CARDS[s[4]].append((g, kind, im, pad))
SEC_START = {"q": starts[1], "c": starts[11]}
SEC_END = {"q": starts[11], "c": TOTAL}

def draw_cards(img, sec, T):
    main = [c for c in CARDS[sec] if c[1] == "main" and c[0] <= T]
    steps = [c for c in CARDS[sec] if c[1] == "step" and c[0] <= T]
    fade_out = clamp((SEC_END[sec] - T) / .3) if sec == "q" else 1
    for (t0, k, im, pad) in main:
        a = ease((T - t0) / .45) * fade_out; x = 60 - (1 - a) * 50
        _p(img, with_alpha(im, a), (int(x - pad), int(170 - pad)))
    for i, (t0, k, im, pad) in enumerate(steps):
        rs = sum(ease((T - c[0]) / .4) for c in steps[i + 1:])
        a_in = ease((T - t0 - .25) / .4); a = a_in * clamp(1 - (rs - 1)) * fade_out
        if a <= 0.01: continue
        y = 345 + 170 * rs; x = 60 - (1 - a_in) * 50
        _p(img, with_alpha(im, a), (int(x - pad), int(y - pad)))

TITLES = {"q": ("INTEGRANTE 3  ·  ALEJANDRO GÓMEZ", "Función cuadrática"),
          "c": ("INTEGRANTE 3  ·  ALEJANDRO GÓMEZ", "Función cúbica")}
def draw_header(img, sec, T, x=60):
    d = ImageDraw.Draw(img, "RGBA"); small, big = TITLES[sec]
    a = ease((T - SEC_START[sec] + .1) / .5)
    if sec == "q": a *= clamp((SEC_END[sec] - T) / .3)
    d.text((x, 60), small, font=font("sb", 16), fill=LAV + (int(220 * a),))
    d.text((x - (1 - a) * 30, 84), big, font=font("xb", 46), fill=WHITE + (int(255 * a),))
    w = font("xb", 46).getlength(big)
    d.rounded_rectangle([x, 144, x + (w * .35) * a, 149], 3, fill=PINK + (int(255 * a),))

# ---- presenter frames ----
PW, PH = 366, 600
def presenter_frames(src, t0, dur, punch):
    crop = "crop=440:721:12:8" if punch else "crop=464:760:0:0"
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t0), "-i", SRC[src], "-t", str(dur),
           "-vf", f"fps={FPS},{crop},scale={PW}:{PH}:flags=lanczos,eq=contrast=1.04:saturation=1.08", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (PW * PH * 3)
    return [Image.frombuffer("RGB", (PW, PH), raw[i * PW * PH * 3:(i + 1) * PW * PH * 3]) for i in range(n)]
PMASK = rounded_mask(PW, PH, 28)
PGLOW, PGPAD = glow_rect(PW, PH, 28, VIOLET, 22, 130)
PX, PY = W - 60 - PW, 60

def audio_seg(src, a, b, sr=48000):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", SRC[src], "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)

def level_fn(src, a, b):
    x = audio_seg(src, a, b, 16000); hop = 16000 // FPS
    r = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12) for i in range(max(1, len(x) // hop))])
    r = np.clip((20 * np.log10(r) + 45) / 30, 0, 1)
    return lambda f: float(r[min(f, len(r) - 1)])

def mic_badge(img, lvl, t):
    d = ImageDraw.Draw(img, "RGBA"); x, y = 60, 650
    d.rounded_rectangle([x, y - 4, x + 275, y + 40], 22, fill=(30, 18, 60, 220), outline=VIOLET2 + (150,), width=2)
    for i in range(5):
        h = 6 + 22 * lvl * (0.5 + 0.5 * math.sin(t * 9 + i * 1.7)) ** 2 * (1 if i % 2 else .8)
        cx = x + 22 + i * 8
        d.rounded_rectangle([cx, y + 18 - h / 2, cx + 4, y + 18 + h / 2], 2, fill=PINK + (255,))
    d.text((x + 72, y + 8), "Alejandro Gómez · narración", font=font("sb", 16), fill=WHITE + (235,))

# ---- graph scenes ----
QG = Graph((110, 200, 760, 600), (-1, 7), (-2, 9), 1, 1, xlabels=[1, 2, 3, 4, 5, 6], ylabels=[-1, 2, 4, 6, 8])
CG = Graph((110, 200, 760, 600), (-0.9, 2.9), (-1.3, 1.3), 0.5, 0.5, xlabels=[1, 2], ylabels=[-1, 1])
SC = 2

def side_panel(img, title, eq, items, t):
    d = ImageDraw.Draw(img, "RGBA"); x = 830
    a = ease(t / .4)
    d.text((x, 214), title.upper(), font=font("sb", 16), fill=LAV + (int(230 * a),))
    mtext(d, (x, 240), eq, font("db", 34), WHITE + (int(255 * a),))
    y = 310
    for (ti, txt, col, icon) in items:
        if t < ti: continue
        b = ease((t - ti) / .35)
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pill(layer, (x + (1 - b) * 30, y), txt, col, b, 19, icon)
        _p(img, layer, (0, 0)); y += 58

def graph_scene(name, t, dur, lvl):
    img = background(starts_cur + t)
    big = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
    g = QG if name.startswith("q") else CG
    f = quad if name.startswith("q") else cub
    xa, xb = (-1, 7) if g is QG else (-0.9, 2.9)
    g.draw_axes(big, ease(t / .4), SC)
    if name in ("qmin", "cy"):
        prog = ease((t - .2) / 1.6)
    else:
        prog = ease((t - .05) / .6)
    if prog > 0:
        pts = g.curve_pts(f, xa, xa + (xb - xa) * prog, 500, SC)
        draw_curve(big, pts, VIOLET2 if g is QG else CYAN, 5, g.box, SC)
    if name == "qmin":
        # arrow showing opening upward
        draw_point(big, g.px(3, -1), PINK, t - 2.4, "Mínimo  V(3, −1)", SC, "d")
    if name == "qroots":
        draw_point(big, g.px(3, -1), PINK, 9, None, SC)
        draw_point(big, g.px(2, 0), GREEN, t - 2.9, "(2, 0)", SC, "l", -40)
        draw_point(big, g.px(4, 0), GREEN, t - 3.9, "(4, 0)", SC, "r", -40)
    if name == "qmono":
        if t > 2.9:
            p = ease((t - 2.9) / 1.3)
            pts = g.curve_pts(f, -0.55, -0.55 + (3 - -0.55) * p, 300, SC)
            draw_curve(big, pts, RED, 8, g.box, SC)
        if t > 5.3:
            p = ease((t - 5.3) / 1.2)
            pts = g.curve_pts(f, 3, 3 + 3.55 * p, 300, SC)
            draw_curve(big, pts, GREEN, 8, g.box, SC)
        for (px_, c, lab, side, dy) in [((2, 0), GREEN, None, "l", 0), ((4, 0), GREEN, None, "r", 0), ((0, 8), AMBER, "(0, 8)", "r", 0), ((3, -1), PINK, "V(3, −1)", "d", 0)]:
            draw_point(big, g.px(*px_), c, 9 if lab is None else t - .3, lab, SC, side, dy)
    if name == "cy":
        for i, r in enumerate([1, 2]):
            draw_point(big, g.px(r, 0), GREEN, t - (1.2 + .3 * i), fmt(r), SC, "u", 0)
        draw_point(big, g.px(0, 0), AMBER, t - 2.6, "(0, 0)", SC, "l", -40)
    if name == "cend":
        for r in [0, 1, 2]:
            draw_point(big, g.px(r, 0), GREEN if r else AMBER, 9, None, SC)
    small = big.resize((W, H), Image.LANCZOS)
    _p(img, small, (0, 0))
    # header + side panel
    sec = "q" if g is QG else "c"
    d = ImageDraw.Draw(img, "RGBA")
    d.text((86, 60), TITLES[sec][0], font=font("sb", 16), fill=LAV + (220,))
    d.text((86, 84), TITLES[sec][1], font=font("xb", 46), fill=WHITE + (255,))
    if name == "qmin":
        side_panel(img, "Análisis", "f(x) = x² − 6x + 8", [(0.6, "Abre hacia arriba (a > 0)", VIOLET2, "↑"), (2.4, "Vértice = mínimo", PINK, "●"), (2.9, "V(3, −1)", PINK, "→")], t)
    if name == "qroots":
        side_panel(img, "Cortes con el eje X", "(x − 2)(x − 4) = 0", [(2.9, "x = 2", GREEN, "●"), (3.9, "x = 4", GREEN, "●")], t)
    if name == "qmono":
        side_panel(img, "Comportamiento", "f(x) = x² − 6x + 8", [(.5, "Continua", CYAN, "✓"), (1.7, "Sin asíntotas", CYAN, "✓"), (2.9, "Decrece en (−∞, 3)", RED, "↘"), (5.3, "Crece en (3, ∞)", GREEN, "↗")], t)
    if name == "cy":
        side_panel(img, "Cortes con los ejes", "f(x) = x³ − 3x² + 2x", [(1.2, "Eje X: 0, 1 y 2", GREEN, "●"), (2.6, "Eje Y: (0, 0)", AMBER, "●")], t)
    if name == "cend":
        side_panel(img, "Conclusión", "f(x) = x³ − 3x² + 2x", [(.3, "Dominio: ℝ   Rango: ℝ", VIOLET2, "●"), (2.3, "Continua", CYAN, "✓"), (3.0, "Sin asíntotas", CYAN, "✓")], t)
    mic_badge(img, lvl, t)
    return img

def video_scene(sec, T, pframe, t, first, punch):
    img = background(T)
    draw_header(img, sec, T)
    # presenter
    _p(img, PGLOW, (PX - PGPAD, PY - PGPAD))
    img.paste(pframe, (PX, PY), PMASK)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([PX, PY, PX + PW, PY + PH], 28, outline=(196, 181, 253, 180), width=2)
    draw_cards(img, sec, T)
    return img

def intro_scene(t):
    img = background(t); d = ImageDraw.Draw(img, "RGBA")
    a = ease(t / .6); b = ease((t - .35) / .6); out = clamp((2.2 - t) / .35)
    f1 = font("sb", 22); f2 = font("xb", 92); f3 = font("m", 30)
    s1 = "INTEGRANTE 3  ·  ALEJANDRO GÓMEZ"; s2 = "Funciones polinómicas"; s3 = "Cuadrática  ·  Cúbica"
    d.text(((W - f1.getlength(s1)) / 2, 230 - (1 - a) * 20), s1, font=f1, fill=PINK + (int(255 * a * out),))
    d.text(((W - f2.getlength(s2)) / 2, 270 + (1 - b) * 30), s2, font=f2, fill=WHITE + (int(255 * b * out),))
    w = 260 * ease((t - .6) / .6)
    d.rounded_rectangle([(W - w) / 2, 395, (W + w) / 2, 401], 3, fill=VIOLET2 + (int(255 * out),))
    c = ease((t - .8) / .6)
    d.text(((W - f3.getlength(s3)) / 2, 425 + (1 - c) * 15), s3, font=f3, fill=LAV + (int(255 * c * out),))
    return img

def thanks_scene(t, dur, lvl):
    img = background(starts_cur + t); d = ImageDraw.Draw(img, "RGBA")
    a = ease_back(t / .6); f = font("xb", int(40 + 60 * clamp(a, 0, 1.2)))
    s = "¡Muchas gracias!"
    al = int(255 * clamp(t / .4))
    d.text(((W - f.getlength(s)) / 2, 290), s, font=f, fill=WHITE + (al,))
    s2 = "Alejandro Gómez  ·  Integrante 3"; f2 = font("m", 26)
    d.text(((W - f2.getlength(s2)) / 2, 420), s2, font=f2, fill=LAV + (int(al * ease((t - .4) / .5)),))
    for i in range(14):
        ang = i / 14 * 2 * math.pi; r = 220 + 160 * ease(t / 1.2)
        x = W / 2 + r * math.cos(ang) * 1.6; y = 340 + r * math.sin(ang) * .8
        rr = 4 * (1 - clamp(t / 1.8)) + 1
        c = [VIOLET2, PINK, CYAN][i % 3]
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c + (int(200 * (1 - clamp(t / 1.8))),))
    fade = clamp((dur - t) / .5)
    if fade < 1:
        img = Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, fade)
    return img

# ---- main ----
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
audio = []
prev_last = None; vid_count = 0
only = None
if PREVIEW: only = set(int(x) for x in sys.argv[3].split(","))
for idx, (s, st) in enumerate(zip(SHOTS, starts)):
    kind, src, a, b, sec, ex = s
    n = round((b - a) * FPS); dur = n / FPS
    starts_cur = st
    if kind == "intro": audio.append(np.zeros(int(round(dur * 48000)), np.float32))
    else:
        seg = audio_seg(src, a, a + dur); need = int(round(dur * 48000))
        seg = np.pad(seg, (0, max(0, need - len(seg))))[:need].copy()
        fl = 480; ramp = np.linspace(0, 1, fl, dtype=np.float32); seg[:fl] *= ramp; seg[-fl:] *= ramp[::-1]
        audio.append(seg)
    if only is not None and idx not in only: continue
    frames = None; lvl = None
    if kind == "video":
        punch = vid_count % 2 == 1; vid_count += 1
        frames = presenter_frames(src, a, dur, punch)
    if kind in ("graph", "thanks"): lvl = level_fn(src, a, a + dur)
    last = None
    for i in range(n):
        t = i / FPS; T = st + t
        if kind == "intro": img = intro_scene(t)
        elif kind == "video": img = video_scene(sec, T, frames[min(i, len(frames) - 1)], t, i == 0, None)
        elif kind == "graph": img = graph_scene(ex["scene"], t, dur, lvl(i))
        else: img = thanks_scene(t, dur, lvl(i))
        img = img.convert("RGB")
        if prev_last is not None and i < 8 and not (kind == "video" and SHOTS[idx - 1][0] == "video"):
            img = Image.blend(prev_last, img, (i + 1) / 9)
        elif prev_last is not None and i < 4:
            img = Image.blend(prev_last, img, (i + 1) / 5)
        enc.stdin.write(img.tobytes()); last = img
        if PREVIEW and i in (n // 2,): img.save(f"{OUT}.shot{idx}.png")
    prev_last = last
    print("shot", idx, kind, f"{dur:.2f}s", flush=True)
enc.stdin.close(); enc.wait()
au = np.concatenate(audio)
import wave
with wave.open(OUT + ".audio.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
    w.writeframes((np.clip(au, -1, 1) * 32767).astype(np.int16).tobytes())
print("total", TOTAL)
