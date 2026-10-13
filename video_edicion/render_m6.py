import sys, math, subprocess, numpy as np, wave
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from style import *

SRC = "/root/.claude/uploads/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/8ee5d282-WhatsApp_Video_2026-10-12_at_8.13.22_PM.mp4"
OUT = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
T0, T1 = 0.0, 59.8
DUR = round((T1 - T0) * FPS) / FPS
SC = 2
def _p(img, im, pos): img.paste(im, pos, im)

SECS = [(0.0, 24.6, "Función exponencial"), (24.6, 43.6, "Función exponencial"), (43.6, 999, "Función logarítmica")]
EVENTS = [
    (6.0, 0, "main", "Primera función", "f(x) = 2ˣ − 1", "Exponencial"),
    (15.6, 0, "step", "Dominio", "D = ℝ", None),
    (17.6, 0, "step", "Rango", "y > −1", "Valores mayores que −1"),
    (21.4, 0, "step", "Asíntota horizontal", "y = −1", None),
    (26.0, 1, "main", "Segunda función", "f(x) = e⁻ˣ", "Exponencial"),
    (36.4, 1, "step", "Dominio", "D = ℝ", None),
    (37.8, 1, "step", "Rango", "y > 0", "Solo valores positivos"),
    (40.6, 1, "step", "Asíntota horizontal", "y = 0", None),
    (45.6, 2, "main", "Tercera función", "f(x) = log(x + 1)", "Logarítmica"),
    (51.0, 2, "step", "Dominio", "x > −1", "x + 1 > 0"),
    (53.2, 2, "step", "Rango", "R = ℝ", None),
    (55.4, 2, "step", "Asíntota vertical", "x = −1", None),
]
CARDS = []
for (ts, sec, kind, lab, txt, sub) in EVENTS:
    im, pad = make_card(lab, txt, sub=sub, accent=(AMBER if kind == "main" else VIOLET2), big=(50 if kind == "main" else 44))
    CARDS.append((ts - T0, sec, kind, im, pad))

# graph scenes (start, end, name)
GS = [(9.8, 14.8, "exp1"), (29.4, 34.8, "exp2"), (47.4, 50.9, "log")]
GA = Graph((110, 200, 760, 600), (-3, 3.5), (-2, 7), 1, 1, xlabels=[-2, -1, 1, 2, 3], ylabels=[-1, 1, 3, 5])
GB = Graph((110, 200, 760, 600), (-2, 4), (-1, 7), 1, 1, xlabels=[-1, 1, 2, 3], ylabels=[1, 3, 5])
GC = Graph((110, 200, 760, 600), (-1.6, 9), (-1.6, 1.4), 1, .5, xlabels=[-1, 1, 3, 5, 7, 9], ylabels=[-1, 1])

def draw_cards(img, T):
    for si, (sa, sb, _) in enumerate(SECS):
        if not (sa - .01 <= T < sb + .01): continue
        fo = clamp((sb - T) / .3)
        main = [c for c in CARDS if c[1] == si and c[2] == "main" and c[0] <= T]
        steps = [c for c in CARDS if c[1] == si and c[2] == "step" and c[0] <= T]
        for (t0, _, k, im, pad) in main:
            a = ease((T - t0) / .45) * fo
            _p(img, with_alpha(im, a), (int(60 - (1 - a) * 50 - pad), int(146 - pad)))
        for i, (t0, _, k, im, pad) in enumerate(steps):
            rs = sum(ease((T - c[0]) / .4) for c in steps[i + 1:])
            a_in = ease((T - t0 - .25) / .4); a = a_in * clamp(1 - (rs - 1)) * fo
            if a <= .01: continue
            _p(img, with_alpha(im, a), (int(60 - (1 - a_in) * 50 - pad), int(345 + 170 * rs - pad)))

def draw_header(img, T, y0=38):
    d = ImageDraw.Draw(img, "RGBA")
    for sa, sb, name in SECS:
        if not (sa <= T < sb): continue
        a = ease((T - sa + .1) / .5) * clamp((sb - T) / .3)
        d.text((60, y0), "INTEGRANTE 6  ·  ISABELLA BOBADILLA", font=font("sb", 16), fill=LAV + (int(220 * a),))
        d.text((60 - (1 - a) * 30, y0 + 22), name, font=font("xb", 46), fill=WHITE + (int(255 * a),))
        w = font("xb", 46).getlength(name)
        d.rounded_rectangle([60, y0 + 82, 60 + w * .35 * a, y0 + 87], 3, fill=PINK + (int(255 * a),))

def dashed(d, p0, p1, col, w, dash=14, gap=10):
    x0, y0 = p0; x1, y1 = p1; L = math.hypot(x1 - x0, y1 - y0); n = int(L // (dash + gap)) + 1
    for i in range(n):
        s = i * (dash + gap) / L; e = min(1, (i * (dash + gap) + dash) / L)
        d.line([(x0 + (x1 - x0) * s, y0 + (y1 - y0) * s), (x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)], fill=col, width=w)

def side_panel(img, title, eq, items, t):
    d = ImageDraw.Draw(img, "RGBA"); x = 830; a = ease(t / .4)
    d.text((x, 214), title.upper(), font=font("sb", 16), fill=LAV + (int(230 * a),))
    mtext(d, (x, 240), eq, font("db", 34), WHITE + (int(255 * a),))
    y = 310
    for (ti, txt, col, icon) in items:
        if t < ti: continue
        b = ease((t - ti) / .35); layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pill(layer, (x + (1 - b) * 30, y), txt, col, b, 19, icon); _p(img, layer, (0, 0)); y += 58

def graph_frame(T, name, t):
    img = background(T + 150)
    g, f, col, asym, eq, items = {
        "exp1": (GA, lambda x: 2 ** x - 1, VIOLET2, ("h", -1), "f(x) = 2ˣ − 1", [(.6, "Creciente (base 2 > 1)", GREEN, "↗"), (2.2, "Asíntota y = −1", AMBER, "–")]),
        "exp2": (GB, lambda x: math.exp(-x), CYAN, ("h", 0), "f(x) = e⁻ˣ", [(.6, "Decreciente", RED, "↘"), (2.2, "Asíntota y = 0", AMBER, "–")]),
        "log": (GC, lambda x: math.log10(x + 1) if x > -1 else float("nan"), PINK, ("v", -1), "f(x) = log(x + 1)", [(.6, "Creciente", GREEN, "↗"), (1.8, "Asíntota x = −1", AMBER, "–")]),
    }[name]
    big = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
    g.draw_axes(big, ease(t / .4), SC)
    at = ease((t - (2.2 if name != "log" else 1.8)) / .5)
    if at > 0:
        d = ImageDraw.Draw(big, "RGBA")
        if asym[0] == "h":
            y = g.px(0, asym[1])[1] * SC; dashed(d, (g.box[0] * SC, y), (g.box[0] * SC + (g.box[2] - g.box[0]) * SC * at, y), AMBER + (230,), 3 * SC, 14 * SC, 10 * SC)
        else:
            x = g.px(asym[1], 0)[0] * SC; dashed(d, (x, g.box[3] * SC), (x, g.box[3] * SC - (g.box[3] - g.box[1]) * SC * at), AMBER + (230,), 3 * SC, 14 * SC, 10 * SC)
    p = ease((t - .2) / 1.6)
    if p > 0:
        xa = g.xr[0] if name != "log" else -0.9995
        draw_curve(big, g.curve_pts(f, xa, xa + (g.xr[1] - xa) * p, 600, SC), col, 5, g.box, SC)
    _p(img, big.resize((W, H), Image.LANCZOS), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((86, 60), "INTEGRANTE 6  ·  ISABELLA BOBADILLA", font=font("sb", 16), fill=LAV + (220,))
    d.text((86, 84), "Función logarítmica" if name == "log" else "Función exponencial", font=font("xb", 46), fill=WHITE + (255,))
    side_panel(img, "Gráfica", eq, items, t)
    return img

PW, PH = 366, 600
PMASK = rounded_mask(PW, PH, 28); PGLOW, PGPAD = glow_rect(PW, PH, 28, VIOLET, 22, 130)
PX, PY = W - 60 - PW, 60
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-t", str(DUR), "-vf",
       f"fps={FPS},crop=576:944:0:40,scale={PW}:{PH}:flags=lanczos,eq=contrast=1.05:saturation=1.08:brightness=0.02", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
if not PREVIEW:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
n = round(DUR * FPS); last = None; prev = None; mode_prev = None; hold = None; k = 99
for i in range(n):
    raw = dec.stdout.read(PW * PH * 3)
    T = i / FPS
    gs = next((g for g in GS if g[0] <= T < g[1]), None)
    # keep the last real face frame for graph-scene spans (inserted screenshots replaced)
    if len(raw) == PW * PH * 3 and gs is None: last = Image.frombuffer("RGB", (PW, PH), raw)
    mode = gs[2] if gs else "video"
    if mode != mode_prev: hold = prev; k = 0
    mode_prev = mode
    if PREVIEW and not any(abs(T - p) < .5 / FPS for p in PREVIEW): k += 1; continue
    if gs: img = graph_frame(T, gs[2], T - gs[0])
    else:
        img = background(T + 150); draw_header(img, T)
        _p(img, PGLOW, (PX - PGPAD, PY - PGPAD)); img.paste(last, (PX, PY), PMASK)
        ImageDraw.Draw(img, "RGBA").rounded_rectangle([PX, PY, PX + PW, PY + PH], 28, outline=(196, 181, 253, 180), width=2)
        draw_cards(img, T)
    img = img.convert("RGB")
    if hold is not None and k < 9: img = Image.blend(hold, img, (k + 1) / 10)
    k += 1
    if PREVIEW: img.save(f"{OUT}.{T:.1f}.png")
    else: enc.stdin.write(img.tobytes())
    prev = img
dec.stdout.close()
if not PREVIEW:
    enc.stdin.close(); enc.wait()
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-t", str(DUR), "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    need = int(round(DUR * 48000)); a = np.pad(a, (0, max(0, need - len(a))))[:need].copy()
    r = np.linspace(0, 1, 2400, dtype=np.float32); a[:2400] *= r; a[-4800:] *= np.linspace(1, 0, 4800, dtype=np.float32)
    with wave.open(OUT + ".audio.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
print("done", DUR)
