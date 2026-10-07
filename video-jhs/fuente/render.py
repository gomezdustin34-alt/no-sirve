"""Builds the JHS Joyería route video: timeline -> frames -> audio mix."""
import json, math, subprocess, sys, os, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gfx as G
from gfx import W, H, ease, ease_out, back_out

HERE = os.path.dirname(os.path.abspath(__file__))
U = '/root/.claude/uploads/ff821385-1560-5275-97a7-46a7cf9fbe1a'
SRC = {k: glob.glob(f'{U}/{v}-*.mov')[0] for k, v in
       {'A': 'b590a87c', 'B': 'b79831d9', 'C': '23b8bb77'}.items()}
FPS = 30
NW, NH = 576, 1024
VODUR = json.load(open(f'{HERE}/vo/dur.json'))
LINES = json.load(open(f'{HERE}/lines.json'))
CUM = G.CUM


def S(i, off=0.0):
    return CUM[i] + off


# ------------------------------------------------------------ timeline
class TL:
    def __init__(self):
        self.pieces = []   # dict(kind, t0, t1, ...)
        self.ovs = []      # dict(kind, t0, t1, ...)
        self.vo = []       # (key, t)
        self.sfx = []      # (name, t, gain)
        self.prog = []     # (t, s)
        self.step = []     # (t0, label)
        self.t = 0.0

    def add(self, kind, dur, **kw):
        p = dict(kind=kind, t0=self.t, t1=self.t + dur, **kw)
        self.pieces.append(p); self.t += dur
        return p

    def ov(self, kind, t0, t1, **kw):
        self.ovs.append(dict(kind=kind, t0=t0, t1=t1, **kw))

    def say(self, key, t):
        self.vo.append((key, t)); return t + VODUR[key]

    def fx(self, name, t, g=1.0):
        self.sfx.append((name, t, g))


T = TL()

# ---- 1. INTRO
t = T.t
T.add('intro', 6.9)
T.say('intro', 0.35)
T.fx('whoosh', 0.0, 0.8); T.fx('pop', 0.55, 0.8); T.fx('pop', 3.35, 0.8); T.fx('ding', 4.6, 0.6)
T.prog += [(0, 0)]

# ---- 2. START
T.step.append((T.t, '1 · PUNTO DE PARTIDA'))
p = T.add('clip', 3.1, src='A', s0=0.2, speed=1.0, z=(1.0, 1.08), c=(288, 520))
T.say('start', p['t0'] + 0.15)
T.ov('tag', p['t0'] + 0.25, p['t1'], txt='PUNTO DE PARTIDA', icon='pin', y=1400)
T.fx('pop', p['t0'] + 0.25); T.fx('whoosh', p['t0'] - 0.25, 0.6)
T.prog += [(p['t0'], S(0)), (p['t1'], S(0))]

# ---- 3. CROSS 1 (speed ramp through the taxi area)
p = T.add('clip', 3.9, src='A', s0=10.5, speed=3.2, z=(1.04, 1.0), c=(288, 512))
T.say('cross1', p['t0'] + 0.05)
T.ov('card', p['t0'] + 0.2, p['t1'], title='CRUZA LA CALLE', sub='hasta la acera del frente', icon='cross')
T.fx('whoosh', p['t0'], 0.5); T.fx('pop', p['t0'] + 0.2)
T.prog += [(p['t1'], S(1))]

# ---- 4. STRAIGHT 1 real
T.step.append((T.t, '2 · SIGUE DERECHO'))
p = T.add('clip', 3.0, src='A', s0=36.0, speed=1.0, z=(1.0, 1.1), c=(288, 470))
T.say('str1', p['t0'] + 0.1)
T.ov('card', p['t0'] + 0.15, p['t1'], title='SIGUE DERECHO', icon='up')
T.ov('bigarrow', p['t0'] + 0.5, p['t1'], icon='up', x=540, y=640)
T.fx('pop', p['t0'] + 0.15)
T.prog += [(p['t1'], S(1, 110))]

# ---- 5. MAP 1
T.fx('whoosh', T.t - 0.2, 0.9)
p = T.add('map', 5.7, sa=S(1, 110), sb=S(2), title='SIGUE DERECHO', sub='hasta la esquina del semáforo', icon='up')
T.say('map1', p['t0'] + 0.25)
T.fx('beep', p['t0'] + 0.15, 0.8); T.fx('beep', p['t1'] - 0.95, 0.9)

# ---- 6. TURN 1 (Farma Vida)
T.step.append((T.t, '3 · GIRO A LA DERECHA'))
T.fx('whoosh', T.t - 0.15, 0.7)
p = T.add('clip', 2.0, src='A', s0=151.75, speed=1.0, z=(1.0, 1.12), c=(288, 330))
T.say('turn1', p['t0'] + 0.1)
T.prog += [(p['t0'], S(2)), (p['t1'], S(2))]
f = T.add('freeze', 0.8, src='A', s0=153.75, z=(1.12, 1.2), c=(288, 330))
T.ov('flash', f['t0'], f['t0'] + 0.18)
T.fx('click', f['t0'], 0.8); T.fx('ding', f['t0'] + 0.1, 0.7)
T.ov('ring', f['t0'] + 0.05, f['t1'] + 0.3, piece=f, nx=278, ny=136, rw=520, rh=150, label='FARMA VIDA', ly=-1)
p = T.add('clip', 2.1, src='A', s0=153.75, speed=1.0, z=(1.2, 1.0), c=(288, 400))
T.ov('card', f['t0'] + 0.3, p['t1'], title='GIRA A LA DERECHA', sub='frente a la Farma Vida', icon='right')
T.ov('bigarrow', p['t0'], p['t1'], icon='right', x=690, y=700)
T.fx('pop', f['t0'] + 0.3); T.fx('whoosh', p['t0'], 0.5)
T.prog += [(p['t1'], S(2, 70))]

# ---- 7. STRAIGHT 2 real
T.step.append((T.t, '4 · TRAMO LARGO'))
p = T.add('clip', 2.6, src='A', s0=157.5, speed=1.0, z=(1.0, 1.08), c=(288, 500))
T.say('str2', p['t0'] + 0.1)
T.ov('card', p['t0'] + 0.15, p['t1'], title='TRAMO LARGO', sub='sigue derecho por esta vía', icon='up')
T.fx('pop', p['t0'] + 0.15)
T.prog += [(p['t1'], S(2, 160))]

# ---- 8. MAP 2a / crossing insert / MAP 2b
T.fx('whoosh', T.t - 0.2, 0.9)
x2 = S(2, 1200)
p = T.add('map', 3.0, sa=S(2, 160), sb=x2 - 50, title='SIGUE DERECHO', sub='cruzando 3 calles', icon='up', recalc=True)
T.say('map2', p['t0'] + 0.25)
T.fx('ticks', p['t0'] + 0.1, 0.8)
T.fx('whoosh', p['t1'] - 0.15, 0.6)
p = T.add('clip', 2.0, src='B', s0=8.3, speed=1.25, z=(1.0, 1.06), c=(288, 520))
T.ov('tag', p['t0'] + 0.1, p['t1'], txt='CRUZA CON CUIDADO', icon='cross', y=1400)
T.fx('pop', p['t0'] + 0.1)
T.prog += [(p['t0'], x2 - 50), (p['t1'], x2 + 50)]
T.fx('whoosh', T.t - 0.15, 0.6)
p = T.add('map', 2.6, sa=x2 + 50, sb=S(3), title='HASTA EL SEMÁFORO', sub='al fondo de la vía', icon='up')
T.fx('beep', p['t1'] - 0.9, 0.9)

# ---- 9. TURN 2 (traffic light, left + cross)
T.step.append((T.t, '5 · GIRO A LA IZQUIERDA'))
T.fx('whoosh', T.t - 0.15, 0.7)
p = T.add('clip', 1.9, src='B', s0=105.5, speed=1.0, z=(1.0, 1.06), c=(288, 470))
T.say('turn2', p['t0'] + 0.1)
T.prog += [(p['t0'], S(3)), (p['t1'], S(3))]
f = T.add('freeze', 0.8, src='B', s0=107.9, z=(1.06, 1.12), c=(330, 420))
T.ov('flash', f['t0'], f['t0'] + 0.18); T.fx('click', f['t0'], 0.8)
T.ov('ring', f['t0'] + 0.05, f['t1'], piece=f, nx=426, ny=268, rw=150, rh=150, label='SEMÁFORO', ly=1)
T.ov('card', f['t0'] + 0.2, T.t + 2.4, title='GIRA A LA IZQUIERDA', sub='y cruza la calle', icon='left')
T.fx('pop', f['t0'] + 0.2)
p = T.add('clip', 2.4, src='B', s0=127.3, speed=1.5, z=(1.0, 1.0), c=(288, 512))
T.ov('bigarrow', p['t0'], p['t1'] - 0.3, icon='left', x=380, y=700)
T.fx('whoosh', p['t0'], 0.5)
T.prog += [(p['t1'], S(4))]

# ---- 10. STRAIGHT 3 real (tree-lined sidewalk)
T.step.append((T.t, '6 · SIGUE DERECHO'))
p = T.add('clip', 3.2, src='B', s0=136.6, speed=1.0, z=(1.0, 1.08), c=(288, 500))
T.say('str3', p['t0'] + 0.1)
T.ov('card', p['t0'] + 0.15, p['t1'], title='SIGUE DERECHO', sub='por el andén con árboles', icon='up')
T.fx('pop', p['t0'] + 0.15)
T.prog += [(p['t1'], S(4, 90))]

# ---- 11. MAP 3
T.fx('whoosh', T.t - 0.2, 0.9)
p = T.add('map', 4.7, sa=S(4, 90), sb=S(5, -40), title='SIGUE DERECHO', sub='atento al Rey Chino', icon='up')
T.say('map3', p['t0'] + 0.2)
T.fx('beep', p['t1'] - 0.9, 0.9)

# ---- 12. REY CHINO reference
T.step.append((T.t, 'REFERENCIA'))
T.fx('whoosh', T.t - 0.15, 0.7)
p = T.add('clip', 2.3, src='B', s0=191.7, speed=1.0, z=(1.0, 1.15), c=(320, 360))
T.say('rey', p['t0'] + 0.1)
T.prog += [(p['t0'], S(5, -40)), (p['t1'], S(5))]
f = T.add('freeze', 0.8, src='B', s0=194.0, z=(1.15, 1.28), c=(330, 330))
T.ov('flash', f['t0'], f['t0'] + 0.18); T.fx('click', f['t0'], 0.8); T.fx('ding', f['t0'] + 0.1, 0.7)
T.ov('ring', f['t0'] + 0.05, f['t1'] + 0.4, piece=f, nx=338, ny=252, rw=230, rh=270, label='RESTAURANTE EL REY CHINO', ly=1)
p = T.add('clip', 2.3, src='B', s0=194.0, speed=1.0, z=(1.28, 1.0), c=(320, 400))
T.ov('card', p['t0'] + 0.3, p['t1'], title='¡VAS BIEN!', sub='pasa a su lado y sigue derecho', icon='up')
T.fx('pop', p['t0'] + 0.3)
T.prog += [(p['t1'], S(5, 60))]

# ---- 13. quick hop map to the park crossing
T.fx('whoosh', T.t - 0.2, 0.9)
p = T.add('map', 1.8, sa=S(5, 60), sb=S(6), title='SIGUE DERECHO', sub='hasta la calle del parque', icon='up', quick=True)
T.fx('beep', p['t1'] - 0.6, 0.8)

# ---- 14. CROSS 2 (park)
T.step.append((T.t, '7 · CRUZA HACIA EL PARQUE'))
T.fx('whoosh', T.t - 0.15, 0.6)
p = T.add('clip', 2.7, src='C', s0=9.4, speed=2.0, z=(1.0, 1.05), c=(288, 470))
T.say('cross2', p['t0'] + 0.15)
T.ov('card', p['t0'] + 0.15, p['t1'], title='CRUZA LA CALLE', sub='hacia el parque', icon='cross')
T.fx('pop', p['t0'] + 0.15)
T.prog += [(p['t0'], S(6)), (p['t1'], S(7))]

# ---- 15. MAP 4a / Jamar insert / MAP 4b
T.fx('whoosh', T.t - 0.2, 0.9)
sj = S(8, -60)
p = T.add('map', 2.3, sa=S(7), sb=sj, title='BORDEA EL PARQUE', sub='y sigue derecho', icon='up')
T.say('map4', p['t0'] + 0.2)
T.fx('whoosh', p['t1'] - 0.15, 0.6)
p = T.add('clip', 1.7, src='C', s0=50.8, speed=1.0, z=(1.0, 1.1), c=(200, 400))
T.ov('ring', p['t0'] + 0.1, p['t1'], piece=p, nx=98, ny=132, rw=210, rh=200, label='JAMAR', ly=1)
T.fx('ding', p['t0'] + 0.1, 0.6)
T.prog += [(p['t0'], sj), (p['t1'], sj + 60)]
T.fx('whoosh', T.t - 0.15, 0.6)
p = T.add('map', 2.3, sa=sj + 60, sb=S(9), title='HASTA EL SEMÁFORO', sub='ya casi llegamos', icon='up')
T.fx('beep', p['t1'] - 0.8, 0.9)

# ---- 16. TURN 3 last crossing
T.step.append((T.t, '8 · ÚLTIMO CRUCE'))
T.fx('whoosh', T.t - 0.15, 0.7)
p = T.add('clip', 2.9, src='C', s0=93.5, speed=1.0, z=(1.0, 1.06), c=(288, 470))
T.say('turn3', p['t0'] + 0.1)
T.prog += [(p['t0'], S(9)), (p['t1'], S(9))]
T.ov('tag', p['t0'] + 0.3, p['t1'] + 0.7, txt='YA ESTAMOS CERCA', icon='pin', y=1400)
f = T.add('freeze', 0.6, src='C', s0=96.45, z=(1.06, 1.12), c=(330, 470))
T.ov('flash', f['t0'], f['t0'] + 0.16); T.fx('click', f['t0'], 0.8)
p = T.add('clip', 2.2, src='C', s0=100.0, speed=2.0, z=(1.0, 1.04), c=(288, 470))
T.ov('card', p['t0'] - 0.3, p['t1'], title='CRUZA AL FRENTE', sub='hacia los toldos rojos', icon='cross')
T.ov('bigarrow', p['t0'], p['t1'], icon='up', x=540, y=620)
T.fx('pop', p['t0'] - 0.3); T.fx('whoosh', p['t0'], 0.5)
T.prog += [(p['t1'], S(10))]

# ---- 17. ENTER passage
T.step.append((T.t, '9 · ENTRA AL PASILLO'))
p = T.add('clip', 2.9, src='C', s0=110.4, speed=2.0, z=(1.0, 1.06), c=(288, 470))
T.say('enter', p['t0'] + 0.05)
T.ov('card', p['t0'] + 0.1, p['t1'], title='ENTRA POR AQUÍ', sub='junto al puesto de comida', icon='enter')
T.fx('pop', p['t0'] + 0.1)
T.prog += [(p['t1'], S(10, 60))]

# ---- 18. MAP FINAL arrival
T.fx('whoosh', T.t - 0.2, 0.9)
p = T.add('map', 2.3, sa=S(10, 60), sb=CUM[-1], title='DESTINO', sub='JHS Joyería', icon='pin', final=True)
T.say('arrive', p['t0'] + 0.15)
T.fx('chime', p['t1'] - 0.75, 1.0)

# ---- 19. ARRIVAL real
T.step.append((T.t, 'LLEGASTE'))
p = T.add('clip', 2.9, src='C', s0=118.2, speed=2.0, z=(1.0, 1.05), c=(288, 470))
T.prog += [(p['t0'], CUM[-1])]
p = T.add('clip', 5.8, src='C', s0=123.6, speed=1.0, z=(1.0, 1.08), c=(330, 520))
T.say('outro', p['t0'] + 0.5)
T.ov('title', p['t0'] + 0.1, p['t1'])
T.ov('ring', p['t0'] + 3.6, p['t1'], piece=p, nx=432, ny=330, rw=160, rh=160, label=None, ly=1)
T.ov('sparkles', p['t0'], p['t1'])
T.fx('pop', p['t0'] + 0.1); T.fx('ding', p['t0'] + 3.6, 0.5)

# ---- 20. END CARD
T.fx('whoosh', T.t - 0.2, 0.8)
p = T.add('end', 3.0)
T.fx('chime', p['t0'] + 0.2, 0.8)

TOTAL = T.t
_v = sorted(T.vo, key=lambda x: x[1])
for (k1, a1), (k2, a2) in zip(_v, _v[1:]):
    if a1 + VODUR[k1] > a2 - 0.1: print('VO OVERLAP', k1, k2, round(a1 + VODUR[k1] - a2, 2))
for k1, a1 in _v:
    pc_ = [p for p in T.pieces if p['t0'] <= a1 < p['t1']]
HUD_START = T.pieces[1]['t0']
HUD_END = T.pieces[-3]['t0'] + 0.4


# ------------------------------------------------------------ helpers
def prog_at(t):
    pts = sorted(T.prog)
    for pc in T.pieces:
        if pc['kind'] == 'map' and pc['t0'] <= t < pc['t1']:
            return map_ball_s(pc, t - pc['t0'])
    if t <= pts[0][0]: return pts[0][1]
    for (ta, sa), (tb, sb) in zip(pts, pts[1:]):
        if ta <= t <= tb:
            return sa + (sb - sa) * ((t - ta) / max(1e-6, tb - ta))
    # in a map piece gap etc.
    last = pts[0][1]
    for ta, sa in pts:
        if ta <= t: last = sa
    for pc in T.pieces:
        if pc['kind'] == 'map' and pc['t1'] <= t: last = max(last, pc['sb'])
    return last


def map_ball_s(pc, lt):
    D = pc['t1'] - pc['t0']
    a, b = (0.08, 0.72) if pc.get('quick') else (0.14, 0.74)
    return pc['sa'] + (pc['sb'] - pc['sa']) * ease((lt / D - a) / (b - a))


def step_at(t):
    lab = ''
    for t0, l in T.step:
        if t >= t0: lab = l
    return lab


class Clips:
    cache = {}

    @classmethod
    def frames(cls, src, s0, dur):
        key = (src, round(s0, 3), round(dur, 3))
        if key not in cls.cache:
            cls.cache.clear()
            cmd = ['ffmpeg', '-v', 'error', '-ss', f'{s0:.3f}', '-i', SRC[src], '-t', f'{dur + 0.2:.3f}',
                   '-vf', f'fps={FPS},eq=contrast=1.06:saturation=1.16:gamma=0.98,unsharp=5:5:0.4',
                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
            raw = subprocess.run(cmd, capture_output=True, check=True).stdout
            arr = np.frombuffer(raw, np.uint8).reshape(-1, NH, NW, 3)
            cls.cache[key] = arr
        return cls.cache[key]


def box_for(z, c):
    w, h = NW / z, NH / z
    x0 = min(max(c[0] - w / 2, 0), NW - w); y0 = min(max(c[1] - h / 2, 0), NH - h)
    return (x0, y0, x0 + w, y0 + h)


def piece_box(pc, lt):
    D = pc['t1'] - pc['t0']; u = ease(lt / D)
    z = pc['z'][0] + (pc['z'][1] - pc['z'][0]) * u
    return box_for(z, pc['c'])


def native_to_screen(box, nx, ny):
    x0, y0, x1, y1 = box
    return (nx - x0) * W / (x1 - x0), (ny - y0) * H / (y1 - y0), W / (x1 - x0)


def render_clip(pc, lt):
    if pc['kind'] == 'freeze':
        arr = Clips.frames(pc['src'], pc['s0'], 0.1); fr = arr[0]
    else:
        D = pc['t1'] - pc['t0']
        arr = Clips.frames(pc['src'], pc['s0'], D * pc['speed'])
        i = min(int(lt * pc['speed'] * FPS), len(arr) - 1); fr = arr[i]
    box = piece_box(pc, lt)
    im = Image.fromarray(fr).resize((W, H), Image.BICUBIC, box=box)
    return im.convert('RGBA'), box


# ------------------------------------------------------------ map rendering
WORLD = None
SPR = {}


def sprites():
    if SPR: return SPR
    SPR['ball'] = G.ball_sprite(24)
    SPR['dest'] = G.dest_pin(130)
    SPR['labels'] = [G.map_label(t, k, c) for (_, t, k, c, _) in G.LANDMARKS]
    SPR['icons'] = [G.glyph_icon(k, 58, c) for (_, t, k, c, _) in G.LANDMARKS]
    SPR['destlabel'] = G.tag('JHS JOYERÍA', 38, icon='gem')
    SPR['spark'] = G.sparkle(64)
    SPR['logo'] = G.logo(1.0)
    SPR['logo_s'] = G.logo(0.62)
    return SPR


def world():
    global WORLD
    if WORLD is None:
        WORLD = G.build_world()
    return WORLD


def seg_bbox(sa, sb):
    pts = [G.route_at(sa + (sb - sa) * k / 20) for k in range(21)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def map_camera(pc, lt):
    D = pc['t1'] - pc['t0']
    sa, sb = pc['sa'], pc['sb']
    x0, y0, x1, y1 = seg_bbox(sa, sb)
    bw, bh = max(x1 - x0, 200) + 500, max(y1 - y0, 200) + 700
    zfit = min(W * 0.9 / bw, H * 0.62 / bh, 0.95)
    zfit = max(zfit, 0.34)
    zend = 1.15 if not pc.get('final') else 1.45
    bc = ((x0 + x1) / 2, (y0 + y1) / 2)
    ball = G.route_at(map_ball_s(pc, lt))
    u = lt / D
    zin = ease((u - 0.0) / 0.16)           # small intro zoom-out settle
    zout = ease((u - 0.68) / 0.3)
    z0 = zfit * 1.25
    z = z0 + (zfit - z0) * zin
    z = z + (zend - z) * zout
    follow = ease((u - 0.25) / 0.6)
    cx = bc[0] + (ball[0] - bc[0]) * follow
    cy = bc[1] + (ball[1] - bc[1]) * follow + 120 / z * (1 - zout)
    return cx, cy, z, ball


def render_map_view(cx, cy, z, s_trav, ball=None, t_glob=0.0, show_labels=True, label_alpha=1.0, dim_route=True,
                    ball_pulse=True):
    sp = sprites(); wd = world()
    hw, hh = W / 2 / z, H / 2 / z
    box = (cx - hw + G.PAD, cy - hh + G.PAD, cx + hw + G.PAD, cy + hh + G.PAD)
    im = wd.resize((W, H), Image.BILINEAR, box=box).convert('RGBA')

    def P(p): return ((p[0] - cx) * z + W / 2, (p[1] - cy) * z + H / 2)

    d = ImageDraw.Draw(im)
    if dim_route:
        d.line([P(p) for p in G.ROUTE], fill=(233, 196, 106, 90), width=max(6, int(14 * min(z, 1))), joint='curve')
        im2 = im
    trav = [P(p) for p in G.route_upto(s_trav)]
    if len(trav) >= 2:
        lw = max(8, int(20 * min(1.0, z * 1.2)))
        glow = Image.new('RGBA', (W // 4, H // 4), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.line([(x / 4, y / 4) for x, y in trav], fill=G.GOLD2 + (200,), width=max(3, lw // 2), joint='curve')
        glow = glow.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
        im.alpha_composite(glow)
        d = ImageDraw.Draw(im)
        d.line(trav, fill=G.GOLD2 + (255,), width=lw, joint='curve')
        for q in trav[1:-1]:
            d.ellipse([q[0] - lw / 2, q[1] - lw / 2, q[0] + lw / 2, q[1] + lw / 2], fill=G.GOLD2 + (255,))
    # landmarks
    if show_labels:
        for k, (wp, txt, kind, col, off) in enumerate(G.LANDMARKS):
            sx, sy = P(wp)
            if -200 < sx < W + 200 and -200 < sy < H + 200:
                ic = sp['icons'][k]
                paste(im, ic, sx - 29, sy - 29, label_alpha)
                if z > 0.5:
                    lb = sp['labels'][k]
                    lx = sx + off[0] if off[0] > 0 else sx + off[0] - lb.width
                    paste(im, lb, lx, sy + off[1], label_alpha)
    # destination
    dx, dy = P(G.ROUTE[-1])
    paste(im, sp['dest'], dx - 65, dy - 125)
    if z > 0.42:
        paste(im, sp['destlabel'], dx - sp['destlabel'].width / 2, dy - 210)
    # ball
    if ball is not None:
        bx, by = P(ball)
        if ball_pulse:
            ph = (t_glob * 1.3) % 1.0
            r = 26 + 60 * ph
            ring = Image.new('RGBA', (int(2 * r + 8), int(2 * r + 8)), (0, 0, 0, 0))
            ImageDraw.Draw(ring).ellipse([4, 4, 2 * r + 4, 2 * r + 4], outline=G.BALL + (int(200 * (1 - ph)),), width=5)
            paste(im, ring, bx - r - 4, by - r - 4)
        b = sp['ball']; paste(im, b, bx - b.width / 2, by - b.height / 2)
    return im, P


def paste(im, spr, x, y, alpha=1.0, scale=1.0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1.0:
        w, h = max(1, int(spr.width * scale)), max(1, int(spr.height * scale))
        cxx, cyy = x + spr.width / 2, y + spr.height / 2
        spr = spr.resize((w, h), Image.BILINEAR); x, y = cxx - w / 2, cyy - h / 2
    if alpha < 0.999:
        spr = spr.copy(); a = spr.getchannel('A').point(lambda v: int(v * alpha)); spr.putalpha(a)
    x, y = int(round(x)), int(round(y))
    if x >= im.width or y >= im.height or x + spr.width <= 0 or y + spr.height <= 0: return
    im.alpha_composite(spr, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))


def render_map(pc, lt, t):
    cx, cy, z, ball = map_camera(pc, lt)
    s = map_ball_s(pc, lt)
    im, P = render_map_view(cx, cy, z, s, ball, t)
    D = pc['t1'] - pc['t0']
    # arrival ripple at end point
    u = lt / D
    if u > 0.74:
        k = (u - 0.74) / 0.26
        ex, ey = P(G.route_at(pc['sb']))
        for j in range(2):
            kk = (k * 1.4 - j * 0.35)
            if 0 < kk < 1:
                r = 30 + 110 * ease_out(kk)
                ring = Image.new('RGBA', (int(2 * r + 10),) * 2, (0, 0, 0, 0))
                ImageDraw.Draw(ring).ellipse([5, 5, 2 * r + 5, 2 * r + 5], outline=G.GOLD2 + (int(230 * (1 - kk)),), width=6)
                paste(im, ring, ex - r - 5, ey - r - 5)
    # vignette top & bottom
    im.alpha_composite(VIG)
    # GPS badge
    paste(im, BADGE, 60, 330, min(1, lt / 0.25))
    if pc.get('recalc') and lt < 1.0:
        a = min(1, lt / 0.15) * min(1, (1.0 - lt) / 0.2)
        paste(im, RECALC, (W - RECALC.width) / 2, 430, a)
    if pc.get('final') and u > 0.78:
        a = ease_out((u - 0.78) / 0.15)
        paste(im, ARRIVE_TAG, (W - ARRIVE_TAG.width) / 2, 430, a, 0.8 + 0.2 * back_out((u - 0.78) / 0.15))
    return im


def make_vig():
    a = np.zeros((H, W), np.float32)
    y = np.arange(H)[:, None]
    a += np.clip(1 - y / 520, 0, 1) ** 1.6 * 0.85
    a += np.clip((y - 1300) / 620, 0, 1) ** 1.4 * 0.8
    v = np.zeros((H, W, 4), np.uint8); v[..., :3] = 8; v[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(v, 'RGBA')


VIG = make_vig()
BADGE = G.tag('GPS · RUTA RESUMIDA', 28, icon='pin', fg=G.IVORY + (255,), bg=(14, 18, 24, 230))
RECALC = G.tag('RECALCULANDO RUTA…', 30, icon='recalc', fg=G.INK + (255,), bg=G.GOLD2 + (255,))
ARRIVE_TAG = G.tag('¡LLEGASTE!', 46, icon='pin')


# ------------------------------------------------------------ overlays
CACHE = {}


def cached(key, fn):
    if key not in CACHE: CACHE[key] = fn()
    return CACHE[key]


def hud(im, t):
    if not (HUD_START <= t < HUD_END): return
    a = min(1, (t - HUD_START) / 0.3, (HUD_END - t) / 0.3)
    s = prog_at(t); frac = min(1, s / CUM[-1])
    x0, x1 = 90, 960
    layer = Image.new('RGBA', (W, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    by = 104
    d.rounded_rectangle([x0, by - 6, x1, by + 6], radius=6, fill=(255, 255, 255, 110))
    xe = x0 + (x1 - x0) * frac
    d.rounded_rectangle([x0, by - 6, max(x0 + 12, xe), by + 6], radius=6, fill=G.GOLD2 + (255,))
    lab = step_at(t)
    if lab:
        ls = cached(('step', lab), lambda: G.tag(lab, 26, fg=G.IVORY + (255,), bg=(10, 12, 16, 210)))
        layer.alpha_composite(ls, (x0 - 6, 0))
    dest = cached('hud_dest', lambda: G.arrow_icon('pin', 54, G.GOLD2 + (255,)))
    layer.alpha_composite(dest, (x1 + 2, by - 46))
    sb = cached('hud_ball', lambda: G.ball_sprite(12))
    paste(layer, sb, xe - sb.width / 2, by - sb.height / 2)
    paste(im, layer, 0, 150, a)


def draw_overlays(im, t, box):
    for o in T.ovs:
        if not (o['t0'] <= t < o['t1']): continue
        lt = t - o['t0']; D = o['t1'] - o['t0']
        out = min(1, (D - lt) / 0.15)
        k = o['kind']
        if k == 'flash':
            a = 1 - lt / D
            im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(170 * a))))
        elif k == 'card':
            spr = cached(('card', o['title'], o.get('sub'), o['icon']), lambda: G.card(o['title'], o.get('sub'), o['icon']))
            sc = 0.85 + 0.15 * back_out(lt / 0.28)
            paste(im, spr, (W - spr.width) / 2, 1440 + 40 * (1 - ease_out(lt / 0.25)), min(1, lt / 0.12) * out, sc)
        elif k == 'tag':
            spr = cached(('tag', o['txt'], o.get('icon')), lambda: G.tag(o['txt'], 44, icon=o.get('icon')))
            sc = 0.7 + 0.3 * back_out(lt / 0.3)
            paste(im, spr, (W - spr.width) / 2, o['y'] + 20, min(1, lt / 0.1) * out, sc)
        elif k == 'bigarrow':
            spr = cached(('big', o['icon']), lambda: big_arrow(o['icon']))
            dx = dy = 0
            ph = math.sin(lt * 2 * math.pi * 1.6)
            if o['icon'] == 'right': dx = 22 * ph
            elif o['icon'] == 'left': dx = -22 * ph
            else: dy = -18 * ph
            sc = 0.5 + 0.5 * back_out(lt / 0.3)
            paste(im, spr, o['x'] - spr.width / 2 + dx, o['y'] - spr.height / 2 + dy, min(1, lt / 0.12) * out * 0.95, sc)
        elif k == 'ring':
            pc = o['piece']
            b = piece_box(pc, min(max(t - pc['t0'], 0), pc['t1'] - pc['t0'] - 1e-3)) if pc['t0'] <= t < pc['t1'] else box
            sx, sy, sc = native_to_screen(b, o['nx'], o['ny'])
            prog = ease_out(lt / 0.35)
            rw, rh = o['rw'] * sc, o['rh'] * sc
            spr = G.ring_sprite(int(rw), int(rh), prog)
            paste(im, spr, sx - spr.width / 2, sy - spr.height / 2, out)
            if o.get('label') and lt > 0.15:
                ls = cached(('rl', o['label']), lambda: G.tag(o['label'], 34, icon='pin'))
                ly = sy + (rh / 2 + 40 if o['ly'] > 0 else -rh / 2 - 40 - ls.height)
                lx = min(max(sx - ls.width / 2, 30), W - 30 - ls.width)
                paste(im, ls, lx, ly, min(1, (lt - 0.15) / 0.15) * out, 0.8 + 0.2 * back_out((lt - 0.15) / 0.3))
        elif k == 'title':
            spr = cached('arrive_title', arrive_title)
            sc = 0.85 + 0.15 * back_out(lt / 0.35)
            paste(im, spr, (W - spr.width) / 2, 1420, min(1, lt / 0.2) * out, sc)
        elif k == 'sparkles':
            sp = sprites()['spark']
            rng = np.random.default_rng(11)
            for j in range(14):
                x = rng.uniform(80, 1000); y = rng.uniform(260, 1100); ph = rng.uniform(0, 1); sp_ = rng.uniform(.6, 1.4)
                v = (lt * sp_ + ph) % 1.0
                a = math.sin(v * math.pi)
                paste(im, sp, x, y, a * 0.9, 0.3 + 0.7 * a)


def big_arrow(kind):
    s = 330
    ic = G.arrow_icon(kind, s, G.GOLD2 + (255,), width=0.2)
    sh = G.arrow_icon(kind, s, (0, 0, 0, 255), width=0.2).filter(ImageFilter.GaussianBlur(10))
    out = Image.new('RGBA', (s + 40, s + 40), (0, 0, 0, 0))
    a = sh.getchannel('A').point(lambda v: v * .6); sh.putalpha(a)
    out.alpha_composite(sh, (20, 28)); out.alpha_composite(ic, (20, 20))
    return out


def arrive_title():
    f1 = G.font('pfb', 74); f2 = G.font('sb', 38)
    t1 = 'Llegamos a JHS Joyería'; t2 = 'CENTRO DE BARRANQUILLA'
    w1, h1, b1 = G.text_size(t1, f1); w2, h2, b2 = G.text_size(t2, f2)
    w = max(w1 + 110, w2 + 80) + 60; h = 250
    def fn(d, k, im):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=40 * k, fill=(12, 14, 20, 225), outline=G.GOLD + (220,), width=3 * k)
    im = G.ss(fn, w, h, 2)
    pin = G.arrow_icon('pin', 76, G.GOLD2 + (255,))
    x = (w - (w1 + 90)) / 2
    im.alpha_composite(pin, (int(x), 34))
    d = ImageDraw.Draw(im)
    d.text((x + 90, 40 - b1[1]), t1, font=f1, fill=G.IVORY)
    d.line([(w / 2 - 160, 150), (w / 2 + 160, 150)], fill=G.GOLD + (220,), width=2)
    d.text(((w - w2) / 2, 172 - b2[1]), t2, font=f2, fill=G.GOLD2)
    return im


def captions(im, t):
    for key, t0 in T.vo:
        txt = LINES[key].replace('Jota Hache Ese', 'JHS').replace('noventa segundos', '90 segundos')
        for a, b, c in cached(('chunks', key), lambda: G.chunk_caption(txt, VODUR[key])):
            if t0 + a <= t < t0 + b:
                spr = cached(('cap', c), lambda: G.caption_sprite(c))
                lt = t - t0 - a
                y = 1180 if not (TOTAL - 9.3 < t) else 1200
                paste(im, spr, 0, y - spr.height / 2, min(1, lt / 0.06), 0.94 + 0.06 * ease_out(lt / 0.12))
                return


# ------------------------------------------------------------ intro / end
def render_intro(lt):
    sp = sprites()
    s_all = CUM[-1]
    x0, y0, x1, y1 = seg_bbox(0, s_all)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 250
    z = 0.29 + 0.03 * lt / 6.9
    draw_s = s_all * ease((lt - 0.7) / 3.6)
    ball = G.route_at(draw_s) if lt > 0.7 else None
    im, P = render_map_view(cx, cy, z, draw_s, ball, lt, show_labels=True, label_alpha=min(1, max(0, (lt - 1.0) / 0.5)))
    im.alpha_composite(Image.new('RGBA', (W, H), (8, 9, 12, int(70))))
    im.alpha_composite(VIG)
    # logo
    lg = sp['logo_s']
    paste(im, lg, (W - lg.width) / 2, 120, min(1, lt / 0.4), 0.85 + 0.15 * back_out(lt / 0.5))
    # photo card of destination
    if lt > 4.3:
        u = (lt - 4.3) / 0.4
        card = cached('photo', photo_card)
        dx, dy = P(G.ROUTE[-1])
        paste(im, card, min(dx + 40, W - card.width - 40), max(dy - card.height / 2 - 40, 330), min(1, u), 0.6 + 0.4 * back_out(u))
    # hook texts
    if lt < 3.3:
        spr = cached('hook1', lambda: hook_text(['¿No sabes cómo', 'llegar a', 'JHS Joyería?'], gold_last=True))
        u = (lt - 0.45) / 0.35
        paste(im, spr, (W - spr.width) / 2, 1250, min(1, max(0, u)) * min(1, (3.3 - lt) / 0.15), 0.8 + 0.2 * back_out(u))
    else:
        spr = cached('hook2', lambda: hook_text(['Te mostramos la ruta', 'completa en', '< 90 segundos'], gold_last=True))
        u = (lt - 3.3) / 0.35
        paste(im, spr, (W - spr.width) / 2, 1250, min(1, u), 0.8 + 0.2 * back_out(u))
    if lt < 0.25:
        im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - lt / 0.25)))))
    return im


def hook_text(lines, gold_last=False):
    f = G.font('blk', 84); fl = G.font('pf', 104)
    im = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 10
    for i, ln in enumerate(lines):
        last = i == len(lines) - 1 and gold_last
        ff = fl if last else f
        w_, h_, b = G.text_size(ln, ff)
        d.text(((W - w_) / 2 - b[0], y - b[1]), ln, font=ff, fill=G.GOLD2 if last else (255, 255, 255), stroke_width=7, stroke_fill=(8, 8, 10))
        y += h_ + 26
    return im.crop((0, 0, W, y + 20))


def photo_card():
    fr = Clips.frames('C', 127.5, 0.1)[0]
    ph = Image.fromarray(fr).crop((60, 120, 576, 820)).resize((260, 352), Image.LANCZOS)
    w, h = 280, 372
    def fn(d, k, im):
        d.rounded_rectangle([0, 0, w * k - 1, h * k - 1], radius=26 * k, fill=G.GOLD2 + (255,))
    base = G.ss(fn, w, h, 2)
    m = Image.new('L', (260 * 3, 352 * 3), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 260 * 3 - 1, 352 * 3 - 1], radius=60, fill=255)
    m = m.resize((260, 352), Image.LANCZOS)
    ph = ph.convert('RGBA'); ph.putalpha(m)
    base.alpha_composite(ph, (10, 10))
    return base


END_BG = None


def render_end(lt):
    global END_BG
    sp = sprites()
    if END_BG is None:
        fr = Clips.frames('C', 129.0, 0.1)[0]
        bg = Image.fromarray(fr).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(22))
        bg = Image.blend(bg, Image.new('RGB', (W, H), (8, 9, 12)), 0.62)
        END_BG = bg.convert('RGBA')
    im = END_BG.copy()
    lg = sp['logo']
    u = lt / 0.5
    paste(im, lg, (W - lg.width) / 2, 560, min(1, u), 0.8 + 0.2 * back_out(u))
    t1 = cached('end_sub', lambda: hook_small('Centro de Barranquilla'))
    paste(im, t1, (W - t1.width) / 2, 560 + lg.height + 20, min(1, max(0, (lt - 0.35) / 0.3)))
    cta = cached('cta', lambda: G.tag('Guarda este video para cuando vengas', 44, icon='bookmark'))
    u2 = (lt - 0.7) / 0.35
    paste(im, cta, (W - cta.width) / 2, 1180, min(1, max(0, u2)), 0.7 + 0.3 * back_out(u2))
    spk = sp['spark']; rng = np.random.default_rng(3)
    for j in range(18):
        x = rng.uniform(80, 1000); y = rng.uniform(380, 1500); ph = rng.uniform(0, 1)
        v = (lt * rng.uniform(.6, 1.3) + ph) % 1.0; a = math.sin(v * math.pi)
        paste(im, spk, x, y, a * 0.8, 0.25 + 0.6 * a)
    if lt > TOTAL - 0:  # no-op
        pass
    fo = (3.0 - lt) / 0.35
    if fo < 1:
        im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - max(0, fo))))))
    return im


def hook_small(txt):
    f = G.font('pfi', 54)
    w_, h_, b = G.text_size(txt, f)
    im = Image.new('RGBA', (w_ + 20, h_ + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), txt, font=f, fill=G.IVORY)
    return im


# ------------------------------------------------------------ main frame
def frame(t):
    pc = next(p for p in T.pieces if p['t0'] <= t < p['t1'] + 1e-9)
    lt = t - pc['t0']; box = None
    if pc['kind'] in ('clip', 'freeze'):
        im, box = render_clip(pc, lt)
        im.alpha_composite(VIG_LIGHT)
    elif pc['kind'] == 'map':
        im = render_map(pc, lt, t)
        cpc = pc
        c = cached(('mapcard', pc['title'], pc['sub']), lambda: G.card(cpc['title'], cpc['sub'], cpc['icon']))
        sc = 0.85 + 0.15 * back_out(lt / 0.28)
        paste(im, c, (W - c.width) / 2, 1440 + 40 * (1 - ease_out(lt / 0.25)), min(1, lt / 0.12), sc)
    elif pc['kind'] == 'intro':
        im = render_intro(lt)
    else:
        im = render_end(lt)
    if pc['kind'] not in ('intro', 'end'):
        draw_overlays(im, t, box)
        hud(im, t)
    if pc['kind'] not in ('end', 'intro'):
        captions(im, t)
    # quick cross-fade into pieces of a different kind (whip feel)
    return im.convert('RGB')


def make_vig_light():
    a = np.zeros((H, W), np.float32)
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a += np.clip(1 - y / 420, 0, 1) ** 1.8 * 0.55
    a += np.clip((y - 1350) / 570, 0, 1) ** 1.5 * 0.55
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    a += np.clip(r - 0.85, 0, 1) * 0.35
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(v, 'RGBA')


VIG_LIGHT = make_vig_light()


# ------------------------------------------------------------ audio
def build_audio(path):
    import soundfile as sf
    from scipy.signal import resample_poly
    import audiolib as A
    SR = A.SR; n = int((TOTAL + 0.5) * SR)
    vo = np.zeros(n); act = np.zeros(n)
    for key, t0 in T.vo:
        a, sr = sf.read(f'{HERE}/vo/{key}.wav')
        if a.ndim > 1: a = a.mean(1)
        a = resample_poly(a, 147, 80) if sr == 24000 else a
        a = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 0.12
        i = int(t0 * SR); m = min(len(a), n - i); vo[i:i + m] += a[:m]; act[i:i + m] = 1
    # music ducking envelope
    k = int(0.25 * SR)
    env = np.convolve(act, np.ones(k) / k, mode='same')
    env = np.clip(env * 1.6, 0, 1)
    mus = A.music(TOTAL + 0.5)
    mg = 0.30 - 0.19 * env
    mus = mus * mg[:len(mus), None]
    sfx = np.zeros((n, 2))
    lib = {k_: getattr(A, k_)() for k_ in ['whoosh', 'pop', 'click', 'beep', 'chime', 'ding', 'ticks']}
    base_g = {'whoosh': 0.32, 'pop': 0.35, 'click': 0.4, 'beep': 0.30, 'chime': 0.5, 'ding': 0.35, 'ticks': 0.35}
    for name, t0, g in T.sfx:
        y = lib[name]; i = int(max(0, t0) * SR); m = min(len(y), n - i)
        if m > 0: sfx[i:i + m] += y[:m] * base_g[name] * g
    out = np.stack([vo, vo], 1)
    out[:len(mus)] += mus
    out += sfx
    out /= max(1.0, np.max(np.abs(out)) / 0.95)
    sf.write(path, out.astype(np.float32), SR, subtype='FLOAT')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    os.makedirs(f'{HERE}/out', exist_ok=True)
    print('TOTAL', round(TOTAL, 2))
    if mode == 'preview':
        for ts in sys.argv[2:]:
            frame(float(ts)).save(f'{HERE}/out/p_{float(ts):06.2f}.jpg', quality=88)
        return
    if mode == 'audio':
        build_audio(f'{HERE}/out/mix.wav'); return
    nfr = int(round(TOTAL * FPS))
    a, b = (int(sys.argv[2]), int(sys.argv[3])) if mode == 'part' else (0, nfr)
    outp = f'{HERE}/out/part_{a:05d}.mp4' if mode == 'part' else f'{HERE}/out/video.mp4'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                            '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(frame(i / FPS).tobytes())
        if i % 150 == 0: print(i, '/', nfr, flush=True)
    enc.stdin.close(); enc.wait()


if __name__ == '__main__':
    main()
