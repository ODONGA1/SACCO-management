const CACHE_NAME = 'Prime SACCO';
const ASSETS = [
  '/',
  '/static/asset/css/styles.css',
  '/static/asset/js/app.js',
  '/static/asset/icons/icon-192x192.png',
  '/static/asset/icons/icon-512x512.png',
  // Add other static assets here
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});