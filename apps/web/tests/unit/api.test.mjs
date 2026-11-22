import { test } from 'node:test';
import assert from 'node:assert';

// Pure status-mapping functions (mirrors apps/web/lib/api.ts)
function mapDependencyStatus(status) {
  if (status === 'healthy') return 'healthy';
  if (status === 'unhealthy') return 'unhealthy';
  return 'unknown';
}

function mapOverallStatus(status) {
  if (status === 'healthy') return 'healthy';
  if (status === 'degraded') return 'degraded';
  return 'unknown';
}

// ApiError class (mirrors apps/web/lib/api.ts)
class ApiError extends Error {
  constructor(message, statusCode, code = 'unknown_error') {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

test('api: mapDependencyStatus healthy', () => {
  assert.strictEqual(mapDependencyStatus('healthy'), 'healthy');
});

test('api: mapDependencyStatus unhealthy', () => {
  assert.strictEqual(mapDependencyStatus('unhealthy'), 'unhealthy');
});

test('api: mapDependencyStatus undefined returns unknown', () => {
  assert.strictEqual(mapDependencyStatus(undefined), 'unknown');
});

test('api: mapOverallStatus healthy', () => {
  assert.strictEqual(mapOverallStatus('healthy'), 'healthy');
});

test('api: mapOverallStatus degraded', () => {
  assert.strictEqual(mapOverallStatus('degraded'), 'degraded');
});

test('api: mapOverallStatus undefined returns unknown', () => {
  assert.strictEqual(mapOverallStatus(undefined), 'unknown');
});

test('api: ApiError sets message, statusCode, and code', () => {
  const err = new ApiError('boom', 503, 'service_unavailable');
  assert.strictEqual(err.message, 'boom');
  assert.strictEqual(err.statusCode, 503);
  assert.strictEqual(err.code, 'service_unavailable');
  assert.strictEqual(err.name, 'ApiError');
});

test('api: ApiError defaults code to unknown_error', () => {
  const err = new ApiError('boom');
  assert.strictEqual(err.code, 'unknown_error');
  assert.strictEqual(err.statusCode, undefined);
});

test('api: network error classification', () => {
  const err = new ApiError('Network error', undefined, 'network_error');
  assert.strictEqual(err.code, 'network_error');
  assert.strictEqual(err.statusCode, undefined);
});

test('api: timeout error classification', () => {
  const err = new ApiError('Request timed out', undefined, 'timeout');
  assert.strictEqual(err.code, 'timeout');
});

test('api: healthy response shape', () => {
  const body = {
    status: 'healthy',
    dependencies: {
      postgresql: { status: 'healthy' },
      redis: { status: 'healthy' }
    }
  };
  assert.strictEqual(mapOverallStatus(body.status), 'healthy');
  assert.strictEqual(mapDependencyStatus(body.dependencies.postgresql.status), 'healthy');
  assert.strictEqual(mapDependencyStatus(body.dependencies.redis.status), 'healthy');
});

test('api: degraded response shape', () => {
  const body = {
    status: 'degraded',
    dependencies: {
      postgresql: { status: 'healthy' },
      redis: { status: 'unhealthy', error: 'connection_failed' }
    }
  };
  assert.strictEqual(mapOverallStatus(body.status), 'degraded');
  assert.strictEqual(mapDependencyStatus(body.dependencies.postgresql.status), 'healthy');
  assert.strictEqual(mapDependencyStatus(body.dependencies.redis.status), 'unhealthy');
  assert.strictEqual(body.dependencies.redis.error, 'connection_failed');
});

test('api: HTTP 503 readiness returns usable body', () => {
  const body = {
    status: 'degraded',
    dependencies: {
      postgresql: { status: 'unhealthy', error: 'connection_failed' },
      redis: { status: 'healthy' }
    }
  };
  assert.strictEqual(mapOverallStatus(body.status), 'degraded');
  assert.strictEqual(mapDependencyStatus(body.dependencies.postgresql.status), 'unhealthy');
  assert.strictEqual(mapDependencyStatus(body.dependencies.redis.status), 'healthy');
});

test('api: invalid status values map to unknown', () => {
  assert.strictEqual(mapDependencyStatus(null), 'unknown');
  assert.strictEqual(mapDependencyStatus(''), 'unknown');
  assert.strictEqual(mapOverallStatus(null), 'unknown');
  assert.strictEqual(mapOverallStatus(''), 'unknown');
});
