const CACHE_NAME = 'nursepass-v5';
const CACHE_FILES = [
  '/nursepass/',
  '/nursepass/index.html',
  '/nursepass/questions.json',
  '/nursepass/images/hikari/hikari_lv0.png',
  '/nursepass/images/hikari/hikari_lv0birth1.png',
  '/nursepass/images/hikari/hikari_lv0birth2.png',
  '/nursepass/images/hikari/hikari_lv01.png',
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

// Fetch: network-first for HTML, cache-first for other assets
self.addEventListener('fetch', function(event) {
  var url = event.request.url;
  var isHtml = event.request.mode === 'navigate' || url.endsWith('.html') || url.endsWith('/nursepass/');

  if (isHtml) {
    // Network-first for HTML: always get fresh code, fall back to cache offline
    event.respondWith(
      fetch(event.request).then(function(response) {
        if (response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      }).catch(function() {
        return caches.match(event.request).then(function(cached) {
          return cached || caches.match('/nursepass/index.html');
        });
      })
    );
  } else {
    // Cache-first for images, sounds, JSON
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        return fetch(event.request).then(function(response) {
          if (event.request.method === 'GET' && response.status === 200) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        });
      })
    );
  }
});
