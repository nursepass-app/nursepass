const CACHE_NAME = 'nursepass-v2';
const CACHE_FILES = [
  '/nursepass/',
  '/nursepass/index.html',
  '/nursepass/images/hikari/hikari_lv1.png',
  '/nursepass/images/hikari/hikari_lv2.png',
  '/nursepass/images/hikari/hikari_lv3.png',
  '/nursepass/images/hikari/hikari_lv4.png',
  '/nursepass/images/hikari/hikari_lv5.png',
  '/nursepass/sounds/correct.mp3'
];

// Install: cache all files
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(CACHE_FILES);
    })
  );
  self.skipWaiting();
});

// Activate: clean up old caches
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) {
          return key !== CACHE_NAME;
        }).map(function(key) {
          return caches.delete(key);
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch: serve from cache, fall back to network
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        // Cache successful GET responses
        if (event.request.method === 'GET' && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      }).catch(function() {
        // Offline fallback: return cached index.html for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/nursepass/index.html');
        }
      });
    })
  );
});
