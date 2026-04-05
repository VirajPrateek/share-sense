const CACHE_NAME = 'sharesense-v2';
const SHELL_URLS = ['/'];

// Cache app shell on install
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(SHELL_URLS))
  );
  self.skipWaiting();
});

// Clean old caches on activate
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for API calls (cache response for offline), cache-first for shell
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API calls: network first, fall back to cache
  if (url.pathname.startsWith('/api/')) {
    // Only cache GET requests
    if (e.request.method !== 'GET') return;

    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // App shell: cache first, fall back to network
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
