import sys, subprocess, numpy as np, wave
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from style import *

SRC = "/root/.claude/uploads/8133a7c7-8cf8-5f4c-b350-10d8c2d82a9f/f10bd89a-WhatsApp_Video_2026-10-12_at_7.47.29_PM.mp4"
OUT = sys.argv[1]
PREVIEW = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
T0, T1 = 0.0, 227.9
DUR = round((T1 - T0) * FPS) / FPS
def _p(img, im, pos): img.paste(im, pos, im)

SECS = [(0.0, 89.0, "Función racional"), (89.0, 163.5, "Función con raíz cuadrada"), (163.5, 999, "Función con raíz cúbica")]
EVENTS = [
    (9.0, 0, "main", "Quinta función", "f(x) = 5/x − 2", "Función racional"),
    (13.0, 0, "step", "Clasificación", "Algebraica racional", "La x está en el denominador"),
    (19.0, 0, "step", "Dominio", "ℝ − {0}", "No se puede dividir entre 0"),
    (25.0, 0, "step", "Rango", "ℝ − {−2}", None),
    (37.0, 0, "step", "Intercepto con X", "(2.5, 0)", "5/x − 2 = 0  →  x = 2.5"),
    (49.0, 0, "step", "Intercepto con Y", "No tiene", "x = 0 no está en el dominio"),
    (67.0, 0, "step", "Comportamiento", "Decreciente", "En cada una de sus ramas"),
    (74.0, 0, "step", "Asíntota vertical", "x = 0", None),
    (80.0, 0, "step", "Asíntota horizontal", "y = −2", None),
    (92.0, 1, "main", "Sexta función", "f(x) = √(x − 3)", "Función irracional"),
    (98.0, 1, "step", "Clasificación", "Algebraica irracional", "La x está dentro de una raíz"),
    (104.0, 1, "step", "Dominio", "x ≥ 3", "x − 3 ≥ 0"),
    (115.0, 1, "step", "Rango", "y ≥ 0", "La raíz cuadrada no da negativos"),
    (128.0, 1, "step", "Intercepto con Y", "No tiene", None),
    (139.0, 1, "step", "Intercepto con X", "(3, 0)", "Donde empieza la gráfica"),
    (151.0, 1, "step", "Comportamiento", "Creciente", "Sube hacia la derecha"),
    (168.0, 2, "main", "Séptima función", "f(x) = ∛(x + 2)", "Función irracional"),
    (175.0, 2, "step", "Clasificación", "Algebraica irracional", "La x está dentro de una raíz cúbica"),
    (182.0, 2, "step", "Dominio", "D = ℝ", "Existe la raíz cúbica de cualquier número"),
    (194.0, 2, "step", "Rango", "R = ℝ", None),
    (205.0, 2, "step", "Intercepto con X", "(−2, 0)", "∛(−2 + 2) = ∛0 = 0"),
    (219.0, 2, "step", "Intercepto con Y", "(0, ≈ 1.26)", "f(0) = ∛2 ≈ 1.26"),
]
CARDS = []
for (ts, sec, kind, lab, txt, sub) in EVENTS:
    im, pad = make_card(lab, txt, sub=sub, accent=(AMBER if kind == "main" else VIOLET2), big=(50 if kind == "main" else 44))
    CARDS.append((ts - T0, sec, kind, im, pad))
SECS = [(a - T0, b - T0, n) for a, b, n in SECS]

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

def draw_header(img, T):
    d = ImageDraw.Draw(img, "RGBA")
    for sa, sb, name in SECS:
        if not (sa <= T < sb): continue
        a = ease((T - sa + .1) / .5) * clamp((sb - T) / .3)
        d.text((60, 38), "INTEGRANTE 4  ·  DUSTIN GÓMEZ", font=font("sb", 16), fill=LAV + (int(220 * a),))
        d.text((60 - (1 - a) * 30, 60), name, font=font("xb", 46), fill=WHITE + (int(255 * a),))
        w = font("xb", 46).getlength(name)
        d.rounded_rectangle([60, 120, 60 + w * .35 * a, 125], 3, fill=PINK + (int(255 * a),))

PW, PH = 366, 600
PMASK = rounded_mask(PW, PH, 28); PGLOW, PGPAD = glow_rect(PW, PH, 28, VIOLET, 22, 130)
PX, PY = W - 60 - PW, 60
cmd = ["ffmpeg", "-v", "error", "-ss", str(T0), "-i", SRC, "-t", str(DUR), "-vf",
       f"fps={FPS},crop=500:820:38:102,scale={PW}:{PH}:flags=lanczos,eq=contrast=1.05:saturation=1.08", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
dec = subprocess.Popen(cmd, stdout=subprocess.PIPE)
if not PREVIEW:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
n = round(DUR * FPS); last = None
for i in range(n):
    raw = dec.stdout.read(PW * PH * 3)
    if len(raw) == PW * PH * 3: last = Image.frombuffer("RGB", (PW, PH), raw)
    T = i / FPS
    if PREVIEW and not any(abs(T - p) < .5 / FPS for p in PREVIEW): continue
    img = background(T + 70)
    draw_header(img, T)
    _p(img, PGLOW, (PX - PGPAD, PY - PGPAD)); img.paste(last, (PX, PY), PMASK)
    ImageDraw.Draw(img, "RGBA").rounded_rectangle([PX, PY, PX + PW, PY + PH], 28, outline=(196, 181, 253, 180), width=2)
    draw_cards(img, T)
    if PREVIEW: img.save(f"{OUT}.{T:.1f}.png")
    else: enc.stdin.write(img.tobytes())
dec.stdout.close()
if not PREVIEW:
    enc.stdin.close(); enc.wait()
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T0), "-i", SRC, "-t", str(DUR), "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    need = int(round(DUR * 48000)); a = np.pad(a, (0, max(0, need - len(a))))[:need].copy()
    r = np.linspace(0, 1, 2400, dtype=np.float32); a[:2400] *= r; a[-2400:] *= r[::-1]
    with wave.open(OUT + ".audio.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
print("done", DUR)
