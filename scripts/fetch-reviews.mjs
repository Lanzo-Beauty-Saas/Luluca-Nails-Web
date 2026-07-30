// Actualiza reviews.json con las reseñas reales de Google (Places API New).
// Se ejecuta desde GitHub Actions (ver .github/workflows/update-reviews.yml).
// Requiere la variable de entorno GOOGLE_MAPS_API_KEY.
// Opcionales: PLACE_ID (recomendado), PLACE_QUERY (para resolver el ID si no se da),
//             MIN_RATING (por defecto 4), MAX (por defecto 6), LANG (por defecto es).

import { readFile, writeFile } from 'node:fs/promises';

const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
let   PLACE_ID = process.env.PLACE_ID || '';
const PLACE_QUERY = process.env.PLACE_QUERY || '';
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

const data = {
  rating: details.rating ?? (prev ? prev.rating : null),
  count: details.userRatingCount ?? (prev ? prev.count : null),
  updated: new Date().toISOString().slice(0, 10),
  source: 'places-api',
  reviews
};

await writeFile(OUT, JSON.stringify(data, null, 2) + '\n', 'utf-8');
console.log('reviews.json actualizado:', data.rating, '·', data.count, 'reseñas ·', reviews.length, 'tarjetas');
