import sys, math, subprocess, numpy as np, wave
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from style import *

SRC = "/root/.claude/uploads/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/96e9e451-WhatsApp_Video_2026-10-12_at_7.49.43_PM.mp4"
OUT = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
T0, T1 = 0.0, 108.0
DUR = round((T1 - T0) * FPS) / FPS
SC = 2
def _p(img, im, pos): img.paste(im, pos, im)

raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "30", "-i", SRC, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
SLIDE = Image.frombuffer("RGB", (1248, 576), raw).crop((236, 116, 1014, 492))
SMASK = None

a1 = lambda x: abs(x - 4)
a2 = lambda x: abs(x * x - 9)
G1 = Graph((110, 200, 760, 600), (-1, 9), (-1, 6), 1, 1, xlabels=[1, 2, 3, 4, 5, 6, 7, 8], ylabels=[1, 2, 3, 4, 5])
G3 = Graph((110, 200, 760, 600), (-2.5, 3), (-1, 7), 1, 1, xlabels=[-2, -1, 1, 2, 3], ylabels=[1, 2, 4, 6])
G1s = Graph((110, 240, 580, 590), (-1, 9), (-1, 6), 1, 1, xlabels=[4], ylabels=[4])
G2s = Graph((710, 240, 1180, 590), (-5, 5), (-1.5, 12), 1, 1, xlabels=[-3, 3], ylabels=[9])
G2 = Graph((110, 200, 760, 600), (-5, 5), (-1.5, 12), 1, 1, xlabels=[-4, -3, -2, -1, 1, 2, 3, 4], ylabels=[3, 6, 9])

def header(img, name, a=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((86, 60), "INTEGRANTE 5  ·  MILLER PINEDO", font=font("sb", 16), fill=LAV + (int(220 * a),))
    d.text((86, 84), name, font=font("xb", 46), fill=WHITE + (int(255 * a),))

def mic_badge(img, lvl, t):
    d = ImageDraw.Draw(img, "RGBA"); x, y = 60, 650
    d.rounded_rectangle([x, y - 4, x + 275, y + 40], 22, fill=(30, 18, 60, 220), outline=VIOLET2 + (150,), width=2)
    for i in range(5):
        h = 6 + 22 * lvl * (0.5 + 0.5 * math.sin(t * 9 + i * 1.7)) ** 2 * (1 if i % 2 else .8)
        cx = x + 22 + i * 8
        d.rounded_rectangle([cx, y + 18 - h / 2, cx + 4, y + 18 + h / 2], 2, fill=PINK + (255,))
    d.text((x + 72, y + 8), "Miller Pinedo · narración", font=font("sb", 16), fill=WHITE + (235,))

def side_panel(img, title, eq, items, t, a=1.0):
    d = ImageDraw.Draw(img, "RGBA"); x = 830
    d.text((x, 214), title.upper(), font=font("sb", 16), fill=LAV + (int(230 * a),))
    mtext(d, (x, 240), eq, font("db", 34), WHITE + (int(255 * a),))
    y = 310
    for (ti, txt, col, icon) in items:
        if t < ti: continue
        b = ease((t - ti) / .35) * a
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pill(layer, (x + (1 - b) * 30, y), txt, col, b, 19, icon)
        _p(img, layer, (0, 0)); y += 58

def slide_view(img, t, z0, z1, cx, cy, dur, a=1.0):
    """ken-burns on slide; z = zoom, (cx,cy) focus in slide coords"""
    z = z0 + (z1 - z0) * ease(t / dur)
    w = 1000; h = int(w * SLIDE.height / SLIDE.width)
    sw, sh = SLIDE.width / z, SLIDE.height / z
    x0 = clamp(cx - sw / 2, 0, SLIDE.width - sw); y0 = clamp(cy - sh / 2, 0, SLIDE.height - sh)
    im = SLIDE.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((w, h), Image.LANCZOS).convert("RGBA")
    m = rounded_mask(w, h, 26)
    if a < 1: m = m.point(lambda v: int(v * a))
    g, pad = glow_rect(w, h, 26, VIOLET, 22, int(130 * a))
    px, py = (W - w) // 2, 100
    _p(img, g, (px - pad, py - pad)); img.paste(im, (px, py), m)

SCENES = [(0, 6.2, "intro"), (6.2, 48.2, "abs1"), (48.2, 84.0, "abs2"), (84.0, 95.5, "trozos"), (95.5, 108.0, "recap")]

def graph_layer(g, f, t, draw_t0, draw_d, col, extra):
    big = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
    g.draw_axes(big, ease(t / .4), SC)
    xa, xb = g.xr
    p = ease((t - draw_t0) / draw_d)
    if p > 0:
        pts = g.curve_pts(f, xa, xa + (xb - xa) * p, 600, SC)
        draw_curve(big, pts, col, 5, g.box, SC)
    extra(big)
    return big.resize((W, H), Image.LANCZOS)

def frame(T, lvl):
    img = background(T + 110)
    for (sa, sb, name) in SCENES:
        if sa <= T < sb: break
    t = T - sa; dur = sb - sa
    if name == "intro":
        a = ease(t / .6); d = ImageDraw.Draw(img, "RGBA")
        slide_view(img, t, 1.0, 1.15, 389, 219, dur, a)
        f1 = font("sb", 18); s = "INTEGRANTE 5  ·  MILLER PINEDO"
        d.text(((W - f1.getlength(s)) / 2, 60), s, font=f1, fill=PINK + (int(255 * a),))
        mic_badge(img, lvl, T)
    elif name == "abs1":
        def ex(big):
            if t > 3.0:
                pts = G1.curve_pts(a1, -1, -1 + 5 * ease((t - 38.5) / 1.4), 300, SC) if t > 38.5 else []
                if pts: draw_curve(big, pts, RED, 8, G1.box, SC)
                if t > 40.5:
                    pts = G1.curve_pts(a1, 4, 4 + 5 * ease((t - 40.5) / 1.4), 300, SC)
                    draw_curve(big, pts, GREEN, 8, G1.box, SC)
            draw_point(big, G1.px(4, 0), PINK, t - 26.0, "Vértice (4, 0)", SC, "d")
        _p(img, graph_layer(G1, a1, t, .3, 1.8, VIOLET2, ex), (0, 0))
        header(img, "Valor absoluto")
        side_panel(img, "Primera función", "f(x) = |x − 4|", [
            (7.5, "Resultados siempre ≥ 0", VIOLET2, "●"), (17.5, "Dominio: ℝ", CYAN, "●"), (21.0, "Rango: y ≥ 0", CYAN, "●"),
            (26.0, "Vértice: (4, 0)", PINK, "●"), (30.5, "Forma de V", AMBER, "✓"), (38.5, "Decrece hasta x = 4", RED, "↘"), (40.5, "Luego crece", GREEN, "↗")], t)
        mic_badge(img, lvl, T)
    elif name == "abs2":
        def ex(big):
            # dashed hint of x^2-9 reflected part
            if t > 13.0:
                for i, r in enumerate([-3, 3]):
                    draw_point(big, G2.px(r, 0), GREEN, t - (18.5 + .5 * i), fmt(r), SC, "d")
            draw_point(big, G2.px(0, 9), AMBER, t - 30.0, "(0, 9)", SC, "r", -40)
        _p(img, graph_layer(G2, a2, t, .3, 2.0, CYAN, ex), (0, 0))
        header(img, "Valor absoluto")
        side_panel(img, "Segunda función", "f(x) = |x² − 9|", [
            (9.5, "Dominio: ℝ", CYAN, "●"), (14.0, "x² − 9 = 0", VIOLET2, "→"), (18.5, "Corta X en x = 3 y x = −3", GREEN, "●"),
            (30.0, "Corta Y en f(0) = 9", AMBER, "●"), (33.0, "Continua (sin cortes)", CYAN, "✓")], t)
        mic_badge(img, lvl, T)
    elif name == "trozos":
        def ex(big):
            p = ease((t - 2.5) / 1.2)
            if p > 0: draw_curve(big, G3.curve_pts(lambda x: 2 * x + 1, 0, 3 * p, 200, SC), GREEN, 5, G3.box, SC)
            if t > 5.5:
                d = ImageDraw.Draw(big, "RGBA")
                for (y, filled) in [(0, False), (1, True)]:
                    X, Y = [v * SC for v in G3.px(0, y)]; r = 8 * SC
                    d.ellipse([X - r, Y - r, X + r, Y + r], fill=(GREEN + (255,)) if filled else (20, 10, 45, 255), outline=(VIOLET2 if not filled else GREEN) + (255,), width=3 * SC)
                draw_point(big, G3.px(0, 0.5), AMBER, t - 5.5, "Salto en x = 0", SC, "r")
        _p(img, graph_layer(G3, lambda x: x * x if x < 0 else float("nan"), t, .3, 1.6, VIOLET2, ex), (0, 0))
        header(img, "Funciones a trozos")
        side_panel(img, "Función definida a trozos", "x² si x < 0;  2x + 1 si x ≥ 0", [
            (1.0, "Una regla para x < 0", VIOLET2, "●"), (2.5, "Otra regla para x ≥ 0", GREEN, "●"), (5.5, "Punto de ruptura", AMBER, "!")], t)
        mic_badge(img, lvl, T)
    else:
        big = Image.new("RGBA", (W * SC, H * SC), (0, 0, 0, 0))
        for k, (g, f, col, eq, x0) in enumerate([(G1s, a1, VIOLET2, "f(x) = |x − 4|", 90), (G2s, a2, CYAN, "f(x) = |x² − 9|", 690)]):
            tk = t - (0.3 if k == 0 else 5.0)
            if tk < 0: continue
            g.draw_axes(big, ease(tk / .4), SC)
            p = ease((tk - .2) / 1.4)
            if p > 0: draw_curve(big, g.curve_pts(f, g.xr[0], g.xr[0] + (g.xr[1] - g.xr[0]) * p, 400, SC), col, 5, g.box, SC)
            ImageDraw.Draw(big, "RGBA").text((x0 * SC, 168 * SC), eq, font=font("db", 30 * SC), fill=WHITE + (int(255 * ease(tk / .4)),))
        _p(img, big.resize((W, H), Image.LANCZOS), (0, 0))
        header(img, "Resumen")
        mic_badge(img, lvl, T)
        fade = clamp((dur - t) / .6)
        if fade < 1: img = Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, fade)
    # crossfade between scenes
    return img

au = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-t", str(DUR), "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
need = int(round(DUR * 48000)); au = np.pad(au, (0, max(0, need - len(au))))[:need].copy()
hop = 48000 // FPS
lv = np.array([np.sqrt((au[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12) for i in range(need // hop + 1)])
lv = np.clip((20 * np.log10(lv) + 45) / 30, 0, 1)

if not PREVIEW:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
n = round(DUR * FPS); prev = None; bounds = [s[0] for s in SCENES[1:]]
for i in range(n):
    T = i / FPS
    if PREVIEW and not any(abs(T - p) < .5 / FPS for p in PREVIEW): continue
    img = frame(T, float(lv[min(i, len(lv) - 1)])).convert("RGB")
    for bt in bounds:
        if 0 <= T - bt < 9 / FPS and prev is not None and not PREVIEW:
            img = Image.blend(prev_scene_last, img, (T - bt) * FPS / 9 + 1 / 9)
    if PREVIEW: img.save(f"{OUT}.{T:.1f}.png"); continue
    if any(0 < bt - T <= 1 / FPS + 1e-6 for bt in bounds): prev_scene_last = img
    enc.stdin.write(img.tobytes()); prev = img
if not PREVIEW:
    enc.stdin.close(); enc.wait()
    r = np.linspace(0, 1, 2400, dtype=np.float32); au[:2400] *= r; au[-2400:] *= r[::-1]
    with wave.open(OUT + ".audio.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(au, -1, 1) * 32767).astype(np.int16).tobytes())
print("done", DUR)
