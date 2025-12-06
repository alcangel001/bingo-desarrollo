// Service Worker para Bingo JyM PWA
const CACHE_NAME = 'bingo-jym-v4';
// NO cachear la página principal - siempre obtenerla de la red
const urlsToCache = [
  '/static/css/admin_styles.css',
  '/static/images/bingo_login_background_v2.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache abierto');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Error al cachear recursos:', error);
      })
  );
  // NO forzar activación inmediata en iOS - puede causar problemas
  // self.skipWaiting();
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eliminando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Limpiar cualquier cache de páginas HTML
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.keys().then((keys) => {
          return Promise.all(
            keys.map((request) => {
              // Eliminar páginas HTML del cache
              if (request.destination === 'document' || 
                  request.url.includes('/lobby/') ||
                  request.url.includes('/game/')) {
                console.log('Eliminando página HTML del cache:', request.url);
                return cache.delete(request);
              }
            })
          );
        });
      });
    })
  );
  // NO tomar control inmediatamente en iOS - puede causar loops
  // return self.clients.claim();
});

// Interceptar peticiones de red
self.addEventListener('fetch', (event) => {
  // Solo cachear peticiones GET
  if (event.request.method !== 'GET') {
    return;
  }

  // Estrategia: Network First para páginas HTML (siempre obtener la versión más reciente)
  if (event.request.destination === 'document' || 
      event.request.url.includes('/lobby/') ||
      event.request.url.includes('/game/') ||
      event.request.url.includes('/login/') ||
      event.request.url.includes('/register/')) {
    
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Si la red funciona, devolver la respuesta (no cachear páginas HTML)
          return response;
        })
        .catch(() => {
          // Solo si la red falla completamente, intentar cache
          return caches.match(event.request);
        })
    );
    return;
  }

  // Para recursos estáticos (CSS, JS, imágenes), usar Cache First
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Si está en cache, devolverlo
        if (response) {
          return response;
        }

        // Si no está en cache, hacer petición de red
        return fetch(event.request).then((response) => {
          // Verificar que la respuesta sea válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Solo cachear recursos estáticos, NO páginas HTML
          if (event.request.destination !== 'document') {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }

          return response;
        }).catch(() => {
          // Si falla la red, devolver del cache solo para recursos estáticos
          return caches.match(event.request);
        });
      })
  );
});

// Manejar notificaciones push (opcional, para futuro)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'Nueva notificación de Bingo JyM',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: 'bingo-notification'
  };

  event.waitUntil(
    self.registration.showNotification('Bingo JyM', options)
  );
});

// Manejar clics en notificaciones
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});

