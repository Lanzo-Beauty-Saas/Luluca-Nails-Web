// Actualiza reviews.json con las reseñas reales de Google (Places API New).
// Se ejecuta desde GitHub Actions (ver .github/workflows/update-reviews.yml).
// Requiere la variable de entorno GOOGLE_MAPS_API_KEY.
//
// DOS SALONES. Cada local tiene su propia ficha de Google y su propia nota
// (Fuenlabrada y Humanes). Antes esto solo miraba una y la web enseñaba ese
// número como si fuera el del negocio entero. Ahora consulta las dos, guarda
// cada agregado por separado y calcula el total ponderado por número de
// reseñas. Las tarjetas que se ven en la web salen de la ficha principal.
//
// Opcionales: PLACE_ID / PLACE_QUERY (ficha principal, Fuenlabrada),
//             PLACE_ID_2 / PLACE_QUERY_2 (segunda ficha, Humanes; si no se da
//             ninguna de las dos, el total es el de la principal),
//             MIN_RATING (por defecto 4), MAX (por defecto 6), LANG (por defecto es).

import { readFile, writeFile } from 'node:fs/promises';

const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
let   PLACE_ID = process.env.PLACE_ID || '';
const PLACE_QUERY = process.env.PLACE_QUERY || '';
let   PLACE_ID_2 = process.env.PLACE_ID_2 || '';
const PLACE_QUERY_2 = process.env.PLACE_QUERY_2 || '';
const MIN_RATING = parseInt(process.env.MIN_RATING || '4', 10);
const MAX = parseInt(process.env.MAX || '6', 10);
const LANG = process.env.LANG_CODE || 'es';
const OUT = process.env.OUT || 'reviews.json';

if (!API_KEY) { console.error('Falta GOOGLE_MAPS_API_KEY'); process.exit(1); }

async function resolvePlaceId(query) {
  const res = await fetch('https://places.googleapis.com/v1/places:searchText', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Goog-Api-Key': API_KEY,
      'X-Goog-FieldMask': 'places.id,places.displayName'
    },
    body: JSON.stringify({ textQuery: query, languageCode: LANG })
  });
  if (!res.ok) throw new Error('searchText ' + res.status + ' ' + await res.text());
  const j = await res.json();
  if (!j.places || !j.places.length) throw new Error('Sin resultados para: ' + query);
  console.log('Place resuelto:', j.places[0].displayName?.text, '->', j.places[0].id);
  return j.places[0].id;
}

async function getDetails(placeId) {
  const url = 'https://places.googleapis.com/v1/places/' + encodeURIComponent(placeId)
            + '?languageCode=' + encodeURIComponent(LANG);
  const res = await fetch(url, {
    headers: {
      'X-Goog-Api-Key': API_KEY,
      'X-Goog-FieldMask': 'rating,userRatingCount,reviews'
    }
  });
  if (!res.ok) throw new Error('placeDetails ' + res.status + ' ' + await res.text());
  return res.json();
}

function mapReview(r) {
  const a = r.authorAttribution || {};
  return {
    name: a.displayName || 'Cliente de Google',
    photo: a.photoUri || null,
    rating: r.rating || 5,
    text: (r.originalText && r.originalText.text) || (r.text && r.text.text) || '',
    date: r.relativePublishTimeDescription || '',
    time: r.publishTime || ''
  };
}

async function readExisting() {
  try { return JSON.parse(await readFile(OUT, 'utf-8')); } catch { return null; }
}

const details = await getDetails(PLACE_ID || (PLACE_ID = await resolvePlaceId(PLACE_QUERY)));

let reviews = (details.reviews || [])
  .map(mapReview)
  .filter(r => r.rating >= MIN_RATING && r.text.trim().length > 0)
  .sort((x, y) => (y.time || '').localeCompare(x.time || ''))
  .slice(0, MAX);

// Si el filtro deja la lista vacía, conservamos las tarjetas anteriores (solo refrescamos el agregado).
const prev = await readExisting();
if (!reviews.length && prev && prev.reviews && prev.reviews.length) {
  console.log('Sin reseñas nuevas tras el filtro; conservo las tarjetas anteriores.');
  reviews = prev.reviews;
}

const fuen = {
  rating: details.rating ?? (prev && prev.salones ? prev.salones.fuen.rating : (prev ? prev.rating : null)),
  count: details.userRatingCount ?? (prev && prev.salones ? prev.salones.fuen.count : (prev ? prev.count : null))
};

// Segunda ficha. Si falla (ID mal puesto, cuota agotada), se conserva lo que
// hubiera: mejor una cifra de ayer que dejar a Humanes sin nota.
let huma = (prev && prev.salones && prev.salones.huma) || null;
if (PLACE_ID_2 || PLACE_QUERY_2) {
  try {
    const d2 = await getDetails(PLACE_ID_2 || (PLACE_ID_2 = await resolvePlaceId(PLACE_QUERY_2)));
    huma = { rating: d2.rating ?? (huma ? huma.rating : null),
             count: d2.userRatingCount ?? (huma ? huma.count : null) };
  } catch (e) {
    console.error('No se pudo leer la segunda ficha, conservo la anterior:', e.message);
  }
}

// Media ponderada por número de reseñas, no media de medias: con 132 y 17
// reseñas, promediar 4,6 y 4,9 daría 4,75 y sería inflar la nota.
function total(a, b) {
  if (!b || !b.count) return { rating: a.rating, count: a.count };
  const n = a.count + b.count;
  return { rating: Math.round(((a.rating * a.count + b.rating * b.count) / n) * 10) / 10, count: n };
}

const data = {
  rating: fuen.rating,
  count: fuen.count,
  salones: { fuen, huma },
  total: total(fuen, huma),
  updated: new Date().toISOString().slice(0, 10),
  source: 'places-api',
  reviews
};

await writeFile(OUT, JSON.stringify(data, null, 2) + '\n', 'utf-8');
console.log('reviews.json actualizado · Fuenlabrada', fuen.rating, '(' + fuen.count + ')',
            '· Humanes', huma ? huma.rating + ' (' + huma.count + ')' : 'sin datos',
            '· total', data.total.rating, '(' + data.total.count + ')',
            '·', reviews.length, 'tarjetas');
