#!/usr/bin/env python3
"""MONTAJE RÁPIDO — "Todo lo que se vivió".

Genera montaje/salida/montaje_rapido.mp4 (1080x1920, 30 fps) a partir de los
clips de montaje/clips/. Requiere ffmpeg (con zscale) y numpy.

    python3 montaje/montaje.py

Ritmo: 150 BPM -> 1 semicorchea = 0.1 s = 3 fotogramas. Todas las duraciones
de la línea de tiempo están en semicorcheas, así cada corte cae en un golpe.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import musica

ROOT = Path(__file__).resolve().parent
CLIPS = ROOT / "clips"
BUILD = ROOT / "build"
OUT = ROOT / "salida" / "montaje_rapido.mp4"
FPS = 30
U = 0.1  # semicorchea en segundos
W, H = 1080, 1920

SOURCES = {
    "A": "IMG_3854.mov",  # banner "Día de la Filosofía", paneo a la derecha
    "B": "IMG_3855.mov",  # "Laberinto Filosófico"
    "C": "IMG_3856.mov",  # salón: compañeros, profesora en tarima
    "D": "IMG_3861.mov",  # póster de Aristóteles, paneo a la derecha
    "E": "IMG_3862.mov",  # compañeros jugando en el patio (dado, tablero)
}


def S(src, t, cx, cy, z0, z1=None, units=4, speed=1.0, dx=0.0, dy=0.0,
      whip_in=0, whip_out=0, ramp=None, blur=False, flash=0.0, shake=0.0, grade=None):
    """Un plano. cx,cy: centro normalizado; z: zoom (1 = cuadro completo).
    whip_in/whip_out: -1 izquierda, +1 derecha. ramp: (vel_a, vel_b, fracción)."""
    return dict(src=src, t=t, cx=cx, cy=cy, z0=z0, z1=z1 if z1 else z0 * 1.06,
                units=units, speed=speed, dx=dx, dy=dy, whip_in=whip_in,
                whip_out=whip_out, ramp=ramp, blur=blur, flash=flash, shake=shake,
                grade=grade)


# ---------------------------------------------------------------------------
# LÍNEA DE TIEMPO (unidades = semicorcheas de 0.1 s)
# El paneo de la cámara en A va hacia la derecha: los whips siguen esa dirección
# para que los planos "empujen" uno hacia el siguiente.
# ---------------------------------------------------------------------------
TIMELINE = [
    # --- Fase 1 (c1-c2): arranque, planos de 0.4-0.8 s ---------------------
    S("A", 0.00, .45, .45, 1.15, 1.35, units=8),                     # banner + globos, push-in
    S("C", 0.20, .50, .50, 1.00, 1.12, units=8, whip_out=+1),        # el salón completo
    S("B", 0.40, .50, .48, 1.35, 1.10, units=6, whip_in=+1),          # laberinto (pull-out)
    S("E", 0.90, .50, .48, 1.60, 1.80, units=6,                      # mano lanzando el dado:
      ramp=(0.6, 2.0, 0.5), blur=True),                               # speed ramp lento->rápido
    S("D", 1.30, .50, .10, 1.90, 2.10, units=4, dx=.05),             # "ARISTÓTELES" (sigue el paneo)

    # --- Fase 2 (c3-c4): sube, con una cámara lenta de contraste ------------
    S("B", 0.30, .60, .45, 2.80, 3.30, units=4, flash=0.25),          # el ojo de la pintura (mirada)
    S("E", 2.50, 1.0, .22, 1.70, 1.85, units=4),                     # compañero mira a cámara y sonríe
    S("C", 0.50, .38, .58, 1.60, 1.75, units=8, ramp=(3.0, 0.3, 0.3)),  # CÁMARA LENTA: rampa
    S("D", 1.70, .50, .33, 2.60, 2.90, units=4),                     # el rostro de Aristóteles
    S("B", 2.00, .50, .13, 2.30, 2.50, units=4, whip_out=+1),        # título "LABERINTO"
    S("C", 1.00, .62, .46, 2.40, 2.70, units=4, whip_in=+1),         # globos rosados + sombrero
    S("E", 3.90, .38, .22, 2.20, 2.40, units=4),                     # concentración sobre el tablero

    # --- Fase 3 (c5): 0.3-0.4 s ---------------------------------------------
    S("A", 2.10, .52, .41, 2.30, 2.70, units=4, dx=.04, flash=0.2),  # "FILOSOFÍA"
    S("E", 1.40, .45, .52, 2.60, 2.90, units=3, speed=1.5, blur=True),  # el dado sobre el tablero
    S("C", 1.60, .37, .40, 3.00, 3.20, units=3, dx=-.02),            # profesora en tarima
    S("D", 2.70, .70, .50, 2.40, 2.60, units=3, whip_out=-1),         # Lógica / Metafísica / Ciencia
    S("B", 3.00, .46, .87, 2.40, 2.60, units=3, whip_in=-1),          # casillas de colores

    # --- Fase 4 (c6, build): 0.2-0.3 s --------------------------------------
    S("C", 1.10, .28, .60, 2.60, 2.90, units=3, speed=1.5, blur=True),  # compañera caminando
    S("A", 0.00, .20, .58, 2.40, 2.80, units=3, shake=8),            # globos de colores
    S("E", 2.50, .75, .78, 2.60, 2.90, units=2, flash=0.2),          # papeles de colores del juego
    S("D", 1.80, .45, .68, 2.40, 2.70, units=2),                     # "La excelencia no es un acto..."
    S("C", 2.50, .36, .62, 2.60, 2.90, units=2),                     # globo burbuja con luces
    S("B", 1.50, .38, .60, 2.80, 3.10, units=2, shake=8),            # clavijas del laberinto
    S("E", 0.60, .45, .10, 2.40, 2.70, units=2, flash=0.3),          # el patio, gente pasando

    # --- RÁFAGA FINAL (c7, drop): 12 flashes de 0.1-0.2 s --------------------
    S("E", 2.40, 1.0, .24, 1.60, 1.80, units=2, flash=0.45, shake=10),
    S("A", 1.80, .50, .40, 1.20, 1.45, units=2, flash=0.45, shake=10),
    S("D", 1.50, .52, .32, 2.00, 2.30, units=2, flash=0.45),
    S("C", 0.70, .40, .55, 1.90, 2.10, units=1, flash=0.5),
    S("B", 0.80, .60, .45, 3.20, 3.80, units=1, flash=0.5),
    S("E", 1.20, .48, .48, 2.20, 2.50, units=1, flash=0.5),
    S("A", 0.60, .60, .38, 2.20, 2.50, units=1, flash=0.5),
    S("D", 1.20, .50, .10, 2.40, 2.70, units=1, flash=0.5),
    S("C", 3.30, .36, .62, 3.00, 3.30, units=1, flash=0.5),
    S("E", 4.10, .32, .25, 2.00, 2.30, units=1, flash=0.5),
    S("B", 3.80, .46, .87, 2.80, 3.10, units=1, flash=0.5),
    S("A", 3.40, .85, .28, 1.60, 1.90, units=2, flash=0.45, shake=12),
]

# Toma final: corte en seco a silencio + cámara lenta del salón con el texto.
FINAL = dict(src="C", t=0.90, cx=.48, cy=.50, z0=1.04, z1=1.16, seconds=5.0, speed=0.35)
FINAL_TEXT = ["Y esto… fue solo una parte", "de lo que vivimos."]
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])
        sys.exit(1)
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)]))


def make_proxies():
    """HDR HLG 10 bits (iPhone) -> SDR bt709, vertical 2160x3840, 30 fps."""
    BUILD.mkdir(exist_ok=True)
    tonemap = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
               "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")
    for key, name in SOURCES.items():
        out = BUILD / f"proxy_{key}.mp4"
        if out.exists():
            continue
        print(f"  proxy {key} <- {name}")
        run(["ffmpeg", "-v", "error", "-y", "-i", str(CLIPS / name), "-an", "-vf", tonemap,
             "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-g", "6", str(out)])


def zoompan_expr(sh, src_frames, out_frames):
    """Zoom animado + deriva + whip (desplazamiento rápido) + temblor."""
    n = max(src_frames - 1, 1)
    p = f"min(on/{n}\\,1)"
    # p suavizado (ease in-out) para que el zoom se sienta de cámara
    pe = f"(0.5-0.5*cos(PI*{p}))"
    z = f"{sh['z0']}+({sh['z1']}-{sh['z0']})*{pe}"
    k = max(2, round(3 * sh["speed"]))  # whip dura ~3 fotogramas de salida
    whip = "0"
    if sh["whip_in"]:
        # entra desde el lado contrario a la dirección del movimiento
        whip += f"-({sh['whip_in']})*0.45*iw/zoom*pow(max(0\\,1-on/{k})\\,2)"
    if sh["whip_out"]:
        whip += f"+({sh['whip_out']})*0.45*iw/zoom*pow(max(0\\,(on-({n}-{k}))/{k})\\,2)"
    shake_x = f"{sh['shake']}*sin(on*2.9)*iw/1080" if sh["shake"] else "0"
    shake_y = f"{sh['shake']}*cos(on*3.7)*ih/1920" if sh["shake"] else "0"
    x = (f"max(0\\,min(iw-iw/zoom\\,({sh['cx']}+{sh['dx']}*{pe})*iw-iw/zoom/2"
         f"+{whip}+{shake_x}))")
    y = (f"max(0\\,min(ih-ih/zoom\\,({sh['cy']}+{sh['dy']}*{pe})*ih-ih/zoom/2"
         f"+{shake_y}))")
    return f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS}"


def render_shot(i, sh, text=None):
    out_frames = round(sh["units"] * U * FPS) if "units" in sh else round(sh["seconds"] * FPS)
    D = out_frames / FPS
    ramp = sh.get("ramp")
    if ramp:
        sa, sb, frac = ramp
        d1 = D * frac
        src_len = sa * d1 + sb * (D - d1)
        a = sa * d1
        setpts = f"setpts='if(lt(T\\,{a})\\,T/{sa}\\,{d1}+(T-{a})/{sb})/TB'"
        slow = min(sa, sb) < 1
        fast = max(sa, sb) > 1
    else:
        s = sh["speed"]
        src_len = s * D
        setpts = f"setpts=PTS/{s}"
        slow, fast = s < 1, s > 1
    src = BUILD / f"proxy_{sh['src']}.mp4"
    avail = duration(src) - 0.05
    start = max(0.0, min(sh["t"], avail - src_len))
    src_frames = round(src_len * FPS) + 2

    chain = [zoompan_expr(sh, src_frames, out_frames), setpts]
    if slow:
        chain.append(f"minterpolate=fps={FPS * 2}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
    if fast and sh.get("blur"):
        chain.append("tmix=frames=3:weights='1 2 1'")  # motion blur
    # recortar justo después de fps: si no, minterpolate + fps siguen generando
    # fotogramas al final del flujo y ffmpeg se queda sin memoria
    chain += [f"fps={FPS}", f"trim=end_frame={out_frames}", "setpts=PTS-STARTPTS"]
    # whip: desenfoque direccional en los fotogramas del barrido
    wins = []
    if sh.get("whip_in"):
        wins.append("lt(t\\,0.1)")
    if sh.get("whip_out"):
        wins.append(f"gt(t\\,{D - 0.11:.3f})")
    if wins:
        chain.append(f"dblur=angle=0:radius=55:enable='{'+'.join(wins)}'")
    if sh.get("flash"):
        chain.append(f"eq=brightness='{sh['flash']}*max(0\\,1-t/0.07)':eval=frame")
    chain.append(sh.get("grade") or "eq=contrast=1.08:saturation=1.18:gamma=0.98")
    if text:
        chain += text
    chain.append("format=yuv420p")

    out = BUILD / f"shot_{i:02d}.mp4"
    stamp = BUILD / f"shot_{i:02d}.txt"
    key = repr((sorted((k, str(v)) for k, v in sh.items()), text, chain))
    if out.exists() and stamp.exists() and stamp.read_text() == key:
        return out  # plano sin cambios: se reutiliza
    run(["ffmpeg", "-v", "error", "-y", "-filter_threads", "2", "-ss", f"{start:.3f}", "-t", f"{src_len + 0.3:.3f}",
         "-i", str(src), "-vf", ",".join(chain), "-frames:v", str(out_frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-threads", "2", "-r", str(FPS), str(out)])
    got = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                   "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(out)]))
    if got != out_frames:
        sys.exit(f"plano {i}: {got} fotogramas, se esperaban {out_frames}")
    stamp.write_text(key)
    return out


def final_text_filters():
    filters = []
    for k, line in enumerate(FINAL_TEXT):
        tf = BUILD / f"texto_{k}.txt"
        tf.write_text(line, encoding="utf-8")
        t_in = 0.7 + k * 1.0
        alpha = f"if(lt(t\\,{t_in})\\,0\\,min(1\\,(t-{t_in})/0.8))*min(1\\,max(0\\,(4.7-t)/0.6))"
        filters.append(
            f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=74:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=0:shadowy=3:"
            f"x=(w-text_w)/2:y=h*0.70+{k}*100:alpha='{alpha}'")
    return filters


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("falta ffmpeg")
    print("1/4 proxies SDR")
    make_proxies()

    print("2/4 planos")
    files, cuts, whips, slow_spans = [], [], [], []
    t = 0.0
    for i, sh in enumerate(TIMELINE):
        files.append(render_shot(i, sh))
        cuts.append(round(t, 4))
        if sh["whip_in"]:
            whips.append(round(t, 4))
        if sh["ramp"] and min(sh["ramp"][:2]) < 1:
            slow_spans.append((t, t + sh["units"] * U))
        t += sh["units"] * U
        print(f"   {i:02d} {sh['src']} {sh['units'] * U:.1f}s  -> corte en {cuts[-1]:.1f}s")
    end_music = t
    drop = end_music - 16 * U  # el último compás = ráfaga final
    grade_final = ("eq=contrast=1.02:saturation=0.72:brightness=-0.05:gamma=1.02,"
                   "colorbalance=rs=.06:gs=.02:bs=-.06:rm=.04:bm=-.04,vignette=PI/3.2")
    fin = dict(FINAL, units=None, dx=0, dy=0, whip_in=0, whip_out=0, shake=0, flash=0,
               blur=False, ramp=None, grade=grade_final)
    fin.pop("units")
    files.append(render_shot(len(TIMELINE), fin, text=final_text_filters()))
    total = end_music + FINAL["seconds"]
    print(f"   montaje: {end_music:.1f}s  ({len(TIMELINE)} planos, ráfaga desde {drop:.1f}s)"
          f" + toma final {FINAL['seconds']:.1f}s = {total:.1f}s")

    print("3/4 música")
    audio = musica.render(cuts, whips, drop, end_music, total, slow_spans)
    wav = BUILD / "musica.wav"
    musica.write_wav(str(wav), audio)

    print("4/4 unión final")
    lst = BUILD / "lista.txt"
    lst.write_text("".join(f"file '{f.name}'\n" for f in files))
    OUT.parent.mkdir(exist_ok=True)
    fade_from = total - 0.8
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-i", str(wav),
         "-vf", f"vignette=PI/5,noise=alls=2:allf=t,fade=t=out:st={fade_from:.2f}:d=0.8,format=yuv420p",
         "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "12M", "-bufsize", "24M", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)])
    print(f"listo: {OUT}")


if __name__ == "__main__":
    main()
