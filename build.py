# -*- coding: utf-8 -*-
"""Generador estático de la web de Luluca Nails.
Ensambla las páginas desde partes comunes (cabecera, pie, scripts) + datos del cliente.
Este es el germen del sistema multi-web: cambiando CLIENT y las imágenes se produce otra web."""
import re, io, sys, json, os

# Directorio de salida = el del propio script (antes estaba cableado a /home/claude/site,
# ruta de un contenedor efimero: el generador no podia ejecutarse fuera de el).
OUT = os.path.dirname(os.path.abspath(__file__)) or "."
SITE_URL = "https://lulucanails.com"

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
  # Humanes (segundo local). WhatsApp propio pendiente: de momento usa el de la marca.
  "huma_addr": "Avenida Campo Hermoso 44, Humanes de Madrid",
  "huma_maps": "https://www.google.com/maps/search/?api=1&query=Avenida%20Campo%20Hermoso%2044%20Humanes%20de%20Madrid",
  "huma_hours": "L-V 09:00–20:00",
  "huma_phone_display": "625 17 97 79",
  "huma_tel": "+34625179779",
}

# Slugs de reservas (cada local a su cuenta de Lanzo)
SLUG_FUEN = "luluca-nails-fuenlabrada"
SLUG_HUMA = "luluca-nails-humanes"
# WhatsApp por local (Humanes hereda el de la marca hasta tener número propio)
CLIENT["huma_whatsapp"] = CLIENT["whatsapp"]

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
<div style="background:var(--forest);color:#fff;text-align:center;font-size:13.5px;padding:9px 16px;line-height:1.35">El mismo Luluca Nails de siempre, ahora también en <b style="color:var(--gold-2)">Humanes de Madrid</b> · Reserva online en Fuenlabrada o Humanes</div>
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
    <p class="about">Centro de uñas, cejas y belleza en Fuenlabrada y Humanes de Madrid. Uñas sanas, 100% veganas y de larga duración, cuidando cada detalle para hacerte brillar.</p>
    <div class="social">
      <a href="{c['instagram']}" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg></a>
      <a href="{c['tiktok']}" target="_blank" rel="noopener" aria-label="TikTok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M15 4v9.5a3.5 3.5 0 1 1-3-3.5"/><path d="M15 6a4 4 0 0 0 4 4"/></svg></a>
      <a href="{c['facebook']}" target="_blank" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M14 8h2V5h-2a3 3 0 0 0-3 3v2H9v3h2v6h3v-6h2l1-3h-3V8a1 1 0 0 1 1-1z"/></svg></a>
      <a href="{c['whatsapp']}" target="_blank" rel="noopener" aria-label="WhatsApp">{WA_ICON}</a>
    </div>
  </div>
  <div><h5>Salón Fuenlabrada</h5><a href="{c['fuen_maps']}" target="_blank" rel="noopener">{c['fuen_addr']}</a><a href="tel:{c['tel']}">{c['phone_display']}</a><a href="mailto:{c['email']}">{c['email']}</a><span style="color:#a9b6a9">{c['fuen_hours']}</span></div>
  <div><h5>Salón Humanes</h5><a href="{c['huma_maps']}" target="_blank" rel="noopener">{c['huma_addr']}</a><a href="tel:{c['huma_tel']}">{c['huma_phone_display']}</a><span style="color:#a9b6a9">{c['huma_hours']}</span></div>
  <div><h5>Enlaces</h5><a href="servicios.html">Servicios y precios</a><a href="galeria.html">Galería</a><a href="index.html#reservar">Reservar cita</a><a href="contacto.html">Contacto</a></div>
</div>
<div class="legal">© 2026 Luluca Nails · Fuenlabrada y Humanes · Reservas gestionadas con Lanzo · <a href="aviso-legal.html">Aviso legal</a> · <a href="privacidad.html">Privacidad</a> · <a href="cookies.html">Cookies</a></div>
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
function lzSwitchLoc(btn){document.querySelectorAll('.lz-locbtn').forEach(function(b){b.classList.toggle('on',b===btn);});if(btn.dataset.k)setLocale(btn.dataset.k);if(window.__lzSwitch)window.__lzSwitch(btn.dataset.slug,btn.dataset.wa||'#');}
function lzGoto(k){var b=document.querySelector('.lz-locbtn[data-k="'+k+'"]');if(b)lzSwitchLoc(b);}
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
// ===== Widget de reservas Lanzo (embebido) v3: calendario visible + desplegable con grupos =====
(function(){
  var root=document.getElementById('lz-book'); if(!root) return;
  var API=root.dataset.api, SLUG='', WA='#';
  var st={service:null,date:null,slot:null,employeeId:null,allowEmp:true,_slots:[],_services:[],_period:{m:[],t:[]},_query:''};
  var view={y:0,m:0};
  var MES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
  // ── Carta de servicios ────────────────────────────────────────────────────
  // Antes esto adivinaba la categoria con expresiones regulares sobre el nombre
  // y la metia en cinco grupos fijos. La API publica YA devuelve el `category`
  // que ha puesto la duena, asi que adivinar teniendo la respuesta delante
  // sobraba: lo que sale aqui es su propia clasificacion.
  //
  // PUENTE, NO DESTINO. El buscador de abajo es una traduccion fiel y minima del
  // motor unico de catalogo (D-393, apps/beautysaas-web/lib/catalog/), que es el
  // que usan el TPV, la agenda y el widget oficial. Aqui no se puede importar
  // porque esta web es HTML estatico sin build de TypeScript. Es una COPIA, y
  // D-393 dice que no se copia: vive solo hasta que esta web pase al widget
  // servido desde Lanzo. Si cambia el criterio alli, hay que traerlo aqui a mano.
  var COL=new Intl.Collator('es',{sensitivity:'base'});
  var OTROS='Otros';
  // Sin diacriticos y en minusculas, igual que `normalizeForSearch`.
  function normTxt(x){return (x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}
  function catOf(sv){var c=(sv.category||'').trim();return c||OTROS;}
  // rank 0 = el nombre empieza por lo escrito · 1 = empieza una palabra · 2 = va dentro
  function rankOf(nom,q){
    if(nom.indexOf(q)===0) return 0;
    var i=nom.indexOf(q); if(i<0) return -1;
    return ' -/(,.+'.indexOf(nom.charAt(i-1))>=0 ? 1 : 2;
  }
  function buscar(q){
    // Dos letras, igual que el motor del producto (MIN_QUERY_LENGTH): con una
    // sola, la carta salta a modo búsqueda antes de que la sugerencia sirva de
    // nada y la clienta pierde de vista las categorías.
    var qn=normTxt(q).trim(); if(qn.length<2) return null;
    var out=[];
    (st._services||[]).forEach(function(sv){
      var r=rankOf(normTxt(sv.name),qn); if(r>=0) out.push({s:sv,r:r});
    });
    out.sort(function(a,b){return a.r-b.r || COL.compare(a.s.name,b.s.name);});
    return out.map(function(o){return o.s;});
  }
  // Agrupa por categoria REAL. Unifica las que solo difieren en mayusculas o
  // acentos —el catalogo de Luluca trae "Uñas" y "uñas", "Pestañas y Cejas" y
  // "Pestañas y cejas"— y ensena como etiqueta la variante mas usada, para que
  // la clienta no vea dos apartados que son el mismo. Orden: alfabetico con
  // "Otros" al final, y dentro de cada uno alfabetico insensible a acentos.
  function agrupar(lista){
    var by={};
    lista.forEach(function(sv){
      var c=catOf(sv), k=normTxt(c);
      if(!by[k]) by[k]={items:[],nombres:{}};
      by[k].items.push(sv);
      by[k].nombres[c]=(by[k].nombres[c]||0)+1;
    });
    return Object.keys(by).map(function(k){
      var n=by[k].nombres;
      var label=Object.keys(n).sort(function(a,b){
        var f=n[b]-n[a]; if(f) return f;
        // A igual frecuencia gana la que empieza en mayuscula: el catalogo trae
        // "Uñas" y "uñas" con el mismo recuento, y un apartado en minuscula
        // canta. Mismo desempate que el script de limpieza del catalogo.
        var ma=/^[A-ZÀ-Ü]/.test(a)?1:0, mb=/^[A-ZÀ-Ü]/.test(b)?1:0;
        if(ma!==mb) return mb-ma;
        return a.localeCompare(b,'es');
      })[0];
      return {label:label,items:by[k].items.sort(function(a,b){return COL.compare(a.name,b.name);})};
    }).sort(function(a,b){
      if(a.label===OTROS) return 1; if(b.label===OTROS) return -1;
      return a.label.localeCompare(b.label,'es');
    });
  }

  var css=[
   // El margen de arriba libra el `.cal-badge`, que va absolute en la esquina:
   // con el titulo corto no se tocaban, pero "Reserva tu cita en 3 pasos" le
   // llegaba justo debajo y el badge lo tapaba.
   '#lz-book .lz-h{font-family:"Cormorant Garamond",serif;color:var(--forest);font-size:24px;margin:28px 0 14px;line-height:1.15}',
   '#lz-book label{display:block;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--forest);margin:18px 0 9px;font-weight:700}',
   '#lz-book label:first-of-type{margin-top:6px}',
   '#lz-book input{width:100%;padding:12px 12px;border:1px solid #d8d5cc;border-radius:12px;font:inherit;background:#fff;color:var(--forest);box-sizing:border-box}',
   // La x nativa de type=search en Chrome se solaparia con la nuestra.
   '#lz-book input[type=search]::-webkit-search-cancel-button{display:none}',
   '#lz-book .lz-meta{font-size:13px;color:var(--muted);margin-top:6px}',
   '.lz-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}',
   '.lz-chip{padding:9px 16px;border:1px solid #d8d5cc;border-radius:999px;background:#fff;cursor:pointer;font:inherit;font-size:14px;color:var(--forest)}',
   '.lz-chip.sel{background:var(--forest);color:#fff;border-color:var(--forest)}',
   '.lz-chip:disabled{opacity:.4;cursor:default}',
   // El paso de mañana/tarde es el que se colaba: dos pildoras blancas con
   // borde gris no piden que las toquen, y la clienta leia la ausencia de horas
   // como ausencia de huecos. `pedir` vive solo hasta que elige periodo.
   '.lz-chip.pedir{border:2px solid var(--gold-2);font-weight:700;box-shadow:0 2px 10px rgba(0,0,0,.06)}',
   '.lz-pick{color:var(--forest);font-size:14.5px;font-weight:700;line-height:1.35;padding:11px 13px;background:#fff;border:1px dashed var(--gold-2);border-radius:12px;margin-top:2px}',
   '.lz-ovl{position:fixed;top:0;right:0;bottom:0;left:0;z-index:2147483000;background:rgba(20,28,22,.55);display:flex;align-items:center;justify-content:center;padding:18px}',
   '.lz-toast{background:#fff;border-radius:16px;box-shadow:0 16px 50px rgba(0,0,0,.3);padding:22px 18px 18px;text-align:center;color:var(--forest);font:inherit;max-width:420px;width:100%;box-sizing:border-box}',
   '.lz-toast-check{width:46px;height:46px;margin:0 auto 10px;border-radius:999px;background:var(--forest);color:#fff;font-size:24px;line-height:46px;font-weight:700}',
   '.lz-toast h4{font-family:"Cormorant Garamond",serif;font-size:25px;font-weight:600;margin:0 0 8px;color:var(--forest)}',
   '.lz-toast p{font-size:15px;color:var(--forest);margin:0 0 10px;line-height:1.45}',
   '.lz-toast .lz-toast-sub{font-size:13px;color:var(--muted);margin-bottom:16px}',
   '.lz-toast-ok{display:block;width:100%;padding:13px;border:none;border-radius:11px;background:var(--forest);color:#fff;font:inherit;font-size:15px;font-weight:700;cursor:pointer}',
   '.lz-search-wrap{position:relative}',
   '.lz-qclear{position:absolute;right:8px;top:50%;transform:translateY(-50%);border:none;background:#eceae3;width:26px;height:26px;border-radius:999px;cursor:pointer;font-size:15px;line-height:1;color:var(--forest)}',
   // El paso 1 va PLEGADO. Abierto en canal empujaba el calendario tan abajo que
   // costaba encontrarlo, que es justo el paso siguiente. Cerrado ocupa una linea;
   // abierto tiene tope de alto y su propio scroll, asi que nunca desplaza el
   // resto de la pagina fuera de la pantalla.
   '.lz-salones{display:flex;gap:8px;flex-wrap:wrap}',
   '.lz-sal{flex:1 1 140px;padding:15px 12px;border:2px solid #d8d5cc;border-radius:12px;background:#fff;font:inherit;font-size:16px;font-weight:700;color:var(--forest);cursor:pointer}',
   '.lz-sal.on{background:var(--forest);color:#fff;border-color:var(--forest)}',
   '.lz-abre{width:100%;display:flex;align-items:center;gap:10px;text-align:left;padding:12px;border:1px solid #d8d5cc;border-radius:12px;background:#fff;font:inherit;font-size:15px;color:var(--forest);cursor:pointer;box-sizing:border-box}',
   '.lz-abre[aria-expanded="true"]{border-color:var(--gold-2)}',
   '.lz-abre.elegido{font-weight:600}',
   '#lz-abre-txt{flex:1;line-height:1.3}',
   '.lz-abre-ch{color:var(--gold);font-size:12px;flex:0 0 auto}',
   '.lz-panel{margin-top:8px;border:1px solid #ece9e2;border-radius:12px;background:#f7f6f1;padding:12px;max-height:58vh;overflow-y:auto;-webkit-overflow-scrolling:touch}',
   '.lz-panel .lz-grouptitle:first-child{margin-top:2px}',
   '.lz-grouptitle{font-family:"Cormorant Garamond",serif;font-size:18px;color:var(--forest);margin:16px 0 8px}',
   '.lz-srvlist{display:flex;flex-direction:column;gap:6px}',
   '.lz-srv{display:flex;flex-direction:column;gap:2px;text-align:left;width:100%;padding:10px 12px;border:1px solid #ece9e2;border-radius:10px;background:#faf9f5;cursor:pointer;font:inherit;color:var(--forest)}',
   '.lz-srv:hover{border-color:var(--forest)}',
   '.lz-srv.sel{background:var(--forest);color:#fff;border-color:var(--forest)}',
   '.lz-srv-n{font-size:14.5px;font-weight:400;line-height:1.3}',
   '.lz-srv-m{font-size:12.5px;color:var(--muted)}',
   '.lz-srv.sel .lz-srv-m{color:rgba(255,255,255,.78)}',
   '.lz-cat{border:1px solid #ece9e2;border-radius:10px;background:#fff;margin-bottom:6px}',
   '.lz-cat>summary{padding:11px 12px;cursor:pointer;font-size:14.5px;font-weight:600;color:var(--forest);list-style:none;display:flex;align-items:center;gap:8px}',
   '.lz-cat>summary::-webkit-details-marker{display:none}',
   '.lz-cat>summary::after{content:"+";margin-left:auto;color:var(--gold);font-weight:700;font-size:17px}',
   '.lz-cat[open]>summary::after{content:"−"}',
   '.lz-catn{font-size:12px;color:var(--muted);font-weight:600}',
   '.lz-cat>div{padding:0 10px 10px}',
   '.lz-calhead{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}',
   '.lz-calhead b{font-family:"Cormorant Garamond",serif;font-weight:600;font-size:19px;color:var(--forest);text-transform:capitalize}',
   '.lz-nav{border:none;background:#eceae3;width:34px;height:34px;border-radius:9px;cursor:pointer;font-size:16px;color:var(--forest)}',
   '.lz-nav:disabled{opacity:.35;cursor:default}',
   '.lz-dow{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-bottom:6px}',
   '.lz-dow span{text-align:center;font-size:11px;color:var(--muted);font-weight:600}',
   '.lz-days{display:grid;grid-template-columns:repeat(7,1fr);gap:6px}',
   '.lz-day{padding:11px 0;border:1px solid #ece9e2;border-radius:10px;background:#faf9f5;cursor:pointer;font:inherit;font-size:15px;color:var(--forest)}',
   '.lz-day:hover:not(.off){border-color:var(--forest)}',
   '.lz-day.off{opacity:.32;background:transparent;border-color:transparent;cursor:default}',
   '.lz-day.sel{background:var(--forest);color:#fff;border-color:var(--forest)}',
   '.lz-hint{color:var(--gold);font-size:13px;margin-top:10px;min-height:16px;font-weight:600}',
   '#lz-times,#lz-emps{display:flex;flex-wrap:wrap;gap:8px}',
   '.lz-time,.lz-emp{padding:10px 15px;border:1px solid #d8d5cc;border-radius:10px;background:#fff;cursor:pointer;font:inherit;color:var(--forest)}',
   '.lz-time:hover,.lz-emp:hover{border-color:var(--forest)}',
   '.lz-time.sel,.lz-emp.sel{background:var(--forest);color:#fff;border-color:var(--forest)}',
   '.lz-msg{color:var(--muted);font-size:14px;padding:6px 0}',
   '.lz-err{color:#b3261e;font-size:13px;margin-top:8px;min-height:16px}',
   '.lz-foot{margin-top:18px;font-size:13px;color:var(--muted)}',
   '.lz-foot a{color:var(--forest);text-decoration:underline}',
   '.lz-ok{text-align:center;padding:10px 0}',
   '.lz-check{width:54px;height:54px;border-radius:50%;background:var(--forest);color:#fff;font-size:27px;display:flex;align-items:center;justify-content:center;margin:6px auto 12px}',
   '.lz-ok h4{font-family:"Cormorant Garamond",serif;color:var(--forest);font-size:25px;margin-bottom:8px}',
   '.lz-ok p{color:var(--muted);margin-bottom:10px}',
   '.lz-locbtn{padding:9px 18px;border:1px solid #d8d5cc;border-radius:999px;background:#fff;cursor:pointer;font:inherit;font-size:14px;color:var(--forest)}',
   '.lz-locbtn.on{background:var(--forest);color:#fff;border-color:var(--forest)}'
  ].join('');
  var stl=document.createElement('style'); stl.textContent=css; document.head.appendChild(stl);

  function esc(s){s=''+(s||'');return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function eur(n){n=Number(n)||0;return (Math.round(n*100)/100).toString().replace('.',',')+' €';}
  function fmt(iso){return new Date(iso).toLocaleTimeString('es-ES',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Madrid'});}
  function hourOf(iso){return parseInt(new Date(iso).toLocaleTimeString('en-GB',{hour:'2-digit',hour12:false,timeZone:'Europe/Madrid'}).slice(0,2),10);}
  function todayYMD(){return new Date().toLocaleDateString('en-CA',{timeZone:'Europe/Madrid'});}
  function ymd(y,m,d){return y+'-'+String(m+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');}
  function api(p){return fetch(API+p).then(function(r){if(!r.ok){var e=new Error('x');e.status=r.status;throw e;}return r.json();});}
  function g(id){return document.getElementById(id);}
  function show(s){var e=g('lz-step-'+s); if(e) e.hidden=false;}
  function hide(s){var e=g('lz-step-'+s); if(e) e.hidden=true;}

  function boot(){
    SLUG=root.dataset.slug||''; WA=root.dataset.wa||'#';
    st={service:null,date:null,slot:null,employeeId:null,allowEmp:true,_slots:[],_services:[],_period:{m:[],t:[]},_query:''};
    view={y:0,m:0};
    root.innerHTML=
     '<span class="cal-badge">Reservas 24/7 con Lanzo</span>'+
     '<div class="lz-h">Reserva tu cita en 3 pasos</div>'+
     '<div id="lz-step-sal"><label>1 · Elige tu salón</label><div id="lz-salones" class="lz-salones"></div><div id="lz-salaviso"></div></div>'+
     '<div id="lz-step-svc" hidden><label>2 · Elige tu servicio</label>'+
     '<button type="button" id="lz-abre" class="lz-abre" aria-expanded="false" aria-controls="lz-panel"><span id="lz-abre-txt">Elige tu servicio…</span><span class="lz-abre-ch" aria-hidden="true">▾</span></button>'+
     '<div id="lz-panel" class="lz-panel" hidden>'+
     '<div class="lz-search-wrap"><input id="lz-q" class="lz-search" type="search" placeholder="Buscar servicio…" aria-label="Buscar servicio" autocomplete="off" autocapitalize="off" spellcheck="false"><button type="button" id="lz-qclear" class="lz-qclear" aria-label="Borrar la búsqueda" hidden>×</button></div>'+
     '<div id="lz-carta"><div class="lz-msg">Cargando servicios…</div></div></div></div>'+
     '<div id="lz-step-date" hidden><label>3 · Elige fecha y hora</label><div id="lz-cal"></div><div id="lz-hint" class="lz-hint"></div></div>'+
     '<div id="lz-step-time" hidden><div id="lz-period" class="lz-chips"></div><div id="lz-times"></div></div>'+
     '<div id="lz-step-emp" hidden><label id="lz-emp-label">Elige profesional</label><div id="lz-emps"></div></div>'+
     '<div id="lz-step-form" hidden><label id="lz-form-label">Tus datos</label><input id="lz-name" placeholder="Nombre y apellidos" autocomplete="name"><div style="height:8px"></div><input id="lz-phone" placeholder="Teléfono móvil" inputmode="tel" autocomplete="tel"><button id="lz-confirm" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:12px">Confirmar reserva</button><div class="lz-err" id="lz-err"></div></div>'+
     '<div class="lz-foot">Confirmación inmediata y recordatorio automático. ¿Prefieres WhatsApp? <a href="'+WA+'" target="_blank" rel="noopener">Escríbenos</a></div>';
    renderSalones();
    // SIN SALON NO SE CARGA NADA, Y ES A PROPOSITO. Antes arrancaba con
    // Fuenlabrada puesta: quien no se fijaba reservaba en el salón equivocado, y
    // eso se arregla en el mostrador o con una llamada. Que elija a mano.
    if(!SLUG){
      g('lz-salaviso').innerHTML='<div class="lz-pick">↑ Elige el salón donde quieres tu cita y te enseñamos sus servicios y sus horas libres</div>';
      return;
    }
    show('svc'); show('date');
    renderCal();
    api('/salon/'+SLUG).then(function(s){
      st.allowEmp = !(s && s.allowEmployeeSelection===false);
      var fl=g('lz-form-label'); if(fl) fl.textContent=(st.allowEmp?'5':'4')+' · Tus datos';
      st._services=(s&&s.services)||[];
      renderCarta();
    }).catch(function(){ g('lz-carta').innerHTML='<div class="lz-pick">No se pudieron cargar los servicios. Recarga la página o escríbenos por WhatsApp.</div>'; });
  }

  // Las sedes vienen del HTML. Los botones llevan las mismas clases y datos que
  // el conmutador viejo, así que `lzGoto('huma')` de la sección de sedes sigue
  // funcionando sin tocar nada.
  var SALONES=[];
  try{ SALONES=JSON.parse(root.dataset.salones||'[]'); }catch(e){ SALONES=[]; }

  function renderSalones(){
    var cont=g('lz-salones'); if(!cont) return;
    cont.innerHTML=SALONES.map(function(sa){
      return '<button type="button" class="lz-locbtn lz-sal'+(SLUG===sa.slug?' on':'')+'" data-k="'+sa.k+
             '" data-slug="'+sa.slug+'" data-wa="'+sa.wa+'">'+esc(sa.nombre)+'</button>';
    }).join('');
  }

  function elegirSalon(slug,wa,k){
    if(!slug || SLUG===slug) return;
    root.dataset.slug=slug; root.dataset.wa=wa||'#';
    // Mantiene en su sitio los nombres de sede del resto de la página.
    if(k && typeof window.setLocale==='function'){ try{ window.setLocale(k); }catch(e){} }
    boot();
  }

  function pintarTrigger(){
    var t=g('lz-abre-txt'), b=g('lz-abre'); if(!t||!b) return;
    if(st.service){
      t.textContent=st.service.name+' · '+(st.service.durationMin||0)+' min · '+eur(st.service.priceEur);
      b.classList.add('elegido');
    } else { t.textContent='Elige tu servicio…'; b.classList.remove('elegido'); }
  }
  function abrirPanel(){
    var pn=g('lz-panel'), b=g('lz-abre'); if(!pn) return;
    pn.hidden=false; if(b) b.setAttribute('aria-expanded','true');
    try{g('lz-q').focus({preventScroll:true});}catch(e){}
  }
  function cerrarPanel(){
    var pn=g('lz-panel'), b=g('lz-abre'); if(!pn) return;
    pn.hidden=true; if(b) b.setAttribute('aria-expanded','false');
  }

  function srvBtn(sv){
    var sel=(st.service&&st.service.id===sv.id)?' sel':'';
    return '<button type="button" class="lz-srv'+sel+'" data-s="'+sv.id+'">'+
           '<span class="lz-srv-n">'+esc(sv.name)+'</span>'+
           '<span class="lz-srv-m">'+(sv.durationMin||0)+' min · '+eur(sv.priceEur)+'</span></button>';
  }

  function renderCarta(){
    var cont=g('lz-carta'); if(!cont) return;
    var res=buscar(st._query||'');
    if(res){
      cont.innerHTML = res.length
        ? '<div class="lz-srvlist">'+res.map(srvBtn).join('')+'</div>'
        : '<div class="lz-pick">No hemos encontrado nada con \u201c'+esc((st._query||'').trim())+'\u201d. Prueba con otra palabra, o mira la carta.</div>';
      return;
    }
    var html='';
    // `destacado` lo calcula el backend con la frecuencia real de reserva de ESE
    // salon. Un salon recien dado de alta no tiene historial y entonces no hay
    // destacados: se ensena la carta y ya.
    var dest=(st._services||[]).filter(function(sv){return sv.destacado;});
    if(dest.length){
      html+='<div class="lz-grouptitle">Los más pedidos</div><div class="lz-srvlist">'+dest.map(srvBtn).join('')+'</div>';
    }
    var grupos=agrupar(st._services||[]);
    if(grupos.length){
      html+='<div class="lz-grouptitle">'+(dest.length?'Todo lo que hacemos':'Nuestros servicios')+'</div>';
      // Si no hay destacados se abre la primera categoria: una carta entera
      // plegada obliga a un toque antes de ver un solo precio.
      html+=grupos.map(function(gr,i){
        return '<details class="lz-cat"'+((i===0&&!dest.length)?' open':'')+'><summary>'+esc(gr.label)+
               ' <span class="lz-catn">'+gr.items.length+'</span></summary><div class="lz-srvlist">'+
               gr.items.map(srvBtn).join('')+'</div></details>';
      }).join('');
    }
    cont.innerHTML=html;
  }

  // No se repinta la carta entera a proposito: si se repintara, el acordeon se
  // cerraria justo cuando la clienta acaba de elegir dentro de una categoria.
  function elegirServicio(id){
    st.service=(st._services||[]).filter(function(v){return v.id===id;})[0]||null;
    st.slot=null; st.employeeId=null; hide('emp'); hide('form');
    g('lz-hint').textContent='';
    var bs=g('lz-carta').querySelectorAll('.lz-srv');
    for(var i=0;i<bs.length;i++) bs[i].classList.toggle('sel', bs[i].dataset.s===id);
    // Se cierra al elegir: asi el calendario vuelve a quedar pegado debajo.
    pintarTrigger();
    cerrarPanel();
    // Si ya habia dia elegido, el flujo se recupera solo y salen las horas.
    if(st.date) loadTimes(st.date); else hide('time');
  }

  function renderCal(){
    var today=todayYMD();
    if(!view.y){ view.y=parseInt(today.slice(0,4),10); view.m=parseInt(today.slice(5,7),10)-1; }
    var first=new Date(view.y,view.m,1).getDay(), offset=(first+6)%7, dim=new Date(view.y,view.m+1,0).getDate();
    var curYM=today.slice(0,7), viewYM=ymd(view.y,view.m,1).slice(0,7);
    var h='<div class="lz-calhead"><button type="button" class="lz-nav" id="lz-prev"'+(viewYM<=curYM?' disabled':'')+'>‹</button><b>'+MES[view.m]+' '+view.y+'</b><button type="button" class="lz-nav" id="lz-next">›</button></div>';
    h+='<div class="lz-dow"><span>L</span><span>M</span><span>X</span><span>J</span><span>V</span><span>S</span><span>D</span></div><div class="lz-days">';
    for(var i=0;i<offset;i++) h+='<span></span>';
    for(var d=1;d<=dim;d++){ var ds=ymd(view.y,view.m,d), past=ds<today; h+='<button type="button" class="lz-day'+(past?' off':'')+(st.date===ds?' sel':'')+'"'+(past?' disabled':'')+' data-d="'+ds+'">'+d+'</button>'; }
    g('lz-cal').innerHTML=h+'</div>';
  }

  function pickDay(ds){
    st.date=ds; st.slot=null; st.employeeId=null; renderCal();
    if(!st.service){
      // Antes esto escondia la seccion de horas ENTERA y dejaba el aviso debajo
      // del calendario: la clienta se queda mirando el sitio donde deberian salir
      // las horas, no ve nada, y concluye que ese dia no tiene hueco. El aviso
      // tiene que estar donde esta mirando, no doscientos pixeles mas arriba.
      // `preventScroll` para que el foco del desplegable no le arrastre la vista
      // justo al mensaje que acabamos de poner delante.
      g('lz-hint').textContent='';
      show('time'); hide('emp'); hide('form');
      g('lz-period').innerHTML='';
      g('lz-times').innerHTML='<div class="lz-pick">↑ Elige primero tu servicio arriba para ver las horas libres</div>';
      abrirPanel();
      return;
    }
    g('lz-hint').textContent=''; loadTimes(ds);
  }

  function loadTimes(ds){
    st.slot=null; st.employeeId=null; hide('emp'); hide('form');
    show('time'); g('lz-period').innerHTML=''; g('lz-times').innerHTML='<div class="lz-msg">Buscando horas libres…</div>';
    api('/availability?salonSlug='+SLUG+'&date='+ds+'&serviceId='+st.service.id).then(function(a){
      var slots=(a&&a.slots)||[]; st._slots=slots;
      if(!slots.length){ g('lz-period').innerHTML=''; g('lz-times').innerHTML='<div class="lz-msg">No hay horas libres ese día. Prueba con otro.</div>'; return; }
      var m=[],tt=[]; slots.forEach(function(s,i){ (hourOf(s.startsAt)<14?m:tt).push(i); });
      st._period={m:m,t:tt};
      g('lz-period').innerHTML='<button type="button" class="lz-chip pedir" data-p="m"'+(m.length?'':' disabled')+'>Mañana ('+m.length+')</button><button type="button" class="lz-chip pedir" data-p="t"'+(tt.length?'':' disabled')+'>Tarde ('+tt.length+')</button>';
      // Decir el numero total es lo que desmonta el "no hay huecos": la clienta ve
      // que hay 20 libres antes de tocar nada.
      g('lz-times').innerHTML='<div class="lz-pick">\u2191 Toca <b>Mañana</b> o <b>Tarde</b> para ver las '+slots.length+' horas libres de ese día</div>';
      if(m.length && !tt.length) showPeriod('m'); else if(tt.length && !m.length) showPeriod('t');
    }).catch(function(){ g('lz-period').innerHTML=''; g('lz-times').innerHTML='<div class="lz-msg">No se pudo cargar la disponibilidad. Prueba de nuevo.</div>'; });
  }

  function showPeriod(p){
    [...g('lz-period').children].forEach(function(b){ if(b.dataset){ b.classList.toggle('sel', b.dataset.p===p); b.classList.remove('pedir'); } });
    var idxs=(p==='m')?st._period.m:st._period.t;
    g('lz-times').innerHTML=idxs.map(function(i){return '<button type="button" class="lz-time" data-i="'+i+'">'+fmt(st._slots[i].startsAt)+'</button>';}).join('');
    st.slot=null; st.employeeId=null; hide('emp'); hide('form');
  }

  function pickTime(i){
    st.slot=st._slots[i]; st.employeeId=null; hide('form');
    var tb=g('lz-times').children; for(var k=0;k<tb.length;k++) tb[k].classList.toggle('sel', String(tb[k].dataset.i)===String(i));
    var emps=(st.slot&&st.slot.employees)||[];
    if(!st.allowEmp){ hide('emp'); st.employeeId=(emps[0]&&emps[0].id)||null; show('form'); return; }
    show('emp');
    g('lz-emps').innerHTML='<button type="button" class="lz-emp" data-e="any">Sin preferencia</button>'+emps.map(function(e){return '<button type="button" class="lz-emp" data-e="'+e.id+'">'+esc(e.name)+'</button>';}).join('');
  }

  function pickEmp(val){
    var emps=(st.slot&&st.slot.employees)||[];
    st.employeeId=(val==='any')?(emps[0]&&emps[0].id):val;
    var eb=g('lz-emps').children; for(var k=0;k<eb.length;k++) eb[k].classList.toggle('sel', eb[k].dataset.e===val);
    show('form');
  }

  function doBooking(){
    var name=g('lz-name').value.trim(), phone=g('lz-phone').value.trim(), err=g('lz-err');
    if(name.length<2){ err.textContent='Escribe tu nombre.'; return; }
    if(phone.replace(/[^0-9]/g,'').length<7){ err.textContent='Escribe un teléfono válido.'; return; }
    if(st.allowEmp && !st.employeeId){ err.textContent='Elige una profesional.'; return; }
    err.textContent='';
    var btn=g('lz-confirm'); btn.disabled=true; btn.textContent='Reservando…';
    var payload={salonSlug:SLUG,serviceId:st.service.id,startTime:st.slot.startsAt,clientName:name,clientPhone:phone};
    if(st.employeeId) payload.employeeId=st.employeeId;
    fetch(API+'/booking',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(function(r){
      if(r.status===201){ return r.json().then(done); }
      if(r.status===409){ err.textContent='Ese hueco se acaba de ocupar. Te muestro otras horas.'; btn.disabled=false; btn.textContent='Confirmar reserva'; loadTimes(st.date); return; }
      err.textContent='No se pudo reservar. Inténtalo de nuevo o escríbenos por WhatsApp.'; btn.disabled=false; btn.textContent='Confirmar reserva';
    }).catch(function(){ err.textContent='Error de conexión. Prueba de nuevo o escríbenos por WhatsApp.'; btn.disabled=false; btn.textContent='Confirmar reserva'; });
  }

  function done(j){
    var iso=(j&&j.startsAt)||st.slot.startsAt;
    var dia=new Date(iso).toLocaleDateString('es-ES',{weekday:'long',day:'numeric',month:'long',timeZone:'Europe/Madrid'});
    var emp=(j&&j.employee&&j.employee.name)||'';
    root.innerHTML='<span class="cal-badge">Reserva confirmada</span><div class="lz-ok" id="lz-ok" tabindex="-1" role="status"><div class="lz-check">✓</div><h4>¡Cita confirmada!</h4><p>'+esc(st.service.name)+(emp?(' con '+esc(emp)):'')+'<br>'+esc(dia)+' a las '+fmt(iso)+'</p><p style="font-size:13px">Te esperamos. Recibirás un recordatorio; si necesitas cambiarla, escríbenos por WhatsApp.</p><a class="btn btn-ghost" href="'+WA+'" target="_blank" rel="noopener">Escribir por WhatsApp</a></div>';
    // La tarjeta de confirmación es mucho más corta que el widget desplegado:
    // al sustituirlo, la página se acorta por encima de donde está mirando la
    // clienta y su scroll acaba en la sección de sedes o en el pie, con la
    // confirmación fuera de pantalla. Hay que traerla a la vista.
    //
    // CUIDADO CON EL SUAVE, QUE AQUÍ NO SE PIDE Y VIENE SOLO.
    // `assets/css/styles.css` declara `html{scroll-behavior:smooth}`, y
    // `scrollIntoView` sin `behavior` usa 'auto', que significa "lo que diga esa
    // propiedad CSS". O sea que este scroll era SUAVE aunque este comentario
    // dijera lo contrario, y una animación en vuelo mientras el documento se
    // encoge acaba clampada donde no toca: el fallo original, intacto. Se fuerza
    // el salto poniendo `scroll-behavior` en el propio <html> —un estilo inline
    // gana a la hoja— y se restaura después, porque el resto de la página usa el
    // desplazamiento suave a propósito (ver `openCat`).
    var raiz=document.documentElement;
    function centrarConfirmacion(){
      var previo=raiz.style.scrollBehavior;
      raiz.style.scrollBehavior='auto';
      var ok=document.getElementById('lz-ok')||root;
      ok.scrollIntoView({block:'center'});
      raiz.style.scrollBehavior=previo;
      return ok;
    }
    // Doble requestAnimationFrame: el primero cede el turno para que el
    // navegador aplique el layout nuevo, el segundo mide ya sobre el definitivo.
    requestAnimationFrame(function(){
      requestAnimationFrame(function(){
        var ok=centrarConfirmacion();
        try{ ok.focus({preventScroll:true}); }catch(e){ }
        // Segundo pase. En móvil la clienta acaba de teclear su teléfono: al
        // sustituir el widget desaparece el <input> enfocado, el teclado se
        // cierra con su propia animación y el área visible crece cuando ya
        // habíamos medido. Un salto instantáneo repetido no se nota y tapa ese
        // caso, que no se puede reproducir sin un teclado de verdad.
        setTimeout(centrarConfirmacion, 350);
      });
    });

    // SEGUNDA CAPA, Y ES LA QUE NO PUEDE FALLAR.
    // Traer la confirmación a la vista depende del navegador, del teclado y del
    // CSS de la página, y ya ha fallado dos veces contra clientas reales: la
    // tarjeta se pinta, pero la clienta se queda en la galería —que está justo
    // debajo de esta sección— y cree que su cita no ha entrado. Así que la
    // confirmación no puede vivir SOLO en un sitio al que hay que llegar
    // desplazándose. Este aviso se pinta sobre el área visible: se ve esté donde
    // esté el scroll, y no se va hasta que ella lo cierra.
    // Cuelga de <body> y no del widget porque un ancestro con `transform`
    // rompería el `position:fixed`.
    var capa=document.createElement('div');
    capa.className='lz-ovl';
    capa.innerHTML='<div class="lz-toast" role="status"><div class="lz-toast-check">✓</div>'+
      '<h4>¡Cita confirmada!</h4>'+
      '<p><b>'+esc(st.service.name)+'</b>'+(emp?(' con '+esc(emp)):'')+'<br>'+esc(dia)+' a las '+fmt(iso)+'</p>'+
      '<p class="lz-toast-sub">Recibirás un recordatorio. Si necesitas cambiarla, escríbenos por WhatsApp.</p>'+
      '<button type="button" class="lz-toast-ok">Entendido</button></div>';
    function cerrarAviso(){
      if(capa.parentNode) capa.parentNode.removeChild(capa);
      centrarConfirmacion();
    }
    capa.addEventListener('click', function(ev){
      if(ev.target===capa || (ev.target.className||'')==='lz-toast-ok') cerrarAviso();
    });
    document.body.appendChild(capa);
  }

  // Se repinta solo la lista de resultados, no el paso entero: repintar el paso
  // le quitaria el foco al <input> y en movil se cerraria el teclado a la
  // primera letra.
  root.addEventListener('input', function(ev){
    if(!ev.target || ev.target.id!=='lz-q') return;
    st._query=ev.target.value;
    var b=g('lz-qclear'); if(b) b.hidden = !st._query;
    renderCarta();
  });

  root.addEventListener('click', function(ev){
    var t=ev.target.closest('button'); if(!t) return;
    if(t.classList.contains('lz-sal')){ elegirSalon(t.dataset.slug,t.dataset.wa,t.dataset.k); return; }
    if(t.id==='lz-abre'){ if(g('lz-panel').hidden) abrirPanel(); else cerrarPanel(); return; }
    if(t.classList.contains('lz-srv')){ elegirServicio(t.dataset.s); return; }
    if(t.id==='lz-qclear'){ st._query=''; var q=g('lz-q'); if(q){ q.value=''; try{q.focus();}catch(e){} } t.hidden=true; renderCarta(); return; }
    if(t.classList.contains('lz-chip')){ if(t.dataset.p && !t.disabled) showPeriod(t.dataset.p); return; }
    if(t.id==='lz-prev'){ var a=new Date(view.y,view.m-1,1); view.y=a.getFullYear(); view.m=a.getMonth(); renderCal(); return; }
    if(t.id==='lz-next'){ var b=new Date(view.y,view.m+1,1); view.y=b.getFullYear(); view.m=b.getMonth(); renderCal(); return; }
    if(t.classList.contains('lz-day') && !t.disabled){ pickDay(t.dataset.d); return; }
    if(t.classList.contains('lz-time')){ pickTime(parseInt(t.dataset.i,10)); return; }
    if(t.classList.contains('lz-emp')){ pickEmp(t.dataset.e); return; }
    if(t.id==='lz-confirm'){ ev.preventDefault(); doBooking(); return; }
  });

  window.__lzSwitch=function(slug,wa){ root.dataset.slug=slug; root.dataset.wa=wa; boot(); };
  boot();
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
      <a href="index.html#reservar" class="btn btn-gold">{CAL_ICON} Reservar cita</a>
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
<section class="booking sec-pad" id="reservar" style="background:#eef1ec"><div class="wrap" style="align-items:start">
  <div class="booking-head" style="grid-column:1/-1;text-align:center;max-width:660px;margin:0 auto 6px">
    <span class="eyebrow">Reserva online</span>
    <h2 style="font-size:clamp(32px,4.6vw,48px);color:var(--forest);margin:12px 0 10px">Reserva online, sin llamadas</h2>
    <p style="color:var(--muted)">Elige tu servicio y el calendario te muestra al momento los días con hueco. Sin llamadas ni esperas.</p>
  </div>
  <div class="booking-copy">
    <h3 style="font-family:'Cormorant Garamond',serif;font-size:27px;color:var(--forest);margin-bottom:14px">En 3 pasos, cita confirmada</h3>
    <ul>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Disponibilidad en tiempo real</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Recordatorio automático de tu cita</li>
      <li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6 9 17l-5-5"/></svg> Cambios y cancelaciones fáciles</li>
    </ul>
    <a href="{c['whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} ¿Prefieres WhatsApp? Escríbenos</a>
  </div>
  <div class="cal" id="lz-book" data-api="https://api.lanzo.es/api/public" data-wa="{c['whatsapp']}" data-salones='[{{"k":"fuen","nombre":"Fuenlabrada","slug":"{SLUG_FUEN}","wa":"{c['whatsapp']}"}},{{"k":"huma","nombre":"Humanes de Madrid","slug":"{SLUG_HUMA}","wa":"{c['huma_whatsapp']}"}}]' style="border-top:4px solid var(--gold-2)">
    <span class="cal-badge">Reservas · Lanzo</span>
    <div class="lz-status" style="color:var(--muted);font-size:14px;padding:20px 0;text-align:center">Cargando el calendario de reservas…</div>
  </div>
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
  <div class="head"><span class="eyebrow">Dónde estamos</span><h2>Nuestros dos salones</h2></div>
  <p class="subnote">Luluca Nails en Fuenlabrada y en Humanes de Madrid. Ven a vernos o reserva online en el salón que prefieras.</p>
  <div class="loc-grid">
    <div class="loc"><div class="map"><iframe loading="lazy" src="https://www.google.com/maps?q=Calle%20Escocia%201,%20Fuenlabrada&output=embed"></iframe></div><div class="body"><span class="tag-here">Fuenlabrada</span><h3>Fuenlabrada</h3><div class="info"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['fuen_addr']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['phone_display']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['fuen_hours']}</div></div><div class="actions"><a href="index.html#reservar" onclick="lzGoto('fuen')" class="btn btn-primary">Reservar aquí</a><a href="{c['fuen_maps']}" target="_blank" rel="noopener" class="btn btn-ghost">Cómo llegar</a></div></div></div>
    <div class="loc"><div class="map"><iframe loading="lazy" src="https://www.google.com/maps?q=Avenida%20Campo%20Hermoso%2044,%20Humanes%20de%20Madrid&output=embed"></iframe></div><div class="body"><span class="tag-here">Humanes</span><h3>Humanes de Madrid</h3><div class="info"><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['huma_addr']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['huma_phone_display']}</div><div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['huma_hours']}</div></div><div class="actions"><a href="index.html#reservar" onclick="lzGoto('huma')" class="btn btn-primary">Reservar aquí</a><a href="{c['huma_maps']}" target="_blank" rel="noopener" class="btn btn-ghost">Cómo llegar</a></div></div></div>
  </div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Luluca Nails — Uñas, manicura semipermanente y nail art en Fuenlabrada y Humanes",
                "Salón de uñas, cejas y pestañas en Fuenlabrada y Humanes de Madrid. Manicura semipermanente, uñas de gel y acrílico, nivelación, pedicura y nail art. 100% veganas. Reserva tu cita online.") + body

# ---------- SERVICIOS ----------
def build_servicios():
    # AVISO: este fichero fuente NO esta en el repositorio y no se conserva en ninguna
    # copia local. Mientras falte, build.py NO se puede ejecutar entero. El servicios.html
    # publicado se genero en su dia y se mantiene a mano. Para recuperar el generador hay
    # que reconstruir la fuente desde el catalogo de servicios.html (revertir cat2 -> cat).
    src=open(os.path.join(OUT,"luluca_servicios.html"),encoding="utf-8").read()
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
<section class="reserva-band" id="reserva"><span class="eyebrow" style="color:var(--gold-2)">Reserva online</span><h2>¿Lo tienes claro? Reserva en un minuto</h2><p>Elige día y hora en la agenda del salón que prefieras: Fuenlabrada o Humanes de Madrid. Sin llamadas ni esperas.</p><a href="index.html#reservar" class="btn btn-gold">Ir a reservar</a></section>
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
      <h3>Fuenlabrada</h3>
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
    <div class="contact-card">
      <h3>Humanes de Madrid</h3>
      <div class="cc-sub">Nuestro segundo salón</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg> {c['huma_addr']}</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg> {c['huma_phone_display']}</div>
      <div class="contact-row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg> {c['huma_hours']}</div>
      <div class="contact-actions">
        <a href="{c['huma_whatsapp']}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} WhatsApp</a>
        <a href="tel:{c['huma_tel']}" class="btn btn-ghost">Llamar</a>
      </div>
    </div>
    <div class="map-embed"><iframe loading="lazy" src="https://www.google.com/maps?q=Avenida%20Campo%20Hermoso%2044,%20Humanes%20de%20Madrid&output=embed"></iframe></div>
  </div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head("Contacto — Luluca Nails","Contacta con Luluca Nails por WhatsApp, teléfono o email. Salones en Fuenlabrada y Humanes de Madrid.")+body

AVISO_BODY = r"""<h2>1. Datos identificativos</h2>
<p>En cumplimiento de la Ley 34/2002 de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSICE), se informan los datos del titular de este sitio web:</p>
<ul>
<li><b>Titular:</b> Shirley Andrea Blanco Cardenas</li>
<li><b>NIF/CIF:</b> 60304664K</li>
<li><b>Nombre comercial:</b> Luluca Nails</li>
<li><b>Domicilio:</b> Calle Escocia 1, 28942 Fuenlabrada (Madrid)</li>
<li><b>Correo electrónico:</b> info@lulucanails.com &nbsp;·&nbsp; <b>Teléfono:</b> +34 690 06 27 62</li>
</ul>
<h2>2. Objeto</h2>
<p>Este sitio web informa sobre los servicios de belleza de Luluca Nails y permite la reserva de citas online.</p>
<h2>3. Alojamiento y reservas</h2>
<p>El sitio se aloja en GitHub Pages (GitHub, Inc.). El sistema de reservas y la agenda están gestionados por Lanzo, que actúa como encargado del tratamiento por cuenta del titular.</p>
<h2>4. Propiedad intelectual</h2>
<p>Los contenidos, textos, imágenes, logotipos y elementos de diseño pertenecen a sus respectivos titulares y no pueden reproducirse sin autorización.</p>
<h2>5. Responsabilidad</h2>
<p>El titular no se responsabiliza de los daños derivados del uso indebido del sitio ni de interrupciones ajenas a su control.</p>
<h2>6. Legislación aplicable</h2>
<p>Estas condiciones se rigen por la legislación española.</p>"""
PRIV_BODY = r"""<p>En Luluca Nails cuidamos la protección de tus datos. Esta política explica cómo tratamos la información que nos facilitas, conforme al Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD).</p>
<h2>1. Responsable del tratamiento</h2>
<ul>
<li><b>Responsable:</b> Shirley Andrea Blanco Cardenas — NIF/CIF 60304664K</li>
<li><b>Domicilio:</b> Calle Escocia 1, 28942 Fuenlabrada (Madrid)</li>
<li><b>Correo electrónico:</b> info@lulucanails.com</li>
</ul>
<h2>2. Qué datos tratamos</h2>
<p>Los que nos facilitas al reservar una cita o contactar: nombre y apellidos, teléfono y, en su caso, el servicio y la fecha elegidos. Si te escribimos por WhatsApp, también el número y el contenido de esa conversación.</p>
<h2>3. Para qué los usamos y base legal</h2>
<ul>
<li>Gestionar tu reserva y tu cita — base: la prestación del servicio que solicitas.</li>
<li>Enviarte confirmaciones y recordatorios de tu cita (WhatsApp, SMS o teléfono) — base: la prestación del servicio y el interés legítimo en evitar olvidos.</li>
<li>Atenderte y responder a tus consultas — base: tu consentimiento.</li>
</ul>
<h2>4. Conservación</h2>
<p>Conservamos tus datos mientras dure la relación y, después, durante los plazos legalmente exigibles; luego se suprimen o anonimizan.</p>
<h2>5. Destinatarios</h2>
<p>No vendemos tus datos. Para prestar el servicio trabajamos con proveedores que actúan como encargados del tratamiento:</p>
<ul>
<li><b>Lanzo</b> — sistema de reservas y agenda.</li>
<li><b>Meta Platforms (WhatsApp)</b> — envío de confirmaciones y recordatorios.</li>
<li><b>Google</b> — mapa de ubicación y reseñas mostradas en la web.</li>
<li><b>GitHub</b> — alojamiento del sitio web.</li>
</ul>
<p>Algunos proveedores pueden implicar transferencias internacionales de datos, amparadas en las garantías del RGPD (p. ej. cláusulas contractuales tipo).</p>
<h2>6. Tus derechos</h2>
<p>Puedes ejercer acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a info@lulucanails.com. Si consideras que no atendemos bien tu solicitud, puedes reclamar ante la Agencia Española de Protección de Datos (www.aepd.es).</p>
<h2>7. Seguridad y menores</h2>
<p>Aplicamos medidas para proteger tus datos. Este sitio no se dirige a menores de 14 años sin el consentimiento de sus tutores.</p>"""
COOKIES_BODY = r"""<p>Esta web utiliza cookies y tecnologías similares para funcionar correctamente y mejorar tu experiencia.</p>
<h2>1. Qué son</h2>
<p>Pequeños archivos que se guardan en tu dispositivo al navegar. Sirven para recordar preferencias y para que funciones como el mapa o el calendario de reservas trabajen bien.</p>
<h2>2. Cookies que utilizamos</h2>
<ul>
<li><b>Técnicas / necesarias:</b> imprescindibles para que la web y el sistema de reservas funcionen.</li>
<li><b>De terceros:</b> al mostrar el mapa y las fuentes de Google y el calendario de reservas de Lanzo, estos servicios pueden instalar cookies propias.</li>
</ul>
<p>No utilizamos cookies publicitarias ni de perfilado.</p>
<h2>3. Cómo gestionarlas</h2>
<p>Puedes permitir, bloquear o eliminar las cookies desde la configuración de tu navegador (Chrome, Safari, Firefox, Edge…). Desactivar algunas puede afectar al funcionamiento de la web.</p>"""

def legal_page(title, desc, body_html):
    body = f"""{header('')}
<section class="sec-pad"><div class="wrap" style="max-width:820px">
  <p style="margin-bottom:10px"><a href="index.html" style="color:var(--gold);text-decoration:none;font-size:14px">← Volver al inicio</a></p>
  <h1 style="font-family:'Cormorant Garamond',serif;color:var(--forest);font-size:clamp(30px,4vw,44px);margin:4px 0 6px">{title}</h1>
  <p style="color:var(--muted);font-size:13px;margin-bottom:26px">Última actualización: agosto de 2026</p>
  <div class="legal-body">{body_html}</div>
</div></section>
{footer()}{mobilebar()}{scripts()}"""
    return head(title+" — Luluca Nails", desc)+body

def canonical_block(path):
    """Metadatos sociales y canonical. Se inyectan aqui, en el escritor, para no
    tocar las 5 llamadas a head(). Sin esto, cada enlace compartido por WhatsApp
    sale como tarjeta sin foto."""
    url = SITE_URL + "/" + ("" if path == "index.html" else path)
    a = '<meta property="og:type" content="website">'
    return a + "\n" + "\n".join([
      '<meta property="og:site_name" content="Luluca Nails">',
      '<meta property="og:locale" content="es_ES">',
      '<meta property="og:url" content="%s">' % url,
      '<meta property="og:image" content="%s/assets/img/hero.jpg">' % SITE_URL,
      '<meta name="twitter:card" content="summary_large_image">',
      '<link rel="canonical" href="%s">' % url,
    ])

def w(path,html):
    a = '<meta property="og:type" content="website">'
    if a in html and 'rel="canonical"' not in html:
        html = html.replace(a, canonical_block(path), 1)
    open(os.path.join(OUT, path),"w",encoding="utf-8").write(html)
    print("wrote",path,len(html)//1024,"KB")

w("index.html",build_index())
w("servicios.html",build_servicios())
w("galeria.html",build_galeria())
w("contacto.html",build_contacto())
w("aviso-legal.html",legal_page("Aviso legal","Aviso legal de Luluca Nails, salón de belleza en Fuenlabrada.",AVISO_BODY))
w("privacidad.html",legal_page("Política de privacidad","Política de privacidad de Luluca Nails conforme al RGPD.",PRIV_BODY))
w("cookies.html",legal_page("Política de cookies","Política de cookies de la web de Luluca Nails.",COOKIES_BODY))
write_reviews_json(os.path.join(OUT,"reviews.json"))
print("wrote reviews.json")
print("OK")
