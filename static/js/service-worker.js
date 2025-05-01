const CACHE_NAME = 'whisky-goggles-v2';
const urlsToCache = [
    '/',
    '/static/css/output.css',
    '/static/js/main.js',
    '/static/manifest.json',
    '/static/icons/favicon.ico',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
    // Immediately activate the new service worker
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    // Immediately take control of all clients
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Always fetch first, fall back to cache
                return fetch(event.request)
                    .catch(() => response);
            })
    );
}); 