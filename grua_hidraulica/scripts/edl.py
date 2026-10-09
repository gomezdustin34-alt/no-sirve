"""Lista de edición (EDL): estructura narrativa, cortes, subtítulos y gráficos.

Todos los tiempos de clip (tin/tout y subtítulos) están en segundos del archivo
ORIGINAL (fuentes/vN.mp4), obtenidos de la transcripción con marcas por palabra.

Para corregir un nombre o una frase basta con editar CUES y volver a renderizar.
Los fragmentos marcados con (…) son palabras que no se entienden con claridad
en la grabación: se dejan así en lugar de inventarlas.
"""

# ───────────────────────── Nombres (editables) ─────────────────────────
# Solo se rotulan los nombres que se oyen con claridad. Rellena los demás si quieres
# que aparezcan en los créditos finales (se dejan vacíos para no inventar).
NOMBRES = {
    "Líder de la investigación": "Dylan Martínez",
    "Coordinadora de planeación": "",
    "Diseñadora estructural": "",
    "Encargado de la construcción": "",
    "Analista de calidad y evaluación": "Juan Chiquillo",
    "Relatora y gestora del informe": "",
}

# Palabras resaltadas en los subtítulos (conceptos científicos / componentes).
KEYWORDS = ["hidráulica", "Pascal", "jeringas", "mangueras", "agua", "líquido", "presión",
            "fuerza", "centímetros", "reciclables", "cronograma", "boceto"]

# ───────────────────────── Subtítulos (tiempo del clip original) ─────────────────────────
CUES = {
    "v1": [
        (0.00, 1.50, "Buenas tardes, mi nombre es Dylan Martínez"),
        (1.50, 3.60, "y soy el líder de la investigación."),
        (3.76, 5.80, "Buenas tardes, mi nombre es (…) Porto"),
        (5.80, 8.05, "y soy la coordinadora de planeación."),
        (8.24, 10.60, "Buenas tardes, mi nombre es (…)"),
        (10.60, 12.30, "y soy diseñadora (…)."),
        (12.56, 14.45, "Buenas tardes, soy (…) Contreras"),
        (14.45, 16.20, "y soy el encargado de la construcción."),
        (16.32, 18.10, "Buenas tardes, soy Juan Chiquillo"),
        (18.10, 20.80, "y soy analista de calidad y evaluación."),
        (20.96, 23.30, "Buenas tardes, mi nombre es Deibelis Mauri"),
        (23.30, 26.30, "y soy la relatora y gestora del informe."),
    ],
    "v3": [
        (0.30, 2.60, "Yo soy la coordinadora de planeación"),
        (2.60, 5.10, "y a continuación mis compañeros me van a dar"),
        (5.10, 8.20, "una breve información sobre la grúa hidráulica."),
    ],
    "v7": [
        (0.16, 1.55, "Bueno, como pueden ver,"),
        (1.55, 4.55, "soy la relatora y gestora del informe."),
        (4.72, 7.40, "Como pueden ver, nuestro equipo desarrolló"),
        (7.40, 11.30, "la actividad STEM «Innovación hidráulica»,"),
        (11.52, 15.30, "cuyo reto era construir una grúa"),
        (15.30, 17.30, "utilizando materiales reciclables"),
        (17.30, 19.70, "para poder mover cargas pequeñas"),
        (19.70, 22.60, "de manera económica y sostenible."),
    ],
    "v8": [
        (0.16, 2.75, "Primeramente hicimos la investigación"),
        (2.75, 5.55, "de la función hidráulica y el principio de Pascal."),
        (5.68, 7.45, "Luego planeamos el trabajo"),
        (7.45, 10.80, "con un cronograma, boceto y la lista de materiales."),
        (11.20, 14.00, "Después construimos las estructuras"),
        (14.00, 16.20, "con cartón y palillos,"),
        (16.24, 18.40, "e instalamos el sistema"),
        (18.40, 20.40, "con agua, jeringas y mangueras."),
        (20.48, 22.60, "Y por último realizamos (…)"),
        (22.60, 25.00, "para evaluar su funcionamiento."),
    ],
    "v2": [
        (0.32, 2.45, "Buenas tardes, mi nombre es Dylan Martínez."),
        (5.44, 8.20, "Pues yo lo investigué en la página web"),
        (10.30, 13.05, "que te habla sobre todo cómo armar una grúa."),
    ],
    "v4": [
        (5.05, 8.70, "Yo soy la diseñadora estructural."),
        (8.96, 11.30, "Aquí les voy a mostrar el diseño."),
        (12.48, 14.90, "Esta es la parte de la base."),
        (16.08, 19.00, "La hice con las medidas que serían"),
        (19.00, 23.70, "11 centímetros y 22 centímetros."),
        (31.44, 33.70, "Estas serían las partes laterales."),
        (36.08, 39.40, "Cada una midió 12 centímetros."),
    ],
    "v5": [
        (0.64, 3.40, "Bueno, esta parte de acá sería"),
        (3.40, 6.30, "lo que sostiene la grúa,"),
        (6.40, 8.70, "que son 22 centímetros."),
        (9.28, 12.00, "Esto es lo que sostienen"),
        (12.00, 14.60, "las partes laterales de la grúa,"),
        (14.72, 16.70, "que serían 3 centímetros."),
    ],
    "v6": [
        (0.15, 1.45, "Buenas tardes, soy (…) Contreras,"),
        (1.45, 2.90, "soy el encargado de la construcción."),
        (2.96, 5.95, "Bueno, primero que todo, utilizamos una base de cartón."),
        (6.72, 10.65, "Hicimos cuatro columnas de cartón a la medida,"),
        (10.72, 12.50, "las pegamos con silicona,"),
        (12.64, 15.55, "usamos una basecita también de cartón"),
        (15.60, 18.00, "para pegar esta basecita que ven aquí."),
        (18.56, 20.35, "Utilizamos lana negra,"),
        (20.40, 24.20, "utilizamos dos mangueras"),
        (24.24, 26.65, "y dos jeringas y un líquido."),
        (26.88, 28.30, "A continuación vamos a probar"),
        (28.30, 31.60, "el funcionamiento de nuestra grúa"),
        (31.68, 34.20, "y vamos a analizar si funciona correctamente."),
        (37.92, 40.10, "Como pueden ver, nuestra grúa"),
        (40.16, 42.00, "funcionó correctamente,"),
        (42.00, 43.15, "tal como estaba planeado."),
        (43.20, 44.20, "Muchas gracias."),
    ],
    "v9": [
        (0.16, 2.65, "Entendimos que planear, trabajar como equipo"),
        (2.65, 5.10, "y documentar cada fase nos ayuda a mejorar."),
        (5.28, 5.95, "Muchas gracias."),
    ],
}

# Posición aproximada de la grúa en los clips en que se sostiene en la mano
# (coordenadas del clip vertical 576×1024), para los acercamientos.
CRANE_V7 = (268, 600)
CRANE_V8 = (205, 560)

# Desplazamientos respecto al lazo de manguera rosa rastreado en v6 (escala ≈ 90 px).
V6_PARTS = {
    "manguera": (-34, 6),
    "jeringa": (44, -20),
    "columna": (10, -55),
    "brazo": (62, -122),
    "base": (98, 2),
    "centro": (55, -60),
    "grua": (62, -100),
}

CH = {
    1: "PRESENTACIÓN",
    2: "INVESTIGACIÓN Y MÉTODO",
    3: "DISEÑO Y MATERIALES",
    4: "¿CÓMO FUNCIONA?",
    5: "DEMOSTRACIÓN",
    6: "CONCLUSIÓN",
}

# ───────────────────────── Secuencia ─────────────────────────
# layout: "portrait" (clip vertical + panel), "full" (clip horizontal a pantalla completa),
#         "crop" (recorte cinematográfico de un clip vertical), "graphic" (animación pura)
# zoom:   lista de (t_local, z, cx, cy); cx/cy en px del clip, o "track:<parte>" para v6.
SEGMENTS = [
    # ── GANCHO (≈7 s, sobre rejilla de 120 BPM: cortes en 1,0 / 4,0 / 7,0 s) ──
    dict(id="hook_a", src="v6", tin=36.45, tout=37.45, layout="crop", crop_w=600, audio=False,
         zoom=[(0, 1.0, "track:grua"), (1.0, 1.2, "track:grua")], fx=["hook_brackets"]),
    dict(id="hook_b", src="v6", tin=37.45, tout=38.65, speed=0.4, layout="crop", crop_w=600, audio=False,
         zoom=[(0, 1.2, "track:grua"), (3.0, 1.27, "track:grua")], fx=["hook_brackets", "lift_arc", "slowmo_tag"]),
    dict(id="hook_c", src="v6", tin=32.75, tout=34.15, speed=0.6, hold=0.67, layout="crop", crop_w=360,
         audio=False, trans="flash",
         zoom=[(0, 1.0, "track:jeringa"), (3.0, 1.12, "track:jeringa")], fx=["question"]),

    # ── TÍTULO ──
    dict(id="title", src="v6", tin=39.2, tout=43.7, layout="crop", crop_w=520, audio=False, trans="flash",
         zoom=[(0, 1.0, "track:centro"), (4.5, 1.1, "track:centro")], fx=["title_card"]),

    # ── 01 PRESENTACIÓN ──
    dict(id="equipo", src="v1", tin=0.0, tout=26.40, layout="full", chapter=1, trans="whip",
         zoom=[(0, 1.0, 512, 300), (26.4, 1.07, 512, 290)],
         tags=[(0.2, 26.0, "EQUIPO DE TRABAJO", "6 integrantes · 6 roles")]),
    dict(id="coord", src="v3", tin=0.30, tout=8.40, layout="portrait", chapter=1,
         lower=("Coordinadora de planeación", 0.3, 8.0),
         zoom=[(0, 1.0, 288, 512), (8.1, 1.06, 288, 470)],
         panel=[("text", 2.6, "A CONTINUACIÓN", "Una breve información sobre la grúa hidráulica.")]),
    dict(id="reto", src="v7", tin=0.10, tout=22.70, layout="portrait", chapter=1,
         lower=("Relatora y gestora del informe", 1.4, 6.0),
         zoom=[(0, 1.0, 288, 512), (13.6, 1.03, 288, 512), (14.4, 1.55, *CRANE_V7), (17.2, 1.6, *CRANE_V7),
               (18.0, 1.0, 288, 512), (22.6, 1.04, 288, 500)],
         panel=[("kv", 4.70, "ACTIVIDAD", "Innovación hidráulica"),
                ("kv", 11.6, "RETO", "Construir una grúa con materiales reciclables"),
                ("kv", 17.7, "PARA", "Mover cargas pequeñas"),
                ("kv", 20.5, "DE MANERA", "Económica · Sostenible")]),

    # ── 02 INVESTIGACIÓN Y MÉTODO ──
    dict(id="metodo", src="v8", tin=0.05, tout=25.10, layout="portrait", chapter=2, trans="whip",
         lower=("Relatora y gestora del informe", 0.4, 4.0),
         zoom=[(0, 1.0, 288, 512), (17.8, 1.02, 288, 512), (18.5, 1.6, *CRANE_V8), (20.6, 1.62, *CRANE_V8),
               (21.4, 1.0, 288, 512), (25.0, 1.04, 288, 500)],
         panel=[("step", 1.0, "01", "Investigación", "Función hidráulica · Principio de Pascal"),
                ("step", 5.6, "02", "Planeación", "Cronograma · Boceto · Lista de materiales"),
                ("step", 11.1, "03", "Construcción", "Cartón y palillos · Agua, jeringas y mangueras"),
                ("step", 20.5, "04", "Evaluación", "Evaluar su funcionamiento")]),
    dict(id="invest_a", src="v2", tin=0.30, tout=2.50, layout="portrait", chapter=2,
         lower=("Dylan Martínez · Líder de la investigación", 0.2, 7.5),
         zoom=[(0, 1.0, 288, 470), (2.2, 1.03, 288, 470)],
         panel=[("text", 0.3, "FUENTE", "Investigación en una página web sobre cómo armar una grúa.")]),
    dict(id="invest_b", src="v2", tin=5.40, tout=8.25, layout="portrait", chapter=2,
         zoom=[(0, 1.14, 288, 430), (2.85, 1.17, 288, 430)], panel_static=True),
    dict(id="invest_c", src="v2", tin=10.25, tout=13.08, layout="portrait", chapter=2,
         zoom=[(0, 1.0, 288, 470), (2.83, 1.03, 288, 470)], panel_static=True),

    # ── 03 DISEÑO Y MATERIALES ──
    dict(id="dis_a", src="v4", tin=4.85, tout=11.55, layout="full", chapter=3, trans="whip",
         lower=("Diseñadora estructural", 0.3, 6.4),
         zoom=[(0, 1.0, 512, 288), (6.7, 1.06, 512, 288)]),
    dict(id="dis_b", src="v4", tin=12.30, tout=15.10, layout="full", chapter=3,
         zoom=[(0, 1.08, 512, 300), (2.8, 1.11, 512, 300)]),
    dict(id="dis_c", src="v4", tin=15.85, tout=23.75, layout="full", chapter=3,
         zoom=[(0, 1.0, 512, 288), (7.9, 1.06, 512, 288)],
         cards=[(22.2 - 15.85, "BASE", "11 cm × 22 cm")]),
    dict(id="dis_d", src="v4", tin=31.25, tout=33.80, layout="full", chapter=3,
         zoom=[(0, 1.06, 512, 288), (2.55, 1.09, 512, 288)], cards_keep=True),
    dict(id="dis_e", src="v4", tin=35.90, tout=39.45, layout="full", chapter=3,
         zoom=[(0, 1.0, 512, 288), (3.55, 1.04, 512, 288)], cards_keep=True,
         cards=[(38.2 - 35.90, "LATERALES", "12 cm cada una")]),
    dict(id="dis_f", src="v5", tin=0.45, tout=16.75, layout="full", chapter=3, trans="flash",
         zoom=[(0, 1.0, 512, 288), (16.3, 1.07, 540, 288)], cards_keep=True,
         cards=[(7.1 - 0.45, "SOPORTE DE LA GRÚA", "22 cm"),
                (15.6 - 0.45, "SOPORTE DE LOS LATERALES", "3 cm")]),
    dict(id="materiales", src="v6", tin=0.10, tout=26.70, layout="portrait", chapter=3,
         lower=("Encargado de la construcción", 0.2, 5.0),
         zoom=[(0, 1.0, 288, 512), (26.6, 1.04, 288, 540)],
         checklist=[(4.96, "Base de cartón"), (8.24, "4 columnas de cartón"), (11.6, "Silicona"),
                    (14.08, "Basecita de cartón"), (19.28, "Lana negra"), (22.8, "2 mangueras"),
                    (24.96, "2 jeringas"), (26.08, "Líquido")],
         inset=dict(t0=15.6, t1=99, z=2.1, part="centro"),
         labels=[(16.3, "Base", "base"), (22.8, "Manguera", "manguera"), (24.96, "Jeringa", "jeringa")]),

    # ── 04 ¿CÓMO FUNCIONA? ──
    dict(id="pascal", layout="graphic", gen="pascal", dur=21.0, chapter=4, trans="whip"),

    # ── 05 DEMOSTRACIÓN ──
    dict(id="demo_a", src="v6", tin=26.80, tout=35.40, layout="portrait", chapter=5, trans="whip",
         zoom=[(0, 1.0, 288, 512), (8.6, 1.05, 288, 560)],
         inset=dict(t0=0.6, t1=99, z=2.1, part="centro"),
         labels=[(1.0, "Brazo", "brazo"), (1.6, "Jeringa", "jeringa"), (2.2, "Manguera", "manguera")],
         panel=[("text", 0.4, "PRUEBA DE FUNCIONAMIENTO", "Se acciona la jeringa y el brazo responde.")]),
    dict(id="demo_b", src="v6", tin=37.05, tout=44.25, layout="portrait", chapter=5, trans="flash",
         zoom=[(0, 1.05, 288, 560), (7.2, 1.08, 288, 560)],
         inset=dict(t0=0.0, t1=99, z=2.1, part="centro"), inset_arc=(0.30, 1.6),
         labels=[(0.0, "Brazo", "brazo")],
         panel=[("result", 3.1, "RESULTADO", "La grúa funcionó correctamente")], panel_keep_prev=True),
    dict(id="replay", src="v6", tin=37.30, tout=38.70, speed=0.35, layout="crop", crop_w=440, audio=False,
         chapter=5, trans="flash", zoom=[(0, 1.05, "track:grua"), (4.0, 1.14, "track:grua")],
         fx=["replay_tag", "lift_arc_replay", "hook_brackets"]),

    # ── 06 CONCLUSIÓN ──
    dict(id="conclusion", src="v9", tin=0.0, tout=6.05, layout="portrait", chapter=6, trans="whip",
         lower=("Relatora y gestora del informe", 0.2, 5.8),
         zoom=[(0, 1.0, 288, 512), (6.0, 1.06, 288, 480)],
         panel=[("quote", 0.3, "APRENDIZAJE", "Planear, trabajar en equipo y documentar cada fase ayuda a mejorar.")]),
    dict(id="final", src="v6", tin=39.0, tout=44.2, speed=0.5, layout="crop", crop_w=560, audio=False,
         trans="dip", zoom=[(0, 1.0, "track:centro"), (10.4, 1.14, "track:centro")], fx=["end_card"],
         crop_shift=380),
]
