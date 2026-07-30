# Luluca Nails — Web

Sitio web estático (HTML/CSS/JS, sin dependencias) para Luluca Nails, salones de
Fuenlabrada y Humanes. Preparado para publicarse en GitHub Pages.

## Estructura
- `index.html` · `servicios.html` · `galeria.html` · `contacto.html`
- `assets/css/styles.css` — diseño (sistema de estilos común)
- `assets/js/` — reservado
- `assets/img/` — logo, fotos y trabajos
- `build.py` — generador: reconstruye las páginas desde partes comunes + datos del
  cliente (`CLIENT`). Es la base para producir otras webs de salón en serie.
- `.nojekyll` — sirve el sitio tal cual en GitHub Pages.

## Editar y regenerar
Los datos del cliente (teléfono, WhatsApp, redes, dirección…) están en `build.py`
(diccionario `CLIENT`). Tras editarlos: `python build.py` regenera las páginas.

## Pendiente antes de producción
- Datos del salón de Humanes (dirección, teléfono, horario).
- Fotos propias de pedicura, pestañas/cejas y depilación (ahora hay stock).
- URL del calendario de Lanzo por salón (para el iframe de reservas real).
- Quitar la barra superior de "Mockup de trabajo".
