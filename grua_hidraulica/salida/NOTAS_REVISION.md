# Notas para revisar antes de publicar

## Transcripción: partes dudosas

He transcrito el audio con dos modelos de reconocimiento de voz (Whisper y Parakeet) y comparado sus
resultados. Donde no coincidían y la grabación no se entendía bien, puse **(…)** en lugar de inventar
palabras. Si sabes lo que se dijo, corrígelo en `scripts/edl.py → CUES` y vuelve a renderizar.

| Clip | Subtítulo actual | Duda |
|---|---|---|
| v1 | «mi nombre es (…) Porto» | El nombre de pila no se entiende ("Pena", "Vena"…). |
| v1 | «mi nombre es (…) / y soy diseñadora (…).» | No se entiende el nombre ni el cargo completo. En v4 se presenta como «diseñadora estructural». |
| v1, v6 | «soy (…) Contreras» | El nombre de pila no se entiende ("Jain", "Yahín"…). |
| v1 | «Deibelis Mauri» | La ortografía del nombre es aproximada (Deibelis / Daybelis / Deybelis). |
| v1, v2 | «Dylan Martínez» | Comprueba la ortografía (Dylan / Dilan). |
| v7 | «la actividad STEM «Innovación hidráulica»» | Un modelo oye "STIM" y el otro "en sí". Lo más probable es STEM. |
| v8 | «Primeramente hicimos…» | Un modelo oye "Previamente". |
| v8 | «Y por último realizamos (…) para evaluar…» | Ninguno de los dos modelos capta la palabra (¿"pruebas"?). |
| v9 | «Entendimos que planear…» | Se oye "Tendimos"/"Tenemos". "Entendimos" es la lectura con sentido. |
| v9 | «cada fase» | Un modelo oye "cada parte". |
| v2 | Se usan solo 3 fragmentos | El nombre del sitio web y el cargo no se entienden, así que se cortaron esas frases. |

Correcciones evidentes que ya he aplicado: «literales» → «laterales» (v5), «Hicimos dos cuatro columnas» →
«Hicimos cuatro columnas» (v6, autocorrección del hablante) y la puntuación.

## Créditos finales

Solo aparecen los nombres que se oyen con claridad (Dylan Martínez, Juan Chiquillo). Puedes completar
el resto en `scripts/edl.py → NOMBRES`.

## Gráficos científicos

- El esquema de Pascal usa dos jeringas **genéricas** con áreas en relación 1:4 para mostrar que
  F₂ = F₁·A₂/A₁ y que A₁·d₁ = A₂·d₂. El vídeo no dice el tamaño de las jeringas de la grúa, así que
  el texto final solo afirma lo que se ve y se dice: al mover una jeringa, el agua transmite la
  presión por la manguera y la otra jeringa mueve el brazo.
- Las medidas que aparecen en las tarjetas (11 × 22 cm, 12 cm, 22 cm y 3 cm) son exactamente las que
  se dicen en v4 y v5.
- Las etiquetas «Brazo», «Jeringa», «Manguera» y «Base» señalan piezas que se ven en la imagen. El
  triángulo negro no lleva etiqueta porque el vídeo no aclara qué es.
