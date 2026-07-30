# -*- coding: utf-8 -*-
"""Generador estático de la web de Luluca Nails.
Ensambla las páginas desde partes comunes (cabecera, pie, scripts) + datos del cliente.
Este es el germen del sistema multi-web: cambiando CLIENT y las imágenes se produce otra web."""
import re, io, sys

CLIENT = {
  "name": "Luluca Nails",
  "phone_display": "+34 690 06 27 62",
  "tel": "+34690062762",
  "whatsapp": "https://wa.me/34690062762?text=Hola%2C%20quiero%20reservar%20una%20cita%20en%20Luluca%20Nails",
  "email": "info@lulucanails.com",
  "instagram": "https://www.instagram.com/lulucanails",
  "tiktok": "https://www.tiktok.com/@lulucanails",
  "facebook": "https://www.facebook.com/lulucanails",
  "fuen_addr": "Calle Escocia 1, Fuenlabrada, Madrid",
  "fuen_maps": "https://www.google.com/maps/search/?api=1&query=Calle%20Escocia%201%20Fuenlabrada",
  "fuen_hours": "L-V 09:00–20:00 · S 09:00–14:00",
}

WA_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12a9 9 0 0 1-13.6 7.7L3 21l1.3-4.4A9 9 0 1 1 21 12z"/></svg>'
CAL_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'

def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/styles.css">
</head>
<body data-locale="fuen">
<div class="mock-note">Mockup de trabajo · <b>Luluca Nails</b> · fotos reales (mejoradas); stock solo donde falta foto propia · datos de Humanes y reservas Lanzo pendientes</div>
<div class="localebar"><div class="lw">
  <span class="lb-label">Elige tu salón:</span>
  <div class="seg">
    <button class="seg-btn on" data-k="fuen" onclick="setLocale('fuen')">Fuenlabrada</button>
    <button class="seg-btn" data-k="huma" onclick="setLocale('huma')">Humanes</button>
  </div>
</div></div>
"""

def header(active):
    def a(href, label, key):
        cls = ' class="active"' if key==active else ''
        return f'<a href="{href}"{cls}>{label}</a>'
    nav = "".join([
        a("index.html","Inicio","inicio"),
        a("servicios.html","Servicios","servicios"),
        a("galeria.html","Galería","galeria"),
        a("index.html#reservar","Reservar","reservar"),
        a("contacto.html","Contacto","contacto"),
    ])
    return f"""<header class="nav"><div class="hw">
  <a class="brand" href="index.html"><img class="logo-img" src="assets/img/logo-dark.png" alt="Luluca Nails"></a>
  <nav class="menu" id="menu">{nav}</nav>
  <div class="nav-cta">
    <a href="index.html#reservar" class="btn btn-primary">{CAL_ICON} Reservar cita</a>
    <button class="burger" aria-label="Menú" onclick="toggleMenu()"><span></span><span></span><span></span></button>
  </div>
</div></header>
"""

def footer():
    c=CLIENT
    return f"""<footer id="contacto-foot"><div class="fw">
  <div>
    <img class="foot-logo" src="assets/img/logo-light.png" alt="Luluca Nails">
    <p class="about">Centro de uñas, cejas y belleza en Fuenlabrada y Humanes. Cuidamos cada detalle para realzar tu estilo y hacerte brillar.</p>
    <div class="social">
      <a href="{c['instagram']}" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></a>
      <a href="{c['tiktok']}" target="_blank" rel="noopener" aria-label="TikTok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M15 4v9.5a3.5 3.5 0 1 1-3-3.5"/><path d="M15 6a4 4 0 0 0 4 4"/></svg></a>
      <a href="{c['facebook']}" target="_blank" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 8h2V5h-2a3 3 0 0 0-3 3v2H9v3h2v6h3v-6h2l1-3h-3V8a1 1 0 0 1 1-1z"/></svg></a>
      <a href="{c['whatsapp']}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_ICON}</a>
    </div>
  </div>
  <div><h5>Salón Fuenlabrada</h5><a href="{c['fuen_maps']}" target="_blank" rel="noopener">{c['fuen_addr']}</a><a href="tel:{c['tel']}">{c['phone_display']}</a><a href="mailto:{c['email']}">{c['email']}</a><span style="color:#a9b6a9">{c['fuen_hours']}</span></div>
  <div><h5>Salón Humanes</h5><a href="#">Dirección (pendiente)</a><a href="#">Teléfono (pendiente)</a><a href="index.html#reservar" onclick="setLocale('huma')">Reservar en Humanes</a><a href="servicios.html">Ver servicios</a></div>
</div>
<div class="legal">© 2026 Luluca Nails · Fuenlabrada y Humanes · Reservas gestionadas con Lanzo · Aviso legal · Privacidad</div>
</footer>
"""

def mobilebar():
    c=CLIENT
    return f"""<div class="mobile-book">
  <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa call" aria-label="WhatsApp">{WA_ICON}</a>
  <a href="index.html#reservar" class="btn btn-primary">Reservar cita</a>
</div>
"""

def scripts():
    return """<div class="lb" id="lb" onclick="closeLb(event)"><button class="lb-close" onclick="closeLb(event)">&times;</button><img id="lb-img" src="" alt=""></div>
<script>
var NAMES={fuen:'Fuenlabrada',huma:'Humanes'};
function setLocale(k){document.body.dataset.locale=k;document.querySelectorAll('[data-locname]').forEach(function(e){e.textContent=NAMES[k];});document.querySelectorAll('.seg-btn').forEach(function(b){b.classList.toggle('on',b.dataset.k===k);});}
function toggleMenu(){document.getElementById('menu').classList.toggle('open');}
function openCat(id){var d=document.getElementById(id);if(d){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});}}
function openLb(src){var lb=document.getElementById('lb');document.getElementById('lb-img').src=src;lb.classList.add('on');}
function closeLb(e){document.getElementById('lb').classList.remove('on');}
</script>
</body>
</html>
"""

# ---------- INDEX ----------
def build_index():
    c=CLIENT
    cats=[
      ("Manicura","Semipermanente, tradicional, sin esmaltar y kids.","assets/img/cat-manicura.jpg"),
      ("Pedicura","Deluxe Spa, semipermanente y tradicional.","https://images.unsplash.com/photo-1519415510236-718bdfcd89c8?w=600&h=420&q=80&auto=format&fit=crop"),
      ("Uñas esculpidas","Gel y acrílico: uñas nuevas y rellenos.","assets/img/cat-esculpidas.jpg"),
      ("Nail art y diseños","Francesa, ojo de gato, baby boomer y decoraciones.","assets/img/cat-nailart.jpg"),
      ("Pestañas y cejas","Lifting de pestañas, tinte y laminado de cejas.","https://images.unsplash.com/photo-1589710751893-f9a6770ad71b?w=600&h=420&q=80&auto=format&fit=crop"),
      ("Depilación con hilo","Cejas, labio, mentón, patillas y cara completa.","https://images.unsplash.com/photo-1618322802324-a9185814211d?w=600&h=420&q=80&auto=format&fit=crop"),
      ("Gemas dentales","Un toque de brillo a tu sonrisa. También Swarovski.","assets/img/cat-gemas.jpg"),
    ]
    cat_html=""
    for i,(t,d,img) in enumerate(cats):
        more = "Pregunta por celebraciones →" if False else "Ver servicios →"
        cat_html+=f'<a class="cat" href="servicios.html"><div class="thumb thumb-fallback"><img src="{img}" alt="{t}" loading="lazy" onerror="this.style.display=\'none\'"></div><div class="c-body"><h3>{t}</h3><p>{d}</p><span class="more">{more}</span></div></a>\n'
    cat_html+='<a class="cat" href="#party"><div class="thumb thumb-fallback" style="display:flex;align-items:center;justify-content:center;background:var(--forest)"><span style="font-family:\'Cormorant Garamond\',serif;color:var(--gold-2);font-size:30px">Beauty Party</span></div><div class="c-body"><h3>Beauty Party</h3><p>Cumpleaños y celebraciones de belleza para grupos.</p><span class="more">Pregunta por celebraciones →</span></div></a>\n'

    gal="".join([f'<div class="gal" onclick="openLb(\'assets/img/work/work-{i}.jpg\')"><img src="assets/img/work/work-{i}.jpg" alt="Trabajo de Luluca Nails" loading="lazy"></div>' for i in range(1,9)])

    days=""
    off={28,29,30,31,2,3,10,17,24,31}
    # simple month grid Aug 2026 starting positions like before
    grid=[('off','28'),('off','29'),('off','30'),('off','31'),('free','1'),('off','2'),('off','3'),
          ('free','4'),('free','5'),('free','6'),('free','7'),('free','8'),('free','9'),('off','10'),
          ('free','11'),('sel','12'),('free','13'),('free','14'),('free','15'),('free','16'),('off','17'),
          ('free','18'),('free','19'),('free','20'),('free','21'),('free','22'),('free','23'),('off','24'),
          ('free','25'),('free','26'),('free','27'),('free','28'),('free','29'),('free','30'),('off','31')]
    days="".join([f'<div class="day {k}">{v}</div>' for k,v in grid])

    body=f"""{header('inicio')}
<section class="hero"><div class="wrap">
  <div class="hero-copy">
    <span class="eyebrow">Salón de uñas, cejas y belleza · <span data-locname>Fuenlabrada</span></span>
    <h1>Uñas <em>sanas</em>,<br>cuidadas al detalle.</h1>
    <p class="lead">Manicura, nail art, cejas y pestañas con técnicas profesionales y un trato cercano. Tu momento de belleza, reservado en un minuto.</p>
    <div class="hero-actions">
      <a href="#reservar" class="btn btn-gold">{CAL_ICON} Reservar cita</a>
      <a href="servicios.html" class="btn btn-ghost">Ver servicios</a>
    </div>
    <div class="hero-trust"><span class="stars">★★★★★</span><span><b style="color:var(--forest)">Excelente</b> · 103 reseñas en Google</span></div>
  </div>
  <div class="hero-photo thumb-fallback"><img src="assets/img/hero.jpg" alt="Trabajo de Luluca Nails"><div class="badge"><div class="n">+8</div><small>años cuidando las uñas<br>de <span data-locname>Fuenlabrada</span></small></div></div>
</div></section>

<section class="cats sec-pad" id="servicios"><div class="wrap">
  <div class="head"><span class="eyebrow">Nuestros servicios</span><h2>Todo para tus manos, tu mirada y tu piel</h2><p>Siete familias de servicios. Toca la que te interese para ver todos los detalles y precios.</p></div>
  <div class="cat-grid">{cat_html}</div>
</div></section>

<section class="gallery sec-pad" id="galeria"><div class="wrap">
  <div class="head"><div><span class="eyebrow">Nuestro trabajo</span><h2>Nail art hecho a tu medida</h2><p>Diseños reales de Luluca. Aquí es donde ponemos el color.</p></div><a href="galeria.html" class="btn btn-ghost">Ver galería completa</a></div>
  <div class="gal-grid">{gal}</div>
</div></section>

<section class="pillars sec-pad" id="nosotros"><div class="wrap">
  <div class="head"><span class="eyebrow">Por qué Luluca</span><h2>Belleza, sí. Pero primero, salud.</h2><p>Cada clienta disfruta de un momento para sí misma y sale con unas uñas cuidadas, elegantes y sanas.</p></div>
  <div class="pil-grid">
    <div class="pil"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.5-7 10-7 10z"/></svg></div><h3>Uñas sanas</h3><p>Priorizamos la salud de tu uña natural en cada técnica y cada retirada.</p></div>
    <div class="pil"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l2.2 4.5L19 8l-3.5 3.4L16.3 16 12 13.7 7.7 16l.8-4.6L5 8l4.8-.5z"/></svg></div><h3>Productos de calidad</h3><p>Marcas profesionales para un acabado que dura y se mantiene bonito.</p></div>
    <div class="pil"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="8" r="3.2"/><path d="M21 21v-2a4 4 0 0 0-3-3.8"/></svg></div><h3>Trato cercano</h3><p>Un espacio pensado para ti, con asesoramiento personalizado.</p></div>
  </div>
</div></section>

<section class="booking sec-pad" id="reservar"><div class="wrap">
  <div class="booking-copy">
    <span class="eyebrow">Reserva online</span>
    <h2>Elige día y hora en un minuto</h2>
    <p>Sin llamadas ni esperas. Consulta la disponibilidad real del salón de <b data-locname style="color:var(--forest)">Fuenlabrada</b> y reserva desde aquí mismo.</p>
    <ul>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Disponibilidad en tiempo real</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Recordatorio automático de tu cita</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Cambios y cancelaciones fáciles</li>
    </ul>
    <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} ¿Prefieres WhatsApp? Escríbenos</a>
  </div>
  <div class="cal">
    <span class="cal-badge">Reservas · Lanzo</span>
    <h4>Salón de <span data-locname>Fuenlabrada</span></h4>
    <div class="cal-title">Agosto 2026</div>
    <div class="dow"><span>L</span><span>M</span><span>X</span><span>J</span><span>V</span><span>S</span><span>D</span></div>
    <div class="days">{days}</div>
    <div class="slots"><div class="slabel">Martes 12 de agosto · elige tu hora</div><div class="slot-row"><span class="slot dim">10:00</span><span class="slot">10:30</span><span class="slot on">11:30</span><span class="slot">12:30</span><span class="slot">17:00</span><span class="slot">18:00</span><span class="slot">19:00</span></div></div>
    <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-primary">Confirmar reserva · 11:30</a>
    <div class="cal-note">Calendario de muestra. La reserva real se activará con la agenda de Lanzo (una cuenta por salón).</div>
  </div>
</div></section>

<section class="party sec-pad" id="party">
  <div class="bg thumb-fallback"><img src="https://images.unsplash.com/photo-1638417568431-d518a9b7c11e?w=1400&h=650&q=80&auto=format&fit=crop" alt="" onerror="this.style.display='none'"></div>
  <div class="ov"></div>
  <div class="wrap"><div class="txt"><span class="eyebrow">Celebraciones</span><h2>Beauty Party: celebra diferente</h2><p>Cumpleaños y fiestas de belleza para grupos, con uñas, cejas y pestañas en un ambiente exclusivo. Cuéntanos tu idea y la preparamos.</p></div><a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-gold">Pregunta por celebraciones</a></div>
</section>

<section class="reviews sec-pad"><div class="wrap">
  <div class="head"><span class="eyebrow">Opiniones</span><h2>Lo que dicen nuestras clientas</h2><span class="rev-score"><span class="stars">★★★★★</span> Excelente · 103 reseñas en Google</span></div>
  <div class="rev-grid">
    <div class="rev"><div class="top"><div class="av">E</div><div><div class="who">Estíbaliz T.</div><div class="stars">★★★★★</div></div></div><p>Trato excepcional y un resultado precioso. Se nota que cuidan cada detalle. Recomendado 100%.</p></div>
    <div class="rev"><div class="top"><div class="av">S</div><div><div class="who">Sara V.</div><div class="stars">★★★★★</div></div></div><p>Llevo yendo desde diciembre y no puedo estar más contenta. Son encantadoras y muy profesionales.</p></div>
    <div class="rev"><div class="top"><div class="av">A</div><div><div class="who">Almudena Z.</div><div class="stars">★★★★★</div></div></div><p>Las uñas me duran perfectas y el ambiente es súper agradable. Mi salón de confianza.</p></div>
  </div>
</div></section>

<section class="locs sec-pad" id="locales"><div class="wrap">
  <div class="head"><span class="eyebrow">Dónde estamos</span><h2>Dos salones para cuidarte</h2></div>
  <p class="subnote">Elige arriba tu salón para reservar en su agenda. Los dos forman parte de Luluca Nails.</p>
  <div class="loc-grid">
    <div class="loc"><div class="map"><iframe loading="lazy" src="https://www.google.com/maps?q=Calle%20Escocia%201,%20Fuenlabrada&output=embed"></iframe></div><div class="body"><span class="tag-here">Salón principal</span><h3>Fuenlabrada</h3><div class="info"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['fuen_addr']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['phone_display']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['fuen_hours']}</div></div><div class="actions"><a href="#reservar" class="btn btn-primary" onclick="setLocale('fuen')">Reservar aquí</a><a href="{c['fuen_maps']}" target="_blank" rel="noopener" class="btn btn-ghost">Cómo llegar</a></div></div></div>
    <div class="loc"><div class="map"><div class="pin"><svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.6"/></svg></div></div><div class="body"><span class="tag-here" style="color:var(--sage)">Nuevo salón</span><h3>Humanes</h3><div class="info"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> Dirección (pendiente)</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> Teléfono (pendiente)</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> Horario (pendiente)</div></div><div class="actions"><a href="#reservar" class="btn btn-primary" onclick="setLocale('huma')">Reservar aquí</a></div></div></div>
  </div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Luluca Nails — Salón de uñas, cejas y belleza en Fuenlabrada y Humanes",
                "Manicura, pedicura, uñas esculpidas, nail art, pestañas, cejas y depilación con hilo. Reserva tu cita online. Fuenlabrada y Humanes.") + body

# ---------- SERVICIOS ----------
def build_servicios():
    src=open("/home/claude/luluca_servicios.html",encoding="utf-8").read()
    i0=src.index('<div class="catalog">')
    i1=src.index('<section class="reserva-band"')
    catalog=src[i0:i1].strip()
    catalog=catalog.replace('class="cat"','class="cat2"')
    c=CLIENT
    body=f"""{header('servicios')}
<section class="page-hero"><span class="eyebrow">Carta de servicios</span><h1>Nuestros servicios y precios</h1><p>Todo lo que hacemos, ordenado por categorías para que encuentres el tuyo en segundos. Toca una categoría para desplegarla.</p></section>
<div class="chips"><div class="cw">
  <span class="chip" onclick="openCat('manicura')">Manicura</span>
  <span class="chip" onclick="openCat('pedicura')">Pedicura</span>
  <span class="chip" onclick="openCat('esculpidas')">Uñas esculpidas</span>
  <span class="chip" onclick="openCat('nailart')">Nail art</span>
  <span class="chip" onclick="openCat('mirada')">Pestañas y cejas</span>
  <span class="chip" onclick="openCat('depilacion')">Depilación con hilo</span>
  <span class="chip" onclick="openCat('gemas')">Gemas dentales</span>
</div></div>
{catalog}
<section class="reserva-band" id="reserva"><span class="eyebrow" style="color:var(--gold-2)">Reserva online</span><h2>¿Lo tienes claro? Reserva en un minuto</h2><p>Elige día y hora en la agenda del salón de <span data-locname>Fuenlabrada</span>. Sin llamadas ni esperas.</p><a href="index.html#reservar" class="btn btn-gold">Ir a reservar</a></section>
<div class="disc">Precios y servicios orientativos según la lista del salón. Las duraciones son aproximadas y pueden variar según el estado de la uña. Consulta cualquier duda antes de tu cita.</div>
{footer()}{mobilebar()}{scripts()}"""
    return head("Servicios y precios — Luluca Nails","Carta completa de servicios y precios de Luluca Nails: manicura, pedicura, uñas esculpidas, nail art, pestañas, cejas, depilación y gemas dentales.")+body

# ---------- GALERÍA ----------
def build_galeria():
    imgs=[f"assets/img/work/work-{i}.jpg" for i in range(1,9)]+["assets/img/cat-manicura.jpg","assets/img/cat-esculpidas.jpg","assets/img/cat-nailart.jpg","assets/img/hero.jpg"]
    tiles="".join([f'<div class="gal" onclick="openLb(\'{s}\')"><img src="{s}" alt="Trabajo de Luluca Nails" loading="lazy"></div>' for s in imgs])
    body=f"""{header('galeria')}
<section class="page-hero"><span class="eyebrow">Nuestro trabajo</span><h1>Galería</h1><p>Diseños reales hechos en Luluca. Toca una foto para verla más grande.</p></section>
<section class="gallery sec-pad" style="background:var(--cream)"><div class="wrap"><div class="gal-grid">{tiles}</div>
<p class="center" style="margin-top:34px"><a href="index.html#reservar" class="btn btn-primary">Reserva tu cita</a></p></div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Galería — Luluca Nails","Galería de trabajos reales de Luluca Nails: nail art, manicura, diseños y más.")+body

# ---------- CONTACTO ----------
def build_contacto():
    c=CLIENT
    body=f"""{header('contacto')}
<section class="page-hero"><span class="eyebrow">Contacto</span><h1>Hablamos cuando quieras</h1><p>Escríbenos por WhatsApp o email, o pásate por el salón. Estaremos encantadas de atenderte.</p></section>
<section class="sec-pad" style="padding-top:30px"><div class="wrap">
  <div class="contact-grid">
    <div class="contact-card">
      <h3><span data-locname>Fuenlabrada</span></h3>
      <div class="cc-sub">Salón principal</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['fuen_addr']}</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['phone_display']}</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg> {c['email']}</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['fuen_hours']}</div>
      <div class="contact-actions">
        <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} WhatsApp</a>
        <a href="tel:{c['tel']}" class="btn btn-ghost">Llamar</a>
        <a href="mailto:{c['email']}" class="btn btn-ghost">Email</a>
      </div>
    </div>
    <div class="map-embed"><iframe loading="lazy" src="https://www.google.com/maps?q=Calle%20Escocia%201,%20Fuenlabrada&output=embed"></iframe></div>
  </div>
  <div class="contact-card" style="margin-top:22px">
    <h3>Humanes</h3><div class="cc-sub">Nuevo salón · datos pendientes</div>
    <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> Dirección de Humanes (pendiente)</div>
    <div class="contact-actions"><a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} WhatsApp</a></div>
  </div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Contacto — Luluca Nails","Contacta con Luluca Nails por WhatsApp, teléfono o email. Fuenlabrada y Humanes.")+body

def w(path,html):
    open("/home/claude/site/"+path,"w",encoding="utf-8").write(html)
    print("wrote",path,len(html)//1024,"KB")

w("index.html",build_index())
w("servicios.html",build_servicios())
w("galeria.html",build_galeria())
w("contacto.html",build_contacto())
print("OK")
