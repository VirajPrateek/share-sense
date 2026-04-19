const CACHE_NAME = 'sharesense-v3';

// All assets to pre-cache on install
const PRECACHE_URLS = [
  '/',
  '/static/style.css',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png',
];

// Install: pre-cache app shell
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Skip non-GET and cross-origin requests
  if (e.request.method !== 'GET') return;
  if (url.origin !== self.location.origin && !url.hostname.includes('fonts.g')) return;

  // API calls: network first, fall back to cache
  if (url.pathname.startsWith('/api/')) {
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

  // Static assets + app shell: cache first, network fallback
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        // Cache successful responses for static assets
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        }
        return res;
      });
    })
  );
});

// Background sync for offline list items
self.addEventListener('sync', e => {
  if (e.tag === 'sync-list-items') {
    e.waitUntil(syncListItems());
  }
});

async function syncListItems() {
  // Open IndexedDB and push any pending items to the server
  const db = await openIDB();
  const pending = await getAllPending(db);
  for (const item of pending) {
    try {
      const res = await fetch(item.url, {
        method: item.method,
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + item.token },
        body: item.body,
      });
      if (res.ok) await deletePending(db, item.id);
    } catch (e) {
      // Still offline, leave for next sync
    }
  }
}

function openIDB() {
  return new Promise((res, rej) => {
    const req = indexedDB.open('sharesense', 1);
    req.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('pending_sync')) {
        db.createObjectStore('pending_sync', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('list_items')) {
        const store = db.createObjectStore('list_items', { keyPath: 'id' });
        store.createIndex('group_id', 'group_id', { unique: false });
      }
    };
    req.onsuccess = e => res(e.target.result);
    req.onerror = e => rej(e.target.error);
  });
}

function getAllPending(db) {
  return new Promise((res, rej) => {
    const tx = db.transaction('pending_sync', 'readonly');
    const req = tx.objectStore('pending_sync').getAll();
    req.onsuccess = () => res(req.result);
    req.onerror = () => rej(req.error);
  });
}

function deletePending(db, id) {
  return new Promise((res, rej) => {
    const tx = db.transaction('pending_sync', 'readwrite');
    const req = tx.objectStore('pending_sync').delete(id);
    req.onsuccess = () => res();
    req.onerror = () => rej(req.error);
  });
}
