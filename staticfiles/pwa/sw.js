/**
 * BeitDesk Service Worker
 * Municipality of Beitbridge IT Help Desk
 *
 * Strategy:
 * - Static assets (CSS, JS, images, fonts): Cache-first, then network
 * - Dashboard pages: Network-first, fallback to cache
 * - Offline fallback page shown when network unavailable and no cache
 */

const CACHE_NAME      = 'beitdesk-v1';
const OFFLINE_URL     = '/static/pwa/offline.html';

// Assets to pre-cache on install
const PRECACHE_ASSETS = [
  '/static/pwa/offline.html',
  '/static/pwa/manifest.json',
  '/static/pwa/icon-192.png',
  '/static/pwa/icon-512.png',
  '/static/img/beitbridge_logo.jpg',
  '/static/img/beitbridge_bg.png',
  '/static/img/favicon.svg',
];

// Pages to cache for offline access
const CACHE_PAGES = [
  '/dashboard/',
  '/dashboard/tickets/',
  '/dashboard/glossary/',
];

// ── Install ───────────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[BeitDesk SW] Pre-caching assets individually...');
      
      // Fetch each asset individually so a missing 404 image or manifest doesn't fail entire SW
      const cachePromises = PRECACHE_ASSETS.map(async (url) => {
        try {
          const response = await fetch(url);
          if (response.ok) {
            await cache.put(url, response);
          } else {
            console.warn(`[BeitDesk SW] Skipped pre-caching ${url}: Status ${response.status}`);
          }
        } catch (err) {
          console.warn(`[BeitDesk SW] Failed to fetch ${url}:`, err);
        }
      });

      await Promise.allSettled(cachePromises);
    }).then(() => self.skipWaiting())
  );
});

// ── Activate ──────────────────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch ─────────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET, API, admin, and Vercel SSO auth requests
  if (request.method !== 'GET') return;
  if (url.href.includes('vercel.com/sso-api')) return;
  if (url.pathname.startsWith('/api/') ||
      url.pathname.startsWith('/dashboard/api/') ||
      url.pathname.startsWith('/admin/')) return;

  // Google Fonts — Cache first, network fallback (allows cross-origin CORS/opaque)
  if (url.hostname.includes('fonts.gstatic.com') || url.hostname.includes('fonts.googleapis.com')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response && (response.status === 200 || response.type === 'opaque')) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, clone));
          }
          return response;
        }).catch(() => undefined);
      })
    );
    return;
  }

  // Skip non-same-origin requests for remaining local logic
  if (url.origin !== location.origin) return;

  // Static assets — Cache first, then network, update cache in background
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => {
        const networkFetch = fetch(request).then(response => {
          if (response && response.status === 200 && response.type === 'basic') {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, clone));
          }
          return response;
        }).catch(() => cached);
        return cached || networkFetch;
      })
    );
    return;
  }

  // HTML pages — Network first, fallback to cache, then offline page
  event.respondWith(
    fetch(request)
      .then(response => {
        // Cache successful HTML page responses
        if (response && response.status === 200 && response.type === 'basic') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(request).then(cached => {
          if (cached) return cached;
          return caches.match(OFFLINE_URL);
        })
      )
  );
});

// ── Background sync for offline ticket creation (future) ─────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-tickets') {
    event.waitUntil(syncOfflineTickets());
  }
});

async function syncOfflineTickets() {
  console.log('[BeitDesk SW] Syncing offline tickets...');
}

// ── Push notifications (future) ───────────────────────────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'BeitDesk', {
      body:    data.body || 'You have a new notification',
      icon:    '/static/pwa/icon-192.png',
      badge:   '/static/pwa/icon-72.png',
      tag:     data.tag || 'beitdesk',
      data:    { url: data.url || '/dashboard/' },
      actions: [
        { action: 'open',    title: 'Open BeitDesk' },
        { action: 'dismiss', title: 'Dismiss' },
      ],
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  if (event.action !== 'dismiss') {
    const url = event.notification.data?.url || '/dashboard/';
    event.waitUntil(clients.openWindow(url));
  }
});