#!/usr/bin/env python3
"""MONTAJE RÁPIDO — "Todo lo que se vivió" (AURA FEST).

Genera montaje/salida/montaje_rapido.mp4 (1080x1920, 30 fps) a partir de los
clips de montaje/clips/ y la canción montaje/clips/cancion.mp4.
Requiere ffmpeg (con zscale).

    python3 montaje/montaje.py

Ritmo: los cortes caen sobre los golpes de la canción (BEATS, ~70 BPM,
detectados con librosa). La edición se acelera por tramos: 2 golpes por plano,
1 golpe, 1/2 golpe y una ráfaga final de 1/4 de golpe en el clímax.
"""
import shutil
import subprocess
import sys
from pathlib import Path

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
    # WhatsApp (464x832, SDR): se escalan con enfoque y se usan con poco zoom
    "F": "WA_122814.mp4",  # exposición al aire libre: compañeros disfrazados, risas
    "G": "WA_122827.mp4",  # compañero con sombrero señalando a cámara
    "H": "WA_122835.mp4",  # "La aventura del pensamiento": compañera saluda y ríe
    "I": "WA_122840.mp4",  # dado gigante y fichas; compañera jugando y saludando
    "J": "WA_123418.mp4",  # compañeras muertas de la risa (1 s)
    "K": "WA_123453.mp4",  # baile en el patio
    "L": "WA_123857.mp4",  # el castillo: escudo y compañeros disfrazados
    "M": "WA_124102.mp4",  # dos compañeros disfrazados leyendo un libro
    "N": "WA_124138.mp4",  # la galería: globos, Kant, Savater, flores, portafolios
    "O": "WA_123828.mp4",  # risas en el auditorio
    "P": "WA_123836.mp4",  # pintando el mural en el patio
    "Q": "WA_124238.mp4",  # pasillo con banderines, compañeras caminando
    "R": "WA_124245.mp4",  # entrada "Día de la Filosofía", pulgar arriba, BIENVENIDOS
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
# Golpes de la canción (s), detectados con librosa.beat.beat_track (~70 BPM).
BEATS = [1.0, 1.88, 2.69, 3.55, 4.39, 5.27, 6.13, 6.99, 7.8, 8.64, 9.5, 10.31, 11.22,
         12.0, 12.84, 13.7, 14.58, 15.51, 16.39, 17.25, 18.13, 18.97, 19.78, 20.67,
         21.57, 22.45, 23.36, 24.24, 25.08, 25.89, 26.75, 27.56, 28.44, 29.35, 30.21,
         31.07, 31.93, 32.79, 33.65, 34.5, 35.39, 36.22, 37.06, 37.92, 38.78, 39.64,
         40.5, 41.33, 42.14, 43.05, 43.89, 44.77, 45.6, 46.46, 47.32, 48.18, 49.04,
         49.9, 50.76, 51.62, 52.45, 53.31, 54.17]
SONG = "cancion.mp4"
SONG_END = 55.0  # después viene el jingle de TikTok


def beat(i, frac=0.0):
    """Tiempo del golpe i (+ fracción hacia el siguiente)."""
    return BEATS[i] + frac * (BEATS[i + 1] - BEATS[i])


def cut_points():
    """Cortes: intro, 2 golpes/plano, 1 golpe y un clímax suave a 1/2 golpe."""
    cuts = [0.0]
    cuts += [beat(i) for i in range(2, 32, 2)]          # estrofa: 15 planos
    cuts += [beat(i) for i in range(32, 53)]            # sube: 21 planos
    cuts += [beat(i, f) for i in range(53, 58) for f in (0, .5)]  # clímax: 10
    cuts.append(beat(58))                               # -> toma final
    return cuts


XFADE = 0.2  # fundido cruzado suave entre planos (empieza justo en el golpe)


# Regla: cada plano es un momento distinto (nada se repite); se priorizan los
# momentos felices, las reacciones y los lugares más bonitos.
TIMELINE = [
    # --- Intro: "Los sabios dicen..." ---------------------------------------
    S("R", 0.00, .50, .38, 1.15, 1.21, speed=0.6),                   # entrada "Día de la Filosofía"

    # --- Estrofa: 2 golpes por plano, cámara lenta y fundidos suaves --------
    S("A", 1.00, .50, .40, 1.10, 1.16, speed=0.8, dx=.04),  # banner principal (4K)
    S("H", 2.40, .45, .25, 1.30, 1.37, speed=0.5),       # saluda y ríe
    S("Q", 3.30, .50, .35, 1.10, 1.16, speed=0.7),       # pasillo de banderines
    S("F", 4.30, .62, .33, 1.40, 1.47, speed=0.7),       # disfrazado riéndose
    S("N", 3.40, .30, .30, 1.30, 1.37, speed=0.7),       # rosas rojas
    S("J", 0.00, .42, .45, 1.25, 1.31, speed=0.6),       # muertas de la risa
    S("L", 1.30, .45, .25, 1.30, 1.37, speed=0.7),       # escudo del castillo
    S("M", 2.00, .50, .30, 1.15, 1.21, speed=0.7),       # leyendo juntos, disfrazados
    S("I", 2.90, .55, .30, 1.35, 1.42, speed=0.6),       # saluda desde el juego
    S("P", 0.50, .50, .35, 1.25, 1.19, speed=0.7),       # pintando el mural
    S("R", 4.40, .50, .40, 1.15, 1.21, speed=0.7),       # llega con el pulgar arriba
    S("C", 2.20, .36, .62, 2.60, 2.73, speed=0.7),       # globo burbuja con luces
    S("K", 1.50, .60, .45, 1.20, 1.26, speed=0.8),       # baile en el patio
    S("D", 1.40, .50, .33, 2.40, 2.52, speed=0.7),       # el rostro de Aristóteles
    S("E", 2.40, 1.0, .22, 1.70, 1.78, speed=0.6),       # mira a cámara y sonríe

    # --- Sube: 1 golpe por plano, fundidos suaves --------------------------------------------
    S("G", 2.60, .50, .30, 1.30, 1.37),                   # señala a cámara
    S("O", 0.10, .65, .30, 1.30, 1.37),                              # risas en el auditorio
    S("N", 0.50, .50, .40, 1.15, 1.21),                 # globos y "Cuadros Vivos"
    S("R", 7.00, .50, .40, 1.20, 1.26),                  # BIENVENIDOS
    S("F", 0.30, .45, .30, 1.30, 1.37),                              # posando con corbata
    S("L", 4.20, .50, .40, 1.20, 1.26),                              # disfrazados en el castillo
    S("C", 1.20, .40, .40, 2.80, 2.94, dx=-.02),                     # profesora en tarima
    S("A", 3.00, .80, .30, 1.90, 1.99),                              # racimo de globos
    S("K", 3.00, .55, .55, 1.20, 1.26),                     # el grupo bailando
    S("M", 3.40, .30, .20, 1.60, 1.68),                              # sonrisa del disfrazado
    S("N", 11.50, .60, .40, 1.25, 1.31),                # Savater
    S("B", 0.40, .50, .48, 1.30, 1.24),                  # laberinto filosófico
    S("O", 2.20, .60, .25, 1.40, 1.47),                              # tapándose la risa
    S("H", 0.80, .50, .60, 1.30, 1.37),                              # "la aventura del pensamiento"
    S("F", 6.00, .60, .33, 1.50, 1.58),                              # sonrisa del expositor
    S("Q", 2.00, .65, .55, 1.20, 1.26, dx=.05),                      # compañeras por el pasillo
    S("N", 5.00, .50, .60, 1.20, 1.26, dx=.04),                      # portafolios de filosofía
    S("N", 15.00, .60, .60, 1.15, 1.21),                             # las mesas de la galería

    S("G", 3.60, .50, .40, 1.30, 1.37),                              # el aro rosado arriba
    S("L", 6.80, .50, .40, 1.25, 1.31),                              # todos tras el castillo
    S("N", 9.00, .40, .35, 1.30, 1.37),                              # ramo de flores

    # --- Clímax: 1/2 golpe, suave --------------------------------------------
    S("H", 3.95, .60, .30, 1.40, 1.47),                              # carcajada
    S("O", 4.30, .45, .38, 1.50, 1.58),                              # sonrisa con gafas
    S("K", 0.50, .40, .45, 1.30, 1.37),                              # arranca el baile
    S("F", 2.00, .50, .45, 1.20, 1.26),                              # todos alrededor del juego
    S("I", 2.00, .55, .35, 1.30, 1.37),                              # concentrada en el juego
    S("M", 0.60, .50, .30, 1.25, 1.31),                              # pasando las páginas
    S("L", 9.60, .50, .50, 1.10, 1.16),                              # el castillo completo
    S("Q", 0.20, .30, .25, 1.40, 1.47),                              # globos en la esquina
    S("R", 13.00, .40, .75, 1.30, 1.37),                             # compañeras con sus libros
    S("G", 1.20, .50, .30, 1.40, 1.47),                              # el sombrero
]

# Toma final: corte en seco a silencio + cámara lenta del salón con el texto.
FINAL = dict(src="R", t=1.70, cx=.50, cy=.50, z0=1.04, z1=1.16, seconds=5.5, speed=0.35)
FINAL_TEXT = ["Y esto… fue solo una parte", "de lo que vivimos."]
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FINAL_TITLE = "AURA FEST"
FONT_TITLE = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
CREDITS_BY = "PRESENTADO POR"
CREDITS = ["Dustin Gomez", "Jairo Maldonado", "Edgar Rivero"]
CREDITS_SECONDS = 3.5


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
    """HDR HLG 10 bits (iPhone) -> SDR bt709, vertical 2160x3840, 30 fps.
    Clips SDR de baja resolución (WhatsApp) -> escalados a 1080 con enfoque."""
    BUILD.mkdir(exist_ok=True)
    tonemap = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
               "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30")
    upscale = "scale=1080:1920:flags=lanczos,unsharp=5:5:0.7:5:5:0,format=yuv420p,fps=30"
    for key, name in SOURCES.items():
        out = BUILD / f"proxy_{key}.mp4"
        if out.exists():
            continue
        print(f"  proxy {key} <- {name}")
        transfer = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=color_transfer", "-of", "csv=p=0", str(CLIPS / name)]).strip()
        vf = tonemap if transfer in ("arib-std-b67", "smpte2084") else upscale
        run(["ffmpeg", "-v", "error", "-y", "-i", str(CLIPS / name), "-an", "-vf", vf,
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
    chain.append(sh.get("grade") or "eq=contrast=1.06:saturation=1.05:gamma=0.98")
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
    end = FINAL["seconds"] - 0.3
    for k, line in enumerate(FINAL_TEXT):
        tf = BUILD / f"texto_{k}.txt"
        tf.write_text(line, encoding="utf-8")
        t_in = 0.5 + k * 0.8
        alpha = f"if(lt(t\\,{t_in})\\,0\\,min(1\\,(t-{t_in})/0.8))*min(1\\,max(0\\,({end}-t)/0.6))"
        filters.append(
            f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=74:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=0:shadowy=3:"
            f"x=(w-text_w)/2:y=h*0.70+{k}*100:alpha='{alpha}'")
    # nombre del evento: aparece después de la frase, con un leve "zoom out"
    t_in = 2.3
    alpha = f"if(lt(t\\,{t_in})\\,0\\,min(1\\,(t-{t_in})/0.5))*min(1\\,max(0\\,({end}-t)/0.6))"
    size = f"150-30*min(1\\,max(0\\,(t-{t_in})/0.6))"
    filters.append(
        f"drawtext=fontfile={FONT_TITLE}:text='{FINAL_TITLE}':fontsize='{size}':"
        f"fontcolor=0xF6E7C1:shadowcolor=black@0.75:shadowx=0:shadowy=4:"
        f"x=(w-text_w)/2:y=h*0.58-text_h/2:alpha='{alpha}'")
    filters.append(f"fade=t=out:st={FINAL['seconds'] - 0.6}:d=0.6")  # a negro, para dar paso a los créditos
    return filters


def render_credits():
    """Placa final en negro: "Presentado por" + nombres."""
    frames = round(CREDITS_SECONDS * FPS)
    end = CREDITS_SECONDS - 0.5

    def alpha(t_in):
        return f"if(lt(t\\,{t_in})\\,0\\,min(1\\,(t-{t_in})/0.6))*min(1\\,max(0\\,({end}-t)/0.5))"

    by = BUILD / "creditos_por.txt"
    by.write_text(CREDITS_BY, encoding="utf-8")
    vf = [f"drawtext=fontfile={FONT_TITLE}:textfile={by}:fontsize=46:fontcolor=0xF6E7C1:"
          f"x=(w-text_w)/2:y=h*0.40:alpha='{alpha(0.3)}'",
          f"drawbox=x=iw/2-90:y=ih*0.40+80:w=180:h=3:color=0xF6E7C1@0.8:t=fill:"
          f"enable='gte(t\\,0.5)'"]
    for k, name in enumerate(CREDITS):
        tf = BUILD / f"creditos_{k}.txt"
        tf.write_text(name, encoding="utf-8")
        vf.append(f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=84:fontcolor=white:"
                  f"x=(w-text_w)/2:y=h*0.40+140+{k}*120:alpha='{alpha(0.7 + 0.35 * k)}'")
    out = BUILD / "creditos.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         f"color=c=black:s={W}x{H}:r={FPS}:d={CREDITS_SECONDS}",
         "-vf", ",".join(vf) + ",format=yuv420p", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-r", str(FPS), str(out)])
    return out


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("falta ffmpeg")
    print("1/4 proxies SDR")
    make_proxies()

    print("2/4 planos")
    cuts = cut_points()
    assert len(cuts) == len(TIMELINE) + 1, (len(cuts), len(TIMELINE))
    frames_at = [round(c * FPS) for c in cuts]  # cortes en fotogramas exactos
    xf = round(XFADE * FPS)  # cada plano dura un poco más para el fundido
    files = []
    for i, sh in enumerate(TIMELINE):
        sh = dict(sh, units=(frames_at[i + 1] - frames_at[i] + xf) / (U * FPS))
        files.append(render_shot(i, sh))
        print(f"   {i:02d} {sh['src']} {(frames_at[i + 1] - frames_at[i]) / FPS:.2f}s"
              f"  -> corte en {cuts[i]:.2f}s")
    end_montage = frames_at[-1] / FPS
    grade_final = ("eq=contrast=1.02:saturation=0.80:brightness=-0.04:gamma=1.02,"
                   "colorbalance=rs=.06:gs=.02:bs=-.06:rm=.04:bm=-.04,vignette=PI/3.2")
    fin = dict(FINAL, dx=0, dy=0, whip_in=0, whip_out=0, shake=0, flash=0,
               blur=False, ramp=None, grade=grade_final)
    files.append(render_shot(len(TIMELINE), fin, text=final_text_filters()))
    credits = render_credits()
    total = end_montage + FINAL["seconds"] + CREDITS_SECONDS
    print(f"   montaje: {end_montage:.2f}s ({len(TIMELINE)} planos) + toma final "
          f"{FINAL['seconds']:.1f}s + créditos {CREDITS_SECONDS:.1f}s = {total:.2f}s")

    print("3/4 canción")
    wav = BUILD / "cancion_cortada.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(CLIPS / SONG), "-vn",
         "-af", f"atrim=0:{SONG_END},afade=t=out:st={SONG_END - 0.6}:d=0.6,apad",
         "-t", f"{total:.3f}", "-ar", "48000", "-ac", "2", str(wav)])

    print("4/4 unión final con look de época")
    OUT.parent.mkdir(exist_ok=True)
    # fundidos cruzados: cada transición empieza exactamente en el golpe
    inputs, graph = [], []
    for k, f in enumerate(files + [credits]):
        inputs += ["-i", str(f)]
        graph.append(f"[{k}:v]settb=AVTB,fps={FPS},format=yuv420p[s{k}]")
    prev = "s0"
    for k in range(1, len(files)):
        graph.append(f"[{prev}][s{k}]xfade=transition=fade:duration={XFADE}:"
                     f"offset={frames_at[k] / FPS:.4f}[x{k}]")
        prev = f"x{k}"
    graph.append(f"[{prev}][s{len(files)}]concat=n=2:v=1:a=0[m]")
    look = ",".join([
        # brillo suave tipo ensueño
        "split[a][b];[b]gblur=sigma=22[g];[a][g]blend=all_mode=screen:all_opacity=0.22",
        # cálido / dorado con un 25 % de sepia
        "colorbalance=rs=.07:gs=.03:bs=-.07:rm=.05:bm=-.05:rh=.03:bh=-.05",
        "colorchannelmixer=.848:.192:.047:0:.087:.9215:.042:0:.068:.1335:.783",
        "eq=saturation=0.9:contrast=1.04",
        "vignette=PI/4.2",
        "noise=alls=5:allf=t",
        f"fade=t=out:st={total - 0.8:.2f}:d=0.8",
        "format=yuv420p",
    ])
    graph.append(f"[m]{look}[v]")
    na = len(files) + 1
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", str(wav),
         "-filter_complex", ";".join(graph), "-map", "[v]", "-map", f"{na}:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "12M",
         "-bufsize", "24M", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT)])
    print(f"listo: {OUT}")


if __name__ == "__main__":
    main()
