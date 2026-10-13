import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 720, 30
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(w, s):
    k = (w, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + {"r": "Inter-Regular", "m": "Inter-Medium", "sb": "Inter-SemiBold",
                                          "b": "Inter-Bold", "xb": "InterDisplay-ExtraBold", "db": "InterDisplay-Bold"}[w] + ".otf", s)
    return _fc[k]

VIOLET = (139, 92, 246); VIOLET2 = (167, 139, 250); PINK = (236, 72, 153); CYAN = (34, 211, 238)
GREEN = (52, 211, 153); RED = (248, 113, 113); WHITE = (255, 255, 255); LAV = (196, 181, 253); AMBER = (251, 191, 36)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

# ---------- background ----------
def _make_base():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    top = np.array([12, 6, 28]); bot = np.array([22, 9, 48])
    g = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    g = np.broadcast_to(g, (H, W, 3)).copy()
    vign = 1 - 0.35 * (((x - .5) ** 2 + (y - .5) ** 2) * 2)
    g *= vign[..., None]
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for gx in range(0, W, 40): d.line([(gx, 0), (gx, H)], fill=(167, 139, 250, 9))
    for gy in range(0, H, 40): d.line([(0, gy), (W, gy)], fill=(167, 139, 250, 9))
    return img
def _blob(r, col, a):
    s = r * 2; yy, xx = np.mgrid[0:s, 0:s]; dd = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    al = np.clip(1 - dd, 0, 1) ** 2 * a
    arr = np.zeros((s, s, 4), np.uint8); arr[..., :3] = col; arr[..., 3] = (al * 255).astype(np.uint8)
    return Image.fromarray(arr)
BASE = _make_base()
BLOBS = [(_blob(380, VIOLET, .32), (1050, 120), (60, 40), .21), (_blob(330, PINK, .16), (150, 650), (70, 30), .17),
         (_blob(280, CYAN, .10), (700, 400), (120, 60), .13)]
def background(t):
    img = BASE.copy()
    for b, (cx, cy), (ax, ay), sp in BLOBS:
        x = cx + ax * math.sin(t * sp * 2 * math.pi * .35) - b.width // 2
        y = cy + ay * math.cos(t * sp * 2 * math.pi * .3) - b.height // 2
        img.paste(b, (int(x), int(y)), b)
    return img

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_dj = {}
def _alt(f):
    k = f.size
    if k not in _dj: _dj[k] = ImageFont.truetype(DJ, int(k * .95))
    return _dj[k]
ALT = set("ℝ∛⌊⌋")
def _runs(s):
    out = []
    for ch in s:
        alt = ch in ALT
        if out and out[-1][0] == alt: out[-1][1] += ch
        else: out.append([alt, ch])
    return out
def text_w(f, s): return sum((_alt(f) if a else f).getlength(r) for a, r in _runs(s))
def mtext(d, xy, s, f, fill):
    x, y = xy
    for a, r in _runs(s):
        ff = _alt(f) if a else f
        d.text((x, y + (f.size * .02 if a else 0)), r, font=ff, fill=fill); x += ff.getlength(r)

def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 1], r * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def glow_rect(w, h, r, col, blur=18, a=150):
    pad = blur * 3; im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([pad, pad, pad + w, pad + h], r, fill=col + (a,))
    return im.filter(ImageFilter.GaussianBlur(blur)), pad

def with_alpha(im, a):
    if a >= 1: return im
    im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al); return im

# ---------- card ----------
def make_card(label, text, w=None, accent=VIOLET2, big=46, sub=None):
    fl = font("sb", 17); ft = font("db", big); fs = font("m", 20)
    tw = text_w(ft, text); sw = text_w(fs, sub) if sub else 0
    w = w or int(max(tw, sw, text_w(fl, label.upper())) + 64)
    h = 40 + 22 + big + 20 + (34 if sub else 0) + 6
    sc = 2
    im = Image.new("RGBA", (w * sc, h * sc), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * sc - 1, h * sc - 1], 20 * sc, fill=(30, 18, 60, 225), outline=accent + (170,), width=2 * sc)
    d.rounded_rectangle([0, 0, 7 * sc, h * sc - 1], 3 * sc, fill=accent + (255,))
    im = im.resize((w, h), Image.LANCZOS); d = ImageDraw.Draw(im)
    d.text((30, 20), label.upper(), font=fl, fill=accent + (255,))
    mtext(d, (30, 50), text, ft, WHITE + (255,))
    if sub: mtext(d, (30, 50 + big + 16), sub, fs, LAV + (230,))
    g, pad = glow_rect(w, h, 20, accent, 16, 70)
    g.alpha_composite(im, (pad, pad))
    return g, pad

# ---------- graph ----------
class Graph:
    def __init__(self, box, xr, yr, xstep=1, ystep=1, xlabels=None, ylabels=None):
        self.box = box; self.xr = xr; self.yr = yr; self.xs = xstep; self.ys = ystep
        self.xlabels = xlabels; self.ylabels = ylabels
    def px(self, x, y):
        x0, y0, x1, y1 = self.box
        return (x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (x1 - x0),
                y1 - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (y1 - y0))
    def draw_axes(self, img, a=1.0, sc=1):
        d = ImageDraw.Draw(img, "RGBA"); x0, y0, x1, y1 = [v * sc for v in self.box]
        d.rounded_rectangle([x0 - 24 * sc, y0 - 24 * sc, x1 + 24 * sc, y1 + 24 * sc], 26 * sc, fill=(18, 10, 40, int(200 * a)), outline=(167, 139, 250, int(60 * a)), width=2 * sc)
        fx = font("m", 15 * sc)
        k = math.ceil(self.xr[0] / self.xs)
        while k * self.xs <= self.xr[1]:
            v = k * self.xs; X = self.px(v, 0)[0] * sc
            d.line([(X, y0), (X, y1)], fill=(167, 139, 250, int(28 * a)), width=sc)
            k += 1
        k = math.ceil(self.yr[0] / self.ys)
        while k * self.ys <= self.yr[1]:
            v = k * self.ys; Y = self.px(0, v)[1] * sc
            d.line([(x0, Y), (x1, Y)], fill=(167, 139, 250, int(28 * a)), width=sc)
            k += 1
        ox, oy = [v * sc for v in self.px(0, 0)]
        d.line([(x0, oy), (x1, oy)], fill=(230, 225, 255, int(200 * a)), width=2 * sc)
        d.line([(ox, y0), (ox, y1)], fill=(230, 225, 255, int(200 * a)), width=2 * sc)
        d.polygon([(x1 + 10 * sc, oy), (x1 - 4 * sc, oy - 7 * sc), (x1 - 4 * sc, oy + 7 * sc)], fill=(230, 225, 255, int(200 * a)))
        d.polygon([(ox, y0 - 10 * sc), (ox - 7 * sc, y0 + 4 * sc), (ox + 7 * sc, y0 + 4 * sc)], fill=(230, 225, 255, int(200 * a)))
        d.text((x1 + 2 * sc, oy + 8 * sc), "x", font=font("sb", 18 * sc), fill=(230, 225, 255, int(220 * a)))
        d.text((ox + 10 * sc, y0 - 16 * sc), "y", font=font("sb", 18 * sc), fill=(230, 225, 255, int(220 * a)))
        for v in (self.xlabels or []):
            X = self.px(v, 0)[0] * sc; s = fmt(v)
            d.line([(X, oy - 5 * sc), (X, oy + 5 * sc)], fill=(230, 225, 255, int(200 * a)), width=2 * sc)
            d.text((X - fx.getlength(s) / 2, oy + 9 * sc), s, font=fx, fill=(200, 190, 240, int(220 * a)))
        for v in (self.ylabels or []):
            Y = self.px(0, v)[1] * sc; s = fmt(v)
            d.line([(ox - 5 * sc, Y), (ox + 5 * sc, Y)], fill=(230, 225, 255, int(200 * a)), width=2 * sc)
            d.text((ox - 12 * sc - fx.getlength(s), Y - 9 * sc), s, font=fx, fill=(200, 190, 240, int(220 * a)))
    def curve_pts(self, f, xa, xb, n=400, sc=1):
        pts = []
        for i in range(n + 1):
            x = xa + (xb - xa) * i / n; y = f(x)
            if y != y: continue
            X, Y = self.px(x, y); pts.append((X * sc, Y * sc))
        return pts

def fmt(v):
    s = ("%g" % v).replace("-", "−")
    return s

def draw_curve(img, pts, col, width, box, sc, glow=True):
    """draw a polyline clipped to box (in sc units) with glow"""
    x0, y0, x1, y1 = [v * sc for v in box]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    seg = []
    segs = []
    for p in pts:
        if y0 - 2 <= p[1] <= y1 + 2: seg.append(p)
        else:
            if len(seg) > 1: segs.append(seg)
            seg = []
    if len(seg) > 1: segs.append(seg)
    for s in segs: d.line(s, fill=col + (255,), width=width * sc, joint="curve")
    if glow:
        g = layer.filter(ImageFilter.GaussianBlur(7 * sc))
        img.alpha_composite(g); img.alpha_composite(g)
    img.alpha_composite(layer)
    if segs:
        for s in segs:
            for p in (s[0], s[-1]):
                r = width * sc / 2
                ImageDraw.Draw(img).ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col + (255,))

def draw_point(img, xy, col, t, label=None, sc=1, side="r", lab_dy=0):
    """pop-in point with pulse ring. t = seconds since appearance"""
    if t < 0: return
    base = img; img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA"); X, Y = xy[0] * sc, xy[1] * sc
    s = ease_back(t / .35)
    ring = (t % 1.4) / 1.4
    rr = (10 + 22 * ring) * sc
    d.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=col + (int(200 * (1 - ring)),), width=3 * sc)
    r = 9 * s * sc
    d.ellipse([X - r - 3 * sc, Y - r - 3 * sc, X + r + 3 * sc, Y + r + 3 * sc], fill=(255, 255, 255, 255))
    d.ellipse([X - r, Y - r, X + r, Y + r], fill=col + (255,))
    if label:
        a = ease(t / .4); f = font("b", 20 * sc)
        tw = f.getlength(label); pad = 10 * sc
        if side == "r": bx = X + 18 * sc
        elif side == "l": bx = X - 18 * sc - tw - 2 * pad
        else: bx = X - tw / 2 - pad
        by = Y - 18 * sc + lab_dy * sc - (1 - a) * 10 * sc
        if side == "u": by = Y - 56 * sc + lab_dy * sc - (1 - a) * 10 * sc
        if side == "d": by = Y + 18 * sc + lab_dy * sc + (1 - a) * 10 * sc
        d.rounded_rectangle([bx, by, bx + tw + 2 * pad, by + 36 * sc], 10 * sc, fill=(20, 10, 45, int(235 * a)), outline=col + (int(255 * a),), width=2 * sc)
        d.text((bx + pad, by + 6 * sc), label, font=f, fill=(255, 255, 255, int(255 * a)))
    base.alpha_composite(img)

def pill(img, xy, text, col, a=1.0, fsize=19, icon=None):
    d = ImageDraw.Draw(img, "RGBA"); f = font("sb", fsize); tw = text_w(f, text)
    x, y = xy; h = fsize + 20
    d.rounded_rectangle([x, y, x + tw + 34 + (22 if icon else 0), y + h], h // 2, fill=col + (int(45 * a),), outline=col + (int(230 * a),), width=2)
    tx = x + 17
    if icon:
        d.text((tx, y + 9), icon, font=font("b", fsize), fill=col + (int(255 * a),)); tx += 24
    mtext(d, (tx, y + 9), text, f, (255, 255, 255, int(255 * a)))
    return tw + 34 + (22 if icon else 0)
