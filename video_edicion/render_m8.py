import sys, math, subprocess, numpy as np, wave
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from style import *

SRC = "/root/.claude/uploads/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/56048a2b-WhatsApp_Video_2026-10-12_at_6.43.32_PM.mp4"
OUT = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
T0, T1 = 0.0, 81.1
DUR = round((T1 - T0) * FPS) / FPS
SC = 2
def _p(img, im, pos): img.paste(im, pos, im)
TAG = "INTEGRANTE 8  ·  FUNCIONES RESTANTES Y CONCLUSIÓN"

SECS = [(0.0, 20.0, "Trigonométrica inversa"), (20.0, 38.6, "Función parte entera"), (38.6, 55.0, "Función a trozos"), (55.0, 999, "Conclusión")]
EVENTS = [
    (3.9, 0, "main", "Función", "f(x) = arctan(x)", "Trigonométrica inversa"),
    (8.6, 0, "step", "Dominio", "D = ℝ", "Todos los números reales"),
    (23.5, 1, "main", "Función", "f(x) = ⌊x + 3⌋", "Parte entera"),
    (25.2, 1, "step", "Regla", "Entero menor o igual", "Asigna a cada número el entero ≤ más cercano"),
    (41.0, 2, "main", "Primera parte", "f(x) = x²   si  x < 0", None),
    (43.6, 2, "step", "Segunda parte", "f(x) = 2x + 1   si  x ≥ 0", None),
    (55.8, 3, "main", "Conclusión", "Análisis de funciones", "Comprender modelos matemáticos"),
    (64.2, 3, "step", "Características", "Dominio · Rango · Gráfica", "Clasificación y comportamiento"),
    (72.2, 3, "step", "Herramientas", "GeoGebra", "Visualizar y comprobar los resultados"),
]
CARDS = []
for (ts, sec, kind, lab, txt, sub) in EVENTS:
    im, pad = make_card(lab, txt, sub=sub, accent=(AMBER if kind == "main" else VIOLET2), big=(48 if kind == "main" else 42))
    CARDS.append((ts - T0, sec, kind, im, pad))

GS = [(10.0, 18.6, "atan"), (28.0, 37.8, "floor"), (45.0, 54.4, "trozos"), (78.6, 99, "thanks")]
GA = Graph((110, 200, 760, 600), (-6, 6), (-2.2, 2.2), 1, .5, xlabels=[-4, -2, 2, 4], ylabels=[-1, 1])
GF = Graph((110, 200, 760, 600), (-5, 2), (-2.5, 5.5), 1, 1, xlabels=[-4, -3, -2, -1, 1], ylabels=[-2, -1, 1, 2, 3, 4, 5])
GT = Graph((110, 200, 760, 600), (-2.5, 3), (-1, 7), 1, 1, xlabels=[-2, -1, 1, 2, 3], ylabels=[1, 2, 4, 6])

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
        d.text((60, y0), TAG, font=font("sb", 16), fill=LAV + (int(220 * a),))
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

def dot(d, xy, col, filled, sc):
    X, Y = xy[0] * sc, xy[1] * sc; r = 7 * sc
    d.ellipse([X - r, Y - r, X + r, Y + r], fill=(col + (255,)) if filled else (20, 10, 45, 255), outline=col + (255,), width=3 * sc)

def graph_frame(T, name, t):
    img = background(T + 190)
    big = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
    if name == "atan":
        g = GA; g.draw_axes(big, ease(t / .4), SC)
        at = ease((t - 1.6) / .6); d = ImageDraw.Draw(big, "RGBA")
        for yv in (math.pi / 2, -math.pi / 2):
            if at > 0:
                y = g.px(0, yv)[1] * SC
                dashed(d, (g.box[0] * SC, y), (g.box[0] * SC + (g.box[2] - g.box[0]) * SC * at, y), AMBER + (230,), 3 * SC, 14 * SC, 10 * SC)
        if at > .5:
            for yv, s in ((math.pi / 2, "π/2"), (-math.pi / 2, "−π/2")):
                X, Y = g.px(g.xr[0], yv); d.text(((X + 8) * SC, (Y - (28 if yv > 0 else -6)) * SC), s, font=font("b", 20 * SC), fill=AMBER + (255,))
        p = ease((t - .2) / 1.6)
        if p > 0: draw_curve(big, g.curve_pts(math.atan, g.xr[0], g.xr[0] + (g.xr[1] - g.xr[0]) * p, 500, SC), CYAN, 5, g.box, SC)
        title, eq, items = "Trigonométrica inversa", "f(x) = arctan(x)", [(1.6, "Rango: (−π/2, π/2)", AMBER, "●"), (5.2, "Creciente", GREEN, "↗"), (6.6, "Continua", CYAN, "✓")]
    elif name == "floor":
        g = GF; g.draw_axes(big, ease(t / .4), SC); d = ImageDraw.Draw(big, "RGBA")
        steps = list(range(-5, 2)); n = len(steps)
        for k, a in enumerate(steps):
            tk = t - (.3 + k * .35)
            if tk < 0: continue
            yv = a + 3; x0, y = g.px(a, yv); x1, _ = g.px(a + 1, yv)
            pe = ease(tk / .3)
            d.line([(x0 * SC, y * SC), ((x0 + (x1 - x0) * pe) * SC, y * SC)], fill=VIOLET2 + (255,), width=5 * SC)
            dot(d, (x0, y), VIOLET2, True, SC)
            if pe >= 1 and a + 1 <= g.xr[1]: dot(d, (x1, y), VIOLET2, False, SC)
        if t > 3.2:
            draw_point(big, g.px(-1, 2.5), PINK, t - 3.2, "Salto", SC, "r")
        title, eq, items = "Parte entera", "f(x) = ⌊x + 3⌋", [(.5, "Gráfica escalonada", VIOLET2, "●"), (3.2, "Presenta saltos", PINK, "!"), (5.6, "No es continua en todos sus puntos", RED, "!")]
    elif name == "trozos":
        g = GT; g.draw_axes(big, ease(t / .4), SC)
        p = ease((t - .2) / 1.4)
        if p > 0: draw_curve(big, g.curve_pts(lambda x: x * x, g.xr[0], g.xr[0] + (0 - g.xr[0]) * p, 300, SC), VIOLET2, 5, g.box, SC)
        p2 = ease((t - 1.8) / 1.4)
        if p2 > 0: draw_curve(big, g.curve_pts(lambda x: 2 * x + 1, 0, 3 * p2, 200, SC), GREEN, 5, g.box, SC)
        if t > 3.4:
            d = ImageDraw.Draw(big, "RGBA"); dot(d, g.px(0, 0), VIOLET2, False, SC); dot(d, g.px(0, 1), GREEN, True, SC)
            draw_point(big, g.px(0, .5), AMBER, t - 5.6, "Cambio en x = 0", SC, "r")
        title, eq, items = "Función a trozos", "x² si x < 0;  2x + 1 si x ≥ 0", [(.3, "x² para x < 0", VIOLET2, "●"), (1.8, "2x + 1 para x ≥ 0", GREEN, "●"), (3.6, "Estudiar cada parte por separado", CYAN, "→"), (5.6, "Observar el punto de cambio", AMBER, "!")]
    else:
        d = ImageDraw.Draw(img, "RGBA")
        a = ease_back(t / .6); f = font("xb", int(40 + 50 * clamp(a, 0, 1.2))); s = "¡Muchas gracias!"
        al = int(255 * clamp(t / .4))
        d.text(((W - f.getlength(s)) / 2, 270), s, font=f, fill=WHITE + (al,))
        s2 = "por su atención"; f2 = font("m", 32)
        d.text(((W - f2.getlength(s2)) / 2, 390), s2, font=f2, fill=LAV + (int(al * ease((t - .3) / .5)),))
        s3 = "Taller de funciones matemáticas  ·  Grado 1106"; f3 = font("sb", 20)
        d.text(((W - f3.getlength(s3)) / 2, 460), s3, font=f3, fill=PINK + (int(al * ease((t - .6) / .5)),))
        f4 = font("m", 17)
        for j, s4 in enumerate(["Nathaly Sánchez  ·  Juan Candanoza  ·  Alejandro Gómez  ·  Dustin Gómez", "Miller Pinedo  ·  Isabella Bobadilla  ·  Álvarez Chaveau"]):
            d.text(((W - f4.getlength(s4)) / 2, 510 + 28 * j), s4, font=f4, fill=LAV + (int(al * ease((t - .9 - .2 * j) / .5)),))
        for i in range(16):
            ang = i / 16 * 2 * math.pi; r = 220 + 160 * ease(t / 1.2)
            x = W / 2 + r * math.cos(ang) * 1.6; y = 360 + r * math.sin(ang) * .8
            rr = 4 * (1 - clamp(t / 1.8)) + 1; c = [VIOLET2, PINK, CYAN][i % 3]
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c + (int(200 * (1 - clamp(t / 1.8))),))
        return img
    _p(img, big.resize((W, H), Image.LANCZOS), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((86, 60), TAG, font=font("sb", 16), fill=LAV + (220,))
    d.text((86, 84), title, font=font("xb", 46), fill=WHITE + (255,))
    side_panel(img, "Gráfica", eq, items, t)
    return img

PW, PH = 366, 600
PMASK = rounded_mask(PW, PH, 28); PGLOW, PGPAD = glow_rect(PW, PH, 28, VIOLET, 22, 130)
PX, PY = W - 60 - PW, 60
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-t", str(DUR), "-vf",
       f"fps={FPS},crop=480:787:0:16,scale={PW}:{PH}:flags=lanczos,eq=contrast=1.05:saturation=1.08", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
if not PREVIEW:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
n = round(DUR * FPS); last = None; prev = None; mode_prev = None; hold = None; k = 99
for i in range(n):
    raw = dec.stdout.read(PW * PH * 3)
    if len(raw) == PW * PH * 3: last = Image.frombuffer("RGB", (PW, PH), raw)
    T = i / FPS
    gs = next((g for g in GS if g[0] <= T < g[1]), None)
    mode = gs[2] if gs else "video"
    if mode != mode_prev: hold = prev; k = 0
    mode_prev = mode
    if PREVIEW and not any(abs(T - p) < .5 / FPS for p in PREVIEW): k += 1; continue
    if gs: img = graph_frame(T, gs[2], T - gs[0])
    else:
        img = background(T + 190); draw_header(img, T)
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
