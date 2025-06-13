// Service Worker para CryptoBot Dashboard
// Versão e cache
const CACHE_VERSION = 'cryptobot-v2.0.1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Recursos estáticos para cache
const STATIC_ASSETS = [
  '/',
  '/static/css/mobile-responsive.css',
  '/static/js/dashboard-mobile.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// URLs da API para cache
const API_URLS = [
  '/api/prices',
  '/api/signals',
  '/api/stats',
  '/api/trades'
];

// Instalar Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache recursos estáticos
      caches.open(STATIC_CACHE).then(cache => {
        console.log('[SW] Caching static assets...');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Forçar ativação imediata
      self.skipWaiting()
    ])
  );
});

// Ativar Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Activating Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Assumir controle de todas as páginas
      self.clients.claim()
    ])
  );
});

// Interceptar requisições
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégias de cache baseadas no tipo de recurso
  if (request.method === 'GET') {
    // Recursos estáticos - Cache First
    if (STATIC_ASSETS.some(asset => request.url.includes(asset))) {
      event.respondWith(cacheFirst(request));
    }
    // APIs - Network First com fallback
    else if (url.pathname.startsWith('/api/')) {
      event.respondWith(networkFirstWithFallback(request));
    }
    // Páginas HTML - Stale While Revalidate
    else if (request.headers.get('accept').includes('text/html')) {
      event.respondWith(staleWhileRevalidate(request));
    }
    // Outros recursos - Cache First com fallback de rede
    else {
      event.respondWith(cacheFirst(request));
    }
  }
});

// Estratégia Cache First
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    // Cache apenas respostas válidas
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Cache first failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

// Estratégia Network First com fallback
async function networkFirstWithFallback(request) {
  try {
    // Tentar rede primeiro
    const networkResponse = await fetch(request);
    
    if (networkResponse && networkResponse.status === 200) {
      // Cache resposta da API
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    // Se rede falhar, tentar cache
    return await caches.match(request) || createOfflineResponse(request);
    
  } catch (error) {
    console.log('[SW] Network first failed, trying cache:', error);
    
    // Tentar cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Retornar dados mock para APIs
    return createOfflineResponse(request);
  }
}

// Estratégia Stale While Revalidate
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse && networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(error => {
    console.log('[SW] Network failed:', error);
    return cachedResponse;
  });
  
  return cachedResponse || fetchPromise;
}

// Criar resposta offline para APIs
function createOfflineResponse(request) {
  const url = new URL(request.url);
  
  // Dados mock para diferentes endpoints
  const mockData = {
    '/api/prices': {
      BTC: { price: 45000, change: 2.5 },
      ETH: { price: 3200, change: -1.2 },
      ADA: { price: 0.85, change: 5.1 }
    },
    '/api/signals': [
      {
        id: 1,
        pair: 'BTC/USDT',
        action: 'BUY',
        confidence: 85,
        timestamp: new Date().toISOString()
      }
    ],
    '/api/stats': {
      totalTrades: 150,
      winRate: 78.5,
      totalProfit: 12.8,
      activeSignals: 3
    },
    '/api/trades': [
      {
        id: 1,
        pair: 'BTC/USDT',
        type: 'BUY',
        amount: 0.001,
        price: 45000,
        timestamp: new Date().toISOString()
      }
    ]
  };
  
  const data = mockData[url.pathname] || { error: 'Offline mode', message: 'Dados indisponíveis offline' };
  
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-cache'
    }
  });
}

// Background Sync para quando voltar online
self.addEventListener('sync', event => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(syncData());
  }
});

// Sincronizar dados quando voltar online
async function syncData() {
  try {
    // Verificar se há dados para sincronizar
    const syncData = await getStoredSyncData();
    
    if (syncData && syncData.length > 0) {
      for (const data of syncData) {
        await fetch(data.url, {
          method: data.method,
          body: data.body,
          headers: data.headers
        });
      }
      
      // Limpar dados sincronizados
      await clearStoredSyncData();
      
      // Notificar cliente sobre sincronização
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'SYNC_COMPLETE',
          message: 'Dados sincronizados com sucesso!'
        });
      });
    }
  } catch (error) {
    console.log('[SW] Sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', event => {
  console.log('[SW] Push received:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Nova atualização disponível!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      timestamp: new Date().toISOString(),
      url: '/'
    },
    actions: [
      {
        action: 'open',
        title: 'Abrir Dashboard'
      },
      {
        action: 'close',
        title: 'Fechar'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('CryptoBot Dashboard', options)
  );
});

// Clique em notificação
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      self.clients.openWindow('/')
    );
  }
});

// Funções auxiliares para IndexedDB
async function getStoredSyncData() {
  // Implementar lógica do IndexedDB se necessário
  return [];
}

async function clearStoredSyncData() {
  // Implementar lógica do IndexedDB se necessário
}

// Log de inicialização
console.log('[SW] Service Worker loaded successfully!');
