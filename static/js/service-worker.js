const CACHE_NAME = 'whisky-goggles-v1';
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
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch new
                return response || fetch(event.request);
            })
    );
}); 