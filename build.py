# -*- coding: utf-8 -*-
"""Generador estático de la web de Luluca Nails.
Ensambla las páginas desde partes comunes (cabecera, pie, scripts) + datos del cliente.
Este es el germen del sistema multi-web: cambiando CLIENT y las imágenes se produce otra web."""
import re, io, sys, json

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

BOOKING_URL = "https://app.lanzo.es/luluca-nails-fuenlabrada"

WA_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 12a9 9 0 0 1-13.6 7.7L3 21l1.3-4.4A9 9 0 1 1 21 12z"/></svg>'
CAL_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
G_SVG = '<svg viewBox="0 0 48 48" width="16" height="16"><path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/><path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/><path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/><path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2 15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg>'

# ------- Reseñas de Google (semilla verbatim + agregado real, 30-jul-2026) -------
# Fuente única. La herramienta de auto-actualización (GitHub Action + Places API)
# reescribe reviews.json con estos mismos campos; la web se renderiza desde ahí.
REVIEWS_RATING = 4.7
REVIEWS_COUNT = 127
REVIEWS_SEED = [
  {"name":"Adriana Sevillano","date":"Hace 3 meses","rating":5,"photo":None,
   "text":"Sitio super recomendable para hacerte las uñas. Trabajan excepcional todas, Laura, Andrea y Jenny, con un trato muy humano y cercano a cada clienta. Te hacen sentir super a gusto desde que entras hasta que te vas."},
  {"name":"Almudena zapatero","date":"Hace 5 meses","rating":5,"photo":None,
   "text":"Empecé a ir a principios de diciembre y no puedo estar más contenta. Ellas son encantadoras y además hacen un trabajo buenísimo. Gracias a ellas me veo las manos mucho más bonitas. Las recomiendo al 100%."},
  {"name":"Maria RV","date":"Hace 3 meses","rating":5,"photo":None,
   "text":"¡Excelente! Llevo casi 1 año haciéndome la manicura y cada día mejor. Antes no me aguantaban ni dos días y desde que me lo hago aquí… ¡más de 15 días! Me encantan ellas, son maravillosas."},
  {"name":"Marjorie Pachacama","date":"Hace 3 meses","rating":5,"photo":None,
   "text":"Un sitio muy bonito, Andrea una chica muy encantadora y todas las chicas muy majas. Muy recomendable. Un trato muy educado, respetuoso y amigable."},
  {"name":"Estibaliz Tirado Muriel","date":"Hace 4 meses","rating":5,"photo":None,
   "text":"Estoy encantada con el sitio y sobre todo con las chicas. El primer día que fui fue porque recibí una mala noticia y necesitaba despejarme un poco. Llevo poco tiempo yendo pero les he cogido un cariño enorme, son especiales todas ellas. Y con las uñas hacen un trabajo espectacular. Las recomiendo 100%."},
  {"name":"Ana Rivera","date":"Hace 6 meses","rating":5,"photo":None,
   "text":"El trato de las chicas es genial y siempre dejan unas uñas preciosas. ¡Recomendable!"},
  {"name":"noelia vacas","date":"Hace 11 meses","rating":5,"photo":None,
   "text":"Andrea y su equipo son maravillosas y muy buenas profesionales. Utilizan materiales de calidad, se nota en la resistencia de los esmaltes y en la uña. Se adaptan y realizan cualquier diseño de uñas que les pidas."},
]

def _esc(s):
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def build_review_cards(reviews=REVIEWS_SEED):
    cards = ""
    for v in reviews:
        name = _esc(v.get("name",""))
        ini = _esc((v.get("name","?").strip()[:1] or "?").upper())
        stars = "★" * max(1, min(5, round(v.get("rating",5))))
        photo = v.get("photo")
        if photo:
            av = f'<div class="av" style="background-image:url(&quot;{_esc(photo)}&quot;);background-size:cover;color:transparent">{ini}</div>'
        else:
            av = f'<div class="av">{ini}</div>'
        cards += (
          '<div class="rev"><div class="top" style="display:flex;align-items:center;gap:12px">'
          + av
          + f'<div><div class="who">{name}</div><div class="stars">{stars}</div></div>'
          + f'<span style="margin-left:auto;width:16px;height:16px;display:inline-flex;flex:0 0 auto">{G_SVG}</span></div>'
          + f'<p>"{_esc(v.get("text",""))}"</p>'
          + f'<div style="color:var(--muted);font-size:12.5px;margin-top:12px">{_esc(v.get("date",""))} · Google</div></div>\n'
        )
    return cards

def write_reviews_json(path="reviews.json"):
    data = {"rating": REVIEWS_RATING, "count": REVIEWS_COUNT,
            "updated": "2026-07-30", "source": "seed",
            "reviews": REVIEWS_SEED}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
<div style="background:var(--forest);color:#fff;text-align:center;font-size:13.5px;padding:9px 16px;line-height:1.35">Hemos estrenado página web — es el mismo salón de siempre: <b style="color:var(--gold-2)">Luluca Nails · Fuenlabrada</b>. ¡Gracias por seguir confiando en nosotras!</div>
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
    <a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-primary">{CAL_ICON} Reservar cita</a>
    <button class="burger" aria-label="Menú" onclick="toggleMenu()"><span></span><span></span><span></span></button>
  </div>
</div></header>
"""

def footer():
    c=CLIENT
    return f"""<footer id="contacto-foot"><div class="fw">
  <div>
    <img class="foot-logo" src="assets/img/logo-light.png" alt="Luluca Nails">
    <p class="about">Centro de uñas, cejas y belleza en Fuenlabrada. Uñas sanas, 100% veganas y de larga duración, cuidando cada detalle para hacerte brillar.</p>
    <div class="social">
      <a href="{c['instagram']}" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></a>
      <a href="{c['tiktok']}" target="_blank" rel="noopener" aria-label="TikTok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M15 4v9.5a3.5 3.5 0 1 1-3-3.5"/><path d="M15 6a4 4 0 0 0 4 4"/></svg></a>
      <a href="{c['facebook']}" target="_blank" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 8h2V5h-2a3 3 0 0 0-3 3v2H9v3h2v6h3v-6h2l1-3h-3V8a1 1 0 0 1 1-1z"/></svg></a>
      <a href="{c['whatsapp']}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_ICON}</a>
    </div>
  </div>
  <div><h5>Salón Fuenlabrada</h5><a href="{c['fuen_maps']}" target="_blank" rel="noopener">{c['fuen_addr']}</a><a href="tel:{c['tel']}">{c['phone_display']}</a><a href="mailto:{c['email']}">{c['email']}</a><span style="color:#a9b6a9">{c['fuen_hours']}</span></div>
  <div><h5>Enlaces</h5><a href="servicios.html">Servicios y precios</a><a href="galeria.html">Galería</a><a href="{BOOKING_URL}" target="_blank" rel="noopener">Reservar cita</a><a href="contacto.html">Contacto</a></div>
</div>
<div class="legal">© 2026 Luluca Nails · Fuenlabrada · Reservas gestionadas con Lanzo · Aviso legal · Privacidad</div>
</footer>
"""

def mobilebar():
    c=CLIENT
    return f"""<div class="mobile-book">
  <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa call" aria-label="WhatsApp">{WA_ICON}</a>
  <a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-primary">Reservar cita</a>
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
// ---- Reseñas de Google: refresco automático desde reviews.json ----
(function(){
  var grid=document.getElementById('rev-grid'); if(!grid) return;
  var G='<svg viewBox="0 0 48 48" width="16" height="16"><path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/><path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/><path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/><path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2 15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg>';
  function esc(s){return (''+(s||'')).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function stars(n){n=Math.max(1,Math.min(5,Math.round(n||5)));var s='';for(var i=0;i<n;i++)s+='★';return s;}
  fetch('reviews.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():null;}).then(function(d){
    if(!d||!d.reviews||!d.reviews.length) return;
    var sc=document.getElementById('rev-score'); if(sc&&d.rating){sc.textContent=(''+d.rating).replace('.',',');}
    var cn=document.getElementById('rev-count-num'); if(cn&&(d.count||d.count===0)){cn.textContent=d.count;}
    grid.innerHTML=d.reviews.map(function(v){
      var ini=esc(((v.name||'?').trim().charAt(0)||'?').toUpperCase());
      var av = v.photo ? '<div class="av" style="background-image:url('+JSON.stringify(v.photo)+');background-size:cover;color:transparent">'+ini+'</div>' : '<div class="av">'+ini+'</div>';
      return '<div class="rev"><div class="top" style="display:flex;align-items:center;gap:12px">'+av+'<div><div class="who">'+esc(v.name)+'</div><div class="stars">'+stars(v.rating)+'</div></div><span style="margin-left:auto;width:16px;height:16px;display:inline-flex;flex:0 0 auto">'+G+'</span></div><p>"'+esc(v.text)+'"</p><div style="color:var(--muted);font-size:12.5px;margin-top:12px">'+esc(v.date)+' · Google</div></div>';
    }).join('');
  }).catch(function(){});
})();
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

    rev_cards_html = build_review_cards()

    body=f"""{header('inicio')}
<section class="hero"><div class="wrap">
  <div class="hero-copy">
    <span class="eyebrow">Salón de uñas, cejas y belleza · <span data-locname>Fuenlabrada</span></span>
    <h1>Uñas <em>sanas</em>,<br>cuidadas al detalle.</h1>
    <p class="lead">Manicura, nail art, cejas y pestañas con técnicas profesionales y un trato cercano. Tu momento de belleza, reservado en un minuto.</p>
    <div class="hero-actions">
      <a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-gold">{CAL_ICON} Reservar cita</a>
      <a href="servicios.html" class="btn btn-ghost">Ver servicios</a>
    </div>
    <div class="hero-trust"><span class="stars">★★★★★</span><span><b style="color:var(--forest)">Excelente</b> · 4,7 · 127 reseñas en Google</span></div>
  </div>
  <div class="hero-photo thumb-fallback"><img src="assets/img/hero.jpg" alt="Uñas y manicura en Luluca Nails Fuenlabrada"><div class="badge"><div class="n">+4</div><small>años cuidando<br>tus uñas en Fuenlabrada</small></div></div>
</div></section>

<section style="background:#edf0ea;border-top:1px solid rgba(0,0,0,.05);border-bottom:1px solid rgba(0,0,0,.05)"><div class="wrap" style="display:flex;flex-wrap:wrap;gap:12px 26px;justify-content:center;align-items:center;padding:18px 20px;font-size:14px;color:var(--forest)">
  <span><b>100% veganas</b></span><span style="opacity:.3">·</span>
  <span><b>Sin testar en animales</b></span><span style="opacity:.3">·</span>
  <span><b>Esmaltes de larga duración</b></span><span style="opacity:.3">·</span>
  <span><b>4,7★</b> · 127 reseñas en Google</span><span style="opacity:.3">·</span>
  <span><b>+4 años</b> en Fuenlabrada</span>
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
    <div class="pil"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l2.2 4.5L19 8l-3.5 3.4L16.3 16 12 13.7 7.7 16l.8-4.6L5 8l4.8-.5z"/></svg></div><h3>Veganas y cruelty-free</h3><p>Productos 100% veganos y sin testar en animales, de calidad profesional y larga duración.</p></div>
    <div class="pil"><div class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="8" r="3.2"/><path d="M21 21v-2a4 4 0 0 0-3-3.8"/></svg></div><h3>Trato cercano</h3><p>Un espacio pensado para ti, con asesoramiento personalizado.</p></div>
  </div>
</div></section>

<section class="booking sec-pad" id="reservar"><div class="wrap">
  <div class="booking-copy">
    <span class="eyebrow">Reserva online</span>
    <h2>Elige día y hora en un minuto</h2>
    <p>Sin llamadas ni esperas. Consulta la disponibilidad real del salón de <b style="color:var(--forest)">Fuenlabrada</b> y reserva online en un clic.</p>
    <ul>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Disponibilidad en tiempo real</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Recordatorio automático de tu cita</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Cambios y cancelaciones fáciles</li>
    </ul>
    <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} ¿Prefieres WhatsApp? Escríbenos</a>
  </div>
  <div class="cal">
    <span class="cal-badge">Reservas · Lanzo</span>
    <h4>Reserva online 24/7</h4>
    <p style="color:var(--muted);margin:8px 0 20px;line-height:1.5">Consulta la disponibilidad real de <b style="color:var(--forest)">Luluca Nails Fuenlabrada</b> y confirma tu cita al instante en la agenda del salón.</p>
    <a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-primary" style="width:100%;justify-content:center">{CAL_ICON} Reservar cita ahora</a>
    <div class="cal-note">Se abre la página de reservas de tu salón · confirmación inmediata y recordatorio automático.</div>
  </div>
</div></section>

<section class="party sec-pad" id="party">
  <div class="bg thumb-fallback"><img src="https://images.unsplash.com/photo-1638417568431-d518a9b7c11e?w=1400&h=650&q=80&auto=format&fit=crop" alt="" onerror="this.style.display='none'"></div>
  <div class="ov"></div>
  <div class="wrap"><div class="txt"><span class="eyebrow">Celebraciones</span><h2>Beauty Party: celebra diferente</h2><p>Cumpleaños y fiestas de belleza para grupos, con uñas, cejas y pestañas en un ambiente exclusivo. Cuéntanos tu idea y la preparamos.</p></div><a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-gold">Pregunta por celebraciones</a></div>
</section>

<section class="reviews sec-pad" id="opiniones"><div class="wrap">
  <div class="head"><span class="eyebrow">Opiniones</span><h2>Lo que dicen nuestras clientas</h2></div>
  <div class="rev-summary" style="display:flex;align-items:center;justify-content:center;gap:16px;margin:0 auto 36px;max-width:540px">
    <div id="rev-score" style="font-family:'Cormorant Garamond',serif;font-size:54px;line-height:1;color:var(--forest);font-weight:600">4,7</div>
    <div>
      <div class="stars" style="font-size:22px;letter-spacing:2px">★★★★★</div>
      <div style="color:var(--muted);font-size:14px;margin-top:5px;display:flex;align-items:center;gap:7px"><span style="width:16px;height:16px;display:inline-flex;flex:0 0 auto"><svg viewBox="0 0 48 48" width="16" height="16"><path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/><path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/><path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/><path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2 15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg></span> <span id="rev-count-num">127</span> reseñas reales en Google</div>
    </div>
  </div>
  <div class="rev-grid" id="rev-grid">{rev_cards_html}</div>
  <p class="center" style="margin-top:28px"><a href="https://www.google.com/maps/search/Luluca+Nails+Fuenlabrada" target="_blank" rel="noopener" class="btn btn-ghost">Ver todas las reseñas en Google</a></p>
</div></section>

<section class="locs sec-pad" id="locales"><div class="wrap">
  <div class="head"><span class="eyebrow">Dónde estamos</span><h2>Nuestro salón en Fuenlabrada</h2></div>
  <p class="subnote">Estamos en el centro de Fuenlabrada. Ven a vernos o reserva tu cita online.</p>
  <div class="loc-grid">
    <div class="loc"><div class="map"><iframe loading="lazy" src="https://www.google.com/maps?q=Calle%20Escocia%201,%20Fuenlabrada&output=embed"></iframe></div><div class="body"><span class="tag-here">Salón principal</span><h3>Fuenlabrada</h3><div class="info"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['fuen_addr']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['phone_display']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['fuen_hours']}</div></div><div class="actions"><a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-primary">Reservar aquí</a><a href="{c['fuen_maps']}" target="_blank" rel="noopener" class="btn btn-ghost">Cómo llegar</a></div></div></div>
  </div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Luluca Nails — Uñas, manicura semipermanente y nail art en Fuenlabrada",
                "Salón de uñas, cejas y pestañas en Fuenlabrada. Manicura semipermanente, uñas de gel y acrílico, nivelación, pedicura y nail art. 100% veganas. Reserva tu cita online.") + body

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
<section class="reserva-band" id="reserva"><span class="eyebrow" style="color:var(--gold-2)">Reserva online</span><h2>¿Lo tienes claro? Reserva en un minuto</h2><p>Elige día y hora en la agenda del salón de <span data-locname>Fuenlabrada</span>. Sin llamadas ni esperas.</p><a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-gold">Ir a reservar</a></section>
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
<p class="center" style="margin-top:34px"><a href="{BOOKING_URL}" target="_blank" rel="noopener" class="btn btn-primary">Reserva tu cita</a></p></div></section>
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
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Contacto — Luluca Nails","Contacta con Luluca Nails por WhatsApp, teléfono o email. Salón en Fuenlabrada.")+body

def w(path,html):
    open("/home/claude/site/"+path,"w",encoding="utf-8").write(html)
    print("wrote",path,len(html)//1024,"KB")

w("index.html",build_index())
w("servicios.html",build_servicios())
w("galeria.html",build_galeria())
w("contacto.html",build_contacto())
write_reviews_json("/home/claude/site/reviews.json")
print("wrote reviews.json")
print("OK")
