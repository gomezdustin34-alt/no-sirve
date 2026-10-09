"""Motor gráfico: lienzo RGBA premultiplicado con primitivas suavizadas (OpenCV)
y texto (Pillow). Todas las capas gráficas del vídeo se dibujan con esto."""
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1920, 1080

# ── Paleta (azul / blanco / tonos oscuros) ──
NAVY = (8, 16, 30)
PANEL = (12, 24, 42)
ACCENT = (46, 168, 255)     # azul eléctrico
CYAN = (92, 225, 230)
WHITE = (242, 246, 250)
MUTED = (143, 163, 184)
WARN = (255, 196, 92)       # ámbar, solo para fuerza/flechas en el esquema


def font(name, size):
    return _font(name, int(size))


@lru_cache(maxsize=256)
def _font(name, size):
    files = {
        "black": "InterDisplay-Black.otf", "bold": "InterDisplay-Bold.otf",
        "semi": "InterDisplay-SemiBold.otf", "dmed": "InterDisplay-Medium.otf",
        "light": "InterDisplay-Light.otf",
        "text": "Inter-Regular.otf", "textmed": "Inter-Medium.otf", "textsemi": "Inter-SemiBold.otf",
        "textbold": "Inter-Bold.otf",
        "mono": "JetBrainsMono-Medium.ttf", "monob": "JetBrainsMono-Bold.ttf", "monor": "JetBrainsMono-Regular.ttf",
    }
    return ImageFont.truetype(str(FONTS / files[name]), size)


# ── easing ──
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, dur):
    return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x, s=1.4):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def fade_io(t, t0, t1, fi=0.35, fo=0.35):
    """Opacidad 0→1→0 para un elemento visible entre t0 y t1."""
    if t < t0 or t > t1:
        return 0.0
    return min(ease_out(prog(t, t0, fi)), ease_out(1 - prog(t, t1 - fo, fo)) if fo > 0 else 1.0)


@lru_cache(maxsize=4096)
def text_image(txt, fname, size, color, tracking=0):
    """Rasteriza un texto (RGBA recto) y lo devuelve premultiplicado como float32."""
    f = font(fname, size)
    if tracking:
        widths = [f.getlength(c) + tracking for c in txt]
        wpx = int(sum(widths)) + 4
    else:
        wpx = int(f.getlength(txt)) + 4
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (max(wpx, 1), asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tracking:
        x = 0
        for c, wc in zip(txt, widths):
            d.text((x, 0), c, font=f, fill=color + (255,))
            x += wc
    else:
        d.text((0, 0), txt, font=f, fill=color + (255,))
    a = np.asarray(img).astype(np.float32) / 255.0
    a[..., :3] *= a[..., 3:4]
    return a, asc


def text_width(txt, fname, size, tracking=0):
    f = font(fname, size)
    return f.getlength(txt) + tracking * len(txt)


def wrap(txt, fname, size, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        cand = (cur + " " + w_).strip()
        if text_width(cand, fname, size) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    """Capa RGBA premultiplicada en float32 (0..1)."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.float32)

    # composición "over" de un parche premultiplicado en (x, y)
    def blit(self, patch, x, y, opacity=1.0):
        if opacity <= 0.003:
            return
        x, y = int(round(x)), int(round(y))
        ph, pw = patch.shape[:2]
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + pw, self.w), min(y + ph, self.h)
        if x0 >= x1 or y0 >= y1:
            return
        p = patch[y0 - y:y1 - y, x0 - x:x1 - x]
        if opacity < 1:
            p = p * opacity
        dst = self.a[y0:y1, x0:x1]
        dst *= (1 - p[..., 3:4])
        dst += p

    def _shape(self, bbox, draw_fn, color, opacity):
        """Dibuja con OpenCV en un parche local opaco y lo compone con opacidad."""
        x0, y0, x1, y1 = [int(v) for v in bbox]
        x0, y0 = max(x0 - 4, 0), max(y0 - 4, 0)
        x1, y1 = min(x1 + 4, self.w), min(y1 + 4, self.h)
        if x0 >= x1 or y0 >= y1 or opacity <= 0.003:
            return
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        draw_fn(m, x0, y0)
        cov = m.astype(np.float32)[..., None] / 255.0
        patch = np.concatenate([cov * (np.array(color, np.float32) / 255.0), cov], axis=2)
        self.blit(patch, x0, y0, opacity)

    def line(self, p, q, color, width=2, opacity=1.0):
        bb = (min(p[0], q[0]) - width, min(p[1], q[1]) - width, max(p[0], q[0]) + width, max(p[1], q[1]) + width)
        self._shape(bb, lambda m, ox, oy: cv2.line(
            m, _pt(p, ox, oy), _pt(q, ox, oy), 255, width, cv2.LINE_AA, shift=4), color, opacity)

    def polyline(self, pts, color, width=2, opacity=1.0, closed=False):
        pts = np.asarray(pts, np.float32)
        if len(pts) < 2:
            return
        bb = (pts[:, 0].min() - width, pts[:, 1].min() - width, pts[:, 0].max() + width, pts[:, 1].max() + width)
        self._shape(bb, lambda m, ox, oy: cv2.polylines(
            m, [np.round((pts - [ox, oy]) * 16).astype(np.int32)], closed, 255, width, cv2.LINE_AA, shift=4),
            color, opacity)

    def poly(self, pts, color, opacity=1.0):
        pts = np.asarray(pts, np.float32)
        bb = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
        self._shape(bb, lambda m, ox, oy: cv2.fillPoly(
            m, [np.round((pts - [ox, oy]) * 16).astype(np.int32)], 255, cv2.LINE_AA, shift=4), color, opacity)

    def circle(self, c, r, color, width=-1, opacity=1.0):
        bb = (c[0] - r - 3, c[1] - r - 3, c[0] + r + 3, c[1] + r + 3)
        self._shape(bb, lambda m, ox, oy: cv2.circle(
            m, _pt(c, ox, oy), int(r * 16), 255, width, cv2.LINE_AA, shift=4), color, opacity)

    def rect(self, x0, y0, x1, y1, color, opacity=1.0, radius=0, width=-1):
        if radius <= 0:
            if width < 0:
                self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, opacity)
            else:
                self.polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, width, opacity, closed=True)
            return
        r = min(radius, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = []
        for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(7):
                ang = np.radians(a0 + k * 15)
                pts.append((cx + r * np.cos(ang), cy + r * np.sin(ang)))
        if width < 0:
            self.poly(pts, color, opacity)
        else:
            self.polyline(pts, color, width, opacity, closed=True)

    def arrow(self, p, q, color, width=3, head=14, opacity=1.0):
        p, q = np.array(p, float), np.array(q, float)
        d = q - p
        n = np.linalg.norm(d)
        if n < 1:
            return
        u = d / n
        v = np.array([-u[1], u[0]])
        base = q - u * head
        self.line(p, base + u * 2, color, width, opacity)
        self.poly([q, base + v * head * 0.55, base - v * head * 0.55], color, opacity)

    def text(self, x, y, txt, fname, size, color=WHITE, opacity=1.0, anchor="lt", tracking=0):
        """anchor: l/m/r + t/m/b/s (s = línea base)."""
        if not txt or opacity <= 0.003:
            return 0
        img, asc = text_image(txt, fname, int(size), tuple(color), tracking)
        th, tw = img.shape[:2]
        ax, ay = anchor[0], anchor[1]
        if ax == "m":
            x -= tw / 2
        elif ax == "r":
            x -= tw
        if ay == "m":
            y -= th / 2
        elif ay == "b":
            y -= th
        elif ay == "s":
            y -= asc
        self.blit(img, x, y, opacity)
        return tw

    def gradient_v(self, x0, y0, x1, y1, color, a_top, a_bot):
        h = int(y1 - y0)
        if h <= 0:
            return
        al = np.linspace(a_top, a_bot, h, dtype=np.float32)[:, None, None]
        patch = np.empty((h, int(x1 - x0), 4), np.float32)
        patch[..., :3] = np.array(color, np.float32) / 255.0
        patch[..., 3:] = 1
        self.blit(patch * al, x0, y0)

    def gradient_h(self, x0, y0, x1, y1, color, a_l, a_r):
        w = int(x1 - x0)
        if w <= 0:
            return
        al = np.linspace(a_l, a_r, w, dtype=np.float32)[None, :, None]
        patch = np.empty((int(y1 - y0), w, 4), np.float32)
        patch[..., :3] = np.array(color, np.float32) / 255.0
        patch[..., 3:] = 1
        self.blit(patch * al, x0, y0)


def _pt(p, ox, oy):
    return (int(round((p[0] - ox) * 16)), int(round((p[1] - oy) * 16)))


def composite(frame_u8, canvas):
    """frame (H,W,3 uint8) + capa premultiplicada → uint8."""
    f = frame_u8.astype(np.float32) / 255.0
    a = canvas.a
    out = f * (1 - a[..., 3:4]) + a[..., :3]
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)


def brackets(cv, x0, y0, x1, y1, color=ACCENT, L=26, width=2, opacity=1.0):
    """Esquinas técnicas tipo visor."""
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        cv.polyline([(cx + sx * L, cy), (cx, cy), (cx, cy + sy * L)], color, width, opacity)


@lru_cache(maxsize=4)
def grid_layer(step=60, alpha=0.06, major=4):
    """Rejilla técnica estática (premultiplicada)."""
    cv = Canvas()
    for i, x in enumerate(range(0, W, step)):
        cv.line((x, 0), (x, H), WHITE, 1, alpha * (2.2 if i % major == 0 else 1))
    for i, y in enumerate(range(0, H, step)):
        cv.line((0, y), (W, y), WHITE, 1, alpha * (2.2 if i % major == 0 else 1))
    return cv.a.copy()


def vignette(strength=0.45):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    return np.clip(1 - strength * d ** 2.2, 0, 1)[..., None]
