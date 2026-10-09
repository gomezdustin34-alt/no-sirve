"""Paso 2 · Render del vídeo final a partir de la EDL (edl.py).

    python scripts/render.py                    → salida/grua_hidraulica_final.mp4 (+ subtítulos, stems)
    python scripts/render.py --jobs 4           → render en paralelo por bloques
    python scripts/render.py --stills 3 12.5    → solo fotogramas PNG de comprobación
    python scripts/render.py --musica pista.mp3 → usa una música con licencia en vez de la sintetizada
    python scripts/render.py --sin-subtitulos   → no quema subtítulos en la imagen
"""
import argparse
import json
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import edl
import gfx
import mix
import sound
from gfx import (ACCENT, CYAN, MUTED, NAVY, WARN, WHITE, Canvas, brackets, clamp, ease_in_out,
                 ease_out, ease_out_back, fade_io, prog, wrap)

ROOT = Path(__file__).resolve().parent.parent
PRE = ROOT / "trabajo" / "pre"
OUT = ROOT / "salida"
FPS = 30
W, H = 1920, 1080
PORTRAIT = {"v2", "v3", "v6", "v7", "v8", "v9"}
CLIP_X, CLIP_Y, CW, CH_ = 150, 28, 576, 1024
PX = 870            # columna del panel lateral
INSET = (1330, 300, 470, 470)
BURN_SUBS = True

TRACK = None


def track_at(st):
    global TRACK
    if TRACK is None:
        TRACK = json.loads((ROOT / "trabajo" / "track_v6.json").read_text())
    i = int(clamp(round(st * FPS), 0, len(TRACK) - 1))
    p = TRACK[i]
    return p["x"], p["y"], p["s"] / 90.0


def part_pos(part, st):
    x, y, s = track_at(st)
    ox, oy = edl.V6_PARTS[part]
    return x + ox * s, y + oy * s


# ───────────────────────── Línea de tiempo ─────────────────────────
class Seg:
    def __init__(self, d, start_f):
        self.d = d
        self.id = d["id"]
        self.layout = d["layout"]
        self.src = d.get("src")
        self.speed = d.get("speed", 1.0)
        if self.layout == "graphic":
            self.n_main = round(d["dur"] * FPS)
        else:
            self.n_main = round((d["tout"] - d["tin"]) / self.speed * FPS)
        self.n = self.n_main + round(d.get("hold", 0) * FPS)
        self.f0 = start_f
        self.t0 = start_f / FPS
        self.dur = self.n / FPS

    def src_t(self, i):
        return self.d["tin"] + min(i, self.n_main - 1) / FPS * self.speed


def build_timeline():
    segs, f = [], 0
    for d in edl.SEGMENTS:
        s = Seg(d, f)
        segs.append(s)
        f += s.n
    # capítulos: instante de inicio de cada uno
    chap_t0 = {}
    for s in segs:
        c = s.d.get("chapter")
        if c and c not in chap_t0:
            chap_t0[c] = s.t0
    # paneles / tarjetas heredados (en tiempo global)
    prev_panel, prev_cards = [], []
    for s in segs:
        own = [(s.t0 + it[1],) + tuple(it) for it in s.d.get("panel", [])]
        if s.d.get("panel_static"):
            s.panel = [(-1e9,) + p[1:] for p in prev_panel]
        elif s.d.get("panel_keep_prev"):
            s.panel = [(-1e9,) + p[1:] for p in prev_panel] + own
        else:
            s.panel = own
        prev_panel = s.panel
        own_c = [(s.t0 + c[0], c[1], c[2]) for c in s.d.get("cards", [])]
        s.cards = ([(-1e9, c[1], c[2]) for c in prev_cards] if s.d.get("cards_keep") else []) + own_c
        prev_cards = s.cards
    return segs, chap_t0


def build_cues(segs):
    cues = []
    for s in segs:
        if s.layout == "graphic" or not s.d.get("audio", True) or s.speed != 1.0:
            continue
        for c0, c1, txt in edl.CUES.get(s.src, []):
            a, b = max(c0, s.d["tin"]), min(c1, s.d["tout"])
            if b - a > 0.25:
                cues.append((s.t0 + a - s.d["tin"], s.t0 + b - s.d["tin"], txt))
    return cues


# ───────────────────────── Lectura de vídeo ─────────────────────────
class Reader:
    def __init__(self, seg, skip=0):
        d = seg.d
        self.w, self.h = (CW, CH_) if seg.src in PORTRAIT else (1024, 576)
        vf = [f"scale={self.w}:{self.h}:flags=lanczos"]
        if seg.speed != 1.0:
            vf += [f"setpts=(PTS-STARTPTS)/{seg.speed}",
                   "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"]
        else:
            vf += ["setpts=PTS-STARTPTS", "fps=30"]
        tin = d["tin"]
        if skip and seg.speed == 1.0:
            tin += skip / FPS
            skip = 0
        self.skip = skip
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{tin:.3f}", "-t", f"{d['tout'] - tin + 0.3:.3f}",
               "-i", str(PRE / f"{seg.src}.mp4"), "-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.last = None
        for _ in range(self.skip):
            self.read()

    def read(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3)
        return self.last if self.last is not None else np.zeros((self.h, self.w, 3), np.uint8)

    def close(self):
        self.p.stdout.close()
        self.p.kill()


# ───────────────────────── Cámara virtual (zoom) ─────────────────────────
def zoom_at(seg, lt, st):
    kf = seg.d.get("zoom") or [(0, 1.0, None, None)]

    def center(k):
        if isinstance(k[2], str) and k[2].startswith("track:"):
            return part_pos(k[2][6:], st)
        if k[2] is None:
            return (CW / 2, CH_ / 2) if seg.src in PORTRAIT else (512, 288)
        return k[2], k[3]

    if lt <= kf[0][0]:
        return (kf[0][1],) + tuple(center(kf[0]))
    for a, b in zip(kf, kf[1:]):
        if a[0] <= lt <= b[0]:
            u = ease_in_out((lt - a[0]) / max(b[0] - a[0], 1e-6))
            ca, cb = center(a), center(b)
            return (a[1] + (b[1] - a[1]) * u, ca[0] + (cb[0] - ca[0]) * u, ca[1] + (cb[1] - ca[1]) * u)
    return (kf[-1][1],) + tuple(center(kf[-1]))


def warp(frame, scale, x0, y0, ow, oh, interp=cv2.INTER_CUBIC):
    M = np.array([[scale, 0, -x0 * scale], [0, scale, -y0 * scale]], np.float32)
    return cv2.warpAffine(frame, M, (ow, oh), flags=interp, borderMode=cv2.BORDER_REFLECT)


def sharpen(img, sigma=1.2, amount=0.35):
    blur = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1 + amount, blur, -amount, 0)


GRID = None
VIGN = None


def tech_bg(frame=None):
    """Fondo azul oscuro con rejilla; si hay fotograma, se usa desenfocado debajo."""
    global GRID, VIGN
    if GRID is None:
        GRID = gfx.grid_layer()
        VIGN = gfx.vignette(0.55)
    base = np.empty((H, W, 3), np.float32)
    base[:] = np.array(NAVY, np.float32) / 255
    if frame is not None:
        h, w = frame.shape[:2]
        band = frame[int(h * 0.3):int(h * 0.3) + int(w * 9 / 16)] if h > w else frame
        small = cv2.resize(band, (48, 27), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 1.6)
        big = cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
        base = base * 0.62 + big * 0.30
    base = base * VIGN
    base = base * (1 - GRID[..., 3:4]) + GRID[..., :3]
    return base


def render_base(seg, frame, lt, st):
    """Devuelve (imagen float 0..1, mapeo fuente→pantalla, info)."""
    if seg.layout == "graphic":
        return tech_bg(), None, {}
    z, cx, cy = zoom_at(seg, lt, st)
    if seg.layout == "portrait":
        sw, sh = CW / z, CH_ / z
        x0, y0 = clamp(cx - sw / 2, 0, CW - sw), clamp(cy - sh / 2, 0, CH_ - sh)
        clip = warp(frame, z, x0, y0, CW, CH_)
        if z > 1.15:
            clip = sharpen(clip, 1.0, 0.3)
        base = tech_bg(frame)
        base[CLIP_Y:CLIP_Y + CH_, CLIP_X:CLIP_X + CW] = clip.astype(np.float32) / 255
        mp = lambda x, y: (CLIP_X + (x - x0) * z, CLIP_Y + (y - y0) * z)
        return base, mp, {"z": z}
    if seg.layout == "full":
        sw, sh = 1024 / z, 576 / z
        x0, y0 = clamp(cx - sw / 2, 0, 1024 - sw), clamp(cy - sh / 2, 0, 576 - sh)
        S = W / 1024 * z
        img = sharpen(warp(frame, S, x0, y0, W, H), 1.3, 0.4)
        mp = lambda x, y: ((x - x0) * S, (y - y0) * S)
        return img.astype(np.float32) / 255, mp, {"z": z}
    if seg.layout == "crop":
        cw = seg.d["crop_w"] / z
        chh = cw * 9 / 16
        S = W / cw
        shift = seg.d.get("crop_shift", 0)
        x0 = clamp(cx - cw / 2 - shift / S, 0, CW - cw)
        y0 = clamp(cy - chh / 2, 0, CH_ - chh)
        img = warp(frame, S, x0, y0, W, H, cv2.INTER_LANCZOS4)
        img = sharpen(img, 2.0, 0.55)
        mp = lambda x, y: ((x - x0) * S, (y - y0) * S)
        return img.astype(np.float32) / 255, mp, {"z": z, "S": S}
    raise ValueError(seg.layout)


# ───────────────────────── Elementos gráficos ─────────────────────────
def draw_hud(cv, t, total, chap_t0, chapter, a):
    if a <= 0:
        return
    cv.text(W - 60, 34, "GRÚA HIDRÁULICA  ·  PRINCIPIO DE PASCAL", "mono", 17, MUTED, 0.85 * a, "rt", tracking=1)
    if chapter:
        cv.text(W - 60, 60, f"{chapter:02d} / 06", "monob", 17, ACCENT, a, "rt", tracking=2)
    y = H - 5
    cv.rect(0, y, W, H, WHITE, 0.08 * a)
    cv.rect(0, y, W * t / total, H, ACCENT, 0.9 * a)
    for c, t0 in chap_t0.items():
        x = W * t0 / total
        cv.rect(x - 1, y - 4, x + 1, H, WHITE, 0.5 * a)


def chapter_portrait(cv, ch, ct):
    """Bloque de capítulo en el panel lateral. ct = tiempo desde el inicio del capítulo."""
    title = edl.CH[ch]
    p = ease_out(prog(ct, 0.0, 0.6))
    cv.text(PX, 74, f"CAPÍTULO {ch:02d}", "monob", 22, ACCENT, p, tracking=4)
    x_off = (1 - p) * 40
    cv.text(PX + x_off, 104, title, "bold", 62, WHITE, p)
    lw = 140 * ease_out(prog(ct, 0.25, 0.7))
    cv.rect(PX, 190, PX + lw, 194, ACCENT, 1)
    cv.rect(PX + lw + 8, 191, PX + lw + 8 + 560 * ease_out(prog(ct, 0.4, 1.0)), 193, WHITE, 0.15)


def chapter_full(cv, ch, ct, tag=None):
    a = 1.0
    cv.gradient_v(0, 0, W, 260, NAVY, 0.72, 0.0)
    p = ease_out(prog(ct, 0.0, 0.6))
    cv.text(60, 46, f"{ch:02d}", "monob", 26, ACCENT, p * a, tracking=2)
    cv.rect(108, 58, 108 + 40 * p, 60, ACCENT, a)
    cv.text(164 - (1 - p) * 30, 38, edl.CH[ch], "bold", 44, WHITE, p * a)
    if tag:
        t0, t1, l1, l2 = tag
        o = fade_io(ct, t0 + 0.4, t1, 0.5, 0.5)
        cv.text(164, 98, l1, "mono", 20, CYAN, o, tracking=3)
        cv.text(164, 126, l2, "text", 22, MUTED, o)


def lower_third(cv, text, t, t0, t1, layout):
    o = fade_io(t, t0, t1, 0.45, 0.45)
    if o <= 0:
        return
    p = ease_out(prog(t, t0, 0.5))
    if layout == "portrait":
        x, y = PX, 218
        cv.rect(x, y, x + 6, y + 62, ACCENT, o)
        cv.text(x + 22, y + 2, "ROL", "mono", 17, MUTED, o, tracking=3)
        cv.text(x + 22 + (1 - p) * 30, y + 22, text, "semi", 34, WHITE, o)
    else:
        f_w = gfx.text_width(text, "semi", 36) + 70
        x, y = 60, 770
        cv.rect(x, y, x + f_w * p, y + 84, NAVY, 0.78 * o, radius=8)
        cv.rect(x, y, x + 6, y + 84, ACCENT, o)
        cv.text(x + 26, y + 12, "ROL", "mono", 17, CYAN, o * p, tracking=3)
        cv.text(x + 26, y + 34, text, "semi", 36, WHITE, o * p)


def draw_panel(cv, items, t, top=300, width=920):
    y = top
    for it in items:
        ta, kind = it[0], it[1]
        if t < ta:
            continue
        p = ease_out(prog(t, ta, 0.55))
        dx = (1 - p) * 40
        if kind == "text":
            _, _, _, title, body = it
            cv.text(PX + dx, y, title, "monob", 20, ACCENT, p, tracking=3)
            yy = y + 36
            for ln in wrap(body, "dmed", 38, width):
                cv.text(PX + dx, yy, ln, "dmed", 38, WHITE, p)
                yy += 50
            y = yy + 34
        elif kind == "kv":
            _, _, _, key, val = it
            cv.rect(PX, y + 4, PX + 3, y + 84, ACCENT, p)
            cv.text(PX + 22 + dx, y, key, "mono", 19, CYAN, p, tracking=3)
            yy = y + 28
            for ln in wrap(val, "semi", 36, width - 40):
                cv.text(PX + 22 + dx, yy, ln, "semi", 36, WHITE, p)
                yy += 46
            y = yy + 26
        elif kind == "step":
            _, _, _, num, title, desc = it
            cx, cy = PX + 30, y + 30
            cv.circle((cx, cy), 29, ACCENT, 2, p)
            cv.text(cx, cy, num, "monob", 22, ACCENT, p, "mm")
            cv.text(PX + 80 + dx, y + 2, title, "bold", 38, WHITE, p)
            cv.text(PX + 80 + dx, y + 50, desc, "text", 25, MUTED, p)
            # conector hacia el siguiente paso
            cv.rect(cx - 1, cy + 34, cx + 1, cy + 34 + 62 * p, ACCENT, 0.35 * p)
            y += 128
        elif kind == "result":
            _, _, _, key, val = it
            pp = ease_out_back(prog(t, ta, 0.5))
            cv.circle((PX + 30, y + 44), 28 * pp, ACCENT, -1, p)
            k = prog(t, ta + 0.2, 0.35)
            if k > 0:
                pts = [(PX + 17, y + 45), (PX + 27, y + 55), (PX + 45, y + 33)]
                seg_pts = pts[:2] if k < 0.5 else pts
                end = np.array(pts[0]) + (np.array(pts[1]) - pts[0]) * min(1, k * 2) if k < 0.5 else \
                    np.array(pts[1]) + (np.array(pts[2]) - pts[1]) * (k - 0.5) * 2
                cv.polyline(seg_pts[:-1] + [tuple(end)], WHITE, 4, p)
            cv.text(PX + 78 + dx, y + 4, key, "monob", 20, ACCENT, p, tracking=3)
            cv.text(PX + 78 + dx, y + 32, val, "bold", 40, WHITE, p)
            y += 120
        elif kind == "quote":
            _, _, _, key, val = it
            cv.text(PX - 6, y - 40, "“", "black", 130, ACCENT, p * 0.9)
            cv.text(PX + 80, y + 6, key, "monob", 20, ACCENT, p, tracking=3)
            yy = y + 52
            for ln in wrap(val, "dmed", 48, width - 80):
                cv.text(PX + 80 + dx, yy, ln, "dmed", 48, WHITE, p)
                yy += 62
            y = yy + 20


def draw_checklist(cv, items, lt, x=PX, top=300):
    cv.text(x, top, "MATERIALES", "monob", 20, ACCENT, 1, tracking=4)
    y = top + 44
    for ta, label in items:
        if lt < ta:
            break
        p = ease_out(prog(lt, ta, 0.4))
        cv.rect(x, y + 4, x + 30, y + 34, ACCENT, p, radius=4, width=2)
        k = prog(lt, ta + 0.1, 0.3)
        if k > 0:
            cv.rect(x + 3, y + 7, x + 27, y + 31, ACCENT, 0.9 * p, radius=3)
            pts = [(x + 8, y + 19), (x + 14, y + 26), (x + 25, y + 12)]
            cv.polyline(pts[:2] if k < 0.5 else pts, NAVY, 3, p)
        cv.text(x + 48 + (1 - p) * 30, y + 2, label, "textmed", 30, WHITE, p)
        y += 56


def draw_cards(cv, cards, t):
    y = 150
    for ta, key, val in cards:
        if t < ta:
            continue
        p = ease_out(prog(t, ta, 0.5))
        x1 = W - 60
        wv = max(gfx.text_width(val, "bold", 44), gfx.text_width(key, "mono", 19, 3)) + 70
        x0 = x1 - wv + (1 - p) * 80
        cv.rect(x0, y, x1, y + 112, NAVY, 0.82 * p, radius=10)
        cv.rect(x0, y, x0 + 6, y + 112, ACCENT, p)
        cv.text(x0 + 28, y + 16, key, "mono", 19, CYAN, p, tracking=3)
        cv.text(x0 + 28, y + 44, val, "bold", 44, WHITE, p)
        y += 132


def sub_words(text):
    out = []
    for w_ in text.split():
        core = w_.strip(".,;:«»¡!¿?()…")
        hl = any(core.lower() == k.lower() for k in edl.KEYWORDS)
        out.append((w_, CYAN if hl else WHITE))
    return out


def draw_subtitle(cv, cue_txt, o, cx, y_bottom, maxw, size):
    fname = "textsemi"
    lines = wrap(cue_txt, fname, size, maxw)
    lh = size * 1.32
    widths = [gfx.text_width(l, fname, size) for l in lines]
    bw = max(widths) + 44
    bh = lh * len(lines) + 22
    y0 = y_bottom - bh
    cv.rect(cx - bw / 2, y0, cx + bw / 2, y_bottom, NAVY, 0.74 * o, radius=10)
    y = y0 + 11
    for ln, lw in zip(lines, widths):
        x = cx - lw / 2
        space = gfx.text_width(" ", fname, size)
        for word, col in sub_words(ln):
            cv.text(x, y, word, fname, size, col, o)
            x += gfx.text_width(word, fname, size) + space
        y += lh


def label_tag(cv, anchor, text, o, side=1, dy=-40):
    ax, ay = anchor
    lx, ly = ax + side * 70, ay + dy
    cv.circle((ax, ay), 9, NAVY, -1, 0.7 * o)
    cv.circle((ax, ay), 8, ACCENT, 2, o)
    cv.circle((ax, ay), 3, WHITE, -1, o)
    cv.polyline([(ax + side * 8, ay - 3), (lx, ly), (lx + side * 18, ly)], ACCENT, 2, o)
    tw = gfx.text_width(text, "textsemi", 26)
    bx0 = lx + side * 18 if side > 0 else lx - 18 - tw - 28
    cv.rect(bx0, ly - 22, bx0 + tw + 28, ly + 22, NAVY, 0.86 * o, radius=6)
    cv.text(bx0 + 14, ly, text, "textsemi", 26, WHITE, o, "lm")


def arc_points(cx, cy, r, a0, a1, n=48):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)


def draw_lift_arc(cv, mp, st, scale_px, t_lift0=37.45, t_lift1=38.6, o=1.0, rfac=1.0, label=True):
    """Arco de trayectoria de la punta del brazo durante la elevación (sobre el vídeo)."""
    k = ease_in_out(prog(st, t_lift0, t_lift1 - t_lift0))
    if k <= 0:
        return
    px_, py_ = part_pos("columna", st)
    _, _, s = track_at(st)
    pivot = mp(px_, py_ - 40 * s)
    r = 150 * s * scale_px * rfac
    a_low, a_high = 22, -30
    pts = arc_points(pivot[0], pivot[1], r, a_low, a_low + (a_high - a_low) * k)
    cv.polyline(pts, ACCENT, 4, 0.9 * o)
    cv.polyline(pts, WHITE, 1, 0.6 * o)
    if len(pts) > 2:
        cv.arrow(pts[-3], pts[-1] + (pts[-1] - pts[-3]) * 1.5, ACCENT, 4, 24, o)
    # líneas de velocidad
    for j, dr in enumerate((-0.12, 0, 0.12)):
        p2 = arc_points(pivot[0], pivot[1], r * (1.12 + dr * 0.4), a_low + (a_high - a_low) * max(0, k - 0.25),
                        a_low + (a_high - a_low) * k, 12)
        cv.polyline(p2, WHITE, 2, 0.35 * o * (1 - abs(dr) * 3))
    tip = pts[-1]
    if label:
        cv.text(tip[0] + 30, tip[1] - 30, "ELEVACIÓN", "monob", 24, WHITE, o * ease_out(prog(k, 0.2, 0.3)), "lb",
            tracking=4)


def draw_inset(cv, img, seg, frame, mp, lt, st, gt):
    spec = seg.d["inset"]
    o = fade_io(lt, spec["t0"], spec["t1"], 0.5, 0.0)
    if o <= 0:
        return
    x, y, w, h = INSET
    z = spec["z"]
    cx, cy = part_pos(spec["part"], st)
    sw = w / z
    x0, y0 = clamp(cx - sw / 2, 0, CW - sw), clamp(cy - sw / 2, 0, CH_ - sw)
    p = ease_out(prog(lt, spec["t0"], 0.5))
    det = sharpen(warp(frame, z, x0, y0, w, h, cv2.INTER_LANCZOS4), 1.2, 0.45).astype(np.float32) / 255
    region = img[y:y + h, x:x + w]
    img[y:y + h, x:x + w] = region * (1 - o * p) + det * o * p
    # marco + conectores con la zona ampliada del clip
    a0, a1 = mp(x0, y0), mp(x0 + sw, y0 + sw)
    cv.rect(a0[0], a0[1], a1[0], a1[1], ACCENT, 0.9 * o, width=2)
    cv.line((a1[0], a0[1]), (x, y), ACCENT, 1, 0.22 * o * p)
    cv.line((a1[0], a1[1]), (x, y + h), ACCENT, 1, 0.22 * o * p)
    cv.rect(x, y, x + w, y + h, ACCENT, o, width=2)
    brackets(cv, x - 8, y - 8, x + w + 8, y + h + 8, WHITE, 22, 2, 0.8 * o)
    cv.text(x, y - 38, f"DETALLE  ×{z:.1f}", "monob", 18, ACCENT, o, tracking=3)
    imp = lambda X, Y: (x + (X - x0) * z, y + (Y - y0) * z)
    for ta, text, part in seg.d.get("labels", []):
        oo = o * ease_out(prog(lt, max(ta, spec["t0"] + 0.4), 0.4))
        if oo <= 0:
            continue
        ax, ay = imp(*part_pos(part, st))
        if not (x - 2 <= ax <= x + w + 2 and y - 2 <= ay <= y + h + 2):
            continue
        side = -1 if ax < x + w * 0.55 else 1
        if part == "brazo":
            side, dy = 1, -50
        elif part == "manguera":
            dy = 50
        else:
            dy = -46 if part != "base" else 56
        label_tag(cv, (ax, ay), text, oo, side, dy)
    if "inset_arc" in seg.d:
        imz = lambda X, Y: imp(X, Y)
        draw_lift_arc(cv, imz, st, z, 37.35, 38.6, o, rfac=0.62, label=False)


def draw_fx(cv, img, seg, mp, info, lt, st, gt):
    fx = seg.d.get("fx", [])
    dur = seg.dur
    if "hook_brackets" in fx:
        cv.rect(0, 0, W, 112, (0, 0, 0), 1)
        cv.rect(0, H - 112, W, H, (0, 0, 0), 1)
        cx, cy = mp(*part_pos("grua", st))
        bw, bh = 0.30 * W, 0.36 * H
        a = ease_out(prog(lt, 0.05, 0.35)) if seg.id == "hook_a" else 1.0
        brackets(cv, cx - bw - 30 * (1 - a), cy - bh - 30 * (1 - a), cx + bw + 30 * (1 - a), cy + bh * 0.8 + 30 * (1 - a),
                 ACCENT, 36, 3, a * 0.9)
        cv.text(80, H - 200, "SISTEMA HIDRÁULICO", "monob", 22, WHITE, 0.9 * a, tracking=5)
        cv.text(80, H - 166, "JERINGAS · MANGUERAS · AGUA", "monob", 20, CYAN, 0.95 * a, tracking=3)
    if "lift_arc" in fx:
        draw_lift_arc(cv, mp, st, info["S"])
    if "lift_arc_replay" in fx:
        draw_lift_arc(cv, mp, st, info["S"], 37.4, 38.6)
    if "slowmo_tag" in fx:
        blink = 0.5 + 0.5 * math.cos(lt * 6)
        cv.circle((W - 340, 56), 7, ACCENT, -1, blink)
        cv.text(W - 322, 56, "CÁMARA LENTA  0.4×", "monob", 22, WHITE, 0.9, "lm", tracking=3)
    if "replay_tag" in fx:
        o = fade_io(lt, 0.0, dur, 0.3, 0.3)
        blink = 0.5 + 0.5 * math.cos(lt * 6)
        cv.circle((W - 370, 56), 7, ACCENT, -1, blink * o)
        cv.text(W - 352, 56, "REPETICIÓN  ·  0.35×", "monob", 22, WHITE, 0.9 * o, "lm", tracking=3)
    if "question" in fx:
        q = ease_out(prog(lt, 0.15, 0.5))
        # desenfoque + oscurecido progresivo bajo el título
        blur = cv2.GaussianBlur(img, (0, 0), 1 + 7 * q)
        img[:] = img * (1 - q) + blur * q
        cv.rect(0, 0, W, H, NAVY, 0.55 * q)
        cv.rect(0, 0, W, 112, (0, 0, 0), 1)
        cv.rect(0, H - 112, W, H, (0, 0, 0), 1)
        p1 = ease_out(prog(lt, 0.25, 0.45))
        p2 = ease_out_back(prog(lt, 0.45, 0.5), 1.2)
        p3 = ease_out(prog(lt, 0.7, 0.45))
        cv.text(W / 2, 330 + (1 - p1) * 30, "¿CÓMO PUEDE UNA SIMPLE", "bold", 70, WHITE, p1, "mt", tracking=4)
        size = 190 * (1.12 - 0.12 * p2)
        cv.text(W / 2, 545, "JERINGA", "black", size, ACCENT, clamp(p2), "mm", tracking=10)
        ul = 520 * ease_out(prog(lt, 0.7, 0.5))
        cv.rect(W / 2 - ul / 2, 652, W / 2 + ul / 2, 658, WHITE, 0.9 * clamp(p2))
        cv.text(W / 2, 690 + (1 - p3) * 30, "LEVANTAR UNA CARGA?", "bold", 70, WHITE, p3, "mt", tracking=4)
    if "title_card" in fx:
        cv.rect(0, 0, W, H, NAVY, 0.70)
        g = gfx.grid_layer()
        cv.blit(g, 0, 0, 0.8)
        p = ease_in_out(prog(lt, 0.25, 0.9))
        # líneas técnicas que se abren desde el centro
        lw = 760 * ease_out(prog(lt, 0.1, 0.8))
        cv.rect(W / 2 - lw, 424, W / 2 + lw, 426, ACCENT, 0.9)
        cv.rect(W / 2 - lw * 0.6, 640, W / 2 + lw * 0.6, 641, WHITE, 0.35)
        # título revelado con barrido
        tmp = Canvas()
        tmp.text(W / 2, 545, "GRÚA HIDRÁULICA", "black", 150, WHITE, 1, "mm", tracking=8)
        edge = int(-40 + (W + 80) * p)
        tmp.a[:, edge:] = 0
        cv.blit(tmp.a, 0, 0, 1.0)
        if 0 < p < 1:
            cv.rect(edge - 2, 470, edge + 2, 620, CYAN, 0.9)
        ps = ease_out(prog(lt, 1.15, 0.7))
        cv.text(W / 2, 668 + (1 - ps) * 16, "Aplicación del principio de Pascal", "light", 50, WHITE, ps, "mt",
                tracking=2)
        pm = ease_out(prog(lt, 1.6, 0.6))
        cv.text(120, H - 120, "PROYECTO ACADÉMICO", "mono", 20, MUTED, pm, "lb", tracking=4)
        cv.text(W - 120, H - 120, "P = F / A", "monob", 26, ACCENT, pm, "rb", tracking=4)
        fo = prog(lt, dur - 0.35, 0.35)
        if fo > 0:
            cv.rect(0, 0, W, H, NAVY, fo * 0.6)
    if "end_card" in fx:
        cv.gradient_h(0, 0, 1250, H, NAVY, 0.94, 0.0)
        g = gfx.grid_layer()
        cv.blit(g * 0.6, 0, 0, 1)
        p1 = ease_out(prog(lt, 0.3, 0.8))
        cv.text(120 + (1 - p1) * 40, 170, "GRÚA HIDRÁULICA", "black", 92, WHITE, p1)
        cv.text(122, 285, "Aplicación del principio de Pascal", "light", 40, WHITE, ease_out(prog(lt, 0.7, 0.7)))
        cv.rect(122, 360, 122 + 420 * ease_out(prog(lt, 0.9, 0.9)), 364, ACCENT, 1)
        cv.text(122, 400, "EQUIPO DE TRABAJO", "monob", 21, ACCENT, ease_out(prog(lt, 1.3, 0.5)), tracking=4)
        y = 446
        for k, (role, name) in enumerate(edl.NOMBRES.items()):
            pk = ease_out(prog(lt, 1.6 + k * 0.25, 0.5))
            cv.text(122 + (1 - pk) * 30, y, role, "textmed", 30, WHITE, pk)
            if name:
                cv.text(122 + (1 - pk) * 30 + gfx.text_width(role, "textmed", 30) + 18, y + 3, name, "text", 27,
                        MUTED, pk)
            y += 52
        pm = ease_out(prog(lt, 3.4, 0.8))
        cv.text(122, H - 120, "PROYECTO ACADÉMICO  ·  GRÚA CON JERINGAS, MANGUERAS Y AGUA", "mono", 18, MUTED, pm,
                tracking=2)
        fo = prog(lt, dur - 1.3, 1.3)
        if fo > 0:
            cv.rect(0, 0, W, H, (0, 0, 0), ease_in_out(fo))


# ───────────────────────── Escena: principio de Pascal ─────────────────────────
def pascal_scene(cv, lt, dur):
    o_all = 1 - prog(lt, dur - 0.4, 0.4) * 0.0
    # Capítulo (versión de pantalla completa)
    chapter_full_lite(cv, 4, lt)
    # ─ Columna izquierda: enunciado y fórmula ─
    LX = 120
    p = ease_out(prog(lt, 0.6, 0.6))
    cv.text(LX, 200, "PRINCIPIO DE PASCAL", "monob", 24, ACCENT, p, tracking=5)
    yy = 244
    for ln in wrap("La presión aplicada a un líquido encerrado se transmite por igual a todos sus puntos.",
                   "dmed", 42, 760):
        cv.text(LX + (1 - p) * 30, yy, ln, "dmed", 42, WHITE, p)
        yy += 56
    # fórmula P = F / A
    pf = ease_out_back(prog(lt, 3.0, 0.6), 1.1)
    of = clamp(prog(lt, 3.0, 0.4))
    fy = 470
    xs = LX
    for tok, col in (("P", CYAN), (" = ", WHITE), ("F", WARN), (" / ", WHITE), ("A", ACCENT)):
        cv.text(xs, fy + (1 - pf) * 20, tok, "black", 140, col, of)
        xs += gfx.text_width(tok, "black", 140)
    legend = [("P", "presión", "Pa", CYAN), ("F", "fuerza", "N", WARN), ("A", "área del émbolo", "m²", ACCENT)]
    for k, (sym, name, unit, col) in enumerate(legend):
        pk = ease_out(prog(lt, 4.0 + 0.35 * k, 0.4))
        y = 660 + 46 * k
        cv.text(LX, y, sym, "monob", 28, col, pk)
        cv.text(LX + 44 + (1 - pk) * 20, y + 2, f"{name}  ({unit})", "text", 28, WHITE, pk * 0.9)
    # ecuaciones de la prensa hidráulica
    pe = ease_out(prog(lt, 10.5, 0.6))
    cv.rect(LX, 830, LX + 700 * pe, 832, WHITE, 0.25)
    cv.text(LX, 852, "P₁ = P₂   →   F₁ / A₁ = F₂ / A₂", "bold", 44, WHITE, pe)
    pe2 = ease_out(prog(lt, 12.5, 0.6))
    cv.text(LX, 918, "F₂ = F₁ · (A₂ / A₁)", "bold", 44, CYAN, pe2)
    # ─ Columna derecha: esquema de dos jeringas conectadas ─
    hydraulic_diagram(cv, lt)
    # nota final sobre la grúa
    pn = fade_io(lt, 15.6, dur, 0.6, 0.3)
    if pn > 0:
        bx, by = 1000, 840
        cv.rect(bx, by, 1810, by + 150, NAVY, 0.85 * pn, radius=10)
        cv.rect(bx, by, bx + 6, by + 150, ACCENT, pn)
        cv.text(bx + 30, by + 18, "EN NUESTRA GRÚA", "monob", 20, ACCENT, pn, tracking=4)
        yy = by + 52
        for ln in wrap("Al mover el émbolo de una jeringa, el agua transmite la presión por la manguera "
                       "y la otra jeringa mueve el brazo.", "text", 28, 740):
            cv.text(bx + 30, yy, ln, "text", 28, WHITE, pn)
            yy += 38


def chapter_full_lite(cv, ch, ct):
    p = ease_out(prog(ct, 0.0, 0.6))
    cv.text(120, 76, f"CAPÍTULO {ch:02d}", "monob", 22, ACCENT, p, tracking=4)
    cv.text(120 + (1 - p) * 30, 104, edl.CH[ch], "bold", 56, WHITE, p)


def hydraulic_diagram(cv, lt):
    """Dos jeringas unidas por una manguera con agua. Émbolo 1 (área A₁) y émbolo 2 (área A₂ = 4·A₁).
    Física: misma presión → F₂ = F₁·A₂/A₁ = 4·F₁; volumen conservado → d₂ = d₁·A₁/A₂ = d₁/4."""
    o = ease_out(prog(lt, 5.0, 0.8))
    if o <= 0:
        return
    d1, d2 = 64, 128                # diámetros → áreas en relación 1:4
    ax1, ay = 1080, 600             # jeringa 1 (cuerpo de ax1 a ax1+L1)
    L1 = 300
    ax2 = 1510
    L2 = 250
    k = ease_in_out(prog(lt, 7.6, 2.4))
    stroke1 = 150 * k
    stroke2 = stroke1 * (d1 / d2) ** 2
    liquid = (40, 120, 220)
    for (bx, L, d) in ((ax1, L1, d1), (ax2, L2, d2)):
        cv.rect(bx, ay - d / 2 - 6, bx + L, ay + d / 2 + 6, WHITE, 0.10 * o, radius=6)
        cv.rect(bx, ay - d / 2 - 6, bx + L, ay + d / 2 + 6, WHITE, 0.85 * o, radius=6, width=2)
    p1x = ax1 + 30 + stroke1                    # cara del émbolo 1
    cv.rect(p1x, ay - d1 / 2, ax1 + L1, ay + d1 / 2, liquid, 0.85 * o)
    p2x = ax2 + 60 + stroke2                    # cara del émbolo 2
    cv.rect(ax2, ay - d2 / 2, p2x, ay + d2 / 2, liquid, 0.85 * o)
    hose = [(ax1 + L1, ay), (ax1 + L1 + 26, ay), (ax1 + L1 + 26, ay + 150), (ax2 - 26, ay + 150),
            (ax2 - 26, ay), (ax2, ay)]
    cv.polyline(hose, WHITE, 22, 0.85 * o)
    cv.polyline(hose, liquid, 16, o)
    if 0 < k < 1:
        pts = np.array(hose, float)
        segl = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        total = segl.sum()
        for j in range(4):
            u = ((lt * 0.9 + j / 4) % 1.0) * total
            acc = 0
            for a_, b_, l_ in zip(pts, pts[1:], segl):
                if acc + l_ >= u:
                    q = a_ + (b_ - a_) * (u - acc) / l_
                    cv.circle(q, 6, CYAN, -1, 0.9 * o)
                    break
                acc += l_
    # émbolos, vástagos y mangos
    cv.rect(p1x - 12, ay - d1 / 2, p1x, ay + d1 / 2, WHITE, o)
    cv.rect(p1x - 120, ay - 5, p1x - 12, ay + 5, WHITE, 0.9 * o)
    cv.rect(p1x - 132, ay - 26, p1x - 120, ay + 26, WHITE, 0.9 * o)
    cv.rect(p2x, ay - d2 / 2, p2x + 12, ay + d2 / 2, WHITE, o)
    cv.rect(p2x + 12, ay - 6, p2x + 100, ay + 6, WHITE, 0.9 * o)
    # flechas de fuerza proporcionales (F₂ = 4·F₁)
    fa = ease_out(prog(lt, 7.0, 0.5)) * o
    f1 = 34
    hx = p1x - 136
    cv.arrow((hx - f1 - 6, ay), (hx - 2, ay), WARN, 6, 18, fa)
    cv.text(hx - f1 / 2 - 6, ay + 46, "F₁", "bold", 36, WARN, fa, "mm")
    cv.arrow((p2x + 106, ay), (p2x + 106 + f1 * 4, ay), WARN, 8, 24, fa)
    cv.text(p2x + 106 + f1 * 2, ay - 96, "F₂ = 4·F₁", "bold", 34, WARN, fa, "mm")
    # rótulos de área (encima de cada jeringa)
    pa = ease_out(prog(lt, 5.8, 0.5)) * o
    cv.text(ax1 + L1 / 2, ay - d1 / 2 - 34, "Émbolo 1 · área A₁", "mono", 21, WHITE, pa, "mb")
    cv.text(ax2 + L2 / 2, ay - d2 / 2 - 34, "Émbolo 2 · área A₂ = 4·A₁", "mono", 21, WHITE, pa, "mb")
    pp = fade_io(lt, 8.2, 99, 0.5, 0) * o
    if pp > 0:
        cv.text((ax1 + L1 + ax2) / 2, ay + 180, "misma presión P en todo el líquido", "mono", 22, CYAN, pp, "mt")
        for (cx, d) in ((ax1 + L1 - 50, d1), (ax2 + 34, d2)):
            for sg in (-1, 1):
                cv.arrow((cx, ay + sg * (d / 2 - 22)), (cx, ay + sg * (d / 2 - 4)), CYAN, 3, 9, pp)
            cv.text(cx, ay, "P", "monob", 24, WHITE, pp, "mm")
    pd = ease_out(prog(lt, 10.0, 0.5)) * o
    if pd > 0:
        cv.text(1000, 300, "Mayor área → más fuerza, pero menos recorrido:", "text", 28, WHITE, pd)
        cv.text(1000, 342, "A₁·d₁ = A₂·d₂", "monob", 32, ACCENT, pd)


# ───────────────────────── Transiciones ─────────────────────────
def apply_transitions(img, t, bounds):
    for T, kind in bounds:
        d = t - T
        if kind == "whip" and abs(d) < 0.2:
            w = 1 - abs(d) / 0.2
            k = int(2 + 120 * w ** 1.5)
            img = cv2.blur(img, (k, 1))
            img = img * (1 - 0.25 * w) + np.array(ACCENT, np.float32) / 255 * 0.25 * w
        elif kind == "flash" and 0 <= d < 0.3:
            w = math.exp(-d * 14)
            img = img + (1 - img) * 0.75 * w
        elif kind == "dip" and abs(d) < 0.35:
            w = 1 - abs(d) / 0.35
            img = img * (1 - w)
    return img


# ───────────────────────── Render de un fotograma ─────────────────────────
class Ctx:
    def __init__(self):
        self.segs, self.chap_t0 = build_timeline()
        self.total = sum(s.n for s in self.segs) / FPS
        self.cues = build_cues(self.segs)
        self.bounds = [(s.t0, s.d["trans"]) for s in self.segs if s.d.get("trans")]


def render_frame(ctx, seg, i, frame):
    lt = i / FPS
    gt = seg.t0 + lt
    st = seg.src_t(i) if seg.layout != "graphic" else 0
    img, mp, info = render_base(seg, frame, lt, st)
    cv = Canvas()
    if seg.layout == "graphic" and seg.d.get("gen") == "pascal":
        pascal_scene(cv, lt, seg.dur)
    ch = seg.d.get("chapter")
    ct = gt - ctx.chap_t0.get(ch, 0) if ch else 0
    if seg.layout == "portrait":
        cv.rect(CLIP_X - 2, CLIP_Y - 2, CLIP_X + CW + 2, CLIP_Y + CH_ + 2, ACCENT, 0.55, width=2)
        brackets(cv, CLIP_X - 12, CLIP_Y - 12, CLIP_X + CW + 12, CLIP_Y + CH_ + 12, WHITE, 22, 2, 0.6)
        if ch:
            chapter_portrait(cv, ch, ct)
        has_inset = "inset" in seg.d
        if "checklist" in seg.d:
            draw_checklist(cv, seg.d["checklist"], lt)
        draw_panel(cv, seg.panel, gt, top=300, width=420 if has_inset else 900)
        if has_inset:
            draw_inset(cv, img, seg, frame, mp, lt, st, gt)
    elif seg.layout == "full":
        if ch:
            tags = seg.d.get("tags")
            chapter_full(cv, ch, ct, tags[0] if tags else None)
        draw_cards(cv, seg.cards, gt)
    if seg.d.get("lower"):
        txt, a, b = seg.d["lower"]
        lower_third(cv, txt, lt, a, b, seg.layout)
    draw_fx(cv, img, seg, mp, info, lt, st, gt)
    if seg.id not in NO_HUD:
        draw_hud(cv, gt, ctx.total, ctx.chap_t0, ch, ease_out(prog(gt, ctx.chap_t0[1], 0.6)))
    if BURN_SUBS:
        for c0, c1, txt in ctx.cues:
            if c0 <= gt <= c1:
                o = fade_io(gt, c0, c1, 0.12, 0.12)
                if seg.layout == "portrait":
                    draw_subtitle(cv, txt, o, (PX + 1810) / 2 + 10, 1036, 880, 40)
                else:
                    cv.gradient_v(0, 860, W, H, NAVY, 0.0, 0.55)
                    draw_subtitle(cv, txt, o, W / 2, 1036, 1400, 44)
    out = img * (1 - cv.a[..., 3:4]) + cv.a[..., :3]
    out = apply_transitions(out, gt, ctx.bounds)
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)


def render_chunk(args):
    seg_ids, path = args
    ctx = Ctx()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-r", str(FPS), str(path)], stdin=subprocess.PIPE)
    for seg in ctx.segs:
        if seg.id not in seg_ids:
            continue
        rd = Reader(seg) if seg.layout != "graphic" else None
        for i in range(seg.n):
            frame = rd.read() if (rd and i < seg.n_main) else (rd.last if rd else None)
            enc.stdin.write(render_frame(ctx, seg, i, frame).tobytes())
        if rd:
            rd.close()
        print(f"  ✓ {seg.id:12s} {seg.dur:6.2f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    return path


# ───────────────────────── Audio ─────────────────────────
NO_HUD = {"hook_a", "hook_b", "hook_c", "title", "final", "replay"}
MUSIC_LEVEL = {"hook_a": 1, "hook_b": 2, "hook_c": 2, "title": 3, "pascal": 2, "replay": 3, "final": 3}


def build_audio(ctx, music_file=None):
    dialogs, sfx, sections, hits = [], [], [], [0.0, 7.0]
    for s in ctx.segs:
        if s.layout != "graphic" and s.d.get("audio", True) and s.speed == 1.0:
            dialogs.append((PRE / f"{s.src}.wav", s.d["tin"], s.d["tout"], s.t0, 0.0))
        sections.append((s.t0, s.t0 + s.dur, MUSIC_LEVEL.get(s.id, 1)))
        kind = s.d.get("trans")
        if kind == "whip":
            sfx.append((sound.sfx_whoosh(0.6), s.t0 - 0.35, 0.55))
            hits.append(s.t0)
        elif kind == "flash":
            sfx.append((sound.sfx_transition(), s.t0 - 0.3, 0.5))
        # elementos que aparecen
        for it in s.panel:
            if it[0] > s.t0 - 0.01:
                sfx.append((sound.sfx_blip(), it[0], 0.35))
        for ta, _ in s.d.get("checklist", []):
            sfx.append((sound.sfx_blip(), s.t0 + ta + 0.1, 0.3))
        for c in s.cards:
            if c[0] > s.t0 - 0.01:
                sfx.append((sound.sfx_blip(), c[0], 0.35))
        for ta, _, _ in s.d.get("labels", []):
            sfx.append((sound.sfx_tick(2200), s.t0 + max(ta, s.d.get("inset", {}).get("t0", 0) + 0.4), 0.5))
        if "inset" in s.d and s.d["inset"]["t0"] > 0.1:
            sfx.append((sound.sfx_shutter(), s.t0 + s.d["inset"]["t0"], 0.6))
    seg = {s.id: s for s in ctx.segs}
    # gancho: golpe grave inicial, subida de tensión y título
    sfx += [(sound.sfx_impact(2.4), 0.0, 1.0), (sound.sfx_whoosh(0.8), 0.6, 0.45),
            (sound.sfx_riser(2.2), 1.8, 0.55), (sound.sfx_impact(2.0), seg["hook_c"].t0 + 0.45, 0.85),
            (sound.sfx_impact(2.6), seg["title"].t0, 0.9), (sound.sfx_riser(1.5), seg["replay"].t0 - 1.5, 0.45),
            (sound.sfx_impact(1.8), seg["replay"].t0 + 2.6, 0.6)]
    mixd = mix.build(ctx.total, dialogs, sfx, sections, hits, music_file=music_file, outdir=OUT / "audio")
    return mixd


# ───────────────────────── Subtítulos ─────────────────────────
def ts(t, sep=","):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"


def export_subs(ctx):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "subtitulos_es.srt", "w", encoding="utf-8") as f:
        for k, (a, b, txt) in enumerate(ctx.cues, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    hl = lambda txt: " ".join(("{\\c&HE6E15C&}" + w_ + "{\\c&HFFFFFF&}") if c == CYAN else w_
                              for w_, c in sub_words(txt))
    with open(OUT / "subtitulos_es.ass", "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n"
                "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
                "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                "Alignment, MarginL, MarginR, MarginV, Encoding\n"
                "Style: Default,Inter SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H50201008,0,0,0,0,100,100,0,0,"
                "3,10,0,2,80,80,50,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
                "Effect, Text\n")
        for a, b, txt in ctx.cues:
            f.write(f"Dialogue: 0,{ts(a, '.')[1:-1]},{ts(b, '.')[1:-1]},Default,,0,0,0,,{hl(txt)}\n")
    with open(OUT / "capitulos.txt", "w", encoding="utf-8") as f:
        f.write("0:00 Introducción\n")
        for c, t0 in ctx.chap_t0.items():
            f.write(f"{int(t0 // 60)}:{int(t0 % 60):02d} {edl.CH[c].capitalize()}\n")


# ───────────────────────── main ─────────────────────────
def main():
    global BURN_SUBS
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--stills", type=float, nargs="*")
    ap.add_argument("--musica", default=None)
    ap.add_argument("--sin-subtitulos", action="store_true")
    ap.add_argument("--solo-audio", action="store_true")
    ap.add_argument("--salida", default="grua_hidraulica_final.mp4")
    a = ap.parse_args()
    BURN_SUBS = not a.sin_subtitulos
    ctx = Ctx()
    print(f"Duración: {ctx.total:.1f} s · {len(ctx.segs)} segmentos · {len(ctx.cues)} subtítulos")
    for s in ctx.segs:
        print(f"  {s.t0:7.2f}  {s.id:12s} {s.dur:6.2f}s  {s.layout}")
    OUT.mkdir(parents=True, exist_ok=True)
    if a.stills is not None:
        d = OUT / "fotogramas"
        d.mkdir(exist_ok=True)
        for t in a.stills:
            seg = next(s for s in ctx.segs if s.t0 <= t < s.t0 + s.dur)
            i = int(round((t - seg.t0) * FPS))
            frame = None
            if seg.layout != "graphic":
                rd = Reader(seg, skip=min(i, seg.n_main - 1))
                frame = rd.read()
                rd.close()
            img = render_frame(ctx, seg, i, frame)
            cv2.imwrite(str(d / f"t{t:07.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print("  →", d / f"t{t:07.2f}.png", seg.id)
        return
    export_subs(ctx)
    print("Audio…")
    mixd = build_audio(ctx, a.musica)
    wav = OUT / "audio" / "mezcla_final.wav"
    mix.write_wav(wav, mixd)
    lst = ROOT / "trabajo" / "chunks" / "lista.txt"
    if a.solo_audio:
        if lst.exists():   # vuelve a unir la imagen ya renderizada con el audio nuevo
            mux(lst, wav, OUT / a.salida)
            print("Audio actualizado en", OUT / a.salida)
        return
    print("Vídeo…")
    tmp = ROOT / "trabajo" / "chunks"
    tmp.mkdir(parents=True, exist_ok=True)
    # reparto de segmentos en bloques de duración parecida
    n = max(1, a.jobs)
    target = sum(s.n for s in ctx.segs) / n
    groups, cur, acc = [], [], 0
    for s in ctx.segs:
        cur.append(s.id)
        acc += s.n
        if acc >= target * (len(groups) + 1) and len(groups) < n - 1:
            groups.append(cur)
            cur = []
    groups.append(cur)
    jobs = [(set(g), tmp / f"chunk_{k:02d}.mp4") for k, g in enumerate(groups) if g]
    with ProcessPoolExecutor(len(jobs)) as ex:
        paths = list(ex.map(render_chunk, jobs))
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths))
    mux(lst, wav, OUT / a.salida)
    print("Listo:", OUT / a.salida)


def mux(lst, wav, final):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", str(final)], check=True)


if __name__ == "__main__":
    sys.exit(main())
