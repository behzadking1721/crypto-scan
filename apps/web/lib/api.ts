const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT_MS = 5000;

export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'unknown' | 'checking';

export interface DependencyHealth {
  status: 'healthy' | 'unhealthy';
  error?: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  dependencies: {
    postgresql: DependencyHealth;
    redis: DependencyHealth;
  };
}

export class ApiError extends Error {
  readonly statusCode?: number;
  readonly code: string;

  constructor(message: string, statusCode?: number, code = 'unknown_error') {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

function parseJsonBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    return Promise.resolve(undefined);
  }
  return response.json().catch(() => undefined);
}

async function fetchWithTimeout<T>(
  path: string,
  { timeout = REQUEST_TIMEOUT_MS }: { timeout?: number } = {}
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
      cache: 'no-store'
    });

    const body = await parseJsonBody(response);

    if (!response.ok) {
      const detail = (body as Record<string, unknown> | undefined)?.detail ||
        `HTTP ${response.status}`;
      throw new ApiError(String(detail), response.status, (body as Record<string, unknown> | undefined)?.code as string);
    }

    return body as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError('Request timed out', undefined, 'timeout');
    }
    throw new ApiError(
      err instanceof Error ? err.message : 'Network error',
      undefined,
      'network_error'
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  return fetchWithTimeout<HealthResponse>('/health');
}

export async function fetchReady(): Promise<HealthResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/ready`, {
      signal: controller.signal,
      headers: { Accept: 'application/json' },
      cache: 'no-store'
    });

    const body = await parseJsonBody(response);

    if (response.status === 503) {
      return body as HealthResponse;
    }

    if (!response.ok) {
      const detail = (body as Record<string, unknown> | undefined)?.detail ||
        `HTTP ${response.status}`;
      throw new ApiError(String(detail), response.status, (body as Record<string, unknown> | undefined)?.code as string);
    }

    return body as HealthResponse;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError('Request timed out', undefined, 'timeout');
    }
    throw new ApiError(
      err instanceof Error ? err.message : 'Network error',
      undefined,
      'network_error'
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export function mapDependencyStatus(status: 'healthy' | 'unhealthy' | undefined): HealthStatus {
  if (status === 'healthy') return 'healthy';
  if (status === 'unhealthy') return 'unhealthy';
  return 'unknown';
}

export function mapOverallStatus(status: 'healthy' | 'degraded' | undefined): HealthStatus {
  if (status === 'healthy') return 'healthy';
  if (status === 'degraded') return 'degraded';
  return 'unknown';
}

export { API_BASE_URL, REQUEST_TIMEOUT_MS };
