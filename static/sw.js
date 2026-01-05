// Service Worker - Minimal version für Safari Kompatibilität
const CACHE_NAME = 'caloriesnap-v2';

// Nur statische Assets cachen, KEINE Seiten mit Redirects
const urlsToCache = [
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Alte Caches löschen
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // Nur GET Requests und keine API calls cachen
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/api/')) return;

  // Navigation Requests (HTML Seiten) NICHT cachen - das verursacht das Safari Problem
  if (event.request.mode === 'navigate') {
    return;
  }

  // Nur statische Assets cachen
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});