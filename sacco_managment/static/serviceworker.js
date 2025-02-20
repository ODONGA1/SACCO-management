// self.addEventListener('install', function(event) {
//     event.waitUntil(
//         caches.open('django-pwa-cache').then(function(cache) {
//             return cache.addAll([
//                 '/',
//                 '/static/images/icon-192x192.png',
//                 '/static/images/icon-512x512.png',
//                 '/static/css/styles.css',
//                 '/static/js/main.js'
//             ]);
//         })
//     );
// });

// self.addEventListener('fetch', function(event) {
//     event.respondWith(
//         caches.match(event.request).then(function(response) {
//             return response || fetch(event.request);
//         })
//     );
// });

const CACHE_NAME = 'Prime SACCO';
const ASSETS = [
  '/',
  '/static/css/styles.css',
  '/static/js/app.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  // Add other static assets here
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});