const DEFAULT_API_BASE_URL = 'http://localhost:3000';

const resolveBaseUrl = () => {
  const envUrl = import.meta.env?.VITE_API_BASE_URL;
  const cleanedEnv = typeof envUrl === 'string' ? envUrl.trim() : '';

  if (cleanedEnv) {
    return cleanedEnv.replace(/\/$/, '');
  }

  return DEFAULT_API_BASE_URL;
};

const API_BASE_URL = resolveBaseUrl();

function buildUrl(path) {
  if (!path.startsWith('/')) {
    throw new Error(`El path de la API debe comenzar con '/': ${path}`);
  }
  return `${API_BASE_URL}${path}`;
}

export async function apiRequest(path, options = {}) {
  const {
    method = 'GET',
    body,
    token,
    headers = {},
    signal,
  } = options;

  const url = buildUrl(path);
  const finalHeaders = { ...headers };

  if (body !== undefined && !finalHeaders['Content-Type']) {
    finalHeaders['Content-Type'] = 'application/json';
  }

  if (token) {
    finalHeaders.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => ({}))
    : await response.text().catch(() => '');

  if (!response.ok) {
    const message =
      (payload && payload.mensaje) ||
      (typeof payload === 'string' && payload) ||
      `Error ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.details = payload;
    throw error;
  }

  return payload;
}

export { API_BASE_URL };
