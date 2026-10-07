"""Sprites, map world and drawing helpers for the JHS route video."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FD = __file__.rsplit('/', 1)[0] + '/fonts/'
GOLD = (233, 196, 106)
GOLD2 = (255, 209, 102)
BALL = (255, 216, 77)
IVORY = (255, 248, 231)
INK = (11, 13, 18)
GLASS = (14, 18, 24, 228)


@lru_cache(None)
def font(name, size):
    files = {
        'xb': 'Montserrat_800ExtraBold.ttf', 'b': 'Montserrat_700Bold.ttf',
        'sb': 'Montserrat_600SemiBold.ttf', 'm': 'Montserrat_500Medium.ttf',
        'blk': 'Montserrat_900Black.ttf',
        'pf': 'PlayfairDisplay_900Black.ttf', 'pfb': 'PlayfairDisplay_700Bold.ttf',
        'pfi': 'PlayfairDisplay_600SemiBold_Italic.ttf',
    }
    return ImageFont.truetype(FD + files[name], size)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def back_out(x):
    x = min(max(x, 0.0), 1.0)
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ss(draw_fn, w, h, k=4):
    """supersampled RGBA sprite: draw_fn(draw, k) draws at k-scale."""
    im = Image.new('RGBA', (w * k, h * k), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im), k, im)
    return im.resize((w, h), Image.LANCZOS)


def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1], b


# ---------------- icons ----------------
def arrow_icon(kind, size, color=INK, width=0.16):
    def fn(d, k, im):
        s = size * k; lw = int(s * width)
        def P(x, y): return (x * s, y * s)
        if kind in ('up', 'cross', 'enter'):
            d.line([P(.5, .9), P(.5, .38)], fill=color, width=lw)
            d.polygon([P(.5, .08), P(.82, .44), P(.18, .44)], fill=color)
        elif kind in ('right', 'left'):
            pts = [P(.3, .92), P(.3, .55)]
            # rounded corner
            for a in np.linspace(math.pi, 1.5 * math.pi, 12):
                pts.append(P(.52 + .22 * math.cos(a), .55 + .22 * math.sin(a)))
            pts.append(P(.6, .33))
            d.line(pts, fill=color, width=lw, joint='curve')
            for p in (pts[0],):
                d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=color)
            d.polygon([P(.94, .33), P(.58, .05), P(.58, .61)], fill=color)
            if kind == 'left':
                im2 = im.transpose(Image.FLIP_LEFT_RIGHT)
                im.paste(im2)
        elif kind == 'pin':
            d.ellipse([P(.2, .05), P(.8, .65)], fill=color)
            d.polygon([P(.26, .48), P(.74, .48), P(.5, .95)], fill=color)
            d.ellipse([P(.38, .23), P(.62, .47)], fill=(0, 0, 0, 0))
        elif kind == 'gem':
            d.polygon([P(.2, .35), P(.35, .15), P(.65, .15), P(.8, .35), P(.5, .88)], fill=color)
            d.line([P(.2, .35), P(.8, .35)], fill=INK, width=max(1, lw // 4))
            d.line([P(.35, .15), P(.42, .35), P(.5, .88), P(.58, .35), P(.65, .15)], fill=INK, width=max(1, lw // 4))
        elif kind == 'bookmark':
            d.polygon([P(.25, .08), P(.75, .08), P(.75, .92), P(.5, .7), P(.25, .92)], fill=color)
        elif kind == 'recalc':
            d.arc([P(.15, .15), P(.85, .85)], 30, 320, fill=color, width=lw)
            d.polygon([P(.86, .22), P(.92, .52), P(.62, .42)], fill=color)
    return ss(fn, size, size)


def glyph_icon(kind, size, bg):
    def fn(d, k, im):
        s = size * k
        d.ellipse([0, 0, s - 1, s - 1], fill=INK + (255,))
        d.ellipse([s * .07, s * .07, s * .93, s * .93], fill=bg)
        c = (255, 255, 255)
        lw = int(s * .1)
        if kind == 'cross':
            d.rectangle([s * .42, s * .24, s * .58, s * .76], fill=c)
            d.rectangle([s * .24, s * .42, s * .76, s * .58], fill=c)
        elif kind == 'food':
            d.line([(s * .38, s * .25), (s * .38, s * .78)], fill=c, width=lw)
            for x in (.3, .38, .46):
                d.line([(s * x, s * .25), (s * x, s * .42)], fill=c, width=max(1, lw // 2))
            d.ellipse([s * .55, s * .24, s * .7, s * .52], fill=c)
            d.line([(s * .62, s * .4), (s * .62, s * .78)], fill=c, width=lw)
        elif kind == 'bag':
            d.rounded_rectangle([s * .27, s * .38, s * .73, s * .78], radius=s * .05, fill=c)
            d.arc([s * .37, s * .2, s * .63, s * .5], 180, 360, fill=c, width=lw)
        elif kind == 'tree':
            d.ellipse([s * .25, s * .18, s * .75, s * .62], fill=c)
            d.rectangle([s * .45, s * .55, s * .55, s * .8], fill=c)
        elif kind == 'light':
            d.rounded_rectangle([s * .36, s * .16, s * .64, s * .84], radius=s * .08, fill=(20, 20, 20))
            for y, col in ((.29, (255, 70, 70)), (.5, (255, 200, 60)), (.71, (70, 220, 120))):
                d.ellipse([s * .43, s * (y - .07), s * .57, s * (y + .07)], fill=col)
        elif kind == 'start':
            d.ellipse([s * .32, s * .32, s * .68, s * .68], fill=c)
        elif kind == 'tent':
            d.polygon([(s * .2, s * .5), (s * .5, s * .25), (s * .8, s * .5)], fill=c)
            d.rectangle([s * .26, s * .5, s * .74, s * .72], fill=c)
    return ss(fn, size, size)


def ball_sprite(r=22):
    S = r * 6
    def fn(d, k, im):
        c = S * k / 2
        for i in range(30, 0, -1):
            rr = r * k * (1 + i * 0.1)
            a = int(110 * (1 - i / 30) ** 2)
            d.ellipse([c - rr, c - rr, c + rr, c + rr], fill=BALL + (a,))
        d.ellipse([c - r * k - 5 * k, c - r * k - 5 * k, c + r * k + 5 * k, c + r * k + 5 * k], fill=INK + (255,))
        d.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], fill=BALL + (255,))
        d.ellipse([c - r * k * .45, c - r * k * .55, c + r * k * .05, c - r * k * .05], fill=(255, 250, 220, 230))
    return ss(fn, S, S, 3)


def dest_pin(size=120):
    def fn(d, k, im):
        s = size * k
        d.ellipse([s * .14, s * .02, s * .86, s * .74], fill=INK + (255,))
        d.polygon([(s * .2, s * .5), (s * .8, s * .5), (s * .5, s * 1.0)], fill=INK + (255,))
        d.ellipse([s * .19, s * .07, s * .81, s * .69], fill=GOLD2 + (255,))
        d.polygon([(s * .25, s * .5), (s * .75, s * .5), (s * .5, s * .93)], fill=GOLD2 + (255,))
        g = s * .2
        cx, cy = s * .5, s * .38
        d.polygon([(cx - g, cy - g * .2), (cx - g * .5, cy - g * .7), (cx + g * .5, cy - g * .7), (cx + g, cy - g * .2), (cx, cy + g)], fill=INK + (255,))
    return ss(fn, size, size)


# ---------------- UI sprites ----------------
def card(title, sub=None, icon='up', w=930):
    ft, fs = font('xb', 56), font('sb', 33)
    h = 176 if sub else 140
    def fn(d, k, im):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=34 * k, fill=GLASS)
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=34 * k, outline=GOLD + (200,), width=3 * k)
        d.rounded_rectangle([14 * k, 14 * k, (h - 14) * k, (h - 14) * k], radius=26 * k, fill=GOLD2 + (255,))
    im = ss(fn, w, h, 2)
    ic = arrow_icon(icon, h - 64)
    im.alpha_composite(ic, (32, 32))
    d = ImageDraw.Draw(im)
    x = h + 14
    if sub:
        d.text((x, 30), title, font=ft, fill=IVORY)
        d.text((x, 104), sub, font=fs, fill=GOLD)
    else:
        tw, th, b = text_size(title, ft)
        d.text((x, (h - th) / 2 - b[1]), title, font=ft, fill=IVORY)
    return im


def tag(txt, size=34, icon=None, fg=INK, bg=GOLD2 + (255,)):
    f = font('xb', size)
    tw, th, b = text_size(txt, f)
    pad = int(size * .55); ih = int(size * 1.15) if icon else 0
    w = tw + pad * 2 + (ih + 10 if icon else 0); h = int(size * 1.9)
    def fn(d, k, im):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=h * k // 2, fill=bg)
    im = ss(fn, w, h, 3)
    x = pad
    if icon:
        ic = arrow_icon(icon, ih, fg if len(fg) == 4 else fg + (255,))
        im.alpha_composite(ic, (x - 4, (h - ih) // 2)); x += ih + 6
    ImageDraw.Draw(im).text((x, (h - th) / 2 - b[1]), txt, font=f, fill=fg)
    return im


def map_label(txt, kind, bg):
    f = font('b', 30)
    tw, th, b = text_size(txt, f)
    ic = glyph_icon(kind, 58, bg)
    w = tw + 58 + 38; h = 66
    def fn(d, k, im):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=h * k // 2, fill=(14, 18, 24, 235), outline=GOLD + (170,), width=2 * k)
    im = ss(fn, w, h, 3)
    im.alpha_composite(ic, (4, 4))
    ImageDraw.Draw(im).text((70, (h - th) / 2 - b[1]), txt, font=f, fill=IVORY)
    return im


def sparkle(size=60, color=GOLD2):
    def fn(d, k, im):
        s = size * k; c = s / 2
        pts = []
        for i in range(8):
            a = i * math.pi / 4
            r = c if i % 2 == 0 else c * .18
            pts.append((c + r * math.cos(a - math.pi / 2), c + r * math.sin(a - math.pi / 2)))
        d.polygon(pts, fill=color + (255,))
    im = ss(fn, size, size)
    glow = im.filter(ImageFilter.GaussianBlur(size / 8))
    out = Image.alpha_composite(glow, im)
    return out


def logo(scale=1.0, sub=True):
    fj = font('pf', int(170 * scale)); fsub = font('sb', int(40 * scale))
    tw, th, b = text_size('JHS', fj)
    sw, sh, sb_ = text_size('J O Y E R Í A', fsub)
    w = int(max(tw, sw) + 80 * scale); h = int(th + (sh + 70 * scale if sub else 0) + 40 * scale)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    # gold gradient text
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.text(((w - tw) / 2 - b[0], 10 * scale - b[1]), 'JHS', font=fj, fill=255)
    grad = np.zeros((h, w, 4), np.uint8)
    yy = np.linspace(0, 1, h)[:, None]
    top = np.array([255, 231, 160]); mid = np.array([233, 186, 86]); bot = np.array([176, 128, 40])
    col = np.where(yy < .5, top + (mid - top) * (yy / .5), mid + (bot - mid) * ((yy - .5) / .5))
    grad[..., :3] = col[:, None, :].astype(np.uint8).repeat(w, 1) if col.ndim == 2 else col
    grad[..., 3] = np.array(mask)
    gi = Image.fromarray(grad, 'RGBA')
    sh_ = gi.filter(ImageFilter.GaussianBlur(10 * scale))
    shadow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); shadow.putalpha(sh_.getchannel('A').point(lambda v: v * 0.6))
    im.alpha_composite(shadow, (0, int(6 * scale)))
    im.alpha_composite(gi)
    if sub:
        d = ImageDraw.Draw(im)
        y = int(th + 40 * scale)
        d.line([(w / 2 - sw / 2 - 10, y - 18 * scale), (w / 2 + sw / 2 + 10, y - 18 * scale)], fill=GOLD + (200,), width=max(1, int(2 * scale)))
        d.text(((w - sw) / 2 - sb_[0], y - sb_[1]), 'J O Y E R Í A', font=fsub, fill=IVORY)
    return im


def ring_sprite(w, h, prog=1.0, color=GOLD2, lw=9):
    pad = 30
    def fn(d, k, im):
        box = [pad * k, pad * k, (w + pad) * k, (h + pad) * k]
        d.arc(box, -90, -90 + 360 * prog, fill=color + (255,), width=lw * k)
    im = ss(fn, w + 2 * pad, h + 2 * pad, 2)
    glow = im.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(glow, im)


# ---------------- captions ----------------
KEY = {'derecha', 'izquierda', 'derecho', 'semáforo', 'farma', 'vida', 'rey', 'chino', 'jamar', 'jhs', 'joyería',
       'parque', 'toldos', 'rojos', 'pasillo', '90', 'cruzamos', 'giramos', 'calle', 'listo', 'joyita', 'cerca', 'guarda'}


def caption_sprite(txt, size=64):
    f = font('xb', size)
    words = txt.split()
    # layout single or two lines max width 900
    lines, cur = [], []
    for wd in words:
        t = ' '.join(cur + [wd])
        if text_size(t, f)[0] > 880 and cur:
            lines.append(cur); cur = [wd]
        else:
            cur.append(wd)
    lines.append(cur)
    lh = int(size * 1.22)
    im = Image.new('RGBA', (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sp = text_size('a a', f)[0] - text_size('aa', f)[0]
    for li, ln in enumerate(lines):
        tot = sum(text_size(w_, f)[0] for w_ in ln) + sp * (len(ln) - 1)
        x = (W - tot) / 2; y = 16 + li * lh
        for w_ in ln:
            key = w_.strip('¿?¡!.,…:').lower()
            col = GOLD2 if key in KEY else (255, 255, 255)
            d.text((x, y), w_, font=f, fill=col, stroke_width=7, stroke_fill=(10, 10, 12))
            x += text_size(w_, f)[0] + sp
    sh = im.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * .55)
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0)); shadow.putalpha(sh)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.alpha_composite(shadow, (0, 0)); out.alpha_composite(im)
    return out


def chunk_caption(txt, dur, maxc=24):
    words = txt.split(); chunks, cur = [], ''
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > maxc:
            chunks.append(cur); cur = wd
        else:
            cur = (cur + ' ' + wd).strip()
        if wd[-1] in '.?!…,' and len(cur) > 10:
            chunks.append(cur); cur = ''
    if cur: chunks.append(cur)
    tot = sum(len(c) + 4 for c in chunks); out = []; t = 0
    for c in chunks:
        d = dur * (len(c) + 4) / tot
        out.append((t, t + d, c)); t += d
    return out


# ---------------- map world ----------------
PAD = 2200
WW, WH = 4400, 5900
ROUTE = [(700, 5330), (700, 5100), (700, 3000), (3300, 3000), (3300, 2900), (3300, 2350), (3300, 2060),
         (3300, 1940), (3300, 1350), (3300, 1150), (3390, 1050), (3560, 930)]
VX = [100, 700, 1300, 1900, 2500, 3300, 3950]
HY = [300, 1150, 2000, 3000, 4200, 5200]
CROSSINGS = [((700, 5200), 'h'), ((1300, 3000), 'v'), ((1900, 3000), 'v'), ((2500, 3000), 'v'), ((3300, 3000), 'h'),
             ((3300, 2000), 'h'), ((3300, 1150), 'h')]


def route_cum():
    c = [0.0]
    for a, b in zip(ROUTE, ROUTE[1:]):
        c.append(c[-1] + math.dist(a, b))
    return c


CUM = route_cum()


def route_at(s):
    s = min(max(s, 0), CUM[-1])
    for i in range(len(ROUTE) - 1):
        if s <= CUM[i + 1] or i == len(ROUTE) - 2:
            f = (s - CUM[i]) / max(1e-6, CUM[i + 1] - CUM[i])
            a, b = ROUTE[i], ROUTE[i + 1]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def route_upto(s):
    pts = []
    for i, p in enumerate(ROUTE):
        if CUM[i] < s:
            pts.append(p)
    pts.append(route_at(s))
    return pts


def build_world():
    w, h = WW + 2 * PAD, WH + 2 * PAD
    im = Image.new('RGB', (w, h), (13, 16, 22))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5)
    def R(x0, y0, x1, y1): return [x0 + PAD, y0 + PAD, x1 + PAD, y1 + PAD]
    xs = [-2000] + VX + [WW + 2000]; ys = [-2000] + HY + [WH + 2000]
    sw = lambda v, main: 120 if main else 64
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x0 = xs[i] + (40 if i else 0); x1 = xs[i + 1] - 40
            y0 = ys[j] + (40 if j else 0); y1 = ys[j + 1] - 40
            if ys[j] == 3000: y0 = ys[j] + 62
            if ys[j + 1] == 3000: y1 = ys[j + 1] - 62
            if x1 - x0 < 50 or y1 - y0 < 50: continue
            d.rounded_rectangle(R(x0, y0, x1, y1), radius=26, fill=(27, 33, 44))
            # building texture
            for _ in range(int((x1 - x0) * (y1 - y0) / 52000)):
                bx = rng.uniform(x0 + 20, x1 - 120); by = rng.uniform(y0 + 20, y1 - 120)
                bw = rng.uniform(60, 180); bh = rng.uniform(60, 180)
                if bx + bw > x1 - 18 or by + bh > y1 - 18: continue
                c = int(rng.uniform(31, 39))
                d.rounded_rectangle(R(bx, by, bx + bw, by + bh), radius=10, fill=(c, c + 5, c + 14))
    # park (west of x=3300, between y=1350..1960)
    d.rounded_rectangle(R(2560, 1600, 3258, 1958), radius=26, fill=(22, 52, 38))
    for _ in range(70):
        x = rng.uniform(2600, 3220); y = rng.uniform(1640, 1920); r = rng.uniform(14, 30)
        d.ellipse(R(x - r, y - r, x + r, y + r), fill=(30, 72, 50))
    # market block NE of light 2
    d.rounded_rectangle(R(3342, 340, 3908, 1108), radius=26, fill=(48, 26, 30))
    for _ in range(40):
        x = rng.uniform(3360, 3860); y = rng.uniform(360, 1070)
        d.rectangle(R(x, y, x + 36, y + 30), fill=(150, 40, 46))
    # avenue lane dashes
    for x in range(-1800, WW + 1800, 90):
        d.rectangle(R(x, 2996, x + 44, 3004), fill=(52, 60, 76))
    # zebra crossings
    for (cx, cy), o in CROSSINGS:
        if o == 'h':  # crossing a horizontal street -> stripes horizontal-ish spanning street height
            for k in range(6):
                y = cy - 38 + k * 14
                d.rectangle(R(cx - 46, y, cx + 46, y + 7), fill=(78, 86, 102))
        else:
            for k in range(7):
                x = cx - 45 + k * 14
                d.rectangle(R(x, cy - 52, x + 7, cy + 52), fill=(78, 86, 102))
    return im


LANDMARKS = [  # world pos, text, glyph, color, side offset (screen px)
    ((700, 5330), 'Inicio', 'start', (90, 98, 115), (40, 10)),
    ((600, 2900), 'Farma Vida', 'cross', (36, 98, 200), (-60, -80)),
    ((700, 3000), 'Semáforo', 'light', (40, 44, 52), (40, 30)),
    ((3300, 3000), 'Semáforo', 'light', (40, 44, 52), (40, 30)),
    ((3200, 2350), 'El Rey Chino', 'food', (200, 50, 40), (-60, -40)),
    ((2900, 1780), 'Parque', 'tree', (40, 130, 80), (-60, -30)),
    ((3200, 1350), 'Jamar', 'bag', (205, 30, 45), (-60, -30)),
    ((3300, 1150), 'Semáforo', 'light', (40, 44, 52), (40, 30)),
    ((3620, 760), 'Toldos rojos', 'tent', (170, 40, 50), (10, -40)),
]
