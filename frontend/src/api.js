const DEFAULT_GATEWAY_URL = 'http://127.0.0.1:8080';

export function getGatewayUrl() {
  return globalThis.SEDUX_GATEWAY_URL || DEFAULT_GATEWAY_URL;
}

async function requestJson(path, { fetchImpl = globalThis.fetch, baseUrl = getGatewayUrl() } = {}) {
  if (typeof fetchImpl !== 'function') {
    throw new Error('Fetch is unavailable in this browser');
  }

  const response = await fetchImpl(`${baseUrl}${path}`, {
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Gateway request failed with status ${response.status}`);
  }

  return response.json();
}

export function getServices(options) {
  return requestJson('/services', options).then((payload) => payload.services || []);
}

export function getHealth(options) {
  return requestJson('/health', options);
}

export function mapServiceStatus(service) {
  return {
    ...service,
    name: service.name.charAt(0).toUpperCase() + service.name.slice(1),
    status: service.status === 'ok' ? 'healthy' : service.status,
    kind: service.kind || 'service',
  };
}

export async function loadServiceRegistry(options) {
  const services = await getServices(options);
  return services.map(mapServiceStatus);
}
